# AquaSentinel v2.0: SOLIDWORKS Build, Simulation & Motion Study Guide
**Project: AquaRight | Device: AquaSentinel**  
**Role: System Design & CAD Modeling (Shriraj Kamble)**  
**Competition: AAKRUTI Innovation Competition (AIC) 2026 — Theme: Robotics**  
**Institution: Sanjivani University, School of Engineering & Technology, Kopargaon**

---

## 1. Executive CAD Overview & Hand-Calculation Benchmarks

This build guide provides step-by-step instructions to model, assemble, simulate, and render **AquaSentinel v2.0** inside **SOLIDWORKS 2026 (Student Edition with 3DEXPERIENCE Connector)**.

> [!IMPORTANT]
> **Hand-Calculation Targets for Simulation Validation:**
> In the AAKRUTI evaluation rubric, judges compare your FEA and CFD outputs against your analytical hand calculations. Your hand-calculation targets from `calculations/verified_design_calcs.json` are:
> 1. **Flow Simulation Drag Force:** Hydrodynamic drag on catamaran float at $1.5\text{ m/s}$ lotic current $\approx \mathbf{93.7\text{ N}}$; drag on guide pole $\approx \mathbf{81.4\text{ N/m}}$.
> 2. **FEA Static Bending Stress:** Under combined $593.7\text{ N}$ lateral point load ($93.7\text{ N}$ drag + $500\text{ N}$ hyacinth snag) at mid-span, guide pole maximum Von Mises stress must be between **$33.5\text{ MPa}$ (clamped brackets)** and **$63.1\text{ MPa}$ (pinned brackets)**. Yield strength of annealed 316L is **$170.0\text{ MPa}$** ($SF = 2.69\times\text{ to }5.08\times$).
> 3. **Guide Pole Mid-Span Deflection:** Maximum deflection must be $\approx \mathbf{9.7\text{ mm}}$ across the $3.2\text{ m}$ bracket span (well within the $16.0\text{ mm}$ limit).
> 4. **Assembly Mass & Draft:** Total assembly mass $\approx \mathbf{25.4\text{ kg}}$; static equilibrium waterline draft $\approx \mathbf{78.3\text{ mm}}$.

---

## 2. Part-by-Part Modeling Guide & Feature Trees

All dimensions in millimeters (MMGS unit system). Materials assigned from the default SOLIDWORKS Material Database.

### 1. Port & Starboard HDPE Pontoons (`AQ-01-Pontoon.sldprt`)
* **Material:** PE High Density (`Density = 955 kg/m^3`, `Tensile Yield = 26 MPa`).
* **Base Extrude (Boss-Extrude1):** Sketch on Right Plane (YZ).
  * Draw a rectangle: Length = $900\text{ mm}$, Height = $220\text{ mm}$.
  * Bow ($+Y$) and Stern ($-Y$) Rakes: Chamfer or sketch angled cuts at $15^\circ$ starting $150\text{ mm}$ from each end.
  * Direction 1: Mid-Plane, Depth = $200\text{ mm}$.
* **Shell (Shell1):** Select top face; set thickness = $4.5\text{ mm}$.
* **Internal Bulkheads (Boss-Extrude2):** Add two $4.5\text{ mm}$ transverse baffle ribs at $Y = +150\text{ mm}$ and $Y = -150\text{ mm}$ for compartmentalized reserve buoyancy.
* **Top Deck Mounting Bosses (Boss-Extrude3):** 4x M8 brass threaded heat-stake inserts on top flange.

### 2. Structural Bridge Deck (`AQ-02-Deck.sldprt`)
* **Material:** 6061-T6 Aluminum (`Density = 2700 kg/m^3`, `Yield = 276 MPa`).
* **Base Extrude (Boss-Extrude1):** Sketch on Top Plane (XZ).
  * Rectangle centered at $(0,0)$: Width = $620\text{ mm}$, Length = $700\text{ mm}$.
  * Extrude downward: Depth = $4.0\text{ mm}$.
* **Central Guide Pole Aperture (Cut-Extrude1):**
  * Centered at $(0,0)$: Draw slotted rectangular cutout: Width ($X$) = $160\text{ mm}$, Length ($Y$) = $220\text{ mm}$ with $R15\text{ mm}$ fillet corners.
  * *Verification:* Minimum clearance to the $\varnothing 60.3\text{ mm}$ guide pole is $> 49.8\text{ mm}$ (exceeding the $5.0\text{ mm}$ mandate).
* **Weight Reduction Pockets (Cut-Extrude2):** 4x triangular pockets retaining $20\text{ mm}$ structural web borders.

