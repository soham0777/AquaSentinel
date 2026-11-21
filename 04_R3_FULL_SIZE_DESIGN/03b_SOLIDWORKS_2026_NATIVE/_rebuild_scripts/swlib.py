"""Small helpers for building AquaSentinel R3 drawings through the SOLIDWORKS API (late-bound COM)."""
import os
import pythoncom
import win32com.client
from win32com.client import VARIANT

ROOT = r"C:\Users\dell\OneDrive\Desktop\AquaSentinel\04_R3_FULL_SIZE_DESIGN"
CAD = os.path.join(ROOT, "03b_SOLIDWORKS_2026_NATIVE")
ASM = os.path.join(CAD, "AquaSentinel_R3_Assembly_NATIVE.SLDASM")
TPL = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\templates\Drawing.DRWDOT"
FMT = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\lang\english\sheetformat\a3 - iso.slddrt"

sw = win32com.client.Dispatch("SldWorks.Application")
mu = sw.GetMathUtility
NOTHING = VARIANT(pythoncom.VT_DISPATCH, None)

# installation parts: everything on the pier, not on the float
INSTALL = ("AS3-101", "AS3-102", "AS3-103", "AS3-111", "AS3-112", "AS3-113", "AS3-114", "AS3-904", "AS3-905")


def part(code):
    for f in os.listdir(CAD):
        if f.startswith(code + "_") and f.upper().endswith(".SLDPRT"):
            return os.path.join(CAD, f)
    raise FileNotFoundError(code)


def arr(vals):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, list(vals))


def close_drawings():
    docs = sw.GetDocuments or []
    for t in list(docs):
        if t.GetType == 3:
            sw.CloseDoc(t.GetTitle)


def new_drawing(props, s1=1, s2=10):
    d = sw.NewDocument(TPL, 8, 0.42, 0.297)
    d.SetupSheet5("Sheet1", 8, 12, s1, s2, True, FMT, 0.42, 0.297, "Default", True)
    # point the model-driven title-block fields at the drawing's own properties
    d.EditTemplate
    v = d.GetFirstView
    n = v.GetFirstNote
    repl = {'$PRPSHEET:"Description"': '$PRP:"Title"', '$PRPSHEET:"Material"': '$PRP:"Material"',
            '$PRPSHEET:"Finish"': '$PRP:"Finish"', 'WEIGHT: $PRP:"Weight"$PRPSHEET:"Weight"': 'WEIGHT: $PRP:"Weight"'}
    while n:
        t = n.PropertyLinkedText
        if t in repl:
            n.PropertyLinkedText = repl[t]
        n = n.GetNext
    d.EditSheet
    d.SetUnits(0, 0, 8, 0, False)  # millimetres
    cpm =d.Extension.CustomPropertyManager("")
    for k, val in props.items():
        cpm.Add3(k, 30, val, 2)
    return d


def view(d, model, orient, x, y, scale=None, mode=2):
    v = d.CreateDrawViewFromModelView3(model, orient, x, y, 0)
    if scale is None:
        v.UseSheetScale = True
    else:
        v.UseSheetScale = False
        v.ScaleDecimal = scale
    v.SetDisplayMode3(False, mode, False, True)
    try:
        v.SetDisplayTangentEdges2(2)
    except Exception:
        pass
    return v


def projected(d, parent, x, y):
    d.ClearSelection2(True)
    d.Extension.SelectByID2(parent.Name, "DRAWINGVIEW", 0, 0, 0, False, 0, NOTHING, 0)
    v = d.CreateUnfoldedViewAt3(x, y, 0, False)
    try:
        v.SetDisplayMode3(False, 2, False, True)
        v.SetDisplayTangentEdges2(2)
    except Exception:
        pass
    return v


def iso_of(d, parent, scale):
    """Isometric that keeps the parent's up direction: a projected view dropped diagonally (below-right, first angle)."""
    o = parent.GetOutline
    v = projected(d, parent, o[2] + 0.06, o[1] - 0.06)
    v.UseSheetScale = False
    v.ScaleDecimal = scale
    v.SetDisplayMode3(False, 3, False, True)
    return v


