#!/usr/bin/env python3
"""AquaSentinel 1:5 LIVE model - wiring test for the Arduino Nano design (v3).

The Nano (USB cable to the Pi) must already run aquasentinel_nano.ino. Run on the Pi:
    python3 wiring_test.py            every test, one after the other
    python3 wiring_test.py <test>     one test: nano temp dht ldr led pump ph tds turb mq3 sim
    python3 wiring_test.py watch      live values every second (Ctrl-C to stop)
Voltages are what the Nano measures at its pins (sensor side). Nothing here is calibrated: it only proves the wiring."""
import glob
import json
import sys
import time

try:
    import serial
except ImportError:
    sys.exit('python3-serial missing:  sudo apt install -y python3-serial')

SIM_PORT = '/dev/serial0'
_nano = None


def nano_port():
    ports = glob.glob('/dev/serial/by-id/*') + glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    return ports[0] if ports else None


def nano():
    global _nano
    if _nano is None:
        p = nano_port()
        if not p:
            raise OSError('no Nano found on USB (ls /dev/ttyUSB* /dev/ttyACM*)')
        _nano = serial.Serial(p, 115200, timeout=2)
        time.sleep(2.5)                     # opening the port resets the Nano
        _nano.reset_input_buffer()
    return _nano


def reading(n=2):
    """The latest of n JSON lines from the Nano."""
    s, last = nano(), None
    t0 = time.time()
    while n and time.time() - t0 < 8:
        line = s.readline().decode(errors='replace').strip()
        if line.startswith('{"vcc"'):
            try:
                last = json.loads(line); n -= 1
            except ValueError:
                pass
    if last is None:
        raise OSError('the Nano sends nothing: is aquasentinel_nano.ino uploaded?')
    return last


def send(cmd):
    nano().write((cmd + '\n').encode()); time.sleep(0.2)


def ok(flag, text):
    print(('  PASS  ' if flag else '  FAIL  ') + text)
    return flag


def ask(q):
    return input('        ' + q + ' [y/n] ').strip().lower().startswith('y')


def test_nano():
    print('\n[nano] Arduino Nano on USB')
    try:
        r = reading()
    except OSError as e:
        return ok(False, str(e))
    return ok(4.4 < r['vcc'] < 5.3, f"Nano answers on {nano_port()}, its supply is {r['vcc']:.2f} V (4.5-5.2 V)")


def test_temp():
    print('\n[temp] DS18B20 water temperature (Nano D2, 4.7k pull-up)')
    t = reading(3)['t_water']
    return ok(t is not None and 5 < t < 60, f'{t} deg C. Hold the tip: it rises within 20 s.' if t is not None
              else 'no reading: check R1 4.7k, the yellow wire on J5-3, red to 5 V')


def test_dht():
    print('\n[dht] DHT11 air temperature + humidity (Nano D3)')
    r = reading(3)
    good = r['t_air'] is not None and r['rh'] is not None
    return ok(good, f"air {r['t_air']} deg C, humidity {r['rh']} %. Breathe on it: humidity rises." if good
              else 'no reading: check DATA on J8-3, + on 5 V')


def test_ldr():
    print('\n[ldr] LDR module DO (Nano D8, digital 1/0)')
    a = reading()['ldr_do']
    input(f'        now DO = {a}. Cover the LDR completely, then press Enter ')
    b = reading()['ldr_do']
    print(f'        covered DO = {b}')
    return ok(a != b, 'DO flips between light and dark (if not, turn the blue trimmer on the module)')


def test_led():
    print('\n[led] RGB beacon (R D6, G D5, B D9): GREEN, RED, BLUE, YELLOW, then FAULT (red blinking)')
    for c, name in (('G', 'green'), ('R', 'red'), ('B', 'blue'), ('Y', 'yellow'), ('F', 'fault blink')):
        print('        ' + name); send('LED ' + c); time.sleep(2)
    send('LED O')
    return ok(ask('Did you see green, red, blue, yellow, then red blinking?'), 'beacon colours')


