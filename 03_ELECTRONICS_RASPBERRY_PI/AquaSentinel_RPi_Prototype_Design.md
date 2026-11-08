# AquaSentinel: Raspberry Pi prototype engineering design

**Version 1.0, 28 October 2026.** Prepared by Team Sanjivani Hero's Journey.
**Inputs:** the team's three handwritten notes (main problems, component list, component purposes). They are treated as the
definitive component selection.
**Status:** a design to build and test. Nothing in it has been wired or measured yet.

---

## 0. Summary

**Verdict:** the selected hardware can make a working AquaSentinel bench prototype for the finale (19–20 Nov 2026). It needs about
**₹3,000 of small additions**: an analog-to-digital converter (ADC), voltage regulators, a level shifter, a real-time clock and
switching parts. It can also run a short supervised field pilot. It is not yet a long-unattended field station: the main limits are
power, 2G-only communication and sensor drift.

**The ten decisions that matter most**

1. **Add 2 × ADS1115 ADCs.** The Raspberry Pi has no analog inputs. pH, TDS, turbidity, MQ-3, the light sensor, the rain sensor and the
   battery voltage are all analog signals. [1][3]
2. **Keep every signal into the Pi and the ADC at or below 3.3 V.** The Pi's pins are not 5 V tolerant. The turbidity, MQ-3 and
   (likely) pH boards can output up to 4.5–5 V, so each gets a 12 kΩ / 20 kΩ divider and an RC filter. [1][3][7]
3. **Give the SIM800L its own 4.0 V supply rated for 2 A bursts, with a 1000 µF low-ESR capacitor.** Never power it from the Pi.
   Level-shift the Pi's transmit line, because the SIM800L accepts at most 3.1 V on its serial input. [4]
4. **Never power the pH and TDS boards at the same time.** Two powered probes in the same water disturb each other. Switch each board's
   supply and read them one after the other; isolator boards are the more expensive alternative. [17]
5. **Keep the "mini L298N" only for a pump of 6 V or less.** It is really an MX1508 chip (motor supply 2–10 V, 1.5 A). For a 12 V
   pump, use a logic-level MOSFET; the pump turns one way only, so it doesn't need an H-bridge. [14][13]
6. **Use the MQ-3 only as a vapour indicator in a sealed headspace above a sample,** as the team planned. It needs a 48 h first
   burn-in, its heater draws up to 0.9 W, and it reacts to alcohol and some solvents. It does not measure the water. [5]
7. **Each cycle reads all sensors first, then transmits and runs the pump.** That keeps GSM bursts and pump noise away from the analog
   readings.
8. **Protect the SD card and the clock.** Run a read-only root file system, the hardware watchdog and a DS3231 real-time clock, so
   power cuts don't corrupt the card or lose the time.
9. **Field power:**
   - With the Pi always on, the system needs about **100 Wh/day**: a 50 W panel and a 20 Ah battery.
   - Waking the Pi only every 15 minutes cuts that to about **19 Wh/day**, which fits the R3's 20 W panel and 6 Ah battery.
10. **Claims language:** call it a prototype built from available parts. The R3 field design (ESP32, industrial RS485 probes, LTE)
    stays the product the jury saw.

---

## 1. Scope, inputs and assumptions

**Problems the team wants to address** (note 1):
- industrial discharge;
- agricultural runoff;
- sewage and wastewater;
- oil spills and leaks;
- plastic and solid waste.

**Hardware the team has** (notes 2 and 3):

| # | Item (team's words) | Team's purpose |
|---|---|---|
| 1 | Raspberry Pi 3 Model B+ 1 GB | Main on-board computer |
| 2 | Rain sensor module (plate + module, "raindrop sensor") | Rain detection |
| 3 | Mini DC submersible pump, 3–12 V | Collect a 250 mL water sample |
| 4 | Mini L298N | Control the pump |
| 5 | LDR | Day/night tracking |
| 6 | MQ-3 | VOCs, solvents or ethanol in the sealed air space above a contaminated sample |
| 7 | TDS Meter V1.0 | Total dissolved solids |
| 8 | DHT11 | Air temperature and humidity above the water |
| 9 | SIM800L GSM/GPRS ("red PCB module") | Send data, messages and alerts |
| 10 | DS18B20 digital temperature probe | Water temperature |
| 11 | pH sensor | Acidity / alkalinity, 0–14 |
| 12 | Turbidity sensor | Water clarity (infrared scattering) |

**Assumptions** (confirm them; section 15 lists what to check):

| # | Assumption | Why it matters |
|---|---|---|
| A1 | The pH sensor is the common **PH-4502C board with an E-201 BNC probe**, powered at 5 V. If it is DFRobot SEN0161-V2 (output 0–3.0 V), its divider can be removed. | Output range and calibration method |
| A2 | "TDS Meter V1.0" is the **DFRobot SEN0244 board or a clone** (3.3–5.5 V in, 0–2.3 V out, 0–1000 ppm). [6] | Range and ADC channel |
| A3 | The turbidity sensor is **DFRobot SEN0189 or a clone** (5 V, 0–4.5 V out, top not waterproof). [7] | Divider and housing |
| A4 | The pump is the common **3–6 V mini submersible pump** (130–220 mA, 80–120 L/h). The note says 3–12 V; a 12 V pump changes the driver. [16] | Driver choice |
| A5 | The "red PCB" SIM800L is the **bare mini module** (VBAT 3.4–4.4 V, no on-board regulator). A blue "SIM800L V2 5V" board has its own regulator and level shifting. [4] | Power and level shifting |
| A6 | The rain and LDR modules are **LM393 comparator boards** with digital (DO) and analog (AO) outputs, working at 3.3–5 V. [15] | Can connect directly at 3.3 V |
| A7 | Finale demo: indoors on mains power. Field pilot: a drain, canal or river bank, 1–2 weeks, supervised. | Power and enclosure sizing |

---

