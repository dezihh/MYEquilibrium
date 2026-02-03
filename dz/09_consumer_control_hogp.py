#!/usr/bin/env python3
import sys, os, time, threading, struct
import dbus, dbus.service
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

BLUEZ = "org.bluez"
DEVICE_NAME = "RC212_Clone"
HCI = 0

REPORT_MAP = bytes([
    0x05, 0x0C, 0x09, 0x01, 0xA1, 0x01, 0x85, 0x01,
    0x19, 0x00, 0x2A, 0x9C, 0x02, 0x15, 0x00, 0x26,
    0x9C, 0x02, 0x95, 0x01, 0x75, 0x10, 0x81, 0x00, 0xC0
])

KEYS = {
    "up": 0x0042, "down": 0x0043, "left": 0x0044, "right": 0x0045,
    "select": 0x0041, "back": 0x0224, "home": 0x0223, "menu": 0x0040,
    "play_pause": 0x00CD, "volume_up": 0x00E9, "volume_down": 0x00EA, "mute": 0x00E2
}

class Application(dbus.service.Object):
    def __init__(self):
        self.path = "/"
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method("org.freedesktop.DBus.ObjectManager", out_signature="a{oa{sa{sv}}}")
    def GetManagedObjects(self):
        resp = {}
        for svc in self.services:
            resp[svc.get_path()] = svc.get_properties()
            for ch in svc.characteristics:
                resp[ch.get_path()] = ch.get_properties()
                for desc in ch.descriptors:
                    resp[desc.get_path()] = desc.get_properties()
        return resp

class Service(dbus.service.Object):
    PATH_BASE = "/org/bluez/app/service"
    def __init__(self, idx, uuid, primary):
        self.path = f"{self.PATH_BASE}{idx}"
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {"org.bluez.GattService1": {
            "UUID": self.uuid, "Primary": self.primary,
            "Characteristics": dbus.Array([c.get_path() for c in self.characteristics], "o")
        }}

    def get_path(self):
        return dbus.ObjectPath(self.path)

class Characteristic(dbus.service.Object):
    def __init__(self, idx, uuid, flags, service):
        self.path = f"{service.path}/char{idx}"
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        self.value = []
        self.notifying = False
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {"org.bluez.GattCharacteristic1": {
            "Service": self.service.get_path(), "UUID": self.uuid, "Flags": self.flags,
            "Descriptors": dbus.Array([d.get_path() for d in self.descriptors], "o")
        }}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options):
        return self.value

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature="aya{sv}")
    def WriteValue(self, value, options):
        self.value = value

    @dbus.service.method("org.bluez.GattCharacteristic1")
    def StartNotify(self):
        self.notifying = True

    @dbus.service.method("org.bluez.GattCharacteristic1")
    def StopNotify(self):
        self.notifying = False

class Descriptor(dbus.service.Object):
    def __init__(self, idx, uuid, flags, chrc):
        self.path = f"{chrc.path}/desc{idx}"
        self.uuid = uuid
        self.flags = flags
        self.chrc = chrc
        self.value = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {"org.bluez.GattDescriptor1": {
            "Characteristic": self.chrc.get_path(), "UUID": self.uuid, "Flags": self.flags
        }}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method("org.bluez.GattDescriptor1", in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options):
        return self.value

class Advertisement(dbus.service.Object):
    PATH_BASE = "/org/bluez/app/adv"
    def __init__(self, idx):
        self.path = f"{self.PATH_BASE}{idx}"
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature="s", out_signature="a{sv}")
    def GetAll(self, iface):
        if iface != "org.bluez.LEAdvertisement1":
            raise dbus.exceptions.DBusException("org.bluez.Error.InvalidArguments")
        return {
            "Type": "peripheral",
            "ServiceUUIDs": dbus.Array(["1812"], "s"),
            "LocalName": dbus.String(DEVICE_NAME),
            "Appearance": dbus.UInt16(0x03C4),  # HID Generic
            "IncludeTxPower": dbus.Boolean(True)
        }

    @dbus.service.method("org.bluez.LEAdvertisement1")
    def Release(self):
        pass

