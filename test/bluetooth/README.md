# Bluetooth Test Scripts

Test scripts for Bluetooth functionality in Equilibrium.

## Prerequisites

```bash
# Ensure Bluetooth is enabled
sudo systemctl start bluetooth

# Your user must be in the bluetooth group
sudo usermod -a -G bluetooth $USER
# Log out and back in for group changes to take effect

# Install Python dependencies (run once, from repo root)
pip install -r requirements.txt

# Run tests from repo root so imports work
cd /home/dezi/dev/MYEquilibrium
```

## Test Scripts

### 1. Pairing Test (`test_pairing.py`)

Tests secure pairing with PIN display.

```bash
# Basic pairing test
python test/bluetooth/test_pairing.py pairing

# Test manual confirmation
python test/bluetooth/test_pairing.py confirm

# List paired devices
python test/bluetooth/test_pairing.py list
```

**What it tests:**
- BluetoothManager initialization
- SecurePairingAgent registration
- Advertisement
- Pairing event handling
- PIN display
- User confirmation workflow

**Expected output:**
```
PAIRING EVENT: display_passkey
Device: Fire TV Stick (AA:BB:CC:DD:EE:FF)
PIN CODE: 123456
Message: Geben Sie diesen PIN auf 'Fire TV Stick' ein: 123456
```

### 2. Remote Control Test (`test_remote_profile.py`)

Tests Remote Control button sending.

```bash
# Test basic navigation buttons
python test/bluetooth/test_remote_profile.py basic

# Test media control buttons
python test/bluetooth/test_remote_profile.py media

# Test volume buttons
python test/bluetooth/test_remote_profile.py volume

# Test press-and-hold
python test/bluetooth/test_remote_profile.py hold

# Interactive mode (control with keyboard)
python test/bluetooth/test_remote_profile.py interactive

# Power on (toggle)
python test/bluetooth/test_remote_profile.py power_on

# Power off (toggle)
python test/bluetooth/test_remote_profile.py power_off

# Wake Android TV from sleep
python test/bluetooth/test_remote_profile.py wake

# Persistent connection test (for integration)
python test/bluetooth/test_remote_profile.py persistent
```

**What it tests:**
- Remote Control profile activation
- Button press/release/click
- D-Pad navigation
- Media controls
- Volume controls
- Long press functionality

**Interactive mode keys:**
- `w/a/s/d` - Navigate (Up/Left/Down/Right)
- `Enter` - Select/OK
- `Backspace` - Back
- `h` - Home
- `m` - Menu
- `Space` - Play/Pause
- `+/-` - Volume Up/Down
- `q` - Quit

### 3. Wake-from-Sleep Test (`test_remote_profile.py wake`)

Tests waking Android TV from sleep via Bluetooth connection.

```bash
python test/bluetooth/test_remote_profile.py wake
```

**Requirements:**
- Device must be **bonded and trusted** (run pairing test first)
- Device must be in sleep/standby mode
- Device Bluetooth address

**What it tests:**
- Device bonding and trust status check
- BLE connection to sleeping device (wakes it up)
- HOME button sent after wakeup to confirm

### 4. Persistent Connection Test (`test_remote_profile.py persistent`)

Tests maintaining a persistent connection loop for integration with RemoteController.

```bash
python test/bluetooth/test_remote_profile.py persistent
```

**What it tests:**
- Continuous connection status monitoring
- Auto-reconnect on disconnect
- Graceful error handling
- Integration-ready architecture

## Testing Workflow

### First-time Pairing

1. **Start pairing test:**
   ```bash
   python test/bluetooth/test_pairing.py pairing
   ```

2. **On your device (Fire TV / Android TV):**
   - Go to Settings → Remotes & Bluetooth Devices
   - Add Bluetooth Device
   - Select "Equilibrium Remote"

3. **In the terminal:**
   - You'll see the PIN code
   - Enter this PIN on your device

4. **Pairing complete!**
   - Device is now paired and trusted
   - Bond is persistent across reboots

### Testing Remote Control

1. **Ensure device is paired** (see above)

2. **Run basic button test:**
   ```bash
   python test/bluetooth/test_remote_profile.py basic
   ```

3. **Watch your TV:**
   - Home screen should appear
   - Navigation should work
   - Buttons should respond

4. **Try interactive mode:**
   ```bash
   python test/bluetooth/test_remote_profile.py interactive
   ```
   - Control your TV with your keyboard!

### Testing Wake-from-Sleep

1. **First ensure device is bonded:**
   ```bash
   python test/bluetooth/test_pairing.py pairing
   ```
   - Device will appear on TV with "Equilibrium Remote"
   - Enter PIN to complete bonding
   - Device is now bonded and trusted

2. **Put device in sleep/standby**

3. **Run wake test:**
   ```bash
   python test/bluetooth/test_remote_profile.py wake
   ```
   - Enter device Bluetooth address
   - Press Enter when TV is asleep
   - Script connects (wakes TV)
   - HOME button sent to confirm wakeup

### Testing Persistent Connection (For Integration)

This simulates how MYEquilibrium will maintain connection to the TV:

```bash
python test/bluetooth/test_remote_profile.py persistent
```

**Behavior:**
- Starts advertising with Remote Control profile
- Continuously monitors connection status
- Auto-reconnects if device disconnects
- Wakes device from sleep on reconnect attempt
- Useful for testing integration with RemoteController

**Key for Integration:**
- Device must be bonded first (pairing test)
- Connection loop handles sleep/wake automatically
- Ready for command sending while connected
- Graceful shutdown on Ctrl+C

## Troubleshooting

### "Permission denied" errors

```bash
# Add user to bluetooth group
sudo usermod -a -G bluetooth $USER

# Restart bluetooth service
sudo systemctl restart bluetooth
```

### "No adapter found"

```bash
# Check Bluetooth adapter status
bluetoothctl show

# Enable adapter
sudo bluetoothctl
[bluetooth]# power on
```

### Device won't pair

```bash
# Remove existing pairing
bluetoothctl
[bluetooth]# devices
[bluetooth]# remove AA:BB:CC:DD:EE:FF

# Try pairing again
```

### Buttons not working

1. Check device is connected:
   ```bash
   python test/bluetooth/test_pairing.py list
   ```

2. Verify profile is active:
   - Check logs for "Activated profile: remote"

3. Try reconnecting device

### PIN not displayed

- Ensure SecurePairingAgent is used (not NoIoAgent)
- Check logs for pairing events
- Verify callback is registered

## Debug Logging

Enable verbose logging:

```python
# In test script
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG for verbose output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Next Steps

Once tests pass:
1. Integrate with RemoteController
2. Add API endpoints
3. Create WebSocket integration for pairing UI
4. Test with production setup

## Known Issues

- **Apple TV:** Requires NoIoAgent, doesn't support PIN pairing
- **Some Android boxes:** May need manual pairing from device first
- **Bluetooth 4.0:** Minimum requirement for BLE HID

## Support

For issues, check:
1. System logs: `journalctl -u bluetooth -f`
2. BlueZ version: `bluetoothctl --version` (need 5.50+)
3. Python version: `python --version` (need 3.10+)
