"""
Event-level evaluation of the AquaSentinel decision logic on the synthetic dataset (read-only).

analytics/evaluate.py only counts NORMAL/WATCH/EVENT cycles and sample triggers; it never compares the
output with the ground-truth labels. This script replays analytics/detector.py exactly the way
evaluate.py does and then reports, per labelled event: detection latency, how the event was caught
(hard limit vs statistical), sample triggers, and false alarms outside the labelled windows. It also
models the firmware's 60-minute sampler lockout and 4-bottle capacity, and the learning-period
convergence of the hourly baselines.

Usage (from anywhere):  python docs/audit/verification/detector_event_metrics.py [repo_root]
Requires: Python 3 standard library only.
"""
import csv
import importlib.util
import os
import sys
from collections import defaultdict

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "..", ".."))
spec = importlib.util.spec_from_file_location("detector", os.path.join(ROOT, "analytics", "detector.py"))
detector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detector)

rows = list(csv.DictReader(open(os.path.join(ROOT, "analytics", "dataset", "synthetic_river_timeseries.csv"), encoding="utf-8")))
det = detector.DualTrackEventDetector()
out = []
for idx, r in enumerate(rows):  # identical call pattern to analytics/evaluate.py
    hour = int(r["timestamp"].split("T")[1].split(":")[0])
    res = det.evaluate(float(r["ph"]), float(r["ec_us_cm"]), float(r["do_mg_l"]), float(r["turbidity_ntu"]),
                       float(r["temp_c"]), hour, total_cycles=idx)
    out.append(res)

# ground-truth events = contiguous is_anomaly==1 runs
events = []
for i, r in enumerate(rows):
    if r["is_anomaly"] == "1" and (i == 0 or rows[i - 1]["is_anomaly"] == "0"):
        j = i
        while j + 1 < len(rows) and rows[j + 1]["is_anomaly"] == "1":
            j += 1
        events.append((i, j, r["anomaly_type"]))

GRACE = 4  # firmware keeps EVENT until 4 clean cycles; tolerate that tail
in_window = set()
for s0, s1, _ in events:
    in_window.update(range(s0, s1 + GRACE + 1))

print(f"cycles={len(rows)} learning_period_cycles=672 (first 7 days: statistical track disabled)")
print(f"{'event':24s} {'start':>16s} {'first EVENT':>12s} {'latency':>8s} {'caught by':>12s} {'triggers':>8s}")
for s0, s1, kind in events:
    first = next((k for k in range(s0, s1 + GRACE + 1) if out[k]["level"] == "EVENT"), None)
    trig = sum(1 for k in range(s0, s1 + GRACE + 1) if out[k]["sample_trigger"])
    by = out[first]["reason"].split(":")[0] if first is not None else "-"
    lat = f"{(first - s0) * 15} min" if first is not None else "MISSED"
    print(f"{kind:24s} {rows[s0]['timestamp']:>16s} {('step ' + str(first)) if first is not None else '-':>12s} {lat:>8s} {by:>12s} {trig:>8d}")

fp = defaultdict(int)
fp_steps = []
for k, res in enumerate(out):
    if k not in in_window and res["level"] in ("WATCH", "EVENT"):
        fp[res["level"]] += 1
        fp_steps.append(k)
print(f"\nalarms outside labelled windows (+{GRACE} cycle tail): {dict(fp)}  steps={fp_steps[:20]}")
print(f"WATCH cycles total={sum(1 for o in out if o['level'] == 'WATCH')}, EVENT cycles total={sum(1 for o in out if o['level'] == 'EVENT')}")
print(f"sample triggers emitted by detector.py: {sum(o['sample_trigger'] for o in out)} "
      f"(evaluate.py prints this number as 'Physical Forensic Samples Sealed')")

# firmware sampler constraints: 60 min lockout (4 cycles) and 4 bottles
bottles, last = [], -10 ** 9
for k, o in enumerate(out):
    if o["sample_trigger"] and k - last >= 4 and len(bottles) < 4:
        bottles.append(k)
        last = k
print(f"with 60-min lockout + 4-bottle carousel: bottles filled at steps {bottles} "
      f"-> events sampled: {sorted({kind for s0, s1, kind in events for b in bottles if s0 <= b <= s1 + GRACE})}")

# learning-period convergence of the hourly pH / DO bins (alpha = 1/96 per update, 4 updates per bin per day)
true_ph, true_do = defaultdict(list), defaultdict(list)
for r in rows[:672]:
    h = int(r["timestamp"][11:13])
    true_ph[h].append(float(r["ph"]))
    true_do[h].append(float(r["do_mg_l"]))
probe = detector.DualTrackEventDetector()
for idx, r in enumerate(rows[:672]):
    probe.evaluate(float(r["ph"]), float(r["ec_us_cm"]), float(r["do_mg_l"]), float(r["turbidity_ntu"]),
                   float(r["temp_c"]), int(r["timestamp"][11:13]), total_cycles=idx)
print("\nbaseline after the 7-day learning period (bin mu vs the true 7-day mean of that hour):")
for h in (2, 8, 14, 20):
    tp, td = sum(true_ph[h]) / len(true_ph[h]), sum(true_do[h]) / len(true_do[h])
    fr_do = (probe.do_bins[h][0] - 6.5) / (td - 6.5) if abs(td - 6.5) > 1e-6 else float("nan")
    print(f"  hour {h:02d}: DO bin mu={probe.do_bins[h][0]:.2f} (true {td:.2f}, default 6.50 -> {100 * fr_do:.0f}% converged); "
          f"pH bin mu={probe.ph_bins[h][0]:.3f} (true {tp:.3f}); EC mu={probe.ec_baseline[0]:.1f}")
