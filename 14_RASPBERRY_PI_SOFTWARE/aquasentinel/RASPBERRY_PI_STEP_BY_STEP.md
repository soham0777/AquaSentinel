# AquaSentinel Raspberry Pi: every step, in order

Follow these steps from top to bottom and tick each one. Each step says what you should see.

**Time needed**
- About 45 minutes the first time.
- About 5 minutes after any later update.

**You need**
- the Raspberry Pi 3B+ and a microSD card of 16 GB or more;
- the **official 5.1 V 2.5 A Pi power supply**: a phone charger is the most common cause of a slow Pi and of USB drop-outs;
- a monitor with HDMI, a USB keyboard and a USB mouse;
- the Sensor Hub with the Nano and its USB cable;
- a USB stick;
- Wi-Fi, needed for the setup only;
- a laptop with this project folder.

---

## Which path?

- **Your Pi is already running**, with its own name and user: do **part P**, then **B**, **C**, **D3–D4** and **E** onwards. Skip A.
- **Fresh SD card:** start at **A**.

## P. Pi already running: get it ready (about 10 minutes)

Do this at the Pi with its keyboard and monitor. Open the **Terminal** (the black icon at the top), type each command and press Enter.

1. **See what you have.**
   ```
   whoami
   hostname
   hostname -I
   cat /proc/device-tree/model; echo
   grep PRETTY /etc/os-release
   systemctl get-default
   vcgencmd get_throttled
   ```
   Write down each answer:

   | Command | Tells you | Example |
   |---|---|---|
   | `whoami` | your **user name** | `pi` |
   | `hostname` | the **current name** of the Pi | `raspberrypi` |
   | `hostname -I` | the **IP address**; the first number is the one you need | `192.168.1.42` |
   | model | the board | Raspberry Pi 3 Model B Plus |
   | `PRETTY` | the system version | Debian 12 (bookworm) |
   | `systemctl get-default` | `graphical.target` = it has a desktop; `multi-user.target` = no desktop (Lite) | |
   | `get_throttled` | `0x0` = power fine. Anything else = the power supply is too weak: change it first. | |

   You do **not** need to change the user name. The installer works with any user.

2. **Change the name to `aquasentinel`.**
   ```
   sudo raspi-config nonint do_hostname aquasentinel
   ```
   This changes both `/etc/hostname` and `/etc/hosts`. If `raspi-config` is missing, use these two lines instead:
   ```
   sudo hostnamectl set-hostname aquasentinel
   sudo sed -i 's/^127\.0\.1\.1.*/127.0.1.1\taquasentinel/' /etc/hosts
   ```

3. **Set Indian time,** so SMS times and the CSV dates are right:
   ```
   sudo timedatectl set-timezone Asia/Kolkata
   ```

4. **Wi-Fi.** Skip this if it is already connected. Put your own network name and password in place of the words in capitals:
   ```
   sudo nmcli dev wifi connect "WIFI_NAME" password "WIFI_PASSWORD"
   ```

5. **Switch on SSH,** so the laptop can copy files to the Pi and you can work on it from the laptop:
   ```
   sudo raspi-config nonint do_ssh 0
   ```

6. **Check that the installer can use `sudo` without a password:**
   ```
   sudo -n true && echo SUDO-OK
   ```
   - ✅ If you see `SUDO-OK`, the installer runs without stopping. If you don't, it asks for your password once.

7. **Restart, so the new name takes effect:**
   ```
   sudo reboot
   ```
   After the restart, open the Terminal again and type `hostname`.
   - ✅ It says `aquasentinel`. From the laptop, the Pi is now reachable as `aquasentinel.local`.

8. **Optional: update the system.** This takes 20–40 minutes on a Pi 3B+, so do it when you have time:
   ```
   sudo apt update && sudo apt full-upgrade -y
   ```

Now continue with **B**. Then do **C** (the Firebase login), **D3–D4** (plug in the Nano, check the power) and **E** (the installer).

In E, if `systemctl get-default` said `multi-user.target` (no desktop), run `bash install.sh --no-kiosk` instead of `bash install.sh`, and watch the dashboard from a phone or laptop.

**Copy without a USB stick.** If the laptop is on the same Wi-Fi, copy the folder over the network in place of part B. In **PowerShell on the laptop**, put your user name from step P1 in place of `USER`:
```
cd C:\Users\dell\OneDrive\Desktop\AquaSentinel\14_RASPBERRY_PI_SOFTWARE
scp -r aquasentinel USER@aquasentinel.local:~/
```
Answer `yes` the first time, then type the Pi password. Then on the Pi:

