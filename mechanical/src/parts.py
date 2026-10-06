"""
AquaSentinel R3 - part library and assembly structure.

build_float()            -> parts + instances of everything that rides on the water (float frame)
build_guide(draft_mm)    -> parts + instances fixed to the pier (world frame), positioned from the draft
build_environment(L)     -> pier (render context only, not part of the product)
"""
import math
import numpy as np

import geom as g
from geom import T, Rx, Ry, Rz, place
from params import *

DZ = DECK_Z1


# ---------------------------------------------------------------------------
# data classes
# ---------------------------------------------------------------------------
class Part:
    def __init__(self, key, pid, name, shells, mat, mass="solid", kg=None, shell_t=None, process="", desc="",
                 note="", kind="part", hollow=False):
        self.key, self.pid, self.name = key, pid, name
        self.shells = shells if isinstance(shells, list) else [shells]
        self.mat = mat
        self.mass_rule = mass          # 'solid' | 'shell' | 'kg'
        self.kg_fixed = kg
        self.shell_t = shell_t
        self.process, self.desc, self.note = process, desc, note
        self.kind = kind               # part | purchased | fastener | harness | env
        self.hollow = hollow           # enclosures: modelled closed, physically a shell with contents

    def volume_mm3(self):
        return sum(s.signed_volume() for s in self.shells)

    def area_mm2(self):
        return sum(s.area() for s in self.shells)

    def mass_kg(self):
        rho = MATERIALS[self.mat]["rho"]
        if self.mass_rule == "kg":
            return float(self.kg_fixed)
        if self.mass_rule == "shell":
            return rho * self.area_mm2() * self.shell_t * 1e-9 + (self.kg_fixed or 0.0)
        return rho * self.volume_mm3() * 1e-9

    def mass_basis(self):
        if self.mass_rule == "kg":
            return "catalogue / assumed"
        if self.mass_rule == "shell":
            return f"CAD area x {self.shell_t:g} mm wall" + (" + fill" if self.kg_fixed else "")
        return "CAD volume x density"

    def centroid_local(self):
        num = np.zeros(3)
        den = 0.0
        for s in self.shells:
            t = s.triangles()
            a, b, c = s.V[t[:, 0]], s.V[t[:, 1]], s.V[t[:, 2]]
            v = np.einsum("ij,ij->i", a, np.cross(b, c)) / 6.0
            num += ((a + b + c) / 4.0 * v[:, None]).sum(axis=0)
            den += v.sum()
        if abs(den) < 1e-9:
            return np.vstack([s.V for s in self.shells]).mean(axis=0)
        return num / den


class Inst:
    def __init__(self, part, name, M=None, group="float", explode=(0, 0, 0), step=0, label=None):
        self.part = part
        self.name = name
        self.M = np.eye(4) if M is None else np.asarray(M, float)
        self.group = group     # float | gate | canopy | podlid | samplerlid | cartridge | guide | env
        self.explode = np.asarray(explode, float)
        self.step = step
        self.label = label or part.name


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _ring(p, axis, a):
    col = np.full(len(p), a)
    if axis == "x":
        return np.c_[col, p[:, 0], p[:, 1]]
    if axis == "y":
        return np.c_[p[:, 0], col, p[:, 1]]
    return np.c_[p[:, 0], p[:, 1], col]


def prism(profile2d, axis, a0, a1):
    p = np.asarray(profile2d, float)
    return g.loft([_ring(p, axis, a0), _ring(p, axis, a1)])


def hollow_prism(outer, inner, axis, a0, a1):
    o, i = np.asarray(outer, float), np.asarray(inner, float)
    return g.loft([_ring(o, axis, a0), _ring(o, axis, a1), _ring(i, axis, a1), _ring(i, axis, a0)], close_loop=True)


def window_plate(outer, inner, axis, a0, a1):
    o, i = g.window_loops(outer, inner)
    return hollow_prism(o, i, axis, a0, a1)


