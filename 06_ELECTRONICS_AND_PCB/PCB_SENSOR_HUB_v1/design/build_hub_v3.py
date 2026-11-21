# AquaSentinel Sensor Hub - single-sided carrier PCB for the Arduino Nano (run with KiCad 10's python.exe)
# Copper on B.Cu only (milled on the TTC-450 Pro), parts on top. Board 145 x 90 mm on a 155 x 100 mm blank.
import os, sys, pcbnew
from pcbnew import VECTOR2I, FromMM

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'AquaSentinel_Sensor_Hub.kicad_pcb')
FPLIB = r'C:/Users/dell/AppData/Local/Programs/KiCad/10.0/share/kicad/footprints/'
W, H = 104.0, 72.0
OX, OY = 100.0, 100.0                       # board origin on the KiCad page
PAD = 1.9                                    # all pads enlarged for milling + hand drilling
SIG, PWR5, BIG = 0.8, 1.0, 2.0              # track widths (mm)

b = pcbnew.BOARD()
P = lambda x, y: VECTOR2I(FromMM(OX + x), FromMM(OY + y))
nets = {}


def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(b, name); b.Add(n); nets[name] = n
    return nets[name]


def set_pad(pad, size=PAD, drill=None):
    for fn in (lambda: pad.SetSize(pcbnew.PADSTACK.ALL_LAYERS, VECTOR2I(FromMM(size), FromMM(size))),
               lambda: pad.SetSize(VECTOR2I(FromMM(size), FromMM(size)))):
        try: fn(); break
        except Exception: pass
    for fn in (lambda: pad.SetShape(pcbnew.PADSTACK.ALL_LAYERS, pcbnew.PAD_SHAPE_CIRCLE),
               lambda: pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)):
        try: fn(); break
        except Exception: pass
    if drill: pad.SetDrillSize(VECTOR2I(FromMM(drill), FromMM(drill)))


fps = {}


def place(lib, name, ref, value, x, y, rot, padnets, size=PAD, drill=None):
    fp = pcbnew.FootprintLoad(FPLIB + lib + '.pretty', name)
    fp.SetReference(ref); fp.SetValue(value)
    fp.SetOrientationDegrees(rot)
    b.Add(fp)
    # put pad 1 exactly at (x, y)
    p1 = [p for p in fp.Pads() if p.GetNumber() == '1'][0].GetPosition()
    pos = fp.GetPosition()
    fp.SetPosition(VECTOR2I(pos.x + P(x, y).x - p1.x, pos.y + P(x, y).y - p1.y))
    for p in fp.Pads():
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
            set_pad(p, size, drill)
        if p.GetNumber() in padnets:
            p.SetNet(net(padnets[p.GetNumber()]))
    fps[ref] = fp
    return fp


def pad_xy(ref, num):
    p = [q for q in fps[ref].Pads() if q.GetNumber() == str(num)][0].GetPosition()
    return (round(pcbnew.ToMM(p.x) - OX, 3), round(pcbnew.ToMM(p.y) - OY, 3))


def track(points, netname, width):
    pts = [pad_xy(*p) if isinstance(p, tuple) and isinstance(p[0], str) else p for p in points]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(P(x1, y1)); t.SetEnd(P(x2, y2)); t.SetWidth(FromMM(width))
        t.SetLayer(pcbnew.B_Cu); t.SetNet(net(netname)); b.Add(t)


def hdr(n, ref, value, x, y, direction, padnets):
    """1 x n pin header, pad 1 at (x, y), pins going 'down' (+y) or 'right' (+x)."""
    rot = 0 if direction == 'down' else 90
    fp = place('Connector_PinHeader_2.54mm', f'PinHeader_1x{n:02d}_P2.54mm_Vertical', ref, value, x, y, rot, padnets)
    if direction == 'right' and pad_xy(ref, 2)[0] < x:          # make sure pins go +x
        fp.SetOrientationDegrees(-90); place_fix(fp, x, y)
    return fp


def place_fix(fp, x, y):
    p1 = [p for p in fp.Pads() if p.GetNumber() == '1'][0].GetPosition()
    pos = fp.GetPosition()
    fp.SetPosition(VECTOR2I(pos.x + P(x, y).x - p1.x, pos.y + P(x, y).y - p1.y))


