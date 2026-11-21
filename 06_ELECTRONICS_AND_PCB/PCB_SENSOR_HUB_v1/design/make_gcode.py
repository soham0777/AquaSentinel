# AquaSentinel Sensor Hub - G-code for the TwoTrees TTC-450 Pro (GRBL), single-sided isolation milling.
# Copper side UP on the machine (the design is mirrored here). Origin X0 Y0 = LOWER-LEFT corner of the 100 (X) x 155 (Y) blank,
# Z0 = copper surface (use Candle's height map / auto-levelling before the isolation job).
import json, math, os, sys
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely import affinity
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, 'gcode'); os.makedirs(OUTDIR, exist_ok=True)
g = json.load(open(os.path.join(HERE, 'geom.json')))
W, H = g['W'], g['H']
BW, BH = W, H                                  # ORIGIN = the board's own lower-left corner (user zeroes there)
MX, MY = 0.0, 0.0

# ---- tool: 30 deg x 0.1 mm V-bit ----
TIP, ANG = 0.1, 30.0
DEPTH = 0.08                                   # isolation depth (mm)
CUTW = TIP + 2 * DEPTH * math.tan(math.radians(ANG / 2))      # ~0.143 mm
OFFS = [CUTW / 2, CUTW / 2 + 0.12, CUTW / 2 + 0.24]           # path centre distance from copper edge (3 passes)
FEED, PLUNGE, SAFE, TRAVEL, RPM = 150, 40, 2.0, 15.0, 10000   # TRAVEL: clears clamps


def to_machine(geom):                          # top view (y down) -> copper-up machine view (mirror X, Y up)
    geom = affinity.scale(geom, xfact=-1, yfact=-1, origin=(0, 0))
    return affinity.translate(geom, W + MX, H + MY)


def poly(item):
    ring, holes = item[0], item[1]
    return Polygon(ring, holes).buffer(0)


feats = [(poly(f), f[2]) for f in g['features']]
gndp = [poly(f[:2]) for f in g['gnd']]
copper = unary_union([p for p, _ in feats])                    # everything that must be isolated

# ---- isolation toolpaths ----
paths = []
for off in OFFS:
    region = copper.buffer(off, join_style=1, resolution=16)
    geoms = getattr(region, 'geoms', [region])
    for pg in geoms:
        for ring in [pg.exterior] + list(pg.interiors):
            paths.append(to_machine(LineString(ring.coords)))


def order(paths):                              # nearest-neighbour ordering to cut travel time
    left, out, cur = paths[:], [], (0.0, 0.0)
    while left:
        i = min(range(len(left)), key=lambda k: Point(cur).distance(Point(left[k].coords[0])))
        p = left.pop(i); out.append(p); cur = p.coords[-1]
    return out


paths = order(paths)


def header(name, note):
    return [f'( AquaSentinel Sensor Hub v1.2 - {name} )', f'( {note} )',
            '( origin X0 Y0 = lower-left corner of the 104 x 72 BOARD, Z0 = copper surface )',
            'G21 G90 G94', 'G17', f'G0 Z{TRAVEL:.2f}', f'M3 S{RPM}', 'G4 P3']


def footer():
    return [f'G0 Z{TRAVEL:.2f}', 'M5', f'G0 X{BW/2:.1f} Y{BH/2:.1f}', 'M30']     # park over the board, never the corners


def write(fname, lines):
    # first XY move happens at TRAVEL height (right after the header), then the tool descends inside the board
    i = next(k for k, l in enumerate(lines) if l.startswith('G0 X'))
    assert lines[i - 1].startswith('G0 Z')              # the per-path 'G0 Z<SAFE>' before the first XY move
    lines = lines[:i - 1] + [f'G0 Z{TRAVEL:.2f}', lines[i], lines[i - 1]] + lines[i + 1:]
    open(os.path.join(OUTDIR, fname), 'w', newline='\n').write('\n'.join(lines) + '\n')


# 1) isolation
L = header('01 ISOLATION', f'30deg x 0.1mm V-bit, depth {DEPTH} mm, {len(OFFS)} passes, feed {FEED} mm/min')
length = 0.0
for p in paths:
    c = list(p.coords)
    L += [f'G0 Z{SAFE:.2f}', f'G0 X{c[0][0]:.3f} Y{c[0][1]:.3f}', f'G1 Z{-DEPTH:.3f} F{PLUNGE}']
    L += [f'G1 X{x:.3f} Y{y:.3f} F{FEED}' for x, y in c[1:]]
    length += p.length
write('01_isolation_Vbit30.nc', L + footer())
t_iso = length / FEED

# 2) spot drill every hole with the same V-bit (centres for hand drilling + clears copper in the hole)
drills = [(to_machine(Point(x, y)), d, ref) for x, y, d, ref in g['drills']]
pts = order([LineString([(p.x, p.y), (p.x, p.y)]) for p, _, _ in drills])
L = header('02 SPOT DRILL', 'same V-bit, 0.5 mm deep cone at every hole centre')
for p in pts:
    x, y = p.coords[0]
    L += [f'G0 Z{SAFE:.2f}', f'G0 X{x:.3f} Y{y:.3f}', f'G1 Z-0.500 F{PLUNGE}']
