from enum import Enum
from typing import Optional
from sqlmodel import SQLModel


class BluetoothProfile(str, Enum):
    """Available Bluetooth profiles"""
    KEYBOARD = "keyboard"
    REMOTE = "remote"


class BluetoothCommandRequest(SQLModel):
    """
    Request model for sending Bluetooth commands.
    """
    profile: Optional[BluetoothProfile] = None  # Use active profile if None
    button: str  # Button name (e.g., "HOME", "DPAD_UP", "VOLUME_UP")
    action: Optional[str] = "click"  # "press", "release", or "click"
    duration: Optional[float] = 0.1  # Click duration in seconds


class BluetoothPairingRequest(SQLModel):
    """
    Request model for pairing operations.
    """
    device_address: str  # MAC address of device to pair
    trust: Optional[bool] = True  # Mark as trusted (persistent bond)


class BluetoothPairingConfirmation(SQLModel):
    """
    Request model for confirming/rejecting pairing.
    """
    device_path: str  # DBus path of the device
    confirmed: bool  # True to confirm, False to reject


class BluetoothAdvertiseRequest(SQLModel):
    """
    Request model for starting advertisement.
    """
    profile: Optional[str] = None  # Profile to advertise (uses active if None)
    duration: Optional[int] = 60  # Advertisement duration in seconds (0 = permanent)


class BluetoothProfileInfo(SQLModel):
    """
    Information about a Bluetooth profile.
    """
    name: str  # Human-readable name
    supports_wake: bool  # Wake-from-sleep support
    is_active: bool  # Currently active


class BluetoothDevice(SQLModel):
    """
    Information about a Bluetooth device.
    """
    path: str  # DBus path
    address: str  # MAC address
    name: str  # Device name/alias
    paired: bool  # Is paired
    connected: bool  # Is currently connected


class BluetoothPairingEvent(SQLModel):
    """
    Pairing event sent via WebSocket.
    """
    type: str  # Event type (display_passkey, confirm_passkey, etc.)
    device: Optional[BluetoothDevice] = None  # Device info
    pin: Optional[str] = None  # PIN code if applicable
    message: str  # Human-readable message
    entered_digits: Optional[int] = None  # For display_passkey events
    service_uuid: Optional[str] = None  # For authorize_service events
