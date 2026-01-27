import logging
from typing import Dict
from BluetoothManager.profiles.BaseProfile import BaseProfile
from BluetoothManager.services.hid.RemoteHidService import RemoteHidService
from BleKeyboard.BatteryService import BatteryService
from BleKeyboard.DeviceInformationService import DeviceInformationService


class HidRemoteProfile(BaseProfile):
    """
    HID Profile for Android TV / Fire TV Remote Control.
    
    Features:
    - Navigation (D-Pad, Select, Back, Home, Menu)
    - Media Control (Play/Pause, Stop, FF, Rewind)
    - Volume Control (Up, Down, Mute)
    - Power button
    - Wake-from-Sleep support
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Services
        self.hid_service = RemoteHidService()
        self.battery_service = BatteryService()
        self.device_info_service = DeviceInformationService()
        
        self.services = [
            self.hid_service,
            self.battery_service,
            self.device_info_service
        ]
        
        self.logger.info("HidRemoteProfile initialized")
    
    async def register_services(self, bus):
        """
        Register all services with BlueZ.
        
        :param bus: dbus_fast message bus
        """
        self.bus = bus
        
        # Register each service individually
        # bluez_peripheral automatically handles GattManager registration
        await self.battery_service.register(
            bus, 
            path="/me/wehrfritz/equilibrium/remote/service_battery"
        )
        await self.device_info_service.register(
            bus, 
            path="/me/wehrfritz/equilibrium/remote/service_info"
        )
        await self.hid_service.register(
            bus, 
            path="/me/wehrfritz/equilibrium/remote/service_hid"
        )
        
        self.logger.info("All services registered for HidRemoteProfile")
    
    async def unregister_services(self):
        """
        Unregister all services.
        """
        for service in self.services:
            try:
                await service.unregister()
            except Exception as e:
                self.logger.error(f"Failed to unregister service: {e}")
        
        self.logger.info("All services unregistered for HidRemoteProfile")
    
    async def send_command(self, command_data: Dict):
        """
        Send a remote control command.
        
        :param command_data: Dict with:
            - button: Button name (e.g., "HOME", "DPAD_UP", "VOLUME_UP")
            - action: "press", "release", or "click" (default)
            - duration: Click duration in seconds (default 0.1)
        """
        button = command_data.get("button")
        action = command_data.get("action", "click")
        duration = command_data.get("duration", 0.1)
        
        if not button:
            raise ValueError("Missing 'button' in command_data")
        
        button = button.upper()
        
        if action == "press":
            self.hid_service.press_button(button)
            self.logger.debug(f"Button pressed: {button}")
        
        elif action == "release":
            self.hid_service.release_button(button)
            self.logger.debug(f"Button released: {button}")
        
        elif action == "click":
            await self.hid_service.click_button(button, duration)
            self.logger.debug(f"Button clicked: {button}")
        
        else:
            raise ValueError(f"Unknown action: {action}. Use 'press', 'release', or 'click'")
    
    def get_advertisement_data(self) -> Dict:
        """
        Get advertisement data for remote control profile.
        
        :return: Dict with advertisement parameters
        """
        return {
            "name": "Equilibrium Remote",
            "uuids": [
                "0000180F-0000-1000-8000-00805F9B34FB",  # Battery Service
                "0000180A-0000-1000-8000-00805F9B34FB",  # Device Information
                "00001812-0000-1000-8000-00805F9B34FB",  # HID Service
            ],
            "appearance": 0x0180,  # Generic Remote Control
            "timeout": 0  # Permanent advertisement for wake-from-sleep
        }
    
    @property
    def supports_wake_from_sleep(self) -> bool:
        """
        This profile supports wake-from-sleep.
        
        :return: True
        """
        return True
    
    @property
    def profile_name(self) -> str:
        """
        Human-readable profile name.
        
        :return: "Remote Control"
        """
        return "Remote Control"
    
    def release_all_buttons(self):
        """
        Release all pressed buttons.
        """
        self.hid_service.release_all_buttons()
        self.logger.debug("All buttons released")
    
    def update_battery_level(self, level: int):
        """
        Update battery level (0-100).
        
        :param level: Battery level percentage
        """
        self.battery_service.update_battery_state(level)
        self.logger.debug(f"Battery level updated: {level}%")
