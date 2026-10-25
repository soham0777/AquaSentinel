"""
AquaSentinel R3 - drawing set (A3, first-angle).    python src/drawings.py
Every dimension is read from params.py / the design-check results, so the drawings change with the model.
Hidden-line views are rendered by the viewer (renders in drawings/views/), sections and the hull are drawn from geometry.
"""
import json
import math
import os
import sys

import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Polygon, Rectangle, Arc

sys.path.insert(0, os.path.dirname(__file__))
from params import *
from drafting import Sheet, View, INK, DIM, BLUE, LW_THIN, LW_MED, LW_THICK, pt
from parts import hull_local, guide_levels
import geom as g

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VIEWS = os.path.join(ROOT, "drawings", "views")
OUT = os.path.join(ROOT, "drawings")
CHK = json.load(open(os.path.join(ROOT, "checks", "design_checks.json"), encoding="utf-8"))
SHOTS = json.load(open(os.path.join(VIEWS, "shots.json"), encoding="utf-8")) if os.path.exists(os.path.join(VIEWS, "shots.json")) else {}
H = CHK["hydrostatics"]
DRAFT = H["draft_mm"]
LV = CHK["levels_world_mm"]


def place_view(sh, key, centre_paper, k):
    s = SHOTS[key]
    sh.image(os.path.join(VIEWS, key + ".png"), centre_paper[0], centre_paper[1], s["s"], k)
    return View(sh, s["center"], centre_paper, k, -1.0 if s["view"] == "bow" else 1.0)


def f0(v):
    return f"{v:.0f}"


