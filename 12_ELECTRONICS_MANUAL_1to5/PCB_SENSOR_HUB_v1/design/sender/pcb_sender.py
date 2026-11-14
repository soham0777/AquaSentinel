#!/usr/bin/env python3
"""AquaSentinel PCB sender for the TwoTrees TTC-450 Pro (GRBL 1.1) - with Z-probe height map (auto-levelling).

Run in a terminal next to the machine:   python pcb_sender.py            (port COM18)
                                         python pcb_sender.py --port COM5
                                         python pcb_sender.py --check FILE.nc   (GRBL check mode, NO motion)

While a job runs:  P = pause (feed hold)   R = resume   S = STOP (soft reset, spindle off).  The red E-stop always wins.
"""
import argparse, json, math, os, re, sys, time

try:
    import serial
except ImportError:
    sys.exit('pyserial missing:  python -m pip install pyserial')
try:
    import msvcrt                                    # Windows keyboard
except ImportError:
    msvcrt = None

HERE = os.path.dirname(os.path.abspath(__file__))
MAPFILE = os.path.join(HERE, 'heightmap.json')
BOARD = (0.0, 0.0, 104.0, 72.0)                      # cut area: origin = board's lower-left corner
SEG = 2.0                                            # split cutting moves into <= 2 mm pieces for levelling


# ------------------------------------------------------------------ GRBL link
class Grbl:
    def __init__(self, port):
        self.s = serial.Serial()                     # open WITHOUT toggling DTR/RTS: never resets the controller
        self.s.port, self.s.baudrate, self.s.timeout = port, 115200, 0.1
        self.s.dtr = False; self.s.rts = False
        self.s.open()
        time.sleep(0.5)
        self.s.write(b'\r\n'); time.sleep(0.5)
        self.s.reset_input_buffer()

    def rt(self, ch):                                # real-time command: ? ! ~ 0x18
        self.s.write(ch if isinstance(ch, bytes) else ch.encode())

    def readline(self, wait=0.1):
        return self.s.readline().decode(errors='replace').strip()     # serial timeout = 0.1 s

    def cmd(self, line, timeout=120, echo=True):
        """Send one line, wait for ok/error. Returns (ok, list_of_messages)."""
        self.s.write((line.strip() + '\n').encode())
        msgs, t = [], time.time()
        while time.time() - t < timeout:
            r = self.readline(0.05)
            if not r:
                continue
            if r == 'ok':
                return True, msgs
            if r.startswith('error') or r.startswith('ALARM'):
                if echo: print('   GRBL:', r)
                return False, msgs + [r]
            msgs.append(r)
            if echo and not r.startswith('<'):
                print('   GRBL:', r)
        return False, msgs + ['timeout']

    def status(self):
        self.s.reset_input_buffer(); self.rt('?')
        t = time.time()
        while time.time() - t < 2:
            r = self.readline(0.05)
            if r.startswith('<'):
                return r
        return '(no status)'

    def wait_idle(self, timeout=600):
        t = time.time()
        while time.time() - t < timeout:
            st = self.status()
            if st.startswith('<Idle'):
                return True
            if st.startswith('<Alarm'):
                return False
            time.sleep(0.2)
        return False


def wpos(st):
    m = re.search(r'WPos:([-\d.]+),([-\d.]+),([-\d.]+)', st)
    if m:
        return tuple(float(v) for v in m.groups())
    m = re.search(r'MPos:([-\d.]+),([-\d.]+),([-\d.]+)', st); w = re.search(r'WCO:([-\d.]+),([-\d.]+),([-\d.]+)', st)
    if m and w:
        return tuple(float(a) - float(b) for a, b in zip(m.groups(), w.groups()))
    return None


def ask(q):
    return input(q + ' ').strip()


