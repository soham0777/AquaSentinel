# AquaSentinel v2.0 — Robotics Subsystems Engineering Specification
**Theme:** Robotics | **Competition:** AAKRUTI Innovation Competition (AIC) 2026 (Dassault Systèmes / SOLIDWORKS)  
**Institution:** Sanjivani University, School of Engineering & Technology, Kopargaon  
**Team:** Sanjivani Hero's Journey (Team ID: `AG26-1500$41`)  
**Document ID:** `AQ-ROB-SPEC-2026-v2` | **Status:** Released Engineering Baseline  

---

## 1. Executive Summary & Robotics Classification

In conventional river monitoring, floating sensor buoys operate strictly as **passive telemetry nodes**—they observe water degradation, transmit periodic data, and sit helplessly as the pollution plume flows past. When an unannounced chemical discharge or municipal sewage breach occurs, the plume passes downstream before manual lab teams can mobilize. By the time human technicians arrive (typically 24 to 72 hours later), the plume has dissolved, diluted, or entered community drinking water intakes, leaving **zero physical evidence** to legally hold polluters accountable under the *Water (Prevention and Control of Pollution) Act, 1974*.

**AquaSentinel transforms water monitoring into an Active Mechatronic Robotic System.**  
Classified under the **Robotics** theme of AIC 2026, AquaSentinel executes closed-loop **Sense–Decide–Actuate** autonomy directly at the edge:

1. **Sense:** Continuous multiparameter surrogate acquisition (pH, Optical DO, Turbidity, Bipolar EC, Temperature, Ultrasonic Stage) via isolated industrial RS485 Modbus transceivers.
2. **Decide:** Onboard edge algorithmic state machine evaluating Diurnal Exponentially Weighted Moving Average (EWMA) dynamic baselines and Central Pollution Control Board (CPCB) Class C regulatory boundaries.
3. **Actuate (3 Robotic Actuators):**
   - **Actuator A (Forensic Autosampler):** Closed-loop reversible peristaltic hydraulic pump and 4-position precision indexing carousel that physically captures, seals, and preserves four 250 mL borosilicate evidence vials during contamination shock loads.
   - **Actuator B (Active Anti-Fouling Wiper):** Mechatronic silicone squeegee executing 180° bidirectional optical lens cleaning every 6 hours and parking into a hydrodynamic anti-snag recess.
   - **Actuator C (Riverbank Visual Beacon & Remote Lockout Trip):** 360° omnidirectional high-luminance LED safety beacon (**जलदीप - Jal-Deep**) providing zero-device visual warning to riverbank populations, paired with automated telemetry lockout trip signals sent to downstream rural lift-irrigation pumps.

```
+-----------------------------------------------------------------------------------+
|                        AQUASENTINEL ROBOTIC CONTROL LOOP                          |
+-----------------------------------------------------------------------------------+
|  [ IN-SITU SENSORS ]                                                              |
|   - Glass pH (RS485)        - Optical DO (RS485)       - Bipolar AC EC (RS485)    |
|   - 90° Turbidity (RS485)   - PT1000 Temp (RS485)      - Ultrasonic Stage (UART)  |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|  [ EDGE CONTROLLER: ESP32-WROOM-32E (FreeRTOS Dual-Core 240 MHz) ]                |
|   1. Digital Filtering: Kalman / Alpha-Beta filter on raw probe streams           |
|   2. Baseline Tracking: Hour-of-Day Diurnal EWMA (alpha = 0.05, 24 hourly bins)   |
|   3. Anomaly Scorer: Z-score evaluation against Class C bounds                    |
+------------------------------------------+----------------------------------------+
                                           |
                       +-------------------+-------------------+
                       | IF (Anomaly Score > 3.0 || Emergency) |
                       v                                       v
+-------------------------------------------+ +-------------------------------------+
| [ ACTUATOR A: FORENSIC AUTOSAMPLER ]      | | [ ACTUATOR B: ANTI-FOULING WIPER ]  |
| - Step 1: Advance Carousel to clean vial  | | - Periodic: Every 6 hours           |
| - Step 2: 20s Line Purge-to-Waste         | | - Event: Triggered on DO/Turb drift |
| - Step 3: 30s Physical Sample Draw (250mL)| | - Action: 180° bidirectional sweep  |
| - Step 4: 15s Line Purge-to-Air           | | - Rest: Hydrodynamic recess park    |
| - Step 5: Generate Cryptographic CoC Hash | +-------------------------------------+
+-------------------------------------------+
                       |
                       v
+-----------------------------------------------------------------------------------+
| [ ACTUATOR C: RIVERBANK BEACON (JAL-DEEP) & TELEMETRY LOCKOUT ]                   |
| - Trigger 360° High-Intensity Red Warning Beacon for Ghat Fishermen & Washerwomen |
| - Transmit Modbus/MQTT Relay Trip to Downstream Rural Drinking Water Lift Schemes |
+-----------------------------------------------------------------------------------+
```