def recenter(v, x, y):
    o = v.GetOutline
    p = v.Position
    v.Position = arr([p[0] + x - (o[0] + o[2]) / 2, p[1] + y - (o[1] + o[3]) / 2])


def hide(v, keep=None, drop=None):
    """Hide components in one view. keep: tuple of code prefixes to keep; drop: prefixes to hide."""
    root = v.RootDrawingComponent
    for c in root.GetChildren or []:
        code = c.Name.split("/")[-1][:7]
        if (keep is not None and not code.startswith(keep)) or (drop is not None and code.startswith(drop)):
            c.Visible = False


def _apply(t, p):
    a = t.ArrayData
    x, y, z = p[:3]
    s = a[12]
    return (s * (x * a[0] + y * a[3] + z * a[6]) + a[9],
            s * (x * a[1] + y * a[4] + z * a[7]) + a[10],
            s * (x * a[2] + y * a[5] + z * a[8]) + a[11])


def _map(a, p, tr):
    x, y, z = p[:3]
    s = a[12]
    if not tr:
        return (s * (x * a[0] + y * a[3] + z * a[6]) + a[9], s * (x * a[1] + y * a[4] + z * a[7]) + a[10])
    return (s * (x * a[0] + y * a[1] + z * a[2]) + a[9], s * (x * a[3] + y * a[4] + z * a[5]) + a[10])


def _choose(v, pts):
    """Pick the rotation convention whose projected extent best matches the view outline."""
    a = v.ModelToViewTransform.ArrayData
    o = v.GetOutline
    W, H = o[2] - o[0] - 0.012, o[3] - o[1] - 0.012
    best = None
    for tr in (False, True):
        m = [_map(a, p, tr) for p in pts]
        xs = [q[0] for q in m]
        ys = [q[1] for q in m]
        err = abs((max(xs) - min(xs)) - W) + abs((max(ys) - min(ys)) - H)
        if best is None or err < best[0]:
            best = (err, tr)
    return a, best[1]


_BOX = {}
ARC_MAX = int(os.environ.get('ARC_MAX', '3'))
DEBUG = bool(os.environ.get('DWGDEBUG'))
_TF = {}
_CMP = {}


def _boxes():
    if not _BOX:
        a = sw.GetOpenDocumentByName(ASM)
        if a is None:
            e = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            a = sw.OpenDoc6(ASM, 2, 1, "", e, w)
        for c in a.GetComponents(True):
            _BOX[c.Name2] = c.GetBox(False, False)
            _TF[c.Name2] = c.Transform2
            _CMP[c.Name2] = c
    return _BOX


def extreme_vertices(v, k=1):
    """(entity, x, y) for vertices that can bound the view; x, y in a frame aligned with the sheet."""
    ref = v.ReferencedDocument
    if ref is not None and ref.GetType == 1:
        comps = v.GetVisibleComponents or []
        c0 = comps[0] if comps else NOTHING
        ents = list(v.GetVisibleEntities2(c0, 2) or [])
        pts = [e.GetPoint for e in ents]
        if not pts:
            return []
        a, tr = _choose(v, pts)
        return [(e, *_map(a, p, tr)) for e, p in zip(ents, pts)]
    comps = v.GetVisibleComponents
    boxes = _boxes()
    corners = {}
    for c in comps:
        b = boxes.get(c.Name2.split("/")[-1])
        if b:
            corners[c.Name2] = [(x, y, z) for x in (b[0], b[3]) for y in (b[1], b[4]) for z in (b[2], b[5])]
    a, tr = _choose(v, [p for ps in corners.values() for p in ps])
    rows = []
    for nm, ps in corners.items():
        m = [_map(a, p, tr) for p in ps]
        rows.append((nm, min(q[0] for q in m), max(q[0] for q in m), min(q[1] for q in m), max(q[1] for q in m)))
    pick = set()
    for i, rev in ((1, False), (2, True), (3, False), (4, True)):
        for r in sorted(rows, key=lambda r: r[i], reverse=rev)[:k]:
            pick.add(r[0])
    out = []
    for c in comps:
        if c.Name2 in pick:
            for e in v.GetVisibleEntities2(c, 2) or []:
                out.append((e, *_map(a, e.GetPoint, tr)))
    return out

