# Start here

**AquaSentinel** is a solar-powered float, designed to ride a stainless guide pole clamped to a bridge pier on the Godavari
at Kopargaon. Every 15 minutes it reads pH, conductivity, dissolved oxygen and turbidity; when a spill passes it decides on
the float itself, turns its beacon red, alerts the water-works and bottles **a sample for a certified lab**.
Team Sanjivani Hero's Journey · AAKRUTI Innovation Competition 2026 · Robotics theme.

> **Honest status:** designed and simulated, **not yet built or tested in water**. Say "designed", not "built".
> The firmware compiles but has not run on hardware; the dashboard is a demo with synthetic data.

## I want to…

| I want to… | Open this |
|---|---|
| see the project in a browser | the live site <https://soham0777.github.io/AquaSentinel/> (source: [`docs/index.html`](docs/index.html)) |
| spin the 3D model | [`docs/viewer.html`](docs/viewer.html), or the live site's "Explore in 3D" |
| see the command dashboard demo | [`docs/dashboard/index.html`](docs/dashboard/index.html) |
| read the competition deck (as submitted) | [`docs/presentation/`](docs/presentation) (note the "superseded figures" list in its README) |
| check what we may claim, and the evidence for each claim | [`engineering/claims_register.md`](engineering/claims_register.md) |
| prepare for jury questions | [`engineering/jury_QA.md`](engineering/jury_QA.md) |
| read or change the decision logic | [`analytics/detector.py`](analytics/detector.py) (Python) and [`firmware/edge_node/src/anomaly_engine.cpp`](firmware/edge_node/src/anomaly_engine.cpp) (C++) |
| build the firmware | [`firmware/README.md`](firmware/README.md): `cd firmware/edge_node && pio run -e esp32dev` |
| see the costs and the power budget | [`hardware/`](hardware) |
| open or rebuild the CAD | [`mechanical/README.md`](mechanical/README.md) |
| 3D-print the 1:5 table model | [`mechanical/scale_model_1to5/README.md`](mechanical/scale_model_1to5/README.md) |
| check that everything still works | `bash tools/verify_all.sh` ([`tools/README.md`](tools/README.md)) |
| know what was moved and what is still open | [`docs/REORG_NOTES.md`](docs/REORG_NOTES.md) |

## Folder map

| Folder | What is inside | Open first |
|---|---|---|
| [`docs/`](docs) | the **GitHub Pages website**: home page, 3D viewer, dashboard demo, images, videos, the submitted deck | [`docs/README.md`](docs/README.md) |
| [`engineering/`](engineering) | claims register (every public number and its evidence) and the jury Q&A | [`engineering/README.md`](engineering/README.md) |
| [`mechanical/`](mechanical) | R3 parametric CAD engine, STEP/STL/GLB, SOLIDWORKS Pack and Go, drawings, simulation, 1:5 scale model | [`mechanical/README.md`](mechanical/README.md) |
| [`firmware/`](firmware) | ESP32 controller (PlatformIO) and the bench-demo plan | [`firmware/README.md`](firmware/README.md) |
| [`analytics/`](analytics) | Python reference of the decision logic, synthetic dataset, plume model | [`analytics/README.md`](analytics/README.md) |
| [`hardware/`](hardware) | electronics notes, power budget, cost estimate, bench test procedure | [`hardware/README.md`](hardware/README.md) |
| [`calculations/`](calculations) | home for the hand-calculation scripts (**not yet in the repository**, see its README) | [`calculations/README.md`](calculations/README.md) |
| [`tools/`](tools) | read-only checks: link checker, C++-vs-Python parity test, `verify_all.sh` | [`tools/README.md`](tools/README.md) |
| [`project-management/`](project-management) | ENOVIA project plan (Gantt, summary) | [`project-management/README.md`](project-management/README.md) |
| [`archive/`](archive) | superseded documents, kept for the record (never deleted) | [`archive/README.md`](archive/README.md) |
| `.github/workflows/` | CI: builds the firmware, replays the detector, checks links (does not touch the website deploy) | [`ci.yml`](.github/workflows/ci.yml) |

Not in this repository, by design: the team's local-only `private/` folder (decks, videos, audit notes, drafts), and any
Wi-Fi / Telegram / modem secrets (they belong in an untracked `firmware/edge_node/include/secrets.h`). Both are in `.gitignore`.
