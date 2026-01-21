#!/bin/bash
#
# Linux BLE Broadcaster - Simple shell script version
# Broadcasts a BLE device name that Android phones can see
#
# Usage: sudo ./linux_broadcast.sh "Device Name"
# Example: sudo ./linux_broadcast.sh "Teja's Xbox"
#

DEVICE_NAME="${1:-Teja's Xbox}"

echo ""
echo "========================================"
echo "📡 Linux BLE Broadcaster"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root:"
    echo "   sudo $0 \"$DEVICE_NAME\""
    exit 1
fi

# Check if Bluetooth adapter exists
if ! hciconfig hci0 > /dev/null 2>&1; then
    echo "❌ No Bluetooth adapter found (hci0)"
    echo "   Make sure Bluetooth hardware is connected"
    exit 1
fi

# Power on Bluetooth
echo "🔵 Powering on Bluetooth..."
hciconfig hci0 up
sleep 1

# Set device name
echo "📝 Setting device name: $DEVICE_NAME"
btmgmt name "$DEVICE_NAME" 2>/dev/null || true

# Make discoverable
echo "👁️ Making discoverable..."
hciconfig hci0 piscan
btmgmt discov yes 2>/dev/null || true

# Enable advertising
echo "📡 Starting BLE advertising..."

# Method 1: Using btmgmt (modern)
btmgmt advertising on 2>/dev/null

# Method 2: Using hciconfig (legacy fallback)
hciconfig hci0 leadv 0 2>/dev/null || true

echo ""
echo "========================================"
echo "✅ NOW BROADCASTING: $DEVICE_NAME"
echo "========================================"
echo ""
echo "On your Android phone:"
echo "  Settings > Connected devices > Pair new device"
echo ""
echo "Look for \"$DEVICE_NAME\""
echo ""
echo "Press Ctrl+C to stop..."
echo ""

# Keep running until Ctrl+C
trap "echo ''; echo '🛑 Stopping...'; hciconfig hci0 noleadv 2>/dev/null; btmgmt advertising off 2>/dev/null; echo 'Done!'; exit 0" INT

while true; do
    sleep 1
done
