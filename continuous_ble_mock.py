#!/usr/bin/env python3
"""
Continuous BLE Mock Broadcaster for Android Emulator.
Simulates real Bluetooth devices continuously advertising.
"""

import json
import subprocess
import random
import time
import sys
from pathlib import Path
from datetime import datetime

# Configuration
INPUT_FILE = "bluetooth_devices.json"
# Use /data/local/tmp which is accessible without storage permissions
ANDROID_PATH = "/data/local/tmp/mock_bluetooth_devices.json"
ADB_PATH = Path.home() / "Library/Android/sdk/platform-tools/adb"

# Simulation settings
UPDATE_INTERVAL = 2.0  # seconds between updates
MIN_VISIBLE_DEVICES = 10  # minimum devices visible at once
RSSI_RANGE = (-50, -25)  # STRONG signal range (dBm) - close proximity
RSSI_FLUCTUATION = 5  # small RSSI change between updates (stable signal)


class BLEMockBroadcaster:
    def __init__(self):
        self.all_devices = {}
        self.visible_devices = {}
        self.device_rssi = {}  # track RSSI per device
        
    def load_devices(self):
        """Load all scanned devices from JSON file."""
        input_path = Path(INPUT_FILE)
        if not input_path.exists():
            print(f"❌ Input file not found: {INPUT_FILE}")
            print("   Run bluetooth_scanner.py first.")
            sys.exit(1)
            
        with open(input_path, "r") as f:
            self.all_devices = json.load(f)
        
        # Initialize RSSI for all devices
        for addr in self.all_devices:
            self.device_rssi[addr] = random.randint(*RSSI_RANGE)
            
        print(f"📂 Loaded {len(self.all_devices)} devices from {INPUT_FILE}")
        
        # Get named devices for display
        named = [d for d in self.all_devices.values() if d.get("name") != "Unknown"]
        print(f"   Named devices: {len(named)}")
        for d in named:
            print(f"   • {d['name']}")
    
    def check_adb(self):
        """Verify ADB connection."""
        try:
            result = subprocess.run(
                [str(ADB_PATH), "devices"],
                capture_output=True, text=True, check=True
            )
            lines = result.stdout.strip().split('\n')
            devices = [l for l in lines[1:] if l.strip() and 'device' in l]
            
            if not devices:
                print("❌ No emulator/device found!")
                return False
                
            print(f"✅ Connected to: {devices[0].split()[0]}")
            return True
            
        except FileNotFoundError:
            print(f"❌ ADB not found at {ADB_PATH}")
            return False
    
    def simulate_scan_cycle(self):
        """
        Simulate a BLE scan cycle:
        - Some devices appear/disappear randomly
        - RSSI values fluctuate
        - Named devices have higher visibility
        """
        all_addrs = list(self.all_devices.keys())
        
        # Determine how many devices are visible this cycle
        # Named devices are more likely to be visible
        named_addrs = [a for a, d in self.all_devices.items() if d.get("name") != "Unknown"]
        unknown_addrs = [a for a in all_addrs if a not in named_addrs]
        
        # Always include ALL named devices (100% visible)
        visible = named_addrs.copy()
        
        # Add random unknown devices
        num_unknown = random.randint(
            max(0, MIN_VISIBLE_DEVICES - len(visible)),
            min(len(unknown_addrs), 15)
        )
        visible.extend(random.sample(unknown_addrs, num_unknown))
        
        # Update visible devices with current timestamp and fluctuating RSSI
        self.visible_devices = {}
        now = datetime.now().isoformat()
        
        for addr in visible:
            device = self.all_devices[addr].copy()
            
            # Fluctuate RSSI (simulate movement/interference)
            current_rssi = self.device_rssi[addr]
            change = random.randint(-RSSI_FLUCTUATION, RSSI_FLUCTUATION)
            new_rssi = max(RSSI_RANGE[0], min(RSSI_RANGE[1], current_rssi + change))
            self.device_rssi[addr] = new_rssi
            
            self.visible_devices[addr] = {
                "address": addr,
                "name": device.get("name", "Unknown"),
                "rssi": new_rssi,
                "lastSeen": now,
                "firstSeen": device.get("first_seen", now),
                "timesSeen": device.get("times_seen", 1),
                "isConnectable": random.random() < 0.7  # 70% connectable
            }
        
        return self.visible_devices
    
    def push_to_emulator(self, devices: dict):
        """Push current visible devices to emulator."""
        # Convert to list format
        device_list = sorted(
            devices.values(),
            key=lambda x: (x["name"] == "Unknown", -x["rssi"])  # Named first, then by signal
        )
        
        # Write to temp file
        temp_file = Path("/tmp/mock_ble_live.json")
        with open(temp_file, "w") as f:
            json.dump(device_list, f, indent=2)
        
        # Push to emulator
        try:
            subprocess.run(
                [str(ADB_PATH), "push", str(temp_file), ANDROID_PATH],
                capture_output=True, check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Push failed: {e.stderr}")
            return False
    
    def broadcast_intent(self, devices: dict):
        """
        Broadcast an intent to notify the app of new scan results.
        Your Android app can register a BroadcastReceiver for this.
        """
        try:
            # Send broadcast intent with device count
            subprocess.run(
                [str(ADB_PATH), "shell", "am", "broadcast",
                 "-a", "com.mock.ble.SCAN_RESULT",
                 "--ei", "device_count", str(len(devices))],
                capture_output=True, check=True
            )
        except subprocess.CalledProcessError:
            pass  # Intent broadcast is optional
    
    def run(self):
        """Main broadcast loop."""
        print("\n" + "=" * 60)
        print("📡 Continuous BLE Mock Broadcaster")
        print("=" * 60)
        
        self.load_devices()
        
        if not self.check_adb():
            sys.exit(1)
        
        print(f"\n🔄 Broadcasting every {UPDATE_INTERVAL}s (Ctrl+C to stop)")
        print("-" * 60)
        
        cycle = 0
        try:
            while True:
                cycle += 1
                
                # Simulate scan
                visible = self.simulate_scan_cycle()
                
                # Push to emulator
                if self.push_to_emulator(visible):
                    # Count named devices
                    named = [d for d in visible.values() if d["name"] != "Unknown"]
                    
                    # Get best signal device
                    best = max(visible.values(), key=lambda x: x["rssi"])
                    
                    # Status line
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] Cycle {cycle}: {len(visible)} devices "
                          f"({len(named)} named) | "
                          f"Best: {best['name'][:20]} ({best['rssi']} dBm)")
                    
                    # Broadcast intent to notify app
                    self.broadcast_intent(visible)
                
                time.sleep(UPDATE_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("🛑 Broadcast stopped")
            print(f"   Total cycles: {cycle}")
            print("=" * 60)


def main():
    broadcaster = BLEMockBroadcaster()
    broadcaster.run()


if __name__ == "__main__":
    main()
