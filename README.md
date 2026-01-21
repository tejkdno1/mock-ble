# Mock BLE 📡

A Python Bluetooth scanner that continuously discovers BLE devices and exports them for Android emulator testing.

## Features

- 🔄 **Continuous Scanning** - Runs until you quit (Ctrl+C)
- 📝 **Auto-Save** - Saves all discovered devices to JSON
- 📱 **Android Integration** - Push mock data to emulators via ADB
- 🕐 **Tracking** - Records first seen, last seen, and times seen for each device

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Scanner

```bash
python3 bluetooth_scanner.py
```

Press `Ctrl+C` to stop. Results are saved to `bluetooth_devices.json`.

### 3. Push to Android Emulator

```bash
python3 push_to_emulator.py
```

This pushes the discovered devices to `/sdcard/Download/mock_bluetooth_devices.json` on your emulator.

## Android Integration

Copy the files from `android_example/` into your Android project:

- `MockBluetoothManager.kt` - Loads mock devices from JSON
- `BluetoothScanActivity.kt` - Example activity with mock/real switching

### Usage in Kotlin

```kotlin
val manager = MockBluetoothManager(context)
val devices = manager.getMockDevices()

devices.forEach { device ->
    println("${device.name} - ${device.address}")
}
```

### Required Permission

Add to `AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
```

## Output Format

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
    "rssi": -65,
    "firstSeen": "2026-01-21T10:30:00",
    "lastSeen": "2026-01-21T10:35:00",
    "timesSeen": 5
  }
]
```

## Requirements

- Python 3.7+
- macOS, Linux, or Windows
- Bluetooth adapter (for scanning)
- ADB (for pushing to Android emulator)

## License

MIT
