# Firmware · ESP32 edge controller

`edge_node/` is a PlatformIO project (Arduino framework, `esp32dev`) for the controller in the AquaSentinel pod.
It runs the **sense → decide → act** loop on a 15-minute deep-sleep cycle, so the float never depends on the cloud to decide.

| Module | Job |
|---|---|
| `main.cpp` | wake, run one cycle, sleep; the decision-cycle counter is kept in flash, and the reset reason tells whether RTC memory survived |
| `sensor_interface` | power-gated 12 V RS485 Modbus bus: pH, EC, optical DO, turbidity; ultrasonic stage sensor (driver still to write). A failed or implausible read is NaN and never used |
| `dsp_filters` | exponential smoothing of each probe before any decision |
| `anomaly_engine` | CPCB Class C hard limits + robust z-score against a 24-bin diurnal baseline; acts on 2 of the last 3 readings; a fitted probe without a valid reading raises SENSOR_FAULT instead of "normal"; one sample per event, which ends after 4 clean cycles; learned baselines and the risk state are saved to flash and restored after a power cut |
| `autosampler` | 20 s purge to waste, 30 s fill, carousel indexing; bottle index kept in NVS; 60-min lockout counted in decision cycles |
| `wiper_actuator` | servo sweeps of the optical faces against biofouling |
| `microsd_logger` | time-stamped evidence log on microSD |
| `telemetry_comm` | builds the JSON telemetry frame and passes it to the LTE modem UART, with an emergency-priority flag (the full A7670C AT-command driver for upload and SMS is still to be written) |

Pin map and power rails are in [`include/config.h`](edge_node/include/config.h); the matching schematic is in
[`../hardware/kicad`](../hardware/kicad). The decision step was written from the Python reference in
[`../analytics/detector.py`](../analytics/detector.py). The audit fixes (sensor faults, one sample per event, the learning-period
event clearing) are not in that reference yet, so it no longer matches the firmware.
[`../analytics/train_proxy_anomaly_engine.py`](../analytics/train_proxy_anomaly_engine.py) regenerates
`include/exported_anomaly_weights.h` from the dataset.

```bash
cd edge_node
pio run -e esp32dev             # field build (15-minute deep-sleep cycle)
pio run -e bench                # bench-demo build for the finale (see BENCH_DEMO_PLAN.md)
pio run -e bench -t upload      # flash
pio device monitor -b 115200    # serial log
pio test -e bench               # unit tests (they run on the connected board)
```

**Status:** compiles cleanly in both environments (espressif32 6.13.0 / Arduino-ESP32 2.0.17) since the audit's P0-1
fixes. Fail-safe sensing (P0-2) is in place: a dead, garbled or implausible probe reading is never used, and a fitted
probe without a valid reading shows SENSOR_FAULT, never "normal". The decision state machine (P0-3) is in place: one
sample per event, hard limits included; no event left over from the learning period; and the learned state, the
learning progress and the sampler lockout survive a power cut. The unit tests in `test/` compile but have not yet run
on a board, and nothing has run on the real probes, actuators or modem. Demo mode is next: see
[BENCH_DEMO_PLAN.md](BENCH_DEMO_PLAN.md).
