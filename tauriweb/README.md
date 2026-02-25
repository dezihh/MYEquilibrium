# Equilibrium – Smart Home Control Panel

Equilibrium ist eine Smart-Home-Steuerungsanwendung, die als **Tauri v2 Desktop-App** und als **Web-Frontend** für einen FastAPI-Hub betrieben werden kann. Die App ermöglicht die Steuerung von Geräten über IR-Befehle, die Verwaltung von Szenen und Makros sowie die Bluetooth-Geräteverwaltung.

> Stand: Diese Doku beschreibt den aktuellen Migrationsstand zur Flutter-Version inkl. Integrations-Features und Build-Ausgabe direkt in `../web`.

## Funktionen

- **Szenen**: Erstelle und verwalte Szenen, die mehrere Geräte und Makros zusammenfassen
- **Geräte**: Verwalte Geräte inkl. Typ `integration`, Hersteller, Modell und Bluetooth-Adresse
- **Befehle**: Definiere Befehle vom Typ **IR**, **Bluetooth**, **Network** oder **Integration**
- **Makros**: Erstelle Befehlssequenzen über `command_ids` + `delays`
- **Bluetooth**: Verwalte BLE-Geräte (Pairing, Verbindung, Trennung)
- **Bilder**: Lade Szenenbilder hoch und verwalte sie
- **Integrationen**: Eigene Integrationsseite mit Ausführen/Löschen/Erstellen von Integrationsbefehlen
- **Common Controls**: Fernbedienungs-UI (Navigation, Volume, Channel, Transport, Input, Colored Buttons, Integration)
- **Home Assistant**: Entity-Auswahl, Actions `toggle_light`, `turn_on`, `turn_off`, `brightness_up`, `brightness_down` und `call_service`

## Voraussetzungen

- **Node.js** 18+
- **npm** 9+
- **Rust / Cargo** (für Tauri Desktop-Build)
- FastAPI-Hub läuft auf dem lokalen Netzwerk (z. B. `http://192.168.1.100:8000`)

## Installation

```bash
cd tauriweb
npm install
```

## Entwicklung

### Web-Entwicklung (Browser)

```bash
npm run dev
```

Öffne `http://localhost:1420/ui/` im Browser.

Für lokale API-Entwicklung wird empfohlen:

```bash
# tauriweb/.env.local
VITE_API_BASE=http://localhost:8000
```

Dann laufen Frontend (`:1420`) und API (`:8000`) sauber getrennt.

### Tauri Desktop-Entwicklung

```bash
npm run tauri dev
```

Im Tauri-Modus erscheint beim ersten Start ein Verbindungsdialog, in dem die Hub-URL eingegeben werden kann. Die URL wird im `localStorage` gespeichert.

## Build

### Web-Build (für FastAPI-Server)

```bash
npm run build
```

Der Build-Output wird direkt nach `../web` geschrieben (über `vite.config.ts` mit `outDir: '../web'`).

Die App ist auf den Pfad `/ui/` ausgelegt (`base: '/ui/'`) und wird vom FastAPI-Server typischerweise per `StaticFiles(directory='web', html=True)` unter `/ui` ausgeliefert.

### Tauri Desktop-Build

```bash
npm run tauri build
```

Das fertige Installationspaket befindet sich unter `src-tauri/target/release/bundle/`.

## Deployment als Web-Frontend

1. `npm run build` in `tauriweb/` ausführen
2. Sicherstellen, dass FastAPI `/ui` auf `web/` mountet
3. App öffnen unter `http://<hub>:8000/ui/`

Hinweise:
- Für Browser-Dev mit separatem Host/Port muss CORS im Backend aktiv sein (z. B. `http://localhost:1420`).
- `BrowserRouter` nutzt `basename={import.meta.env.BASE_URL}` für korrektes Routing unter `/ui/`.
- **SPA Deep-Links**: Der FastAPI-Server nutzt `SPAStaticFiles` als Static-Mount, der bei 404 auf `index.html` zurückfällt. Dadurch funktionieren Browser-Reloads auf Unterseiten wie `/ui/scenes` ohne `Not Found`-Fehler.