### 3. Ergonomic Top Canopy & Fairing (`AQ-03-Canopy.sldprt`)
* **Material:** ABS or Woven Carbon/Epoxy Composite (`Density = 1040 kg/m^3`).
* **Lofted Surface / Thin Extrude:** Sculpted aerodynamic dome with $15^\circ$ sloping brow.
* **Molded Grab Handles:** Two ergonomic marine handles on Port and Starboard edges for river workers.
* **Solar Recesses:** Two recessed trays ($365 \times 225 \times 28\text{ mm}$) to flush-mount the split 10W PV panels.

### 4. 2-Inch Schedule 40S 316L Guide Pole (`AQ-04-GuidePole.sldprt`)
* **Material:** AISI 316L Stainless Steel, Annealed (`Yield = 170 MPa`, `E = 193 GPa`).
* **Revolve / Extrude:** Outer Diameter = $60.30\text{ mm}$, Inner Diameter = $52.48\text{ mm}$ ($3.91\text{ mm}$ wall), Length = $3600\text{ mm}$.
* **Surface Finish:** Longitudinal centerless polish annotation $R_a \le 0.4\ \mu\text{m}$.

### 5. Dual Pier Mounting Brackets (`AQ-05-PierBracket.sldprt`)
* **Material:** AISI 316L Stainless Steel Plate ($5.0\text{ mm}$ thickness).
* **Sheet Metal / Boss-Extrude:** Formed mounting angle with 4x $\varnothing 14\text{ mm}$ clearance holes for M12 Hilti masonry anchors. Split clamping collar with 2x M10 316 bolts to clamp the guide pole.

### 6. Anti-Jamming 8-Roller Carriage (`AQ-06-RollerCarriage.sldasm`)
* **Sub-Assembly Components:**
  * Split 6061-T6 aluminum structural cage ($250\text{ mm}$ vertical span).
  * 8x Concave pile-guide rollers machined from virgin UHMW-PE (`Density = 940 kg/m^3`, $\mu = 0.05$).
  * 8x 316L precision shoulder bolts ($\varnothing 10\text{ mm}$) with sealed stainless ball bearings.

### 7. Modular Forensic Autosampler Cassette (`AQ-07-Autosampler.sldasm`)
* **Sub-Assembly Components:**
  * Insulated carousel housing with carrying handle.
  * 4-position rotary carousel holding 4x $250\text{ mL}$ borosilicate bottles with captive silicone septa.
  * 12V food-grade peristaltic pump with Santoprene quick-disconnect tubing.

### 8. 360° Visual Safety Beacon (Jal-Deep) (`AQ-08-Beacon.sldprt`)
* **Material:** UV-stabilized Polycarbonate (`Clear/Frosted`).
* **Geometry:** Cylindrical halo ring ($\varnothing 90\text{ mm} \times 60\text{ mm}$ height) mounted at canopy apex.

---

## 3. SOLIDWORKS Assembly Mating Scheme (`AquaSentinel_Master.sldasm`)

1. **Ground Reference / Fixed Component:**
   * Insert `AQ-04-GuidePole.sldprt` and fix its axis along the assembly $Z$-axis.
2. **Pier Bracket Mates:**
   * Lower Bracket: Distance mate = $200\text{ mm}$ from pole base; Concentric mate to pole.
   * Upper Bracket: Distance mate = $3200\text{ mm}$ from Lower Bracket; Concentric mate to pole.
3. **Roller Carriage to Pole:**
   * **Concentric Mate:** Carriage cylindrical axis concentric to Guide Pole axis.
   * **Limit-Distance Mate:** Allows vertical travel along $Z$ between $Z_{\text{min}} = 350\text{ mm}$ (Bottom Stop) and $Z_{\text{max}} = 2350\text{ mm}$ (Top Stop). Travel range = $2000\text{ mm}$ ($2.0\text{ m}$).
4. **Floating Platform to Carriage:**
   * Coincident mate between carriage mounting flange and deck top face.
   * Pontoon symmetry: Coincident mates between cross-frame aluminum tubes and pontoon deck bosses.
5. **Dual Pods Symmetry:**
   * Electronics Pod: Distance mate $= +180.0\text{ mm}$ from $YZ$ plane.
   * Battery Pod: Distance mate $= -180.0\text{ mm}$ from $YZ$ plane.

---

## 4. SOLIDWORKS Motion Study: 1-DOF Water Level Compliance

