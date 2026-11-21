# AquaSentinel — the complete skill set for this project

Written 15 November 2026. Paste this whole file into a new Claude conversation (after, or instead of, `_ai_working_notes/PROMPT_MASTER_FABLE_5.2.md` when the task is about *capability*, not identity). It lists every skill the project actually needs, what each one produces, which files it touches, and what "done" means. Nothing here is decoration: every line maps to a real deliverable in this workspace.

One sentence for the top of the chat: *"You support a student hardware team four days before a national final; the skill map below is the whole job. Do not invent skills, and do not skip one because it is small."*

---

## 1. Competition and compliance

**What it is:** knowing the AAKRUTI rules better than the judges expect — submission formats, naming, deadlines, what may and may not change after evaluation.

- Task-title convention (`AAKRUTI_AG26-1500$41_Sanjivani Hero's Journey`), team ID `AG26-1500$41`, theme Robotics.
- FDC evaluated 5 October 2026; Part 2 of the public page is frozen and may only be explained, never rewritten.
- Team change (Prasad Ugale replaced Shriraj Kamble, approved 22 Oct) must be stated wherever the old team appears.
- Deadline discipline: booth 19 Nov, pitch 20 Nov, DS Campus Pune; top 2 go to Nashville.

**Touches:** `09_SUBMISSIONS_AND_CERTIFICATES/` (every stage), `01_FINALE_PRESENTATION/_SUBMISSION_RECORD_7Nov2026/`, `00_PROJECT_CONTROL/FDC_REVIEW_2026-11-15.md`.
**Done means:** every public artefact shows the right title, the right team, and nothing claims the October submission was altered.

## 2. Water-quality science (the instrument must be believable)

**What it is:** the chemistry and physics behind each number the float reports.

- pH: glass electrode, buffer calibration at 4.0 / 7.0 / 9.2, Nernst slope (≈59 mV/pH ideal, ours reads ≈38 mV), why raw voltage is meaningless until calibrated, probe storage (bulb wet, cap off).
- TDS: conductivity→ppm conversion, temperature compensation, why the Nano powers the TDS board only while reading (pH interference).
- Turbidity: NTU vs raw voltage, the module's blue trimmer, why soil reads "cloudy, salts flat".
- MQ-3: heater warm-up (90 s guard vs 3-minute reality), vapour vs immersion, why sanitiser is detected above the bottle.
- DS18B20 (water), DHT11 (air): one-wire vs single-bus, 4.7 k pull-up.
- Decision rules: hard limits (pH <6 or >9, TDS >1,400 ppm), learned baseline, 2-of-3 confirmation, SENSOR FAULT never NORMAL.
- CPCB framing: 296 polluted river stretches, 54 of them in Maharashtra — the most of any state (deck slide 4). Quote it that way; it is not a count of unmonitored stretches.

**Touches:** `14_RASPBERRY_PI_SOFTWARE/aquasentinel/aquasentinel/brain.py`, `tools/calibrate_ph.py`, `config.json`, electronics manual §sensors, deck slides on sensing.
**Done means:** the team can answer "how do you know that number is real?" at three levels: raw signal, calibration, and standard.

## 3. Analogue and power electronics

**What it is:** making seven cheap sensors behave on one board without lying to each other.

- Power architecture: 5 V AUX on J12 → step-up 9.0 V (J14, pH board) → step-down 4.0 V max (J16, SIM800L). Never >5 V into J12; never >4.2 V into the SIM.
- Multimeter discipline: measure every rail before plugging a load; write the number down.
- Interference: pH high-impedance output, 4.7 k series, TDS board switched by a Nano pin, ADS1115 in the October bay vs direct ADC now.
- Connectors: J1–J18 map, which pin is which, what must stay empty (RST, rain pocket).
- Beacon: common anode vs cathode, 220 R on board, red/green/blue wiring to D7/D8/D9; pump via Mini L298N, 10 k pull-down.

**Touches:** `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1/PCB_v1.2_BUILD_AND_PINOUT.md`, `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1/guide/picture_guides/`, wiring cards in `14_RASPBERRY_PI_SOFTWARE/`.
**Done means:** `tools/check_hardware.py` prints OK on every line, twice in a row, with the numbers recorded.

