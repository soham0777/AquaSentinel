# Firmware · ESP32 edge controller

`edge_node/` is a PlatformIO project (Arduino framework, `esp32dev`) for the controller in the AquaSentinel pod.
It runs the **sense → decide → act** loop on a 15-minute deep-sleep cycle, so the float never depends on the cloud to decide.

| Module | Job |
|---|---|
| `main.cpp` | wake, run one cycle, sleep; counters kept in RTC memory across deep sleep |
| `sensor_interface` | power-gated 12 V RS485 Modbus bus: pH, EC, optical DO, turbidity; ultrasonic stage sensor |
| `dsp_filters` | exponential smoothing of each probe before any decision |
| `anomaly_engine` | CPCB Class C hard limits + robust z-score against a 24-bin diurnal baseline; acts on 2 of the last 3 readings |
| `autosampler` | 20 s purge to waste, 30 s fill, carousel indexing; bottle index and lockout kept in NVS |
| `wiper_actuator` | servo sweeps of the optical faces against biofouling |
| `microsd_logger` | time-stamped evidence log on microSD |
| `telemetry_comm` | builds the JSON telemetry frame and passes it to the LTE modem UART, with an emergency-priority flag (the full A7670C AT-command driver for upload and SMS is still to be written) |

Pin map and power rails are in [`include/config.h`](edge_node/include/config.h); the matching schematic is in
[`../hardware/kicad`](../hardware/kicad). The decision step has a bit-for-bit Python reference in
[`../analytics/detector.py`](../analytics/detector.py), and [`../analytics/train_proxy_anomaly_engine.py`](../analytics/train_proxy_anomaly_engine.py)
regenerates `include/exported_anomaly_weights.h` from the dataset.

```bash
cd edge_node
pio run            # build
pio run -t upload  # flash
```

**Status:** not yet compiled and bench-run on the real probes and modem.
