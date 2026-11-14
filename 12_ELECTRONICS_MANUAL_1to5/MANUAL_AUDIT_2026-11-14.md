# Manual Audit — AquaSentinel_LIVE_1to5_Electronics_Assembly_Manual.pdf

Date: 2026-11-14. Auditor: automated project manager (with full project files + recovered conversation history).

## Verdict
The PDF dated 10 Nov 2026 ("Revision 1.0 · Electronics design v2, bay layout") taught the **abandoned Hub-HAT / bay-v2 design**.
Building from it would fail: it wires the Pi to read sensors directly through an ADS1115, uses a DS3231, a 12 V adapter
with two buck converters, a rain sensor, an MX1508, and GPIO assignments that no longer exist.
The build actually made on **12–13 Nov 2026** is the **Arduino Nano + Sensor Hub PCB v1.2 + Raspberry Pi 3B+**.
The manual has been rewritten as **Revision 2.0 (14 Nov 2026)** and installed at the original path.

## Errors found in the old PDF (v1.0, 10 Nov)

| # | Wrong claim in old manual | Verified truth (12–13 Nov build) |
|---|---|---|
| 1 | "A Raspberry Pi 3B+ … and one 12 V adapter make the 1:5 model live" | An **Arduino Nano on the Sensor Hub PCB v1.2** reads all sensors; the Pi only decides/communes. Power input is **AUX 5 V on J12**. |
| 2 | "1 Hub HAT, 12 plug-in headers" | **No HAT.** Our own milled PCB v1.2 with connectors **J1–J18**. |
| 3 | "10 boards on one slide-out tray" (bay v2, LD-S08 tray) | One carrier PCB; it sits in the model base. |
| 4 | "12 V 2 A in, 2 buck converters" | **5 V in** → step-up **9 V** (pH board) → step-down **4.0 V** (SIM800L). |
| 5 | "8 sensors" (incl. rain) | **7 sensors**: pH, TDS, turbidity, DS18B20, DHT11, LDR, MQ-3. Rain dropped. |
| 6 | config.txt: `dtparam=i2c_arm=on`, ADS1115 0x48, DS3231 0x68, `dtoverlay=w1-gpio,gpiopin=4`, `dtoverlay=dht11,gpiopin=17`, `dtoverlay=i2c-rtc,ds3231` | All gone. Only serial for the SIM800L: `enable_uart=1` + `dtoverlay=disable-bt` (GPIO14/15). |
| 7 | `gpio=13=op,dh` (TDS supply), `gpio=22=op,dl` (rain), `gpio=23=op,dl` (pump), `gpio=12,26=op,dl` (beacon), `gpio=16=ip,pu` (ACK button) | Nothing on the Pi. TDS switch = Nano **A0**; beacon = Nano **D7/D8/D9**; pump = Nano **D10**. No ACK button, no rain. |
| 8 | `i2cdetect` expecting 0x48 / 0x57 / UU at 0x68 | **No I2C devices at all** on the Pi. |
| 9 | DHT11 through the kernel driver / `/sys/bus/iio` | DHT11 on the **Nano (D3)**, arrives in the USB JSON line. |
| 10 | MX1508 pump driver | **Mini L298N** (control J7, power J13). |
| 11 | Level converter, DS3231 RTC, SMA antenna on the tray, DC jack panel, inline fuse, WAGO | Dropped. Logic divider (4.7 k/10 k) is **on the board (J18)**; SIM800L direct on J17. |
| 12 | Pi reads sensors each cycle | **Nano reads every sensor 1×/s** and streams one JSON line over USB (115200) to the Pi. |
| 13 | Pi-side software driving GPIO (old booth sentinel) | `14_RASPBERRY_PI_SOFTWARE` — Nano link over USB, SIM800L on `/dev/serial0` (9600), dashboard :8080. |
| 14 | Views of "electronics bay v2" assembly | Replaced with Sensor Hub renders + live_v2 model images. |

## Corrected manual (Revision 2.0 — installed 14 Nov 2026)
- 17 pages: what changed → system block → parts → board tour (J1–J18) → power chain → board build →
  sensor wiring → sensor 3D → SIM800L/Pi link → model mount → Nano flash → Pi setup → calibration/checks →
  six demo waters + decision rules → troubleshooting + revision history.
- New accurate diagrams: `system_block_v2.svg`, `power_chain_v2.svg`, `wiring_map_v2.svg`.
- Sources of truth used: `PCB_SENSOR_HUB_v1/PCB_v1.2_BUILD_AND_PINOUT.md` (v1.2), `firmware/aquasentinel_nano/aquasentinel_nano.ino`,
  `14_RASPBERRY_PI_SOFTWARE/aquasentinel/PI_SETUP_AND_OPERATION.md`, `install.sh`, `config.json`, `sensors.py`, `brain.py`, recovered 12–14 Nov conversations.
- Verification: 17-page PDF, per-page content checks all pass; old-design terms appear only on the revision-history page.

## Backups
- The old v1.0 PDF was deleted in the 14 Nov 2026 purge; this audit is the record of why it was replaced.
- Build sources (editable): `12_ELECTRONICS_MANUAL_1to5/_build_v2/` (manual_v2.html, 3 SVGs, verify_pdf.py).
