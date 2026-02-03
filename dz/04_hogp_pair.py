import asyncio
from bluez_peripheral.util import get_message_bus
from bluez_peripheral.advert import Advertisement
from bluez_peripheral.gatt.service import Service
from bluez_peripheral.gatt.characteristic import characteristic, CharacteristicFlags as CharFlags

# Hinweis: bluez-peripheral 0.1.7 hat keinen Agent-Wrapper.
# Agent lassen wir vorerst über bluetoothctl laufen (agent on + default-agent),
# damit Pairing/Bonding klappt. Das ist der kleinste stabile Schritt.

DEVICE_NAME = "EquilibriumRemote1"

# HID Report Map: Standard Keyboard (8-byte Input Report)
REPORT_MAP = bytes([
    0x05, 0x01,       # Usage Page (Generic Desktop)
    0x09, 0x06,       # Usage (Keyboard)
    0xA1, 0x01,       # Collection (Application)
    0x05, 0x07,       #   Usage Page (Key Codes)
    0x19, 0xE0,       #   Usage Minimum (224)
    0x29, 0xE7,       #   Usage Maximum (231)
    0x15, 0x00,       #   Logical Minimum (0)
    0x25, 0x01,       #   Logical Maximum (1)
    0x75, 0x01,       #   Report Size (1)
    0x95, 0x08,       #   Report Count (8)
    0x81, 0x02,       #   Input (Data, Variable, Absolute) Modifier byte
    0x95, 0x01,       #   Report Count (1)
    0x75, 0x08,       #   Report Size (8)
    0x81, 0x03,       #   Input (Const, Variable, Absolute) Reserved byte
    0x95, 0x06,       #   Report Count (6)
    0x75, 0x08,       #   Report Size (8)
    0x15, 0x00,       #   Logical Minimum (0)
    0x25, 0x65,       #   Logical Maximum (101)
    0x19, 0x00,       #   Usage Minimum (0)
    0x29, 0x65,       #   Usage Maximum (101)
    0x81, 0x00,       #   Input (Data, Array)
    0xC0              # End Collection
])

class HIDService(Service):
    def __init__(self):
        super().__init__("1812", True)  # HID Service (16-bit UUID)

    @characteristic("2A4A", CharFlags.READ)
    def hid_information(self, options):
        # bcdHID=0x0111, country=0, flags=0x03 (remote wake + normally connectable)
        return bytes([0x11, 0x01, 0x00, 0x03])

    @characteristic("2A4B", CharFlags.READ)
    def report_map(self, options):
        return REPORT_MAP

    @characteristic("2A4E", CharFlags.READ | CharFlags.WRITE_WITHOUT_RESPONSE)
    def protocol_mode(self, options):
        # 1 = Report Protocol
        return bytes([0x01])

    @characteristic("2A4C", CharFlags.WRITE_WITHOUT_RESPONSE)
    def control_point(self, options):
        # Host can suspend/resume; we ignore.
        return

    @characteristic("2A4D", CharFlags.READ | CharFlags.NOTIFY)
    def input_report(self, options):
        # 8 bytes: modifiers, reserved, 6 keycodes. Default all 0.
        return bytes(8)

async def main():
    bus = await get_message_bus()

    hid = HIDService()
    await hid.register(bus)

    advert = Advertisement(
        local_name=DEVICE_NAME,
        service_uuids=["1812"],
        appearance=0x03C1,  # Keyboard appearance
        timeout=0
    )
    await advert.register(bus)

    print("OK: HOGP (BLE HID) GATT + Advertising läuft.")
    print("Wichtig: In einem zweiten Terminal bluetoothctl laufen lassen:")
    print("  bluetoothctl")
    print("  power on; agent on; default-agent; pairable on; discoverable on")
    print("Dann auf der Nokia 8010 per BLE-App verbinden und 'Pair/Bond' auslösen.")
    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())
