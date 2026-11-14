# AquaSentinel — start here

**Team Sanjivani Hero's Journey** · AG26-1500$41 · AAKRUTI 2026 · Robotics
**India Geo Finale:** booth **19 Nov**, pitch **20 Nov 2026**, DS Campus, Pune (7 min pitch + Q&A; top 2 go to Nashville).

AquaSentinel is a float on a guide pole clamped to a bridge pier. Every 15 minutes it reads the river; when a spill passes, it turns its beacon red, sends an SMS and keeps a bottle of that water for the lab.

> **This file is the map.** It is the only place that says which version of each thing is current.
> Old versions were deleted on 14 Nov 2026 with the project lead's approval; what remains is the current build.

---

## 1. Read this first: what is current on 14 Nov 2026

| What | The current file | Notes |
|---|---|---|
| **Pitch deck** | `01_FINALE_PRESENTATION/AquaSentinel_Finale_7min.pptx` | Last edited 14 Nov. This is the only deck to present or edit. |
| **1:5 model assembly manual** | `02_LIVE_MODEL_1to5/00_ASSEMBLY_MANUAL/AquaSentinel_LIVE_1to5_Assembly_Manual_SOLIDWORKS.pdf` | 30 pages, 24 steps. Read `00_MANUAL_STATUS_READ_FIRST.md` beside it first. |
| **1:5 model electronics manual** | `12_ELECTRONICS_MANUAL_1to5/AquaSentinel_LIVE_1to5_Electronics_Assembly_Manual.pdf` | **Revision 2.0, 14 Nov, 17 pages** — Sensor Hub PCB v1.2 + Nano |
| **Sensor Hub PCB + Nano firmware** | `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1` | KiCad design, DRC, CNC G-code, placement/soldering/power-up guides, firmware |
| **Raspberry Pi software** | `14_RASPBERRY_PI_SOFTWARE` | Decision engine, dashboard :8080, SIM800L, logging, install script, pH calibration tool |
| **Full-size R3 assembly manual** | `05_R3_FULL_SIZE_CAD/00_ASSEMBLY_MANUAL/AquaSentinel_R3_Assembly_Manual_SOLIDWORKS.pdf` | 27 pages, 66 part numbers, 12 steps |
| **R3 CAD as submitted (FDC)** | `05_R3_FULL_SIZE_CAD/02_SOLIDWORKS_PackAndGo_FDC` | Pack-and-Go folder + zip |
| **Cost to quote** | `07_COST_AND_BUSINESS/04_AquaSentinel_Cost_48k_Value_Engineered.pdf` | ₹47,886 ex-GST at 100 units (≈ ₹56,505 with GST); prototype ₹64,616 |
| **Pitch video (final)** | `08_VIDEOS/AquaSentinel_Pitch_Video_Clean_Water_Now_FINAL_v3.mp4` | 8 Nov voice-over, on the FDC. Earlier takes were deleted on 14 Nov. |
| **Working audit + critical path** | `PROJECT_IDENTIFICATION_AND_CRITICAL_PATH_2026-11-14.md` | The 7 P0/P1/P2 problems, verified-vs-unverified table, Q&A traps |

### Status at 14 Nov 2026 — do not overclaim at the booth

- Sensors, beacon and pump are **bench-proven** (12–13 Nov).
- The 1:5 model has **not yet been trial-assembled or floated**.
- The **Pi ↔ Nano USB link** and **SIM800L SMS** are **not yet verified end to end**.
- **pH is not calibrated**, so the absolute pH limits (6–9) are inactive; only sudden pH changes act.
- **`sms_numbers` is empty**, so the station currently cannot send an SMS.
- The self-test printing **ALL PASS** exercises the decision engine on simulated data — it is not a hardware test.

The full explanation, with what is safe to say, is in the control report above (§5 and §7).

---

## 2. I need…

