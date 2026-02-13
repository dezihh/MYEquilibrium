#!/usr/bin/env python3
import dbus, dbus.mainloop.glib, dbus.service, sys, signal, time
from gi.repository import GLib

BLUEZ = 'org.bluez'
ADAPTER_IFACE = 'org.bluez.Adapter1'
AGENT_IFACE = 'org.bluez.Agent1'
AGENT_PATH = '/org/bluez/blekbd/agent'
GATT_MANAGER = 'org.bluez.GattManager1'
LE_ADV_MANAGER = 'org.bluez.LEAdvertisingManager1'
LE_ADV_IFACE = 'org.bluez.LEAdvertisement1'
HID_SERVICE_UUID = '00001812-0000-1000-8000-00805f9b34fb'
HID_REPORT_CHAR_UUID = '00002a4d-0000-1000-8000-00805f9b34fb'
ADV_PATH = '/org/bluez/blekbd/adv0'
SVC_PATH = '/org/bluez/blekbd/service0'
CHAR_PATH = SVC_PATH + '/char0'

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

def find_adapter():
    om = dbus.Interface(bus.get_object(BLUEZ, '/'), 'org.freedesktop.DBus.ObjectManager')
    for p, i in om.GetManagedObjects().items():
        if ADAPTER_IFACE in i: return p
    return None

adapter = find_adapter()
if not adapter:
    print('Kein Adapter gefunden'); sys.exit(1)
print('Nutze Adapter:', adapter)

class HIDService(dbus.service.Object):
    def __init__(self):
        dbus.service.Object.__init__(self, bus, SVC_PATH)
        self.chars = []
    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, itf):
        if itf == 'org.bluez.GattService1':
            return {'UUID': HID_SERVICE_UUID, 'Primary': True,
                    'Characteristics': dbus.Array([c.get_path() for c in self.chars], signature='o')}
        return {}
    def get_path(self): return dbus.Object.Path(SVC_PATH)

class HIDReportChar(dbus.service.Object):
    def __init__(self, path, uuid, svc):
        dbus.service.Object.__init__(self, bus, path)
        self.uuid = uuid
        self.svc = svc
        self.value = dbus.Array([dbus.Byte(0)], signature='y')
    @dbus.service.method('org.bluez.GattCharacteristic1', in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options): return self.value
    @dbus.service.method('org.bluez.GattCharacteristic1', in_signature='aya{sv}')
    def WriteValue(self, value, options): self.value = value
    def get_path(self): return dbus.ObjectPath(self.object_path)

class HIDApp(dbus.service.Object):
    def __init__(self):
        dbus.service.Object.__init__(self, bus, '/')
        self.svc = HIDService()
        self.rep = HIDReportChar(CHAR_PATH, HID_REPORT_CHAR_UUID, self.svc)
        self.svc.chars.append(self.rep)
    @dbus.service.method('org.freedesktop.DBus.ObjectManager', out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        r = {}
        r[SVC_PATH] = {'org.bluez.GattService1': {
            'UUID': HID_SERVICE_UUID, 'Primary': True,
            'Characteristics': dbus.Array([self.rep.get_path()], signature='o')}}
        r[self.rep.get_path()] = {'org.bluez.GattCharacteristic1': {
            'UUID': self.rep.uuid, 'Service': self.svc.get_path(),
            'Flags': dbus.Array(['read', 'write'], signature='s')}}
        return r

class Adv(dbus.service.Object):
    def __init__(self):
        dbus.service.Object.__init__(self, bus, ADV_PATH)
    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface == LE_ADV_IFACE:
            return {
                'Type': dbus.String('peripheral'),
                'ServiceUUIDs': dbus.Array([HID_SERVICE_UUID], signature='s'),
                'LocalName': dbus.String('BLEKeyb'),
                'Appearance': dbus.UInt16(0x03C1),
                'Timeout': dbus.UInt16(0)
            }
        return {}
    @dbus.service.method(LE_ADV_IFACE)
    def Release(self): pass

class Agent(dbus.service.Object):
    def __init__(self):
        dbus.service.Object.__init__(self, bus, AGENT_PATH)
    @dbus.service.method(AGENT_IFACE, in_signature='', out_signature='')
    def Release(self): pass
    @dbus.service.method(AGENT_IFACE, in_signature='os', out_signature='')
    def AuthorizeService(self, dev, uuid): print('[Agent] Authorize:', dev, uuid)
    @dbus.service.method(AGENT_IFACE, in_signature='o', out_signature='')
    def RequestAuthorization(self, dev): print('[Agent] ReqAuth', dev)
    @dbus.service.method(AGENT_IFACE, in_signature='ouq', out_signature='')
    def DisplayPasskey(self, dev, pk, entered): print('[Agent] Passkey:', pk)
    @dbus.service.method(AGENT_IFACE, in_signature='os', out_signature='')
    def DisplayPinCode(self, dev, code): print('[Agent] PIN:', code)

def robust_register(gattmgr, advmgr, app_path, adv_path, max_tries=3):
    for n in range(max_tries):
        try:
            gattmgr.RegisterApplication(app_path, {}, reply_handler=lambda: print('[GATT] OK'), error_handler=lambda e: print('[GATT]', e))
            time.sleep(1)
            advmgr.RegisterAdvertisement(adv_path, {}, reply_handler=lambda: print('[ADV] OK'), error_handler=lambda e: print('[ADV]', e))
            return True
        except dbus.exceptions.DBusException as e:
            if "AlreadyExists" in str(e):
                print('[Register] Handle busy – versuche entfernen...')
                try: gattmgr.UnregisterApplication(app_path)
                except: pass
                try: advmgr.UnregisterAdvertisement(adv_path)
                except: pass
                time.sleep(2)
            else:
                print('[Register] Schwerer Fehler:', e)
                return False
        time.sleep(2)
    print('[Register] Gibt auf.')
    return False

def main():
    print('[*] BLE Keyboard FÜR PAIRING (Script 1)')
    agent = Agent()
    mgr = dbus.Interface(bus.get_object(BLUEZ, '/org/bluez'), 'org.bluez.AgentManager1')
    mgr.RegisterAgent(AGENT_PATH, 'NoInputNoOutput')
    mgr.RequestDefaultAgent(AGENT_PATH)
    print('[*] Agent registriert.')
    app = HIDApp()
    gattmgr = dbus.Interface(bus.get_object(BLUEZ, adapter), GATT_MANAGER)
    advmgr = dbus.Interface(bus.get_object(BLUEZ, adapter), LE_ADV_MANAGER)
    robust_register(gattmgr, advmgr, '/', ADV_PATH, 4)
    print('[*] Jetzt auf dem Client pairen/trusten, dann Script stoppen und Script 2 ausführen.')
    loop = GLib.MainLoop()
    def handler(sig, frame):
        print('\n[*] Script beendet (Bond bleibt erhalten!)')
        loop.quit()
    signal.signal(signal.SIGINT, handler)
    loop.run()
    print('[*] Ordnungsgemäß beendet!')
if __name__ == '__main__':
    main()
