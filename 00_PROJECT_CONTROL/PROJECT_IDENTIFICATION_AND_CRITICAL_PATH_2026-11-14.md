# AquaSentinel — Project Identification and Critical Path

| Field | Detail |
|---|---|
| **Prepared** | 14 November 2026 |
| **Team** | Sanjivani Hero's Journey · AG26-1500$41 · Sanjivani University, Kopargaon |
| **Competition** | AAKRUTI Innovation Competition 2026 · India Geo Finale · Robotics |
| **Booth** | 19 November 2026, arrive by 10:00 |
| **Pitch** | 20 November 2026, 09:00–16:30 · DS Campus, Pune |
| **Format** | 7-minute pitch + 6–7 minutes Q&A · 10 teams · top 2 go to the International Finale, 14–17 February 2027, Nashville |

**Scope of this audit:** read-only inspection of the current project folder, the recovered Claude/DeepSeek conversation history, the AAKRUTI emails, the 3DSwym community, and the public GitHub repository. No project file was modified. This report is a new file.

---

## 1. Bottom line

AquaSentinel is real. It is not a slide-deck concept: there is a 1:5 model built from the final STLs (the team reports all parts printed), a custom milled PCB, working Nano firmware, a Raspberry Pi decision engine, a 66-part full-size CAD package, a 28-slide finale deck, and a 17-page electronics manual written after the build changed.

The engineering is ahead of the paperwork. The biggest risk in the next five days is not the idea or the CAD. It is the gap between **what the public documents claim** and **what the hardware has actually proven** — plus one backup problem that could cost the team the deck itself.

Five things can hurt the booth:

1. **SMS is the headline feature, and it cannot send yet** because `sms_numbers` is empty.
2. **pH is not calibrated**, so the absolute pH limits are switched off; only a sudden change counts.
3. **The deck says “rain” and “8 sensors”; the real build is 7 sensors with no rain.** The electronics manual, the top-level README and the Nano firmware all say 7.
4. **The manual says “everything verified”, but the 13 Nov note says the SIM800L and the Pi link were not tested.** One of those is wrong, and a judge may ask.
5. **Git is not a backup of the things that matter.** `.git/info/exclude` deliberately excludes `00_*` through `07_*`, which includes the deck, the live-model STLs, the R3 CAD and the cost pack. The updated 14 Nov deck is outside git, on this laptop and OneDrive.

None of these is fatal. All are fixable before 19 November if they are fixed in the right order.

---

## 2. What AquaSentinel is

A solar-powered float rides a stainless/GI guide pole clamped to a bridge pier. It rises and falls with the river: no anchor, no motor, no riverbed work. Every 15 minutes it reads the water, decides on board without a cloud connection, and acts:

- **SENSE:** pH, dissolved solids (TDS), turbidity, water temperature; plus light, air temperature/humidity and vapour above the sample bottle.
- **DECIDE:** hard limits plus a learned baseline, with a confirmation rule, into six classes: `LEARNING`, `NORMAL`, `ACIDIC`, `INDUSTRIAL`, `RUNOFF`, `SOLVENT`, `SENSOR FAULT`. A failed sensor is reported as a fault, never as normal.
- **ACT:** red beacon for the bank, SMS to the water-works/board through a SIM800L, and a pump that bottles the water at the moment of the spill.

The one-sentence story used in the deck is accurate: **“It rides the river, names the spill, keeps the evidence.”**

The 1:5 LIVE model on the booth table runs the same sensors and the same decision rules, once per second instead of every 15 minutes.

---

## 3. The two builds in the folder

These are different objects and should never be mixed in a sentence.

