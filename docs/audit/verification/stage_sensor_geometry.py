"""
Ultrasonic stage-sensor geometry over the design travel (read-only).

The stage sensor (AS3-712) sits on top of the guide carriage and looks up at the stage target plate (AS3-103)
welded to the upper clamp cap (parts.py lines 596-599 and 691-692). This script computes the sensor-to-target
range at low / mid / high water from params.py and design_checks.json, and the lateral offset to the upper
stop collar, which sits in the acoustic path below the target plate.

Typical waterproof ultrasonic modules quote a minimum range ("blind zone") of roughly 0.2-0.25 m and a wide
beam; confirm the real figures for the selected sensor from its datasheet.

Usage:  python docs/audit/verification/stage_sensor_geometry.py [repo_root]
"""
import json
import os
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "..", ".."))
lv = json.load(open(os.path.join(ROOT, "mechanical", "checks", "design_checks.json"), encoding="utf-8"))["levels_world_mm"]
TIER_Z1, TIER_T = 530.0, 6.0
CARR_TOP = TIER_Z1 + TIER_T + 56.0          # params.py line 62
SENSOR_TOP_FLOAT = CARR_TOP + 46.0          # parts.py line 597 (sensor body + face)
CLAMP_H, STOP_OD, STOP_H, BUFFER_H = 80.0, 100.0, 30.0, 20.0
target_underside = lv["zb_up"] + CLAMP_H / 2 - 4.0   # parts.py line 691 (4 mm plate at the clamp top)
collar_underside = lv["up_bot"]                       # EPDM buffer underside (parts.py line 727)
sensor_x, sensor_r = 118.0, 20.0                       # sensor axis 118 mm from the pole axis
for name, keel in (("low water", lv["keel_low"]), ("mid water", lv["keel_mid"]), ("high water", lv["keel_high"])):
    s = keel + SENSOR_TOP_FLOAT
    print(f"{name:10s}: sensor face z={s:7.1f} mm  range to target plate={target_underside - s:7.1f} mm  "
          f"range to upper buffer/collar={collar_underside - s:7.1f} mm")
print(f"target plate spans x=55..185 mm (130 x 110 mm); upper buffer/collar outer radius {STOP_OD / 2:.0f} mm; "
      f"lateral gap from the collar edge to the sensor edge = {sensor_x - sensor_r - STOP_OD / 2:.0f} mm")
print("=> near high water the range falls below a ~200-250 mm blind zone, and at every level the collar and buffer"
      " (a nearer reflector only ~48 mm to the side) can return the first echo instead of the plate.")
