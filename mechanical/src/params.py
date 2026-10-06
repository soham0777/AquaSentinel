"""
AquaSentinel R3 - design parameters (millimetres, kilograms).

FLOAT FRAME (all float parts are modelled in this frame)
  origin  = guide-pole axis, at pontoon keel level
  +X      = downstream (aft): the float trails behind the pole
  +Y      = starboard (looking forward toward the pole, starboard is on the right), +Z = up
WORLD FRAME = float frame shifted vertically by the keel height for the water stage.
The pier face is upstream of the pole (x < 0).

(v2)          carried over unchanged from calculations/verified_design_calcs.py
(R3)          new decision in this refinement - reason in README / design_report
(ASSUMPTION)  needs a supplier drawing, a site survey or a test before it is final
"""

# ---------------------------------------------------------------- guide pole (v2)
POLE_OD = 60.3            # 2" Sch 40S SS316L, ASME B36.19M (v2)
POLE_WALL = 3.91          # (v2)
POLE_R = POLE_OD / 2

# ---------------------------------------------------------------- site / stage
STAGE_RANGE = 2000.0      # design water-level travel (v2 ASSUMPTION - confirm from site gauge / WRD records)
W_LOW = 0.0               # world z of the lowest design water level
W_HIGH = W_LOW + STAGE_RANGE
PIER_STANDOFF = 360.0     # pole axis to pier face (R3)
RIVERBED_Z = -1400.0      # ASSUMPTION (renders and clearance only)
STOP_GAP = 20.0           # float still floats 20 mm short of a stop at W_LOW / W_HIGH

# ---------------------------------------------------------------- pontoons (R3: re-sized from CAD mass)
PONT_L, PONT_W, PONT_H = 1000.0, 230.0, 260.0
PONT_YC = 270.0           # 540 mm centre-to-centre
PONT_X0 = -100.0          # bow tip; the pole sits 100 mm inside the bow line, between the hulls (R3, sets LCB over LCG)
PONT_X1 = PONT_X0 + PONT_L
BOW_PLAN_R = 90.0         # plan-view bow corner radius (debris shedding)
STERN_PLAN_R = 55.0
BOW_ROCKER_L, BOW_ROCKER_H = 260.0, 125.0   # keel rises toward the bow
STERN_ROCKER_L, STERN_ROCKER_H = 130.0, 50.0
HULL_RB, HULL_RT = 40.0, 14.0               # section corner radii (rotomould-friendly)
HULL_WALL = 5.0           # rotomoulded PE wall
FOAM_DENSITY = 32.0       # closed-cell PU foam fill, kg/m3 (hull stays afloat if punctured)
RUBRAIL_Z, RUBRAIL_R = 190.0, 9.0

# ---------------------------------------------------------------- frame
BEAM_A, BEAM_T = 40.0, 3.0                  # 6061-T6 SHS 40x40x3
BEAM_X = [120.0, 380.0, 660.0, 860.0]       # crossbeam centrelines
BEAM_HALF = 375.0
BEAM_Z0 = PONT_H                            # beams sit on the hull tops (moulded-in M8 inserts)
BEAM_Z1 = BEAM_Z0 + BEAM_A
DECK_T = 3.0                                # 6061 tread plate
DECK_X0, DECK_X1, DECK_HW = 100.0, 885.0, 170.0
DECK_Z0, DECK_Z1 = BEAM_Z1, BEAM_Z1 + DECK_T

# ---------------------------------------------------------------- guide carriage (R3: bow mounted, opening gate)
ROLLER_RC = 52.0          # roller centre radius from pole axis
ROLLER_CLEAR = 1.5        # running clearance between roller throat and pole
ROLLER_W = 40.0
ROLLER_BORE = 10.0
TIER_Z = [180.0, 530.0]   # tier-plate bottoms -> roller tiers 350 mm apart (v2: 250)
TIER_T = 6.0
CARR_PLATE_T = 5.0        # 6061 plate, lightening windows
CARR_HALF = 95.0          # tier plates are 190 x 190
CARR_TOP = TIER_Z[1] + TIER_T + 56.0        # top of upper roller cheeks
HINGE_XY = (-111.0, 111.0)                  # gate hinge axis (starboard-front corner)

# ---------------------------------------------------------------- sensor well + cartridge (R3)
WELL_X = 240.0
WELL_OD, WELL_WALL = 160.0, 6.2             # PE100 SDR26 pipe
WELL_BOT = -60.0
CAGE_BOT = -380.0
CAGE_ROD_R, CAGE_ROD_D = 74.0, 6.0
FLANGE_OD, FLANGE_T = 190.0, 6.0
WELL_TOP = DECK_Z1 + FLANGE_T - 0.5
CART_Z0 = DECK_Z1 + FLANGE_T              # cartridge cap seats on the flange
CAP_D, CAP_T = 186.0, 14.0
PROBE_R, PROBE_D = 45.0, 32.0
PROBE_TIP_Z = -340.0
PROBE_LEN = 300.0         # envelope - replace with supplier STEP (ASSUMPTION)

