#!/usr/bin/env python3
"""
Test script for Remote Control profile.

Usage:
    python test/bluetooth/test_remote_profile.py

Tests:
- Initialize and activate Remote Control profile
- Send button commands
- Test different button combinations
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from BluetoothManager.BluetoothManager import BluetoothManager


# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_basic_buttons():
    """
    Test basic button sending.
    """
    manager = BluetoothManager()
    
    try:
        # Initialize
        logger.info("Initializing BluetoothManager...")
        await manager.initialize(pairing_mode="noio")  # NoIo for testing
        
        # Activate remote profile
        logger.info("Activating Remote Control profile...")
        await manager.activate_profile("remote")
        
        # Start advertising
        logger.info("Starting advertisement...")
        await manager.advertise()
        
        logger.info("\n" + "=" * 60)
        logger.info("Connect your device first, then press Enter to start test")
        logger.info("=" * 60)
        input()
        
        # Test sequence
        buttons = [
            ("HOME", "Home button"),
            ("DPAD_UP", "Navigate up"),
            ("DPAD_DOWN", "Navigate down"),
            ("DPAD_LEFT", "Navigate left"),
            ("DPAD_RIGHT", "Navigate right"),
            ("SELECT", "Select/OK"),
            ("BACK", "Back button"),
            ("MENU", "Menu button"),
        ]
        
        for button, description in buttons:
            logger.info(f"\nSending: {description} ({button})")
            await manager.send_command({
                "button": button,
                "action": "click",
                "duration": 0.1
            })
            await asyncio.sleep(1)
        
        logger.info("\nBasic button test complete!")
    
    except KeyboardInterrupt:
        logger.info("\nStopping test...")
    
    finally:
        await manager.shutdown()


async def test_media_buttons():
    """
    Test media control buttons.
    """
    manager = BluetoothManager()
    
    try:
        await manager.initialize(pairing_mode="noio")
        await manager.activate_profile("remote")
        await manager.advertise()
        
        logger.info("Connect device and press Enter to test media buttons")
        input()
        
        media_buttons = [
            ("PLAY_PAUSE", "Play/Pause"),
            ("STOP", "Stop"),
            ("FAST_FORWARD", "Fast Forward"),
            ("REWIND", "Rewind"),
        ]
        
        for button, description in media_buttons:
            logger.info(f"\nSending: {description} ({button})")
            await manager.send_command({
                "button": button,
                "action": "click"
            })
            await asyncio.sleep(1.5)
        
        logger.info("\nMedia button test complete!")
    
    finally:
        await manager.shutdown()


async def test_volume_buttons():
    """
    Test volume control buttons.
    """
    manager = BluetoothManager()
    
    try:
        await manager.initialize(pairing_mode="noio")
        await manager.activate_profile("remote")
        await manager.advertise()
        
        logger.info("Connect device and press Enter to test volume buttons")
        input()
        
        # Volume up 3 times
        logger.info("\nVolume UP (3x)")
        for _ in range(3):
            await manager.send_command({"button": "VOLUME_UP", "action": "click"})
            await asyncio.sleep(0.5)
        
        await asyncio.sleep(1)
        
        # Volume down 3 times
        logger.info("\nVolume DOWN (3x)")
        for _ in range(3):
            await manager.send_command({"button": "VOLUME_DOWN", "action": "click"})
            await asyncio.sleep(0.5)
        
        await asyncio.sleep(1)
        
        # Mute
        logger.info("\nMUTE")
        await manager.send_command({"button": "MUTE", "action": "click"})
        
        logger.info("\nVolume test complete!")
    
    finally:
        await manager.shutdown()


async def test_press_and_hold():
    """
    Test press and hold functionality.
    """
    manager = BluetoothManager()
    
    try:
        await manager.initialize(pairing_mode="noio")
        await manager.activate_profile("remote")
        await manager.advertise()
        
        logger.info("Connect device and press Enter to test press-and-hold")
        input()
        
        # Long press HOME (common for app switcher)
        logger.info("\nLong press HOME (3 seconds)")
        await manager.send_command({
            "button": "HOME",
            "action": "click",
            "duration": 3.0
        })
        
        await asyncio.sleep(2)
        
        # Press and hold VOLUME_UP
        logger.info("\nPress and hold VOLUME_UP for 2 seconds")
        await manager.send_command({"button": "VOLUME_UP", "action": "press"})
        await asyncio.sleep(2)
        await manager.send_command({"button": "VOLUME_UP", "action": "release"})
        
        logger.info("\nPress-and-hold test complete!")
    
    finally:
        await manager.shutdown()


async def test_interactive():
    """
    Interactive test - send commands via keyboard input.
    """
    manager = BluetoothManager()
    
    try:
        await manager.initialize(pairing_mode="noio")
        await manager.activate_profile("remote")
        await manager.advertise()
        
        logger.info("\n" + "=" * 60)
        logger.info("INTERACTIVE REMOTE CONTROL TEST")
        logger.info("Connect your device and control it via keyboard")
        logger.info("=" * 60)
        logger.info("\nAvailable commands:")
        logger.info("  w/a/s/d  - Navigate (Up/Left/Down/Right)")
        logger.info("  enter    - Select/OK")
        logger.info("  backspace - Back")
        logger.info("  h        - Home")
        logger.info("  m        - Menu")
        logger.info("  space    - Play/Pause")
        logger.info("  +/-      - Volume Up/Down")
        logger.info("  q        - Quit")
        logger.info("=" * 60 + "\n")
        
        print("Press Enter to start...", end='', flush=True)
        input()
        
        # Button mapping
        key_map = {
            'w': 'DPAD_UP',
            's': 'DPAD_DOWN',
            'a': 'DPAD_LEFT',
            'd': 'DPAD_RIGHT',
            '\r': 'SELECT',  # Enter
            '\x7f': 'BACK',  # Backspace
            'h': 'HOME',
            'm': 'MENU',
            ' ': 'PLAY_PAUSE',
            '+': 'VOLUME_UP',
            '-': 'VOLUME_DOWN',
        }
        
        import sys
        import tty
        import termios
        
        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        
        try:
            tty.setcbreak(sys.stdin.fileno())
            
            print("\nReady! Use keyboard to control. Press 'q' to quit.\n")
            
            while True:
                # Read single character
                char = sys.stdin.read(1)
                
                if char == 'q':
                    break
                
                if char in key_map:
                    button = key_map[char]
                    logger.info(f"Sending: {button}")
                    await manager.send_command({
                        "button": button,
                        "action": "click"
                    })
                else:
                    logger.warning(f"Unknown key: {repr(char)}")
        
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        
        logger.info("\nInteractive test complete!")
    
    except KeyboardInterrupt:
        logger.info("\nStopping test...")
    
    finally:
        await manager.shutdown()


async def send_power(button: str):
    """Send power button click (can be used for on/off depending on device)."""
    manager = BluetoothManager()
    try:
        await manager.initialize(pairing_mode="noio")
        await manager.activate_profile("remote")
        await manager.advertise()
        await asyncio.sleep(1)
        await manager.send_command({"button": button, "action": "click"})
        logger.info(f"Sent power button: {button}")
        await asyncio.sleep(1)
    finally:
        await manager.shutdown()


async def test_wake_from_sleep():
    """
    Test waking Android TV from sleep.
    
    Requires:
    1. Device must be bonded and trusted (done via pairing test first)
    2. Device address configured
    """
    manager = BluetoothManager()
    
    DEVICE_ADDRESS = input("Enter Android TV Bluetooth address (e.g., AA:BB:CC:DD:EE:FF): ").strip()
    
    try:
        # Initialize
        logger.info("Initializing BluetoothManager...")
        await manager.initialize(pairing_mode="noio")
        
        # Activate remote profile  
        logger.info("Activating Remote Control profile...")
        await manager.activate_profile("remote")
        
        # Start advertising
        logger.info("Starting advertisement...")
        await manager.advertise()
        
        # Check if device is bonded
        is_bonded = await manager.is_bonded(DEVICE_ADDRESS)
        if not is_bonded:
            logger.error(f"Device {DEVICE_ADDRESS} is not bonded!")
            logger.error("Please run pairing test first to bond and trust the device")
            return
        
        logger.info(f"Device {DEVICE_ADDRESS} is bonded and trusted")
        
        logger.info("\n" + "=" * 60)
        logger.info("Put Android TV in sleep/standby mode")
        logger.info("Press Enter when ready, then watch TV wake up...")
        logger.info("=" * 60)
        input()
        
        # Attempt connection (this wakes the TV)
        logger.info(f"Connecting to {DEVICE_ADDRESS} (waking device)...")
        connected = await manager.connect(DEVICE_ADDRESS, timeout=5)
        
        if connected:
            logger.info("✓ Device woke up and connected!")
            
            # Optional: Send power button to ensure it's fully awake
            logger.info("Sending HOME button...")
            await manager.send_command({"button": "HOME", "action": "click"})
            
            await asyncio.sleep(2)
            
            logger.info("Wakeup test successful!")
        else:
            logger.warning("Failed to connect - device may not support BLE wakeup")
            logger.info("Or device may require explicit pairing from its side first")
    
    except KeyboardInterrupt:
        logger.info("\nStopping test...")
    
    finally:
        await manager.shutdown()


async def test_persistent_connection():
    """
    Test persistent connection loop (for integration with RemoteController).
    
    This simulates how MYEquilibrium would maintain connection to TV:
    - Keep device connected when possible
    - Reconnect on disconnect (wakes from sleep)
    - Send commands while connected
    - Handle graceful shutdown
    """
    manager = BluetoothManager()
    
    DEVICE_ADDRESS = input("Enter Android TV Bluetooth address (e.g., AA:BB:CC:DD:EE:FF): ").strip()
    
    try:
        # Initialize
        logger.info("Initializing BluetoothManager for persistent connection...")
        await manager.initialize(pairing_mode="noio")
        
        # Activate remote profile
        logger.info("Activating Remote Control profile...")
        await manager.activate_profile("remote")
        
        # Start advertising
        logger.info("Starting advertisement...")
        await manager.advertise()
        
        # Check if device is bonded
        is_bonded = await manager.is_bonded(DEVICE_ADDRESS)
        if not is_bonded:
            logger.error(f"Device {DEVICE_ADDRESS} is not bonded!")
            logger.error("Please run pairing test first")
            return
        
        logger.info(f"Device {DEVICE_ADDRESS} is bonded - ready for persistent connection")
        
        logger.info("\n" + "=" * 60)
        logger.info("PERSISTENT CONNECTION TEST")
        logger.info("This loop will:")
        logger.info("1. Maintain connection to the device")
        logger.info("2. Auto-reconnect if device disconnects")
        logger.info("3. Handle periodic status checks")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60 + "\n")
        
        reconnect_attempts = 0
        max_reconnect_attempts = 5
        
        while True:
            try:
                # Check connection status
                is_connected = await manager.is_connected(DEVICE_ADDRESS)
                
                if not is_connected:
                    logger.info(f"Device disconnected. Attempting reconnect ({reconnect_attempts + 1}/{max_reconnect_attempts})...")
                    
                    if reconnect_attempts >= max_reconnect_attempts:
                        logger.warning(f"Max reconnect attempts reached. Waiting 30s before retry...")
                        await asyncio.sleep(30)
                        reconnect_attempts = 0
                        continue
                    
                    # Try to reconnect (this will wake the device from sleep)
                    connected = await manager.connect(DEVICE_ADDRESS, timeout=5)
                    
                    if connected:
                        logger.info(f"✓ Reconnected to {DEVICE_ADDRESS}")
                        reconnect_attempts = 0
                    else:
                        reconnect_attempts += 1
                        await asyncio.sleep(2)
                else:
                    logger.debug(f"✓ Connected to {DEVICE_ADDRESS}")
                    reconnect_attempts = 0
                    
                    # Device is connected - could send periodic commands or heartbeat here
                    # For now, just monitor connection status
                    
                    # Check every 5 seconds
                    await asyncio.sleep(5)
            
            except Exception as e:
                logger.error(f"Error in connection loop: {e}")
                await asyncio.sleep(2)
    
    except KeyboardInterrupt:
        logger.info("\nStopping persistent connection test...")
    
    finally:
        # Try to disconnect gracefully
        try:
            await manager.disconnect(DEVICE_ADDRESS)
        except:
            pass
        
        await manager.shutdown()
        logger.info("Persistent connection test stopped")


if __name__ == "__main__":
    tests = {
        "basic": test_basic_buttons,
        "media": test_media_buttons,
        "volume": test_volume_buttons,
        "hold": test_press_and_hold,
        "interactive": test_interactive,
        "power_on": lambda: asyncio.run(send_power("POWER")),
        "power_off": lambda: asyncio.run(send_power("POWER")),
        "wake": test_wake_from_sleep,
        "persistent": test_persistent_connection,
    }
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
    else:
        test_name = "basic"
    
    if test_name in tests:
        asyncio.run(tests[test_name]())
    else:
        print(f"Unknown test: {test_name}")
        print(f"Available tests: {', '.join(tests.keys())}")
        sys.exit(1)
