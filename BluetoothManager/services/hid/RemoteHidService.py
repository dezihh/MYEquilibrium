import logging
import asyncio
from bluez_peripheral.gatt.service import Service
from bluez_peripheral.gatt.characteristic import characteristic, CharacteristicFlags as CharFlags, DescriptorFlags as DescFlags
from bluez_peripheral.gatt.descriptor import descriptor

from BluetoothManager.services.hid.descriptors.RemoteDescriptor import REMOTE_REPORT_MAP, get_button_value, REMOTE_CONTROL_ID


class RemoteHidService(Service):
    """
    HID Service for Android TV / Fire TV Remote Control.
    Implements HID over GATT (HOGP) profile.
    
    UUID: 0x1812 (Human Interface Device)
    """
    
    logger = logging.getLogger(__name__)
    
    def __init__(self):
        # HID Service UUID: 0x1812
        super().__init__("1812", True)
        self.pressed_buttons = 0x0000  # 16-bit button state
        self.logger.debug("RemoteHidService initialized")
    
    # HID Information Characteristic
    # UUID: 0x2A4A
    @characteristic("2A4A", CharFlags.READ)
    def hid_info(self, options):
        """
        HID Information characteristic.
        Returns HID version, country code, and flags.
        """
        bcd_version = [0x01, 0x11]  # HID v1.11
        b_country_code = [0x00]     # No country code
        flags = [0x03]              # RemoteWake=True, NormallyConnectable=True
        # This enables wake-from-sleep functionality
        
        return bytes(bytearray(bcd_version + b_country_code + flags))
    
    # Report Map Characteristic
    # UUID: 0x2A4B
    @characteristic("2A4B", CharFlags.READ)
    def report_map(self, options):
        """
        HID Report Map (Descriptor).
        Defines the structure of HID reports.
        """
        return bytes(REMOTE_REPORT_MAP)
    
    # HID Control Point Characteristic
    # UUID: 0x2A4C
    @characteristic("2A4C", CharFlags.WRITE_WITHOUT_RESPONSE)
    def control_point(self, options):
        """
        HID Control Point for suspend/resume.
        """
        return bytes([0x00])
    
    @control_point.setter
    def control_point(self, value, options):
        """
        Handle control point writes (suspend/resume).
        """
        self.logger.debug(f"Control point set to {value}")
    
    # Report Characteristic (Input)
    # UUID: 0x2A4D
    @characteristic("2A4D", CharFlags.SECURE_READ | CharFlags.NOTIFY)
    def report(self, options):
        """
        HID Input Report.
        Returns current button state (2 bytes for 16 buttons).
        """
        # Return button state as 2 bytes (little-endian)
        report = [
            self.pressed_buttons & 0xFF,         # Low byte
            (self.pressed_buttons >> 8) & 0xFF   # High byte
        ]
        return bytes(report)
    
    # Report Reference Descriptor
    @descriptor("2908", report, DescFlags.READ)
    def report_descriptor(self, options):
        """
        Report Reference Descriptor.
        Identifies this as Report ID 1, Input Report.
        """
        return bytes([REMOTE_CONTROL_ID, 0x01])  # Report ID, Report Type (Input)
    
    # Protocol Mode Characteristic
    # UUID: 0x2A4E
    @characteristic("2A4E", CharFlags.READ | CharFlags.WRITE_WITHOUT_RESPONSE)
    def protocol_mode(self, options):
        """
        HID Protocol Mode (Report Protocol = 0x01).
        """
        return bytes([0x01])
    
    @protocol_mode.setter
    def protocol_mode(self, value, options):
        """
        Handle protocol mode changes.
        """
        self.logger.debug(f"Protocol mode set to {value}")
    
    # Public API for sending button presses
    
    def press_button(self, button_name: str):
        """
        Press a button (set bit).
        
        :param button_name: Button name (e.g., "HOME", "DPAD_UP")
        """
        try:
            button_value = get_button_value(button_name)
            self.pressed_buttons |= button_value
            self._notify_button_state()
            self.logger.debug(f"Button pressed: {button_name} (0x{self.pressed_buttons:04X})")
        except ValueError as e:
            self.logger.error(str(e))
    
    def release_button(self, button_name: str):
        """
        Release a button (clear bit).
        
        :param button_name: Button name (e.g., "HOME", "DPAD_UP")
        """
        try:
            button_value = get_button_value(button_name)
            self.pressed_buttons &= ~button_value
            self._notify_button_state()
            self.logger.debug(f"Button released: {button_name} (0x{self.pressed_buttons:04X})")
        except ValueError as e:
            self.logger.error(str(e))
    
    def release_all_buttons(self):
        """
        Release all buttons.
        """
        self.pressed_buttons = 0x0000
        self._notify_button_state()
        self.logger.debug("All buttons released")
    
    async def click_button(self, button_name: str, duration: float = 0.1):
        """
        Click a button (press and release).
        
        :param button_name: Button name (e.g., "HOME", "DPAD_UP")
        :param duration: Press duration in seconds
        """
        self.press_button(button_name)
        await asyncio.sleep(duration)
        self.release_button(button_name)
    
    def _notify_button_state(self):
        """
        Send notification with current button state.
        """
        report_data = bytes([
            self.pressed_buttons & 0xFF,
            (self.pressed_buttons >> 8) & 0xFF
        ])
        
        try:
            self.report.changed(report_data)
            self.logger.debug(f"Notified button state: {report_data.hex()}")
        except Exception as e:
            self.logger.warning(f"Failed to notify button state: {e}")