| Aspect | 1:5 LIVE model | Full-size R3 |
|---|---|---|
| Purpose | Booth proof of the measurement-and-decision chain | Product design, FEA, drawings, cost |
| Status | Printed (team report); bench electronics tested 12–13 Nov; full model not floated or trial-assembled per the 5 Nov README | CAD and simulation only; no physical build |
| Structure | 37 assembly print files + 1 printable sample bottle = 38 STL files; 17 LD parts designed new in SOLIDWORKS | 66-part SOLIDWORKS assembly; 14 design checks; 6-sheet drawing set; Pack and Go + STEP |
| Sensors | 7 real modules: PH-4502C + E-201-C, DFRobot SEN0244 TDS, DFRobot SEN0189 turbidity, DS18B20, DHT11, LDR, MQ-3 | Same sensor set in the product design; dissolved oxygen, wiper and ultrasonic stage sensor were dropped |
| Controllers | Arduino Nano (ATmega328P) on the custom Sensor Hub PCB v1.2 (104 × 72 mm, single-sided, milled 12 Nov) + Raspberry Pi 3B+ | Raspberry Pi 3B+ as the product brain |
| Link | Nano sends one JSON line per second at 115200 over USB; Pi decides, logs CSV, serves dashboard on :8080, drives SIM800L on `/dev/serial0` at 9600 | Same architecture |
| Simulation | No FEA; CAD fit checks + bench test | Pole SF min 2.66; FEA 38.3 MPa; pinned 54.8; pinned + couple 64.0 vs 316L yield 170 MPa |
| Cost | Prototype ≈ ₹64,616 | ≈ ₹47,886 ex-GST at 100 units; ≈ ₹56,505 with GST; service ≈ ₹8,000/month; hardware payback ≈ 11.9 months |

**Important distinction for the pitch:** the R3 was imported into SOLIDWORKS, not natively designed there. The 17 LIVE-model parts were designed natively. The deck already says “assembled and simulated in SOLIDWORKS”, which is the honest wording. Keep it.

---

## 4. Current source of truth

| Source | What it is | Trust level |
|---|---|---|
| `C:\Users\dell\OneDrive\Desktop\AquaSentinel` (14 Nov state) | The current project folder | **Primary** |
| `12_ELECTRONICS_MANUAL_1to5/AquaSentinel_LIVE_1to5_Electronics_Assembly_Manual.pdf` (Rev 2.0, 17 pages) | Current electronics build: PCB v1.2 + Nano + Pi + SIM800L | **Primary for electronics** |
| `14_RASPBERRY_PI_SOFTWARE` | Current Pi code, config, install, self-test, calibration | **Primary for software** |
| `02_LIVE_MODEL_1to5/00_ASSEMBLY_MANUAL/AquaSentinel_LIVE_1to5_Assembly_Manual_SOLIDWORKS.pdf` (30 pages, 7 Nov) | Mechanical assembly manual | **Stale**: predates the 12–13 Nov electronics change and still includes the rain plate/LM393 |
| `05_R3_FULL_SIZE_CAD` + `06_SIMULATION` | R3 CAD, drawings, FEA | Current for the design that was submitted |
| `01_FINALE_PRESENTATION/AquaSentinel_Finale_7min.pptx` (44 MB, 14 Nov 20:34) | Finale deck | Current deck file, but some slides are stale on sensors/status |
| `09_SUBMISSIONS_AND_CERTIFICATES` | FDC records, certificates, portal evidence | Historical record; do not rewrite |
| `99_ARCHIVE` | Superseded material, including the old ADS1115/HAT electronics and old videos | Do not use for the booth |
| `https://github.com/soham0777/AquaSentinel` | Public repo and GitHub Pages site | **Older and divergent**; its README says “eight sensors” and includes rain |
| 3DSwym / AAKRUTI dashboard | Submission platform | The submitted record; task status not fully readable in the in-app browser |

**The local folder is the truth. The public GitHub is not.** The remote `main` is at `e44b7fa`; the local `main` is at `2a92c7c`, and the two histories have diverged 14 commits each way. Do not assume a push will be a fast-forward.

---

## 5. What is actually verified

This is the table to use when a judge asks “Have you built it?”

