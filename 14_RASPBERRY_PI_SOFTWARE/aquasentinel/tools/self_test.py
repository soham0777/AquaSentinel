"""Checks the decision engine against the six booth waters, without hardware.
Run:  python3 tools/self_test.py      (prints PASS/FAIL for each case)"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aquasentinel import settings              # noqa: E402
from aquasentinel.brain import Brain           # noqa: E402
from aquasentinel.sensors import derive        # noqa: E402

CLEAN = {"vcc": 4.75, "ph_v": 2.16, "tds_v": 0.62, "turb_v": 1.8, "mq3_v": 1.6, "ldr_do": 0, "ph_do": 0,
         "turb_do": 1, "mq3_do": 1, "t_water": 26.0, "t_air": 28.4, "rh": 40, "pump": 0, "up": 1}
CASES = [("clean tap water", {}, "NORMAL"),
         ("salty water", {"tds_v": 1.9}, "INDUSTRIAL"),
         ("vinegar", {"ph_v": 1.98}, "ACIDIC"),
         ("muddy water", {"turb_do": 0, "turb_v": 1.2}, "RUNOFF"),
         ("sanitiser at the bottle", {"mq3_do": 0, "mq3_v": 2.6, "up": 200}, "SOLVENT"),
         ("MQ-3 still warming up (5 s)", {"mq3_do": 0, "mq3_v": 2.6, "up": 5}, "NORMAL"),
         ("temperature probe unplugged", {"t_water": None}, "SENSOR FAULT")]


def run():
    cfg = settings.load()
    ok = True
    for name, change, want in CASES:
        b = Brain(cfg)
        b.started = time.time() - 999               # skip the learning period...
        b.baseline = {"ph": None, "tds": None}
        for _ in range(5):                          # ...but learn the clean water first
            b.started = time.time()
            b.step(derive(CLEAN, cfg))
        b.started = time.time() - 999
        for _ in range(5):
            b.step(derive(CLEAN, cfg))
        state = None
        for _ in range(4):
            state, _, reasons = b.step(derive({**CLEAN, **change}, cfg))
        good = state == want
        ok &= good
        print(f"{'PASS' if good else 'FAIL'}  {name:30s} -> {state:13s} {'; '.join(reasons)}")
    print("\nALL PASS" if ok else "\nSOME FAILED")
    return ok


if __name__ == "__main__":
    good = run()
    print()
    print("--- reliability (drop-outs, damaged lines, calibration, cloud) ---")
    import test_reliability
    good = test_reliability.run() and good
    sys.exit(0 if good else 1)
