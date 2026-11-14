# AquaSentinel R3 — 1:5 LIVE sensor model

Everything for the 1:5 LIVE model shown at the AAKRUTI finale (19–20 Nov 2026).
It is a 1:5 model of the R3 float on its pier column, built around the **real, full-size sensors**.

**Start with:** `00_ASSEMBLY_MANUAL/00_MANUAL_STATUS_READ_FIRST.md`, then the assembly manual PDF.

## Folders — what is current

| Folder / file | Contents | Status |
|---|---|---|
| `00_ASSEMBLY_MANUAL/AquaSentinel_LIVE_1to5_Assembly_Manual_SOLIDWORKS.pdf` | Step-by-step assembly, A4, **30 pages, 24 steps** (safety, parts, dry-fit, steps A1–D7, operation, troubleshooting, appendices) | Current, with the caveats in the status note |
| `00_ASSEMBLY_MANUAL/images/` | The manual's 73 illustrations (PNG), rendered from the final STL files in their assembled positions | Current; used by the PDF |
| `01_FINAL_STL/` | **38 STL files** + `PARTS_LIST.csv` (37 listed parts; the extra file is the `LD-S16_sample_bottle_printable.STL` variant) | Current print set |
| `02_CAD_SOLIDWORKS/` | SOLIDWORKS parts of the 17 **LD** parts, with descriptive names; `02_CAD_SOLIDWORKS/reference/` = supplied SEN0189 turbidity sensor model | Current part models |
| `04_DESIGN_NOTES/` | `LIVE_model_design_notes.md` (design rationale, 31 Oct), `verification_summary.json`, `print_list.csv` (36 files), `CLEANUP_LOG_2026-11-05.csv` | Historical reference — partly outdated |
| `05_SOLIDWORKS_ASSEMBLY/` | The complete 1:5 assembly (`AquaSentinel_LIVE_1to5_Assembly.SLDASM`), all parts as used for the manual renders, and `05_SOLIDWORKS_ASSEMBLY/views/` | Current assembly |
| `06_PART_LABELS_A4/` | A4 sheet of part labels for the booth (PDF + PNG) | Current |
| `07_PRINTED_DISH_LD-S17/` | The 3D-printed sensing dish: print settings, STL, STEP, F3D, preview | Current |

**Part names:** `LD-` = new for the LIVE model · `ORIG-` = unchanged part of the original 1:5 kit · `P-` = bought/probe stand-in.

## Status (14 Nov 2026)

- All parts are printed (team report). The plinth `LD-S01` is assumed printed in one piece.
- CAD geometry has been checked; the printed set has **not yet been trial-assembled and the model has not been floated**.
  Do the dry-fit list in section 0 of the manual before gluing.
- The sensors, beacon and pump have been **bench-tested** (12–13 Nov) through the Sensor Hub PCB.
- Open build points are in manual Appendix D and in `00_PROJECT_CONTROL/PROJECT_IDENTIFICATION_AND_CRITICAL_PATH_2026-11-14.md`.

## Known differences between the manual and the final build

The 30-page manual was generated on 7 Nov, before the last hardware change. In the PDF:

- the meteorological plate (`LD-S10b`) still shows the **rain plate + LM393** that were later removed — the final build has **7 sensors and no rain sensor**;
- the wiring pin map is from the **ADS1115 era**. The current pin map is in the Sensor Hub PCB folder and the Nano firmware:
  `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1` and `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1/firmware`;
- the cover says “37 printed parts”; the print folder contains **38 STL files** because the sample bottle has two variants.

The **electronics manual Rev 2.0 (14 Nov)** is the authoritative document for anything electrical.

## Not stored here

- `03_PRINT_RECORDS` (sliced plates and print status) was referenced by an older README but **does not exist** in this folder or the archive.
- The scripts that generated the manual (`make_images.py`, `build_manual.py`, `manual_content.py`) are **not present**; the finished PDF and its images are. Rebuilding the PDF would need those scripts recovered first.

## Archive

The 31 Oct concept renders and the original kit's Scale Model Guide were moved to
`99_ARCHIVE/11_LiveModel_superseded_31Oct2026/` on 14 Nov 2026. They are still available, but they are not the final design.
