#!/usr/bin/env python3
import dbus, dbus.mainloop.glib, dbus.service, sys, signal
from gi.repository import GLib

BLUEZ = 'org.bluez'
ADAPTER_IFACE = 'org.bluez.Adapter1'
DEVICE_IFACE = 'org.bluez.Device1'
AGENT_IFACE = 'org.bluez.Agent1'
AGENT_PATH = '/org/bluez/blekbd/agent'
GATT_MANAGER = 'org.bluez.GattManager1'
LE_ADV_MANAGER = 'org.bluez.LEAdvertisingManager1'
LE_ADV_IFACE = 'org.bluez.LEAdvertisement1'
DBUS_OM = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROPS = 'org.freedesktop.DBus.Properties'

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

def find_adapter():
    om = dbus.Interface(bus.get_object(BLUEZ, '/'), DBUS_OM)
    for p, i in om.GetManagedObjects().items():
        if ADAPTER_IFACE in i:
            return p
    return None

adapter = find_adapter()
if not adapter:
    print('[!] Kein Adapter gefunden')
    sys.exit(1)
print(f'[+] Nutze Adapter: {adapter}')

# --- GATT Service/Char Dummy Klasse ---
class DummyService(dbus.service.Object):
    PATH = '/org/bluez/blekbd/service0'
    UUID = '00001812-0000-1000-8000-00805f9b34fb' # HID

    def __init__(self):
        dbus.service.Object.__init__(self, bus, self.PATH)
        self.chars = []

    @dbus.service.method(DBUS_PROPS, in_signature='s', out_signature='a{sv}')
    def GetAll(self, itf):
        if itf == 'org.bluez.GattService1':
            return {'UUID': self.UUID, 'Primary': True,
                    'Characteristics': dbus.Array([c.get_path() for c in self.chars], signature='o')}
        return {}

    def get_path(self):
        return dbus.ObjectPath(self.PATH)

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
        self.char = DummyChar(self.svc.PATH + '/char0',
                              '00002a4d-0000-1000-8000-00805f9b34fb', self.svc)
        self.svc.chars.append(self.char)

    @dbus.service.method(DBUS_OM, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        r = {}
        r[self.svc.PATH] = {'org.bluez.GattService1': {
            'UUID': self.svc.UUID, 'Primary': True,
            'Characteristics': dbus.Array([self.char.get_path()], signature='o')}}
        r[self.char.get_path()] = {'org.bluez.GattCharacteristic1': {
            'UUID': self.char.uuid, 'Service': self.svc.get_path(),
            'Flags': dbus.Array(['read', 'write'], signature='s')}}
        return r

# --- Advertisement ---
class Adv(dbus.service.Object):
    PATH = '/org/bluez/blekbd/adv0'
    def __init__(self):
        dbus.service.Object.__init__(self, bus, self.PATH)

    @dbus.service.method(DBUS_PROPS, in_signature='s', out_signature='a{sv}')
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

# --- Agent ---
class Agent(dbus.service.Object):
    def __init__(self):
        dbus.service.Object.__init__(self, bus, AGENT_PATH)

    @dbus.service.method(AGENT_IFACE, in_signature='', out_signature='')
    def Release(self): pass

    @dbus.service.method(AGENT_IFACE, in_signature='os', out_signature='')
    def AuthorizeService(self, dev, uuid): print(f'[Agent] Authorize: {dev} {uuid}')

    @dbus.service.method(AGENT_IFACE, in_signature='o', out_signature='')
    def RequestAuthorization(self, dev): print(f'[Agent] RequestAuth: {dev}')

    @dbus.service.method(AGENT_IFACE, in_signature='ouq', out_signature='')
    def DisplayPasskey(self, dev, pk, entered): print(f'[Agent] Passkey: {pk}')

    @dbus.service.method(AGENT_IFACE, in_signature='os', out_signature='')
    def DisplayPinCode(self, dev, code): print(f'[Agent] PIN: {code}')

# --- Advertising- und Connection-Management ---
adv_active = False
adv_obj = None
advmgr = dbus.Interface(bus.get_object(BLUEZ, adapter), LE_ADV_MANAGER)

def start_advertising():
    global adv_active, adv_obj
    if adv_active:
        return False
    adv = Adv()
    adv_obj = adv
    try:
        advmgr.RegisterAdvertisement(Adv.PATH, {},
            reply_handler=lambda: print('[+] Advertising aktiv'),
            error_handler=lambda e: print(f'[!] Adv Fehler: {e}'))
        adv_active = True
    except Exception as e:
        print(f'[!] Adv Fehler: {e}')
    return False # For GLib.timeout_add compatibility

def stop_advertising():
    global adv_active, adv_obj
    if not adv_active:
        return
    try:
        advmgr.UnregisterAdvertisement(Adv.PATH)
        print('[+] Advertising gestoppt')
    except Exception as e:
        print(f'[!] Adv Unregister Fehler: {e}')
    adv_active = False
    adv_obj = None

def on_props_changed(iface, changed, invalidated, path=None):
    # Prüft, ob sich der Verbindungsstatus ändert
    if iface != DEVICE_IFACE:
        return
    if 'Connected' in changed:
        now = bool(changed['Connected'])
        if now:
            print('[+] Verbindung aktiv – Advertising STOP')
            stop_advertising()
        else:
            print('[~] Verbindung getrennt – Advertising (wieder) STARTEN')
            GLib.timeout_add_seconds(2, start_advertising)

def main():
    print('[*] Initialisiere BLE Keyboard Demo (persistent reconnect / auto-advertise)...')
    # Agent Registrieren
    agent = Agent()
    mgr = dbus.Interface(bus.get_object(BLUEZ, '/org/bluez'), 'org.bluez.AgentManager1')
    mgr.RegisterAgent(AGENT_PATH, 'NoInputNoOutput')
    mgr.RequestDefaultAgent(AGENT_PATH)
    print('[+] Agent registriert')

    # GATT-App registrieren
    app = DummyApp()
    gattmgr = dbus.Interface(bus.get_object(BLUEZ, adapter), GATT_MANAGER)
    gattmgr.RegisterApplication('/', {},
                                reply_handler=lambda: print('[+] GATT service registriert'),
                                error_handler=lambda e: print(f'[!] GATT error: {e}'))

    # PropertiesChanged-Signale abonnieren
    bus.add_signal_receiver(
        on_props_changed,
        dbus_interface=DBUS_PROPS,
        signal_name='PropertiesChanged',
        path_keyword='path'
    )

    # Start advertising!
    start_advertising()

    loop = GLib.MainLoop()

    def handler(sig, frame):
        print('\n[*] SIGINT empfangen – KEIN Cleanup! Services bleiben bis Re-Start erhalten!')
        loop.quit()

    signal.signal(signal.SIGINT, handler)
    print('[*] Bereit für Pairing/Reconnection. Ctrl+C zum Stop.')
    loop.run()
    print('[*] Ordnungsgemäß beendet – GATT/Adv bleiben auf dem System.')

if __name__ == '__main__':
    main()
