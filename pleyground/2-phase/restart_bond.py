#!/usr/bin/env python3
import dbus, dbus.mainloop.glib, dbus.service, sys, signal, time
from gi.repository import GLib

# -- Die Service/Char/Adv/Agent-Klassen und robust_register sind IDENTISCH zu Script 1: einfach aus dem Code von Script 1 übernehmen! --

# ... (copy the Full DummyService, DummyChar, DummyApp, Adv, Agent, robust_register, find_adapter ... from Script 1 here!)

# Kurzfassung:
# - Adapter- und DBus-Setup kopieren
# - DummyService, DummyChar, DummyApp, Adv, Agent, robust_register übernehmen
# - Main: wie unten

def main():
    print('[*] BLE Keyboard Demo – Reconnect Phase')
    adapter = find_adapter()
    if not adapter:
        print('Kein Adapter gefunden'); sys.exit(1)
    agent = Agent()
    mgr = dbus.Interface(bus.get_object('org.bluez', '/org/bluez'), 'org.bluez.AgentManager1')
    mgr.RegisterAgent(AGENT_PATH, 'NoInputNoOutput')
    mgr.RequestDefaultAgent(AGENT_PATH)
    print('[+] Agent registriert.')
    app = DummyApp()
    gattmgr = dbus.Interface(bus.get_object('org.bluez', adapter), GATT_MANAGER)
    adv = Adv()
    advmgr = dbus.Interface(bus.get_object('org.bluez', adapter), LE_ADV_MANAGER)
    robust_register(gattmgr, advmgr, '/', Adv.PATH, 4)
    print('[*] Gerät ist bereit für automatischen Reconnect durch den bereits gebondeten Client! (Ctrl+C zum Beenden)')
    loop = GLib.MainLoop()
    def handler(sig, frame):
        print('\n[*] Script beendet (Bond und Trust bleiben erhalten)!')
        loop.quit()
    signal.signal(signal.SIGINT, handler)
    loop.run()
    print('[*] Ordn. beendet.')

if __name__ == '__main__':
    main()
