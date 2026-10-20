"""
Data-integrity checks on the committed CSV/JSON artifacts (read-only).

  1  hardware/AquaSentinel_Cost_Estimate_BOM.csv: unquoted commas break the CSV, and the line items do not
     add up to the stated TOTAL row
  2  hardware/power_budget.csv: arithmetic of each line, and whether the beacon appears at all
  3  analytics/dataset: columns/dates/events actually in the CSV vs what dataset/README.md describes
  4  mechanical/cad/BOM_R3.csv vs checks/design_checks.json mass table
  5  file paths referenced by the docs that do not exist in the repository

Usage:  python docs/audit/verification/data_integrity_checks.py [repo_root]
"""
import csv
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)

print("== 1 cost estimate ==")
NUM, QTY = re.compile(r"^-?\d+(\.\d+)?$"), re.compile(r"^\d+( Set)?$")
items, total, malformed = [], None, []
lines = open(P("hardware", "AquaSentinel_Cost_Estimate_BOM.csv"), encoding="utf-8").read().splitlines()
ncol = len(lines[0].split(","))
for ln in lines[1:]:
    raw = next(csv.reader([ln]))
    if len(raw) != ncol:
        malformed.append(raw[0])
    i = next(k for k in range(4, len(raw) - 3) if QTY.match(raw[k]) and all(NUM.match(raw[k + j]) for j in (1, 2, 3)))
    rec = dict(item=raw[0], qty=raw[i], inr=float(raw[i + 1]), usd=float(raw[i + 2]), s100=float(raw[i + 3]))
    if raw[0] == "TOTAL":
        total = rec
    else:
        items.append(rec)
inr = sum(r["inr"] for r in items)
print(f"rows with unquoted commas (break any CSV reader): {malformed}")
print(f"line items sum INR {inr:.0f} vs TOTAL row {total['inr']:.0f}; USD {sum(r['usd'] for r in items):.2f} vs {total['usd']}; "
      f"scale-100 USD {sum(r['s100'] for r in items):.2f} vs {total['s100']}")
print(f"if Prototype_Cost_INR were unit prices: {sum(r['inr'] * float(r['qty'].split()[0]) for r in items):.0f}")
print(f"probes (E-01..E-04) {sum(r['inr'] for r in items if r['item'].startswith('E-')):.0f} INR")

print("\n== 2 power budget ==")
pb = list(csv.DictReader(open(P("hardware", "power_budget.csv"), encoding="utf-8")))
loads = [r for r in pb if r["Subsystem"] not in ("TOTAL_NOMINAL", "DESIGN_TARGET_MARGIN", "BATTERY_CAPACITY",
                                                   "DARK_AUTONOMY_DAYS", "PV_MONSOON_GENERATION",
                                                   "PV_ANNUAL_GENERATION", "CRISIS_MODE_EXTRA")]
print(f"sum of load lines = {sum(float(r['Daily_Energy_Wh']) for r in loads):.3f} Wh/day (stated 3.390)")
print(f"beacon / Jal-Deep line present: {any('eacon' in (r['Subsystem'] + r['Engineering_Notes']) for r in pb)}")
print("note: docs/engineering/robotics_subsystems_spec.md budgets the beacon at 0.600 Wh/day and an 8 mA baseline;"
      " power_budget.csv uses a 0.60 mA floor and no beacon - both total ~3.4 Wh/day")

print("\n== 3 dataset vs dataset/README.md ==")
rows = list(csv.DictReader(open(P("analytics", "dataset", "synthetic_river_timeseries.csv"), encoding="utf-8")))
readme = open(P("analytics", "dataset", "README.md"), encoding="utf-8").read()
cols = list(rows[0].keys())
doc_cols = re.findall(r"^\| `([a-z_]+)`", readme, flags=re.M)
print(f"CSV columns ({len(cols)}): {cols}")
print(f"README columns ({len(doc_cols)}): {doc_cols}")
print(f"in README but not CSV: {sorted(set(doc_cols) - set(cols))}; in CSV but not README: {sorted(set(cols) - set(doc_cols))}")
print(f"CSV time span {rows[0]['timestamp']} .. {rows[-1]['timestamp']}; README says 2026-10-01 to 2026-10-31")
ev = defaultdict(list)
for r in rows:
    if r["is_anomaly"] == "1":
        ev[r["anomaly_type"]].append(r["timestamp"])
print("CSV events:", {k: v[0] for k, v in ev.items()})

print("\n== 4 BOM_R3 vs design_checks mass table ==")
dc = json.load(open(P("mechanical", "checks", "design_checks.json"), encoding="utf-8"))
mt = defaultdict(float)
for r in dc["mass_table"]:
    mt[r["part_no"]] += r["kg"]
bom = list(csv.DictReader(open(P("mechanical", "cad", "BOM_R3.csv"), encoding="utf-8")))
diff = [(b["part_no"], round(int(b["qty"]) * float(b["mass_each_kg"]), 3), round(mt[b["part_no"]], 3)) for b in bom
        if b["part_no"] in mt and abs(int(b["qty"]) * float(b["mass_each_kg"]) - mt[b["part_no"]]) > 0.01]
print(f"float mass from BOM = {sum(int(b['qty']) * float(b['mass_each_kg']) for b in bom if b['part_no'] in mt):.2f} kg; "
      f"design_checks total = {dc['mass']['total_kg']} kg; mismatching part numbers: {diff}")
print(f"pier-side hardware (not in the float mass) = "
      f"{sum(int(b['qty']) * float(b['mass_each_kg']) for b in bom if b['part_no'] not in mt):.2f} kg")

print("\n== 5 referenced paths that do not exist ==")
refs = ["calculations/verified_design_calcs.py", "calculations/verified_design_calcs.json",
        "hardware/bom/AquaSentinel_BOM.csv", "firmware/edge_node/test/test_sleep_current.cpp",
        "mechanical/drawings/views/shots.json", "mechanical/renders", "mechanical/animation"]
for ref in refs:
    print(f"  {ref:50s} exists={os.path.exists(P(*ref.split('/')))}")
