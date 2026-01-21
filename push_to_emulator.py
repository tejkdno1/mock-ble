#!/usr/bin/env python3
"""
Push Bluetooth scan results to Android Emulator.
Your Android app should read from this file to get mock Bluetooth devices.
"""

import json
import subprocess
import sys
from pathlib import Path

INPUT_FILE = "bluetooth_devices.json"
# Location on Android device/emulator where the file will be pushed
ANDROID_PATH = "/sdcard/Download/mock_bluetooth_devices.json"


def load_devices(filepath: Path) -> dict:
    """Load scanned devices from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def convert_to_android_format(devices: dict) -> list:
    """
    Convert to a simpler format for Android consumption.
    Returns a list of device objects.
    """
    android_devices = []
    for address, info in devices.items():
        android_devices.append({
            "address": address,
            "name": info.get("name", "Unknown"),
            "rssi": info.get("rssi"),
            "firstSeen": info.get("first_seen"),
            "lastSeen": info.get("last_seen"),
            "timesSeen": info.get("times_seen", 1)
        })
    
    # Sort by name (Unknown devices last)
    android_devices.sort(key=lambda x: (x["name"] == "Unknown", x["name"].lower()))
    return android_devices


def check_adb():
    """Check if ADB is available and an emulator is running."""
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.strip().split('\n')
        devices = [l for l in lines[1:] if l.strip() and 'device' in l]
        
        if not devices:
            print("❌ No Android devices/emulators found!")
            print("   Make sure your emulator is running.")
            return False
        
        print(f"✅ Found {len(devices)} Android device(s):")
        for d in devices:
            print(f"   - {d.split()[0]}")
        return True
        
    except FileNotFoundError:
        print("❌ ADB not found!")
        print("   Make sure Android SDK platform-tools is in your PATH.")
        print("   Typically: ~/Library/Android/sdk/platform-tools")
        return False


def push_to_device(data: list, android_path: str):
    """Push the JSON data to the Android device."""
    # Create temp file
    temp_file = Path("/tmp/mock_bluetooth_devices.json")
    with open(temp_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"\n📤 Pushing to {android_path}...")
    
    try:
        result = subprocess.run(
            ["adb", "push", str(temp_file), android_path],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Success! File pushed to emulator.")
        print(f"   Path: {android_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to push file: {e.stderr}")
        return False


def main():
    print("=" * 60)
    print("📱 Bluetooth Mock Data Pusher for Android Emulator")
    print("=" * 60)
    
    # Check input file
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        print(f"❌ Input file not found: {INPUT_FILE}")
        print("   Run bluetooth_scanner.py first to generate device data.")
        sys.exit(1)
    
    # Load and convert devices
    print(f"\n📂 Loading devices from {INPUT_FILE}...")
    devices = load_devices(input_path)
    print(f"   Found {len(devices)} unique devices")
    
    android_data = convert_to_android_format(devices)
    
    # Show preview
    named_devices = [d for d in android_data if d["name"] != "Unknown"]
    print(f"\n📋 Named devices ({len(named_devices)}):")
    for d in named_devices:
        print(f"   • {d['name']} ({d['address'][:8]}...)")
    
    print(f"   + {len(android_data) - len(named_devices)} unknown devices")
    
    # Check ADB
    print("\n🔍 Checking ADB connection...")
    if not check_adb():
        # Still save the file locally for manual transfer
        output_file = Path("mock_bluetooth_devices.json")
        with open(output_file, "w") as f:
            json.dump(android_data, f, indent=2)
        print(f"\n💾 Saved locally to: {output_file.absolute()}")
        print("   You can manually copy this file to your emulator/device.")
        sys.exit(1)
    
    # Push to device
    push_to_device(android_data, ANDROID_PATH)
    
    print("\n" + "=" * 60)
    print("📝 In your Android app, read from:")
    print(f"   {ANDROID_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