## 4. PCB design, milling and soldering

**What it is:** the Sensor Hub v1.2 exists because a breadboard cannot go in a 1:5 model.

- KiCad schematic → single-sided 104×72 mm layout → DRC clean.
- Isolation milling on a CNC: G-code generation, board hold-down, Windows blocking the sender (why we wrote our own), re-mill after a bad cut (`PCB_MILL_AGAIN_step_by_step.pdf`).
- Soldering order: lowest profile first, headers last; continuity beep test before power; power-up sequence card.
- Through-hole and SMD joints that survive a booth day.

**Touches:** `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1/design`, `guide/`, `PCB_MILL_AGAIN_step_by_step.pdf`, `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1/guide/picture_guides/`.
**Done means:** the board on the table is the one in the photos, every joint tested, and the story of the second mill is accurate.

## 5. Embedded firmware (Arduino Nano)

**What it is:** one `.ino` that samples seven sensors, drives three outputs and speaks JSON to the Pi.

- `#define BOARD_PCB 1` pin map vs breadboard map; change the one define, not the code.
- Libraries: OneWire, DallasTemperature, Adafruit DHT; board = Nano, ATmega328P **Old Bootloader**.
- Protocol: one JSON line per second at 115200; commands `LED G/R/B/Y/W/F/O`, `PUMP n` (≤30 s), `PING`.
- Loop hygiene: no `delay()` in the sampling path; uptime counter the Pi uses for the MQ-3 guard.
- Upload failure triage: wrong bootloader, wrong port, CH340 driver.

**Touches:** `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1/firmware/aquasentinel_nano/aquasentinel_nano.ino`, electronics manual §firmware.
**Done means:** the Nano answers `PING`, the Pi logs one row per second, and pulling the cable produces SENSOR FAULT then recovery.

## 6. Raspberry Pi systems

**What it is:** the Pi must boot, listen, decide and show — with no keyboard at the booth.

- Raspberry Pi OS Desktop on a 3B+; Python 3, `python3-serial`, Chromium, `unclutter`.
- UART for the SIM800L: pins 8 (GPIO14 TXD) and 10 (GPIO15 RXD), `raspi-config do_serial_cons 1` + `do_serial_hw 0`, `enable_uart=1`, `dtoverlay=disable-bt`, `dialout` group, `/dev/serial0`.
- systemd: unit file, `Restart=always`, start on boot, `journalctl` triage.
- Kiosk: autostart `.desktop`, labwc autostart on new images, `Alt+F4` to escape.
- USB reality: four ports on one hub, no per-port switch; a weak 5 V supply drops ports first — check the adapter before blaming software.

**Touches:** `14_RASPBERRY_PI_SOFTWARE/aquasentinel/install.sh`, `kiosk/start-kiosk.sh`, `PI_SETUP_AND_OPERATION.md`.
**Done means:** cold boot → dashboard full-screen in under 60 s, service survives a reboot loop, SIM pill green.

## 7. Python application engineering

**What it is:** the decision engine, the dashboard, the log — small, readable, arguable.

- Package layout: `nano.py` (serial link), `brain.py` (rules), `sms.py`, `web.py`, `core.py`, `settings.py`, `simulator.py`.
- Config-driven behaviour: `config.json` is the only place numbers live (`sms_numbers`, limits, `mq3_warmup_s`, calibration).
- Logging: one CSV per day, header once, ISO timestamps, no gaps on restart.
- Testing: `self_test.py` proves logic on simulated data (7 checks); `check_hardware.py` proves wiring; `--simulate` runs without hardware.
- Web: dashboard on :8080, `/api/state`, `/api/csv`, buttons for beacon, sample, test SMS, learn-new-water.

**Touches:** `14_RASPBERRY_PI_SOFTWARE/aquasentinel/aquasentinel/*.py`, `web/`.
**Done means:** 141 lines of rules a judge can read; every failure mode shows as a state, never as a silent zero.

## 8. Telecom and SMS

**What it is:** a 2G module that must actually deliver one message at the booth.

