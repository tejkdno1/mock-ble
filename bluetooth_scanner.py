#!/usr/bin/env python3
"""
Bluetooth Scanner - Continuously scans for Bluetooth devices and saves them to a file.
Press Ctrl+C to quit.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

try:
    from bleak import BleakScanner
except ImportError:
    print("Error: 'bleak' library not found.")
    print("Install it with: pip install bleak")
    exit(1)


OUTPUT_FILE = "bluetooth_devices.json"
SCAN_INTERVAL = 5  # seconds between scans


def load_existing_devices(filepath: Path) -> dict:
    """Load existing devices from file if it exists."""
    if filepath.exists():
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_devices(filepath: Path, devices: dict):
    """Save devices to JSON file."""
    with open(filepath, "w") as f:
        json.dump(devices, f, indent=2, default=str)


async def scan_bluetooth():
    """Perform a single Bluetooth scan and return discovered devices."""
    devices = await BleakScanner.discover(timeout=4.0)
    return devices


async def main():
    filepath = Path(OUTPUT_FILE)
    all_devices = load_existing_devices(filepath)
    
    print("=" * 60)
    print("🔵 Bluetooth Scanner Started")
    print("=" * 60)
    print(f"Output file: {filepath.absolute()}")
    print(f"Scan interval: {SCAN_INTERVAL} seconds")
    print("Press Ctrl+C to stop scanning and save results.")
    print("=" * 60)
    print()

    scan_count = 0
    
    try:
        while True:
            scan_count += 1
            timestamp = datetime.now().isoformat()
            
            print(f"[{timestamp}] Scan #{scan_count} - Searching for devices...")
            
            try:
                devices = await scan_bluetooth()
                
                new_count = 0
                updated_count = 0
                
                for device in devices:
                    address = device.address
                    name = device.name or "Unknown"
                    rssi = device.rssi if hasattr(device, 'rssi') else None
                    
                    device_info = {
                        "name": name,
                        "address": address,
                        "rssi": rssi,
                        "last_seen": timestamp,
                    }
                    
                    if address not in all_devices:
                        device_info["first_seen"] = timestamp
                        device_info["times_seen"] = 1
                        all_devices[address] = device_info
                        new_count += 1
                        print(f"  ✨ NEW: {name} ({address}) RSSI: {rssi}")
                    else:
                        all_devices[address]["last_seen"] = timestamp
                        all_devices[address]["rssi"] = rssi
                        all_devices[address]["times_seen"] = all_devices[address].get("times_seen", 1) + 1
                        if name != "Unknown" and all_devices[address].get("name") == "Unknown":
                            all_devices[address]["name"] = name
                        updated_count += 1
                
                # Save after each scan
                save_devices(filepath, all_devices)
                
                print(f"  Found {len(devices)} devices this scan ({new_count} new, {updated_count} updated)")
                print(f"  Total unique devices: {len(all_devices)}")
                print()
                
            except Exception as e:
                print(f"  ⚠️  Scan error: {e}")
                print()
            
            # Wait before next scan
            await asyncio.sleep(SCAN_INTERVAL)
            
    except KeyboardInterrupt:
        print()
        print("=" * 60)
        print("🛑 Scanner stopped by user")
        print("=" * 60)
        
        # Final save
        save_devices(filepath, all_devices)
        
        print(f"\n📊 Final Summary:")
        print(f"   Total scans performed: {scan_count}")
        print(f"   Total unique devices found: {len(all_devices)}")
        print(f"   Results saved to: {filepath.absolute()}")
        print()
        
        # Print all discovered devices
        if all_devices:
            print("📋 All Discovered Devices:")
            print("-" * 60)
            for addr, info in sorted(all_devices.items(), key=lambda x: x[1].get("name", "").lower()):
                name = info.get("name", "Unknown")
                rssi = info.get("rssi", "N/A")
                times = info.get("times_seen", 1)
                print(f"   {name}")
                print(f"      Address: {addr}")
                print(f"      RSSI: {rssi} dBm | Seen {times} time(s)")
                print()


if __name__ == "__main__":
    asyncio.run(main())
