import logging
import asyncio
from typing import Optional, Callable, Awaitable, Dict
from dbus_fast.service import method
from bluez_peripheral.agent import BaseAgent, AgentCapability, RejectedError


class SecurePairingAgent(BaseAgent):
    """
    Secure Bluetooth pairing agent with PIN display and user confirmation.
    Suitable for Android TV / Fire TV Remote Control pairing.
    """
    
    def __init__(self, pairing_callback: Optional[Callable[[Dict], Awaitable[None]]] = None):
        super().__init__(AgentCapability.DISPLAY_YES_NO)
        self.logger = logging.getLogger(__name__)
        self.pairing_callback = pairing_callback
        self.pending_confirmations: Dict[str, asyncio.Future] = {}
    
    async def _notify_event(self, event_data: Dict):
        if self.pairing_callback:
            try:
                await self.pairing_callback(event_data)
            except Exception as e:
                self.logger.error(f"Error in pairing callback: {e}", exc_info=True)
    
    async def _wait_for_confirmation(self, device_path: str, timeout: int = 30) -> bool:
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
                "message": "Pairing-Timeout"
            })
            return False
        finally:
            if device_path in self.pending_confirmations:
                del self.pending_confirmations[device_path]
    
    async def confirm_from_api(self, device_path: str, confirmed: bool):
        if device_path in self.pending_confirmations:
            future = self.pending_confirmations[device_path]
            if not future.done():
                future.set_result(confirmed)
                self.logger.info(f"Pairing {'confirmed' if confirmed else 'rejected'}")
    
    async def _get_device_info(self, device_path: str) -> Dict:
        try:
            bus = self._export_bus
            if not bus:
                return {"path": device_path, "address": "unknown", "name": "Unknown"}
            
            introspection = await bus.introspect("org.bluez", device_path)
            proxy = bus.get_proxy_object("org.bluez", device_path, introspection)
            device_iface = proxy.get_interface("org.bluez.Device1")
            
            address = await device_iface.get_address()
            alias = await device_iface.get_alias()
            
            return {"path": device_path, "address": address, "name": alias}
        except Exception as e:
            self.logger.error(f"Failed to get device info: {e}")
            return {"path": device_path, "address": "unknown", "name": "Unknown"}
    
    @method("RequestAuthorization")
    async def _request_authorization(self, device: "o"):
        self.logger.info("\n" + "%" * 70)
        self.logger.info("%%% RequestAuthorization called %%%")
        self.logger.info("%" * 70 + "\n")
        
        device_info = await self._get_device_info(device)
        self.logger.info(f"Auth request from {device_info['name']} ({device_info['address']})")
        
        await self._notify_event({
            "type": "authorization_request",
            "device": device_info,
            "message": f"Gerät '{device_info['name']}' möchte sich verbinden"
        })
        
        confirmed = await self._wait_for_confirmation(device, timeout=30)
        if not confirmed:
            raise RejectedError("Authorization rejected")
        
        self.logger.info(f"Authorization granted for {device_info['name']}")
    
    @method("RequestPinCode")
    def _request_pin_code(self, device: "o") -> "s":
        self.logger.info("\n!!! RequestPinCode called !!!\n")
        pin = "0000"
        self.logger.info(f"Returning PIN: {pin}")
        return pin
    
    @method("RequestPasskey")
    def _request_passkey(self, device: "o") -> "u":
        self.logger.info("\n!!! RequestPasskey called !!!\n")
        passkey = 123456
        self.logger.info(f"Returning passkey: {passkey:06d}")
        return passkey
    
    @method("DisplayPasskey")
    async def _display_passkey(self, device: "o", passkey: "u", entered: "q"):
        self.logger.info("\n*** DisplayPasskey called ***\n")
        
        device_info = await self._get_device_info(device)
        pin = f"{passkey:06d}"
        
        self.logger.info("\n" + "=" * 70)
        self.logger.info(f"PIN CODE: {pin}")
        self.logger.info("=" * 70 + "\n")
        
        await self._notify_event({
            "type": "display_passkey",
            "device": device_info,
            "pin": pin,
            "message": f"PIN für '{device_info['name']}': {pin}"
        })
    
    @method("RequestConfirmation")
    async def _request_confirmation(self, device: "o", passkey: "u"):
        self.logger.info("\n### RequestConfirmation called ###\n")
        
        device_info = await self._get_device_info(device)
        pin = f"{passkey:06d}"
        
        self.logger.info("\n" + "=" * 70)
        self.logger.info(f"CONFIRM PIN MATCHES: {pin}")
        self.logger.info("=" * 70 + "\n")
        
        await self._notify_event({
            "type": "confirm_passkey",
            "device": device_info,
            "pin": pin,
            "message": f"PIN bestätigen: {pin}?"
        })
        
        confirmed = await self._wait_for_confirmation(device, timeout=30)
        if not confirmed:
            raise RejectedError("Confirmation rejected")
        
        self.logger.info(f"Passkey confirmed for {device_info['name']}")
    
    @method("AuthorizeService")
    async def _authorize_service(self, device: "o", uuid: "s"):
        self.logger.info(f"\n@@@ AuthorizeService: {uuid} @@@\n")
        
        device_info = await self._get_device_info(device)
        
        # Auto-approve HID service
        if uuid.lower() == "00001812-0000-1000-8000-00805f9b34fb":
            self.logger.info(f"Auto-authorized HID service")
            return
        
        await self._notify_event({
            "type": "authorize_service",
            "device": device_info,
            "service_uuid": uuid,
            "message": f"Service {uuid} autorisieren?"
        })
        
        confirmed = await self._wait_for_confirmation(device, timeout=15)
        if not confirmed:
            raise RejectedError("Service authorization rejected")
        
        self.logger.info(f"Service authorized")
    
    @method("Cancel")
    def _cancel(self):
        self.logger.warning("Pairing canceled")
        
        for device, future in list(self.pending_confirmations.items()):
            if not future.done():
                future.set_exception(Exception("Pairing cancelled"))
        
        self.pending_confirmations.clear()
        
        asyncio.create_task(self._notify_event({
            "type": "pairing_cancelled",
            "message": "Pairing wurde abgebrochen"
        }))

    @method("DisplayPinCode")
    def _display_pin_code(self, device: "o", pincode: "s"):
        self.logger.info("\n*** DisplayPinCode called ***\n")
        self.logger.info(f"PIN CODE: {pincode}")
