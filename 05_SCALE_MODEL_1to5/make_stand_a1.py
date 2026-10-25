"""Stand plates for a Bambu Lab A1 (256 x 256 x 256 mm bed), so the stand can print while the H2D prints the float.

The H2D stand plate (AquaSentinel_R3_1to5_STAND.stl) is 236 x 304 mm, and two of its parts are longer than the A1's bed in
any orientation: the display base S01 (260 mm) and the pier column S02 (304 mm). This script works directly on the part
STLs in parts/ (plain numpy, no CAD kernel):
  - S01: 5 mm is cut off each plain end, so the base is 250 mm long. The window, rod socket, column mortise and engraving
    are untouched, and each cut end is closed with a flat cap;
  - S02: the column is cut in two at mid-height, between the two brackets' anchor pins, and both cut faces are capped;
  - S07: a 40 x 50 x 2.4 mm splice plate, glued across the column joint on its back face (the face that lies on the bed).
Plates:
  AquaSentinel_R3_1to5_STAND_A1_plate1.stl   base, both brackets, both stop collars and the pole cap (inside the window)
  AquaSentinel_R3_1to5_STAND_A1_plate2.stl   the two column halves and the splice plate
The H2D files are not touched.

Usage (from this folder):  python -I make_stand_a1.py
"""
import json
import os
import struct
import sys

import numpy as np
from scipy.spatial import ConvexHull

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

A1_BED = 256.0
TRIM = 5.0                                 # off each end of the 260 mm base
SPLICE = (50.0, 40.0, 2.4)                 # splice plate: across the column, along it, thickness
WINDOW = (179.0, 85.0, 61.0, 50.0)         # trimmed base, print frame: window centre x, y and half sizes (122 x 100)


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
    code, rcode = e[:, 0] * n + e[:, 1], e[:, 1] * n + e[:, 0]
    _, cnt = np.unique(code, return_counts=True)
    bad = int((cnt > 1).sum()) + int((~np.isin(rcode, code)).sum())
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    vol = float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)
    return dict(triangles=int(len(F)), open_or_bad_edges=bad, volume_cm3=round(vol / 1000, 2), watertight=bad == 0 and vol > 0)