1. Clear the test logs that came along from the laptop (they hold simulator readings, not river data):
   ```
   rm -rf ~/aquasentinel/logs ~/aquasentinel/aquasentinel/__pycache__
   ```
2. In E1, skip the `cp -r /media/...` line and start at `cd ~/aquasentinel`.
3. Skip E3: no stick was used.

## A. Fresh SD card only: prepare it (on the laptop, once)

1. **Install the Imager.** Download and install **Raspberry Pi Imager** from raspberrypi.com/software.
2. **Choose the board, system and card.** In the Imager:
   - **Device:** Raspberry Pi 3.
   - **OS:** Raspberry Pi OS (64-bit), the version *with desktop*.
   - **Storage:** your SD card.
3. **Fill in the settings.** Click **Next → Edit settings**:
   - Hostname: `aquasentinel`
   - Username: `aqua`. Pick a password and write it down.
   - Wi-Fi: your Wi-Fi name and password. Country: IN.
   - Time zone: Asia/Kolkata.
   - Services tab: tick **Enable SSH** (use password authentication).
4. **Write the card.** Click **Save → Yes** and wait until it says the card is ready.
   - ✅ You see "Write successful".

## B. Put the software on the USB stick (on the laptop)

1. Copy the whole folder `14_RASPBERRY_PI_SOFTWARE/aquasentinel` to the USB stick.
2. Make sure the folder **includes `secrets.json`**. This file holds the 4 SMS numbers and the Firebase key.
   - ✅ On the stick: `aquasentinel/install.sh`, `aquasentinel/secrets.json`, `aquasentinel/firmware/aquasentinel_nano_v2.hex`.
   - ⚠ `secrets.json` contains phone numbers. Do not share the stick, and delete the file from the stick after setup.

## C. Create the station's login in Firebase (once)

**Easiest way, which nobody types a password for (done for the Kopargaon station on 17 Nov 2026).** On the Pi, after part E, run:
```
python3 ~/aquasentinel/tools/cloud_register.py
```
It creates `station-<station_id>@aquasentinel.local` with a random password and saves the login only in `secrets.json`. It also prints a **UID**: put that UID at `owners/<station_id>` in the Firebase Data tab (step 4 below). Then run `python3 ~/aquasentinel/tools/cloud_test.py` and `bash ~/aquasentinel/install.sh --no-flash`.

**Never put a personal Gmail address or password in `secrets.json`.** The station has its own login.

The manual way, on the laptop, follows.

1. **Open the users page.** Go to console.firebase.google.com and open project **aquasentinel-live**. Then go to **Build → Authentication → Users**.
2. **Add the user.** Click **Add user**:
   - Email: `station-kopargaon@aquasentinel.local`
   - Password: a long password of your own. Write it down.
   - Click **Add user**.
3. **Copy the User UID.** It is a long code in the user's row.
4. **Link the UID to the station.** Go to **Build → Realtime Database → Data**:
   1. Hover over the top line (the database address) and click **+**.
   2. Key: `owners`. Then click the **+** next to it to add a child.
   3. Child key: `kopargaon-1to5`. Value: paste the UID.
   4. Click **Add**.
   - ✅ The data tree shows `owners → kopargaon-1to5: "<the UID>"`.
5. **Put the login in `secrets.json`.** Open `secrets.json` on the USB stick in Notepad:
   - replace `PUT_STATION_EMAIL` with the e-mail from step 2;
   - replace `PUT_STATION_PASSWORD` with the password from step 2;
   - keep the quotes, and save.

## D. First start of the Pi

1. **Connect everything.** Put the SD card in the Pi. Connect the monitor, keyboard and mouse.
2. **Plug in the Nano.** Plug the **Nano's USB cable** into a USB port you know works. If you are not sure which ports work, any port is fine for now; part F finds them.
3. **Power on.** Plug in the **official power supply** last.
   - ✅ After 1–2 minutes the Raspberry Pi desktop appears.
   - ⚠ A small **lightning bolt** at the top right means the power supply is too weak. Change it before going on.
4. **Check the Wi-Fi.** Click the network icon at the top right.
   - ✅ It shows your Wi-Fi as connected.

