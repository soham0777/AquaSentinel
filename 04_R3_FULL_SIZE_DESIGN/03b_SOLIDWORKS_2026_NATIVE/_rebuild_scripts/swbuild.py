"""Build native, feature-based SOLIDWORKS parts from prims.pkl (exact feature descriptions of the R3 parts).
Usage: python swbuild.py <out_dir> [PID ...]"""
import math
import os
import pickle
import sys
import time
import json

import numpy as np
import pythoncom
import win32com.client
from win32com.client import VARIANT

HERE = os.path.dirname(os.path.abspath(__file__))
sw = win32com.client.Dispatch("SldWorks.Application")
NOTHING = VARIANT(pythoncom.VT_DISPATCH, None)
TPL = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\templates\Part.PRTDOT"
M = 0.001
PLANES = {"z": "Front Plane", "y": "Top Plane", "x": "Right Plane"}

MATS = {  # generator material key -> (SOLIDWORKS library material, label kept as a custom property)
    "HDPE_YELLOW": "PE High Density", "AL6061": "6061-T6 (SS)", "SS316L": "AISI Type 316L stainless steel",
    "SS_BRUSHED": "AISI 316 Annealed Stainless Steel Bar (SS)", "UHMW": "PE High Density",
    "POM_BLACK": "POM Acetal Copolymer", "PE_PIPE": "PE High Density", "PC_GREY": "ABS PC", "PC_DARK": "ABS PC",
    "RUBBER": "EPDM", "PV_CELL": "Glass", "PCB": "E-Glass Fiber", "BATTERY": None, "WHITE_PE": "PE High Density",
    "TUBING": "PVC 0.007 Plasticized", "CABLE": "PVC Rigid", "BEACON_LENS": "ABS PC", "PROBE_PH": "ABS",
    "PROBE_EC": "ABS", "PROBE_DO": "ABS", "PROBE_TU": "ABS",
}


def cv(x):
    import inspect
    return x() if inspect.ismethod(x) or inspect.isfunction(x) else x


def arr(vals):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(v) for v in vals])


def dispatch_arr(objs):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, list(objs))


# ----------------------------------------------------------------------------- 2D fitting
def _circ3(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        return None
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return ux, uy, math.hypot(ax - ux, ay - uy)


def _dedupe(pts, closed):
    out = []
    for p in pts:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 1e-6:
            out.append((float(p[0]), float(p[1])))
    if closed and len(out) > 2 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) < 1e-6:
        out.pop()
    return out