def read_stl(path):
    data = open(path, "rb").read()
    n = struct.unpack("<I", data[80:84])[0]
    rec = np.frombuffer(data[84:84 + 50 * n], dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    V = rec["v"].reshape(-1, 3).astype(float)
    return weld(V, np.arange(len(V)).reshape(-1, 3))


def write_stl(path, meshes, name):
    T = np.concatenate([V[F] for V, F in meshes]).astype(np.float64)
    nrm = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    ln = np.linalg.norm(nrm, axis=1, keepdims=True)
    nrm = np.divide(nrm, ln, out=np.zeros_like(nrm), where=ln > 0)
    rec = np.zeros(len(T), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = nrm, T
    with open(path, "wb") as fh:
        fh.write((name + " - binary STL, mm").encode("ascii", "replace")[:80].ljust(80, b" "))
        fh.write(np.uint32(len(T)).tobytes())
        fh.write(rec.tobytes())
    return len(T)


def plane_cut(V, F, axis, c, keep_below):
    """keep the side of the plane V[axis] = c (below or above) and close the cut with a flat cap.
    The cut section must be one convex outline (checked); returns (V, F, cap area in mm2)."""
    sgn = 1.0 if keep_below else -1.0
    d = sgn * (V[:, axis] - c)
    if np.abs(d).min() < 1e-6:
        raise ValueError("a vertex lies on the cut plane: move the plane slightly")
    inside = d < 0
    pts, edge_pt, faces, ring = list(V), {}, [], set()

    def ip(i, j):
        key = (i, j) if i < j else (j, i)
        if key not in edge_pt:
            a, b = key
            t = d[a] / (d[a] - d[b])
            edge_pt[key] = len(pts)
            pts.append(V[a] + t * (V[b] - V[a]))
        return edge_pt[key]

    for f in F:
        ins = inside[f]
        k = int(ins.sum())
        if k == 3:
            faces.append(tuple(f))
        elif k == 1:                                   # one vertex kept: a triangle
            r = int(np.argmax(ins))
            a, b, cc = f[r], f[(r + 1) % 3], f[(r + 2) % 3]
            p, q = ip(a, b), ip(cc, a)
            faces.append((a, p, q))
            ring.update((p, q))
        elif k == 2:                                   # two vertices kept: a quad, as two triangles
            r = int(np.argmin(ins))
            cc, a, b = f[r], f[(r + 1) % 3], f[(r + 2) % 3]
            p, q = ip(b, cc), ip(cc, a)
            faces += [(a, b, p), (a, p, q)]
            ring.update((p, q))
    P = np.array(pts)
    idx = np.array(sorted(ring))
    other = [ax for ax in range(3) if ax != axis]
    P2 = P[idx][:, other]
    cen = P2.mean(axis=0)
    order = idx[np.argsort(np.arctan2(P2[:, 1] - cen[1], P2[:, 0] - cen[0]))]
    poly = P[order][:, other]
    area = 0.5 * abs(np.dot(poly[:, 0], np.roll(poly[:, 1], -1)) - np.dot(poly[:, 1], np.roll(poly[:, 0], -1)))
    hull = ConvexHull(P2).volume                       # 2-D hull "volume" is its area
    if abs(area - hull) > 1e-3 * hull:
        raise ValueError(f"cut section is not one convex outline (area {area:.2f} vs hull {hull:.2f})")
    ci = len(P)
    P = np.vstack([P, P[idx].mean(axis=0)])
    cap = [(ci, order[k], order[(k + 1) % len(order)]) for k in range(len(order))]
    nz = np.cross(P[cap[0][1]] - P[ci], P[cap[0][2]] - P[ci])[axis]
    if np.sign(nz) != sgn:                              # cap normal must face the removed side
        cap = [(a, cc, b) for a, b, cc in cap]
    F2 = np.array(faces + cap, dtype=np.int64)
    used = np.unique(F2)
    remap = np.full(len(P), -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    V3, F3 = weld(P[used], remap[F2])
    return V3, F3, round(float(area), 1)


def box_mesh(sx, sy, sz):
    V = np.array([[x, y, z] for z in (0, sz) for y in (0, sy) for x in (0, sx)], dtype=float)
    F = np.array([[0, 2, 1], [1, 2, 3], [4, 5, 6], [5, 7, 6], [0, 1, 4], [1, 5, 4],
                  [2, 6, 3], [3, 6, 7], [0, 4, 2], [2, 4, 6], [1, 3, 5], [3, 7, 5]], dtype=np.int64)
    return V, F


def drop(V):
    return V - V.min(axis=0)


def place(V, x, y):
    return V + np.array([x, y, 0.0])


def preview(items, path, title, sub):
    """top view of an A1 plate with the bed outline, using render_previews.py's renderer"""
    import render_previews as RP
    from PIL import Image, ImageDraw
    W, H = 1400, 1240
    cx = cy = A1_BED / 2
    scale = min((W - 120) / A1_BED, (H - 260) / A1_BED)
    cam = RP.look_at((cx, cy - 1e-4, 2000.0), (cx, cy, 0.0), up=(0, 1, 0))
    im = RP.render([(v, f, RP.COL[c]) for _, c, v, f in items], cam, W, H - 140, ortho_scale=scale,
                   light=(-0.3, -0.4, 0.86), bg_top=(246, 247, 249), bg_bot=(238, 240, 244))
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    canvas.paste(im, (0, 140))
    d = ImageDraw.Draw(canvas)
    ox, oy = W / 2 - cx * scale, 140 + (H - 140) / 2 + cy * scale
    d.rectangle([ox, oy - A1_BED * scale, ox + A1_BED * scale, oy], outline=(0, 86, 134), width=3)
    d.text((ox + 6, oy - A1_BED * scale - 30), "Bambu Lab A1 bed: 256 x 256 mm", font=RP.font(22), fill=(0, 86, 134))
    for pid, _, v, _ in items:
        px = ox + (v[:, 0].min() + v[:, 0].max()) / 2 * scale
        py = oy - (v[:, 1].min() + v[:, 1].max()) / 2 * scale
        tw = d.textlength(pid, font=RP.font(24, True))
        d.rounded_rectangle([px - tw / 2 - 6, py - 15, px + tw / 2 + 6, py + 15], radius=8, fill=(255, 255, 255),
                            outline=(218, 9, 28), width=2)
        d.text((px - tw / 2, py - 13), pid, font=RP.font(24, True), fill=(218, 9, 28))
    d.text((40, 28), title, font=RP.font(44, True), fill=(18, 43, 66))
    d.text((42, 84), sub, font=RP.font(26), fill=(60, 72, 84))
    canvas.save(path)


def main():
    part = lambda f: read_stl(os.path.join(HERE, "parts", f + ".stl"))
    report = dict(printer="Bambu Lab A1, 256 x 256 x 256 mm", parts={}, plates={})

    # S01: trim 5 mm off each end (print frame x 0..260; the mortise starts at x 12.8, the window ends at x 245)
    V, F = part("S01_display_base")
    L = float(V[:, 0].max())
    V, F, cap1 = plane_cut(V, F, 0, TRIM + 0.0013, keep_below=False)
    V, F, cap2 = plane_cut(V, F, 0, L - TRIM - 0.0013, keep_below=True)
    base = (drop(V), F)
    # S02: cut at mid-length (print frame y 0..304.2; the anchor pins sit at 84-108 mm from each end)
    V, F = part("S02_pier_column")
    ymax = float(V[:, 1].max())
    mid = ymax / 2 + 0.0017
    a_V, a_F, cap3 = plane_cut(V, F, 1, mid, keep_below=True)
    b_V, b_F, cap4 = plane_cut(V, F, 1, mid, keep_below=False)
    # the column's bottom end carries the tenon, which is narrower (48 mm) than the column (60 mm)
    width_at = lambda y0: float(np.ptp(V[np.abs(V[:, 1] - y0) < 1.0][:, 0]))
    tenon_at_high_y = width_at(ymax) < width_at(0.0)
    bottom, top = ((b_V, b_F), (a_V, a_F)) if tenon_at_high_y else ((a_V, a_F), (b_V, b_F))
    lower, upper = (drop(bottom[0]), bottom[1]), (drop(top[0]), top[1])
    splice = box_mesh(*SPLICE)
    report["cut_caps_mm2"] = dict(base_ends=[cap1, cap2], column_joint=[cap3, cap4])

    parts = {"S01": ("S01_display_base_A1_250mm", base, "grey"),
             "S02a": ("S02a_pier_column_bottom_half_A1", lower, "concrete grey"),
             "S02b": ("S02b_pier_column_top_half_A1", upper, "concrete grey"),
             "S07": ("S07_column_splice_plate_A1", splice, "concrete grey")}
    for pid, f in (("S03", "S03_pier_bracket_lower"), ("S04", "S04_pier_bracket_upper"), ("S05a", "S05a_stop_collar_lower"),
                   ("S05b", "S05b_stop_collar_upper"), ("S06", "S06_pole_cap")):
        parts[pid] = (f, part(f), "silver" if pid in ("S03", "S04") else "dark grey")
    for pid, (fname, (V, F), _) in parts.items():
        report["parts"][pid] = dict(file=f"parts/{fname}.stl", size_mm=[round(float(s), 1) for s in V.max(axis=0)], **mesh_check(V, F))
        if fname.endswith("_A1") or fname.endswith("_A1_250mm"):
            write_stl(os.path.join(HERE, "parts", fname + ".stl"), [(V, F)], f"AquaSentinel R3 1:5 {pid} for Bambu A1")

    # plate 1: base centred; the small parts stand inside its window, as on the H2D plate
    bV, bF = parts["S01"][1]
    bx, by = (A1_BED - bV[:, 0].max()) / 2, (A1_BED - bV[:, 1].max()) / 2
    wx, wy = bx + WINDOW[0], by + WINDOW[1]
    spots = {"S03": (-24.0, -20.0), "S04": (24.0, -20.0), "S05a": (-30.0, 30.0), "S05b": (0.0, 30.0), "S06": (30.0, 30.0)}
    plate1 = [("S01", "grey", place(bV, bx, by), bF)]
    inside_window = {}
    for pid, (dx, dy) in spots.items():
        V, F = parts[pid][1]
        w, h = V[:, 0].max(), V[:, 1].max()
        Vp = place(V, wx + dx - w / 2, wy + dy - h / 2)
        plate1.append((pid, parts[pid][2], Vp, F))
        inside_window[pid] = bool(Vp[:, 0].min() > wx - WINDOW[2] + 2 and Vp[:, 0].max() < wx + WINDOW[2] - 2
                                  and Vp[:, 1].min() > wy - WINDOW[3] + 2 and Vp[:, 1].max() < wy + WINDOW[3] - 2)
    # plate 2: the two column halves and the splice plate, side by side
    gap = 12.0
    (lV, lF), (uV, uF), (sV, sF) = lower, upper, splice
    x0 = (A1_BED - (lV[:, 0].max() + uV[:, 0].max() + sV[:, 0].max() + 2 * gap)) / 2
    plate2 = [("S02a", "concrete grey", place(lV, x0, (A1_BED - lV[:, 1].max()) / 2), lF)]
    x1 = x0 + lV[:, 0].max() + gap
    plate2.append(("S02b", "concrete grey", place(uV, x1, (A1_BED - uV[:, 1].max()) / 2), uF))
    x2 = x1 + uV[:, 0].max() + gap
    plate2.append(("S07", "dark grey", place(sV, x2, (A1_BED - sV[:, 1].max()) / 2), sF))

    for name, items, title, sub in (
            ("AquaSentinel_R3_1to5_STAND_A1_plate1.stl", plate1, "Stand for the A1: plate 1 of 2",
             "Base (trimmed to 250 mm) with the brackets, stop collars and pole cap inside its window"),
            ("AquaSentinel_R3_1to5_STAND_A1_plate2.stl", plate2, "Stand for the A1: plate 2 of 2",
             "Pier column in two halves + splice plate: glue the halves, then the plate across the joint on the back")):
        allV = np.concatenate([v for _, _, v, _ in items])
        lo, hi = allV.min(axis=0), allV.max(axis=0)
        n = write_stl(os.path.join(HERE, name), [(v, f) for _, _, v, f in items], "AquaSentinel R3 1:5 stand for Bambu A1")
        boxes = [(p, v.min(0)[:2], v.max(0)[:2]) for p, _, v, _ in items if p != "S01"]
        clash = [(a[0], b[0]) for i, a in enumerate(boxes) for b in boxes[i + 1:]
                 if np.all(a[1] < b[2] - 2.0) and np.all(b[1] < a[2] - 2.0)]
        report["plates"][name] = dict(triangles=n, footprint_mm=[round(float(v), 1) for v in hi - lo],
                                      xy_from=[round(float(v), 1) for v in lo[:2]], xy_to=[round(float(v), 1) for v in hi[:2]],
                                      fits_a1=bool(lo[0] >= 0 and lo[1] >= 0 and hi[0] <= A1_BED and hi[1] <= A1_BED and hi[2] <= A1_BED),
                                      parts_closer_than_2mm=clash)
        preview(items, os.path.join(HERE, "previews", name.replace("AquaSentinel_R3_1to5_", "").replace(".stl", ".png")), title, sub)
    report["plates"]["AquaSentinel_R3_1to5_STAND_A1_plate1.stl"]["small_parts_inside_window"] = inside_window
    with open(os.path.join(HERE, "build_report_A1.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, indent=1)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
