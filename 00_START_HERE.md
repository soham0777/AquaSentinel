# AquaSentinel: start here

**Team Sanjivani Hero's Journey** · AG26-1500$41 · AAKRUTI 2026 · Robotics

**India Geo Finale:** booth on **19 Nov** and pitch on **20 Nov 2026**, at DS Campus, Pune. The pitch is 7 minutes plus Q&A; the top 2 teams go to Nashville.

AquaSentinel is a float on a guide pole clamped to a bridge pier. Every 15 minutes it reads the river. When a spill passes, it turns its beacon red, sends an SMS and keeps a bottle of that water for the lab.

> **This file is the map.** It is the only place that says which version of each thing is current. Last checked **17 Nov 2026**.

---

## 1. What is current (17 Nov 2026)

| What | The current file | Notes |
|---|---|---|
| **Pitch deck** | `01_FINALE_PRESENTATION/AquaSentinel_Finale_7min.pptx` (+ `.pdf`) | The same file is on the FDC; the organisers downloaded it on 17 Nov, so no more changes. Every number is checked in `AquaSentinel_Deck_Fact_Check.md`. |
| **Pitch script (one speaker)** | `01_FINALE_PRESENTATION/AquaSentinel_Live_Pitch_Script_v3.pdf` (+ `.docx`) | Slide by slide from the greeting; about 6 min 40 s. |
| **Cost and business numbers** | `07_COST_AND_BUSINESS/00_COST_SUMMARY_READ_FIRST.md` | ₹47,886 a float (≈ ₹48,000), ₹64,616 prototype, ₹8,000 a month. **The only figures to quote.** |
| **Printable cost sheet** | `07_COST_AND_BUSINESS/04_AquaSentinel_Cost_48k_Value_Engineered.pdf` | On the FDC and in the print pack. |
| **Booth print files** | `00_PROJECT_CONTROL/PRINT_READY/` | Corrected 17 Nov: figures match the deck, and the photos are restored. The order is in `00_PRINT_LIST.txt`. |
| **1:5 model assembly manual** | `02_LIVE_MODEL_1to5/00_ASSEMBLY_MANUAL/AquaSentinel_LIVE_1to5_Assembly_Manual_SOLIDWORKS.pdf` | Read `00_MANUAL_STATUS_READ_FIRST.md` and the 15 Nov addendum first. |
| **1:5 model electronics manual** | `12_ELECTRONICS_MANUAL_1to5/AquaSentinel_LIVE_1to5_Electronics_Assembly_Manual.pdf` | Revision 2.0, 17 pages. |
| **Sensor Hub PCB + Nano firmware v2** | `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1/` | KiCad design, G-code, build guides, picture guides, firmware v2 (17 Nov). |
| **Raspberry Pi software** | `14_RASPBERRY_PI_SOFTWARE/aquasentinel/` | Start with `RASPBERRY_PI_STEP_BY_STEP.md`. Includes the installer, calibration, health doctor, SMS and Firebase cloud. |
| **Full-size R3 assembly manual** | `05_R3_FULL_SIZE_CAD/00_ASSEMBLY_MANUAL/AquaSentinel_R3_Assembly_Manual_SOLIDWORKS.pdf` | 27 pages, 66 part numbers, 12 steps. |
| **R3 CAD on the FDC** | `05_R3_FULL_SIZE_CAD/02_SOLIDWORKS_PackAndGo_FDC/AquaSentinel_R3_SOLIDWORKS_NATIVE_PackAndGo.zip` | Native parts, assembly and 6 drawings. |
| **Films on the FDC** | `08_VIDEOS/AquaSentinel_Pitch_Film_2026-11-16.mp4`, `AquaSentinel_Journey_Film_2026-11-16.mp4` | Both have a music bed: show them muted, or talk over them. The deck's own videos are silent. |

### Status on 17 Nov 2026: what is proven, and what is not yet

**Proven:**
- Sensors, beacon and pump on the bench (12–13 Nov).
- The Pi reads the Nano live.
- pH, turbidity and MQ-3 calibrated on the Pi (17 Nov).
- 4 SMS numbers set.
- The Firebase project and the station login created.

**Not yet proven:**
- An SMS received end to end.
- The cloud test on the Pi.
- The 1:5 model floated.
- The full-size R3 built: it is a design, not a build.

The self-test (ALL PASS) proves the software logic on simulated data. It is not a hardware test.

## 2. I need…

