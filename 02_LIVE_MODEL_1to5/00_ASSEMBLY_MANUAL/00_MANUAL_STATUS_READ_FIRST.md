# Read this before using the 1:5 assembly manual

**The PDF beside this note** — `AquaSentinel_LIVE_1to5_Assembly_Manual_SOLIDWORKS.pdf` — is the current mechanical assembly manual:
**30 pages, 24 steps**, generated **7 Nov 2026** from the SOLIDWORKS assembly. Read it with
`AquaSentinel_LIVE_1to5_Assembly_Manual_ADDENDUM_2026-11-15.pdf` (one page), which corrects the electronics and the
meteorological plate to the final 7-sensor build.

## What is still correct

- The 38 printed parts and their assembly order (sections A–D).
- The dry-fit list, glue points, clearances, the sensing-dish and bayonet steps, the park/travel positions.
- All illustrations in `images/`.

## What the addendum corrects — do not wire from the 30-page PDF

1. **Rain sensor.** The meteorological plate picture still shows a rain plate and an LM393 board. They were removed.
   The final build has **7 sensors and no rain sensor**; the rain pocket and LM393 bay stay empty.
2. **Pin map.** The wiring pages come from the earlier ADS1115 design. The current pin map is:
   - `12_ELECTRONICS_MANUAL_1to5/AquaSentinel_LIVE_1to5_Electronics_Assembly_Manual.pdf` — **Rev 2.0, 14 Nov**, authoritative;
   - `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1/firmware/aquasentinel_nano/aquasentinel_nano.ino` — the actual firmware.
3. **Part count.** The cover says “37 printed parts”. The print folder has **38 STL files** because the sample bottle has two variants
   (`LD-S16_sample_bottle_printable` and the preview). 37 is the number of printed parts.

Everything electrical is in the electronics manual Rev 2.0. Use this PDF for mechanics only.

A corrected mechanical manual should be reissued after the finale; the scripts that generated this PDF are not stored in the project.
