# Hardware Validation: 72-Hour Bench Energy Logging Procedure
**Device:** AquaSentinel v2.0 Smart Edge Node  
**Subsystem:** Power Architecture & Energy Autonomy  
**Target Metric:** Total Daily Consumption $\le 4.07\text{ Wh/day}$ (matching `verified_design_calcs.json`)

---

## 1. Test Objectives & Scope
1. Empirically verify the current consumption profile across all microcontroller operational states:
   - Deep sleep current with RTC timer running (Target: $< 15\ \mu\text{A}$ at MCU rail).
   - High-side P-MOSFET leakage floor when sensor rail is switched off (Target: $< 5\ \mu\text{A}$).
   - Submerged RS485 sensor array active warmup current (Target: $108\text{ mA}$ at $12.0\text{ V}$).
   - ESP32 active computation and DSP filtering current (Target: $120\text{ mA}$ at $3.3\text{ V}$).
   - Cellular SIMCom A7670C LTE Cat-1 connection and MQTT transmission bursts (Target: $< 2.0\text{ W}$ average burst).
2. Measure total energy consumption over 72 continuous hours (288 continuous 15-minute cycles) without solar input to empirically confirm the **15.1-day dark autonomy baseline**.

---

## 2. Equipment Setup & Test Architecture

```
  [ Rigol DP832 / Agilent E3631A DC Power Supply ] (Set to 12.80 V Constant Voltage)
                           │
                           ▼
  [ INA226 Precision High-Side Current & Power Monitor IC ]
  (10 mΩ 0.1% Shunt Resistor, 16-bit ADC, I2C Interface, 1.1 ms conversion time)
                           │
                           ├───────────────────────────────────┐
                           │ (High-Side Current Sensing)        │ (I2C Bus to PC Logger)
                           ▼                                   ▼
  [ AquaSentinel Mainboard Battery Input (J1) ]       [ Raspberry Pi / Dedicated PC ]
                           │                          (Running continuous Python logger)
    ┌──────────────────────┴──────────────────────┐
    │                                             │
    ▼                                             ▼
  [ Always-On 3.3V Buck (TPS563200) ]     [ Switched Power Rails (AO3401A P-MOSFETs) ]
    - ESP32-WROOM-32E                       - 12V Sensor Rail (4x RS485 Probes)
    - DS3231SN Real-Time Clock              - 4V LTE Modem Rail (SIMCom A7670C)
    - MicroSD Card Interface                - 5V Peripheral Rail (PCA9685 & Servos)
                                            - 12V Peristaltic Autosampler Pump
```

---

## 3. Step-by-Step Test Procedure

### Phase 1: Zero-State Quiescent Calibration (T = 0 to 1 Hour)
1. Disconnect all external sensor probes and actuators.
2. Flash diagnostic firmware `firmware/edge_node/test/test_sleep_current.cpp` onto the ESP32.
3. Power the mainboard from the calibrated 12.80 V source.
4. Record quiescent current with all P-MOSFET gates disabled.
   - **Pass Criterion:** Measured current must be $\le 0.60\text{ mA}$ at $12.8\text{ V}$ ($7.68\text{ mW}$ standby floor).

### Phase 2: Active Duty-Cycle Profile Capture (T = 1 to 2 Hours)
1. Connect all 4 RS485 Modbus probes (pH, EC, DO, Turbidity), cellular antenna, and MicroSD card.
2. Flash production master firmware `firmware/edge_node/src/main.cpp`.
3. Set INA226 logging interval to $50\text{ ms}$ sampling.
4. Record continuous trace across one complete 15-minute operational cycle:
   - **T = 0s to 30s:** 12V Sensor Rail enabled; probe stabilization warmup.
   - **T = 30s to 45s:** RS485 Modbus query frames dispatched; 3-sample median filter computed.
   - **T = 45s to 50s:** Multivariate EWMA anomaly engine executed; FAT32 record committed to MicroSD.
   - **T = 50s:** 12V Sensor Rail shut off via P-MOSFET gate.
   - **T = 50s to 900s:** ESP32 enters deep sleep; RTC timer counts down.
   - **Pass Criteria:** 
     - Active sensor window energy $\le 0.0163\text{ Wh}$ per cycle.
     - Deep sleep average power $\le 8.5\text{ mW}$ at battery terminals.

### Phase 3: 72-Hour Continuous Autonomy Endurance Run (T = 2 to 74 Hours)
1. Maintain mainboard in an environmental chamber at $30^\circ\text{C} \pm 2^\circ\text{C}$.
2. Run unattended for 72 hours (288 full cycles with hourly LTE batch uploads).
3. Compute cumulative watt-hours from the INA226 timestamped energy integration:
   $$E_{\text{total}} = \sum_{k=1}^{N} V_k \cdot I_k \cdot \Delta t$$
4. **Acceptance Benchmark:**
   - 72-hour cumulative energy must not exceed $12.21\text{ Wh}$ ($4.07\text{ Wh/day} \times 3\text{ days}$).
   - Zero unexpected brownouts, hardware watchdog resets, or unhandled exceptions.

---

## 4. Test Data Sheet (Template)

```
Test Date: ____________________    Operator: ____________________
Station ID: AquaSentinel-SN01      Firmware Version: v2.0.0-PROD
Supply Voltage: 12.80 VDC          Shunt Resistor: 0.010 Ω (0.1%)

┌───────────────────────────────────────┬────────────┬─────────────┬────────┐
│ Parameter                             │ Target     │ Measured    │ Status │
├───────────────────────────────────────┼────────────┼─────────────┼────────┤
│ Quiescent Standby Current (Sleep)     │ ≤ 0.60 mA  │ _____ mA    │ [ ]    │
│ Sensor Rail Warmup Current (12V)      │ ≤ 110 mA   │ _____ mA    │ [ ]    │
│ MCU Active Current (3.3V rail)        │ ≤ 125 mA   │ _____ mA    │ [ ]    │
│ LTE Upload Peak Current (4.0V rail)   │ ≤ 1800 mA  │ _____ mA    │ [ ]    │
│ Average Daily Energy (24-Hour)        │ ≤ 4.07 Wh  │ _____ Wh    │ [ ]    │
│ 72-Hour Cumulative Energy             │ ≤ 12.21 Wh │ _____ Wh    │ [ ]    │
└───────────────────────────────────────┴────────────┴─────────────┴────────┘
Test Result: [ ] PASS   [ ] FAIL   Sign-off: ____________________
```
