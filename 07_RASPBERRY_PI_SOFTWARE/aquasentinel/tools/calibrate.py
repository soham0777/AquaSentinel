"""Calibration wizard for every sensor. The service can keep running: the wizard reads the live values from it.

  python3 ~/aquasentinel/tools/calibrate.py          (menu)
  python3 ~/aquasentinel/tools/calibrate.py --show   (print the stored calibration)

  1  pH           buffers 7.0, 4.0 and 9.2 (two are enough)
  2  TDS          a standard solution with a known ppm on the bottle (for example 342 or 707 ppm)
  3  Turbidity    the probe in clean, clear water (sets "clear"; cloudy is judged against it)
  4  MQ-3         clean air after at least 3 minutes switched on (sets the vapour baseline)
  5  Water temp   a kitchen or lab thermometer in the same water (sets an offset)

Each result is saved in config.json with the date, and the running service picks it up at once.
If the service is not running, the wizard reads the Nano directly over USB.
"""
import json
import os
import statistics
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aquasentinel import settings                         # noqa: E402
from aquasentinel.sensors import fit_line, tds_ppm         # noqa: E402


class Source:
    """Live readings: from the running service if it answers, otherwise straight from the Nano."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.url = f"http://127.0.0.1:{cfg.get('web_port', 8080)}"
        self.ser = None
        try:
            urllib.request.urlopen(self.url + "/api/state", timeout=3).read()
            self.mode = "service"
            print("Reading live values from the running AquaSentinel service.")
        except Exception:
            self.mode = "serial"
            import serial
            from aquasentinel.nano import candidate_ports
            for port in candidate_ports(cfg.get("nano_port", "auto")):
                try:
                    self.ser = serial.Serial(port, cfg["nano_baud"], timeout=1)
                    time.sleep(2.2); self.ser.reset_input_buffer()
                    print(f"Service not running: reading the Nano directly on {port}.")
                    break
                except Exception as e:
                    print(f"{port}: {e}")
            if not self.ser:
                sys.exit("No live values: start the service (sudo systemctl start aquasentinel) or plug in the Nano.")

    def one(self):
        if self.mode == "service":
            time.sleep(1)
            s = json.loads(urllib.request.urlopen(self.url + "/api/state", timeout=5).read())
            return s.get("latest") or {}
        from aquasentinel.nano import check_line
        while True:
            m = check_line(self.ser.readline().decode("ascii", errors="replace").strip())
            if m and "vcc" in m:
                return m

    def settle(self, key, seconds=15, fmt="{:.3f}"):
        """Read `key` for `seconds`, show it live, return the median and spread of the settled second half."""
        vals, t0 = [], time.time()
        while time.time() - t0 < seconds:
            v = self.one().get(key)
            if isinstance(v, (int, float)):
                vals.append(float(v)); print("\r   " + fmt.format(v) + "      ", end="", flush=True)
        print()
        if len(vals) < 4:
            print("   Too few readings. Is the sensor plugged in?"); return None, None
        tail = vals[len(vals) // 2:]
        return statistics.median(tail), statistics.pstdev(tail)

    def reload(self):
        if self.mode == "service":
            req = urllib.request.Request(self.url + "/api/cmd", data=json.dumps({"action": "reload_config"}).encode(),
                                         headers={"Content-Type": "application/json"}, method="POST")
            urllib.request.urlopen(req, timeout=5).read()
            print("   The running service now uses it.")
        else:
            print("   Used from the next start of the service.")


def ask(q):
    return input(q).strip().lower()


def cal_ph(src):
    points = []
    for ph in (7.0, 4.0, 9.2):
        if ask(f"\n pH {ph} buffer: rinse the probe, dip it, press Enter (s = skip): ") == "s":
            continue
        print("   reading 15 s, keep the probe still...")
        v, sd = src.settle("ph_v")
        if v is None:
            continue
        print(f"   pH {ph}: {v:.3f} V  (noise {sd * 1000:.1f} mV)")
        if sd > 0.02:
            print("   Still moving. Wait a little longer next time for a better result.")
        points.append((v, ph))
    if len(points) < 2:
        print(" Need at least two buffers. Nothing saved."); return
    a, b = fit_line(points)
    mv = abs(1 / a) * 1000
    print(f"\n Result: pH = {a:.3f} x V + {b:.3f}   ({mv:.0f} mV per pH unit)")
    for v, ph in points:
        print(f"   check: {v:.3f} V -> pH {a * v + b:.2f}  (buffer {ph})")
    if mv < 30:
        print(" WARNING: very small change per pH unit. Check the probe and the board's gain trimmer.")
    if ask(" Save? (y/n): ") == "y":
        settings.save_ph_calibration(points); print("   Saved."); src.reload()


def cal_tds(src, cfg):
    try:
        known = float(ask("\n TDS: ppm written on the standard solution bottle (for example 342 or 707): "))
    except ValueError:
        print(" Not a number."); return
    input(" Put the TDS probe AND the temperature probe in the solution, press Enter...")
    v, _ = src.settle("tds_v")
    t, _ = src.settle("t_water", 4, "{:.1f} degC")
    if not v:
        return
    measured = tds_ppm(v, t, k=1.0)                     # t already has the stored temperature offset applied
    if measured < 1:
        print(" The probe reads almost zero. Is it in the solution?"); return
    k = known / measured
    print(f"\n Reads {measured:.0f} ppm before calibration; factor k = {k:.3f}")
    if not 0.5 < k < 2.0:
        print(" WARNING: k is far from 1. Check the probe, the solution and the TDS board.")
    if ask(" Save? (y/n): ") == "y":
        settings.save_calibration(tds_k=round(k, 4)); print("   Saved."); src.reload()


def cal_turbidity(src):
    input("\n Turbidity: put the probe in clean, clear water (no bubbles on the window), press Enter...")
    v, sd = src.settle("turb_v")
    if not v:
        return
    print(f"\n Clear water: {v:.3f} V. Water counts as cloudy below {v * 0.85:.3f} V (15 % darker).")
    if v < 2.5:
        print(" Note: a clear-water reading under 2.5 V often means a dirty window or the probe out of the water.")
    if ask(" Save? (y/n): ") == "y":
        settings.save_calibration(turbidity_clear_v=round(v, 3)); print("   Saved."); src.reload()


def cal_mq3(src):
    input("\n MQ-3: the model must have been ON for at least 3 minutes, in clean air. Press Enter...")
    v, sd = src.settle("mq3_v", 20)
    if not v:
        return
    print(f"\n Clean air: {v:.3f} V. Vapour is reported above {v + 0.35:.3f} V.")
    if ask(" Save? (y/n): ") == "y":
        settings.save_calibration(mq3_clean_v=round(v, 3)); print("   Saved."); src.reload()


def cal_temp(src, cfg):
    input("\n Water temperature: put the probe and a thermometer in the same water, press Enter...")
    t, _ = src.settle("t_water", 10, "{:.2f} degC")
    if t is None:
        return
    raw = t - (cfg["calibration"].get("t_water_offset") or 0.0)
    try:
        ref = float(ask(" What does the thermometer read (degC)? "))
    except ValueError:
        print(" Not a number."); return
    off = round(ref - raw, 2)
    print(f" Offset {off:+.2f} degC")
    if abs(off) > 3:
        print(" WARNING: more than 3 degC off. Check the probe and the thermometer.")
    if ask(" Save? (y/n): ") == "y":
        settings.save_calibration(t_water_offset=off); print("   Saved."); src.reload()


def show(cfg):
    c, p = cfg["calibration"], cfg["ph_calibration"]
    d = c.get("dates", {})
    print("\n Stored calibration")
    print(f"   pH          {'calibrated ' + p.get('date', '') if p.get('calibrated') else 'NOT calibrated'}  points {p.get('points')}")
    print(f"   TDS k       {c.get('tds_k')}  {d.get('tds_k', '(default)')}")
    print(f"   Turbidity   clear = {c.get('turbidity_clear_v')} V  {d.get('turbidity_clear_v', '(module trimmer used)')}")
    print(f"   MQ-3        clean air = {c.get('mq3_clean_v')} V  {d.get('mq3_clean_v', '(module trimmer used)')}")
    print(f"   Water temp  offset {c.get('t_water_offset')} degC  {d.get('t_water_offset', '(default)')}")


def main():
    cfg = settings.load()
    show(cfg)
    if "--show" in sys.argv:
        return
    src = Source(cfg)
    while True:
        cfg = settings.load()
        ch = ask("\n 1 pH   2 TDS   3 Turbidity   4 MQ-3   5 Water temp   6 Show   q Quit : ")
        if ch == "1": cal_ph(src)
        elif ch == "2": cal_tds(src, cfg)
        elif ch == "3": cal_turbidity(src)
        elif ch == "4": cal_mq3(src)
        elif ch == "5": cal_temp(src, cfg)
        elif ch == "6": show(settings.load())
        elif ch in ("q", ""): break


if __name__ == "__main__":
    main()
