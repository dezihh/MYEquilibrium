#!/usr/bin/env python3
import dbus, dbus.mainloop.glib, dbus.service, sys, signal, time
from gi.repository import GLib
from datetime import datetime

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

def log(msg, kind="INFO"):
    now = datetime.now().strftime("%H:%M:%S")
    if kind=="OK":
        prefix = "\033[92m[+]\033[0m"
    elif kind=="WARN":
        prefix = "\033[93m[~]\033[0m"
    elif kind=="ERR":
        prefix = "\033[91m[!]\033[0m"
    else:
        prefix = "[*]"
    print(f"{prefix} {now} {msg}")

def find_adapter():
    om = dbus.Interface(bus.get_object(BLUEZ, '/'), 'org.freedesktop.DBus.ObjectManager')
    for p, i in om.GetManagedObjects().items():
        if ADAPTER_IFACE in i: return p
    return None

def print_existing_gatt_services():
    om = dbus.Interface(bus.get_object(BLUEZ, '/'), 'org.freedesktop.DBus.ObjectManager')
    managed = om.GetManagedObjects()
    found = []
    log("Registered GATT-Services im System:", "WARN")
    for path, obj in managed.items():
        svc = obj.get('org.bluez.GattService1')
        if svc:
            uuid = svc.get('UUID', '<keine UUID>')
            prim = svc.get('Primary', False)
            log(f"GATT at {path} - UUID: {uuid} - {'Primary' if prim else 'Secondary'}", "WARN")
            found.append((path, uuid))
    if not found:
        log("Keine GATT-Services registriert.", "OK")
    else:
        log(f"Insgesamt {len(found)} GATT-Services im System.", "WARN")
    return found

adapter = find_adapter()
if not adapter:
    log('Kein Adapter gefunden', "ERR")
    sys.exit(1)
log(f'Nutze Adapter: {adapter}',"OK")

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
    def get_path(self): return dbus.ObjectPath(SVC_PATH)

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
    def AuthorizeService(self, dev, uuid): log(f'[Agent] Authorize: {dev} {uuid}',"OK")
    @dbus.service.method(AGENT_IFACE, in_signature='o', out_signature='')
    def RequestAuthorization(self, dev): log(f'[Agent] ReqAuth {dev}',"OK")
    @dbus.service.method(AGENT_IFACE, in_signature='ouq', out_signature='')
    def DisplayPasskey(self, dev, pk, entered): log(f'[Agent] Passkey: {pk}',"OK")
    @dbus.service.method(AGENT_IFACE, in_signature='os', out_signature='')
    def DisplayPinCode(self, dev, code): log(f'[Agent] PIN: {code}',"OK")

def robust_register(gattmgr, advmgr, app_path, adv_path, max_tries=5):
    for n in range(max_tries):
        log(f'Versuch, GATT und Advertisement zu registrieren (Versuch {n+1})')
        ok = True
        try:
            gattmgr.RegisterApplication(app_path, {}, reply_handler=lambda: log('[GATT] Registration erfolgreich',"OK"), error_handler=lambda e: log(f'[GATT] Error: {e}',"ERR"))
        except dbus.exceptions.DBusException as e:
            if "AlreadyExists" in str(e):
                log('[GATT] Service existiert noch – versuche Remove (UnregisterApplication)',"WARN")
                try:
                    gattmgr.UnregisterApplication(app_path)
                    log("[GATT] UnregisterApplication erfolgreich.","OK")
                    time.sleep(2)
                except Exception as e2:
                    log(f"[GATT] Konnte nicht entfernen: {e2}","ERR")
                ok = False
            else:
                log(f'[GATT] Schwerer Fehler beim Registrieren: {e}',"ERR")
                return False
        try:
            advmgr.RegisterAdvertisement(adv_path, {}, reply_handler=lambda: log('[ADV] Registration erfolgreich',"OK"), error_handler=lambda e: log(f'[ADV] Error: {e}',"ERR"))
        except dbus.exceptions.DBusException as e:
            if "AlreadyExists" in str(e):
                log('[ADV] Advertisement existiert noch – versuche UnregisterAdvertisement',"WARN")
                try:
                    advmgr.UnregisterAdvertisement(adv_path)
                    log("[ADV] UnregisterAdvertisement erfolgreich.","OK")
                    time.sleep(2)
                except Exception as e2:
                    log(f"[ADV] Konnte nicht entfernen: {e2}","ERR")
                ok = False
            else:
                log(f'[ADV] Schwerer Fehler beim Registrieren: {e}',"ERR")
                return False
        if ok:
            log('Registrierung erfolgreich abgeschlossen!',"OK")
            return True
        log('Wiederhole nach Fehler in 2s...',"WARN")
        time.sleep(2)
    log('Nach mehreren Versuchen kein Erfolg. Bitte prüfen Sie den bluetoothd oder rebooten.',"ERR")
    return False

