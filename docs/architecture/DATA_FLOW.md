# Data flow

Three independent data flows exist in the repository: the **field flow** the device is meant to run, the **design flow** that
produces every mechanical artefact from one parameter file, and the **analytics flow** that exercises the decision logic on
synthetic data. Each is shown as designed, with its verified status. Interfaces are catalogued in [INTERFACE_REGISTER.md](INTERFACE_REGISTER.md).

## 1. Field data flow (designed; firmware does not compile)

```mermaid
sequenceDiagram
  autonumber
  participant RTC as ESP32 RTC timer
  participant MCU as ESP32 (main.cpp)
  participant RAIL as 12 V sensor rail
  participant P as 4 RS485 probes
  participant ST as Ultrasonic stage
  participant AE as anomaly_engine
  participant AS as autosampler
  participant B as Beacon
  participant SD as microSD
  participant M as LTE modem
  RTC->>MCU: wake (deep-sleep timer, 15 min)
  MCU->>RAIL: enable (GPIO32)
  MCU->>P: Modbus 0x03, reg 0x0000, x3 per probe (9600 8N1)
  P-->>MCU: raw registers (pH x100, temp x10, EC, DO x100, NTU x10)
  Note over MCU,P: on timeout/CRC error: fallback constant, valid=false
  MCU->>ST: (not implemented: constant 1.35 m)
  MCU->>RAIL: disable
  MCU->>AE: evaluate(readings, hour, boot_counter)
  AE-->>MCU: level, score, flags, trigger
  MCU->>B: set colour (print only)
  alt trigger
    MCU->>AS: purge 20 s, index carousel (simulated), fill 30 s
    AS->>AS: NVS SampleRecord + bottle index
  end
  MCU->>SD: logTelemetry (method does not exist)
  alt EVENT or every 4th wake
    MCU->>M: transmitTelemetry (method does not exist)
  end
  MCU->>RTC: arm 15-min timer, deep sleep
```

### 1.1 Data items and units along the path

