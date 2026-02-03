#!/usr/bin/env python3
"""
Test script for Bluetooth Pairing functionality.

Usage:
    python test/bluetooth/test_pairing.py

Tests:
- Initialize BluetoothManager
- Activate Remote Control profile
- Start advertisement
- Handle pairing events
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


async def pairing_event_handler(event_data: dict):
    """
    Callback for pairing events.
    In production, this would send to WebSocket.
    """
    event_type = event_data.get("type")
    device = event_data.get("device", {})
    message = event_data.get("message", "")
    
    logger.info("=" * 60)
    logger.info(f"PAIRING EVENT: {event_type}")
    
    if device:
        logger.info(f"Device: {device.get('name')} ({device.get('address')})")
    
    if "pin" in event_data:
        logger.info(f"PIN CODE: {event_data['pin']}")
    
    logger.info(f"Message: {message}")
    logger.info("=" * 60)


async def test_pairing():
    """
    Test pairing functionality.
    """
    manager = BluetoothManager()
    known_devices = {}
    removed_devices = set()
    
    try:
        # Initialize with secure pairing
        logger.info("Initializing BluetoothManager with secure pairing...")
        await manager.initialize(pairing_mode="secure")
        
        # Register pairing callback
        manager.register_pairing_callback(pairing_event_handler)
        
        # Activate remote control profile
        logger.info("Activating Remote Control profile...")
        await manager.activate_profile("remote")
        
        # Get available profiles
        profiles = manager.get_available_profiles()
        logger.info(f"Available profiles: {profiles}")
        
        # Start advertising
        logger.info("Starting advertisement...")
        await manager.advertise()
        
        logger.info("\n" + "=" * 60)
        logger.info("READY FOR PAIRING")
        logger.info("Connect from your device (Fire TV, Android TV, etc.)")
        logger.info("When prompted, use the displayed PIN")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60 + "\n")
        
        # Wait for events
        while True:
            # Check for pending pairing requests
            pending = manager.get_pending_pairing_requests()
            if pending:
                logger.info(f"Pending pairing requests: {pending}")

            # Poll device list to see if TV connects/pairs
            devices = await manager.get_devices()
            for device in devices:
                key = device.get("address") or device.get("path")
                if not key:
                    continue

                prev = known_devices.get(key)
                if prev != device:
                    logger.info(f"Device state changed: {device}")
                    known_devices[key] = device

                # If device is paired but never connects, remove once to force fresh pairing
                if device.get("paired") and not device.get("connected"):
                    addr = device.get("address")
                    if addr and addr not in removed_devices:
                        logger.info(f"Removing device {addr} to force fresh pairing")
                        try:
                            await manager.remove_device(addr)
                            removed_devices.add(addr)
                        except Exception as e:
                            logger.warning(f"Failed to remove device {addr}: {e}")
            
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("\nStopping test...")
    
    finally:
        # Cleanup
        await manager.shutdown()
        logger.info("Test complete")


async def test_manual_confirmation():
    """
    Test manual pairing confirmation via API.
    """
    manager = BluetoothManager()
    
    try:
        await manager.initialize(pairing_mode="secure")
        manager.register_pairing_callback(pairing_event_handler)
        await manager.activate_profile("remote")
        await manager.advertise()
        
        logger.info("Waiting for pairing request...")
        logger.info("When you see a pairing request, this script will auto-confirm after 5 seconds")
        
        # Monitor for pairing requests
        while True:
            pending = manager.get_pending_pairing_requests()
            
            if pending:
                device_path = pending[0]["device_path"]
                logger.info(f"\nFound pending request: {device_path}")
                logger.info("Auto-confirming in 5 seconds...")
                await asyncio.sleep(5)
                
                # Confirm pairing
                await manager.confirm_pairing(device_path, confirmed=True)
                logger.info("Pairing confirmed!")
                
                break
            
            await asyncio.sleep(1)
        
        # Keep running to complete pairing
        logger.info("Waiting for pairing to complete...")
        await asyncio.sleep(10)
    
    except KeyboardInterrupt:
        logger.info("\nStopping test...")
    
    finally:
        await manager.shutdown()


async def test_list_devices():
    """
    Test listing paired/connected devices.
    """
    manager = BluetoothManager()
    
    try:
        await manager.initialize(pairing_mode="secure")
        
        logger.info("Listing Bluetooth devices...")
        devices = await manager.get_devices()
        
        logger.info(f"\nFound {len(devices)} devices:")
        logger.info("=" * 60)
        
        for device in devices:
            logger.info(f"Name: {device['name']}")
            logger.info(f"  Address: {device['address']}")
            logger.info(f"  Paired: {device['paired']}")
            logger.info(f"  Connected: {device['connected']}")
            logger.info("-" * 60)
    
    finally:
        await manager.shutdown()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_mode = sys.argv[1]
    else:
        test_mode = "pairing"
    
    if test_mode == "pairing":
        asyncio.run(test_pairing())
    elif test_mode == "confirm":
        asyncio.run(test_manual_confirmation())
    elif test_mode == "list":
        asyncio.run(test_list_devices())
    else:
        print(f"Unknown test mode: {test_mode}")
        print("Usage: python test_pairing.py [pairing|confirm|list]")
        sys.exit(1)