def on_props_changed(iface, changed, invalidated, path=None):
    if iface != 'org.bluez.Device1': return
    if 'Connected' in changed:
        now = bool(changed['Connected'])
        if now:
            log('Verbindung aktiv – Advertising wird beendet.',"OK")
            stop_advertising()
        else:
            log('Verbindung getrennt – Advertising wird nach 2s neugestartet.',"WARN")
            GLib.timeout_add_seconds(2, start_advertising)

adv_active = False
adv_obj = None
advmgr = None
def start_advertising():
    global adv_active, adv_obj, advmgr
    if adv_active: return False
    adv = Adv()
    adv_obj = adv
    try:
        advmgr.RegisterAdvertisement(ADV_PATH, {},
            reply_handler=lambda: log('Advertising aktiviert.','OK'),
            error_handler=lambda e: log(f'Advertising ERROR: {e}','ERR'))
        adv_active = True
    except Exception as e:
        log(f'Advertising Exception: {e}','ERR')
    return False

def stop_advertising():
    global adv_active, adv_obj, advmgr
    if not adv_active: return
    try:
        advmgr.UnregisterAdvertisement(ADV_PATH)
        log('Advertising gestoppt.','OK')
    except Exception as e:
        log(f'Advertising-Stop Exception: {e}','ERR')
    adv_active = False
    adv_obj = None

def main():
    log('BLE Keyboard – RECONNECT DEMO (Script 2).')
    print_existing_gatt_services()
    agent = Agent()
    mgr = dbus.Interface(bus.get_object(BLUEZ, '/org/bluez'), 'org.bluez.AgentManager1')
    mgr.RegisterAgent(AGENT_PATH, 'NoInputNoOutput')
    mgr.RequestDefaultAgent(AGENT_PATH)
    log('Agent registriert.','OK')
    app = HIDApp()
    gattmgr = dbus.Interface(bus.get_object(BLUEZ, adapter), GATT_MANAGER)
    global advmgr
    advmgr = dbus.Interface(bus.get_object(BLUEZ, adapter), LE_ADV_MANAGER)

    log('Starte robuste Registrierung (GATT/Advertising)...')
    if not robust_register(gattmgr, advmgr, '/', ADV_PATH, 5):
        log('Fehler beim Registrieren, Skript beendet sich.',"ERR")
        sys.exit(2)

    bus.add_signal_receiver(
        on_props_changed,
        dbus_interface='org.freedesktop.DBus.Properties',
        signal_name='PropertiesChanged',
        path_keyword='path'
    )
    start_advertising()

    loop = GLib.MainLoop()
    def handler(sig, frame):
        log('SIGINT empfangen – Script wird beendet. Keine explizite Deregistrierung (siehe Diskussion).',"WARN")
        loop.quit()
    signal.signal(signal.SIGINT, handler)

    log('Demo bereit – Client kann reconnecten oder neu verbinden. (Ctrl+C zum Stoppen)',"OK")
    loop.run()
    log('Script ordnungsgemäß beendet. (Bond bleibt erhalten)','OK')

if __name__ == '__main__':
    main()
