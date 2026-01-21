# Mock BLE 📡

A comprehensive Bluetooth Low Energy (BLE) mocking solution for Android development and testing. Scan real BLE devices, convert them to mock data, and broadcast them to Android emulators or physical devices.

## Features

- 🔄 **Continuous BLE Scanning** - Scans and tracks BLE devices in real-time
- 📝 **Auto-Save** - Automatically saves discovered devices to JSON
- 📱 **Android Integration** - Push mock data to emulators via ADB
- 🎮 **Interactive Broadcasting** - Choose which device to broadcast to physical Android phones
- 🐧 **Linux Support** - Broadcast BLE devices from Linux machines
- 💻 **Mac Support** - Broadcast BLE devices from macOS
- 🕐 **Device Tracking** - Records first seen, last seen, and times seen for each device
- 📊 **Signal Simulation** - Realistic RSSI fluctuations and signal strength indicators

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Scan Real BLE Devices

```bash
python3 bluetooth_scanner.py
```

Press `Ctrl+C` to stop. Results are saved to `bluetooth_devices.json`.

### 3. Push to Android Emulator

```bash
python3 push_to_emulator.py
```

This pushes the discovered devices to `/data/local/tmp/mock_bluetooth_devices.json` on your emulator.

### 4. Continuous Broadcasting (For MockBLEApp)

```bash
python3 continuous_ble_mock.py
```

This continuously updates the mock data file on the emulator every 2 seconds with realistic signal fluctuations.

## Android App

### MockBLEApp

A complete Android app that displays mock BLE devices in a Bluetooth Settings-like interface.

**Build and Install:**

```bash
cd MockBLEApp
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
```

**Features:**
- Shows all mock devices with signal strength
- Connect/disconnect simulation
- Real-time updates every 1.5 seconds
- System Bluetooth Settings UI design

## Broadcasting to Physical Android Phones

### macOS Broadcasting

Broadcast BLE devices from your Mac that physical Android phones can see:

```bash
source venv/bin/activate
python3 broadcast_device.py
```

Then select which device to broadcast. Your Android phone will see it in **Settings > Connected devices > Pair new device**.

**Note:** macOS can only broadcast one device name at a time. If you see a real device with the same name, turn it off first.

### Linux Broadcasting

Broadcast BLE devices from a Linux machine:

**Option 1: Shell Script (Simplest)**
```bash
chmod +x linux_broadcast.sh
sudo ./linux_broadcast.sh "Teja's Xbox"
```

**Option 2: Python Script (Interactive)**
```bash
sudo python3 linux_ble_broadcaster.py
```

**Requirements:**
- BlueZ installed (`sudo apt install bluez`)
- Bluetooth adapter (built-in or USB)
- Root access (sudo)

## Project Structure

```
mock-ble/
├── bluetooth_scanner.py          # Scans real BLE devices
├── continuous_ble_mock.py         # Continuous broadcaster for emulator
├── push_to_emulator.py           # One-time push to emulator
├── broadcast_device.py           # Interactive Mac broadcaster
├── linux_ble_broadcaster.py      # Linux broadcaster (Python)
├── linux_broadcast.sh            # Linux broadcaster (Shell)
├── bluetooth_devices.json        # Scanned device data
├── mock_bluetooth_devices.json   # Android-formatted device data
├── MockBLEApp/                   # Android app
│   └── app/src/main/java/com/mockble/app/
│       ├── MainActivity.kt       # Main UI
│       ├── MockBLEScanner.kt    # Scanner implementation
│       └── BLEDevice.kt          # Device data model
└── android_example/              # Example Android code
    ├── MockBluetoothManager.kt
    └── BluetoothScanActivity.kt
```

## Usage Examples

### Example 1: Scan and Push to Emulator

```bash
# 1. Scan devices
python3 bluetooth_scanner.py
# Press Ctrl+C after scanning

# 2. Push to emulator
python3 push_to_emulator.py
```

### Example 2: Continuous Broadcasting for App Testing

```bash
# Terminal 1: Start continuous broadcaster
python3 continuous_ble_mock.py

# Terminal 2: Launch MockBLEApp on emulator
adb shell am start -n com.mockble.app/.MainActivity
```

### Example 3: Broadcast to Physical Phone (Mac)

```bash
source venv/bin/activate
python3 broadcast_device.py
# Select device from menu
# Check phone: Settings > Bluetooth > Pair new device
```