| Stage | Item | Type / unit | Source |
|---|---|---|---|
| Probe register | pH | uint16, pH × 100 (assumed) | [sensor_interface.cpp:122](../../firmware/edge_node/src/sensor_interface.cpp#L122) |
| Probe register | water temperature | uint16, °C × 10 (assumed; signed temperatures not handled) | [:121](../../firmware/edge_node/src/sensor_interface.cpp#L121) |
| Probe register | EC | uint16, µS/cm (0–65,535; probe range 10–20,000) | [:132](../../firmware/edge_node/src/sensor_interface.cpp#L132) |
| Probe register | DO | uint16, mg/L × 100 | [:142](../../firmware/edge_node/src/sensor_interface.cpp#L142) |
| Probe register | turbidity | uint16, NTU × 10 (confirmed by DFRobot forum) | [:152](../../firmware/edge_node/src/sensor_interface.cpp#L152) |
| `SensorReadings` | ph, ec, do_val, turbidity, temperature, stage | float32; stage in m | [anomaly_engine.h:20-29](../../firmware/edge_node/include/anomaly_engine.h#L20-L29) |
| `SensorReadings` | timestamp | uint32 seconds from `time(NULL)` (clock never set) | [sensor_interface.cpp:168](../../firmware/edge_node/src/sensor_interface.cpp#L168) |
| `SensorReadings` | valid[6] | bool per channel (ignored downstream) | [:196-198](../../firmware/edge_node/src/sensor_interface.cpp#L196-L198) |
| `AnomalyResult` | level, max_score, reason[128], contributing_flags, autosampler_trigger | enum, float, text, bitmask (bit0 pH, bit1 EC, bit2 DO, bit3 turbidity) | [anomaly_engine.h:31-37](../../firmware/edge_node/include/anomaly_engine.h#L31-L37) |
| RTC memory | 24-bin pH/DO baselines, EC/turbidity baselines, outlier history, risk state, boot counter | float pairs (μ, d), bytes | [anomaly_engine.cpp:14-26](../../firmware/edge_node/src/anomaly_engine.cpp#L14-L26) |
| NVS (`aquasampler`) | `bottle_idx`, `last_ts`, `rec_0`…`rec_3` (`SampleRecord`: index, timestamp, pH, EC, DO, turbidity, reason[64], collected) | binary struct | [autosampler.cpp:106-115](../../firmware/edge_node/src/autosampler.cpp#L106-L115) |
| microSD CSV (older schema) | epoch_timestamp, ph, turbidity_ntu, temp_c, ec_us_cm, do_mg_l, depth_m, battery_v, anomaly_score, is_anomaly, alert_desc | text | [microsd_logger.cpp:23](../../firmware/edge_node/src/microsd_logger.cpp#L23) |
| Telemetry JSON (older schema) | device_id, fw_ver, stretch, boot_seq, ts, telemetry{ph, turb_ntu, temp_c, ec_us, do_mg, depth_m, v_batt}, anomaly_engine{is_alert, score, z_score, type} | ArduinoJson ≤ 512 B | [telemetry_comm.cpp:9-36](../../firmware/edge_node/src/telemetry_comm.cpp#L9-L36) |

Gaps on this path: no battery-voltage measurement (INA226 has no driver), so the `battery_v`/`v_batt` fields have no source; no
stage data; no time base; the logger and telemetry modules belong to an older data model and must be rewritten against
`SensorReadings`/`AnomalyResult`.

### 1.2 Time base

The only clock in use is the ESP32 system time, never set from SNTP, the LTE network or the DS3231. After a power-on reset it starts
at 1970-01-01, and between deep sleeps it is kept by the RC slow clock, whose drift is large. Consequences: the hour-of-day bins
are not local time, sample time stamps are not evidence-grade, and the sampler lockout can be bypassed after a reset
([autosampler.cpp:61-68](../../firmware/edge_node/src/autosampler.cpp#L61-L68)). The dataset and the dashboard label times "UTC";
the diurnal photosynthesis cycle follows local solar time (IST = UTC + 5:30).

## 2. Design data flow (working, reproducible)

```mermaid
flowchart LR
  P["params.py<br/>dimensions, materials"] --> PARTS["parts.py + geom.py<br/>66 parts, 121 float instances,<br/>guide parts"]
  PARTS --> AN["analysis.py<br/>mass, draft, GZ, drag, pole, carriage,<br/>clearances, voxels"]
  AN --> DC["checks/design_checks.json"]
  AN --> BOM["cad/BOM_R3.csv"]
  PARTS --> EXP["export.py"]
  EXP --> STEP["cad/parts/*.step (66)<br/>cad/assembly/*_MidWater.step"]
  EXP --> STL["cad/parts/*.stl (66)"]
  EXP --> GLB["cad/assembly/AquaSentinel_R3.glb"]
  GLB --> VIEW["viewer/template.html"] --> PUB["publish.py viewer"] --> SITE["docs/viewer.html"]
  VIEW -->|"AS.ortho via drawing_shots.js + serve.py"| VIEWS["drawings/views/*.png<br/>(not in repo)"]
  VIEWS --> DRW["drawings.py"] --> SHEETS["drawings/*.png + PDF"]
  DC --> DRW
  DC --> CS["check_sheet.py"] --> CSP["checks/*.png"]
  V2["../calculations/verified_design_calcs.json<br/>(not in repo)"] -.-> CS
  STEP --> SWX["SOLIDWORKS Pack and Go<br/>(manual, 2026-10-05)"]
  STEP --> OCC["tools/step_check.html<br/>OpenCascade read check"] --> SV["checks/step_validation.json"]
  SWX --> FEA["SOLIDWORKS Simulation<br/>pole + bracket reports"]
```

Units: millimetres and kilograms inside the engine; STEP files declare millimetres; GLB uses metres under a Y-up root
(`np.diag([0.001]*3) @ Rx(-90)`, [build.py:396](../../mechanical/src/build.py#L396)); the viewer converts with `m2t()`
([template.html:194](../../mechanical/viewer/template.html#L194)).

Verified: `build.py` regenerates every CAD/BOM/check file identically (STEP differs only in its header time stamp);
`publish.py viewer` regenerates `docs/viewer.html` exactly. Not reproducible from the repository: drawing views, drawings,
check-sheet v2 table, motion-study triptych, assembly GIF, renders, videos, SOLIDWORKS files and FEA reports.

## 3. Analytics data flow (working on synthetic data)

```mermaid
flowchart LR
  GEN["dataset/generate_water_quality_timeseries.py<br/>seed 42"] --> CSV["synthetic_river_timeseries.csv<br/>2,880 rows, 4 events"]
  CSV --> EVAL["evaluate.py"] --> DET["detector.py"]
  EVAL --> PNG["plot_detector_evaluation.png"]
  CSV --> TRAIN["train_proxy_anomaly_engine.py"] --> HDR["firmware/.../exported_anomaly_weights.h<br/>(unused by firmware)"]
  ADE["advection_dispersion_model.py"] --> PNG2["advection_dispersion_breakthrough_curves.png"]
  DET -. "mirrors" .-> FWAE["firmware anomaly_engine.cpp"]
```

Dataset schema (actual, not the one in `dataset/README.md`): `timestamp` (ISO, naive, starting 2026-03-01T00:00), `step_index`,
`ph`, `turbidity_ntu`, `temp_c`, `ec_us_cm`, `do_mg_l`, `depth_m`, `flow_velocity_m_s`, `event_label` (NORMAL/CONTAMINATION),
`is_anomaly` (0/1), `anomaly_type` (NONE, INDUSTRIAL_ACID_DUMP, RAW_SEWAGE_OVERFLOW, CHEMICAL_SALT_SPILL, HEAVY_SILT_SURGE).
Full analysis in [ANALYTICS_AND_DATA_REVIEW.md](../analytics/ANALYTICS_AND_DATA_REVIEW.md).

## 4. Presentation data flow

`docs/index.html` embeds `viewer.html` (iframe) and links the dashboard, PDF deck and videos. The dashboard has no data input: all
values are constants in `app.js` changed by demo buttons. There is no path today from a float, or from any file in the repository,
into the dashboard.
