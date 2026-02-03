import asyncio
from dbus_next.aio import MessageBus
from dbus_next.constants import BusType
from dbus_next import Variant

BLUEZ = "org.bluez"
RC212_MAC = "F4:22:7A:54:B4:9A"

async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    # Find device
    om_intro = await bus.introspect(BLUEZ, "/")
    om_obj = bus.get_proxy_object(BLUEZ, "/", om_intro)
    om = om_obj.get_interface("org.freedesktop.DBus.ObjectManager")
    objects = await om.call_get_managed_objects()

    dev_path = None
    for path, ifaces in objects.items():
        if "org.bluez.Device1" in ifaces:
            addr = ifaces["org.bluez.Device1"].get("Address", Variant("s", "")).value
            if addr.upper() == RC212_MAC.upper():
                dev_path = path
                break

    if not dev_path:
        print(f"Device {RC212_MAC} nicht gefunden. Pairing ok?")
        return

    print(f"Device: {dev_path}")

    try:
        intro = await bus.introspect(BLUEZ, dev_path)
        obj = bus.get_proxy_object(BLUEZ, dev_path, intro)
        dev = obj.get_interface("org.bluez.Device1")

        print("Connect ...")
        await dev.call_connect()
        print("Connected. Warte 3s ...")
        await asyncio.sleep(3)

        # Re-scan objects for GATT
        objects = await om.call_get_managed_objects()
        for path, ifaces in objects.items():
            if dev_path in path and "org.bluez.GattCharacteristic1" in ifaces:
                char = ifaces["org.bluez.GattCharacteristic1"]
                uuid = char.get("UUID", Variant("s", "?")).value
                flags = char.get("Flags", Variant("as", [])).value
                print(f"  Char: {uuid} flags={flags}")

                if uuid == "00002a4b-0000-1000-8000-00805f9b34fb":  # Report Map
                    char_intro = await bus.introspect(BLUEZ, path)
                    char_obj = bus.get_proxy_object(BLUEZ, path, char_intro)
                    char_iface = char_obj.get_interface("org.bluez.GattCharacteristic1")
                    report_map = await char_iface.call_read_value({})
                    print(f"\n=== Report Map ===")
                    print(bytes(report_map).hex())

        await dev.call_disconnect()
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
