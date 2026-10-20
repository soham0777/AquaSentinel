# Mechanical and visual design review — AquaSentinel R3

Evidence base: the parametric engine `mechanical/src/*` (read in full and rebuilt), `checks/design_checks.json`, 66 STEP + 66 STL
parts and the mid-water assembly (validated with OpenCascade 7.9), the GLB scene, the six A3 drawings and PDF, the two SOLIDWORKS
Simulation reports (text and 33 embedded images extracted), the Pack-and-Go archive (listed, CRC-checked), renders, GIFs and video
key-frames. SOLIDWORKS itself is not installed, so `.SLDPRT/.SLDASM` content (feature trees, mates, materials) could not be opened;
statements about them rely on the reports and indirect evidence. All results here are **design-stage**: nothing has been built,
weighed or tested in water.

## 1. Revision and naming conventions

* **R3** is the third design state, following "v2". Evidence: `params.py` tags values `(v2)` / `(R3)` "new decision in this
  refinement" ([params.py:11-13](../../mechanical/src/params.py#L11-L13)), the check sheet heading "What the refinement changed
  (v2 -> R3)", and the deck's journey slide (IDC → research → calcs → CAD → checks → FEA → R3). The word "R3" is never defined
  explicitly; "revision/refinement 3" is an inference.
* **Part numbers `AS3-xyz`** ("AquaSentinel R3"): the hundreds digit is the subsystem — 1 guide/pier hardware, 2 hulls and frame,
  3 guide carriage, 4 sensing well and cartridge, 5 power and control, 6 autosampler, 7 signalling and comms, 8 handling and
  harness, 9 fasteners. Drawings are `AS3-DWG-01…06`. The title block calls the project **AquaRight** and carries the team id
  `AG26-1500$41`.
* `docs/engineering/*.md` and `hardware/AquaSentinel_Cost_Estimate_BOM.csv` describe **v2** (25.4 kg, 900×200×220 hulls, 250 mm
  roller span, pole through the centre, two 10 W panels, borosilicate vials). Treat them as history, not as the R3 definition.

## 2. Overall arrangement (R3, from CAD)

