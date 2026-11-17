#!/usr/bin/env bash
# AquaSentinel health check. Tells you in plain words what is wrong and what to do.
#   bash ~/aquasentinel/tools/doctor.sh              full report
#   bash ~/aquasentinel/tools/doctor.sh --short      summary only (used at the end of install.sh)
#   bash ~/aquasentinel/tools/doctor.sh --usb-test   find which USB ports work: plug one device into each port in turn
#   bash ~/aquasentinel/tools/doctor.sh --usb-reset  restart the Pi's USB system (all USB devices drop for ~5 s)
set -u
APP="$(cd "$(dirname "$0")/.." && pwd)"
G='\033[32m'; Y='\033[33m'; R='\033[31m'; N='\033[0m'
ok(){ printf "  ${G}OK${N}    %s\n" "$1"; }
note(){ printf "  ${Y}CHECK${N} %s\n" "$1"; }
bad(){ printf "  ${R}FIX${N}   %s\n" "$1"; }
hdr(){ printf "\n\033[1m%s\033[0m\n" "$1"; }
MODE="${1:-}"

usb_devices(){ for d in /sys/bus/usb/devices/*; do
  [ -f "$d/bDeviceClass" ] || continue; [ "$(cat "$d/bDeviceClass")" = "09" ] && continue
  echo "$(basename "$d")  $(cat "$d/product" 2>/dev/null || echo device) $(cat "$d/idVendor" 2>/dev/null):$(cat "$d/idProduct" 2>/dev/null)"; done; }

if [ "$MODE" = "--usb-test" ]; then
  echo "USB port test (60 s). Take ONE device (a keyboard, a mouse or the Nano) and plug it into each USB port in turn,"
  echo "waiting 3 s in each. Every port that works prints a line. A port that prints nothing is not working."
  before=$(usb_devices); end=$((SECONDS + 60))
  while [ $SECONDS -lt $end ]; do
    now=$(usb_devices)
    comm -13 <(echo "$before" | sort) <(echo "$now" | sort) | while read -r l; do printf "  ${G}+ plugged${N}   port %s\n" "$l"; done
    comm -23 <(echo "$before" | sort) <(echo "$now" | sort) | while read -r l; do printf "  - removed   port %s\n" "$l"; done
    before="$now"; sleep 1
  done
  echo "Done. Port names look like 1-1.2 or 1-1.1.3: write down which physical socket gave which name."
  exit 0
fi

if [ "$MODE" = "--usb-reset" ]; then
  echo "Restarting the USB system (keyboard, mouse, Nano and wired network drop for a few seconds)..."
  if command -v uhubctl >/dev/null; then sudo uhubctl -l 1-1 -a cycle -d 3 >/dev/null 2>&1 && echo "Power to the USB ports switched off and on."; fi
  for h in /sys/bus/usb/drivers/usb/1-1; do
    [ -e "$h" ] && { echo 1-1 | sudo tee /sys/bus/usb/drivers/usb/unbind >/dev/null; sleep 2; echo 1-1 | sudo tee /sys/bus/usb/drivers/usb/bind >/dev/null; }
  done
  sleep 4; echo "USB devices now:"; usb_devices | sed 's/^/  /'
  exit 0
fi

hdr "Raspberry Pi"
MODEL=$(tr -d '\0' < /proc/device-tree/model 2>/dev/null || echo unknown); ok "$MODEL"
if command -v vcgencmd >/dev/null; then
  T=$(vcgencmd get_throttled | cut -d= -f2)
  if (( T & 0x1 )); then bad "power supply too weak RIGHT NOW ($T): the Pi slows down and USB devices can drop. Use the official 5.1 V 2.5 A supply, a short thick cable, and power the pump/sensors from the AUX supply, not the Pi."
  elif (( T & 0x10000 )); then note "the power supply dipped since the last boot ($T). Likely cause of drop-outs and slowness."
  else ok "power supply fine"; fi
  (( T & 0x4 )) && note "the Pi is slowed down now (heat or power)"
  TEMP=$(vcgencmd measure_temp | grep -o '[0-9.]*'); awk "BEGIN{exit !($TEMP > 75)}" && note "hot: ${TEMP} degC (add a heatsink or air)" || ok "temperature ${TEMP} degC"
fi
MEM=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); [ "$MEM" -lt 120 ] && note "only $MEM MB memory free" || ok "$MEM MB memory free"
DISK=$(df -m / | awk 'NR==2{print $4}'); [ "$DISK" -lt 1000 ] && bad "only $DISK MB free on the SD card" || ok "$((DISK/1024)) GB free on the SD card"
LOAD=$(cut -d' ' -f1 /proc/loadavg); ok "load $LOAD (under 3 is fine on 4 cores)"

hdr "USB"
CNT=$(usb_devices | wc -l); ok "$CNT USB device(s) plugged in:"
usb_devices | sed 's/^/          /'
OC=$(dmesg 2>/dev/null | grep -ciE 'over-current|overcurrent')
EN=$(dmesg 2>/dev/null | grep -ciE 'device descriptor read|unable to enumerate|device not accepting address')
[ "$OC" -gt 0 ] && bad "$OC over-current message(s): a device draws too much. Unplug the pump/motors from the Pi, use a powered USB hub."
[ "$EN" -gt 0 ] && note "$EN message(s) that a device could not start: bad cable, bad socket or weak power."
[ "$OC" -eq 0 ] && [ "$EN" -eq 0 ] && ok "no USB errors since boot"
CFGF=/boot/firmware/config.txt; [ -f "$CFGF" ] || CFGF=/boot/config.txt
grep -qE '^\s*dtoverlay=dwc2|otg_mode|dr_mode=peripheral' "$CFGF" 2>/dev/null && bad "config.txt has a USB gadget/OTG line (dwc2 / otg_mode): on a Pi 3 this can switch USB host ports off. Remove it and reboot."
if [ "$MODE" != "--short" ]; then
  echo "          Ports not working? Run:  bash $APP/tools/doctor.sh --usb-test"
  echo "          A port that never shows a device in that test is damaged or unpowered; software cannot repair a broken"
  echo "          socket. Use a working port with a powered USB hub. After an over-current: --usb-reset or a full power-off."
fi

hdr "Sensor hub (Nano)"
[ -e /dev/aquasentinel-nano ] && ok "Nano plugged in: /dev/aquasentinel-nano -> $(readlink -f /dev/aquasentinel-nano)" || \
  { ls /dev/ttyUSB* /dev/ttyACM* >/dev/null 2>&1 && note "a serial device is there but not named; run install.sh again" || bad "no Nano on USB: cable, port, or the Nano itself"; }
systemctl is-active --quiet ModemManager 2>/dev/null && bad "ModemManager is running and can grab the Nano's port: run install.sh again"
STATE=$(curl -s -m 4 http://127.0.0.1:8080/api/state || true)
if systemctl is-active --quiet aquasentinel && [ -n "$STATE" ]; then
  ok "AquaSentinel service running"
  python3 - "$STATE" <<'PY'
import json, sys
s = json.loads(sys.argv[1]); L = s.get("link", {}); st = L.get("stats", {}); sysi = s.get("system", {}); c = s.get("cloud", {})
G, Y, R, N = "\033[32m", "\033[33m", "\033[31m", "\033[0m"
def ok(t): print(f"  {G}OK{N}    {t}")
def note(t): print(f"  {Y}CHECK{N} {t}")
def bad(t): print(f"  {R}FIX{N}   {t}")
(ok if L.get("nano") else bad)(f"Nano link: {'connected on ' + str(L.get('port')) if L.get('nano') else 'NOT connected'}; last reading {L.get('age')} s ago")
fw = st.get("fw")
if fw is not None:
    (ok if fw >= 2 else note)(f"Nano firmware v{fw}" + ("" if fw >= 2 else ": flash v2 for steadier data (tools/flash_nano.sh)"))
lines = st.get("lines", 0) or 1
for k, label, lim in (("bad", "damaged lines dropped", 0.01), ("lost", "lines lost", 0.01)):
    v = st.get(k, 0); (ok if v / lines <= lim else note)(f"{label}: {v} of {st.get('lines', 0)}")
if st.get("reconnects"): note(f"USB link to the Nano restarted {st['reconnects']} time(s); last: {st.get('last_problem')}")
for k, name in (("e_dht", "DHT11 (air) failed reads"), ("e_ds", "DS18B20 (water temp) failed reads")):
    v = st.get(k, 0)
    if v: (note if v > 50 else ok)(f"{name}: {v} since the Nano started (bridged automatically; many = loose wire or missing pull-up)")
lat = s.get("latest") or {}
for k, name in (("t_water", "water temp"), ("t_air", "air temp"), ("ph_v", "pH"), ("tds_v", "TDS")):
    if lat.get(k) is None: bad(f"no {name} value right now")
if not s.get("ph_calibrated"): note("pH not calibrated: python3 ~/aquasentinel/tools/calibrate.py")
(ok if L.get("sim") == "ready" else note)(f"SIM800L: {L.get('sim')}" + (f", signal {L.get('signal')}/31" if L.get("signal") is not None else ""))
if c.get("enabled"): (ok if c.get("status") == "online" else note)(f"cloud: {c.get('status')}, {c.get('queued', 0)} waiting, {c.get('sent', 0)} sent")
else: ok("cloud: off (local only)")
PY
else
  bad "AquaSentinel service not answering: sudo systemctl restart aquasentinel ; journalctl -u aquasentinel -n 40"
fi

hdr "Network"
IP=$(hostname -I 2>/dev/null | awk '{print $1}'); [ -n "$IP" ] && ok "address $IP (dashboard http://$IP:8080)" || note "no network address"
curl -s -m 5 -o /dev/null https://firebaseio.com && ok "internet reachable" || note "no internet (the station still works; the cloud catches up later)"
echo
