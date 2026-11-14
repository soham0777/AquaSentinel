#!/usr/bin/env bash
# Opens the AquaSentinel dashboard full-screen. Started automatically after login (see install.sh).
URL="http://localhost:8080"
# wait until the service answers (max 60 s)
for i in $(seq 1 60); do
  curl -s -o /dev/null "$URL" && break
  sleep 1
done
command -v unclutter >/dev/null && (unclutter -idle 2 &)          # hide the mouse pointer when idle
xset s off 2>/dev/null; xset -dpms 2>/dev/null; xset s noblank 2>/dev/null   # screen never sleeps
BROWSER=$(command -v chromium-browser || command -v chromium)
exec "$BROWSER" --kiosk --noerrdialogs --disable-infobars --incognito \
  --disable-session-crashed-bubble --check-for-update-interval=31536000 "$URL"
