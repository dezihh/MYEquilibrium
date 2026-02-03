import asyncio
from bleak import BleakClient, BleakScanner

ANDROID_TV_NAME = "Android TV"  # Passe ggf. an!
# ALTERNATIV: ANDROID_TV_MAC = "AA:BB:CC:DD:EE:FF"

async def main():
    print("Suche Android TV...")
    devices = await BleakScanner.discover()
    target = next((d for d in devices if ANDROID_TV_NAME in d.name), None)
    if not target:
        print("Android TV nicht gefunden.")
        return

    print(f"Verbinde zu {target.address} ...")
    async with BleakClient(target.address) as client:
        if client.is_connected:
            print("Verbunden!")
            # Viele Android TV unterstützen Pairing direkt nach Verbindung
            # Pairing (Bonding) ist meist handled vom OS/Adapter
            # Manche Adapter popupen ein System-Pairing-Dialog
            # bleak Bibliothek unterstützt kein explizites Pairing API
            print("Pairing/Bonding sollte jetzt automatisch ausgelöst werden!")
        else:
            print("Verbindung fehlgeschlagen.")

asyncio.run(main())
