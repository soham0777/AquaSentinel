# firmware/edge_node: the ESP32 PlatformIO project

Open this folder in VS Code with the PlatformIO extension, or use the command line (`pip install platformio`):

```bash
pio run -e esp32dev          # field build (15-minute deep-sleep cycle)
pio run -e bench             # table-demo build for the 19-20 Nov finale (see ../BENCH_DEMO_PLAN.md)
pio test -e bench            # 26 Unity tests; they run on a connected board (none has run on a board yet)
```

| Folder / file | Contents |
|---|---|
| `platformio.ini` | pinned toolchain: espressif32 6.13.0, ArduinoJson 6.21.6, two environments (`esp32dev`, `bench`) |
| `include/` | headers; `config.h` holds the pin map, intervals and hard limits |
| `src/` | the code: `main.cpp` (one wake cycle), `sensor_interface`, `anomaly_engine` (the decision logic), `autosampler`, `wiper_actuator`, `microsd_logger`, `telemetry_comm`, `dsp_filters` |
| `test/` | Unity tests: `test_fail_safe` (12) and `test_state_machine` (14) |

Secrets: Wi-Fi / Telegram / modem credentials must go in `include/secrets.h`, which is **git-ignored**. Never commit it.

To check the decision engine without a board: `python tools/parity/compare.py` (from the repository root).
Module-by-module description and status: [`../README.md`](../README.md).
