# BluetoothManager - Architecture Overview

Refactored Bluetooth functionality with secure pairing and profile support.

## 📁 Structure

```
BluetoothManager/
├── BluetoothManager.py           # Central manager for all BT operations
├── agents/
│   ├── PairingAgentBase.py       # Abstract base for pairing agents
│   └── SecurePairingAgent.py     # Secure pairing with PIN display
├── profiles/
│   ├── BaseProfile.py            # Abstract base for BT profiles
│   └── HidRemoteProfile.py       # Android TV / Fire TV Remote
└── services/
    └── hid/
        ├── RemoteHidService.py   # HID service for remote control
        └── descriptors/
            └── RemoteDescriptor.py # HID Report Map
```

## 🎯 Key Features

### ✅ Secure Pairing
- PIN display and user confirmation
- Persistent bonding (survives reboots)
- API callbacks for pairing events
- WebSocket integration ready

### ✅ Wake-from-Sleep
- RemoteWake flag enabled in HID descriptor
- Persistent bond required
- Tested with Fire TV and Android TV

### ✅ Profile Architecture
- Extensible design for multiple profiles
- Easy to add new device types
- Profile switching at runtime

### ✅ API-First Design
- All operations accessible via REST API
- WebSocket for real-time pairing events
- Test scripts for standalone testing

## 🚀 Quick Start

### 1. Testing (Standalone)

```bash
# Test pairing
python test/bluetooth/test_pairing.py pairing

# Test remote control
python test/bluetooth/test_remote_profile.py interactive
```

See [test/bluetooth/README.md](../../test/bluetooth/README.md) for detailed testing guide.

### 2. Integration with RemoteController

```python
# In RemoteController.py

from BluetoothManager.BluetoothManager import BluetoothManager

class RemoteController:
    @classmethod
    async def create(cls, ...):
        self = cls()
        
        # Replace old BleKeyboard
        # self.ble_keyboard = await BleKeyboard.create()
        
        # Use new BluetoothManager
        self.bluetooth_manager = BluetoothManager()
        await self.bluetooth_manager.initialize(pairing_mode="secure")
        
        # Register pairing callback for WebSocket
        self.bluetooth_manager.register_pairing_callback(
            self._handle_bluetooth_pairing_event
        )
        
        # Activate default profile
        await self.bluetooth_manager.activate_profile("remote")
        
        return self
    
    async def _handle_bluetooth_pairing_event(self, event_data: dict):
        """Forward pairing events to WebSocket clients"""
        if self.status_callback:
            await self.status_callback({
                "type": "bluetooth_pairing",
                "data": event_data
            })
```

### 3. API Integration

```python
# In Api/app.py or main.py

from BluetoothManager.BluetoothManager import BluetoothManager

async def startup_event():
    # Initialize BluetoothManager
    app.state.bluetooth_manager = BluetoothManager()
    await app.state.bluetooth_manager.initialize(pairing_mode="secure")
    
    # Or pass to RemoteController
    controller = await RemoteController.create(...)
    app.state.controller = controller
```

Add router in `Api/app.py`:
```python
from Api.routers import bluetooth_v2_example as bluetooth_v2

app.include_router(bluetooth_v2.router)
```

## 📡 Pairing Flow

### User initiates pairing from device (e.g., Fire TV):

```
1. Fire TV: Settings → Add Bluetooth Device
2. API: POST /bluetooth/v2/advertise
3. Fire TV: Selects "Equilibrium Remote"
4. BlueZ: Pairing initiated
5. SecurePairingAgent: Generates PIN
6. WebSocket: Sends pairing event to frontend
   {
     "type": "display_passkey",
     "device": {"name": "Fire TV", "address": "AA:BB:CC:DD:EE:FF"},
     "pin": "123456",
     "message": "Enter PIN on Fire TV: 123456"
   }
7. Frontend: Shows PIN dialog
8. User: Enters PIN on Fire TV
9. BlueZ: Pairing complete
10. API: Device trusted (persistent bond)
11. WebSocket: Pairing success event
```

### User initiates pairing from Equilibrium:

```
1. API: POST /bluetooth/v2/pair {"device_address": "AA:BB:CC:DD:EE:FF"}
2. BlueZ: Connection + pairing initiated
3. SecurePairingAgent: PIN flow (see above)
4. API: POST /bluetooth/v2/pair/confirm {"device_path": "...", "confirmed": true}
5. Pairing complete
```

