"""
Longitudinal dispersion coefficient check for analytics/advection_dispersion_model.py (read-only).

The repo computes Kashefipour & Falconer (2002) as  D = [10.612 (U/u*) + 2.0] U H (W/H)^0.65  (line 44).
The paper (Water Research 36(6):1596-1608, doi:10.1016/S0043-1354(01)00351-7) gives a piecewise equation,
reproduced e.g. in Table 2 of arXiv:2106.11026:
    (i)  W/H > 50 :  D = 10.612 H U^2 / u*
    (ii) W/H <= 50:  D = [7.428 + 1.775 (W/H)^0.620 (u*/U)^0.572] H U (U/u*)   (form most often cited)
         variant  :  same with (U/u*)^0.572, as printed in the arXiv review table
Here W/H = 27.8, so (ii) applies. Check the exponent's ratio against the original paper; either way the coded
expression matches neither form. This script shows the size of the difference, its effect on peak plume
concentration, and the 1-D model's validity limit (mixing length).

Usage:  python docs/audit/verification/dispersion_check.py
"""
import math

U, W, H, S, g = 0.60, 50.0, 1.80, 0.00035, 9.80665  # the repo's scenario values (advection_dispersion_model.py)
us = math.sqrt(g * H * S)
fischer = 0.011 * U ** 2 * W ** 2 / (H * us)
repo_kf = (10.612 * (U / us) + 2.0) * U * H * (W / H) ** 0.65
kf_i = 10.612 * H * U ** 2 / us
kf_ii = (7.428 + 1.775 * (W / H) ** 0.620 * (us / U) ** 0.572) * H * U * (U / us)
kf_ii_alt = (7.428 + 1.775 * (W / H) ** 0.620 * (U / us) ** 0.572) * H * U * (U / us)
print(f"u* = {us:.4f} m/s, W/H = {W / H:.1f}")
print(f"Fischer (1975)                  D = {fischer:7.1f} m^2/s")
print(f"K&F as coded in the repo        D = {repo_kf:7.1f} m^2/s   <- {repo_kf / kf_ii:.1f}x form (ii), "
      f"{repo_kf / kf_ii_alt:.1f}x the variant")
print(f"K&F (i)  10.612 H U^2/u*        D = {kf_i:7.1f} m^2/s   (W/H > 50 only)")
print(f"K&F (ii) (u*/U)^0.572           D = {kf_ii:7.1f} m^2/s")
print(f"K&F (ii) variant (U/u*)^0.572   D = {kf_ii_alt:7.1f} m^2/s")
A = W * H
for name, D in (("repo mean", (fischer + repo_kf) / 2), ("Fischer/K&F(ii) mean", (fischer + kf_ii) / 2)):
    for x in (4500.0, 19000.0):
        t = x / U
        cpk = 500.0 * 1000 / (A * math.sqrt(4 * math.pi * D * t))  # g/m3 at the advective peak (no decay)
        print(f"  {name:22s} D={D:6.1f}  x={x / 1000:4.1f} km: peak ~{cpk:6.2f} mg/L at t={t / 3600:.1f} h")
eps_t = 0.6 * H * us  # transverse mixing coefficient, Fischer et al. (1979) typical value
for where, k in (("centreline release", 0.1), ("bank release", 0.4)):
    Lm = k * U * W ** 2 / eps_t
    print(f"distance to full cross-sectional mixing ({where}): ~{Lm / 1000:.1f} km "
          f"(the 1-D Fickian solution is not valid upstream of this)")
print("receptors in the repo: 4.5, 11.0 and 19.0 km (straight-line; the script notes ~22.8 km channel length but uses 19.0)")
