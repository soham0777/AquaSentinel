#!/usr/bin/env bash
# AquaSentinel - one-command setup for the Raspberry Pi.
#   cd ~/aquasentinel && bash install.sh      (then reboot)
# What it does:
#   1. installs Python serial support and Chromium
#   2. turns on the serial port for the SIM800L (and turns off the serial login console)
#   3. installs the AquaSentinel service so it starts on every boot and restarts if it ever stops
#   4. opens the dashboard full-screen on the monitor after login
set -e
APP="$(cd "$(dirname "$0")" && pwd)"
USER_NAME="${SUDO_USER:-$USER}"
HOME_DIR="$(getent passwd "$USER_NAME" | cut -d: -f6)"
say(){ printf "\n\033[1;36m==> %s\033[0m\n" "$1"; }

say "1/5  Installing packages (needs internet, about 2-5 minutes)"
sudo apt-get update -y
sudo apt-get install -y python3-serial
sudo apt-get install -y chromium-browser || sudo apt-get install -y chromium || true
sudo apt-get install -y unclutter || true

say "2/5  Serial port for the SIM800L (GPIO 14/15, pins 8 and 10)"
if command -v raspi-config >/dev/null; then
  sudo raspi-config nonint do_serial_cons 1   # no login shell on the serial port
  sudo raspi-config nonint do_serial_hw 0     # serial hardware on
fi
CFG=/boot/firmware/config.txt; [ -f "$CFG" ] || CFG=/boot/config.txt
grep -q '^enable_uart=1' "$CFG" || echo 'enable_uart=1' | sudo tee -a "$CFG" >/dev/null
# give the stable UART to pins 8/10 (Bluetooth is not used)
grep -q '^dtoverlay=disable-bt' "$CFG" || echo 'dtoverlay=disable-bt' | sudo tee -a "$CFG" >/dev/null
sudo systemctl disable --now hciuart 2>/dev/null || true
sudo usermod -aG dialout "$USER_NAME"

say "3/5  Background service (starts on boot, restarts by itself)"
sudo tee /etc/systemd/system/aquasentinel.service >/dev/null <<EOF
[Unit]
Description=AquaSentinel river monitor (1:5 live model)
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$APP
ExecStart=/usr/bin/python3 -m aquasentinel
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable aquasentinel.service

say "4/5  Dashboard opens full-screen after login"
chmod +x "$APP/kiosk/start-kiosk.sh" "$APP"/*.sh
mkdir -p "$HOME_DIR/.config/autostart"
cat > "$HOME_DIR/.config/autostart/aquasentinel-kiosk.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=AquaSentinel dashboard
Exec=$APP/kiosk/start-kiosk.sh
X-GNOME-Autostart-enabled=true
EOF
# Wayland desktops (labwc) on newer Raspberry Pi OS
if [ -d "$HOME_DIR/.config/labwc" ] || command -v labwc >/dev/null; then
  mkdir -p "$HOME_DIR/.config/labwc"
  grep -q start-kiosk "$HOME_DIR/.config/labwc/autostart" 2>/dev/null || echo "$APP/kiosk/start-kiosk.sh &" >> "$HOME_DIR/.config/labwc/autostart"
fi
chown -R "$USER_NAME":"$USER_NAME" "$HOME_DIR/.config" "$APP"
if command -v raspi-config >/dev/null; then
  sudo raspi-config nonint do_boot_behaviour B4 || true   # boot straight to the desktop, logged in
fi

say "5/5  Quick self-test of the decision engine"
python3 "$APP/tools/self_test.py" || true

IP=$(hostname -I | awk '{print $1}')
say "Done. Reboot now:   sudo reboot"
echo "After the reboot the dashboard opens by itself."
echo "From a phone or laptop on the same Wi-Fi:   http://$IP:8080"
echo "Status:   systemctl status aquasentinel     Live log:   journalctl -u aquasentinel -f"
