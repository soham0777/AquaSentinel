# Technical research beyond the repository

Searched on 2026-10-18. Each entry separates **what the repository says**, **what the external source says**, and **what follows**.
Primary sources (standards bodies, regulators, manufacturers, peer-reviewed papers) are preferred; secondary sources are marked.
Items that could not be confirmed are stated as such and appear in [OPEN_QUESTIONS_AND_NEXT_STEPS.md](../audit/OPEN_QUESTIONS_AND_NEXT_STEPS.md).

## 1. Regulation and legal use of data

### 1.1 CPCB designated-best-use criteria — subsystem: decision logic, claims
* **Repository:** EC ≤ 2250 µS/cm is used as a "CPCB Class C" hard limit (firmware `config.h`, README, claims register).
* **Sources:** [CPCB water quality criteria](https://cpcb.nic.in/water-quality-criteria/) (primary); [WII summary](https://v1.wii.gov.in/node/564);
  [UKPCB copy](https://ukpcb.uk.gov.in//public/fileupload/84.pdf). Class C (drinking-water source after conventional treatment and
  disinfection): total coliforms ≤ 5000 MPN/100 mL, pH 6–9, DO ≥ 4 mg/L, BOD₅ ≤ 3 mg/L. **Class E** (irrigation, industrial cooling,
  controlled waste disposal): pH 6.0–8.5, EC ≤ 2250 µmhos/cm, SAR ≤ 26, boron ≤ 2 mg/L.
* **Follows:** relabel the EC limit (Class E) or justify 2250 µS/cm on its own merits. Class C's BOD and coliform criteria cannot be
  measured by the probes — which supports the project's own "probes give clues, labs give proof" position.

### 1.2 Water (Prevention and Control of Pollution) Act 1974, Section 21 — subsystem: autosampler, evidence claims
* **Repository:** the sampler "seals a time-stamped water sample" as legal evidence for NABL analysis.
* **Sources:** [Section 21 text](https://lawx.in/acts/section/122/1090/9382); [MPCB standing order on evidentiary samples](https://www.mpcb.gov.in/sites/default/files/standing_orders/LawEvidenceSample.pdf);
  [NGT document](https://www.greentribunal.gov.in/sites/default/files/news_updates/2719_9.pdf). The analysis of a sample of sewage or
  trade effluent is admissible in legal proceedings only if the Board serves notice on the occupier, divides the sample into two parts
  in the occupier's presence, and seals and signs the containers with them (§21(2)–(5)).
* **Follows:** an unattended float cannot satisfy this procedure. Position the bottle as an early-warning/triage sample that triggers
  formal sampling by the Board; get a lawyer's view before using the word "evidence". (Full text of §21(4)–(5) and case law not checked.)

### 1.3 Sample preservation and holding times — subsystem: autosampler
* **Sources:** 40 CFR 136 Table II as reproduced by the [NY ELAP manual](https://cfwww10-origin.wadsworth.org/sites/default/files/WebDoc/I242_12.pdf)
  and [Wisconsin DNR](https://dnr.wisconsin.gov/topic/labCert/BODSampleHandling.html): BOD — cool to ≤ 6 °C (not frozen), analyse
  within 48 h; Standard Methods recommends ≤ 6 h for grab samples. Older excerpts say 4 °C. (Indian IS 3025 holding-time tables were
  not checked.)
* **Follows:** an insulated, uncooled cassette on a sunny river does not preserve BOD or microbiology samples; define per-analyte
  bottles, preservation and maximum time-to-collection with the receiving laboratory.

### 1.4 Navigation lights — subsystem: beacon
* **Sources** (secondary/educational): [Maritime Safety Queensland](https://www.msq.qld.gov.au/Safety/Navigation-buoys-marks-and-beacons),
  [IALA special marks summary](https://ialacolreg.com/en/iala/iala-special). India uses IALA Region A: red lights mark the port side of a
  channel and green the starboard side; special marks are yellow with yellow lights.
* **Follows:** a flashing red/green light on a structure in a river can be read as a lateral mark at night. Ask the waterway authority;
  a yellow special-mark light or a shielded, bank-facing indicator may be required.

## 2. Sensors and electronics

### 2.1 DFRobot RS485 probes — subsystem: sensing, firmware
| Probe | Range / accuracy | Supply / power | Comms default | Other | Source |
|---|---|---|---|---|---|
| SEN0708 pH | 0–14 pH, ±0.15, 0.01 res. | 10–30 V, 0.4 W | Modbus RTU, address 1, **4800 baud** | ATC; response < 1 s; poll ≥ 200 ms | [wiki](https://wiki.dfrobot.com/sen0708/) |
| SEN0707 EC (K=10) | 10–20,000 µS/cm, **±1 % FS (±200 µS/cm)** | 10–30 V, 0.4 W | address 1, **4800 baud** | calibration solution 12,880 µS/cm | [wiki](https://wiki.dfrobot.com/sen0707/) |
| SEN0680 optical DO | 0–20 mg/L, **±3 % FS** | 10–30 V | address 1 (baud not found) | **response ≤ 60 s**, 0–40 °C, film life ≈ 1 year | [wiki](https://wiki.dfrobot.com/sen0680/) |
| SEN0710 turbidity | 0–1000 NTU, **±5 % FS (±50 NTU)** | 10–30 V, 0.2 W | address 1, **4800 baud**; reg 0x0000 ÷ 10 = NTU | IR 90° scatter; recalibrate ≈ 90 days | [wiki](https://wiki.dfrobot.com/sen0710/), [forum](https://www.dfrobot.com/forum/topic/401813) |

* **Repository:** bus at 9600 baud, addresses 1–4, 1 s warm-up, no inter-poll delay ([sensor_interface.cpp](../../firmware/edge_node/src/sensor_interface.cpp)).
* **Follows:** commission each probe (unique address, common baud); poll at ≥ 200 ms intervals; warm up long enough for the DO probe;
  read the register maps from DFRobot's reference documents before trusting the scaling. Full-scale accuracies are coarse at river
  levels (EC ~300 µS/cm, turbidity ~10 NTU): detection must rely on changes (repeatability) and on field calibration, and the
  K = 10 EC cell is a poor match for fresh water — DFRobot lists a K = 1 cell (SEN0706) worth evaluating. Costs quoted by
  DFRobot for SEN0707 ($159) and SEN0710 ($229) are consistent in magnitude with the project's cost estimate.

### 2.2 Power-switch MOSFET — subsystem: electronics
* **Source:** [Alpha & Omega AO3401A datasheet](https://aosmd.com/sites/default/files/res/data_sheets/AO3401A.pdf): VGS absolute
  maximum **±12 V** (repository notes say ±20 V).
* **Follows:** with a 12.8–14.6 V battery rail and the gate pulled to 0 V, the rating is exceeded. Use a ±20 V part or clamp VGS.

### 2.3 INA226 power monitor — subsystem: bench energy test
* **Source:** [TI INA226](https://www.ti.com/product/INA226): shunt-voltage LSB 2.5 µV; offset ±2.5 µV typical, **±10 µV maximum**.
* **Follows:** with 10 mΩ the resolution is 0.25 mA and the offset up to ±1 mA — unable to verify a 0.6 mA standby floor. Use a
  separate low-current measurement for sleep.

### 2.4 Ultrasonic stage sensor — subsystem: stage sensing
* **Sources** (vendor/secondary): [components101](https://components101.com/node/1522), [atomic14](https://www.atomic14.com/esp32/sensors/jsn-sr04t/):
  blind zone ≈ 20–25 cm, beam up to ≈ 75°, range 4.5–6 m, only the transducer is waterproof, serial mode selected by a resistor.
* **Follows:** the R3 geometry gives 146 mm range at high water (below the blind zone) and a reflector 48 mm off-axis. Alternatives:
  vented pressure transducer on the float (measures immersion, not stage) or on the bracket (measures stage directly, needs barometric
  compensation if absolute); downward-looking radar or ultrasonic level sensor on the upper bracket (non-contact, but the float and
  debris can be in its view). Each needs a bench test.

### 2.5 LTE modem current — subsystem: power
* **Sources:** [SIMCom A7670 hardware design](https://www.elecrow.com/download/product/CRT01260S/A7670_Series_Hardware_Design_V1.00.pdf)
  (official, power chapter not read); secondary notes cite bursts up to ≈ 2 A at 3.4–4.2 V.
* **Follows:** size the 4 V buck, bulk capacitance and wiring for 2 A bursts; keep the MCU supply isolated to avoid brown-outs that
  erase RTC memory.

### 2.6 ESP32 RTC memory — subsystem: firmware
* **Source:** [ESP-IDF memory types](https://docs.espressif.com/projects/esp-idf/en/v5.0/esp32/api-guides/memory-types.html): RTC
  memory keeps data through deep sleep; forum reports show it is cleared by power-on/brown-out resets and sometimes software restarts.
* **Follows:** store learned baselines and counters in NVS/flash (rate-limited writes) and check `esp_reset_reason()` at boot.

### 2.7 LiFePO4 temperature limits — subsystem: power
* **Source** (manufacturer education page): [Battle Born](https://battlebornbatteries.com/blogs/academy/understanding-temperature-limits-of-lifepo4-batteries-the-battle-born-educational-series);
  typical charge window 0–45 °C, some packs to 50–55 °C; pack-specific BMS cut-offs.
* **Follows:** the shading canopy is justified; choose a pack whose BMS enforces the charge window and log enclosure temperature.

## 3. Methods for monitoring, detection and transport

### 3.1 Continuous monitor operation — subsystem: operations, analytics
* **Source:** USGS Techniques and Methods 1-D3, [Wagner et al. (2006)](https://pubs.usgs.gov/tm/2006/tm1D3/): site selection, field
  cleaning and calibration, fouling and drift error determination, record computation and data reporting for temperature, specific
  conductance, pH, DO and turbidity. Still the operative USGS reference.
* **Follows:** adopt its service-visit protocol (before/after cleaning readings, calibration checks) to quantify fouling and drift,
  and its record-correction method for the data the float produces.

### 3.2 Event detection — subsystem: decision logic
* **CANARY** (US EPA / Sandia; [GitHub](https://github.com/USEPA/CANARY), LGPL/Apache): open-source event detection for water-quality
  time series. [Burkhardt et al. (2022), Environ. Sci.: Adv., doi:10.1039/D2VA00014H](https://pubs.rsc.org/en/Content/ArticleLanding/2022/VA/D2VA00014H)
  applied it to near-real-time watershed monitoring for illicit discharges and note that some discharges produce no sensor signal.
  The repository's claims register cites this paper as "> 90 % of illicit discharge events" — that figure was **not** confirmed here.
* **Leigh et al. (2019)**, [arXiv:1810.13076](https://arxiv.org/abs/1810.13076v2), *Science of the Total Environment*: a framework for
  automated anomaly detection in high-frequency in-situ water-quality data (turbidity, conductivity, level); regression/ARIMA methods
  found most high-priority technical anomalies (spikes, level shifts).
* **SCCWRP field test** ([2024 news](https://www.sccwrp.org/news/field-testing-phase-shows-success-in-using-low-cost-sensors-to-automate-detection-of-illicit-discharges/)):
  low-cost sensors detected four of five intentional discharges upstream of monitoring sites (secondary report).
* **Follows:** keep the simple on-board rules for autonomy, add a sensor-fault layer (Leigh et al.), and benchmark against CANARY and
  control-chart baselines on harder synthetic data and, later, pilot data.

### 3.3 Longitudinal dispersion — subsystem: plume model
* **Sources:** Kashefipour & Falconer (2002), *Water Research* 36(6):1596–1608, [doi:10.1016/S0043-1354(01)00351-7](https://orca.cardiff.ac.uk/7872);
  the equation as tabulated in [arXiv:2106.11026, Table 2](https://arxiv.org/pdf/2106.11026): D/(H u*) = 10.612 (U/u*)² for W/H > 50, and
  (7.428 + 1.775 (W/H)^0.62 (U/u*)^0.572)(U/u*)² for W/H ≤ 50 (the exponent's ratio is usually cited as u*/U; check the original).
  Fischer's D = 0.011 U²W²/(H u*) and the transverse mixing length L ≈ 0.1–0.4 U W²/ε_t with ε_t ≈ 0.6 H u* are textbook results
  (Fischer et al., *Mixing in Inland and Coastal Waters*, 1979).
* **Follows:** correct line 44 of the model, show the W/H ≤ 50 branch, and restrict the 1-D solution to distances beyond the mixing
  length; for warnings, travel time (distance ÷ velocity, with an uncertainty band) matters more than peak concentration.

### 3.4 Flow around bridge piers — subsystem: mechanical siting
* **Source:** HR Wallingford study on piers in tandem ([PDF](https://eprints.hrwallingford.com/1023/1/PA_1_9-Beg-M.pdf)): vortices shed
  by a front pier influence a rear pier until spacing exceeds ≈ 6 pier widths; wake vortices drive scour behind piers.
* **Follows:** the float sits well inside the pier's near wake; expect unsteady yaw and cyclic loads. Test in a flume or observe on site;
  consider a side-face mounting clear of the wake.

### 3.5 Pipe tolerances — subsystem: guide
* **Source** (secondary): [Rolled Alloys](https://www.rolledalloys.com/pipe-sizes-and-tolerances/) on ASTM A999: OD tolerance −0.031 in
  on all sizes and +0.031 in for NPS 1½–4, ovality included.
* **Follows:** NPS 2 OD 59.5–61.1 mm; a 60.7 mm reamed clamp bore may not accept the pipe; measure before machining.

## 4. Context and claims checked
| Claim in the repository | Finding | Source |
|---|---|---|
| Maharashtra has the most polluted river stretches (55, CPCB 2022) | Confirmed by press coverage of CPCB's 2022 report; a later review gives 54 | [Hitavada](https://thehitavada.com/Encyc/2023/1/28/Maha-tops-India-in-most-polluted-river-stretches.html) |
| Real-time stations cost ₹35 lakh+ (CSE) | CSE quotes ₹35–40 lakh for 10-parameter instruments; other public figures ≈ ₹50–84 lakh per station including systems. Stations measure more parameters than AquaSentinel, so "1/25th the cost" is not like-for-like | [CSE](https://www.cseindia.org/cpcbs-real-time-water-quality-monitoring-4587), [Lok Sabha reply](https://eparlib.nic.in/bitstream/123456789/700028/1/5115.pdf) |
| 9.98 MLD untreated sewage at Kopargaon (NGT affidavit) | Not found in public sources during this audit | — |
| Kopargaon flood stage range | Not found; check CWC flood forecasting stations and Maharashtra WRD gauge records | CWC FFS (not verified) |

## 5. Comparable approaches and alternatives
| Topic | AquaSentinel choice | Alternatives and trade-offs (evidence-based where cited) |
|---|---|---|
| Platform | Float on a guide pole at a bridge pier | Perforated stilling pipe bolted to the pier with probes at fixed elevation (simpler, no moving parts; probes exposed at low water, no constant depth). Moored buoy (no pier needed; mooring and theft issues). The float's real advantage is constant depth below the surface and deck access |
| Data logger | Custom ESP32 board (not built) | EnviroDIY Mayfly + Monitor My Watershed (open hardware, solar, cellular, 15-min sampling, open data portal; [Eos](https://eos.org/science-updates/a-digital-mayfly-swarm-is-emerging)) — proven ecosystem; Modbus support not confirmed here |
| Probes | Four separate DFRobot RS485 probes | Integrated multiparameter sondes with a central wiper (better accuracy, field-proven; much higher cost — get quotes) |
| Detection | EWMA + robust z + 2-of-3 + hard limits | CUSUM/EWMA control charts; CANARY; ARIMA residuals with a technical-anomaly filter (Leigh et al.) |
| Comms | LTE Cat-1 | LTE-M/NB-IoT (lower power where covered), LoRaWAN (needs a gateway), SMS-only fallback |
| Stage | Upward ultrasonic to a plate | Pressure transducer; downward radar from the bracket |
| Fouling | Mechanical wiper on all faces | Wipe optical faces only; copper guards; scheduled manual cleaning per USGS TM1-D3 |

## 6. Research opportunities
1. Quantify detection limits on a realistic synthetic generator calibrated with pilot data (drift, fouling, rain pulses).
2. Field comparison of float-mounted probes vs a pier-mounted stilling pipe at the same site (effect of the pier wake and well).
3. Low-cost sample preservation on the float (passive cooling, preservative-dosed bottles) with laboratory acceptance criteria.
4. A community-legible warning signal designed with users and the waterway authority (colour, placement, meaning, false-alarm cost).
5. Travel-time warnings using real-time flow from the stage record, with uncertainty, validated by a dye or salt tracer test.
