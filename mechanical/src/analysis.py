"""
Engineering checks computed from the R3 CAD geometry (not from a hand-entered mass list).

  * mass properties          - every instance, mass rule stated per part
  * hydrostatics             - draft, freeboard, reserve buoyancy, LCB/LCG, waterplane, LCF
  * large-angle stability    - GZ curve for the free-floating float (deployment / towing / detached)
  * hydrodynamic areas       - submerged frontal + lateral projected area, centre of lateral resistance
  * pole + carriage          - same load case and formulas as v2 (calculations/verified_design_calcs.py),
                               re-run with the R3 geometry: span, drag area, eccentricity, roller spacing
  * clearances               - pole corridor, float vs fixed hardware over the full stage travel,
                               part-to-part interference by voxelisation (2 mm)

All results are DESIGN ESTIMATES. Nothing here is a measurement.
"""
import math
import numpy as np

from params import *

RHO_W = 1000.0
G = 9.80665


# ---------------------------------------------------------------------------
# geometry soup
# ---------------------------------------------------------------------------
def inst_shells(inst):
    return [s.transformed(inst.M) for s in inst.part.shells]


def tri_soup(insts):
    Vs, Fs, off = [], [], 0
    for i in insts:
        for s in inst_shells(i):
            t = s.triangles()
            Vs.append(s.V)
            Fs.append(t + off)
            off += len(s.V)
    V = np.vstack(Vs)
    F = np.vstack(Fs)
    return V[F]          # (m, 3, 3)


# ---------------------------------------------------------------------------
# mass properties
# ---------------------------------------------------------------------------
def mass_properties(insts):
    rows, M, mom = [], 0.0, np.zeros(3)
    for i in insts:
        m = i.part.mass_kg()
        c = (i.M @ np.r_[i.part.centroid_local(), 1.0])[:3]
        rows.append(dict(instance=i.name, pid=i.part.pid, part=i.part.name, kg=m, cg=c, basis=i.part.mass_basis(),
                         group=i.group))
        M += m
        mom += m * c
    return rows, M, mom / M


# ---------------------------------------------------------------------------
# hydrostatics on a triangle soup (exact for polyhedra)
# ---------------------------------------------------------------------------
def _clip_below(tris, d):
    """Return triangles of the part of every input triangle that lies below z = d (orientation kept)."""
    s = tris[:, :, 2] - d
    below = s <= 0
    nb = below.sum(axis=1)
    out = [tris[nb == 3]]
    # one vertex below
    m1 = nb == 1
    if m1.any():
        t = tris[m1]
        b = below[m1]
        k = np.argmax(b, axis=1)
        idx = (k[:, None] + np.arange(3)[None, :]) % 3
        t = np.take_along_axis(t, idx[:, :, None], axis=1)
        ss = t[:, :, 2] - d
        a, bb, c = t[:, 0], t[:, 1], t[:, 2]
        pab = a + (bb - a) * (ss[:, 0] / (ss[:, 0] - ss[:, 1]))[:, None]
        pac = a + (c - a) * (ss[:, 0] / (ss[:, 0] - ss[:, 2]))[:, None]
        out.append(np.stack([a, pab, pac], axis=1))
    m2 = nb == 2
    if m2.any():
        t = tris[m2]
        ab = ~below[m2]
        k = np.argmax(ab, axis=1)
        idx = (k[:, None] + np.arange(3)[None, :]) % 3
        t = np.take_along_axis(t, idx[:, :, None], axis=1)
        ss = t[:, :, 2] - d
        a, bb, c = t[:, 0], t[:, 1], t[:, 2]
        pab = a + (bb - a) * (ss[:, 0] / (ss[:, 0] - ss[:, 1]))[:, None]
        pca = a + (c - a) * (ss[:, 0] / (ss[:, 0] - ss[:, 2]))[:, None]
        out.append(np.stack([pab, bb, c], axis=1))
        out.append(np.stack([pab, c, pca], axis=1))
    return np.concatenate(out, axis=0)


