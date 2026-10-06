"""
Minimal drafting kit for A3 engineering sheets (matplotlib, paper units = mm).
First-angle projection, ISO 5457 border, ISO 7200-style title block.
"""
import math
import datetime
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyArrowPatch
from PIL import Image

A3 = (420.0, 297.0)
LW_THIN, LW_MED, LW_THICK = 0.25, 0.4, 0.7
INK = "#15191d"
DIM = "#1f2a33"
BLUE = "#0b6e99"
TXT = 2.6          # mm text height for dimensions


def pt(mm):  # mm text height -> points
    return mm / 0.3528 * 0.72 / 0.72


class Sheet:
    def __init__(self, number, title, scale_note, material="See parts list", sheet="1/1", dpi=150):
        self.fig = plt.figure(figsize=(A3[0] / 25.4, A3[1] / 25.4), dpi=dpi)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, A3[0])
        self.ax.set_ylim(0, A3[1])
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.dpi = dpi
        self.number, self.title, self.scale_note, self.material, self.sheet = number, title, scale_note, material, sheet
        self._frame()

    # ------------------------------------------------------------------ frame
    def _frame(self):
        a = self.ax
        a.add_patch(Rectangle((0, 0), A3[0], A3[1], fill=True, color="white", zorder=-10))
        a.add_patch(Rectangle((20, 10), A3[0] - 30, A3[1] - 20, fill=False, lw=LW_THICK * 1.4, ec=INK))
        for i in range(8):  # zone marks
            x = 20 + (A3[0] - 30) * (i + 0.5) / 8
            a.text(x, A3[1] - 7, str(i + 1), ha="center", va="center", fontsize=6, color=INK)
            a.text(x, 5.5, str(i + 1), ha="center", va="center", fontsize=6, color=INK)
        for i, ch in enumerate("ABCDEF"):
            y = A3[1] - 10 - (A3[1] - 20) * (i + 0.5) / 6
            a.text(15, y, ch, ha="center", va="center", fontsize=6, color=INK)
            a.text(A3[0] - 5, y, ch, ha="center", va="center", fontsize=6, color=INK)
        # title block 180 x 52 at bottom right
        x0, y0, w, h = A3[0] - 10 - 180, 10, 180, 52
        a.add_patch(Rectangle((x0, y0), w, h, fill=True, fc="white", ec=INK, lw=LW_THICK, zorder=5))
        rows = [(y0 + 40, 12), (y0 + 26, 14), (y0 + 13, 13), (y0, 13)]
        for yy, hh in rows[1:]:
            a.plot([x0, x0 + w], [yy + hh, yy + hh], color=INK, lw=LW_THIN, zorder=6)
        a.plot([x0 + 110, x0 + 110], [y0, y0 + 40], color=INK, lw=LW_THIN, zorder=6)
        a.plot([x0 + 145, x0 + 145], [y0, y0 + 26], color=INK, lw=LW_THIN, zorder=6)
        a.text(x0 + 3, y0 + 47.5, "AquaRight  |  AquaSentinel R3", fontsize=9.5, weight="bold", color=INK, va="center", zorder=7)
        a.text(x0 + w - 3, y0 + 47.5, "AAKRUTI 2026 - Robotics", fontsize=7, color=BLUE, ha="right", va="center", zorder=7)
        a.text(x0 + 3, y0 + 43.2, "Team Sanjivani Hero's Journey (AG26-1500$41)  |  Sanjivani University, Kopargaon",
               fontsize=5.6, color="#4b5b68", va="center", zorder=7)
        a.text(x0 + 3, y0 + 33, self.title, fontsize=9, weight="bold", color=INK, va="center", zorder=7)
        a.text(x0 + 113, y0 + 36.5, "DRAWING No.", fontsize=4.6, color="#4b5b68", zorder=7)
        a.text(x0 + 113, y0 + 30.0, self.number, fontsize=8.5, weight="bold", color=INK, zorder=7)
        a.text(x0 + 3, y0 + 22.0, "MATERIAL", fontsize=4.6, color="#4b5b68", zorder=7)
        a.text(x0 + 3, y0 + 16.5, self.material, fontsize=6.2, color=INK, zorder=7)
        a.text(x0 + 113, y0 + 22.0, "SCALE", fontsize=4.6, color="#4b5b68", zorder=7)
        a.text(x0 + 113, y0 + 16.5, self.scale_note, fontsize=6.6, color=INK, zorder=7)
        a.text(x0 + 148, y0 + 22.0, "SHEET / REV", fontsize=4.6, color="#4b5b68", zorder=7)
        a.text(x0 + 148, y0 + 16.5, f"{self.sheet}   R3", fontsize=6.6, color=INK, zorder=7)
        a.text(x0 + 3, y0 + 9.0, "UNITS mm  |  GENERAL TOL. ISO 2768-m  |  FIRST-ANGLE PROJECTION", fontsize=5.0, color=INK, zorder=7)
        a.text(x0 + 3, y0 + 3.4, "STATUS: design release for prototype - confirm bought-out parts against supplier drawings",
               fontsize=4.7, color="#8a3b12", zorder=7)
        a.text(x0 + 113, y0 + 9.0, "DATE", fontsize=4.6, color="#4b5b68", zorder=7)
        a.text(x0 + 113, y0 + 3.4, datetime.date.today().isoformat(), fontsize=6, color=INK, zorder=7)
        a.text(x0 + 148, y0 + 9.0, "GENERATED FROM", fontsize=4.6, color="#4b5b68", zorder=7)
        a.text(x0 + 148, y0 + 3.4, "src/params.py", fontsize=5.6, color=INK, zorder=7)
        self._projection_symbol(x0 + w - 20, y0 + 30.5)

    def _projection_symbol(self, cx, cy):
        a = self.ax
        a.add_patch(Polygon([(cx - 9, cy - 3), (cx - 9, cy + 3), (cx - 2, cy + 1.6), (cx - 2, cy - 1.6)], closed=True,
                            fill=False, ec=INK, lw=LW_THIN, zorder=7))
        a.add_patch(Circle((cx + 5, cy), 3, fill=False, ec=INK, lw=LW_THIN, zorder=7))
        a.add_patch(Circle((cx + 5, cy), 1.6, fill=False, ec=INK, lw=LW_THIN, zorder=7))

    # ------------------------------------------------------------------ primitives
    def text(self, x, y, s, size=TXT, **kw):
        kw.setdefault("color", INK)
        self.ax.text(x, y, s, fontsize=pt(size), zorder=kw.pop("zorder", 8), **kw)

    def line(self, pts, lw=LW_THIN, color=INK, ls="-", z=6):
        p = np.asarray(pts)
        self.ax.plot(p[:, 0], p[:, 1], color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="butt")

    def centerline(self, p0, p1):
        self.line([p0, p1], lw=LW_THIN, color="#3b4a55", ls=(0, (8, 2, 1.5, 2)))

    def arrow(self, p_from, p_to):
        self.ax.annotate("", xy=p_to, xytext=p_from, zorder=8,
                         arrowprops=dict(arrowstyle="-|>,head_length=0.55,head_width=0.18", lw=LW_THIN, color=DIM,
                                         shrinkA=0, shrinkB=0))

    def dim(self, p1, p2, offset, text, vertical=False, size=TXT, flip_text=False):
        """Linear dimension between paper points p1 and p2, dimension line offset perpendicular."""
        p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
        if vertical:
            xd = p1[0] + offset if abs(offset) > 0 else p1[0]
            a, b = np.array([xd, p1[1]]), np.array([xd, p2[1]])
            self.line([(p1[0] + math.copysign(1.0, offset), p1[1]), (xd + math.copysign(1.8, offset), p1[1])], color=DIM)
            self.line([(p2[0] + math.copysign(1.0, offset), p2[1]), (xd + math.copysign(1.8, offset), p2[1])], color=DIM)
            mid = (a + b) / 2
            self.arrow(mid, a)
            self.arrow(mid, b)
            self.ax.text(xd - 1.0 if not flip_text else xd + 1.0, mid[1], text, rotation=90, ha="right" if not flip_text else "left",
                         va="center", fontsize=pt(size), color=DIM, zorder=9,
                         bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.85))
        else:
            yd = p1[1] + offset
            a, b = np.array([p1[0], yd]), np.array([p2[0], yd])
            self.line([(p1[0], p1[1] + math.copysign(1.0, offset)), (p1[0], yd + math.copysign(1.8, offset))], color=DIM)
            self.line([(p2[0], p2[1] + math.copysign(1.0, offset)), (p2[0], yd + math.copysign(1.8, offset))], color=DIM)
            mid = (a + b) / 2
            self.arrow(mid, a)
            self.arrow(mid, b)
            self.ax.text(mid[0], yd + 0.8, text, ha="center", va="bottom", fontsize=pt(size), color=DIM, zorder=9,
                         bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.85))

    def leader(self, p_at, p_text, text, size=TXT, ha="left"):
        self.line([p_at, p_text], color=DIM)
        self.ax.add_patch(Circle(p_at, 0.55, color=DIM, zorder=9))
        self.line([p_text, (p_text[0] + (12 if ha == "left" else -12), p_text[1])], color=DIM)
        self.ax.text(p_text[0] + (13 if ha == "left" else -13), p_text[1], text, ha=ha, va="center", fontsize=pt(size),
                     color=DIM, zorder=9, bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.9))

    def balloon(self, p_at, p_ball, n, r=3.4):
        v = np.asarray(p_ball) - np.asarray(p_at)
        L = np.linalg.norm(v)
        end = np.asarray(p_ball) - v / L * r if L > r else p_ball
        self.line([p_at, end], color=DIM)
        self.ax.add_patch(Circle(p_at, 0.6, color=DIM, zorder=9))
        self.ax.add_patch(Circle(p_ball, r, fc="white", ec=INK, lw=LW_MED, zorder=9))
        self.ax.text(p_ball[0], p_ball[1], str(n), ha="center", va="center", fontsize=pt(2.6), weight="bold", color=INK, zorder=10)

    def waterline(self, x0, x1, y, label):
        self.line([(x0, y), (x1, y)], lw=LW_MED, color=BLUE, ls=(0, (6, 2)))
        tri = [(x1 - 6, y + 0.2), (x1 - 3.5, y + 3.2), (x1 - 8.5, y + 3.2)]
        self.ax.add_patch(Polygon(tri, closed=True, fc="white", ec=BLUE, lw=LW_THIN, zorder=9))
        self.ax.text(x1 - 10, y + 1.6, label, ha="right", va="bottom", fontsize=pt(2.4), color=BLUE, zorder=9)

    def view_title(self, x, y, s, sub=None):
        self.ax.text(x, y, s, ha="center", va="top", fontsize=pt(3.3), weight="bold", color=INK, zorder=9)
        if sub:
            self.ax.text(x, y - 4.6, sub, ha="center", va="top", fontsize=pt(2.4), color="#4b5b68", zorder=9)

    def note_block(self, x, y, lines, title="NOTES", width=150, size=2.3):
        self.ax.text(x, y, title, fontsize=pt(2.8), weight="bold", color=INK, va="top", zorder=9)
        yy = y - 5
        for i, ln in enumerate(lines, 1):
            self.ax.text(x, yy, f"{i}.  {ln}", fontsize=pt(size), color=INK, va="top", zorder=9, wrap=True)
            yy -= size * 1.75

    def table(self, x, y, cols, rows, widths, row_h=4.2, size=2.15, header_fc="#e6edf2"):
        """Table anchored at its top-left (x, y)."""
        total = sum(widths)
        self.ax.add_patch(Rectangle((x, y - row_h), total, row_h, fc=header_fc, ec=INK, lw=LW_THIN, zorder=7))
        cx = x
        for c, w_ in zip(cols, widths):
            self.ax.text(cx + 1.2, y - row_h / 2, c, fontsize=pt(size), weight="bold", va="center", color=INK, zorder=8)
            cx += w_
        yy = y - row_h
        for r in rows:
            self.ax.add_patch(Rectangle((x, yy - row_h), total, row_h, fc="white", ec=INK, lw=LW_THIN * 0.7, zorder=7))
            cx = x
            for c, w_ in zip(r, widths):
                s = str(c)
                maxch = int(w_ / (size * 0.52))
                if len(s) > maxch:
                    s = s[:maxch - 1] + "..."
                self.ax.text(cx + 1.2, yy - row_h / 2, s, fontsize=pt(size), va="center", color=INK, zorder=8)
                cx += w_
            yy -= row_h
        cx = x
        for w_ in widths[:-1]:
            cx += w_
            self.line([(cx, y), (cx, yy)], lw=LW_THIN * 0.7, z=8)
        return yy

    def image(self, path, cx_paper, cy_paper, s_px_per_mm, k_paper_per_mm, white_to_alpha=True):
        im = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32) / 255.0
        if white_to_alpha:
            wht = (im[:, :, 0] > 0.985) & (im[:, :, 1] > 0.985) & (im[:, :, 2] > 0.985)
            im[wht, 3] = 0.0
        h, w = im.shape[:2]
        half_w = w / 2 / s_px_per_mm * k_paper_per_mm
        half_h = h / 2 / s_px_per_mm * k_paper_per_mm
        self.ax.imshow(im, extent=[cx_paper - half_w, cx_paper + half_w, cy_paper - half_h, cy_paper + half_h],
                       interpolation="lanczos", zorder=2)

    def save(self, path_png, pdf=None):
        self.fig.savefig(path_png, dpi=self.dpi)
        if pdf is not None:
            pdf.savefig(self.fig)
        plt.close(self.fig)


class View:
    """Maps model coordinates in a view plane to paper mm. sign_u = -1 for views whose u-axis is mirrored."""

    def __init__(self, sheet, centre_model, centre_paper, k, sign_u=1.0):
        self.sh, self.cm, self.cp, self.k, self.su = sheet, np.asarray(centre_model, float), np.asarray(centre_paper, float), k, sign_u

    def P(self, a, b):
        return (self.cp[0] + self.su * (a - self.cm[0]) * self.k, self.cp[1] + (b - self.cm[1]) * self.k)
