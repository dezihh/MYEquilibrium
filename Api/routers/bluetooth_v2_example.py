"""
Extended Bluetooth API Router (Example)

This shows how to integrate the new BluetoothManager with the API.
To use this, you would need to:
1. Initialize BluetoothManager in main.py
2. Pass it to RemoteController or directly to the API
3. Replace/extend the existing bluetooth.py router

This is a template - actual integration depends on your architecture decisions.
"""

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from Api.models.Bluetooth import (
    BluetoothCommandRequest,
    BluetoothPairingRequest,
    BluetoothPairingConfirmation,
    BluetoothAdvertiseRequest,
    BluetoothProfileInfo,
    BluetoothDevice
)

router = APIRouter(
    prefix="/bluetooth/v2",
    tags=["Bluetooth (New)"],
    responses={404: {"description": "Not found"}}
)


@router.get("/profiles", response_model=dict[str, BluetoothProfileInfo])
async def get_bluetooth_profiles(request: Request):
    """
    Get all available Bluetooth profiles.
    
    Returns:
        Dict of profile_name -> profile info
    """
    # Access BluetoothManager from app state or RemoteController
    bt_manager = request.app.state.bluetooth_manager
    
    profiles = bt_manager.get_available_profiles()
    return profiles


@router.post("/profile/activate")
async def activate_bluetooth_profile(profile_name: str, request: Request):
    """
    Activate a specific Bluetooth profile.
    
    Args:
        profile_name: Profile to activate (e.g., "remote", "keyboard")
    
    Returns:
        Success status
    """
    bt_manager = request.app.state.bluetooth_manager
    
    try:
        await bt_manager.activate_profile(profile_name)
        return {
            "success": True,
            "active_profile": profile_name,
            "message": f"Profile '{profile_name}' activated"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate profile: {str(e)}")


@router.post("/advertise")
async def start_bluetooth_advertisement(
    request_data: BluetoothAdvertiseRequest,
    request: Request
):
    """
    Start Bluetooth advertisement.
    Makes device discoverable for pairing.
    
    Args:
        request_data: Advertisement configuration
    
    Returns:
        Success status
    """
    bt_manager = request.app.state.bluetooth_manager
    
    try:
        await bt_manager.advertise(profile_name=request_data.profile)
        return {
            "success": True,
            "message": "Advertisement started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start advertising: {str(e)}")


@router.post("/advertise/stop")
async def stop_bluetooth_advertisement(request: Request):
    """
    Stop Bluetooth advertisement.
    
    Returns:
        Success status
    """
    bt_manager = request.app.state.bluetooth_manager
    
    try:
        await bt_manager.stop_advertising()
        return {
            "success": True,
            "message": "Advertisement stopped"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop advertising: {str(e)}")


@router.post("/command")
async def send_bluetooth_command(
    command: BluetoothCommandRequest,
    request: Request
):
    """
    Send a Bluetooth command (button press, etc.).
    
    Args:
        command: Command to send (button, action, duration)
    
    Returns:
        Success status
    """
    bt_manager = request.app.state.bluetooth_manager
    
    try:
        command_data = {
            "button": command.button,
            "action": command.action,
            "duration": command.duration
        }
        
        await bt_manager.send_command(command_data)
        
        return {
            "success": True,
            "message": f"Command '{command.button}' sent"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send command: {str(e)}")


@router.get("/devices", response_model=list[BluetoothDevice])
async def get_bluetooth_devices(request: Request):
    """
    Get all paired and connected Bluetooth devices.
    
    Returns:
        List of device information
    """
    bt_manager = request.app.state.bluetooth_manager
    
    try:
        devices = await bt_manager.get_devices()
        return devices
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get devices: {str(e)}")


@router.post("/pair")
async def pair_bluetooth_device(
    pairing_request: BluetoothPairingRequest,
    request: Request
):
    """
    Initiate pairing with a Bluetooth device.
    User will need to confirm via pairing events (WebSocket).
    
    Args:
        pairing_request: Device address and trust settings
    
    Returns:
        Success status
    """
    bt_manager = request.app.state.bluetooth_manager
    
    try:
        await bt_manager.pair_device(
            pairing_request.device_address,
            trust=pairing_request.trust
        )
        return {
            "success": True,
            "message": f"Pairing initiated with {pairing_request.device_address}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pairing failed: {str(e)}")


@router.post("/pair/confirm")
async def confirm_bluetooth_pairing(
    confirmation: BluetoothPairingConfirmation,
    request: Request
):
    """
    Confirm or reject a pairing request.
    Called in response to pairing events from WebSocket.
    
    Args:
        confirmation: Device path and confirmation status
    
    Returns:
        Success status
    """
    bt_manager = request.app.state.bluetooth_manager
    
    try:
        await bt_manager.confirm_pairing(
            confirmation.device_path,
            confirmation.confirmed
        )
        return {
            "success": True,
            "confirmed": confirmation.confirmed,
            "message": f"Pairing {'confirmed' if confirmation.confirmed else 'rejected'}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to confirm pairing: {str(e)}")


@router.get("/pair/pending")
async def get_pending_pairings(request: Request):
    """
    Get list of pending pairing requests awaiting confirmation.
    
    Returns:
        List of pending pairing requests
    """
    bt_manager = request.app.state.bluetooth_manager
    
    pending = bt_manager.get_pending_pairing_requests()
    return {
        "pending": pending,
        "count": len(pending)
    }


# Note: WebSocket integration for pairing events should be added to
# Api/routers/websockets.py to broadcast pairing events to connected clients