def submerged(tris, d):
    """Volume (mm3) and centroid of the closed geometry below the plane z = d."""
    t = _clip_below(tris, d)
    if len(t) == 0:
        return 0.0, np.zeros(3)
    a, b, c = t[:, 0], t[:, 1], t[:, 2]
    va = 0.5 * np.cross(b - a, c - a)                     # vector area
    zb = (a[:, 2] + b[:, 2] + c[:, 2]) / 3.0
    vol = float(np.sum(va[:, 2] * (zb - d)))

    def s2(i):
        return a[:, i] ** 2 + b[:, i] ** 2 + c[:, i] ** 2 + a[:, i] * b[:, i] + b[:, i] * c[:, i] + c[:, i] * a[:, i]

    mx = float(np.sum(va[:, 0] * s2(0) / 12.0))
    my = float(np.sum(va[:, 1] * s2(1) / 12.0))
    mz = float(np.sum(va[:, 2] * (s2(2) / 12.0 - d * d / 2.0)))
    if vol <= 0:
        return 0.0, np.zeros(3)
    return vol, np.array([mx, my, mz]) / vol


def solve_waterplane(tris, vol_target, lo=None, hi=None):
    zmin, zmax = tris[:, :, 2].min(), tris[:, :, 2].max()
    lo = zmin if lo is None else lo
    hi = zmax if hi is None else hi
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        v, _ = submerged(tris, mid)
        if v < vol_target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def rotate_x(tris, deg, about_z=0.0):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    R = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    p = tris.copy()
    p[:, :, 2] -= about_z
    p = p @ R.T
    p[:, :, 2] += about_z
    return p, R


def rotate_y(tris, deg, about=(0.0, 0.0)):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    p = tris.copy()
    p[:, :, 0] -= about[0]
    p[:, :, 2] -= about[1]
    p = p @ R.T
    p[:, :, 0] += about[0]
    p[:, :, 2] += about[1]
    return p, R


def gz_curve(tris, cg, vol, angles):
    out = []
    for ang in angles:
        p, R = rotate_x(tris, ang, cg[2])
        g_ = cg.copy()
        g_[2] -= cg[2]
        g_ = R @ g_
        g_[2] += cg[2]
        d = solve_waterplane(p, vol)
        _, cb = submerged(p, d)
        # heel to starboard (port side up); restoring if CB is further to starboard than G
        out.append(float(g_[1] - cb[1]))
    return out


def projected_area(tris, d, plane="yz", h=2.0):
    """Union area of the submerged geometry projected on a vertical plane, and its centroid."""
    t = _clip_below(tris, d)
    i0, i1 = (1, 2) if plane == "yz" else (0, 2)
    P = t[:, :, [i0, i1]]
    lo, hi = P.reshape(-1, 2).min(axis=0), P.reshape(-1, 2).max(axis=0)
    nu = int((hi[0] - lo[0]) / h) + 2
    nv = int((hi[1] - lo[1]) / h) + 2
    grid = np.zeros((nu, nv), bool)
    us = lo[0] + (np.arange(nu) + 0.5) * h
    vs = lo[1] + (np.arange(nv) + 0.5) * h
    for tri in P:
        a, b, c = tri
        den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-9:
            continue
        u0, u1 = np.searchsorted(us, [tri[:, 0].min(), tri[:, 0].max()])
        v0, v1 = np.searchsorted(vs, [tri[:, 1].min(), tri[:, 1].max()])
        if u1 <= u0 or v1 <= v0:
            continue
        U, Vv = np.meshgrid(us[u0:u1], vs[v0:v1], indexing="ij")
        l1 = ((b[1] - c[1]) * (U - c[0]) + (c[0] - b[0]) * (Vv - c[1])) / den
        l2 = ((c[1] - a[1]) * (U - c[0]) + (a[0] - c[0]) * (Vv - c[1])) / den
        inside = (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1)
        grid[u0:u1, v0:v1] |= inside
    area = grid.sum() * h * h
    U, Vv = np.meshgrid(us, vs, indexing="ij")
    cu = float(U[grid].mean()) if area else 0.0
    cv = float(Vv[grid].mean()) if area else 0.0
    return area, cu, cv


# ---------------------------------------------------------------------------
# clearance helpers
# ---------------------------------------------------------------------------
def min_dist_xy_to_origin(tris):
    """2-D distance from the pole axis (x=y=0) to the XY projection of every triangle."""
    P = tris[:, :, :2]
    a, b, c = P[:, 0], P[:, 1], P[:, 2]

    def seg(p, q):
        d = q - p
        L2 = np.maximum((d * d).sum(axis=1), 1e-12)
        t = np.clip(-(p * d).sum(axis=1) / L2, 0, 1)
        r = p + d * t[:, None]
        return np.sqrt((r * r).sum(axis=1))

    dist = np.minimum(np.minimum(seg(a, b), seg(b, c)), seg(c, a))

    def cross(o, p, q):
        return (p[:, 0] - o[:, 0]) * (q[:, 1] - o[:, 1]) - (p[:, 1] - o[:, 1]) * (q[:, 0] - o[:, 0])

    z = np.zeros_like(a)
    s1, s2, s3 = cross(a, b, z), cross(b, c, z), cross(c, a, z)
    inside = ((s1 >= 0) & (s2 >= 0) & (s3 >= 0)) | ((s1 <= 0) & (s2 <= 0) & (s3 <= 0))
    dist[inside] = 0.0
    return dist


