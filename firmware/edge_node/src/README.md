# src

`main.cpp` is the entry point: one wake cycle (read, decide, act, log, sleep). Each other file has a matching header in [`../include`](../include).

| File | Job |
|---|---|
| `sensor_interface.cpp` | power-gated RS485 Modbus-RTU reads, CRC16, median of three, warm-up, health flags |
| `anomaly_engine.cpp` | the decision logic: hard limits + learned baseline; must stay identical to `analytics/detector.py` (check with `python tools/parity/compare.py`) |
| `autosampler.cpp` | purge, fill, carousel index, lockout; bottle state saved to flash |
| `wiper_actuator.cpp` | anti-fouling wiper sweep |
| `microsd_logger.cpp` | reading log on microSD |
| `telemetry_comm.cpp` | JSON telemetry frame to the LTE modem |
| `dsp_filters.cpp` | median / smoothing helpers (not wired in yet) |

Changing logic here changes behaviour: re-run `pio test -e bench` (on a board) and `python tools/parity/compare.py` afterwards.
