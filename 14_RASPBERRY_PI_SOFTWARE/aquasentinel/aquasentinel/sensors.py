"""Turns the Nano's raw line into clean readings in real units.

Nano line (firmware v2), one per second:
  {"vcc":4.75,"ph_v":2.15,"ph":5.8,"tds_v":0.64,"turb_v":1.79,"mq3_v":1.64,"ldr_do":0,"ph_do":0,"turb_do":1,
   "mq3_do":1,"t_water":27.1,"t_air":28.4,"rh":17,"pump":0,"up":18,"seq":18,"led":"G","e_dht":0,"e_ds":0,"fw":2,"ck":93}

Two layers:
  Conditioner  makes the signal steady: a median of the last 3 analog readings removes single spikes, and a missing
               temperature or humidity value is bridged with the last good one for a few seconds (hold_seconds).
               Only a value that stays missing becomes None, and only then can the brain call a SENSOR FAULT.
  derive()     turns volts into pH, ppm, cloudy/clear and vapour yes/no, using the stored calibration.
"""
import time
from collections import deque


def fit_line(points):
    """Least-squares line pH = a*V + b through the calibration points (2 or 3 points)."""
    n = len(points)
    if n < 2:
        return None
    sx = sum(v for v, _ in points); sy = sum(p for _, p in points)
    sxx = sum(v * v for v, _ in points); sxy = sum(v * p for v, p in points)
    den = n * sxx - sx * sx
    if abs(den) < 1e-12:
        return None
    a = (n * sxy - sx * sy) / den
    b = (sy - a * sx) / n
    return a, b


def ph_from_voltage(v, cal):
    if v is None:
        return None
    line = fit_line(cal.get("points", []))
    if not line:
        return None
    a, b = line
    return max(0.0, min(14.0, a * v + b))


def tds_ppm(v, water_temp_c, k=1.0):
    """DFRobot SEN0244 formula, temperature-compensated to 25 degC, times the calibration factor k."""
    if v is None:
        return None
    t = 25.0 if water_temp_c is None else water_temp_c
    cv = v / (1.0 + 0.02 * (t - 25.0))
    ppm = (133.42 * cv ** 3 - 255.86 * cv ** 2 + 857.39 * cv) * 0.5 * k
    return max(0.0, ppm)


ANALOG = ("vcc", "ph_v", "tds_v", "turb_v", "mq3_v")
HELD = ("t_water", "t_air", "rh")


class Conditioner:
    """Per-channel smoothing and short dropout bridging. One instance per station."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.buf = {k: deque(maxlen=max(1, int(cfg.get("median_of", 3)))) for k in ANALOG}
        self.last_good = {k: (None, 0.0) for k in HELD}
        self.missing = {k: 0 for k in HELD}          # consecutive missing readings (for the dashboard)

    def reset(self):
        for d in self.buf.values():
            d.clear()

    def clean(self, raw, now=None):
        now = time.time() if now is None else now
        out = dict(raw)
        for k in ANALOG:
            v = raw.get(k)
            if isinstance(v, (int, float)):
                self.buf[k].append(float(v))
            if self.buf[k]:
                s = sorted(self.buf[k])
                out[k] = s[len(s) // 2]
            else:
                out[k] = None
        hold = self.cfg.get("hold_seconds", {})
        held = []
        for k in HELD:
            v = raw.get(k)
            if isinstance(v, (int, float)):
                self.last_good[k] = (float(v), now)
                self.missing[k] = 0
            else:
                self.missing[k] += 1
                lv, lt = self.last_good[k]
                if lv is not None and now - lt <= hold.get(k, 0):
                    out[k] = lv
                    held.append(k)
                else:
                    out[k] = None
        out["_held"] = held
        return out


def derive(raw, cfg):
    """Return a clean reading dict with units and flags. Missing values stay None."""
    do = cfg["digital_outputs"]
    cal = cfg.get("calibration", {})
    t_water = raw.get("t_water")
    if t_water is not None:
        t_water = round(t_water + (cal.get("t_water_offset") or 0.0), 2)
    ph_v = raw.get("ph_v")
    tds_v = raw.get("tds_v")
    turb_v = raw.get("turb_v")
    mq3_v = raw.get("mq3_v")

    # Turbidity: with a stored clear-water voltage the analog value decides (the voltage falls as the water clouds);
    # without it, the module's digital output (its blue trimmer) decides.
    clear_v = cal.get("turbidity_clear_v")
    if clear_v and turb_v is not None:
        turbid = turb_v < clear_v * (1.0 - cal.get("turbidity_drop_ratio", 0.15))
        turb_pct = max(0.0, min(100.0, (1.0 - turb_v / clear_v) * 100.0))   # % darker than clear water
    else:
        turbid = raw.get("turb_do") == do["turbidity_dirty_value"] if raw.get("turb_do") is not None else None
        turb_pct = None
    clean_v = cal.get("mq3_clean_v")
    if clean_v and mq3_v is not None:
        vapour = mq3_v > clean_v + cal.get("mq3_rise_v", 0.35)
    else:
        vapour = raw.get("mq3_do") == do["mq3_vapour_value"] if raw.get("mq3_do") is not None else None

    r = {
        "vcc": raw.get("vcc"),
        "ph_v": ph_v,
        "ph": ph_from_voltage(ph_v, cfg["ph_calibration"]),
        "tds_v": tds_v,
        "tds": tds_ppm(tds_v, t_water, cal.get("tds_k") or 1.0),
        "turb_v": turb_v,
        "turbid": turbid,
        "turb_pct": None if turb_pct is None else round(turb_pct),
        "mq3_v": mq3_v,
        "vapour": vapour,
        "dark": raw.get("ldr_do") == do["ldr_dark_value"] if raw.get("ldr_do") is not None else None,
        "t_water": t_water,
        "t_air": raw.get("t_air"),
        "rh": raw.get("rh"),
        "pump": bool(raw.get("pump")),
        "nano_uptime": raw.get("up"),
        "held": raw.get("_held", []),
    }
    for k in ("ph", "tds"):
        if r[k] is not None:
            r[k] = round(r[k], 2 if k == "ph" else 0)
    return r
