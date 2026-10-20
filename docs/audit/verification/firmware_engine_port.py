"""
Line-by-line float32 port of firmware/edge_node/src/anomaly_engine.cpp (AnomalyEngine::evaluate), used to
(1) test the claim that analytics/detector.py is a "bit-for-bit" reference of the firmware, and
(2) replay failure scenarios the firmware can meet in the field. Read-only; nothing in the project changes.

Scenarios
  A  nominal replay of the synthetic dataset (firmware port vs detector.py)
  B  all probes dead: SensorManager returns its hard-coded fallback values (sensor_interface.cpp lines 112-153)
  C  one brown-out reset on day 20: RTC_DATA_ATTR state (baselines, boot_counter) is re-initialised,
     so the 7-day learning period restarts (anomaly_engine.cpp lines 14-26, main.cpp line 28)

Usage:  python docs/audit/verification/firmware_engine_port.py [repo_root]
Requires: numpy
"""
import csv
import importlib.util
import os
import sys

import numpy as np

f32 = np.float32
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ALPHA = f32(1.0) / f32(96.0)


class FirmwareEngine:
    """Mirrors anomaly_engine.cpp; comments give the C++ line numbers."""

    def __init__(self):  # init(), lines 32-48 (cold boot defaults)
        self.ph = [[f32(7.50), f32(0.15)] for _ in range(24)]
        self.do = [[f32(6.50), f32(0.40)] for _ in range(24)]
        self.ec = [f32(450.0), f32(35.0)]
        self.tu = [f32(12.0), f32(3.0)]
        self.hist, self.normal_consec, self.risk = 0, 0, "NORMAL"

    @staticmethod
    def z(val, mu, d, floor):  # computeZScore, lines 50-56
        s = f32(1.4826) * d
        if s < floor:
            s = f32(floor)
        return abs(f32(val) - mu) / s

    def _upd(self, b, x):  # EWMA update as written in lines 122-129 (d uses the *updated* mu)
        x = f32(x)
        b[0] = f32(b[0] + ALPHA * (x - b[0]))
        b[1] = f32(b[1] + ALPHA * (abs(x - b[0]) - b[1]))

    def evaluate(self, ph, ec, do, tu, hour, cycles):
        ph, ec, do, tu = f32(ph), f32(ec), f32(do), f32(tu)
        flags = 0
        tripped = False
        if ph < f32(6.0) or ph > f32(9.0):  # checkHardLimits, lines 58-78: all limits checked, flags OR-ed
            tripped, flags = True, flags | 1
        if do < f32(4.0):
            tripped, flags = True, flags | 4
        if ec > f32(2250.0):
            tripped, flags = True, flags | 2
        if tripped:  # lines 91-98
            self.risk, self.normal_consec = "EVENT", 0
            return dict(level="EVENT", score=99.0, flags=flags, trigger=True)
        zp = self.z(ph, *self.ph[hour], 0.05)
        ze = self.z(ec, *self.ec, 10.0)
        zd = self.z(do, *self.do[hour], 0.20)
        zt = self.z(tu, *self.tu, 2.0)
        max_z, flags = zp, 0  # lines 106-112: max_z starts at z_ph; others only if > 3
        if zp > 3: flags |= 1
        if ze > 3:
            flags |= 2
            max_z = max(max_z, ze)
        if zd > 3:
            flags |= 4
            max_z = max(max_z, zd)
        if zt > 3:
            flags |= 8
            max_z = max(max_z, zt)
        if cycles < 672:  # learning bypass, lines 118-131 (flags are still reported)
            self._upd(self.ph[hour], ph); self._upd(self.ec, ec); self._upd(self.do[hour], do); self._upd(self.tu, tu)
            return dict(level="NORMAL", score=float(max_z), flags=flags, trigger=False)
        self.hist = ((self.hist << 1) | (1 if flags else 0)) & 7  # lines 134-140
        n = bin(self.hist).count("1")
        if n >= 2:
            trig = self.risk != "EVENT"
            self.risk, self.normal_consec = "EVENT", 0
            return dict(level="EVENT", score=float(max_z), flags=flags, trigger=trig)
        if n == 1:
            self.risk, self.normal_consec = "WATCH", 0
            return dict(level="WATCH", score=float(max_z), flags=flags, trigger=False)
        self.normal_consec += 1
        if self.normal_consec >= 4:
            self.risk = "NORMAL"
        if self.risk == "NORMAL":
            self._upd(self.ph[hour], ph); self._upd(self.ec, ec); self._upd(self.do[hour], do); self._upd(self.tu, tu)
        return dict(level=self.risk, score=float(max_z), flags=flags, trigger=False)