# ---------------------------------------------------------------------------
# DWG-01 General arrangement
# ---------------------------------------------------------------------------
def dwg_ga(pdf):
    sh = Sheet("AS3-DWG-01", "GENERAL ARRANGEMENT - FLOAT", "1:10", "As parts list", "1/6")
    k = 0.1
    E = place_view(sh, "ga_elev", (128, 205), k)
    Pn = place_view(sh, "ga_plan", (128, 80), k)
    B = place_view(sh, "ga_bow", (247, 205), k)
    sh.view_title(128, 286, "ELEVATION (from port)")
    sh.view_title(52, 128, "PLAN")
    sh.view_title(247, 286, "BOW VIEW (A)")
    # waterline + key levels on elevation
    x_l, x_r = E.P(PONT_X0 - 60, 0)[0], E.P(PONT_X1 + 40, 0)[0]
    sh.waterline(x_l, x_r, E.P(0, DRAFT)[1], f"DWL  draft {DRAFT:.0f}")
    sh.centerline(E.P(0, -420), E.P(0, 960))
    sh.text(E.P(0, 965)[0] - 1, E.P(0, 965)[1], "pole axis", size=2.0, ha="right", color=DIM)
    # overall length / height
    sh.dim(E.P(PONT_X0 - 16, -380), E.P(PONT_X1, -380), -10, f"{PONT_X1 - PONT_X0 + 16:.0f} overall")
    sh.dim(E.P(PONT_X0, -380), E.P(0, -380), -4, "100")
    top = MAST_TOP + 96
    sh.dim(E.P(PONT_X1 + 15, 0), E.P(PONT_X1 + 15, top), 14, f"{top:.0f}", vertical=True, flip_text=True)
    sh.dim(E.P(PONT_X1 + 15, 0), E.P(PONT_X1 + 15, PONT_H), 6, f"{PONT_H:.0f}", vertical=True, flip_text=True)
    sh.dim(E.P(PONT_X0 - 20, 0), E.P(PONT_X0 - 20, CAGE_BOT), -6, f"{-CAGE_BOT:.0f}", vertical=True)
    sh.leader(E.P(PONT_X0 + 30, DECK_Z1), (E.P(PONT_X0 - 40, 0)[0] - 8, E.P(0, DECK_Z1 + 70)[1]), f"deck {DECK_Z1:.0f}", ha="right")
    # plan dims
    yo = PONT_YC + PONT_W / 2
    sh.dim(Pn.P(PONT_X1 + 10, -yo), Pn.P(PONT_X1 + 10, yo), 10, f"{2 * yo:.0f}", vertical=True, flip_text=True)
    sh.dim(Pn.P(PONT_X1 + 10, -PONT_YC), Pn.P(PONT_X1 + 10, PONT_YC), 4, f"{2 * PONT_YC:.0f} c/c", vertical=True, flip_text=True)
    for bx in BEAM_X:
        pass
    sh.dim(Pn.P(0, -yo - 10), Pn.P(WELL_X, -yo - 10), -6, f"{WELL_X:.0f}")
    sh.dim(Pn.P(WELL_X, -yo - 10), Pn.P((POD["x0"] + POD["x1"]) / 2, -yo - 10), -6, f"{(POD['x0'] + POD['x1']) / 2 - WELL_X:.0f}")
    sh.dim(Pn.P((POD["x0"] + POD["x1"]) / 2, -yo - 10), Pn.P((SAMPLER["x0"] + SAMPLER["x1"]) / 2, -yo - 10), -6,
           f"{(SAMPLER['x0'] + SAMPLER['x1']) / 2 - (POD['x0'] + POD['x1']) / 2:.0f}")
    sh.centerline(Pn.P(-150, 0), Pn.P(PONT_X1 + 60, 0))
    sh.dim(B.P(yo, -420), B.P(-yo, -420), -4, f"{2 * yo:.0f} overall beam")
    sh.centerline(B.P(0, -440), B.P(0, 960))
    # balloons
    items = [
        (1, "AS3-201", "Pontoon hull, rotomoulded PE, foam filled", 2, E.P(600, 120), E.P(600, -150)),
        (2, "AS3-211", "Crossbeam 6061 SHS 40x40x3", 4, E.P(BEAM_X[2], 280), E.P(BEAM_X[2] + 40, 640)),
        (3, "AS3-213", "Equipment deck plate 6061 t3", 1, Pn.P(300, 120), Pn.P(200, 440)),
        (4, "AS3-301/302", "Guide carriage (fixed half + gate)", 1, E.P(0, 470), E.P(-160, 740)),
        (5, "AS3-311", "Concave guide roller UHMW-PE", 8, Pn.P(37, 37), Pn.P(-60, 440)),
        (6, "AS3-401/403", "Sensor well + guard cage", 1, E.P(WELL_X, -230), E.P(WELL_X - 230, -300)),
        (7, "AS3-404", "V debris deflector HDPE", 1, E.P(150, -100), E.P(20, -230)),
        (8, "AS3-411..417", "Pull-up sensor cartridge (4 probes)", 1, E.P(WELL_X, 380), E.P(150, 900)),
        (9, "AS3-511", "Power and control pod IP67", 1, E.P(495, 420), E.P(430, 900)),
        (10, "AS3-521", "PV module 20 W on hinged canopy", 1, E.P(600, 610), E.P(600, 900)),
        (11, "AS3-601", "Autosampler cassette (4 x 250 mL)", 1, E.P(760, 450), E.P(720, 900)),
        (12, "AS3-703", "Jal-Deep 360 deg beacon", 1, E.P(MAST_XY[0], MAST_TOP + 40), E.P(MAST_XY[0] - 160, 960)),
        (13, "AS3-712", "Stage sensor (ultrasonic, up)", 1, E.P(118, CARR_TOP + 30), E.P(20, 900)),
        (14, "AS3-801", "Grab handle", 4, Pn.P(760, -360), Pn.P(820, -470)),
        (15, "AS3-802", "Lifting eye M12", 4, Pn.P(BEAM_X[1], 270), Pn.P(BEAM_X[1] + 40, 440)),
    ]
    for n, pid, desc, q, at, bp in items:
        sh.balloon(at, bp, n)
    rows = [(n, pid, desc, q) for n, pid, desc, q, _, _ in items]
    sh.table(282, 160, ["ITEM", "PART No.", "DESCRIPTION", "QTY"], rows, [10, 22, 88, 10], row_h=4.2, size=2.2)
    h = CHK["hydrostatics"]
    sh.note_block(282, 90, [
        f"Mass from CAD {CHK['mass']['total_kg']} kg (sampler bottles full); draft {h['draft_mm']} mm, freeboard {h['freeboard_mm']} mm.",
        f"Reserve buoyancy {h['reserve_buoyancy_sf']}x; GM_T {h['GM_T_m']} m; GZ positive to 60 deg (free floating).",
        "Pole sits 100 mm inside the bow line between the hulls; float trails downstream (weathervane).",
        "All fasteners A4-70 stainless; nylon isolation at every 316/6061 joint.",
        "Full BOM: cad/BOM_R3.csv. Every part has a STEP file in cad/parts/.",
    ], width=128, size=2.1)
    sh.save(os.path.join(OUT, "AS3-DWG-01_General_Arrangement.png"), pdf)