## 2. What the system can and cannot detect

The sensors measure **physical and chemical indicators**. They do not identify specific pollutants. A change in indicators shows that
something happened; the 250 mL sample tells the lab what it was.

| Problem | Measured directly | Can only be inferred | Cannot detect with this hardware | Scientifically justified addition |
|---|---|---|---|---|
| **Industrial discharge** | TDS rise (dissolved salts and metal ions), pH out of range, water temperature rise (thermal discharge), turbidity | A discharge event, from a sudden multi-parameter change | Which chemical; heavy metals; COD | Lab analysis of the auto-collected sample. An EC sensor with a wider range than TDS (0–20 mS/cm) |
| **Agricultural runoff** | Turbidity rise (sediment), TDS rise | Runoff when the rain sensor says "raining" and turbidity or TDS jumps | Nitrate, phosphate, pesticides | Nitrate ion-selective electrode or lab tests |
| **Sewage and wastewater** | Turbidity, TDS, pH and temperature changes | Organic pollution, only weakly | Dissolved oxygen, ammonia, BOD, coliform bacteria | **Dissolved oxygen sensor:** the single most useful addition for sewage. It is already in the R3 design |
| **Oil spills and leaks** | Nothing directly. The MQ-3 responds weakly to some petrol vapours | A volatile fuel or solvent spill, from the headspace test | Heavy oils (diesel, crude); oil film thickness | Oil-in-water fluorescence sensor (expensive), or a camera watching for sheen |
| **Plastic and solid waste** | Nothing | Nothing | Floating plastic, debris | **Raspberry Pi Camera Module 3** with image capture, plus later object detection. The Pi is well suited to this |

**MQ-3 in particular:**
- **What it detects:** alcohol vapour, 25–500 ppm in air, and it is cross-sensitive to other gases. [5]
- **The method that works:** fill a sample, seal the air space above it, let vapours equilibrate, then read the MQ-3. A rise means
  "volatile organics present". A distillery effluent, solvent or petrol spill is the plausible cause.
- **How to state it:** treat the reading as an indicator. Never report it as a concentration in water.

---

## 3. Component analysis

### 3.1 Raspberry Pi 3 Model B+ (main computer)
- **Key specs:**
  - power supply 5 V, 2.5 A recommended; about 500 mA typical bare-board current;
  - GPIO at 3.3 V and **not 5 V tolerant**, up to 16 mA per pin and 50 mA for all pins together. [1]
- **No analog inputs**, so it needs an external ADC.
- **Interfaces used:**
  - I2C1 (GPIO2/3) for the two ADCs and the RTC;
  - 1-Wire (GPIO4) for the DS18B20;
  - a kernel driver (dtoverlay) for the DHT11;
  - the PL011 UART on GPIO14/15 for the SIM800L;
  - WiFi for MQTT;
  - GPIO for the pump, power switches, LED and button. [1][2][12]
- **Limitations:** about 2.5 W or more continuously; SD-card corruption on sudden power loss; no real-time clock. It needs shade in an
  enclosure.
- **Verdict:** a good choice for the prototype (Python, logging, dashboard, camera later). For a solar field unit, wake it on a timer
  (section 5.3).

### 3.2 ADS1115 ADC (to add)
- **Key specs:**
  - 16-bit, 4 single-ended inputs, I2C (addresses 0x48–0x4B), supply 2.0–5.5 V;
  - programmable gain, full-scale range ±0.256 V to ±6.144 V;
  - inputs must stay between ground and the supply voltage. [3]
- **Design:**
  - Power both ADCs from the Pi's 3.3 V pin, so the I2C lines stay at 3.3 V and need no level shifting.
  - Use the ±4.096 V range (125 µV per step) and keep every input below 3.3 V with dividers.
  - #1 at 0x48 reads the water sensors; #2 at 0x49 reads the housekeeping signals.

### 3.3 pH sensor (PH-4502C assumed)
- **Principle:** a glass electrode produces about 59 mV per pH unit at 25 °C. The board amplifies and offsets this so the output is near
  2.5 V at pH 7 after the offset is trimmed. [9]
- **Supply:** 5 V.
- **Output:** analog Po. Listings disagree on the output range, so treat it as **up to 5 V** and divide it.
- **Calibration:**
  1. Offset: short the BNC input and trim the potentiometer until Po reads 2.50 V. [9]
  2. Two or three points in buffers pH 4.01, 6.86/7.00 and 9.18.
- **Limitations:**
  - The probe must be stored wet in KCl.
  - The glass bulb is fragile.
  - Readings drift, so calibrate before each demo day and weekly in the field.
  - Readings are temperature dependent; the DS18B20 corrects for this.
  - Other powered probes in the same water disturb the reading (section 6.3).