- SIM800L: 4.0 V rail, 2 A supply, spring antenna, RST empty, micro-SIM from Airtel/Vi/BSNL (not Jio — no 2G).
- AT layer: `AT`, `AT+CSQ` (10+ good), `AT+CREG?`, `AT+CMGS`, text-mode SMS, PDU fallback.
- Readiness: LED 1 s blink = searching, 3 s = registered; dashboard pill shows operator, not "searching".
- Operational: SMS balance, +91 formatting, cooldown of 10 min between alerts, test button vs real event.

**Touches:** `sms.py`, wiring cards `SIM800L_wiring_diagram.png`, `D11_SIM800L_on_J17.png`, `D12_J18_to_Raspberry_Pi.png`.
**Done means:** a real phone buzzes from the test button and from a real event, with a photo of the message kept.

## 9. Mechanical CAD (SOLIDWORKS)

**What it is:** two models — the full-size R3 concept and the 1:5 live model that must actually assemble.

- Part modelling to print tolerances; assemblies with mates that reflect reality (float on pole, cage on plinth, dish under probes).
- Interference detection *before* printing (it caught the pole through the electronics pod and the 48.5 vs 25.4 kg mass error).
- Pack and Go discipline: every part, material, part number, one zip that opens on a judge's machine.
- Drawings: AS-LIVE sheets, section views, BOM tables, revision notes.
- Honesty: the 66 R3 parts are imported bodies assembled and simulated in SOLIDWORKS — say it that way.

**Touches:** `02_LIVE_MODEL_1to5/05_SOLIDWORKS_ASSEMBLY/`, `05_R3_FULL_SIZE_CAD/03_SOLIDWORKS_2026_assembly_for_manual/`, `01_BOM_R3.csv`.
**Done means:** a dry fit with every printed part present, and the CAD someone else opens matches the object on the table.

## 10. Simulation / FEA

**What it is:** two static studies that support the design without overclaiming.

- Linear static setup: fixtures that match the clamp reality, mesh independence, 316L properties (yield 170 MPa).
- Results: pole safety factor 2.66, peak von Mises 38.3 MPa, bracket study, displacement plots.
- Language: "design-stage estimate, not a test"; flood above 2 m is a known open case.
- Report hygiene: the DOCX exports print `1.255e+07 am` and `<Model_Name/>` tokens — never print them raw; rebuild clean pages.

**Touches:** `06_SIMULATION/`, `05_R3_FULL_SIZE_CAD/05_Design_Checks/`, deck slide on structure.
**Done means:** one A4/A3 results sheet a judge can read in 20 seconds, and no number on it that the team cannot defend.

## 11. Additive manufacturing (FDM)

**What it is:** 38 STL files that become a model that holds water and survives a booth.

- Orientation per part, supports where they can be removed, wall counts for screw bosses, clearance for fits (printed hole ≠ CAD hole).
- Material choice for wet parts (PETG over PLA where it matters), gasket/seal strategy for the dish.
- Print list discipline: `PARTS_LIST.csv` (37 listed + LD-S16 variant), file naming, spares for the parts most likely to snap.
- Post-processing: reaming holes, sanding mating faces, test-fit before the model day.

**Touches:** `02_LIVE_MODEL_1to5/01_FINAL_STL/`, `04_DESIGN_NOTES/`, `07_PRINTED_DISH_LD-S17/`.
**Done means:** the dish holds water with the cage lowered, all four probes wet, nothing leaks toward the plinth.

## 12. Technical writing and documentation

**What it is:** manuals that a judge — or a tired teammate at 1 a.m. — can follow without asking.

- Structure: numbered steps, one action per step, a picture per action, warnings before hazards, checkpoints ("you should see…").
- Two manuals exist: 1:5 assembly (30 pages, 24 steps) and electronics Rev 2.0 (17 pages); a one-page addendum carries the 15 Nov changes.
- Register: instruction, not marketing. No adjective does a noun's work.
- Versioning: status page (`00_MANUAL_STATUS_READ_FIRST.md`) explains which page is current and what changed.

