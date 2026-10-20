"""
Guide-pole bending including the moment the two-tier carriage transmits (read-only check).

mechanical/src/build.py (lines 126-142) checks the pole with the whole float load P applied as one point force
at mid-span: M = P*L/4 + w*L^2/8 (pinned) and P*L/8 + w*L^2/12 (fixed). But build.py itself (lines 145-159)
shows the float load acts h = 428 mm below the carriage mid-height, so the two roller tiers (s = 350 mm apart)
push on the pole with r1 = P/2 + P*h/s and r2 = P/2 - P*h/s (1106.9 N and -464.8 N). This script applies those
two tier forces (plus the pole's own drag w) to a pinned-pinned and a fixed-fixed beam, scans every carriage
position inside the 2 m travel, and compares the peak stress with the repo's single-force method.

Usage:  python docs/audit/verification/pole_carriage_couple.py [repo_root]
Requires: numpy
"""
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "..", ".."))
C = json.load(open(os.path.join(ROOT, "mechanical", "checks", "design_checks.json"), encoding="utf-8"))
pole, car, lv = C["pole"], C["carriage"], C["levels_world_mm"]
L = pole["bracket_span_mm"] / 1000.0
P = pole["load_at_float_N"]
w = pole["pole_drag_N_per_m"]
s = car["roller_tier_spacing_mm"] / 1000.0
h = car["load_height_below_carriage_mid_mm"] / 1000.0
OD, WALL = 0.0603, 0.00391
I = math.pi / 64 * (OD ** 4 - (OD - 2 * WALL) ** 4)
Z = I / (OD / 2)
E, SY = 193e9, 170e6
r1, r2 = P / 2 + P * h / s, P / 2 - P * h / s
print(f"span L={L:.3f} m, P={P} N, w={w} N/m, tier spacing s={s} m, load height below carriage mid h={h} m")
print(f"tier forces: lower r1={r1:.1f} N, upper r2={r2:.1f} N (sum {r1 + r2:.1f} N; couple P*h={P * h:.1f} N.m)")

x = np.linspace(0, L, 4001)


def moment_pinned(a1, F1, a2, F2):
    M = w * x * (L - x) / 2
    for a, F in ((a1, F1), (a2, F2)):
        M += np.where(x <= a, F * (L - a) * x / L, F * a * (L - x) / L)
    return M


def moment_fixed(a1, F1, a2, F2):
    """Fixed-fixed beam by superposition (point load F at a: end moments -F a b^2/L^2, -F a^2 b/L^2)."""
    M = w * (6 * L * x - 6 * x ** 2 - L ** 2) / 12
    for a, F in ((a1, F1), (a2, F2)):
        b = L - a
        MA, MB = -F * a * b ** 2 / L ** 2, -F * a ** 2 * b / L ** 2
        RA = (F * b + MB - MA) / L  # from M(L) = MA + RA*L - F*b = MB; equals F*b^2*(3a+b)/L^3
        M += MA + RA * x - np.where(x > a, F * (x - a), 0.0)
    return M


# roller tier positions measured from the lower bracket centre, over the whole design travel
z_lower_roller_float = 180 + 6 + 31  # TIER_Z[0] + TIER_T + 31 (parts.py roller placement)
best_p = best_f = (0, None)
for keel in np.linspace(lv["keel_low"], lv["keel_high"], 401):
    a1 = (keel + z_lower_roller_float - lv["zb_low"]) / 1000.0
    a2 = a1 + s
    if not (0 < a1 < L and 0 < a2 < L):
        continue
    mp = np.abs(moment_pinned(a1, r1, a2, r2)).max()
    mf = np.abs(moment_fixed(a1, r1, a2, r2)).max()
    if mp > best_p[0]:
        best_p = (mp, a1)
    if mf > best_f[0]:
        best_f = (mf, a1)
for label, (m, a1), repo_s in (("pinned", best_p, pole["stress_pinned_MPa"]), ("fixed", best_f, pole["stress_fixed_MPa"])):
    sig = m / Z / 1e6
    print(f"{label:6s}: max M={m:.0f} N.m at lower tier {a1:.2f} m above lower bracket -> {sig:.1f} MPa, SF={SY / 1e6 / sig:.2f}"
          f"   (repo single-force method: {repo_s} MPa, SF={SY / 1e6 / repo_s:.2f})")
print(f"section: I={I:.4e} m^4, Z={Z:.4e} m^3; yield 170 MPa (annealed 316L)")