# ---------------------------------------------------------------------------
# DWG-02 Installation and stage envelope
# ---------------------------------------------------------------------------
def dwg_install(pdf):
    sh = Sheet("AS3-DWG-02", "INSTALLATION AND STAGE ENVELOPE", "1:25", "316L / concrete pier", "2/6")
    k = 0.04
    s = SHOTS["inst_low"]
    from PIL import Image
    lo = np.asarray(Image.open(os.path.join(VIEWS, "inst_low.png")).convert("L")).astype(np.float32)
    hi = np.asarray(Image.open(os.path.join(VIEWS, "inst_high.png")).convert("L")).astype(np.float32)
    ghost = 255 - (255 - hi) * 0.35
    comb = np.minimum(lo, ghost).astype(np.uint8)
    Image.fromarray(comb).save(os.path.join(VIEWS, "inst_combined.png"))
    cp = (118, 152)
    sh.image(os.path.join(VIEWS, "inst_combined.png"), cp[0], cp[1], s["s"], k)
    E = View(sh, s["center"], cp, k)
    sh.view_title(118, 286, "ELEVATION - lowest (solid) and highest (phantom) float positions")
    for w_, lab in ((LV["water_low"], f"W low  {LV['water_low']:.0f}"), (LV["water_high"], f"W high  +{LV['water_high']:.0f}")):
        sh.waterline(E.P(-700, 0)[0], E.P(1150, 0)[0], E.P(0, w_)[1], lab)
    sh.line([E.P(-1100, RIVERBED_Z), E.P(1300, RIVERBED_Z)], lw=LW_MED, color="#6b5b45")
    sh.text(E.P(1300, RIVERBED_Z)[0], E.P(0, RIVERBED_Z)[1] + 1, "riverbed (assumed)", size=2.1, ha="right", color="#6b5b45")
    sh.dim(E.P(-PIER_STANDOFF, LV["zb_up"] + 300), E.P(0, LV["zb_up"] + 300), 6, f"{PIER_STANDOFF:.0f}")
    sh.dim(E.P(260, LV["zb_low"]), E.P(260, LV["zb_up"]), 8, f"bracket span {LV['zb_up'] - LV['zb_low']:.0f}", vertical=True, flip_text=True)
    sh.dim(E.P(1180, LV["water_low"]), E.P(1180, LV["water_high"]), 8, f"stage range {STAGE_RANGE:.0f}", vertical=True, flip_text=True)
    sh.dim(E.P(-560, LV["pole_z0"]), E.P(-560, LV["pole_z1"]), -8, f"pole {LV['pole_z1'] - LV['pole_z0']:.0f}", vertical=True)
    cage_low = LV["keel_low"] + CAGE_BOT
    sh.dim(E.P(500, RIVERBED_Z), E.P(500, cage_low), 8, f"{cage_low - RIVERBED_Z:.0f} min.", vertical=True, flip_text=True)
    sh.leader(E.P(0, LV["low_top"]), (E.P(-700, 0)[0], E.P(0, LV["low_top"] - 250)[1]), "lower stop + EPDM buffer", ha="right")
    sh.leader(E.P(0, LV["up_bot"]), (E.P(-700, 0)[0], E.P(0, LV["up_bot"] + 250)[1]), "upper stop + EPDM buffer", ha="right")
    sh.leader(E.P(120, LV["zb_up"] + 38), (E.P(700, 0)[0], E.P(0, LV["zb_up"] + 380)[1]), "stage target plate")
    # plan: yaw envelope
    s2 = SHOTS["inst_plan"]
    cp2 = (318, 222)
    k2 = 0.05
    sh.image(os.path.join(VIEWS, "inst_plan.png"), cp2[0], cp2[1], s2["s"], k2)
    P = View(sh, s2["center"], cp2, k2)
    sh.view_title(318, 286, "PLAN - free yaw about the pole (weathervane)")
    r_env = math.hypot(PONT_X1, PONT_YC + PONT_W / 2)
    c = P.P(0, 0)
    sh.ax.add_patch(Circle(c, r_env * k2, fill=False, ec=BLUE, lw=LW_THIN, ls=(0, (4, 2)), zorder=9))
    sh.leader(P.P(r_env * 0.7071, r_env * 0.7071), (c[0] + 30, c[1] + 42), f"swing radius R{r_env:.0f}")
    sh.text(c[0] - 40, c[1] - 52, "flow", size=2.4, color=BLUE)
    sh.arrow((c[0] - 44, c[1] - 47), (c[0] - 14, c[1] - 47))
    sh.note_block(240, 150, [
        f"Brackets are identical (AS3-101). Install the lower one at or below the lowest recorded level ({LV['zb_low']:.0f} on this datum).",
        "Anchors: 4x M12 A4 chemical anchors per bracket into sound pier concrete; confirm pull-out with the pier owner / WRD.",
        f"Design stage range {STAGE_RANGE:.0f} mm is an ASSUMPTION: set from the site gauge record before cutting the pole.",
        "Float rides on 8 rollers between the stops; at the stops it is held, never jammed (EPDM buffers).",
        "Free yaw: the float trails downstream. Only the hull rub rails and bow bumpers can touch the pier.",
        f"Beyond {STAGE_RANGE / 1000:.0f} m stage or 1.5 m/s current: park at the top stop or open the gate and retrieve.",
        "Pole loads (1.5 m/s + 500 N debris): " + f"{CHK['pole']['stress_pinned_MPa']} MPa pinned, SF {CHK['pole']['SF_pinned']} vs 170 MPa yield.",
    ], width=160, size=2.15)
    sh.save(os.path.join(OUT, "AS3-DWG-02_Installation_and_Stage_Envelope.png"), pdf)


