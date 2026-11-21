"""Native pontoon hull AS3-201: lofted bow and stern through exact sections (lines + true arcs),
a straight mid-body extrusion, and straight rub rails, all from the generator's parameters."""
import math
import numpy as np
from swbuild import M, NOTHING

P = dict(L=1000.0, W=230.0, H=260.0, Rb=90.0, Rs=55.0, BL=260.0, BH=125.0, SL=130.0, SH=50.0, RB=40.0, RT=14.0,
         RUB_Z=190.0, RUB_R=9.0)


def hw(x):
    L, W, Rb, Rs = P["L"], P["W"], P["Rb"], P["Rs"]
    if x < Rb:
        return (W / 2 - Rb) + math.sqrt(max(Rb ** 2 - (Rb - x) ** 2, 0))
    if x > L - Rs:
        return (W / 2 - Rs) + math.sqrt(max(Rs ** 2 - (x - (L - Rs)) ** 2, 0))
    return W / 2


def zb(x):
    L = P["L"]
    if x < P["BL"]:
        return P["BH"] * (1 - x / P["BL"]) ** 2
    if x > L - P["SL"]:
        return P["SH"] * (1 - (L - x) / P["SL"]) ** 2
    return 0.0


def section(x):
    h, z0, H = hw(x), zb(x), P["H"]
    w, hh = 2 * h, H - z0
    rb = min(P["RB"], h - 0.6, hh / 2 - 0.6)
    rt = min(P["RT"], h - 0.6)
    rb = max(0.2, min(rb, w / 2 - 0.05, hh / 2 - 0.05))
    rt = max(0.2, min(rt, w / 2 - 0.05, hh / 2 - 0.05))
    y0, y1, z1 = -h, h, H
    kb, kt = rb * (1 - math.sqrt(0.5)), rt * (1 - math.sqrt(0.5))
    # same entity order for every station so the loft connects corresponding edges
    return [("line", (y0 + rb, z0), (y1 - rb, z0)),
            ("arc", (y1 - rb, z0), (y1 - kb, z0 + kb), (y1, z0 + rb)),
            ("line", (y1, z0 + rb), (y1, z1 - rt)),
            ("arc", (y1, z1 - rt), (y1 - kt, z1 - kt), (y1 - rt, z1)),
            ("line", (y1 - rt, z1), (y0 + rt, z1)),
            ("arc", (y0 + rt, z1), (y0 + kt, z1 - kt), (y0, z1 - rt)),
            ("line", (y0, z1 - rt), (y0, z0 + rb)),
            ("arc", (y0, z0 + rb), (y0 + kb, z0 + kb), (y0 + rb, z0))]


def loft(p, stations, name, start_tan, end_tan):
    names = []
    for x in stations:
        p.open_sketch("x", x)
        p.draw(section(x))
        f = p.close_sketch(p.nm("Hull station "))
        names.append(f.Name)
    p.d.ClearSelection2(True)
    for n in names:
        p.d.Extension.SelectByID2(n, "SKETCH", 0, 0, 0, True, 1, NOTHING, 0)
    f = p.fm.InsertProtrusionBlend2(False, True, False, 1.0, start_tan, end_tan, 1.0, 1.0, True, True, False, 0, 0, 0,
                                    True, True, True, 0)
    return p._named(f, name)


def build(p, info):
    L = P["L"]
    bow = [0, 4, 12, 26, 45, 66, 90, 120, 155, 195, 230, 260]
    stern = [L - 130, L - 100, L - 75, L - 55, L - 38, L - 22, L - 10, L - 3, L]
    loft(p, bow, "Bow loft (rocker + R90 plan radius)", 0, 1)
    # mid-body: constant section, extruded from the end of the bow loft to the start of the stern loft
    p.open_sketch("x", 0.0)
    p.draw(section(400.0))
    p.close_sketch("Hull mid-section")
    p.fm.FeatureExtrusion3(True, False, False, 0, 0, (stern[0] - bow[-1]) * M, 0, False, False, False, False, 0, 0,
                           False, False, False, False, True, True, True, 3, bow[-1] * M, False)
    p._named(p.d.FeatureByPositionReverse(0), "Mid-body extrude")
    loft(p, stern, "Stern loft (R55 plan radius)", 1, 0)
    # rub rails, both sides (one mould makes both hulls)
    for s in (1, -1):
        p.open_sketch("x", 0.0)
        p.draw([("circle", (s * (P["W"] / 2 - 3), P["RUB_Z"]), P["RUB_R"])])
        p.close_sketch(p.nm("Rub rail profile "))
        f = p.fm.FeatureExtrusion3(True, False, False, 0, 0, (L - 75 - 105) * M, 0, False, False, False, False, 0, 0,
                                   False, False, False, False, True, True, True, 3, 105 * M, False)
        p._named(f, "Rub rail " + ("starboard" if s > 0 else "port"))
