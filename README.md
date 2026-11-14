# AquaSentinel

**Team Sanjivani Hero's Journey · AG26-1500$41 · AAKRUTI 2026 · Robotics**
**India Geo Finale: booth 19 Nov, pitch 20 Nov 2026 (Pune)**

AquaSentinel is a solar-powered float that rides on a stainless guide pole clamped to a bridge pier.
Every 15 minutes it reads the river; when a spill passes it turns its light red, sends an SMS through the
SIM800L, and keeps a bottle of that water for the lab. No motor, no anchor — it rises and falls with the river.

## Current build (as of 14 Nov 2026)

**1:5 LIVE model** — a scale model built around the real, full-size sensors:

| Layer | Hardware | Role |
|---|---|---|
| Sensors | **PH-4502C** (pH, E-201-C electrode), **SEN0244** (TDS), **SEN0189** (turbidity), **DS18B20** (water temp), **DHT11** (air temp/humidity), **LDR** (light), **MQ-3** (vapour) | measure the water |
| Sensor hub | **Arduino Nano (ATmega328P)** on our own milled **Sensor Hub PCB v1.2** (104 × 72 mm, single-sided, KiCad, CNC-milled 12 Nov) | reads every sensor, drives RGB beacon + pump, streams 1 JSON line/s over USB |
| Brain | **Raspberry Pi 3B+** | decisions (NORMAL / ACIDIC / INDUSTRIAL / RUNOFF / SOLVENT / SENSOR FAULT), dashboard, SIM800L SMS, pump/bottle sampling, CSV logging |

- Electronics build guide: `12_ELECTRONICS_MANUAL_1to5/AquaSentinel_LIVE_1to5_Electronics_Assembly_Manual.pdf`
- Board design + Nano firmware: `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1`
- Raspberry Pi software: `14_RASPBERRY_PI_SOFTWARE` (auto-start service, dashboard on port 8080, SMS, calibration tools)

**Full-size R3 design** — 66-part float in SOLIDWORKS (`05_R3_FULL_SIZE_CAD`), FEA in `06_SIMULATION`,
value-engineered product cost ≈ ₹48,000 (`07_COST_AND_BUSINESS`).

## Folder map

| Folder | Contents |
|---|---|
| `01_FINALE_PRESENTATION` | the 7-minute finale deck (7 Nov submission), PDF backup, submission zip |
| `02_LIVE_MODEL_1to5` | the 1:5 live model: assembly manual, print STLs, SOLIDWORKS parts/assembly, design notes |
| `05_R3_FULL_SIZE_CAD` | full-size R3: manual, BOM, SOLIDWORKS, drawings, design checks, renders, STEP/STL |
| `06_SIMULATION` | SOLIDWORKS Simulation studies and reports (guide pole, pier bracket) |
| `07_COST_AND_BUSINESS` | costed BOM, Pi product cost, value-engineered ≈ ₹48,000 cost |
| `08_VIDEOS` | pitch (FINAL v3), journey, marketing 60 s, R3 assembly videos |
| `09_SUBMISSIONS_AND_CERTIFICATES` | per-stage records: earlier stages, FDC Oct, FDC update 7 Nov, team change, certificates, portal records, Maker Fest 2027 form |
| `12_ELECTRONICS_MANUAL_1to5` | live-model electronics assembly manual, Sensor Hub PCB v1.2 (design + firmware) |
| `13_CREATIVE_EXPERIENCE_STORYTELLING` | 3DEXCITE Creative Experience storyline, assets, source scripts (current) |
| `14_RASPBERRY_PI_SOFTWARE` | the Raspberry Pi 3B+ software: nano link, decisions, SMS, dashboard, logging, install |
| `99_ARCHIVE` | superseded material + reorganisation logs (see `09_Cleanup_2026-11-14`) |

Gaps in numbering (03, 04, 10, 11) are intentional: those folders were archived on 14 Nov 2026 —
see `99_ARCHIVE/09_Cleanup_2026-11-14/MANIFEST.md`. Nothing was deleted.

## Git

- `main` — current work; pre-cleanup state tagged `backup/pre-reorg-2026-11-14` (commit fd3c3a3).
- Working tree may show uncommitted changes from the pre-reorg era; the tag records the exact pre-cleanup state.
- Start here: `00_START_HERE.md`.