def orient(ref, x, y, want2):
    """rotate a 2-pad part until pad 2 sits at want2 (pad 1 stays at x, y)"""
    for r in (0, 90, 180, 270):
        fps[ref].SetOrientationDegrees(r); place_fix(fps[ref], x, y)
        px, py = pad_xy(ref, 2)
        if abs(px - want2[0]) < 0.05 and abs(py - want2[1]) < 0.05:
            return
    raise RuntimeError(f'{ref}: cannot orient pad 2 to {want2}')


# ===== AquaSentinel Sensor Hub v1.2 - 104 x 72 mm landscape layout (appended to the helpers of build_hub.py) =====
# Sensors' 5 V now comes from the AUX charger rail (+5V_AUX); the Nano is powered by the Pi's USB. Grounds shared.

for (x1, y1, x2, y2) in ((0, 0, W, 0), (W, 0, W, H), (W, H, 0, H), (0, H, 0, 0)):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
    s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2)); s.SetWidth(FromMM(0.1)); b.Add(s)

# ---------------- Arduino Nano: top row y=36 (pins 1-15), bottom row y=51.24, USB at the left ----------------
NANO = {'4': 'GND', '29': 'GND',
        '5': 'D2_TEMP', '6': 'D3_AIR', '7': 'D4_LIGHT', '8': 'D5_TURB', '9': 'D6_ALC',
        '10': 'D7_G', '11': 'D8_R', '12': 'D9_B', '13': 'D10_PUMP', '14': 'D11_SP', '15': 'D12_SP',
        '19': 'A0_TDSPWR', '20': 'A1_TDS', '21': 'A2_SP', '22': 'A3_SP', '23': 'A4_SP', '24': 'A5_SP', '25': 'A6_PH'}
NX0, NY0 = 43.56, 36.0
nano = place('Module', 'Arduino_Nano', 'A1', 'Arduino Nano (socket)', NX0, NY0, 90, NANO)
if not (abs(pad_xy('A1', 15)[0] - 8.0) < 0.05 and abs(pad_xy('A1', 16)[1] - 51.24) < 0.05):
    nano.SetOrientationDegrees(-90); place_fix(nano, NX0, NY0)
assert abs(pad_xy('A1', 15)[0] - 8.0) < 0.05 and abs(pad_xy('A1', 16)[1] - 51.24) < 0.05
NX = lambda pin: pad_xy('A1', pin)[0]

# ---------------- top band: 5 V sensors, column = 5V / GND / SIG ----------------
cols = [('J1', 'ALCOHOL MQ-3', 'D6_ALC', 9, 32.0, 21.5), ('J2', 'TURBIDITY', 'D5_TURB', 8, 39.0, 23.5),
        ('J3', 'LIGHT LDR', 'D4_LIGHT', 7, 46.0, 25.5), ('J4', 'AIR DHT11', 'D3_AIR', 6, 53.0, 27.5),
        ('J5', 'WATER TEMP DS18B20', 'D2_TEMP', 5, 60.0, 29.5)]
for ref, val, sig, pin, cx, turn in cols:
    hdr(3, ref, val, cx, 12.0, 'down', {'1': '+5V_AUX', '2': 'GND', '3': sig})
    track([('A1', pin), (NX(pin), turn), (cx, turn), (ref, 3)], sig, SIG)
    track([(ref, 1), (cx, 6.0)], '+5V_AUX', PWR5)
track([(32.0, 6.0), (72.0, 6.0)], '+5V_AUX', PWR5)                                  # sensor 5 V bus
track([('J1', 2), ('J2', 2), ('J3', 2), ('J4', 2), ('J5', 2), (64.0, 14.54), (64.0, 31.5), (35.94, 31.5), ('A1', 4)],
      'GND', PWR5)                                                                   # GND chain -> Nano GND
place('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 'R1', '4.7k DS18B20 pull-up',
      56.5, 9.0, 90, {'1': '+5V_AUX', '2': 'D2_TEMP'})
orient('R1', 56.5, 9.0, (56.5, 19.16))
track([('R1', 1), (56.5, 6.0)], '+5V_AUX', PWR5)
track([('R1', 2), (60.0, 19.16)], 'D2_TEMP', SIG)

# ---------------- top-left: RGB beacon (standing 220R), pump control (+10k), spare ----------------
for ref, rnet, pin, y1 in (('R2', 'D7_G', 10, 28.0), ('R3', 'D8_R', 11, 23.0), ('R4', 'D9_B', 12, 18.0)):
    x = NX(pin)
    place('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical', ref, '220R', x, y1, 0,
          {'1': rnet, '2': rnet + '_LED'})
    orient(ref, x, y1, (x, y1 - 2.54))
    track([('A1', pin), (ref, 1)], rnet, SIG)