**Touches:** `02_LIVE_MODEL_1to5/00_ASSEMBLY_MANUAL/`, `12_ELECTRONICS_MANUAL_1to5/`, `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1/guide/picture_guides/`.
**Done means:** someone who has never seen the project can wire J1–J18 and assemble the float using only the PDF.

## 13. Cost engineering and business modelling

**What it is:** ₹47,886 ex-GST per unit at 100 units (≈₹56,505 with GST), ₹64,616 prototype — defendable line by line.

- BOM costing from supplier listings, ex-GST vs landed, quantity breaks, value engineering (what was removed and why: wiper, rain sensor, carousel, ultrasonic level).
- Benchmarking: ₹35–40 lakh real-time stations → 73–84 units; ₹8,000/month service proposal with installation, monthly visit, alerts, four lab samples.
- Payback arithmetic stated honestly ("about twelve months, after monthly service"), and the caveat that galvanised steel is assumed while CAD still shows 316L.
- Never quote the 23 Oct research workbook; quote the value-engineered PDF.

**Touches:** `07_COST_AND_BUSINESS/04_AquaSentinel_Cost_48k_Value_Engineered.pdf`, `_superseded_DO_NOT_QUOTE/2026-10-23_Costed_BOM_ESP32_industrial_design.xlsx`, deck cost slide.
**Done means:** every rupee on the slide is traceable to a line, and the estimate-vs-quote distinction is spoken aloud.

## 14. Pitch craft (7 minutes + Q&A)

**What it is:** a 28-slide deck that survives contact with judges and a clock.

- Narrative order: river problem → what exists today → our object → evidence → cost → what is not proven → ask.
- Timing: slide-by-slide budget, speaker split across the team, rehearsed with a visible timer.
- Q&A traps prepared: "why not commercial sensors?", "what happens in a flood?", "who pays?", "is it calibrated?", "has it been in the river?" — answer with the proven/not-proven table.
- Rule: never overclaim; "not yet proven" is a stronger answer than a guess.

**Touches:** `01_FINALE_PRESENTATION/AquaSentinel_Finale_7min.pptx`, `_SUBMISSION_RECORD_7Nov2026/00_TODAY_7Nov_Submission_and_Messages.md`, `PROJECT_IDENTIFICATION_AND_CRITICAL_PATH_2026-11-14.md` §Q&A.
**Done means:** a full run at 6:40–6:55, every speaker knows their handover word, and no slide contradicts the pre-flight sheet.

## 15. Presentation production

**What it is:** building and auditing the deck as a designed object, not a pile of slides.

- Layout system: one accent colour, one type scale, consistent margins; diagrams drawn, not screenshotted.
- Slide QA each pass: 7 sensors (not 8), no rain sensor anywhere, status language matches bench truth, 15 Nov corrections applied.
- Export discipline: fonts embedded/checked, images at final resolution, PDF for backup, file on a USB stick.
- Editing without breaking: change content in place, keep the deck's visual grammar.

**Touches:** `01_FINALE_PRESENTATION/AquaSentinel_Finale_7min.pptx` (only current deck).
**Done means:** deck is re-read against `00_START_HERE.md` and the pre-flight sheet the morning of the pitch, and nothing on it is untrue that evening.

## 16. Motion graphics and video

**What it is:** a 66 s story film, an 8 Nov pitch video (v3, the submitted one), journey cut, 60 s marketing cut.

- Storyboarding from CAD; knowing what CAD can and cannot show (no fake live footage).
- Tools: web renderer for the CAD story, ffmpeg for cuts/format, voice-over recording and levels; music **not** used in anything submitted (licensing unresolved).
- Distinguish "3D animation of our CAD" from real footage — always.

**Touches:** `08_VIDEOS/`, `13_CREATIVE_EXPERIENCE_STORYTELLING/04_story_video/`, `06_source_scripts/`.
**Done means:** booth loop plays unattended for hours, v3 is on the USB stick, and every caption is truthful about what the viewer is seeing.

## 17. Creative and public writing

**What it is:** the public FDC page must read like people, not a submission.

