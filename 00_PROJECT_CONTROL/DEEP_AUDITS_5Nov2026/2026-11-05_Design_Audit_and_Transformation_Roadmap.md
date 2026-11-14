# AquaSentinel: design audit and transformation roadmap

**Prepared:** 5 Nov 2026, for Team Sanjivani Hero's Journey (AG26-1500$41), India Geo Finalist, AAKRUTI 2026.

**Ground rules:** this is a read-only audit. No existing file, CAD model or design was changed. Every proposal below needs your approval before anything is modified.

**Evidence labels.** These are used throughout so nothing is overclaimed:
- **[measured]**: tested or measured.
- **[calculated]**: from analysis or CAD.
- **[vendor]**: a manufacturer's claim.
- **[research]**: a paper or patent.
- **[assumption]**: not yet verified.

---

## 1. Ground truth: what the project is today

### 1.1 How the project evolved, reconstructed from the folder, mail, WhatsApp, the portal and our sessions

| Period | What happened | Status today |
|---|---|---|
| Apr–Oct | Registration, Product Introduction, IDC, then **FDC (5 Oct)** with the full-size **R3** design: a twin-hull float on a guide pole, ESP32, RS485 probes, LTE, 4-bottle autosampler, PV canopy | **Current full-size design** (CAD, analysis, cost model) |
| 18–25 Oct | Top 30, then the semi-final (25 Oct), then **India Top 10 Geo Finalist**. The semi-final promised "1:5 model in water + logic on an ESP32 with a real probe" | Promise only partly met; see 1.3 |
| 20–27 Oct | 1:5 R3 display model (float and stand) designed and printed | Superseded by the LIVE model, which reuses its parts |
| 28 Oct | The team's **real hardware** is confirmed: a Pi 3B+, hobby analog sensors (pH-4502C, TDS V1.0, SEN0189, DS18B20, DHT11, MQ-3, rain, LDR), SIM800L, a mini pump and MX1508 | Basis of the physical demonstrator |
| 28–30 Oct | Six alternative demo concepts: 11 station, 12 simple housing, 14 P1 float (rejected by you), 15 Sensor Tower and 16 Pi payload (you distrust both), and 17 R3 Pi-hardware fit (CAD only) | **All superseded.** Keep them as an archive and don't show them |
| 30 Oct–5 Nov | **1:5 LIVE sensor model** (designed with Vector): pier stand, float, real sensors in a 1:1 cage dipping into a Ø115 mm dish, Pi electronics in a plinth, met head, MQ-3 bottle, LED beacon | **The current physical prototype.** 31 of 37 parts printed; plinth (LD-S01) blocked; frame and column (PLATE_05) unconfirmed; assembly manual being generated on 5 Nov |
| 5 Nov | FDC banner pack (`18_FDC_UPDATE_7Nov`) | Waiting for your upload by 7 Nov |

### 1.2 The current design baseline: two things, no more

1. **R3, the full-size product.**
   - Twin rotomoulded HDPE hulls (1000 × 230 × 260 mm) on 40 × 40 aluminium SHS beams, riding a 2-inch Sch 40S SS316L guide pole clamped to a bridge pier.
   - 8 UHMW rollers carry it through 2 m of river level change, with no motor.
   - Sensor well with a lift-out cartridge: pH, EC, DO and turbidity RS485 probes, plus an optical wiper.
   - IP67 pod: ESP32, LTE, MPPT, 12.8 V 6 Ah LiFePO4. 20 W PV canopy. 4-bottle autosampler with a peristaltic pump. LED beacon. Ultrasonic river-level sensor.
   - Published figures:
     - 48.5 kg, freeboard 143 mm, reserve buoyancy 2.27× **[calculated]**
     - pole safety factor 2.66 in the static case **[calculated + FEA]**
     - about 12 days without sun **[calculated, preliminary]**
     - 4 of 4 synthetic spills detected **[synthetic data]**
     - ₹1,86,710 prototype (float plus bridge kit) **[estimate]**
2. **The 1:5 LIVE model, the physical demonstrator of the sensing chain.**
   - Real full-size sensors in a 1:1 cage on a 1:5 float.
   - Raspberry Pi electronics.
   - Not yet assembled, wired, programmed or wet-tested.

### 1.3 Gaps between promise and reality, which the jury may probe

