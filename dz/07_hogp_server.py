import asyncio
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method, dbus_property, signal
from dbus_next import Variant
from dbus_next.constants import PropertyAccess, BusType

BLUEZ = "org.bluez"
DBUS_OM = "org.freedesktop.DBus.ObjectManager"
DBUS_PROPS = "org.freedesktop.DBus.Properties"

ADAPTER_IFACE = "org.bluez.Adapter1"
GATT_MGR_IFACE = "org.bluez.GattManager1"
ADV_MGR_IFACE = "org.bluez.LEAdvertisingManager1"
AGENT_MGR_IFACE = "org.bluez.AgentManager1"

DEVICE_NAME = "EquilibriumRemote1"

# Keyboard report map (8 bytes input: modifiers, reserved, 6 keycodes)
REPORT_MAP = bytes([
    0x05, 0x01, 0x09, 0x06, 0xA1, 0x01,
    0x05, 0x07, 0x19, 0xE0, 0x29, 0xE7,
    0x15, 0x00, 0x25, 0x01, 0x75, 0x01, 0x95, 0x08, 0x81, 0x02,
    0x95, 0x01, 0x75, 0x08, 0x81, 0x03,
    0x95, 0x06, 0x75, 0x08, 0x15, 0x00, 0x25, 0x65, 0x19, 0x00, 0x29, 0x65, 0x81, 0x00,
    0xC0
])

def find_adapter(objects):
    for path, ifaces in objects.items():
        if ADAPTER_IFACE in ifaces:
            return path
    raise RuntimeError("Kein org.bluez.Adapter1 gefunden")

class Agent(ServiceInterface):
    def __init__(self):
        super().__init__("org.bluez.Agent1")

    @method()
    def Release(self):
        print("[agent] Release")

    @method()
    def RequestConfirmation(self, device: "o", passkey: "u"):
        print(f"[agent] Confirm {device} passkey={passkey:06d} -> OK")

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
        return ["1812"]  # HID service

    @dbus_property(access=PropertyAccess.READ)
    def Appearance(self) -> "q":
        return 0x03C1  # Keyboard

    @method()
    def Release(self):
        print("[adv] Release")

class Application(ServiceInterface):
    def __init__(self):
        super().__init__(DBUS_OM)
        self._managed = {}

    def add_managed(self, path, ifaces):
        self._managed[path] = ifaces

    @method()
    def GetManagedObjects(self) -> "a{oa{sa{sv}}}":
        return self._managed

class Service(ServiceInterface):
    def __init__(self, uuid, primary=True):
        super().__init__("org.bluez.GattService1")
        self.uuid = uuid
        self.primary = primary

    @dbus_property(access=PropertyAccess.READ)
    def UUID(self) -> "s":
        return self.uuid

    @dbus_property(access=PropertyAccess.READ)
    def Primary(self) -> "b":
        return self.primary

class Characteristic(ServiceInterface):
    def __init__(self, uuid, service_path, flags):
        super().__init__("org.bluez.GattCharacteristic1")
        self.uuid = uuid
        self.service_path = service_path
        self.flags = flags
        self._notifying = False

    @dbus_property(access=PropertyAccess.READ)
    def UUID(self) -> "s":
        return self.uuid

    @dbus_property(access=PropertyAccess.READ)
    def Service(self) -> "o":
        return self.service_path

    @dbus_property(access=PropertyAccess.READ)
    def Flags(self) -> "as":
        return self.flags

    @signal()
    def PropertiesChanged(self, interface: "s", changed: "a{sv}", invalidated: "as"):
        ...

    @method()
    def ReadValue(self, options: "a{sv}") -> "ay":
        return []

    @method()
    def WriteValue(self, value: "ay", options: "a{sv}"):
        return

    @method()
    def StartNotify(self):
        self._notifying = True

    @method()
    def StopNotify(self):
        self._notifying = False

class HIDInformationChar(Characteristic):
    def __init__(self, service_path):
        super().__init__("2a4a", service_path, ["read"])

    def ReadValue(self, options):
        # bcdHID 1.11, country 0, flags 0x03 (remote wake + normally connectable)
        return list(bytes([0x11, 0x01, 0x00, 0x03]))

class ReportMapChar(Characteristic):
    def __init__(self, service_path):
        super().__init__("2a4b", service_path, ["read"])

    def ReadValue(self, options):
        return list(REPORT_MAP)

class ProtocolModeChar(Characteristic):
    def __init__(self, service_path):
        super().__init__("2a4e", service_path, ["read", "write-without-response"])
        self._mode = 1  # report protocol

    def ReadValue(self, options):
        return [self._mode]

    def WriteValue(self, value, options):
        if value:
            self._mode = int(value[0])