class Agent(dbus.service.Object):
    def __init__(self, path):
        dbus.service.Object.__init__(self, bus, path)

    @dbus.service.method("org.bluez.Agent1", in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        print(f"AuthorizeService({device}, {uuid})")
        return

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print(f"RequestPasskey({device})")
        return dbus.UInt32(0)

    @dbus.service.method("org.bluez.Agent1", in_signature="ou", out_signature="")
    def DisplayPasskey(self, device, passkey):
        print(f"DisplayPasskey({device}, {passkey})")

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print(f"RequestPinCode({device})")
        return ""

    @dbus.service.method("org.bluez.Agent1", in_signature="o")
    def RequestConfirmation(self, device):
        print(f"RequestConfirmation({device}) -> auto-accept")
        return

    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Cancel(self):
        print("Pairing cancelled")

input_char = None

def send_key(name):
    global input_char
    if name not in KEYS:
        print(f"Unknown: {name}")
        return
    code = KEYS[name]
    rpt = bytes([0x01]) + struct.pack("<H", code)
    input_char.value = dbus.Array(rpt, "y")
    print(f"Sent {name}: {rpt.hex()}")
    time.sleep(0.05)
    input_char.value = dbus.Array([0x01, 0x00, 0x00], "y")

def input_thread():
    print("\nReady. Keys: up down left right select back home menu play_pause volume_up volume_down mute (q=quit)")
    while True:
        cmd = input("> ").strip().lower()
        if cmd == "q":
            os._exit(0)
        elif cmd in KEYS:
            send_key(cmd)

def main():
    global input_char

    adapter = bus.get_object(BLUEZ, f"/org/bluez/hci{HCI}")
    aprops = dbus.Interface(adapter, "org.freedesktop.DBus.Properties")
    aprops.Set("org.bluez.Adapter1", "Powered", True)
    aprops.Set("org.bluez.Adapter1", "Discoverable", True)
    aprops.Set("org.bluez.Adapter1", "Pairable", True)
    aprops.Set("org.bluez.Adapter1", "Alias", DEVICE_NAME)

    # Register Agent
    agent_path = "/org/bluez/agent"
    agent = Agent(agent_path)
    am = dbus.Interface(bus.get_object(BLUEZ, "/org/bluez"), "org.bluez.AgentManager1")
    am.RegisterAgent(agent_path, "NoInputNoOutput")
    am.RequestDefaultAgent(agent_path)
    print("Agent registered (NoInputNoOutput)")

    app = Application()
    hid = Service(0, "1812", True)

    rmap = Characteristic(0, "2a4b", ["read"], hid)
    rmap.value = dbus.Array(REPORT_MAP, "y")
    hid.characteristics.append(rmap)

    hinfo = Characteristic(1, "2a4a", ["read"], hid)
    hinfo.value = dbus.Array([0x11, 0x01, 0x00, 0x03], "y")
    hid.characteristics.append(hinfo)

    ctrl = Characteristic(2, "2a4c", ["write-without-response"], hid)
    hid.characteristics.append(ctrl)

    input_char = Characteristic(3, "2a4d", ["read", "notify"], hid)
    input_char.value = dbus.Array([0x01, 0x00, 0x00], "y")
    
    # CCC Descriptor for notify
    ccc = Descriptor(0, "2902", ["read", "write"], input_char)
    ccc.value = dbus.Array([0x00, 0x00], "y")
    input_char.descriptors.append(ccc)
    
    # Report Reference Descriptor
    rref = Descriptor(1, "2908", ["read"], input_char)
    rref.value = dbus.Array([0x01, 0x01], "y")  # ReportID=1, Type=Input
    input_char.descriptors.append(rref)
    
    hid.characteristics.append(input_char)

    app.services.append(hid)

    gatt_mgr = dbus.Interface(adapter, "org.bluez.GattManager1")
    gatt_mgr.RegisterApplication(app.get_path(), {}, reply_handler=lambda: print("GATT registered"), error_handler=lambda e: print(f"GATT error: {e}"))

    ad = Advertisement(0)
    ad_mgr = dbus.Interface(adapter, "org.bluez.LEAdvertisingManager1")
    ad_mgr.RegisterAdvertisement(ad.get_path(), {}, reply_handler=lambda: print("Advertising started"), error_handler=lambda e: print(f"Ad error: {e}"))

    threading.Thread(target=input_thread, daemon=True).start()
    GLib.MainLoop().run()

if __name__ == "__main__":
    main()