### 3.4 TDS Meter V1.0 (DFRobot SEN0244 type)
- **Key specs:** 3.3–5.5 V, 0–2.3 V output, 3–6 mA, **0–1000 ppm**, ±10 % of full scale at 25 °C, 2-needle waterproof probe. [6]
- **Conversion** (DFRobot sample code):
  - Temperature compensation: k = 1 + 0.02 × (T − 25 °C), then V' = V / k.
  - TDS (ppm) = (133.42 V'³ − 255.86 V'² + 857.39 V') × 0.5.
- **Limitations:**
  - TDS is estimated from conductivity, so it cannot tell which ions are present.
  - **The 1000 ppm ceiling is about 2,000 µS/cm**, below the R3's 2,250 µS/cm alarm level, so the TDS alarm must sit lower (section 7.4).
  - It disturbs the pH probe if both are powered at once.
- **Connection:** direct to the ADC (its output stays below 3.3 V), with an RC filter.

### 3.5 Turbidity sensor (SEN0189 type)
- **Principle:** infrared light is scattered by suspended particles; the output voltage **falls** as turbidity rises. [7]
- **Key specs:** 5 V, about 40 mA, analog 0–4.5 V. **The top of the probe is not waterproof.** [7]
- **Conversion:** DFRobot's approximate curve, valid for 2.5–4.2 V on a 5 V supply: NTU ≈ −1120.4 V² + 5742.3 V − 4352.9. It is not a
  certified NTU; use it for trends.
- **Limitations:**
  - Ambient light and bubbles affect the reading, so measure inside the housing, out of direct sun.
  - The optics foul and need cleaning.
  - Calibration against standards is only approximate.
- **Connection:** 12 k / 20 k divider (4.5 V → 2.8 V), then RC filter, then ADC.

### 3.6 DS18B20 waterproof probe
- **Key specs:** 3.0–5.5 V; −55 to +125 °C; ±0.5 °C from −10 to +85 °C; 9–12 bit resolution; 750 ms per 12-bit conversion; 1-Wire
  bus with a 4.7 kΩ pull-up. [10]
- **On the Pi:** the `w1-gpio` overlay on GPIO4; the readings appear under `/sys/bus/w1/devices/28-*`. [12]
- **Use:** water temperature, temperature compensation for pH and TDS, and thermal-discharge detection.

### 3.7 DHT11 (air temperature and humidity)
- **Key specs:** humidity 20–90 % ±5 %; temperature 0–50 °C ±2 °C; 3.3–5.5 V; a single-wire protocol with tight timing; read no faster
  than every 1–2 s. [11]
- **On the Pi:** use the kernel driver `dtoverlay=dht11,gpiopin=17`. Python bit-banging of this protocol is unreliable under Linux. [12]
- **Limitations:**
  - Close to water the humidity often exceeds 90 %, outside the DHT11's range.
  - Mount it in a louvered shade 0.5–1 m above the water.
- **Use:** context and correction for the MQ-3, plus the enclosure climate.

### 3.8 MQ-3 alcohol / VOC gas sensor
- **Key specs** (Winsen datasheet): [5]
  - heater 5.0 V ±0.1 V, about 29 Ω, **up to 900 mW**;
  - detection range **25–500 ppm alcohol**;
  - **preheat over 48 hours** before first use;
  - readings depend on temperature and humidity.
- **Module:** the sensor and a load resistor RL form a divider; the analog output reaches up to 5 V and needs dividing. The digital
  output (an LM393 threshold) is 5 V logic and is not used here.
- **Use:**
  1. Calculate Rs = RL × (5 V − Vout) / Vout.
  2. Find R0 in clean air after burn-in.
  3. Alarm on Rs/R0 dropping in the sealed headspace test.
  4. Measure RL on your module with a multimeter.
- **Limitations:** cross-sensitive to other vapours; slow recovery; high power. It is an indicator only.

### 3.9 Rain sensor (plate + LM393 module)
- **Function:** a nickel-plated comb, wet or dry. The module gives a digital and an analog output. [15]
- **Supply:** 3.3 V, so the digital output can go straight to a GPIO pin.
- **Limitations:** the comb **corrodes when powered continuously**. Power it only while reading, through a transistor switch.
- **Use:** context. A turbidity or TDS jump while it rains is flagged "runoff-likely" (agricultural runoff).

### 3.10 LDR (light-dependent resistor)
- **Function:** a photoresistor on an LM393 module.
- **Use:** the digital output gives day/night; the analog output gives a rough light level on ADC #2.
- **Limitations:** it is shaded by the panel and fooled by street lights. The RTC time plus a sunrise table is a more reliable
  day/night signal; keep the LDR as a sanity check and for dimming the status light at night.

### 3.11 Mini submersible pump
- **Typical** 3–6 V model: 130–220 mA, 80–120 L/h, lift 40–110 cm (some listings print mm by mistake), about 500 h rated life. **Must not run dry.** [16]
- **Fill time:** 250 mL at 100 L/h takes about 9 s. Calibrate it on the bench, because tubing and lift reduce the flow.
- **Placement:** the pump must sit in the water (with the intake strainer) and push up to the bottle; a 0.2 m lift is well within its range.

### 3.12 "Mini L298N" motor driver
- **What it is:** these boards carry an **MX1508** chip (sometimes a clone):
  - motor supply 2–10 V, 1.5 A continuous;
  - logic inputs 1.8–7 V, so the Pi's 3.3 V GPIO is fine. [14]
- **Verdict:** suitable for a pump of 6 V or less. **Not suitable for a 12 V pump.**
- **Why not the full-size L298N:** it is a bipolar bridge rated to 46 V and 2 A per channel, but it loses roughly 2–3 V across the
  bridge. [13]
- **For one direction only,** the simplest option is a logic-level MOSFET (IRLZ44N or AO3400) with a flyback diode.

### 3.13 SIM800L GSM/GPRS
- **Key specs** (SIMCom Hardware Design V2.02): [4]
  - quad-band 2G GSM/GPRS;
  - **VBAT 3.4–4.4 V, 4.0 V recommended, up to 2 A bursts**; a low-ESR bypass capacitor (100 µF or more) is strongly recommended;
  - 17 mA idle; 175–530 mA average during GPRS transfer.
- **Serial levels:** input high 2.1–3.1 V, output high 2.8 V. **The Pi's 3.3 V transmit line exceeds the 3.1 V maximum**, so it needs a
  divider or level shifter. The SIM800L's own transmit line (2.8 V) is read correctly by the Pi.
- **Reset:** a 3.3 V GPIO can drive the RESET pin directly. [4]
- **Network:**
  - It is 2G only. In India, Jio has no 2G network. Vodafone Idea retired 3G but kept 2G, and Airtel still runs 2G; no shutdown
    announcement was found as of this research. [19]
  - Use an **Airtel or Vi SIM**, and check the signal strength at the site with `AT+CSQ`.
  - Upgrade path: the SIMCom A7670C LTE Cat-1 module from the R3 design.

---

## 4. System architecture

*The wiring is drawn in SOLIDWORKS drawing [AS-LIVE-ELEC-01](SOLIDWORKS_Electronics_Bay/AS-LIVE-ELEC-01_Electronics_Bay_Drawing.pdf) and as a diagram on the [project page](../README.md#-one-raspberry-pi-eight-sensors-three-actions).*

**Interface decisions**

| Concern | Decision |
|---|---|
| Analog inputs | 2 × ADS1115 on I2C, powered at 3.3 V. Every input is limited to 3.3 V |
| Voltage levels | 3.3 V everywhere at the Pi. 5 V module outputs are divided. The Pi's transmit line to the SIM800L goes through a 1 kΩ / 2 kΩ divider (3.3 → 2.2 V) |
| pH and TDS in the same water | Switch each board's supply and never power both at once. Read them in separate time windows |
| Noise | Read the analog sensors only while the pump and GSM radio are idle. Average 32 samples, take the median, RC filter on every input |
| Timekeeping | DS3231 RTC on I2C (0x68), plus network time when online |
| Storage | SQLite on the SD card with a read-only root file system; daily CSV export |

---

## 5. Electrical design

### 5.1 Raspberry Pi pin map (BCM numbering)

| Pi pin | GPIO | Connects to | Notes |
|---|---|---|---|
| 1 | 3.3 V | ADS1115 #1 and #2, DS3231, DHT11, DS18B20 pull-up, rain and LDR modules | About 20 mA in total |
| 2, 4 | 5 V | (Pi supply input from Buck A, or use micro-USB) | Feeding the 5 V pins bypasses the Pi's input fuse; add an external fuse |
| 3 / 5 | GPIO2 / GPIO3 | I2C SDA / SCL: both ADS1115s, DS3231 | The modules have pull-ups |
| 7 | GPIO4 | DS18B20 data | 4.7 kΩ to 3.3 V |
| 8 | GPIO14 (TXD) | SIM800L RXD **through a 1 kΩ / 2 kΩ divider** | VIH maximum 3.1 V [4] |
| 10 | GPIO15 (RXD) | SIM800L TXD | 2.8 V output, read correctly |
| 11 | GPIO17 | DHT11 data | `dtoverlay=dht11,gpiopin=17` |
| 12 | GPIO18 | SIM800L RST | Directly, or through an NPN transistor |
| 13 | GPIO27 | Rain module DO | Module powered at 3.3 V |
| 15 | GPIO22 | Rain module power switch (NPN to a P-MOSFET) | Powered only while reading |
| 16 | GPIO23 | MX1508 IN1 (pump) | IN2 tied low |
| 29 | GPIO5 | LDR module DO | |
| 31 | GPIO6 | pH board 5 V high-side switch | Never on together with GPIO13 |
| 33 | GPIO13 | TDS board high-side switch | |
| 35 | GPIO19 | MQ-3 heater MOSFET | About 180 mA heater current |
| 36 | GPIO16 | ACK / reset button to ground | Internal pull-up |
| 37 | GPIO26 | Status LED / beacon (through a transistor) | |
| 6, 9, 14 … | GND | Star ground at ADS1115 #1 | |

### 5.2 ADC channels

| ADC | Ch | Signal | Raw range | Conditioning | Range at the ADC |
|---|---|---|---|---|---|
| #1 0x48 | A0 | pH Po | 0–5 V (centred about 2.5 V) | 12 k / 20 k divider, 1 k + 100 nF | 0–3.1 V |
| #1 | A1 | TDS | 0–2.3 V | 1 k + 100 nF | 0–2.3 V |
| #1 | A2 | Turbidity | 0–4.5 V | 12 k / 20 k, 1 k + 100 nF | 0–2.8 V |
| #1 | A3 | MQ-3 AO | 0–5 V | 12 k / 20 k, 1 k + 100 nF | 0–3.1 V |
| #2 0x49 | A0 | LDR AO | 0–3.3 V | 100 nF | 0–3.3 V |
| #2 | A1 | Rain AO | 0–3.3 V | 100 nF | 0–3.3 V |
| #2 | A2 | Battery voltage | 0–14.6 V | 100 k / 22 k divider | 0–2.6 V |
| #2 | A3 | Spare (DO probe or pump current later) | | | |

To recover the sensor voltage, multiply by 1.6 for a 12 k / 20 k divider, and by 5.55 for the battery divider. The divider's source
resistance causes a small gain error; the per-sensor calibration removes it.

### 5.3 Power architecture and budget

*Power rails: see the table below and drawing [AS-LIVE-ELEC-01](SOLIDWORKS_Electronics_Bay/AS-LIVE-ELEC-01_Electronics_Bay_Drawing.pdf), sheet 2.*

| Load | Power | Always-on: Wh/day | Pi woken 3 min every 15 min: Wh/day |
|---|---|---|---|
| Raspberry Pi 3 B+ (500 mA typical at 5 V) [1] | about 2.5 W | 60 | 12 |
| MQ-3 heater (on continuously in always-on mode; about 1 h/day for tests in timed mode) [5] | about 0.86 W | 20.6 | 0.9 |
| ADCs, RTC, sensor boards (switched) | about 0.15 W | 3.6 | 0.7 |
| SIM800L idle (17 mA at 4 V) plus a few SMS [4] | about 0.07 W | 1.7 | 1.7 |
| Pump (30 s per event) | about 1 W | <0.1 | <0.1 |
| Wake-up timer board | | | about 0.5 |
| Buck converter losses (15 %) | | +13 | +2.4 |
| **Total** | | **about 100 Wh/day** | **about 19 Wh/day** |

**Sizing:**

| Mode | Battery | Panel |
|---|---|---|
| **Always on** | 12.8 V 20 Ah LiFePO4 (2 days) | 50 W (100 Wh ÷ (4.5 sun-hours × 0.7) ≈ 32 W, plus monsoon margin) |
| **Timed** (recommended for the field) | 12.8 V 6 Ah (about 3.5 days; the R3's battery) | 20 W (the R3's panel) |

Timed mode needs a wake-up timer board such as Witty Pi, or a small microcontroller, to switch the Pi on.

**On the bench and at the finale:** use a 12 V 3 A adapter, or a 5 V 3 A adapter for the Pi plus separate 4 V and 5 V rails.

### 5.4 Protection, grounding and noise

- **One star ground point** at ADS1115 #1:
  - the analog grounds return there;
  - the pump and SIM800L currents return directly to the supply bus, not through the analog ground.
- **Every ADC input:** 1 kΩ series resistor and 100 nF to ground. On long sensor cables add a BAT54S clamp to 3.3 V and ground.
- **SIM800L:**
  - 1000 µF low-ESR plus 100 nF across VBAT, and a 5.1 V Zener as SIMCom recommends; [4]
  - short wires of at least 0.5 mm²;
  - an antenna outside the box, away from the analog cables.
- **Pump:** a flyback diode (1N5819) and 100 nF across the motor. Run it only after the analog readings.
- **Main supply:** fuse (3 A), reverse-polarity protection and a TVS diode on the 12 V input.
- **Wiring:** twisted or shielded sensor cables, kept away from the pump and antenna wires.

---

## 6. Sampling mechanism and sensor placement

### 6.1 Continuous sensing (every cycle)
The pH, TDS, turbidity and DS18B20 probes sit in the **3D-printed circular sensor housing** in `12_SIMPLE_SENSOR_HOUSING`:
- **TDS probe:** goes in the former "EC" port; its probe is smaller, so the bore will be resized.
- **Spare port:** takes the pump intake.

Measure every probe before printing; resizing the bores is a one-minute rebuild.

### 6.2 Event sample and MQ-3 headspace test

1. The alert logic confirms an event (section 7.4).
2. The pump fills the 250 mL bottle to about **150 mL**, leaving about 100 mL of air:
   - time-based fill, calibrated on the bench (about 6 s at 100 L/h);
   - an optional float switch stops overfill.
3. The bottle is sealed. Its lid carries the MQ-3, which has been preheated because the heater is already on.
4. Wait **5 minutes** for vapours to equilibrate, then read Rs/R0 every 10 s for 2 minutes. Record the minimum.
5. Log the result, send the SMS, and label the bottle with the time for the lab. One bottle per event; a replaced bottle re-arms
   sampling.

**Caveats:**
- The MQ-3 heater warms the headspace slightly. For a lab-grade BOD sample, use a second, cooled bottle.
- The tubing holds about 20 mL from the previous cycle. Run the pump for 2 s to waste first, if the tubing allows it.

### 6.3 Avoiding pH and TDS interference
The TDS board drives an AC signal into the water, while the pH probe is a high-impedance electrode. Powered together they share a
current path through the water and their common ground. DFRobot documents this and sells isolators as the fix. [17]

The design instead switches each board's supply with a P-MOSFET high-side switch (AO3401 plus an NPN driver):
1. **TDS window:** TDS on for 5 s, then read.
2. **TDS off.**
3. **pH window:** pH on for 30 s to settle, then read.

**Bench test:** compare the pH reading with the TDS board switched on and off. If the difference stays above 0.05 pH, add DFRobot
DFR0504 isolators at ₹2,219 each.

---

## 7. Software design

### 7.1 Operating system configuration
Raspberry Pi OS Lite (Bookworm). In `/boot/firmware/config.txt`:

```
dtparam=i2c_arm=on
dtoverlay=w1-gpio,gpiopin=4
dtoverlay=dht11,gpiopin=17
enable_uart=1
dtoverlay=disable-bt
dtoverlay=i2c-rtc,ds3231
dtparam=watchdog=on
```

`disable-bt` gives the reliable PL011 UART on GPIO14/15. Then:
- disable `hciuart`;
- in `raspi-config`, turn the serial login shell off and the serial hardware on;
- in `raspi-config`, enable the overlay file system (read-only root) before deployment. [2][12]

### 7.2 Services (Python 3, systemd, `Restart=always`)

| Service | Job | Libraries |
|---|---|---|
| `acquire` | Runs the measurement cycle (section 8), filters readings, applies calibration | adafruit-circuitpython-ads1x15, gpiozero, sysfs (1-Wire, DHT11) |
| `decide` | Hard limits, hourly baselines, 2-of-3 confirmation, events | Plain Python (the R3 algorithm, ported) |
| `store` | SQLite tables `readings`, `events`, `samples`; daily CSV | sqlite3 |
| `comms` | SIM800L SMS and HTTP over GPRS; MQTT over WiFi; retry queue | pyserial, paho-mqtt |
| `sampler` | Pump control, one bottle per event, MQ-3 headspace test | gpiozero |
| `health` | Watchdog, disk and battery checks, daily status SMS | |

**Data flow:** sensors → `acquire` → SQLite → `decide` → events → `sampler` / `comms`.
- **Dashboard:** MQTT topic `aquasentinel/<site>/readings` → Node-RED or Grafana on a laptop for the finale, a cloud broker later.
- **SMS commands:** `STATUS`, `SAMPLE`, `RESET` from approved numbers only.

### 7.3 SIM800L commands
- **Start-up:** `AT`, `AT+CPIN?`, `AT+CSQ` (signal 10 or more is usable), `AT+CREG?`.
- **SMS:** `AT+CMGF=1`, then `AT+CMGS="+91…"`, the text and Ctrl-Z.
- **GPRS:** `AT+SAPBR=3,1,"APN","<operator APN>"`, `AT+HTTPINIT`, `AT+HTTPPARA="URL",…`, then `AT+HTTPACTION=1`.
- **Network time:** `AT+CLTS=1`.
- Keep phone numbers and server keys in a local configuration file, never in the repository.

### 7.4 Alert logic

| Parameter | Watch | Alarm | Basis |
|---|---|---|---|
| pH | outside 6.5–8.5 | outside 6.0–9.0 | CPCB water-quality criteria; the R3 limits [18] |
| TDS | +25 % over the hourly baseline | above 900 ppm (near the sensor's ceiling) or +50 % | Sensor range [6]; the CPCB irrigation limit (EC 2,250 µS/cm) is beyond this sensor |
| Turbidity | +25 % over baseline (estimated NTU) | +50 % | Relative, because readings are uncalibrated |
| Water temperature | +2 °C over the hourly baseline | +3 °C | Thermal discharge |
| MQ-3 headspace | Rs/R0 below 0.8 | below 0.6 | Relative, from clean-air R0 |
| Rain | — | — | Context only: raises the turbidity thresholds and tags events "runoff-likely" |

- **Event:** 2 of the last 3 cycles abnormal on any parameter, or any alarm confirmed on 2 consecutive cycles.
- **Actions:**
  1. Log it.
  2. Turn the beacon red.
  3. Send an SMS to the list.
  4. Send an HTTP or MQTT message.
  5. Take one sample, with the MQ-3 test.
- **Lockout:** no second sample until the event clears or the bottle is replaced.
- **Faults:** a dead or disconnected sensor raises **SENSOR FAULT**, never "normal". This is the R3 audit's fail-safe fix.

---

## 8. Measurement cycle

Every 15 minutes in the field; every 15 s in demo mode, labelled as such.

| Time | Step |
|---|---|
| 0 s | Wake: read the DS3231 time and battery voltage; DS18B20 conversion (750 ms) |
| 1 s | DHT11 read; rain module on, read its outputs, off; LDR read |
| 2 s | Turbidity: 32 samples, median |
| 3 s | TDS window: TDS on, 5 s settle, 32 samples, off |
| 9 s | pH window: pH on, 30 s settle, 32 samples, off (with temperature compensation) |
| 40 s | Compute, store, decide |
| 41 s | Communicate: GSM or MQTT; pump only if an event was confirmed |
| about 60 s | Sleep (timed mode: the Pi shuts down until the next wake) |

---

## 9. Calibration

| Sensor | Procedure | How often |
|---|---|---|
| pH | 1. Offset: short the BNC, trim Po to 2.50 V. 2. Two-point calibration in pH 6.86/7.00 and 4.01 (add 9.18 for alkaline water). 3. Record slope and offset in the configuration | Before each demo day; weekly in the field |
| TDS | Measure a reference solution: 707 ppm (1,413 µS/cm KCl) or a meter-checked sample. Adjust the K factor. Temperature-compensate to 25 °C | Every 2 weeks |
| Turbidity | Measure clear filtered water (about 0 NTU) and two dilutions of a cloudy suspension, cross-checked against a lab turbidimeter if possible. Fit a curve | Monthly; clean the optics weekly |
| MQ-3 | 48 h burn-in. R0 in clean air at known temperature and humidity. Check the response with a drop of hand sanitiser in a sealed jar | Re-baseline weekly |
| DS18B20 | Ice water (0 °C) and room temperature against a reference thermometer | Once, then yearly |
| DHT11 | Compare against a reference hygrometer | Once |
| Pump | Time how long it takes to fill 150 mL and 250 mL on the actual tubing and lift | After any tubing change |

---

## 10. Enclosure, waterproofing and environmental protection

**Electronics box:** IP65/IP67 ABS or PC enclosure, about 250 × 200 × 120 mm.
- **Inside:**
  - the Pi and an ADC carrier board (perfboard with screw terminals);
  - the three buck converters;
  - the SIM800L, close to an SMA bulkhead with the antenna outside;
  - a fuse block.
- **Glands:** M16/PG7 cable glands, with drip loops on every cable.
- **Moisture:** a breathable vent (Gore-type) and a desiccant pack.
- **Heat:** mount it in shade.

**Outside the box:**

| Item | Placement |
|---|---|
| DHT11 | Louvered radiation shield |
| Rain plate | On top, tilted about 30° to shed water |
| LDR | Facing the sky behind a clear window, not shaded by the panel |
| Battery | Separate box, never in the electronics box |

**Water side:**
- The printed sensor housing holds the probes. Probe cables reach the box through glands.
- The turbidity sensor's top must stay above the waterline (the housing's fill grooves).
- The pump intake has a strainer.

**Corrosion:**
- stainless or nylon fasteners;
- conformal coating on the boards, never on sensing parts;
- the rain comb powered only while reading;
- the pH probe never allowed to dry.

**Field risks:** floods (a lift-out procedure), vandalism (a lockable box, low visibility), lightning (TVS diodes, short cables).

---

## 11. Maintenance plan

| How often | Task |
|---|---|
| Daily (pilot) | Check the status SMS: battery, last reading, signal strength |
| Weekly | Clean the pH, TDS and turbidity probes (soft brush, rinse). pH one-point check at 7.00. Clean the turbidity optics. Remove the sample bottle. Check the desiccant |
| Every 2 weeks | Full pH calibration; TDS check; refill the pH storage solution |
| Monthly | Turbidity check; MQ-3 re-baseline; inspect glands and seals; back up the SD card |
| Every 6–12 months | Replace the pH probe (sooner in dirty water) and the rain comb if corroded |

---

## 12. Bill of materials: what to add

**Existing hardware:** all 12 items in section 1, which the team already has.

**Essential for the bench prototype** (Robu.in, prices including GST, checked 28 Oct 2026; "est." means not checked):

| Item | Qty | Price | Link |
|---|---|---|---|
| ADS1115 16-bit 4-channel ADC module | 2 | ₹129 each | [Robu](https://robu.in/product/ads1115-16-bit-adc-4-channel-programmable-gain-amplifier/) |
| DS3231 RTC module | 1 | ₹125 | [Robu](https://robu.in/product/ds3231-rtc-module-precise-real-time-clock-i2c-at24c32/) |
| 5 V 5 A buck converter (Pi supply, Buck A) | 1 | ₹199 | [Robu](https://robu.in/product/dc-dc-step-down-buck-converter-power-supply-module-24v-12v-9v-to-5v-5a-25w-replace-lm2596s/) |
| LM2596 buck converter with display (SIM800L 4.0 V, Buck B) | 1 | ₹129 | [Robu](https://robu.in/product/lm2596-buck-step-power-converter-module-dc-4-040-1-3-37v-led-voltmeter/) |
| LM2596S buck converter (5 V sensor rail, Buck C) | 1 | ₹49 | [Robu](https://robu.in/product/lm2596s-dc-dc-buck-converter-power-supply/) |
| 4-channel level converter (optional; a resistor divider also works) | 1 | ₹39 | [Robu](https://robu.in/product/level-converter-4-channel/) |
| Resistor kit (12 k, 20 k, 1 k, 2 k, 4.7 k, 100 k, 22 k) | 1 | ₹489 | [Robu](https://robu.in/product/pro-range-new-1500pcs-75-kinds-specifications-x-20pcs-1-4w-metal-film-resistor-pack-error-1-common-component-package/) |
| 1000 µF 16 V low-ESR capacitor, 100 nF ceramic capacitors, 1N5819 diodes, 5.1 V Zener | set | about ₹150 (est.) | Any local shop |
| AO3401 P-MOSFET × 3, 2N3904 × 4, IRLZ44N × 1 (power switches) | set | about ₹120 (est.) | Any local shop |
| Perfboard, screw terminals, female headers | set | about ₹200 (est.) | Any local shop |
| 12 V 3 A adapter and DC jack (bench) | 1 | about ₹350 (est.) | Any local shop |
| 32 GB high-endurance microSD | 1 | about ₹600 (est.) | Any local shop |
| pH buffer set (4.01 / 6.86 / 9.18) | 1 | about ₹250 (est.) | Any local shop |
| **Bench total** | | **about ₹3,000** | |

**For the field pilot only** (prices from the team's 23 Oct cost research unless marked est.):
- LiFePO4 12.8 V 6 Ah battery: ₹2,200; or 20 Ah for always-on, about ₹6,000 (est.).
- 20 W solar panel: ₹1,299.
- Charge controller: about ₹600 (est.).
- IP67 enclosure: ₹1,500.
- Cable glands: ₹70 each.
- Breathable vent: about ₹150 (est.).
- Wake-up timer board: about ₹3,000 (est.).

**Scientifically justified optional additions:**

| Item | Gap it closes | Price |
|---|---|---|
| Raspberry Pi Camera Module 3 | Floating plastic and solid waste; visual evidence for events | About ₹3,280 including GST ([Evelta](https://evelta.com/raspberry-pi-camera-module-3-noir/), NoIR version listed) |
| Dissolved oxygen sensor | Sewage and organic pollution | Optical RS485 type ₹19,040 ex-GST ([Evelta](https://evelta.com/rs485-fluorescence-dissolved-oxygen-sensor-for-freshwater/)); a cheaper galvanic type needs membrane upkeep |
| 4G LTE Cat-1 module (SIMCom A7670C) | Removes the 2G risk | About ₹1,900 (R3 cost research) |
| DFRobot DFR0504 isolators | Only if switching the supplies doesn't remove the pH/TDS interference | ₹2,219 each ([Robu](https://robu.in/product/dfrobot-gravity-analog-signal-isolator/)) |

---

## 13. Implementation and test roadmap

The finale exhibition is on 19 Nov.

| Phase | Dates (2026) | Work | Done when |
|---|---|---|---|
| **0. Prepare** | 28–31 Oct | Answer section 15. Order the section 12 parts. Flash Raspberry Pi OS and apply the section 7.1 configuration. **Start the MQ-3's 48 h burn-in on the day the parts arrive** | `i2cdetect` shows 0x48, 0x49 and 0x68; the DS18B20 appears under `/sys/bus/w1` |
| **1. One sensor at a time** | 1–6 Nov | DS18B20 → DHT11 → ADS1115 + TDS → pH (calibrate) → turbidity → MQ-3 → rain and LDR → pump (fill time) → SIM800L SMS (signal strength) | Each sensor reads plausibly in tap water, salt water, vinegar and muddy water; an SMS is received |
| **2. Integrate** | 7–12 Nov | Switched pH and TDS supplies (interference test). Measurement cycle, SQLite, alert logic, sampler, MQTT dashboard. Print the sensor housing with the measured bores. 24 h unattended run on the bench | No reset during GSM bursts; the pH change with TDS on/off is under 0.05; 24 h log without gaps |
| **3. Demo hardening** | 13–17 Nov | Demo mode (15 s cycle), read-only root file system, watchdog, spare probe and bottle, demo script with salt, vinegar, muddy water and sanitiser. Three full rehearsals | Three clean runs back to back; recovers after the power is pulled |
| **4. Field pilot** | After 20 Nov | Enclosure, solar, timed waking, a 2-week supervised trial at a drain or canal with lab samples for comparison | Over 90 % of readings received; events match the lab results |
| **5. Upgrade path** | 2027 | 4G LTE, dissolved oxygen, industrial probes: converge on the R3 field design | — |

---

## 14. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| SIM800L brown-outs reset the module or the Pi | High | High | Dedicated 4.0 V rail with 2 A capacity, 1000 µF, short wires (section 5.4) |
| pH reading disturbed by the TDS board | High | High | Switched supplies and time windows; isolators if needed |
| No 2G at the site | Medium | High | Check with `AT+CSQ`; Airtel or Vi SIM; store and forward over WiFi; 4G upgrade |
| SD-card corruption after a power cut | Medium | High | Read-only root, data on a separate partition, a safe-shutdown script |
| MQ-3 false alarms from humidity or temperature | High | Medium | Sealed headspace protocol, relative threshold, DHT11 context, "indicator" wording |
| Turbidity affected by light or bubbles | Medium | Medium | Measure inside the housing, out of the sun; median filter |
| pH probe dries out or drifts | Medium | High | Wet storage, calibration schedule, spare probe |
| Pump runs dry or sucks debris | Medium | Medium | Intake strainer; run only when submerged; time limit |
| Water in the electronics box | Medium | High | IP67 box, glands, drip loops, vent, desiccant |
| Field power shortfall with the Pi always on | High | High | Timed waking (19 Wh/day) |
| Overclaiming to the jury | Medium | High | "Indicators, not identification"; "prototype"; the R3 is the field design |

---

## 15. Missing information (please confirm)

| # | Question | Default used here |
|---|---|---|
| 1 | Exact pH board and probe (photo of the board)? | PH-4502C with E-201 probe (A1) |
| 2 | Exact turbidity and TDS boards (photo, markings)? | SEN0189 and SEN0244 types (A2, A3) |
| 3 | Pump voltage and flow (label on the pump)? | 3–6 V, about 100 L/h (A4) |
| 4 | SIM800L board: red mini module or blue "V2 5V" board? Which SIM operator? | Red mini module; Airtel or Vi (A5) |
| 5 | MQ-3 module load resistor (RL) value? | Measure it before calibrating |
| 6 | Finale demo powered from mains? Field site and dates? | Mains at the finale; supervised pilot afterwards (A7) |
| 7 | Who receives alerts, and which dashboard (laptop or cloud)? | Team phones; Node-RED on a laptop |
| 8 | Lab partner for the samples? | To arrange before the pilot |

---

## 16. Next actions (this week)

1. **Team:** answer section 15. Photos of the pH, TDS, turbidity and SIM800L boards are enough.
2. **Team:** order the section 12 essentials (about ₹3,000) from Robu, which is in Pune.
3. **Team:** flash Raspberry Pi OS Lite and apply section 7.1. Start the MQ-3 burn-in as soon as it's powered.
4. **Team:** measure the probe diameters with calipers, then resize the printed sensor housing to fit.
5. **Software:** write the Python services in section 7, the wiring sheet for the carrier board, and the demo script.

---

## 17. References

1. Raspberry Pi documentation: GPIO voltage specifications ("aren't 5 V tolerant"), power table for 3 B+ (2.5 A, 1.2 A, 500 mA), GPIO
   current limits. https://www.raspberrypi.com/documentation/computers/raspberry-pi.html
2. Raspberry Pi documentation: configuration, UARTs and overlays. https://www.raspberrypi.com/documentation/computers/configuration.html
3. Texas Instruments, ADS1115 datasheet. https://www.ti.com/lit/ds/symlink/ads1115.pdf
4. SIMCom, SIM800H & SIM800L Hardware Design V2.02 (VBAT 3.4–4.4 V, 2 A bursts, serial levels, current table).
   https://www.electrokit.com/upload/product/41018/41018214/SIM800L-SIMCom.pdf
5. Winsen MQ-3 datasheet (heater 5.0 V, up to 900 mW, 25–500 ppm alcohol, preheat over 48 h).
   https://cdn.sparkfun.com/datasheets/Sensors/Biometric/MQ-3%20ver1.3%20-%20Manual.pdf
6. DFRobot, Gravity Analog TDS Sensor (SEN0244) wiki and sample code. https://wiki.dfrobot.com/Gravity__Analog_TDS_Sensor___Meter_For_Arduino_SKU__SEN0244
7. DFRobot, Turbidity sensor (SEN0189) wiki ("the top of probe is not waterproof"). https://wiki.dfrobot.com/Turbidity_sensor_SKU__SEN0189
8. DFRobot, Gravity Analog pH Sensor Kit V2 (SEN0161-V2) wiki. https://wiki.dfrobot.com/Gravity__Analog_pH_Sensor_Meter_Kit_V2_SKU_SEN0161-V2
9. PH-4502C pH sensor with Arduino (offset calibration at 2.5 V). https://raw.org/software/drivers/ph-4502c-ph-sensor-with-arduino/
10. Analog Devices, DS18B20 datasheet. https://www.analog.com/media/en/technical-documentation/data-sheets/DS18B20.pdf
11. DHT11 technical data sheet (translated). https://www.mouser.com/datasheet/2/758/DHT11-Technical-Data-Sheet-Translated-Version-1143054.pdf
12. Raspberry Pi overlays as quoted in: Waveshare, 1-Wire DS18B20 tutorial, https://www.waveshare.com/wiki/Raspberry_Pi_Tutorial_Series:_1-Wire_DS18B20_Sensor ;
    and I-Programmer, DHT overlay, https://www.i-programmer.info/programming/hardware/14353-pi-iot-in-c-using-linux-drivers-the-dht22.html?start=1
13. STMicroelectronics, L298 datasheet. https://www.st.com/resource/en/datasheet/l298.pdf
14. Components101, MX1508 DC motor driver ("mini L298N"). https://components101.com/modules/mx1508-dc-motor-driver-pinout-features-datasheet
15. Components101, Rain drop sensor module (LM393). https://components101.com/sensors/rain-drop-sensor-module
16. Mini submersible pump 3–6 V specification (vendor listing). https://techiesms.com/product/submersible-mini-dc-water-pump/
17. DFRobot, Gravity Analog Signal Isolator (pH affected by EC; isolate the power supply). https://www.dfrobot.com/product-1621.html
18. Central Pollution Control Board, water quality criteria. https://cpcb.nic.in/water-quality-criteria/
19. Light Reading: Vodafone Idea retiring 3G while keeping 2G, https://www.lightreading.com/services/indias-vodafone-idea-to-shut-down-3g-network/d/d-id/767407 ;
    Jio and 2G in India, https://www.lightreading.com/business-management/jio-s-dream-of-a-2g-free-india-is-a-nightmare-for-telcos
20. Robu.in and Evelta.com product pages (prices in section 12), checked 28 Oct 2026.
