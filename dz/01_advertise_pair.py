import asyncio
from bluez_peripheral.util import get_message_bus
from bluez_peripheral.advert import Advertisement
from bluez_peripheral.agent import NoInputNoOutputAgent
from bluez_peripheral.gatt.service import Service
from bluez_peripheral.gatt.characteristic import characteristic, CharacteristicFlags as CharFlags

DEVICE_NAME = "EquilibriumRemote1"

class DummyService(Service):
    def __init__(self):
        super().__init__("12345678-1234-5678-1234-56789abcdef0", True)

    @characteristic("12345678-1234-5678-1234-56789abcdef1", CharFlags.READ)
    def ping(self, options):
        return b"ping"

async def main():
    bus = await get_message_bus()

    # Agent: "Just Works" (Android TV bestätigt i.d.R. nur)
    agent = NoInputNoOutputAgent(capability="NoInputNoOutput")
    await agent.register(bus)

    service = DummyService()
    await service.register(bus)

    advert = Advertisement(
        local_name=DEVICE_NAME,
        service_uuids=[service.uuid],
        appearance=0,
        timeout=0
    )
    await advert.register(bus)

    print("OK: Advertising + Agent aktiv.")
    print("Android TV: Einstellungen -> Fernbedienungen & Zubehör -> Zubehör hinzufügen")
    print("Warte... (STRG+C zum Beenden)")
    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())
