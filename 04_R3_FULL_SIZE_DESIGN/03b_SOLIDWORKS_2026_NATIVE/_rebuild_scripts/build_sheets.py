"""Build the AquaSentinel R3 drawing set in SOLIDWORKS, one A3 drawing per sheet (first-angle, ISO title block).
Usage: python build_sheets.py 1 2 3 ...   (no args = all six)"""
import sys
import textwrap
import time
from swlib import *

BASE = {"DrawnBy": "Team SHJ", "DrawnDate": "16-11-2026", "Revision": "A", "Finish": "-",
        "COMPANYNAME": "AquaSentinel R3"}
CARRIAGE = ("AS3-301", "AS3-302", "AS3-311", "AS3-312", "AS3-313", "AS3-314", "AS3-321", "AS3-902")
WELL = ("AS3-40", "AS3-41", "AS3-42")


def props(**kw):
    p = dict(BASE)
    p.update(kw)
    return p


def notes(d, lines, x, y, width=110):
    out = ["NOTES"]
    for i, t in enumerate(lines, 1):
        w = textwrap.wrap(t, width - 4)
        out.append(f"{i}.  {w[0]}")
        out += [f"     {s}" for s in w[1:]]
    return note(d, "\n".join(out), x, y, 2.5)


def dims(d, v, w=True, h=True):
    try:
        r = overall_edges(d, v, w, h)
        return {k: round(x.GetDimension2(0).Value) for k, x in (r or {}).items() if x}
    except Exception as e:
        return f"dim error {e}"


def finish(d, s, views, targets=()):
    """Set sheet scale, rebuild, then move views so their visible content centres on the targets.
    targets: (view, x or None, y or None) in order (parents before aligned children)."""
    set_scale(d, 1, s)
    d.ForceRebuild3(True)
    for v, x, y in targets:
        o = v.GetOutline
        p = v.Position
        dx = 0 if x is None else x - (o[0] + o[2]) / 2
        dy = 0 if y is None else y - (o[1] + o[3]) / 2
        v.Position = arr([p[0] + dx, p[1] + dy])
        d.ForceRebuild3(True)
    for v in views:
        print("  ", v.Name, [round(c * 1000) for c in v.GetOutline])


def s1():
    s = 20
    d = new_drawing(props(Title="R3 INSTALLATION GA", Material="As parts list", Weight="float 48.5 kg (est.)"), 1, s)
    el = view(d, ASM, "*Bottom", 0.075, 0.18, 1 / s)
    bow = projected(d, el, 0.16, 0.18)
    iso = iso_of(d, el, 1 / 25)
    finish(d, s, (el, bow, iso), [(el, 0.075, 0.18), (bow, 0.16, None), (iso, 0.31, 0.185)])
    print("el", dims(d, el), "bow", dims(d, bow, True, False))
    label(d, el, "ELEVATION (from port)")
    label(d, bow, "END VIEW (from bow)")
    label(d, iso, "ISOMETRIC (1:25)")
    notes(d, ["Upper and lower pier brackets are identical (AS3-101). Fit the lower one at or below the lowest recorded level.",
              "Anchors: 4 x M12 A4 chemical anchors per bracket into sound pier concrete; confirm pull-out with the pier owner.",
              "Design stage range 2000 mm between the stops; bracket span 2678 mm. Set from the site gauge record before cutting the pole.",
              "The float rides on 8 rollers between EPDM-buffered stops and turns freely about the pole, trailing downstream.",
              "Pole 2 in Sch 40S 316L, 2978 mm, at 1.5 m/s current + 500 N debris: 64.0 MPa with pinned ends and the carriage couple, SF 2.66 on 170 MPa yield."],
          0.024, 0.088, 118)
    return d, "AS3-DWG-01"