| Quantity | Value | Source |
|---|---|---|
| Float envelope | 1016 × 770 × 896 mm (L incl. bumpers × beam × height to beacon) | DWG-01 |
| Hulls | 2 × 1000 × 230 × 260 mm, 540 mm centres, bow rocker 260/125 mm, stern rocker 130/50 mm, 5 mm PE wall + 32 kg/m³ PU foam | [params.py:30-42](../../mechanical/src/params.py#L30-L42) |
| Mass (bottles full) | 48.54 kg (CG x = 395 mm aft of pole, z = 250 mm above keel); dry transport 43.6 kg | design_checks.json |
| Mass basis | 42 % CAD volume × density, 38 % shell area × wall (hulls, pod, sampler), **20 % catalogue/assumed** | [data_integrity_checks.py](../audit/verification/data_integrity_checks.py) |
| Draft / freeboard | 116.8 / 143.2 mm | design_checks.json |
| Reserve buoyancy | 2.27 × (hull volume 110.3 L vs displacement 48.5 L) | " |
| GM_T / GM_L | 0.551 m / 2.19 m; GZ max 180 mm at 25°, positive at every computed angle to 60° | " |
| Pier hardware | 52.2 kg (two 12.7 kg brackets, 16.4 kg pole, caps, stops, anchors) | BOM_R3.csv |
| Guide | 2 in Sch 40S 316L pole, 2,978 mm long, brackets 2,678 mm apart, 360 mm off the pier face | DWG-02 |

## 3. Subsystem review

### 3.1 Guide: brackets, pole, stops, target (AS3-101…114)
* **Purpose / principle:** a fixed vertical rail; the float follows the water level along it, so no motor or mooring is needed.
* **Components and interfaces:** two identical TIG-welded 316L brackets (12 mm back plate, 10 mm arms, half-ring clamp) with a
  bolted clamp cap (2× M10), each on 4× M12×130 A4 chemical anchors; ASTM A312 TP316L pole; split stop collars with EPDM buffers;
  stage target plate welded to the upper clamp cap.
* **Critical dimensions:** standoff 360 mm; clamp bore reamed 60.7 mm for a 60.3 mm pipe; buffers end the travel 20 mm before
  contact at the design extremes ([parts.py:652-661](../../mechanical/src/parts.py#L652-L661)).
* **Materials:** 316L throughout, A4-70 fasteners, EPDM. 316L in fresh river water is appropriate; crevice corrosion under the
  clamp and buffers, and stray-current corrosion near bridge services, should be inspected periodically.
* **Assembly:** anchor brackets → drop pole → collars, buffers, target → float on → gate closed. Bracket positions follow from the
  computed draft (`guide_levels`), so the pole length must be cut from site data.
* **Risks / open questions:** (1) the 2 m stage range is an assumption; if the river rises past the top stop the float is pinned
  and progressively submerged (its pod is IP67, not rated for long immersion), and if it falls below the bottom stop the float hangs
  on the collar with its CG ≈ 0.4 m aft of the pole, loading the rollers and pole in a case nobody has analysed; (2) anchor capacity,
  edge distances and approval from the pier owner; (3) pipe tolerances: ASTM A999 allows NPS 2 pipe an OD of 60.3 ± 0.8 mm
  (0.031 in, ovality included, per secondary sources — confirm in the current standard), i.e. 59.5–61.1 mm. A pipe above 60.7 mm will
  not enter the reamed clamp bore specified on DWG-06, and straightness/ovality eat into the 1.5 mm roller clearance: measure the
  delivered pipe before reaming the clamps; (4) vortex shedding from a 60 mm cylinder at 1.5 m/s is ≈ 5 Hz (St ≈ 0.2) — vibration
  and fatigue have not been screened.

### 3.2 Hulls, frame and deck (AS3-201…213, 801-802, 901)
* Twin rotomoulded, foam-filled hulls from one mould; four 6061 SHS crossbeams on moulded-in M8 inserts; 3 mm 6061 tread-plate deck.
* Foam fill keeps the float afloat when a hull is punctured: good practice. Leak test at 0.1 bar before filling (DWG-05 note 4).
* **Drawing inconsistency:** DWG-05 marks the four handle inserts on one side only ([drawings.py:326-333](../../mechanical/src/drawings.py#L326-L333)),
  but the handles sit on the outboard side of each hull ([parts.py:606-610](../../mechanical/src/parts.py#L606-L610)) and both hulls come
  from one mould. Either mould inserts on both sides or mirror the handle layout.
* ISO 2768-m general tolerances on a rotomoulded hull are unrealistic; rotomoulding tolerances are typically about ±1 % of size.
  Give the moulder a separate tolerance note.
* Dissimilar metals: 316 fasteners into 6061 — the notes call for nylon isolation; specify it on each joint.

### 3.3 Guide carriage (AS3-301…321)
* Two welded 6061 halves: a fixed half bolted to crossbeam 1 and braced to crossbeam 2, and a hinged **gate** carrying the two
  upstream rollers of each tier. Eight concave UHMW-PE rollers on M10 316 axles with nylon washers; tiers 350 mm apart.
* **Jamming (drawer rule):** no self-locking while the eccentricity of the buoyancy change (LCF = 406 mm from the pole) stays below
  s/(2μ): margin 8.62 at μ 0.05 and 1.72 if rollers seize (μ 0.25). Method correct ([build.py:145-164](../../mechanical/src/build.py#L145-L164)).
* **Float lag:** under the full design load the rollers press with 1,107 N and 465 N; with seized rollers the friction requires
  **88.7 mm** of extra immersion before the float moves — 62 % of the freeboard. Only the μ 0.05 case (17.7 mm) is checked against
  the 30 mm criterion.
* **Load path not analysed:** current and debris push the float downstream, so the **gate's** rollers bear on the pole; the drag
  load therefore passes through the gate hinge pin, the two T-handle latch pins, their lugs and welds. None is checked. 6061-T6 loses
  much of its strength in the weld heat-affected zone.
* Plain UHMW bores on 316 axles in silty water will wear; specify a wear allowance and inspection interval.

### 3.4 Sensing well and pull-up cartridge (AS3-401…424)
* PE100 D160 SDR26 sleeve through the deck; open 316L rod cage below (to 380 mm under the keel); V debris deflector ahead of it;
  cartridge = POM cap with wiper servo housing and 4× M16 glands, 316L spine and wiper shaft, two POM spiders holding four D32×300
  probe envelopes on PCD 90, colour bands, intake strainer at probe depth.
* Good: probes and intake co-located; cartridge serviceable as one unit; colour keying prevents port swaps.
* **Wiper:** R3 sweeps all four probe tips ("parks between probes"), including the pH glass bulb and EC electrodes. Mechanical
  wiping of a pH membrane risks breakage and changes calibration; v2 limited the wiper to the optical windows. Confirm with the
  probe makers which faces may be wiped.
* **Placeholders:** real DFRobot probe lengths differ by model; the wiper only works if all tips are coplanar. Replace envelopes
  with supplier STEP files and re-run the build (DWG-04 note 2).
* Measurement environment: probes sit inside a well, behind a deflector and in the pole's wake (DWG-04 note 3); exchange with the
  river is reduced, and any sediment that accumulates in the open well can bias turbidity.

### 3.5 Power and control pod, solar canopy (AS3-501…523)
* IP67 polycarbonate enclosure with pressure-equalising vent, 5 × M16 glands, battery, MPPT and controller on a plate; 20 W panel
  (450 × 350 assumed) on four stanchions, 8° tilt, aft pair hinged to open the canopy.
* Shading the pod is a sound thermal decision (LiFePO4 charging is usually limited to 0–45 °C). The panel yaws with the float and
  sits almost flat; soiling by birds is likely on a river structure. Wind load on the canopy and stanchions is not analysed.
* IP67 is rated for 1 m for 30 minutes; it does not cover the over-topping case of §3.1.

### 3.6 Autosampler (AS3-601…606)
* Insulated twin-wall PE cassette, hinged lid with tamper-seal hasp, lift-out carousel of four 250 mL HDPE bottles with septum caps,
  12 V reversible peristaltic pump. Purge 20 s, fill 30 s.
* **Sample integrity:** the cassette is insulated but not cooled. BOD samples must be cooled to ≤ 6 °C and analysed within 48 h
  (40 CFR 136 Table II); microbiological samples are stricter. A bottle sitting for up to 24 h at river-side temperatures will not
  meet these rules. Bottle material (HDPE in R3, borosilicate in v2 and the dashboard) must match the analytes.
* **Legal status:** a sample drawn by an unattended float cannot follow the Water Act 1974 §21 procedure (notice to the occupier, split
  in their presence, sealed and signed by both). It is a triage sample that should trigger official sampling.
* Priming: the intake strainer (≈ 300 mm below the keel) is ≈ 0.8 m below the pump (≈ 515 mm above the keel), i.e. ≈ 0.4 m of
  static suction lift above the waterline; peristaltic pumps self-prime, but the 20 s purge must move more than the line volume —
  compute it from the real tubing (6 mm ID in R3, 3 mm in v2).

### 3.7 Signalling and comms (AS3-701…712)
* Beacon mast (6061 tube 32 × 2.5) at the starboard stern, beacon base and 360° lens; LTE whip antenna at the port stern; ultrasonic
  stage sensor on the carriage top looking up.
* **Stage sensor geometry** ([stage_sensor_geometry.py](../audit/verification/stage_sensor_geometry.py)): range to the target plate is
  2,146 mm at low water and **146 mm at high water**, below the 20–25 cm blind zone of JSN-SR04T-class sensors; at high water the face
  is only 20 mm below the upper EPDM buffer. At every level the upper buffer and collar sit 48 mm to the side of the acoustic axis,
  nearer than the plate, so with a 45–75° beam they can return the first echo. The plate is 130 × 110 mm. Bench-test range, beam and
  first-echo behaviour on a mock-up before committing to this layout; alternatives are a pressure (depth) transducer or a radar sensor
  on the bracket looking down at the water.
* **Beacon:** no optical design, power budget or visibility evidence exists ("800 m in daylight" is unverified). A red/green flashing
  light on a river structure can be read as an IALA lateral mark at night; consult the waterway authority.

### 3.8 Handling and harness (AS3-801…812)
Four grab handles, four M12 DIN 580 lifting eyes, probe/PV/beacon harness with drip loops and IP68 glands, intake and purge hoses.
A 43.6 kg dry float is a two-person lift; installation over water needs a written lift plan (boat or bridge davit), PPE and rescue
cover.

## 4. Hydrostatics and stability — verification
* The buoyancy method is exact for closed polyhedra ([analysis.py:97-115](../../mechanical/src/analysis.py#L97-L115)); it was re-derived
  for this audit and the rebuild reproduced every number.
* Independent plausibility check: two hulls of ≈ 0.226 m² waterplane at ±0.27 m give I_T ≈ 0.035 m⁴, BM = I_T/V ≈ 0.72 m,
  GM ≈ KB + BM − KG ≈ 0.053 + 0.72 − 0.250 ≈ 0.52 m (CAD: 0.551 m). Consistent.
* GZ is computed for the free-floating float at fixed trim, heeling to port only (the CG is 1.3 mm to starboard). "Rights itself to
  60°" in the README means GZ > 0 at every angle computed up to 60°; the angle of vanishing stability was not computed.
* Mass is the largest uncertainty: 20 % is catalogue values and shell-rule items use nominal walls. Every 1 kg added sinks the float
  ≈ 2.2 mm (waterplane 0.4517 m²). Weigh components and re-run.

## 5. Structural analyses — review

### 5.1 Hand calculations ([build.py:126-142](../../mechanical/src/build.py#L126-L142))
Load case: float drag 142 N (Cd 1.05 × 0.1202 m² × ½ρV², V = 1.5 m/s) + 500 N debris at mid-span, plus pole drag 81.4 N/m over the
whole 2.678 m span (conservative). Pinned: 54.8 MPa, SF 3.10, 5.8 mm; fixed: 28.7 MPa, SF 5.92. Formulas and arithmetic are correct.
**Omitted:** the couple. The float load acts 428 mm below the carriage centre, so the tiers push with +1,107 N and −465 N. Including it
([pole_carriage_couple.py](../audit/verification/pole_carriage_couple.py)): **pinned 64.0 MPa, SF 2.66**; fixed 38.5 MPa, SF 4.41.
Still above the SF ≥ 2 criterion, but with no dynamic factor for debris impact, no fatigue and no VIV check.

### 5.2 SOLIDWORKS Simulation: guide pole ("Pole flood and debris", 5 Oct 2026)
* Geometry: pole body with split lines, 16.558 kg (true cylinder volume, unlike the facetted export). Material: library "AISI 316L",
  E 200 GPa, ν 0.265, σy 170 MPa, ρ 8,027 kg/m³.
* Fixtures: **Fixed Geometry on two faces** (the clamp zones). Loads: 645.3 N (point region) + 2×104.1 N + 2×8.95 N (distributed
  drag split into faces) = 871 N; reactions 871.3 N, balanced.
* Mesh: standard solid, 6 mm elements, 179,650 nodes, 89,812 elements, aspect ratio ≤ 4.9 — about one element through the 3.91 mm wall.
* Results: von Mises max 38.32 MPa (single node), displacement 1.255 mm, strain 1.32e-4. The deflected shape (zero slope at both
  clamps) confirms clamped-clamped behaviour; most of the pole is at 20–25 MPa and the peak is a local value at a fixture or load face.
* **Interpretation:** the headline "SF 4.4, 1.3 mm sway" is the fixed-fixed idealisation. Real clamps on bolted brackets on a pier
  are not rigid; the pinned case (SF 3.1 without, 2.66 with the couple) is the conservative bound. Report sections "Description",
  "Assumptions" and "Conclusion" are empty; no mesh-convergence study; some plots use a nonsensical displacement unit ("am").

### 5.3 SOLIDWORKS Simulation: pier bracket ("Bracket pole reaction")
* Body "Pier bracket weldment (AS3-101), welded for FEA", 12.68 kg; back face Fixed Geometry; loads 2×215 N horizontal + 2×80.5 N
  vertical (= the 430 N design reaction plus the pole's 161 N weight); 4 mm mesh, 268,389 nodes.
* Result 3.65 MPa, 0.004 mm: the plate is far from its limits for this load. What matters for the bracket — anchor tension/shear and
  prying, weld throats, impact by drifting debris or the float itself, uplift from a pinned float — is not in the model.

### 5.4 Not analysed anywhere
Float buoyancy uplift on the upper stop in an over-topping flood (up to ≈ 600 N net with the hulls submerged); the stranded-on-lower-stop
case; gate pins and lugs; canopy wind load; wave and wake slamming; debris impact energy; fatigue of welded 6061; galvanic corrosion;
UV ageing of PE and EPDM.

## 6. Hydrodynamic and site assumptions
* Design point: stage range 2.0 m, current 1.5 m/s, debris 500 N, riverbed −1.4 m — all marked as assumptions. Site flood levels for
  the Godavari at Kopargaon were not found in public sources during this audit; obtain gauge records (CWC / Maharashtra WRD) before
  cutting the pole.
* **Pier wake:** the bracket is on the pier's downstream face, so the float rides 0.3–1.4 m behind a ≈ 1.1 m wide pier (modelled), inside
  its near wake. Interaction between piers in tandem is known to persist to about six pier widths; in the near wake the flow is
  unsteady, sheds vortices and can reverse. The weathervane argument (lateral-area centre 351 mm aft of the pivot) assumes uniform
  approaching flow. Expect yaw oscillation, pier contact by the rub rails and cyclic loads on the carriage; test it in a flume with a
  pier model or observe at the site.
* Cage clearance to the assumed bed: 903 mm at low water; pier scour holes or dry-season deposition change this.

## 7. Electronics and power hardware artefacts
* **No schematic exists.** [AquaSentinel_Mainboard.kicad_sch](../../hardware/kicad/AquaSentinel_Mainboard.kicad_sch) contains a title
  block and `#` comment lines describing nets; there are no symbols, wires or footprints (KiCad not installed, so whether KiCad even
  opens the file was not tested).
* **AO3401A gate rating:** the notes quote VGS ±20 V; the Alpha & Omega datasheet gives **±12 V absolute maximum**. With the source at
  12.8–14.6 V and the gate pulled to ground, VGS exceeds the rating. Use a P-FET rated ±20 V or clamp the gate (zener + resistor divider).
* **Polarity conflict:** the notes drive each P-FET through a 2N7002 (GPIO HIGH = rail on); firmware writes LOW to turn the sensor rail on.
* **I2C addresses:** PCA9685 and INA226 both default to 0x40 with address pins grounded.
* **Power budget** ([power_budget.csv](../../hardware/power_budget.csv)): lines add correctly to 3.390 Wh/day, but the **beacon is not
  budgeted** (the v2 spec allowed 0.6 Wh/day for a night-only green pulse; a daylight-visible 360° beacon needs watts, i.e. tens of Wh
  per day if lit continuously). The v2 spec reaches the same 3.4 Wh/day with an 8 mA floor that the CSV puts at 0.6 mA — two
  different breakdowns of one total. Modem bursts of ≈ 2 A at 3.8 V need bulk capacitance and must not brown out the MCU rail.
* **Bench energy test** ([bench_energy_test_procedure.md](../../hardware/bench_energy_test_procedure.md)): an INA226 with a 10 mΩ shunt
  has 2.5 µV ≈ 0.25 mA resolution and up to ±10 µV ≈ ±1 mA offset, so it cannot verify the 0.6 mA standby criterion. Use a larger
  shunt range or a dedicated low-current analyser for sleep, and the INA226 for active phases. The procedure references a test
  firmware file that does not exist.
* **Cost estimate** (v2 layout): line items sum to ₹1,38,000, not the stated ₹1,34,000; four rows contain unquoted commas that break
  CSV readers; probes are ₹81,100 (59 %). Unit costs in `BOM_R3.csv` are all "TO QUOTE".

## 8. CAD data quality
* STEP AP214 written by the project's own exporter as **facetted planar B-reps**; OpenCascade reads 66/66 parts and the assembly
  (453 solids). **65/66 parts are valid**; AS3-416 (probe cables, swept tubes) is invalid, which also flags the assembly compound.
  STL and STEP volumes agree within 0.03 %; 64/66 STLs are closed manifolds (AS3-411 and AS3-711 are multi-body STLs with touching
  shells). Masses recomputed from STEP volumes match the BOM for every "CAD volume × density" part.
* SOLIDWORKS Pack and Go: 66 `.SLDPRT` + one `.SLDASM`, all written between 13:29 and 13:30 on 2026-10-05, consistent with batch
  creation from the generated geometry. The deck's "66 parts, native SOLIDWORKS" claim cannot be verified without SOLIDWORKS; the
  simulation models, at least, use true cylinders (their volumes match exact geometry, not the facets).

## 9. Drawings (AS3-DWG-01…06)
Six A3 sheets, first-angle, ISO-style title blocks, generated by `drawings.py` on 2026-10-04 from the parameters and check results;
all dimensions read on the sheets agree with `params.py` and `design_checks.json` (overall 1016 × 770 × 896; pole 2978, bracket span
2678, stage range 2000, standoff 360; carriage 412/350/190; roller throat R20.35–R27.5; hull 1000 × 230 × 260; bracket 220 × 180 × 12,
anchors 160 × 120, bore 60.7). Issues: the one-sided handle inserts (DWG-05); general tolerance class; the views are hidden-line
renders from the browser viewer that are not in the repository, so the set cannot be regenerated (`KeyError: 'ga_elev'`).

## 10. Visual assets and discrepancies
The [visual asset catalogue](../audit/VISUAL_ASSET_CATALOGUE.md) lists every image and video with thumbnails. Renders, GIFs and the
assembly video are produced by the three.js viewer from the same GLB, so they match the CAD exactly. Discrepancies are textual:
v2 documents (vials, pole position, masses), the KPI tile's "4.4× guide-pole safety factor" (fixed-end FEA), the journey video's
closing claim "deployment ready on the Godavari" (contradicted by "not tested in water yet"), and the dashboard's borosilicate
bottles and 4 °C cooler.

## 11. Recommended mechanical tests (before any river deployment)
1. **Weigh** every purchased component and the built float; re-run `build.py` with measured masses.
2. **Tank test** (as planned): draft, trim, heel to 25°, reserve buoyancy with flooded hull compartment.
3. **Carriage rig:** a 2 m pole section, roller friction dry/wet/silty, lag versus applied side load, gate pins under 1.2 kN.
4. **Stage-sensor mock-up:** sensor, collar, buffer and plate at full scale over 0.1–2.2 m.
5. **Flume or field observation** in a pier wake: yaw motion, rub-rail contact, carriage load spectrum.
6. **Anchor pull-out test** on the pier concrete with the owner's approval.
7. **IP check** of pod glands and vent after thermal cycling; sampler cooling and holding-time trial with the lab.
