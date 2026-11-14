# AquaSentinel

**Team Sanjivani Hero's Journey · AG26-1500$41 · AAKRUTI 2026 · Robotics**
**India Geo Finale: booth 19 Nov, pitch 20 Nov 2026 (Pune)**

AquaSentinel is a solar-powered float that rides on a stainless guide pole clamped to a bridge pier.
Every 15 minutes it reads the river; when a spill passes it turns its light red, sends an SMS through the
SIM800L, and keeps a bottle of that water for the lab. No motor, no anchor — it rises and falls with the river.

> **Local project map:** `00_START_HERE.md`. This repository is an older public snapshot; the full folder on the team
> laptop (CAD, decks, videos, manuals) is the source of truth.

## Current build (as of 14 Nov 2026)

**1:5 LIVE model** — a scale model built around the real, full-size sensors:

| Layer | Hardware | Role |
|---|---|---|
| Sensors | **PH-4502C** (pH, E-201-C electrode), **SEN0244** (TDS), **SEN0189** (turbidity), **DS18B20** (water temp), **DHT11** (air temp/humidity), **LDR** (light), **MQ-3** (vapour) | measure the water |
| Sensor hub | **Arduino Nano (ATmega328P)** on our own milled **Sensor Hub PCB v1.2** (104 × 72 mm, single-sided, KiCad, CNC-milled 12 Nov) | reads every sensor, drives RGB beacon + pump, streams 1 JSON line/s over USB |
| Brain | **Raspberry Pi 3B+** | decisions (NORMAL / ACIDIC / INDUSTRIAL / RUNOFF / SOLVENT / SENSOR FAULT), dashboard, SIM800L SMS, pump/bottle sampling, CSV logging |

- Electronics build guide: `12_ELECTRONICS_MANUAL_1to5/AquaSentinel_LIVE_1to5_Electronics_Assembly_Manual.pdf` (Rev 2.0)
- Mechanical build guide: `02_LIVE_MODEL_1to5/00_ASSEMBLY_MANUAL/AquaSentinel_LIVE_1to5_Assembly_Manual_SOLIDWORKS.pdf` (30 pages, 7 Nov) **plus the one-page 15 Nov addendum in the same folder** — read the addendum before wiring; it supersedes the manual's rain pocket and pin map
- Board design + Nano firmware: `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1`
- Raspberry Pi software: `14_RASPBERRY_PI_SOFTWARE` (auto-start service, dashboard on port 8080, SMS, calibration tools)

**Full-size R3 design** — 66-part float in SOLIDWORKS (`05_R3_FULL_SIZE_CAD`), FEA in `06_SIMULATION`,
value-engineered product cost ≈ ₹48,000 (`07_COST_AND_BUSINESS`).

### Status, honestly

Sensors, beacon and pump are bench-proven; the model has **not yet been floated**. The Pi ↔ Nano link and the SIM800L
SMS path were **not yet verified end to end** at 14 Nov, pH is **not calibrated**, and no SMS numbers are configured.
See `PROJECT_IDENTIFICATION_AND_CRITICAL_PATH_2026-11-14.md` in the local folder.

## Folder map (local project)

| Folder | Contents |
|---|---|
| `00_PROJECT_CONTROL` | audit/critical path, reorg log, backup policy |
| `01_FINALE_PRESENTATION` | current 7-minute finale deck; 7 Nov submission in `01_FINALE_PRESENTATION/_SUBMISSION_RECORD_7Nov2026/` |
| `02_LIVE_MODEL_1to5` | 1:5 live model: assembly manual, 38 STLs, SOLIDWORKS parts/assembly, labels, printed dish |
| `05_R3_FULL_SIZE_CAD` | full-size R3: manual, BOM, CAD, drawings, design checks, renders, STEP/STL |
| `06_SIMULATION` | SOLIDWORKS Simulation studies and reports (guide pole, pier bracket) |
| `07_COST_AND_BUSINESS` | costed BOM, earlier estimate, value-engineered ≈ ₹48,000 cost + PDF |
| `08_VIDEOS` | pitch (FINAL v3), assembly, journey, marketing 60 s, raw teammate recordings |
| `09_SUBMISSIONS_AND_CERTIFICATES` | per-stage records: earlier stages, FDC Oct, FDC update 7 Nov, team change, certificates, portal, Maker Fest 2027 |
| `12_ELECTRONICS_MANUAL_1to5` | electronics manual Rev 2.0, Sensor Hub PCB v1.2 (design + firmware) |
| `13_CREATIVE_EXPERIENCE_STORYTELLING` | 3DEXCITE Creative Experience storyline, assets, story video, AR model, scripts |
| `14_RASPBERRY_PI_SOFTWARE` | Raspberry Pi 3B+ software: nano link, decisions, SMS, dashboard, logging, install |
| `99_ARCHIVE` | purge record and the SHA-256 manifest of the pre-purge state |

Number gaps (03, 04, 10, 11) are intentional: those folders were archived and then deleted on 14 Nov 2026, and their
numbers were not reused. See `00_PROJECT_CONTROL/PURGE_REPORT_2026-11-14.md`.

## Repository note

The public repository is an older, divergent snapshot. Heavy assets (decks, videos, CAD, manuals, archive) are
intentionally local-only and are **not** in git. Read `00_PROJECT_CONTROL/BACKUP_AND_VERSION_CONTROL.md` before
committing or pushing. Start at `00_START_HERE.md`.
