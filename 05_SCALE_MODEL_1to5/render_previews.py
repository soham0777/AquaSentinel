"""
Preview renders of the AquaSentinel R3 1:5 model: a small z-buffer rasteriser (numpy + PIL) with crease-aware
smooth shading and CAD-style outlines. Reads the meshes that make_scale_model.py saved in previews/.

Usage:  python -I render_previews.py [model_dir]
Writes previews/*.png.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "src")))
from export import creased_normals  # noqa: E402  (same crease-split normals as the CAD's GLB export)

COL = {
    "yellow": (250, 184, 10), "silver": (196, 201, 206), "black": (44, 46, 50), "dark grey": (78, 80, 86),
    "light grey": (206, 208, 200), "white": (240, 240, 235), "dark blue": (30, 46, 96),
    "translucent green": (70, 215, 120), "translucent red": (230, 50, 50), "grey": (170, 170, 164),
    "concrete grey": (186, 183, 172), "rod": (170, 176, 182),
}
FONT_B = "C:/Windows/Fonts/calibrib.ttf"
FONT_R = "C:/Windows/Fonts/calibri.ttf"


def font(size, bold=False):
    try:
        return ImageFont.truetype(FONT_B if bold else FONT_R, size)
    except OSError:
        return ImageFont.load_default()


def load(npz, prefix=None):
    d = np.load(npz)
    items = {}
    for k in d.files:
        if k.startswith("ROD_"):
            continue
        parts = k.split("|")
        if prefix:
            if parts[0] != prefix:
                continue
            parts = parts[1:]
        pid, col, kind = parts
        items.setdefault((pid, col), {})[kind] = d[k]
    out = [(pid, col, v["V"], v["F"]) for (pid, col), v in items.items()]
    rod = (d["ROD_V"], d["ROD_F"]) if "ROD_V" in d.files else None
    return out, rod


def look_at(eye, target, up=(0, 0, 1)):
    eye, target = np.asarray(eye, float), np.asarray(target, float)
    f = target - eye
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return eye, r, u, f


def render(meshes, cam, W, H, fov=None, ortho_scale=None, ss=2, bg_top=(250, 251, 253), bg_bot=(222, 228, 236),
           light=(-0.35, -0.55, 0.76), outline=True):
    """meshes: list of (V, F, rgb). cam = look_at(...). Perspective if fov (deg) else orthographic (px per mm)."""
    eye, r, u, f = cam
    Ws, Hs = W * ss, H * ss
    zbuf = np.full((Hs, Ws), np.inf, np.float32)
    nbuf = np.zeros((Hs, Ws, 3), np.float32)
    cbuf = np.zeros((Hs, Ws, 3), np.float32)
    ibuf = np.full((Hs, Ws), -1, np.int32)
    focal = (Hs / 2) / math.tan(math.radians(fov) / 2) if fov else None
    for mid, (V, F, rgb) in enumerate(meshes):
        Vn, N, Fn = creased_normals(np.asarray(V, float), np.asarray(F, np.int64), 30.0)
        Vn = Vn.astype(np.float64)
        rel = Vn - eye
        xc, yc, zc = rel @ r, rel @ u, rel @ f
        if focal:
            sx, sy = Ws / 2 + xc / zc * focal, Hs / 2 - yc / zc * focal
        else:
            sx, sy = Ws / 2 + xc * ortho_scale * ss, Hs / 2 - yc * ortho_scale * ss
        Fn = Fn.astype(np.int64)
        p0, p1, p2 = Fn[:, 0], Fn[:, 1], Fn[:, 2]
        area = (sx[p1] - sx[p0]) * (sy[p2] - sy[p0]) - (sx[p2] - sx[p0]) * (sy[p1] - sy[p0])
        keep = area < -1e-9                                   # screen y points down: front faces have negative area
        if focal:
            keep &= (zc[p0] > 1) & (zc[p1] > 1) & (zc[p2] > 1)
        col = np.asarray(rgb, np.float32) / 255.0
        for t in np.flatnonzero(keep):
            i0, i1, i2 = p0[t], p1[t], p2[t]
            xs = (sx[i0], sx[i1], sx[i2])
            ys = (sy[i0], sy[i1], sy[i2])
            x0, x1 = max(int(math.floor(min(xs))), 0), min(int(math.ceil(max(xs))), Ws - 1)
            y0, y1 = max(int(math.floor(min(ys))), 0), min(int(math.ceil(max(ys))), Hs - 1)
            if x0 > x1 or y0 > y1:
                continue
            X, Y = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            a = area[t]
            w0 = ((xs[2] - xs[1]) * (Y - ys[1]) - (ys[2] - ys[1]) * (X - xs[1])) / a
            w1 = ((xs[0] - xs[2]) * (Y - ys[2]) - (ys[0] - ys[2]) * (X - xs[2])) / a
            w2 = 1.0 - w0 - w1
            inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not inside.any():
                continue
            if focal:
                iz = w0 / zc[i0] + w1 / zc[i1] + w2 / zc[i2]
                z = 1.0 / np.maximum(iz, 1e-12)
            else:
                z = w0 * zc[i0] + w1 * zc[i1] + w2 * zc[i2]
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            m = inside & (z < sub)
            if not m.any():
                continue
            sub[m] = z[m]
            n = (w0[..., None] * N[i0] + w1[..., None] * N[i1] + w2[..., None] * N[i2])
            nbuf[y0:y1 + 1, x0:x1 + 1][m] = n[m]
            cbuf[y0:y1 + 1, x0:x1 + 1][m] = col
            ibuf[y0:y1 + 1, x0:x1 + 1][m] = mid
    # shading
    hit = np.isfinite(zbuf)
    nrm = nbuf / np.maximum(np.linalg.norm(nbuf, axis=2, keepdims=True), 1e-9)
    L = np.asarray(light, float)
    L /= np.linalg.norm(L)
    L2 = np.array([0.6, 0.5, 0.25])
    L2 /= np.linalg.norm(L2)
    view = -f
    ndl = np.clip(nrm @ L, 0, 1)
    ndl2 = np.clip(nrm @ L2, 0, 1)
    hvec = (L + view) / np.linalg.norm(L + view)
    spec = np.clip(nrm @ hvec, 0, 1) ** 40
    shade = 0.36 + 0.58 * ndl[..., None] + 0.16 * ndl2[..., None]
    img = cbuf * shade + 0.20 * spec[..., None]
    # background gradient
    t = np.linspace(0, 1, Hs)[:, None, None]
    bg = (np.asarray(bg_top, np.float32) * (1 - t) + np.asarray(bg_bot, np.float32) * t) / 255.0
    out = np.where(hit[..., None], img, np.broadcast_to(bg, img.shape))
    if outline:
        zf = np.where(hit, zbuf, np.nan)
        edge = np.zeros(hit.shape, bool)
        for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
            a_ = np.roll(np.roll(ibuf, dy, 0), dx, 1)
            edge |= (a_ != ibuf)
            za = np.roll(np.roll(zf, dy, 0), dx, 1)
            with np.errstate(invalid="ignore"):
                if focal:
                    rel = np.abs(za - zf) / np.maximum(np.minimum(za, zf), 1e-6) > 0.012
                else:
                    rel = np.abs(za - zf) > 0.45
            edge |= np.where(np.isnan(za) | np.isnan(zf), True, rel)
            na = np.roll(np.roll(nrm, dy, 0), dx, 1)
            edge |= (np.einsum("ijk,ijk->ij", na, nrm) < 0.55) & hit
        edge &= hit | np.roll(hit, 1, 0) | np.roll(hit, 1, 1)
        edge[0, :] = edge[:, 0] = edge[:, -1] = False      # np.roll wraps around: ignore the frame border
        out = np.where(edge[..., None], out * 0.35, out)
    im = Image.fromarray(np.clip(out * 255, 0, 255).astype(np.uint8))
    return im.resize((W, H), Image.LANCZOS) if ss > 1 else im


def caption(im, title, lines, foot=None):
    d = ImageDraw.Draw(im)
    d.text((40, 30), title, font=font(46, True), fill=(18, 43, 66))
    y = 88
    for ln in lines:
        d.text((42, y), ln, font=font(28), fill=(60, 72, 84))
        y += 36
    if foot:
        d.text((40, im.height - 50), foot, font=font(24), fill=(100, 110, 120))
    return im


def plate_view(items, bed, W, H, title, sub):
    """top view of a print plate with the H2D bed outline and part ids"""
    allv = np.concatenate([v for _, _, v, _ in items])
    cx, cy = bed[0] / 2, bed[1] / 2
    scale = min((W - 120) / bed[0], (H - 260) / bed[1])
    eye = (cx, cy - 1e-4, 2000.0)
    cam = look_at(eye, (cx, cy, 0.0), up=(0, 1, 0))
    meshes = [(v, f, COL[c]) for _, c, v, f in items]
    im = render(meshes, cam, W, H - 140, ortho_scale=scale, light=(-0.3, -0.4, 0.86), bg_top=(246, 247, 249),
                bg_bot=(238, 240, 244))
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    canvas.paste(im, (0, 140))
    d = ImageDraw.Draw(canvas)
    ox, oy = W / 2 - cx * scale, 140 + (H - 140) / 2 + cy * scale
    d.rectangle([ox, oy - bed[1] * scale, ox + bed[0] * scale, oy], outline=(0, 86, 134), width=3)
    d.text((ox + 6, oy - bed[1] * scale - 30), f"H2D plate area for both nozzles: {bed[0]:.0f} x {bed[1]:.0f} mm",
           font=font(22), fill=(0, 86, 134))
    for pid, _, v, _ in items:
        c = (v[:, 0].min() + v[:, 0].max()) / 2, (v[:, 1].min() + v[:, 1].max()) / 2
        px, py = ox + c[0] * scale, oy - c[1] * scale
        tw = d.textlength(pid, font=font(24, True))
        d.rounded_rectangle([px - tw / 2 - 6, py - 15, px + tw / 2 + 6, py + 15], radius=8, fill=(255, 255, 255),
                            outline=(218, 9, 28), width=2)
        d.text((px - tw / 2, py - 13), pid, font=font(24, True), fill=(218, 9, 28))
    d.text((40, 28), title, font=font(44, True), fill=(18, 43, 66))
    d.text((42, 84), sub, font=font(26), fill=(60, 72, 84))
    del allv
    return canvas


def main(model_dir):
    pv = os.path.join(model_dir, "previews")
    asm, rod = load(os.path.join(pv, "_asm_meshes.npz"))
    meshes = [(v, f, COL[c]) for _, c, v, f in asm] + ([(rod[0], rod[1], COL["rod"])] if rod else [])
    W, H = 1800, 1350

    print("hero view ...")
    tgt = np.array([40.0, 0.0, 168.0])
    d = np.array([0.62, 0.60, 0.50])
    cam = look_at(tgt + 830 * d / np.linalg.norm(d), tgt)
    im = render(meshes, cam, W, H, fov=30)
    caption(im, "AquaSentinel R3  \u00b7  1:5 printed scale model",
            ["Float on its pole, held off the pier face by two brackets (display stand)",
             "Hand travel on the stand: 65 mm  (the real 2.0 m range would be 400 mm at 1:5)",
             "Rendered from the print files  ·  float at mid-travel  ·  colours = suggested filaments"])
    im.save(os.path.join(pv, "01_assembled_starboard_aft.png"))

    print("bow view ...")
    d = np.array([-0.55, -0.70, 0.42])
    tgt = np.array([18.0, 0.0, 182.0])
    cam = look_at(tgt + 790 * d / np.linalg.norm(d), tgt)
    im = render(meshes, cam, W, H, fov=30)
    caption(im, "Pier side: brackets, 12 mm pole, bow guide carriage",
            ["The bracket arms pass between the hull bows; the carriage rides the pole on 8 rollers",
             "Stop collars set the lowest and highest positions; the upper bracket carries the stage target plate"])
    im.save(os.path.join(pv, "02_assembled_port_bow.png"))

    print("float close-up ...")
    fl = [(v, f, COL[c]) for pid, c, v, f in asm if pid.startswith("F")]
    d = np.array([0.30, -0.80, 0.52])
    tgt = np.array([82.0, 0.0, 168.0])
    cam = look_at(tgt + 600 * d / np.linalg.norm(d), tgt)
    im = render(fl, cam, W, H, fov=30)
    caption(im, "The float (F01 to F15)",
            ["Twin yellow hulls, deck, solar canopy, control pod, autosampler, beacon, LTE antenna",
             "Sensor well with guard cage below the deck; the probe cartridge lifts out by its handle"])
    im.save(os.path.join(pv, "03_float_port_side.png"))

    print("plates ...")
    bed = (300.0, 320.0)
    fp, _ = load(os.path.join(pv, "_plate_meshes.npz"), "FLOAT")
    plate_view(fp, bed, 1500, 1700, "Plate 1  \u00b7  AquaSentinel_R3_1to5_FLOAT.stl",
               "18 float parts in print orientation  \u00b7  no supports  \u00b7  PLA 0.2 mm").save(
        os.path.join(pv, "04_plate1_float.png"))
    sp, _ = load(os.path.join(pv, "_plate_meshes.npz"), "STAND")
    plate_view(sp, bed, 1500, 1700, "Plate 2  \u00b7  AquaSentinel_R3_1to5_STAND.stl",
               "Display stand: base, pier column, 2 brackets, 2 stop collars, pole cap  \u00b7  no supports").save(
        os.path.join(pv, "05_plate2_stand.png"))
    print("done")


KEEL_VIEW, TRAVEL = 113.3, 65.0      # float position stored in _asm_meshes.npz (mid-travel) and the hand travel

EXPLODE = {"F01": (0, -34, -10), "F02": (0, 34, -10), "F03": (0, 0, 34), "F04": (-46, 0, 40), "F05": (0, 0, -62),
           "F06": (-22, 0, -70), "F07": (0, 0, 150), "F08": (0, 0, 150), "F09": (0, 0, 66), "F10": (0, 0, 80),
           "F11": (0, 0, 118), "F12": (0, 0, 64), "F13": (0, 0, 84), "F15a": (0, -10, 26), "F15b": (0, 10, 26),
           "F15c": (0, -10, 26), "F15d": (0, 10, 26)}
NAMES = {"F01": "hull", "F02": "hull", "F03": "frame + deck", "F04": "guide carriage", "F05": "well + cage",
         "F06": "deflector", "F07": "cartridge cap", "F08": "probe cluster", "F09": "control pod", "F10": "autosampler",
         "F11": "PV canopy", "F12": "beacon mast", "F13": "lens", "F15a": "handles"}


def project(p, cam, W, H, fov):
    eye, r, u, f = cam
    rel = np.asarray(p, float) - eye
    focal = (H / 2) / math.tan(math.radians(fov) / 2)
    return W / 2 + (rel @ r) / (rel @ f) * focal, H / 2 - (rel @ u) / (rel @ f) * focal


def exploded(model_dir, asm):
    pv = os.path.join(model_dir, "previews")
    W, H, fov = 1800, 1500, 30
    items, labels = [], []
    for pid, c, v, f in asm:
        if not pid.startswith("F") or pid not in EXPLODE:
            continue
        off = np.asarray(EXPLODE[pid], float)
        vv = v + off
        items.append((vv, f, COL[c]))
        if pid in NAMES:
            labels.append((pid, NAMES[pid], (vv.min(axis=0) + vv.max(axis=0)) / 2))
    tgt = np.array([75.0, 0.0, 205.0])
    d = np.array([0.52, -0.74, 0.43])
    cam = look_at(tgt + 900 * d / np.linalg.norm(d), tgt)
    im = render(items, cam, W, H, fov=fov)
    dr = ImageDraw.Draw(im)
    boxes = []
    for pid, name, c in labels:
        x, y = project(c, cam, W, H, fov)
        txt = f"{pid}  {name}" if not pid.startswith("F15") else "F15  grab handles (4)"
        tw = dr.textlength(txt, font=font(24, True))
        boxes.append([x, y, x, max(y, 190.0), tw, txt])
    for _ in range(60):                                       # push overlapping labels apart (vertically)
        moved_any = False
        boxes.sort(key=lambda b: b[3])
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i], boxes[j]
                if abs(a[2] - b[2]) < (a[4] + b[4]) / 2 + 20 and abs(a[3] - b[3]) < 38:
                    b[3] = a[3] + 38
                    moved_any = True
        if not moved_any:
            break
    for x0, y0, x, y, tw, txt in boxes:
        dr.ellipse([x0 - 5, y0 - 5, x0 + 5, y0 + 5], fill=(218, 9, 28))
        if abs(y - y0) > 4:
            dr.line([(x0, y0), (x, y)], fill=(218, 9, 28), width=2)
        dr.rounded_rectangle([x - tw / 2 - 8, y - 16, x + tw / 2 + 8, y + 16], radius=9, fill=(255, 255, 255),
                             outline=(218, 9, 28), width=2)
        dr.text((x - tw / 2, y - 14), txt, font=font(24, True), fill=(218, 9, 28))
    caption(im, "Assembly: how the float parts go together",
            ["Hulls take the frame in 0.8 mm pockets; carriage hangs on the deck edge; well drops through the deck hatch",
             "Probe cluster is glued into the cartridge cap, then the cartridge lifts in and out of the well"])
    im.save(os.path.join(pv, "06_exploded_float.png"))


def heave(model_dir, asm, rod):
    """port-side elevations at the lowest and highest stop: the river lifts the float along the pole"""
    pv = os.path.join(model_dir, "previews")
    W, H = 900, 1200
    panels = []
    for tag, dz in (("lowest stop (river low)", -TRAVEL / 2), ("highest stop (river high)", TRAVEL / 2)):
        ms = []
        for pid, c, v, f in asm:
            vv = v + np.array([0, 0, dz]) if pid.startswith("F") else v
            ms.append((vv, f, COL[c]))
        ms.append((rod[0], rod[1], COL["rod"]))
        cam = look_at((25.0, -2000.0, 170.0), (25.0, 0.0, 170.0))
        im = render(ms, cam, W, H, ortho_scale=2.55, light=(-0.35, -0.75, 0.55))
        d = ImageDraw.Draw(im)
        d.text((30, 26), tag, font=font(34, True), fill=(18, 43, 66))
        panels.append(im)
    canvas = Image.new("RGB", (2 * W, H + 110), (255, 255, 255))
    for i, im in enumerate(panels):
        canvas.paste(im, (i * W, 110))
    d = ImageDraw.Draw(canvas)
    d.text((30, 18), "Passive heave: the float slides up the pole with the water, no motor", font=font(40, True),
           fill=(18, 43, 66))
    d.text((32, 68), f"Model travel {TRAVEL:.0f} mm between the stop collars (design: 2.0 m stage range = 400 mm at 1:5)",
           font=font(26), fill=(60, 72, 84))
    d.line([(W, 120), (W, H + 100)], fill=(200, 205, 212), width=2)
    canvas.save(os.path.join(pv, "07_heave_low_high.png"))


def extras(model_dir):
    pv = os.path.join(model_dir, "previews")
    asm, rod = load(os.path.join(pv, "_asm_meshes.npz"))
    print("exploded view ...")
    exploded(model_dir, asm)
    print("heave view ...")
    heave(model_dir, asm, rod)


def slide_image(model_dir):
    """caption-free hero view for the deck's backup slide (the slide itself carries the 'render' label)"""
    pv = os.path.join(model_dir, "previews")
    asm, rod = load(os.path.join(pv, "_asm_meshes.npz"))
    meshes = [(v, f, COL[c]) for _, c, v, f in asm] + ([(rod[0], rod[1], COL["rod"])] if rod else [])
    tgt = np.array([40.0, 0.0, 146.0])
    d = np.array([0.62, 0.60, 0.50])
    cam = look_at(tgt + 790 * d / np.linalg.norm(d), tgt)
    im = render(meshes, cam, 1500, 1200, fov=30, bg_top=(255, 255, 255), bg_bot=(234, 243, 248))
    im.save(os.path.join(pv, "08_slide_render.png"))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    md = args[0] if args else HERE
    if "--slide-only" in sys.argv:
        slide_image(md)
        sys.exit(0)
    if "--extras-only" not in sys.argv:
        main(md)
    extras(md)
    slide_image(md)