def load():
    return list(csv.DictReader(open(os.path.join(ROOT, "analytics", "dataset", "synthetic_river_timeseries.csv"), encoding="utf-8")))


def replay(rows, engine_factory, transform=None, reset_at=None):
    eng, out, boot = engine_factory(), [], 0
    for idx, r in enumerate(rows):
        if reset_at is not None and idx == reset_at:
            eng, boot = engine_factory(), 0  # RTC memory lost: defaults + boot_counter = 0
        vals = [float(r["ph"]), float(r["ec_us_cm"]), float(r["do_mg_l"]), float(r["turbidity_ntu"])]
        if transform:
            vals = transform(idx, vals)
        out.append(eng.evaluate(*vals, int(r["timestamp"][11:13]), boot))
        boot += 1
    return out


def events(rows):
    ev = []
    for i, r in enumerate(rows):
        if r["is_anomaly"] == "1" and (i == 0 or rows[i - 1]["is_anomaly"] == "0"):
            j = i
            while j + 1 < len(rows) and rows[j + 1]["is_anomaly"] == "1":
                j += 1
            ev.append((i, j, r["anomaly_type"]))
    return ev


def summarize(name, rows, out):
    print(f"\n[{name}]")
    for s0, s1, kind in events(rows):
        hit = next((k for k in range(s0, s1 + 5) if out[k]["level"] == "EVENT"), None)
        print(f"  {kind:24s} {'detected at +%d min' % ((hit - s0) * 15) if hit is not None else 'MISSED'}")
    print(f"  EVENT cycles={sum(o['level'] == 'EVENT' for o in out)}  triggers={sum(o['trigger'] for o in out)}")


if __name__ == "__main__":
    rows = load()
    fw = replay(rows, FirmwareEngine)
    spec = importlib.util.spec_from_file_location("detector", os.path.join(ROOT, "analytics", "detector.py"))
    det_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(det_mod)
    det = det_mod.DualTrackEventDetector()
    py = [det.evaluate(float(r["ph"]), float(r["ec_us_cm"]), float(r["do_mg_l"]), float(r["turbidity_ntu"]),
                       float(r["temp_c"]), int(r["timestamp"][11:13]), total_cycles=i) for i, r in enumerate(rows)]
    lvl = sum(a["level"] != b["level"] for a, b in zip(fw, py))
    trg = sum(a["trigger"] != b["sample_trigger"] for a, b in zip(fw, py))
    flg = sum(a["flags"] != b["flags"] for a, b in zip(fw, py))
    scr = sum(abs(a["score"] - b["score"]) > 1e-3 for a, b in zip(fw, py))
    print("[A] firmware port vs analytics/detector.py over 2880 cycles")
    print(f"  level mismatches={lvl}  trigger mismatches={trg}  flags mismatches={flg}  score mismatches(>1e-3)={scr}")
    case = FirmwareEngine().evaluate(5.0, 2400.0, 3.0, 10.0, 12, 700)
    pycase = det_mod.DualTrackEventDetector().evaluate(5.0, 2400.0, 3.0, 10.0, 24.0, 12, 700)
    print(f"  simultaneous pH 5.0 + EC 2400 + DO 3.0 -> firmware flags=0x{case['flags']:02X}, detector.py flags=0x{pycase['flags']:02X}")
    summarize("A firmware port, nominal", rows, fw)
    dead = replay(rows, FirmwareEngine, transform=lambda i, v: [7.42, 380.0, 6.85, 8.2])
    summarize("B all probes dead -> fallback constants (pH 7.42, EC 380, DO 6.85, turb 8.2)", rows, dead)
    reset = replay(rows, FirmwareEngine, reset_at=20 * 96)
    summarize("C brown-out reset at day 20 (learning restarts)", rows, reset)
