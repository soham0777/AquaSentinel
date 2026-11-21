# AquaSentinel on the Raspberry Pi

> **Setting up a Pi?** Follow `RASPBERRY_PI_STEP_BY_STEP.md`: every step in order, from a blank SD card to SMS and cloud. This page explains how the system works.

The Arduino Nano on our Sensor Hub board reads every sensor. This folder is the Raspberry Pi side. It:

- reads the Nano over USB, once a second;
- decides whether the water is normal, using the same rules as our finale deck;
- acts on an event: turns the beacon red, runs the pump to bottle a sample, and sends an SMS through the SIM800L;
- shows everything live on a dashboard, on the Pi's monitor and on any phone on the same Wi-Fi;
- saves every reading to a CSV file;
- optionally publishes everything to the cloud (Firebase), so the dashboard can be seen from anywhere.

Everything starts by itself when the Pi is switched on. The station works without internet; the cloud catches up later.

---

## What changed on 17 Nov 2026, and why

| Problem we saw | Cause we found | What now handles it |
|---|---|---|
| Sensors sometimes give data, sometimes not | The DHT11 was asked for a reading every second, but it can only answer about every 2 s. One failed read of the DHT11 or DS18B20 turned straight into "no value", and the brain counted it as a fault. | **Nano firmware v2** reads the DHT11 every 2.5 s and keeps the last good value for 10 s; the DS18B20 keeps its value for 5 s. **On the Pi**, a short gap is bridged, and only a gap longer than `hold_seconds` becomes SENSOR FAULT. A median of 3 readings removes single spikes. |
| Damaged or lost data from the Nano | A USB line can arrive cut off or with a wrong digit. | Every line now has a line counter and a checksum. Damaged lines are dropped and counted. |
| Beacon sometimes does not change colour | A command can be lost while the Nano is busy reading the DHT11. | Commands are re-sent until the Nano confirms them. The Nano reports its beacon colour in every line, and the Pi corrects it if needed. |
| Nano port changes name, or disappears | The Nano can come back as ttyUSB0 or ttyUSB1. ModemManager and brltty also probe it and can grab it. | A fixed name, `/dev/aquasentinel-nano`. ModemManager and brltty are switched off, and USB power saving is off. |
| Pi feels slow | The dashboard's river animation ran at 60 frames a second. Chromium extras were running, there was no compressed swap, and unused services were on. A weak power supply also slows the Pi. | The dashboard runs at 10 frames a second on the Pi. Chromium is lighter. Compressed memory swap (zram) is on, logs are limited and unused services are off. The installer and the dashboard warn about a weak power supply. Nothing is compiled on the Pi: all packages come ready-made from apt, with no pip. |
| Only 2 of 4 USB ports work | See "USB ports" below. | `tools/doctor.sh` finds the cause, `--usb-test` finds which sockets work, and `--usb-reset` restarts the USB system. |
| Calibration only for pH, and the service had to be stopped | — | One wizard, `tools/calibrate.py`, calibrates pH, TDS, turbidity, MQ-3 and water temperature while the service runs, and applies the result at once. |
| Everything was local only | — | Firebase cloud with an offline queue (`cloud/FIREBASE_SETUP.md`). |
| Manual setup steps | — | `install.sh` does all ten steps and can be run again at any time. `update.sh` updates the software without losing settings. `tools/flash_nano.sh` flashes the Nano from the Pi. |

---

## Setup (once, about 15 minutes)

**You need:**
- the Pi with Raspberry Pi OS;
- a monitor, keyboard and mouse;
- the official **5.1 V 2.5 A** power supply;
- internet, for the setup only;
- this folder on a USB stick.

1. **Copy the folder to the Pi.** Copy `aquasentinel` to the home folder, so it is at `/home/<your-user>/aquasentinel`.
2. **Plug the Nano's USB cable into a working USB port.**
3. **Open a terminal** and type:
   ```
   cd ~/aquasentinel
   bash install.sh
   ```
   It asks once whether to flash the Nano with firmware v2. Answer **y**.
   
   At the end it prints:
   - ALL PASS for the self-test;
   - a health report;
   - "Reboot once now".
4. **Reboot:** `sudo reboot`. The dashboard then opens full-screen by itself.

