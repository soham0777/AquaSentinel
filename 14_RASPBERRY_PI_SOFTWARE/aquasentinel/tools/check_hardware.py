"""Checks every part of the hardware in about 30 seconds and prints a clear report.

  sudo systemctl stop aquasentinel
  python3 tools/check_hardware.py
  sudo systemctl start aquasentinel
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import serial                                   # noqa: E402
from aquasentinel import settings              # noqa: E402
from aquasentinel.nano import candidate_ports  # noqa: E402

OK, BAD, WARN = "\033[32mOK  \033[0m", "\033[31mFAIL\033[0m", "\033[33mCHECK\033[0m"


def nano_check(cfg):
    print("\n--- Sensor hub (Arduino Nano) ---")
    ports = candidate_ports(cfg.get("nano_port", "auto"))
    if not ports:
        print(BAD, "no USB serial port found. Plug the Nano's USB cable into the Pi."); return None
    s = serial.Serial(ports[0], cfg["nano_baud"], timeout=1)
    time.sleep(2.2); s.reset_input_buffer()
    rows, t0 = [], time.time()
    while time.time() - t0 < 10:
        try:
            j = json.loads(s.readline().decode(errors="replace"))
            if "vcc" in j:
                rows.append(j)
        except ValueError:
            pass
    print(OK if rows else BAD, f"{ports[0]}: {len(rows)} readings in 10 s")
    if not rows:
        return None
    last = rows[-1]
    def rng(k):
        v = [r[k] for r in rows if isinstance(r.get(k), (int, float))]
        return (min(v), max(v)) if v else None
    checks = [
        ("Supply (vcc)", "vcc", lambda a, b: 4.5 <= a and b <= 5.3, "V"),
        ("pH board", "ph_v", lambda a, b: 0.2 < a and b < 4.8, "V"),
        ("TDS", "tds_v", lambda a, b: b < 4.8, "V  (near 0 = probe in air)"),
        ("Turbidity", "turb_v", lambda a, b: b < 4.9, "V"),
        ("MQ-3", "mq3_v", lambda a, b: 0.1 < a and b < 4.9, "V"),
        ("Water temp DS18B20", "t_water", lambda a, b: -5 < a and b < 60, "degC"),
        ("Air temp DHT11", "t_air", lambda a, b: -5 < a and b < 60, "degC"),
        ("Humidity DHT11", "rh", lambda a, b: 0 <= a and b <= 100, "%"),
    ]
    for name, k, good, unit in checks:
        r = rng(k)
        if r is None:
            print(BAD, f"{name:20s} no value (unplugged?)")
        else:
            print(OK if good(*r) else WARN, f"{name:20s} {r[0]} .. {r[1]} {unit}")
    print(OK, f"Digital outputs: LDR {last['ldr_do']}, turbidity {last['turb_do']}, MQ-3 {last['mq3_do']}")
    print("\nBeacon: watch it go RED, GREEN, BLUE, then back to GREEN")
    for c in "RGBG":
        s.write(f"LED {c}\n".encode()); time.sleep(1.5)
    if input("Pump: run it for 2 s? Its end must be in water (y/n): ").strip().lower() == "y":
        s.write(b"PUMP 2\n"); time.sleep(3)
    s.close()
    return True


def sim_check(cfg):
    print("\n--- SIM800L (SMS) ---")
    try:
        m = serial.Serial(cfg["sim_port"], cfg.get("sim_baud", 9600), timeout=1)
    except Exception as e:
        print(BAD, f"cannot open {cfg['sim_port']}: {e}. Run install.sh and reboot."); return
    def at(c, w=1.5):
        m.reset_input_buffer(); m.write((c + "\r").encode()); time.sleep(w); return m.read(m.in_waiting or 1).decode(errors="replace")
    r = at("AT")
    if "OK" not in r:
        print(BAD, "no answer. Check: SIM800L power (4.0 V on J17), TX/RX wires on J18, antenna."); return
    print(OK, "SIM800L answers")
    print(OK if "READY" in at("AT+CPIN?") else BAD, "SIM card")
    q = at("AT+CSQ")
    try:
        v = int(q.split("+CSQ:")[1].split(",")[0]); print(OK if 8 <= v < 99 else WARN, f"signal {v}/31 (10+ is good)")
    except Exception:
        print(WARN, "signal unknown")
    reg = at("AT+CREG?")
    print(OK if (",1" in reg or ",5" in reg) else WARN, "network registration", "(registered)" if (",1" in reg or ",5" in reg) else "(still searching: wait 30 s and retry)")
    m.close()


if __name__ == "__main__":
    cfg = settings.load()
    nano_check(cfg)
    if cfg.get("sim_enabled", True):
        sim_check(cfg)
    print("\nDone. Start the service again:  sudo systemctl start aquasentinel")