| Claimed or promised | Reality today | Risk |
|---|---|---|
| "Logic on an ESP32 with a real probe" (semi-final) | Pi + hobby sensors; **no software yet** | High, if it's not explained first |
| "1:5 model in water" | The LIVE float sits at its low stop with the cage dipping into a dish; the float itself is not floating | Medium |
| One cost figure | Our own files differ: README ₹1.87 lakh ex-GST; an earlier note ₹2.19 lakh (probably including GST) | Medium: **pick one figure and state "ex-GST"** |
| Team | Portal and deck: Prasad ✓. FDC post and GitHub: Shriraj ✗ | Fixed by the 7 Nov pack and a later GitHub update |

### 1.4 Competition context that should drive priorities

- **Judging (rules Art. 4.1).**
  - Stage 2A covers CAD quality.
  - Stage 2B covers the pitch and business, including *"a study of the target market and estimation of cost for real-world application"* and *"raw materials, assembly plans, and manufacturability"*.
- **Finale format.**
  - 19 Nov: booth with a banner and **one display driven by the organisers' laptop. No personal laptops.**
  - 20 Nov: 7 min pitch plus 6–7 min Q&A.
  - Finale videos: **no background music**.
- **Tools you already have.**
  - The portal shows your SOLIDWORKS licence includes **Simulation (Structure, Flow, Plastics) and photorealistic rendering**.
  - **3DEXPERIENCE ENGINEER** and **VIRTUAL STORYTELLER** are requestable.
  - Flow Simulation (CFD) and Visualize are available now and unused.

---

## 2. Benchmark: where AquaSentinel stands globally

| Solution | What it is | Indicative cost | What it lacks that we have |
|---|---|---|---|
| YSI EXO2 sonde + EMM25 buoy | Industry-standard multiparameter sonde on a spar buoy | EXO2 $7,090–8,770 [vendor list]; buoy quote-only | No sample capture, no public warning, no stage-following mount; drifts or is moored |
| In-Situ Aqua TROLL 600 + Rugged Buoy + VuLink | Sonde, buoy and cellular telemetry | £3,540 + $2,695 + £845 [vendor list] ≈ ₹7–8 lakh | Same as above |
| CPCB RTWQMS (Ganga) | Shore-based stations | ₹25 lakh per station (2012 pilot); ≈ ₹84 lakh per station across the ₹94.45 crore, 113-station project [our arithmetic from public figures] | Fixed to the bank, costly, few sites (36 + 40 commissioned on the Ganga) |
| Academic low-cost nodes (GatorByte, Amrita LoRa buoys, Ganga buoy 2023, IIT-G R-SAM-PRO ₹12k) | Open or low-cost IoT sensing | < $1,000; ₹12k for R-SAM-PRO | No forensic sample, no flood-following, limited antifouling, rarely field-proven |
| Floodplain "float on a pole" stations (USA) and Cal Poly pole-guided platforms | Floats riding a pole through more than 10 ft of water-level change | – | Lake or floodplain use; no sampler or alerting chain |
| Chinese patents CN118150784A, CN102211650A, CN117446093B | Floating monitoring platforms with solar, probes and sample lift | – | **No patent found that combines a bridge pier, a guide pole, a stage-following float and an event-triggered sample.** This is a distinctiveness argument, not a freedom-to-operate opinion |

**Positioning.** AquaSentinel is not "another sonde". It is an **event-to-evidence system**:

- *watch* the river continuously;
- *decide* on board;
- *warn* the bank (beacon) and the authority (SMS or LTE);
- *preserve evidence*: a sealed sample taken during the event.

It costs about 1/3 to 1/4 of an imported sonde-buoy system and about 1/10 to 1/40 of a CPCB-class station. That is the story to own. The weaknesses below are where a strong jury will push.

---

## 3. Critical audit

Each finding is graded by severity: 🔴 must fix or address, 🟠 significant, 🟡 improvement.

### 3.1 Architecture and function

- 🔴 **A1. It cannot see organic pollution.**
  - Sewage and most industrial discharges show up first as organic load (BOD, COD, TOC). R3 measures pH, EC, DO, turbidity and temperature only.
  - DO responds to organics only slowly and indirectly. EC misses organic-rich, low-salt discharges such as dairy, sugar and distillery wastes, which are exactly the 17-category and grossly polluting industries in Maharashtra.
  - **Proposal: add an optical "organic channel".**
    - **UV254 absorbance (SAC254)** is a recognised surrogate for TOC and COD. Research sensors read 254 nm (TOC) and 220 nm (nitrate) using LEDs and photodiodes [research: Kim et al. 2025; NPMS 2024].
    - Optionally add **tryptophan-like fluorescence**, a recognised marker for sewage.
    - Both are compact, low-cost and wiper-cleanable.
