import asyncio
from dbus_next.aio import MessageBus
from dbus_next.constants import BusType

BLUEZ = "org.bluez"
DEVICE_MAC = "22:22:09:C3:08:3D"
HCI = "hci0"

# AVRCP Target (aus deiner Services-Liste): 0000110c-0000-1000-8000-00805f9b34fb
UUID = "0000110c-0000-1000-8000-00805f9b34fb"

async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    dev_path = f"/org/bluez/{HCI}/dev_{DEVICE_MAC.replace(':', '_')}"
    intro = await bus.introspect(BLUEZ, dev_path)
    obj = bus.get_proxy_object(BLUEZ, dev_path, intro)
    dev = obj.get_interface("org.bluez.Device1")

    print("ConnectProfile() ...", UUID)
    await dev.call_connect_profile(UUID)
    print("Connected profile.")

    await asyncio.sleep(5)

    print("Disconnect() ...")
    await dev.call_disconnect()
    print("Disconnected.")

if __name__ == "__main__":
    asyncio.run(main())
