"""
AquaSentinel R3: 1:5 printable scale model for a Bambu Lab H2D (fits any FDM printer with a 300 x 320 x 300 mm volume).

Builds watertight solids with OpenCascade (OCP) from the R3 design parameters in ../src/params.py, scaled 1:5, and
writes binary STL files in millimetres:

  AquaSentinel_R3_1to5_FLOAT.stl          every float part on one plate, each already in its print orientation
  AquaSentinel_R3_1to5_STAND.stl          the display stand (base, pier column, brackets, stops, pole cap), second plate
  AquaSentinel_R3_1to5_ASSEMBLED_view.stl the model as assembled on its stand, for viewing only (do not print)
  parts/<id>_<name>.stl                   each printed part on its own, in print orientation
  parts/OPT_rod_half_print_2.stl          optional printed pole (print two, glue together) if no 12 mm rod is at hand
  build_report.json                       sizes, volumes, mesh checks, fits, clearances, mass and draft estimate

Usage:  python -I make_scale_model.py [out_dir]        (default: the folder this script is in)

The model follows the R3 CAD at 1:5 except where printing needs it; README.md lists every change.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "src")))
import geom as G      # noqa: E402  (R3 transform helpers: same matrices as the CAD)
import params as R    # noqa: E402  (R3 design parameters, full scale)

from OCP.BRep import BRep_Tool                                                   # noqa: E402
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse  # noqa: E402
from OCP.BRepBndLib import BRepBndLib                                            # noqa: E402
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_Transform  # noqa: E402
from OCP.BRepCheck import BRepCheck_Analyzer                                     # noqa: E402
from OCP.BRepExtrema import BRepExtrema_DistShapeShape                           # noqa: E402
from OCP.BRepGProp import BRepGProp                                              # noqa: E402
from OCP.BRepMesh import BRepMesh_IncrementalMesh                                # noqa: E402
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections                         # noqa: E402
from OCP.BRepPrimAPI import (BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCone, BRepPrimAPI_MakeCylinder,  # noqa: E402
                             BRepPrimAPI_MakePrism, BRepPrimAPI_MakeRevol, BRepPrimAPI_MakeSphere,
                             BRepPrimAPI_MakeTorus)
from OCP.Bnd import Bnd_Box                                                      # noqa: E402
from OCP.GProp import GProp_GProps                                               # noqa: E402
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain                        # noqa: E402
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED, TopAbs_SOLID                # noqa: E402
from OCP.TopExp import TopExp_Explorer                                           # noqa: E402
from OCP.TopLoc import TopLoc_Location                                           # noqa: E402
from OCP.TopTools import TopTools_ListOfShape                                    # noqa: E402
from OCP.TopoDS import TopoDS                                                    # noqa: E402
from OCP.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec               # noqa: E402

S = 0.2                       # model scale 1:5


def m(v):
    """full-scale mm -> model mm"""
    return v * S


# ---------------------------------------------------------------- printer and fit allowances (model mm)
BED = (300.0, 320.0, 300.0)   # H2D: 300 x 320 with both nozzles (325 x 320 with one), 325 high; every part stays inside
ROD_D = 12.0                  # the pole: a 12 mm rod (aluminium, steel or hardwood dowel) = 1:5 of the 60.3 mm pole
RUN_CLEAR = 0.4               # radial running clearance, rod to roller throat (the CAD has 1.5 mm = 0.3 at 1:5)
FIT_BORE = 12.3               # rod in clamp rings / pole cap (snug; a drop of glue makes it permanent)
FIT_STOP = 12.25              # stop collars grip the rod by friction
PIN_HOLE = 2.0                # holes for 1.75 mm filament pins (lens, grab handles)
MIN_WALL = 1.2                # thinnest printed wall / plate

DZ = m(R.DECK_Z1)             # deck top, 60.6
BEAM_BOT = m(R.BEAM_Z0) - 0.8  # beams sit 0.8 mm deep in pockets in the hull tops
DECK_BOT = DZ - 1.6           # deck plate thickened from 0.6 to 1.6 mm (top stays at the CAD height)
WX = m(R.WELL_X)              # sensor well axis x = 48


# =============================================================================================== OCC helpers
def P(x, y, z):
    return gp_Pnt(float(x), float(y), float(z))


def box(x0, x1, y0, y1, z0, z1):
    return BRepPrimAPI_MakeBox(P(min(x0, x1), min(y0, y1), min(z0, z1)), P(max(x0, x1), max(y0, y1), max(z0, z1))).Shape()


def cyl(r, z0, z1, cx=0.0, cy=0.0):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(P(cx, cy, z0), gp_Dir(0, 0, 1)), float(r), float(z1 - z0)).Shape()


def cyl_axis(r, p0, p1):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    L = float(np.linalg.norm(d))
    return BRepPrimAPI_MakeCylinder(gp_Ax2(P(*p0), gp_Dir(*(d / L))), float(r), L).Shape()


def cone(r0, r1, z0, z1, cx=0.0, cy=0.0):
    return BRepPrimAPI_MakeCone(gp_Ax2(P(cx, cy, z0), gp_Dir(0, 0, 1)), float(r0), float(r1), float(z1 - z0)).Shape()


def sphere(c, r):
    return BRepPrimAPI_MakeSphere(P(*c), float(r)).Shape()


def torus_quarter(center, normal, xdir, R_, r_):
    """quarter torus: sweep starts on +xdir and turns 90 deg toward normal x xdir"""
    ax = gp_Ax2(P(*center), gp_Dir(*normal), gp_Dir(*xdir))
    return BRepPrimAPI_MakeTorus(ax, float(R_), float(r_), math.pi / 2).Shape()


def pipe_fillet(points, r, fillet):
    """solid tube of radius r swept along a polyline whose interior corners are rounded with radius `fillet`"""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
    from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipe
    from OCP.GC import GC_MakeArcOfCircle, GC_MakeSegment
    from OCP.gp import gp_Circ
    pts = [np.asarray(p, float) for p in points]
    segs = []                                               # list of ('L', a, b) / ('A', a, m, b)
    cur = pts[0]
    for i in range(1, len(pts) - 1):
        d1 = (pts[i] - pts[i - 1]) / np.linalg.norm(pts[i] - pts[i - 1])
        d2 = (pts[i + 1] - pts[i]) / np.linalg.norm(pts[i + 1] - pts[i])
        half = math.acos(max(-1.0, min(1.0, float(-d1 @ d2)))) / 2
        t = fillet / math.tan(half)
        a, b = pts[i] - d1 * t, pts[i] + d2 * t
        n = d2 - d1 * float(d1 @ d2)
        n /= np.linalg.norm(n)
        c = a + n * fillet
        mid = c + ((a - c) + (b - c)) / np.linalg.norm((a - c) + (b - c)) * fillet
        segs.append(("L", cur, a))
        segs.append(("A", a, mid, b))
        cur = b
    segs.append(("L", cur, pts[-1]))
    mw = BRepBuilderAPI_MakeWire()
    for sg in segs:
        if sg[0] == "L":
            if np.linalg.norm(sg[2] - sg[1]) < 1e-6:
                continue
            e = BRepBuilderAPI_MakeEdge(GC_MakeSegment(P(*sg[1]), P(*sg[2])).Value()).Edge()
        else:
            e = BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(P(*sg[1]), P(*sg[2]), P(*sg[3])).Value()).Edge()
        mw.Add(e)
    path = mw.Wire()
    d0 = (pts[1] - pts[0]) / np.linalg.norm(pts[1] - pts[0])
    circ = gp_Circ(gp_Ax2(P(*pts[0]), gp_Dir(*d0)), float(r))
    prof = BRepBuilderAPI_MakeFace(BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(circ).Edge()).Wire(), True).Face()
    mp = BRepOffsetAPI_MakePipe(path, prof)
    mp.Build()
    return mp.Shape()


def _dedupe(pts):
    out = []
    for p in pts:
        if not out or np.linalg.norm(np.subtract(p, out[-1])) > 1e-6:
            out.append(tuple(float(c) for c in p))
    if len(out) > 1 and np.linalg.norm(np.subtract(out[0], out[-1])) < 1e-6:
        out.pop()
    return out


def wire(pts3):
    mp = BRepBuilderAPI_MakePolygon()
    for p in _dedupe(pts3):
        mp.Add(P(*p))
    mp.Close()
    return mp.Wire()


def face(pts3):
    return BRepBuilderAPI_MakeFace(wire(pts3), True).Face()


def prism_xy(pts, z0, z1):
    """polygon in (x, y), extruded along +z"""
    return BRepPrimAPI_MakePrism(face([(x, y, z0) for x, y in pts]), gp_Vec(0, 0, float(z1 - z0))).Shape()


def prism_xz(pts, y0, y1):
    """polygon in (x, z), extruded along +y"""
    return BRepPrimAPI_MakePrism(face([(x, y0, z) for x, z in pts]), gp_Vec(0, float(y1 - y0), 0)).Shape()


def prism_yz(pts, x0, x1):
    """polygon in (y, z), extruded along +x"""
    return BRepPrimAPI_MakePrism(face([(x0, y, z) for y, z in pts]), gp_Vec(float(x1 - x0), 0, 0)).Shape()


def revolve(profile_rz, cx=0.0, cy=0.0, z0=0.0):
    """closed (r, z) profile revolved about the vertical axis through (cx, cy)"""
    f = face([(cx + r, cy, z0 + z) for r, z in profile_rz])
    return BRepPrimAPI_MakeRevol(f, gp_Ax1(P(cx, cy, 0), gp_Dir(0, 0, 1)), 2 * math.pi).Shape()


def loft(sections):
    ts = BRepOffsetAPI_ThruSections(True, True, 1e-6)
    for pts in sections:
        ts.AddWire(wire(pts))
    ts.CheckCompatibility(False)
    ts.Build()
    if not ts.IsDone():
        raise RuntimeError("loft failed")
    return ts.Shape()


def _list(shapes):
    lst = TopTools_ListOfShape()
    for s in shapes:
        lst.Append(s)
    return lst


def clean(s):
    u = ShapeUpgrade_UnifySameDomain(s, True, True, False)
    u.Build()
    return u.Shape()


def fuse(*shapes):
    shapes = [s for s in shapes if s is not None]
    if len(shapes) == 1:
        return shapes[0]
    op = BRepAlgoAPI_Fuse()
    op.SetArguments(_list(shapes[:1]))
    op.SetTools(_list(shapes[1:]))
    op.SetFuzzyValue(1e-5)
    op.SetRunParallel(True)
    op.Build()
    if not op.IsDone():
        raise RuntimeError("fuse failed")
    return clean(op.Shape())


def cut(base, *tools):
    tools = [t for t in tools if t is not None]
    if not tools:
        return base
    op = BRepAlgoAPI_Cut()
    op.SetArguments(_list([base]))
    op.SetTools(_list(tools))
    op.SetFuzzyValue(1e-5)
    op.SetRunParallel(True)
    op.Build()
    if not op.IsDone():
        raise RuntimeError("cut failed")
    return clean(op.Shape())


def common(a, b):
    op = BRepAlgoAPI_Common(a, b)
    op.Build()
    return op.Shape()


def trsf_from(M):
    t = gp_Trsf()
    t.SetValues(*[float(M[i, j]) for i in range(3) for j in range(4)])
    return t


def xform(s, M):
    return BRepBuilderAPI_Transform(s, trsf_from(np.asarray(M, float)), True).Shape()


def moved(s, dx=0.0, dy=0.0, dz=0.0):
    return xform(s, G.T(dx, dy, dz))


def mirror_y(s):
    t = gp_Trsf()
    t.SetMirror(gp_Ax2(P(0, 0, 0), gp_Dir(0, 1, 0)))
    return BRepBuilderAPI_Transform(s, t, True).Shape()


def n_solids(s):
    e, n = TopExp_Explorer(s, TopAbs_SOLID), 0
    while e.More():
        n += 1
        e.Next()
    return n


def volume(s):
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(s, g)
    return g.Mass()


def centroid(s):
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(s, g)
    c = g.CentreOfMass()
    return np.array([c.X(), c.Y(), c.Z()])


def area(s):
    g = GProp_GProps()
    BRepGProp.SurfaceProperties_s(s, g)
    return g.Mass()


def bbox(s):
    b = Bnd_Box()
    BRepBndLib.Add_s(s, b, False)
    return np.array(b.Get())


def distance(a, b):
    d = BRepExtrema_DistShapeShape(a, b)
    d.Perform()
    return d.Value()


def overlap_volume(a, b):
    try:
        return volume(common(a, b))
    except Exception:
        return float("nan")


# =============================================================================================== 2-D profiles
def rrect(cx, cy, w, h, r, n=8):
    """rounded rectangle polygon centred on (cx, cy)"""
    r = min(r, w / 2 - 1e-3, h / 2 - 1e-3)
    if r < 1e-3:
        return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]
    pts = []
    for qx, qy, a0 in ((cx + w / 2 - r, cy - h / 2 + r, -90), (cx + w / 2 - r, cy + h / 2 - r, 0),
                       (cx - w / 2 + r, cy + h / 2 - r, 90), (cx - w / 2 + r, cy - h / 2 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((qx + r * math.cos(a), qy + r * math.sin(a)))
    return pts


def rblock(cx, cy, w, h, z0, z1, r_side, r_top=0.0, r_bot=0.0, n=6):
    """box with rounded vertical edges and optionally rounded top / bottom edges (loft of offset sections)"""
    def sec(inset, z):
        return [(x, y, z) for x, y in rrect(cx, cy, w - 2 * inset, h - 2 * inset, r_side - inset, n)]
    secs = []
    if r_bot > 0:
        for k in range(4):
            a = math.radians(30.0 * k)
            secs.append(sec(r_bot * (1 - math.sin(a)), z0 + r_bot * (1 - math.cos(a))))
    else:
        secs.append(sec(0.0, z0))
    if r_top > 0:
        for k in range(4):
            a = math.radians(30.0 * k)
            secs.append(sec(r_top * (1 - math.cos(a)), z1 - r_top + r_top * math.sin(a)))
    else:
        secs.append(sec(0.0, z1))
    return loft(secs)


def sector(cx, cy, r, a0, a1, n=8):
    pts = [(cx, cy)]
    for a in np.radians(np.linspace(a0, a1, n)):
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def hull_section(y0, y1, z0, z1, rb, rt, n=7):
    """CAD hull cross-section (rounded rectangle, bilge radius rb, deck-edge radius rt), full-scale (y, z)"""
    pts = []
    for cy, cz, r, a0 in ((y1 - rb, z0 + rb, rb, -90), (y1 - rt, z1 - rt, rt, 0),
                          (y0 + rt, z1 - rt, rt, 90), (y0 + rb, z0 + rb, rb, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cy + r * math.cos(a), cz + r * math.sin(a)))
    return pts


# =============================================================================================== FLOAT PARTS
# Float frame, model mm: origin on the pole axis at keel level, +x aft (downstream), +y starboard, +z up.

def hull_starboard():
    """F01: pontoon hull, exactly the CAD loft (stations, rocker, plan radii, section radii) at 1:5"""
    L, W, H = R.PONT_L, R.PONT_W, R.PONT_H
    Rb, Rs = R.BOW_PLAN_R, R.STERN_PLAN_R
    xs = [Rb * (1 - math.cos(t)) for t in np.linspace(0, math.pi / 2, 10)]
    xs += list(np.linspace(Rb, R.BOW_ROCKER_L, 7)[1:])
    xs += list(np.linspace(R.BOW_ROCKER_L, L - R.STERN_ROCKER_L, 4)[1:])
    xs += list(np.linspace(L - R.STERN_ROCKER_L, L - Rs, 5)[1:])
    xs += [L - Rs * (1 - math.cos(t)) for t in np.linspace(math.pi / 2, 0, 9)[1:]]
    xs = sorted(set(round(x, 4) for x in xs))

    def hw(x):
        if x < Rb:
            return (W / 2 - Rb) + math.sqrt(max(Rb ** 2 - (Rb - x) ** 2, 0))
        if x > L - Rs:
            return (W / 2 - Rs) + math.sqrt(max(Rs ** 2 - (x - (L - Rs)) ** 2, 0))
        return W / 2

    def zb(x):
        if x < R.BOW_ROCKER_L:
            return R.BOW_ROCKER_H * (1 - x / R.BOW_ROCKER_L) ** 2
        if x > L - R.STERN_ROCKER_L:
            return R.STERN_ROCKER_H * (1 - (L - x) / R.STERN_ROCKER_L) ** 2
        return 0.0

    secs = []
    for x in xs:
        h, z0 = hw(x), zb(x)
        rb = min(R.HULL_RB, h - 0.6, (H - z0) / 2 - 0.6)
        rt = min(R.HULL_RT, h - 0.6)
        secs.append([(m(x + R.PONT_X0), m(y + R.PONT_YC), m(z)) for y, z in hull_section(-h, h, z0, H, rb, rt)])
    hull = loft(secs)

    yc, x0 = m(R.PONT_YC), m(R.PONT_X0)                       # 54, -20
    adds = []
    for s in (1, -1):                                          # integral rub rails, r 1.8 at z 38
        y = yc + s * m(W / 2 - 3)
        a, b = (x0 + m(105), y, m(R.RUBRAIL_Z)), (x0 + m(L - 75), y, m(R.RUBRAIL_Z))
        adds += [cyl_axis(m(R.RUBRAIL_R), a, b), sphere(a, m(R.RUBRAIL_R)), sphere(b, m(R.RUBRAIL_R))]
    tip_z = m((R.BOW_ROCKER_H + H) / 2)                        # bow bumper pad, top chamfered 45 deg for printing
    adds.append(prism_xz([(x0 + 0.6, tip_z - 9.0), (x0 - 3.2, tip_z - 9.0), (x0 - 3.2, tip_z + 9.0),
                          (x0 + 0.6, tip_z + 12.8)], yc - 4.4, yc + 4.4))
    hull = fuse(hull, *adds)

    cuts = []
    for bx in R.BEAM_X:                                        # beam pockets, 0.8 deep, closed at the outboard end
        cuts.append(box(m(bx) - 4.15, m(bx) + 4.15, yc - m(W / 2) - 5, m(R.BEAM_HALF) + 0.3, BEAM_BOT, m(H) + 1))
    for hx in (240.0, 760.0):                                  # grab-handle pin holes (outboard side)
        for dx in (-12.0, 12.0):
            cuts.append(cyl(PIN_HOLE / 2, m(H) - 2.5, m(H) + 1, m(hx) + dx, m(R.PONT_YC + W / 2 - 24)))
    return cut(hull, *cuts)


def z_under_fn():
    """PV canopy: the CAD transform PV_M and the underside plane z(x), both at 1:5"""
    V_ = R.PV
    pvL = V_["x1"] - V_["x0"]
    aft_z = R.DECK_Z1 + V_["aft_clear"]
    ref = G.apply(G.Ry(V_["tilt"]), [(pvL / 2, 0, -V_["t"] / 2)])[0]
    PV_M = G.T(V_["x1"] - ref[0], 0, aft_z - ref[2]) @ G.Ry(V_["tilt"])
    p_front = G.apply(PV_M, [(-pvL / 2, 0, -V_["t"] / 2)])[0] * S
    p_aft = G.apply(PV_M, [(pvL / 2, 0, -V_["t"] / 2)])[0] * S
    Mm = PV_M.copy()
    Mm[:3, 3] *= S

    def z_under(x):
        return p_front[2] + (x - p_front[0]) * (p_aft[2] - p_front[2]) / (p_aft[0] - p_front[0])
    return z_under, Mm, p_front, p_aft


Z_UNDER, PV_MM, PV_FRONT, PV_AFT = z_under_fn()
STAN_X = tuple(m(x) for x in R.STANCHION_X)    # 84, 158
STAN_Y = 32.6                                   # CAD 33.0; moved in 0.4 so the canopy pin hole keeps a 1.1 mm wall
STRUT_FOOT = [(m(R.BEAM_X[1]), s * m(155), DZ + 1.0) for s in (1, -1)]
STRUT_TIP = [(26.4, s * 17.2, 113.6) for s in (1, -1)]    # 0.2 mm aft of the carriage strut lugs (glue joint)
STRUT_R = 2.2                      # CAD tube 20 mm = 4.0 at 1:5; 4.4 mm so the free-standing struts print stiffly
MAST_XY = (m(R.MAST_XY[0]), m(R.MAST_XY[1]))
ANT_XY = (m(R.ANT_XY[0]), m(R.ANT_XY[1]))
POD_PINS = [(75.0, 20.0), (123.0, -14.0)]          # asymmetric: the pod only fits glands-forward
SAMPLER_PINS = [(140.0, 15.0), (163.0, -9.0)]   # asymmetric: the sampler only fits one way round


def frame():
    """F03: crossbeams + deck + struts + canopy stanchions + LTE antenna, one print (beams on the bed)"""
    sh = []
    zc = (BEAM_BOT + m(R.BEAM_Z1)) / 2
    for bx in R.BEAM_X:                                       # SHS 40x40 -> 8 x 8 (+0.8 in the hull pockets)
        sh.append(prism_xz(rrect(m(bx), zc, m(R.BEAM_A), m(R.BEAM_Z1) - BEAM_BOT, 0.8), -m(R.BEAM_HALF), m(R.BEAM_HALF)))
    sh.append(prism_xy(rrect(m((R.DECK_X0 + R.DECK_X1) / 2), 0, m(R.DECK_X1 - R.DECK_X0), m(2 * R.DECK_HW), m(14)),
                       DECK_BOT, DZ))
    for x, y in POD_PINS + SAMPLER_PINS:                      # locating pins for the pod and the sampler
        sh.append(cyl(0.95, DZ - 0.2, DZ + 1.2, x, y))
    for sx in STAN_X:                                         # stanchions with 8 deg seats and lift-off pins
        for s in (1, -1):
            y = s * STAN_Y
            zt0, zt1 = Z_UNDER(sx - 2.8), Z_UNDER(sx + 2.8)
            zb_ = zt1 - 1.5
            sh += [prism_xy(rrect(sx, y, 8, 8, 1.2), DZ - 0.2, DZ + 1.2),
                   cyl(2.0, DZ + 1.0, zb_ + 0.2, sx, y),
                   prism_xz([(sx - 2.8, zb_), (sx + 2.8, zb_), (sx + 2.8, zt1), (sx - 2.8, zt0)], y - 2.8, y + 2.8),
                   cyl(1.0, Z_UNDER(sx) - 0.6, Z_UNDER(sx) + 2.5, sx, y)]
    for b, a in zip(STRUT_FOOT, STRUT_TIP):                   # carriage brace struts, 45 deg (prints without support)
        sh += [cyl_axis(STRUT_R, b, a), sphere(a, STRUT_R), sphere(b, STRUT_R),
               cyl(3.4, DZ - 0.2, DZ + 1.2, b[0], b[1]), cyl(2.2, DZ + 1.0, DZ + 3.2, b[0], b[1])]
    ax, ay = ANT_XY                                           # LTE whip on crossbeam 4
    sh += [cyl(3.0, m(R.BEAM_Z1) - 0.2, m(R.BEAM_Z1) + 3.6, ax, ay), cyl(1.8, m(R.BEAM_Z1) + 3.4, m(R.DECK_Z1 + 252), ax, ay),
           cone(1.8, 0.0, m(R.DECK_Z1 + 252), m(R.DECK_Z1 + 252) + 1.6, ax, ay)]
    body = fuse(*sh)
    return cut(body, cyl(m(R.WELL_OD / 2) + 0.5, DECK_BOT - 1, DZ + 1, WX, 0),   # sensor-well hatch, 0.5 radial clearance
               cyl(1.65, m(R.BEAM_Z1) - 5.5, m(R.BEAM_Z1) + 0.5, *MAST_XY))       # beacon-mast socket in crossbeam 4


CARR_Z0 = 35.2                     # lower tier bottom (tier plates thickened 1.2 -> 2.0 mm, tops at the CAD height)
CARR_TOP = m(R.CARR_TOP)           # 118.4
TIER_TOPS = [m(z + R.TIER_T) for z in R.TIER_Z]    # 37.2, 107.2


def carriage():
    """F04: bow guide carriage (fixed half + gate fused), 8 concave rollers in 2 tiers, stage sensor, strut lugs"""
    H0, H1 = CARR_Z0, CARR_TOP
    sh = []
    for tt in TIER_TOPS:                                      # tier plates 38 x 38 with the pole hole (r 8)
        sh.append(cut(box(-19, 19, -19, 19, tt - 2.0, tt), cyl(m(40.0), tt - 3, tt + 1)))
    wz0, wz1 = m(R.TIER_Z[0] + R.TIER_T + 42), m(R.TIER_Z[1] - 38)          # 45.6 .. 98.4
    wzc, wh = (wz0 + wz1) / 2, wz1 - wz0
    sh.append(cut(box(18.6, 20.0, -20.2, 20.2, H0, H1), prism_yz(rrect(0, 88.0, 24.8, 30.0, 3.2), 18, 21)))      # back
    sh.append(cut(box(-20.2, -18.8, -20.2, 20.2, H0, H1), prism_yz(rrect(0, wzc, 24.8, wh, 3.2), -21, -18)))     # gate
    sh.append(cut(box(-20.2, 20.0, 19.0, 20.2, H0, H1), prism_xz(rrect(0, wzc, 28.0, wh, 3.2), 18.5, 21)))      # stbd
    sh.append(cut(box(-20.2, 20.0, -20.2, -19.0, H0, H1), prism_xz(rrect(9.6, wzc, 11.2, wh, 2.8), -21, -18.5),
                  prism_xz(rrect(-9.6, wzc, 11.2, wh, 2.8), -21, -18.5)))                                          # port
    rc, rp, hw_ = m(R.ROLLER_RC), ROD_D / 2 + RUN_CLEAR, m(R.ROLLER_W) / 2
    prof = [(0.0, -hw_)] + [(rc - math.sqrt(rp ** 2 - u ** 2), u) for u in np.linspace(-hw_, hw_, 13)] + [(0.0, hw_)]
    for tt in TIER_TOPS:
        zc = tt + 5.0
        f = face([(rc - r, u, zc) for r, u in prof])       # profile in the plane z = zc, roller axis along y
        roller0 = BRepPrimAPI_MakeRevol(f, gp_Ax1(P(rc, 0, zc), gp_Dir(0, 1, 0)), 2 * math.pi).Shape()
        cheeks0 = [box(rc - 3.6, rc + 5.6, y0, y1, tt - 0.2, tt + 11.2) for y0, y1 in ((4.0, 5.2), (-5.2, -4.0))]
        for al in (45, -45, 135, 225):
            Rz = G.Rz(al)
            sh += [xform(roller0, Rz)] + [xform(c, Rz) for c in cheeks0]
    hx, hy = m(R.HINGE_XY[0]), m(R.HINGE_XY[1])              # gate hinge barrel (starboard-front corner)
    sh += [cyl(2.0, H0, 110.0, hx, hy), box(hx, -19.8, 19.8, hy, H0, 110.0)]
    for zl in (m(R.TIER_Z[0] + 110), m(R.TIER_Z[1] - 80)):   # tool-free latch lugs + T-pins (port side)
        sh += [prism_yz([(-20.0, zl - 3.4), (-23.6, zl), (-23.6, zl + 5.0), (-20.0, zl + 5.0)], -3.2, 3.2),
               cyl(1.0, zl - 1.4, zl + 7.5, 0.0, -21.9)]
    sx_ = m(118.0)                                            # stage-sensor shelf, gusset and ultrasonic sensor
    sh += [box(20.0, 28.0, -5.2, 5.2, H1 - 1.2, H1), prism_xz([(19.9, H1 - 9.2), (19.9, H1 - 1.1), (28.0, H1 - 1.1)], -1.2, 1.2),
           cyl(4.0, H1 - 0.1, H1 + 8.0, sx_, 0), cyl(3.0, H1 + 7.9, H1 + 9.2, sx_, 0)]
    for s in (1, -1):                                         # strut lugs (struts on the frame end 0.2 mm aft)
        y0, y1 = s * 17.2 - 1.6, s * 17.2 + 1.6
        sh += [box(19.9, 24.0, y0, y1, 110.4, 116.8), prism_xz([(19.9, 106.4), (19.9, 110.5), (24.0, 110.5)], y0, y1)]
    sh.append(box(19.9, 22.4, -10.0, 10.0, DZ, DZ + 1.4))    # hook: hangs the carriage on the deck edge while gluing
    return fuse(*sh)


def well_and_cage():
    """F05: sensor well sleeve + hatch flange + guard cage (one print, flange on the bed)"""
    ro, ri = m(R.WELL_OD / 2), m(R.WELL_OD / 2) - 1.6        # wall 1.24 -> 1.6 mm
    zb_cage = m(R.CAGE_BOT) - 0.8                            # -76.8
    ri_c = 14.2                                              # cage bore: 1.0 mm radial clearance to the probe spiders
    body = fuse(tube_(ro, ri, m(R.WELL_BOT), m(R.WELL_TOP), WX, 0),
                tube_(m(R.FLANGE_OD / 2), ri + 0.5, DZ, DZ + m(R.FLANGE_T), WX, 0),
                tube_(ro, ri_c, zb_cage, m(R.WELL_BOT) + 0.3, WX, 0),
                box(WX - ri_c - 0.2, WX + ri_c + 0.2, -0.8, 0.8, zb_cage, zb_cage + 1.6),
                box(WX - 0.8, WX + 0.8, -ri_c - 0.2, ri_c + 0.2, zb_cage, zb_cage + 1.6))
    windows = []
    for za, zb_ in ((-75.2, -55.8), (-54.2, -34.8), (-33.2, -14.4)):   # rings at the CAD heights
        for k in range(8):
            a = 45.0 * k
            windows.append(prism_xy(sector(WX, 0, ro + 2, a - 18.2, a + 18.2), za, zb_))
    return cut(body, *windows)


def tube_(ro, ri, z0, z1, cx=0.0, cy=0.0):
    return cut(cyl(ro, z0, z1, cx, cy), cyl(ri, z0 - 1, z1 + 1, cx, cy))


def deflector():
    """F06: V debris deflector under crossbeam 1, with glue tabs that reach the well (0.25 mm gap)"""
    t = 1.6 * math.sqrt(2)
    ax, tx, ty = m(110), m(172), m(62)                       # apex 22, tips at x 34.4, y +-12.4
    rg = m(R.WELL_OD / 2) + 0.25

    def xend(y):
        return WX - math.sqrt(rg ** 2 - y ** 2)
    pts = [(ax, 0), (tx, -ty), (xend(ty), -ty), (xend(ty - t), -(ty - t)), (tx, -(ty - t)), (ax + t, 0),
           (tx, ty - t), (xend(ty - t), ty - t), (xend(ty), ty), (tx, ty)]
    return prism_xy(pts, m(-330), BEAM_BOT)


def cartridge_cap():
    """F07: pull-up cartridge cap + wiper-drive housing + glands + quarter-turn knobs + lift handle"""
    c0 = m(R.CART_Z0)                                        # 61.8 (sits on the hatch flange)
    c1 = c0 + m(R.CAP_T)
    sh = [cyl(m(R.CAP_D / 2), c0, c1, WX, 0), cyl(5.6, c1 - 0.1, c1 + 9.2, WX, 0),
          revolve([(0, 0), (5.6, 0), (4.8, 1.6), (0, 2.2)], WX, 0, c1 + 9.2)]
    for gx, gy in ((12, 5), (12, -5), (-12, 5), (-12, -5)):
        sh += [prism_xy([(WX + gx + 2.31 * math.cos(math.radians(60 * k + 30)), gy + 2.31 * math.sin(math.radians(60 * k + 30)))
                         for k in range(6)], c1 - 0.1, c1 + 1.8), cyl(1.6, c1 + 1.7, c1 + 3.0, WX + gx, gy)]
    for s in (1, -1):
        sh.append(cyl(1.8, c1 - 0.1, c1 + 2.8, WX, s * 15))
    top, rr, bend = c1 + 18.2, 1.6, 4.8                     # lift handle: tube r 1.6, legs at y +-9
    sh.append(pipe_fillet([(WX, -9, c1 - 0.1), (WX, -9, top), (WX, 9, top), (WX, 9, c1 - 0.1)], rr, bend))
    cap = fuse(*sh)
    return cut(cap, cyl(1.65, c0 - 1, c0 + 4.0, WX, 0))    # socket for the probe-cluster spine pin


PROBE_ANG = (45, 135, 225, 315)    # pH, EC, DO, turbidity (CAD order)
TIP_Z = m(R.PROBE_TIP_Z)           # -68


def probe_cluster():
    """F08: spine + 4 probes + 2 spider holders + wiper arm (prints standing on the probe tips)"""
    pr = m(R.PROBE_R)                                        # probes on a 9 mm radius
    full = [(0, 0), (12.5, 0), (14, 2), (14, 16), (16, 19), (16, 232), (17, 234), (17, 270), (11, 273), (11, 300), (0, 300)]
    prof = [(m(r), m(z)) for r, z in full]
    sh = [cyl(3.0, TIP_Z, m(R.CART_Z0), WX, 0), cyl(1.5, m(R.CART_Z0) - 0.1, m(R.CART_Z0) + 3.6, WX, 0)]
    for al in PROBE_ANG:
        a = math.radians(al)
        px, py = WX + pr * math.cos(a), pr * math.sin(a)
        sh += [revolve(prof, px, py, TIP_Z), tube_(3.5, 3.0, TIP_Z + 40.0, TIP_Z + 45.6, px, py)]   # ID band to paint
    for zh in (m(-62.0), m(-212.0)):
        for al in PROBE_ANG:
            a = math.radians(al)
            px, py = WX + pr * math.cos(a), pr * math.sin(a)
            sh.append(tube_(4.2, 3.0, zh, zh + 2.4, px, py))
            sh.append(xform(box(2.5, 5.2, -1.0, 1.0, zh, zh + 2.4), G.T(WX, 0, 0) @ G.Rz(al)))
        sh.append(tube_(3.8, 2.9, zh, zh + 2.4, WX, 0))
    sh.append(box(WX - 12.4, WX + 12.4, -1.4, 1.4, TIP_Z, TIP_Z + 1.0))                  # optical wiper arm
    for s in (1, -1):
        sh.append(box(WX + s * 9 - 2.2, WX + s * 9 + 2.2, -1.6, 1.6, TIP_Z + 0.9, TIP_Z + 2.8))  # brush pads
    return fuse(*sh)


def pod():
    """F09: IP67 power & control pod on its rails (body + lid + glands + vent + hinges + latches)"""
    Pd = R.POD
    x0, x1, hw_ = m(Pd["x0"]), m(Pd["x1"]), m(Pd["hw"])
    pz0, ph, pl = DZ + m(12), m(Pd["h"]), m(Pd["lid"])
    pcx = (x0 + x1) / 2
    sh = [box(x0 + 1, x1 - 1, s * 20 - 2.4, s * 20 + 2.4, DZ, pz0 + 0.2) for s in (1, -1)]      # rails
    sh.append(rblock(pcx, 0, x1 - x0, 2 * hw_, pz0, pz0 + ph, 2.8, r_top=0.0, r_bot=1.0))
    sh.append(rblock(pcx, 0, x1 - x0 + 0.8, 2 * hw_ + 0.8, pz0 + ph - 0.01, pz0 + ph + pl, 3.0, r_top=1.4, r_bot=0.3))
    for gy in (-16, -8, 0, 8, 16):                            # cable glands, front face
        sh += hexgland((x0, gy, pz0 + 6), -1)
    for gy in (-20, 20):                                      # cable glands, aft face
        sh += hexgland((x1, gy, pz0 + 11), +1)
    sh.append(cyl_axis(2.2, (pcx + 18, -hw_ + 0.5, pz0 + 22), (pcx + 18, -hw_ - 1.8, pz0 + 22)))  # pressure vent
    for bx in (pcx - 16, pcx + 16):
        for lx in (bx - 6.2, bx + 3.8):                       # hinge knuckles (starboard)
            sh.append(box(lx, lx + 2.4, hw_ - 0.1, hw_ + 1.8, pz0 + ph - 4.4, pz0 + ph - 1.5))
        sh.append(cyl_axis(1.4, (bx - 3.4, hw_ + 1.2, pz0 + ph + 0.4), (bx + 3.4, hw_ + 1.2, pz0 + ph + 0.4)))
        sh.append(box(bx - 2.8, bx + 2.8, -hw_ - 2.0, -hw_ + 0.1, pz0 + ph - 6.8, pz0 + ph - 1.2))  # latches (port)
    body = fuse(*sh)
    return cut(body, *[cyl(1.2, DZ - 1, DZ + 1.6, x, y) for x, y in POD_PINS])


def hexgland(p, sx):
    """hex nut + cable on a vertical face whose outward normal is (sx, 0, 0)"""
    x, y, z = p
    hexf = face([(x - sx * 0.1, y + 2.54 * math.cos(math.radians(60 * k)), z + 2.54 * math.sin(math.radians(60 * k)))
                 for k in range(6)])
    hx = BRepPrimAPI_MakePrism(hexf, gp_Vec(sx * 1.7, 0, 0)).Shape()
    return [hx, cyl_axis(1.7, (x + sx * 1.5, y, z), (x + sx * 3.0, y, z))]


def sampler():
    """F10: autosampler cassette (body + lid + tamper-seal hasp + purge port)"""
    Sm = R.SAMPLER
    x0, x1, hw_ = m(Sm["x0"]), m(Sm["x1"]), m(Sm["hw"])
    top = DZ + m(Sm["h"])
    scx = (x0 + x1) / 2
    sh = [rblock(scx, 0, x1 - x0, 2 * hw_, DZ, top, 2.8, r_top=0.0, r_bot=0.6),
          rblock(scx, 0, x1 - x0 + 0.8, 2 * hw_ + 0.8, top - 0.01, top + m(Sm["lid"]), 3.0, r_top=1.0, r_bot=0.2)]
    lt = top + m(Sm["lid"])
    hy = -hw_ + 3.6
    for s in (1, -1):                                         # hasp loop
        sh += [cyl(1.0, lt - 0.1, lt + 1.8, scx + s * 8, hy), sphere((scx + s * 8, hy, lt + 1.8), 1.0)]
    sh.append(cyl_axis(1.0, (scx - 8, hy, lt + 1.8), (scx + 8, hy, lt + 1.8)))
    sh.append(box(x1 - 0.1, x1 + 2.0, -18.0, -6.0, DZ + 6.0, DZ + 14.0))                     # purge-to-waste port
    body = fuse(*sh)
    return cut(body, *[cyl(1.2, DZ - 1, DZ + 1.6, x, y) for x, y in SAMPLER_PINS])


def canopy_local():
    """F11 in its own frame: 90 x 70 x 5 PV module, glass face at +z; 6 x 4 cell grid, open back, junction box"""
    V_ = R.PV
    L, Wd, t = m(V_["x1"] - V_["x0"]), m(2 * V_["hw"]), m(V_["t"])     # 90, 70, 5
    slab = prism_xy(rrect(0, 0, L, Wd, 1.2), -t / 2, t / 2)
    back = prism_xy(rrect(0, 0, L - 8.0, Wd - 10.0, 0.8), -t / 2 - 1, t / 2 - 3.0)       # open back, 2 mm glass plate
    jbox = box(m(60), m(140), -m(40), m(40), -t / 2 - 3.6, t / 2 - 2.7)
    cells_x, cells_y = L - 2 * 4.4, Wd - 2 * 4.4
    grooves = [prism_xy(rrect(0, 0, cells_x + 1.2, cells_y + 1.2, 0.3), t / 2 - 0.4, t / 2 + 1)]
    inner = [prism_xy(rrect(0, 0, cells_x, cells_y, 0.01), t / 2 - 0.5, t / 2 + 1)]
    g_ = cut(grooves[0], inner[0])                          # frame / glass boundary groove
    lines = []
    for i in range(1, 6):
        x = -cells_x / 2 + i * cells_x / 6
        lines.append(box(x - 0.3, x + 0.3, -cells_y / 2, cells_y / 2, t / 2 - 0.4, t / 2 + 1))
    for j in range(1, 4):
        y = -cells_y / 2 + j * cells_y / 4
        lines.append(box(-cells_x / 2, cells_x / 2, y - 0.3, y + 0.3, t / 2 - 0.4, t / 2 + 1))
    panel = fuse(cut(slab, back), jbox)
    Minv = np.linalg.inv(PV_MM)
    holes = []
    for sx in STAN_X:                                       # vertical (assembly frame) pin holes, 3.2 deep
        for s in (1, -1):
            zu = Z_UNDER(sx)
            holes.append(xform(cyl(1.25, zu - 1.0, zu + 3.2, sx, s * STAN_Y), Minv))
    return cut(panel, g_, *lines, *holes)


def mast():
    """F12: beacon mast + welded flange + Jal-Deep beacon base (prints upside down, base on the bed)"""
    mx, my = MAST_XY
    z0, ztop = m(R.BEAM_Z1), m(R.MAST_TOP)                   # 60, 160
    body = fuse(cyl(1.5, z0 - 5.4, z0 + 0.1, mx, my), cone(6.0, 3.2, z0, z0 + 2.8, mx, my),
                cyl(3.2, z0 + 2.7, ztop + 0.1, mx, my), cyl(8.0, ztop, ztop + 4.4, mx, my))
    return cut(body, cyl(PIN_HOLE / 2, ztop + 4.4 - 3.0, ztop + 5.0, mx, my))           # lens pin hole


def lens():
    """F13 / F14: 360 deg beacon lens (print one green, one red); 1.75 mm filament pin into the beacon base"""
    mx, my = MAST_XY
    lz = m(R.MAST_TOP) + 4.4
    body = revolve([(0, 0), (7.4, 0), (7.4, 8.8), (6.0, 12.8), (3.2, 14.4), (0, 14.8)], mx, my, lz)
    return cut(body, cyl(PIN_HOLE / 2, lz - 1, lz + 2.5, mx, my))


HANDLE_POS = [(m(hx), s * m(R.PONT_YC + R.PONT_W / 2 - 24)) for hx in (240.0, 760.0) for s in (1, -1)]


def grab_handle(cx, cy):
    """F15: two-person grab handle, 24 x 11 loop of 4.4 mm tube; two filament pins into the hull top"""
    z0, r_, bend, half, hgt = m(R.PONT_H), 2.2, 4.4, 12.0, 11.0
    sh = [cyl(3.4, z0, z0 + 0.8, cx + s * half, cy) for s in (1, -1)]
    sh.append(pipe_fillet([(cx - half, cy, z0 + 0.6), (cx - half, cy, z0 + hgt), (cx + half, cy, z0 + hgt),
                           (cx + half, cy, z0 + 0.6)], r_, bend))
    body = fuse(*sh)
    return cut(body, *[cyl(PIN_HOLE / 2, z0 - 1, z0 + 2.0, cx + s * half, cy) for s in (1, -1)])


# =============================================================================================== STAND PARTS
# Stand frame, model mm: pole axis at x = y = 0, table at z = 0, pier face at x = -72.
BASE_T = 8.0
KEEL_LOW = 116.0 - CARR_Z0 + 0.0          # float resting on the lower stop: tier 1 on the buffer (keel 80.8)
TRAVEL = 65.0                              # hand travel on the stand (the real 2.0 m range would be 400 mm at 1:5)
KEEL_HIGH = KEEL_LOW + TRAVEL
Z_CLAMP_LO = 98.0                          # lower clamp centre: buffer top = 98 + 8 + 6 + 4 = 116
Z_CLAMP_HI = KEEL_HIGH + CARR_TOP + 4.0 + 6.0 + 8.0     # carriage top meets the upper buffer at KEEL_HIGH
COL_TOP = Z_CLAMP_HI + 18.0 + 6.0
ROD_Z0, ROD_Z1 = 2.2, Z_CLAMP_HI + 8.0 + m(110.0)        # rod 310 mm, its foot in the base socket
PIER_FACE = -m(R.PIER_STANDOFF)           # -72
COL_DEPTH, COL_HW = 20.0, 30.0


def base():
    """S01: display base (riverbed); window under the sensor cage, rod socket, column mortise, engraved name"""
    plate = prism_xy(rrect(25.0, 0, 260.0, 170.0, 8.0), 0, BASE_T)
    win = prism_xy(rrect(79.0, 0, 122.0, 100.0, 6.0), -1, BASE_T + 1)
    sock = cyl(FIT_BORE / 2 + 0.05, 2.0, BASE_T + 1, 0, 0)
    mort = box(PIER_FACE - COL_DEPTH - 0.2, PIER_FACE - 4 + 0.2, -24.2, 24.2, 2.0, BASE_T + 1)
    cuts = [win, sock, mort]
    txt = text_solid("AQUASENTINEL R3  \u00b7  1:5 SCALE MODEL", 6.5, (-95.0, -71.0, BASE_T - 0.6), 0.6 + 1.0)
    if txt is not None:
        cuts.append(txt)
    return cut(plate, *cuts)


def text_solid(s, height, origin, depth):
    """engraving tool: text glyphs (cap height ~ height) extruded by depth from origin; None if no font loads"""
    try:
        from OCP.Font import Font_FontAspect_Bold, Font_StrictLevel_Any
        from OCP.Graphic3d import Graphic3d_HTA_LEFT, Graphic3d_VTA_BOTTOM
        from OCP.NCollection import NCollection_Utf8String
        from OCP.StdPrs import StdPrs_BRepFont, StdPrs_BRepTextBuilder
        from OCP.TCollection import TCollection_AsciiString
        from OCP.gp import gp_Ax3
    except Exception as e:                                   # pragma: no cover
        print("  (text skipped:", e, ")")
        return None
    em = height * 1.40                                       # Arial Bold cap height ~ 0.716 em
    font = StdPrs_BRepFont()
    ok = False
    for path in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf"):
        if not os.path.exists(path):
            continue
        for arg in (NCollection_Utf8String(path), TCollection_AsciiString(path)):
            try:
                ok = bool(font.Init(arg, em, 0))
            except Exception:
                ok = False
            if ok:
                break
        if ok:
            break
    if not ok:
        try:
            ok = bool(font.FindAndInit(TCollection_AsciiString("Arial"), Font_FontAspect_Bold, em, Font_StrictLevel_Any))
        except Exception:
            ok = False
    if not ok:
        print("  (text skipped: no font)")
        return None
    try:
        shp = StdPrs_BRepTextBuilder().Perform(font, NCollection_Utf8String(s), gp_Ax3(), Graphic3d_HTA_LEFT,
                                               Graphic3d_VTA_BOTTOM)
        sol = BRepPrimAPI_MakePrism(shp, gp_Vec(0, 0, float(depth))).Shape()
        return moved(sol, *origin)
    except Exception as e:                                   # pragma: no cover
        print("  (text skipped:", e, ")")
        return None


def anchor_pattern(upper):
    """4 chemical-anchor pins (CAD: y +-80, z +-60 -> +-16, +-12); the upper pattern is keyed (target plate on top)"""
    if upper:
        return [(-16.0, 12.0), (16.0, 12.0), (-11.0, -12.0), (11.0, -12.0)]
    return [(-16.0, 12.0), (16.0, 12.0), (-16.0, -12.0), (16.0, -12.0)]


def column():
    """S02: bridge-pier face (concrete) with the 4 chemical-anchor pins for each bracket, tenon into the base"""
    x0, x1 = PIER_FACE - COL_DEPTH, PIER_FACE
    c = 1.5
    prof = [(x0 + c, -COL_HW), (x1 - c, -COL_HW), (x1, -COL_HW + c), (x1, COL_HW - c), (x1 - c, COL_HW), (x0 + c, COL_HW),
            (x0, COL_HW - c), (x0, -COL_HW + c)]
    sh = [prism_xy(prof, BASE_T, COL_TOP), box(x0, x1 - 4.0, -24.0, 24.0, 2.0, BASE_T + 0.1)]
    for zc, upper in ((Z_CLAMP_LO, False), (Z_CLAMP_HI, True)):
        for yy, zz in anchor_pattern(upper):
            sh.append(cyl_axis(1.2, (x1 - 0.1, yy, zc + zz), (x1 + 2.1, yy, zc + zz)))
    return fuse(*sh)


def bracket(upper=False):
    """S03 / S04: pier bracket weldment + clamp cap (fused); the upper one carries the stage target plate"""
    zc = 0.0
    sx_, wy, hz = (m(v) for v in R.BRK_PLATE)                # 2.4, 44, 36
    xp = PIER_FACE
    sh = [prism_yz(rrect(0, zc, wy, hz, 2.8), xp, xp + sx_)]
    arm = [(xp + sx_ - 0.2, zc - 16.0), (-9.6, zc - 7.2), (-9.6, zc + 7.2), (xp + sx_ - 0.2, zc + 16.0)]
    for s in (1, -1):
        y0 = s * m(R.BRK_ARM_Y) - m(R.BRK_ARM_T) / 2
        sh.append(prism_xz(arm, y0, y0 + m(R.BRK_ARM_T)))
    sh.append(box(m(-262), m(-252), -5.7, 5.7, zc - 9.2, zc + 9.2))                       # tie plate
    sh.append(box(-24.0, -8.0, -7.6, 7.6, zc - 7.2, zc + 7.2))                             # clamp web (model only)
    sh.append(cyl(m(R.CLAMP_OD / 2), zc - 8.0, zc + 8.0))                                  # clamp ring OD 24 x 16
    for s in (1, -1):                                                                       # clamp bolt lugs
        sh.append(prism_xy([(-2.8, s * 11.2), (2.8, s * 11.2), (2.8, s * 15.2), (1.2, s * 15.2)], zc - 6.4, zc + 6.4))
    if upper:
        sh.append(box(7.0, 37.0, -10.0, 10.0, zc + 6.4, zc + 8.0))                         # stage target plate
    body = fuse(*sh)
    rb = FIT_BORE / 2
    bore = fuse(cyl(rb, zc - 9, zc + 9), prism_xy([(rb / math.sqrt(2), -rb / math.sqrt(2)), (rb * math.sqrt(2), 0),
                                                    (rb / math.sqrt(2), rb / math.sqrt(2)), (0, 0)], zc - 9, zc + 9))
    holes = [cyl_axis(1.35, (xp - 1, yy, zc + zz), (xp + sx_ + 1, yy, zc + zz)) for yy, zz in anchor_pattern(upper)]
    return cut(body, bore, *holes)


def stop_collar():
    """S05: split stop collar + EPDM buffer ring (one print; 2 needed)"""
    return fuse(tube_(m(R.STOP_OD / 2), FIT_STOP / 2, 0.0, 6.0), tube_(m(R.STOP_OD / 2 - 2), m(R.POLE_R + 2), 5.99, 10.0),
                box(9.6, 12.4, -2.0, 2.0, 0.0, 6.0))


def pole_cap():
    """S06: pole top cap"""
    body = revolve([(0, 0), (7.4, 0), (7.4, 4.2), (5.6, 6.6), (0, 7.5)])
    return cut(body, cyl(FIT_BORE / 2, -1, 3.5))


def rod_half():
    """OPT: half of a printed 12 mm pole, lying on its split face; glue two halves with 1.75 mm filament pins"""
    L = ROD_Z1 - ROD_Z0
    r = ROD_D / 2
    pts = [(r * math.cos(a), r * math.sin(a)) for a in np.linspace(0, math.pi, 49)]
    body = prism_xz(pts, 0, L)                                # semicircle in (x, z), length along y
    return cut(body, *[cyl(PIN_HOLE / 2, -1, 3.0, 0, y) for y in (25.0, L / 2, L - 25.0)])


# =============================================================================================== mesh + STL
def mesh(shape, lin=0.02, ang=0.15):
    BRepMesh_IncrementalMesh(shape, lin, False, ang, True)
    V, F, off = [], [], 0
    e = TopExp_Explorer(shape, TopAbs_FACE)
    while e.More():
        f = TopoDS.Face_s(e.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(f, loc)
        if tri is not None:
            tr = loc.Transformation()
            n = tri.NbNodes()
            V.extend((p.X(), p.Y(), p.Z()) for p in (tri.Node(i).Transformed(tr) for i in range(1, n + 1)))
            rev = f.Orientation() == TopAbs_REVERSED
            for i in range(1, tri.NbTriangles() + 1):
                a, b, c = tri.Triangle(i).Get()
                F.append((off + a - 1, off + c - 1, off + b - 1) if rev else (off + a - 1, off + b - 1, off + c - 1))
            off += n
        e.Next()
    V, F = np.asarray(V, float), np.asarray(F, np.int64)
    return weld(V, F)


def weld(V, F, tol=1e-5):
    key = np.round(V / tol).astype(np.int64)
    _, idx, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    V2, F2 = V[idx], inv.reshape(-1)[F]
    keep = (F2[:, 0] != F2[:, 1]) & (F2[:, 1] != F2[:, 2]) & (F2[:, 0] != F2[:, 2])
    return V2, F2[keep]


def mesh_check(V, F):
    """watertight + consistently oriented: every directed edge appears once and its reverse once"""
    e = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    n = len(V)
    code = e[:, 0] * n + e[:, 1]
    rcode = e[:, 1] * n + e[:, 0]
    uniq, cnt = np.unique(code, return_counts=True)
    dup = int((cnt > 1).sum())
    missing = int((~np.isin(rcode, code)).sum())
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    vol = float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)
    return dict(triangles=int(len(F)), open_or_bad_edges=missing + dup, signed_volume_mm3=round(vol, 1),
                watertight=bool(missing == 0 and dup == 0 and vol > 0))


def write_stl(path, meshes, name="AquaSentinel R3 1:5"):
    tris = []
    for V, F in meshes:
        tris.append(V[F])
    T_ = np.concatenate(tris).astype(np.float64)
    nrm = np.cross(T_[:, 1] - T_[:, 0], T_[:, 2] - T_[:, 0])
    ln = np.linalg.norm(nrm, axis=1, keepdims=True)
    nrm = np.divide(nrm, ln, out=np.zeros_like(nrm), where=ln > 0)
    rec = np.zeros(len(T_), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = nrm, T_
    with open(path, "wb") as fh:
        hdr = (name + " - binary STL, mm").encode("ascii", "replace")[:80]
        fh.write(hdr.ljust(80, b" "))
        fh.write(np.uint32(len(T_)).tobytes())
        fh.write(rec.tobytes())
    return len(T_)


def overhang_stats(V, F, bed_tol=0.3):
    """downward-facing area above the bed in print orientation: > 45 deg overhang, and near-flat (bridges)"""
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    n = np.cross(b - a, c - a)
    ar = np.linalg.norm(n, axis=1) / 2
    nz = n[:, 2] / np.maximum(2 * ar, 1e-12)
    zc = (a[:, 2] + b[:, 2] + c[:, 2]) / 3
    up = zc > bed_tol
    steep = up & (nz < -math.cos(math.radians(45)))
    flat = up & (nz < -0.985)
    return dict(overhang_gt45_mm2=round(float(ar[steep].sum()), 1), flat_downward_mm2=round(float(ar[flat].sum()), 1))


def apply_M(V, M):
    return V @ M[:3, :3].T + M[:3, 3]


def rot_to(src, dst):
    """4x4 rotation taking unit vector src onto dst"""
    a, b = np.asarray(src, float), np.asarray(dst, float)
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    c = float(a @ b)
    if c > 1 - 1e-12:
        return np.eye(4)
    if c < -1 + 1e-12:
        ax = np.cross(a, [1, 0, 0]) if abs(a[0]) < 0.9 else np.cross(a, [0, 1, 0])
        return G.Raxis(ax, 180.0)
    return G.Raxis(np.cross(a, b), math.degrees(math.acos(c)))


# =============================================================================================== build
def build(out_dir):
    os.makedirs(os.path.join(out_dir, "parts"), exist_ok=True)
    rep = dict(scale="1:5", units="mm", source="mechanical/src/params.py (R3)", bed_used_mm=list(BED), parts=[], checks={})

    # ------------------------------------------------------------ parts: (id, file, label, colour, qty, shape_asm, print R)
    print("building float parts ...")
    hs = hull_starboard()
    fr = frame()
    ca = carriage()
    wc = well_and_cage()
    de = deflector()
    cc = cartridge_cap()
    pc = probe_cluster()
    po = pod()
    sa = sampler()
    cl = canopy_local()
    cn = xform(cl, PV_MM)
    ma = mast()
    le = lens()
    handles = [grab_handle(*p) for p in HANDLE_POS]
    print("building stand parts ...")
    bs = base()
    co = column()
    bl, bu = bracket(False), bracket(True)
    sc = stop_collar()
    pk = pole_cap()
    rh = rod_half()

    Rflip = G.Rx(180)
    # print orientation = rotation applied to the assembly-frame solid (then dropped onto the bed)
    defl_n = np.array([-1.0, -1.0, 0.0]) / math.sqrt(2)    # outer face of the port arm goes on the bed
    kit = [
        ("F01", "hull_starboard", "Pontoon hull, starboard", "yellow", 1, hs, Rflip, "float"),
        ("F02", "hull_port", "Pontoon hull, port", "yellow", 1, mirror_y(hs), Rflip, "float"),
        ("F03", "frame_deck_struts_stanchions", "Frame: 4 crossbeams, deck, carriage struts, canopy stanchions, LTE antenna",
         "silver", 1, fr, np.eye(4), "float"),
        ("F04", "guide_carriage", "Bow guide carriage, 8 rollers, stage sensor", "silver", 1, ca, np.eye(4), "float"),
        ("F05", "sensor_well_and_cage", "Sensor well, hatch flange and guard cage", "black", 1, wc, Rflip, "float"),
        ("F06", "debris_deflector", "V debris deflector", "black", 1, de, G.Rz(45) @ rot_to(defl_n, (0, 0, -1)), "float"),
        ("F07", "cartridge_cap_handle", "Sensor cartridge cap with lift handle", "black", 1, cc, np.eye(4), "float"),
        ("F08", "probe_cluster", "Probe cluster: 4 probes, spine, holders, wiper", "dark grey", 1, pc, np.eye(4), "float"),
        ("F09", "control_pod", "Power and control pod", "light grey", 1, po, np.eye(4), "float"),
        ("F10", "autosampler", "Autosampler cassette", "white", 1, sa, np.eye(4), "float"),
        ("F11", "pv_canopy", "Solar (PV) canopy", "dark blue", 1, cn, G.Rx(180) @ np.linalg.inv(PV_MM), "float"),
        ("F12", "beacon_mast", "Beacon mast and beacon base", "silver", 1, ma, Rflip, "float"),
        ("F13", "beacon_lens_green", "Beacon lens, GREEN (normal)", "translucent green", 1, le, np.eye(4), "float"),
        ("F14", "beacon_lens_red", "Beacon lens, RED (alert)", "translucent red", 1, le, np.eye(4), "float"),
    ]
    for i, h in enumerate(handles):
        kit.append((f"F15{'abcd'[i]}", f"grab_handle_{i + 1}", f"Grab handle {i + 1} of 4", "silver", 1, h, np.eye(4), "float"))
    kit += [
        ("S01", "display_base", "Display base (riverbed)", "grey", 1, bs, np.eye(4), "stand"),
        ("S02", "pier_column", "Bridge pier column", "concrete grey", 1, co, G.Rz(90) @ G.Ry(-90), "stand"),
        ("S03", "pier_bracket_lower", "Pier bracket, lower", "silver", 1, moved(bl, 0, 0, Z_CLAMP_LO), G.Ry(-90), "stand"),
        ("S04", "pier_bracket_upper", "Pier bracket, upper (with stage target plate)", "silver", 1,
         moved(bu, 0, 0, Z_CLAMP_HI), G.Ry(-90), "stand"),
        ("S05a", "stop_collar_lower", "Stop collar + buffer, lower", "silver", 1, moved(sc, 0, 0, Z_CLAMP_LO + 8.0), np.eye(4), "stand"),
        ("S05b", "stop_collar_upper", "Stop collar + buffer, upper (fit upside down)", "silver", 1,
         moved(xform(sc, Rflip), 0, 0, Z_CLAMP_HI - 8.0), Rflip, "stand"),
        ("S06", "pole_cap", "Pole top cap", "black", 1, moved(pk, 0, 0, ROD_Z1 - 3.5), np.eye(4), "stand"),
    ]

    # ------------------------------------------------------------ mesh, check, orient for print
    keel_view = KEEL_LOW + TRAVEL / 2
    print("meshing and checking ...")
    printed = {}
    asm_meshes = []
    for pid, fname, label, colour, qty, shp, Rp, grp in kit:
        V, F = mesh(shp)
        chk = mesh_check(V, F)
        ana = BRepCheck_Analyzer(shp).IsValid()
        Va = apply_M(V, G.T(0, 0, keel_view)) if grp == "float" else V
        if pid != "F14":
            asm_meshes.append((pid, colour, Va, F))
        Vp = apply_M(V, Rp)
        lo, hi = Vp.min(axis=0), Vp.max(axis=0)
        Vp = Vp - np.array([lo[0], lo[1], lo[2]])
        size = (hi - lo)
        printed[pid] = (Vp, F)
        ovh = overhang_stats(Vp, F)
        vol = volume(shp)
        rep["parts"].append(dict(id=pid, file=f"parts/{pid}_{fname}.stl", name=label, colour=colour, qty=qty,
                                 print_size_mm=[round(float(v), 1) for v in size], volume_cm3=round(vol / 1000, 2),
                                 solids=n_solids(shp), brep_valid=bool(ana), **chk, **ovh))
        write_stl(os.path.join(out_dir, "parts", f"{pid}_{fname}.stl"), [(Vp, F)], f"AquaSentinel R3 1:5 {pid} {label}")
        print(f"  {pid:5s} {label[:58]:58s} {size[0]:6.1f} x {size[1]:6.1f} x {size[2]:6.1f}  "
              f"solids={n_solids(shp)} valid={ana} watertight={chk['watertight']}")
    V, F = mesh(rh)
    Vr = V - V.min(axis=0)
    rep["optional_rod_half"] = dict(file="parts/OPT_rod_half_print_2.stl", print_size_mm=[round(float(v), 1) for v in Vr.max(axis=0)],
                                    **mesh_check(V, F))
    write_stl(os.path.join(out_dir, "parts", "OPT_rod_half_print_2.stl"), [(Vr, F)], "AquaSentinel R3 1:5 optional rod half (print 2)")

    # ------------------------------------------------------------ plates
    float_ids = [k[0] for k in kit if k[7] == "float"]
    stand_ids = [k[0] for k in kit if k[7] == "stand"]
    lay_f = layout(printed, float_ids, BED)
    lay_s = layout_stand(printed)
    for name, lay in (("AquaSentinel_R3_1to5_FLOAT.stl", lay_f), ("AquaSentinel_R3_1to5_STAND.stl", lay_s)):
        meshes = [(printed[pid][0] + off, printed[pid][1]) for pid, off in lay.items()]
        n = write_stl(os.path.join(out_dir, name), meshes, "AquaSentinel R3 1:5 " + name.split("_")[-1][:-4] + " plate")
        allv = np.concatenate([mm[0] for mm in meshes])
        ext = allv.max(axis=0) - allv.min(axis=0)
        rep["checks"][name] = dict(parts=len(lay), triangles=n, extent_mm=[round(float(v), 1) for v in ext],
                                   fits_300x320x300=bool(ext[0] <= BED[0] and ext[1] <= BED[1] and ext[2] <= BED[2]),
                                   layout={k: [round(float(v), 1) for v in o[:2]] for k, o in lay.items()})
    plate_store = {}
    for plate, lay in (("FLOAT", lay_f), ("STAND", lay_s)):
        for pid, off in lay.items():
            col = next(k[3] for k in kit if k[0] == pid)
            plate_store[f"{plate}|{pid}|{col}|V"] = printed[pid][0] + off
            plate_store[f"{plate}|{pid}|{col}|F"] = printed[pid][1]
    np.savez_compressed(os.path.join(out_dir, "previews", "_plate_meshes.npz"), **plate_store)
    rod = mesh(cyl(ROD_D / 2, ROD_Z0, ROD_Z1))
    write_stl(os.path.join(out_dir, "AquaSentinel_R3_1to5_ASSEMBLED_view.stl"),
              [(v, f) for _, _, v, f in asm_meshes] + [rod], "AquaSentinel R3 1:5 assembled view - do not print")
    np.savez_compressed(os.path.join(out_dir, "previews", "_asm_meshes.npz") if os.path.isdir(os.path.join(out_dir, "previews"))
                        else os.path.join(out_dir, "_asm_meshes.npz"),
                        **{f"{pid}|{col}|V": v for pid, col, v, f in asm_meshes},
                        **{f"{pid}|{col}|F": f for pid, col, v, f in asm_meshes}, ROD_V=rod[0], ROD_F=rod[1])

    if FAST:
        old = os.path.join(out_dir, "build_report.json")
        if os.path.exists(old):
            prev = json.load(open(old, encoding="utf-8"))
            for k, v in prev.get("checks", {}).items():
                rep["checks"].setdefault(k, v)
            rep["float_mass_estimate"] = prev.get("float_mass_estimate")
        rep["note"] = "fast rebuild: fit checks and mass estimate copied from the previous full build"
        with open(old, "w", encoding="utf-8", newline=chr(10)) as fh:
            json.dump(rep, fh, indent=1)
        return rep

    # ------------------------------------------------------------ fits and clearances (assembly frame)
    print("checking fits ...")
    rodS = cyl(ROD_D / 2, ROD_Z0 - keel_view, ROD_Z1 - keel_view)   # rod in the float frame at the view position
    by = {k[0]: k[5] for k in kit}
    fl = lambda a, b: round(float(distance(a, b)), 3)            # noqa: E731
    ck = rep["checks"]
    ck["rod_to_rollers_mm"] = fl(rodS, ca)
    ck["carriage_frame_overlap_mm3"] = round(overlap_volume(ca, fr), 3)
    ck["strut_tips_to_lugs_mm"] = [fl(sphere(t, STRUT_R), ca) for t in STRUT_TIP]
    ck["well_tube_to_deck_hole_mm"] = fl(cyl(m(R.WELL_OD / 2), DECK_BOT - 0.5, DZ - 0.05, WX, 0), fr)
    ck["probe_cluster_to_well_and_cage_mm"] = fl(pc, wc)
    ck["cartridge_cap_well_overlap_mm3"] = round(overlap_volume(cc, wc), 3)
    ck["deflector_to_well_mm"] = fl(de, wc)
    ck["deflector_frame_overlap_mm3"] = round(overlap_volume(de, fr), 3)
    ck["canopy_frame_overlap_mm3"] = round(overlap_volume(cn, fr), 3)
    ck["canopy_to_sampler_mm"] = fl(cn, sa)
    ck["canopy_to_pod_mm"] = fl(cn, po)
    ck["struts_to_cartridge_lift_path_mm"] = fl(fr, cyl(m(R.CAP_D / 2), DZ + 2, 140, WX, 0))
    ck["pod_frame_overlap_mm3"] = round(overlap_volume(po, fr), 3)
    ck["sampler_frame_overlap_mm3"] = round(overlap_volume(sa, fr), 3)
    ck["mast_frame_overlap_mm3"] = round(overlap_volume(ma, fr), 3)
    ck["hulls_frame_overlap_mm3"] = round(overlap_volume(by["F01"], fr) + overlap_volume(by["F02"], fr), 3)
    ck["carriage_to_hulls_mm"] = min(fl(ca, by["F01"]), fl(ca, by["F02"]))
    float_all = [(k, by[k]) for k in float_ids if k != "F14"]
    stand_all = [(k, by[k]) for k in stand_ids]
    for tag, keel in (("lowest", KEEL_LOW), ("highest", KEEL_HIGH)):
        worst_ov, dmin, pair = 0.0, 1e9, None
        for ka, a in float_all:
            aw = moved(a, 0, 0, keel)
            for kb, b in stand_all:
                ov = overlap_volume(aw, b)
                worst_ov = max(worst_ov, ov if ov == ov else 0.0)
                if ka != "F04":
                    d = distance(aw, b)
                    if d < dmin:
                        dmin, pair = d, f"{ka}-{kb}"
        ck[f"at_{tag}_overlap_float_vs_stand_mm3"] = round(worst_ov, 4)
        ck[f"at_{tag}_closest_noncarriage_mm"] = [round(float(dmin), 2), pair]
        ck[f"at_{tag}_carriage_to_stops_mm"] = round(float(min(distance(moved(ca, 0, 0, keel), by[k])
                                                          for k in ("S05a", "S05b"))), 3)
        ck[f"at_{tag}_cage_bottom_above_table_mm"] = round(float(bbox(by["F05"])[2] + keel), 2)
    ck["stand"] = dict(keel_lowest=KEEL_LOW, keel_highest=KEEL_HIGH, travel=TRAVEL, clamp_lower_z=Z_CLAMP_LO,
                       clamp_upper_z=round(Z_CLAMP_HI, 2), column_top=round(COL_TOP, 2),
                       rod_length=round(ROD_Z1 - ROD_Z0, 1), rod_d=ROD_D)

    # ------------------------------------------------------------ mass, CG, draft estimate (printed PLA)
    rep["float_mass_estimate"] = float_mass(kit)
    with open(os.path.join(out_dir, "build_report.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rep, fh, indent=1)
    return rep


def layout(printed, ids, bed, gap=4.0, margin=3.0):
    """skyline bottom-left packing of footprints (each part may turn 90 deg); returns {id: offset}"""
    items = []
    for pid in ids:
        V = printed[pid][0]
        w, h = V[:, 0].max(), V[:, 1].max()
        items.append((pid, w, h))
    items.sort(key=lambda t: -max(t[1], t[2]) * min(t[1], t[2]))
    W, H = bed[0] - 2 * margin, bed[1] - 2 * margin
    sky = [(0.0, W, 0.0)]        # segments (x0, x1, y)
    out = {}
    for pid, w, h in items:
        best = None
        for rot in (False, True):
            ww, hh = (h, w) if rot else (w, h)
            for x0, _, _ in sky:
                if x0 + ww > W + 1e-6:
                    continue
                y = max(y_ for a, b, y_ in sky if a < x0 + ww - 1e-9 and b > x0 + 1e-9)
                if y + hh > H + 1e-6:
                    continue
                if best is None or (y, x0) < (best[0], best[1]):
                    best = (y, x0, rot, ww, hh)
        if best is None:
            raise RuntimeError(f"part {pid} does not fit on the plate")
        y, x0, rot, ww, hh = best
        V, F = printed[pid]
        if rot:
            V2 = np.c_[V[:, 1], -V[:, 0], V[:, 2]]
            V2 -= V2.min(axis=0)
            printed[pid] = (V2, F)
        out[pid] = np.array([margin + x0, margin + y, 0.0])
        top = y + hh + gap
        new = []
        for a, b, yy in sky:
            if b <= x0 or a >= x0 + ww + gap:
                new.append((a, b, yy))
            else:
                if a < x0:
                    new.append((a, x0, yy))
                if b > x0 + ww + gap:
                    new.append((x0 + ww + gap, b, yy))
        new.append((x0, min(x0 + ww + gap, W), top))
        sky = sorted(new)
    return out


def layout_stand(printed, margin=3.0):
    """hand layout: column along Y on the left, base turned 90 deg, small parts inside the base window"""
    def turn(pid):
        V, F = printed[pid]
        V2 = np.c_[V[:, 1], -V[:, 0], V[:, 2]]
        printed[pid] = (V2 - V2.min(axis=0), F)
    turn("S01")
    out = {}
    out["S02"] = np.array([margin, margin + 6.0, 0.0])
    cw = printed["S02"][0][:, 0].max()
    bx = margin + cw + 6.0
    out["S01"] = np.array([bx, margin + 25.0, 0.0])
    bV = printed["S01"][0]
    # base turned: window centre is at stand (x 79, y 0) -> find its place in the turned frame
    win_cx = bx + (85.0 - 0.0)            # turned: new x = old y + 85 (old y range -85..85)
    win_cy = margin + 25.0 + (155.0 - 79.0)  # new y = 155 - old x
    small = ["S03", "S04", "S05a", "S05b", "S06"]
    pos = {"S03": (-21.0, -30.0), "S04": (21.0, -30.0), "S05a": (-24.0, 24.0), "S05b": (4.0, 24.0), "S06": (30.0, 24.0)}
    for pid in small:
        V = printed[pid][0]
        w, h = V[:, 0].max(), V[:, 1].max()
        dx, dy = pos[pid]
        out[pid] = np.array([win_cx + dx - w / 2, win_cy + dy - h / 2, 0.0])
    del bV
    return out


def float_mass(kit, rho=1.24, walls=0.84, skin=0.9, infill=0.15):
    """printed-PLA mass estimate (2 walls, ~1 mm skins, 15 % infill), CG, and the draft from the hull geometry"""
    tot, mom = 0.0, np.zeros(3)
    rows = []
    float_solids = []
    for pid, fname, label, colour, qty, shp, Rp, grp in kit:
        if grp != "float" or pid == "F14":                  # only one lens is fitted at a time
            continue
        vol, ar = volume(shp) / 1000.0, area(shp) / 100.0    # cm3, cm2
        shell = min(vol, ar * (0.5 * walls + 0.5 * skin) / 10.0)
        g = rho * (shell + infill * (vol - shell))
        tot += g
        mom += g * centroid(shp)
        rows.append(dict(id=pid, grams=round(g, 1)))
        if bbox(shp)[2] < 50.0:
            float_solids.append(shp)
    cg = mom / tot
    # draft: displaced volume of every float solid below the waterline (fresh water) = mass
    def displaced(d):
        cutter = box(-200, 400, -200, 200, -200, d)
        v, mx = 0.0, 0.0
        for s in float_solids:
            c = common(s, cutter)
            vv = volume(c)
            if vv > 1e-6:
                v += vv
                mx += vv * centroid(c)[0]
        return v / 1000.0, (mx / v if v > 0 else 0.0)
    lo, hi = 0.0, 50.0
    for _ in range(16):
        mid = (lo + hi) / 2
        if displaced(mid)[0] < tot:
            lo = mid
        else:
            hi = mid
    d = (lo + hi) / 2
    vdisp, lcb = displaced(d)
    target = 48.54 * S ** 3 * 1000.0       # CAD mass 48.54 kg at 1:5 (mass scales with S^3)
    return dict(assumptions="PLA 1.24 g/cm3, 2 walls, ~1 mm top/bottom skins, 15 % infill, one lens fitted",
                grams_total=round(tot, 0), per_part=rows, cg_mm=[round(float(c), 1) for c in cg],
                draft_mm=round(d, 1), lcb_x_mm=round(lcb, 1), lcg_minus_lcb_mm=round(float(cg[0] - lcb), 1),
                design_scaled=dict(grams=round(target, 0), draft_mm=round(116.8 * S, 1), lcg_x_mm=round(395.1 * S, 1)))


FAST = "--fast" in sys.argv

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else HERE
    os.makedirs(os.path.join(out, "previews"), exist_ok=True)
    r = build(out)
    print(json.dumps(r["checks"], indent=1)[:6000])
    print(json.dumps(r["float_mass_estimate"], indent=1)[:2000])