Installer options:
- `bash install.sh --no-kiosk` sets the Pi up with no browser on its own screen. This is the lightest setup: watch the dashboard from a phone or laptop instead.
- `bash install.sh --flash` flashes the Nano without asking.

Every step is logged to `~/aquasentinel-install.log`.

## Before the booth (once)

**Phone numbers for the SMS.**
1. Open `config.json` and add the numbers with the +91 code: `"sms_numbers": ["+91XXXXXXXXXX"],`.
2. Run `sudo systemctl restart aquasentinel`.

**Calibrate.** The service can keep running while you do this:
```
python3 ~/aquasentinel/tools/calibrate.py
```

| Menu | You need | Sets |
|---|---|---|
| 1 pH | buffers 7.0, 4.0 and 9.2 (two are enough) | the pH line. Until it is set, only a sudden pH change counts. |
| 2 TDS | a standard solution with its ppm on the bottle | the TDS factor |
| 3 Turbidity | clean, clear water | the clear-water voltage; cloudy is then judged by the number, not the module's trimmer |
| 4 MQ-3 | clean air, after the model has been on for at least 3 minutes | the vapour baseline |
| 5 Water temp | a thermometer in the same water | the temperature offset |

`python3 tools/calibrate.py --show` prints what is stored, with dates.

**Check all the hardware** in 30 seconds. This needs the port, so stop the service first:
```
sudo systemctl stop aquasentinel
python3 ~/aquasentinel/tools/check_hardware.py
sudo systemctl start aquasentinel
```

**Health check** at any time:
```
bash ~/aquasentinel/tools/doctor.sh
```
It checks:
- power, temperature, memory and SD card;
- USB devices and errors;
- the Nano: firmware version, damaged or lost lines, sensor read errors;
- the SIM800L, the cloud and the network.

**MQ-3 warm-up.** Keep the model powered for at least 3 minutes before relying on SOLVENT detection.

## USB ports (only 2 of 4 working)

On a Pi 3B+ all four sockets hang off one USB hub chip, so there is no setting that switches two of them off. The usual causes are below.

1. **Weak power supply.** The doctor reports "power supply too weak". Use the official 5.1 V 2.5 A supply with a short, thick cable. Do not power the pump or the sensors from the Pi's USB.
2. **Over-current.** A device drew too much and the ports were shut off. The doctor counts "over-current" messages. Unplug the heavy device, then run `bash tools/doctor.sh --usb-reset` or switch the Pi fully off and on.
3. **A USB gadget/OTG line in config.txt** (`dtoverlay=dwc2`, `otg_mode`). On a Pi 3 this can disable the host ports. The doctor flags it. Remove it and reboot.
4. **A damaged socket or solder joint.** No software can repair it.

To find which sockets work, run:
```
bash ~/aquasentinel/tools/doctor.sh --usb-test
```
Then plug one device into each socket in turn. A working socket prints a line, such as `port 1-1.2`. A socket that never prints is dead.

If two stay dead, use the working ones. If you need more ports, add a **powered** USB hub on a working socket. The Nano, a keyboard and a mouse fit on 2 ports with a small hub.

## At the booth: the six waters

The first 20 seconds after start, the dashboard says **LEARNING**: it learns what normal is for the water in the dish. Then try each water and wait about 5 seconds.

| Put in the dish / do | Dashboard shows | Beacon |
|---|---|---|
| Clean tap water | NORMAL | green |
| A spoon of salt, stirred | INDUSTRIAL (dissolved solids jump) | red + sample + SMS |
| A little vinegar | ACIDIC (pH falls) | red + sample + SMS |
| A spoon of soil | RUNOFF (cloudy, salts flat) | red + sample + SMS |
| Sanitiser on a tissue at the bottle cone | SOLVENT (vapour) | red + sample + SMS |
| Unplug the temperature probe | SENSOR FAULT after about 10 to 15 s (short gaps are bridged) | blinking red |

Back in clean water, it returns to NORMAL after a few seconds. To start fresh with new water, press **Learn new water** on the dashboard. Only one SMS is sent per 10 minutes, so the phone is not flooded.

## Cloud (Firebase)

To set up the cloud, follow `cloud/FIREBASE_SETUP.md`. In short:
1. Create a free Firebase project.
2. Create one user for the station.
3. Paste the rules.
4. Fill in `secrets.json` on the Pi and run `bash install.sh`.