## 🎮 Sending Commands

### Via API:

```bash
# Click HOME button
curl -X POST http://localhost:8000/bluetooth/v2/command \
  -H "Content-Type: application/json" \
  -d '{"button": "HOME", "action": "click"}'

# Navigate up
curl -X POST http://localhost:8000/bluetooth/v2/command \
  -d '{"button": "DPAD_UP", "action": "click"}'

# Long press (3 seconds)
curl -X POST http://localhost:8000/bluetooth/v2/command \
  -d '{"button": "HOME", "action": "click", "duration": 3.0}'

# Press and hold
curl -X POST http://localhost/v2/command -d '{"button": "VOLUME_UP", "action": "press"}'
# ... wait ...
curl -X POST http://localhost/v2/command -d '{"button": "VOLUME_UP", "action": "release"}'
```

### Via Python:

```python
await bluetooth_manager.send_command({
    "button": "HOME",
    "action": "click"
})
```

## 🔧 Available Buttons

### Navigation
- `DPAD_UP`, `DPAD_DOWN`, `DPAD_LEFT`, `DPAD_RIGHT`
- `SELECT` (OK/Enter)
- `BACK`, `HOME`, `MENU`

### Media Control
- `PLAY_PAUSE`, `STOP`
- `FAST_FORWARD`, `REWIND`

### Volume
- `VOLUME_UP`, `VOLUME_DOWN`, `MUTE`

### Other
- `POWER`

See [services/hid/descriptors/RemoteDescriptor.py](services/hid/descriptors/RemoteDescriptor.py) for complete list.

## 🔄 Migration from BleKeyboard

### Old Code:
```python
self.ble_keyboard = await BleKeyboard.create()
await self.ble_keyboard.advertise()
await self.ble_keyboard.send_key("HOME")
```

### New Code:
```python
self.bluetooth_manager = BluetoothManager()
await self.bluetooth_manager.initialize()
await self.bluetooth_manager.activate_profile("remote")
await self.bluetooth_manager.advertise()
await self.bluetooth_manager.send_command({"button": "HOME", "action": "click"})
```

### Benefits:
- ✅ Secure pairing instead of NoIoAgent
- ✅ Better wake-from-sleep support
- ✅ Profile switching (remote, keyboard, etc.)
- ✅ Cleaner API
- ✅ Better testability

## 🎨 Frontend Integration

WebSocket pairing event handling:

```typescript
socket.on('bluetooth_pairing', (event) => {
  switch(event.type) {
    case 'display_passkey':
      showPinDialog(event.device.name, event.pin);
      break;
    
    case 'confirm_passkey':
      showConfirmDialog(event.device.name, event.pin);
      break;
    
    case 'pairing_cancelled':
      closePairingDialog();
      showError(event.message);
      break;
  }
});

// User confirms pairing
async function confirmPairing(devicePath: string, confirmed: boolean) {
  await fetch('/bluetooth/v2/pair/confirm', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({device_path: devicePath, confirmed})
  });
}
```

## 🔮 Future Enhancements (Phase 2)

### Receiver Mode
Act as HID host to receive commands from physical remotes:

```python
# profiles/ReceiverProfile.py
class ReceiverProfile(BaseProfile):
    async def listen_for_commands(self):
        """Receive button presses from physical remote"""
        # Listen on HID reports
        # Forward to RemoteController command queue
```

### Additional Profiles
- `HidKeyboardProfile` - Refactored keyboard (Apple TV)
- `HidGamepadProfile` - Game controller
- `HidMouseProfile` - Mouse/trackpad

## 📚 Documentation

- [Test Scripts README](../../test/bluetooth/README.md)
- [API Models](../../Api/models/Bluetooth.py)
- [Example Router](../../Api/routers/bluetooth_v2_example.py)

## 🐛 Troubleshooting

### Common Issues

**"No adapter found"**
```bash
sudo systemctl restart bluetooth
bluetoothctl power on
```

**"Permission denied"**
```bash
sudo usermod -a -G bluetooth $USER
# Log out and back in
```

**Pairing fails**
- Check SecurePairingAgent is used (not NoIoAgent)
- Verify device supports BLE HID
- Remove old pairings: `bluetoothctl remove <address>`

**Buttons don't work**
- Ensure profile is activated
- Check device is connected: `GET /bluetooth/v2/devices`
- Verify HID service is registered (check logs)

## 📝 License

Part of Equilibrium project.
