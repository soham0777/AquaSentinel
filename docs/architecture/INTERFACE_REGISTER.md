# Interface register

Every interface between AquaSentinel subsystems, with its specification, the file that defines it, its status and open issues.
Status values: **Defined** (specified in CAD/code), **Partial**, **Conflicting** (two sources disagree), **Undefined**.

## Mechanical

| ID | Interface | Specification | Source | Status | Open issues |
|---|---|---|---|---|---|
| M1 | Pier ↔ bracket | 220×180×12 316L plate, 4× M12×130 A4 chemical anchors at 160×120 mm; design reaction 430 N horizontal + 161 N pole weight | DWG-06, [parts.py:672-707](../../mechanical/src/parts.py#L672-L707), bracket FEA | Partial | Anchor embedment/edge distance, concrete grade, pier owner approval, impact and uplift loads |
| M2 | Bracket ↔ pole | Split clamp OD 120 × 80 high, bore 60.7 (pole 60.3), 2× M10 A4 at 35 N·m | DWG-06 note 5 | Conflicting | ASTM A999 OD tolerance for NPS 2 is about ±0.8 mm (59.5–61.1 mm, ovality included): a pipe above 60.7 mm will not fit the reamed bore; measure before reaming; slip capacity not calculated |
| M3 | Pole ↔ stops | Split stop collar OD 100 × 30 with M8 clamp screw + EPDM buffer 20 mm; 20 mm gap to the float at both design extremes | [parts.py:652-661](../../mechanical/src/parts.py#L652-L661), [:719-728](../../mechanical/src/parts.py#L719-L728) | Partial | Uplift on the upper stop when water exceeds the top level; friction capacity of one M8 screw |
| M4 | Pole ↔ carriage | 8 concave UHMW-PE rollers, r = 52 mm, throat = pole r + 1.5 mm, two tiers 350 mm apart; μ 0.05 assumed (0.25 seized) | [parts.py:283-305](../../mechanical/src/parts.py#L283-L305), DWG-03 | Defined | Plain M10 axles in silty water; pole straightness; roller loads up to 1,107 N per tier |
| M5 | Carriage gate ↔ fixed half | D10 316 hinge pin + 2 T-handle latch pins, gate swings 100° | [parts.py:307-317](../../mechanical/src/parts.py#L307-L317) | Partial | Gate carries the upstream rollers (full drag load); pins, lugs and welds not analysed |
| M6 | Carriage ↔ float | 2× M10×70 into crossbeam 1 + pair of 316L brace struts to crossbeam 2 | [parts.py:318-332](../../mechanical/src/parts.py#L318-L332) | Partial | 6061 weldment HAZ strength, galvanic isolation detail |
| M7 | Hull ↔ crossbeams | 4 SHS 40×40×3 6061 on moulded-in M8 inserts (8 per hull), 16× M8×60 A4 | [parts.py:192-216](../../mechanical/src/parts.py#L192-L216), DWG-05 | Conflicting | Single mould vs one-sided handle inserts (DWG-05); insert pull-out "to be verified by the moulder" |
| M8 | Deck ↔ sensor well | 316L hatch flange ring OD 190 × 6, 6× M6 into the deck; PE100 D160 SDR26 sleeve | [parts.py:335-348](../../mechanical/src/parts.py#L335-L348) | Defined | Sleeve-to-flange joint not detailed |
| M9 | Well ↔ cartridge | Cartridge cap D186 seats on the flange with quarter-turn knobs; lift 700 mm | [parts.py:371-387](../../mechanical/src/parts.py#L371-L387), DWG-04 | Partial | Locking detail, sealing, torque to lift 3.95 kg over the water |
| M10 | Cartridge ↔ probes | Two POM spider holders, PCD 90, colour bands pH/EC/DO/turbidity | [parts.py:390-419](../../mechanical/src/parts.py#L390-L419) | Partial | Probe envelope D32×300 is a placeholder; tips must be coplanar for the wiper |
| M11 | Pod ↔ deck | 6061 rails 25×25×3; IP67 PC enclosure 300×260×150 | [parts.py:445-492](../../mechanical/src/parts.py#L445-L492) | Partial | IP67 enclosure under a flood (submersion beyond 1 m / 30 min) |
| M12 | Canopy ↔ stanchions | 20 W PV on 4 stanchions, aft pair hinged, front pair quick-release pins, 8° tilt | [parts.py:493-535](../../mechanical/src/parts.py#L493-L535) | Partial | Wind load on the canopy not analysed |
| M13 | Sampler ↔ water | Intake strainer at the probe depth, 6 mm tubing, purge outlet aft of the deck | [parts.py:436-442](../../mechanical/src/parts.py#L436-L442), [:634-639](../../mechanical/src/parts.py#L634-L639) | Partial | Line volume, priming lift from −335 mm to the pump at deck level |
| M14 | Stage sensor ↔ target plate (acoustic) | Sensor face 638 mm above keel on the carriage; 130×110×4 plate under the upper clamp; range 2,146 mm (low) to 146 mm (high) | [parts.py:596-599](../../mechanical/src/parts.py#L596-L599), [:691-692](../../mechanical/src/parts.py#L691-L692) | Conflicting | Range at high water below a 20–25 cm blind zone; upper buffer 48 mm to the side is a nearer reflector |
| M15 | Float ↔ pier (yaw) | Only rub rails (y = 391 mm) and bow bumpers may touch; swing radius 979 mm vs 360 mm standoff | [build.py:200-205](../../mechanical/src/build.py#L200-L205), DWG-02 | Partial | Impact energy from eddies in the pier wake not assessed |

## Electrical (described only in text; no schematic exists)

| ID | Interface | Specification | Source | Status | Open issues |
|---|---|---|---|---|---|
| E1 | PV ↔ charger | 20 W 12 V mono module (≈ 18 V Vmp) → Schottky → CN3795 charger | [kicad_sch:21](../../hardware/kicad/AquaSentinel_Mainboard.kicad_sch#L21) | Partial | CN3795 is a fixed-voltage input regulation charger, not true MPPT |
| E2 | Charger ↔ battery | LiFePO4 12.8 V 6 Ah with BMS; 5 A fuse, SMAJ15A TVS, P-MOS reverse protection, INA226 with 10 mΩ shunt | [kicad_sch:22-23](../../hardware/kicad/AquaSentinel_Mainboard.kicad_sch#L22-L23) | Partial | Charge temperature window; BMS cut-off behaviour |
| E3 | Battery ↔ switched rails | AO3401A P-FETs with 2N7002 gate drivers for 12 V sensors, 4 V modem buck (TPS54331), 5 V buck (TPS563200); IRLZ44N low-side pump switch | [kicad_sch:25-29](../../hardware/kicad/AquaSentinel_Mainboard.kicad_sch#L25-L29), [:55-58](../../hardware/kicad/AquaSentinel_Mainboard.kicad_sch#L55-L58) | Conflicting | AO3401A VGS max ±12 V < battery voltage; firmware polarity (LOW = on) vs 2N7002 driver (HIGH = on) |
| E4 | ESP32 GPIO map | Modem TX17/RX16/PWRKEY4; RS485 TX27/RX26/DE25; SD 18/19/23/CS5; I2C 21/22; stage RX34; enables 32/33/13/14; carousel 35; LED 2 | [config.h:19-50](../../firmware/edge_node/include/config.h#L19-L50) | Conflicting | v2 spec pin map is entirely different ([robotics_subsystems_spec.md:240-253](../../docs/engineering/robotics_subsystems_spec.md#L240-L253)); GPIO34/35 lack pull-ups; GPIO14 boot toggling |
| E5 | RS485 bus | SP3485 half duplex, UART1 9600 8N1, addresses 1–4, 120 Ω termination jumper, SM712 TVS | [config.h:24-27](../../firmware/edge_node/include/config.h#L24-L27), [:65-68](../../firmware/edge_node/include/config.h#L65-L68) | Conflicting | Probes default to address 1 and (pH, EC, turbidity) 4800 baud; polling interval ≥ 200 ms advised |
| E6 | Probes power | 10–30 V DC, 0.2–0.4 W each (DFRobot wikis); 12 V switched rail | DFRobot wikis | Defined | Optical DO response ≤ 60 s vs 1 s warm-up in firmware |
| E7 | Modem | SIMCom A7670C LTE Cat-1, 3.4–4.2 V, ≈ 2 A bursts, UART2 115200 | [kicad_sch:27](../../hardware/kicad/AquaSentinel_Mainboard.kicad_sch#L27), [telemetry_comm.cpp:6](../../firmware/edge_node/src/telemetry_comm.cpp#L6) | Partial | Bulk capacitance, brown-out isolation from the MCU rail; AT driver absent |
| E8 | I2C devices | DS3231SN RTC (CR1220 backup), INA226 (0x40?), PCA9685 (0x40) | [config.h:35-37](../../firmware/edge_node/include/config.h#L35-L37), [:53](../../firmware/edge_node/include/config.h#L53) | Conflicting | PCA9685 default address 0x40 equals the INA226 default 0x40 — set different address straps; no drivers |
| E9 | PCA9685 outputs | Ch0-2 beacon RGB (AO3400A), Ch3 wiper servo, Ch4 carousel motor, Ch5 pinch valve | [config.h:55-60](../../firmware/edge_node/include/config.h#L55-L60) | Partial | Motor driver for the carousel and valve driver not specified |
| E10 | Stage sensor | JSN-SR04T-class, UART RX on GPIO34 only | [config.h:39-40](../../firmware/edge_node/include/config.h#L39-L40) | Partial | Needs the sensor's auto-output serial mode; 5 V supply; control board not waterproof |

## Software and data

| ID | Interface | Specification | Source | Status | Open issues |
|---|---|---|---|---|---|
| S1 | `SensorReadings` | six floats + uint32 timestamp + valid[6] | [anomaly_engine.h:20-29](../../firmware/edge_node/include/anomaly_engine.h#L20-L29) | Defined | `valid[]` not consumed |
| S2 | `AnomalyResult` | level, max_score, reason[128], flags, trigger | [anomaly_engine.h:31-37](../../firmware/edge_node/include/anomaly_engine.h#L31-L37) | Defined | — |
| S3 | Logger / telemetry data model | `WaterQualityReading`, `AnomalyReport` | microsd_logger.*, telemetry_comm.* | Undefined | Types do not exist |
| S4 | NVS namespace `aquasampler` | keys `bottle_idx`, `last_ts`, `rec_0..3` | [autosampler.cpp:19-21](../../firmware/edge_node/src/autosampler.cpp#L19-L21), [:106-115](../../firmware/edge_node/src/autosampler.cpp#L106-L115) | Defined | No integrity protection |
| S5 | Telemetry wire format | JSON over LTE (MQTT per budget notes), ≤ 512 B | [telemetry_comm.cpp:9-36](../../firmware/edge_node/src/telemetry_comm.cpp#L9-L36) | Undefined | Broker, topic, auth, TLS, retries, SMS format |
| S6 | `design_checks.json` | mass, hydrostatics, hydrodynamics, pole, carriage, clearances, levels, checks, mass_table | [build.py:66-283](../../mechanical/src/build.py#L66-L283) | Defined | — |
| S7 | GLB scene metadata | node extras (pid, part, label, desc, process, material, kg, kind, step, explode, group); pivots; scene extras (steps, levels, draft, checks, key_numbers) | [build.py:365-406](../../mechanical/src/build.py#L365-L406) | Defined | Rendered with `innerHTML` in the viewer |
| S8 | Viewer capture API | `window.AS`: still, ortho, seek, recordWC, record; `POST /save?path=` | [template.html:679-756](../../mechanical/viewer/template.html#L679-L756), [serve.py](../../mechanical/tools/serve.py) | Defined | Unauthenticated local writes |
| S9 | Dataset CSV | 12 columns (see DATA_FLOW §3) | generator | Conflicting | `dataset/README.md` documents a different 10-column schema |

## Human interfaces

| ID | Interface | Specification | Source | Status | Open issues |
|---|---|---|---|---|---|
| H1 | Beacon colours | Green normal, amber advisory, red danger (v2 spec); R3 docs mention green/red | [robotics_subsystems_spec.md:196-202](../../docs/engineering/robotics_subsystems_spec.md#L196-L202) | Partial | Not implemented; red/green lights on water read as IALA lateral marks at night; visibility claims (800 m day) unverified; power not budgeted |
| H2 | Dashboard / community portal | English, Marathi, Hindi; command and community views | [docs/dashboard](../../docs/dashboard/index.html) | Partial (demo) | No live data; can be made to look live |
| H3 | SMS alerts | Subscription prompt | [app.js:575-580](../../docs/dashboard/js/app.js#L575-L580) | Undefined | No backend; misleading confirmation |
| H4 | Sample hand-over | Technician collects carousel, lab analysis, CoC sheet | [robotics_subsystems_spec.md:285-314](../../docs/engineering/robotics_subsystems_spec.md#L285-L314) | Partial | Water Act §21 procedure; cooling ≤ 6 °C and 48 h BOD holding time |
| H5 | Service access | Canopy/lids open; cartridge lifts out; gate T-pins | DWG-03/04 | Partial | Float cannot carry a person; boat procedure, PPE, two-person lift 43.6 kg dry |
