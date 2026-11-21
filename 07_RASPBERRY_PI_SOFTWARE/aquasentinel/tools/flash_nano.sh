#!/usr/bin/env bash
# Flashes the Nano from the Pi with the ready-made firmware (nothing is compiled on the Pi).
#   bash ~/aquasentinel/tools/flash_nano.sh                  firmware/aquasentinel_nano_v2.hex
#   bash ~/aquasentinel/tools/flash_nano.sh other.hex        another .hex file
# The .hex is built on a PC with the Arduino IDE or arduino-cli from firmware/aquasentinel_nano/aquasentinel_nano.ino.
set -u
APP="$(cd "$(dirname "$0")/.." && pwd)"
HEX="${1:-$APP/firmware/aquasentinel_nano_v2.hex}"
[ -f "$HEX" ] || { echo "No firmware file: $HEX"; exit 1; }
command -v avrdude >/dev/null || { echo "avrdude missing: sudo apt-get install -y avrdude"; exit 1; }
PORT=""
for p in /dev/aquasentinel-nano /dev/ttyUSB0 /dev/ttyACM0 /dev/ttyUSB1; do [ -e "$p" ] && { PORT=$(readlink -f "$p"); break; }; done
[ -n "$PORT" ] || { echo "Nano not found. Plug its USB cable into a working USB port of the Pi."; exit 1; }
WAS_RUNNING=0
systemctl is-active --quiet aquasentinel && { WAS_RUNNING=1; sudo systemctl stop aquasentinel; }
echo "Flashing $HEX to the Nano on $PORT ..."
OK=0
for BAUD in 57600 115200; do          # 57600 = old bootloader (most clones), 115200 = new bootloader
  if avrdude -p atmega328p -c arduino -P "$PORT" -b $BAUD -D -q -q -U "flash:w:$HEX:i"; then OK=1; echo "Done (bootloader at $BAUD baud)."; break; fi
  echo "No answer at $BAUD baud, trying the other bootloader..."
done
if [ $OK = 1 ]; then
  sleep 3
  python3 - "$PORT" <<'PY'
import json, sys, time, serial
s = serial.Serial(sys.argv[1], 115200, timeout=1); time.sleep(2.5); s.reset_input_buffer()
for _ in range(6):
    l = s.readline().decode(errors="replace").strip()
    if l.startswith("{") and '"vcc"' in l:
        j = json.loads(l); print("Nano answers: firmware v%s, %d values per line" % (j.get("fw", 1), len(j))); break
else:
    print("Flashed, but no data line yet. Check the sensors' power (AUX charger on J12).")
PY
  [ $WAS_RUNNING = 1 ] && sudo systemctl start aquasentinel
  exit 0
fi
[ $WAS_RUNNING = 1 ] && sudo systemctl start aquasentinel
echo "Flashing failed. Try: another USB cable or port; press the Nano's reset button just as it starts; or flash from the Arduino IDE."
exit 1
