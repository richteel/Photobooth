#!/bin/bash
# VK-172 USB GPS dongle was having issues sending messages
# dmesg | tail -n 20
# Showed that the USB Bus was having with dwc_otg_hcd_urb_dequeue
# The following commands mimic unplugging the USB and plugging it back in.

# Look for a serial device with 'u-blox' in the ID string
DEVICE_PATH=$(readlink -f /dev/serial/by-id/*u-blox*)

# Extract the most specific USB path (e.g. 1-1.3)
USB_ID=$(udevadm info -a -n "$DEVICE_PATH" | awk -F'"' '/KERNELS=="1-/ { if ($2 !~ /:/) { print $2; exit } }')

# Log what we found (optional for debugging)
echo "Reinitializing USB device at $USB_ID"

# Rebind to simulate replug
echo "$USB_ID" > /sys/bus/usb/drivers/usb/unbind
sleep 1
echo "$USB_ID" > /sys/bus/usb/drivers/usb/bind


sleep 5  # wait for USB to settle
# ubxtool -f /dev/ttyACM0 -P 14 -p CFG-MSG,240,0,1   # GGA
# ubxtool -f /dev/ttyACM0 -P 14 -p CFG-MSG,240,4,1   # RMC
# ubxtool -f /dev/ttyACM0 -P 14 -p CFG-MSG,240,2,1   # GSA
# ubxtool -f /dev/ttyACM0 -P 14 -p CFG-MSG,240,3,1   # GSV
# ubxtool -f /dev/ttyACM0 -P 14 -p CFG-PRT,3,0,0,0,0,0,0  # ensure USB outputs NMEA

# The following command seemed to make no difference.
# If enabled systemctl will show errors but that is to be expected
# gpsctl -s -f /dev/ttyACM0


# Disable system-wide USB power management for GPS stability
echo "Configuring system USB power management..."
# Disable USB autosuspend globally (temporary)
echo -1 > /sys/module/usbcore/parameters/autosuspend 2>/dev/null || true

# Check if ttyACM0 exists and is accessible
if [ ! -c /dev/ttyACM0 ]; then
    echo "ERROR: /dev/ttyACM0 not found after USB reset"
    logger "GPS Setup: ERROR - /dev/ttyACM0 not found after USB reset"
    exit 1
fi

# echo "Performing GPS factory reset..."
# logger "GPS Setup: Performing factory reset"
# ubxtool -f /dev/ttyACM0 -v 2 -p RESET,1
sleep 5  # wait for USB to settle