| Item | Status | Evidence / caveat |
|---|---|---|
| 7 sensors read by the Nano | **Bench-proven 12–13 Nov** | Electronics manual p.2 and the bench-check section (pp.13–15); Nano firmware reads D2–D6, D8–D12, A0–A3, A6 |
| RGB beacon + pump driven by the Nano | **Bench-proven 12–13 Nov** | Electronics manual p.2; firmware commands `LED`, `PUMP`, `PING` |
| TDS power sequencing | **Implemented** | A0 powers the TDS board for 600 ms, reads A1, then powers it down for 300 ms |
| Pi decision engine | **Code complete; self-test ALL PASS** | `tools/self_test.py` passes clean→NORMAL, salty→INDUSTRIAL, vinegar→ACIDIC, muddy→RUNOFF, sanitiser→SOLVENT, unplugged→SENSOR FAULT. This is a **simulator/data test**, not a hardware test |
| Pi ↔ Nano USB link | **Unverified** | Manual v2.0 implies it; the 13 Nov storytelling note says the Pi link was not tested yet. Prove it and record a video |
| SIM800L SMS | **Unverified / disabled** | Wiring and 4.0 V supply are documented; `sms_numbers` is `[]`, so `send_all()` returns “no numbers set”. The headline demo will not send an SMS |
| pH absolute reading | **Uncalibrated** | `ph_calibration.calibrated=false`; only a sudden pH change from baseline is used. The “pH < 6 or > 9” hard limit is inactive |
| 1:5 model printed | **Team report** | README says all parts printed (team report); design notes still say “not yet printed”; the printed set has not been trial-assembled or wet-tested per the 5 Nov README |
| 1:5 model wet test | **Full model not floated; sensor probes bench-tested** | The README says the model has not been wet-tested; the 12–13 Nov bench test used the probes in water. Confirm the dish demo; the model does not need to float at the booth |
| R3 physical build | **Not built** | CAD, checks and FEA only; the tank test is after the finale |
| Cost | **Estimate** | ₹47,886 ex-GST at 100 units, not a supplier quote |
| Dashboard | **Runs** | Stdlib HTTP server, SSE stream, CSV download, command buttons; tested on the dev machine, not on the Pi |
| Simulator fallback | **Runs** | `python3 -m aquasentinel --simulate` plays the six booth waters; useful if the Nano fails |

**Useful nuance for the pitch:** the 1:5 model proves the chain *from sensor to decision to beacon/pump/SMS*. It does not prove river-scale performance. The deck already says this on slide 40 (“A 0.5 L dish is not a river”). Keep that line.

---

## 6. The competition, as it stands

- **19 Nov:** booth/exhibition. Arrive by 10:00. One display and laptop are provided by the organisers; personal laptops are not the plan. Plan how the dashboard will be shown.
- **20 Nov:** 09:00–16:30. 7-minute pitch + 6–7 minutes Q&A. 10 teams. Top 2 go to Nashville, 14–17 February 2027.
- **Travel reimbursement:** up to ₹4,000 per person.
- **Rules that matter:** Art. 10 — no false statements; Art. 7.4 — no third-party copyright; videos without music; one FDC post per team.
- **Submission status:** the FDC was submitted on 7 Nov (Task 6, Final Design Concept). The 3DSwym community is reachable. The **AAKRUTI Students Dashboard task list could not be read**: its iframes stayed on “Loading…” in the in-app browser even after reload and repeated waits. Verify Task 6, Team Community, Mentor Registration and any FDC post tasks manually before travel.
- **No new AAKRUTI deadline email** appeared after 9 Nov in the Gmail search. The shortlist email is 25 Oct; team/travel documents are 29–31 Oct; the Top-10 update is 9 Nov. Do not rely on email alone — check the dashboard.

---

## 7. Findings: what is wrong or inconsistent

### P0 — fix first; these can break the demo or a truthfulness claim

**P0-1. SMS cannot send.**
`14_RASPBERRY_PI_SOFTWARE/aquasentinel/config.json` has `"sms_numbers": []`. `sms.py` returns “no numbers set” and the event records that string. The beacon and pump still work, but the demo line “an SMS goes out” is false until a number is added and a test message is delivered.
**Fix:** add two real +91 numbers, confirm the SIM has SMS balance, run the dashboard’s “Send test SMS” and `tools/check_hardware.py`, and keep the sent message on a phone for the booth.

