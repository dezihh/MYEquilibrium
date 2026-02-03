import logging
import asyncio
from typing import Dict, Optional, Callable, Awaitable
from dbus_fast import Variant
from bluez_peripheral.util import get_message_bus
from bluez_peripheral.adapter import Adapter
from bluez_peripheral.advert import Advertisement

from BluetoothManager.profiles.BaseProfile import BaseProfile
from BluetoothManager.profiles.HidRemoteProfile import HidRemoteProfile
from BluetoothManager.agents.SecurePairingAgent import SecurePairingAgent


class BluetoothManager:
    """
    Central manager for all Bluetooth profiles and operations.
    Handles profile switching, pairing, advertising, and device management.

    API-First design: All operations accessible via defined interfaces.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bus = None
        self.adapter = None
        self.agent = None
        self.active_advertisement = None

        # Profile registry
        self.profiles: Dict[str, BaseProfile] = {}
        self.active_profile: Optional[BaseProfile] = None
        self.active_profile_name: Optional[str] = None

        # Callbacks
        self.pairing_callback: Optional[Callable[[Dict], Awaitable[None]]] = None

        self.logger.info("BluetoothManager initialized")

    async def initialize(self, pairing_mode: str = "secure"):
        """
        Initialize Bluetooth Manager.

        :param pairing_mode: "secure" (with PIN) or "noio" (auto-accept, dev only)
        """
        self.logger.info("Initializing BluetoothManager...")

        # Get D-Bus connection
        self.bus = await get_message_bus()
        self.logger.debug("Connected to D-Bus")

        # Get Bluetooth adapter
        self.adapter = await Adapter.get_first(self.bus)
        self.logger.debug(f"Using Bluetooth adapter: {self.adapter}")
        
        # Initialize pairing agent
        if pairing_mode == "secure":
            self.agent = SecurePairingAgent(pairing_callback=self._handle_pairing_event)
            # Register with bluez_peripheral's BaseAgent.register (no capability needed, it's set in __init__)
            await self.agent.register(self.bus, path="/me/wehrfritz/equilibrium/agent")
            self.logger.info("Registered SecurePairingAgent")
        else:
            from bluez_peripheral.agent import NoIoAgent
            self.agent = NoIoAgent()
            await self.agent.register(self.bus, path="/me/wehrfritz/equilibrium/agent")
            self.logger.warning("Using NoIoAgent (insecure, dev only!)")

        # Register default profiles
        await self.register_profile("remote", HidRemoteProfile())

        self.logger.info("BluetoothManager ready")

    async def register_profile(self, profile_name: str, profile: BaseProfile):
        """
        Register a Bluetooth profile.

        :param profile_name: Unique profile identifier (e.g., "remote", "keyboard")
        :param profile: Profile instance
        """
        if profile_name in self.profiles:
            self.logger.warning(f"Profile '{profile_name}' already registered, overwriting")

        self.profiles[profile_name] = profile
        self.logger.info(f"Registered profile: {profile_name} ({profile.profile_name})")

    async def activate_profile(self, profile_name: str):
        """
        Activate a specific profile.
        Deactivates current profile if any.

        :param profile_name: Profile to activate (e.g., "remote")
        """
        if profile_name not in self.profiles:
            raise ValueError(f"Profile '{profile_name}' not registered. Available: {list(self.profiles.keys())}")

        # Deactivate current profile
        if self.active_profile:
            self.logger.info(f"Deactivating profile: {self.active_profile_name}")
            await self.active_profile.unregister_services()
            self.active_profile = None
            self.active_profile_name = None

        # Activate new profile
        profile = self.profiles[profile_name]
        await profile.register_services(self.bus)

        self.active_profile = profile
        self.active_profile_name = profile_name

        self.logger.info(f"Activated profile: {profile_name} ({profile.profile_name})")

    async def advertise(self, profile_name: Optional[str] = None):
        """
        Start Bluetooth advertisement.

        :param profile_name: Profile to advertise (uses active profile if None)
        """
        # Stop existing advertisement
        if self.active_advertisement:
            await self.stop_advertising()

        # Determine which profile to advertise
        if profile_name:
            if profile_name not in self.profiles:
                raise ValueError(f"Profile '{profile_name}' not registered")
            profile = self.profiles[profile_name]
        else:
            if not self.active_profile:
                raise RuntimeError("No active profile. Call activate_profile() first.")
            profile = self.active_profile

        # Get advertisement data from profile
        adv_data = profile.get_advertisement_data()

        # Set adapter alias so BlueZ shows correct device name
        try:
            # BlueZ adapter paths are like /org/bluez/hci0, /org/bluez/hci1, etc.
            # We'll use the standard first adapter path
            adapter_path = "/org/bluez/hci0"
            introspection = await self.bus.introspect("org.bluez", adapter_path)
            adapter_interface = self.bus.get_proxy_object("org.bluez", adapter_path, introspection).get_interface("org.bluez.Adapter1")
            await adapter_interface.set_alias(adv_data["name"])
            self.logger.debug(f"Set adapter alias to: {adv_data['name']}")
        except Exception as e:
            self.logger.warning(f"Failed to set adapter alias: {e}")

        # Create advertisement
        self.active_advertisement = Advertisement(
            adv_data["name"],
            adv_data["uuids"],
            appearance=adv_data.get("appearance", 0x0180),
            timeout=adv_data.get("timeout", 60)
        )

        await self.active_advertisement.register(self.bus, adapter=self.adapter)

        self.logger.info(f"Started advertising as '{adv_data['name']}'")

    async def stop_advertising(self):
        """
        Stop current advertisement.
        """
        if self.active_advertisement:
            try:
                await self.active_advertisement.unregister()
                self.logger.info("Stopped advertising")
            except Exception as e:
                self.logger.error(f"Failed to stop advertising: {e}")
            finally:
                self.active_advertisement = None

    async def send_command(self, command_data: Dict):
        """
        Send a command through the active profile.

        :param command_data: Command data (profile-specific)
        """
        if not self.active_profile:
            raise RuntimeError("No active profile. Call activate_profile() first.")

        await self.active_profile.send_command(command_data)

    async def get_devices(self) -> list[Dict]:
        """
        Get all paired and connected Bluetooth devices.

        :return: List of device dicts with path, address, name, paired, connected, trusted
        """
        introspection = await self.bus.introspect("org.bluez", "/")
        proxy_object = self.bus.get_proxy_object("org.bluez", "/", introspection)
        interface = proxy_object.get_interface('org.freedesktop.DBus.ObjectManager')
        managed_objects = await interface.call_get_managed_objects()

        devices = []

        for path in managed_objects:
            device = managed_objects[path].get("org.bluez.Device1", {})

            if not device:
                continue

            alias = device.get("Alias")
            address = device.get("Address")
            paired = device.get("Paired", False)
            connected = device.get("Connected", False)
            
            if address and alias:
                devices.append({
                    "path": path,
                    "address": address.value if hasattr(address, 'value') else address,
                    "name": alias.value if hasattr(alias, 'value') else alias,
                    "paired": paired.value if hasattr(paired, 'value') else paired,
                    "connected": connected.value if hasattr(connected, 'value') else connected
                })

        return devices

    async def pair_device(self, device_address: str, trust: bool = True):
        """
        Initiate pairing with a device.

        :param device_address: MAC address of the device
        :param trust: Mark device as trusted (persistent bond)
        """
        devices = await self.get_devices()
        device_path = None

        for device in devices:
            if device["address"] == device_address:
                device_path = device["path"]
                break

        if not device_path:
            raise ValueError(f"Device {device_address} not found")

        # Get device interface
        introspection = await self.bus.introspect("org.bluez", device_path)
        proxy_object = self.bus.get_proxy_object("org.bluez", device_path, introspection)
        device_interface = proxy_object.get_interface("org.bluez.Device1")

        # Initiate pairing
        self.logger.info(f"Pairing with {device_address}...")
        await device_interface.call_pair()

        # Trust device for persistent bond
        if trust:
            await device_interface.set_trusted(True)
            self.logger.info(f"Device {device_address} trusted (persistent bond)")
    
    async def confirm_pairing(self, device_path: str, confirmed: bool):
        """
        Confirm or reject a pairing request.
        Called from API when user responds to pairing dialog.

        :param device_path: DBus path of the device
        :param confirmed: True to confirm, False to reject
        """
        if isinstance(self.agent, SecurePairingAgent):
            await self.agent.confirm_from_api(device_path, confirmed)
        else:
            self.logger.warning("Cannot confirm pairing: Agent is not SecurePairingAgent")

    def register_pairing_callback(self, callback: Callable[[Dict], Awaitable[None]]):
        """
        Register callback for pairing events.
        RemoteController will register WebSocket broadcast here.

        :param callback: Async function that receives pairing event dicts
        """
        self.pairing_callback = callback
        self.logger.debug("Pairing callback registered")

    async def _handle_pairing_event(self, event_data: Dict):
        """
        Internal handler for pairing events from agent.
        Forwards to registered callback (e.g., WebSocket).

        :param event_data: Event data from pairing agent
        """
        self.logger.debug(f"Pairing event: {event_data.get('type')}")

        if self.pairing_callback:
            try:
                await self.pairing_callback(event_data)
            except Exception as e:
                self.logger.error(f"Error in pairing callback: {e}", exc_info=True)

    def get_available_profiles(self) -> Dict[str, Dict]:
        """
        Get list of available profiles.

        :return: Dict of profile_name -> profile info
        """
        profiles_info = {}

        for name, profile in self.profiles.items():
            profiles_info[name] = {
                "name": profile.profile_name,
                "supports_wake": profile.supports_wake_from_sleep,
                "is_active": name == self.active_profile_name
            }

        return profiles_info

    def get_pending_pairing_requests(self) -> list[Dict]:
        """
        Get list of pending pairing requests waiting for confirmation.

        :return: List of pending confirmations
        """
        if isinstance(self.agent, SecurePairingAgent):
            pending = []
            for device_path in self.agent.pending_confirmations.keys():
                pending.append({"device_path": device_path})
            return pending

        return []

    async def is_bonded(self, device_address: str) -> bool:
        """
        Check if a device is bonded (paired and trusted).
        Required for Android TV wakeup from sleep.

        :param device_address: MAC address of the device
        :return: True if bonded and trusted, False otherwise
        """
        devices = await self.get_devices()
        for device in devices:
            if device["address"] == device_address:
                return device.get("paired", False) and device.get("trusted", False)
        return False

    async def is_connected(self, device_address: str) -> bool:
        """
        Check if a device is currently connected.

        :param device_address: MAC address of the device
        :return: True if connected, False otherwise
        """
        devices = await self.get_devices()
        for device in devices:
            if device["address"] == device_address:
                return device.get("connected", False)
        return False

    async def connect(self, device_address: str, timeout: int = 10) -> bool:
        """
        Connect to a paired device.
        This will wake an Android TV from sleep if properly bonded.

        :param device_address: MAC address of the device
        :param timeout: Connection timeout in seconds
        :return: True if connected, False if failed
        """
        devices = await self.get_devices()
        device_path = None

        for device in devices:
            if device["address"] == device_address:
                device_path = device["path"]
                break

        if not device_path:
            self.logger.error(f"Device {device_address} not found")
            return False

        # Get device interface
        introspection = await self.bus.introspect("org.bluez", device_path)
        proxy_object = self.bus.get_proxy_object("org.bluez", device_path, introspection)
        device_interface = proxy_object.get_interface("org.bluez.Device1")

        try:
            self.logger.info(f"Connecting to {device_address}...")
            await asyncio.wait_for(
                device_interface.call_connect(),
                timeout=timeout
            )
            self.logger.info(f"Connected to {device_address}")
            return True
        except asyncio.TimeoutError:
            self.logger.warning(f"Connection timeout for {device_address}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to connect to {device_address}: {e}")
            return False

    async def disconnect(self, device_address: str) -> bool:
        """
        Disconnect from a device.

        :param device_address: MAC address of the device
        :return: True if disconnected, False if failed
        """
        devices = await self.get_devices()
        device_path = None

        for device in devices:
            if device["address"] == device_address:
                device_path = device["path"]
                break

        if not device_path:
            self.logger.error(f"Device {device_address} not found")
            return False

        # Get device interface
        introspection = await self.bus.introspect("org.bluez", device_path)
        proxy_object = self.bus.get_proxy_object("org.bluez", device_path, introspection)
        device_interface = proxy_object.get_interface("org.bluez.Device1")

        try:
            self.logger.info(f"Disconnecting from {device_address}...")
            await device_interface.call_disconnect()
            self.logger.info(f"Disconnected from {device_address}")
            if self.active_profile:
                await self.advertise()
            else:
                self.logger.warning("Skipping advertise after disconnect: no active profile")
            return True
        except Exception as e:
            self.logger.error(f"Failed to disconnect from {device_address}: {e}")
            return False

    async def shutdown(self):
        """
        Shutdown Bluetooth Manager.
        Cleanup all resources.
        """
        self.logger.info("Shutting down BluetoothManager...")

        # Stop advertising
        await self.stop_advertising()

        # Deactivate profile
        if self.active_profile:
            await self.active_profile.unregister_services()

        # Unregister agent
        if self.agent:
            try:
                await self.agent.unregister()
            except Exception as e:
                self.logger.error(f"Failed to unregister agent: {e}")

        self.logger.info("BluetoothManager shutdown complete")
