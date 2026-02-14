# BLE HID Peripheral – Persistente Verbindung (Reconnect-Analyse)

## Übersicht

Dieses Dokument beschreibt die Analyse und Lösung eines Problems mit BLE HID Peripheral-Verbindungen zwischen einem Raspberry Pi (BlueZ-Stack, `bluez_peripheral`-Bibliothek) und einer Nokia 8010 AndroidTV Box.

**Ziel:** Eine bootfeste, persistente BLE-Verbindung, die nach Prozess-Neustart, BlueZ-Neustart und System-Reboot automatisch wieder aufgebaut wird – ohne erneutes Pairing.

---

## Das Problem

Beim Beenden eines BLE HID Peripheral-Prozesses zerstört BlueZ die Bluetooth-Verbindung so, dass die Nokia 8010 **nicht mehr reconnecten kann** – auch nicht nach einem Neustart. Das Bonding wird effektiv „vergiftet".

---

## Die Ursachenkette im Detail

### Was bei einem normalen Prozess-Exit passiert

```
Python-Prozess beendet sich
    → dbus_fast schließt D-Bus-Verbindung (Finalizer)
    → D-Bus-Daemon meldet BlueZ: "Client :1.xx ist weg"
    → BlueZ ruft intern proxy_removed_cb() auf
    → GATT Services werden entfernt (gatt_db_service_removed)
    → BlueZ sendet "Service Changed Indication" an Nokia
       (send_notification_to_device)
    → Nokia empfängt Indication WÄHREND sie noch verbunden ist
    → Nokia macht volle GATT Re-Discovery
    → Nokia findet KEINE HID Services mehr (sind ja gerade entfernt)
    → Nokia trennt sich selbst (reason 3 = Remote User Terminated)
    → BlueZ setzt "Automatic connection disabled"
    → Bonding ist dauerhaft kaputt
```

### Warum `Automatic connection disabled` fatal ist

BlueZ setzt dieses Flag wenn ein Gerät sich **selbst** trennt (`reason 3`) nach einem fehlgeschlagenen Bonding-Versuch (`status 14`). Das Flag verhindert, dass BlueZ zukünftige Reconnect-Versuche der Nokia akzeptiert – **auch nach Neustart von BlueZ oder Reboot**.

### Relevante BlueZ-Log-Zeilen (Fehlschlag)

```
src/gatt-database.c:proxy_removed_cb() Proxy removed - removing service: .../service_hid/service0
src/gatt-database.c:gatt_db_service_removed() Local GATT service removed
src/gatt-database.c:send_notification_to_device() GATT server sending indication
...
src/adapter.c:dev_disconnected() Device 22:22:09:C3:08:3D disconnected, reason 3
src/device.c:device_bonding_failed() status 14
src/device.c:att_disconnected_cb() Automatic connection disabled
```

---

## Getestete Ansätze und warum sie scheiterten

| Versuch | Warum gescheitert |
|---|---|
| `os._exit(0)` | Kernel schließt Socket → BlueZ bemerkt Client weg → `proxy_removed_cb` → Services entfernt während Nokia verbunden |
| `SIGKILL` | Identisch – der Kernel schließt den Socket, BlueZ reagiert gleich |
| Explizites `unregister_services()` | Noch schlimmer – sendet `UnregisterApplication` D-Bus-Calls die BlueZ **sequentiell** verarbeitet während Nokia verbunden ist |
| Disconnect dann Exit | Nokia reconnected **sofort** nach Disconnect (typisches BLE HID Verhalten), trifft auf leeren GATT Server |
| Services neu registrieren vor Exit | Timing-Problem – Services werden nach Exit trotzdem entfernt |
| D-Bus Socket manuell schließen | BlueZ bemerkt verschwundenen Client trotzdem und räumt auf |

---

## Die funktionierende Lösung

### Kernprinzip

```
Nokia MUSS bereits getrennt und "aufgegeben" haben,
BEVOR die GATT Services entfernt werden.

Reihenfolge:  Advertising weg → Disconnect → Nokia gibt auf → Prozess stirbt
Falsch:       Disconnect → Prozess stirbt → Services weg → Nokia noch verbunden → KAPUTT
```

### Implementierung

