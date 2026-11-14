# Full-size R3 — CAD, drawings and manual

The full-size AquaSentinel R3: a twin-hull float that rides up and down a 2-inch guide pole fixed to a bridge pier,
with its sensor cartridge in a well between the hulls. **66 part numbers, 144 parts** (including fasteners).

**Start with:** `00_ASSEMBLY_MANUAL/AquaSentinel_R3_Assembly_Manual_SOLIDWORKS.pdf` — 27 pages, 12 build steps.

## Folders

| Folder / file | What it is | Status |
|---|---|---|
| `00_ASSEMBLY_MANUAL/…_SOLIDWORKS.pdf` | 27-page assembly manual: 66 part numbers, 144 parts, 12 steps | Current |
| `01_BOM_R3.csv` | Bill of materials for the R3 | Current |
| `02_SOLIDWORKS_PackAndGo_FDC/` | Pack-and-Go **as submitted at the FDC**, kept as `AquaSentinel_R3_SOLIDWORKS_PackAndGo.zip`; the unzipped copy was removed on 14 Nov 2026 after 67/67 entries were verified identical | Frozen submission record |
| `03_SOLIDWORKS_2026_assembly_for_manual/` | Working SOLIDWORKS 2026 assembly used to render the manual (66 parts + assembly) + `views.zip` (100 derived renders) | Current working set |
| `04_Drawings/` | Six A3 sheets (AS3-DWG-01…06) + the combined drawing set PDF (the duplicate A3 PDF was removed 14 Nov) | Current |
| `05_Design_Checks/` | 14 design checks (`design_checks.json`), STEP validation, check sheet PNG | Current |
| `06_Renders/` | 15 renders used in the deck, manual and FDC | Current |
| `07_Parts_STEP_STL/` | Neutral **STEP** of all 66 R3 parts + `R3_parts_STL_exports.zip` (66 STL; the R3 has never been printed) | Current |
| `08_Assembly_STEP_GLB/` | Whole-assembly STEP + GLB (`AquaSentinel_R3_Assembly_MidWater.step`, `AquaSentinel_R3.glb`) | Current |

## Simulation

Structural studies (guide pole, pier bracket) are **not here** — they are in `06_SIMULATION`.
Headline results: pole safety factor 2.66 min; FEA peak 38.3 MPa; pinned 54.8 MPa; pinned + couple 64.0 MPa
against 316L yield 170 MPa.

## Notes

- The R3 is an **imported** SOLIDWORKS assembly, not native history-based design. The honest wording for the pitch is
  “assembled and simulated in SOLIDWORKS”, not “designed in SOLIDWORKS”.
- The R3 has **not been built**. All results are design-stage.
- `SOLIDWORKS_2026_manual_assembly` (an empty placeholder) was removed on 14 Nov 2026; it contained nothing.
- The FDC Pack-and-Go is the version the platform has. Do not edit it in place; edit `03_…` and export a new package if needed.