# ---------------------------------------------------------------------------
# DWG-03 Guide carriage
# ---------------------------------------------------------------------------
def dwg_carriage(pdf):
    sh = Sheet("AS3-DWG-03", "GUIDE CARRIAGE ASSEMBLY", "1:4 (detail 1:1)", "6061-T6 hard anodised / UHMW-PE / 316", "3/6")
    k = 0.25
    from PIL import Image as _I
    a_ = np.asarray(_I.open(os.path.join(VIEWS, "carr_plan.png")).convert("L")).astype(np.float32)
    b_ = np.asarray(_I.open(os.path.join(VIEWS, "carr_plan_open.png")).convert("L")).astype(np.float32)
    _I.fromarray(np.minimum(a_, 255 - (255 - b_) * 0.35).astype(np.uint8)).save(os.path.join(VIEWS, "carr_plan_combined.png"))
    sp = SHOTS["carr_plan"]
    sh.image(os.path.join(VIEWS, "carr_plan_combined.png"), 95, 100, sp["s"], k)
    Pn = View(sh, sp["center"], (95, 100), k)
    E = place_view(sh, "carr_elev", (95, 225), k)
    sh.view_title(95, 286, "ELEVATION (from port)")
    sh.view_title(95, 149, "PLAN (gate closed / phantom: gate open)")
    from PIL import Image
    t1, t2 = TIER_Z
    sh.dim(E.P(-CARR_HALF - 8, t1), E.P(-CARR_HALF - 8, t2), -14, f"roller tiers {t2 - t1:.0f}", vertical=True)
    sh.dim(E.P(-CARR_HALF - 8, t1), E.P(-CARR_HALF - 8, CARR_TOP), -24, f"{CARR_TOP - t1:.0f}", vertical=True)
    sh.dim(E.P(-CARR_HALF - 8, t1), E.P(CARR_HALF + 8, t1), -12, f"{2 * CARR_HALF + 2 * CARR_PLATE_T:.0f}")
    sh.leader(E.P(CARR_HALF + 5, 280), (E.P(CARR_HALF + 60, 0)[0], E.P(0, 300)[1]), "2x M10 to crossbeam 1")
    sh.leader(E.P(118, CARR_TOP + 30), (E.P(CARR_HALF + 60, 0)[0], E.P(0, CARR_TOP + 70)[1]), "stage sensor AS3-712")
    sh.dim(Pn.P(-CARR_HALF, -CARR_HALF - 30), Pn.P(CARR_HALF, -CARR_HALF - 30), -6, f"{2 * CARR_HALF:.0f}")
    sh.leader(Pn.P(HINGE_XY[0], HINGE_XY[1]), (Pn.P(-200, 0)[0], Pn.P(0, 140)[1]), "hinge pin D10 (gate swings 100 deg)", ha="right")
    sh.leader(Pn.P(0, -CARR_HALF - 17), (Pn.P(-200, 0)[0], Pn.P(0, -175)[1]), "2x T-handle latch pins (tool-free)", ha="right")
    sh.centerline(Pn.P(-160, 0), Pn.P(160, 0))
    sh.centerline(Pn.P(0, -160), Pn.P(0, 160))
    # roller detail drawn from the exact profile (scale 1:1)
    cx, cy, k1 = 250, 200, 1.0
    rc, rp = ROLLER_RC, POLE_R + ROLLER_CLEAR
    a = np.linspace(-ROLLER_W / 2, ROLLER_W / 2, 60)
    r = rc - np.sqrt(rp ** 2 - a ** 2)
    # roller section: axis horizontal (a along x), radius up/down
    top = np.c_[cx + a * k1, cy + r * k1]
    bot = np.c_[cx + a * k1, cy - r * k1]
    poly = np.vstack([top, bot[::-1]])
    sh.ax.add_patch(Polygon(poly, closed=True, fc="#eef2f4", ec=INK, lw=LW_MED, zorder=6))
    for yy in (-5, 5):
        sh.line([(cx - ROLLER_W / 2 * k1, cy + yy * k1), (cx + ROLLER_W / 2 * k1, cy + yy * k1)], lw=LW_THIN)
    sh.centerline((cx - 30, cy), (cx + 30, cy))
    # pole arc that the throat follows
    pole_c = (cx, cy - rc * k1)
    th = np.linspace(math.radians(55), math.radians(125), 50)
    sh.line(np.c_[pole_c[0] + POLE_R * np.cos(th), pole_c[1] + POLE_R * np.sin(th)], lw=LW_MED, color="#5b6b78")
    sh.text(pole_c[0], pole_c[1] + POLE_R * k1 - 9, "pole OD 60.3", size=2.2, ha="center", color="#5b6b78")
    sh.dim((cx - ROLLER_W / 2, cy + 30), (cx + ROLLER_W / 2, cy + 30), 2, f"{ROLLER_W:.0f}")
    sh.dim((cx + 26, cy), (cx + 26, cy + r.max()), 6, f"R{r.max():.1f}", vertical=True, flip_text=True)
    sh.dim((cx - 26, cy), (cx - 26, cy + r.min()), -6, f"R{r.min():.2f}", vertical=True)
    sh.view_title(cx, 245, "DETAIL B - CONCAVE ROLLER (1:1)", "throat r(a) = 52 - sqrt(31.65^2 - a^2)")
    rows = [("AS3-301", "Carriage fixed half (weldment)", 1, "6061-T6, 5/6 mm"), ("AS3-302", "Carriage gate (weldment)", 1, "6061-T6"),
            ("AS3-311", "Concave roller", 8, "UHMW-PE"), ("AS3-312", "Axle M10 + nyloc nuts", 8, "316"),
            ("AS3-313", "Hinge pin D10 + R-clip", 1, "316"), ("AS3-314", "T-handle latch pin", 2, "316"),
            ("AS3-321", "Brace struts (pair)", 1, "316L tube 20x2"), ("AS3-902", "Bolt M10x70 + washer", 2, "A4-70")]
    sh.table(200, 140, ["PART No.", "DESCRIPTION", "QTY", "MATERIAL"], rows, [20, 64, 10, 32], row_h=4.4, size=2.2)
    c = CHK["carriage"]
    sh.note_block(200, 98, [
        "Throat follows the pole radius + 1.5 mm running clearance: line contact, no point loading of the UHMW.",
        f"Drawer rule: with rollers (mu 0.05) jam margin {c['rollers_mu_0_05']['jam_margin']}x; seized rollers sliding (mu 0.25) {c['seized_rollers_sliding_mu_0_25']['jam_margin']}x.",
        f"Design roller loads {c['rollers_mu_0_05']['roller_loads_N'][0]:.0f} N / {c['rollers_mu_0_05']['roller_loads_N'][1]:.0f} N; float lag under full load {c['rollers_mu_0_05']['float_lag_mm']} mm.",
        "Hard-anodise after welding; nylon washers isolate 316 axles from the 6061 cheeks.",
        "Gate: remove both T-pins, swing forward 100 deg, back the float off the pole. Lanyard both pins.",
    ], size=2.15)
    sh.save(os.path.join(OUT, "AS3-DWG-03_Guide_Carriage.png"), pdf)