- Voice: first person plural, concrete objects before specifications, short sentences next to long ones, admit the seam.
- Banned words: innovative, seamless, leverage, cutting-edge, revolutionary, empowering, robust, holistic, synergy, next-generation, state-of-the-art, "not just X, it's Y".
- Structure: river opening → object → six waters → the board story → software → who it is for → cost → what still does not work → the two days → team → frozen Part 2 as a museum label.
- Tests: read aloud; cut any sentence that could sit on another team's page; end on uncertainty, not a promise.
- The three residual "machine tells": no names in the story, no remembered 13 Nov moment, even polish — only the team can supply the raw material.

**Touches:** live 3DEXPERIENCE post, `00_PROJECT_CONTROL/_ai_working_notes/PROMPT_HUMANISE_FDC.md`, `_ai_working_notes/PROMPT_MASTER_FABLE_5.2.md` §writing.
**Done means:** a judge who has read forty pages remembers this one's first line.

## 18. 3DEXPERIENCE platform and creative platforms

**What it is:** where the project lives publicly, and where the storytelling happens.

- Communities: `AAKRUTI Innovation Competition 2026 Community - For Students` → post `AAKRUTI_AG26-1500$41_Sanjivani Hero's Journey`; post editor, images, video embeds.
- ENOVIA Project Planning: 4 members, 7 tasks with owners/dates, Gantt — the bonus challenge entry.
- 3DEXCITE Creative Experience: "Creative Experience00011982" in soham k's space, R3 mid-water + sunset ambience; launch through the compass (Virtual Storyteller for Education), never 3DEXPERIENCE.exe directly (tenant OnPremise error).
- Publishing rule: nothing goes public without an explicit instruction in the same conversation.

**Touches:** `13_CREATIVE_EXPERIENCE_STORYTELLING/`, live post, `09_SUBMISSIONS_AND_CERTIFICATES/03_FDC_Update_7Nov2026/`.
**Done means:** the post opens on the booth laptop, the experience orbits smoothly, and the public page matches the build of that morning.

## 19. Print production

**What it is:** what goes on paper for the booth, at the right size, first time.

- Resolution math: dpi at final size, not file pixels; vector for frames, raster only for renders.
- Formats: A2 poster, A3 drawings (6 sheets), A4 labels/report/leave-behind, check sheet at 150 dpi A3.
- Print-shop instructions: 100% scale, no "fit to page", matte stock, addendum as page 2 of the manual.
- Do-not-print list: simulation DOCX exports with `1.255e+07 am` and `<Model_Name/>` tokens.
- Budget: ≈₹3,300–5,100 for the full pack.

**Touches:** `00_PROJECT_CONTROL/PRINT_PACK_2026-11-15.md`, `PRINT_READY/00_PRINT_LIST.txt`.
**Done means:** every sheet is legible from 1.5 m, nothing is cropped, and the pack is printed before 18 Nov.

## 20. Booth operations and demonstration

**What it is:** the 19th is a performance with hardware that can fail in public.

- Choreography: LEARNING 20 s → six waters table → red beacon → pump → SMS; reset to NORMAL between tests; MQ-3 90 s block after any restart.
- Failure playbook: sensor hub offline, SIM no answer, searching network, black screen, pH "calibrate" — each has a one-line fix.
- Evidence capture: one 60 s phone video, one take, salt → class → beacon → pump → SMS; dashboard photos in NORMAL and event; wired-board photo.
- Numbers to take home: pump volume in mL (deck says 250), spill-to-red seconds, real MQ-3 warm-up seconds.

**Touches:** `00_PROJECT_CONTROL/PREFLIGHT_CHECKLIST_2026-11-15.html`, `PI_SETUP_AND_OPERATION.md` §booth.
**Done means:** the run sheet is followed by someone who did not write it, and the video exists before the booth opens.

## 21. Project control, versioning and evidence

**What it is:** the workspace is the single source of truth; nothing is lost, nothing is repeated.

- Git for text and code (old backup tags removed 17 Nov; their commits are in `main`; old branch work is in `archive/…` tags on GitHub); OneDrive history is the only backup for videos/decks/CAD.
- Audits: file-by-file CSV, PNG verdicts, CAD verdicts; purge log and move log; pre-purge manifest of 4,266 files.
- Frozen records: submissions, audits, archive are never rewritten — correct active docs only.
- Naming and numbering: folder numbers are stable; gaps (03, 04, 10, 11) are deliberate.
- Sensitive data: credentials, config backups, app caches, bank/Aadhaar workbooks are out of scope, always.

