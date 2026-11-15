"""Turns the Nano's raw line into real units.

Nano line (firmware aquasentinel_nano.ino, BOARD_PCB 1), one per second:
  {"vcc":4.75,"ph_v":2.15,"ph":5.8,"tds_v":0.64,"turb_v":1.79,"mq3_v":1.64,
   "ldr_do":0,"ph_do":0,"turb_do":1,"mq3_do":1,"t_water":27.1,"t_air":28.4,"rh":17,"pump":0,"up":18}
"""


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


def tds_ppm(v, water_temp_c):
    """DFRobot SEN0244 formula, temperature-compensated to 25 degC."""
    if v is None:
        return None
    t = 25.0 if water_temp_c is None else water_temp_c
    cv = v / (1.0 + 0.02 * (t - 25.0))
    ppm = (133.42 * cv ** 3 - 255.86 * cv ** 2 + 857.39 * cv) * 0.5
    return max(0.0, ppm)


def derive(raw, cfg):
    """Return a clean reading dict with units and flags. Missing values stay None."""
    do = cfg["digital_outputs"]
    t_water = raw.get("t_water")
    ph_v = raw.get("ph_v")
    tds_v = raw.get("tds_v")
    r = {
        "vcc": raw.get("vcc"),
        "ph_v": ph_v,
        "ph": ph_from_voltage(ph_v, cfg["ph_calibration"]),
        "tds_v": tds_v,
        "tds": tds_ppm(tds_v, t_water),
        "turb_v": raw.get("turb_v"),
        "turbid": raw.get("turb_do") == do["turbidity_dirty_value"] if raw.get("turb_do") is not None else None,
        "mq3_v": raw.get("mq3_v"),
        "vapour": raw.get("mq3_do") == do["mq3_vapour_value"] if raw.get("mq3_do") is not None else None,
        "dark": raw.get("ldr_do") == do["ldr_dark_value"] if raw.get("ldr_do") is not None else None,
        "t_water": t_water,
        "t_air": raw.get("t_air"),
        "rh": raw.get("rh"),
        "pump": bool(raw.get("pump")),
        "nano_uptime": raw.get("up"),
    }
    for k in ("ph", "tds"):
        if r[k] is not None:
            r[k] = round(r[k], 2 if k == "ph" else 0)
    return r