# ---------------------------------------------------------------------------
# DWG-04 Sensor well and cartridge
# ---------------------------------------------------------------------------
def dwg_sensor(pdf):
    sh = Sheet("AS3-DWG-04", "SENSOR WELL AND PULL-UP CARTRIDGE", "1:4", "PE100 / 316L / POM", "4/6")
    k = 0.25
    E = place_view(sh, "well_section", (90, 155), k)
    sh.view_title(90, 286, "SECTION C-C (on centreline)")
    wx = WELL_X
    sh.dim(E.P(wx - 80, WELL_BOT - 30), E.P(wx + 80, WELL_BOT - 30), -4, "OD 160")
    sh.dim(E.P(wx + 105, CART_Z0), E.P(wx + 105, PROBE_TIP_Z), 6, f"{CART_Z0 - PROBE_TIP_Z:.0f}", vertical=True, flip_text=True)
    sh.dim(E.P(wx + 125, 0), E.P(wx + 125, CAGE_BOT), 6, f"{-CAGE_BOT:.0f} below keel", vertical=True, flip_text=True)
    sh.dim(E.P(wx - 110, 0), E.P(wx - 110, DRAFT), -6, f"{DRAFT:.0f}", vertical=True)
    sh.waterline(E.P(wx - 200, 0)[0], E.P(wx + 200, 0)[0], E.P(0, DRAFT)[1], "DWL")
    sh.leader(E.P(wx, CART_Z0 + CAP_T + 90), (E.P(wx + 150, 0)[0], E.P(0, CART_Z0 + 160)[1]), "lift handle")
    sh.leader(E.P(wx + 60, CART_Z0 + CAP_T + 8), (E.P(wx + 150, 0)[0], E.P(0, CART_Z0 + 90)[1]), "4x M16 cable glands")
    sh.leader(E.P(wx, CART_Z0 + CAP_T + 40), (E.P(wx + 150, 0)[0], E.P(0, CART_Z0 + 30)[1]), "wiper servo housing (IP68)")
    sh.leader(E.P(wx + 45, -300), (E.P(wx + 150, 0)[0], E.P(0, -250)[1]), "sample intake strainer")
    sh.leader(E.P(wx - 45, -353), (E.P(wx - 150, 0)[0], E.P(0, -420)[1]), "wiper arm + brush pads", ha="right")
    sh.leader(E.P(wx - 74, -220), (E.P(wx - 150, 0)[0], E.P(0, -150)[1]), "316L rod cage D6", ha="right")
    sh.leader(E.P(141, 0), (E.P(wx - 150, 0)[0], E.P(0, 60)[1]), "V deflector (HDPE 8)", ha="right")
    # plan of probe ring, drawn from parameters (scale 1:1.33)
    cx, cy, kr = 245, 212, 0.65
    sh.ax.add_patch(Circle((cx, cy), (WELL_OD / 2 - WELL_WALL) * kr, fc="#f4f7f9", ec=INK, lw=LW_MED, zorder=5))
    sh.ax.add_patch(Circle((cx, cy), WELL_OD / 2 * kr, fill=False, ec=INK, lw=LW_MED, zorder=5))
    cols = {"pH": "#1a59cc", "EC": "#f07a0d", "DO": "#26b240", "TU": "#d9268c"}
    for nm, al in (("pH", 45), ("EC", 135), ("DO", 225), ("TU", 315)):
        px, py = cx + PROBE_R * kr * math.cos(math.radians(al)), cy + PROBE_R * kr * math.sin(math.radians(al))
        sh.ax.add_patch(Circle((px, py), PROBE_D / 2 * kr, fc=cols[nm], ec=INK, lw=LW_THIN, zorder=6))
        sh.text(px, py, nm, size=2.4, ha="center", va="center", color="white", weight="bold")
    sh.ax.add_patch(Circle((cx, cy), 12.5 * kr, fc="#c8d0d6", ec=INK, lw=LW_THIN, zorder=6))
    sh.ax.add_patch(Circle((cx + 45 * kr, cy), 12 * kr, fc="#9aa6af", ec=INK, lw=LW_THIN, zorder=6))
    sh.text(cx + 45 * kr, cy - 13, "intake", size=2.0, ha="center")
    sh.line([(cx - 62 * kr, cy), (cx + 62 * kr, cy)], lw=LW_MED, color="#5b6b78")
    sh.text(cx - 64 * kr - 2, cy + 2, "wiper (parked)", size=2.0, ha="right", color="#5b6b78")
    sh.centerline((cx - 70, cy), (cx + 70, cy))
    sh.centerline((cx, cy - 70), (cx, cy + 70))
    sh.ax.add_patch(Arc((cx, cy), 2 * PROBE_R * kr, 2 * PROBE_R * kr, theta1=0, theta2=360, ec=DIM, lw=LW_THIN, ls=(0, (3, 2)), zorder=6))
    sh.leader((cx, cy - PROBE_R * kr), (cx + 52, cy - 50), f"PCD {2 * PROBE_R:.0f}")
    sh.leader((cx + WELL_OD / 2 * kr * 0.7071, cy + WELL_OD / 2 * kr * 0.7071), (cx + 52, cy + 52), "sleeve OD 160")
    sh.view_title(cx, 285, "PROBE LAYOUT (1:1.5, looking down)", "colour bands key each probe to its port")
    rows = [("AS3-401", "Sensor well sleeve PE100 160 SDR26", 1), ("AS3-402", "Hatch flange ring 316L t6", 1),
            ("AS3-403", "Guard cage 316L", 1), ("AS3-404", "V debris deflector HDPE 8", 1),
            ("AS3-411", "Cartridge cap + servo housing (POM)", 1), ("AS3-412", "Lift handle 316", 1),
            ("AS3-413", "Spine 25x1.5 + wiper shaft", 1), ("AS3-414", "Probe holder spiders (POM)", 2),
            ("AS3-415", "Wiper arm + brush pads", 1), ("AS3-417", "Intake strainer + riser", 1),
            ("AS3-421..424", "pH / EC / DO / turbidity probes (RS485)", 4)]
    sh.table(185, 152, ["PART No.", "DESCRIPTION", "QTY"], rows, [24, 92, 10], row_h=4.2, size=2.2)
    sh.note_block(185, 96, [
        "Service: quarter-turn the cap, lift the cartridge by the handle - all probes, the wiper and the intake come up together.",
        "Probe envelopes are D32 x 300 placeholders: replace with the supplier STEP and re-run the build.",
        "Probe tips sit 340 mm below the keel, inside the cage, behind the deflector and in the pole wake.",
        "Cable run inside the sleeve; drip loop at the cap; IP68 glands only.",
    ], size=2.15)
    sh.save(os.path.join(OUT, "AS3-DWG-04_Sensor_Well_and_Cartridge.png"), pdf)