# ------------------------------------------------------------------ height map
def bilinear(hm, x, y):
    xs, ys, z = hm['xs'], hm['ys'], hm['z']
    x = min(max(x, xs[0]), xs[-1]); y = min(max(y, ys[0]), ys[-1])
    i = max(0, min(len(xs) - 2, next((k for k in range(len(xs) - 1) if x <= xs[k + 1]), len(xs) - 2)))
    j = max(0, min(len(ys) - 2, next((k for k in range(len(ys) - 1) if y <= ys[k + 1]), len(ys) - 2)))
    tx = (x - xs[i]) / (xs[i + 1] - xs[i]); ty = (y - ys[j]) / (ys[j + 1] - ys[j])
    a, b = z[j][i], z[j][i + 1]; c, d = z[j + 1][i], z[j + 1][i + 1]
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


def level(lines, hm):
    """Add the height map to every Z at or below 0 (cutting / plunging); split long cutting moves."""
    out, x, y, z = [], 0.0, 0.0, 15.0
    for raw in lines:
        l = raw.split('(')[0].strip().upper()
        if not l:
            continue
        m = re.match(r'G([01])\b', l)
        if not m:
            out.append(l); continue
        g = m.group(1)
        vals = dict((a, float(v)) for a, v in re.findall(r'([XYZF])(-?[\d.]+)', l))
        nx, ny, nz = vals.get('X', x), vals.get('Y', y), vals.get('Z', z)
        f = f' F{vals["F"]:g}' if 'F' in vals else ''
        if nz > 0.0001 or hm is None:                 # travel height: unchanged
            out.append(l)
        elif g == '1' and ('X' in vals or 'Y' in vals):
            dist = math.hypot(nx - x, ny - y); n = max(1, int(math.ceil(dist / SEG)))
            for k in range(1, n + 1):
                px = x + (nx - x) * k / n; py = y + (ny - y) * k / n; pz = z + (nz - z) * k / n
                out.append(f'G1 X{px:.3f} Y{py:.3f} Z{pz + bilinear(hm, px, py):.3f}' + (f if k == 1 else ''))
        else:                                          # plunge at the current XY
            out.append(f'G{g} X{nx:.3f} Y{ny:.3f} Z{nz + bilinear(hm, nx, ny):.3f}{f}')
        x, y, z = nx, ny, nz
    return out


# ------------------------------------------------------------------ actions
def act_status(g):
    print('  ', g.status())


def act_unlock(g):
    print('   unlocking ($X)'); g.cmd('$X')


def act_home(g):
    if ask('   HOME the machine now? Clamps clear of the axes? type YES:') != 'YES':
        return
    ok, _ = g.cmd('$H', timeout=180); print('   homed' if ok else '   homing FAILED')


def act_jog(g):
    print('   jog: e.g.  x 10   y -5   z 1   z -0.1   (mm, relative).  empty line = back to menu')
    while True:
        l = ask('   jog>')
        if not l:
            return
        try:
            ax, d = l.split(); d = float(d); ax = ax.upper(); assert ax in 'XYZ'
        except Exception:
            print('   ?'); continue
        f = 300 if ax == 'Z' else 600
        g.cmd(f'$J=G91 G21 {ax}{d:g} F{f}'); g.wait_idle(); print('  ', g.status())


def act_zero_xy(g):
    print('   the bit must be exactly over the LOWER-LEFT corner of the copper blank')
    if ask('   set X0 Y0 here? type YES:') == 'YES':
        g.cmd('G10 L20 P1 X0 Y0'); print('  ', g.status())


def probe_test(g):
    print('   PROBE TEST: touch the probe clip (on the copper) to the bit by hand ...')
    for _ in range(40):
        st = g.status()
        if re.search(r'Pn:[A-Z]*P', st):
            print('   probe signal OK (Pn:P seen)'); return True
        time.sleep(0.25)
    print('   no probe signal seen in 10 s - check the clip wiring before probing'); return False


