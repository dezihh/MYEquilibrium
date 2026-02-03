import asyncio
from dbus_next.aio import MessageBus
from dbus_next.constants import BusType

BLUEZ = "org.bluez"
DEVICE_MAC = "22:22:09:C3:08:3D"
HCI = "hci0"

async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    dev_path = f"/org/bluez/{HCI}/dev_{DEVICE_MAC.replace(':', '_')}"

    intro = await bus.introspect(BLUEZ, dev_path)
    obj = bus.get_proxy_object(BLUEZ, dev_path, intro)
    dev = obj.get_interface("org.bluez.Device1")

    print("Connect() ...")
    await dev.call_connect()
    print("Connected (call_connect returned).")

    await asyncio.sleep(5)

    print("Disconnect() ...")
    await dev.call_disconnect()
    print("Disconnected.")

if __name__ == "__main__":
    asyncio.run(main())