def s2():
    s = 10
    d = new_drawing(props(Title="R3 FLOAT GA", Material="As parts list", Weight="48.5 kg (design est.)"), 1, s)
    el = view(d, ASM, "*Bottom", 0.08, 0.2, 1 / s)
    hide(el, drop=INSTALL)
    bow = projected(d, el, 0.185, 0.2)
    hide(bow, drop=INSTALL)
    pl = projected(d, el, 0.08, 0.075)
    hide(pl, drop=INSTALL)
    finish(d, s, (el, bow, pl), [(el, 0.092, 0.195), (bow, 0.2, None), (pl, None, 0.07)])
    print("el", dims(d, el), "bow", dims(d, bow, True, False), "plan", dims(d, pl, False, True))
    label(d, el, "ELEVATION (from port)")
    label(d, bow, "END VIEW (from bow)")
    label(d, pl, "PLAN (from above)")
    rows = [("ITEM", "PART No.", "DESCRIPTION", "QTY"),
            (1, "AS3-201", "Pontoon hull, rotomoulded PE, foam filled", 2),
            (2, "AS3-211", "Crossbeam 6061 SHS 40x40x3", 4),
            (3, "AS3-213", "Equipment deck plate 6061 t3", 1),
            (4, "AS3-301/302", "Guide carriage, fixed half + gate", 1),
            (5, "AS3-311", "Concave guide roller UHMW-PE", 8),
            (6, "AS3-401/403", "Sensor well + guard cage", 1),
            (7, "AS3-404", "V debris deflector HDPE", 1),
            (8, "AS3-411..417", "Pull-up sensor cartridge, 4 probes", 1),
            (9, "AS3-511", "Power and control pod IP67", 1),
            (10, "AS3-521", "PV module 20 W on hinged canopy", 1),
            (11, "AS3-601", "Autosampler cassette, 4 x 250 mL", 1),
            (12, "AS3-703", "Jal-Deep 360 deg beacon", 1),
            (13, "AS3-712", "Stage sensor, ultrasonic, looking up", 1),
            (14, "AS3-801", "Grab handle", 4),
            (15, "AS3-802", "Lifting eye M12", 4)]
    table(d, 0.262, 0.283, rows, (9, 24, 95, 9))
    notes(d, ["Mass 48.54 kg with sample bottles full (design estimate from CAD); draft 116.8 mm, freeboard 143.2 mm.",
              "Reserve buoyancy 2.27; GM(T) 0.551 m; righting arm positive to 60 deg.",
              "The pole runs 100 mm inside the bow line between the hulls; the float trails downstream like a vane.",
              "All fasteners A4-70 stainless; nylon isolation at every 316 / 6061 joint.",
              "Full parts list: 66 part numbers, 144 parts in AquaSentinel_R3_Assembly_NATIVE.SLDASM."], 0.262, 0.13, 70)
    return d, "AS3-DWG-02"


def s3():
    s = 5
    d = new_drawing(props(Title="GUIDE CARRIAGE", Material="6061-T6 / UHMW-PE / 316", Weight="see design checks"), 1, s)
    el = view(d, ASM, "*Bottom", 0.085, 0.2, 1 / s)
    hide(el, keep=CARRIAGE)
    pl = projected(d, el, 0.085, 0.08)
    hide(pl, keep=CARRIAGE)
    iso = iso_of(d, el, 1 / 6)
    hide(iso, keep=CARRIAGE)
    finish(d, s, (el, pl, iso), [(el, 0.09, 0.218), (pl, None, 0.12), (iso, 0.222, 0.17)])
    print("el", dims(d, el, True, False), "plan", dims(d, pl, False, True))
    label(d, el, "ELEVATION (from port)")
    label(d, pl, "PLAN (from above)")
    label(d, iso, "ISOMETRIC (1:6)")
    rows = [("PART No.", "DESCRIPTION", "QTY", "MATERIAL"),
            ("AS3-301", "Carriage fixed half, weldment", 1, "6061-T6"),
            ("AS3-302", "Carriage gate, weldment", 1, "6061-T6"),
            ("AS3-311", "Concave guide roller", 8, "UHMW-PE"),
            ("AS3-312", "Roller axle M10 + nyloc nuts", 8, "316"),
            ("AS3-313", "Gate hinge pin D10", 1, "316"),
            ("AS3-314", "T-handle latch pin, tool-free", 2, "316"),
            ("AS3-321", "Brace struts, pair", 1, "316L tube 20x2"),
            ("AS3-902", "Bolt M10 x 70 + washer", 2, "A4-70")]
    table(d, 0.285, 0.283, rows, (18, 56, 9, 30))
    notes(d, ["Roller throat follows the pole radius + 1.5 mm running clearance: line contact on the 60.3 mm pole.",
              "Jam margin 8.62 with rollers turning (mu 0.05); 1.72 with seized rollers sliding (mu 0.25).",
              "Design roller loads 1107 N / 465 N.",
              "Hard-anodise after welding; nylon washers isolate the 316 axles from the 6061 cheeks.",
              "Gate: pull both T-pins, swing forward 100 deg, back the float off the pole. Lanyard both pins."], 0.024, 0.056, 118)
    return d, "AS3-DWG-03"