def probe_here(g, depth, feed):
    """G38.2 from the current height; returns the work Z of contact or None."""
    ok, msgs = g.cmd(f'G91 G38.2 Z-{depth:g} F{feed:g}', timeout=120)
    g.cmd('G90')
    for m in msgs:
        r = re.match(r'\[PRB:([-\d.]+),([-\d.]+),([-\d.]+):1\]', m)
        if r:
            st = g.status(); w = wpos(st)
            if w:
                return w[2]
    return None


def act_zero_z(g):
    print('   Put the probe clip on the copper blank (clean copper!) and the other clip on the bit.')
    print('   Jog the bit to 2-5 mm ABOVE the copper first.')
    if not probe_test(g):
        return
    if ask('   start Z probe (max 10 mm down, slow)? type YES:') != 'YES':
        return
    z = probe_here(g, 10, 30)
    if z is None:
        print('   no contact - nothing changed'); g.cmd('$X'); return
    g.cmd('G10 L20 P1 Z0')                            # contact point = Z0
    g.cmd('G91 G0 Z2'); g.cmd('G90')
    print('   Z0 set on the copper surface, bit lifted 2 mm.', g.status())


def act_heightmap(g):
    nx = int(ask('   grid points in X [5]:') or 5); ny = int(ask('   grid points in Y [5]:') or 5)
    x0, y0, x1, y1 = BOARD
    xs = [x0 + 3 + (x1 - x0 - 6) * i / (nx - 1) for i in range(nx)]
    ys = [y0 + 3 + (y1 - y0 - 6) * j / (ny - 1) for j in range(ny)]
    print(f'   {nx * ny} points over X {xs[0]:.1f}..{xs[-1]:.1f}  Y {ys[0]:.1f}..{ys[-1]:.1f}.  Z0 must already be set.')
    if not probe_test(g):
        return
    if ask('   start the height map? clamps below Z 2 mm only outside the board? type YES:') != 'YES':
        return
    z = [[None] * nx for _ in range(ny)]
    g.cmd('G90 G0 Z2')
    for j, y in enumerate(ys):
        order = range(nx) if j % 2 == 0 else range(nx - 1, -1, -1)
        for i in order:
            g.cmd(f'G0 X{xs[i]:.3f} Y{ys[j]:.3f}'); g.cmd('G0 Z1')
            v = probe_here(g, 2.5, 20)
            if v is None:
                print('   probe failed at', xs[i], y, '- map aborted'); g.cmd('$X'); g.cmd('G90 G0 Z5'); return
            z[j][i] = round(v, 3); print(f'   X{xs[i]:6.1f} Y{y:6.1f}  Z {v:+.3f}')
            g.cmd('G0 Z2')
    g.cmd('G0 Z15')
    flat = [v for row in z for v in row]
    print(f'   height range {min(flat):+.3f} .. {max(flat):+.3f} mm (spread {max(flat) - min(flat):.3f})')
    json.dump({'xs': xs, 'ys': ys, 'z': z, 'time': time.ctime()}, open(MAPFILE, 'w'), indent=1)
    print('   saved', MAPFILE)


