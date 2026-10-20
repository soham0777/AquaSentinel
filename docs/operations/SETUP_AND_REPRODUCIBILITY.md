# Setup and reproducibility

What runs, on what, with which command, and what actually happened when it was run on 2026-10-18. Commands are for Windows
PowerShell on this PC; the repository lives at `C:\Users\dell\OneDrive\Desktop\AquaSentinel`.

## 1. Verified environment (this PC)
| Item | Version / state |
|---|---|
| OS | Windows 11 Pro 10.0.26200, 64-bit |
| Git / Git LFS | 2.55.0.windows.3 / 3.7.1 (LFS not needed: repo has no LFS objects) |
| Python | 3.14.4 at `C:\Python314` — numpy 2.4.6, matplotlib 3.11.0, Pillow 12.2.0, scipy 1.18.0, pandas 3.0.3, OCP (OpenCascade) 7.9.3.1, pypdf 6.18.0, PyMuPDF 1.28.2, python-docx 1.2.0 |
| Node.js | 24.14.1 (used only for `node --check` syntax checks) |
| ffmpeg | 8.1.1 (video metadata and frames) |
| Not installed | SOLIDWORKS, KiCad, PlatformIO / ESP32 toolchain, any C/C++ compiler, FreeCAD, OpenCV |

The project needs only `numpy`, `matplotlib` and `Pillow` for its Python code (stated in the READMEs; there is no `requirements.txt`).

## 2. Repository-specific setup notes
1. **Line endings.** `.gitattributes` sets `* text=auto`. On Windows the default checkout converts text files to CRLF even with
   `core.autocrlf=false`. This clone has `core.eol=lf` set locally so files equal their committed bytes. Any new clone:
   ```powershell
   git clone --config core.autocrlf=false --config core.eol=lf --config core.longpaths=true https://github.com/soham0777/AquaSentinel.git
   ```
2. **OneDrive.** The Desktop is synchronised by OneDrive, including `.git`. Mark the folder "Always keep on this device" so files are
   never cloud-only placeholders, and avoid editing the same clone from two machines.
3. **Scripts overwrite tracked files.** `mechanical/src/build.py`, `drawings.py`, `check_sheet.py`, `publish.py`,
   `analytics/dataset/generate_water_quality_timeseries.py`, `analytics/train_proxy_anomaly_engine.py`, `analytics/evaluate.py` and
   `advection_dispersion_model.py` write next to the files they came from. Run them in a separate copy unless you intend to update
   the committed outputs. On Windows they also write CRLF line endings, which shows up as whole-file diffs.
4. **Path length.** Windows long-path support is off in the registry (`LongPathsEnabled = 0`); keep working copies at short paths.

## 3. Make a disposable working copy
```powershell
$copy = Join-Path $env:TEMP 'as_work'
git -C C:\Users\dell\OneDrive\Desktop\AquaSentinel archive --format=tar HEAD -o "$env:TEMP\as_work.tar"
New-Item -ItemType Directory $copy | Out-Null
tar -xf "$env:TEMP\as_work.tar" -C $copy
```
(`git worktree add` is an alternative that keeps history; either way, never point the scripts at the Desktop clone.)