# ---------------------------------------------------------------------------
# DWG-05 Pontoon hull (manufacturing drawing for the rotomoulder)
# ---------------------------------------------------------------------------
def dwg_hull(pdf):
    sh = Sheet("AS3-DWG-05", "PONTOON HULL - ROTOMOULDED (2 OFF, ONE MOULD)", "1:5 (sections 1:4)",
               "PE rotomoulding grade, UV stabilised, RAL 1003", "5/6")
    _, hw, zb = hull_local()
    L, W, Hh = PONT_L, PONT_W, PONT_H
    k = 0.2
    x0p, yprof, yplan = 40, 200, 118
    xs = np.linspace(0, L, 400)
    # profile
    keel = np.array([zb(x) for x in xs])
    prof = np.vstack([np.c_[xs, keel], [[L, Hh], [0, Hh]]])
    sh.ax.add_patch(Polygon(np.c_[x0p + prof[:, 0] * k, yprof + prof[:, 1] * k], closed=True, fc="#fbf6e3", ec=INK, lw=LW_THICK, zorder=5))
    for zr in (RUBRAIL_Z - RUBRAIL_R, RUBRAIL_Z + RUBRAIL_R):
        sh.line([(x0p + 105 * k, yprof + zr * k), (x0p + (L - 75) * k, yprof + zr * k)], lw=LW_THIN)
    sh.waterline(x0p - 5, x0p + L * k + 5, yprof + DRAFT * k, f"DWL {DRAFT:.0f}")
    sh.view_title(x0p + L * k / 2, 280, "PROFILE", "bow at left (pole side)")
    sh.dim((x0p, yprof), (x0p + L * k, yprof), -12, f"{L:.0f}")
    sh.dim((x0p + L * k, yprof), (x0p + L * k, yprof + Hh * k), 8, f"{Hh:.0f}", vertical=True, flip_text=True)
    sh.dim((x0p, yprof), (x0p + BOW_ROCKER_L * k, yprof), -5, f"rocker {BOW_ROCKER_L:.0f}")
    sh.dim((x0p, yprof), (x0p, yprof + BOW_ROCKER_H * k), -6, f"{BOW_ROCKER_H:.0f}", vertical=True)
    sh.dim((x0p + (L - STERN_ROCKER_L) * k, yprof), (x0p + L * k, yprof), -5, f"{STERN_ROCKER_L:.0f}")
    sh.dim((x0p + L * k, yprof), (x0p + L * k, yprof + STERN_ROCKER_H * k), 16, f"{STERN_ROCKER_H:.0f}", vertical=True, flip_text=True)
    sh.leader((x0p + 600 * k, yprof + RUBRAIL_Z * k), (x0p + 640 * k, yprof + 300 * k), f"rub rail R{RUBRAIL_R:.0f} at z {RUBRAIL_Z:.0f}, both sides")
    sh.text(x0p + 4, yprof + (Hh * k) / 2 + 3, "keel: z = H(1 - x/L)^2 over the rocker length", size=1.9, color="#4b5b68")
    # plan
    half = np.array([hw(x) for x in xs])
    plan = np.vstack([np.c_[xs, half], np.c_[xs[::-1], -half[::-1]]])
    sh.ax.add_patch(Polygon(np.c_[x0p + plan[:, 0] * k, yplan + plan[:, 1] * k], closed=True, fc="#fbf6e3", ec=INK, lw=LW_THICK, zorder=5))
    sh.centerline((x0p - 6, yplan), (x0p + L * k + 6, yplan))
    sh.view_title(x0p + L * k / 2, yplan + W * k / 2 + 14, "PLAN", "moulded-in M8 A4 inserts shown +")
    sh.dim((x0p + L * k, yplan - W / 2 * k), (x0p + L * k, yplan + W / 2 * k), 8, f"{W:.0f}", vertical=True, flip_text=True)
    sh.leader((x0p + 18 * k, yplan + (W / 2 - 18) * k), (x0p - 2, yplan + 40), f"R{BOW_PLAN_R:.0f}", ha="right")
    sh.leader((x0p + (L - 12) * k, yplan + (W / 2 - 12) * k), (x0p + L * k + 4, yplan + 40), f"R{STERN_PLAN_R:.0f}")
    inserts = []
    for bx in BEAM_X:
        for dy in (-30, 30):
            inserts.append((bx - PONT_X0, dy, "beam M8"))
    for hx in (240.0, 760.0):
        for dx in (-60, 60):
            inserts.append((hx + dx - PONT_X0, (W / 2 - 24), "handle M8"))
    inserts.append((780 - PONT_X0, 0.0, "vent plug boss G3/4"))
    for xi, yi, _ in inserts:
        px, py = x0p + xi * k, yplan + yi * k
        sh.line([(px - 1.5, py), (px + 1.5, py)], lw=LW_MED)
        sh.line([(px, py - 1.5), (px, py + 1.5)], lw=LW_MED)
    # sections
    def section(xl, cx, cy, ks, tag):
        h_ = hw(xl)
        z0 = zb(xl)
        rb = min(HULL_RB, h_ - 0.6, (Hh - z0) / 2 - 0.6)
        ring = g.rrect2d_tb(-h_, h_, z0, Hh, rb, min(HULL_RT, h_ - 0.6), 10)
        sh.ax.add_patch(Polygon(np.c_[cx + ring[:, 0] * ks, cy + ring[:, 1] * ks], closed=True, fc="#fbf6e3", ec=INK, lw=LW_THICK, zorder=5))
        inner = g.rrect2d_tb(-h_ + HULL_WALL, h_ - HULL_WALL, z0 + HULL_WALL, Hh - HULL_WALL, max(rb - HULL_WALL, 1), max(HULL_RT - HULL_WALL, 1), 10)
        sh.ax.add_patch(Polygon(np.c_[cx + inner[:, 0] * ks, cy + inner[:, 1] * ks], closed=True, fc="#e8dfc2", ec=INK, lw=LW_THIN,
                                hatch="..", zorder=6))
        if xl > 100:
            for s_ in (1, -1):
                sh.ax.add_patch(Circle((cx + s_ * (h_ - 3) * ks, cy + RUBRAIL_Z * ks), RUBRAIL_R * ks, fc="#fbf6e3", ec=INK, lw=LW_MED, zorder=5))
        sh.waterline(cx - (h_ + 25) * ks, cx + (h_ + 25) * ks, cy + DRAFT * ks, "DWL")
        sh.view_title(cx, cy + Hh * ks + 16, f"SECTION {tag}", f"x = {xl:.0f} from bow tip")
        return h_, z0
    ks = 0.25
    cy0 = 192
    h_, z0 = section(500, 300, cy0, ks, "D-D")
    sh.dim((300 - h_ * ks, cy0), (300 + h_ * ks, cy0), -7, f"{2 * h_:.0f}")
    sh.leader((300 + (h_ - 12) * ks, cy0 + 12 * ks), (300 + 40, cy0 - 12), f"R{HULL_RB:.0f}")
    sh.leader((300 + (h_ - 4) * ks, cy0 + (Hh - 4) * ks), (300 + 40, cy0 + Hh * ks + 4), f"R{HULL_RT:.0f}")
    sh.leader((300 - (h_ - HULL_WALL / 2) * ks, cy0 + 150 * ks), (300 - 42, cy0 + 50), f"wall {HULL_WALL:.0f}", ha="right")
    sh.leader((300 - 30 * ks, cy0 + 90 * ks), (300 - 42, cy0 + 8), "PU foam fill", ha="right")
    section(60, 372, cy0, ks, "E-E")
    hv = H["hull_volume_L"] / 2
    sh.note_block(260, 112, [
        "Rotomoulded PE, UV-stabilised rotomoulding grade, colour RAL 1003 (signal yellow, IALA special-mark colour for data buoys).",
        "Wall 5 mm nominal, 4 mm minimum at corners. Both hulls from ONE mould (rub rails on both sides).",
        "Moulded-in 316 M8 inserts as marked (8 beam + 4 handle) + vent plug boss; pull-out to be verified by the moulder.",
        "Leak test 0.1 bar air / soap before foam fill; fill with closed-cell PU foam 32 kg/m3 (stays afloat if punctured).",
        f"Moulded volume {hv:.1f} L each; shell + foam mass {CHK['mass_table'][0]['kg']} kg each (CAD estimate).",
    ], size=2.15)
    sh.save(os.path.join(OUT, "AS3-DWG-05_Pontoon_Hull.png"), pdf)