write('02_spot_drill_Vbit30.nc', L + footer())

# 3) real drilling, one file per drill size (only if you have these bits; else drill by hand at the spots)
for size in sorted({d for _, d, _ in drills}):
    pts = order([LineString([(p.x, p.y), (p.x, p.y)]) for p, d, _ in drills if d == size])
    L = header(f'03 DRILL {size:.1f} mm', f'{size:.1f} mm drill bit, through 1.6 mm board (Z -1.9), peck')
    for p in pts:
        x, y = p.coords[0]
        L += [f'G0 Z{SAFE:.2f}', f'G0 X{x:.3f} Y{y:.3f}', f'G1 Z-1.000 F60', f'G0 Z0.500', f'G1 Z-1.900 F60']
    write(f'03_drill_{size:.1f}mm.nc', L + footer())

# 4) outline score lines (cut the board out along them by hand)
ob = to_machine(box(0, 0, W, H))
c = list(ob.exterior.coords)
L = header('04 OUTLINE SCORE', 'V-bit score along the board edge, 3 passes to 0.6 mm (cut/snap by hand)')
for dz in (0.2, 0.4, 0.6):
    L += [f'G0 Z{SAFE:.2f}', f'G0 X{c[0][0]:.3f} Y{c[0][1]:.3f}', f'G1 Z{-dz:.3f} F{PLUNGE}']
    L += [f'G1 X{x:.3f} Y{y:.3f} F{FEED}' for x, y in c[1:]]
write('04_outline_score_Vbit30.nc', L + footer())

# ---- self-check: simulate the milled copper and look for shorts / opens ----
cut = unary_union([LineString(p.coords).buffer(CUTW / 2, resolution=8) for p in paths])
remaining = to_machine(box(0, 0, W, H)).difference(cut)
comps = list(getattr(remaining, 'geoms', [remaining]))
featm = [(to_machine(p), n) for p, n in feats]
gndm = [to_machine(p) for p in gndp]
shorts, nets_in = [], {}
for ci, cp in enumerate(comps):
    ns = {n for p, n in featm if cp.intersects(p.representative_point())}
    if any(cp.intersects(p.representative_point()) for p in gndm) or cp.area > 2000:
        ns.add('GND')
    real = {n for n in ns if n != 'TEXT'}
    if len(real) > 1:
        shorts.append(sorted(real))
    for n in real:
        nets_in.setdefault(n, set()).add(ci)
opens = {n: len(s) for n, s in nets_in.items() if len(s) > 1 and not n.startswith('NC_') and n != 'GND'}
print(f'board {W}x{H} at X{MX}..{MX+W} Y{MY}..{MY+H} on the {BW}x{BH} blank')
print(f'isolation passes: {len(paths)}  cut length {length/1000:.2f} m  time ~{t_iso:.0f} min at {FEED} mm/min')
print(f'cut width {CUTW:.3f} mm, total isolation {OFFS[-1] + CUTW/2:.2f} mm per side')
print('SHORTS:', shorts if shorts else 'none')
print('OPENS (net split into pieces):', opens if opens else 'none')
print('holes:', {d: sum(1 for _, dd, _ in drills if dd == d) for d in sorted({d for _, d, _ in drills})})

# ---- preview ----
fig, ax = plt.subplots(figsize=(8.5, 12.5), dpi=110)
ax.add_patch(plt.Rectangle((0, 0), BW, BH, fc='#c98b5a', ec='k', lw=1))
for (x0, y0, w0, h0) in ((0, 0, BW, MY - 3), (0, MY + H + 3, BW, BH - MY - H - 3), (0, 0, MX - 3, BH), (MX + W + 3, 0, BW - MX - W - 3, BH)):
    ax.add_patch(plt.Rectangle((x0, y0), w0, h0, fc='#7fb3ff', alpha=0.25, ec='none'))
for cp in comps:
    for pg in getattr(cp, 'geoms', [cp]):
        ax.fill(*pg.exterior.xy, fc='#e6b07a', ec='none')
for p in paths:
    ax.plot(*p.xy, color='#5a1a00', lw=0.35)
for p, d, _ in drills:
    ax.add_patch(plt.Circle((p.x, p.y), d / 2, fc='k'))
ax.plot(*ob.exterior.xy, 'b--', lw=0.8)
ax.set_xlim(-2, BW + 2); ax.set_ylim(-2, BH + 2); ax.set_aspect('equal')
ax.set_title('COPPER SIDE as clamped (mirrored). Origin X0 Y0 = lower-left corner of the 104 x 72 board.\n'
             'Blue = SAFE for clamps/supports (3 mm from any cut). Dashed = outline score.', fontsize=9)
ax.set_xlabel('X (mm)'); ax.set_ylabel('Y (mm)')
fig.tight_layout(); fig.savefig(os.path.join(OUTDIR, 'preview_copper_side.png'))
print('files:', sorted(os.listdir(OUTDIR)))