# ---------------------------------------------------------------- deck equipment
POD = dict(x0=345.0, x1=645.0, hw=130.0, h=150.0, lid=30.0)     # IP67 polycarbonate pod
SAMPLER = dict(x0=670.0, x1=845.0, hw=115.0, h=240.0, lid=12.0)
PV = dict(x0=360.0, x1=810.0, hw=175.0, t=25.0, tilt=8.0, aft_clear=277.0)  # 20 W module (ASSUMPTION size)
STANCHION_X = (420.0, 790.0)
STANCHION_Y = 165.0
MAST_XY = (860.0, 225.0)                    # starboard-aft
ANT_XY = (860.0, -225.0)                    # port-aft
MAST_TOP = DECK_Z1 + 497.0

# ---------------------------------------------------------------- pier bracket (R3: identical upper/lower)
BRK_PLATE = (12.0, 220.0, 180.0)   # thickness (x), width (y), height (z)
BRK_ARM_T, BRK_ARM_Y = 10.0, 33.0  # arm side plates thickness and centre offset
CLAMP_OD, CLAMP_H = 120.0, 80.0
STOP_OD, STOP_H, BUFFER_H = 100.0, 30.0, 20.0

# ---------------------------------------------------------------- materials (density kg/m3, PBR look)
MATERIALS = {
    "HDPE_YELLOW":  dict(rho=955,  color=(0.98, 0.72, 0.04), rough=0.5, metal=0.0, label="Rotomoulded PE, RAL 1003 signal yellow"),
    "AL6061":       dict(rho=2700, color=(0.80, 0.82, 0.84), rough=0.38, metal=0.85, label="Aluminium 6061-T6, anodised"),
    "SS316L":       dict(rho=7980, color=(0.68, 0.69, 0.70), rough=0.28, metal=1.0, label="Stainless steel 316L"),
    "SS_BRUSHED":   dict(rho=7980, color=(0.58, 0.59, 0.60), rough=0.42, metal=1.0, label="Stainless steel 316 (brushed)"),
    "UHMW":         dict(rho=940,  color=(0.93, 0.93, 0.90), rough=0.65, metal=0.0, label="UHMW-PE"),
    "POM_BLACK":    dict(rho=1410, color=(0.10, 0.10, 0.11), rough=0.45, metal=0.0, label="Acetal (POM) black"),
    "PE_PIPE":      dict(rho=955,  color=(0.13, 0.14, 0.16), rough=0.5,  metal=0.0, label="PE100 black"),
    "PC_GREY":      dict(rho=1200, color=(0.82, 0.83, 0.80), rough=0.45, metal=0.0, label="Polycarbonate RAL 7035"),
    "PC_DARK":      dict(rho=1200, color=(0.30, 0.32, 0.34), rough=0.5,  metal=0.0, label="Polycarbonate dark grey"),
    "RUBBER":       dict(rho=1250, color=(0.06, 0.06, 0.06), rough=0.9,  metal=0.0, label="EPDM"),
    "PV_CELL":      dict(rho=2500, color=(0.05, 0.09, 0.20), rough=0.15, metal=0.3, label="Mono-Si PV cells + glass"),
    "PCB":          dict(rho=1850, color=(0.05, 0.35, 0.18), rough=0.5,  metal=0.0, label="PCB"),
    "BATTERY":      dict(rho=2200, color=(0.10, 0.28, 0.55), rough=0.5,  metal=0.0, label="LiFePO4 pack"),
    "WHITE_PE":     dict(rho=955,  color=(0.95, 0.95, 0.93), rough=0.6,  metal=0.0, label="PE white"),
    "TUBING":       dict(rho=1200, color=(0.70, 0.85, 0.95), rough=0.2,  metal=0.0, alpha=0.75, label="Clear PVC tubing"),
    "CABLE":        dict(rho=1500, color=(0.04, 0.04, 0.05), rough=0.7,  metal=0.0, label="Marine cable"),
    "BEACON_LENS":  dict(rho=1200, color=(0.55, 1.00, 0.70), rough=0.1,  metal=0.0, alpha=0.85,
                         emissive=(0.05, 0.75, 0.30), label="PC lens (green = normal)"),
    "PROBE_PH":     dict(rho=1300, color=(0.10, 0.35, 0.80), rough=0.4, metal=0.0, label="pH ID band (blue)"),
    "PROBE_EC":     dict(rho=1300, color=(0.95, 0.45, 0.05), rough=0.4, metal=0.0, label="EC ID band (orange)"),
    "PROBE_DO":     dict(rho=1300, color=(0.15, 0.70, 0.25), rough=0.4, metal=0.0, label="DO ID band (green)"),
    "PROBE_TU":     dict(rho=1300, color=(0.85, 0.15, 0.55), rough=0.4, metal=0.0, label="Turbidity ID band (magenta)"),
    "CONCRETE":     dict(rho=2400, color=(0.62, 0.61, 0.58), rough=0.95, metal=0.0, label="Concrete pier"),
    "RIVERBED":     dict(rho=1800, color=(0.45, 0.40, 0.32), rough=1.0, metal=0.0, label="Riverbed"),
}