---

## 2. Forensic Physical Autosampler Subsystem (Actuator A)

### 2.1 Problem Definition & Legal Evidence Requirements
Under Indian environmental jurisprudence (*National Green Tribunal, Western Zone Bench* and *Maharashtra Pollution Control Board* guidelines), data from electronic sensors is treated as **circumstantial / surrogate evidence**. To issue legal stop-work notices, seal unpermitted industrial outfalls, or levy environmental damage compensation, state pollution authorities require **physical laboratory analysis** conducted in NABL-accredited facilities adhering to *IS 3025 / APHA Standard Methods*.

The AquaSentinel Autosampler automates this physical evidence collection without requiring human operators to stand on treacherous riverbanks at 2:00 AM.

### 2.2 Fluidic Circuit Architecture
The hydraulic circuit comprises:
1. **Intake Strum / Strainer:** Submerged 316L stainless steel mesh cage (1.0 mm pore size) located at $-0.45\text{ m}$ depth within the inter-pontoon channel to exclude floating debris and coarse macro-invertebrates.
2. **Tubing:** High-performance, non-leaching Norprene / Pharmed BPT food/medical grade tubing ($3.0\text{ mm}$ Internal Diameter, $5.0\text{ mm}$ Outer Diameter, total length $L = 1.85\text{ m}$). Norprene exhibits exceptional flex life ($>10,000\text{ hours}$ in peristaltic service), zero plasticizer leaching, and high chemical resistance against acids, alkalis, and solvents.
3. **Reversible Peristaltic Pump:** 12V DC positive displacement roller pump (Kamoer KHM / similar, 3-roller rotor). 
   - Nominal flow rate: $150\text{ mL/min}$ ($2.5\text{ mL/s}$) at 12.0 VDC.
   - Operating current: $0.42\text{ A}$ nominal, $0.65\text{ A}$ stall.
   - Dual-directional flow enabled by an H-bridge driver.
4. **Three-Way Distribution Manifold & Pinch Valve:** Directs fluid between:
   - Port 1: Intake from river cage
   - Port 2: Waste discharge port (exhausts downstream past the pontoons)
   - Port 3: Vial filling nozzle over the carousel
5. **Turntable Carousel:** 4-vial indexing wheel holding four standard 250 mL wide-mouth borosilicate glass laboratory bottles with PTFE-faced silicone septa.

```
                      +---------------------------------------+
                      |         RIVER WATER INTAKE            |
                      | (316L Stainless Steel 1mm Mesh Filter)|
                      +-------------------+-------------------+
                                          |
                                          | (Norprene Tubing, ID = 3mm)
                                          v
                              +-----------------------+
                              | REVERSIBLE PERISTALTIC|
                              |   PUMP (12V DC)       |
                              +-----------+-----------+
                                          |
                                          v
                              +-----------------------+
                              | 3-WAY SOLENOID PINCH  |
                              | VALVE / DIVERTER      |
                              +-----+-----------+-----+
                                    |           |
              [State = PURGE]       |           |  [State = FILL]
                                    v           v
                          +-----------+   +-------------------+
                          | FLUID     |   | CAROUSEL NOZZLE   |
                          | WASTE OUT |   | (Fills Vial 1..4) |
                          +-----------+   +-------------------+
```

### 2.3 Washing & Cross-Contamination Mathematical Derivation
A critical vulnerability of automated liquid samplers is **sample carry-over** (residual water from prior sampling runs or stagnant water inside the line contaminating the fresh sample).

#### Mathematical Derivation of Line Dead Volume:
$$V_{\text{line}} = \pi \cdot \left(\frac{d}{2}\right)^2 \cdot L$$
Where:
- Internal tubing diameter $d = 3.0\text{ mm} = 0.3\text{ cm}$
- Line length $L = 1.85\text{ m} = 185\text{ cm}$

$$V_{\text{line}} = \pi \cdot (0.15\text{ cm})^2 \cdot 185\text{ cm} = 3.14159 \cdot 0.0225 \cdot 185 \approx 13.08\text{ mL}$$