# ---------------------------------------------------------------------------
# DWG-06 Pier bracket
# ---------------------------------------------------------------------------
def dwg_bracket(pdf):
    sh = Sheet("AS3-DWG-06", "PIER BRACKET (WELDMENT) + CLAMP CAP", "1:4", "SS 316L, passivated", "6/6")
    k = 0.25
    zb = LV["zb_low"]
    E = place_view(sh, "brk_elev", (120, 215), k)
    Pn = place_view(sh, "brk_plan", (120, 110), k)
    A_ = place_view(sh, "brk_end", (300, 215), k)
    sh.view_title(120, 286, "ELEVATION")
    sh.view_title(120, 160, "PLAN")
    sh.view_title(300, 286, "VIEW FROM RIVER (B)")
    xp = -PIER_STANDOFF
    sh.dim(E.P(xp, zb - 120), E.P(0, zb - 120), -4, f"{PIER_STANDOFF:.0f}")
    sh.dim(E.P(xp - 10, zb - 90), E.P(xp - 10, zb + 90), -6, f"{BRK_PLATE[2]:.0f}", vertical=True)
    sh.dim(E.P(70, zb - CLAMP_H / 2), E.P(70, zb + CLAMP_H / 2), 6, f"{CLAMP_H:.0f}", vertical=True, flip_text=True)
    sh.dim(Pn.P(-CLAMP_OD / 2, -100), Pn.P(CLAMP_OD / 2, -100), -4, f"OD {CLAMP_OD:.0f}")
    sh.dim(Pn.P(xp, -130), Pn.P(xp + BRK_PLATE[0], -130), -4, f"{BRK_PLATE[0]:.0f}")
    sh.dim(A_.P(-110, zb - 110), A_.P(110, zb - 110), -4, f"{BRK_PLATE[1]:.0f}")
    sh.dim(A_.P(-80, zb + 110), A_.P(80, zb + 110), 4, "160 anchor ctrs")
    sh.dim(A_.P(130, zb - 60), A_.P(130, zb + 60), 6, "120", vertical=True, flip_text=True)
    sh.leader(Pn.P(0, 0), (Pn.P(60, 0)[0], Pn.P(0, 70)[1]), "bore 60.7 (pole 60.3)")
    rows = [("AS3-101", "Pier bracket weldment", "2", "316L 10/12 mm"), ("AS3-102", "Clamp cap", "2", "316L"),
            ("AS3-103", "Stage target plate (upper only)", "1", "316L t4"), ("AS3-905", "Bolt M10x40 + washer", "4", "A4-70"),
            ("AS3-904", "Chemical anchor M12x130", "8", "A4 + mortar"), ("AS3-113/114", "Stop collar + EPDM buffer", "2+2", "316L / EPDM")]
    sh.table(225, 145, ["PART No.", "DESCRIPTION", "QTY", "MATERIAL"], rows, [24, 66, 10, 30], row_h=4.4, size=2.2)
    sh.note_block(225, 108, [
        "Upper and lower brackets are identical: one weld fixture, one drawing.",
        f"Design reaction per bracket {CHK['pole']['bracket_reaction_N']} N horizontal (1.5 m/s current + 500 N debris).",
        "Anchor embedment and edge distance to the anchor maker's data for the pier concrete grade - verify on site.",
        "Weld: TIG, ER316LSi filler, full fillet all round; pickle and passivate after welding.",
        "Clamp bore reamed 60.7; tighten M10 to 35 N.m; pole must not rotate or slip under hand load.",
    ], size=2.15)
    sh.save(os.path.join(OUT, "AS3-DWG-06_Pier_Bracket.png"), pdf)


def main(which=None):
    os.makedirs(OUT, exist_ok=True)
    fns = [("ga", dwg_ga), ("install", dwg_install), ("carriage", dwg_carriage), ("sensor", dwg_sensor),
           ("hull", dwg_hull), ("bracket", dwg_bracket)]
    with PdfPages(os.path.join(OUT, "AquaSentinel_R3_Drawing_Set.pdf")) as pdf:
        for key, fn in fns:
            if which and key not in which:
                continue
            fn(pdf)
            print("drawn", key)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