**P0-2. pH absolute limits are switched off.**
`"ph_calibration": {"calibrated": false, "points": [[2.082, 4.0], [2.279, 9.2]]}`. `brain.py` only applies `pH < 6` / `pH > 9` when `calibrated` is true. Vinegar will still trigger `ACIDIC` through the 1.0 pH drop from baseline, so the demo works — but the pitch’s hard-limit claim does not.
**Fix:** run `tools/calibrate_ph.py` with pH 4.0 and 7.0 buffers (9.2 optional), confirm `calibrated: true`, and re-run the self-test. Store the electrode in KCl; do not let it dry.

**P0-3. “Rain” and “8 sensors” contradict the real build.**
The real build has **7 sensor modules**: pH, TDS, turbidity, DS18B20, DHT11, LDR, MQ-3. There is **no rain sensor** in the Nano firmware, no rain input in `brain.py`, and the electronics manual Rev 2.0 explicitly says the rain sensor was dropped. Yet:
- Deck slide 18: “rain, light and humidity”;
- Deck slide 31: a “Rain” column in the decision table;
- Deck slide 34: “Rain, light and humidity sensors”;
- Deck slide 37: header says “Seven sensors” but the list includes Rain;
- Deck slide 46: “Raspberry Pi, 8 sensors”;
- Deck A4 (slide 67): “turbidity↑ with TDS flat = runoff (rain plate wet: stronger)”;
- Public GitHub README: “One Raspberry Pi, eight sensors” and a rain-sensor diagram.

This is a direct Art. 10 risk: two documents dated 14 Nov say different things, and the public repo says the wrong one. A judge who scans the QR code will see “eight sensors”.
**Fix (recommended):** remove Rain from the deck and the public README; change “8 sensors” to “7 sensors / 8 readings” where the distinction is useful (pH, TDS, turbidity, water temp, air temp, humidity, light, vapour); remove the Rain column and the “rain plate wet” clause. Do **not** try to add a rain sensor in four days — the PCB v1.2 and firmware are not wired for it.

**P0-4. “Everything verified” is not supported yet.**
Electronics manual p.17 says “Everything verified on the bench 12–13 Nov 2026”. The 13 Nov storytelling note says: every sensor and output was proven through the PCB, **but the SIM800L and the Raspberry Pi link were not tested yet**. The self-test I ran is the decision engine on simulated data, not the hardware chain.
**Fix:** test the Pi↔Nano link and one real SMS. If they pass, the manual is true — record the evidence (photo/video/log line). If they do not, soften the manual to “sensors, beacon and pump verified; Pi link and SMS to be verified at the booth” and do not claim otherwise in the pitch.

**P0-5. Git is not a backup of the deck, CAD or print files.**
`.git/info/exclude` contains `00_*`, `01_*`, `02_*`, `03_*`, `04_*`, `05_*`, `06_*`, `07_*`, `*.zip`, `*.bat`, `private/`, `.claude/worktrees/`. That excludes:
- the finale deck (`01_*`),
- the live-model STLs and SOLIDWORKS (`02_*`),
- the R3 CAD (`05_*`),
- the simulation (`06_*`),
- the cost pack (`07_*`),
- the submission zip (`*.zip`).

Only 345 files are tracked, mostly the older `mechanical/`, `docs/`, `firmware/` and `analytics/` tree. The 14 Nov deck update is outside git, on this laptop and OneDrive. The PDF backup next to it is dated **7 Nov**, so if the venue laptop cannot open the PPTX, the PDF shows the older deck. The 137 MB R3 animation is over GitHub’s 100 MB file limit; a `git add .` would try to add it and fail on push.
**Fix:** copy the 14 Nov PPTX and a freshly exported PDF to a USB stick; make a full folder backup; commit the small code/docs selectively; create a git bundle; do not force-push the diverged `main`.

### P1 — fix before you print, hand over or present