def s4():
    s = 8
    d = new_drawing(props(Title="SENSOR WELL AND CARTRIDGE", Material="PE100 / 316L / POM", Weight="cartridge 3.95 kg"), 1, s)
    el = view(d, ASM, "*Bottom", 0.07, 0.185, 1 / s)
    hide(el, keep=WELL)
    pl = projected(d, el, 0.07, 0.07)
    hide(pl, keep=WELL)
    iso = iso_of(d, el, 1 / s)
    hide(iso, keep=WELL)
    finish(d, s, (el, pl, iso), [(el, 0.07, 0.19), (pl, None, 0.07), (iso, 0.19, 0.2)])
    print("el", dims(d, el), "plan", dims(d, pl, True, False))
    label(d, el, "ELEVATION (from port)")
    label(d, pl, "PLAN (from above)")
    label(d, iso, "ISOMETRIC (1:8)")
    rows = [("PART No.", "DESCRIPTION", "QTY"),
            ("AS3-401", "Sensor well sleeve PE100 D160 SDR26", 1),
            ("AS3-402", "Hatch flange ring, quarter-turn seat", 1),
            ("AS3-403", "Sensor guard cage 316L", 1),
            ("AS3-404", "V debris deflector HDPE", 1),
            ("AS3-411", "Cartridge cap + wiper drive housing", 1),
            ("AS3-412", "Cartridge lift handle", 1),
            ("AS3-413", "Cartridge spine + wiper shaft", 1),
            ("AS3-414", "Probe holder spiders", 2),
            ("AS3-415", "Optical wiper arm + brush pads", 1),
            ("AS3-416", "Probe cables, in-well run", 1),
            ("AS3-417", "Sampler intake strainer + riser", 1),
            ("AS3-420", "Probe body, 32 x 300 envelope", 4),
            ("AS3-421..424", "ID bands: pH, EC, DO, turbidity", 4)]
    table(d, 0.29, 0.283, rows, (24, 80, 9))
    notes(d, ["Service: quarter-turn the cap and lift the cartridge by its handle; probes, wiper and intake come up together.",
              "Probe bodies are drawn as their 32 x 300 mm envelope; colour bands key each probe to its port.",
              "Probe tips sit 340 mm below the keel, inside the cage, behind the deflector and in the pole wake.",
              "Cables run inside the sleeve with a drip loop at the cap; IP68 glands only."], 0.125, 0.11, 62)
    return d, "AS3-DWG-04"