```python
import asyncio
import signal
import logging
import os
from BleKeyboard.BleKeyboard import BleKeyboard

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("startBLE")

async def main():
    kb = await BleKeyboard.create()
    logger.info("BleKeyboard Modul ist eigenständig aktiv.")

    stop_event = asyncio.Event()

    def _shutdown():
        logger.info("Signal empfangen...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _shutdown)

    await stop_event.wait()

    # 1) Connection Monitor stoppen
    if kb._connection_monitor_task is not None:
        kb._connection_monitor_task.cancel()
        kb._connection_monitor_task = None

    # 2) Advertising stoppen
    if kb.active_advertisement is not None:
        try:
            await kb.active_advertisement.unregister()
        except Exception:
            pass
        kb.active_advertisement = None

    # 3) Warten bis Nokia kein Advertising mehr sieht
    await asyncio.sleep(1)

    # 4) Disconnect
    await kb.disconnect()

    # 5) Warten bis Nokia den Reconnect-Versuch aufgibt
    await asyncio.sleep(2)

    # 6) Hart beenden – keine Python/dbus_fast Finalizer
    logger.info("Beende Prozess...")
    os.kill(os.getpid(), signal.SIGKILL)

if __name__ == "__main__":
    asyncio.run(main())
```

### Warum jeder Schritt notwendig ist

| Schritt | Was passiert | Warum notwendig |
|---|---|---|
| **1. Monitor stoppen** | Connection Monitor Task wird gecancelt | Verhindert dass der Monitor während des Shutdowns ein neues Advertising startet |
| **2. Advertising stoppen** | `UnregisterAdvertisement` → BlueZ entfernt BLE Advertisement | Nokia kann den Raspberry danach **nicht mehr finden** und wird keinen Reconnect versuchen |
| **3. 1s warten** | Advertising wird auf HCI-Ebene entfernt | Nokia muss Zeit haben zu bemerken, dass das Advertising weg ist |
| **4. Disconnect** | `Device1.Disconnect` → ATT-Verbindung wird getrennt (`reason 2`) | Nokia sieht saubere Trennung – aber ohne Advertising kann sie nicht reconnecten |
| **5. 2s warten** | Nokia versucht kurz zu reconnecten, findet kein Advertising, gibt auf | **Entscheidend**: Nokia muss aufgeben BEVOR der Prozess stirbt und die Services entfernt werden |
| **6. SIGKILL** | Prozess wird sofort getötet, keine Python-Finalizer | Verhindert dass `dbus_fast` beim Aufräumen `UnregisterApplication`-Calls sendet – aber da die Nokia nicht mehr verbunden ist, schadet `proxy_removed_cb` nicht mehr |

### Vergleich der Disconnect-Reasons

| Reason | Bedeutung | Auslöser | Auswirkung |
|---|---|---|---|
| `reason 2` | Local Host Terminated | Unser `Device1.Disconnect` | Nokia sieht saubere Trennung ✅ |
| `reason 3` | Remote User Terminated | Nokia trennt sich selbst (leerer GATT Server) | `Automatic connection disabled` → Bonding kaputt ❌ |

---

## Relevante BlueZ-Log-Zeilen (Erfolg)

```
# Advertising wird entfernt
src/advertising.c:unregister_advertisement() UnregisterAdvertisement

# Sauberer Disconnect (reason 2, nicht reason 3!)
src/adapter.c:dev_disconnected() Device 22:22:09:C3:08:3D disconnected, reason 2

# Services werden entfernt NACHDEM Nokia nicht mehr verbunden ist
# → Keine "send_notification_to_device" mehr möglich!
src/gatt-database.c:proxy_removed_cb() Proxy removed - removing service: ...
src/gatt-database.c:gatt_db_service_removed() Local GATT service removed
src/gatt-database.c:client_disconnect_cb() Client disconnected
```

---

## Regeln für die Weiterentwicklung

### 1. Niemals `unregister_services()` aufrufen während ein Gerät verbunden sein könnte

```python
# ❌ FALSCH – löst Service Changed Indication aus
await kb.unregister_services()

# ✅ RICHTIG – Advertising weg → Disconnect → Warten → SIGKILL
```

### 2. Shutdown-Reihenfolge immer einhalten

