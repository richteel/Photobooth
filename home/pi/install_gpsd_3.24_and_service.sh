#!/bin/bash
set -e

# Customize this if needed
GPSD_DEVICE="/dev/ttyACM0"
INSTALL_DIR=~/gpsd_build
GPSD_VERSION_TAG="release-3.24"

echo "📡 Installing gpsd $GPSD_VERSION_TAG and setting up custom service..."

# Step 1: Clean and update
sudo systemctl stop gpsd.socket || true
sudo systemctl disable gpsd.socket || true
sudo apt-get remove -y gpsd gpsd-clients || true
sudo apt-get update
sudo apt-get install -y git scons libncurses-dev python3-dev python3-setuptools \
  python3-pip libusb-1.0-0-dev pps-tools

# Step 2: Clone gpsd
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"
if [ ! -d gpsd ]; then
  git clone https://gitlab.com/gpsd/gpsd.git
fi
cd gpsd
git fetch
git checkout "$GPSD_VERSION_TAG"

# Step 3: Build and install
scons
sudo scons install
sudo ldconfig

# Step 4: Create custom systemd service
echo "🛠️ Creating systemd service..."

SERVICE_FILE="/etc/systemd/system/gpsd-custom.service"
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Custom GPSD Service (manual launch)
After=network.target

[Service]
ExecStart=/usr/local/sbin/gpsd -n -N -D 2 -b $GPSD_DEVICE
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Step 5: Enable the new service
sudo systemctl daemon-reload
sudo systemctl enable gpsd-custom.service
sudo systemctl start gpsd-custom.service

echo "✅ gpsd installed and running. Use 'systemctl status gpsd-custom.service' to check."

echo "Make it executable: chmod +x install_gpsd_3.24_and_service.sh"
echo "Run it with: ./install_gpsd_3.24_and_service.sh"