import asyncio
from bluez_peripheral.gatt.service import Service
from bluez_peripheral.gatt.characteristic import characteristic, CharacteristicFlags as CharFlags
from bluez_peripheral.util import *
from bluez_peripheral.advert import Advertisement
from bluez_peripheral.agent import NoInputNoOutputAgent

# 1. Definiere einen Dummy-Service (damit Android etwas sieht)
class MySmartService(Service):
    def __init__(self):
        # UUIDs müssen unique sein (hier generisch)
        super().__init__("12345678-1234-5678-1234-56789abcdef0", True)

    @characteristic("12345678-1234-5678-1234-56789abcdef1", CharFlags.READ | CharFlags.WRITE)
    def my_char(self, options):
        # Das Lesen dieser Charakteristik ist für Android möglich
        return bytes("Hallo Android TV", "utf-8")

async def main():
    # Bus initialisieren
    bus = await get_message_bus()

    # 2. Service erstellen
    service = MySmartService()
    await service.register(bus)

    # 3. Agent registrieren (WICHTIG für Bonding!)
    # "NoInputNoOutput" = "Just Works" Pairing (meist ein Bestätigungsdialog am TV)
    # Alternativ: DisplayOnlyAgent (zeigt PIN im Terminal an)
    agent = NoInputNoOutputAgent(capability="NoInputNoOutput")
    await agent.register(bus)

    # 4. Advertising starten
    advert = Advertisement(
        "Python Device",  # Name, der am TV erscheint
        [service.uuid],   # Service UUID ankündigen
        0,                # Erscheinungsbild (0 = unbekannt)
        0
    )
    await advert.register(bus)

    print("Werbung gestartet. Gehe am Android TV zu: Einstellungen -> Fernbedienungen & Zubehör -> Zubehör hinzufügen")
    print("Drücke STRG+C zum Beenden.")

    # Loop halten
    await asyncio.get_event_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())