| I need… | Open this |
|---|---|
| The deck, its fact check, the script | `01_FINALE_PRESENTATION/` |
| Exactly what was submitted on 7 Nov | `01_FINALE_PRESENTATION/_SUBMISSION_RECORD_7Nov2026/` (frozen record) |
| The deck as it was before the 16 Nov update | `01_FINALE_PRESENTATION/_backup_before_16Nov_update/` |
| The 38 print files for the 1:5 model | `02_LIVE_MODEL_1to5/01_FINAL_STL` (`PARTS_LIST.csv` lists 37; the extra file is a bottle variant) |
| The 1:5 model in SOLIDWORKS | `02_LIVE_MODEL_1to5/05_SOLIDWORKS_ASSEMBLY/AquaSentinel_LIVE_1to5_Assembly.SLDASM` |
| The R3 native SOLIDWORKS parts | `05_R3_FULL_SIZE_CAD/03b_SOLIDWORKS_2026_NATIVE` |
| R3 drawings, checks, renders, STEP/STL, BOM | `05_R3_FULL_SIZE_CAD/04_Drawings`, `05_Design_Checks`, `06_Renders`, `07_Parts_STEP_STL`, `01_BOM_R3.csv` |
| Pole and bracket FEA | `06_SIMULATION` |
| Every cost line and rate | `07_COST_AND_BUSINESS/03_Value_Engineered_Cost_48k_2026-11-07.md` |
| PCB soldering and power-up picture cards | `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1/guide/picture_guides/` |
| Set up a Raspberry Pi from scratch | `14_RASPBERRY_PI_SOFTWARE/aquasentinel/RASPBERRY_PI_STEP_BY_STEP.md` |
| Firebase cloud set-up | `14_RASPBERRY_PI_SOFTWARE/aquasentinel/cloud/FIREBASE_SETUP.md` (project `aquasentinel-live`) |
| Creative Experience storytelling | `13_CREATIVE_EXPERIENCE_STORYTELLING/00_START_HERE.md` |
| Certificates, FDC records, team change | `09_SUBMISSIONS_AND_CERTIFICATES/` (frozen records) |

## 3. Folder map

| Folder | What lives there | State |
|---|---|---|
| `00_PROJECT_CONTROL/` | booth print files (`PRINT_READY`), audits, reorg logs, backup policy; AI prompt notes in `_ai_working_notes/` | working + records |
| `01_FINALE_PRESENTATION/` | the 7-minute deck, fact check, solo pitch script; the 7 Nov submission and a pre-16 Nov backup | **current** |
| `02_LIVE_MODEL_1to5/` | the 1:5 LIVE model: manual, 38 STLs, SOLIDWORKS parts and assembly, labels, printed dish | **current** |
| `05_R3_FULL_SIZE_CAD/` | full-size R3: manual, BOM, native CAD, drawings, checks, renders, STEP/STL | **current** |
| `06_SIMULATION/` | SOLIDWORKS static studies of the guide pole and pier bracket (lowest pole safety factor 2.66) | **current** |
| `07_COST_AND_BUSINESS/` | **`00_COST_SUMMARY_READ_FIRST.md`**, the full working (03), the cost sheet PDF (04); old estimates in `_superseded_DO_NOT_QUOTE/` | **current** |
| `08_VIDEOS/` | the two 16 Nov films, the R3 assembly animation, teammates' raw recordings; older cuts in `_earlier_cuts/` | **current** |
| `09_SUBMISSIONS_AND_CERTIFICATES/` | one sub-folder per stage | frozen record |
| `12_ELECTRONICS_MANUAL_1to5/` | electronics manual Rev 2.0, Sensor Hub PCB v1.2, CAD working copies. Do not move or rename CAD parts: the assemblies point to them | **current** |
| `13_CREATIVE_EXPERIENCE_STORYTELLING/` | 3DEXCITE storyline, assets, story video, AR model | **current** |
| `14_RASPBERRY_PI_SOFTWARE/` | Pi software, firmware copy, installer, cloud | **current** |
| `99_ARCHIVE/` | the pre-purge manifest and purge note | frozen record |

The missing folder numbers (03, 04, 10, 11) are deliberate. Those folders were archived and deleted on 14 Nov 2026, and their numbers were not reused.

`PROJECT_IDENTIFICATION_AND_CRITICAL_PATH_2026-11-14.md` at the root is the 14 Nov working audit. Some of its status lines are older than this page.

---

## 4. How this workspace is kept safe

- **Git** tracks the text and code. **Videos, decks and CAD are local only**, so OneDrive version history is their only backup. Read `00_PROJECT_CONTROL/BACKUP_AND_VERSION_CONTROL.md` before committing or pushing.
- **Never commit `14_RASPBERRY_PI_SOFTWARE/aquasentinel/secrets.json`.** It holds the SMS numbers and the Firebase key. `.gitignore` already excludes it.
- **Frozen records are never edited:**
  - the 7 Nov export;
  - `09_SUBMISSIONS_AND_CERTIFICATES`;
  - the audit CSVs and reports in `00_PROJECT_CONTROL`;
  - `99_ARCHIVE`;
  - `_SUBMISSION_RECORD_7Nov2026`.

### History of cleanups

| Date | What happened | Where the record is |
|---|---|---|
| 6–7 Nov | first cleanup; R3 folders numbered; submissions split by stage | `00_PROJECT_CONTROL/PURGE_REPORT_2026-11-14.md` |
| 14 Nov | workspace reorganised; old versions deleted with the project lead's approval | `WORKSPACE_REORG_REPORT_2026-11-14.md`, `PURGE_REPORT_2026-11-14.md` |
| 14–15 Nov | file, PNG and CAD audits | `FILE_AUDIT_2026-11-14.md`, `PNG_AUDIT_2026-11-15.csv`, `CAD_AUDIT_2026-11-15.md` |
| 17 Nov | Project-wide cost audit. Booth prints corrected from ₹47,900 / ₹64,600 to ₹47,886 / ₹64,616, and 19 → 18 Wh. 4 broken photo links repaired. Cost folder cut to one summary, with old estimates moved to `_superseded_DO_NOT_QUOTE/`. PCB picture guides moved next to the PCB. AI prompts moved to `_ai_working_notes/`. Older video cuts moved to `_earlier_cuts/`. Python caches and simulator test logs removed. The first script draft sent to the Recycle Bin. | this table |
