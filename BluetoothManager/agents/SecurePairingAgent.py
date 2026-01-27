import logging
from typing import Optional, Callable, Awaitable, Dict
from dbus_fast.service import method
from BluetoothManager.agents.PairingAgentBase import PairingAgentBase


class SecurePairingAgent(PairingAgentBase):
    """
    Secure Bluetooth pairing agent with PIN display and user confirmation.
    Suitable for Android TV / Fire TV Remote Control pairing.
    
    Implements org.bluez.Agent1 interface with DisplayYesNo capability.
    """
    
    def __init__(self, pairing_callback: Optional[Callable[[Dict], Awaitable[None]]] = None):
        """
        Initialize secure pairing agent.
        
        :param pairing_callback: Async callback for pairing events (sent to WebSocket/API)
        """
        super().__init__(pairing_callback)
        self.logger = logging.getLogger(__name__)
    
    @method()
    async def RequestAuthorization(self, device: "o"):
        """
        BlueZ requests authorization for a device connection.
        User must explicitly approve.
        
        :param device: DBus object path of the device
        """
        self.logger.info("\n" + "%" * 70)
        self.logger.info("%%% RequestAuthorization called %%%")
        self.logger.info("%%% Device wants to connect %%%")
        self.logger.info("%" * 70 + "\n")
        
        device_info = await self._get_device_info(device)
        
        self.logger.info(f"Authorization request from {device_info['name']} ({device_info['address']})")
        
        await self._notify_event({
            "type": "authorization_request",
            "device": device_info,
            "message": f"Gerät '{device_info['name']}' möchte sich verbinden. Zulassen?"
        })
        
        # Wait for user decision
        confirmed = await self._wait_for_confirmation(device, timeout=30)
        
        if not confirmed:
            self.logger.info(f"Authorization rejected for {device_info['name']}")
            raise Exception("org.bluez.Error.Rejected")
        
        self.logger.info(f"Authorization granted for {device_info['name']}")
    
    @method()
    def RequestPinCode(self, device: "o") -> "s":
        """
        Legacy pairing - BlueZ requests us to provide a PIN.
        Return fixed PIN (Android TV/Fire TV might use this!).
        
        :param device: DBus object path of the device
        :return: PIN code string ("0000" or similar)
        """
        self.logger.info("\n" + "!" * 70)
        self.logger.info("!!! RequestPinCode called (LEGACY) !!!")
        self.logger.info("!!! Device wants PIN from US !!!")
        self.logger.info("!" * 70 + "\n")
        
        pin = "0000"  # Default PIN
        
        self.logger.info(f"Returning PIN: {pin}")
        return pin
    
    @method()
    def RequestPasskey(self, device: "o") -> "u":
        """
        Bluetooth LE pairing - BlueZ requests numeric passkey from us.
        Return fixed 6-digit passkey.
        
        :param device: DBus object path of the device
        :return: Numeric passkey (0-999999)
        """
        self.logger.info("\n" + "!" * 70)
        self.logger.info("!!! RequestPasskey called !!!")
        self.logger.info("!!! Device wants PASSKEY from US !!!")
        self.logger.info("!" * 70 + "\n")
        
        passkey = 123456  # Fixed passkey
        
        self.logger.info(f"Returning passkey: {passkey:06d}")
        return passkey
    
    @method()
    async def DisplayPasskey(self, device: "o", passkey: "u", entered: "q"):
        """
        Display 6-digit PIN code. User enters this on the target device (e.g., Fire TV).
        
        :param device: DBus object path of the device
        :param passkey: 6-digit passkey (0-999999)
        :param entered: Number of digits already entered
        """
        self.logger.info("\n" + "*" * 70)
        self.logger.info("*** DisplayPasskey called ***")
        self.logger.info("*** We show PIN, device enters it ***")
        self.logger.info("*" * 70 + "\n")
        
        device_info = await self._get_device_info(device)
        pin = f"{passkey:06d}"
        
        self.logger.info(f"Displaying passkey {pin} for {device_info['name']} (entered: {entered})")
        
        # Log PIN prominently
        self.logger.info("\n" + "=" * 70)
        self.logger.info(f"*** PIN CODE FOR {device_info['name'].upper()} ***")
        self.logger.info(f"*** {pin} ***")
        self.logger.info("Enter this PIN on your device!")
        self.logger.info("=" * 70 + "\n")
        
        await self._notify_event({
            "type": "display_passkey",
            "device": device_info,
            "pin": pin,
            "entered_digits": entered,
            "message": f"Geben Sie diesen PIN auf '{device_info['name']}' ein: {pin}"
        })
    
    @method()
    async def RequestConfirmation(self, device: "o", passkey: "u"):
        """
        Both devices display PIN - user confirms they match.
        Common for Fire TV / Android TV pairing.
        
        :param device: DBus object path of the device
        :param passkey: 6-digit passkey to confirm
        """
        self.logger.info("\n" + "#" * 70)
        self.logger.info("### RequestConfirmation called ###")
        self.logger.info("### Both devices show same PIN - confirm it matches ###")
        self.logger.info("#" * 70 + "\n")
        
        device_info = await self._get_device_info(device)
        pin = f"{passkey:06d}"
        
        self.logger.info(f"Requesting confirmation for passkey {pin} with {device_info['name']}")
        
        # Log PIN prominently
        self.logger.info("\n" + "=" * 70)
        self.logger.info(f"*** CONFIRM THIS PIN MATCHES ON {device_info['name'].upper()} ***")
        self.logger.info(f"*** {pin} ***")
        self.logger.info("=" * 70 + "\n")
        
        await self._notify_event({
            "type": "confirm_passkey",
            "device": device_info,
            "pin": pin,
            "message": f"Wird dieser PIN auf '{device_info['name']}' angezeigt?\n\n{pin}"
        })
        
        confirmed = await self._wait_for_confirmation(device, timeout=30)
        
        if not confirmed:
            self.logger.info(f"Passkey confirmation rejected for {device_info['name']}")
            raise Exception("org.bluez.Error.Canceled")
        
        self.logger.info(f"Passkey confirmed for {device_info['name']}")
    
    @method()
    async def AuthorizeService(self, device: "o", uuid: "s"):
        """
        Authorize a specific service (e.g., HID).
        Auto-approve HID service after successful pairing.
        
        :param device: DBus object path of the device
        :param uuid: Service UUID
        """
        self.logger.info("\n" + "@" * 70)
        self.logger.info("@@@ AuthorizeService called @@@")
        self.logger.info(f"@@@ Service UUID: {uuid} @@@")
        self.logger.info("@" * 70 + "\n")
        
        device_info = await self._get_device_info(device)
        
        # Auto-approve HID service (0x1812)
        if uuid.lower() == "00001812-0000-1000-8000-00805f9b34fb":
            self.logger.info(f"Auto-authorized HID service for {device_info['name']}")
            return
        
        self.logger.info(f"Authorization request for service {uuid} from {device_info['name']}")
        
        await self._notify_event({
            "type": "authorize_service",
            "device": device_info,
            "service_uuid": uuid,
            "message": f"Service {uuid} für '{device_info['name']}' autorisieren?"
        })
        
        confirmed = await self._wait_for_confirmation(device, timeout=15)
        
        if not confirmed:
            self.logger.info(f"Service authorization rejected for {device_info['name']}")
            raise Exception("org.bluez.Error.Rejected")
        
        self.logger.info(f"Service authorized for {device_info['name']}")
    
    @method()
    def Cancel(self):
        """
        Pairing was canceled (timeout, user cancel, etc.)
        Clean up all pending confirmations.
        """
        self.logger.warning("Pairing canceled")
        
        # Cancel all pending confirmations
        for device, future in list(self.pending_confirmations.items()):
            if not future.done():
                future.set_exception(Exception("Pairing cancelled"))
        
        self.pending_confirmations.clear()
        
        # Notify via callback
        asyncio.create_task(self._notify_event({
            "type": "pairing_cancelled",
            "message": "Pairing wurde abgebrochen"
        }))
    
    async def handle_pairing_request(self, device_path: str) -> bool:
        """
        Handle pairing request (implementation of abstract method).
        
        :param device_path: DBus path of the device
        :return: True if pairing accepted
        """
        # This is handled via the BlueZ callbacks (RequestAuthorization, etc.)
        # This method is for programmatic pairing initiation
        device_info = await self._get_device_info(device_path)
        
        await self._notify_event({
            "type": "pairing_initiated",
            "device": device_info,
            "message": f"Pairing mit '{device_info['name']}' wird gestartet..."
        })
        
        return True
