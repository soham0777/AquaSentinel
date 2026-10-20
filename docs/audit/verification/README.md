# Audit verification scripts

Small, read-only programs written during the audit. Each reads files from the repository and prints results; none writes into the
project. They double as executable examples for the [knowledge base](../../learning/ENGINEERING_KNOWLEDGE_BASE.md).

Run from the repository root with Python 3 (numpy needed where noted):

| Script | What it shows | Key result (2026-10-18) |
|---|---|---|
| [detector_event_metrics.py](detector_event_metrics.py) | Replays `analytics/detector.py` like `evaluate.py`, then scores it against the labels; models the firmware's 60-min lockout and 4 bottles; baseline convergence | 4/4 events at +30 min; 3 stale EVENT cycles (rows 672-674); bottles used by the first two events; hourly DO bins 21-26 % converged |
| [firmware_engine_port.py](firmware_engine_port.py) (numpy) | Line-by-line float32 port of `anomaly_engine.cpp`; compares with the Python reference; failure scenarios | levels/triggers identical; 8 flag and 2,462 score differences; all probes dead → 0/4; reset on day 20 → one event late, one missed |
| [pole_carriage_couple.py](pole_carriage_couple.py) (numpy) | Pole bending with the two roller-tier forces over the whole travel | pinned 64.0 MPa (SF 2.66) vs 54.8 (3.10); fixed 38.5 MPa (4.41) vs 28.7 (5.92) |
| [dispersion_check.py](dispersion_check.py) | Fischer vs Kashefipour–Falconer forms vs the coded formula; mixing length | coded 778 m²/s vs 97 or 429; mixing length 1.8-7.1 km |
| [stage_sensor_geometry.py](stage_sensor_geometry.py) | Ultrasonic range to the target plate and to the upper buffer over the travel | 2,146 → 146 mm; buffer 20 mm above at high water, 48 mm off-axis |
| [data_integrity_checks.py](data_integrity_checks.py) | Cost BOM parsing and totals, power budget, dataset vs README, BOM vs mass table, missing referenced files | ₹1,38,000 vs ₹1,34,000; beacon not budgeted; dataset README mismatch; 7 missing paths |

```powershell
python docs\audit\verification\detector_event_metrics.py
python docs\audit\verification\firmware_engine_port.py
python docs\audit\verification\pole_carriage_couple.py
python docs\audit\verification\dispersion_check.py
python docs\audit\verification\stage_sensor_geometry.py
python docs\audit\verification\data_integrity_checks.py
```

An optional argument gives the repository root if you run them from elsewhere.
