#!/usr/bin/env bash
# Update the software on the Pi from a new copy of this folder, keeping your settings, calibration, secrets and logs.
#
#   1. copy the new "aquasentinel" folder to the Pi, anywhere except ~/aquasentinel (for example ~/aquasentinel_new)
#   2. bash ~/aquasentinel_new/update.sh
#
# It copies the program files into ~/aquasentinel, keeps config.json / secrets.json / logs, restarts the service and
# runs the self-test. If the firmware file changed it offers to flash the Nano.
set -u
NEW="$(cd "$(dirname "$0")" && pwd)"
DEST="${1:-$HOME/aquasentinel}"
[ "$NEW" = "$(cd "$DEST" 2>/dev/null && pwd)" ] && { echo "Run update.sh from the NEW copy, not from $DEST."; exit 1; }
mkdir -p "$DEST"
OLD_HEX=$(md5sum "$DEST/firmware/aquasentinel_nano_v2.hex" 2>/dev/null | cut -d' ' -f1)
STAMP=$(date +%Y%m%d-%H%M); [ -f "$DEST/config.json" ] && cp "$DEST/config.json" "$DEST/config.backup-$STAMP.json"
echo "Copying the new program into $DEST (keeping config.json, secrets.json and logs)..."
if command -v rsync >/dev/null; then
  rsync -a --exclude config.json --exclude secrets.json --exclude logs/ --exclude 'config.backup-*' "$NEW/" "$DEST/"
else
  (cd "$NEW" && tar cf - --exclude=./config.json --exclude=./secrets.json --exclude=./logs .) | (cd "$DEST" && tar xf -)
fi
[ -f "$DEST/config.json" ] || cp "$NEW/config.json" "$DEST/config.json"
chmod +x "$DEST"/*.sh "$DEST"/tools/*.sh "$DEST"/kiosk/*.sh 2>/dev/null
python3 "$DEST/tools/self_test.py" || { echo "Self-test FAILED: the old config is in $DEST/config.backup-$STAMP.json"; }
sudo systemctl restart aquasentinel && echo "Service restarted."
NEW_HEX=$(md5sum "$DEST/firmware/aquasentinel_nano_v2.hex" 2>/dev/null | cut -d' ' -f1)
if [ -n "$NEW_HEX" ] && [ "$NEW_HEX" != "$OLD_HEX" ]; then
  read -r -p "New Nano firmware in this update. Flash it now? (y/n) " a
  [ "$a" = y ] && bash "$DEST/tools/flash_nano.sh"
fi
echo "Updated. Health check:  bash $DEST/tools/doctor.sh"