def rect2d(u0, u1, v0, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def revolve_partial(loop_rz, a0_deg, a1_deg, n=24):
    loop = np.asarray(loop_rz, float)
    rings = []
    for t in np.radians(np.linspace(a0_deg, a1_deg, n)):
        rings.append(np.c_[loop[:, 0] * math.cos(t), loop[:, 0] * math.sin(t), loop[:, 1]])
    return g.loft(rings, closed_rings=True)


# ---------------------------------------------------------------------------
# FLOAT
# ---------------------------------------------------------------------------
def hull_local():
    """Rotomoulded pontoon: local x = 0 at bow tip ... PONT_L at stern, y = 0 on its centreline."""
    L, W, H = PONT_L, PONT_W, PONT_H
    Rb, Rs = BOW_PLAN_R, STERN_PLAN_R
    xs = [Rb * (1 - math.cos(t)) for t in np.linspace(0, math.pi / 2, 10)]
    xs += list(np.linspace(Rb, BOW_ROCKER_L, 7)[1:])
    xs += list(np.linspace(BOW_ROCKER_L, L - STERN_ROCKER_L, 4)[1:])
    xs += list(np.linspace(L - STERN_ROCKER_L, L - Rs, 5)[1:])
    xs += [L - Rs * (1 - math.cos(t)) for t in np.linspace(math.pi / 2, 0, 9)[1:]]
    xs = sorted(set(round(x, 4) for x in xs))

    def hw(x):
        if x < Rb:
            return (W / 2 - Rb) + math.sqrt(max(Rb ** 2 - (Rb - x) ** 2, 0))
        if x > L - Rs:
            return (W / 2 - Rs) + math.sqrt(max(Rs ** 2 - (x - (L - Rs)) ** 2, 0))
        return W / 2

    def zb(x):
        if x < BOW_ROCKER_L:
            return BOW_ROCKER_H * (1 - x / BOW_ROCKER_L) ** 2
        if x > L - STERN_ROCKER_L:
            return STERN_ROCKER_H * (1 - (L - x) / STERN_ROCKER_L) ** 2
        return 0.0

    rings = []
    for x in xs:
        h = hw(x)
        z0 = zb(x)
        rb = min(HULL_RB, h - 0.6, (H - z0) / 2 - 0.6)
        sec = g.rrect2d_tb(-h, h, z0, H, rb, min(HULL_RT, h - 0.6), 7)
        rings.append(np.c_[np.full(len(sec), x), sec[:, 0], sec[:, 1]])
    shells = [g.loft(rings)]
    for s in (1, -1):  # rub rails on both sides -> one mould makes both hulls
        shells.append(g.pipe_along([(105, s * (W / 2 - 3), RUBRAIL_Z), (L - 75, s * (W / 2 - 3), RUBRAIL_Z)],
                                   RUBRAIL_R, 14))
    return shells, hw, zb


def build_float():
    parts, inst = {}, []

    def add(p):
        parts[p.key] = p
        return p

    # ---------------- 2xx hull and frame ---------------------------------
    hshells, hw_fn, zb_fn = hull_local()
    foam_kg = FOAM_DENSITY * hshells[0].signed_volume() * 1e-9
    pont = add(Part("pontoon", "AS3-201", "Pontoon hull (rotomoulded, foam filled)", hshells, "HDPE_YELLOW",
                    mass="shell", shell_t=HULL_WALL, kg=foam_kg,
                    process="Rotomoulded PE, one mould for both hulls; PU foam fill; moulded-in M8 inserts",
                    desc=f"{PONT_L:.0f} x {PONT_W:.0f} x {PONT_H:.0f} hull with bow rocker, rounded plan form, integral rub rails"))
    for s, nm in ((1, "Pontoon_Starboard"), (-1, "Pontoon_Port")):
        inst.append(Inst(pont, nm, T(PONT_X0, s * PONT_YC, 0), explode=(0, s * 700, -60), step=3))

    tip_z = (BOW_ROCKER_H + PONT_H) / 2
    bumper = add(Part("bumper", "AS3-202", "Bow bumper pad", [g.rounded_box(16, 44, 90, 6, 3, 5, 3)], "RUBBER",
                      process="Moulded EPDM, bonded", desc="Pier-contact pad on each bow"))
    for s in (1, -1):
        inst.append(Inst(bumper, f"Bow_Bumper_{'S' if s > 0 else 'P'}", T(PONT_X0 - 8, s * PONT_YC, tip_z),
                         explode=(-260, s * 700, -60), step=3))

    plug = add(Part("plug", "AS3-203", "Hull vent / test plug",
                    [g.revolve([(0, 0), (17, 0), (17, 5), (13, 9), (0, 9)], 28), g.hex_prism(14, 9, 15)], "POM_BLACK",
                    process="Purchased PE threaded plug", kind="purchased"))
    for s in (1, -1):
        inst.append(Inst(plug, f"Hull_Plug_{'S' if s > 0 else 'P'}", T(780, s * PONT_YC, PONT_H),
                         explode=(0, s * 700, 140), step=3))

    outer = g.rrect2d(BEAM_A, BEAM_A, 4.0, 4)
    inner = g.rrect2d(BEAM_A - 2 * BEAM_T, BEAM_A - 2 * BEAM_T, 1.5, 4)
    beam = add(Part("beam", "AS3-211", "Crossbeam SHS 40x40x3", [hollow_prism(outer, inner, "y", -BEAM_HALF, BEAM_HALF)],
                    "AL6061", process="Saw-cut 6061-T6 SHS, drilled for M8", desc="Ties both hulls, carries the deck"))
    zc = (BEAM_Z0 + BEAM_Z1) / 2
    for i, bx in enumerate(BEAM_X):
        inst.append(Inst(beam, f"Crossbeam_{i + 1}", T(bx, 0, zc), explode=(0, 0, 450 + 60 * i), step=4))
    cap = add(Part("beamcap", "AS3-212", "Beam end cap", [prism(g.rrect2d(BEAM_A + 1, BEAM_A + 1, 4.5, 4), "y", 0, 4)],
                   "POM_BLACK", process="Purchased PE plug", kind="purchased"))
    for i, bx in enumerate(BEAM_X):
        inst.append(Inst(cap, f"Beam_Cap_{i + 1}S", T(bx, BEAM_HALF, zc), explode=(0, 170, 450 + 60 * i), step=4))
        inst.append(Inst(cap, f"Beam_Cap_{i + 1}P", T(bx, -BEAM_HALF, zc) @ Rz(180), explode=(0, -170, 450 + 60 * i), step=4))

    deck = add(Part("deck", "AS3-213", "Equipment deck plate",
                    [g.plate_with_hole(g.rrect2d(DECK_X1 - DECK_X0, 2 * DECK_HW, 14, 5, (DECK_X0 + DECK_X1) / 2, 0),
                                       (WELL_X, 0), WELL_OD / 2 + 2, DECK_Z0, DECK_Z1, 64)],
                    "AL6061", process="Laser-cut 3 mm 6061 tread plate", desc="Deck with hatch for the sensor well"))
    inst.append(Inst(deck, "Deck_Plate", explode=(0, 0, 720), step=4))

    m8 = add(Part("m8", "AS3-901", "Bolt M8 x 60 A4 + washer", g.bolt(8, 60), "SS316L", process="A4-70", kind="fastener"))
    for i, bx in enumerate(BEAM_X):
        for s in (1, -1):
            for dy in (-30, 30):
                inst.append(Inst(m8, f"M8_B{i + 1}_{'S' if s > 0 else 'P'}{'a' if dy < 0 else 'b'}",
                                 T(bx, s * PONT_YC + dy, BEAM_Z1), explode=(0, 0, 950 + 60 * i), step=4))

    # ---------------- 3xx guide carriage (6061 weldment, opening gate) ----
    t1, t2 = TIER_Z
    pt = CARR_PLATE_T
    H0, H1 = t1, CARR_TOP
    hole_r = 40.0
    half_poly = [(0.5, -CARR_HALF), (CARR_HALF, -CARR_HALF), (CARR_HALF, CARR_HALF), (0.5, CARR_HALF), (0.5, hole_r)]
    half_poly += [tuple(p) for p in g.arc(0.5, 0, hole_r, math.pi / 2, -math.pi / 2, 15)[1:-1]]
    half_poly += [(0.5, -hole_r)]
    gate_poly = [(-x, y) for (x, y) in reversed(half_poly)]
    gate_poly = [(x, min(y, CARR_HALF - 1)) for (x, y) in gate_poly]

    def cheeks(alpha_deg, ztop):
        a = math.radians(alpha_deg)
        M = T(ROLLER_RC * math.cos(a), ROLLER_RC * math.sin(a), ztop) @ Rz(alpha_deg)
        out = []
        for y0, y1 in ((22, 28), (-28, -22)):
            out += place(g.box(-18, 28, y0, y1, 0, 56), M)
        return out

    wz0, wz1 = t1 + TIER_T + 42, t2 - 38
    fixed, gate = [], []
    for tz in (t1, t2):
        fixed.append(g.extrude(half_poly, tz, tz + TIER_T))
        gate.append(g.extrude(gate_poly, tz, tz + TIER_T))
        for al in (45, -45):
            fixed += cheeks(al, tz + TIER_T)
        for al in (135, 225):
            gate += cheeks(al, tz + TIER_T)
    # back plate (bolts to crossbeam 1), window above the bolt line
    fixed.append(window_plate(rect2d(-CARR_HALF, CARR_HALF, H0, H1), g.rrect2d(124, 150, 16, 4, 0, 440.0),
                              "x", CARR_HALF, CARR_HALF + pt))
    # starboard side plate, full length (carries the hinge)
    fixed.append(window_plate(rect2d(-CARR_HALF - pt, CARR_HALF + pt, H0, H1), g.rrect2d(140, wz1 - wz0, 16, 4, 0, (wz0 + wz1) / 2),
                              "y", CARR_HALF, CARR_HALF + pt))
    # port side plate, fixed half
    fixed.append(window_plate(rect2d(0.5, CARR_HALF, H0, H1), g.rrect2d(56, wz1 - wz0, 14, 4, 48, (wz0 + wz1) / 2),
                              "y", -CARR_HALF - pt, -CARR_HALF))
    # gate: front plate + port side plate
    gate.append(window_plate(rect2d(-CARR_HALF, CARR_HALF - 1, H0, H1), g.rrect2d(124, wz1 - wz0, 16, 4, 0, (wz0 + wz1) / 2),
                             "x", -CARR_HALF - pt, -CARR_HALF))
    gate.append(window_plate(rect2d(-CARR_HALF, -0.5, H0, H1), g.rrect2d(56, wz1 - wz0, 14, 4, -48, (wz0 + wz1) / 2),
                             "y", -CARR_HALF - pt, -CARR_HALF))
    hx, hy = HINGE_XY
    for z0, z1 in ((t1 + 50, t1 + 90), (t2 - 70, t2 - 30)):
        fixed.append(g.cylinder(10, z0, z1, 24, hx, hy))
        fixed.append(g.box(hx, -CARR_HALF - pt + 0.5, CARR_HALF + pt - 0.5, hy, z0, z1))
    for z0, z1 in ((t1 + 92, t1 + 132), (t2 - 112, t2 - 72)):
        gate.append(g.cylinder(10, z0, z1, 24, hx, hy))
        gate.append(g.box(hx, -CARR_HALF - pt, CARR_HALF - 0.5, hy - 1, z0, z1))
    latch_z = (t1 + 110, t2 - 80)
    for zl in latch_z:
        fixed.append(g.box(-16, 16, -CARR_HALF - pt - 18, -CARR_HALF - pt, zl, zl + 12))
        gate.append(g.box(-16, 16, -CARR_HALF - pt - 18, -CARR_HALF - pt, zl + 13, zl + 25))
    fixed.append(g.box(CARR_HALF + pt, 140, -26, 26, H1 - 6, H1))                     # stage-sensor shelf
    for s in (1, -1):                                                                   # strut lugs
        fixed.append(g.box(CARR_HALF + pt, CARR_HALF + pt + 18, s * 86 - 8, s * 86 + 8, H1 - 40, H1 - 8))
    carr_fixed = add(Part("carr_fixed", "AS3-301", "Guide carriage - fixed half (weldment)", fixed, "AL6061",
                          process="Laser-cut 6061 plate 5/6 mm, TIG welded, hard anodised; nylon isolation at 316 axles",
                          desc="Two roller tiers 350 mm apart; carries hinge knuckles, latch lugs and the stage-sensor shelf"))
    carr_gate = add(Part("carr_gate", "AS3-302", "Guide carriage - opening gate (weldment)", gate, "AL6061",
                         process="Laser-cut 6061 plate, TIG welded, hard anodised",
                         desc="Front half with the two upstream rollers per tier; swings forward to release the pole"))
    inst.append(Inst(carr_fixed, "Carriage_Fixed", explode=(0, 0, 950), step=5))
    inst.append(Inst(carr_gate, "Carriage_Gate", group="gate", explode=(-700, 0, 950), step=5))

    rc, rp = ROLLER_RC, POLE_R + ROLLER_CLEAR
    loop = [(ROLLER_BORE / 2 + 0.5, -ROLLER_W / 2)]
    for a in np.linspace(-ROLLER_W / 2, ROLLER_W / 2, 15):
        loop.append((rc - math.sqrt(rp ** 2 - a ** 2), a))
    loop.append((ROLLER_BORE / 2 + 0.5, ROLLER_W / 2))
    roller = add(Part("roller", "AS3-311", "Concave guide roller UHMW-PE", [g.revolve_closed(loop, 40)], "UHMW",
                      process="CNC-turned UHMW-PE; throat profile = pole radius + 1.5 mm",
                      desc="Throat profile follows the pole, so contact is a line, not a point"))
    axle = add(Part("axle", "AS3-312", "Roller axle M10 + nyloc nuts",
                    [g.cylinder(ROLLER_BORE / 2, -33, 33, 20), g.hex_prism(16, 28, 35), g.hex_prism(16, -35, -28)],
                    "SS_BRUSHED", process="316 shoulder bolt, nylon isolation washers", kind="fastener"))
    k = 0
    for tz in (t1, t2):
        for al in (45, -45, 135, 225):
            a = math.radians(al)
            M = T(rc * math.cos(a), rc * math.sin(a), tz + TIER_T + 31) @ g.align_z_to((-math.sin(a), math.cos(a), 0))
            grp = "gate" if al in (135, 225) else "float"
            k += 1
            ex = np.array([math.cos(a), math.sin(a), 0]) * 260 + np.array([0, 0, 950])
            if grp == "gate":
                ex = ex + np.array([-700, 0, 0])
            inst.append(Inst(roller, f"Roller_{k}", M, group=grp, explode=ex, step=5))
            inst.append(Inst(axle, f"Axle_{k}", M, group=grp, explode=ex * 1.3, step=5))

    hinge_pin = add(Part("hingepin", "AS3-313", "Gate hinge pin D10",
                         [g.cylinder(5, t1 + 45, t2 - 25, 20, hx, hy), g.cylinder(9, t2 - 25, t2 - 17, 20, hx, hy)],
                         "SS_BRUSHED", process="316 bar + R-clip", kind="fastener"))
    inst.append(Inst(hinge_pin, "Hinge_Pin", explode=(0, 0, 1600), step=5))
    latch = add(Part("latch", "AS3-314", "T-handle latch pin (tool-free)",
                     [g.cylinder(5, -22, 30, 20), g.cylinder(9, 26, 32, 20),
                      g.pipe_along([(-24, 0, 38), (24, 0, 38)], 4.5, 14), g.cylinder(4.5, 30, 38, 14)],
                     "SS_BRUSHED", process="316 bar + welded T-bar, lanyard eye", kind="fastener"))
    for i, zl in enumerate(latch_z):
        inst.append(Inst(latch, f"Latch_Pin_{i + 1}", T(0, -CARR_HALF - pt - 9, zl + 5), group="gate",
                         explode=(-700, 0, 1400), step=5))
    m10 = add(Part("m10", "AS3-902", "Bolt M10 x 70 A4 + washer", g.bolt(10, 70), "SS316L", process="A4-70", kind="fastener"))
    for i, dy in enumerate((-60, 60)):
        inst.append(Inst(m10, f"M10_Carriage_{i + 1}", T(CARR_HALF, dy, zc) @ g.align_z_to((-1, 0, 0)),
                         explode=(-320, 0, 950), step=5))

    strut_sh = []
    for s in (1, -1):
        a = np.array([CARR_HALF + pt + 26, s * 86, H1 - 24])
        b = np.array([BEAM_X[1], s * 155, DZ + 10])
        strut_sh += [g.pipe_along([a, b], 10, 18), g.cylinder(17, DZ, DZ + 6, 24, b[0], b[1]),
                     g.cylinder(11, DZ + 6, DZ + 16, 18, b[0], b[1])]
    strut = add(Part("strut", "AS3-321", "Carriage brace struts (pair)", strut_sh, "SS316L", mass="kg", kg=0.85,
                     process="316L tube 20 x 2, flattened ends, bolted through deck into crossbeam 2",
                     desc="Triangulates the carriage tower; splayed to keep the cartridge lift path clear"))
    inst.append(Inst(strut, "Carriage_Struts", explode=(0, 0, 1200), step=5))

    # ---------------- 4xx sensing ----------------------------------------
    wx = WELL_X
    well = add(Part("well", "AS3-401", "Sensor well sleeve PE100 D160 SDR26",
                    [g.tube(WELL_OD / 2, WELL_OD / 2 - WELL_WALL, WELL_BOT, WELL_TOP, 64, wx, 0)], "PE_PIPE",
                    process="Cut PE100 pressure pipe", desc="Dry-to-wet guide tube for the pull-up sensor cartridge"))
    inst.append(Inst(well, "Sensor_Well", explode=(0, 0, -950), step=6))
    flange = add(Part("flange", "AS3-402", "Hatch flange ring (quarter-turn seat)",
                      [g.tube(FLANGE_OD / 2, WELL_OD / 2, DZ, DZ + FLANGE_T, 64, wx, 0)], "SS316L",
                      process="Laser-cut 6 mm 316L ring, 6x M6 into deck"))
    inst.append(Inst(flange, "Hatch_Flange", explode=(0, 0, 640), step=6))
    m6 = add(Part("m6", "AS3-903", "Screw M6 x 25 A4", g.bolt(6, 25), "SS316L", process="A4-70", kind="fastener"))
    for k6 in range(6):
        a = math.radians(30 + 60 * k6)
        inst.append(Inst(m6, f"M6_Flange_{k6 + 1}", T(wx + 87.5 * math.cos(a), 87.5 * math.sin(a), DZ + FLANGE_T),
                         explode=(0, 0, 840), step=6))
    cage_sh = [g.tube(82, 66, WELL_BOT - 12, WELL_BOT, 48, wx, 0)]
    for k8 in range(8):
        a = math.radians(22.5 + 45 * k8)
        cage_sh.append(g.cylinder(CAGE_ROD_D / 2, CAGE_BOT, WELL_BOT - 12, 12, wx + CAGE_ROD_R * math.cos(a),
                                  CAGE_ROD_R * math.sin(a)))
    for zr in (-170.0, -275.0):
        cage_sh.append(g.tube(80, 70, zr, zr + 4, 48, wx, 0))
    cage_sh.append(g.tube(80, 64, CAGE_BOT - 4, CAGE_BOT, 48, wx, 0))
    cage_sh.append(g.box(wx - 64.5, wx + 64.5, -3, 3, CAGE_BOT - 4, CAGE_BOT))
    cage_sh.append(g.box(wx - 3, wx + 3, -64.5, -3.01, CAGE_BOT - 4, CAGE_BOT))
    cage_sh.append(g.box(wx - 3, wx + 3, 3.01, 64.5, CAGE_BOT - 4, CAGE_BOT))
    cage = add(Part("cage", "AS3-403", "Sensor guard cage", cage_sh, "SS316L",
                    process="316L rod D6 + laser-cut rings, TIG welded; screwed to the sleeve",
                    desc="Open rod cage: water flows through, debris and hands stay out"))
    inst.append(Inst(cage, "Sensor_Cage", explode=(0, 0, -1350), step=6))
    t_ = 8.0
    v = [(110, 0), (172, -62), (172, -62 + t_ * 1.414), (110 + t_ * 1.414, 0), (172, 62 - t_ * 1.414), (172, 62)]
    defl = add(Part("deflector", "AS3-404", "V debris deflector", [g.extrude(v, -330, BEAM_Z0 - 0.5)], "PE_PIPE",
                    process="8 mm HDPE sheet, heat-bent V, bolted under crossbeam 1",
                    desc="Splits floating debris ahead of the sensor well"))
    inst.append(Inst(defl, "Debris_Deflector", explode=(0, 0, -1550), step=6))

    # pull-up sensor cartridge
    c0 = CART_Z0
    c1 = c0 + CAP_T
    cap_sh = [g.cylinder(CAP_D / 2, c0, c1, 64, wx, 0), g.cylinder(28, c1, c1 + 46, 32, wx, 0),
              g.revolve([(28, 0), (24, 8), (0, 11)], 32).transformed(T(wx, 0, c1 + 46))]
    for gx, gy in ((wx + 60, 25), (wx + 60, -25), (wx - 60, 25), (wx - 60, -25)):
        cap_sh.append(g.hex_prism(20, c1, c1 + 9, gx, gy))
        cap_sh.append(g.cylinder(8, c1 + 9, c1 + 15, 16, gx, gy))
    for s in (1, -1):  # quarter-turn lock knobs
        cap_sh.append(g.cylinder(9, c1, c1 + 14, 20, wx, s * 75))
    ccap = add(Part("cart_cap", "AS3-411", "Cartridge cap + wiper drive housing", cap_sh, "POM_BLACK",
                    process="Machined acetal; IP68 servo housing; 4x M16 cable glands",
                    desc="Quarter-turn seat on the hatch flange; houses the wiper servo"))
    hand = add(Part("cart_handle", "AS3-412", "Cartridge lift handle",
                    [g.pipe_along([(wx, -45, c1), (wx, -45, c1 + 91), (wx, 45, c1 + 91), (wx, 45, c1)], 8, 18, fillet=24)],
                    "SS_BRUSHED", mass="kg", kg=0.15, process="316 tube 16 x 1.5 bent"))
    spine = add(Part("cart_spine", "AS3-413", "Cartridge spine + wiper shaft",
                     [g.tube(12.5, 11, -350, c0, 32, wx, 0), g.cylinder(4, -351, c0, 16, wx, 0)], "SS316L",
                     process="316L tube 25 x 1.5 + 316 shaft D8"))
    holder_sh = []
    for zh in (-62.0, -212.0):
        for al in (45, 135, 225, 315):
            a = math.radians(al)
            px, py = wx + PROBE_R * math.cos(a), PROBE_R * math.sin(a)
            holder_sh.append(g.tube(21, PROBE_D / 2, zh, zh + 12, 32, px, py))
            holder_sh.append(g.box(12.5, 25, -5, 5, zh, zh + 12).transformed(T(wx, 0, 0) @ Rz(al)))
        holder_sh.append(g.tube(19, 12.5, zh, zh + 12, 32, wx, 0))
    holder = add(Part("cart_holder", "AS3-414", "Probe holder spiders (x2)", holder_sh, "POM_BLACK",
                      process="Machined acetal, split collars", desc="Fix the four probes at colour-keyed positions"))
    probe = add(Part("probe", "AS3-420", "Probe body (envelope)",
                     [g.revolve([(0, 0), (12.5, 0), (14, 2), (14, 16), (PROBE_D / 2, 19), (PROBE_D / 2, PROBE_LEN - 68),
                                 (17, PROBE_LEN - 66), (17, PROBE_LEN - 30), (11, PROBE_LEN - 27), (11, PROBE_LEN),
                                 (0, PROBE_LEN)], 40)],
                     "POM_BLACK", mass="kg", kg=0.45, kind="purchased",
                     process="Purchased; D32 x 300 envelope - replace with the supplier STEP",
                     note="0.45 kg incl. 5 m cable (assumed)"))
    band_geo = [g.tube(PROBE_D / 2 + 0.8, PROBE_D / 2, PROBE_LEN - 100, PROBE_LEN - 72, 40)]
    for p_, nm in ((ccap, "Cartridge_Cap"), (hand, "Cartridge_Handle"), (spine, "Cartridge_Spine"), (holder, "Cartridge_Holders")):
        inst.append(Inst(p_, nm, group="cartridge", explode=(0, 0, 1400), step=11))
    for key, pid, nm, mat, al in (("ph", "AS3-421", "pH probe RS485 (SEN0708 class)", "PROBE_PH", 45),
                                  ("ec", "AS3-422", "EC probe RS485 K=10 (SEN0707 class)", "PROBE_EC", 135),
                                  ("do", "AS3-423", "Optical DO probe RS485 (SEN0680 class)", "PROBE_DO", 225),
                                  ("tu", "AS3-424", "Turbidity probe RS485 (SEN0710 class)", "PROBE_TU", 315)):
        bp = add(Part(f"band_{key}", pid, f"ID band - {nm.split(' ')[0]} {nm.split(' ')[1]}", band_geo, mat, mass="kg",
                      kg=0.005, process="Colour-keyed PE sleeve", kind="purchased"))
        a = math.radians(al)
        M = T(wx + PROBE_R * math.cos(a), PROBE_R * math.sin(a), PROBE_TIP_Z)
        inst.append(Inst(probe, f"Probe_{key.upper()}", M, group="cartridge", explode=(0, 0, 1400), step=11, label=nm))
        inst.append(Inst(bp, f"Probe_Band_{key.upper()}", M, group="cartridge", explode=(0, 0, 1400), step=11, label=nm))
    wip_sh = [g.box(wx - 62, wx + 62, -7, 7, -356, -351)]
    for s in (1, -1):
        wip_sh.append(g.box(wx + s * 45 - 11, wx + s * 45 + 11, -8, 8, -351, -341.5))
    wiper = add(Part("wiper", "AS3-415", "Optical wiper arm + brush pads", wip_sh, "SS316L",
                     process="316L flat bar 14 x 5 + nylon brush pads", desc="Sweeps all four probe windows; parks between probes"))
    inst.append(Inst(wiper, "Wiper_Arm", group="cartridge", explode=(0, 0, 1400), step=11))
    cab_sh = []
    tz_ = PROBE_TIP_Z + PROBE_LEN
    for al in (45, 135, 225, 315):
        a = math.radians(al)
        px, py = wx + PROBE_R * math.cos(a), PROBE_R * math.sin(a)
        gx, gy = wx + (60 if math.cos(a) > 0 else -60), (25 if math.sin(a) > 0 else -25)
        cab_sh.append(g.pipe_along([(px, py, tz_), (px, py, 150), (gx, gy, 240), (gx, gy, c0 - 0.5)], 3.5, 10, fillet=30))
    pcab = add(Part("probe_cables", "AS3-416", "Probe cables (in-well run)", cab_sh, "CABLE", mass="kg", kg=0.0,
                    process="Supplied with probes (mass counted with the probes)", kind="harness"))
    inst.append(Inst(pcab, "Probe_Cables", group="cartridge", explode=(0, 0, 1400), step=11))
    ix = wx + 45
    intake = add(Part("intake", "AS3-417", "Sampler intake strainer + riser",
                      [g.cylinder(12, -335, -270, 24, ix, 0), g.tube(5, 3, -270, c0, 16, ix, 0),
                       g.cylinder(8, c1, c1 + 21, 20, ix, 0)], "SS_BRUSHED", mass="kg", kg=0.15,
                      process="316 mesh strainer + 10 mm tube + quick-connect",
                      desc="Draws the sample at the same depth as the probes"))
    inst.append(Inst(intake, "Sampler_Intake", group="cartridge", explode=(0, 0, 1400), step=11))

    # ---------------- 5xx power and control pod --------------------------
    P = POD
    pcx = (P["x0"] + P["x1"]) / 2
    rails = add(Part("podrails", "AS3-501", "Pod mounting rails (pair)",
                     [g.box(P["x0"] + 5, P["x1"] - 5, s * 100 - 12, s * 100 + 12, DZ, DZ + 12) for s in (1, -1)],
                     "AL6061", process="6061 angle 25 x 25 x 3"))
    inst.append(Inst(rails, "Pod_Rails", explode=(0, 0, 520), step=7))
    pz0 = DZ + 12
    body = [g.rounded_box(P["x1"] - P["x0"], 2 * P["hw"], P["h"], 14, 5, 6, 3, (pcx, 0, pz0 + P["h"] / 2))]
    for gy in (-80, -40, 0, 40, 80):
        body += place([g.hex_prism(22, 0, 8), g.cylinder(8.5, 8, 15, 20)], T(P["x0"], gy, pz0 + 30) @ g.align_z_to((-1, 0, 0)))
    for gy in (-100, 100):
        body += place([g.hex_prism(22, 0, 8), g.cylinder(8.5, 8, 15, 20)], T(P["x1"], gy, pz0 + 55) @ g.align_z_to((1, 0, 0)))
    body += place([g.cylinder(11, 0, 9, 24)], T(pcx + 90, -P["hw"], pz0 + 110) @ g.align_z_to((0, -1, 0)))  # pressure vent
    for bx in (pcx - 80, pcx + 80):
        for lx in (bx - 31, bx + 19):
            body.append(g.box(lx, lx + 12, P["hw"] - 0.5, P["hw"] + 9, pz0 + P["h"] - 22, pz0 + P["h"] - 7.5))
        body.append(g.box(bx - 14, bx + 14, -P["hw"] - 10, -P["hw"] + 0.5, pz0 + P["h"] - 34, pz0 + P["h"] - 6))
    pod = add(Part("pod", "AS3-511", "Power & control pod IP67 (body)", body, "PC_GREY", mass="shell", shell_t=3.5,
                   process="Purchased PC enclosure, machined for glands, pressure-equalising vent",
                   desc="ESP32 controller, LTE modem, MPPT and LiFePO4 battery; shaded by the PV canopy", hollow=True))
    inst.append(Inst(pod, "Pod_Body", explode=(0, 0, 680), step=7))
    lid_sh = [g.rounded_box(P["x1"] - P["x0"] + 4, 2 * P["hw"] + 4, P["lid"], 15, 7, 6, 3, (pcx, 0, pz0 + P["h"] + P["lid"] / 2))]
    for bx in (pcx - 80, pcx + 80):
        lid_sh.append(g.cylinder(7, -17, 17, 16).transformed(T(bx, P["hw"] + 6, pz0 + P["h"] + 2) @ Ry(90)))
    lid = add(Part("podlid", "AS3-512", "Pod lid (hinged)", lid_sh, "PC_DARK", mass="shell", shell_t=3.5,
                   process="Supplied with the enclosure; EPDM gasket"))
    inst.append(Inst(lid, "Pod_Lid", group="podlid", explode=(0, 0, 940), step=7))
    ix0 = P["x0"] + 12
    plate = add(Part("podplate", "AS3-513", "Pod mounting plate",
                     [g.box(ix0, P["x1"] - 12, -P["hw"] + 10, P["hw"] - 10, pz0 + 6, pz0 + 8)], "AL6061", process="2 mm 5052 plate"))
    batt = add(Part("battery", "AS3-514", "LiFePO4 12.8 V 6 Ah with BMS",
                    [g.rounded_box(151, 65, 94, 3, 2, 3, 2, (ix0 + 85.5, -P["hw"] + 50, pz0 + 55))], "BATTERY",
                    mass="kg", kg=0.80, kind="purchased", note="catalogue-class value, confirm"))
    pcb_sh = [g.box(ix0 + 120, ix0 + 280, 5, 105, pz0 + 30, pz0 + 31.6),
              g.box(ix0 + 140, ix0 + 165, 30, 48, pz0 + 31.6, pz0 + 34.6),
              g.box(ix0 + 190, ix0 + 230, 45, 85, pz0 + 31.6, pz0 + 35.6),
              g.box(ix0 + 245, ix0 + 268, 20, 40, pz0 + 31.6, pz0 + 34.0)]
    for sx_ in (ix0 + 125, ix0 + 275):
        for sy_ in (10, 100):
            pcb_sh.append(g.cylinder(3, pz0 + 8, pz0 + 30, 10, sx_, sy_))
    pcb = add(Part("pcb", "AS3-515", "Controller board (ESP32, RS485, RTC, microSD, LTE Cat-1)", pcb_sh, "PCB",
                   mass="kg", kg=0.20, kind="purchased"))
    mppt = add(Part("mppt", "AS3-516", "MPPT charge controller",
                    [g.rounded_box(100, 60, 28, 3, 2, 3, 2, (ix0 + 225, -P["hw"] + 50, pz0 + 22))], "PC_DARK",
                    mass="kg", kg=0.15, kind="purchased"))
    for p_, nm in ((plate, "Pod_Plate"), (batt, "Battery"), (pcb, "Controller_Board"), (mppt, "MPPT")):
        inst.append(Inst(p_, nm, explode=(0, 0, 800), step=7))

    # ---------------- 52x PV canopy (hinges up on the aft stanchions) ----
    V_ = PV
    pvL = V_["x1"] - V_["x0"]
    aft_z = DZ + V_["aft_clear"]
    ref = g.apply(Ry(V_["tilt"]), [(pvL / 2, 0, -V_["t"] / 2)])[0]
    PV_M = T(V_["x1"] - ref[0], 0, aft_z - ref[2]) @ Ry(V_["tilt"])
    frame_sh = [hollow_prism(g.rrect2d(pvL, 2 * V_["hw"], 6, 3), g.rrect2d(pvL - 40, 2 * V_["hw"] - 40, 2, 3), "z",
                             -V_["t"] / 2, V_["t"] / 2),
                g.box(-pvL / 2 + 20, pvL / 2 - 20, -V_["hw"] + 20, V_["hw"] - 20, -V_["t"] / 2 + 4, -V_["t"] / 2 + 7),
                g.box(60, 140, -40, 40, -V_["t"] / 2 - 18, -V_["t"] / 2 + 4)]
    pvframe = add(Part("pvframe", "AS3-521", "PV module 20 W (frame + backsheet)", [s.transformed(PV_M) for s in frame_sh],
                       "AL6061", mass="kg", kg=1.55, kind="purchased", note="20 W 12 V mono module, 450 x 350 assumed"))
    cells = []
    nx, ny = 6, 4
    cw, ch = (pvL - 44) / nx, (2 * V_["hw"] - 44) / ny
    for i in range(nx):
        for j in range(ny):
            x0 = -pvL / 2 + 22 + i * cw + 1.5
            y0 = -V_["hw"] + 22 + j * ch + 1.5
            cells.append(g.box(x0, x0 + cw - 3, y0, y0 + ch - 3, V_["t"] / 2 - 3.2, V_["t"] / 2 - 1.0).transformed(PV_M))
    pvcells = add(Part("pvcells", "AS3-522", "PV module 20 W (cells + glass)", cells, "PV_CELL", mass="kg", kg=0.45,
                       kind="purchased"))
    inst.append(Inst(pvframe, "PV_Module_Frame", group="canopy", explode=(0, 0, 1250), step=8))
    inst.append(Inst(pvcells, "PV_Module_Cells", group="canopy", explode=(0, 0, 1250), step=8))

    p_front = g.apply(PV_M, [(-pvL / 2, 0, -V_["t"] / 2)])[0]
    p_aft = g.apply(PV_M, [(pvL / 2, 0, -V_["t"] / 2)])[0]

    def z_under(x):
        return p_front[2] + (x - p_front[0]) * (p_aft[2] - p_front[2]) / (p_aft[0] - p_front[0])

    st_sh = []
    for sx_ in STANCHION_X:
        zt = z_under(sx_ + 14) - 8
        for s in (1, -1):
            st_sh += [g.rounded_box(40, 40, 6, 6, 1.5, 3, 2, (sx_, s * STANCHION_Y, DZ + 3)),
                      g.tube(10, 8, DZ + 6, zt, 24, sx_, s * STANCHION_Y),
                      g.box(sx_ - 14, sx_ + 14, s * STANCHION_Y - 14, s * STANCHION_Y + 14, zt, zt + 7.5)]
    stanch = add(Part("stanchions", "AS3-523", "Canopy stanchions + hinge / pin blocks", st_sh, "AL6061",
                      process="6061 tube 20 x 2, welded base plates; aft pair hinged, front pair quick-release pins",
                      desc="Canopy hinges up on the aft pair for pod and sampler access"))
    inst.append(Inst(stanch, "Canopy_Stanchions", explode=(0, 0, 1000), step=8))
    canopy_hinge = (STANCHION_X[1], 0.0, z_under(STANCHION_X[1]) - 4)

    # ---------------- 6xx autosampler -------------------------------------
    S = SAMPLER
    scx = (S["x0"] + S["x1"]) / 2
    sz0 = DZ
    s_sh = [g.rounded_box(S["x1"] - S["x0"], 2 * S["hw"], S["h"], 14, 6, 6, 3, (scx, 0, sz0 + S["h"] / 2))]
    s_sh += place([g.box(-30, 30, -20, 20, 0, 10)], T(S["x1"], -60, sz0 + 50) @ g.align_z_to((1, 0, 0)))
    sbody = add(Part("sampler", "AS3-601", "Autosampler cassette (insulated body)", s_sh, "WHITE_PE", mass="shell",
                     shell_t=6.0, kg=0.35, process="Twin-wall rotomoulded PE, PU insulated",
                     desc="4-bottle carousel, peristaltic pump, purge-to-waste valve", hollow=True))
    inst.append(Inst(sbody, "Sampler_Body", explode=(0, 0, 720), step=9))
    top = sz0 + S["h"]
    slid = add(Part("samplerlid", "AS3-602", "Autosampler lid (hinged, tamper-seal hasp)",
                    [g.rounded_box(S["x1"] - S["x0"] + 4, 2 * S["hw"] + 4, S["lid"], 15, 5, 6, 3, (scx, 0, top + S["lid"] / 2)),
                     g.pipe_along([(scx - 40, -S["hw"] + 18, top + S["lid"]), (scx - 40, -S["hw"] + 18, top + S["lid"] + 14),
                                   (scx + 40, -S["hw"] + 18, top + S["lid"] + 14), (scx + 40, -S["hw"] + 18, top + S["lid"])],
                                  5, 12, fillet=8)],
                    "PC_DARK", mass="shell", shell_t=4.0, process="Moulded PC, EPDM gasket"))
    inst.append(Inst(slid, "Sampler_Lid", group="samplerlid", explode=(0, 0, 980), step=9))
    carousel = add(Part("carousel", "AS3-603", "Bottle carousel (lift-out cassette)",
                        [g.cylinder(86, sz0 + 14, sz0 + 20, 48, scx, 0), g.cylinder(10, sz0 + 6, sz0 + 14, 20, scx, 0)],
                        "POM_BLACK", process="Machined acetal; the whole carousel swaps out (chain of custody)"))
    inst.append(Inst(carousel, "Bottle_Carousel", explode=(0, 0, 840), step=9))
    bottle = add(Part("bottle", "AS3-604", "Sample bottle 250 mL HDPE (lab-supplied)",
                      [g.revolve([(0, 0), (29, 0), (31, 3), (31, 112), (26, 124), (15, 132), (15, 140), (0, 140)], 36)],
                      "WHITE_PE", mass="kg", kg=0.29, kind="purchased", note="0.04 kg bottle + 0.25 kg sample (full)"))
    bcap = add(Part("bottlecap", "AS3-605", "Bottle cap (septum)", [g.cylinder(16, 0, 14, 28)], "PROBE_PH", mass="kg",
                    kg=0.005, kind="purchased"))
    for kb, al in enumerate((45, 135, 225, 315)):
        a = math.radians(al)
        bx, by = scx + 52 * math.cos(a), 52 * math.sin(a)
        inst.append(Inst(bottle, f"Bottle_{kb + 1}", T(bx, by, sz0 + 20), explode=(0, 0, 840), step=9))
        inst.append(Inst(bcap, f"Bottle_Cap_{kb + 1}", T(bx, by, sz0 + 160), explode=(0, 0, 860), step=9))
    pump = add(Part("pump", "AS3-606", "Peristaltic pump 12 V (reversible)",
                    [s.transformed(T(scx, 0, sz0 + 212) @ Rx(-90)) for s in (g.cylinder(16, -60, -12, 24), g.cylinder(26, -12, 14, 32))],
                    "PC_DARK", mass="kg", kg=0.35, kind="purchased", desc="Purge 20 s to waste, then fill 30 s"))
    inst.append(Inst(pump, "Peristaltic_Pump", explode=(0, 0, 900), step=9))

    # ---------------- 7xx signalling & comms ------------------------------
    mx, my = MAST_XY
    mast = add(Part("mast", "AS3-701", "Beacon mast",
                    [g.cylinder(30, BEAM_Z1, BEAM_Z1 + 8, 32, mx, my), g.tube(16, 13.5, BEAM_Z1 + 8, MAST_TOP, 32, mx, my)],
                    "AL6061", process="6061 tube 32 x 2.5, welded flange"))
    inst.append(Inst(mast, "Beacon_Mast", explode=(0, 320, 1150), step=10))
    beac_base = add(Part("beacon_base", "AS3-702", "Jal-Deep beacon base", [g.cylinder(40, MAST_TOP, MAST_TOP + 22, 40, mx, my)],
                         "PC_DARK", mass="kg", kg=0.18, kind="purchased"))
    lz = MAST_TOP + 22
    lens = g.revolve([(37, lz), (37, lz + 44), (30, lz + 64), (16, lz + 72), (0, lz + 74)], 40).transformed(T(mx, my, 0))
    beac_lens = add(Part("beacon_lens", "AS3-703", "Jal-Deep 360 deg LED lens (green normal / red alert)", [lens],
                         "BEACON_LENS", mass="kg", kg=0.08, kind="purchased",
                         desc="Status light for people on the bank - works without a phone"))
    inst.append(Inst(beac_base, "Beacon_Base", explode=(0, 320, 1350), step=10))
    inst.append(Inst(beac_lens, "Beacon_Lens", explode=(0, 320, 1450), step=10))
    ax_, ay_ = ANT_XY
    ant_top = DZ + 252
    ant = add(Part("antenna", "AS3-711", "LTE antenna (whip, N-type)",
                   [g.cylinder(15, BEAM_Z1, BEAM_Z1 + 18, 24, ax_, ay_), g.cylinder(9, BEAM_Z1 + 18, ant_top, 20, ax_, ay_),
                    g.revolve([(9, 0), (6, 6), (0, 8)], 20).transformed(T(ax_, ay_, ant_top))],
                   "POM_BLACK", mass="kg", kg=0.12, kind="purchased"))
    inst.append(Inst(ant, "LTE_Antenna", explode=(0, -320, 1150), step=10))
    us = add(Part("ultrasonic", "AS3-712", "Stage sensor (waterproof ultrasonic, looking up)",
                  [g.cylinder(20, CARR_TOP, CARR_TOP + 40, 32, 118, 0), g.cylinder(15, CARR_TOP + 40, CARR_TOP + 46, 28, 118, 0)],
                  "POM_BLACK", mass="kg", kg=0.06, kind="purchased", desc="Distance to the target plate -> river stage"))
    inst.append(Inst(us, "Stage_Sensor", explode=(0, 0, 1300), step=10))

    # ---------------- 8xx handling + harness ------------------------------
    handle_p = add(Part("grabhandle", "AS3-801", "Grab handle (two-person carry)",
                        [g.pipe_along([(-60, 0, 0), (-60, 0, 55), (60, 0, 55), (60, 0, 0)], 11, 18, fillet=22),
                         g.cylinder(17, 0, 4, 24, -60, 0), g.cylinder(17, 0, 4, 24, 60, 0)],
                        "SS_BRUSHED", mass="kg", kg=0.23, process="316 tube 22 x 1.5 bent, welded pads, into hull inserts"))
    yo = PONT_YC + PONT_W / 2 - 24
    for hxp in (240.0, 760.0):
        for s in (1, -1):
            inst.append(Inst(handle_p, f"Grab_Handle_{'Bow' if hxp < 500 else 'Stern'}_{'S' if s > 0 else 'P'}",
                             T(hxp, s * yo, PONT_H), explode=(0, s * 720, 150), step=12))
    eye = add(Part("eyebolt", "AS3-802", "Lifting eye bolt M12 (DIN 580)",
                   [g.cylinder(6, -14, 0.5, 16), g.cylinder(12, 0, 6, 24),
                    g.revolve_closed(g.circle2d(5, 12, cx=18), 32).transformed(T(0, 0, 29) @ Rx(90))],
                   "SS316L", kind="fastener"))
    for bi in (1, 2):
        for s in (1, -1):
            inst.append(Inst(eye, f"Lift_Eye_{bi + 1}{'S' if s > 0 else 'P'}", T(BEAM_X[bi], s * PONT_YC, BEAM_Z1),
                             explode=(0, 0, 1300), step=12))

    zc_ = c1
    harness = []
    for s in (1, -1):
        harness.append(g.pipe_along([(wx + 60, s * 25, zc_ + 14), (wx + 60, s * 25, zc_ + 34), (P["x0"] - 18, s * 40, zc_ + 34),
                                     (P["x0"] - 16, s * 40, pz0 + 30)], 5, 12, fillet=12))
    harness.append(g.pipe_along([(138, 0, CARR_TOP + 22), (152, 0, CARR_TOP + 22), (152, 0, DZ + 67), (165, 118, DZ + 67),
                                 (320, 118, DZ + 37), (P["x0"] - 16, 80, pz0 + 30)], 4, 10, fillet=20))
    harness.append(g.pipe_along([(690, -30, z_under(690) - 12), (700, -128, z_under(700) - 40), (662, -128, DZ + 197),
                                 (662, -128, pz0 + 70), (P["x1"] + 16, -100, pz0 + 55)], 4, 10, fillet=18))
    harness.append(g.pipe_along([(mx - 14, my, BEAM_Z1 + 30), (mx - 20, 140, BEAM_Z1 + 12), (662, 140, DZ + 10),
                                 (P["x1"] + 16, 100, pz0 + 55)], 4, 10, fillet=18))
    harn = add(Part("harness", "AS3-811", "Cable harness (probes, stage sensor, PV, beacon)", harness, "CABLE", mass="kg",
                    kg=0.6, process="Marine cable, IP68 glands, drip loops", kind="harness"))
    inst.append(Inst(harn, "Cable_Harness", explode=(0, 0, 1550), step=12))
    hose = [g.pipe_along([(ix, 0, c1 + 21), (ix, 0, c1 + 44), (wx + 65, -110, c1 + 44), (wx + 65, -110, BEAM_Z0 - 20),
                          (690, -110, BEAM_Z0 - 20), (690, -110, DZ + 12)], 6, 12, fillet=22),
            g.pipe_along([(S["x1"] + 10, -60, sz0 + 50), (DECK_X1 + 10, -60, sz0 + 50), (DECK_X1 + 10, -60, 180)], 6, 12, fillet=10)]
    hoses = add(Part("hoses", "AS3-812", "Sampler hoses (intake + purge-to-waste)", hose, "TUBING", mass="kg", kg=0.15,
                     process="6 mm ID food-grade tubing", kind="harness"))
    inst.append(Inst(hoses, "Sampler_Hoses", explode=(0, 0, 1550), step=12))

    pivots = {"gate": dict(origin=(HINGE_XY[0], HINGE_XY[1], 0.0), axis=(0, 0, 1), open_deg=-100.0),
              "canopy": dict(origin=canopy_hinge, axis=(0, 1, 0), open_deg=50.0),
              "podlid": dict(origin=(pcx, P["hw"] + 6, pz0 + P["h"] + 2), axis=(1, 0, 0), open_deg=-100.0),
              "samplerlid": dict(origin=(scx, S["hw"] + 2, top), axis=(1, 0, 0), open_deg=-95.0),
              "cartridge": dict(origin=(wx, 0.0, 0.0), axis=(0, 0, 1), open_deg=0.0, lift=700.0)}
    return parts, inst, pivots


# ---------------------------------------------------------------------------
# GUIDE (pier side, world frame)
# ---------------------------------------------------------------------------
def guide_levels(draft):
    keel_low = W_LOW - draft
    keel_high = W_HIGH - draft
    low_top = keel_low + TIER_Z[0] - STOP_GAP            # top of lower buffer
    up_bot = keel_high + CARR_TOP + STOP_GAP + 46.0      # bottom of upper buffer (clears the stage sensor)
    zb_low = low_top - BUFFER_H - STOP_H - CLAMP_H / 2
    zb_up = up_bot + BUFFER_H + STOP_H + CLAMP_H / 2
    return dict(keel_low=keel_low, keel_high=keel_high, keel_mid=(keel_low + keel_high) / 2,
                low_top=low_top, up_bot=up_bot, zb_low=zb_low, zb_up=zb_up,
                pole_z0=zb_low - CLAMP_H / 2 - 110, pole_z1=zb_up + CLAMP_H / 2 + 110)


def build_guide(draft):
    L = guide_levels(draft)
    parts, inst = {}, []

    def add(p):
        parts[p.key] = p
        return p

    sx, wy, hz = BRK_PLATE
    xp = -PIER_STANDOFF
    br = [prism(g.rrect2d(wy, hz, 14, 4), "x", xp, xp + sx)]
    arm = [(xp + sx - 1, -80), (-48, -36), (-48, 36), (xp + sx - 1, 80)]
    for s in (1, -1):
        br.append(prism(arm, "y", s * BRK_ARM_Y - BRK_ARM_T / 2, s * BRK_ARM_Y + BRK_ARM_T / 2))
    br.append(g.box(-262, -252, -BRK_ARM_Y + BRK_ARM_T / 2, BRK_ARM_Y - BRK_ARM_T / 2, -46, 46))
    br.append(revolve_partial([(POLE_R + 0.2, -CLAMP_H / 2), (CLAMP_OD / 2, -CLAMP_H / 2), (CLAMP_OD / 2, CLAMP_H / 2),
                               (POLE_R + 0.2, CLAMP_H / 2)], 90.5, 269.5, 28))
    for s in (1, -1):
        br.append(g.box(-14, -0.5, s * 66 - 10, s * 66 + 10, -32, 32))
    bracket = add(Part("bracket", "AS3-101", "Pier bracket (weldment) - upper and lower identical", br, "SS316L",
                       process="Laser-cut 316L 10/12 mm, TIG welded, passivated; 4x M12 chemical anchors",
                       desc="Holds the pole 360 mm off the pier face; the arm passes between the hull bows"))
    capsh = [revolve_partial([(POLE_R + 0.2, -CLAMP_H / 2), (CLAMP_OD / 2, -CLAMP_H / 2), (CLAMP_OD / 2, CLAMP_H / 2),
                              (POLE_R + 0.2, CLAMP_H / 2)], -89.5, 89.5, 28)]
    for s in (1, -1):
        capsh.append(g.box(0.5, 14, s * 66 - 10, s * 66 + 10, -32, 32))
    ccap = add(Part("clampcap", "AS3-102", "Pole clamp cap", capsh, "SS316L", process="Machined 316L"))
    tgt = add(Part("target", "AS3-103", "Stage target plate", [g.box(55, 185, -55, 55, CLAMP_H / 2 - 4, CLAMP_H / 2)],
                   "SS316L", process="4 mm 316L welded to the upper clamp cap", desc="Flat reflector above the stage sensor"))
    m10 = add(Part("m10g", "AS3-905", "Bolt M10 x 40 A4 + washer", g.bolt(10, 40), "SS316L", process="A4-70", kind="fastener"))
    anchor = add(Part("anchor", "AS3-904", "Chemical anchor M12 x 130 A4", g.bolt(12, 130), "SS316L", kind="fastener",
                      process="A4 threaded rod + injection mortar"))
    for tag, zb in (("Lower", L["zb_low"]), ("Upper", L["zb_up"])):
        Mz = T(0, 0, zb)
        inst.append(Inst(bracket, f"Pier_Bracket_{tag}", Mz, group="guide", explode=(900, 0, 0), step=1))
        inst.append(Inst(ccap, f"Clamp_Cap_{tag}", Mz, group="guide", explode=(700, 0, 0), step=2))
        for s in (1, -1):
            inst.append(Inst(m10, f"Clamp_Bolt_{tag}_{'S' if s > 0 else 'P'}", Mz @ T(14, s * 66, 0) @ g.align_z_to((1, 0, 0)),
                             group="guide", explode=(950, 0, 0), step=2))
        for yy in (-80, 80):
            for zz in (-60, 60):
                inst.append(Inst(anchor, f"Anchor_{tag}_{'S' if yy > 0 else 'P'}{'U' if zz > 0 else 'L'}",
                                 Mz @ T(xp + sx, yy, zz) @ g.align_z_to((1, 0, 0)), group="guide",
                                 explode=(1150, 0, 0), step=1))
        if tag == "Upper":
            inst.append(Inst(tgt, "Stage_Target_Plate", Mz, group="guide", explode=(700, 0, 0), step=2))
    pole = add(Part("pole", "AS3-111", "Guide pole 2in Sch 40S SS316L",
                    [g.tube(POLE_R, POLE_R - POLE_WALL, L["pole_z0"], L["pole_z1"], 48)], "SS316L",
                    process="ASTM A312 TP316L pipe, cut to length, ends deburred",
                    desc=f"{L['pole_z1'] - L['pole_z0']:.0f} mm long; brackets {L['zb_up'] - L['zb_low']:.0f} mm apart"))
    inst.append(Inst(pole, "Guide_Pole", group="guide", explode=(0, 0, 3600), step=2))
    pcap = add(Part("polecap", "AS3-112", "Pole top cap",
                    [g.revolve([(0, 0), (POLE_R + 2, 0), (POLE_R + 2, 18), (24, 30), (0, 34)], 40)], "POM_BLACK",
                    kind="purchased"))
    inst.append(Inst(pcap, "Pole_Cap", T(0, 0, L["pole_z1"]), group="guide", explode=(0, 0, 3700), step=2))
    stop = add(Part("stop", "AS3-113", "Stop collar (split, clamp-on)",
                    [g.tube(STOP_OD / 2, POLE_R + 0.2, 0, STOP_H, 48), g.box(46, 62, -10, 10, 3, STOP_H - 3)], "SS316L",
                    process="Machined 316L, M8 clamp screw"))
    buf = add(Part("buffer", "AS3-114", "Stop buffer ring (EPDM)", [g.tube(STOP_OD / 2 - 2, POLE_R + 2, 0, BUFFER_H, 48)],
                   "RUBBER", process="Moulded EPDM 70 ShA"))
    zl, zu = L["low_top"], L["up_bot"]
    inst.append(Inst(stop, "Stop_Collar_Lower", T(0, 0, zl - BUFFER_H - STOP_H), group="guide", explode=(0, 0, 3300), step=2))
    inst.append(Inst(buf, "Buffer_Lower", T(0, 0, zl - BUFFER_H), group="guide", explode=(0, 0, 3350), step=2))
    inst.append(Inst(buf, "Buffer_Upper", T(0, 0, zu), group="guide", explode=(0, 0, 1000), step=2))
    inst.append(Inst(stop, "Stop_Collar_Upper", T(0, 0, zu + BUFFER_H), group="guide", explode=(0, 0, 1050), step=2))
    return parts, inst, L


# ---------------------------------------------------------------------------
# ENVIRONMENT (renders only)
# ---------------------------------------------------------------------------
def build_environment(L):
    top = L["zb_up"] + 900
    pier = Part("pier", "ENV-1", "Bridge pier (context)",
                [prism(g.rrect2d(1500, 1100, 300, 10, -PIER_STANDOFF - 750, 0), "z", RIVERBED_Z - 50, top)],
                "CONCRETE", kind="env")
    return {"pier": pier}, [Inst(pier, "Bridge_Pier", group="env", step=0)]