**P1-1. The mechanical assembly manual is stale.**
`02_LIVE_MODEL_1to5/00_ASSEMBLY_MANUAL/AquaSentinel_LIVE_1to5_Assembly_Manual_SOLIDWORKS.pdf` is 30 pages, dated 7 Nov, and still instructs the builder to fit the rain plate + LM393 and says 37 parts. The 14 Nov electronics manual says rain was dropped. The `02_LIVE_MODEL_1to5/README.md` also references a 43-page manual that is not in the folder, a `03_PRINT_RECORDS/` folder that is missing, and a `pH_Electrode_Quick_Guide.pdf` that is missing. `00_START_HERE.md` says 37 STL; the folder has 38 (37 assembly print files + the printable sample bottle).
**Fix:** add a one-page addendum to the mechanical manual (“rain plate is not instrumented; 38 STL files = 37 assembly print files + printable bottle”), fix the broken links, and do not hand the old manual to a judge without the addendum.

**P1-2. Several deck technical claims are not matched by the code.**
These are the ones a sharp Q&A judge could catch:

| Deck claim | Code reality | Safe wording |
|---|---|---|
| “A baseline for every hour of the day” (slides 18, 31, A4) | `brain.py` keeps **one** baseline for pH and one for TDS, no hourly table | “a baseline learned from the water” |
| “First 7 days: baseline learning only” (A4) | `learn_seconds` is **20 s** at the booth | “20 s at the booth; 7 days in the river design” or remove |
| “The learned baseline is saved to disk, so a reboot doesn’t erase it” (A4) | `brain.py` keeps the baseline in memory; no save/load | remove, or implement persistence |
| “turbidity 3× its baseline” (A4) | `classify()` uses the turbidity **digital DO**, not a 3× analog baseline | “turbidity turns cloudy” |
| “Hard limits act at once” (A4) | hard limits still go through the 2-of-3 confirmation window | “hard limits need 2 of the last 3 readings” |
| “pH and TDS boards are never powered together” (A4) | pH is **always** powered from 9 V; only TDS is switched by A0 | “the TDS board is powered only while it is read, because it disturbs pH” |
| “4 of 4 spills flagged in a 30-day test” (slide 46) | The 30-day test is **synthetic data**; the archived analytics README says so | “4 of 4 simulated spills in a 30-day synthetic test” |

**P1-3. `.ino` header says the wrong board.**
The firmware comment says “AquaSentinel Sensor Hub PCB v1.1 (84 × 84 mm …)”. The actual board is **v1.2, 104 × 72 mm**. The pin map below the comment is the v1.2 map, so the code is right and the comment is stale. Fix the comment; a judge reading the source will notice.

**P1-4. MQ-3 warm-up is inconsistent.**
`config.json` has `mq3_warmup_s: 90`; the manual and troubleshooting page say **wait 3 min**. The code suppresses SOLVENT until 90 s. If the booth demo uses sanitiser before 3 minutes, it may do nothing.
**Fix:** set `mq3_warmup_s` to 180 (or document 90 s as the bench value), and keep the MQ-3 powered continuously at the booth. Dry the station between solvent runs.

**P1-5. Deck status chips are from 7 Nov.**
Slide 34 says “✓ designed / ✓ printed / wiring + code / live 19 Nov / status at submission, 7 Nov 2026”. Slide 46 says “Electronics wiring and code … are under way”. On 20 Nov, the audience will hear a status that is four days old. A4 says the decision logic is “being coded in Python” — the code is written and the self-test passes.
**Fix:** update to the 14 Nov/19 Nov truth: “printed; sensors, beacon and pump bench-proven; Pi + SMS verified [only if true]”; “code written, self-test ALL PASS”; “live at the booth”. If something is not proven, say so in the same sentence.

**P1-6. Night/river footage copyright is unresolved.**
The FDC rules validation still lists “source of the night/river footage (Art. 7.4)” as “to confirm”. If the footage is not the team’s own, replace it with the team’s R3 render/animation or credit it with permission. Do not let a copyright question disqualify the entry.

