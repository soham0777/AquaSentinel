# Assembly + validation guide images for the AquaSentinel Sensor Hub v1.2, drawn from the real KiCad data.
import json, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Polygon as MPoly

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'guide'); os.makedirs(OUT, exist_ok=True)
D = json.load(open(os.path.join(HERE, 'parts.json')))
G = json.load(open(os.path.join(HERE, 'geom.json')))
W, H = 104.0, 72.0
P = {p['ref']: p for p in D['parts']}

SHORT = {'+5V_AUX': '5V', 'GND': 'GND', '+9V': '9V', '+4V0': '4V', 'D2_TEMP': 'D2', 'D3_AIR': 'D3', 'D4_LIGHT': 'D4',
         'D5_TURB': 'D5', 'D6_ALC': 'D6', 'D7_G_LED': 'G', 'D8_R_LED': 'R', 'D9_B_LED': 'B', 'D10_PUMP': 'IN1',
         'D11_SP': 'D11', 'D12_SP': 'D12', 'A0_TDSPWR': 'PWR', 'A1_TDS': 'SIG', 'A2_SP': 'A2', 'A3_SP': 'A3',
         'A4_SP': 'A4', 'A5_SP': 'A5', 'PH_IN': 'O', 'SIM_RXD': 'RXD', 'SIM_TXD': 'TXD', 'PI_TX': 'TX8'}
NAME = {'J1': 'J1  MQ-3', 'J2': 'J2  TURBIDITY', 'J3': 'J3  LDR', 'J4': 'J4  DHT11', 'J5': 'J5  DS18B20',
        'J6': 'J6  RGB BEACON', 'J7': 'J7  PUMP CTRL', 'J8': 'J8  SPARE', 'J9': 'J9  TDS', 'J10': 'J10  ANALOG SPARE',
        'J11': 'J11  pH SIGNAL', 'J12': 'J12  AUX 5V IN', 'J13': 'J13  PUMP POWER', 'J14': 'J14  STEP-UP',
        'J15': 'J15  pH 9V', 'J16': 'J16  STEP-DOWN', 'J17': 'J17  SIM800L', 'J18': 'J18  RASPBERRY PI'}
J18TXT = {'1': 'GND\npin6', '2': 'TX\npin8', '3': 'RX\npin10'}
NETCOL = lambda n: ('#d62728' if n == '+5V_AUX' else '#ff7f0e' if n == '+9V' else '#9467bd' if n == '+4V0'
                    else '#555555' if n == 'GND' else '#1f77b4')


def board(ax, title, mirror=False):
    ax.add_patch(Rectangle((0, 0), W, H, fc='#1f5e3a' if not mirror else '#c98b5a', ec='k', lw=1.5, zorder=0))
    for r in ('H1', 'H2', 'H3', 'H4'):
        x, y = xy(P[r]['pads'][0], mirror)
        ax.add_patch(Circle((x, y), 1.6, fc='white', ec='k', lw=0.8, zorder=2))
    ax.set_xlim(-3, W + 3); ax.set_ylim(H + 3, -3); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title, fontsize=15, fontweight='bold', loc='left')


def xy(pad, mirror=False):
    return (W - pad['x'] if mirror else pad['x'], pad['y'])


def pads_bbox(ref, mirror=False, m=1.5):
    xs = [xy(p, mirror)[0] for p in P[ref]['pads']]; ys = [p['y'] for p in P[ref]['pads']]
    return min(xs) - m, min(ys) - m, max(xs) - min(xs) + 2 * m, max(ys) - min(ys) + 2 * m