- 🔴 **A2. Detection stops at "something happened".**
  - The source attribution question is "*what kind of discharge, and is it ours to act on?*".
  - **Proposal: a pollution-source "fingerprint" engine.** Classify each event from the *pattern* across channels:
    - EC↑ pH↓ = acidic industrial;
    - EC↑ alone = saline or effluent;
    - turbidity↑ with EC flat = runoff or erosion;
    - UV254↑ + DO↓ = sewage or organic.
  - The precedent is a sewer-network system using multiparameter sensors and XGBoost, which verified 330 discharge events over 8 months [research/trade].
  - This upgrades the "4 of 4 spills detected" claim into "detected **and classified**", and it is demonstrable on the LIVE model with dish samples.
- 🟠 **A3. Biofouling is the classic killer of in-situ sensors.** Unprotected sensors can fail within 1–2 weeks [trade].
  - R3 relies on a single servo wiper with brushes. That is a moving part in silt-laden monsoon water.
  - **Proposal: layered antifouling.**
    1. Pulsed **UV-C LEDs** aimed at the optical windows. The IOW lens-focused UV-C system kept conductivity sensors within spec and free of fouling for **237 days** [research/patent]. WHOI also holds a patent on UV-C for optical surfaces.
    2. Copper-mesh probe guards (no biocide paint).
    3. Keep the wiper only for the turbidity and UV windows.
  - Avoid toxic antifouling paint, which is being phased out [trade]. Biomimetic micro-texture (Sharklet-type, about 85 % less spore settlement in marine tests [research]) is **not** recommended for now: there is no freshwater or 3D-print evidence.
- 🟠 **A4. The flood extreme is unresolved.**
  - At the top stop collar the float can be overtopped. Large debris can load the pole beyond the static case: SF 2.66 static, and dynamic impact is "still to verify".
  - **Proposals:**
    - a **breakaway fuse link** with a retrieval tether;
    - a **flood "dive" mode**, where the cartridge retracts and the pod is sealed;
    - a **CFD drag study** in Flow Simulation, which you already own, to replace the hand-calculated current load;
    - a dynamic debris-impact case (energy method).
- 🟠 **A5. Power under monsoon cloud.**
  - The 12-day autonomy assumes the ESP32 duty cycle. The Pi build would draw roughly 100 Wh/day always-on.
  - **Proposals:**
    - Keep the **ESP32 as the field controller**; the Pi is a demo and gateway only. Say this explicitly.
    - Add an optional **micro-hydrokinetic trickle charger**, a 0.2–0.7 W river-flow generator [research]. Monsoon is when sun is lowest and current is highest, so the two sources complement each other.
- 🟡 **A6. Level sensing is ultrasonic.**
  - The float already *is* a level gauge, because it rides the pole. A **magnetic or draw-wire encoder** on the carriage gives stage for nearly free and removes a sensor.

### 3.2 Mechanical, structure, DFMA

- 🟠 **M1. Rotomoulded hulls need a mould.** That is a high fixed cost and a long lead time. For units 1 to 10:
  - use **fabricated HDPE sheet hulls**, which are hot-gas welded and foam-filled;
  - or use **commercial modular HDPE pontoon floats** as a stopgap.
  - Rotomould only at about 100 units or more. Show this staging in the manufacturing slide; it is exactly what rubric 2B asks for.
- 🟠 **M2. 66 part numbers with many weldments.** DFMA moves:
  - Combine the pier bracket upper and lower (already identical, good).
  - Replace welded carriage struts with **bolted aluminium extrusions**.
  - Standardise to **M6, M8 and M10 A4 stainless** with captive fasteners.
  - Make the cartridge **tool-less**: the quarter-turn exists, now add a keyed probe spider.
  - Target **−25 % part count** and a single tool size for field service.
- 🟡 **M3. Theft and vandalism at Indian bridges.** Add:
  - security fasteners and a hidden GPS tag;
  - a tamper alert (pod-lid switch);
  - a low-value-looking exterior with no exposed brand-new metal;
  - an engraved owner ID.