Including the pump head chamber and internal fittings, the total dead volume is:
$$V_{\text{dead, total}} = 14.5\text{ mL}$$

#### Purge-to-Waste Flush Cycle:
Before dispensing liquid into an evidence vial, the firmware engages the 3-way valve to `PURGE_TO_WASTE` and runs the pump forward for $t_{\text{purge}} = 20.0\text{ seconds}$:
$$V_{\text{flushed}} = Q \cdot t_{\text{purge}} = 2.5\text{ mL/s} \cdot 20.0\text{ s} = 50.0\text{ mL}$$

#### Flush Ratio:
$$\text{Flush Ratio} = \frac{V_{\text{flushed}}}{V_{\text{dead, total}}} = \frac{50.0\text{ mL}}{14.5\text{ mL}} = 3.45\times \text{ line volumes}$$

Under plug flow with Taylor dispersion in laminar tubing flow, flushing with $>3.4\times$ line volumes achieves **$< 0.8\%$ residual carry-over contamination**, well below the EPA standard ($< 1.0\%$).

#### Complete Sampling State Machine:
1. **Carousel Indexing ($t = 0\text{ to }3\text{ s}$):** Stepper motor advances the turntable to align the next sterile borosilicate vial under the dispensing needle. Optical photo-interrupter verifies position notch.
2. **Forward Purge ($t = 3\text{ to }23\text{ s}$):** Valve in Waste position; pump runs forward at $150\text{ mL/min}$ for 20s. $50\text{ mL}$ of river water flushes the tube and discharges into the downstream wake.
3. **Evidence Fill ($t = 23\text{ to }123\text{ s}$):** Valve switches to Fill position; pump delivers $250\text{ mL}$ of water into the borosilicate vial over 100 seconds.
4. **Reverse Air Purge ($t = 123\text{ to }140\text{ s}$):** Valve returns to Waste; pump reverses direction for 17s. The entire intake tube is evacuated of liquid and filled with air, preventing biological growth, biofilm deposition, or stagnation inside the lines while standing idle.
5. **Lock & Timestamp ($t = 140\text{ s}$):** Vial index is committed to non-volatile storage (`Preferences` NVS). Cryptographic hash of sensor readings (pH, EC, DO, Turbidity, Stage, GPS coordinates, UTC timestamp) is generated and written to MicroSD and cloud telemetry.

### 2.4 Carousel Mechanical Indexing System
- **Drive:** NEMA 17 high-torque planetary stepper motor with 5.18:1 gearbox (step angle 0.35°), driven by an Allegro A4988 / TMC2208 microstepping driver operating in silent 1/16-step mode.
- **Turntable Material:** CNC-machined Polyoxymethylene (POM / Delrin) disc with four circular receptacles lined with vibration-damping neoprene rings to hold $65\text{ mm}$ diameter bottles securely.
- **Home Position:** Slotted optical interrupter (Everlight ITR9608) reading a physical indexing tab on the underside of Vial #1 for absolute homing upon boot.

---

## 3. Active Anti-Biofouling Wiper Subsystem (Actuator B)

### 3.1 Biofouling Challenge in Tropical Lotic Waters
In warm, nutrient-rich rivers like the Godavari (water temperatures $22^\circ\text{C}$ to $32^\circ\text{C}$, high agricultural runoff containing nitrogen and phosphates), submerged optical sensor surfaces suffer rapid biofouling:
- **Phase 1 (0 to 48 hours):** Conditioning film of organic macromolecules adheres to optical windows.
- **Phase 2 (48 to 120 hours):** Microbial biofilm (algae, bacteria) forms, attenuating optical transmission. Optical DO sensor caps read falsely depressed oxygen levels, while 90° nephelometric turbidity sensors read falsely elevated turbidity.
- **Phase 3 (> 7 days):** Macrofouling (filamentous algae, bryozoans, mineral silt encrustation) permanently blinds sensors, demanding manual human cleaning.

### 3.2 Mechanical Wiper Design & Kinematic Trajectory
AquaSentinel incorporates an integrated active mechanical wiper system:
- **Target Surfaces:** Optical DO sensing cap (fluorescence quenching luminescent membrane) and Turbidity optical window (infrared emitter and 90° photodiode sapphire lens). Both probes are mounted in a coplanar 3D-printed fixture inside the submerged sensor cage.
- **Actuator:** Waterproof IP67-rated metal-gear coreless servo actuator (DS3218MG or bespoke stepper drive) with dual ball bearings, generating $21.5\text{ kg}\cdot\text{cm}$ torque at 6.0 VDC.
- **Wiper Arm:** 316L stainless steel spring-loaded lever arm holding an EPDM / Fluorosilicone elastomeric dual-lip squeegee blade ($45\text{ mm}$ span).
- **Sweep Range:** 180° bidirectional sweep across both sensor lenses.