| I need… | Open this |
|---|---|
| The pitch deck | `01_FINALE_PRESENTATION/AquaSentinel_Finale_7min.pptx` |
| The speaker split for the 7 minutes | `01_FINALE_PRESENTATION/_SUBMISSION_RECORD_7Nov2026/00_TODAY_7Nov_Submission_and_Messages.md` |
| Exactly what was submitted on 7 Nov | `01_FINALE_PRESENTATION/_SUBMISSION_RECORD_7Nov2026/` (PDF + zip) |
| The 38 print files for the 1:5 model | `02_LIVE_MODEL_1to5/01_FINAL_STL` (38 STL + `PARTS_LIST.csv` lists 37; the extra is the LD-S16 bottle variant) |
| The 1:5 model in SOLIDWORKS | `02_LIVE_MODEL_1to5/05_SOLIDWORKS_ASSEMBLY/AquaSentinel_LIVE_1to5_Assembly.SLDASM` |
| The 17 LD parts, named | `02_LIVE_MODEL_1to5/02_CAD_SOLIDWORKS` |
| The printed dish (LD-S17) | `02_LIVE_MODEL_1to5/07_PRINTED_DISH_LD-S17` |
| A4 part labels for the booth | `02_LIVE_MODEL_1to5/06_PART_LABELS_A4` |
| Design notes and print list | `02_LIVE_MODEL_1to5/04_DESIGN_NOTES` |
| The R3 in SOLIDWORKS | `05_R3_FULL_SIZE_CAD/03_SOLIDWORKS_2026_assembly_for_manual` |
| R3 drawings / checks / renders | `05_R3_FULL_SIZE_CAD/04_Drawings`, `05_Design_Checks`, `06_Renders` |
| R3 STEP/STL and GLB | `05_R3_FULL_SIZE_CAD/07_Parts_STEP_STL`, `08_Assembly_STEP_GLB` |
| R3 bill of materials | `05_R3_FULL_SIZE_CAD/01_BOM_R3.csv` |
| Pole and bracket FEA | `06_SIMULATION` |
| Costed BOM (researched base data) | `07_COST_AND_BUSINESS/01_AquaSentinel_Costed_BOM_Researched.xlsx` |
| Videos | `08_VIDEOS` (read its `README.md` first — the 60 s marketing video has music and must not go in the finale deck) |
| FDC portal contents | `09_SUBMISSIONS_AND_CERTIFICATES/03_FDC_Update_7Nov2026/FDC_post_contents_7Nov2026.md` |
| Certificates | `09_SUBMISSIONS_AND_CERTIFICATES/05_Participation_Certificates` |
| Earlier stages / team change | `09_SUBMISSIONS_AND_CERTIFICATES/01_Earlier_stages`, `04_Team_change_Oct2026` |
| Creative Experience storytelling | `13_CREATIVE_EXPERIENCE_STORYTELLING/00_README_START_HERE.md` |
| What was deleted, and what was rescued | `00_PROJECT_CONTROL/PURGE_REPORT_2026-11-14.md` |
| What remains, file by file (709 project files) and every PNG verdict | `00_PROJECT_CONTROL/FILE_AUDIT_2026-11-14.md` + `FILE_AUDIT_2026-11-14.csv` + `PNG_AUDIT_2026-11-15.csv` |

**Not present:** the old `AquaSentinel_pH_Electrode_Quick_Guide.pdf` link was broken and has been removed from this map. For pH work use `14_RASPBERRY_PI_SOFTWARE/aquasentinel/tools/calibrate_ph.py` and the electronics manual.

---

## 3. Folder map

