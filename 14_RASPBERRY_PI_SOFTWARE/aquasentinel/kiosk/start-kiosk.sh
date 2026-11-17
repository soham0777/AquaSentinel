#!/usr/bin/env bash
# Opens the AquaSentinel dashboard full-screen. Started automatically after login (see install.sh).
# "?lite" runs the river animation at 10 frames a second; the flags below switch off browser extras the Pi does not need.
URL="http://localhost:8080/?lite"
for i in $(seq 1 60); do                 # wait until the service answers (max 60 s)
  curl -s -o /dev/null "http://localhost:8080/api/state" && break
  sleep 1
done
command -v unclutter >/dev/null && (unclutter -idle 2 &)          # hide the mouse pointer when idle
xset s off 2>/dev/null; xset -dpms 2>/dev/null; xset s noblank 2>/dev/null   # screen never sleeps
BROWSER=$(command -v chromium-browser || command -v chromium)
exec "$BROWSER" --kiosk --noerrdialogs --disable-infobars --incognito --no-first-run \
  --disable-session-crashed-bubble --check-for-update-interval=31536000 \
  --disable-background-networking --disable-sync --disable-translate --disable-extensions \
  --disable-features=Translate,MediaRouter,OptimizationHints --disk-cache-size=1048576 \
  --renderer-process-limit=1 "$URL"