hdr(4, 'J6', 'BEACON RGB (B R G -)', NX(12), 5.0, 'right', {'1': 'D9_B_LED', '2': 'D8_R_LED', '3': 'D7_G_LED', '4': 'GND'})
track([('R4', 2), ('J6', 1)], 'D9_B_LED', SIG)
track([('R3', 2), ('J6', 2)], 'D8_R_LED', SIG)
track([('R2', 2), ('J6', 3)], 'D7_G_LED', SIG)
hdr(3, 'J7', 'PUMP CTRL (GND IN2 IN1)', 5.46, 5.0, 'right', {'1': 'GND', '2': 'GND', '3': 'D10_PUMP'})
track([('A1', 13), (13.08, 10.0), (10.54, 10.0), ('J7', 3)], 'D10_PUMP', SIG)
place('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical', 'R7', '10k pump pull-down', 13.08, 13.0, 0,
      {'1': 'D10_PUMP', '2': 'GND'})
orient('R7', 13.08, 13.0, (10.54, 13.0))
hdr(3, 'J8', 'SPARE (D11 D12 GND)', 3.0, 17.0, 'down', {'1': 'D11_SP', '2': 'D12_SP', '3': 'GND'})
track([('A1', 14), (10.54, 17.0), ('J8', 1)], 'D11_SP', SIG)
track([('A1', 15), (8.0, 19.54), ('J8', 2)], 'D12_SP', SIG)

# ---------------- bottom-left: TDS, analog spare, pH signal ----------------
hdr(3, 'J9', 'TDS (GND PWR SIG)', 10.0, 64.0, 'right', {'1': 'GND', '2': 'A0_TDSPWR', '3': 'A1_TDS'})
track([('A1', 19), (NX(19), 57.0), (12.54, 57.0), ('J9', 2)], 'A0_TDSPWR', SIG)
track([('A1', 20), (NX(20), 60.0), (15.08, 60.0), ('J9', 3)], 'A1_TDS', SIG)
hdr(4, 'J10', 'ANALOG SPARE (A2 A3 A4 A5)', NX(21), 64.0, 'right', {'1': 'A2_SP', '2': 'A3_SP', '3': 'A4_SP', '4': 'A5_SP'})
for pin, k, nn in ((21, 1, 'A2_SP'), (22, 2, 'A3_SP'), (23, 3, 'A4_SP'), (24, 4, 'A5_SP')):
    track([('A1', pin), ('J10', k)], nn, SIG)
place('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical', 'R8', '4.7k pH protect', NX(25), 57.0, 0,
      {'1': 'A6_PH', '2': 'PH_IN'})
orient('R8', NX(25), 57.0, (NX(25), 59.54))
track([('A1', 25), ('R8', 1)], 'A6_PH', SIG)
hdr(2, 'J11', 'pH SIGNAL (O GND)', NX(25), 67.5, 'right', {'1': 'PH_IN', '2': 'GND'})
track([('R8', 2), ('J11', 1)], 'PH_IN', SIG)

# ---------------- right side: power (AUX 5 V -> step-up 9 V -> step-down 4.0 V -> SIM800L) ----------------
place('TerminalBlock_Phoenix', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal', 'J12', 'AUX 5V IN',
      98.0, 14.0, 90, {'1': '+5V_AUX', '2': 'GND'}, size=2.6, drill=1.3)
