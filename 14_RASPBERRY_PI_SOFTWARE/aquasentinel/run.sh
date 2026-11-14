#!/usr/bin/env bash
# Run by hand (for testing). Stops the background service first so the ports are free.
#   bash run.sh            real sensors
#   bash run.sh --simulate no hardware needed
cd "$(dirname "$0")"
sudo systemctl stop aquasentinel 2>/dev/null || true
python3 -m aquasentinel "$@"