def s5():
    s = 5
    p = part("AS3-201")
    d = new_drawing(props(Title="PONTOON HULL", Material="PE, UV stab., RAL 1003", Weight="6.82 kg each (est.)"), 1, s)
    pr = view(d, p, "*Bottom", 0.15, 0.225, 1 / s)
    en = projected(d, pr, 0.315, 0.225)
    pl = projected(d, pr, 0.15, 0.148)
    iso = view(d, p, "*Isometric", 0.335, 0.135, 1 / 8, 3)
    finish(d, s, (pr, en, pl, iso))
    print("profile", dims(d, pr), "end", dims(d, en, True, False), "plan", dims(d, pl, False, True))
    label(d, pr, "PROFILE (bow at left, pole side)")
    label(d, en, "END VIEW")
    label(d, pl, "PLAN (from above)")
    label(d, iso, "ISOMETRIC (1:8)")
    notes(d, ["2 off per float. Rotomoulded PE, UV-stabilised, colour RAL 1003 signal yellow.",
              "Wall 5 mm nominal, 4 mm minimum at corners. Both hulls from one mould, rub rails on both sides.",
              "Moulded-in 316 M8 inserts (8 for the beams, 4 for the handles) and a vent plug boss; moulder to verify pull-out.",
              "Leak test at 0.1 bar before filling with closed-cell PU foam, 32 kg/m3, so a holed hull still floats.",
              "Moulded volume 55.1 L each; shell + foam 6.821 kg each (design estimate from CAD)."], 0.024, 0.085, 118)
    return d, "AS3-DWG-05"


def s6():
    s = 4
    p = part("AS3-101")
    c = part("AS3-102")
    d = new_drawing(props(Title="PIER BRACKET AND CLAMP CAP", Material="SS 316L, passivated", Weight="see design checks"), 1, s)
    el = view(d, p, "*Bottom", 0.095, 0.215, 1 / s)
    pl = projected(d, el, 0.095, 0.125)
    en = projected(d, el, 0.205, 0.215)
    iso = view(d, p, "*Isometric", 0.205, 0.125, 1 / 6, 3)
    cp = view(d, c, "*Bottom", 0.3, 0.225, 1 / s)
    ci = view(d, c, "*Isometric", 0.37, 0.225, 1 / s, 3)
    finish(d, s, (el, pl, en, iso, cp, ci))
    print("el", dims(d, el), "plan", dims(d, pl, False, True), "end", dims(d, en, True, False), "cap", dims(d, cp))
    label(d, el, "ELEVATION")
    label(d, pl, "PLAN (along the pole)")
    label(d, en, "END VIEW")
    label(d, iso, "ISOMETRIC (1:6)")
    label(d, cp, "AS3-102 CLAMP CAP")
    rows = [("PART No.", "DESCRIPTION", "QTY", "MATERIAL"),
            ("AS3-101", "Pier bracket weldment", 2, "316L 10/12 mm"),
            ("AS3-102", "Pole clamp cap", 2, "316L"),
            ("AS3-103", "Stage target plate, upper only", 1, "316L t4"),
            ("AS3-905", "Bolt M10 x 40 + washer", 4, "A4-70"),
            ("AS3-904", "Chemical anchor M12 x 130", 8, "A4 + mortar"),
            ("AS3-113/114", "Stop collar + EPDM buffer", "2+2", "316L / EPDM")]
    table(d, 0.272, 0.172, rows, (22, 52, 9, 28))
    notes(d, ["Upper and lower brackets are identical: one weld fixture, one drawing.",
              "Design reaction per bracket 430 N horizontal (1.5 m/s current + 500 N debris).",
              "Anchor embedment and edge distance to the anchor maker's data for the pier concrete grade; verify on site.",
              "TIG weld, ER316LSi filler, full fillet all round; pickle and passivate after welding.",
              "Clamp bore reamed 60.7 for the 60.3 pole; tighten M10 to 35 N.m."], 0.024, 0.07, 118)
    return d, "AS3-DWG-06"


SHEETS = {1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 6: s6}
if __name__ == "__main__":
    which = [int(a) for a in sys.argv[1:]] or list(SHEETS)
    for n in which:
        t = time.time()
        close_drawings()
        d, name = SHEETS[n]()
        print(n, save(d, name)[1], round(time.time() - t), "s", flush=True)

