#!/bin/bash

# Configure GNSS system (GPS, SBAS, disable QZSS, enable GLONASS)
ubxtool -p CFG-GNSS,0,1,1,0,0 \
        -p CFG-GNSS,1,1,3,0,0 \
        -p CFG-GNSS,5,0,3,0,0 \
        -p CFG-GNSS,6,1,8,0,0 \
        -p CFG-RATE,1000,1 \
        -p CFG-NAV5,0,3,0,0,0,0,0,0,0 \
        -p CFG-PM2,1,0,0,0 \
        -d NMEA \
        -c 06,01,08,00,01,07,01,01,01,01,01 \
        --device /dev/ttyACM0

# Stop gpsd socket (if running)
systemctl stop gpsd.socket
systemctl disable gpsd.socket

# Launch gpsd in NMEA-safe mode
gpsd -n -N -D 2 -b /dev/ttyACM0