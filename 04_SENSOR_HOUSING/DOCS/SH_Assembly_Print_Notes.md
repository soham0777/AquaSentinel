# AquaSentinel R3 – 3D-printed sensor housing (SH)

Concept prototype: a lift-out sensor cartridge in a perforated housing, styled on the R3 sensor
well. Holds pH (DFRobot SEN0161-V2), EC (DFR0300), turbidity (SEN0189) and DS18B20 temperature
(DFR0198) probes.

Files
- CAD – one multibody part, every size driven from Tools > Equations: `CAD/SH_SensorHousing_Master.SLDPRT`
- Neutral CAD: `CAD/SH_SensorHousing_Master.step`
- Print files, already rotated to print orientation (mm): `STL/SH-01 … SH-12`
- Tables: `DOCS/SH_Parameters.csv`, `DOCS/SH_Parts_Mass.csv`, `DOCS/SH_BOM.csv`, `DOCS/SH_Sensor_Measurement_Sheet.csv`
- Build script (re-runnable): `CAD/scripts/sh_build_all.py`

## 1  Measure the sensors first
PhD, PhL, EcD, EcL, TuFitD, TuH, PhCapD, PhCapH and CableW are placeholders. Measure the real
probes with calipers, type the values into Tools > Equations, rebuild (Ctrl+Q) and re-export
the STL files. Rules:
- SocketD ≥ TuFitD + 5.4 (the snorkel must pass the lower spider)
- KeyholeD ≥ largest connector + 2 (BNC plug ≈ 14.5 mm)
- TipY + PhL and TipY + EcL ≤ −15 (room for the cable bend under the cap)

## 2  Print settings – PETG, Bambu A1 / H2D, 0.4 mm nozzle
| Setting | Value |
|---|---|
| Profile | Bambu PETG Basic / HF system profile (nozzle ≈ 250 °C, bed 70 °C), textured PEI |
| Layer height | 0.20 mm |
| Walls | 4 (≥ 1.6 mm) – collets and snorkel must be watertight |
| Top / bottom | 5 / 5 layers |
| Infill | 25 % gyroid (cap and handle 40 %) |
| Supports | none needed in the exported orientations – check the slicer preview |
| Brim | 5 mm for SH-01 housing and SH-10 snorkel |
| Part cooling | 30–50 % |

Every part fits a 256 mm cube; the housing is the largest (190 × 190 × 210 mm).

## 3  Assembly
1. Heat-set inserts (≈ 245 °C): 2 in the handle feet, 2 in the cap top under the cup.
2. Handle: 2 × M3×16 from underneath the cap. Cup: 2 × M3×8 from inside the cup.
3. Drop the M6 nut into the hex pocket on the cap top; screw the 185 mm M6 rod in from below
   until it is 1 mm below the cap top.
4. Upper spider: fit the O-rings in the pH and EC collets, then drop the pH collet, EC collet and
   turbidity snorkel into their sockets from above (flanges rest on the spider).
5. On the rod, from below: upper spacer → upper spider → lower spacer.
6. Lower spider: fit the O-ring in the temperature collet and drop it into its socket; slide the
   spider onto the rod (the snorkel passes through its large socket); washer + nyloc. Tighten
   until the stack is firm – do not crush the PETG.
7. Probes
   - pH / EC: from above through the cap keyhole, the collet and the lower-spider guide hole.
     Set all tips level, 15 mm above the housing bottom.
   - DS18B20: thread the cable up through the temperature collet (from below) and the cap
     keyhole before fitting any connector; push the steel tube 12 mm into the collet nose.
   - Turbidity: thread the cable up through the snorkel and keyhole; coat the top 12 mm of the
     probe with neutral-cure silicone and push it into the snorkel. Cure 24 h. The snorkel keeps
     the non-waterproof top of the SEN0189 dry – never submerge above the snorkel top.
8. Cables: pass each connector through its Ø17 keyhole, slide the cable into the slot, seal with
   silicone or a split grommet.
9. Lower the cartridge into the housing by the handle, align the two lugs with the entry slots,
   push down and twist 30° to lock (180° symmetric). Reverse to lift out for cleaning and
   calibration. Park the pH storage cap in the cup while deployed.

## 4  Water level
The two grooves on the housing are the fill lines: 80 mm and 100 mm probe-tip immersion. Keep
the water between them – the snorkel top and the pH / EC cable exits must stay dry.

## 5  Electronics notes
- SEN0189 turbidity output is 0–4.5 V: use a divider before the ESP32 ADC (e.g. 10 kΩ top /
  20 kΩ bottom → 3.0 V max) and calibrate the ADC.
- DS18B20: 4.7 kΩ pull-up from DQ to 3.3 V.

## 6  Status
CAD concept, geometrically checked in SOLIDWORKS (rebuild, body interference, parameter-change
test, print envelope). Not yet validated: fit of the real probes, O-ring sealing (submerge the
cartridge for 1 h and check the snorkel and temperature collet stay dry), long-term PETG
water / UV exposure.
The housing OD of 160 mm matches the R3 D160 sleeve OD – it is a stand-alone printed well and
does not slide inside a PE100 D160 SDR26 sleeve (ID ≈ 147.6 mm).
