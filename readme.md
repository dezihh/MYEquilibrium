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

## API-Übersicht (FastAPI)

OpenAPI/Swagger ist verfügbar unter `/docs` und `/redoc`, sobald die App läuft.

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

### BluetoothManager (NICHT AKTIV)

[BluetoothManager/](BluetoothManager/) ist eine **umfassendere Bluetooth-Architektur** mit:
- Multi-Profile Support (HID-Remote, Keyboard, etc.)
- Secure Pairing Agent
- GattManager Integration

**Status:** Vollständig implementiert, aber **NICHT in RemoteController integriert**. Aktuell wird nur `BleKeyboard` genutzt.

**Use-Case für später:** Falls man mehrere BLE-Profile gleichzeitig unterstützen möchte (z.B. Keyboard UND Audio-Receiver), könnte man RemoteController auf BluetoothManager migrieren.

Beispiel-Integration: [Api/routers/bluetooth_v2_example.py](Api/routers/bluetooth_v2_example.py)

### Alte Dateien
- `BluetoothManager/BluetoothManager.py.04.02.26` – Backup (löschen?)
- `BleKeyboard/BleKeyboard.py.sic` – Fragment (löschen?)
- `Api/routers/bluetooth_v2_example.py` – Template für künftige Multi-Profile-Architektur

## Pictures

### The Hub
![Image of the hub itself](Extras/Images/hub-small.png)

### The App
![UI Screenshots](Extras/Images/UI-Screenshots.png)

## Troubleshooting

If an error occurs, you should check the output from Equilibrium. If you have daemonized it, you can do so via `journalctl`.
In some cases, you may want to use the `--verbose` or `--debug` flags to get more verbose logs, though I don't recommend using either for longer times due to the number of log entries they create.