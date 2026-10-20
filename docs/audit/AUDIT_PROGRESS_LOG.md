# Audit progress log

Audit of `soham0777/AquaSentinel` at `840f1a65453bfc757174bfe90a9ab636c7dd5269`, carried out on 2026-10-18 on SOHAM-PC
(Windows 11 Pro). This log records what was done in each phase, with exact results, so later work can resume from evidence.

## Phase A — access, environment, destination
* Desktop resolves to `C:\Users\dell\OneDrive\Desktop` (OneDrive-redirected); target `...\Desktop\AquaSentinel` did not exist.
* Tools: Git 2.55 + LFS 3.7.1, Python 3.14.4 (numpy, matplotlib, Pillow, scipy, OCP/OpenCascade, pypdf, PyMuPDF, python-docx,
  python-pptx), Node 24, Java 21, ffmpeg 8.1.1. Not available: SOLIDWORKS, KiCad, PlatformIO/toolchain, any C/C++ compiler.
* `git ls-remote`: main = 840f1a6, tag v1.0-fdc = 8ba1e44 (lightweight). GitHub API: public, Python/HTML/C++/C, Pages enabled,
  release with 4 assets (PPTX + three 1080p videos, ≈ 279 MB) not in git.
* Note: git commands fail in the session's scratch folder (repository discovery walks into a protected `D:\WpSystem`); all git
  commands were run with `-C <path>`.

## Phase B — clone, integrity, baseline, backups
* `git clone --config core.autocrlf=false --config core.longpaths=true` → 283 files, 3 commits, `fsck --full --strict` clean,
  no LFS/submodules/symlinks.
* Line endings: `text=auto` produced CRLF in 64 files; set `core.eol=lf` locally, removed the 64 converted copies and restored them
  from git → **283/283 files byte-identical to their blobs**. (A first inventory taken before the fix is kept in the scratchpad.)
