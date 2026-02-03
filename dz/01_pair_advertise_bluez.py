import asyncio
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method, dbus_property
from dbus_next import Variant
from dbus_next.constants import PropertyAccess, BusType

BLUEZ = "org.bluez"
AGENT_MGR_PATH = "/org/bluez"
ADVERT_MGR_IFACE = "org.bluez.LEAdvertisingManager1"
AGENT_MGR_IFACE = "org.bluez.AgentManager1"
ADAPTER_IFACE = "org.bluez.Adapter1"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"

DEVICE_NAME = "EquilibriumRemote1"
ADAPTER_PATH = None  # None => auto (erster Adapter)

def _find_adapter_path(objects):
    for path, ifaces in objects.items():
        if ADAPTER_IFACE in ifaces:
            return path
    raise RuntimeError("Kein Bluetooth Adapter (org.bluez.Adapter1) gefunden")

class Agent(ServiceInterface):
    def __init__(self, path="/com/example/agent"):
        super().__init__("org.bluez.Agent1")
        self._path = path

    @method()
    def Release(self):
        print("[agent] Release")

    @method()
    def RequestAuthorization(self, device: "o"):
        print(f"[agent] RequestAuthorization: {device}")

    @method()
    def AuthorizeService(self, device: "o", uuid: "s"):
        print(f"[agent] AuthorizeService: {device} uuid={uuid}")

    @method()
    def RequestPinCode(self, device: "o") -> "s":
        print(f"[agent] RequestPinCode: {device} (nicht unterstützt für NoInputNoOutput)")
        raise Exception("NoInputNoOutput")

    @method()
    def RequestPasskey(self, device: "o") -> "u":
        print(f"[agent] RequestPasskey: {device} (nicht unterstützt für NoInputNoOutput)")
        raise Exception("NoInputNoOutput")

    @method()
    def DisplayPinCode(self, device: "o", pincode: "s"):
        print(f"[agent] DisplayPinCode: {device} pincode={pincode}")

    @method()
    def DisplayPasskey(self, device: "o", passkey: "u", entered: "q"):
        print(f"[agent] DisplayPasskey: {device} passkey={passkey:06d} entered={entered}")

    @method()
    def RequestConfirmation(self, device: "o", passkey: "u"):
        print(f"[agent] RequestConfirmation: {device} passkey={passkey:06d} -> OK")

    @method()
    def RequestPairing(self, device: "o"):
        print(f"[agent] RequestPairing: {device} -> OK")

    @method()
    def Cancel(self):
        print("[agent] Cancel")

class Advertisement(ServiceInterface):
    def __init__(self, path="/com/example/advertisement", local_name=DEVICE_NAME):
        super().__init__("org.bluez.LEAdvertisement1")
        self._path = path
        self._local_name = local_name

    @dbus_property(access=PropertyAccess.READ)
    def Type(self) -> "s":
        return "peripheral"

    @dbus_property(access=PropertyAccess.READ)
    def LocalName(self) -> "s":
        return self._local_name

    @dbus_property(access=PropertyAccess.READ)
    def ServiceUUIDs(self) -> "as":
        return []

    @dbus_property(access=PropertyAccess.READ)
    def Includes(self) -> "as":
        return []

    @method()
    def Release(self):
        print("[adv] Release")

async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    om_intro = await bus.introspect(BLUEZ, "/")
    om_obj = bus.get_proxy_object(BLUEZ, "/", om_intro)
    om = om_obj.get_interface(DBUS_OM_IFACE)
    objects = await om.call_get_managed_objects()

    adapter_path = ADAPTER_PATH or _find_adapter_path(objects)
    print("Adapter:", adapter_path)

    adap_intro = await bus.introspect(BLUEZ, adapter_path)
    adap_obj = bus.get_proxy_object(BLUEZ, adapter_path, adap_intro)
    props = adap_obj.get_interface("org.freedesktop.DBus.Properties")

    await props.call_set(ADAPTER_IFACE, "Powered", Variant("b", True))
    await props.call_set(ADAPTER_IFACE, "Discoverable", Variant("b", True))
    await props.call_set(ADAPTER_IFACE, "Pairable", Variant("b", True))
    await props.call_set(ADAPTER_IFACE, "Alias", Variant("s", DEVICE_NAME))

    agent_path = "/com/example/agent"
    agent = Agent(agent_path)
    bus.export(agent_path, agent)

    mgr_intro = await bus.introspect(BLUEZ, AGENT_MGR_PATH)
    mgr_obj = bus.get_proxy_object(BLUEZ, AGENT_MGR_PATH, mgr_intro)
    agent_mgr = mgr_obj.get_interface(AGENT_MGR_IFACE)

    await agent_mgr.call_register_agent(agent_path, "NoInputNoOutput")
    await agent_mgr.call_request_default_agent(agent_path)
    print("OK: Agent registriert (NoInputNoOutput)")

    adv_path = "/com/example/advertisement"
    adv = Advertisement(adv_path, DEVICE_NAME)
    bus.export(adv_path, adv)

    adv_mgr = adap_obj.get_interface(ADVERT_MGR_IFACE)
    await adv_mgr.call_register_advertisement(adv_path, {})
    print("OK: Advertising aktiv:", DEVICE_NAME)

    print("Android TV: Einstellungen -> Fernbedienungen & Zubehör -> Zubehör hinzufügen")
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
