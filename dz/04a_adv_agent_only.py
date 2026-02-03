import asyncio
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method, dbus_property
from dbus_next import Variant
from dbus_next.constants import PropertyAccess, BusType

BLUEZ = "org.bluez"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
PROPS_IFACE = "org.freedesktop.DBus.Properties"
ADAPTER_IFACE = "org.bluez.Adapter1"
AGENT_MGR_IFACE = "org.bluez.AgentManager1"
ADV_MGR_IFACE = "org.bluez.LEAdvertisingManager1"

DEVICE_NAME = "EquilibriumRemote1"

def find_adapter(objects):
    for path, ifaces in objects.items():
        if ADAPTER_IFACE in ifaces:
            return path
    raise RuntimeError("Kein org.bluez.Adapter1 gefunden (BlueZ/Adapter Problem)")

class Agent(ServiceInterface):
    def __init__(self):
        super().__init__("org.bluez.Agent1")

    @method()
    def Release(self):
        print("[agent] Release")

    @method()
    def RequestConfirmation(self, device: "o", passkey: "u"):
        print(f"[agent] RequestConfirmation {device} passkey={passkey:06d} -> OK")

    @method()
    def RequestAuthorization(self, device: "o"):
        print(f"[agent] RequestAuthorization {device} -> OK")

    @method()
    def AuthorizeService(self, device: "o", uuid: "s"):
        print(f"[agent] AuthorizeService {device} uuid={uuid} -> OK")

    @method()
    def Cancel(self):
        print("[agent] Cancel")

class Advertisement(ServiceInterface):
    def __init__(self):
        super().__init__("org.bluez.LEAdvertisement1")

    @dbus_property(access=PropertyAccess.READ)
    def Type(self) -> "s":
        return "peripheral"

    @dbus_property(access=PropertyAccess.READ)
    def LocalName(self) -> "s":
        return DEVICE_NAME

    @dbus_property(access=PropertyAccess.READ)
    def ServiceUUIDs(self) -> "as":
        # HID Service UUID (HOGP)
        return ["1812"]

    @dbus_property(access=PropertyAccess.READ)
    def Appearance(self) -> "q":
        # Keyboard appearance
        return 0x03C1

    @method()
    def Release(self):
        print("[adv] Release")

async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    # Adapter finden
    intro = await bus.introspect(BLUEZ, "/")
    root = bus.get_proxy_object(BLUEZ, "/", intro)
    om = root.get_interface(DBUS_OM_IFACE)
    objects = await om.call_get_managed_objects()
    adapter_path = find_adapter(objects)
    print("Adapter:", adapter_path)

    adap_intro = await bus.introspect(BLUEZ, adapter_path)
    adap_obj = bus.get_proxy_object(BLUEZ, adapter_path, adap_intro)
    props = adap_obj.get_interface(PROPS_IFACE)

    # Adapter Einstellungen
    await props.call_set(ADAPTER_IFACE, "Powered", Variant("b", True))
    await props.call_set(ADAPTER_IFACE, "Discoverable", Variant("b", True))
    await props.call_set(ADAPTER_IFACE, "Pairable", Variant("b", True))
    await props.call_set(ADAPTER_IFACE, "Alias", Variant("s", DEVICE_NAME))

    # Agent registrieren
    agent_path = "/com/example/agent"
    bus.export(agent_path, Agent())

    mgr_intro = await bus.introspect(BLUEZ, "/org/bluez")
    mgr_obj = bus.get_proxy_object(BLUEZ, "/org/bluez", mgr_intro)
    agent_mgr = mgr_obj.get_interface(AGENT_MGR_IFACE)

    await agent_mgr.call_register_agent(agent_path, "NoInputNoOutput")
    await agent_mgr.call_request_default_agent(agent_path)
    print("OK: Agent aktiv (NoInputNoOutput)")

    # Advertising registrieren
    adv_path = "/com/example/advertisement"
    bus.export(adv_path, Advertisement())

    adv_mgr = adap_obj.get_interface(ADV_MGR_IFACE)
    await adv_mgr.call_register_advertisement(adv_path, {})
    print("OK: Advertising aktiv (HID UUID 1812, Keyboard appearance)")

    print("Jetzt auf der Nokia 8010 mit einer BLE-App scannen/verbinden (z.B. nRF Connect).")
    print("STRG+C zum Beenden")
    try:
        await asyncio.get_running_loop().create_future()
    finally:
        try:
            await adv_mgr.call_unregister_advertisement(adv_path)
        except Exception:
            pass
        try:
            await agent_mgr.call_unregister_agent(agent_path)
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(main())