* Branch `audit/engineering-knowledge-base` created at 840f1a6 for the documentation; `main` untouched; nothing committed or pushed.
* Backups in `C:\Users\dell\OneDrive\Desktop\AquaSentinel_Backups`: full-history bundle (verified, test-restored: same tree
  16fff1fc…, same HEAD and tag, fsck clean) and a ZIP of all 283 files (every entry's SHA-256 checked). Checksums in `SHA256SUMS.txt`.

## Phase C — inventory and tracker
* 283 files classified (41 source, 5 config, 4 data, 17 docs, 74 images, 4 videos, 136 CAD, 1 archive, 1 other).
* Missing referenced inputs identified (calculations/, drawings/views/, renders/, animation/, test firmware, old BOM path).
* Outputs: [REPOSITORY_INVENTORY.md](REPOSITORY_INVENTORY.md), [FILE_REVIEW_TRACKER.csv](FILE_REVIEW_TRACKER.csv), [ARCHIVE_MANIFEST.json](ARCHIVE_MANIFEST.json).

## Phase D — line-by-line review
* All 41 source files read in full (firmware 17 + platformio.ini, analytics 5, mechanical engine 10, tools 3, viewer template,
  site 5), plus every text document, CSV and JSON. Symbol search proved the firmware cannot compile.
* Output: [CODE_REVIEW.md](CODE_REVIEW.md).

## Phase E — artefacts
* PDFs: deck (13 pages) and drawing set (6 A3) text extracted; all six drawing sheets and the check sheet viewed at full size.
* SOLIDWORKS reports: full text from document XML and 33 embedded images; both stress and displacement plots viewed.
* STEP/STL: 66 parts + assembly read with OpenCascade 7.9 (65/66 valid), STL manifold checks, volume and mass cross-checks.
* GLB parsed; `docs/viewer.html` proven to equal the template + GLB. Pack and Go listed and CRC-checked; SLDPRT binaries could not be
  opened. 74 images reviewed on contact sheets; 32 video key-frames reviewed; audio not reviewed.
* Outputs: [MECHANICAL_DESIGN_REVIEW.md](../mechanical/MECHANICAL_DESIGN_REVIEW.md), [VISUAL_ASSET_CATALOGUE.md](VISUAL_ASSET_CATALOGUE.md).

## Phase F — execution, reproducibility, security
* Isolated copy under `%TEMP%\as_repro` (from `git archive`); every project script run there, never in the repository.
* Analytics reproduced (dataset and weights identical apart from CRLF). Mechanical build reproduced (66 STL + GLB byte-identical, STEP
  identical except time stamp). Check sheet runs without its v2 table; drawings and triptych fail on missing inputs; viewer publish
  reproduces `docs/viewer.html`.
* Website, viewer and dashboard run in the built-in browser from a localhost static server: no console errors.
* Node syntax check of all JavaScript; Python AST parse of all .py files.
* Secret scan over all revisions: none found.
* Verification scripts written to `docs/audit/verification/`.
* Outputs: [SETUP_AND_REPRODUCIBILITY.md](../operations/SETUP_AND_REPRODUCIBILITY.md), [SECURITY_AND_RISK_REGISTER.md](SECURITY_AND_RISK_REGISTER.md),
  [ANALYTICS_AND_DATA_REVIEW.md](../analytics/ANALYTICS_AND_DATA_REVIEW.md).

## Phase G — research and learning
* Sources checked: CPCB criteria, Water Act §21, 40 CFR 136 holding times, USGS TM1-D3, IALA conventions, DFRobot wikis, AO3401A,
  INA226, JSN-SR04T, SIMCom A7670, ESP-IDF memory, LiFePO4 limits, Kashefipour–Falconer (via review table), CANARY, Burkhardt 2022,
  Leigh 2019, pier wake, ASTM A999 tolerance, station costs, CPCB 2022 stretches.
* Outputs: [TECHNICAL_RESEARCH.md](../research/TECHNICAL_RESEARCH.md), [ENGINEERING_KNOWLEDGE_BASE.md](../learning/ENGINEERING_KNOWLEDGE_BASE.md),
  [SYSTEM_ARCHITECTURE.md](../architecture/SYSTEM_ARCHITECTURE.md), [DATA_FLOW.md](../architecture/DATA_FLOW.md), [INTERFACE_REGISTER.md](../architecture/INTERFACE_REGISTER.md).

## Phase H — documentation and final checks
* Master context: [README_PROJECT_CONTEXT.md](../../README_PROJECT_CONTEXT.md); next steps: [OPEN_QUESTIONS_AND_NEXT_STEPS.md](OPEN_QUESTIONS_AND_NEXT_STEPS.md).
* Link validation, Jekyll/Liquid check, manifest update with audit outputs, ZIP of the documentation added to the backups.

## Release assets (after your approval, 2026-10-18)
* The four `v1.0-fdc` release files (279.2 MB) were downloaded with `curl.exe` into `AquaSentinel_Backups\release_v1.0-fdc\`.
  Size and SHA-256 of all four equal the values the GitHub releases API publishes.
* PPTX: ZIP CRC clean, 13 slides; slide text matches the committed PDF on 13/13. It adds speaker notes on every slide
  (471 words) that restate the slide claims. No hidden slides, comments, embeddings or external links.
* Videos: 1920×1080 H.264 (60, 50 and 30 fps), durations equal to the `docs/media/` copies. Frames at 5/30/60/90 s agree with
  the copies at 31–60 dB PSNR (8–13 dB for frames from different times), so they are the same edits.
* Manifest, checksums and restore instructions updated; a second documentation ZIP (`_v2`) replaces the first.

## Not done (and why)
* Firmware not compiled — no toolchain; installing PlatformIO + ESP32 platform needs your approval; it would fail anyway until fixed.
* SOLIDWORKS files not opened — software not installed.
* Video audio not reviewed — no speech-to-text tool available (this also applies to the 1080p release copies).
* KiCad not installed — the schematic file was read as text only.