1. **Study Type:** Select **Motion Analysis** (requires SOLIDWORKS Motion add-in).
2. **Gravity:** Enable standard gravity along $-Z$ ($9.80665\text{ m/s}^2$).
3. **Linear Actuator (Water Elevation Driver):**
   * Apply a linear motor to the float assembly along $+Z$.
   * Function: Data Points / Harmonic Ramp.
   * Motion: $0.0\text{ s}$ to $10.0\text{ s}$: Float ascends smoothly from $Z = 350\text{ mm}$ to $Z = 2350\text{ mm}$ ($2.0\text{ m}$ flood rise).
4. **Contact Pairs:**
   * Define 3D Solid Contact between UHMW-PE rollers and 316L Guide Pole (Dynamic friction $\mu_k = 0.05$).
5. **Output Results:**
   * Plot vertical translation velocity and roller normal reaction forces.
   * Verify: Smooth vertical sliding without chatter or jamming.

---

## 5. SOLIDWORKS Simulation (FEA Static Study)

1. **Study Type:** Static FEA.
2. **Components Included:** `AQ-04-GuidePole`, `AQ-05-PierBracket` (Upper and Lower).
3. **Fixtures:**
   * Fixed Geometry on the rear face of the Upper and Lower pier brackets (simulating rigid anchoring to concrete bridge masonry).
4. **Loads Applied:**
   * **Distributed Force (Current Drag on Pole):** Select pole cylindrical face; apply distributed force = $81.4\text{ N/m} \times 3.2\text{ m} = \mathbf{260.5\text{ N}}$ along $+Y$.
   * **Point / Bearing Load (Float Drag + Debris Snag):** Apply lateral resultant load $P = 93.7\text{ N} + 500.0\text{ N} = \mathbf{593.7\text{ N}}$ along $+Y$ at mid-span ($Z = 1800\text{ mm}$).
5. **Mesh Settings:**
   * Curvature-based solid mesh; element size $= 5.0\text{ mm}$ along pole, refined to $2.0\text{ mm}$ near bracket fillets.
6. **Expected Results & Hand-Calc Comparison:**
   * **Peak Von Mises Stress:** Max stress should occur near bracket clamping zones, reading between **$33.5\text{ MPa}$ and $63.1\text{ MPa}$**.
   * **Safety Factor:** $\frac{170.0\text{ MPa}}{63.1\text{ MPa}} \approx \mathbf{2.69\times}$ (Pinned) to $\mathbf{5.08\times}$ (Fixed).
   * **Maximum Deflection:** Mid-span displacement should read $\approx \mathbf{9.7\text{ mm}}$.
   * *Conclusion:* Guide pole easily withstands monsoon flood currents and severe hyacinth snagging without plastic deformation.

---

## 6. SOLIDWORKS Flow Simulation (CFD Lotic Hydrodynamics)

1. **Project Setup:** External Flow; Fluid = Water (Liquid); Flow velocity in $Y$-direction = $1.5\text{ m/s}$.
2. **Computational Domain:**
   * $X$: $\pm 1.5\text{ m}$ from centerline.
   * $Y$: $-2.0\text{ m}$ to $+3.0\text{ m}$.
   * $Z$: $-0.8\text{ m}$ (riverbed) to $+0.2\text{ m}$ (water surface).
3. **Boundary Conditions & Waterline:** Free surface / volume-of-fluid at draft level ($78.3\text{ mm}$).
4. **Goals:**
   * Global Goal: Force ($Y$) on Catamaran Float.
   * Global Goal: Force ($Y$) on Guide Pole.
5. **Expected Results:**
   * Total drag on catamaran float $\approx \mathbf{94\text{ N}}$ (matching hand calculation $93.7\text{ N}$).
   * Total drag on submerged pole $\approx \mathbf{81\text{ N/m}}$.

---

## 7. SOLIDWORKS Visualize Render Guidelines

1. **Environment:** Riverbed / Bridge Abutment HDR lighting (daylight overcast / sunset).
2. **Materials & Appearances:**
   * Pontoons: High-Gloss Yellow or Marine Orange UV-HDPE (`Roughness = 0.15`).
   * Deck: Anodized Brushed Marine Aluminum (`Roughness = 0.25`).
   * Guide Pole: Mirror-Polished Centerless Ground 316L Stainless Steel (`Metal / Chrome / Polished Steel`, `Roughness = 0.05`).
   * Solar Panels: Textured Monocrystalline Silicon (`Photovoltaic Glass`, dark blue/black with silver busbars).
   * 360° Visual Beacon: Emissive LED Halo (Green in normal mode, pulsing Red in event mode).
3. **Camera Views:**
   * Hero Shot: Isometric 3/4 view showing river water flowing around pontoons with bridge pier in background.
   * Exploded View: Vertical exploded assembly demonstrating central pole clearance and cassette detachment.
   * Human-Centric Vignette: Riverbank perspective looking toward the glowing Jal-Deep visual beacon.
