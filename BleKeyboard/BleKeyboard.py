import asyncio
import logging
from random import randint

from dbus_fast import Variant

from bluez_peripheral.advert import Advertisement
from bluez_peripheral.agent import NoIoAgent
from bluez_peripheral.util import get_message_bus
from bluez_peripheral.adapter import Adapter

from BleKeyboard.BatteryService import BatteryService
from BleKeyboard.DeviceInformationService import DeviceInformationService
from BleKeyboard.HidService import HidService
from BleKeyboard.KeymapHelper import create_keycode, create_media_keycode


# For Apple TV:
# 1. Advertise
# 2. (On Apple TV) connect
# 3. Connect to initiate pairing
# 4. (On Apple TV) confirm pairing
# 6. send keystrokes
#
# Controls:
# esc                 = back
# esc (hold)          = home
# AC_HOME             = back
# AC_HOME (hold)      = home
# AC_HOME (double)    = app switcher
# MENU                = home
# MENU (hold)         = Control Center


class BleKeyboard:
    """
    Class representing a BLE keyboard.
    """
    logger = logging.getLogger(__package__)

    bus = None
    battery_service = None
    device_info_service = None
    hid_service = None
    agent = None
    active_advertisement = None
    _connection_monitor_task = None

    pressed_keys = []
    pressed_media_keys = []

    @classmethod
    async def create(cls):
        self = cls()
        self.bus = await get_message_bus()
        await self._ensure_adapter_state()
        await self.register_services()
        await self.advertise()
        if self._connection_monitor_task is None:
            self._connection_monitor_task = asyncio.create_task(self._connection_monitor())
        return self

    async def _ensure_adapter_state(self):
        try:
            adapter_path = "/org/bluez/hci0"
            introspection = await self.bus.introspect("org.bluez", adapter_path)
            proxy = self.bus.get_proxy_object("org.bluez", adapter_path, introspection)
            props_iface = proxy.get_interface("org.freedesktop.DBus.Properties")

            await props_iface.call_set("org.bluez.Adapter1", "Powered", Variant("b", True))
            await props_iface.call_set("org.bluez.Adapter1", "DiscoverableTimeout", Variant("u", 0))
            await props_iface.call_set("org.bluez.Adapter1", "PairableTimeout", Variant("u", 0))
            await props_iface.call_set("org.bluez.Adapter1", "Discoverable", Variant("b", True))
            await props_iface.call_set("org.bluez.Adapter1", "Pairable", Variant("b", True))
            try:
                await props_iface.call_set("org.bluez.Adapter1", "Privacy", Variant("s", "off"))
            except Exception:
                pass
        except Exception:
            self.logger.warning("Failed to set adapter state", exc_info=True)

    async def _connection_monitor(self, interval: float = 5.0):
        while True:
            try:
                await asyncio.sleep(interval)
                await self._ensure_adapter_state()

                devices = await self.devices
                any_connected = any(d.get("connected") for d in devices)

                # Auto-trust paired devices for persistent reconnects
                for device in devices:
                    if device.get("paired") and not device.get("trusted"):
                        path = device.get("path")
                        if not path:
                            continue
                        try:
                            device_interface = await self._get_device_interface(path)
                            await device_interface.set_trusted(True)
                            self.logger.info(f"Device trusted: {device.get('address')}")
                        except Exception:
                            self.logger.debug("Failed to set trusted", exc_info=True)
                if not any_connected and self.active_advertisement is None:
                    await self.advertise()
            except asyncio.CancelledError:
                break
            except Exception:
                self.logger.debug("Connection monitor error", exc_info=True)

    async def register_services(self):
        self.battery_service = BatteryService()
        self.device_info_service = DeviceInformationService()
        self.hid_service = HidService()

        await self.battery_service.register(self.bus, path="/me/wehrfritz/bluez_peripheral/service_battery")
        await self.device_info_service.register(self.bus, path="/me/wehrfritz/bluez_peripheral/service_info")
        await self.hid_service.register(self.bus, path="/me/wehrfritz/bluez_peripheral/service_hid")
        self.logger.debug("Registered services")

    async def unregister_services(self):
        if self.battery_service is not None:
            await self.battery_service.unregister()
        if self.device_info_service is not None:
            await self.device_info_service.unregister()
        if self.hid_service is not None:
            await self.hid_service.unregister()
        if self.agent is not None:
            try:
                await self.agent.unregister()
            except Exception:
                self.logger.warning("Failed to unregister BLE agent", exc_info=True)
            self.agent = None
        if self.active_advertisement is not None:
            try:
                await self.active_advertisement.unregister()
            except Exception:
                self.logger.warning("Failed to unregister BLE advertisement", exc_info=True)
            self.active_advertisement = None
        if self._connection_monitor_task is not None:
            self._connection_monitor_task.cancel()
            self._connection_monitor_task = None

    async def advertise(self):
        """
        Starts advertisement for the keyboard service. Call this to make the keyboard discoverable.
        Warning: Starting the advertisement might lead to previously connected devices reconnecting.
        """

        if self.agent is None:
            self.agent = NoIoAgent()
            await self.agent.register(self.bus, path="/me/wehrfritz/bluez_peripheral/agent")

        adapter = await Adapter.get_first(self.bus)

        if self.active_advertisement is not None:
            try:
                await self.active_advertisement.unregister()
            except Exception:
                self.logger.debug("Failed to stop previous advertisement", exc_info=True)
            self.active_advertisement = None

        # Start an advert that will last for 60 seconds.
        advert = Advertisement(
            "Virtual Keyboard",
            [
                "0000180F-0000-1000-8000-00805F9B34FB",
                "0000180A-0000-1000-8000-00805F9B34FB",
                "00001812-0000-1000-8000-00805F9B34FB",
            ],
            appearance=0x03C1,
            timeout=0,
        )

        await advert.register(self.bus, adapter=adapter)
        self.active_advertisement = advert
        self.logger.info("Started advertising!")

    async def stop_advertising(self):
        """
        Stop BLE advertising. Must be called before attempting to connect as central.
        """
        if self.active_advertisement is not None:
            try:
                await self.active_advertisement.unregister()
                self.logger.info("Stopped advertising")
            except Exception as e:
                self.logger.warning(f"Failed to stop advertising: {e}")
            finally:
                self.active_advertisement = None

    def press_key(self, key_str: str):
        """
        Send a key press to the connected device
        :param key_str: Key descriptor from key_map_helper.KEY_TABLE
        """

        key = create_keycode(key_str)
        if key:
            self.release_keys()
            self.pressed_keys.append(key)
            self.hid_service.update_pressed_keys(key)

    def release_keys(self):
        """
        Send a key release to the connected device
        """
        if self.pressed_keys:
            self.hid_service.update_pressed_keys([00, 00, 00, 00, 00, 00, 00, 00])
            self.pressed_keys = []


    async def send_key(self, key_str: str, delay=0.1):
        """
        Send a single key to the connected device
        :param key_str: Key descriptor from key_map_helper.KEY_TABLE
        :param delay: Delay after which the key is released
        """
        self.press_key(key_str)
        await asyncio.sleep(delay)
        self.release_keys()


    def press_media_key(self, key_str: str):
        """
        Send a media key press to the connected device
        :param key_str: Key descriptor from key_map_helper.MEDIA_KEYS
        """

        key = create_media_keycode(key_str)
        if key:
            self.release_media_keys()
            self.pressed_media_keys.append(key)
            self.hid_service.update_pressed_media_keys(key)

    def release_media_keys(self):
        """
        Send a key release to the connected device
        """
        if self.pressed_media_keys:
            self.hid_service.update_pressed_media_keys([00, 00])
            self.pressed_media_keys = []

    async def send_media_key(self, key_str, delay=0.1):
        """
        Send a single media key to the connected device
        :param key_str: Key descriptor from keymap_helper.MEDIA_KEYS
        :param delay: Delay after which the key is released
        """
        self.press_media_key(key_str)
        await asyncio.sleep(delay)
        self.release_media_keys()


    def update_battery_state(self, new_level=randint(1, 100)):
        """
        Update the reported battery state of the keyboard. I don't think this has any practical use
        :param new_level: Battery level to set (0-100)
        """
        self.battery_service.update_battery_state(new_level)


    async def _get_device_interface(self, path):
        """
        Gets the DBUS interface for the device at the given path
        :param path:
        :return:
        """
        introspection = await self.bus.introspect("org.bluez", path)
        proxy_object = self.bus.get_proxy_object("org.bluez", path, introspection)
        return proxy_object.get_interface("org.bluez.Device1")

    async def initiate_pairing(self):
        """
        Will initiate pairing with all connected devices that are not currently paired. This is necessary for my Apple TV.
        """
        introspection = await self.bus.introspect("org.bluez", "/")
        proxy_object = self.bus.get_proxy_object("org.bluez", "/", introspection)
        interface = proxy_object.get_interface('org.freedesktop.DBus.ObjectManager')
        managed_objects = await interface.call_get_managed_objects()

        for path in managed_objects:
            device = managed_objects[path].get("org.bluez.Device1", {})
            address = device.get("Address")
            paired = device.get("Paired", False)
            connected = device.get("Connected", False)
            trusted = device.get("Trusted", False)

            if address and paired and connected:
                if not paired.value and connected.value:
                    self.logger.info(f"Trying to pair with {address.value}")
                    interface = await self._get_device_interface(path)
                    self.logger.info("Trying to pair, confirm pairing on your device...")
                    await interface.call_pair()

    @property
    async def devices(self):
        """
        Get all connected or paired devices.
        :return: A list of all connected or paired devices
        """
        introspection = await self.bus.introspect("org.bluez", "/")
        proxy_object = self.bus.get_proxy_object("org.bluez", "/", introspection)
        interface = proxy_object.get_interface('org.freedesktop.DBus.ObjectManager')
        managed_objects = await interface.call_get_managed_objects()

        connected_devices = []

        for path in managed_objects:
            device = managed_objects[path].get("org.bluez.Device1", {})
            alias = device.get("Alias")
            address = device.get("Address")
            paired = device.get("Paired", False)
            connected = device.get("Connected", False)
            trusted = device.get("Trusted", False)

            # Extract actual values from Variant objects
            paired_value = paired.value if hasattr(paired, 'value') else paired
            connected_value = connected.value if hasattr(connected, 'value') else connected
            trusted_value = trusted.value if hasattr(trusted, 'value') else trusted
            address_value = address.value if hasattr(address, 'value') else address
            alias_value = alias.value if hasattr(alias, 'value') else alias

            # My ATV 4K doesn't pair automatically after connecting...
            if address_value and paired_value is False and connected_value:
                self.logger.info(f"Trying to pair with {address_value}")
                device_interface = await self._get_device_interface(path)
                self.logger.info("Trying to pair, confirm pairing on your device...")
                try:
                    await device_interface.call_pair()
                except Exception as e:
                    self.logger.warning(f"Failed to auto-pair: {e}")

            # Include ALL devices (paired OR connected, not just both)
            if address_value and alias_value and (paired_value or connected_value):
                connected_devices.append({
                    "path": path,
                    "address": address_value,
                    "alias": alias_value,
                    "paired": paired_value,
                    "connected": connected_value,
                    "trusted": trusted_value
                })
        
        self.logger.debug(f"Found {len(connected_devices)} BLE devices: {[d['alias'] for d in connected_devices]}")
        return connected_devices



    @property
    async def is_connected(self):
        """
        Get current connection status
        :return: `True` if a device is currently connected and paired, `False` else
        """
        devices = await self.devices
        for device in devices:
            if device.get("paired") and device.get("connected"):
                return True
        return False


    async def connect(self, address: str, timeout: int = 30) -> bool:
        """
        Prepare for reconnect from a paired Central device (typically Android TV).
        As a BLE Peripheral, we cannot initiate the connection. We refresh advertising
        so the Central can reconnect automatically.

        :param address: The MAC address of the device that should connect to us
        :param timeout: Time to wait for the connection (seconds)
        :return: True if connected successfully, False otherwise
        """
        self.logger.info(f"Preparing for reconnect from device {address}...")

        try:
            devices = await self.devices
            target_device = None
            
            for device in devices:
                if device.get("address") == address:
                    target_device = device
                    break
            
            if not target_device:
                self.logger.error(f"Device {address} not found in paired devices. Available: {[d['address'] for d in devices]}")
                return False

            path = target_device.get("path")
            if not path:
                self.logger.error(f"No D-Bus path found for device {address}")
                return False

            # If already connected, we're done
            if target_device.get("connected"):
                self.logger.info(f"Already connected to {address}")
                return True

            # Ensure adapter is powered, discoverable, and pairable
            await self._ensure_adapter_state()

            # Get device interface
            device_interface = await self._get_device_interface(path)

            # Ensure device is trusted for persistent connection
            try:
                await device_interface.set_trusted(True)
                self.logger.debug(f"Device {address} is trusted")
            except Exception as e:
                self.logger.warning(f"Failed to set trusted: {e}")

            # Refresh advertising to trigger reconnect on the Central side
            self.logger.info("Refreshing advertising to trigger reconnect...")
            await self.stop_advertising()
            await asyncio.sleep(0.5)
            await self.advertise()

            # Wait for connection to establish
            self.logger.info(f"Waiting for {address} to connect (up to {timeout}s)...")
            for i in range(timeout):
                await asyncio.sleep(1)
                if i % 10 == 0 and i > 0:
                    await self._ensure_adapter_state()
                devices = await self.devices
                for device in devices:
                    if device.get("address") == address and device.get("connected"):
                        self.logger.info(f"✓ Successfully connected to {address}!")
                        return True
                
                if i % 5 == 0 and i > 0:
                    self.logger.debug(f"Still waiting for {address}... ({i}/{timeout}s)")
            
            self.logger.error(f"Failed to connect to {address} within {timeout}s")
            return False
                
        except Exception as e:
            self.logger.error(f"Error during connection attempt to {address}: {e}", exc_info=True)
            return False


    async def disconnect(self, address=None):
        """
        Attempt to disconnect from the currently connected device(s)
        :param address: The address of the device that should be disconnected
        """
        devices = await self.devices
        for device in devices:
            if device.get("connected") and (address is None or address == device.get("address")):
                path = device.get("path")
                if path:
                    interface = await self._get_device_interface(path)
                    await interface.call_disconnect()
                else:
                    self.logger.error("No path found for connected device")

    async def remove_device(self, address: str) -> bool:
        """
        Remove (forget) a device from BlueZ.

        :param address: MAC address of the device to remove
        :return: True if removed, False otherwise
        """
        devices = await self.devices
        device_path = None

        for device in devices:
            if device.get("address") == address:
                device_path = device.get("path")
                break

        if not device_path:
            self.logger.error(f"Device {address} not found")
            return False

        try:
            adapter_path = "/org/bluez/hci0"
            introspection = await self.bus.introspect("org.bluez", adapter_path)
            adapter_interface = self.bus.get_proxy_object(
                "org.bluez",
                adapter_path,
                introspection
            ).get_interface("org.bluez.Adapter1")

            await adapter_interface.call_remove_device(device_path)
            self.logger.info(f"Device {address} removed from BlueZ")
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove device {address}: {e}")
            return False