**P1-7. The 14 Nov deck has no current PDF backup.**
The PPTX was updated at 20:34 on 14 Nov; the PDF is 7 Nov. Export a fresh PDF after the content fixes and test it on a machine that is not this laptop.

### P2 — tidy, but do not let it consume the week

- **Design notes are stale:** `02_LIVE_MODEL_1to5/04_DESIGN_NOTES/LIVE_model_design_notes.md` says “CAD concept, not yet printed or wet-tested”, references a `STL_print/` folder with 35 files, and still describes the ADS1115/rain design. It contradicts the README and the deck.
- **Cost doc still carries the old design:** `07_COST_AND_BUSINESS/02_Pi_Based_Product_Cost_Estimate_2026-11-06.md` includes a “Rain plate + LM393 ₹100” line and “2 × ADS1115, DS3231, 3 buck converters … ₹3,000”. `03_Value_Engineered_Cost_48k_2026-11-07.md` includes “rain” in the electronics line and “2 × ADS1115, RTC, bucks …” in the bench additions. The ₹47,886 total is close enough for the pitch, but add a footnote: “rain sensor and ADS1115 removed in the final build; total unchanged within estimate tolerance.”
- **Credentials in OneDrive:** `Claude_Conversation_Recovery/00_CONFIG_BACKUP` contains `.credentials.json` (19.4 KB), `.claude.json`, `buddy-tokens.json` and a `README_SENSITIVE.md`. This is a security risk, not a project risk. After re-login, delete the backup and empty the Recycle Bin; do not sync it to a shared folder.
- **Booth display:** the organisers provide one display driven by their laptop. Plan how the Pi dashboard is shown: a small HDMI monitor/tablet on the team’s own table if allowed, or a phone on the Pi’s Wi-Fi hotspot, or printed dashboard stills. The beacon + pump demo works without a dashboard; the dashboard is the “wow”, not the proof.
- **“250 mL” sample:** the pump runs 5 s; the deck says “pump fills 250 mL”. Measure it once. If it is not 250 mL, say “a sample” instead of a number.
- **“Solar-powered”:** the full-size product is solar; the 1:5 booth model runs on mains. Say “the product is solar-powered; the model runs on mains” if asked.
- **DHT11 humidity >90%:** the DHT11 is not reliable in condensing conditions. At a wet booth, mount it away from splashes; if it fails, it reports FAULT, which is the correct behaviour.

---

## 8. The critical path: 15–20 November

Today is 14 November. That leaves four working days (15–18) plus travel and the booth. Do not add new features. Freeze scope.

### Saturday 15 November — hardware truth day

- Dry-fit the printed 1:5 model; check the manual’s open points.
- Wire the Sensor Hub PCB v1.2 to the Nano, beacon, pump, pH/TDS/turbidity/DS18B20/DHT11/LDR/MQ-3, SIM800L.
- Run `python3 tools/check_hardware.py`; fix every FAIL.
- Calibrate pH with 4.0 and 7.0 buffers; confirm `calibrated: true`.
- Put two +91 numbers in `config.json`; run “Send test SMS”; keep the received message.
- Prove the Pi↔Nano link for 10 minutes; confirm one JSON line per second.
- Run `tools/self_test.py`; expect ALL PASS.
- Record a 60-second phone video of the full chain: water → class → red beacon → pump → SMS.

**Exit criterion:** you can demonstrate the full chain on real hardware, not the simulator.

### Sunday 16 November — deck truth pass

- Remove Rain and “8 sensors” from slides 18, 31, 34, 37, 46 and A4; use “7 sensors / 8 readings”.
- Fix “37 printed parts” to “37 printed parts + printable sample bottle” or “38 print files”.
- Add “simulated” to the 4-of-4 30-day claim.
- Fix the six code-vs-claim rows in P1-2.
- Update the status chips on slides 34, 46 and A4 to the 14 Nov truth.
- Export a fresh PDF; test it on another machine.
- Update the speaker notes; keep the 7-minute split (Soham 2,3,4,5,14,16 · Tanmay 6,7,10,13 · Prasad 8,9,11 · Bhakti 12,15).
- Print one A4 “demo + Q&A” sheet for each team member.

