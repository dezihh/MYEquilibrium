from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseProfile(ABC):
    """
    Abstract base class for all Bluetooth HID profiles.
    Defines common interface that all profiles must implement.
    """
    
    def __init__(self):
        self.bus = None
        self.services = []
    
    @abstractmethod
    async def register_services(self, bus):
        """
        Register GATT services with BlueZ.
        
        :param bus: dbus_fast message bus
        """
        pass
    
    @abstractmethod
    async def unregister_services(self):
        """
        Unregister all GATT services.
        """
        pass
    
    @abstractmethod
    async def send_command(self, command_data: Dict):
        """
        Send a command through this profile.
        
        :param command_data: Dict with command data (button, action, etc.)
        """
        pass
    
    @abstractmethod
    def get_advertisement_data(self) -> Dict:
        """
        Get advertisement data for this profile.
        
        :return: Dict with 'name', 'uuids', 'appearance', etc.
        """
        pass
    
    @property
    @abstractmethod
    def supports_wake_from_sleep(self) -> bool:
        """
        Whether this profile supports waking devices from sleep.
        
        :return: True if RemoteWake is supported
        """
        pass
    
    @property
    @abstractmethod
    def profile_name(self) -> str:
        """
        Human-readable name of this profile.
        
        :return: Profile name (e.g., "Remote Control", "Keyboard")
        """
        pass
