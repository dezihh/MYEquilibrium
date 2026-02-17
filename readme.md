# Equilibrium

Open source network attached universal remote; aiming to become a drop-in replacement for Logitech's discontinued Harmony Hub.

**This software is in a very early stage of development and every update should be considered breaking!**

**Don't use this if you're looking for a stable piece of equipment that you can rely on!**

The setup currently requires at least some basic understanding of the Linux terminal, python and GPIO hardware.

If you run into any issues, check the [Troubleshooting](#troubleshooting) section. If you think you found a bug, please create an issue here on GitHub.

## Features

- [x] Record and send infrared commands
- [x] Emulate a bluetooth keyboard to control devices like the Apple TV (WIP)
- [x] Configurable scenes (activities) with user-definable start and stop macros
- [x] Track device state to make scene switches only execute necessary commands (WIP)
- [x] iOS app to control and manage the hub (Beta available in [Testflight](https://testflight.apple.com/join/dyzEZYMs), [source code](https://github.com/LeoKlaus/Equilibrium-iOS))
- [x] Works with the original Harmony companion remote
- [x] Frontend for Android/Web (Beta available [here](https://github.com/LeoKlaus/Equilibrium-Flutter))

### Todo
- [ ] Expand support for physical remotes
- [ ] Home Assistant integration
- [ ] Philips Hue integration?
- [ ] Amazon Alexa integration?
- [ ] Improve set up guide
- [ ] Add some form of IR database

## Setup and usage

I've created a [Wiki in this repo](https://github.com/LeoKlaus/Equilibrium/wiki) to cover the basic setup and usage of Equilibrium.

## Projektstruktur (Überblick)

Die Funktionen sind sauber nach Domänen getrennt. Die Kernlogik liegt in eigenen Modulen, die API ist nur eine dünne Schicht darüber.

**Core-Module**
- [RemoteController/RemoteController.py](RemoteController/RemoteController.py) – zentrale Orchestrierung (IR, RF, BLE, HA, Queue, Status)
- [BleKeyboard/](BleKeyboard/) – BLE/HID-Keyboard Peripheral, Advertising, Pairing/Trust, Keycodes
- [IrManager/](IrManager/) – IR Senden/Empfangen
- [RfManager/](RfManager/) – RF Listener/Sender
- [HaManager/](HaManager/) – Home-Assistant Integration (optional)
- [DbManager/](DbManager/) – SQLModel/SQLite Datenbank + Session
- [ZeroconfManager/](ZeroconfManager/) – Bonjour/Zeroconf Service-Ankündigung
- [config/](config/) – Konfigurationsdateien (Keymaps, RF-Adressen, HA-Creds)

**API & Laufzeit**
- [Api/app.py](Api/app.py) – FastAPI App, Router-Registrierung
- [Api/lifespan.py](Api/lifespan.py) – Startup/Shutdown (DB init, Controller, Zeroconf)
- [main.py](main.py) – Uvicorn Start mit Flags

**UI (späterer Fokus)**
- [web/](web/) – Flutter Web UI (aktuell nicht im Fokus)
- [gui/](gui/) – React/Vite UI (build output unter `gui/dist`, wird optional via `/gui` ausgeliefert)

## API-Übersicht (FastAPI)

OpenAPI/Swagger ist verfügbar unter `/docs` und `/redoc`, sobald die App läuft.

### Web UIs (parallel)

Die Flutter-Web-UI wird unter `/ui` ausgeliefert. Die neue React/Vite-UI kann
parallel unter `/gui` ausgeliefert werden, wenn zuvor der Build ausgefuehrt wurde:

``` bash
cd gui
npm install
npm run build
```

Anschliessend startet `python main.py` beide UIs parallel (siehe `/ui` und `/gui`).

### Bluetooth
Router: [Api/routers/bluetooth.py](Api/routers/bluetooth.py)
- GET `/bluetooth/devices` – gekoppelte/verbundene BLE-Geräte
- POST `/bluetooth/start_advertisement` – Advertising starten (Discovery)
- POST `/bluetooth/start_pairing` – Pairing-Trigger für spezielle Geräte
- POST `/bluetooth/connect/{mac}` – Reconnect-Flow
- POST `/bluetooth/disconnect` – BLE trennen
- DELETE `/bluetooth/remove/{mac}` – Gerät aus BlueZ entfernen (neuer Endpunkt)

### Devices
Router: [Api/routers/devices.py](Api/routers/devices.py)
- GET `/devices/` – Geräte-Liste
- GET `/devices/{id}` – Gerät lesen
- POST `/devices/` – Gerät erstellen
- PATCH `/devices/{id}` – Gerät aktualisieren
- DELETE `/devices/{id}` – Gerät löschen

### Commands
Router: [Api/routers/commands.py](Api/routers/commands.py)
- GET `/commands/` – Befehle-Liste
- GET `/commands/{id}` – Befehl lesen
- POST `/commands/` – Befehl erstellen
- POST `/commands/{id}/send` – Befehl senden
- DELETE `/commands/{id}` – Befehl löschen

### Scenes
Router: [Api/routers/scenes.py](Api/routers/scenes.py)
- GET `/scenes/` – Szenen-Liste
- POST `/scenes/` – Szene erstellen
- PATCH `/scenes/{id}` – Szene aktualisieren
- DELETE `/scenes/{id}` – Szene löschen (weiter unten im File)

### Macros
Router: [Api/routers/macros.py](Api/routers/macros.py)
- GET `/macros/` – Macros-Liste
- GET `/macros/{id}` – Macro lesen
- POST `/macros/` – Macro erstellen
- PATCH `/macros/{id}` – Macro aktualisieren
- DELETE `/macros/{id}` – Macro löschen
- POST `/macros/{id}/execute` – Macro ausführen

### Images
Router: [Api/routers/images.py](Api/routers/images.py)
- GET `/images/` – Bilder-Liste
- GET `/images/{id}` – Bild laden
- POST `/images/` – Bild hochladen
- DELETE `/images/{id}` – Bild löschen

### System
Router: [Api/routers/system.py](Api/routers/system.py)
- GET `/system/status` – Statusreport

### WebSockets
Router: [Api/routers/websockets.py](Api/routers/websockets.py)
- WS `/ws/bt_pairing` – BLE Pairing/Advertise/Connect/Devices
- WS `/ws/commands` – IR Aufnahme (Record)
- WS `/ws/status` – Status-Updates (Push)
- WS `/ws/keyboard` – Platzhalter (TODO)

## Core ↔ API Mapping

**Wie die API-Router die Core-Module nutzen:**

| Router | Nutzt Core | Wichtige Funktionen |
|--------|-----------|-------------------|
| [bluetooth.py](Api/routers/bluetooth.py) | BleKeyboard | get_ble_devices(), start_ble_advertisement(), ble_connect(), ble_disconnect(), ble_remove() |
| [devices.py](Api/routers/devices.py) | DbManager (Session) | CRUD Geräte-DB |
| [commands.py](Api/routers/commands.py) | DbManager + RemoteController | CRUD Commands, send_command() |
| [scenes.py](Api/routers/scenes.py) | DbManager | CRUD Scenes, Macro-Bindung |
| [macros.py](Api/routers/macros.py) | DbManager + RemoteController | CRUD Macros, execute_macro() |
| [images.py](Api/routers/images.py) | DbManager | CRUD Images, Datei-Upload |
| [system.py](Api/routers/system.py) | RemoteController | get_current_status() |
| [websockets.py](Api/routers/websockets.py) | RemoteController + BleKeyboard | start_ble_advertisement(), ble_connect(), record_ir_command(), status-broadcast |

**Zentrale Orchestrierung:** [RemoteController/RemoteController.py](RemoteController/RemoteController.py)
- Erzeugt/verwaltet: BleKeyboard, IrManager, RfManager, HaManager, AsyncQueueManager
- Exponiert API-Funktionen für alle Router

## Alte/Alternative Komponenten

Keine aktuell (BluetoothManager wurde entfernt).

## Core-Module Detailliert

### IrManager – Infrarot Senden & Empfangen

**Datei:** [IrManager/IrManager.py](IrManager/IrManager.py)

**Funktionalität:**
- **Senden:** IR-Befehle per GPIO (Pin 18) an Geräte wie TV, AV-Receiver
- **Empfangen:** IR-Befehle vom Benutzer per IR-Sensor (GPIO Pin 17) aufnehmen/aufzeichnen

**Hardware:**
- IR-TX: GPIO 18 (Transmitter)
- IR-RX: GPIO 17 (Receiver/Sensor)
- Nutzt `pigpio` für präzise GPIO-Timing
- Trägerfrequenz: 38 kHz

**Wichtige Methoden:**
- `send_command(code: [int])` – Sendet einen IR-Code (Mark/Space Array)
- `send_and_repeat(code: [int])` – Sendet IR-Code wiederholt (0,25s Intervall)
- `record_command(name: str, websocket)` – Zeichnet IR-Code vom Benutzer auf
  - Erfordert 2x Drücken derselben Taste für Validierung
  - Normalisiert Timing-Variationen (±20%)

**Code-Format:**
IR-Codes werden als integer-Arrays gespeichert:
```
[mark1, space1, mark2, space2, ...]  # Mikrosekunden
```
Beispiel: `[9024, 4512, 564, ...]`

**Workflow Aufnahme:**
1. User drückt "Record" in UI
2. IrManager prompt: "Press the IR button"
3. User drückt Taste auf IR-Fernbedienung
4. IrManager speichert Code
5. IrManager prompt: "Repeat the same button"
6. User drückt Taste nochmal → Validierung (±20% Toleranz)
7. Code gespeichert in DB

### RfManager – RF (2,4 GHz) Listener & Decoder

**Datei:** [RfManager/RfManager.py](RfManager/RfManager.py)

**Funktionalität:**
- **Listener:** Empfängt Befehle von RF-Fernbedienungen (Harmony-kompatibel)
- **Decoder:** Erkennt Tasten anhand von RF-Payloads
- **Callback:** Löst Aktionen aus (Button press, repeat, release, sleep)

**Hardware:**
- Radio: nRF24L01+ (SPI Bus 0)
- CE Pin: 25
- CSN Pin: 0 (SPI Chip Select)
- Datenrate: 2 Mbps
- Dynamische Payload-Größe

**Konfiguration:**
- RF-Adressen: `config/rf_addresses.json` (2 Empfänger-Adressen)
- Button-Keymap: `config/remote_keymap.json` (RF-Command → Button-Name)

**Wichtige Methoden:**
- `start_listener(addresses: [bytes])` – Startet RF-Listener-Thread
- `stop_listener()` – Stoppt Listener
- `set_callback(callback)` – Registriert Button-Press-Handler
- `set_repeat_callback(callback)` – Handler für Wiederholungen (0x400028)
- `set_release_callback(callback)` – Handler für Button-Release (0x4f0004)

**RF-Payload Dekodierung:**
Bekannte RF-Commands:
- `0x40044c` – Remote Idle (ignoriert)
- `0x4f0300` – Remote Going to Sleep
- `0x4f0700` – Remote Woke Up
- `0x400028` – Repeat (letzte Taste nochmal)
- `0x4f0004` – All Buttons Released
- `0xc10000/0xc30000` – Released Button
- Alles andere: Nachschlag in `remote_keymap.json`

**Setup Remote-Adressen:**
Script [RfManager/getRemoteAddress.py](RfManager/getRemoteAddress.py) findet RF-Adresse neuer Remotes:
```bash
python getRemoteAddress.py
# Output: RF24 address as hex (z.B. 75a5dc0abb)
```

**Integration in RemoteController:**
- IrManager & RfManager werden in `RemoteController.__init__()` erzeugt
- RfManager-Callbacks sind registriert → auslösende Commands
- IR-Recording via WebSocket `/ws/commands`

## Pictures

### The Hub
![Image of the hub itself](Extras/Images/hub-small.png)

### The App
![UI Screenshots](Extras/Images/UI-Screenshots.png)

## Troubleshooting

If an error occurs, you should check the output from Equilibrium. If you have daemonized it, you can do so via `journalctl`.
In some cases, you may want to use the `--verbose` or `--debug` flags to get more verbose logs, though I don't recommend using either for longer times due to the number of log entries they create.