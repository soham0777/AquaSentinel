# Export B.Cu copper features (everything except the GND pour/pads), drills and outline to JSON. Run with KiCad python.
import json, sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); OX = OY = 100.0
mm = lambda v: pcbnew.ToMM(v)
def polys(ps):
    out = []
    for i in range(ps.OutlineCount()):
        o = ps.Outline(i); ring = [(mm(o.CPoint(k).x) - OX, mm(o.CPoint(k).y) - OY) for k in range(o.PointCount())]
        holes = []
        for h in range(ps.HoleCount(i)):
            hh = ps.Hole(i, h); holes.append([(mm(hh.CPoint(k).x) - OX, mm(hh.CPoint(k).y) - OY) for k in range(hh.PointCount())])
        out.append([ring, holes])
    return out
def shape(item):
    ps = pcbnew.SHAPE_POLY_SET()
    item.TransformShapeToPolygon(ps, pcbnew.B_Cu, 0, pcbnew.FromMM(0.005), pcbnew.ERROR_INSIDE)
    return polys(ps)
feat, gnd, drills = [], [], []
for t in b.GetTracks():
    (gnd if t.GetNetname() == 'GND' else feat).extend([[r, h, t.GetNetname()] for r, h in shape(t)])
for fp in b.GetFootprints():
    for p in fp.Pads():
        d = p.GetDrillSize().x
        if d > 0: drills.append([mm(p.GetPosition().x) - OX, mm(p.GetPosition().y) - OY, round(mm(d), 2), fp.GetReference()])
        if p.IsOnLayer(pcbnew.B_Cu):
            (gnd if p.GetNetname() == 'GND' else feat).extend([[r, h, p.GetNetname() or ('NC_' + fp.GetReference() + '_' + p.GetNumber())] for r, h in shape(p)])
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.B_Cu and isinstance(d, pcbnew.PCB_TEXT):
        ps = pcbnew.SHAPE_POLY_SET(); d.TransformTextToPolySet(ps, 0, pcbnew.FromMM(0.005), pcbnew.ERROR_INSIDE); feat.extend([[r, h, 'TEXT'] for r, h in polys(ps)])
zones = []
for z in b.Zones():
    zones.extend(polys(z.GetFilledPolysList(pcbnew.B_Cu)))
json.dump({'W': 104.0, 'H': 72.0, 'features': feat, 'gnd': gnd, 'zones': zones, 'drills': drills}, open(sys.argv[2], 'w'))
print('features', len(feat), 'gnd', len(gnd), 'zones', len(zones), 'drills', len(drills))