### Monday 17 November — rehearse, do not edit

- Three timed run-throughs of the 7-minute pitch. Cut words, not slides.
- Q&A drill with the 10 hardest questions: “Have you built it?”, “Is the SMS real?”, “How do you know it is not just salt?”, “What about false alarms?”, “Why not a commercial sonde?”, “What is actually simulated?”, “What happens if a sensor fails?”, “What is the TRL?”, “What is the IP?”, “What is the cost basis?”.
- Pack spares: Nano, USB cable, Pi SD card image, SIM, antenna, pH buffer sachets, KCl, distilled water, paper towels, extension cord, multimeter, screwdriver, tape, labels.
- Test the full demo on the power arrangement you will use at the venue.

### Tuesday 18 November — freeze and travel

- Copy to a USB stick: the 14 Nov PPTX, the fresh PDF, the pitch video, the journey video, the R3 animation, the electronics manual, the assembly manual, the one-page demo sheet, and the AR/QR assets.
- Make a second USB stick. Keep one on your person.
- Do not edit the deck after 18:00.
- Charge every phone, power bank and laptop.
- Travel to Pune. Confirm the hotel and the 10:00 arrival.

### Wednesday 19 November — booth

- Set up by 10:00. Power the MQ-3 first; it needs 3 minutes.
- Keep the pH electrode wet; keep the turbidity slot clean; keep the sample bottle station dry between solvent runs.
- Run the six demos in this order: clean → salty → clean → vinegar → clean → muddy → clean → sanitiser → clean → unplug temperature probe.
- After each event, wait for the 4-clean-readings clear (a few seconds in the model) before the next water.
- Respect the 10-minute SMS cooldown; do not promise an SMS on every demo. If the cooldown is active, show the dashboard event log and say “the SMS is rate-limited so the phone is not flooded.”
- Keep a printed “what is real / what is simulated” card on the table.

### Thursday 20 November — pitch

- Use the 7-minute deck. The model is the proof; do not read the slides.
- In the first 30 seconds: the 2 a.m. Godavari story, the three actions, the 1:5 model on the table.
- In the Q&A: answer the question that was asked. If you do not know, say “we have not measured that yet; here is how we would.” That is stronger than a guess.
- Close with the ask: pilot, mentorship, and the path to Nashville.

---

## 9. Booth demo run sheet

| Water / action | Expected class | Beacon | Action | One line to say |
|---|---|---|---|---|
| Clean tap water | NORMAL | Green | — | “This is the river on a normal day.” |
| Spoon of salt, stirred | INDUSTRIAL | Red | Sample + SMS (if cooldown clear) | “Dissolved solids jumped; this is a saline or industrial discharge.” |
| A little vinegar | ACIDIC | Red | Sample + SMS | “pH fell; this is an acid spill.” |
| Spoon of soil | RUNOFF | Red | Sample + SMS | “Cloudy water, salts flat; this is farm runoff.” |
| Sanitiser on a tissue at the bottle cone | SOLVENT | Red | Sample + SMS | “Vapour above the sample; this is a solvent or fuel.” |
| Unplug the temperature probe | SENSOR FAULT | Blinking red | — | “A broken sensor is a fault, never ‘normal’.” |

**Timing:** 20 s LEARNING at startup; ≈5 s to react; 4 clean readings to clear; 10-minute SMS cooldown. The model reads once per second; the river product reads every 15 minutes.

**Fallbacks:**
- If SMS fails, show the dashboard’s event log and the queued status. Do not pretend a message was sent.
- If a sensor fails, use it as the SENSOR FAULT demo. That is a feature, not an embarrassment.
- If the Nano fails, switch to `--simulate` on the Pi and say clearly “this is the simulator; the hardware chain is what we showed a minute ago.” Have the 60-second hardware video ready.
- If the dashboard cannot be displayed, the beacon and pump still prove the chain. Use the printed stills.

