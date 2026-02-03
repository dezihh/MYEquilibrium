import logging
import asyncio
from abc import abstractmethod
from typing import Callable, Awaitable, Optional, Dict
from bluez_peripheral.agent import BaseAgent, AgentCapability


class PairingAgentBase(BaseAgent):
    """
    Abstract base class for Bluetooth pairing agents.
    Provides common functionality and callback mechanisms for API integration.
    Inherits from bluez_peripheral.agent.BaseAgent for proper D-Bus integration.
    """
    
    def __init__(self, pairing_callback: Optional[Callable[[Dict], Awaitable[None]]] = None, capability: AgentCapability = AgentCapability.KEYBOARD_DISPLAY):
        """
        Initialize pairing agent.
        
        :param pairing_callback: Async callback function for pairing events.
                                 Will be called with dict containing event data.
        :param capability: Agent capability (KEYBOARD_DISPLAY, DISPLAY_ONLY, etc.)
        """
        super().__init__(capability)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pairing_callback = pairing_callback
        self.pending_confirmations: Dict[str, asyncio.Future] = {}
        self._export_bus = None
    
    async def _notify_event(self, event_data: Dict):
        """
        Send pairing event to registered callback (e.g., WebSocket).
        
        :param event_data: Event data dict with 'type', 'device', 'message', etc.
        """
        if self.pairing_callback:
            try:
                await self.pairing_callback(event_data)
            except Exception as e:
                self.logger.error(f"Error in pairing callback: {e}", exc_info=True)
    
    async def _wait_for_confirmation(self, device_path: str, timeout: int = 30) -> bool:
        """
        Wait for user confirmation via API.
        
        :param device_path: DBus path of the device
        :param timeout: Timeout in seconds
        :return: True if confirmed, False if rejected or timeout
        """
        future = asyncio.Future()
        self.pending_confirmations[device_path] = future
        
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            self.logger.warning(f"Pairing timeout for device {device_path}")
            await self._notify_event({
                "type": "pairing_timeout",
                "device_path": device_path,
                "message": "Pairing-Timeout - keine Bestätigung erhalten"
            })
            return False
        finally:
            if device_path in self.pending_confirmations:
                del self.pending_confirmations[device_path]
    
    async def confirm_from_api(self, device_path: str, confirmed: bool):
        """
        API calls this method to confirm or reject pairing.
        
        :param device_path: DBus path of the device
        :param confirmed: True to confirm, False to reject
        """
        if device_path in self.pending_confirmations:
            future = self.pending_confirmations[device_path]
            if not future.done():
                future.set_result(confirmed)
                self.logger.info(f"Pairing {'confirmed' if confirmed else 'rejected'} for {device_path}")
        else:
            raise ValueError(f"No pending confirmation for device {device_path}")
    
    async def _get_device_info(self, device_path: str) -> Dict:
        """
        Get device information from BlueZ.
        
        :param device_path: DBus path of the device
        :return: Dict with device info (path, address, name)
        """
        try:
            # Get bus from BaseAgent (stored as _export_bus)
            bus = self._export_bus
            if not bus:
                self.logger.error("Bus not available for device info retrieval")
                return {
                    "path": device_path,
                    "address": "unknown",
                    "name": "Unknown Device"
                }
            
            introspection = await bus.introspect("org.bluez", device_path)
            proxy_object = bus.get_proxy_object("org.bluez", device_path, introspection)
            device_interface = proxy_object.get_interface("org.bluez.Device1")
            
            address = await device_interface.get_address()
            alias = await device_interface.get_alias()
            
            return {
                "path": device_path,
                "address": address,
                "name": alias
            }
        except Exception as e:
            self.logger.error(f"Failed to get device info for {device_path}: {e}")
            return {
                "path": device_path,
                "address": "unknown",
                "name": "Unknown Device"
            }

    async def register(self, bus, path: str = "/me/wehrfritz/equilibrium/agent", capability: str = None):
        """
        Register this agent with BlueZ AgentManager1.
        Uses bluez_peripheral's BaseAgent.register method.
        
        Note: capability parameter is ignored - set via __init__
        """
        await super().register(bus, path=path, default=True)
        self.logger.info(f"Agent registered at {path}")

    async def unregister(self):
        """
        Unregister this agent from BlueZ AgentManager1 and unexport from D-Bus.
        Uses bluez_peripheral's BaseAgent.unregister method.
        """
        try:
            await super().unregister()
            self.logger.info(f"Agent unregistered")
        except Exception as e:
            self.logger.warning(f"Failed to unregister agent: {e}")
    @abstractmethod
    async def handle_pairing_request(self, device_path: str) -> bool:
        """
        Handle pairing request. Must be implemented by subclasses.
        
        :param device_path: DBus path of the device
        :return: True if pairing accepted, False if rejected
        """
        pass