| Folder | What lives there | Current? |
|---|---|---|
| `00_PROJECT_CONTROL/` | audit, critical path, reorg log, backup policy | working documents |
| `01_FINALE_PRESENTATION/` | the 7-minute deck; the 7 Nov submission is in `01_FINALE_PRESENTATION/_SUBMISSION_RECORD_7Nov2026/` | **current** |
| `02_LIVE_MODEL_1to5/` | the 1:5 LIVE model: manual, 38 STLs, SOLIDWORKS parts/assembly, labels, printed dish | **current** |
| `05_R3_FULL_SIZE_CAD/` | full-size R3: manual, BOM, CAD, drawings, checks, renders, STEP/STL | **current** |
| `06_SIMULATION/` | SOLIDWORKS Simulation: guide pole and pier bracket | **current** |
| `07_COST_AND_BUSINESS/` | costed BOM, 6 Nov estimate, value-engineered cost + PDF | **current** (read its README for caveats) |
| `08_VIDEOS/` | final pitch, R3 assembly, journey and 60 s marketing videos, plus the raw teammate recordings in `08_VIDEOS/00_source_recordings/` | **current** |
| `09_SUBMISSIONS_AND_CERTIFICATES/` | one sub-folder per stage: earlier, FDC Oct, FDC update 7 Nov, team change, certificates, portal, Maker Fest 2027 | **record** |
| `12_ELECTRONICS_MANUAL_1to5/` | electronics manual Rev 2.0, Sensor Hub PCB v1.2, CAD working copies, manual build source | **current** |
| `13_CREATIVE_EXPERIENCE_STORYTELLING/` | 3DEXCITE Creative Experience storyline, assets, story video, AR model, scripts | **current** |
| `14_RASPBERRY_PI_SOFTWARE/` | Pi 3B+ software and install/calibration/self-test tools | **current** |
| `99_ARCHIVE/` | the pre-purge file manifest and purge note only; old versions were deleted on 14 Nov 2026 | historical record |

Number gaps (03, 04, 10, 11) are deliberate: those folders were archived and then deleted on 14 Nov 2026, and their numbers were not reused, so old links and conversations still make sense. `00_PROJECT_CONTROL/PURGE_REPORT_2026-11-14.md` lists what each one was.

---

## 4. How this workspace is kept safe

- **Old versions were deleted on 14 Nov 2026** with the project lead's approval. Current work only. A later file audit packed derived files into four verified zips: **709 project files / 783 MB**, plus the four audit records (see `00_PROJECT_CONTROL/FILE_AUDIT_2026-11-14.md`).
- **Every move is logged** in `00_PROJECT_CONTROL/WORKSPACE_REORG_LOG_2026-11-14.csv` (source, destination, size, SHA-256, reason).
- **A pre-purge fingerprint exists:** `99_ARCHIVE/file_manifest_before_purge_2026-11-14.csv` records SHA-256, size and timestamp of all 4,266 files that existed before the purge.
- **Git holds the tracked text and code**, on every branch, plus tags `backup/pre-reorg-2026-11-14` and `workspace/reorg-2026-11-14`.
- **Git is not a backup for videos, decks or CAD.** Those are local-only; OneDrive version history is the only recovery path. Read `00_PROJECT_CONTROL/BACKUP_AND_VERSION_CONTROL.md` before committing or pushing.

### History of cleanups

| Date | What happened | Where the record is |
|---|---|---|
| 6 Nov | first cleanup (some files went to the Recycle Bin) | described in the purge report |
| 7 Nov | R3 folders numbered, submissions split by stage, coursework archived | described in the purge report |
| 14 Nov, afternoon | old electronics, housing, storytelling, LinkedIn post, old video takes archived | described in the purge report |
| 14 Nov, evening | workspace reorganised: current deck separated from the submission, navigation rebuilt | `00_PROJECT_CONTROL/WORKSPACE_REORG_REPORT_2026-11-14.md` |
| 14 Nov, night | old versions, Claude worktrees and safety bundles permanently deleted; four unique documents rescued first | `00_PROJECT_CONTROL/PURGE_REPORT_2026-11-14.md` |
| 14 Nov, late night | file-by-file audit: 259 derived files packed into four verified zips, 68 duplicates removed; 1,034 → 714 files (711 project + 3 records) | `00_PROJECT_CONTROL/FILE_AUDIT_2026-11-14.md` |
| 15 Nov | every remaining PNG inspected: 232 kept, 2 with no content or unique value deleted; 3 missing SIM800L diagrams restored from git | `00_PROJECT_CONTROL/PNG_AUDIT_2026-11-15.csv` |

**If something looks missing,** read the purge report first (it lists every deleted folder), then the move log (it lists every move).