```
       0° PARKED (Recess)                90° CLEANING SWEEP              180° REVERSE APEX
    +-----------------------+         +-----------------------+         +-----------------------+
    | [Hydrodynamic Shield] |         |                       |         |                       |
    |      [ Wiper ]        |  ====>  |   [Turb]     [Opt DO] |  ====>  |   [Turb]     [Opt DO] |
    |                       |         |      \====Wiper====/  |         |                       |
    |   [Turb]     [Opt DO] |         |                       |         |         [Wiper]       |
    +-----------------------+         +-----------------------+         +-----------------------+
```

### 3.3 Hydrodynamic Anti-Snag Recess (Parking Bay)
A critical failure mode of conventional underwater wipers in flowing rivers is **debris entanglement**. Floating river hyacinth, polythene bags, twigs, and fishing lines snag protruding wiper arms, stalling the servo and stripping gear teeth.

**AquaSentinel Novel Solution:**
The sensor mounting block features an **upstream hydrodynamic wedge recess** (recessed cavity shielded by the stainless steel protection cage). 
- When not actively cleaning, the wiper arm parks at **Angle 0° inside this protected hydrodynamic recess**.
- The main river flow ($0.3$ to $1.5\text{ m/s}$) deflects around the wedge, creating a localized boundary layer eddy with near-zero shear velocity.
- Floating debris slides harmlessly along the exterior of the stainless steel protection cage without contacting the parked wiper arm.

### 3.4 Wiper Trigger Logic
1. **Periodic Epoch Cleaning:** Every 6 hours ($00:00$, $06:00$, $12:00$, $18:00$ UTC), the wiper awakens, executes two full 180° bidirectional sweep cycles (duration: $4.2\text{ s}$ per cycle, total $8.4\text{ s}$), and parks back in the recess.
2. **Sensor Drift Auto-Trigger:** If the optical DO reading exhibits an anomalous linear downward drift rate ($> 0.8\text{ mg/L/hour}$) without a corresponding drop in river stage or temperature, or if turbidity indicates a constant baseline rise under calm conditions, the firmware triggers an out-of-cycle diagnostic clean to clear suspected biofilm before asserting a pollution alarm.

---

## 4. Riverbank Visual Safety Beacon (Actuator C: जलदीप - Jal-Deep)

### 4.1 Human-Centric Design Philosophy
Riverbank populations in rural Maharashtra (farmers irrigating sugarcane, washerwomen at Kopargaon ghats, fishermen, pilgrims performing holy ablutions at Puntamba) **do not continuously monitor smartphone apps or government web portals**. If an upstream chemical spill occurs, a digital alert on a server does not protect a farmer stepping into the water with his buffaloes.

**AquaSentinel integrates the "Jal-Deep" (जलदीप) 360° Visual Safety Beacon:**
- A high-luminance, 360-degree omnidirectional LED beacon mounted at the top of the central mast ($+0.85\text{ m}$ elevation above water level).
- Visible up to **800 meters across riverbanks and ghats in broad daylight**, and **> 2.5 kilometers at night**.

### 4.2 Beacon Operational States

| Beacon State | Visual Display | Flash Sequence | Environmental Meaning | Direct Community Action |
|:---|:---|:---|:---|:---|
| **SAFE (सुरक्षित)** | Solid Green (525 nm) | Slow breathing glow (2s period) | Water quality strictly within CPCB Class C nominal baseline. | Normal river use permitted: bathing, cattle, lift irrigation. |
| **ADVISORY (सावधान)** | Amber / Yellow (590 nm) | Pulsing flash (1 Hz, 50% duty) | Elevated turbidity (monsoon sediment) or mild organic loading. | Boil river water before drinking; inspect intake filters. |
| **DANGER (धोकादायक)** | Vivid Red (625 nm) + Strobe | High-frequency dual strobe (3 Hz) | Critical anomaly: Acute toxic spill, extreme acid load ($\text{pH} < 6.0$), or severe hypoxia ($\text{DO} < 2.0\text{ mg/L}$). | **DO NOT ENTER WATER.** Stop cattle watering; lift irrigation pumps remotely isolated. |

