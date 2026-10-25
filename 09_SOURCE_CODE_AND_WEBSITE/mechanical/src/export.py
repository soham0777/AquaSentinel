"""
Exporters: binary STL, glTF 2.0 binary (GLB) with a node tree, and
STEP AP214 (planar-face ADVANCED_BREP solids, with a real assembly structure:
one PRODUCT per part, placed by NEXT_ASSEMBLY_USAGE_OCCURRENCE).
"""
import json
import math
import struct
import datetime
import numpy as np

from geom import triangulate_polygon


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def shells_to_tris(shells):
    Vs, Fs, off = [], [], 0
    for s in shells:
        t = s.triangles()
        Vs.append(s.V)
        Fs.append(t + off)
        off += len(s.V)
    if not Vs:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64)
    return np.vstack(Vs), np.vstack(Fs)


def creased_normals(V, F, crease_deg=32.0):
    """Split vertices where adjacent faces meet at more than `crease_deg`."""
    if len(F) == 0:
        return V.astype(np.float32), np.zeros_like(V, dtype=np.float32), F.astype(np.uint32)
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    fn = np.cross(b - a, c - a)
    area2 = np.linalg.norm(fn, axis=1)
    fnu = fn / np.maximum(area2[:, None], 1e-15)
    cv = F.ravel()
    cf = np.repeat(np.arange(len(F)), 3)
    order = np.argsort(cv, kind="stable")
    cv_s, cf_s = cv[order], cf[order]
    starts = np.r_[0, np.flatnonzero(np.diff(cv_s)) + 1]
    sizes = np.diff(np.r_[starts, len(cv_s)])
    gid = np.repeat(np.arange(len(starts)), sizes)
    k = sizes[gid]
    I = np.repeat(np.arange(len(cv_s)), k)
    within = np.arange(len(I)) - np.repeat(np.cumsum(k) - k, k)
    J = starts[gid[I]] + within
    cosang = math.cos(math.radians(crease_deg))
    dots = np.einsum("ij,ij->i", fnu[cf_s[I]], fnu[cf_s[J]])
    m = dots > cosang
    acc = np.zeros((len(cv_s), 3))
    np.add.at(acc, I[m], fn[cf_s[J[m]]])
    nrm = acc / np.maximum(np.linalg.norm(acc, axis=1)[:, None], 1e-15)
    corner_n = np.empty_like(nrm)
    corner_n[order] = nrm
    # weld identical (vertex, normal) corners
    key = np.c_[cv[:, None].astype(np.float64), np.round(corner_n, 4)]
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.ravel()
    newV = V[uniq[:, 0].astype(np.int64)].astype(np.float32)
    newN = uniq[:, 1:4].astype(np.float32)
    nl = np.linalg.norm(newN, axis=1)
    newN = newN / np.maximum(nl[:, None], 1e-9)
    newF = inv.reshape(-1, 3).astype(np.uint32)
    return newV, newN.astype(np.float32), newF


# ---------------------------------------------------------------------------
# STL
# ---------------------------------------------------------------------------
def write_stl(path, shells, name="AquaSentinel"):
    V, F = shells_to_tris(shells)
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    n = np.cross(b - a, c - a)
    n /= np.maximum(np.linalg.norm(n, axis=1)[:, None], 1e-15)
    rec = np.zeros(len(F), dtype=[("n", "<f4", 3), ("a", "<f4", 3), ("b", "<f4", 3), ("c", "<f4", 3), ("attr", "<u2")])
    rec["n"], rec["a"], rec["b"], rec["c"] = n, a, b, c
    with open(path, "wb") as f:
        f.write(f"AquaSentinel R3 {name} (mm)".encode("ascii", "replace")[:80].ljust(80, b" "))
        f.write(struct.pack("<I", len(F)))
        f.write(rec.tobytes())
    return len(F)


