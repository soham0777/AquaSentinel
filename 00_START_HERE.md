# AquaSentinel: start here

**Team Sanjivani Hero's Journey** · AG26-1500$41 · Sanjivani University, Kopargaon · AAKRUTI 2026 · Robotics

🏆 **Encouragement Award, AAKRUTI 2026 India Finale** (Dassault Systèmes, DS Campus, Pune, 20 Nov 2026). Sanjivani University also received Outstanding College Participation. Sources: the organisers' results post on LinkedIn and Punekar News, 20 Nov 2026 (links in `README.md`).

AquaSentinel is a float on a guide pole clamped to a bridge pier. Every 15 minutes it reads the river. When a spill passes, it turns its beacon red, sends an SMS and keeps a bottle of that water for the lab.

> **This file is the map.** Last checked **21 Nov 2026**, after the folder was reorganised into the layout below. Every move is listed in `11_PROJECT_RECORDS_AND_AUDITS/REORG_LOG_2026-11-21.csv`.

---

## 1. Folder map

| Folder | What lives there |
|---|---|
| `01_PITCH_20Nov/` | `00_GLANCE_CARD_Bhakti_1page` · `01_FINAL_Pitch_Script_Bhakti_20Nov` (PDF + Word) · `02_Pitch_Deck_7min_AS_SUBMITTED_17Nov` (PPTX + PDF; the organisers downloaded it on 17 Nov, never edit) · `03_QA_Mechanical_Design_Prasad_Tanmay` · `04_Deck_Fact_Check_every_number_and_source.md` |
| `02_FILMS/` | pitch film and journey film (both have music: play muted, or talk over them), R3 assembly animation, teammates' raw recordings |
| `03_BOOTH_PRINTS/` | 21 numbered print files and `00_PRINT_ORDER_19Nov.pdf` (size and copies in each name); HTML sources in `_source_html/` |
| `04_R3_FULL_SIZE_DESIGN/` | R3 assembly manual, parts list (CSV + PDF), Pack and Go, native SOLIDWORKS parts, 6 drawings, 14 design checks, renders, STEP/STL, and the FEA in `09_Simulation_FEA_pole_and_bracket/` |
| `05_LIVE_MODEL_1to5/` | 1:5 LIVE model: manual (read `00_MANUAL_STATUS_READ_FIRST.md` and the 15 Nov addendum first), 38 STLs, SOLIDWORKS parts and assembly, design notes, printed dish |
| `06_ELECTRONICS_AND_PCB/` | electronics manual Rev 2.0, Sensor Hub PCB v1.2 (KiCad, G-code, build and picture guides, Nano firmware v2), electronics CAD |
| `07_RASPBERRY_PI_SOFTWARE/` | the Pi station. Start with `aquasentinel/RASPBERRY_PI_STEP_BY_STEP.md`. Firebase set-up in `aquasentinel/cloud/FIREBASE_SETUP.md` |
| `08_COST_AND_BUSINESS/` | **`00_COST_SUMMARY_READ_FIRST.md`** (the only figures to quote), the full working, the cost sheet PDF |
| `09_CREATIVE_EXPERIENCE_3DEXCITE/` | 3DEXCITE storyline, assets, renders, AR model, story video |
| `10_SUBMISSIONS_AND_CERTIFICATES/` | one sub-folder per stage, certificates, and `08_Finale_submission_7Nov2026_FROZEN`. **Frozen records: never edit** |
| `11_PROJECT_RECORDS_AND_AUDITS/` | audits, reorganisation and purge reports, backup policy, the purge record, AI working notes (local only) |
| `99_OLDER_VERSIONS_DO_NOT_USE/` | the deck before 16 Nov, earlier film cuts, superseded cost estimates, old CAD zips. Kept on the laptop only |
| `docs/` | the GitHub website (soham0777.github.io/AquaSentinel), films and images, and `media/award/` (official photos, © Dassault Systèmes) |

## 2. Numbers to quote

₹47,886 a float at 100 units (≈ ₹48,000) · ₹64,616 first prototype · ₹8,000 a month · 66 part designs, 144 pieces, 48.5 kg · 14/14 design checks · lowest pole safety factor 2.66 · 296 polluted stretches in India, 54 in Maharashtra.

**Never say** "designed natively in SOLIDWORKS". The geometry started in our Python code; on 16 Nov we rebuilt all 66 parts as native SOLIDWORKS features (712). Never call a render a photo.

## 3. Status (21 Nov 2026)

**Proven:** all 7 sensors, the beacon and the pump through our own board (13 Nov) · the Pi reads the Nano live · pH, turbidity and MQ-3 calibrated · live cloud dashboard https://aquasentinel-live.web.app (18 Nov) · R3: 14/14 CAD checks and 2 FEA studies.

**Not yet:** an SMS received end to end (the SIM800L's serial port was busy on 18 Nov; fix in the Pi guide) · the 1:5 model floated · the full-size R3 built or tank-tested.

## 4. Keeping it safe

- **Never commit or share `07_RASPBERRY_PI_SOFTWARE/aquasentinel/secrets.json`** (SMS numbers, Firebase key). `.gitignore` excludes every `secrets.json`.
- Kept off GitHub on purpose: the team-change emails and spreadsheets, the portal access record, AI notes, `99_OLDER_VERSIONS_DO_NOT_USE`, and the 132 MB R3 animation (over GitHub's 100 MB limit).
- Do not rename CAD part files: SOLIDWORKS assemblies find their parts by file name.

### History of cleanups

| Date | What happened | Record |
|---|---|---|
| 6–7 Nov | first cleanup; R3 folders numbered; submissions split by stage | `11_PROJECT_RECORDS_AND_AUDITS/PURGE_REPORT_2026-11-14.md` |
| 14 Nov | workspace reorganised; old versions deleted with the project lead's approval | `WORKSPACE_REORG_REPORT_2026-11-14.md` |
| 14–15 Nov | file, PNG and CAD audits | `FILE_AUDIT_2026-11-14.md`, `PNG_AUDIT_2026-11-15.csv`, `CAD_AUDIT_2026-11-15.md` |
| 17 Nov | project-wide cost audit; booth prints corrected | this table (earlier version) |
| 19 Nov | 25 superseded items sent to the Recycle Bin (scripts v4–v6, duplicate print PDFs, build folder, old labels) | this table |
| 21 Nov | folder reorganised into the layout above (moves only); award added; published to GitHub on top of the existing history | `REORG_LOG_2026-11-21.csv` |