- 🟡 **M4. Corrosion and galvanic coupling.** SS316L pole + 6061 aluminium beams + A4 fasteners need **isolation washers** in the BOM.
- 🟡 **M5. Ergonomics, scored with NIOSH-style limits.**
  - The 48.5 kg float is a two-person carry: about 24 kg each, which is OK with 4 grab handles.
  - The cartridge is 3.95 kg: OK one-handed.
  - Specify a **service time target of 15 minutes per visit** and design for it.

### 3.3 Sensors, data quality, standards

- 🔴 **S1. No validation protocol yet.** A jury will ask how we know the readings are right. Adopt the structure of **ISO 15839** (performance tests for online water-quality sensors):
  - repeatability;
  - drift over 7 days;
  - response time T90;
  - interference;
  - field comparison against lab samples taken per ISO 5667.
  - For the finale, run a **mini bench version** on the LIVE model: pH 4/7 buffers, a TDS standard and a turbidity step, and show the numbers.
- 🟠 **S2. The four RS485 probes are 44 % of the float cost** (₹69k). Value engineering: **tiered sensor packs**.
  - **Sentinel Basic**: EC, temperature, turbidity, UV254, level. The low-cost optical channel catches most events.
  - **Sentinel Pro**: adds pH, DO and fluorescence.
  - This cuts the entry price, widens the market (village panchayats, CETPs) and keeps the hardware the same.
- 🟡 **S3. Hobby sensors in the LIVE model.** They're fine for a demo; say so plainly. The value is that the *decision chain* runs on real signals.

### 3.4 Human-centred design (stakeholders and their moments of truth)

| Stakeholder | Moment of truth | Gap | HCD move |
|---|---|---|---|
| PCB field officer | Gets an alert: "is it real, where do I go, is there evidence?" | The alert gives a number, not a decision | Alert = **class + confidence + sample ID + map pin + "sample sealed at 14:32"** |
| Water-works operator | "Do I close the intake?" | No lead-time estimate | Add **travel-time estimate to the intake** (distance ÷ velocity) |
| People at the ghat | "Is the water safe right now?" | Colour-only beacon; colour-blind users can't read it | **Colour + flash pattern**: steady = normal, slow pulse = caution, fast = stay out, plus a bilingual sign plate |
| Field technician | Monsoon visit, 20 minutes on a bridge | Tools and screws | Tool-less cartridge, colour-keyed probes (exist), QR-coded parts, a 1-page service card |
| Lab analyst | Chain of custody | Not formalised | Tamper-seal ID on bottle and cap; the logged event links to the bottle QR |

### 3.5 Sustainability and responsible design

- **No biocides.** UV-C and copper mesh instead.
- **Recyclable mono-material hulls** (HDPE). LiFePO4 rather than lead-acid. Repairable modules.
- **End-of-life take-back** in the service contract. A design-for-disassembly part map.
- **Carbon/benefit framing:** one float replaces repeated manual sampling trips. Quantify the km driven per month avoided **[assumption: needs a survey]**.

### 3.6 Technology readiness (be honest, and use it as a strength)

| Subsystem | TRL now | Evidence | Next gate |
|---|---|---|---|
| Guide-pole float mechanics | 3–4 | CAD, hydrostatics, FEA; printed 1:5 kinematics | 1:5 float in a tank, then full-size hull in a tank |
| Sensing chain (decide/act) | 3 → **4 by the finale** if the LIVE model runs | Synthetic-data detector | LIVE wet test with 4 samples |
| Autosampler | 3 | CAD | Bench peristaltic test |
| Antifouling (UV-C) | 2 | Literature | Bench coupon test |
| Organic optical channel (UV254) | 2 | Literature | Breadboard with standards |

---

## 4. The 1:5 LIVE model: specific engineering review and fixes

This is the prototype the jury will touch. Fix these first.