---

## 10. Backup, git and travel

Do this before you leave, in this order:

1. **Copy the whole folder to an external drive** (or a second USB stick). OneDrive is synced, but it is not a second copy if the laptop is lost.
2. **Copy the 14 Nov PPTX and a fresh PDF** to the USB stick. The current PDF backup is 7 Nov.
3. **Create a git bundle** of the local history:
   `git bundle create AquaSentinel_2026-11-14.bundle --all`
   Keep it on the USB stick and in OneDrive.
4. **Selective commit** the small code/docs, not the videos:
   - `12_ELECTRONICS_MANUAL_1to5` (manual + PCB + firmware)
   - `14_RASPBERRY_PI_SOFTWARE` (Pi code, config, tools)
   - `PROJECT_IDENTIFICATION_AND_CRITICAL_PATH_2026-11-14.md`
   - the updated `README.md`, `00_START_HERE.md`, and the live-model docs after the fixes
   Do **not** `git add .`; the 137 MB video and the excluded `00_*`–`07_*` folders will cause problems.
5. **Do not force-push `main`.** Local and remote have diverged 14/14. If you want GitHub updated, push a new branch (for example `finale-2026-11-14`) or create a new repository; keep the old `main` as the submitted history. If you must replace it, take a bundle first and use `--force-with-lease`, never plain `--force`.
6. **Update or banner the public GitHub README.** It currently says “eight sensors” and includes rain. Either correct it or add a one-line banner: “This repository is the semi-final archive; the final 7-sensor build is documented in the 14 Nov electronics manual.” A judge scanning the QR should not land on a contradiction.
7. **Credentials:** delete `Claude_Conversation_Recovery/00_CONFIG_BACKUP` after you have re-logged in; do not sync `.credentials.json` or tokens to a shared folder. This is separate from the project, but it is sitting in OneDrive.

---

## 11. What I could not verify

Be honest with yourself about these; do not let them become surprises at the venue.

- **The 3DSwym AAKRUTI Students Dashboard task list.** The community page loads, but the dashboard widgets stayed on “Loading…” in the in-app browser. I could not confirm which tasks are marked complete. Check Task 6, Team Community, Mentor Registration and the FDC post manually.
- **The physical model.** I cannot see or touch it. The “printed” status is a team report; the design notes say not printed. Confirm by inspection.
- **The Pi↔Nano link and the SIM800L.** No hardware is connected to this machine. The manual and the 13 Nov note disagree; only a bench test settles it.
- **The exact pump volume.** The code runs 5 s; the deck says 250 mL. Measure it.
- **The night/river footage licence.** The FDC validation still marks it “to confirm”.
- **The updated deck’s visual layout after text edits.** If we remove “Rain” and change counts, the slides need a visual check for overflow; a text-only edit is not enough.

---

## 12. The recommended next deliverable

The highest risk reduction per hour is **a corrected “booth edition” of the deck plus a one-page demo/Q&A sheet**. It removes the rain/8-sensor contradiction, fixes the counts and status, adds the “simulated” qualifier, and gives every team member the same words.

I will not overwrite the submitted 7 Nov deck. I will create a copy, for example:

`01_FINALE_PRESENTATION/BOOTH_19Nov/AquaSentinel_Finale_7min_BOOTH.pptx`

and a fresh PDF next to it. After that, the second pass is the documentation truth fix: the live-model README/addendum, the `.ino` header, the design notes, the cost footnote, and the backup bundle.

If you want me to start, say **“do the booth deck”** and I will produce the copy and show you the changed slides before saving over anything. If you would rather start with the hardware checklist, say **“do the pre-flight”** and I will turn Section 8 into a printable checklist with tick boxes.

---

*This report is based on the 14 November 2026 local folder, the recovered conversation history, the AAKRUTI emails and the 3DSwym pages. It does not modify the project. All paths are relative to `C:\Users\dell\OneDrive\Desktop\AquaSentinel` unless stated otherwise.*
