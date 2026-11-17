"""The decision engine: is the water normal, and if not, what kind of event is it?

Same rules as our finale deck:
  - hard limits: pH < 6 or > 9, dissolved solids > 1,400 ppm
  - plus a baseline learned from the water itself (a sudden jump counts even below the limit)
  - an event needs 2 unusual readings out of the last 3 (no false alarm from one bad reading)
  - a broken or missing sensor is reported as SENSOR FAULT, never as "normal"

Classes: NORMAL, ACIDIC, INDUSTRIAL, RUNOFF, SOLVENT, SENSOR FAULT (plus LEARNING at start-up).
"""
import time
from collections import deque

CLASS_INFO = {
    "LEARNING":     ("Learning the water",   "Reading the water to learn what is normal here."),
    "NORMAL":       ("Water normal",         "All readings inside the safe range."),
    "ACIDIC":       ("Acid spill",           "pH has fallen: an acid is in the water."),
    "INDUSTRIAL":   ("Industrial discharge", "Dissolved solids jumped: salts or effluent in the water."),
    "RUNOFF":       ("Muddy runoff",         "The water turned cloudy while salts stayed flat: soil or runoff."),
    "SOLVENT":      ("Solvent or fuel",      "Vapour detected above the sample: a solvent or fuel."),
    "SENSOR FAULT": ("Sensor fault",         "A sensor stopped answering. We never call that 'normal'."),
}


class Brain:
    def __init__(self, cfg):
        self.cfg = cfg
        self.lim = cfg["limits"]
        self.started = time.time()
        self.baseline = {"ph": None, "tds": None}
        self._learn = {"ph": [], "tds": []}
        self.window = deque(maxlen=cfg.get("confirm_window", 3))
        self.state = "LEARNING"
        self.state_since = time.time()
        self.normal_streak = 0
        self.last_reasons = []

    def relearn(self):
        self.started = time.time()
        self.baseline = {"ph": None, "tds": None}
        self._learn = {"ph": [], "tds": []}
        self.window.clear()
        self._set("LEARNING")

    def _set(self, state):
        if state != self.state:
            self.state = state
            self.state_since = time.time()

    # ---------- per-reading checks ----------
    def faults(self, r):
        f = []
        if r["t_water"] is None:
            f.append("water temperature probe not answering")
        if r["ph_v"] is None or r["ph_v"] < 0.05 or r["ph_v"] > 4.9:
            f.append("pH probe signal out of range")
        if r["tds_v"] is not None and r["tds_v"] < 0.02 and (self.baseline["tds"] or 0) > 50:
            f.append("TDS probe reads zero (out of the water or unplugged)")
        if r["t_air"] is None:
            f.append("air sensor (DHT11) not answering")
        return f

    def classify(self, r):
        """Return (class, reasons) for one reading, ignoring confirmation."""
        reasons = []
        f = self.faults(r)
        if f:
            return "SENSOR FAULT", f
        lim, base = self.cfg["limits"], self.baseline           # read each time: calibration can be reloaded live
        ph, tds = r["ph"], r["tds"]
        acid = industrial = False
        # Absolute pH limits only count once the probe is calibrated; before that only a sudden change counts.
        absolute = self.cfg["ph_calibration"].get("calibrated", False)
        if ph is not None:
            if absolute and ph < lim["ph_low"]:
                acid = True; reasons.append(f"pH {ph:.1f} below {lim['ph_low']}")
            elif base["ph"] is not None and base["ph"] - ph > lim["ph_drop_from_baseline"]:
                acid = True; reasons.append(f"pH fell {base['ph'] - ph:.1f} from normal")
            if absolute and ph > lim["ph_high"]:
                industrial = True; reasons.append(f"pH {ph:.1f} above {lim['ph_high']}")
            elif base["ph"] is not None and ph - base["ph"] > lim["ph_rise_from_baseline"]:
                industrial = True; reasons.append(f"pH rose {ph - base['ph']:.1f} from normal")
        if tds is not None:
            if tds > lim["tds_high_ppm"]:
                industrial = True; reasons.append(f"dissolved solids {tds:.0f} ppm above {lim['tds_high_ppm']}")
            elif base["tds"] and tds > base["tds"] * lim["tds_jump_ratio"] and tds - base["tds"] > lim["tds_jump_min_ppm"]:
                industrial = True; reasons.append(f"dissolved solids jumped {base['tds']:.0f} -> {tds:.0f} ppm")
        if r["t_water"] is not None and r["t_water"] > lim["water_temp_high_c"]:
            industrial = True; reasons.append(f"hot discharge {r['t_water']:.1f} degC")
        if acid:
            return "ACIDIC", reasons
        if industrial:
            return "INDUSTRIAL", reasons
        if r["turbid"]:
            return "RUNOFF", ["water turned cloudy, salts flat"]
        warmup_s = self.cfg.get("mq3_warmup_s", 0)
        up = r.get("nano_uptime")                     # seconds since the Nano (and the MQ-3 heater) powered up
        warmed = up is None or up >= warmup_s
        if r["vapour"] and warmed:
            return "SOLVENT", ["vapour detected above the sample"]
        return "NORMAL", []

    # ---------- main step ----------
    def step(self, r):
        """Feed one reading. Returns (state, changed, reasons)."""
        prev = self.state
        cls, reasons = self.classify(r)
        learning = time.time() - self.started < self.cfg.get("learn_seconds", 20)

        if cls == "NORMAL" or (learning and cls != "SENSOR FAULT"):
            for k in ("ph", "tds"):
                if r[k] is not None:
                    if learning:
                        self._learn[k].append(r[k])
                        vals = sorted(self._learn[k])
                        self.baseline[k] = vals[len(vals) // 2]          # median while learning
                    elif self.baseline[k] is not None:
                        self.baseline[k] = 0.97 * self.baseline[k] + 0.03 * r[k]  # slow drift
        if learning and cls != "SENSOR FAULT":
            self._set("LEARNING")
            self.last_reasons = []
            return self.state, self.state != prev, []

        self.window.append(cls)
        need = self.cfg.get("confirm_needed", 2)
        counts = {}
        for c in self.window:
            if c != "NORMAL":
                counts[c] = counts.get(c, 0) + 1
        confirmed = max(counts, key=counts.get) if counts and max(counts.values()) >= need else None

        if confirmed:
            self.normal_streak = 0
            self._set(confirmed)
            self.last_reasons = reasons if cls == confirmed else self.last_reasons
        elif cls == "NORMAL":
            self.normal_streak += 1
            if self.state in ("LEARNING",) or self.normal_streak >= self.cfg.get("clear_after_normal", 4):
                self._set("NORMAL")
                self.last_reasons = []
        return self.state, self.state != prev, self.last_reasons