## Flutter-Frontend (`/gui/`)

Neben der React-App wird die Flutter-Webapp (Build-Output in `../www`) unter `/gui/` ausgeliefert.

- Erreichbar unter `http://<hub>:8000/gui/`
- Der FastAPI-Server setzt für alle `/gui/*`-Antworten die Header `Cross-Origin-Opener-Policy: same-origin` und `Cross-Origin-Embedder-Policy: require-corp`, die der Flutter-WASM-Renderer (skwasm) für `SharedArrayBuffer` benötigt.
- `www/index.html` muss `<base href="/gui/">` gesetzt haben (nicht `/ui/`).

## Schnellzugriff-Menü ("Mehr")

In der unteren Navigationsleiste befindet sich ganz rechts ein **3-Punkte-Button** (`⋮`) mit einem Aufklapp-Menü:

| Eintrag | Ziel | Verhalten |
|---------|------|-----------|
| RemoteAdmin | `/scenes` | interner React-Router-Link |
| RemoteControl | `/scenes` | interner React-Router-Link (zukünftig eigene Ansicht) |
| Flutter | `/gui/` | neuer Tab |
| REST-Interface | `/docs` | neuer Tab |
| ReDoc | `/redoc` | neuer Tab |

Das Menü schließt sich automatisch bei Klick außerhalb.

## API-Endpunkte (FastAPI-Hub)

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/info` | Server-Informationen |
| GET/POST | `/devices/` | Geräte auflisten / erstellen |
| GET/PATCH/DELETE | `/devices/{id}` | Gerät abrufen / aktualisieren / löschen |
| GET/POST | `/scenes/` | Szenen auflisten / erstellen |
| PATCH/DELETE | `/scenes/{id}` | Szene aktualisieren / löschen |
| POST | `/scenes/{id}/start` | Szene starten |
| POST | `/scenes/stop` | Alle Szenen stoppen |
| GET/POST | `/commands/` | Befehle auflisten / erstellen |
| DELETE | `/commands/{id}` | Befehl löschen |
| POST | `/commands/{id}/send` | IR-Befehl senden |
| GET/POST | `/macros/` | Makros auflisten / erstellen |
| PATCH/DELETE | `/macros/{id}` | Makro aktualisieren / löschen |
| POST | `/macros/{id}/execute` | Makro ausführen |
| GET/POST | `/images/` | Bilder auflisten / hochladen |
| DELETE | `/images/{id}` | Bild löschen |
| GET | `/bluetooth/devices` | BLE-Geräte auflisten |
| POST | `/bluetooth/start_advertisement` | BLE-Werbung starten |
| POST | `/bluetooth/start_pairing` | Pairing-Modus starten |
| POST | `/bluetooth/connect/{mac}` | BLE-Gerät verbinden |
| POST | `/bluetooth/disconnect` | BLE-Verbindung trennen |
| DELETE | `/bluetooth/remove/{mac}` | BLE-Gerät entfernen |
| GET | `/system/status` | Systemstatus |
| GET | `/system/ha/lights` | Home-Assistant Licht-Entities auflisten |
| WS | `/ws/status` | Echtzeit-Statusupdates |
| WS | `/ws/bt_pairing` | Bluetooth-Pairing-Events |
| WS | `/ws/commands` | IR-Befehlsaufnahme |

## Projektstruktur

```
tauriweb/
├── src/
│   ├── api/
│   │   └── apiClient.ts        # Zentraler API-Client für alle Endpunkte
│   ├── components/
│   │   ├── BottomNav.tsx       # Untere Navigationsleiste
│   │   ├── CommonControls.tsx  # Gemeinsame Fernbedienungs-Controls
│   │   ├── DeviceCard.tsx      # Geräte-Karte
│   │   ├── Layout.tsx          # App-Layout mit App-Bar
│   │   ├── SceneCard.tsx       # Szenen-Karte
│   │   └── controls/           # Control-Gruppen inkl. IntegrationControlGroup
│   ├── context/
│   │   └── AppContext.tsx      # Globaler App-Zustand (Hub-URL, aktive Szene)
│   ├── hooks/
│   │   ├── useApi.ts           # Generischer API-Hook mit Loading/Error-State
│   │   └── useWebSocket.ts     # WebSocket-Hook
│   ├── models/
│   │   ├── bleDevice.ts        # BLE-Gerät-Interface
│   │   ├── command.ts          # Befehl-Interface
│   │   ├── device.ts           # Gerät-Interface
│   │   ├── enums.ts            # DeviceType und RemoteButton Enums
│   │   ├── image.ts            # Bild-Interface
│   │   ├── macro.ts            # Makro-Interface
│   │   ├── scene.ts            # Szene-Interface
│   │   └── statusReport.ts     # Status-Interface
│   ├── pages/
│   │   ├── BluetoothDevicesPage.tsx
│   │   ├── CommandListPage.tsx
│   │   ├── ConnectPage.tsx
│   │   ├── CreateCommandPage.tsx
│   │   ├── CreateDevicePage.tsx
│   │   ├── CreateMacroPage.tsx
│   │   ├── CreateScenePage.tsx
│   │   ├── DeviceDetailPage.tsx
│   │   ├── DevicesPage.tsx
│   │   ├── ImageListPage.tsx
│   │   ├── IntegrationsPage.tsx
│   │   ├── MacroListPage.tsx
│   │   ├── SceneDetailPage.tsx
│   │   ├── ScenesPage.tsx
│   │   └── SettingsPage.tsx
│   ├── styles/
│   │   └── globals.css         # Globale Dark-Theme CSS-Variablen und Klassen
│   ├── theme/
│   │   └── theme.ts            # Theme-Konstanten
│   ├── App.tsx                 # Routing-Konfiguration
│   ├── main.tsx                # React-Einstiegspunkt
│   └── vite-env.d.ts
├── src-tauri/
│   ├── src/
│   │   └── main.rs             # Tauri-Hauptdatei
│   ├── build.rs
│   ├── Cargo.toml
│   └── tauri.conf.json         # Tauri-Konfiguration
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

