import asyncio
from bleak import BleakClient, BleakScanner

# Name deines Android TV
DEVICE_NAME = "Android TV"

# Standard GATT Service "Device Information" (oft geschützt/bonding-relevant)
MODEL_NUMBER_UUID = "00002a24-0000-1000-8000-00805f9b34fb"

async def main():
    print(f"Suche nach '{DEVICE_NAME}'...")
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name and DEVICE_NAME in d.name
    )

    if not device:
        print("Gerät nicht gefunden.")
        return

    print(f"Verbinde mit {device.address}...")
    async with BleakClient(device.address) as client:
        print(f"Verbunden: {client.is_connected}")

        try:
            # Der Versuch, eine geschützte Charakteristik zu lesen,
            # triggert oft den Bonding-Prozess (PIN-Eingabe am TV/PC).
            print("Versuche, geschützte Daten zu lesen (Trigger für Bonding)...")
            model_number = await client.read_gatt_char(MODEL_NUMBER_UUID)
            print(f"Modellnummer gelesen: {model_number.decode('utf-8')}")
            print("Bonding war erfolgreich oder bestand bereits.")
            
            # Wichtig für Bonding unter Linux (BlueZ):
            # Manchmal muss explizit 'pair' aufgerufen werden (nur Linux/BlueZ backend)
            if hasattr(client, "pair"):
                try:
                    await client.pair(protection_level=2)
                    print("Explizites Pairing/Bonding angefordert (Linux).")
                except Exception as e:
                    print(f"Pairing-Call fehlgeschlagen (evtl. schon gepairt): {e}")

        except Exception as e:
            print(f"Fehler (Könnte bedeuten, dass Bonding abgelehnt wurde): {e}")

if __name__ == "__main__":
    asyncio.run(main())
