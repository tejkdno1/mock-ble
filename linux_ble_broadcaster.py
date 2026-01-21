#!/usr/bin/env python3
"""
Linux BLE Broadcaster - Broadcasts mock BLE devices using BlueZ.

Your Android phone will see these devices in Settings > Bluetooth > Pair new device.

Requirements:
  - Linux with Bluetooth adapter
  - BlueZ installed (usually pre-installed)
  - Python 3.7+
  - Run as root or with sudo

Install dependencies:
  pip3 install dbus-python PyGObject

Usage:
  sudo python3 linux_ble_broadcaster.py
"""

import subprocess
import sys
import time
import signal

# Your BLE devices
DEVICES = [
    "Bose Color II SoundLink",
    "Teja's Keys",
    "Teja's Xbox",
    "Tejkdno1",
]


def check_bluetooth():
    """Check if Bluetooth is available and powered on."""
    try:
        result = subprocess.run(
            ["bluetoothctl", "show"],
            capture_output=True, text=True, timeout=5
        )
        if "Powered: yes" not in result.stdout:
            print("⚠️  Bluetooth is OFF. Turning it on...")
            subprocess.run(["bluetoothctl", "power", "on"], timeout=5)
            time.sleep(1)
        return True
    except FileNotFoundError:
        print("❌ bluetoothctl not found. Install BlueZ:")
        print("   sudo apt install bluez")
        return False
    except Exception as e:
        print(f"❌ Error checking Bluetooth: {e}")
        return False


def set_device_name(name):
    """Set the Bluetooth device name."""
    try:
        # Using bluetoothctl to set name
        subprocess.run(
            ["bluetoothctl", "system-alias", name],
            capture_output=True, timeout=5
        )
        return True
    except Exception as e:
        print(f"Error setting name: {e}")
        return False


def start_advertising_hcitool(name):
    """Start BLE advertising using hcitool (legacy method)."""
    try:
        # Encode device name for advertising data
        name_bytes = name.encode('utf-8')[:20]  # Max 20 bytes for name
        name_hex = name_bytes.hex()
        name_len = len(name_bytes)
        
        # Build advertising data
        # Format: Length, Type, Data
        # 0x02 0x01 0x06 = Flags (LE General Discoverable)
        # name_len+1, 0x09, name = Complete Local Name
        flags = "02 01 06"
        name_ad = f"{name_len + 1:02x} 09 {name_hex}"
        
        # Pad to 31 bytes
        ad_data = f"{flags} {name_ad}"
        ad_bytes = bytes.fromhex(ad_data.replace(" ", ""))
        padded = ad_bytes.ljust(31, b'\x00')
        ad_hex = " ".join(f"{b:02x}" for b in padded)
        
        # Stop any existing advertising
        subprocess.run(
            ["hciconfig", "hci0", "noleadv"],
            capture_output=True, timeout=5
        )
        
        # Set advertising data
        subprocess.run(
            ["hcitool", "-i", "hci0", "cmd", "0x08", "0x0008"] + ad_hex.split(),
            capture_output=True, timeout=5
        )
        
        # Enable advertising
        subprocess.run(
            ["hciconfig", "hci0", "leadv", "0"],
            capture_output=True, timeout=5
        )
        
        return True
    except Exception as e:
        print(f"hcitool error: {e}")
        return False


def start_advertising_btmgmt(name):
    """Start BLE advertising using btmgmt (modern method)."""
    try:
        # Set the name
        subprocess.run(
            ["btmgmt", "name", name],
            capture_output=True, timeout=5
        )
        
        # Power on
        subprocess.run(
            ["btmgmt", "power", "on"],
            capture_output=True, timeout=5
        )
        
        # Make discoverable
        subprocess.run(
            ["btmgmt", "discov", "yes"],
            capture_output=True, timeout=5
        )
        
        # Enable advertising
        subprocess.run(
            ["btmgmt", "advertising", "on"],
            capture_output=True, timeout=5
        )
        
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"btmgmt error: {e}")
        return False


def stop_advertising():
    """Stop BLE advertising."""
    try:
        subprocess.run(["hciconfig", "hci0", "noleadv"], capture_output=True, timeout=5)
        subprocess.run(["btmgmt", "advertising", "off"], capture_output=True, timeout=5)
    except:
        pass


def show_menu():
    """Display device selection menu."""
    print()
    print("=" * 55)
    print("📡 Linux BLE Broadcaster")
    print("=" * 55)
    print()
    print("Select a device to broadcast:")
    print()
    for i, device in enumerate(DEVICES, 1):
        print(f"  [{i}] {device}")
    print()
    print("  [0] Exit")
    print()


def broadcast_device(name):
    """Broadcast the selected device."""
    print()
    print(f"📡 Broadcasting: {name}")
    print()
    
    # Try btmgmt first (modern), fall back to hcitool (legacy)
    success = start_advertising_btmgmt(name)
    if not success:
        print("   Trying legacy hcitool method...")
        success = start_advertising_hcitool(name)
    
    if success:
        print("=" * 55)
        print(f"✅ NOW BROADCASTING: {name}")
        print("=" * 55)
        print()
        print("On your Android phone:")
        print("  Settings > Connected devices > Pair new device")
        print()
        print(f'Look for "{name}"')
        print()
        print("Press Enter to stop and choose another device...")
        
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass
        
        stop_advertising()
        print("🛑 Stopped broadcasting")
    else:
        print("❌ Failed to start advertising")
        print("   Make sure you're running as root (sudo)")


def main():
    print()
    print("Checking Bluetooth...")
    
    if not check_bluetooth():
        sys.exit(1)
    
    print("✅ Bluetooth ready!")
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n\n👋 Goodbye!")
        stop_advertising()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-4, or 0 to exit): ").strip()
            
            if choice == '0':
                print("\n👋 Goodbye!")
                stop_advertising()
                break
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(DEVICES):
                    broadcast_device(DEVICES[index])
                else:
                    print("   ⚠️ Invalid choice")
            except ValueError:
                print("   ⚠️ Please enter a number")
                
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Goodbye!")
            stop_advertising()
            break


if __name__ == "__main__":
    # Check if running as root
    import os
    if os.geteuid() != 0:
        print("⚠️  This script needs root privileges for BLE advertising.")
        print("   Run with: sudo python3 linux_ble_broadcaster.py")
        print()
    
    main()
