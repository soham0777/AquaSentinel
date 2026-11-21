"""Drop-in replacement for the R3 generator's geom.py.
Instead of faceted shells, every builder returns a Prim: an exact description of the feature
(extrude / revolve / rounded box / pipe / loft) plus a 4x4 placement. swbuild.py turns Prims into
native SOLIDWORKS features. Transform helpers are re-exported unchanged from the original kernel."""
import math
import importlib.util
import numpy as np

_spec = importlib.util.spec_from_file_location("geom_orig", __import__("os").environ["R3_GEOM_ORIG"])
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

TAU = G.TAU
T, Rx, Ry, Rz, Raxis, apply, align_z_to = G.T, G.Rx, G.Ry, G.Rz, G.Raxis, G.apply, G.align_z_to
arc, rrect2d_tb, resample_by_angle = G.arc, G.rrect2d_tb, G.resample_by_angle


def rrect2d(w, h, r, n=6, cx=0.0, cy=0.0):
    # same outline; at least 8 points per corner so the builder can recognise every corner as a true arc
    return G.rrect2d(w, h, r, max(n, 8), cx, cy)


def circle2d(r, n=32, cx=0.0, cy=0.0, phase=0.0):
    return G.circle2d(r, max(n, 16), cx, cy, phase)
fillet_path = G.fillet_path


class Prim:
    def __init__(self, kind, M=None, **data):
        self.kind = kind
        self.data = data
        self.M = np.eye(4) if M is None else np.asarray(M, float)

    def transformed(self, M):
        return Prim(self.kind, np.asarray(M, float) @ self.M, **self.data)

    # analysis stubs (mass is taken from SOLIDWORKS for the native parts)
    def signed_volume(self):
        return 0.0

    def area(self):
        return 0.0

    def fix_orientation(self):
        return self

    def __repr__(self):
        return f"Prim({self.kind})"


Shell = Prim


def _a(p):
    return np.asarray(p, float)


def ext(loops, axis, a0, a1):
    if a1 < a0:
        a0, a1 = a1, a0
    return Prim("ext", loops=[_a(l) for l in loops], axis=axis, a0=float(a0), a1=float(a1))


def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1))
    return ext([[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]], "z", z0, z1)


def extrude(poly2d, z0, z1):
    return ext([poly2d], "z", z0, z1)


def cylinder(r, z0, z1, n=32, cx=0.0, cy=0.0, phase=0.0):
    return Prim("ext", circles=[(cx, cy, r)], loops=[], axis="z", a0=float(min(z0, z1)), a1=float(max(z0, z1)))


def tube(ro, ri, z0, z1, n=32, cx=0.0, cy=0.0):
    return Prim("ext", circles=[(cx, cy, ro), (cx, cy, ri)], loops=[], axis="z", a0=float(min(z0, z1)), a1=float(max(z0, z1)))


def hex_prism(af, z0, z1, cx=0.0, cy=0.0, phase=math.pi / 6):
    r = af / math.sqrt(3)
    pts = [(cx + r * math.cos(phase + k * math.pi / 3), cy + r * math.sin(phase + k * math.pi / 3)) for k in range(6)]
    return Prim("ext", loops=[_a(pts)], axis="z", a0=float(z0), a1=float(z1), straight=True)


def frustum(r0, r1, z0, z1, n=32):
    return revolve([(0, z0), (r0, z0), (r1, z1), (0, z1)])


def ring_plate(outer2d, inner2d, z0, z1):
    return ext([outer2d, inner2d], "z", z0, z1)


def plate_with_hole(outer2d, hole_c, hole_r, z0, z1, n_uniform=48):
    return Prim("ext", loops=[_a(outer2d)], circles=[(hole_c[0], hole_c[1], hole_r)], axis="z",
                a0=float(min(z0, z1)), a1=float(max(z0, z1)))


def window_loops(outer2d, inner2d, n_uniform=48):
    return _a(outer2d), _a(inner2d)


def rounded_box(sx, sy, sz, r_side=10.0, r_edge=0.0, n=6, ne=4, center=(0, 0, 0)):
    return Prim("rbox", sx=sx, sy=sy, sz=sz, r_side=r_side, r_edge=r_edge, center=tuple(center))


def revolve(profile, n=48, phase=0.0):
    prof = [tuple(map(float, p)) for p in profile]
    if prof[0][0] > 1e-9:
        prof = [(0.0, prof[0][1])] + prof
    if prof[-1][0] > 1e-9:
        prof = prof + [(0.0, prof[-1][1])]
    return Prim("rev", loop=_a(prof), a0=0.0, a1=360.0, on_axis=True)


def revolve_closed(loop_rz, n=48, phase=0.0):
    return Prim("rev", loop=_a(loop_rz), a0=0.0, a1=360.0, on_axis=False)


def revolve_partial(loop_rz, a0_deg, a1_deg, n=24):
    return Prim("rev", loop=_a(loop_rz), a0=float(a0_deg), a1=float(a1_deg), on_axis=False)


def loft(rings, closed_rings=True, close_loop=False, cap0=True, cap1=True):
    return Prim("loft", rings=[_a(r) for r in rings])


def sweep(path, profile2d, closed=False):
    raise NotImplementedError("sweep with a custom profile")


def pipe_along(path, r, n=16, closed=False, fillet=0.0):
    return Prim("pipe", path=_a(path), r=float(r), fillet=float(fillet), closed=bool(closed))


def place(shells, M):
    if isinstance(shells, Prim):
        return [shells.transformed(M)]
    return [s.transformed(M) for s in shells]


def bolt(d, length, head_h=None, washer=True):
    af = {6: 10, 8: 13, 10: 16, 12: 18, 16: 24}.get(int(d), 1.6 * d)
    head_h = head_h or 0.65 * d
    shells = []
    z = 0.0
    if washer:
        shells.append(cylinder(1.0 * af * 0.62 + 1.0, 0, 0.18 * d, 24))
        z = 0.18 * d
    shells.append(hex_prism(af, z, z + head_h))
    shells.append(cylinder(d / 2, -length, 0.01, 16))
    return shells


# --- helpers that parts.py defines on top of geom (patched into parts after import) ---
def prism(profile2d, axis, a0, a1):
    return ext([profile2d], axis, a0, a1)


def hollow_prism(outer, inner, axis, a0, a1):
    return ext([outer, inner], axis, a0, a1)


def window_plate(outer, inner, axis, a0, a1):
    return ext([outer, inner], axis, a0, a1)