## 4. Runnable components — tested results
| Component | Prerequisites | Command (in the copy) | Result on 2026-10-18 | Blockers / notes |
|---|---|---|---|---|
| Synthetic dataset | Python 3 | `python analytics\dataset\generate_water_quality_timeseries.py` | OK, 2,880 rows; content identical to the committed CSV (CRLF only) | — |
| Detector benchmark | numpy, matplotlib | `python analytics\evaluate.py` | OK: NORMAL 2808, WATCH 15, EVENT 57, 25 triggers; plot written | Does not compute latency/recall/false alarms (use the audit script) |
| Proxy weights | numpy | `python analytics\train_proxy_anomaly_engine.py` | OK: threshold 4.011, recall 87.5 %, FPR 0.53 % (in-sample); header identical (CRLF only) | Writes into `firmware\edge_node\include` |
| Plume model | numpy, matplotlib | `python analytics\advection_dispersion_model.py` | OK: D Fischer 69.97, K&F 777.92, mean 423.95 m²/s | Formula issue (see analytics review) |
| Mechanical build | numpy | `python mechanical\src\build.py` | OK in 28.6 s; 14/14 checks PASS; 66 STL + GLB byte-identical, 67 STEP identical except time stamp, BOM/checks identical (CRLF only) | Also writes Low/High-water assemblies (git-ignored) |
| Check sheet | matplotlib | `python mechanical\src\check_sheet.py` | OK, but the v2 → R3 table is empty | Needs `..\calculations\verified_design_calcs.json` (absent) |
| Drawing set | matplotlib, Pillow | `python mechanical\src\drawings.py` | **Fails**: `KeyError: 'ga_elev'` | Needs `mechanical\drawings\views\*.png` + `shots.json` from the viewer capture step (§5) |
| Standalone viewer | — | `python mechanical\src\publish.py viewer` | OK; output identical to `docs\viewer.html` | Copy to `docs\viewer.html` is manual |
| Motion triptych | Pillow | `python mechanical\src\publish.py triptych` | **Fails**: `renders\motion_low.png` missing | Needs renders from the viewer |
| Assembly GIF | Pillow | `python mechanical\src\publish.py gif` | Prints "no gif frames" | Needs `animation\gif_frames` from the viewer |
| Website, viewer, dashboard | browser | `python -m http.server 8777 --bind 127.0.0.1 --directory docs` then open `http://127.0.0.1:8777/` | OK in the built-in browser: pages render; viewer lists 66 parts, 14/14 checks; dashboard demo works; no console errors | Viewer needs internet (three.js from jsDelivr) |
| STEP read check | browser + `serve.py` | `python mechanical\tools\serve.py` then open `http://127.0.0.1:8765/tools/step_check.html` | Not re-run (writes `checks\step_validation.json`); equivalent independent check done with OpenCascade in Python: 66/66 read, 65/66 valid | Needs internet for occt-import-js |
| Firmware build | PlatformIO + ESP32 platform | `cd firmware\edge_node; pio run` | **Not run** (no toolchain; installing it downloads several hundred MB). Static analysis shows it will fail to compile | Fix the issues in CODE_REVIEW F1 first |
| Firmware flash | ESP32 board, USB | `pio run -t upload` | Not run | Requires hardware |
| SOLIDWORKS model | SOLIDWORKS (version not stated; the old README badge said 2019, the v2 guide 2026 Student) | Unzip Pack and Go, open `AquaSentinel_R3_Assembly.SLDASM` | Not run | No SOLIDWORKS on this PC |
| FEA studies | SOLIDWORKS Simulation | open the two `*_Simulation.SLDPRT` | Not run; reports reviewed | — |

## 5. Regenerating the drawings (documented pipeline, not reproduced)
1. `python mechanical\tools\serve.py` (serves `mechanical\` on `http://127.0.0.1:8765`, accepts POST `/save`).
2. Open `http://127.0.0.1:8765/viewer/template.html?capture=1` in a WebGL browser.
3. Run the contents of `mechanical\tools\drawing_shots.js` in the page console → writes `drawings\views\*.png` through `/save`.
   `shots.json` (scale and centre per view, read by `drawings.py`) is not written by this script and is not in the repository;
   it must be recreated from the `SH` table in `drawing_shots.js` (keys `s`, `center`, `view`).
4. `python mechanical\src\drawings.py` → six PNG sheets + PDF.

## 6. Audit verification scripts
All read-only; they read the repository and print results (see [verification/README.md](../audit/verification/README.md)).
```powershell
cd C:\Users\dell\OneDrive\Desktop\AquaSentinel
python docs\audit\verification\detector_event_metrics.py
python docs\audit\verification\firmware_engine_port.py
python docs\audit\verification\pole_carriage_couple.py
python docs\audit\verification\dispersion_check.py
python docs\audit\verification\stage_sensor_geometry.py
python docs\audit\verification\data_integrity_checks.py
```

## 7. Documented deployment targets (not verified)
* **Edge device:** ESP32-WROOM-32E carrier board (not designed yet), PlatformIO `env:esp32dev`, Arduino framework. Before the first
  flash: assign Modbus addresses/baud to each probe, set the RTC, and verify the rail polarity on the real board.
* **Website:** GitHub Pages from `docs/` on `main` (`https://soham0777.github.io/AquaSentinel/`). Note that Markdown added under
  `docs/` is published and processed by Jekyll unless a `.nojekyll` file exists.
* **No server component exists** for telemetry or SMS; one must be designed (broker/API, storage, alert routing, authentication).

## 8. Environment variables and secrets
None are read by any code in the repository. Future telemetry credentials (APN, broker passwords, device keys) must live outside git
(device NVS provisioned at manufacture, or a local `secrets.h` listed in `.gitignore`).