## E. Install AquaSentinel (one command)

1. **Copy the folder from the stick.** Plug in the USB stick, then open the **Terminal** (the black icon at the top). Type each line and press Enter:
   ```
   cp -r /media/$USER/*/aquasentinel ~/
   cd ~/aquasentinel
   ls
   ```
   - ✅ You see `install.sh`, `secrets.json`, `tools`, `firmware` and the other files.
2. **Run the installer:**
   ```
   bash install.sh
   ```
   - It asks for your Pi password once, the one from step A3.
   - It asks: **"Flash the Nano with firmware v2 now?"** Type `y` and press Enter.
   - It works through steps 1/10 to 10/10, taking about 5–10 minutes.
   - ✅ At the end you see all of these:
     - `Nano answers: firmware v2`;
     - `OK  signed in as station-kopargaon@…` and `cloud switched on`;
     - `4 phone number(s) for SMS alerts`;
     - `ALL PASS` twice (the decision self-test and the reliability tests);
     - a health report with mostly green **OK** lines.
   - If a line says **NOTE** or **FIX**, read it. It says exactly what to do. The full log is in `~/aquasentinel-install.log`.
3. **Remove the secrets file from the stick:**
   ```
   rm /media/$USER/*/aquasentinel/secrets.json
   ```
   The Pi keeps its own copy, readable only by your user.
4. **Restart the Pi:**
   ```
   sudo reboot
   ```
   - ✅ After the restart the AquaSentinel dashboard opens full-screen by itself. It says **LEARNING** for 20 seconds, then **NORMAL**.

## F. Check the health, and find the working USB ports

1. **Leave full-screen.** Press `Alt + F4`. You can reopen the dashboard later from the browser at `http://localhost:8080`.
2. **Run the health check.** In the Terminal:
   ```
   bash ~/aquasentinel/tools/doctor.sh
   ```
   - ✅ Green **OK** for: the power supply, the Nano link, `Nano firmware v2`, the SIM800L and `cloud: online`.
3. **Test the USB ports.**
   ```
   bash ~/aquasentinel/tools/doctor.sh --usb-test
   ```
   Take one USB device, such as the mouse, and plug it into each of the 4 ports in turn, waiting 3 seconds in each.
   - A working port prints `+ plugged port 1-1.x …`.
   - A port that prints nothing is dead. Mark it with tape and don't use it.
   - If the health report showed **over-current**, run `bash ~/aquasentinel/tools/doctor.sh --usb-reset` and test again.
   - If a port is still dead, no software can repair it. Use the working ports. For more devices, use a **powered** USB hub on a working port.

## G. Calibrate the sensors (about 15 minutes)

The service keeps running while you calibrate. Start the wizard:
```
python3 ~/aquasentinel/tools/calibrate.py
```

| Option | Do this | ✅ Result |
|---|---|---|
| `1` pH | Rinse the probe, put it in the pH 7.0 buffer and press Enter. Repeat with 4.0 and 9.2. | "Result: pH = …". Type `y` to save. |
| `2` TDS | Type the ppm on the standard solution bottle. Put the TDS probe and the temperature probe in it. | "factor k = …" (close to 1). Save with `y`. |
| `3` Turbidity | Probe in clean, clear water, with no bubbles on the window. | "Clear water: … V". Save with `y`. |
| `4` MQ-3 | The model must have been on for at least 3 minutes, in clean air. | "Clean air: … V". Save with `y`. |
| `5` Water temp | The probe and a thermometer in the same water. Type the thermometer's reading. | "Offset …". Save with `y`. |

Type `q` to finish, then check what was saved:
```
python3 ~/aquasentinel/tools/calibrate.py --show
```
- ✅ The pH line says **calibrated** and shows today's date.

## H. Check the SMS alerts

1. **Prepare the SIM card.** Put a SIM card with **SMS balance** in the SIM800L. Make sure the antenna is on and the module has 4.0 V on J17.
2. **Check the SIM800L.**
   - ✅ On the dashboard, the SIM pill shows the network name and signal bars, after about 30 seconds.
3. **Send a test.** Click **Send test SMS** and confirm.
   - ✅ All 4 phones receive the test message:
     - Tanmay +91 87676 01857
     - Prasad +91 93708 27548
     - Bhakti +91 93596 87231
     - Soham +91 90215 38647
