#!/usr/bin/env bash
# AquaSentinel - one-command setup for the Raspberry Pi (v2, 17 Nov 2026). Safe to run again at any time.
#
#   cd ~/aquasentinel && bash install.sh            full setup (asks before flashing the Nano)
#   bash install.sh --flash                          also flash the Nano firmware without asking
#   bash install.sh --no-kiosk                       no full-screen browser on the Pi (lightest: view from a phone/laptop)
#
# What it does, step by step (every step is logged to ~/aquasentinel-install.log):
#   1  checks the Pi, the power supply and the internet
#   2  installs only ready-made packages (apt): nothing is compiled on the Pi, no pip
#   3  serial port for the SIM800L
#   4  the Nano always gets the same name (/dev/aquasentinel-nano) and the modem manager keeps its hands off it
#   5  makes the Pi lighter: compressed memory swap, smaller system logs, unused services off
#   6  background service: starts on boot, restarts by itself, old CSV files cleaned after 90 days
#   7  full-screen dashboard (light mode) unless --no-kiosk
#   8  Nano firmware v2 (asks first)
#   9  cloud (Firebase) if secrets.json is present
#  10  self-test and a health report
set -uo pipefail
APP="$(cd "$(dirname "$0")" && pwd)"
USER_NAME="${SUDO_USER:-$USER}"
HOME_DIR="$(getent passwd "$USER_NAME" | cut -d: -f6)"
LOG="$HOME_DIR/aquasentinel-install.log"
FLASH=ask; KIOSK=1
for a in "$@"; do case "$a" in --flash) FLASH=yes;; --no-flash) FLASH=no;; --no-kiosk) KIOSK=0;; esac; done
exec > >(tee -a "$LOG") 2>&1
say(){ printf "\n\033[1;36m==> %s\033[0m\n" "$1"; }
ok(){ printf "   \033[32mOK\033[0m   %s\n" "$1"; }
warn(){ printf "   \033[33mNOTE\033[0m %s\n" "$1"; WARNINGS+=("$1"); }
WARNINGS=()
echo "AquaSentinel install $(date)"

# ---------------------------------------------------------------- 1
say "1/10  Checking the Pi"
MODEL=$(tr -d '\0' < /proc/device-tree/model 2>/dev/null || echo "unknown")
ok "model: $MODEL, $(free -m | awk '/Mem:/{print $2}') MB memory, Python $(python3 -V 2>&1 | cut -d' ' -f2)"
if command -v vcgencmd >/dev/null; then
  T=$(vcgencmd get_throttled | cut -d= -f2)
  if (( T & 0x50000 )); then warn "the power supply has been too weak since boot ($T). This makes the Pi slow and USB devices drop out. Use the official 5.1 V 2.5 A supply."; else ok "power supply fine ($T)"; fi
fi
ONLINE=1; curl -s -m 8 -o /dev/null https://deb.debian.org || ONLINE=0
[ $ONLINE = 1 ] && ok "internet available" || warn "no internet: packages already installed are kept, missing ones are skipped"