def dim_between(d, v, a, b, horizontal, x, y):
    """Dimension between two vertex tuples, text at sheet (x, y) metres."""
    d.ClearSelection2(True)
    sm = d.SelectionManager
    for e in (a[0], b[0]):
        sd = sm.CreateSelectData
        sd.View = v
        e.Select4(True, sd)
    dd = d.AddHorizontalDimension2(x, y, 0) if horizontal else d.AddVerticalDimension2(x, y, 0)
    d.ClearSelection2(True)
    if dd:
        try:
            dd.SetPrecision3(0, 0, 0, 0)
        except Exception:
            pass
    return dd


def _drop(d, dd):
    d.ClearSelection2(True)
    ok = False
    try:
        ok = dd.GetAnnotation.Select3(False, NOTHING)
    except Exception:
        pass
    if not ok:
        try:
            ok = d.Extension.SelectByID2(dd.GetNameForSelection, "DIMENSION", 0, 0, 0, False, 0, NOTHING, 0)
        except Exception:
            pass
    r = d.Extension.DeleteSelection2(0) if ok else False
    if not r:
        r = d.EditDelete
    if not ok:
        print("   DELETE FAILED")


def overall(d, v, w=True, h=True, gap=0.007, pts=None, tol=0.85):
    """Overall dimensions between extreme vertices, placed from the view outline. A dimension that would fall short
    of the drawn extent (a curved extreme with no vertex on it) is left off rather than shown."""
    pts = pts or extreme_vertices(v)
    if not pts:
        return None
    o = v.GetOutline
    s = v.ScaleDecimal
    cx, cy = (o[0] + o[2]) / 2, (o[1] + o[3]) / 2
    xs = sorted(pts, key=lambda t: t[1])
    ys = sorted(pts, key=lambda t: t[2])
    res = {}
    for key, on, lo, hi, out_ext, horiz in (("w", w, xs[0], xs[-1], o[2] - o[0], True), ("h", h, ys[0], ys[-1], o[3] - o[1], False)):
        if not on:
            continue
        span = (hi[1] - lo[1]) if horiz else (hi[2] - lo[2])
        exp = out_ext - 0.012
        if span < tol * exp:
            print(f"   skip {key}: vertex span {span / s * 1000:.0f} < drawn ~{exp / s * 1000:.0f}")
            continue
        dd = dim_between(d, v, lo, hi, horiz, cx if horiz else o[0] - gap, o[3] + gap if horiz else cy)
        res[key] = dd
    return res


def set_scale(d, s1, s2):
    sh = d.GetCurrentSheet
    sh.SetProperties2(8, 12, s1, s2, True, 0.42, 0.297, True)


def note(d, text, x, y, h_mm=3.5, bold=False):
    d.ClearSelection2(True)
    n = d.InsertNote(text)
    if n:
        ann = n.GetAnnotation
        ann.SetPosition2(x, y, 0)
        tf = ann.GetTextFormat(0)
        tf.CharHeight = h_mm / 1000
        tf.Bold = bold
        ann.SetTextFormat(0, False, tf)
    return n


def label(d, v, text, dy=0.006):
    """View label under a view."""
    o = v.GetOutline
    return note(d, text, o[0], o[1] - dy, 3.0, True)


