import asyncio
import logging
from bluez_peripheral.advert import Advertisement
from bluez_peripheral.agent import NoIoAgent
from bluez_peripheral.util import get_message_bus
from bluez_peripheral.adapter import Adapter

# Importiere deine spezifischen Services und Helper
from BleKeyboard.BatteryService import BatteryService
from BleKeyboard.DeviceInformationService import DeviceInformationService
from BleKeyboard.HidService import HidService
from BleKeyboard.KeymapHelper import create_keycode, create_media_keycode

class BleKeyboard:
    def __init__(self):
        self.bus = None
        self.battery_service = None
        self.device_info_service = None
        self.hid_service = None
        self.agent = None
        self.pressed_keys = []
        self.pressed_media_keys = []

    @classmethod
    async def create(cls):
        self = cls()
        try:
            self.bus = await get_message_bus()
            print("!!! STATUS: DBus System Bus verbunden.")
        except Exception as e:
            print(f"!!! FEHLER: DBus Verbindung: {e}")
        return self

    def _unwrap_variant(self, val, default=""):
        if val is None: return default
        if hasattr(val, "value"): return str(val.value)
        return str(val)

    async def _get_gatt_manager_path(self):
        try:
            introspection = await self.bus.introspect("org.bluez", "/")
            proxy = self.bus.get_proxy_object("org.bluez", "/", introspection)
            manager = proxy.get_interface("org.freedesktop.DBus.ObjectManager")
            objects = await manager.call_get_managed_objects()
            for path, interfaces in objects.items():
                if "org.bluez.GattManager1" in interfaces:
                    return path
        except: return None
        return None

    async def register_services(self):
        print("!!! DEBUG: Starte dynamische Service-Registrierung...")
        self.battery_service = BatteryService()
        self.device_info_service = DeviceInformationService()
        self.hid_service = HidService()
        base_path = "/me/wehrfritz/ble"
        
        try:
            await self.battery_service.register(self.bus, path=f"{base_path}/service_battery")
            await self.device_info_service.register(self.bus, path=f"{base_path}/service_info")
            await self.hid_service.register(self.bus, path=f"{base_path}/service_hid")
            
            adapter_path = await self._get_gatt_manager_path()
            if adapter_path:
                intro = await self.bus.introspect("org.bluez", adapter_path)
                obj = self.bus.get_proxy_object("org.bluez", adapter_path, intro)
                service_manager = obj.get_interface("org.bluez.GattManager1")
                await service_manager.call_register_application(base_path, {})
                print(f"!!! ERFOLG: GattManager1 auf {adapter_path} registriert.")
            
            print("!!! STATUS: Alle GATT Services sind bereit.")
        except Exception as e:
            print(f"!!! FEHLER bei Service-Registrierung: {e}")

    @property
    async def devices(self):
        if not self.bus: return []
        try:
            introspection = await self.bus.introspect("org.bluez", "/")
            proxy = self.bus.get_proxy_object("org.bluez", "/", introspection)
            obj_mgr = proxy.get_interface('org.freedesktop.DBus.ObjectManager')
            objects = await obj_mgr.call_get_managed_objects()

            dev_list = []
            for path, interfaces in objects.items():
                if "org.bluez.Device1" in interfaces:
                    dev = interfaces["org.bluez.Device1"]
                    dev_list.append({
                        "path": str(path),
                        "alias": self._unwrap_variant(dev.get("Alias") or dev.get("Name"), "Unknown"),
                        "address": self._unwrap_variant(dev.get("Address"), ""),
                        "connected": bool(self._unwrap_variant(dev.get("Connected"), False) == "True"),
                        "paired": bool(self._unwrap_variant(dev.get("Paired"), False) == "True")
                    })
            return dev_list
        except Exception as e:
            print(f"!!! FEHLER devices: {e}")
            return []

    async def connect(self, identifier: str):
        """
        Versucht ein Gerät zu verbinden. 
        identifier kann ein D-Bus Pfad oder eine MAC-Adresse sein.
        """
        device_path = identifier
        
        # Falls eine MAC-Adresse übergeben wurde (z.B. 22:22...), Pfad suchen
        if ":" in identifier and not identifier.startswith("/"):
            devs = await self.devices
            for d in devs:
                if d['address'].lower() == identifier.lower():
                    device_path = d['path']
                    break
        
        print(f"!!! DEBUG: Verbindungsversuch zu {device_path}...")
        try:
            introspection = await self.bus.introspect("org.bluez", device_path)
            device_obj = self.bus.get_proxy_object("org.bluez", device_path, introspection)
            device_interface = device_obj.get_interface("org.bluez.Device1")
            
            await device_interface.call_connect()
            print(f"!!! ERFOLG: Verbindung zu {device_path} angefordert.")
            return True
        except Exception as e:
            print(f"!!! FEHLER beim Verbinden: {e}")
            return False
    async def disconnect(self, identifier: str = None):
            """
            Trennt die Verbindung zu einem oder allen Geräten.
            """
            try:
                devs = await self.devices
                # Wenn kein Identifier (Pfad/MAC) übergeben wurde, trenne alle verbundenen
                target_devs = [d for d in devs if d['connected']]
                
                if identifier:
                    # Falls wir eine MAC/einen Pfad haben, filtern wir darauf
                    target_devs = [d for d in target_devs if identifier.lower() in [d['path'].lower(), d['address'].lower()]]
    
                if not target_devs:
                    print("!!! INFO: Keine aktiven Verbindungen zum Trennen gefunden.")
                    return True
    
                for d in target_devs:
                    print(f"!!! DEBUG: Trenne Verbindung zu {d['alias']} ({d['path']})...")
                    introspection = await self.bus.introspect("org.bluez", d['path'])
                    device_obj = self.bus.get_proxy_object("org.bluez", d['path'], introspection)
                    device_interface = device_obj.get_interface("org.bluez.Device1")
                    
                    await device_interface.call_disconnect()
                    print(f"!!! ERFOLG: {d['alias']} getrennt.")
                
                return True
            except Exception as e:
                print(f"!!! FEHLER beim Disconnect: {e}")
                return False

    async def advertise(self):
        if self.hid_service is None:
            await self.register_services()

        adapter = await Adapter.get_first(self.bus)
        if self.agent is None:
            self.agent = NoIoAgent()
            await self.agent.register(self.bus, path="/me/wehrfritz/ble/agent")

        advert = Advertisement(
            "Virtual Keyboard",
            ["1812", "180F", "180A"], 
            appearance=0x03C1,
            timeout=0,
            discoverable=True
        )
        await advert.register(self.bus, adapter=adapter)
        print("!!! ERFOLG: Advertising ist aktiv.")
        
        # Dem System Zeit geben, das Advertising stabil zu starten
        await asyncio.sleep(2)
        # Auto-Reconnect für gepairte Geräte
        devs = await self.devices
        for d in devs:
            if d['paired'] and not d['connected']:
                asyncio.create_task(self.connect(d['path']))

    # --- HID Methoden ---
    def press_key(self, key_str):
        key = create_keycode(key_str)
        if key and self.hid_service:
            self.release_keys()
            self.pressed_keys.append(key)
            self.hid_service.update_pressed_keys(self.pressed_keys)

    def release_keys(self):
        if self.pressed_keys and self.hid_service:
            self.hid_service.update_pressed_keys([])
            self.pressed_keys = []

    async def send_key(self, key_str, delay=0.1):
        self.press_key(key_str)
        await asyncio.sleep(delay)
        self.release_keys()

    def press_media_key(self, key_str):
        key = create_media_keycode(key_str)
        if key and self.hid_service:
            self.release_media_keys()
            self.pressed_media_keys.append(key)
            self.hid_service.update_pressed_media_keys(key)

    def release_media_keys(self):
        if self.pressed_media_keys and self.hid_service:
            self.hid_service.update_pressed_media_keys([0, 0])
            self.pressed_media_keys = []

    async def send_media_key(self, key_str, delay=0.1):
        self.press_media_key(key_str)
        await asyncio.sleep(delay)
        self.release_media_keys()

    async def unregister_services(self):
        if self.agent: await self.agent.unregister()