# ---------------------------------------------------------------- 2
say "2/10  Packages (ready-made, nothing compiled on the Pi)"
NEED=(python3-serial avrdude usbutils curl)
[ $KIOSK = 1 ] && NEED+=(unclutter)
OPTIONAL=(uhubctl)
# Raspberry Pi OS trixie already has compressed swap (rpi-swap / zram); add zram-tools only when nothing is there
if ! swapon --show 2>/dev/null | grep -q zram && ! dpkg -s rpi-swap >/dev/null 2>&1; then OPTIONAL+=(zram-tools); fi
missing=(); for p in "${NEED[@]}" "${OPTIONAL[@]}"; do dpkg -s "$p" >/dev/null 2>&1 || missing+=("$p"); done
if [ $KIOSK = 1 ] && ! command -v chromium-browser >/dev/null && ! command -v chromium >/dev/null; then missing+=(chromium); fi
if [ ${#missing[@]} -eq 0 ]; then ok "all packages already installed"
elif [ $ONLINE = 1 ]; then
  sudo apt-get update -y -qq
  for p in "${missing[@]}"; do
    if sudo apt-get install -y -qq --no-install-recommends "$p" >/dev/null 2>&1; then ok "installed $p"
    elif [ "$p" = chromium ] && sudo apt-get install -y -qq chromium-browser >/dev/null 2>&1; then ok "installed chromium-browser"
    else warn "could not install $p"; fi
  done
else warn "skipped: ${missing[*]}"; fi
python3 -c "import serial" 2>/dev/null && ok "Python serial support" || warn "python3-serial missing: the Nano cannot be read"

# ---------------------------------------------------------------- 3
say "3/10  Serial port for the SIM800L (GPIO 14/15, pins 8 and 10)"
CFG=/boot/firmware/config.txt; [ -f "$CFG" ] || CFG=/boot/config.txt
CMDLINE=/boot/firmware/cmdline.txt; [ -f "$CMDLINE" ] || CMDLINE=/boot/cmdline.txt
REBOOT=0
if command -v raspi-config >/dev/null; then
  sudo raspi-config nonint do_serial_cons 1 2>/dev/null   # no login shell on the serial port
  sudo raspi-config nonint do_serial_hw 0 2>/dev/null     # serial hardware on
fi
grep -q '^enable_uart=1' "$CFG" || { echo 'enable_uart=1' | sudo tee -a "$CFG" >/dev/null; REBOOT=1; }
grep -q '^dtoverlay=disable-bt' "$CFG" || { echo 'dtoverlay=disable-bt' | sudo tee -a "$CFG" >/dev/null; REBOOT=1; }
sudo systemctl disable --now hciuart 2>/dev/null || true
sudo usermod -aG dialout "$USER_NAME"
ok "serial port ready (pins 8/10), user $USER_NAME in group dialout"

# ---------------------------------------------------------------- 4
say "4/10  A fixed name for the Nano, and nothing else touching it"
sudo tee /etc/udev/rules.d/99-aquasentinel.rules >/dev/null <<'EOF'
# Arduino Nano clones (CH340) and FTDI Nanos get the fixed name /dev/aquasentinel-nano.
# ID_MM_DEVICE_IGNORE stops ModemManager from probing the port (it can steal or reset it).
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="aquasentinel-nano", GROUP="dialout", MODE="0660", ENV{ID_MM_DEVICE_IGNORE}="1"
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", SYMLINK+="aquasentinel-nano", GROUP="dialout", MODE="0660", ENV{ID_MM_DEVICE_IGNORE}="1"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger --subsystem-match=tty
if systemctl list-unit-files 2>/dev/null | grep -q '^ModemManager'; then
  sudo systemctl disable --now ModemManager 2>/dev/null; sudo systemctl mask ModemManager 2>/dev/null; ok "ModemManager switched off (it probes USB serial ports)"
fi
sudo systemctl disable --now brltty 2>/dev/null && ok "brltty switched off (it grabs CH340 serial chips)" || true
# USB power saving off, so the Nano is never put to sleep
if [ -f "$CMDLINE" ] && ! grep -q 'usbcore.autosuspend=-1' "$CMDLINE"; then
  sudo sed -i '1 s/$/ usbcore.autosuspend=-1/' "$CMDLINE"; REBOOT=1; ok "USB power saving off"
fi
[ -e /dev/aquasentinel-nano ] && ok "Nano found: /dev/aquasentinel-nano -> $(readlink -f /dev/aquasentinel-nano)" || warn "Nano not plugged in now (fine; it is found when plugged in)"

# ---------------------------------------------------------------- 5
say "5/10  Making the Pi lighter"
if swapon --show 2>/dev/null | grep -q zram && ! dpkg -s zram-tools >/dev/null 2>&1; then
  ok "compressed memory swap (zram) already on (from the system)"
elif dpkg -s zram-tools >/dev/null 2>&1; then
  echo -e "ALGO=lz4\nPERCENT=50" | sudo tee /etc/default/zramswap >/dev/null; sudo systemctl restart zramswap 2>/dev/null; ok "compressed memory swap (zram) on"
fi
sudo mkdir -p /etc/systemd/journald.conf.d
echo -e "[Journal]\nSystemMaxUse=50M" | sudo tee /etc/systemd/journald.conf.d/aquasentinel.conf >/dev/null
sudo systemctl restart systemd-journald 2>/dev/null; ok "system logs limited to 50 MB"
for s in cups cups-browsed triggerhappy packagekit; do
  systemctl is-enabled "$s" >/dev/null 2>&1 && sudo systemctl disable --now "$s" >/dev/null 2>&1 && ok "unused service off: $s"
done

# ---------------------------------------------------------------- 6
say "6/10  Background service"
sudo tee /etc/systemd/system/aquasentinel.service >/dev/null <<EOF
[Unit]
Description=AquaSentinel river monitor
After=network.target
StartLimitIntervalSec=0

[Service]
User=$USER_NAME
SupplementaryGroups=dialout
WorkingDirectory=$APP
Environment=PYTHONUNBUFFERED=1
ExecStart=/usr/bin/python3 -m aquasentinel
Restart=always
RestartSec=3
Nice=-5

[Install]
WantedBy=multi-user.target
EOF
sudo tee /etc/cron.daily/aquasentinel-clean >/dev/null <<EOF
#!/bin/sh
find "$APP/logs" -name 'readings_*.csv' -mtime +90 -delete 2>/dev/null
EOF
sudo chmod +x /etc/cron.daily/aquasentinel-clean
sudo systemctl daemon-reload
sudo systemctl enable aquasentinel.service >/dev/null 2>&1 && ok "service enabled (starts on boot, restarts if it stops)"

# ---------------------------------------------------------------- 7
say "7/10  Dashboard on the Pi's screen"
chmod +x "$APP"/kiosk/*.sh "$APP"/*.sh "$APP"/tools/*.sh 2>/dev/null
AUTO="$HOME_DIR/.config/autostart/aquasentinel-kiosk.desktop"
if [ $KIOSK = 1 ]; then
  mkdir -p "$HOME_DIR/.config/autostart"
  printf "[Desktop Entry]\nType=Application\nName=AquaSentinel dashboard\nExec=%s/kiosk/start-kiosk.sh\nX-GNOME-Autostart-enabled=true\n" "$APP" > "$AUTO"
  if [ -d "$HOME_DIR/.config/labwc" ] || command -v labwc >/dev/null; then
    mkdir -p "$HOME_DIR/.config/labwc"
    grep -q start-kiosk "$HOME_DIR/.config/labwc/autostart" 2>/dev/null || echo "$APP/kiosk/start-kiosk.sh &" >> "$HOME_DIR/.config/labwc/autostart"
  fi
  command -v raspi-config >/dev/null && sudo raspi-config nonint do_boot_behaviour B4 2>/dev/null
  ok "full-screen dashboard after login (light mode, 10 frames a second)"
else
  rm -f "$AUTO"; sed -i '/start-kiosk/d' "$HOME_DIR/.config/labwc/autostart" 2>/dev/null
  ok "no full-screen browser on the Pi; open http://<pi-address>:8080 on a phone or laptop"
fi
chown -R "$USER_NAME":"$USER_NAME" "$HOME_DIR/.config" "$APP" 2>/dev/null

# ---------------------------------------------------------------- 8
say "8/10  Nano firmware"
if [ -e /dev/aquasentinel-nano ] || ls /dev/ttyUSB* /dev/ttyACM* >/dev/null 2>&1; then
  if [ $FLASH = ask ]; then read -r -p "   Flash the Nano with firmware v2 now (about 20 s)? (y/n) " a; [ "$a" = y ] && FLASH=yes || FLASH=no; fi
  if [ $FLASH = yes ]; then bash "$APP/tools/flash_nano.sh" && ok "Nano firmware v2 flashed" || warn "flashing failed: see the messages above"; else ok "skipped (run tools/flash_nano.sh any time)"; fi
else warn "Nano not plugged in: flash later with  bash $APP/tools/flash_nano.sh"; fi

# ---------------------------------------------------------------- 9
say "9/10  Cloud (Firebase)"
if [ -f "$APP/secrets.json" ]; then
  chmod 600 "$APP/secrets.json"
  if python3 "$APP/tools/cloud_test.py"; then
    python3 - "$APP" <<'PY'
import json, sys
p = sys.argv[1] + "/config.json"; c = json.load(open(p)); c.setdefault("cloud", {})["enabled"] = True
json.dump(c, open(p, "w"), indent=2)
PY
    ok "cloud login and write work: cloud switched on"
  else
    warn "cloud not switched on yet: fix secrets.json, then run  bash install.sh  again (see the message above)"
  fi
  N=$(python3 -c "import sys; sys.path.insert(0,'$APP'); from aquasentinel import settings; print(len(settings.load()['sms_numbers']))")
  ok "$N phone number(s) for SMS alerts (from secrets.json)"
else ok "no secrets.json: the station runs local only (see cloud/FIREBASE_SETUP.md to add the cloud)"; fi

# ---------------------------------------------------------------- 10
say "10/10  Self-test and health report"
python3 "$APP/tools/self_test.py" || warn "self-test failed"
sudo systemctl restart aquasentinel
sleep 4
systemctl is-active --quiet aquasentinel && ok "service running" || warn "service not running: journalctl -u aquasentinel -n 50"
bash "$APP/tools/doctor.sh" --short || true

IP=$(hostname -I | awk '{print $1}')
say "Done"
[ ${#WARNINGS[@]} -gt 0 ] && { echo "Things to look at:"; for w in "${WARNINGS[@]}"; do echo "  - $w"; done; }
echo "Dashboard: http://localhost:8080 on the Pi, http://$IP:8080 from a phone or laptop on the same Wi-Fi"
echo "Calibrate: python3 $APP/tools/calibrate.py      Health: bash $APP/tools/doctor.sh"
echo "Full log of this install: $LOG"
[ $REBOOT = 1 ] && echo -e "\n\033[1;33mReboot once now to finish:  sudo reboot\033[0m"
exit 0