### Example 4: Broadcast to Physical Phone (Linux)

```bash
sudo ./linux_broadcast.sh "Teja's Xbox"
# Check phone: Settings > Bluetooth > Pair new device
```

## Output Formats

### bluetooth_devices.json (Scanner Output)

```json
{
  "AA:BB:CC:DD:EE:FF": {
    "name": "My Device",
    "address": "AA:BB:CC:DD:EE:FF",
    "rssi": -65,
    "first_seen": "2026-01-21T10:30:00",
    "last_seen": "2026-01-21T10:35:00",
    "times_seen": 5
  }
}
```

### mock_bluetooth_devices.json (Android Format)

```json
[
  {
    "address": "AA:BB:CC:DD:EE:FF",
    "name": "My Device",
    "rssi": -45,
    "firstSeen": "2026-01-21T10:30:00",
    "lastSeen": "2026-01-21T10:35:00",
    "timesSeen": 5,
    "isConnectable": true
  }
]
```

## Android Integration

### Using MockBLEScanner in Your App

```kotlin
val scanner = MockBLEScanner(context)

scanner.startScan(object : MockBLEScanner.ScanCallback {
    override fun onDevicesUpdated(devices: List<BLEDevice>) {
        // Update UI with devices
        updateDeviceList(devices)
    }
    
    override fun onScanError(message: String) {
        // Handle error
        showError(message)
    }
})

// Stop scanning
scanner.stopScan()
```

### File Location

The mock data file is read from:
- Primary: `/data/local/tmp/mock_bluetooth_devices.json` (accessible via ADB push)
- Fallback: `/sdcard/Download/mock_bluetooth_devices.json` (requires storage permissions)

## Configuration

### Signal Strength Settings

Edit `continuous_ble_mock.py`:

```python
RSSI_RANGE = (-50, -25)  # Signal strength range (dBm)
RSSI_FLUCTUATION = 5     # Max RSSI change between updates
UPDATE_INTERVAL = 2.0    # Seconds between updates
```

### Device Visibility

All named devices are always visible (100% chance). Unknown devices appear randomly.

## Requirements

- Python 3.7+
- macOS, Linux, or Windows
- Bluetooth adapter (for scanning)
- ADB (for pushing to Android emulator)
- Android SDK (for building MockBLEApp)

### Python Dependencies

- `bleak` - BLE scanning
- `bumble` - BLE advertising (for Mac/Linux broadcasting)
- `pyobjc-framework-CoreBluetooth` - macOS CoreBluetooth (for Mac broadcasting)

### Linux Dependencies

- `bluez` - Bluetooth stack
- `bluetoothctl` - Bluetooth control tool
- `hciconfig` - HCI configuration (legacy)
- `btmgmt` - Bluetooth management (modern)

## Limitations

### Android Emulator

- **Cannot show fake devices in system Bluetooth settings** - This is a hardware limitation
- Use **MockBLEApp** instead - it shows all devices with full functionality
- System-wide Bluetooth mocking requires real hardware

### macOS Broadcasting

- Can only broadcast **one device name at a time**
- If a real device with the same name is nearby, turn it off first
- Requires Bluetooth to be enabled

### Linux Broadcasting

- Requires root access (sudo)
- Needs BlueZ installed
- Requires a Bluetooth adapter

## Troubleshooting

### "No devices found" in MockBLEApp

1. Check if broadcaster is running: `ps aux | grep continuous_ble_mock`
2. Verify file exists: `adb shell ls -la /data/local/tmp/mock_bluetooth_devices.json`
3. Check app logs: `adb logcat -s MockBLEScanner:D`

### "Permission denied" when pushing to emulator

The script automatically uses `/data/local/tmp/` which doesn't require permissions. If issues persist:
- Check ADB connection: `adb devices`
- Verify emulator is running

### Linux broadcasting not working

1. Check Bluetooth adapter: `hciconfig`
2. Verify BlueZ is installed: `bluetoothctl --version`
3. Ensure running as root: `sudo`
4. Check adapter is powered: `bluetoothctl show`

### Mac broadcasting only shows one device

This is expected - macOS can only advertise one device name at a time. The script cycles through devices. If you see a real device, turn it off.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT

## Author

Created for testing and development purposes.

## Acknowledgments

- Uses [Bumble](https://github.com/google/bumble) for BLE advertising
- Uses [Bleak](https://github.com/hbldh/bleak) for BLE scanning
- Android app uses Material Design components