def fit(pts, closed=True, tol=2e-3, straight=False):
    """Polyline -> exact entities: ('circle',c,r) | ('line',p,q) | ('arc',p,m,q). Runs of >=4 concyclic points
    become one true arc; collinear runs become one line."""
    P = _dedupe(pts, closed)
    n = len(P)
    if straight:
        return [("line", P[i], P[(i + 1) % n]) for i in range(n if closed else n - 1)]
    if closed and n >= 8:
        c = _circ3(P[0], P[n // 3], P[2 * n // 3])
        if c and c[2] < 1e5 and all(abs(math.hypot(p[0] - c[0], p[1] - c[1]) - c[2]) < tol for p in P):
            return [("circle", (c[0], c[1]), c[2])]
    if closed:  # start at the beginning of the longest segment so no arc is split by the seam
        L = [math.hypot(P[(i + 1) % n][0] - P[i][0], P[(i + 1) % n][1] - P[i][1]) for i in range(n)]
        k = int(np.argmax(L))
        P = P[k:] + P[:k] + [P[k]]
    m = len(P)
    ents, i = [], 0
    while i < m - 1:
        best = None
        j = i + 3
        while j < m:
            c = _circ3(P[i], P[(i + j) // 2], P[j])
            if not c or c[2] > 2e4:
                break
            seg = P[i:j + 1]
            if not all(abs(math.hypot(p[0] - c[0], p[1] - c[1]) - c[2]) < tol for p in seg):
                break
            # all turning the same way
            cr = [(seg[t + 1][0] - seg[t][0]) * (seg[t + 2][1] - seg[t + 1][1]) -
                  (seg[t + 1][1] - seg[t][1]) * (seg[t + 2][0] - seg[t + 1][0]) for t in range(len(seg) - 2)]
            if not (all(v > 1e-12 for v in cr) or all(v < -1e-12 for v in cr)):
                break
            ch = [math.hypot(seg[t + 1][0] - seg[t][0], seg[t + 1][1] - seg[t][1]) for t in range(len(seg) - 1)]
            if max(ch) > 1.02 * min(ch) + 1e-6 or max(ch) > 2 * c[2] * math.sin(math.radians(24)):
                break
            best = j
            j += 1
        if best is not None:
            seg = P[i:best + 1]
            ents.append(("arc", seg[0], seg[len(seg) // 2], seg[-1]))
            i = best
        else:
            ents.append(("line", P[i], P[i + 1]))
            i += 1
    # merge collinear consecutive lines
    out = []
    for e in ents:
        if out and e[0] == "line" and out[-1][0] == "line":
            a, b = out[-1][1], out[-1][2]
            q = e[2]
            cr = (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0])
            if abs(cr) < 1e-6 * max(1.0, math.hypot(q[0] - a[0], q[1] - a[1])) ** 2:
                out[-1] = ("line", a, q)
                continue
        out.append(e)
    return out


# ----------------------------------------------------------------------------- transforms
def euler_zyx(R):
    """R = Rz(c) Ry(b) Rx(a)"""
    b = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    if abs(math.cos(b)) > 1e-9:
        a = math.atan2(R[2, 1], R[2, 2])
        c = math.atan2(R[1, 0], R[0, 0])
    else:
        a = math.atan2(-R[1, 2], R[1, 1])
        c = 0.0
    return a, b, c


# ----------------------------------------------------------------------------- part builder
class NPart:
    def __init__(self, pid, info):
        self.pid, self.info = pid, info
        self.d = sw.NewDocument(TPL, 0, 0, 0)
        self.d.Extension.SetUserPreferenceInteger(263, 0, 5)  # MMGS
        self.sm, self.fm = self.d.SketchManager, self.d.FeatureManager
        self.sm.AddToDB = True
        self.sm.DisplayWhenAdded = False
        self.planes = {}
        self.log = []
        self.counter = {}

    def nm(self, base):
        self.counter[base] = self.counter.get(base, 0) + 1
        return f"{base}{self.counter[base]}"

    # planes / sketches
    def plane(self, axis, off):
        if abs(off) < 1e-9:
            return PLANES[axis]
        key = (axis, round(off, 4))
        if key not in self.planes:
            self.d.ClearSelection2(True)
            self.d.Extension.SelectByID2(PLANES[axis], "PLANE", 0, 0, 0, False, 0, NOTHING, 0)
            pl = self.fm.InsertRefPlane(8 | (256 if off < 0 else 0), abs(off) * M, 0, 0, 0, 0)
            name = f"Plane {axis.upper()}={off:g}"
            pl.Name = name
            self.planes[key] = name
        return self.planes[key]

    def open_sketch(self, axis, off=0.0):
        name = self.plane(axis, off)
        self.d.ClearSelection2(True)
        self.d.Extension.SelectByID2(name, "PLANE", 0, 0, 0, False, 0, NOTHING, 0)
        self.sm.InsertSketch(True)
        self.xf = self.sm.ActiveSketch.ModelToSketchTransform.ArrayData
        self.ax, self.w = axis, off

    def sp(self, u, v):
        if self.ax == "z":
            x, y, z = u, v, self.w
        elif self.ax == "y":
            x, y, z = u, self.w, v
        else:
            x, y, z = self.w, u, v
        a = self.xf
        x, y, z = x * M, y * M, z * M
        return (a[12] * (x * a[0] + y * a[3] + z * a[6]) + a[9], a[12] * (x * a[1] + y * a[4] + z * a[7]) + a[10])

    def draw(self, ents):
        for e in ents:
            if e[0] == "circle":
                p = self.sp(*e[1])
                self.sm.CreateCircleByRadius(p[0], p[1], 0, e[2] * M)
            elif e[0] == "line":
                p, q = self.sp(*e[1]), self.sp(*e[2])
                self.sm.CreateLine(p[0], p[1], 0, q[0], q[1], 0)
            else:
                p, m, q = self.sp(*e[1]), self.sp(*e[2]), self.sp(*e[3])
                self.sm.Create3PointArc(p[0], p[1], 0, q[0], q[1], 0, m[0], m[1], 0)

    def close_sketch(self, name, dims=True):
        if dims:  # auto-dimension + relations so the sketch is driven by editable dimensions
            try:
                self.sm.FullyDefineSketch(True, True, 1023, True, 1, NOTHING, 1, NOTHING, 1, 1)
            except Exception:
                pass
        self.sm.InsertSketch(True)
        f = self.d.FeatureByPositionReverse(0)
        try:
            f.Name = name
        except Exception:
            pass
        self.d.ClearSelection2(True)
        f.Select2(False, 0)
        return f

    def bodies(self):
        return list(self.d.GetBodies2(0, False) or [])

    def _named(self, f, name):
        if f is None:
            self.log.append("FAILED " + name)
            return None
        try:
            f.Name = name
        except Exception:
            pass
        return f

    # features
    def extrude(self, a0, a1, name):
        depth = a1 - a0
        st = 3 if abs(a0) > 1e-9 else 0
        f = self.fm.FeatureExtrusion3(True, False, False, 0, 0, abs(depth) * M, 0, False, False, False, False, 0, 0,
                                      False, False, False, False, False, True, True, st, abs(a0) * M, a0 < 0)
        return self._named(f, name)

    def revolve(self, ang_deg, name):
        f = self.fm.FeatureRevolve2(True, True, False, False, False, False, 0, 0, math.radians(ang_deg), 0, False,
                                    False, 0, 0, 0, 0, 0, False, True, True)
        return self._named(f, name)

    def move_body(self, body, tr=(0, 0, 0), rot=(0, 0, 0), name="Move"):
        self.d.ClearSelection2(True)
        ok = body.Select2(False, NOTHING) if False else self.d.Extension.SelectByID2(body.Name, "SOLIDBODY", 0, 0, 0, False, 1, NOTHING, 0)
        dist = math.sqrt(sum(t * t for t in tr)) * M
        # measured: the three angle arguments act about Z, Y, X in that order
        f = self.fm.InsertMoveCopyBody2(tr[0] * M, tr[1] * M, tr[2] * M, 0, 0, 0, 0, rot[2], rot[1], rot[0], False, 1)
        return self._named(f, name)

    def fillet(self, pts, r, name):
        self.d.ClearSelection2(True)
        ok = 0
        for (x, y, z) in pts:
            if self.d.Extension.SelectByID2("", "EDGE", x * M, y * M, z * M, True, 1, NOTHING, 0):
                ok += 1
        if not ok:
            self.log.append(f"FAILED {name}: no edges")
            return None
        fd = self.fm.CreateDefinition(1)
        fd.Initialize(0)
        fd.DefaultRadius = r * M
        try:
            fd.TangentPropagation = True
        except Exception:
            pass
        f = self.fm.CreateFeature(fd)
        return self._named(f, name)

    # ------------------------------------------------------------------ prims
    def prim(self, kind, data, Mx, label):
        R, t = Mx[:3, :3], Mx[:3, 3]
        rot_id = np.allclose(R, np.eye(3), atol=1e-9)
        # rotations about z only are folded into the 2D loops of z-extrusions
        if kind == "ext" and data["axis"] == "z" and np.allclose(R[2], [0, 0, 1], atol=1e-9) and not rot_id:
            data = dict(data)
            R2 = R[:2, :2]
            data["loops"] = [l @ R2.T for l in data.get("loops", [])]
            data["circles"] = [tuple(list(R2 @ np.array([c[0], c[1]])) + [c[2]]) for c in data.get("circles", [])]
            rot_id = True
        before = {b.Name for b in self.bodies()}
        fold = t if rot_id else np.zeros(3)
        getattr(self, "p_" + kind)(data, fold, label)
        if not rot_id:
            a, b_, c = euler_zyx(R)
            steps = []
            for k, ang in enumerate((a, b_, c)):
                if abs(ang) > 1e-9:
                    rv = [0, 0, 0]; rv[k] = ang
                    steps.append(dict(rot=rv, name=f"{label} rotate "))
            if np.linalg.norm(t) > 1e-9:
                steps.append(dict(tr=t, name=f"{label} place "))
            for st in steps:  # body names change after each move, so look the new body up every time
                for body in [b for b in self.bodies() if b.Name not in before]:
                    self.move_body(body, rot=st.get("rot", (0, 0, 0)), tr=st.get("tr", (0, 0, 0)), name=self.nm(st["name"]))

    def p_ext(self, data, t, label):
        ax = data["axis"]
        iu, iv, iw = {"z": (0, 1, 2), "y": (0, 2, 1), "x": (1, 2, 0)}[ax]
        du, dv, dw = t[iu], t[iv], t[iw]
        self.open_sketch(ax, 0.0)
        for l in data.get("loops", []):
            l = np.asarray(l) + [du, dv]
            self.draw(fit(l, True, straight=data.get("straight", False)))
        for (cx, cy, r) in data.get("circles", []):
            self.draw([("circle", (cx + du, cy + dv), r)])
        self.close_sketch(self.nm(f"{label} sketch "))
        self.extrude(data["a0"] + dw, data["a1"] + dw, self.nm(f"{label} "))

    def p_rev(self, data, t, label):
        loop = np.asarray(data["loop"], float)
        a0, a1 = data["a0"], data["a1"]
        self.open_sketch("y", t[1])  # XZ plane through the axis
        pts = np.c_[loop[:, 0] + t[0], loop[:, 1] + t[2]]
        self.draw(fit(pts, True))
        zs = loop[:, 1] + t[2]
        p, q = self.sp(t[0], zs.min() - 5), self.sp(t[0], zs.max() + 5)
        self.sm.CreateCenterLine(p[0], p[1], 0, q[0], q[1], 0)
        self.close_sketch(self.nm(f"{label} profile "))
        before = {b.Name for b in self.bodies()}
        self.revolve(a1 - a0, self.nm(f"{label} "))
        if abs(a0) > 1e-9 and abs((a1 - a0) - 360) > 1e-6:
            for body in [b for b in self.bodies() if b.Name not in before]:
                if np.allclose(t, 0):
                    self.move_body(body, rot=(0, 0, math.radians(a0)), name=self.nm(f"{label} index "))
                else:
                    self.move_body(body, tr=-t, name=self.nm("tmp "))
                    self.move_body(body, rot=(0, 0, math.radians(a0)), name=self.nm(f"{label} index "))
                    self.move_body(body, tr=t, name=self.nm("tmp "))

    def p_rbox(self, data, t, label):
        sx, sy, sz, rs, re_ = data["sx"], data["sy"], data["sz"], data["r_side"], data["r_edge"]
        cx, cy, cz = np.array(data["center"]) + t
        self.open_sketch("z", 0.0)
        r = max(0.0, min(rs, sx / 2 - 0.05, sy / 2 - 0.05))
        x0, x1, y0, y1 = cx - sx / 2, cx + sx / 2, cy - sy / 2, cy + sy / 2
        if r > 0.05:
            k = r * (1 - math.sqrt(0.5))
            ents = [("line", (x0 + r, y0), (x1 - r, y0)), ("arc", (x1 - r, y0), (x1 - k, y0 + k), (x1, y0 + r)),
                    ("line", (x1, y0 + r), (x1, y1 - r)), ("arc", (x1, y1 - r), (x1 - k, y1 - k), (x1 - r, y1)),
                    ("line", (x1 - r, y1), (x0 + r, y1)), ("arc", (x0 + r, y1), (x0 + k, y1 - k), (x0, y1 - r)),
                    ("line", (x0, y1 - r), (x0, y0 + r)), ("arc", (x0, y0 + r), (x0 + k, y0 + k), (x0 + r, y0))]
        else:
            ents = fit([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], True, straight=True)
        self.draw(ents)
        self.close_sketch(self.nm(f"{label} sketch "))
        self.extrude(cz - sz / 2, cz + sz / 2, self.nm(f"{label} "))
        if re_ > 0.05:
            z0, z1 = cz - sz / 2, cz + sz / 2
            pts = []
            for z in (z0, z1):
                pts += [(cx, y0, z), (cx, y1, z), (x0, cy, z), (x1, cy, z)]
            self.fillet(pts, min(re_, sz / 2 - 0.1), self.nm(f"{label} edge fillet "))

    def p_pipe(self, data, t, label):
        path = np.asarray(data["path"], float) + t
        r, fr = data["r"], data["fillet"]
        if len(path) == 2:  # straight: a cylinder built on its own axis
            self._cyl_between(path[0], path[1], r, label)
            return
        self.sm.Insert3DSketch(True)
        segs = []
        for a, b in zip(path[:-1], path[1:]):
            segs.append(self.sm.CreateLine(a[0] * M, a[1] * M, a[2] * M, b[0] * M, b[1] * M, b[2] * M))
        if fr > 0:
            for p in path[1:-1]:
                self.d.ClearSelection2(True)
                if self.d.Extension.SelectByID2("", "SKETCHPOINT", p[0] * M, p[1] * M, p[2] * M, False, 0, NOTHING, 0):
                    self.sm.CreateFillet(min(fr, 0.45 * self._seglen(path, p)) * M, 1)
        path_f = self.close_sketch(self.nm(f"{label} path "), dims=False)
        sd = self.fm.CreateDefinition(17)
        sd.CircularProfile = True
        sd.CircularProfileDiameter = 2 * r * M
        sd.Path = path_f
        try:
            sd.Merge = False
        except Exception:
            pass
        f = self.fm.CreateFeature(sd)
        self._named(f, self.nm(f"{label} "))

    @staticmethod
    def _seglen(path, p):
        i = int(np.argmin(np.linalg.norm(path - p, axis=1)))
        return min(np.linalg.norm(path[i] - path[i - 1]), np.linalg.norm(path[i + 1] - path[i]))

    def _cyl_between(self, a, b, r, label):
        d = b - a
        L = float(np.linalg.norm(d))
        u = d / L
        # local frame: z along the pipe
        z = np.array([0, 0, 1.0])
        Mx = np.eye(4)
        if not np.allclose(u, z):
            if np.allclose(u, -z):
                Mx[:3, :3] = np.diag([1, -1, -1])
            else:
                ax = np.cross(z, u); ax /= np.linalg.norm(ax)
                ang = math.acos(max(-1, min(1, float(z @ u))))
                K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
                Mx[:3, :3] = np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K
        Mx[:3, 3] = a
        self.prim("ext", dict(circles=[(0, 0, r)], loops=[], axis="z", a0=0.0, a1=L), Mx, label)

    def p_loft(self, data, t, label):
        raise NotImplementedError("loft handled by the hull builder")

    # ------------------------------------------------------------------ finish
    def combine(self):
        bs = self.bodies()
        if len(bs) < 2:
            return len(bs)
        self.d.ClearSelection2(True)
        f = self.fm.InsertCombineFeature(15903, NOTHING, dispatch_arr(bs))
        if f is not None:
            f.Name = "Combine (weld / assembly of features)"
        return len(self.bodies())

    def finish(self, path):
        info = self.info
        mat = MATS.get(info["mat"])
        if mat:
            self.d.SetMaterialPropertyName2("", "SOLIDWORKS Materials", mat)
        cpm = self.d.Extension.CustomPropertyManager("")
        for k, v in (("PartNo", self.pid), ("Description", info["name"]), ("Material_spec", info["mat"]),
                     ("Process", info["process"]), ("Notes", info["desc"]), ("Kind", info["kind"]),
                     ("Source", "AquaSentinel R3 generator (parts.py) rebuilt as native SOLIDWORKS features")):
            cpm.Add3(k, 30, str(v), 2)
        self.d.ForceRebuild3(False)
        e = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        self.d.Extension.SaveAs3(path, 0, 1, NOTHING, NOTHING, e, w)
        return e.value

    def measure(self):
        self.d.ForceRebuild3(False)
        bs = self.bodies()
        box, faces, ftypes = None, 0, {}
        for b in bs:
            bb = b.GetBodyBox()
            box = list(bb) if box is None else [min(box[i], bb[i]) for i in range(3)] + [max(box[i], bb[i]) for i in range(3, 6)]
            for f in b.GetFaces() or []:
                faces += 1
                s = cv(f.GetSurface)
                typ = "plane" if cv(s.IsPlane) else "cyl" if cv(s.IsCylinder) else "cone" if cv(s.IsCone) else \
                      "torus" if cv(s.IsTorus) else "sphere" if cv(s.IsSphere) else "other"
                ftypes[typ] = ftypes.get(typ, 0) + 1
        mp = self.d.Extension.CreateMassProperty
        return dict(volume_cm3=round(mp.Volume * 1e6, 2), mass_kg=round(mp.Mass, 3), bodies=len(bs), faces=faces,
                    face_types=ftypes, bbox_mm=[round(v * 1000, 1) for v in (box or [])])


def measure_ref(path):
    e = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    d = sw.OpenDoc6(path, 1, 1 | 2, "", e, w)
    if d is None:
        return None
    bs = list(d.GetBodies2(0, False) or [])
    box, faces = None, 0
    for b in bs:
        bb = b.GetBodyBox()
        faces += b.GetFaceCount()
        box = list(bb) if box is None else [min(box[i], bb[i]) for i in range(3)] + [max(box[i], bb[i]) for i in range(3, 6)]
    mp = d.Extension.CreateMassProperty
    out = dict(volume_cm3=round(mp.Volume * 1e6, 2), bodies=len(bs), faces=faces, bbox_mm=[round(v * 1000, 1) for v in (box or [])])
    sw.CloseDoc(d.GetTitle)
    return out


SRC_DIR = r"C:\Users\dell\OneDrive\Desktop\AquaSentinel\04_R3_FULL_SIZE_DESIGN\03_SOLIDWORKS_2026_assembly_for_manual"


def ref_file(pid):
    for f in os.listdir(SRC_DIR):
        if f.startswith(pid + "_") and f.endswith(".SLDPRT"):
            return f
    return None


def build_one(pid, info, out_dir, builder=None):
    t0 = time.time()
    p = NPart(pid, info)
    if builder:
        builder(p, info)
    else:
        for k, (kind, data, Mx) in enumerate(info["prims"]):
            try:
                p.prim(kind, data, Mx, kind_label(kind))
            except Exception as ex:
                p.log.append(f"prim {k} {kind}: {ex!r}"[:300])
    nb = p.combine()
    fn = ref_file(pid)
    path = os.path.join(out_dir, fn)
    err = p.finish(path)
    meas = p.measure()
    sw.CloseDoc(p.d.GetTitle)
    ref = measure_ref(os.path.join(SRC_DIR, fn))
    return dict(pid=pid, file=fn, save_err=err, native=meas, ref=ref, log=p.log, secs=round(time.time() - t0, 1))


def kind_label(kind):
    return {"ext": "Extrude", "rev": "Revolve", "rbox": "Block", "pipe": "Pipe", "loft": "Loft"}[kind]


if __name__ == "__main__":
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    data = pickle.load(open(os.path.join(HERE, "prims.pkl"), "rb"))
    pids = sys.argv[2:] or sorted(data["parts"])
    import hull
    res = []
    for pid in pids:
        info = data["parts"][pid]
        r = build_one(pid, info, out_dir, hull.build if pid == "AS3-201" else None)
        res.append(r)
        n, f = r["native"], r["ref"] or {}
        print(pid, "vol", n["volume_cm3"], "ref", f.get("volume_cm3"), "bbox", n["bbox_mm"], "ref", f.get("bbox_mm"),
              "faces", n["faces"], "ref", f.get("faces"), n["face_types"], r["log"][:3], r["secs"], "s", flush=True)
    json.dump(res, open(os.path.join(out_dir, "_build_report.json"), "w"), indent=1)