def draw_parts(ax, highlight=None, labels=True, pinlabels=True, mirror=False, dim='#3d7a57'):
    hl = lambda r: highlight is None or r in highlight
    # Nano socket
    a = P['A1']; x0, y0, w, h = pads_bbox('A1', mirror, 1.6)
    on = hl('A1')
    ax.add_patch(Rectangle((x0, y0), w, h, fc='#2b6cb0' if on else dim, ec='white', lw=1.2, alpha=0.9, zorder=3))
    ux = x0 - 6 if not mirror else x0 + w
    ax.add_patch(Rectangle((ux, y0 + h / 2 - 4), 6, 8, fc='#cccccc' if on else dim, ec='white', lw=1, zorder=3))
    ax.text(ux + 3, y0 + h / 2, 'USB', ha='center', va='center', fontsize=8, rotation=90, zorder=4)
    for p in a['pads']:
        x, y = xy(p, mirror)
        ax.add_patch(Circle((x, y), 0.8, fc='#f2c94c', ec='k', lw=0.4, zorder=4))
    if labels:
        ax.text(x0 + w / 2, y0 + h / 2, 'ARDUINO NANO\n(female socket, USB to the LEFT)', ha='center', va='center',
                fontsize=10, color='white', fontweight='bold', zorder=5)
        for p in a['pads']:
            nm = {'4': 'GND', '29': 'GND', '27': '5V', '30': 'VIN'}.get(p['n'])
            pin = int(p['n']); lab = nm or (f"D{pin - 3}" if 5 <= pin <= 15 else f"A{pin - 19}" if 19 <= pin <= 26 else '')
            if lab:
                x, y = xy(p, mirror)
                ax.text(x, y + (-2.2 if pin <= 15 else 2.2), lab, ha='center', va='center', fontsize=5.5, color='white', zorder=5)
    for ref, part in P.items():
        if ref[0] not in 'JRC' or ref == 'A1':
            continue
        on = hl(ref)
        if ref.startswith('J'):
            x0, y0, w, h = pads_bbox(ref, mirror, 1.4 if ref != 'J12' else 2.2)
            ax.add_patch(Rectangle((x0, y0), w, h, fc='#111111' if on else dim, ec='#f2c94c' if on else 'none', lw=1.2, zorder=3))
            for p in part['pads']:
                x, y = xy(p, mirror)
                ax.add_patch(Circle((x, y), 0.75 if ref != 'J12' else 1.2, fc='#f2c94c' if on else '#7aa58a', ec='k', lw=0.4, zorder=4))
                if pinlabels and on and ref not in ('J1', 'J2', 'J3', 'J4', 'J5'):
                    t = J18TXT[p['n']] if ref == 'J18' else SHORT.get(p['net'], p['net'])
                    if ref == 'J12' or ref == 'J13':
                        t = '+' if p['net'] == '+5V_AUX' else '-'
                    if ref == 'J14' or ref == 'J16':
                        t = ['IN+', 'IN-', 'OUT+', 'OUT-'][int(p['n']) - 1]
                    if ref == 'J15':
                        t = ['+9V', '-'][int(p['n']) - 1]
                    vert = h > w
                    dy = 2.6 if ref == 'J17' else -2.6
                    ax.text(x + (2.6 if vert else 0), y + (0 if vert else dy), t, ha='left' if vert else 'center',
                            va='center', fontsize=6.5, color='#ffe08a', fontweight='bold', zorder=6)
            if labels and on:
                vert = h > w
                tx, ty = (x0 + w / 2, y0 - 1.0) if vert else (x0 + w / 2, y0 + h + 1.6)
                if ref in ('J9', 'J10', 'J18'):
                    tx, ty = x0 + w / 2, y0 - 3.2
                if ref in ('J11', 'J17'):
                    tx, ty = x0 + w / 2, y0 + h + (4.0 if ref == 'J17' else 0.6)
                if ref in ('J1', 'J2', 'J3', 'J4', 'J5') and pinlabels:
                    sig = SHORT[[q for q in part['pads'] if q['n'] == '3'][0]['net']]
                    ax.text(x0 + w / 2, y0 + h + 0.8, '5V\nGND\n' + sig, ha='center', va='top', fontsize=6.5,
                            color='#ffe08a', fontweight='bold', zorder=6, linespacing=1.0)
                ax.text(tx, ty, NAME[ref], ha='center', va='bottom' if vert else 'top', fontsize=7.5, color='white',
                        fontweight='bold', zorder=6, bbox=dict(fc='#000000aa', ec='none', pad=1))
        elif ref.startswith('R'):
            (xa, ya), (xb, yb) = xy(part['pads'][0], mirror), xy(part['pads'][1], mirror)
            col = '#e9c46a' if on else dim
            standing = abs(xa - xb) + abs(ya - yb) < 3
            if standing:
                ax.add_patch(Circle((xa, ya), 1.3, fc=col, ec='k', lw=0.6, zorder=4))
                ax.plot([xa, xb], [ya, yb], color='#cccccc', lw=1.2, zorder=3)
                ax.add_patch(Circle((xb, yb), 0.6, fc='#f2c94c', ec='k', lw=0.4, zorder=4))
            else:
                ax.plot([xa, xb], [ya, yb], color='#cccccc', lw=1.2, zorder=3)
                cx, cy = (xa + xb) / 2, (ya + yb) / 2
                ax.add_patch(FancyBboxPatch((cx - 1.3, cy - 3.2), 2.6, 6.4, boxstyle='round,pad=0.2', fc=col, ec='k', lw=0.6, zorder=4))
                for (x, y) in ((xa, ya), (xb, yb)):
                    ax.add_patch(Circle((x, y), 0.6, fc='#f2c94c', ec='k', lw=0.4, zorder=4))
            if labels and on:
                v = part['val'].split()[0].replace('R', ' ohm') if part['val'].startswith('220') else part['val'].split()[0]
                ox, oy = {'R5': (-6.3, 2.4), 'R6': (-8.4, -4.6), 'R1': (2.0, 4.0)}.get(ref, (2.0, 1.6))
                ax.text(xa + ox, ya + oy, f"{ref} {v}", fontsize=7, color='white', fontweight='bold', zorder=6,
                        bbox=dict(fc='#7a5c00', ec='none', pad=0.6))
        elif ref.startswith('C'):
            (xa, ya), (xb, yb) = xy(part['pads'][0], mirror), xy(part['pads'][1], mirror)
            r = 4.0 if ref == 'C1' else 5.0
            cx, cy = (xa + xb) / 2, (ya + yb) / 2
            ax.add_patch(Circle((cx, cy), r, fc='#2f6fd6' if on else dim, ec='white', lw=1, alpha=0.85, zorder=3))
            L = ((xb - xa) ** 2 + (yb - ya) ** 2) ** 0.5; ux, uy = (xb - xa) / L, (yb - ya) / L; vx, vy = -uy, ux
            if on:
                sx, sy = cx + ux * r * 0.72, cy + uy * r * 0.72
                ax.plot([sx - vx * r * 0.68, sx + vx * r * 0.68], [sy - vy * r * 0.68, sy + vy * r * 0.68], color='white', lw=5, zorder=4)
            for (x, y), sg, k in (((xa, ya), '+', -1), ((xb, yb), '-', 1)):
                ax.add_patch(Circle((x, y), 0.8, fc='#f2c94c', ec='k', lw=0.4, zorder=5))
                if on:
                    ax.text(x + vx * 1.9, y + vy * 1.9, sg, ha='center', va='center', fontsize=13, color='yellow', fontweight='bold', zorder=6)
            if labels and on:
                ly, va = (cy - r - 0.6, 'bottom') if ref == 'C2' else (cy + r + 1.5, 'top')
                ax.text(cx, ly, f"{ref} {part['val']}\nLONG leg = +", ha='center', va=va, fontsize=7,
                        color='white', fontweight='bold', zorder=6, bbox=dict(fc='#1d3f7a', ec='none', pad=0.8))


