# tools/parity: does the firmware decide like the Python reference?

`compare.py` compiles the real `firmware/edge_node/src/anomaly_engine.cpp` for your PC (no ESP32 needed) and replays the
30-day synthetic dataset through it and through `analytics/detector.py`. It then checks that the level (NORMAL / WATCH /
EVENT), the autosampler trigger and the contributing-flag bits are identical on all 2,880 rows.

```bash
python tools/parity/compare.py        # needs Python 3 and any C++17 compiler (g++, clang++, or: pip install ziglang)
```

Expected last line: `PARITY: PASS` (0 mismatches, 4 samples each, 69 EVENT rows each).

| File | What it is |
|---|---|
| `compare.py` | builds the harness in a temp folder, runs both engines, prints PASS / FAIL |
| `harness.cpp` | tiny C++ driver that feeds CSV rows to `AnomalyEngine` |
| `shim/Arduino.h`, `shim/Preferences.h` | host-side stand-ins so the engine compiles off-device (`RTC_DATA_ATTR` is empty, `Preferences` is in memory) |

Known, accepted difference: C++ `max_score` is not always the true maximum z-score (see `docs/REORG_NOTES.md`, TODO list).
That field is only reported, never used for decisions, and this test deliberately compares decisions only.
