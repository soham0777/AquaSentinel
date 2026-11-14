# 1:5 LIVE model — electronics manual and Sensor Hub PCB

**Authoritative electrical document:** `AquaSentinel_LIVE_1to5_Electronics_Assembly_Manual.pdf`
— **Revision 2.0, 14 November 2026, 17 pages**.

It covers the final architecture: **Arduino Nano (ATmega328P) on our own Sensor Hub PCB v1.2** reading seven sensors,
streaming one JSON line per second over USB to the **Raspberry Pi 3B+**, which decides, drives the beacon/pump and sends SMS through the SIM800L.

## Folders

| Folder / file | What it is | Status |
|---|---|---|
| `AquaSentinel_LIVE_1to5_Electronics_Assembly_Manual.pdf` | Rev 2.0 manual, 17 pages | **Current** |
| `PCB_SENSOR_HUB_v1/` | Sensor Hub PCB v1.2: KiCad file, DRC report, CNC G-code, placement/soldering/continuity/power-up guides, Nano firmware | **Current** |
| `PCB_SENSOR_HUB_v1/firmware/aquasentinel_nano/aquasentinel_nano.ino` | The firmware that actually runs on the Nano | **Current** |
| `PCB_SENSOR_HUB_v1/firmware/wiring_test.py` | Bench wiring test helper | Current |
| `PCB_SENSOR_HUB_v1/older_versions/` | Earlier board layouts (`v1_145x90`, `v1_1_84x84`) | Superseded — do not mill |
| `images/` | 63 figures for the manual (`images/bay/`, `images/diagrams/`, `images/live/`, `images/parts/`) | Current |
| `_build_v2/` | The build source of the current PDF (`manual_v2.html`, SVGs, `verify_pdf.py`); `manual_v2.pdf` is byte-identical to the manual above | Source, keep |
| `CAD/` | SOLIDWORKS working copies and electronics models | Working set — see warning below |

## `CAD/` warning — do not reorganise

These are SOLIDWORKS assemblies with external references. **Moving or renaming individual parts breaks the assemblies.**

| Sub-folder | What it is |
|---|---|
| `CAD/bay_v2/`, `CAD/live_v2/` | Current electronics-bay and LIVE assembly with electronics |
| `CAD/bay_copy/`, `CAD/live_copy/` | Copies used to render the manual — older than `*_v2` |
| `CAD/parts_new/` | Electronic modules modelled for the bay. **`E27_Rain_plate`, `E28_Rain_LM393`, `E02_ADS1115`, `E03_DS3231`, `E07_Buck_C`, `E12_Level_converter` are legacy parts** not used in the final build (no rain sensor; no ADS1115/RTC; one 9 V step-up + one 4.0 V step-down). Do not delete them from the CAD without checking which assemblies reference them. |

## Before the booth

- The manual is current, but the **Pi ↔ Nano USB link and the SIM800L SMS path have not yet been verified end to end**.
- The firmware still carries a stale comment saying “PCB v1.1 (84 × 84 mm)”; the build is **v1.2, 104 × 72 mm**. Comment only — the pin defines are correct.
- `12_…/…` is not the software. The Pi-side software is in `14_RASPBERRY_PI_SOFTWARE`.

Old Pi-direct ADS1115 electronics are archived in `99_ARCHIVE/09_Cleanup_2026-11-14/03_ELECTRONICS_RASPBERRY_PI_old_ADS1115_design/`.