def table(d, x, y, rows, widths_mm):
    """General table, top-left corner at (x, y) sheet metres."""
    t = d.InsertTableAnnotation2(False, x, y, 1, "", len(rows), len(rows[0]))
    did = t._oleobj_.GetIDsOfNames("Text")
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            t._oleobj_.Invoke(did, 0, pythoncom.DISPATCH_PROPERTYPUT, False, r, c, str(val))
    try:
        tf = t.GetTextFormat
        tf.CharHeight = 0.0025
        t.SetTextFormat(False, tf)
    except Exception as e:
        print("   table font", e)
    for r in range(len(rows)):
        try:
            t.SetRowHeight(r, 0.0055, 0)
        except Exception as e:
            print("   row height", e)
            break
    for c, w in enumerate(widths_mm):
        try:
            t.SetColumnWidth(c, w / 1000, 0)
        except Exception as e:
            print("   col width", e)
    return t


def save(d, name):
    out_dir = os.path.join(ROOT, "04_Drawings", "SOLIDWORKS")
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, name + ".SLDDRW")
    d.ForceRebuild3(True)
    r = d.SaveAs3(p, 0, 1)
    pdf = os.path.join(out_dir, name + ".pdf")
    r2 = d.SaveAs3(pdf, 0, 1)
    return p, pdf, r, r2



# ---- native model: true circles have no vertices, so bound views by edges ----
def _rot(c):
    t = _TF.get(c.Name2.split("/")[-1]) if c is not None else None
    if t is None:
        return lambda q: q
    a = t.ArrayData
    return lambda q: (q[0] * a[0] + q[1] * a[3] + q[2] * a[6], q[0] * a[1] + q[1] * a[4] + q[2] * a[7], q[0] * a[2] + q[1] * a[5] + q[2] * a[8])


def _ctf(c):
    """part-space -> assembly-space function for a drawing component (identity for part views)."""
    _boxes()
    t = _TF.get(c.Name2.split("/")[-1])
    for get in (() if t is not None else (lambda: c.Transform2,)):
        try:
            t = get()
            if t is not None:
                break
        except Exception:
            t = None
    return (lambda p: _apply(t, p)) if t is not None else (lambda p: tuple(p[:3]))


def _edge_samples(ed, f):
    cu = ed.GetCurve
    par = ed.GetCurveParams3
    s, t = par.UMinValue, par.UMaxValue
    if cu.IsLine:
        return [f(par.StartPoint[:3]), f(par.EndPoint[:3])]
    if cu.IsCircle:
        return [f(cu.Evaluate2(s + (t - s) * i / 47, 0)[:3]) for i in range(48)]
    sp, ep = par.StartPoint[:3], par.EndPoint[:3]
    pts = cu.GetTessPts(2e-5, 1e-3, arr(sp), arr(ep))
    pts = list(pts or [])
    return [f(pts[i:i + 3]) for i in range(0, len(pts) - 2, 3)] or [f(sp), f(ep)]


def extreme_edges(v, k=2):
    """[(kind, entity, xmin, xmax, ymin, ymax)] for edges of the components that bound the view."""
    ref = v.ReferencedDocument
    if ref is not None and ref.GetType == 1:
        comps = list(v.GetVisibleComponents or []) or [None]
        cand = comps
    else:
        comps = list(v.GetVisibleComponents or [])
        boxes = _boxes()
        corners = {}
        for c in comps:
            b = boxes.get(c.Name2.split("/")[-1])
            if b:
                corners[c.Name2] = [(x, y, z) for x in (b[0], b[3]) for y in (b[1], b[4]) for z in (b[2], b[5])]
        a, tr = _choose(v, [p for ps in corners.values() for p in ps])
        rows = []
        for nm, ps in corners.items():
            m = [_map(a, p, tr) for p in ps]
            rows.append((nm, min(q[0] for q in m), max(q[0] for q in m), min(q[1] for q in m), max(q[1] for q in m)))
        pick = set()
        for i, rev in ((1, False), (2, True), (3, False), (4, True)):
            for r in sorted(rows, key=lambda r: r[i], reverse=rev)[:k]:
                pick.add(r[0])
        cand = [c for c in comps if c.Name2 in pick]
    raw = []
    for c in cand:
        f = _ctf(c) if c is not None else (lambda p: tuple(p[:3]))
        for ed in v.GetVisibleEntities2(c if c is not None else NOTHING, 1) or []:
            try:
                cu = ed.GetCurve
                ax = None
                if cu.IsCircle:
                    cp = cu.CircleParams
                    _boxes()
                    ax = _rot(c)(cp[3:6])
                elif not cu.IsLine:
                    continue          # splines and ellipses: no reliable extreme to dimension to
                raw.append((_proxy(c, ed), _edge_samples(ed, f), f, ax))
            except Exception:
                pass
    if not raw:
        return []
    a, tr = _choose(v, [p for _, ps, _, _ in raw for p in ps])
    if os.environ.get('TR') is not None:
        tr = bool(int(os.environ['TR']))
    if DEBUG:
        print('    tr', tr)
    out = []
    vz = (a[2], a[5], a[8])
    for ed, ps, f, ax in raw:
        face = False
        if ax is not None:
            n = abs(ax[0] * vz[0] + ax[1] * vz[1] + ax[2] * vz[2]) / (sum(x * x for x in ax) ** 0.5 or 1)
            if 0.02 < n < 0.98:
                continue      # circle seen at an angle (ellipse on the sheet)
            face = n >= 0.98
        m = [_map(a, p, tr) for p in ps]
        xs, ys = [q[0] for q in m], [q[1] for q in m]
        out.append(("line" if ed.GetCurve.IsLine else "curve", ed, min(xs), max(xs), min(ys), max(ys), f, m, face))
    return out, a, tr


