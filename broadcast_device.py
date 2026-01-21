#!/usr/bin/env python3
"""
Interactive BLE Broadcaster - Choose which device to broadcast to your Android phone.
"""

import sys
from pathlib import Path

# Add venv packages
for p in (Path(__file__).parent / 'venv' / 'lib').glob('python*/site-packages'):
    sys.path.insert(0, str(p))

import objc
from Foundation import NSObject, NSRunLoop, NSDate
from CoreBluetooth import (
    CBPeripheralManager,
    CBAdvertisementDataLocalNameKey,
    CBAdvertisementDataServiceUUIDsKey,
    CBUUID
)

# Your Bluetooth devices
DEVICES = [
    "Bose Color II SoundLink",
    "Teja's Keys",
    "Teja's Xbox",
    "Tejkdno1",
]


class BLEDelegate(NSObject):
    ready = objc.ivar('ready', objc._C_BOOL)
    advertising = objc.ivar('advertising', objc._C_BOOL)
    
    def init(self):
        self = objc.super(BLEDelegate, self).init()
        if self:
            self.ready = False
            self.advertising = False
        return self
    
    def peripheralManagerDidUpdateState_(self, pm):
        if pm.state() == 5:  # PoweredOn
            self.ready = True
    
    def peripheralManagerDidStartAdvertising_error_(self, pm, error):
        if error:
            print(f"   ❌ Error: {error}")
        else:
            self.advertising = True


def show_menu():
    """Display device selection menu."""
    print()
    print("=" * 55)
    print("📡 BLE Device Broadcaster")
    print("=" * 55)
    print()
    print("Select a device to broadcast to your Android phone:")
    print()
    
    for i, device in enumerate(DEVICES, 1):
        print(f"  [{i}] {device}")
    
    print()
    print("  [0] Exit")
    print()


def broadcast_device(pm, delegate, device_name):
    """Broadcast the selected device."""
    
    # Stop any existing advertising
    pm.stopAdvertising()
    delegate.advertising = False
    
    # Wait a moment
    for _ in range(5):
        NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.1))
    
    # Service UUID for better discoverability
    service_uuid = CBUUID.UUIDWithString_('180A')
    
    # Start advertising
    ad_data = {
        CBAdvertisementDataLocalNameKey: device_name,
        CBAdvertisementDataServiceUUIDsKey: [service_uuid]
    }
    
    pm.startAdvertising_(ad_data)
    
    # Wait for advertising to start
    for _ in range(20):
        NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.1))
        if delegate.advertising:
            break
    
    if delegate.advertising:
        print()
        print("=" * 55)
        print(f"✅ NOW BROADCASTING: {device_name}")
        print("=" * 55)
        print()
        print("On your Android phone:")
        print("  1. Go to Settings > Connected devices")
        print("  2. Tap 'Pair new device'")
        print(f"  3. Look for '{device_name}'")
        print()
        print("Press Enter to stop and choose another device...")
        print("(or Ctrl+C to exit)")
        print()
        
        # Keep advertising until user presses Enter
        try:
            import select
            import threading
            
            stop_flag = threading.Event()
            
            def wait_for_input():
                input()
                stop_flag.set()
            
            input_thread = threading.Thread(target=wait_for_input, daemon=True)
            input_thread.start()
            
            seconds = 0
            while not stop_flag.is_set():
                NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(1.0))
                seconds += 1
                if seconds % 10 == 0:
                    print(f"   📡 Still broadcasting '{device_name}'... ({seconds}s)")
            
        except EOFError:
            # No input available, just broadcast for 60 seconds
            for i in range(60):
                NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(1.0))
                if i % 10 == 0:
                    print(f"   📡 Broadcasting... ({60-i}s remaining)")
        
        pm.stopAdvertising()
        delegate.advertising = False
        print()
        print("   🛑 Stopped broadcasting")
        
    else:
        print("   ❌ Failed to start advertising")


def main():
    print()
    print("Initializing Mac Bluetooth...")
    
    # Initialize Bluetooth
    delegate = BLEDelegate.alloc().init()
    pm = CBPeripheralManager.alloc().initWithDelegate_queue_(delegate, None)
    
    # Wait for Bluetooth to be ready
    for _ in range(40):
        NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.1))
        if delegate.ready:
            break
    
    if not delegate.ready:
        print("❌ Bluetooth not available!")
        print("   Make sure Bluetooth is ON on your Mac")
        return
    
    print("✅ Bluetooth ready!")
    
    # Main loop
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-4, or 0 to exit): ").strip()
            
            if choice == '0' or choice.lower() == 'exit':
                print()
                print("👋 Goodbye!")
                break
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(DEVICES):
                    device_name = DEVICES[index]
                    broadcast_device(pm, delegate, device_name)
                else:
                    print("   ⚠️ Invalid choice. Please enter 1-4.")
            except ValueError:
                print("   ⚠️ Please enter a number.")
                
        except KeyboardInterrupt:
            print()
            print()
            print("👋 Goodbye!")
            break
        except EOFError:
            break
    
    pm.stopAdvertising()


if __name__ == "__main__":
    main()