class ControlPointChar(Characteristic):
    def __init__(self, service_path):
        super().__init__("2a4c", service_path, ["write-without-response"])

class InputReportChar(Characteristic):
    def __init__(self, service_path):
        super().__init__("2a4d", service_path, ["read", "notify"])
        self._value = bytes(8)

    def ReadValue(self, options):
        return list(self._value)

    def set_report(self, report_bytes: bytes):
        self._value = report_bytes
        if self._notifying:
            self.PropertiesChanged(
                "org.bluez.GattCharacteristic1",
                {"Value": Variant("ay", list(self._value))},
                []
            )

async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    # find adapter
    root_intro = await bus.introspect(BLUEZ, "/")
    root_obj = bus.get_proxy_object(BLUEZ, "/", root_intro)
    om = root_obj.get_interface(DBUS_OM)
    objects = await om.call_get_managed_objects()
    adapter_path = find_adapter(objects)
    print("Adapter:", adapter_path)

    adap_intro = await bus.introspect(BLUEZ, adapter_path)
    adap_obj = bus.get_proxy_object(BLUEZ, adapter_path, adap_intro)
    props = adap_obj.get_interface(DBUS_PROPS)

    await props.call_set(ADAPTER_IFACE, "Powered", Variant("b", True))
    await props.call_set(ADAPTER_IFACE, "Discoverable", Variant("b", True))
    await props.call_set(ADAPTER_IFACE, "Pairable", Variant("b", True))
    await props.call_set(ADAPTER_IFACE, "Alias", Variant("s", DEVICE_NAME))

    # agent
    agent_path = "/com/example/agent"
    bus.export(agent_path, Agent())
    mgr_intro = await bus.introspect(BLUEZ, "/org/bluez")
    mgr_obj = bus.get_proxy_object(BLUEZ, "/org/bluez", mgr_intro)
    agent_mgr = mgr_obj.get_interface(AGENT_MGR_IFACE)
    await agent_mgr.call_register_agent(agent_path, "NoInputNoOutput")
    await agent_mgr.call_request_default_agent(agent_path)
    print("OK: Agent")

    # application + HID service + characteristics
    app_path = "/com/example/app"
    svc_path = app_path + "/service0"
    ch_info_path = svc_path + "/char0"
    ch_map_path  = svc_path + "/char1"
    ch_proto_path= svc_path + "/char2"
    ch_ctrl_path = svc_path + "/char3"
    ch_in_path   = svc_path + "/char4"

    app = Application()

    svc = Service("1812", True)
    bus.export(svc_path, svc)

    ch_info = HIDInformationChar(svc_path); bus.export(ch_info_path, ch_info)
    ch_map  = ReportMapChar(svc_path);      bus.export(ch_map_path, ch_map)
    ch_proto= ProtocolModeChar(svc_path);   bus.export(ch_proto_path, ch_proto)
    ch_ctrl = ControlPointChar(svc_path);   bus.export(ch_ctrl_path, ch_ctrl)
    ch_in   = InputReportChar(svc_path);    bus.export(ch_in_path, ch_in)

    app.add_managed(svc_path, {
        "org.bluez.GattService1": {
            "UUID": Variant("s", "1812"),
            "Primary": Variant("b", True),
        }
    })
    for p, uuid, flags in [
        (ch_info_path, "2a4a", ["read"]),
        (ch_map_path, "2a4b", ["read"]),
        (ch_proto_path, "2a4e", ["read", "write-without-response"]),
        (ch_ctrl_path, "2a4c", ["write-without-response"]),
        (ch_in_path, "2a4d", ["read", "notify"]),
    ]:
        app.add_managed(p, {
            "org.bluez.GattCharacteristic1": {
                "UUID": Variant("s", uuid),
                "Service": Variant("o", svc_path),
                "Flags": Variant("as", flags),
            }
        })

    bus.export(app_path, app)

    gatt_mgr = adap_obj.get_interface(GATT_MGR_IFACE)
    await gatt_mgr.call_register_application(app_path, {})
    print("OK: GATT app registered (HID service)")

    # advertising
    adv_path = "/com/example/advertisement"
    bus.export(adv_path, Advertisement())
    adv_mgr = adap_obj.get_interface(ADV_MGR_IFACE)
    await adv_mgr.call_register_advertisement(adv_path, {})
    print("OK: Advertising (HOGP)")

    print("Läuft. (Noch keine Tasten). STRG+C beendet.")
    try:
        await asyncio.get_running_loop().create_future()
    finally:
        try: await adv_mgr.call_unregister_advertisement(adv_path)
        except Exception: pass
        try: await gatt_mgr.call_unregister_application(app_path)
        except Exception: pass
        try: await agent_mgr.call_unregister_agent(agent_path)
        except Exception: pass

if __name__ == "__main__":
    asyncio.run(main())
