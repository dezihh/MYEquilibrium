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

class DummyService(dbus.service.Object):
    PATH = '/org/bluez/blekbd/service0'
    UUID = '00001812-0000-1000-8000-00805f9b34fb'  # HID

    def __init__(self):
        dbus.service.Object.__init__(self, bus, self.PATH)
        self.chars = []

    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, itf):
        if itf == 'org.bluez.GattService1':
            return {'UUID': self.UUID, 'Primary': True,
                    'Characteristics': dbus.Array([c.get_path() for c in self.chars], signature='o')}
        return {}

    def get_path(self): return dbus.ObjectPath(self.PATH)

class DummyChar(dbus.service.Object):
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

class DummyApp(dbus.service.Object):
    def __init__(self):
        dbus.service.Object.__init__(self, bus, '/')
        self.svc = DummyService()
        self.char = DummyChar(self.svc.PATH + '/char0', '00002a4d-0000-1000-8000-00805f9b34fb', self.svc)
        self.svc.chars.append(self.char)

    @dbus.service.method('org.freedesktop.DBus.ObjectManager', out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        r = {}
        r[self.svc.PATH] = {'org.bluez.GattService1': {
            'UUID': self.svc.UUID, 'Primary': True,
            'Characteristics': dbus.Array([self.char.get_path()], signature='o')}}
        r[self.char.get_path()] = {'org.bluez.GattCharacteristic1': {
            'UUID': self.char.uuid, 'Service': self.svc.get_path(),
            'Flags': dbus.Array(['read', 'write'], signature='s')}}
        return r

class Adv(dbus.service.Object):
    PATH = '/org/bluez/blekbd/adv0'
    def __init__(self):
        dbus.service.Object.__init__(self, bus, self.PATH)

    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface == LE_ADV_IFACE:
            return {
                'Type': dbus.String('peripheral'),
                'ServiceUUIDs': dbus.Array(['00001812-0000-1000-8000-00805F9B34FB'], signature='s'),
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
    def RequestAuthorization(self, dev): print('[Agent] RequestAuth', dev)
    @dbus.service.method(AGENT_IFACE, in_signature='ouq', out_signature='')
    def DisplayPasskey(self, dev, pk, entered): print('[Agent] Passkey:', pk)
    @dbus.service.method(AGENT_IFACE, in_signature='os', out_signature='')
    def DisplayPinCode(self, dev, code): print('[Agent] PIN:', code)

def robust_register(gattmgr, advmgr, app_path, adv_path, max_tries=3):
    for n in range(max_tries):
        adv_ok, gatt_ok = False, False
        try:
            gattmgr.RegisterApplication(app_path, {},
                reply_handler=lambda: print('[GATT] Registration erfolgreich'),
                error_handler=lambda e: print(f'[GATT] Error: {e}'))
            gatt_ok = True
        except dbus.exceptions.DBusException as e:
            if "AlreadyExists" in str(e):
                print('[GATT] Handle busy, versuche Unregister und Retry in 2s...')
                try: gattmgr.UnregisterApplication(app_path)
                except: pass
                time.sleep(2)
                continue
            else:
                print('[GATT] Schwerer Fehler:', e)
                break
        try:
            advmgr.RegisterAdvertisement(adv_path, {},
                reply_handler=lambda: print('[ADV] Registrierung erfolgreich'),
                error_handler=lambda e: print(f'[ADV] Error: {e}'))
            adv_ok = True
        except dbus.exceptions.DBusException as e:
            if 'AlreadyExists' in str(e):
                print('[ADV] Handle busy, versuche Unregister und Retry in 2s...')
                try: advmgr.UnregisterAdvertisement(adv_path)
                except: pass
                time.sleep(2)
                continue
            else:
                print('[ADV] Schwerer Fehler:', e)
                break
        if adv_ok and gatt_ok:
            return True
        time.sleep(2)
    print('[*] Nach mehreren Versuchen kein Erfolg.')
    return False

def main():
    print('[*] BLE Keyboard Demo – Pairing / TRUST Phase')
    agent = Agent()
    mgr = dbus.Interface(bus.get_object(BLUEZ, '/org/bluez'), 'org.bluez.AgentManager1')
    mgr.RegisterAgent(AGENT_PATH, 'NoInputNoOutput')
    mgr.RequestDefaultAgent(AGENT_PATH)
    print('[+] Agent registriert.')
    app = DummyApp()
    gattmgr = dbus.Interface(bus.get_object(BLUEZ, adapter), GATT_MANAGER)
    adv = Adv()
    advmgr = dbus.Interface(bus.get_object(BLUEZ, adapter), LE_ADV_MANAGER)
    robust_register(gattmgr, advmgr, '/', Adv.PATH, 4)
    print('[*] Gerät ist bereit – auf deinem Client (TV/Handy) jetzt Pairing/Bonding durchführen! (Ctrl+C zum Beenden)')
    loop = GLib.MainLoop()
    def handler(sig, frame):
        print('\n[*] Script beendet (Bond und Trust bleiben erhalten)!')
        loop.quit()
    signal.signal(signal.SIGINT, handler)
    loop.run()
    print('[*] Ordn. beendet.')

if __name__ == '__main__':
    main()