orient('J12', 98.0, 14.0, (98.0, 19.08))
track([(72.0, 6.0), (72.0, 34.0), (80.0, 34.0)], '+5V_AUX', BIG)                     # trunk -> step-up IN+
track([('J12', 1), (72.0, 14.0)], '+5V_AUX', BIG)
place('Capacitor_THT', 'CP_Radial_D8.0mm_P3.50mm', 'C1', '470uF 16V', 86.0, 14.0, 0, {'1': '+5V_AUX', '2': 'GND'})
orient('C1', 86.0, 14.0, (86.0, 17.5))
hdr(2, 'J13', 'PUMP POWER (+ -)', 88.0, 26.0, 'right', {'1': '+5V_AUX', '2': 'GND'})
track([(72.0, 26.0), ('J13', 1)], '+5V_AUX', BIG)
hdr(4, 'J14', 'STEP-UP 9V (IN+ IN- OUT+ OUT-)', 80.0, 34.0, 'down', {'1': '+5V_AUX', '2': 'GND', '3': '+9V', '4': 'GND'})
hdr(2, 'J15', 'pH POWER 9V (+ -)', 90.0, 39.08, 'down', {'1': '+9V', '2': 'GND'})
track([('J14', 3), ('J15', 1)], '+9V', 1.2)
hdr(4, 'J16', 'STEP-DOWN 4.0V (IN+ IN- OUT+ OUT-)', 80.0, 46.0, 'down', {'1': '+9V', '2': 'GND', '3': '+4V0', '4': 'GND'})
track([(84.0, 39.08), (84.0, 46.0), ('J16', 1)], '+9V', 1.2)
hdr(4, 'J17', 'SIM800L (RXD TXD GND VCC)', 87.38, 64.0, 'right', {'1': 'SIM_RXD', '2': 'SIM_TXD', '3': 'GND', '4': '+4V0'})
track([('J16', 3), (95.0, 51.08), ('J17', 4)], '+4V0', BIG)
place('Capacitor_THT', 'CP_Radial_D10.0mm_P5.00mm', 'C2', '1000uF 16V', 95.0, 56.0, 0, {'1': '+4V0', '2': 'GND'})
orient('C2', 95.0, 56.0, (90.0, 56.0))
hdr(3, 'J18', 'RASPBERRY PI (GND6 TX8 RX10)', 70.0, 64.0, 'right', {'1': 'GND', '2': 'PI_TX', '3': 'SIM_TXD'})
track([('J17', 2), (89.92, 67.0), (75.08, 67.0), ('J18', 3)], 'SIM_TXD', SIG)
place('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical', 'R5', '4.7k', 84.0, 61.0, 0,
      {'1': 'SIM_RXD', '2': 'PI_TX'})
orient('R5', 84.0, 61.0, (81.46, 61.0))
place('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical', 'R6', '10k', 87.38, 61.0, 0,
      {'1': 'SIM_RXD', '2': 'GND'})
orient('R6', 87.38, 61.0, (87.38, 58.46))
track([('J17', 1), ('R6', 1), ('R5', 1)], 'SIM_RXD', SIG)
track([('R5', 2), (72.54, 61.0), ('J18', 2)], 'PI_TX', SIG)

# ---------------- title (B.Cu, mirrored to read from the copper side) ----------------
for txt, x, y, hgt, th in (('AquaSentinel', 53.0, 44.0, 2.4, 0.5), ('HUB v1.2', 58.0, 44.0, 2.0, 0.45)):
    t = pcbnew.PCB_TEXT(b); t.SetText(txt); t.SetLayer(pcbnew.B_Cu); t.SetMirrored(True)
    t.SetTextSize(VECTOR2I(FromMM(hgt), FromMM(hgt))); t.SetTextThickness(FromMM(th))
    t.SetTextAngleDegrees(90); t.SetPosition(P(x, y)); b.Add(t)

# ---------------- mounting holes ----------------
for i, (x, y) in enumerate(((3.5, 29.0), (100.5, 3.5), (3.5, 68.5), (100.5, 68.5))):
    fp = pcbnew.FootprintLoad(FPLIB + 'MountingHole.pretty', 'MountingHole_3.2mm_M3')
    fp.SetReference(f'H{i+1}'); fp.SetPosition(P(x, y)); b.Add(fp)

# ---------------- GND pour on B.Cu + rules ----------------
z = pcbnew.ZONE(b); z.SetLayer(pcbnew.B_Cu); z.SetNet(net('GND'))
o = z.Outline(); o.NewOutline()
for (x, y) in ((0.5, 0.5), (W - 0.5, 0.5), (W - 0.5, H - 0.5), (0.5, H - 0.5)):
    o.Append(FromMM(OX + x), FromMM(OY + y))
z.SetLocalClearance(FromMM(0.6)); z.SetMinThickness(FromMM(0.5))
z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
b.Add(z)
ds = b.GetDesignSettings()
try:
    nc = ds.m_NetSettings.GetDefaultNetclass(); nc.SetClearance(FromMM(0.5)); nc.SetTrackWidth(FromMM(SIG))
except Exception as e:
    print('netclass rule not set:', e)
ds.m_MinClearance = FromMM(0.5); ds.m_TrackMinWidth = FromMM(0.5)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(OUT)
print('saved', OUT)