| # | Finding | Evidence | Fix | Effort |
|---|---|---|---|---|
| L1 | 🔴 Plinth LD-S01 (300 × 200) not printable on a P1S or A1 | PRINT_STATUS: BLOCKED | Print on the H2D if available, **or** split into two pieces with pins and glue (a CAD change; needs your OK) | 1 h CAD + ~10 h print |
| L2 | 🔴 Deck frame F03 and column not confirmed | PLATE_05 still "LOADED" | Print or confirm PLATE_05 (5 h 14 min) | 5 h |
| L3 | 🔴 Cage sizes printed from **assumed** sensor dimensions | Design notes: "measure before printing" | **Test-fit every real sensor now**; reprint the cage plate if needed (~3.5 h) | 1 h test |
| L4 | 🔴 Water only 1.5 mm over the cage plate; a 50 mL sample drops the level 5.4 mm, leaving the pump with 2.6 mm of submergence | Section sheet 08 | Take samples from a **separate cup**, or use a deeper dish, or lower the cage 5 mm | Process change: 0 h |
| L5 | 🟠 Turbidity reads open IR in a glass dish under exhibition lights | SEN0189 is an open optical fork | An opaque sleeve round the dish, or a dark dish; calibrate at the booth | 1 h |
| L6 | 🟠 No SOLIDWORKS **assembly** of the LIVE model (parts only); the generator script is in the Recycle Bin | Folder 05 listing; cleanup log | Build `LIVE-00.SLDASM` with mates, an exploded view, one drawing sheet and a motion study of the float lifting to park. This scores on CAD criteria. Restore the generator from the Recycle Bin if parameters change | 3–4 h |
| L7 | 🟠 Booth rule: no personal laptop | WhatsApp, 2 Nov | Put a **small HDMI screen (5–7")** on the Pi with a full-screen dashboard; confirm with Shubham | 2 h + purchase |
| L8 | 🟠 All parts are white | Print log | Apply the kit colour scheme: yellow hulls, grey column, dark plinth, blue cage. Paint or reprint the highly visible parts | 3–5 h |
| L9 | 🟡 Cable routing through the 1:5 well (5 cables plus LED wires) is untested | Not modelled | Dry-fit with the real cables; add a spiral wrap and a 70 mm service loop | 1 h |
| L10 | 🟡 The float can rotate ±7° and touch the dish | Design notes | Glue the deflector to the well (as the notes say); mark the "square" position | 0.5 h |

**The demo that wins the booth, about 90 s, all achievable in 14 days with the parts you have:**

1. Clean water: beacon green, screen "NORMAL".
2. Salty water (industrial-like): EC↑, beacon red, **"Class: saline / industrial (EC↑, pH ~)"**; the pump fills the bottle.
3. Vinegar (acidic discharge): pH↓, **"Class: acidic"**.
4. Muddy water (runoff): turbidity↑ with EC flat, **"Class: runoff / erosion"**.
5. Sanitiser drop in the sample bottle: the MQ-3 rises, **"Solvent vapour detected in sample"**.
6. Unplug a probe: **"SENSOR FAULT"**, never green. This is the fail-safe.

This turns hobby sensors into a visible **source-fingerprinting** capability, the strongest innovation story available before 20 Nov.

---

## 5. Breakthrough options, ranked by value against feasibility

| Rank | Idea | Value | Feasible by 20 Nov? | How to show it |
|---|---|---|---|---|
| 1 | **Source-fingerprint classification** (rule-based now, ML later) | Very high: answers "so what?" | ✅ in software on the LIVE model | Live demo + 1 slide |
| 2 | **Organic channel: UV254 (+ optional tryptophan)** | Very high: closes the biggest sensing gap | ⚠ concept + CAD only; breadboard after the finale | R4 cartridge render + research citation |
| 3 | **Layered antifouling: UV-C + copper mesh** | High: long-life credibility | ⚠ concept + CAD | Cartridge cut-away render |
| 4 | **Event-to-evidence chain** (sample ID, seal, QR, alert with class) | High: unique versus all benchmarks | ✅ software + label mock-up | Alert screenshot + bottle label |
| 5 | **Tiered sensor packs (Basic/Pro)** | High: business 2B | ✅ slide | Pricing table |
| 6 | **CFD current and debris load** (Flow Simulation) | Medium-high: CAD 2A | ✅ 1 day | Velocity-plot image + updated SF |
| 7 | **Hydrokinetic trickle charge** | Medium: monsoon resilience | ⚠ concept | Render + energy note |
| 8 | **Encoder stage sensing** replacing the ultrasonic | Medium: cost and robustness | ⚠ concept | 1 line in the R4 spec |
| 9 | **Fabricated-HDPE to rotomould staging** | Medium: manufacturability 2B | ✅ slide | Manufacturing roadmap |
| 10 | Biomimetic micro-texture antifouling | Low now (no freshwater evidence) | ❌ | Mention only as future research |

**R4 concept, to present as the "next iteration, designed, not built".** It is the R3 platform, plus:

- the optical organic module;
- UV-C antifouling;
- the fingerprint engine;
- the encoder stage;
- fabricated hulls for the pilot batch;
- tiered packs.

Keep R3 as the fully calculated baseline. R4 is clearly labelled as a concept.

---

## 6. Transformation roadmap (prioritised and dated)

### Phase 0, by 7 Nov: lock the banner

- Upload the `18_FDC_UPDATE_7Nov` pack to the FDC post. *Owner: team.*
- Ask Shubham three things: the required role screenshot, whether a Pi with its own screen is allowed at the booth, and the format and deadline for files on their laptop.

### Phase 1, 7–12 Nov: make it work (gate: wet test passes)

- Print L1 and L2. Test-fit sensors (L3). Buy:
  - ADS1115 ×2
  - a 4 V buck converter rated for 2 A + a 1000 µF capacitor
  - a 5–7" HDMI screen
  - an Airtel or Vi SIM
  - Ø12 × 310 mm rod, a dish, the bottle and hose
  - pH 4/7 buffers and a TDS standard
- Pi software: sensor drivers, the fail-safe state machine, the fingerprint rules, beacon, pump, SMS and a full-screen dashboard. **I can write this on request.**
- Start the MQ-3 burn-in on day 1 (24–48 h).
- **Gate (12 Nov):** all 6 demo steps work three times in a row; pH within ±0.2 of the buffers; TDS within ±10 % of the standard **[targets to verify]**.

### Phase 2, 10–15 Nov: make it compelling (CAD and story)

- `LIVE-00.SLDASM` with mates, an exploded view, a drawing and a motion study (L6).
- CFD current-load study on R3 in Flow Simulation: one plot and an updated pole safety factor.
- R4 concept renders: optical module, UV-C, encoder. Clearly labelled "concept".
- Finale deck, **7:00 min**:
  1. Problem (CPCB: 296 polluted stretches).
  2. The event-to-evidence idea.
  3. R3 design, with the CAD depth.
  4. LIVE demo, with a video fallback.
  5. Validation numbers from the gate.
  6. Business: tiered packs, a cost line ex-GST, the OCEMS context.
  7. R4 roadmap.
  8. Team and ask.
- Voice-over versions of the videos, **no music**.
- Q&A bank: add "why the Pi and not the ESP32", "how do you know the readings are right" (the ISO 15839-style bench), "fouling", "theft", "cost versus a CPCB station", "patents".

### Phase 3, 16–20 Nov: perform

- Two full rehearsals with the live demo and a timed Q&A.
- Files on USB for the organisers' laptop.
- Pack the booth kit: model, Pi + screen, spare SD, 4 water samples, buffers, towels, tools, spare small printed parts, a printed A4 one-pager.

### Phase 4, Dec 2026–Feb 2027: if in the top 2, the international version

- 1:5 float in a real tank: flotation and trim versus the calculation (**[measured]**, closes a semi-final promise).
- Full-size cartridge bench: UV254 breadboard with standards; UV-C coupon test (4 weeks); ISO 15839-structured drift and response tests.
- DFMA pass: −25 % part count, a single tool size, fabricated-hull drawings, a costed BOM v3.
- Prior-art search (Google Patents / CNIPA, using the three CN patents as a seed). Decide on a provisional patent filing in India for the "guide-pole stage-following float + event-triggered evidence sample" combination **[needs a patent attorney]**.
- Approach MPCB for a supervised pilot site and line up a lab partner (NABL).

### Phase 5, 2027: pilot and product

- A 30-day Kopargaon (Godavari) pilot with lab cross-checks, then the service model with a PCB, a municipality or a CETP.

---

## 7. Decisions needed from you

I'll change nothing until you approve.

1. **The H2D, or split the plinth?** If split, I make the CAD change in a new file and keep the original.
2. **Build the LIVE model SOLIDWORKS assembly** (a new file; parts untouched)?
3. **Write the Pi software** with the fingerprint demo and an on-device screen?
4. **R4 concept renders and a CFD study** for the deck?
5. **Which cost figure is official** (₹1.87 lakh ex-GST?), so every document matches.
6. **Restore the generator script** `build_live_model_sw.py` from the Recycle Bin into folder 05?

---

## Sources

- YSI EMM25 buoy and EXO sondes: https://ysi.com/emm25, https://www.ysi.com/products/multiparameter-sondes
- In-Situ buoys, Aqua TROLL and VuLink price lists: https://in-situ.com/us/products, https://in-situ.com/uk/products/
- CPCB Ganga water-quality monitoring overview: https://cpcb.nic.in/ngrba/WQM_overvew.php
- CSE on CPCB real-time water-quality monitoring (station cost): https://www.cseindia.org/cpcbs-real-time-water-quality-monitoring--4587
- Infrastructure Today on the 113-station network: https://infrastructuretoday.co.in/automatic-water-quality-monitoring-on-ganga/
- UV-C LED antifouling: https://www.laserfocusworld.com/articles/print/volume-52/issue-07/features/photonic-frontiers-leds-uvc-leds-reduce-marine-biofouling.html, WHOI https://techtransfer.whoi.edu/uv-anti-fouling, IOW patent https://www.iow.de/short-news-archive-details/items/iow-gets-a-patent-for-its-innovative-anti-fouling-system.html, Marine Technology News https://www.marinetechnologynews.com/news/biofouling-control-marine-instruments-529539
- UV254 for TOC and nitrate in river water (Kim et al. 2025): https://mdpi-res.com/d_attachment/water/water-17-03586/article_deploy/water-17-03586.pdf
- Low-cost UV nitrate system (Sensors 2024): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11359284/
- ISO 15839:2003, on-line water-quality sensors, specifications and performance tests: https://www.iso.org/standard/28740.html
- Discharge detection with multiparameter sensors and ML: https://smartwatermagazine.com/news/xylem-vue/real-time-eyes-sewer-inference-continuous-evidence; source localisation https://pmc.ncbi.nlm.nih.gov/articles/PMC8156765; SCCWRP illicit-discharge sensors https://ftp.sccwrp.org/pub/download/PRESENTATIONS/Commission_Meetings/26_03.06/DischargeSensors.pdf
- Guide-pole floating stations: https://fondriest.com/news/floodplain-restoration-water-quality.htm, https://marine.calpoly.edu/slosea/image-gallery; YSI platform guide https://www.ysi.com/ysi-blog/water-blogged-blog/2013/03/setting-up-floating-platforms-for-continuous-lake-monitoring
- Patents: CN118150784A https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_epo_espacenet_CN118150784A, CN102211650A https://eureka.patsnap.com/patent-CN102211650A, CN117446093B https://eureka.patsnap.com/patent/CN117446093B
- Low-cost Indian and open nodes: Amrita https://www.amrita.edu/school/sustainable-futures/academics/live-in-labs/thematic-area/water-security-climate-resilience-community-water-governance/, IIT-G R-SAM-PRO https://techovedas.com/iit-guwahati-develops-a-groundbreaking-solution-for-low-cost-iot-water-quality-monitor/, Ganga buoy https://ouci.dntb.gov.ua/works/4Kw0Meg4, GatorByte https://data.mendeley.com/datasets/y2gc2fwj5b
- Libelium Smart Water: https://libelium.com/?p=12708; low-cost probe study (Water 2024) https://www.mdpi.com/2073-4441/16/12/1708; multiparameter freshwater system https://arxiv.org/pdf/2307.11630
- Biomimetic antifouling (marine evidence only): https://pmc.ncbi.nlm.nih.gov/articles/PMC4890670, https://www.jstage.jst.go.jp/article/trol/16/1/16_70/_article
- OCEMS and grossly polluting industries: CPCB common protocol https://www.cpcb.nic.in/upload/thrust-area/Common_Protocol_final-13.03.2018.pdf; Rajya Sabha reply 2023 https://rsdebate.nic.in/bitstream/123456789/744864/1/PQ_262_14122023_U1318_p138_p140.pdf; CAG audit https://cag.gov.in/webroot/uploads/download_audit_report/2022/Chapter5-0632d8a52c09035.58405028.pdf
- Hydrokinetic micro-generator for sensor nodes: https://www.bib.irb.hr/715361; hydrokinetic USV charging https://www.osti.gov/servlets/purl/2434098