def _sel_for(t, want_lo, horiz, A, TR):
    lo_i, hi_i = (2, 3) if horiz else (4, 5)
    ed = t[1]
    width = t[hi_i] - t[lo_i]
    ext = t[lo_i] if want_lo else t[hi_i]
    if t[0] == "line":
        if width > 1e-4:
            best = None
            for vx in (ed.GetStartVertex, ed.GetEndVertex):
                if vx is None:
                    continue
                q = _map(A, t[6](vx.GetPoint), TR)[0 if horiz else 1]
                if best is None or abs(q - ext) < best[0]:
                    best = (abs(q - ext), vx)
            return ("v", best[1] if best else ed)
        return ("e", ed)
    return ("c" if width > 3e-4 else "e", ed)


def _rank(t, horiz):
    lo_i, hi_i = (2, 3) if horiz else (4, 5)
    w = t[hi_i] - t[lo_i]
    return 0 if t[0] == "line" else (1 if w <= 3e-4 else 2)


def overall_edges(d, v, w=True, h=True, gap=0.007, tol=0.85, band=0.0006, tries=4):
    """Overall dimension between true model edges at the view extremes. A dimension is kept only if SOLIDWORKS'
    measured value matches the drawn extent (within 0.6 mm on the sheet); otherwise it is deleted."""
    r = extreme_edges(v)
    if not r:
        return None
    ents, A, TR = r
    o = v.GetOutline
    s = v.ScaleDecimal
    cx, cy = (o[0] + o[2]) / 2, (o[1] + o[3]) / 2
    res = {}
    for key, on, lo_i, hi_i, out_ext, horiz in (("w", w, 2, 3, o[2] - o[0], True), ("h", h, 4, 5, o[3] - o[1], False)):
        if not on:
            continue
        gmin = min(t[lo_i] for t in ents)
        gmax = max(t[hi_i] for t in ents)
        span = gmax - gmin
        if span < tol * (out_ext - 0.012):
            print(f"   skip {key}: edge span {span / s * 1000:.0f} < drawn ~{(out_ext - 0.012) / s * 1000:.0f}")
            continue
        ok = lambda t: t[0] == "line" or t[8] or (t[hi_i] - t[lo_i]) <= 3e-4
        bnd = band
        lo_all = sorted([t for t in ents if t[lo_i] - gmin < bnd], key=lambda t: (not ok(t), _rank(t, horiz), t[lo_i]))
        hi_all = sorted([t for t in ents if gmax - t[hi_i] < bnd], key=lambda t: (not ok(t), _rank(t, horiz), -t[hi_i]))
        los, his = lo_all[:tries], hi_all[:tries]
        done = False
        for lo in los:
            for hi in his:
                sels = [_sel_for(lo, True, horiz, A, TR), _sel_for(hi, False, horiz, A, TR)]
                d.ClearSelection2(True)
                for (kind, ent), t, want_lo in ((sels[0], lo, True), (sels[1], hi, False)):
                    j = 0 if horiz else 1
                    q = (min if want_lo else max)(t[7], key=lambda p: p[j])
                    if kind == "c" or kind == "e" or True:
                        # pick on the sheet at the extreme point: selects the right instance (edge or vertex there)
                        typ = "VERTEX" if kind == "v" else "EDGE"
                        if not d.Extension.SelectByID2("", typ, q[0], q[1], 0, True, 0, NOTHING, 0):
                            sd = d.SelectionManager.CreateSelectData
                            sd.View = v
                            ent.Select4(True, sd)
                smx = d.SelectionManager
                for k in range(smx.GetSelectedObjectCount2(-1), 0, -1):
                    if smx.GetSelectedObjectType3(k, -1) == 12:
                        smx.DeSelect2(k, -1)
                if DEBUG:
                    info = []
                    for k in range(1, smx.GetSelectedObjectCount2(-1) + 1):
                        cmp_ = smx.GetSelectedObjectsComponent4(k, -1)
                        info.append((smx.GetSelectedObjectType3(k, -1), (getattr(cmp_, 'Name', None) or str(cmp_))[-40:] if cmp_ else None, [round(x * 1000, 1) for x in (smx.GetSelectionPoint2(k, -1) or (0, 0))[:2]]))
                    print('    sel', info, 'q', [[round(x * 1000, 1) for x in (min if wl else max)(t[7], key=lambda p: p[0 if horiz else 1])] for t, wl in ((lo, True), (hi, False))], [c.Name2.split('/')[-1][:12] for c in []])
                dd = d.AddHorizontalDimension2(cx, o[3] + gap, 0) if horiz else d.AddVerticalDimension2(o[0] - gap, cy, 0)
                d.ClearSelection2(True)
                if not dd:
                    continue
                v0 = dd.GetDimension2(0).Value
                for i, (kind, _) in enumerate(sels, 1):
                    if kind == "c":
                        try:
                            _early_dim(dd).SetArcEndCondition(i, ARC_MAX)
                        except Exception:
                            pass
                try:
                    dd.SetPrecision3(0, 0, 0, 0)
                except Exception:
                    pass
                d.ForceRebuild3(False)
                val = dd.GetDimension2(0).Value
                if abs(val - span / s * 1000) <= 2.5:
                    res[key] = dd
                    done = True
                    break
                if DEBUG:
                    print('    try', key, [k for k, _ in sels], lo[0], hi[0], round(v0), round(val), [round(x/s*1000) for x in (lo[lo_i], lo[hi_i], hi[lo_i], hi[hi_i])], lo[1].GetCurve.IsCircle, hi[1].GetCurve.IsCircle, 'want', round(span / s * 1000))
                _drop(d, dd)
            if done:
                break
        if not done:
            print(f"   none for {key} (extent {span / s * 1000:.0f})")
    return res


_SWMOD = None


def _early_dd(dd):
    global _SWMOD
    if _SWMOD is None:
        from win32com.client import gencache
        _SWMOD = gencache.EnsureModule("{83A33D31-27C5-11CE-BFD4-00400513BB57}", 0, 34, 0)
    return _SWMOD.IDisplayDimension(dd._oleobj_)


def _early_dim(dd):
    _early_dd(dd)
    return _SWMOD.IDimension(dd.GetDimension2(0)._oleobj_)


def _proxy(c, ent):
    """assembly-context entity for one component instance (part entities are shared by every instance)."""
    if c is None:
        return ent
    comp = _CMP.get(c.Name2.split("/")[-1])
    if comp is None:
        return ent
    try:
        pe = comp.GetCorrespondingEntity(ent)
        return pe if pe is not None else ent
    except Exception:
        return ent