# ---------------------------------------------------------------------------
# GLB
# ---------------------------------------------------------------------------
class GLBWriter:
    def __init__(self):
        self.bin = bytearray()
        self.accessors, self.views, self.meshes, self.materials, self.nodes = [], [], [], [], []
        self._mat_index = {}
        self._mesh_index = {}

    def _view(self, data, target):
        while len(self.bin) % 4:
            self.bin += b"\0"
        off = len(self.bin)
        self.bin += data
        self.views.append({"buffer": 0, "byteOffset": off, "byteLength": len(data), "target": target})
        return len(self.views) - 1

    def material(self, name, spec):
        if name in self._mat_index:
            return self._mat_index[name]
        lin = [((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92 for c in spec["color"]]  # sRGB -> linear
        m = {"name": name, "pbrMetallicRoughness": {
            "baseColorFactor": lin + [spec.get("alpha", 1.0)],
            "metallicFactor": spec.get("metal", 0.0), "roughnessFactor": spec.get("rough", 0.6)}}
        if spec.get("emissive"):
            m["emissiveFactor"] = [((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92 for c in spec["emissive"]]
        if spec.get("alpha", 1.0) < 1.0:
            m["alphaMode"] = "BLEND"
            m["doubleSided"] = True
        self.materials.append(m)
        self._mat_index[name] = len(self.materials) - 1
        return self._mat_index[name]

    def mesh(self, key, shells, mat_index, crease=32.0):
        if key in self._mesh_index:
            return self._mesh_index[key]
        V, F = shells_to_tris(shells)
        V, N, F = creased_normals(V, F, crease)
        pv = self._view(V.astype("<f4").tobytes(), 34962)
        self.accessors.append({"bufferView": pv, "componentType": 5126, "count": len(V), "type": "VEC3",
                               "min": V.min(axis=0).tolist(), "max": V.max(axis=0).tolist()})
        pa = len(self.accessors) - 1
        nv = self._view(N.astype("<f4").tobytes(), 34962)
        self.accessors.append({"bufferView": nv, "componentType": 5126, "count": len(N), "type": "VEC3"})
        na = len(self.accessors) - 1
        iv = self._view(F.astype("<u4").ravel().tobytes(), 34963)
        self.accessors.append({"bufferView": iv, "componentType": 5125, "count": int(F.size), "type": "SCALAR"})
        ia = len(self.accessors) - 1
        self.meshes.append({"name": key, "primitives": [{"attributes": {"POSITION": pa, "NORMAL": na},
                                                          "indices": ia, "material": mat_index}]})
        self._mesh_index[key] = len(self.meshes) - 1
        return self._mesh_index[key]

    def node(self, name, matrix=None, mesh=None, children=None, extras=None):
        n = {"name": name}
        if matrix is not None and not np.allclose(matrix, np.eye(4)):
            n["matrix"] = np.asarray(matrix, float).T.ravel().tolist()  # column-major
        if mesh is not None:
            n["mesh"] = mesh
        if children:
            n["children"] = children
        if extras:
            n["extras"] = extras
        self.nodes.append(n)
        return len(self.nodes) - 1

    def write(self, path, root_nodes, extras=None):
        while len(self.bin) % 4:
            self.bin += b"\0"
        gltf = {"asset": {"version": "2.0", "generator": "AquaSentinel R3 design build (Python)"},
                "scene": 0, "scenes": [{"nodes": root_nodes, "extras": extras or {}}],
                "nodes": self.nodes, "meshes": self.meshes, "materials": self.materials,
                "accessors": self.accessors, "bufferViews": self.views,
                "buffers": [{"byteLength": len(self.bin)}]}
        js = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
        js += b" " * ((4 - len(js) % 4) % 4)
        total = 12 + 8 + len(js) + 8 + len(self.bin)
        with open(path, "wb") as f:
            f.write(struct.pack("<4sII", b"glTF", 2, total))
            f.write(struct.pack("<I4s", len(js), b"JSON"))
            f.write(js)
            f.write(struct.pack("<I4s", len(self.bin), b"BIN\0"))
            f.write(bytes(self.bin))
        return total


# ---------------------------------------------------------------------------
# STEP AP214
# ---------------------------------------------------------------------------
def _real(x):
    s = f"{float(x):.5f}"
    s = s.rstrip("0")
    if s.endswith("."):
        s = s  # keep trailing dot: valid STEP real
    if s in ("-0.", "-0"):
        s = "0."
    return s


def _str(s):
    return "'" + str(s).replace("'", "''").encode("ascii", "replace").decode("ascii") + "'"


class StepWriter:
    def __init__(self, name, author="AquaSentinel team", org="Sanjivani University"):
        self.lines = []
        self.n = 0
        self.name = name
        self.author, self.org = author, org
        self.styled = []
        self._colour = {}

    def add(self, text):
        self.n += 1
        self.lines.append(f"#{self.n}={text};")
        return self.n

    # -- context ------------------------------------------------------------
    def context(self):
        self.app_ctx = self.add("APPLICATION_CONTEXT('core data for automotive mechanical design processes')")
        self.add(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#{self.app_ctx})")
        self.prod_ctx = self.add(f"PRODUCT_CONTEXT('',#{self.app_ctx},'mechanical')")
        self.pd_ctx = self.add(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{self.app_ctx},'design')")
        lu = self.add("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
        au = self.add("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
        su = self.add("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
        unc = self.add(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-04),#{lu},'distance_accuracy_value','confusion accuracy')")
        self.geo_ctx = self.add(
            f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc}))"
            f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu},#{au},#{su}))REPRESENTATION_CONTEXT('Context','3D Context with UNIT and UNCERTAINTY'))")
        self.products = []

    def point(self, p):
        return self.add(f"CARTESIAN_POINT('',({_real(p[0])},{_real(p[1])},{_real(p[2])}))")

    def direction(self, d):
        d = np.asarray(d, float)
        d = d / np.linalg.norm(d)
        return self.add(f"DIRECTION('',({_real(d[0])},{_real(d[1])},{_real(d[2])}))")

    def axis(self, origin=(0, 0, 0), z=(0, 0, 1), x=(1, 0, 0)):
        o = self.point(origin)
        zz = self.direction(z)
        xx = self.direction(x)
        return self.add(f"AXIS2_PLACEMENT_3D('',#{o},#{zz},#{xx})")

    def product(self, pid, name, desc=""):
        p = self.add(f"PRODUCT({_str(pid)},{_str(name)},{_str(desc)},(#{self.prod_ctx}))")
        pdf = self.add(f"PRODUCT_DEFINITION_FORMATION('','',#{p})")
        pd = self.add(f"PRODUCT_DEFINITION('design','',#{pdf},#{self.pd_ctx})")
        pds = self.add(f"PRODUCT_DEFINITION_SHAPE('','',#{pd})")
        self.products.append(p)
        return p, pd, pds

    def colour(self, rgb):
        key = tuple(round(c, 3) for c in rgb)
        if key in self._colour:
            return self._colour[key]
        c = self.add(f"COLOUR_RGB('',{_real(key[0])},{_real(key[1])},{_real(key[2])})")
        fasc = self.add(f"FILL_AREA_STYLE_COLOUR('',#{c})")
        fas = self.add(f"FILL_AREA_STYLE('',(#{fasc}))")
        ssfa = self.add(f"SURFACE_STYLE_FILL_AREA(#{fas})")
        sss = self.add(f"SURFACE_SIDE_STYLE('',(#{ssfa}))")
        ssu = self.add(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss})")
        psa = self.add(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu}))")
        self._colour[key] = psa
        return psa

    # -- geometry -----------------------------------------------------------
    def brep(self, shell, rgb=None):
        V = shell.V
        vp = {}
        cp_cache = {}

        def vertex(i):
            if i not in vp:
                cp = self.point(V[i])
                cp_cache[i] = cp
                vp[i] = self.add(f"VERTEX_POINT('',#{cp})")
            return vp[i]

        edges = {}

        def edge(a, b):
            k = (a, b) if a < b else (b, a)
            if k not in edges:
                p0, p1 = V[k[0]], V[k[1]]
                d = p1 - p0
                L = float(np.linalg.norm(d))
                va, vb = vertex(k[0]), vertex(k[1])
                dr = self.direction(d)
                vec = self.add(f"VECTOR('',#{dr},{_real(L)})")
                ln = self.add(f"LINE('',#{cp_cache[k[0]]},#{vec})")
                edges[k] = self.add(f"EDGE_CURVE('',#{va},#{vb},#{ln},.T.)")
            return edges[k], (a, b) == k

        # planar polygons; non-planar ones are split into triangles
        polys = []
        for p in shell.P:
            if len(p) > 3:
                pts = V[list(p)]
                n = _newell(pts)
                if n is None:
                    polys += triangulate_polygon(V, p)
                    continue
                dev = np.abs((pts - pts.mean(axis=0)) @ n).max()
                if dev > 1e-3:
                    polys += triangulate_polygon(V, p)
                    continue
            polys.append(p)

        faces = []
        for p in polys:
            pts = V[list(p)]
            n = _newell(pts)
            if n is None:
                continue
            oes = []
            for i in range(len(p)):
                e, same = edge(p[i], p[(i + 1) % len(p)])
                oes.append(self.add(f"ORIENTED_EDGE('',*,*,#{e},{'.T.' if same else '.F.'})"))
            loop = self.add("EDGE_LOOP('',(" + ",".join(f"#{o}" for o in oes) + "))")
            bound = self.add(f"FACE_OUTER_BOUND('',#{loop},.T.)")
            xdir = pts[1] - pts[0]
            xdir = xdir - n * (xdir @ n)
            ax = self.axis(pts[0], n, xdir)
            pl = self.add(f"PLANE('',#{ax})")
            faces.append(self.add(f"ADVANCED_FACE('',(#{bound}),#{pl},.T.)"))
        cs = self.add("CLOSED_SHELL('',(" + ",".join(f"#{f}" for f in faces) + "))")
        solid = self.add(f"MANIFOLD_SOLID_BREP('',#{cs})")
        if rgb is not None:
            psa = self.colour(rgb)
            self.styled.append(self.add(f"STYLED_ITEM('color',(#{psa}),#{solid})"))
        return solid

    def part_rep(self, shells, rgb=None):
        origin = self.axis()
        solids = [self.brep(s, rgb) for s in shells]
        rep = self.add("ADVANCED_BREP_SHAPE_REPRESENTATION('',(" + ",".join(f"#{x}" for x in [origin] + solids)
                       + f"),#{self.geo_ctx})")
        return rep, origin

    def finish(self, path):
        if self.styled:
            self.add("MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',(" +
                     ",".join(f"#{s}" for s in self.styled) + f"),#{self.geo_ctx})")
        if self.products:
            self.add("PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,(" + ",".join(f"#{p}" for p in self.products) + "))")
        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        head = ["ISO-10303-21;", "HEADER;",
                "FILE_DESCRIPTION(('AquaSentinel R3 - planar B-rep export'),'2;1');",
                f"FILE_NAME({_str(self.name)},'{now}',({_str(self.author)}),({_str(self.org)}),"
                "'AquaSentinel R3 python build','AquaSentinel R3','');",
                "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));", "ENDSEC;", "DATA;"]
        with open(path, "w", encoding="ascii", newline="\n") as f:
            f.write("\n".join(head) + "\n")
            f.write("\n".join(self.lines) + "\n")
            f.write("ENDSEC;\nEND-ISO-10303-21;\n")


def _newell(pts):
    n = np.zeros(3)
    m = len(pts)
    for i in range(m):
        c, d = pts[i], pts[(i + 1) % m]
        n += [(c[1] - d[1]) * (c[2] + d[2]), (c[2] - d[2]) * (c[0] + d[0]), (c[0] - d[0]) * (c[1] + d[1])]
    L = np.linalg.norm(n)
    if L < 1e-9:
        return None
    return n / L


def write_step_part(path, pid, name, shells, rgb=None, desc=""):
    w = StepWriter(name)
    w.context()
    p, pd, pds = w.product(pid, name, desc)
    rep, _ = w.part_rep(shells, rgb)
    w.add(f"SHAPE_DEFINITION_REPRESENTATION(#{pds},#{rep})")
    w.finish(path)


def write_step_assembly(path, asm_name, parts, instances):
    """
    parts: {key: dict(pid, name, shells, rgb, desc)}
    instances: list of (key, 4x4 matrix in assembly frame, instance_name)
    Writes one top-level assembly product with each part placed by a rigid transform.
    """
    w = StepWriter(asm_name)
    w.context()
    ap, apd, apds = w.product(asm_name, asm_name, "AquaSentinel R3 assembly")
    asm_origin = w.axis()
    part_ids = {}
    for key, spec in parts.items():
        p, pd, pds = w.product(spec["pid"], spec["name"], spec.get("desc", ""))
        rep, _ = w.part_rep(spec["shells"], spec.get("rgb"))
        w.add(f"SHAPE_DEFINITION_REPRESENTATION(#{pds},#{rep})")
        part_ids[key] = (pd, rep)
    placements = []
    rels = []
    for i, (key, M, iname) in enumerate(instances, 1):
        pd, rep = part_ids[key]
        M = np.asarray(M, float)
        ax = w.axis(M[:3, 3], M[:3, 2], M[:3, 0])
        placements.append(ax)
        idt = w.add(f"ITEM_DEFINED_TRANSFORMATION('','',#{asm_origin},#{ax})")
        rr = w.add(f"(REPRESENTATION_RELATIONSHIP('','',#{rep},#ASMREP)"
                   f"REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION(#{idt})SHAPE_REPRESENTATION_RELATIONSHIP())")
        nauo = w.add(f"NEXT_ASSEMBLY_USAGE_OCCURRENCE({_str(i)},{_str(iname)},'',#{apd},#{pd},$)")
        pdsp = w.add(f"PRODUCT_DEFINITION_SHAPE('Placement','Placement of an item',#{nauo})")
        w.add(f"CONTEXT_DEPENDENT_SHAPE_REPRESENTATION(#{rr},#{pdsp})")
        rels.append(rr)
    asm_rep = w.add("SHAPE_REPRESENTATION('',(" + ",".join(f"#{x}" for x in [asm_origin] + placements)
                    + f"),#{w.geo_ctx})")
    w.add(f"SHAPE_DEFINITION_REPRESENTATION(#{apds},#{asm_rep})")
    w.lines = [ln.replace("#ASMREP", f"#{asm_rep}") for ln in w.lines]
    w.finish(path)
