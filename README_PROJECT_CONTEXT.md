# AquaSentinel — master project context

**Start here.** This file is the compact, authoritative summary of what AquaSentinel is, what has been verified, and where every
piece of evidence lives. Update it whenever a verified understanding changes (see the change log at the end).

## 1. Snapshot
| | |
|---|---|
| Repository | https://github.com/soham0777/AquaSentinel (public), branch `main` |
| Audited commit | `840f1a65453bfc757174bfe90a9ab636c7dd5269` (2026-10-06, "Redesign the README and project site"); tag `v1.0-fdc` = `8ba1e44` (Final Design Concept submission) |
| Local copy | `C:\Users\dell\OneDrive\Desktop\AquaSentinel` (OneDrive-synced), checked out on `bench-demo`. Local branches, none pushed: `audit/engineering-knowledge-base` (these audit docs), `bench-demo` (firmware fixes P0-1 to P0-3), `scale-model-1to5` (the 1:5 printable model). Each is based on `840f1a6`, so the folder shows the other branches' files as untracked |
| Backups | `C:\Users\dell\OneDrive\Desktop\AquaSentinel_Backups`, every file listed with its SHA-256 in `SHA256SUMS.txt`. 18 Oct: full-history git bundle, ZIP of all files, docs ZIPs, and the four `v1.0-fdc` release files (editable PPTX deck, three 1080p videos) in `release_v1.0-fdc\`, which match GitHub's published digests. 20 Oct: a bundle of all local branches, a ZIP of the audit docs and the 1:5 model, and a ZIP of the private competition folder |
| Audit date | 2026-10-18 |
| Team | Team Sanjivani Hero's Journey, Sanjivani University, Kopargaon — AAKRUTI Innovation Competition 2026 (Robotics) |

## 2. What AquaSentinel is
A solar-powered catamaran float (≈ 1.0 × 0.8 × 0.9 m, 48.5 kg) that slides on a 2 in stainless pole clamped to a bridge pier, so the
river moves it up and down and turns it like a weathervane. Every 15 minutes it is meant to read pH, conductivity, optical DO,
turbidity, temperature and river level, decide on board (CPCB-style hard limits + a learned diurnal baseline, 2-of-3 persistence),
and on an event light a red beacon, send an LTE alert and pump a 250 mL sample into a bottle for a laboratory. Target site: the
Godavari at Kopargaon.

## 3. Verified status (one line each)
| Part | Status |
|---|---|
| Mechanical design (66 parts) | **Complete and reproducible.** `build.py` regenerates CAD, BOM and checks identically; 14/14 design checks pass |
| Structural checks | Hand calcs + 2 SOLIDWORKS static studies. FEA SF 4.4 is a fixed-end idealisation; pinned SF 3.10, **2.66 with the carriage couple** |
| Drawings (6 × A3) | Consistent with the CAD; **not regenerable** from the repo (view renders missing) |
| Firmware (ESP32) | On `main`: **does not compile**; dead probes read as normal water. On local branch `bench-demo` (20 Oct): compiles in both builds with 0 warnings (P0-1); a dead probe raises SENSOR_FAULT (P0-2); one sample per event, and the learned state survives a power cut (P0-3); 26 unit tests compile but **none has run on a board**. Still to write: actuator, beacon, stage sensor, clock and modem drivers |
| Electronics | **No schematic** (the `.kicad_sch` is prose); MOSFET rating and rail-polarity conflicts |
| Decision logic | Works on synthetic data: **4/4 events flagged at +30 min** (audit script). The state-machine and persistence flaws are fixed on `bench-demo` (P0-3); not yet run on hardware |
| 1:5 scale model | STL files for a Bambu H2D, with a print and assembly guide (branch `scale-model-1to5`). A scale model of the form and mechanism, not a working prototype |
| Data | **All synthetic** or design estimates; no field data |
| Website / viewer / dashboard | Run without errors; dashboard is a demo that can look live |
| Built or tested in water | **No** |

## 4. Key numbers (all reproduced in this audit unless stated)
Mass 48.54 kg (20 % catalogue-assumed) · draft 116.8 mm · freeboard 143.2 mm · reserve buoyancy 2.27 · GM_T 0.551 m · GZ max 180 mm
at 25° · drag at 1.5 m/s 142 N · pole: 54.8 MPa pinned (64.0 MPa with couple), 28.7 MPa fixed, FEA 38.3 MPa · carriage jam margin
8.62 (1.72 seized), float lag 17.7 mm (88.7 mm seized) · bracket span 2,678 mm, pole 2,978 mm · energy budget 3.39 Wh/day
(beacon excluded, not measured) · cost lines ₹1,38,000 (stated ₹1,34,000; v2 layout).

## 5. Ten things to know before changing anything
1. A failed probe read returns a normal-looking constant and the decision engine ignores validity flags → fail-silent "green".
   *Fixed on `bench-demo` (P0-2).*
2. Firmware modules `microsd_logger` and `telemetry_comm` belong to an older data model; `main.cpp` calls methods that do not exist.
   *Fixed on `bench-demo` (P0-1).*
3. Learned baselines live in RTC memory and vanish on any power loss/brown-out (LTE bursts make brown-outs likely).
   *Fixed on `bench-demo` (P0-3).*
4. Hard-limit trips re-trigger the sampler every reading; four bottles go to the first one or two events. *Fixed on `bench-demo` (P0-3).*
5. The 2 m stage range, 1.5 m/s current and 500 N debris load are assumptions; above the top stop the float is held under water.
6. The float sits in the bridge pier's wake; the weathervane argument assumes uniform flow.
7. The upward ultrasonic stage sensor is inside its blind zone near high water and sees the upper stop collar first.
8. EC ≤ 2250 µS/cm is CPCB Class E, not Class C; an unattended float sample cannot meet Water Act §21 evidence procedure.
9. `docs/engineering/*` and the cost estimate describe the older v2 design; the dataset README describes a different dataset.
10. Every build/analytics script overwrites committed files and writes CRLF on Windows: run them in a copy.

## 6. Where things are
| Folder | Contents |
|---|---|
| `mechanical/src` | Parametric design engine (params → parts → analysis → export → drawings) |
| `mechanical/cad`, `checks`, `drawings`, `simulation`, `solidworks` | Generated CAD/BOM/checks, drawing set, FEA studies and reports, SOLIDWORKS Pack and Go |
| `firmware/edge_node` | ESP32 PlatformIO project: does not compile on `main`, compiles on `bench-demo`. [firmware/BENCH_DEMO_PLAN.md](firmware/BENCH_DEMO_PLAN.md) (on `bench-demo`) is the plan to the finale |
| `mechanical/scale_model_1to5` | 1:5 printable model and the scripts that generate it (branch `scale-model-1to5`) |
| `competition_private` | Private, never committed: the semi-final preparation pack and `WORK_REGISTER.md`, the register of all work and presentations |
| `analytics` | Synthetic dataset + generator, decision reference, evaluation, proxy model, plume model |
| `hardware` | Text "schematic", power budget, v2 cost estimate, bench energy procedure |
| `docs` | GitHub Pages site (index, viewer, dashboard, media, deck) and v2 engineering notes |
| `project-management` | ENOVIA screenshots |

Conventions: millimetres and kilograms in the design engine; float frame origin on the pole axis at keel level, +X downstream, +Z up;
part numbers `AS3-xyz` with the hundreds digit = subsystem (1 guide, 2 hull/frame, 3 carriage, 4 sensing, 5 power/control,
6 sampler, 7 signalling/comms, 8 handling/harness, 9 fasteners).

## 7. Audit documentation map
| Document | Purpose |
|---|---|
| [docs/audit/REPOSITORY_INVENTORY.md](docs/audit/REPOSITORY_INVENTORY.md) | every path, sizes, status, missing inputs, release assets |
| [docs/audit/FILE_REVIEW_TRACKER.csv](docs/audit/FILE_REVIEW_TRACKER.csv) | per-file hash, status, method, notes, limitations |
| [docs/audit/ARCHIVE_MANIFEST.json](docs/audit/ARCHIVE_MANIFEST.json) | revision, refs, backups, checksums, inventory |
| [docs/audit/CODE_REVIEW.md](docs/audit/CODE_REVIEW.md) | file-by-file, line-referenced analysis and traces |
| [docs/architecture/SYSTEM_ARCHITECTURE.md](docs/architecture/SYSTEM_ARCHITECTURE.md) | context, subsystems, status matrix |
| [docs/architecture/DATA_FLOW.md](docs/architecture/DATA_FLOW.md) | field, design and analytics data flows and formats |
| [docs/architecture/INTERFACE_REGISTER.md](docs/architecture/INTERFACE_REGISTER.md) | mechanical, electrical, software and human interfaces |
| [docs/mechanical/MECHANICAL_DESIGN_REVIEW.md](docs/mechanical/MECHANICAL_DESIGN_REVIEW.md) | CAD, drawings, hydrostatics, FEA, electronics artefacts |
| [docs/analytics/ANALYTICS_AND_DATA_REVIEW.md](docs/analytics/ANALYTICS_AND_DATA_REVIEW.md) | datasets, algorithm maths, evaluation, transport model |
| [docs/audit/SECURITY_AND_RISK_REGISTER.md](docs/audit/SECURITY_AND_RISK_REGISTER.md) | secrets scan, software and physical risks, test sequence |
| [docs/research/TECHNICAL_RESEARCH.md](docs/research/TECHNICAL_RESEARCH.md) | external sources, comparisons, research directions |
| [docs/operations/SETUP_AND_REPRODUCIBILITY.md](docs/operations/SETUP_AND_REPRODUCIBILITY.md) | environment, commands, tested results, blockers |
| [docs/learning/ENGINEERING_KNOWLEDGE_BASE.md](docs/learning/ENGINEERING_KNOWLEDGE_BASE.md) | three-level teaching material, glossary, units, decision log |
| [docs/audit/OPEN_QUESTIONS_AND_NEXT_STEPS.md](docs/audit/OPEN_QUESTIONS_AND_NEXT_STEPS.md) | open questions, claims to reword, prioritised plan |
| [docs/audit/VISUAL_ASSET_CATALOGUE.md](docs/audit/VISUAL_ASSET_CATALOGUE.md) | all images and videos with thumbnail sheets |
| [docs/audit/AUDIT_PROGRESS_LOG.md](docs/audit/AUDIT_PROGRESS_LOG.md) | what was done in each phase |
| [docs/audit/verification/](docs/audit/verification/README.md) | read-only scripts that reproduce the audit's numbers |

## 8. Decisions waiting for the owner
1. ~~Download the four GitHub release assets~~ — done 2026-10-18: downloaded and verified (size and SHA-256 equal GitHub's digests).
2. ~~Install PlatformIO + ESP32 platform~~ — done 2026-10-20: VS Code and PlatformIO Core 6.2.0, `espressif32` pinned at 6.13.0.
3. Keep the audit docs on the audit branch, or merge them? (Anything under `docs/` is published by GitHub Pages.) Since 2026-10-20
   they are committed on the local branch `audit/engineering-knowledge-base`: not merged, not pushed.
4. ~~Which items of the prioritised plan to start~~ — P0-1, P0-2 and P0-3 done on `bench-demo` (2026-10-20). Next, from
   `firmware/BENCH_DEMO_PLAN.md`: demo mode, probe commissioning, drivers and the phone alert.
5. What to push to GitHub, and when. Nothing has been pushed: `main` on GitHub is still `840f1a6`.

## 9. Change log of this file
| Date | Change |
|---|---|
| 2026-10-18 | Created from the full audit of commit 840f1a6 |
| 2026-10-18 | Release `v1.0-fdc` assets downloaded with your approval and verified; archive now complete |
| 2026-10-20 | Updated after the first fixes: firmware status (P0-1 to P0-3 on `bench-demo`), the 1:5 model, the branch layout, the 20 Oct backups and the private work register |