## Wichtige Datenmodelle (aktuell)

- `Scene`: `device_ids`, `start_macro_id`, `stop_macro_id`, `image_id`, `bluetooth_address`
- `Macro`: `command_ids`, `delays`
- `Command`: `type`, `command_group`, `device_id`, `host`, `method`, `body`, `bt_action`, `bt_media_action`, `integration_action`, `integration_entity`
- `Device`: `name`, `type`, `manufacturer`, `model`, `image_id`, `bluetooth_address`

## Integrations-Workflow

1. In **Einstellungen → Integrationen** wechseln
2. Über **+ Neu** einen Integrationsbefehl erstellen
3. Typ `integration` wählen, Aktion setzen (`toggle_light`, `turn_on`, `turn_off`, `brightness_up`, `brightness_down`, `call_service`)
4. Für Entity-basierte Aktionen `integration_entity` setzen (z. B. `light.ceiling_lamp`)
5. Für `call_service` statt Entity den Service im Format `domain.service` angeben (z. B. `scene.turn_on`)
6. Optional JSON-Daten setzen, z. B. `{"entity_id": "scene.evening"}`
7. Befehl kann auf der Integrationsseite und in Device/Scene-Controls direkt ausgeführt werden

## Hinweise zur HA-Anbindung

- Die Hub-Integration normalisiert die konfigurierte HA-URL automatisch auf `/api`.
- Service-Aufrufe laufen robust über direkte HA-REST-Calls (`/api/services/...`).
- Wenn Home Assistant verbunden ist, nutzt die Command-Erstellung die Entity-Liste aus `/system/ha/lights`.

## Stabilitäts-Fixes (neu)

- Szenen-Editor ist tolerant gegenüber älteren Feldnamen (`device_ids` vs. Legacy `devices`).
- Command-Senden ist gegen uninitialisierten Cache abgesichert (kein Absturz bei fehlender Keymap).