# ---------- 1. placement ----------
fig, ax = plt.subplots(figsize=(17, 12.5), dpi=130)
board(ax, '1.  PART PLACEMENT  -  component side (no copper)   |   Sensor Hub v1.2, 104 x 72 mm')
draw_parts(ax)
fig.text(0.02, 0.03, 'Read it like this: the yellow text next to every pin is what that pin carries.  '
         '5V = sensor power (from AUX charger on J12), GND = ground, D2..D12 / A0..A6 = Nano pins.\n'
         'Resistors:  R1 4.7k (lies flat)  |  R2 R3 R4 220 ohm, R5 4.7k, R6 10k, R7 10k, R8 4.7k (all STANDING: body on the round pad, '
         'bent leg into the small pad).   Capacitors: LONG leg into the + pad.', fontsize=10)
fig.savefig(os.path.join(OUT, '1_part_placement.png'), bbox_inches='tight'); plt.close(fig)

# ---------- 2. assembly order ----------
steps = [('STEP 1 - resistors (lowest parts first)', {'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8'}),
         ('STEP 2 - Nano socket: two 1x15 FEMALE headers', {'A1'}),
         ('STEP 3 - all pin headers J1-J11, J13-J18', {f'J{i}' for i in range(1, 19)} - {'J12'}),
         ('STEP 4 - capacitors (+ !) and screw terminal J12', {'C1', 'C2', 'J12'})]
fig, axs = plt.subplots(2, 2, figsize=(20, 14), dpi=110)
for ax, (t, hs) in zip(axs.flat, steps):
    board(ax, t); draw_parts(ax, highlight=hs, pinlabels=False)
fig.suptitle('2.  SOLDERING ORDER  (bright = solder now, dim = later).   Solder on the COPPER side, parts on this side.',
             fontsize=15, fontweight='bold', x=0.02, ha='left')