def act_run(g, path=None):
    path = path or ask('   G-code file (drag the file here):').strip('"')
    if not os.path.isfile(path):
        print('   no such file'); return
    lines = open(path).read().splitlines()
    hm = json.load(open(MAPFILE)) if os.path.isfile(MAPFILE) else None
    if hm is None:
        print('   WARNING: no height map - the job runs without levelling.')
    elif ask(f'   use height map from {hm["time"]}? [Y/n]:').lower().startswith('n'):
        hm = None
    job = level(lines, hm)
    zs = [float(v) for l in job for v in re.findall(r'Z(-?[\d.]+)', l)]
    print(f'   {os.path.basename(path)}: {len(job)} lines, lowest Z {min(zs):.3f} mm')
    print('   Spindle starts at full speed. Glasses on, E-stop in reach, dust brush ready.')
    if ask('   type GO to start:') != 'GO':
        return
    t0, n, paused = time.time(), 0, False
    for l in job:
        if msvcrt and msvcrt.kbhit():
            k = msvcrt.getch().upper()
            if k == b'P':
                g.rt('!'); paused = True; print('\n   PAUSED - press R to resume, S to stop')
            if k == b'S':
                g.rt(b'\x18'); time.sleep(1); g.cmd('$X'); g.cmd('M5'); g.cmd('G90 G0 Z15')
                print('\n   STOPPED. Spindle off, bit raised.'); return
        while paused and msvcrt:
            k = msvcrt.getch().upper()
            if k == b'R':
                g.rt('~'); paused = False; print('   resumed')
            elif k == b'S':
                g.rt(b'\x18'); time.sleep(1); g.cmd('$X'); g.cmd('M5'); g.cmd('G90 G0 Z15')
                print('\n   STOPPED. Spindle off, bit raised.'); return
        ok, msgs = g.cmd(l, timeout=600, echo=True)
        if not ok:
            g.rt('!'); print(f'\n   GRBL refused line {n + 1}: {l}  -> job HELD. S = stop, R = resume');
            paused = True
        n += 1
        if n % 25 == 0 or n == len(job):
            el = time.time() - t0
            print(f'\r   {n}/{len(job)} lines  {100 * n / len(job):5.1f} %  {el / 60:5.1f} min', end='')
    g.wait_idle(); print('\n   job finished.', g.status())


def act_check(g, path):
    lines = open(path).read().splitlines()
    print(f'   GRBL check mode ($C) - NO MOTION - {os.path.basename(path)}')
    ok, m = g.cmd('$#', echo=False)                   # leaving $C soft-resets this controller and CLEARS G54: save it
    g54 = next((re.search(r'\[G54:([-\d.]+),([-\d.]+),([-\d.]+)', x).groups() for x in m if x.startswith('[G54:')), None)
    if g54 is None:
        print('   could not read the work zero - check NOT run'); return False
    g.cmd('$C', echo=False)
    bad = 0
    for i, l in enumerate(lines):
        l = l.split('(')[0].strip()
        if not l:
            continue
        ok, msgs = g.cmd(l, timeout=10, echo=False)
        if not ok:
            bad += 1; print(f'   line {i + 1}: {l}  -> {msgs[-1] if msgs else "?"}')
    g.cmd('$C', echo=False)                           # leave check mode (GRBL soft-resets)
    time.sleep(1.5); g.s.reset_input_buffer()
    g.cmd(f'G10 L2 P1 X{g54[0]} Y{g54[1]} Z{g54[2]}', echo=False); g.cmd('G54', echo=False)   # restore the zero
    print(f'   work zero restored: G54 = {g54[0]}, {g54[1]}, {g54[2]}')
    print(f'   {"OK - every line accepted" if bad == 0 else str(bad) + " lines rejected"}')
    return bad == 0


MENU = [('status', act_status), ('unlock alarm ($X)', act_unlock), ('home ($H)', act_home), ('jog', act_jog),
        ('set X0 Y0 (blank lower-left)', act_zero_xy), ('probe Z0 on copper', act_zero_z),
        ('height map', act_heightmap), ('run a G-code file', act_run)]

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', default='COM18'); ap.add_argument('--check', nargs='*')
    ap.add_argument('--run', help='run this file directly (still asks for GO)')
    a = ap.parse_args()
    g = Grbl(a.port)
    print('connected', a.port, g.status())
    if a.run:
        act_run(g, a.run)
        g.s.close()                                   # free COM18 at once for the next job
        print('   COM18 released - ready for the next file.')
        sys.exit(0)
    if a.check:
        sys.exit(0 if all(act_check(g, p) for p in a.check) else 1)
    while True:
        print('\n'.join(f'  {i + 1}. {n}' for i, (n, _) in enumerate(MENU)) + '\n  q. quit')
        c = ask('choose:')
        if c.lower() == 'q':
            break
        if c.isdigit() and 1 <= int(c) <= len(MENU):
            MENU[int(c) - 1][1](g)