**Touches:** `00_PROJECT_CONTROL/` (all), `99_ARCHIVE/`, `00_START_HERE.md`.
**Done means:** any file can be traced to why it exists and which version is current, in under a minute.

## 22. Team coordination and handover

**What it is:** five people, four days, one table.

- Role clarity: Soham (lead), Prasad (system design), Bhakti (electronics), Tanmay (software), Dr. Wakchaure (mentor, Director Projects).
- Who-did-what sentences for the public page — the audit's biggest remaining gap; only the team can write them.
- Handover: a new chat or a new person starts from `_ai_working_notes/PROMPT_MASTER_FABLE_5.2.md` + `00_START_HERE.md`, never from memory.
- Decision rights: routine edits proceed; publishing, deletions, and claims about the river need the lead's explicit word.

**Done means:** anyone can pick up any folder and know the next action without a meeting.

---

## The skill ladder in one table

| # | Skill | Produces | Proof it is real |
|---|---|---|---|
| 1 | Competition compliance | Correct titles, dates, frozen Part 2 | No mismatched artefact |
| 2 | Water-quality science | Defensible numbers | Calibrated pH, known standards |
| 3 | Analogue/power electronics | Stable rails, clean signals | Meter readings on the sheet |
| 4 | PCB milling/soldering | Sensor Hub v1.2 | Continuity + check_hardware OK |
| 5 | Nano firmware | JSON stream, actuators | PING + LED/PUMP tests |
| 6 | Pi systems | Boot-to-dashboard | Cold boot, service restart |
| 7 | Python engineering | Decision engine, log, UI | self_test 7/7, CSV rows |
| 8 | Telecom/SMS | One real message | Photo of the phone |
| 9 | Mechanical CAD | Two models that assemble | Dry fit |
| 10 | FEA | Two honest studies | Results sheet, 2.66 SF |
| 11 | 3D printing | 38 parts | Dish holds water |
| 12 | Technical writing | Two manuals | Stranger can follow |
| 13 | Cost engineering | ₹47,886/unit | Line-by-line PDF |
| 14 | Pitch craft | 7 minutes | Timed run |
| 15 | Presentation production | 28 slides | Re-read vs truth |
| 16 | Motion/video | Story + pitch films | Plays unattended |
| 17 | Creative writing | Public page voice | First line remembered |
| 18 | 3DEXPERIENCE | Live post, experience | Opens on booth laptop |
| 19 | Print production | Booth paper pack | Legible at 1.5 m |
| 20 | Booth operations | Live demo + evidence | 60 s video exists |
| 21 | Project control | Traceable workspace | Audit chain |
| 22 | Team coordination | Named ownership | Who-did-what sentences |

---

## What only the team can supply

No model — Claude, me, anyone — can invent these. They are the last gaps on the page and in the pack:

1. **Who did what** — three or four one-line facts (who soldered the board, who wrote the rules, who argued the rain sensor out).
2. **One remembered moment** from the 13 November bench day, in your own words, however rough.
3. **The three measured numbers**: pump volume in mL, spill-to-red seconds, real MQ-3 warm-up seconds.
4. **A retaken electronics photo** with the final board.
5. **One phone call** to a real user (pollution board / water works) if it can still happen.

Everything else on this list is already built or can be built from the workspace.

---

## Machine-side skills available in this workspace (for the AI, not the team)

| Capability | Used for |
|---|---|
| `pptx` engine | Deck edits page-by-page, layout QA, PDF export |
| `excel` engine | Costed BOM, audit CSVs, check sheets |
| `docx` engine | Manuals, leave-behind, reports |
| Image generation | Illustrative diagrams only, always labelled |
| Browser automation | Reading and (with permission) editing the live FDC post |
| Node REPL | Verifying files, counts, ffprobe, PDF page counts |
| Print layout | A2/A3/A4 packs at true scale |

Read this file with `00_START_HERE.md`: the map says which version is current, this file says what skill each job needs.