def test_pump():
    print('\n[pump] Pump via mini L298N (Nano D7). Pump IN WATER, AUX charger ON')
    send('PUMP 2'); time.sleep(3)
    return ok(ask('Did the pump run about 2 seconds and stop?'), 'pump on/off')


def analog(key, label, lo, hi, hint):
    print(f'\n[{key}] {label}')
    v = reading(2)[key + '_v']
    return ok(lo <= v <= hi, f'{v:.3f} V (expected {lo}-{hi} V). {hint}')


def digital(key, label, how):
    print(f'\n[{key}] {label}')
    a = reading()[key + '_do']
    input(f'        now Do = {a}. {how}, then press Enter ')
    b = reading()[key + '_do']
    print(f'        after: Do = {b}')
    return ok(a != b, 'digital output flips (if not, turn the module trimmer that sets the limit)')


def test_ph():
    return digital('ph', 'pH board Do (Nano D10)', 'Turn the limit trimmer (the one farther from the BNC) until the Do LED changes')


def test_tds():
    return analog('tds', 'TDS (Nano A1, board powered from D4). Probe in tap water', 0.05, 2.3, 'Add salt: it rises. Dry probe: about 0.')


def test_turb():
    return digital('turb', 'Turbidity DO (Nano D11). Probe in clear water', 'Block the probe slot with paper')


def test_mq3():
    return digital('mq3', 'MQ-3 DO (Nano D12). Warmed up 3 min', 'Hold hand sanitizer near the sensor for 10 s')


def test_sim():
    print('\n[sim] SIM800L on the Pi serial port (pins 8/10). AUX charger ON, wait 10 s after power')
    try:
        s = serial.Serial(SIM_PORT, 9600, timeout=1)
    except OSError as e:
        return ok(False, f'cannot open {SIM_PORT} ({e}). Serial enabled and its console off (step C1)?')

    def at(c):
        s.reset_input_buffer(); s.write((c + '\r\n').encode()); time.sleep(1)
        return s.read(s.in_waiting or 1).decode(errors='replace').strip().replace('\r\n', ' | ')

    r = at('AT')
    good = ok('OK' in r, f'AT -> {r or "(nothing)"}')
    if good:
        print('        AT+CPIN? ->', at('AT+CPIN?'), '  (READY = SIM found)')
        print('        AT+CSQ   ->', at('AT+CSQ'), '  (first number 10-31 good, 99 = no signal)')
        print('        AT+CREG? ->', at('AT+CREG?'), '  (,1 or ,5 = on the network)')
    s.close()
    return good


TESTS = {'nano': test_nano, 'temp': test_temp, 'dht': test_dht, 'ldr': test_ldr, 'led': test_led, 'pump': test_pump,
         'ph': test_ph, 'tds': test_tds, 'turb': test_turb, 'mq3': test_mq3, 'sim': test_sim}

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if cmd == 'watch':
        print('vcc  | pH V  | TDS V | turb V | MQ-3 V | LDR DO | water C | air C | RH %   (Ctrl-C to stop)')
        while True:
            r = reading(1)
            print(f"{r['vcc']:.2f} | {r['ph_v']:.3f} | {r['tds_v']:.3f} | {r['turb_v']:.3f}  | {r['mq3_v']:.3f}  | "
                  f"{r['ldr_do']}      | {r['t_water']}   | {r['t_air']}  | {r['rh']}")
    elif cmd in TESTS or cmd == 'all':
        names = list(TESTS) if cmd == 'all' else [cmd]
        res = {}
        for n in names:
            try:
                res[n] = TESTS[n]()
            except OSError as e:
                res[n] = ok(False, str(e))
        print('\nRESULT: ' + '  '.join(f'{n}:{"PASS" if r else "FAIL"}' for n, r in res.items()))
        if all(res.values()):
            print('ALL PASS - write it in the diary and photograph the hub.')
    else:
        print(__doc__)