fig.savefig(os.path.join(OUT, '2_soldering_order.png'), bbox_inches='tight'); plt.close(fig)

# ---------- 3. copper side continuity test ----------
from shapely.geometry import Polygon
fig, ax = plt.subplots(figsize=(17, 12.5), dpi=130)
ax.add_patch(Rectangle((0, 0), W, H, fc='#c98b5a', ec='k', lw=1.5, zorder=0))
for f in G['features']:
    pg = Polygon(f[0], f[1]).buffer(0)
    for g in getattr(pg, 'geoms', [pg]):
        xs, ys = g.exterior.xy
        ax.fill([W - x for x in xs], ys, fc=NETCOL(f[2]) if not f[2].startswith(('NC_', 'TEXT')) else '#e6b07a',
                ec='#3b2a1a', lw=0.5, zorder=2)
for p in P['A1']['pads'] + [q for r in P for q in P[r]['pads'] if r != 'A1' and q['net'] == 'GND']:
    x, y = xy(p, True)
    ax.add_patch(Circle((x, y), 0.3, fc='k', zorder=3))
for ref in NAME:
    x0, y0, w, h = pads_bbox(ref, True, 1.6)
    ax.text(x0 + w / 2, y0 - 0.8, ref, ha='center', va='bottom', fontsize=8, fontweight='bold', color='k',
            bbox=dict(fc='white', ec='none', alpha=0.8, pad=0.5), zorder=6)
nx0, ny0, nw, nh = pads_bbox('A1', True, 1.6)
ax.text(nx0 + nw / 2, ny0 + nh / 2, 'NANO pads\n(USB end is on the RIGHT\nwhen you look at the copper)', ha='center',
        va='center', fontsize=9, zorder=6, bbox=dict(fc='white', ec='none', alpha=0.85))
ax.set_xlim(-3, W + 3); ax.set_ylim(H + 3, -3); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('3.  COPPER SIDE - continuity test colours (board turned over, copper facing you)', fontsize=15,
             fontweight='bold', loc='left')
leg = [('#d62728', '5V sensor/AUX rail'), ('#ff7f0e', '9V rail'), ('#9467bd', '4.0V SIM rail'),
       ('#1f77b4', 'signal tracks'), ('#c98b5a', 'big copper area = GND')]
for i, (c, t) in enumerate(leg):
    ax.add_patch(Rectangle((2 + i * 21, H + 0.6), 3, 2, fc=c, ec='k', lw=0.5, zorder=7, clip_on=False))
    ax.text(6 + i * 21, H + 1.6, t, va='center', fontsize=9, zorder=7)
fig.text(0.02, 0.02, 'RULES:  same colour = must BEEP together.   Red / orange / purple / blue must NEVER beep to the big copper (GND).\n'
         'Two different blue tracks must never beep to each other.   Every GND pin (black dot on copper) must beep to J12 "-".',
         fontsize=11, fontweight='bold')
fig.savefig(os.path.join(OUT, '3_copper_continuity_colours.png'), bbox_inches='tight'); plt.close(fig)

# ---------- 4. power-up voltages ----------
fig, ax = plt.subplots(figsize=(17, 12.5), dpi=130)
board(ax, '4.  POWER-UP CHECK - DC volts, black probe on J12 "-" (GND).  NO Nano, NO modules plugged in yet')
draw_parts(ax, pinlabels=True)
marks = [('J12', '1', 'A', '+5.0 V  (AUX charger)'), ('J5', '1', 'B', '+5.0 V on pin "5V" of J1..J5'),
         ('J13', '1', 'C', '+5.0 V  (pump power)'), ('J15', '1', 'D', '+9.0 V  (after setting the step-up)'),
         ('J17', '4', 'E', '+4.0 V  (set step-down BEFORE the SIM800L)')]
for ref, n, k, t in marks:
    p = [q for q in P[ref]['pads'] if q['n'] == n][0]
    ax.add_patch(Circle((p['x'], p['y']), 2.2, fc='none', ec='#ff2d2d', lw=3, zorder=8))
    ax.text(p['x'] + 2.6, p['y'] - 2.6, k, fontsize=16, color='#ff2d2d', fontweight='bold', zorder=8)
fig.text(0.02, 0.02, '   '.join(f'{k}: {t}' for _, _, k, t in marks), fontsize=11, fontweight='bold')
fig.savefig(os.path.join(OUT, '4_power_up_voltages.png'), bbox_inches='tight'); plt.close(fig)
print(sorted(os.listdir(OUT)))
