# HID Report Descriptor Helper Functions
# Taken from https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/HIDTypes.h

def HIDINPUT(size):
    return 0x80 | size

def HIDOUTPUT(size):
    return 0x90 | size

def COLLECTION(size):
    return 0xa0 | size

def END_COLLECTION(size):
    return 0xc0 | size

def USAGE_PAGE(size):
    return 0x04 | size

def LOGICAL_MINIMUM(size):
    return 0x14 | size

def LOGICAL_MAXIMUM(size):
    return 0x24 | size

def REPORT_SIZE(size):
    return 0x74 | size

def REPORT_ID(size):
    return 0x84 | size

def REPORT_COUNT(size):
    return 0x94 | size

def USAGE(size):
    return 0x08 | size

def USAGE_MINIMUM(size):
    return 0x18 | size

def USAGE_MAXIMUM(size):
    return 0x28 | size


# Report IDs
REMOTE_CONTROL_ID = 0x01

# Button mapping for Android TV / Fire TV Remote
REMOTE_BUTTONS = {
    # Navigation
    "DPAD_UP": 0x0001,      # Bit 0
    "DPAD_DOWN": 0x0002,    # Bit 1
    "DPAD_LEFT": 0x0004,    # Bit 2
    "DPAD_RIGHT": 0x0008,   # Bit 3
    "SELECT": 0x0010,       # Bit 4 (OK/Enter)
    
    # System
    "BACK": 0x0020,         # Bit 5
    "HOME": 0x0040,         # Bit 6
    "MENU": 0x0080,         # Bit 7
    
    # Media Control
    "PLAY_PAUSE": 0x0100,   # Bit 8
    "STOP": 0x0200,         # Bit 9
    "REWIND": 0x0400,       # Bit 10
    "FAST_FORWARD": 0x0800, # Bit 11
    
    # Volume
    "VOLUME_UP": 0x1000,    # Bit 12
    "VOLUME_DOWN": 0x2000,  # Bit 13
    "MUTE": 0x4000,         # Bit 14
    
    # Additional
    "POWER": 0x8000,        # Bit 15
}

# HID Report Map for Android TV / Fire TV Remote Control
REMOTE_REPORT_MAP = [
    # Consumer Control Collection
    USAGE_PAGE(1), 0x0C,           # Usage Page (Consumer)
    USAGE(1), 0x01,                # Usage (Consumer Control)
    COLLECTION(1), 0x01,           # Collection (Application)
    REPORT_ID(1), REMOTE_CONTROL_ID, # Report ID (1)
    
    # Navigation Buttons (D-Pad)
    USAGE_PAGE(1), 0x01,           # Usage Page (Generic Desktop)
    USAGE(1), 0x90,                # Usage (D-pad Up) - Bit 0
    USAGE(1), 0x91,                # Usage (D-pad Down) - Bit 1
    USAGE(1), 0x92,                # Usage (D-pad Right) - Bit 2
    USAGE(1), 0x93,                # Usage (D-pad Left) - Bit 3
    
    # Select/OK Button
    USAGE_PAGE(1), 0x0C,           # Usage Page (Consumer)
    USAGE(1), 0x41,                # Usage (Menu Pick / Select) - Bit 4
    
    # System Navigation
    USAGE(2), 0x24, 0x02,          # Usage (AC Back) - Bit 5
    USAGE(2), 0x23, 0x02,          # Usage (AC Home) - Bit 6
    USAGE(1), 0x40,                # Usage (Menu) - Bit 7
    
    # Media Control
    USAGE(1), 0xCD,                # Usage (Play/Pause) - Bit 8
    USAGE(1), 0xB7,                # Usage (Stop) - Bit 9
    USAGE(1), 0xB4,                # Usage (Rewind) - Bit 10
    USAGE(1), 0xB3,                # Usage (Fast Forward) - Bit 11
    
    # Volume Control
    USAGE(1), 0xE9,                # Usage (Volume Up) - Bit 12
    USAGE(1), 0xEA,                # Usage (Volume Down) - Bit 13
    USAGE(1), 0xE2,                # Usage (Mute) - Bit 14
    
    # Power
    USAGE(1), 0x30,                # Usage (Power) - Bit 15
    
    # Input properties (16 bits total)
    LOGICAL_MINIMUM(1), 0x00,      # Logical Minimum (0)
    LOGICAL_MAXIMUM(1), 0x01,      # Logical Maximum (1)
    REPORT_SIZE(1), 0x01,          # Report Size (1 bit)
    REPORT_COUNT(1), 0x10,         # Report Count (16 buttons)
    HIDINPUT(1), 0x02,             # Input (Data,Var,Abs)
    
    END_COLLECTION(0)              # End Collection
]


def format_hex_string(report_map: list[int]) -> str:
    """
    Format report map as hex string for debugging.
    
    :param report_map: Report map as list of integers
    :return: Formatted hex string
    """
    hex_str = " ".join(f"{byte:02X}" for byte in report_map)
    return hex_str


def get_button_value(button_name: str) -> int:
    """
    Get the bit value for a button name.
    
    :param button_name: Button name (e.g., "HOME", "DPAD_UP")
    :return: Button bit value
    :raises ValueError: If button name is unknown
    """
    button_name = button_name.upper()
    if button_name not in REMOTE_BUTTONS:
        raise ValueError(f"Unknown button: {button_name}. Valid buttons: {list(REMOTE_BUTTONS.keys())}")
    
    return REMOTE_BUTTONS[button_name]
