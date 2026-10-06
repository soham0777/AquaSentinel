"""
Small polygon-mesh modelling kernel used to build the AquaSentinel R3 parts.

Every builder returns a closed, outward-oriented Shell made of planar
polygons (quads / n-gons where they are planar by construction, triangles
otherwise). Shells are what the exporters turn into STL, GLB and STEP
(planar-face B-rep) bodies. Units: millimetres.
"""
import math
import numpy as np

TAU = 2 * math.pi


# ---------------------------------------------------------------------------
# Transforms (4x4, column vectors)
# ---------------------------------------------------------------------------
def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def _rot(axis, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    x, y, z = np.asarray(axis, float) / np.linalg.norm(axis)
    m = np.eye(4)
    m[:3, :3] = [
        [c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
        [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
        [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)],
    ]
    return m


def Rx(deg):
    return _rot((1, 0, 0), deg)


def Ry(deg):
    return _rot((0, 1, 0), deg)


def Rz(deg):
    return _rot((0, 0, 1), deg)


def Raxis(axis, deg):
    return _rot(axis, deg)


def apply(M, pts):
    pts = np.asarray(pts, float)
    return pts @ M[:3, :3].T + M[:3, 3]


# ---------------------------------------------------------------------------
# Shell
# ---------------------------------------------------------------------------
class Shell:
    """Closed polyhedral surface: vertices V (n,3) and polygons P (index tuples)."""

    __slots__ = ("V", "P")

    def __init__(self, V, P):
        self.V = np.asarray(V, dtype=float)
        self.P = [tuple(int(i) for i in p) for p in P]

    def copy(self):
        return Shell(self.V.copy(), list(self.P))

    def transformed(self, M):
        s = Shell(apply(M, self.V), list(self.P))
        if np.linalg.det(M[:3, :3]) < 0:
            s.P = [tuple(reversed(p)) for p in s.P]
        return s

    # -- triangulation -----------------------------------------------------
    def triangles(self):
        tris = []
        V = self.V
        for p in self.P:
            n = len(p)
            if n == 3:
                tris.append(p)
            elif n == 4:
                a, b, c, d = p
                # split along the shorter diagonal (keeps quads from loft clean)
                if np.sum((V[a] - V[c]) ** 2) <= np.sum((V[b] - V[d]) ** 2):
                    tris += [(a, b, c), (a, c, d)]
                else:
                    tris += [(a, b, d), (b, c, d)]
            else:
                tris += triangulate_polygon(V, p)
        return np.array(tris, dtype=np.int64).reshape(-1, 3)

    def signed_volume(self):
        t = self.triangles()
        a, b, c = self.V[t[:, 0]], self.V[t[:, 1]], self.V[t[:, 2]]
        return float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)

    def area(self):
        t = self.triangles()
        a, b, c = self.V[t[:, 0]], self.V[t[:, 1]], self.V[t[:, 2]]
        return float(np.linalg.norm(np.cross(b - a, c - a), axis=1).sum() / 2.0)

    def fix_orientation(self):
        if self.signed_volume() < 0:
            self.P = [tuple(reversed(p)) for p in self.P]
        return self

    def is_closed(self):
        """Every directed edge must have exactly one opposite partner."""
        edges = {}
        for p in self.P:
            n = len(p)
            for i in range(n):
                e = (p[i], p[(i + 1) % n])
                edges[e] = edges.get(e, 0) + 1
        for (a, b), cnt in edges.items():
            if cnt != 1 or edges.get((b, a), 0) != 1:
                return False
        return True

    def bounds(self):
        return self.V.min(axis=0), self.V.max(axis=0)


def triangulate_polygon(V, p):
    """Ear clipping in the polygon's best-fit plane (handles concave caps)."""
    pts = V[list(p)]
    n = len(p)
    normal = np.zeros(3)
    for i in range(n):  # Newell normal
        c, d = pts[i], pts[(i + 1) % n]
        normal += [(c[1] - d[1]) * (c[2] + d[2]), (c[2] - d[2]) * (c[0] + d[0]), (c[0] - d[0]) * (c[1] + d[1])]
    nn = np.linalg.norm(normal)
    if nn < 1e-12:
        return [(p[0], p[i], p[i + 1]) for i in range(1, n - 1)]
    normal /= nn
    u = np.cross(normal, [1, 0, 0] if abs(normal[0]) < 0.9 else [0, 1, 0])
    u /= np.linalg.norm(u)
    v = np.cross(normal, u)
    xy = np.c_[pts @ u, pts @ v]

    def cross2(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    # fast path: convex polygon -> fan
    signs = [cross2(xy[i - 1], xy[i], xy[(i + 1) % n]) for i in range(n)]
    if all(s >= -1e-9 for s in signs):
        return [(p[0], p[i], p[i + 1]) for i in range(1, n - 1)]

    idx = list(range(n))
    out = []
    guard = 0
    while len(idx) > 3 and guard < 10000:
        guard += 1
        m = len(idx)
        for k in range(m):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % m]
            if cross2(xy[i0], xy[i1], xy[i2]) <= 1e-12:
                continue
            ok = True
            for j in idx:
                if j in (i0, i1, i2):
                    continue
                if (cross2(xy[i0], xy[i1], xy[j]) >= 0 and cross2(xy[i1], xy[i2], xy[j]) >= 0
                        and cross2(xy[i2], xy[i0], xy[j]) >= 0):
                    ok = False
                    break
            if ok:
                out.append((p[i0], p[i1], p[i2]))
                idx.pop(k)
                break
        else:
            break
    if len(idx) == 3:
        out.append((p[idx[0]], p[idx[1]], p[idx[2]]))
    return out


# ---------------------------------------------------------------------------
# 2D profiles (CCW)
# ---------------------------------------------------------------------------
def arc(cx, cy, r, a0, a1, n):
    t = np.linspace(a0, a1, n)
    return np.c_[cx + r * np.cos(t), cy + r * np.sin(t)]


def rrect2d(w, h, r, n=6, cx=0.0, cy=0.0):
    """Rounded rectangle, CCW, constant point count (4*n)."""
    r = max(0.2, min(r, w / 2 - 0.05, h / 2 - 0.05))
    hw, hh = w / 2 - r, h / 2 - r
    pts = [arc(cx + hw, cy - hh, r, -math.pi / 2, 0, n),
           arc(cx + hw, cy + hh, r, 0, math.pi / 2, n),
           arc(cx - hw, cy + hh, r, math.pi / 2, math.pi, n),
           arc(cx - hw, cy - hh, r, math.pi, 1.5 * math.pi, n)]
    return np.vstack(pts)


def rrect2d_tb(y0, y1, z0, z1, rb, rt, n=6):
    """Rounded rectangle with different bottom/top corner radii (in y-z), CCW."""
    w, h = y1 - y0, z1 - z0
    rb = max(0.2, min(rb, w / 2 - 0.05, h / 2 - 0.05))
    rt = max(0.2, min(rt, w / 2 - 0.05, h / 2 - 0.05))
    return np.vstack([
        arc(y1 - rb, z0 + rb, rb, -math.pi / 2, 0, n),
        arc(y1 - rt, z1 - rt, rt, 0, math.pi / 2, n),
        arc(y0 + rt, z1 - rt, rt, math.pi / 2, math.pi, n),
        arc(y0 + rb, z0 + rb, rb, math.pi, 1.5 * math.pi, n),
    ])


def circle2d(r, n=32, cx=0.0, cy=0.0, phase=0.0):
    t = np.linspace(0, TAU, n, endpoint=False) + phase
    return np.c_[cx + r * np.cos(t), cy + r * np.sin(t)]


def resample_by_angle(poly, center, angles):
    """Ray-cast a star-shaped polygon from `center` at the given angles."""
    poly = np.asarray(poly, float)
    c = np.asarray(center, float)
    out = []
    a_pts = poly
    b_pts = np.roll(poly, -1, axis=0)
    for th in angles:
        d = np.array([math.cos(th), math.sin(th)])
        best = None
        for a, b in zip(a_pts, b_pts):
            e = b - a
            den = d[0] * (-e[1]) - d[1] * (-e[0])
            if abs(den) < 1e-12:
                continue
            w = a - c
            t = (w[0] * (-e[1]) - w[1] * (-e[0])) / den
            s = (d[0] * w[1] - d[1] * w[0]) / den
            if t > 0 and -1e-9 <= s <= 1 + 1e-9 and (best is None or t < best):
                best = t
        out.append(c + best * d)
    return np.array(out)


# ---------------------------------------------------------------------------
# 3D builders
# ---------------------------------------------------------------------------
def loft(rings, closed_rings=True, close_loop=False, cap0=True, cap1=True):
    rings = [np.asarray(r, float) for r in rings]
    n = len(rings[0])
    k = len(rings)
    V = np.vstack(rings)

    def idx(i, j):
        return i * n + (j % n)

    P = []
    seg = n if closed_rings else n - 1
    pairs = list(range(k - 1)) + ([k - 1] if close_loop else [])
    for i in pairs:
        i2 = (i + 1) % k
        for j in range(seg):
            P.append((idx(i, j), idx(i, j + 1), idx(i2, j + 1), idx(i2, j)))
    if not close_loop:
        if cap0:
            P.append(tuple(idx(0, j) for j in reversed(range(n))))
        if cap1:
            P.append(tuple(idx(k - 1, j) for j in range(n)))
    return Shell(V, P).fix_orientation()


def box(x0, x1, y0, y1, z0, z1):
    V = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    P = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return Shell(V, P).fix_orientation()


def ring_on_plane(pts2d, z):
    pts2d = np.asarray(pts2d, float)
    return np.c_[pts2d, np.full(len(pts2d), z)]


def extrude(poly2d, z0, z1):
    """Prism along +z from a CCW 2D polygon (may be concave)."""
    return loft([ring_on_plane(poly2d, z0), ring_on_plane(poly2d, z1)])


def rounded_box(sx, sy, sz, r_side=10.0, r_edge=0.0, n=6, ne=4, center=(0, 0, 0)):
    """Box with vertical edges rounded by r_side and top/bottom edges filleted by r_edge."""
    cx, cy, cz = center
    z0, z1 = cz - sz / 2, cz + sz / 2
    rings = []
    if r_edge > 0.05:
        for t in np.linspace(0, math.pi / 2, ne + 1):
            inset = r_edge * (1 - math.sin(t))
            z = z0 + r_edge * (1 - math.cos(t))
            rings.append(ring_on_plane(rrect2d(sx - 2 * inset, sy - 2 * inset, r_side - inset, n, cx, cy), z))
        for t in np.linspace(math.pi / 2, 0, ne + 1):
            inset = r_edge * (1 - math.sin(t))
            z = z1 - r_edge * (1 - math.cos(t))
            rings.append(ring_on_plane(rrect2d(sx - 2 * inset, sy - 2 * inset, r_side - inset, n, cx, cy), z))
    else:
        rings = [ring_on_plane(rrect2d(sx, sy, r_side, n, cx, cy), z0),
                 ring_on_plane(rrect2d(sx, sy, r_side, n, cx, cy), z1)]
    return loft(rings)


def cylinder(r, z0, z1, n=32, cx=0.0, cy=0.0, phase=0.0):
    c = circle2d(r, n, cx, cy, phase)
    return loft([ring_on_plane(c, z0), ring_on_plane(c, z1)])


def tube(ro, ri, z0, z1, n=32, cx=0.0, cy=0.0):
    co = circle2d(ro, n, cx, cy)
    ci = circle2d(ri, n, cx, cy)
    return loft([ring_on_plane(co, z0), ring_on_plane(co, z1), ring_on_plane(ci, z1), ring_on_plane(ci, z0)],
                close_loop=True)


def ring_plate(outer2d, inner2d, z0, z1):
    """Planar plate between an outer and an inner loop with matching point counts."""
    return loft([ring_on_plane(outer2d, z0), ring_on_plane(outer2d, z1),
                 ring_on_plane(inner2d, z1), ring_on_plane(inner2d, z0)], close_loop=True)


def plate_with_hole(outer2d, hole_c, hole_r, z0, z1, n_uniform=48):
    """Plate (outer polygon star-shaped about hole_c) with a round hole."""
    outer2d = np.asarray(outer2d, float)
    c = np.asarray(hole_c, float)
    ang = set(np.round(np.linspace(0, TAU, n_uniform, endpoint=False), 9))
    for p in outer2d:
        ang.add(round(math.atan2(p[1] - c[1], p[0] - c[0]) % TAU, 9))
    angles = np.array(sorted(ang))
    outer = resample_by_angle(outer2d, c, angles)
    inner = np.c_[c[0] + hole_r * np.cos(angles), c[1] + hole_r * np.sin(angles)]
    return ring_plate(outer, inner, z0, z1)


def revolve(profile, n=48, phase=0.0):
    """Open profile [(r, z), ...] revolved about z. End points with r == 0 become flat caps."""
    prof = [tuple(p) for p in profile]
    cap0 = cap1 = True
    if prof[0][0] <= 1e-9:
        prof = prof[1:]
    if prof[-1][0] <= 1e-9:
        prof = prof[:-1]
    th = np.linspace(0, TAU, n, endpoint=False) + phase
    rings = [np.c_[r * np.cos(th), r * np.sin(th), np.full(n, z)] for r, z in prof]
    return loft(rings, cap0=cap0, cap1=cap1)


def revolve_closed(loop_rz, n=48, phase=0.0):
    """Closed profile loop [(r, z), ...] (r > 0) revolved about z (rings, tyres, collars)."""
    loop = np.asarray(loop_rz, float)
    th = np.linspace(0, TAU, n, endpoint=False) + phase
    rings = []
    for t in th:
        rings.append(np.c_[loop[:, 0] * math.cos(t), loop[:, 0] * math.sin(t), loop[:, 1]])
    return loft(rings, closed_rings=True, close_loop=True)


def fillet_path(points, radius, segs=6):
    """Replace interior corners of a 3D polyline with circular arcs."""
    P = [np.asarray(p, float) for p in points]
    if len(P) < 3 or radius <= 0:
        return np.array(P)
    out = [P[0]]
    for i in range(1, len(P) - 1):
        a, b, c = P[i - 1], P[i], P[i + 1]
        u = (a - b) / np.linalg.norm(a - b)
        v = (c - b) / np.linalg.norm(c - b)
        ang = math.acos(max(-1.0, min(1.0, float(u @ v))))
        if ang > math.pi - 1e-3:
            out.append(b)
            continue
        d = radius / math.tan(ang / 2)
        d = min(d, 0.45 * np.linalg.norm(a - b), 0.45 * np.linalg.norm(c - b))
        p0, p1 = b + u * d, b + v * d
        for t in np.linspace(0, 1, segs + 1):  # quadratic Bezier approximates the arc well enough
            out.append((1 - t) ** 2 * p0 + 2 * (1 - t) * t * b + t ** 2 * p1)
    out.append(P[-1])
    return np.array(out)


def sweep(path, profile2d, closed=False):
    """Sweep a 2D profile along a 3D polyline with rotation-minimising frames."""
    path = np.asarray(path, float)
    m = len(path)
    tang = np.zeros_like(path)
    for i in range(m):
        if closed:
            d = path[(i + 1) % m] - path[i - 1]
        elif i == 0:
            d = path[1] - path[0]
        elif i == m - 1:
            d = path[-1] - path[-2]
        else:
            d = (path[i + 1] - path[i]) / np.linalg.norm(path[i + 1] - path[i]) + \
                (path[i] - path[i - 1]) / np.linalg.norm(path[i] - path[i - 1])
        tang[i] = d / np.linalg.norm(d)
    ref = np.array([0, 0, 1.0]) if abs(tang[0][2]) < 0.9 else np.array([1.0, 0, 0])
    nrm = np.cross(tang[0], ref)
    nrm /= np.linalg.norm(nrm)
    rings = []
    prof = np.asarray(profile2d, float)
    for i in range(m):
        if i > 0:  # parallel transport
            nrm = nrm - tang[i] * (nrm @ tang[i])
            nrm /= np.linalg.norm(nrm)
        bin_ = np.cross(tang[i], nrm)
        rings.append(path[i] + np.outer(prof[:, 0], nrm) + np.outer(prof[:, 1], bin_))
    return loft(rings, close_loop=closed)


def pipe_along(path, r, n=16, closed=False, fillet=0.0):
    pts = fillet_path(path, fillet) if fillet > 0 and not closed else np.asarray(path, float)
    return sweep(pts, circle2d(r, n), closed=closed)


def hex_prism(af, z0, z1, cx=0.0, cy=0.0, phase=math.pi / 6):
    """Hexagon prism with across-flats `af` (bolt heads, nuts)."""
    r = af / math.sqrt(3)
    return extrude(circle2d(r, 6, cx, cy, phase), z0, z1)


def frustum(r0, r1, z0, z1, n=32):
    return loft([ring_on_plane(circle2d(r0, n), z0), ring_on_plane(circle2d(r1, n), z1)])


def place(shells, M):
    if isinstance(shells, Shell):
        return [shells.transformed(M)]
    return [s.transformed(M) for s in shells]


def align_z_to(direction):
    """Rotation taking +z onto `direction`."""
    d = np.asarray(direction, float)
    d = d / np.linalg.norm(d)
    z = np.array([0, 0, 1.0])
    c = float(z @ d)
    if c > 1 - 1e-12:
        return np.eye(4)
    if c < -1 + 1e-12:
        return Rx(180)
    ax = np.cross(z, d)
    return Raxis(ax, math.degrees(math.acos(c)))


def bolt(d, length, head_h=None, washer=True):
    """Hex head bolt pointing down from z=0 (head on top, sitting on the surface)."""
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


def window_loops(outer2d, inner2d, n_uniform=48):
    """Resample an outer outline and an inner window on common rays from the window centre,
    so a plate-with-window can be built as a closed ring (both loops star-shaped about that centre)."""
    outer2d = np.asarray(outer2d, float)
    inner2d = np.asarray(inner2d, float)
    c = inner2d.mean(axis=0)
    ang = set(np.round(np.linspace(0, TAU, n_uniform, endpoint=False), 9))
    for p in np.vstack([outer2d, inner2d]):
        ang.add(round(math.atan2(p[1] - c[1], p[0] - c[0]) % TAU, 9))
    angles = np.array(sorted(ang))
    return resample_by_angle(outer2d, c, angles), resample_by_angle(inner2d, c, angles)
