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
# echo "$USB_ID" > /sys/bus/usb/drivers/usb/unbind
# sleep 1
# echo "$USB_ID" > /sys/bus/usb/drivers/usb/bind

# sleep 5  # wait for USB to settle

# Check if ttyACM0 exists and is accessible
if [ ! -c /dev/ttyACM0 ]; then
    echo "ERROR: /dev/ttyACM0 not found after USB reset"
    logger "GPS Setup: ERROR - /dev/ttyACM0 not found after USB reset"
    exit 1
fi

# Wait until gpsd is running for 2 minutes
# timeout=120
# while ! systemctl is-active --quiet gpsd; do
#     echo "Waiting for gpsd to start..."
#     sleep 5
#     timeout=$((timeout - 5))
#     if [ $timeout -le 0 ]; then
#         echo "ERROR: gpsd did not start within the timeout period."
#         logger "GPS Setup: ERROR - gpsd did not start within the timeout period."
#         exit 1
#     fi
# done

# # Should not be necessary but just in case
# if ! systemctl is-active --quiet gpsd; then
#     echo "gpsd service is not active after starting."
#     logger "GPS Setup: ERROR - gpsd service is not active after starting."
#     exit 1
# fi

# # ubxtool -f /dev/ttyACM0 -P 14 -p CFG-MSG,240,0,1   # GGA
# # ubxtool -f /dev/ttyACM0 -P 14 -p CFG-MSG,240,4,1   # RMC
# # ubxtool -f /dev/ttyACM0 -P 14 -p CFG-MSG,240,2,1   # GSA
# # ubxtool -f /dev/ttyACM0 -P 14 -p CFG-MSG,240,3,1   # GSV
# # ubxtool -f /dev/ttyACM0 -P 14 -p CFG-PRT,3,0,0,0,0,0,0  # ensure USB outputs NMEA

# ubxtool -p CFG-MSG,240,0,1 --device /dev/ttyACM0        # GGA
# ubxtool -p CFG-MSG,240,4,1 --device /dev/ttyACM0        # RMC
# ubxtool -p CFG-MSG,240,2,1 --device /dev/ttyACM0        # GSA
# ubxtool -p CFG-MSG,240,3,1 --device /dev/ttyACM0        # GSV
# ubxtool -p CFG-PRT,3,0,0,0,0,0,0 --device /dev/ttyACM0        # ensure USB outputs NMEA

# # The following command seemed to make no difference.
# # If enabled systemctl will show errors but that is to be expected
# # gpsctl -s -f /dev/ttyACM0

# # sleep 5  # wait for USB to settle

# # Stop gpsd socket (if running)
# systemctl stop gpsd.socket
# systemctl disable gpsd.socket

# # Launch gpsd in NMEA-safe mode
# gpsd -n -N -D 2 -b /dev/ttyACM0