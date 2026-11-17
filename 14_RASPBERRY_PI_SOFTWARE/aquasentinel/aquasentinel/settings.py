"""Loads config.json (next to the package) and keeps it in one place.

Every setting has a default here, so an older config.json keeps working after an update: missing keys are filled in.
"""
import copy
import json
import os
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config.json")
SECRETS_PATH = os.path.join(ROOT, "secrets.json")
_lock = threading.Lock()

DEFAULTS = {
    "site_name": "AquaSentinel station",
    "team": "",
    "nano_port": "auto",
    "nano_baud": 115200,
    "sim_enabled": True,
    "sim_port": "/dev/serial0",
    "sim_baud": 9600,
    "sms_numbers": [],
    "sms_cooldown_minutes": 10,
    "web_port": 8080,
    "auto_sample": True,
    "sample_pump_seconds": 5,
    "learn_seconds": 20,
    "confirm_window": 3,
    "confirm_needed": 2,
    "clear_after_normal": 4,
    "limits": {"ph_low": 6.0, "ph_high": 9.0, "ph_drop_from_baseline": 1.0, "ph_rise_from_baseline": 1.0,
               "tds_high_ppm": 1400, "tds_jump_ratio": 1.5, "tds_jump_min_ppm": 150, "water_temp_high_c": 40.0},
    "digital_outputs": {"turbidity_dirty_value": 0, "mq3_vapour_value": 0, "ldr_dark_value": 1},
    "ph_calibration": {"calibrated": False, "points": [[2.082, 4.0], [2.279, 9.2]]},
    # set by tools/calibrate.py; None = not calibrated (the module's digital output is used instead)
    "calibration": {"tds_k": 1.0, "t_water_offset": 0.0, "turbidity_clear_v": None, "turbidity_drop_ratio": 0.15,
                    "mq3_clean_v": None, "mq3_rise_v": 0.35, "dates": {}},
    # how long a missing reading is bridged with the last good one before it counts as a fault (seconds)
    "hold_seconds": {"t_water": 10, "t_air": 20, "rh": 20},
    "median_of": 3,                      # median filter on the analog channels (kills single spikes)
    "log_dir": "logs",
    "mq3_warmup_s": 90,
    "cloud": {"enabled": False, "station_id": "kopargaon-1to5", "live_every_s": 5, "reading_every_s": 60,
              "max_queue": 50000},
}


def _merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def load():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = _merge(DEFAULTS, json.load(f))
    log_dir = cfg.get("log_dir", "logs")
    if not os.path.isabs(log_dir):
        cfg["log_dir"] = os.path.join(ROOT, log_dir)
    os.makedirs(cfg["log_dir"], exist_ok=True)
    # Phone numbers are personal data: they live in secrets.json (never in git). config.json can still hold them.
    sec = load_secrets() or {}
    nums = [n for n in sec.get("sms_numbers", []) if isinstance(n, str) and n.strip().startswith("+")]
    if nums:
        cfg["sms_numbers"] = nums
    return cfg


def load_secrets():
    """secrets.json (never shared, never in git): Firebase web API key, database URL, device e-mail and password."""
    if not os.path.exists(SECRETS_PATH):
        return None
    with open(SECRETS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _write(raw):
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2)
    os.replace(tmp, CONFIG_PATH)


def save_section(name, value):
    """Replace or merge one top-level section of config.json, keeping everything else as it is."""
    with _lock:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(value, dict) and isinstance(raw.get(name), dict):
            raw[name] = _merge(raw[name], value)
        else:
            raw[name] = value
        _write(raw)


def save_ph_calibration(points):
    """Write new pH calibration points into config.json."""
    save_section("ph_calibration", {"calibrated": True, "points": [[round(v, 4), round(p, 2)] for v, p in points],
                                    "date": time.strftime("%Y-%m-%d %H:%M")})


def save_calibration(**values):
    """Save calibration values (tds_k, t_water_offset, turbidity_clear_v, mq3_clean_v) with today's date."""
    dates = {k: time.strftime("%Y-%m-%d %H:%M") for k in values}
    save_section("calibration", {**values, "dates": dates})