The cloud dashboard in `cloud/public` shows every station from anywhere. Without internet, readings wait on the SD card and are sent later.

## Updating the software

Copy the new `aquasentinel` folder to the Pi under another name, for example `~/aquasentinel_new`. Then run:
```
bash ~/aquasentinel_new/update.sh
```

The update keeps `config.json`, `secrets.json`, the calibration and the logs. It also backs up the old config, runs the self-test and restarts the service. If the update brings new Nano firmware, it offers to flash it.

## Useful commands

| What | Command |
|---|---|
| Health report | `bash ~/aquasentinel/tools/doctor.sh` |
| Is it running? | `systemctl status aquasentinel` |
| Live log | `journalctl -u aquasentinel -f` |
| Restart | `sudo systemctl restart aquasentinel` |
| Run by hand / without hardware | `bash ~/aquasentinel/run.sh` or `bash ~/aquasentinel/run.sh --simulate` |
| Flash the Nano | `bash ~/aquasentinel/tools/flash_nano.sh` |
| All tests | `python3 ~/aquasentinel/tools/self_test.py` |
| Today's readings | `~/aquasentinel/logs/readings_YYYY-MM-DD.csv`, or the dashboard address + `/api/csv` |
| Dashboard from a phone | `http://<pi-address>:8080` (address: `hostname -I`) |
| Leave full-screen | `Alt + F4` |

## If something is wrong

| You see | Do this |
|---|---|
| *Sensor hub offline* | Check the USB cable from the Nano to the Pi and use a working port. Then run `bash tools/doctor.sh`. |
| *⚠ POWER SUPPLY TOO WEAK* in the footer | Use the official supply. Pump and sensors run from the AUX supply, not the Pi. |
| *SIM800L · no answer* | Check for 4.0 V on J17, the TX/RX wires on J18 and the antenna. Then run `tools/check_hardware.py`. |
| *no serial port ([Errno 16])* or *serial port busy* | A login console holds the SIM800L's port. Run `sudo systemctl disable --now serial-getty@ttyS0 serial-getty@ttyAMA0`, `sudo raspi-config nonint do_serial_cons 1`, then `sudo reboot`. |
| *searching network* | Wait 30 s and check that the SIM card has SMS balance. |
| *cloud: offline* | Nothing is lost: readings wait and are sent later. Check the Wi-Fi. |
| *cloud: login refused* | Check `secrets.json`, then run `python3 tools/cloud_test.py`. |
| Black screen, no dashboard | Open the browser at `http://localhost:8080`. |
| pH tile says *calibrate* | Run `python3 tools/calibrate.py`, option 1. |

## Wiring reminder (Sensor Hub v1.2)

- Nano to Pi: **USB cable** (power and data).
- SIM800L to Pi through **J18**:
  - GND to pin 6;
  - Pi TX (pin 8) through the divider on the board to SIM RXD;
  - SIM TXD to Pi RX (pin 10).
- SIM800L power: **J17**, 4.0 V from the step-down module.

## How it decides

The rules are the same as in the finale deck:
- hard limits: pH below 6 or above 9, dissolved solids above 1,400 ppm;
- a baseline learned from the water, so a sudden jump counts even below the limit;
- two unusual readings out of three make an event;
- a sensor that stays missing is reported as SENSOR FAULT, never as normal.

A short gap of a few seconds is bridged with the last good value. The model reads once a second for the demo; the river design reads every 15 minutes.

## Files

```
aquasentinel/
  install.sh              one-command setup (safe to run again)
  update.sh               update from a new copy, keeping settings
  run.sh                  run by hand
  config.json             site name, SMS numbers, limits, calibration, cloud on/off
  secrets.json            Firebase login for this station (you create it; never shared)
  aquasentinel/           the program: nano link, sensors, decisions, SMS, cloud, Pi health, web server, simulator
  web/                    the dashboard on the Pi
  cloud/                  Firebase rules, the cloud dashboard, FIREBASE_SETUP.md
  firmware/               Nano firmware v2: ready-made .hex + source (master copy in 06_ELECTRONICS_AND_PCB)
  kiosk/start-kiosk.sh    opens the dashboard full-screen
  tools/                  calibrate.py, doctor.sh, flash_nano.sh, check_hardware.py, cloud_test.py, self_test.py
  logs/                   daily CSV files, and the cloud outbox
```
