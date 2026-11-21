# AquaSentinel: ground-truth technical audit and portal cross-check

**Date:** 5 Nov 2026 (night). **Scope:** the whole folder `C:\Users\dell\OneDrive\Desktop\AquaSentinel` (excluding `.git` and Claude's worktrees), plus the AAKRUTI portal, Gmail and the WhatsApp export.

**Ground rules:** read-only. Nothing in the project or on the portal was changed. The only things run were the detector benchmark (on a scratch copy) and read-only STL checks.

**Status labels used throughout:**
- ✅ **DONE**: exists and is verified.
- 🟨 **IMPLEMENTED, UNVERIFIED**: code or design exists but has not run on hardware or in water.
- 🟥 **STUB / MISSING**: claimed or needed, but not implemented.
- ⬜ **SUPERSEDED**: kept as an archive; don't present it.
- 📤 **PORTAL ACTION**: must be uploaded or updated.

---

## 0. Method: what was actually checked

| Area | What I did | Coverage |
|---|---|---|
| Inventory | Walked every file and recorded type, size and SHA-1 | **1,643 files, 1.11 GB**: 463 SLDPRT, 11 SLDASM, 141 STEP, 351 STL, 245 PNG, 68 JPG, 13 MP4, 21 PDF, 9 PPTX, 5 DOCX, 7 XLSX, 61 MD |
| Source code | Listed all 155 code files (31,291 lines). Read the firmware line by line (all 17 modules + 2 test suites); read analytics, web, schematic and build scripts | Firmware 100 %; analytics and web: core files; build and render scripts: purpose and outputs |
| Duplicates | Hash comparison | The firmware exists in **3 identical copies** (06/edge_node, 06/ArduinoIDE, 09/firmware): no drift |
| Execution | Re-ran `evaluate.py` on a copy | **4 of 4 synthetic events detected, 30 min latency, 0 false alarms**: reproduces |
| CAD/STL | Mesh watertightness on all 37 printable LIVE-model STLs and 66 R3 STLs; read the R3 design checks | Details in §5 |
| Documents | Extracted text from **96** PDF/PPTX/DOCX/MD files and checked team, cost, autonomy, stage and architecture claims | Details in §6 |
| Portal | Students Dashboard (tasks, team, timeline, licences), team community, FDC post, FDC guidelines and template, "Best Teams", rules | Rules PDF: **only page 1 readable** in the portal viewer (see §8) |
| **Not done** | SOLIDWORKS rebuild of the 17 LIVE-model parts (**Vector was running**, and both act on the active document); compiling the firmware (PlatformIO not installed) | Can be done on request |

---

## 1. Ground truth: what AquaSentinel is today

### 1.1 Two products, many archives

| Item | Folder | Status | Present to the jury? |
|---|---|---|---|
| **R3 full-size design** (float on a guide pole, ESP32, RS485 probes, LTE, autosampler) | 01, 03, 04, 06, 09 | ✅ CAD + analysis + cost; 🟥 never built | **Yes**: the product |
| **1:5 LIVE sensor model** (real sensors in a 1:1 cage, Raspberry Pi) | 05 | 🟨 31/37 parts printed; plinth not printed; F03 and column unconfirmed; not wired; no software | **Yes**: the physical prototype |
| 1:5 display kit (original) | 05 (in the LIVE model) | ✅ printed and reused | Part of the LIVE model |
| Sensor housing, demo station, simple housing, P1 float, Sensor Tower, Pi payload | 10–16 | ⬜ SUPERSEDED | No |
| R3 + Pi hardware fit | 17 | ✅ CAD only (an analysis of how the hobby hardware would fit R3) | Optional backup slide |
| FDC banner pack | 18 | ✅ ready, 📤 waiting for upload | Portal |
| Design audit and roadmap | 19 | ✅ | Internal |

### 1.2 Architecture: as designed vs as built

| Subsystem | Designed (R3) | Implemented (code or hardware) | Status |
|---|---|---|---|
| Sensing | 4× RS485 Modbus probes (pH, EC, DO, turbidity) + temperature + ultrasonic stage | Modbus driver with CRC, exception handling, 3-read median, range checks, health bits; stage reports "no reading" (NaN) | 🟨 Driver written; **never run on a probe**; register maps "confirm on bench" |
| Decision | Diurnal robust z-score + CPCB hard limits + 2-of-3 persistence + learning + fail-safe | Fully coded; persistence to flash; 26 unit tests written | 🟨 Logic sound; **tests never run on a board**; clock missing (§2) |
| Act: beacon | PCA9685 RGB 360° beacon | `Serial.println` only | 🟥 STUB |
| Act: autosampler | Pump + 3-way valve + carousel + optical index | Pump GPIO toggled; valve, carousel and index simulated; "reverse" ignored | 🟥 Mostly STUB |
| Act: wiper | Servo sweep every 6 h | Prints + delays | 🟥 STUB |
| Communication | A7670C LTE: MQTT/HTTP + SMS | JSON frame built; written raw to the UART; modem never powered or registered; `transmit()` always returns true | 🟥 STUB |
| Storage | microSD CSV log + backlog queue | Log works in code; the backlog is never used and `popBacklogRecord` doesn't remove the line | 🟨 / 🟥 |
| Time | DS3231 RTC | **Not used**: `time(NULL)` is never set | 🟥 MISSING |
| Power | MPPT, LiFePO4, gated rails, INA226 | Only the 12 V sensor rail and the pump are switched; the 4 V modem and 5 V peripheral rails are never enabled; INA226 not read | 🟥 Partial |
| Dashboard | Live data + alerts | Static GitHub Pages **demo**, honestly labelled, in 3 languages | ✅ demo; 🟥 no live link |
| LIVE model electronics | Pi 3B+ + ADS1115 ×2 + sensors + SIM800L + MX1508 | Design document (13) only; **no Pi code**; purchases unconfirmed | 🟥 MISSING |

---

## 2. Firmware audit: new findings and earlier findings re-verified

Line references are to `06_ELECTRONICS_AND_FIRMWARE/firmware/edge_node/` (identical in the other two copies).

### 2.1 Open defects

| # | Severity | Finding | Evidence |
|---|---|---|---|
| FW-1 | 🔴 Critical | **All actuators and the modem are print statements.** Beacon, valve, carousel, wiper and LTE upload do nothing physical (earlier finding F3 still open) | `main.cpp:67-82`, `autosampler.cpp:41-66`, `wiper_actuator.cpp:16-29`, `telemetry_comm.cpp:59-71` |
| FW-2 | 🔴 Critical | **Power-rail polarity contradiction (F6 still open).** The firmware drives the enables active-LOW ("HIGH = OFF"); the schematic text drives each P-MOSFET through a 2N7002, which makes them active-HIGH. Built as described, **every switched rail is ON when the firmware thinks it is OFF**, and the reverse | `sensor_interface.cpp:49,60,69` vs `kicad_sch:55-57` |
| FW-3 | 🟠 High | **No real clock.** Timestamps come from `time(NULL)`, which is never set, so the 24 hourly baselines are indexed by "hours since power-on". After any power cut the diurnal phase shifts and baselines misalign. The DS3231 on the board is never read | `sensor_interface.cpp:208`, `main.cpp:122` |
| FW-4 | 🟠 High | **Warm-up is 1 s, not 30 s** ("1s simulation delay in demo"). Optical DO and turbidity probes would read unstable values | `sensor_interface.cpp:64` |
| FW-5 | 🟠 High | **Telemetry can't fail.** `transmit()` returns `true` regardless, and the SD backlog is never called, so lost alerts are not detected or re-sent | `telemetry_comm.cpp:59-71`, `microsd_logger.cpp:67-97` |
| FW-6 | 🟡 Medium | `popBacklogRecord()` reads the first line but doesn't delete it; it would loop forever if used | `microsd_logger.cpp:90-97` |
| FW-7 | 🟡 Medium | Hourly baselines converge slowly: α = 1/96 applied about 4× a day per bin (F12 still open) | `anomaly_engine.cpp:36` |
| FW-8 | 🟡 Low | Dead code: `rtc_temp_bins` is never used; `dsp_filters` and `exported_anomaly_weights.h` are never called; the 5 V and 4 V rails and the status LED are never driven | `anomaly_engine.cpp:17`, `dsp_filters.cpp`, `config.h:44-50` |
| FW-9 | 🟡 Low | Log lines state unmeasured figures as facts ("0 µA sleep current", "15 µA", "250 mL preserved", "Carousel… [CONFIRMED]") | `sensor_interface.cpp:68`, `main.cpp:152`, `autosampler.cpp:64,125` |
| FW-10 | 🟡 Low | Deep sleep doesn't hold GPIO states (`gpio_hold_en`). Rail states during sleep depend entirely on board pull resistors, which are undocumented | `main.cpp:155-156` |
| FW-11 | ⚪ Unverified | "Compiles cleanly in both environments" is stated in the README. Not verifiable here (no PlatformIO). Unit tests **never run on a board** (README says so) | `firmware/README.md` |

### 2.2 Earlier findings confirmed fixed

| Finding | What was fixed |
|---|---|
| F2 | Fail-safe: a dead probe is never "normal" |
| F4 (part) | Stage is no longer a fake constant |
| F5 | Learned state survives a power cut |
| F7 | One sample per event |
| F9 | `evaluate.py` now computes 4/4 against the labels |
| F11 | No stale event after learning |
| F16 | The dashboard is labelled DEMO |
| F18 | The EC limit is correctly called CPCB Class E |

**Credit where due:** the decision engine is genuinely well engineered: a health-bit model, fail-safe overlay, flash persistence, a one-sample-per-event state machine and 26 targeted unit tests. **Its weakness is everything around it:** clock, actuators, modem and hardware polarity.

---

## 3. Analytics, web and tools

| Item | Finding | Status |
|---|---|---|
| Detector benchmark | Re-ran it: **4/4 events, 30 min latency, 0 false alarms, 4 samples**. But the data is **synthetic and made by the same team**, the events are large, and the benchmark assumes a correct clock that the firmware doesn't have | ✅ reproduces; ⚠ limited validity |
| `advection_dispersion_model.py:44` | The Kashefipour–Falconer coefficient is still coded in a non-published form (F10 still open); dispersion feeds the dashboard's downstream countdown | 🟠 fix or drop the formula |
| `train_proxy_anomaly_engine.py` | Writes over the firmware header in place (F13 still open); the header isn't used | 🟡 |
| Dashboard / site | Honest demo labels, EN/MR/HI, no personal data collected, `innerText` used (no XSS sink in `app.js`); the viewer loads three.js 0.169.0 from jsDelivr **without SRI** | ✅ / 🟡 |
| `mechanical/tools/serve.py` | Local dev server; POST writes are path-restricted; local use only | 🟡 OK for local use |
| Secrets | None found in code or config; the earlier audit's register confirms it | ✅ |

---

## 4. Electronics documentation

| Item | Finding | Severity |
|---|---|---|
| `hardware/kicad/AquaSentinel_Mainboard.kicad_sch` | **Not a real schematic.** It has **0 wires and 0 placed symbols**; the netlist exists only as `#` comment text, so KiCad can't open it as a circuit. If presented as "our schematic", a juror who opens it sees nothing | 🔴 credibility |
| Same file, title block | "CAD: Shriraj Kamble" (former member); "Project AquaRight" (old name) | 🟡 |
| `power_budget.csv` | 3.39 Wh/day, **15.1 days** autonomy, no beacon load. The README and deck say **about 12 days** including an assumed beacon. Both are estimates; label which is which | 🟡 |
| Cost figures | **Four totals in circulation:** ₹1.38 lakh (`hardware/AquaSentinel_Cost_Estimate_BOM.csv`, v2 layout), ₹1.57 lakh float only, ₹1.87 lakh float + kit (README, deck), ₹2.19 lakh (an earlier note, likely including GST) | 🟠 pick one source of truth |

---

## 5. CAD and STL verification

| Check | Result |
|---|---|
| R3 generator design checks (`design_checks.json`) | **14/14 PASS** [calculated]: buoyancy 2.27×, freeboard 143 mm, GZ to 60°, pole SF ≥ 2 (2.66), no jamming, no clash over 2 m travel, and so on |
| R3 in SOLIDWORKS (Pack and Go, 144 components) | Opens, all references resolve. **141 SOLIDWORKS interferences**: bolts modelled without holes, and contents inside solid pod and sampler blocks. This conflicts with the generator's "No part-to-part interference: PASS". **Explain it, or clean it with simplified fastener and hollow enclosure bodies before showing interference detection to a juror** |
| R3 STLs (66) | 64 watertight; **2 with small open edges** (AS3-411 cartridge cap: 32 edges; AS3-711 antenna: 20). Display only |
| **LIVE-model STLs (37, `05/01_FINAL_STL`)** | **37/37 watertight**, 0 degenerate faces |
| LIVE-model print fit | LD-S01 plinth **300 × 200 mm: too big for a 256 mm bed** (blocked). ORIG-OPT rod 310 mm fits only diagonally. Everything else fits |
| LIVE-model native CAD | 17 SLDPRT, **no SLDASM** (the assembly exists only as a JSON of transforms for the renderer). The generator script `build_live_model_sw.py` referenced by the design notes was **recycled on 5 Nov** (cleanup log) |
| LIVE-model SOLIDWORKS rebuild check | **Not run** (Vector active) |

---

## 6. Documentation consistency (96 documents scanned)

| Issue | Where | Action |
|---|---|---|
| **Former member still named** | `AquaSentinel_Complete_Project_Dossier.pdf` (root), semi-final deck notes/PDF/script, ML Capstone PDF/DOCX, the FDC deck copy in `09/docs/presentation`, KiCad title block, GitHub README/site/LICENSE/build guide | Update outward-facing documents. Credit Shriraj as a former member where history matters |
| **Architecture mismatch** | Every R3 document says ESP32 + RS485 + LTE; the physical prototype uses a Pi + hobby analog sensors + 2G SIM800L | Say it plainly in the pitch: "R3 field design vs the LIVE demonstrator from available parts" |
| **Stage wording** | The README and site say "India Semi-Final"; you are now an **India Geo Finalist** | Update after the finale materials are ready |
| **Cost** | 4 different totals (§4) | One costed BOM, ex-GST, quoted the same everywhere |
| **Autonomy** | 12 days vs 15.1 days | State which includes the beacon |
| Superseded material | 10–17 and two root files (Pi-concept ZIP, R3P dimension check) | Fine as an archive; mark "superseded" in a short root note (on approval) |

---

## 7. Prototype readiness (1:5 LIVE model)

| Gate | Status |
|---|---|
| Parts printed | 31/37 ✅; F03 frame and column 🟨 (PLATE_05 "LOADED" since 2 Nov); plinth 🟥 blocked |
| Sensor fit in the cage | 🟥 not test-fitted (the cage was printed from assumed sizes) |
| Purchased items (dish, bottle, hose, LED, rod, screws) | 🟥 no evidence |
| Pi electronics (ADS1115 ×2, bucks, SIM800L supply, switches) | 🟥 no evidence of purchase or wiring |
| Software | 🟥 none |
| Wet test and calibration | 🟥 not done |
| Booth constraints (no personal laptop; video without music) | 🟥 not yet addressed |
| Known design risks | Water only 1.5 mm over the cage plate; turbidity sensitive to ambient light; the float can rotate ±7° (§4 of report 19) |

---

## 8. AAKRUTI portal requirements vs our implementation

Sources:
- the FDC guideline (Task 6) and the FDC template post;
- the "Best Teams" page, where every winner gave pitch video, journey video, CAD, FDC presentation, and rendered images or video;
- WhatsApp, 2 Nov: lock the data by 7 Nov, update the existing FDC post, hero images go on the banner, no laptops at the booth, no music in videos;
- the Students Dashboard;
- the rules PDF (*Competition rules – AAKRUTI – 18032026.pdf*), of which only page 1 is readable in the portal viewer.

| Portal requirement | What is on the portal now | Verdict | Action |
|---|---|---|---|
| Team & Product details (ID, name, theme, product) | ✅ correct; product name says "(R3 design)" | ✅ | Optional: add "+ 1:5 live demonstrator" |
| Final Presentation (official template) | ✅ uploaded 5 Oct; **its team slide shows Shriraj** | 📤 UPDATE | Add the team image from pack 18 and a note on the 22 Oct change |
| Pitch / marketing video, 90 s to 2 min | ✅ 110 s video. The finale rule says no background music; **the 60 s marketing video has a "generated music bed"**. The 110 s pitch video and journey video are unchecked | 📤 CHECK | Listen to both. Make voice-over or silent versions for the finale PPT |
| Journey video, 90 s to 2 min | ✅ 1:58 | ✅ | Music check as above |
| CAD model: assembly + parts in one zip (Pack and Go) | ✅ R3 Pack and Go (66 parts) | ✅ for R3; 🟥 for the LIVE model | **Add a LIVE-model Pack and Go**, which needs the SLDASM to be built first |
| Additional: simulation (DS tools only) | ✅ SOLIDWORKS Simulation pole and bracket reports | ✅ | Optional: a SOLIDWORKS **Flow Simulation** study (licence available) |
| Additional: rendered images | ✅ 21 images, displayed at ≤ 960 px | 📤 UPDATE by **7 Nov** | Upload pack 18: 4800 px heroes + team image |
| Rendered **video** (winners included one) | ✗ not in the post; `07_VIDEOS/AquaSentinel_R3_Assembly_and_Operation_1080p.mp4` exists (1:47, **no audio track**: music-safe) | 📤 ADD (recommended) | Upload or link it under rendered images/video |
| Banner: "hero images of your product" (WhatsApp, 2 Nov) | Old renders only | 📤 **by 7 Nov** | Pack 18 |
| Compass role (WhatsApp, 2 and 4 Nov) | Roles held: 3DSwymer, Collaborative Industry Innovator, xDesign for Education. Requestable licences: 3DEXPERIENCE ENGINEER, VIRTUAL STORYTELLER | ❓ | Compare with the organisers' screenshot; request the role in the portal (your approval) |
| Certificates | Unlock **6 Nov** | 📤 download | Team + mentor |
| Assigned tasks (registration → FDC, bonuses, regional) | All ✅ | ✅ | None |
| Team details on the portal | ✅ Prasad as Member 01 | ✅ | None |
| Booth (19 Nov): table, banner, 1 display via **their** laptop | Our demo plan assumed a laptop | 🟥 | Pi with its own screen; ask the organisers how to hand over files |
| Finale pitch: 7 min + 6–7 min Q&A | Deck and script are semi-final versions (8 min) | 🟥 | New 7:00 deck |
| Travel bills | After the trip, **as a reply on the AAKRUTI thread** | Later | |

---

## 9. Prioritised action plan

Official dates are marked ★; all other dates are my recommendation.

| Pri | When | Action | Depends on | Owner |
|---|---|---|---|---|
| P0 | **★ by Sat 7 Nov** | Update the FDC post: pack 18 (hero images + team image + text). Optionally add the R3 assembly/operation video | – | You (upload) |
| P0 | 6 Nov | Download certificates (★ unlock 6 Nov). Ask Shubham: the role screenshot; whether a Pi with its own screen is allowed; how and when to hand over files | – | You |
| P0 | 6–7 Nov | Confirm PLATE_05; decide the plinth (H2D, or a CAD split in a new file); order the parts; get an Airtel or Vi SIM | – | Team (+ me for the split) |
| P1 | 7–11 Nov | **Pi software for the LIVE model:** sensor drivers through the ADS1115s; fail-safe and fingerprint rules ported from the ESP32 engine; beacon, pump, SMS; full-screen dashboard on a small HDMI screen | Parts | Me (on request) + team test |
| P1 | 8–11 Nov | Build the LIVE-model **SLDASM** + exploded view + drawing; Pack and Go for the portal; SOLIDWORKS rebuild check of the 17 parts (when Vector is idle) | Plinth decision | Me (on request) |
| P1 | 11–13 Nov | Assembly, wet test with 4 samples, calibration (pH 4/7, TDS standard); record a demo video **with voice-over** | P1 software + parts | Team |
| P2 | 12–15 Nov | Finale deck **7:00**: R3 + LIVE + validation numbers + one cost figure + roadmap; Q&A update (Pi vs ESP32, accuracy, fouling, schematic) | Wet test | Me + team |
| P2 | by 15 Nov | **Fix the documentation credibility gaps:** draw a real KiCad schematic (or stop calling the comment file a schematic); resolve the rail polarity; one cost figure; current team in every outward document | – | Me (on request) |
| P3 | after the finale | ESP32 firmware: RTC driver, warm-up 30 s, modem driver with failure handling and backlog, PCA9685 beacon, servo, valve, carousel with index feedback; run the unit tests on a board; GPIO hold in sleep | Hardware | Team + me |
| P3 | after the finale | Fix F10 (dispersion), a real-data validation plan (ISO 15839 style), a clean SOLIDWORKS interference model, a GitHub update (with your approval to push) | – | |

---

## 10. Recommended next development phase

**"Make the demonstrator real, keep the R3 honest."** For the next 14 days, put every hour into these four things, in order:

1. **FDC post by 7 Nov**, because the banner depends on it.
2. **A LIVE model that works end to end:** read, decide, act, alert, with fail-safe and the four-sample fingerprint demo, running on a Pi with its own screen.
3. **CAD evidence of the prototype:** SLDASM, Pack and Go, drawing, and renders from the real assembly.
4. **A 7-minute pitch** that tells the R3 to LIVE story with measured numbers from the wet test.

Defer the deep R3 firmware work (modem, actuators, RTC) and the R4 innovations (UV254 organic channel, UV-C antifouling, CFD) until after 20 Nov, unless you reach the top 2. They are documented in report 19.

---

## 11. Approvals I need

I'll change nothing until you approve.

1. Download the official rules PDF from the portal (*Competition rules – AAKRUTI – 18032026.pdf*), so I can read Article 4 (judging criteria) in full. The portal viewer renders only page 1.
2. Request the Compass role or licence in the portal, once you've confirmed which one from the organisers' screenshot.
3. Start the Pi software for the LIVE model.
4. Build the LIVE-model SLDASM and Pack and Go as new files, after checking that Vector is idle.
5. Decide the plinth: H2D, or a CAD split as a new file.
6. Fix the KiCad file: draw a real schematic as a **new** file, and keep the comment file as "netlist notes".