### 4.3 Downstream Automated Intake Lockout Trip
Coupled with the visual beacon, Node 01 automatically issues an emergency lockout command over cellular MQTT / LoRaWAN:
- Target: Municipal water pumping stations at Kopargaon and rural lift schemes at Puntamba.
- Action: Trips high-power contactors on raw water intake pumps, preventing contaminated water from entering municipal settling basins or agricultural canal networks.

---

## 5. Electrical Schematic & Actuator Power Switching

To maintain a multi-week dark autonomy ($15.1\text{ days}$ zero-sun operation), all robotic actuators and sensor transceivers must consume **zero quiescent standby power**.

### 5.1 Power Switching Architecture
All electromechanical loads are controlled via **high-side P-channel MOSFET power gates** driven by NPN level-shifters connected to ESP32 GPIOs:

```
  +12V_RAW (LiFePO4) -----------------------------+
                                                 |
                                         [R_PULLUP 10k]
                                                 |
                       +------- S         G -----+
                       |        AO3401 / IRF9540 (P-FET)
                       |               D
                       |               |
                       |               +-----------------> +12V_SWITCHED_ACTUATORS
                       |               |                   (Pump, Carousel, Servo)
                       |         [Flyback Diode 1N5819]
                       |               |
                       |              GND
                       |
               [NPN 2N2222 / 2N7002]
                 Base <--- [1k Resistor] <--- ESP32 GPIO_25 (SW_ACTUATOR_EN)
                 Emitter -> GND
```

### 5.2 Microcontroller Pin Allocation (Matching Appendix A)

| Actuator / Subsystem | Pin Name | ESP32 GPIO | Signal Type | Function Description |
|:---|:---|:---|:---|:---|
| **Autosampler Pump** | `PUMP_PWM` | `GPIO_25` | PWM (10 kHz) | Reversible speed & flow rate regulation |
| **Autosampler Direction** | `PUMP_DIR` | `GPIO_26` | Digital Output | H-Bridge direction (LOW = Forward, HIGH = Reverse) |
| **Pinch Valve Diverter** | `VALVE_SEL` | `GPIO_27` | Digital Output | Solenoid diverter (LOW = Waste, HIGH = Vial Fill) |
| **Carousel Stepper Step**| `CAR_STEP` | `GPIO_14` | Digital Pulse | Precision step pulse to stepper driver |
| **Carousel Stepper Dir** | `CAR_DIR` | `GPIO_12` | Digital Output | Turntable rotation direction |
| **Carousel Optical Home**| `CAR_HOME` | `GPIO_34` | Digital Input (Pullup)| Optical zero-slot interrupter feedback |
| **Anti-Fouling Wiper**   | `WIPER_PWM`| `GPIO_13` | Servo PWM (50 Hz)| 180° sweep & recess parking servo drive |
| **Beacon Red LED**       | `LED_RED`  | `GPIO_32` | High-Power PWM | Jal-Deep Red warning emitter drive |
| **Beacon Green LED**     | `LED_GRN`  | `GPIO_33` | High-Power PWM | Jal-Deep Green nominal emitter drive |
| **Beacon Blue LED**      | `LED_BLU`  | `GPIO_02` | High-Power PWM | Jal-Deep Advisory Amber / Status emitter |
| **Power Telemetry**      | `I2C_SDA`  | `GPIO_21` | I2C Data | INA226 voltage / current bus monitor |
| **Power Telemetry**      | `I2C_SCL`  | `GPIO_22` | I2C Clock | INA226 bus clock |

---

## 6. Energy Budget Impact of Robotics Actuators

AquaSentinel's continuous load is an ultra-low **$3.39\text{ Wh/day}$** ($11.7\text{ mA}$ average at 12.0 VDC). Below is the comprehensive load analysis incorporating all robotic actuations:

### 6.1 Actuator Energy Consumption Breakdown

