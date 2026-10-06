# Mechanical design · AquaSentinel R3

Everything mechanical is generated from one parametric source in [`src/`](src). Change a dimension in
[`src/params.py`](src/params.py), rebuild, and the geometry, checks, CAD exports, BOM and drawings update together.

## What is here

| Folder | Contents |
|---|---|
| [`solidworks/`](solidworks) | **SOLIDWORKS Pack and Go**: `AquaSentinel_R3_Assembly.SLDASM` + all 66 part files, materials and part numbers assigned |
| [`cad/parts/`](cad/parts) | one STEP + STL per part, in its local frame |
| [`cad/assembly/`](cad/assembly) | assembly STEP at mid water, GLB scene used by the web viewer |
| [`cad/BOM_R3.csv`](cad/BOM_R3.csv) | bill of materials: part no, qty, material, process, mass, CAD file |
| [`simulation/`](simulation) | SOLIDWORKS Simulation studies of the guide pole and pier bracket: parts, plots, full reports |
| [`drawings/`](drawings) | 6 × A3 drawing set (PNG per sheet + one PDF) |
| [`checks/`](checks) | `design_checks.json`, the check sheet, STEP validation results |
| [`src/`](src) | params, geometry kernel, parts, analysis, exporters, drawings |
| [`viewer/`](viewer) · [`tools/`](tools) | 3D viewer source, local preview server, STEP validation page |

## The design in one paragraph

A twin-hull float with a guide carriage at its bow. The carriage runs on a 2 in Sch 40S SS316L pole clamped to a bridge
pier. When the river rises or falls, buoyancy moves the float up or down the pole on eight concave UHMW-PE rollers (two tiers,
350 mm apart). The current turns the float so it trails downstream like a weathervane, so the pole carries no torque. A
sensor cartridge hangs in a protected well between the hulls and lifts out through a deck hatch. A shaded pod holds the
electronics and battery, an autosampler stores water samples, and a beacon shows the station's status to people on the bank.

## Key numbers (from [`checks/design_checks.json`](checks/design_checks.json))

Mass 48.5 kg · draft 117 mm · freeboard 143 mm · reserve buoyancy 2.27× · GM<sub>T</sub> 0.55 m · GZ positive to 60°
(max 180 mm at 25°) · float drag at 1.5 m/s 142 N · pole 54.8 MPa pinned hand calc (SF 3.1); 38.3 MPa in SOLIDWORKS
Simulation (SF 4.4) · carriage jam margin 8.6× (1.7× with seized rollers) · 0 clashes over the full 2 m travel.

> **Design estimates, not test results.** Probe, battery, PV and pump masses are catalogue-class values and should be
> replaced with weighed ones. The 2.0 m stage range, 1.5 m/s current and 500 N debris load are design assumptions; confirm
> the stage range from the site gauge record before cutting the pole.

## How R3 improved on v2

| v2 | R3 | Why |
|---|---|---|
| Pole through the centre of the float, passing through the pod, canopy and beacon (a real clash) | Pole at the bow, between the two hull bows | Nothing sits on the pole axis; the float can be released forward |
| Round pole + collar called "1-DOF" (it is not: the float can rotate) | Rotation about the pole is designed in (weathervane) | The pole carries no torque; only the rub rails can touch the pier |
| Mass 25.4 kg from a hand list | 48.5 kg from CAD mass properties | Hulls enlarged to 1000 × 230 × 260 mm to keep reserve buoyancy ≥ 2 and freeboard ≥ 100 mm |
| Roller tiers 250 mm apart | 350 mm apart | Bow mounting puts buoyancy 406 mm from the pole; this keeps the carriage from self-locking |
| Float removable only by dismantling the pole | Front half of the carriage is a hinged gate with two T-handle pins | Retrieve the float before a flood, no tools, no climbing |
| Sensors fixed under the hull | Pull-up cartridge: four probes, wiper and sample intake | Clean and calibrate from the deck; colour bands key each probe to its port |
| Electronics box in the sun | 20 W PV canopy shades the pod and sampler, hinges up for access | LiFePO4 must not be charged above about 45 °C |

## Open it in SOLIDWORKS

Unzip `solidworks/AquaSentinel_R3_SOLIDWORKS_PackAndGo.zip` and open `AquaSentinel_R3_Assembly.SLDASM`.
For the simulation load case on the pole, use 643 N at mid-span plus 81 N/m with the brackets 2678 mm apart.

## Rebuild from source

Requires Python 3 with numpy, matplotlib and Pillow.

```bash
python src/build.py       # geometry, every check, STEP/STL/GLB exports, BOM
python src/drawings.py    # the 6-sheet drawing set
python src/check_sheet.py # the check sheet image
```

`build.py` also writes the low- and high-water assembly STEP/STL files, which are left out of the repository to keep it small.
For renders and animation, run `python tools/serve.py`, open `viewer/template.html?capture=1` and drive it with the
`window.AS` API (`AS.still`, `AS.ortho`, `AS.recordWC`); see [`tools/drawing_shots.js`](tools/drawing_shots.js).
