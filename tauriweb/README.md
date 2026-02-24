# Equilibrium – Smart Home Control Panel

Equilibrium ist eine Smart-Home-Steuerungsanwendung, die als **Tauri v2 Desktop-App** und als **Web-Frontend** für einen FastAPI-Hub betrieben werden kann. Die App ermöglicht die Steuerung von Geräten über IR-Befehle, die Verwaltung von Szenen und Makros sowie die Bluetooth-Geräteverwaltung.

## Funktionen

- **Szenen**: Erstelle und verwalte Szenen, die mehrere Geräte und Makros zusammenfassen
- **Geräte**: Verwalte IR-fähige Geräte (Display, Verstärker, Player, Sonstige)
- **Befehle**: Definiere IR-Befehle pro Gerät und nehme neue Signale auf
- **Makros**: Erstelle Befehlssequenzen mit konfigurierbaren Verzögerungen
- **Bluetooth**: Verwalte BLE-Geräte (Pairing, Verbindung, Trennung)
- **Bilder**: Lade Szenenbilder hoch und verwalte sie

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

Öffne `http://localhost:1420` im Browser. Im Web-Modus verbindet sich die App automatisch mit dem Server, der die Seite ausliefert.

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

Der Build-Output liegt in `dist/`. Diese Dateien können direkt in das `/web`-Verzeichnis des FastAPI-Servers kopiert werden:

```bash
cp -r dist/* ../web/
```

Der FastAPI-Server liefert dann die Web-App unter seiner Root-URL aus. Die App verbindet sich automatisch mit dem Server (`window.location.origin`).

### Tauri Desktop-Build

```bash
npm run tauri build
```

Das fertige Installationspaket befindet sich unter `src-tauri/target/release/bundle/`.

## Deployment als Web-Frontend

1. `npm run build` ausführen
2. Den Inhalt von `dist/` in das `/web`-Verzeichnis des FastAPI-Servers kopieren
3. Der FastAPI-Server muss statische Dateien aus `/web` ausliefern (z. B. mit `StaticFiles`)
4. Die App ist dann über die Server-URL erreichbar, z. B. `http://192.168.1.100:8000`

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
│   │   ├── DeviceCard.tsx      # Geräte-Karte
│   │   ├── Layout.tsx          # App-Layout mit App-Bar
│   │   └── SceneCard.tsx       # Szenen-Karte
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
