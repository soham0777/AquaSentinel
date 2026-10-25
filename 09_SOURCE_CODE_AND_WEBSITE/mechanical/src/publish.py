"""Final packaging: motion-study composite, assembly GIF, standalone viewer with the model embedded.
python src/publish.py
"""
import base64
import glob
import json
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
C = json.load(open(os.path.join(ROOT, "checks", "design_checks.json"), encoding="utf-8"))


def font(size, bold=False):
    for name in (("segoeuib.ttf" if bold else "segoeui.ttf"), ("arialbd.ttf" if bold else "arial.ttf")):
        try:
            return ImageFont.truetype(os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", name), size)
        except OSError:
            continue
    return ImageFont.load_default()


def motion_triptych():
    names = [("motion_low.png", "LOW WATER", "stage 0.00 m"), ("motion_mid.png", "NORMAL", "stage 1.00 m"),
             ("motion_high.png", "FLOOD", "stage 2.00 m")]
    ims = [Image.open(os.path.join(ROOT, "renders", n)).convert("RGB") for n, _, _ in names]
    w, h = ims[0].size
    cw = int(w * 0.62)
    x0 = int(w * 0.20)
    pad, head, foot = 24, 150, 110
    W = 3 * cw + 4 * pad
    H = h + head + foot
    out = Image.new("RGB", (W, H), (246, 248, 250))
    d = ImageDraw.Draw(out)
    d.text((pad, 28), "Motion study - the float follows the river on the guide pole", font=font(54, True), fill=(19, 32, 43))
    d.text((pad, 96), f"Same camera, three water levels. Draft stays {C['hydrostatics']['draft_mm']:.0f} mm at every level; "
                      "no motor, no GPS, no station-keeping energy.", font=font(32), fill=(75, 91, 104))
    for i, (im, (_, t, sub)) in enumerate(zip(ims, names)):
        crop = im.crop((x0, 0, x0 + cw, h))
        xo = pad + i * (cw + pad)
        out.paste(crop, (xo, head))
        d.rectangle([xo, head, xo + 330, head + 92], fill=(255, 255, 255))
        d.text((xo + 18, head + 8), t, font=font(40, True), fill=(11, 110, 153))
        d.text((xo + 18, head + 54), sub, font=font(30), fill=(19, 32, 43))
    d.text((pad, H - foot + 28), "Design estimate from CAD geometry (src/build.py). Stage range 2.0 m is a site ASSUMPTION - set it from the gauge record.",
           font=font(28), fill=(138, 59, 18))
    out.save(os.path.join(ROOT, "renders", "12_motion_study_low_normal_flood.png"), optimize=True)
    print("triptych saved")


def assembly_gif(max_seconds=48, width=560):
    frames = sorted(glob.glob(os.path.join(ROOT, "animation", "gif_frames", "*.jpg")))
    if not frames:
        print("no gif frames")
        return
    n = min(len(frames), int(max_seconds * 10))
    seq = []
    for f in frames[:n]:
        im = Image.open(f).convert("RGB")
        im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
        seq.append(im.quantize(colors=160, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
    out = os.path.join(ROOT, "animation", "AquaSentinel_R3_Assembly_Sequence.gif")
    seq[0].save(out, save_all=True, append_images=seq[1:], duration=100, loop=0, optimize=True)
    print("gif", len(seq), "frames", round(os.path.getsize(out) / 1e6, 1), "MB")


def standalone_viewer():
    tpl = open(os.path.join(ROOT, "viewer", "template.html"), encoding="utf-8").read()
    glb = open(os.path.join(ROOT, "cad", "assembly", "AquaSentinel_R3.glb"), "rb").read()
    html = tpl.replace("/*GLB_BASE64*/", base64.b64encode(glb).decode("ascii"))
    out = os.path.join(ROOT, "AquaSentinel_R3_Viewer.html")
    open(out, "w", encoding="utf-8").write(html)
    print("viewer", round(os.path.getsize(out) / 1e6, 1), "MB")


if __name__ == "__main__":
    import sys
    what = set(sys.argv[1:]) or {"triptych", "gif", "viewer"}
    if "triptych" in what:
        motion_triptych()
    if "gif" in what:
        assembly_gif()
    if "viewer" in what:
        standalone_viewer()
