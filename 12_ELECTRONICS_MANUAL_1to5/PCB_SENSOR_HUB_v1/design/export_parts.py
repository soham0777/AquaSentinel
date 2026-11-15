import json, sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); OX = OY = 100.0
mm = pcbnew.ToMM
parts = []
for fp in b.GetFootprints():
    bb = fp.GetBoundingBox(False)
    pads = [{'n': p.GetNumber(), 'x': mm(p.GetPosition().x) - OX, 'y': mm(p.GetPosition().y) - OY,
             'net': p.GetNetname(), 'd': mm(p.GetDrillSize().x), 's': mm(p.GetSize(pcbnew.F_Cu).x) if hasattr(p, 'GetSize') else 1.9}
            for p in fp.Pads()]
    parts.append({'ref': fp.GetReference(), 'val': fp.GetValue(), 'fp': fp.GetFPIDAsString(),
                  'bb': [mm(bb.GetX()) - OX, mm(bb.GetY()) - OY, mm(bb.GetWidth()), mm(bb.GetHeight())], 'pads': pads})
tracks = [{'x1': mm(t.GetStart().x) - OX, 'y1': mm(t.GetStart().y) - OY, 'x2': mm(t.GetEnd().x) - OX,
           'y2': mm(t.GetEnd().y) - OY, 'w': mm(t.GetWidth()), 'net': t.GetNetname()} for t in b.GetTracks()]
json.dump({'parts': parts, 'tracks': tracks}, open(sys.argv[2], 'w'), indent=0)
print(len(parts), 'parts', len(tracks), 'tracks')