def xy_occupancy(tris, lo, hi, h=4.0):
    nu = int((hi[0] - lo[0]) / h) + 1
    nv = int((hi[1] - lo[1]) / h) + 1
    grid = np.zeros((max(nu, 1), max(nv, 1)), bool)
    us = lo[0] + (np.arange(grid.shape[0]) + 0.5) * h
    vs = lo[1] + (np.arange(grid.shape[1]) + 0.5) * h
    for tri in tris[:, :, :2]:
        a, b, c = tri
        den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-9:
            continue
        u0, u1 = np.searchsorted(us, [tri[:, 0].min() - h, tri[:, 0].max() + h])
        v0, v1 = np.searchsorted(vs, [tri[:, 1].min() - h, tri[:, 1].max() + h])
        if u1 <= u0 or v1 <= v0:
            continue
        U, Vv = np.meshgrid(us[u0:u1], vs[v0:v1], indexing="ij")
        l1 = ((b[1] - c[1]) * (U - c[0]) + (c[0] - b[0]) * (Vv - c[1])) / den
        l2 = ((c[1] - a[1]) * (U - c[0]) + (a[0] - c[0]) * (Vv - c[1])) / den
        grid[u0:u1, v0:v1] |= (l1 >= -0.02) & (l2 >= -0.02) & (l1 + l2 <= 1.02)
    return grid


def voxel_inside(shells, lo, hi, h=2.0):
    """Boolean occupancy of the union of closed shells on a grid (scanline parity along z)."""
    xs = lo[0] + (np.arange(int((hi[0] - lo[0]) / h) + 1) + 0.5) * h + 1.3e-4
    ys = lo[1] + (np.arange(int((hi[1] - lo[1]) / h) + 1) + 0.5) * h + 1.7e-4
    zs = lo[2] + (np.arange(int((hi[2] - lo[2]) / h) + 1) + 0.5) * h + 1.1e-4
    occ = np.zeros((len(xs), len(ys), len(zs)), bool)
    for s in shells:
        t = s.triangles()
        tri = s.V[t]
        smin, smax = tri.reshape(-1, 3).min(0), tri.reshape(-1, 3).max(0)
        if (smax < lo).any() or (smin > hi).any():
            continue
        cols, zc = [], []
        for T3 in tri:
            a, b, c = T3
            den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(den) < 1e-12:
                continue
            i0, i1 = np.searchsorted(xs, [T3[:, 0].min(), T3[:, 0].max()])
            j0, j1 = np.searchsorted(ys, [T3[:, 1].min(), T3[:, 1].max()])
            if i1 <= i0 or j1 <= j0:
                continue
            X, Y = np.meshgrid(xs[i0:i1], ys[j0:j1], indexing="ij")
            l1 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / den
            l2 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / den
            l3 = 1 - l1 - l2
            m = (l1 >= 0) & (l2 >= 0) & (l3 >= 0)
            if not m.any():
                continue
            Z = l1 * a[2] + l2 * b[2] + l3 * c[2]
            ii, jj = np.nonzero(m)
            cols.append((ii + i0) * len(ys) + (jj + j0))
            zc.append(Z[m])
        if not cols:
            continue
        cols = np.concatenate(cols)
        zc = np.concatenate(zc)
        order = np.lexsort((zc, cols))
        cols, zc = cols[order], zc[order]
        uc, start = np.unique(cols, return_index=True)
        ends = np.r_[start[1:], len(cols)]
        for col, s0, s1 in zip(uc, start, ends):
            zz = zc[s0:s1]
            if len(zz) < 2:
                continue
            cnt_above = len(zz) - np.searchsorted(zz, zs, side="right")
            inside = (cnt_above % 2) == 1
            occ[col // len(ys), col % len(ys)] |= inside
    return occ


def bbox(shells):
    V = np.vstack([s.V for s in shells])
    return V.min(0), V.max(0)
