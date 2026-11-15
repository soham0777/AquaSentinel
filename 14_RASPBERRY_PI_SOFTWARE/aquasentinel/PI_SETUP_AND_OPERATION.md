# AquaSentinel on the Raspberry Pi

The Arduino Nano on our Sensor Hub board reads every sensor. This folder is the Raspberry Pi side:

- it reads the Nano over USB, once a second;
- it decides whether the water is normal (same rules as our finale deck);
- it acts on an event: turns the beacon red, runs the pump to bottle a sample, sends an SMS through the SIM800L;
- it shows everything live on a full-screen dashboard on the monitor (and on any phone on the same Wi-Fi);
- it saves every reading to a CSV file.

Everything starts by itself when the Pi is switched on. No internet is needed after the setup.

---

## Setup (once, about 15 minutes)

**You need:** the Pi with Raspberry Pi OS (Desktop), monitor, keyboard, mouse, internet for the setup only,
and this folder on a USB stick.

1. **Copy the folder to the Pi.** Plug in the USB stick and copy the folder `aquasentinel` to the home folder,
   so it is at `/home/<your-user>/aquasentinel`.
2. **Open a terminal** (black icon at the top) and type:
   ```
   cd ~/aquasentinel
   bash install.sh
   ```
   It installs what it needs, sets up the SIM800L serial port, the background service and the full-screen
   dashboard. At the end it prints **ALL PASS** for the decision-engine self-test.
3. **Plug the Nano's USB cable into the Pi.**
4. **Reboot:** `sudo reboot`. After the reboot the dashboard opens full-screen by itself.

## Before the booth (once)

**Phone numbers for the SMS.** Open `config.json` in the text editor and put the numbers in, with +91:
```
"sms_numbers": ["+91XXXXXXXXXX", "+91YYYYYYYYYY"],
```
Save, then restart the service: `sudo systemctl restart aquasentinel`.

**Calibrate pH** with your buffer solutions (until then the dashboard shows *calibrate* on the pH tile, and only a
sudden pH change counts as an event):
```
sudo systemctl stop aquasentinel
python3 ~/aquasentinel/tools/calibrate_ph.py
sudo systemctl start aquasentinel
```

**Check all the hardware** in 30 seconds (prints OK / FAIL for every sensor, the beacon, the pump and the SIM800L):
```
sudo systemctl stop aquasentinel
python3 ~/aquasentinel/tools/check_hardware.py
sudo systemctl start aquasentinel
```

**MQ-3 warm-up.** Keep the model powered for at least 3 minutes before relying on SOLVENT detection. `mq3_warmup_s` in
`config.json` is 90 s; some documents say about 3 minutes.

**Self-test.** `tools/self_test.py` prints ALL PASS on simulated data. It proves the decision logic, not the wiring.

## At the booth: the six waters

The first 20 seconds after start the dashboard says **LEARNING**: it learns what normal is for the water in the dish.
Then try each water and wait about 5 seconds:

| Put in the dish / do | Dashboard shows | Beacon |
|---|---|---|
| Clean tap water | NORMAL | green |
| A spoon of salt, stirred | INDUSTRIAL (dissolved solids jump) | red + sample + SMS |
| A little vinegar | ACIDIC (pH falls) | red + sample + SMS |
| A spoon of soil | RUNOFF (cloudy, salts flat) | red + sample + SMS |
| Sanitiser on a tissue at the bottle cone | SOLVENT (vapour) | red + sample + SMS |
| Unplug the temperature probe | SENSOR FAULT | blinking red |

Back in clean water it returns to NORMAL after a few seconds. To start fresh with new water press
**Learn new water** on the dashboard. Only one SMS is sent per 10 minutes, so the phone is not flooded.

Buttons on the dashboard: **Beacon test**, **Take a sample** (pump 5 s), **Send test SMS**, **Learn new water**.

## Useful commands

| What | Command |
|---|---|
| Is it running? | `systemctl status aquasentinel` |
| Live log | `journalctl -u aquasentinel -f` |
| Restart | `sudo systemctl restart aquasentinel` |
| Run by hand / without hardware | `bash ~/aquasentinel/run.sh` or `bash ~/aquasentinel/run.sh --simulate` |
| Today's readings | `~/aquasentinel/logs/readings_YYYY-MM-DD.csv` (or the dashboard address + `/api/csv`) |
| Dashboard from a phone | `http://<pi-address>:8080` (address: `hostname -I`) |
| Leave full-screen | `Alt + F4` |

## If something is wrong

| You see | Do this |
|---|---|
| *Sensor hub offline* | USB cable Nano → Pi; then `sudo systemctl restart aquasentinel` |
| *SIM800L · no answer* | 4.0 V on J17, TX/RX wires on J18, antenna on; run `tools/check_hardware.py` |
| *searching network* | wait 30 s; check the SIM card has SMS balance |
| Black screen, no dashboard | open the browser at `http://localhost:8080` |
| pH tile says *calibrate* | run `tools/calibrate_ph.py` |

## Wiring reminder (Sensor Hub v1.2)

- Nano → Pi: **USB cable** (power and data).
- SIM800L → Pi via **J18**: GND → pin 6, Pi TX pin 8 → (divider on board) → SIM RXD, SIM TXD → Pi RX pin 10.
- SIM800L power: **J17**, 4.0 V from the step-down module.

## How it decides

Same rules as the finale deck: hard limits (pH below 6 or above 9, dissolved solids above 1,400 ppm) plus a baseline
learned from the water, so a sudden jump counts even below the limit. Two unusual readings out of three make an event.
A missing or broken sensor is reported as SENSOR FAULT, never as normal. The model reads once a second for the demo;
the river design reads every 15 minutes.

## Files

```
aquasentinel/
  install.sh            one-command setup
  run.sh                run by hand
  config.json           site name, SMS numbers, limits, pH calibration
  aquasentinel/         the program (nano link, decisions, SMS, logging, web server, simulator)
  web/                  the dashboard
  kiosk/start-kiosk.sh  opens the dashboard full-screen
  tools/                calibrate_ph.py, check_hardware.py, self_test.py
  logs/                 daily CSV files of all readings
```
