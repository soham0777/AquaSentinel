#!/usr/bin/env python3
"""Replay the synthetic dataset through BOTH decision engines and compare their decisions.

  * C++  : firmware/edge_node/src/anomaly_engine.cpp, compiled for the host with the shims in ./shim
  * Python: analytics/detector.py

Read-only: nothing in the repository is modified (the compiled harness goes to a temporary folder).
Usage: python tools/parity/compare.py [repo_root]
Exit code 0 = identical decisions on every row, 1 = mismatch, 2 = no C++ compiler found.
Needs a C++17 compiler: g++, clang++, c++, or `python -m ziglang c++` (pip install ziglang).
"""
import csv
import os
import shutil
import subprocess
import sys
import tempfile

root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
here = os.path.join(root, "tools", "parity")
fw = os.path.join(root, "firmware", "edge_node")
csv_path = os.path.join(root, "analytics", "dataset", "synthetic_river_timeseries.csv")

cxx = None
for c in (["g++"], ["clang++"], ["c++"], [sys.executable, "-m", "ziglang", "c++"]):
    try:
        subprocess.run(c + ["--version"], capture_output=True, check=True)
        cxx = c
        break
    except Exception:
        continue
if cxx is None:
    print("PARITY: SKIPPED (no C++ compiler found)")
    sys.exit(2)

tmp = tempfile.mkdtemp(prefix="aqs_parity_")
exe = os.path.join(tmp, "harness")
cmd = cxx + ["-std=c++17", "-O1", "-I" + os.path.join(here, "shim"), "-I" + os.path.join(fw, "include"),
             os.path.join(here, "harness.cpp"), os.path.join(fw, "src", "anomaly_engine.cpp"), "-o", exe]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("PARITY: FAIL (C++ did not compile)\n" + r.stderr[:2000])
    sys.exit(1)
cpp = [l.split() for l in subprocess.run([exe, csv_path], capture_output=True, text=True, check=True).stdout.splitlines()]

sys.path.insert(0, os.path.join(root, "analytics"))
from detector import DualTrackEventDetector  # noqa: E402

lv = {"NORMAL": 0, "WATCH": 1, "EVENT": 2}
det = DualTrackEventDetector()
rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
mism = 0
py_samples = py_events = 0
for i, row in enumerate(rows):
    hour = int(row["timestamp"].split("T")[1][:2])
    o = det.evaluate(float(row["ph"]), float(row["ec_us_cm"]), float(row["do_mg_l"]), float(row["turbidity_ntu"]),
                     float(row["temp_c"]), hour, total_cycles=i)
    p = (lv[o["level"]], int(o["sample_trigger"]), int(o["flags"]))
    c = (int(cpp[i][1]), int(cpp[i][2]), int(cpp[i][3]))
    py_samples += p[1]
    py_events += p[0] == 2
    if p != c:
        mism += 1
        if mism <= 5:
            print("  mismatch row", i, "python", p, "c++", c)
shutil.rmtree(tmp, ignore_errors=True)
cpp_samples = sum(int(c[2]) for c in cpp)
cpp_events = sum(1 for c in cpp if int(c[1]) == 2)
print(f"PARITY: rows={len(rows)} decision_mismatches={mism} samples py/c++={py_samples}/{cpp_samples} "
      f"event_rows py/c++={py_events}/{cpp_events}")
print("PARITY: PASS" if mism == 0 and len(cpp) == len(rows) else "PARITY: FAIL")
sys.exit(0 if mism == 0 and len(cpp) == len(rows) else 1)