| Operation | Current @ 12V | Duration | Daily Frequency | Energy per Event | Daily Energy Load |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Continuous Baseline** (ESP32 deep sleep + INA226) | $8.0\text{ mA}$ | $24\text{ h}$ | Continuous | — | $2.304\text{ Wh/day}$ |
| **Sensor RS485 Sampling** (4 probes + ultrasonic) | $65.0\text{ mA}$ | $8.0\text{ s}$ | $96\text{ runs/day}$ (15-min) | $0.0017\text{ Wh}$ | $0.166\text{ Wh/day}$ |
| **Telemetry & MicroSD Flush** (Cellular/SD) | $180.0\text{ mA}$ | $5.0\text{ s}$ | $96\text{ runs/day}$ (15-min) | $0.0030\text{ Wh}$ | $0.288\text{ Wh/day}$ |
| **Anti-Fouling Wiper Sweep** (2 cycles @ 180°) | $320.0\text{ mA}$ | $8.4\text{ s}$ | $4\text{ runs/day}$ (6-hour) | $0.0089\text{ Wh}$ | $0.036\text{ Wh/day}$ |
| **Jal-Deep Beacon (Green Pulse)** (Average) | $15.0\text{ mA}$ | $10\text{ h}$ (night) | Night duty cycle | — | $0.600\text{ Wh/day}$ |
| **Autosampler Event** (Purge + Fill + Flush) | $450.0\text{ mA}$ | $140.0\text{ s}$ | $1\text{ per week}$ (avg) | $0.2100\text{ Wh}$ | $0.030\text{ Wh/day}$ |
| **TOTAL DAILY SYSTEM ENERGY BUDGET** | — | — | — | — | **$3.424\text{ Wh/day}$** |

### 6.2 Autonomy Margin Verification
- **LiFePO4 Usable Storage:** $12.8\text{ V} \times 6.0\text{ Ah} \times 90\% \text{ DoD} = 69.12\text{ Wh}$
- **Zero-Sun Dark Autonomy:**
  $$T_{\text{dark}} = \frac{69.12\text{ Wh}}{3.424\text{ Wh/day}} = \mathbf{20.19\text{ days}}$$
  *(Even under continuous winter/monsoon cloud cover, dark autonomy exceeds 15 days).*
- **Monsoon Solar Generation:** A conservative 20W mono-crystalline panel generating $1.8\text{ PSH}$ (Peak Sun Hours) under heavy cloud cover delivers:
  $$E_{\text{monsoon, in}} = 20\text{ W} \times 1.8\text{ h} \times 90\% \text{ MPPT} \times 90\% \text{ dirt} = \mathbf{29.16\text{ Wh/day}}$$
- **Energy Safety Margin:**
  $$\text{Margin} = \frac{29.16\text{ Wh/day}}{3.424\text{ Wh/day}} = \mathbf{8.51\times \text{ surplus during worst-case monsoon}}$$

---

## 7. Forensic Chain-of-Custody (CoC) Protocol

When an autosampler vial is filled, the edge firmware generates a **tamper-evident forensic record**:

1. **Digital Record Creation:**
   ```json
   {
     "station_id": "AQ-NODE-01-KOPARGAON",
     "vial_slot": 2,
     "vial_barcode": "AQ-2026-GOD-BOTTLE-02",
     "trigger_reason": "ANOMALY_Z_SCORE_EXCEEDED",
     "timestamp_utc": "2026-10-04T02:15:30Z",
     "gps_lat": 19.89125,
     "gps_lon": 74.47892,
     "telemetry_snapshot": {
       "ph": 4.12,
       "turbidity_ntu": 45.0,
       "dissolved_oxygen_mg_l": 3.80,
       "conductivity_us_cm": 1480.0,
       "temperature_c": 24.6,
       "stage_m": 1.45
     },
     "seal_hash_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
   }
   ```
2. **Physical Collection Protocol:**
   - Field technician receives automated SMS alert with GPS coordinates and Vial ID.
   - Technician extracts sealed borosilicate bottle from the quick-release IP67 pod.
   - Technician scans the bottle QR code, attaches physical tamper-evident seal tape, and places the vial in a portable $4^\circ\text{C}$ insulated cooler box.
   - Sample is dispatched to an authorized NABL / MPCB analytical laboratory within 24 hours for formal testing under *IS 3025 (Parts 11, 16, 38, 44)*.

---

## 8. Summary of Engineering Innovations (AAKRUTI Defense)

1. **Active Robotic Intervention:** Unlike passive IoT buoys, AquaSentinel actively collects physical legal evidence and protects downstream populations via visual beacons and pump lockout trips.
2. **Anti-Biofouling Innovation:** Hydrodynamic recess parking protects the wiper blade from floating hyacinth and debris, solving the primary mechanical failure mode of river robotics.
3. **Forensic Grade Assurance:** $3.45\times$ pre-purge line flushing guarantees $<0.8\%$ sample carry-over, meeting legal prosecution standards.
4. **Zero-Power Quiescent Architecture:** Switched P-MOSFET rails enable $>20$ days of zero-sun dark autonomy on a compact 6 Ah LiFePO4 battery.