4. **To change the numbers later:**
   ```
   nano ~/aquasentinel/secrets.json
   ```
   Edit the list under `"sms_numbers"`. Then save (Ctrl+O, Enter, Ctrl+X) and restart the service:
   ```
   sudo systemctl restart aquasentinel
   ```

## I. Check the cloud

1. **Test the login and a write:**
   ```
   python3 ~/aquasentinel/tools/cloud_test.py
   ```
   - ✅ `OK signed in`, `OK wrote and read back`, `Cloud ready for station 'kopargaon-1to5'`.
2. **Look at the data.** In the Firebase console, open **Realtime Database → Data**.
   - ✅ You see `stations → kopargaon-1to5 → live`, and the values change every 5 seconds.
3. **Publish the cloud dashboard.** Do this on the laptop, once:
   ```
   npm install -g firebase-tools
   firebase login
   cd 14_RASPBERRY_PI_SOFTWARE/aquasentinel/cloud
   firebase deploy --only hosting,database
   ```
   - ✅ Open https://aquasentinel-live.web.app on any phone. It shows the station live.

## J. The six-water demo (at the booth)

1. **Before visitors come:**
   - switch on 5 minutes early, so the MQ-3 can warm up;
   - wait for **NORMAL**;
   - press **Learn new water** after filling the dish with fresh water.
2. **Run the waters.** Each takes about 5 seconds:

   | Do | Dashboard | Beacon |
   |---|---|---|
   | clean tap water | NORMAL | green |
   | a spoon of salt | INDUSTRIAL | red, sample, SMS |
   | a little vinegar | ACIDIC | red, sample, SMS |
   | a spoon of soil | RUNOFF | red, sample, SMS |
   | sanitiser on a tissue at the bottle cone | SOLVENT | red, sample, SMS |
   | unplug the temperature probe | SENSOR FAULT after 10–15 s | blinking red |

3. **Avoid flooding the phones.** Only one SMS goes out per 10 minutes. For the demo, tell the team their phones will buzz once.

## K. Every day

| What | How |
|---|---|
| Switch on | Plug in the power. Everything starts by itself. |
| Switch off | `sudo shutdown now`. Wait for the green light to stop, then unplug. Never just pull the plug while it is writing. |
| Is it OK? | `bash ~/aquasentinel/tools/doctor.sh` |
| Today's readings | `~/aquasentinel/logs/readings_YYYY-MM-DD.csv`, or `http://<pi-address>:8080/api/csv` |
| Dashboard on a phone, same Wi-Fi | `http://<pi-address>:8080`. Find the address with `hostname -I`. |
| Dashboard from anywhere | https://aquasentinel-live.web.app (after step I3) |

## L. Updating later

Copy the new `aquasentinel` folder from the laptop to the stick. Then on the Pi:
```
cp -r /media/$USER/*/aquasentinel ~/aquasentinel_new
bash ~/aquasentinel_new/update.sh
rm -rf ~/aquasentinel_new
```
- The update keeps your settings, calibration, `secrets.json` and logs.
- If the update brings new Nano firmware, it asks before flashing it.

## M. If something goes wrong

| You see | Do |
|---|---|
| Lightning bolt or *POWER SUPPLY TOO WEAK* | Use the official 5.1 V 2.5 A supply. Pump and sensors run from the AUX supply, not the Pi. |
| *Sensor hub offline* | Check the Nano's USB cable and use a working port. Run `doctor.sh`. |
| `Nano firmware v1` in doctor | `bash ~/aquasentinel/tools/flash_nano.sh` |
| Flashing fails | Try another cable or port. Press the Nano's reset button the moment flashing starts. |
| *SIM800L · no answer* | Check for 4.0 V on J17, the TX/RX wires on J18 and the antenna. Run `python3 ~/aquasentinel/tools/check_hardware.py`, stopping the service first as that tool says. |
| *cloud: offline* | Nothing is lost: readings wait and go up when the Wi-Fi is back. |
| `FAIL sign-in` in cloud_test | Check the e-mail and password in `secrets.json`. They must match step C2 exactly. |
| `FAIL write` in cloud_test | In the Firebase Data tab, `owners/kopargaon-1to5` must hold this user's UID (step C4). |
| Dashboard does not open | Open the browser at `http://localhost:8080`. Check the service: `systemctl status aquasentinel`. |
| Anything else | Run `journalctl -u aquasentinel -n 50` and send the output to the software lead. |
