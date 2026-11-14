"""Loads config.json (next to the package) and keeps it in one place."""
import json
import os
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config.json")
_lock = threading.Lock()


def load():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    log_dir = cfg.get("log_dir", "logs")
    if not os.path.isabs(log_dir):
        cfg["log_dir"] = os.path.join(ROOT, log_dir)
    os.makedirs(cfg["log_dir"], exist_ok=True)
    return cfg


def save_ph_calibration(points):
    """Write new pH calibration points into config.json, keeping everything else as it is."""
    with _lock:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        raw["ph_calibration"] = {"calibrated": True, "points": [[round(v, 4), round(p, 2)] for v, p in points]}
        tmp = CONFIG_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(raw, f, indent=2)
        os.replace(tmp, CONFIG_PATH)