```
1. Connection Monitor stoppen
2. Advertising stoppen
3. 1s warten
4. Disconnect
5. 2-3s warten
6. Prozess hart beenden (SIGKILL)
```

### 3. Kein normaler Python-Exit nach BLE-Nutzung

`asyncio.run()` return, `sys.exit()`, `os._exit()` – alle lösen `dbus_fast`-Finalizer aus die `proxy_removed_cb` triggern. Nur `SIGKILL` verhindert das zuverlässig.

### 4. Bei Integration in größere Anwendungen (z.B. FastAPI/uvicorn)

Der `shutdown()`-Handler muss die gleiche Sequenz nutzen:

```python
async def shutdown(self):
    # Connection Monitor stoppen
    if self.ble_keyboard._connection_monitor_task is not None:
        self.ble_keyboard._connection_monitor_task.cancel()
        self.ble_keyboard._connection_monitor_task = None

    # Advertising stoppen
    if self.ble_keyboard.active_advertisement is not None:
        try:
            await self.ble_keyboard.active_advertisement.unregister()
        except Exception:
            pass
        self.ble_keyboard.active_advertisement = None

    await asyncio.sleep(1)
    await self.ble_keyboard.disconnect()
    await asyncio.sleep(2)
    # Danach darf der Prozess sterben
```

### 5. BlueZ-Neustart und Reboot sind sicher

Solange die Shutdown-Sequenz korrekt durchgeführt wurde, überlebt das Bonding:

- ✅ BlueZ-Neustart
- ✅ System-Reboot
- ✅ Manueller Neustart des Python-Prozesses

---

## Technischer Hintergrund

### Warum BLE HID Geräte sofort reconnecten

BLE HID Hosts (wie die Nokia AndroidTV Box) speichern die Bonding-Informationen (LTK, IRK) und versuchen **automatisch** eine Verbindung wiederherzustellen sobald sie das Peripheral-Gerät im Advertising sehen. Das ist Standard-BLE-Verhalten für HID-Geräte und der Grund warum das Advertising **vor** dem Disconnect gestoppt werden muss.

### Warum `proxy_removed_cb` passiert

Wenn ein D-Bus-Client verschwindet (egal wie – normaler Exit, `os._exit`, `SIGKILL`), erkennt der D-Bus-Daemon das über den geschlossenen Unix-Socket und sendet ein `NameOwnerChanged`-Signal. BlueZ reagiert darauf mit `proxy_removed_cb()` für alle registrierten GATT Services dieses Clients. Das ist unvermeidbar – daher muss die Nokia **vorher** getrennt sein.

### Rolle der `Service Changed Indication`

Die `Service Changed Indication` (ATT Handle Value Indication, UUID 0x2A05) ist ein BLE-Mechanismus der verbundene Clients informiert, dass sich die GATT-Datenbank geändert hat. Wenn BlueZ Services entfernt und diese Indication sendet **während ein Client verbunden ist**, führt der Client eine volle GATT Re-Discovery durch. Findet er die erwarteten HID Services nicht, trennt er die Verbindung und markiert das Bonding als fehlerhaft.

### GATT Handle-Stabilität

Bei jedem Prozess-Neustart registriert `bluez_peripheral` die GATT Services neu. BlueZ vergibt dabei **neue Handle-Werte** (z.B. 0x0049 statt vorher 0x0033). Der BLE-Client (Nokia) erkennt die Handle-Änderung über den geänderten `Database Hash` und führt eine Re-Discovery durch. Das ist normal und funktioniert – solange die Services **vorhanden** sind wenn die Re-Discovery stattfindet.

---

## Zusammenfassung

Das Kernproblem war eine **Race Condition**: Beim Prozess-Exit werden GATT Services entfernt, aber die Nokia ist noch verbunden und bekommt eine `Service Changed Indication`. Sie macht eine Re-Discovery auf einem leeren GATT Server, findet keine HID Services, und verwirft das Bonding dauerhaft.

Die Lösung: **Advertising stoppen bevor disconnected wird**, damit die Nokia nach dem Disconnect den Raspberry nicht mehr finden und keinen sofortigen Reconnect versuchen kann. Erst wenn die Nokia „aufgegeben" hat, darf der Prozess sterben und die Services können sicher entfernt werden.
