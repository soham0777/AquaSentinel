"""One-page design check sheet from checks/design_checks.json (+ the v2 baseline for comparison)."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
C = json.load(open(os.path.join(ROOT, "checks", "design_checks.json"), encoding="utf-8"))
V2P = os.path.join(ROOT, "..", "calculations", "verified_design_calcs.json")
V2 = json.load(open(V2P, encoding="utf-8")) if os.path.exists(V2P) else None

INK, MUTED, GRID, BLUE, SURF = "#13202b", "#5b6b78", "#dde3e8", "#0b6e99", "#ffffff"
GOOD, BAD = "#1f7a45", "#b3261e"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED})

fig = plt.figure(figsize=(16.54, 11.69), dpi=150)
fig.patch.set_facecolor(SURF)
fig.text(0.035, 0.955, "AquaSentinel R3 - design check sheet", fontsize=22, weight="bold", color=INK)
fig.text(0.035, 0.928, "Every number below is computed from the R3 CAD geometry by src/build.py (mass properties, exact submerged "
         "volume, large-angle stability, projected areas, voxel interference).", fontsize=10.5, color=MUTED)
fig.text(0.035, 0.910, "DESIGN ESTIMATES - not test results. Catalogue masses (probes, battery, PV, pump) to be replaced by weighed values.",
         fontsize=10.5, color="#8a3b12", weight="bold")

h, p, cr, hd, m = C["hydrostatics"], C["pole"], C["carriage"], C["hydrodynamics"], C["mass"]
tiles = [("Mass (CAD, bottles full)", f"{m['total_kg']} kg"), ("Draft / freeboard", f"{h['draft_mm']:.0f} / {h['freeboard_mm']:.0f} mm"),
         ("Reserve buoyancy", f"{h['reserve_buoyancy_sf']} x"), ("GM transverse", f"{h['GM_T_m']} m"),
         ("Max righting arm", f"{h['GZ_max_mm']:.0f} mm @ {h['angle_of_GZ_max_deg']} deg"),
         ("Float drag at 1.5 m/s", f"{hd['float_drag_N']:.0f} N"),
         ("Pole stress (pinned)", f"{p['stress_pinned_MPa']} MPa  SF {p['SF_pinned']}"),
         ("Pole deflection", f"{p['deflection_pinned_mm']} mm"),
         ("Carriage jam margin", f"{cr['rollers_mu_0_05']['jam_margin']} x  (seized {cr['seized_rollers_sliding_mu_0_25']['jam_margin']} x)"),
         ("Float lag, full load", f"{cr['rollers_mu_0_05']['float_lag_mm']} mm")]
for i, (k, v) in enumerate(tiles):
    col, row = i % 5, i // 5
    x, y = 0.035 + col * 0.188, 0.80 - row * 0.085
    fig.patches.append(FancyBboxPatch((x, y), 0.175, 0.07, boxstyle="round,pad=0.002,rounding_size=0.008",
                                      transform=fig.transFigure, fc="#f3f6f8", ec=GRID, lw=0.8))
    fig.text(x + 0.010, y + 0.047, k, fontsize=9.5, color=MUTED)
    fig.text(x + 0.010, y + 0.014, v, fontsize=15, weight="bold", color=INK)

# GZ curve
ax = fig.add_axes([0.05, 0.40, 0.40, 0.27])
ang = [int(a) for a in h["GZ_curve_mm"].keys()]
gz = list(h["GZ_curve_mm"].values())
ax.plot(ang, gz, color=BLUE, lw=2.2, solid_capstyle="round")
ax.scatter(ang, gz, s=22, color=BLUE, zorder=3, edgecolor=SURF, linewidth=1.5)
i = gz.index(max(gz))
ax.annotate(f"max {gz[i]:.0f} mm at {ang[i]} deg", (ang[i], gz[i]), (ang[i] + 6, gz[i] + 12), color=INK, fontsize=9.5,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
ax.set_xlim(0, 60)
ax.set_ylim(0, max(gz) * 1.25)
ax.set_xlabel("heel angle (deg)")
ax.set_ylabel("righting arm GZ (mm)")
ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Large-angle stability - free floating (deployment, towing, gate open)", loc="left", fontsize=11.5, color=INK, pad=10)

# mass by subsystem
groups = [("Hulls, frame, deck", "AS3-2"), ("Guide carriage", "AS3-3"), ("Sensing", "AS3-4"), ("Power + control", "AS3-5"),
          ("Autosampler", "AS3-6"), ("Signal + comms", "AS3-7"), ("Handling + harness", "AS3-8"), ("Fasteners", "AS3-9")]
vals = []
for nm, pre in groups:
    vals.append(sum(r["kg"] for r in C["mass_table"] if r["part_no"].startswith(pre)))
ax2 = fig.add_axes([0.56, 0.40, 0.40, 0.27])
order = sorted(range(len(vals)), key=lambda k: vals[k])
ax2.barh([groups[k][0] for k in order], [vals[k] for k in order], color=BLUE, height=0.62)
for j, k in enumerate(order):
    ax2.text(vals[k] + 0.25, j, f"{vals[k]:.1f} kg", va="center", fontsize=9.5, color=INK)
ax2.set_xlim(0, max(vals) * 1.22)
ax2.set_xlabel("mass (kg)")
ax2.grid(True, axis="x", color=GRID, lw=0.6); ax2.set_axisbelow(True)
ax2.spines[["top", "right"]].set_visible(False)
ax2.set_title(f"Mass by subsystem - total {m['total_kg']} kg, CG {m['cg_mm'][0]:.0f} mm aft of the pole", loc="left",
              fontsize=11.5, color=INK, pad=10)

# checks
fig.text(0.035, 0.335, "Checks (pass criteria)", fontsize=13, weight="bold", color=INK)
for j, (k, ok) in enumerate(C["checks"].items()):
    col, row = j // 7, j % 7
    x, y = 0.035 + col * 0.235, 0.305 - row * 0.032
    fig.text(x, y, "PASS" if ok else "FAIL", fontsize=10, weight="bold", color=GOOD if ok else BAD)
    fig.text(x + 0.038, y, k, fontsize=10, color=INK)

# what changed vs v2
fig.text(0.53, 0.335, "What the refinement changed (v2 -> R3)", fontsize=13, weight="bold", color=INK)
rows = []
if V2:
    f2, p2, c2 = V2["float"], V2["pole_2in_sch40_316L"], V2["carriage"]
    rows = [("Mass basis", f"{f2['total_mass_kg']} kg hand budget", f"{m['total_kg']} kg from CAD", "real parts weigh more"),
            ("Hulls (each)", "900x200x220", "1000x230x260", "reserve >= 2, freeboard >= 100"),
            ("Draft / freeboard", f"{f2['draft_mm']} / {f2['freeboard_mm']} mm", f"{h['draft_mm']} / {h['freeboard_mm']} mm", ""),
            ("Pole position", "centre of float", "bow, between hulls", "no clash, short bracket, free yaw"),
            ("Roller tiers", f"{c2['roller_spacing_m'] * 1000:.0f} mm", f"{cr['roller_tier_spacing_mm']} mm", "bow pole needs more span"),
            ("Bracket span", f"{p2['bracket_span_m'] * 1000:.0f} mm", f"{p['bracket_span_mm']} mm", "set by stage + carriage"),
            ("Pole stress pinned", f"{p2['stress_pinned_MPa']} MPa", f"{p['stress_pinned_MPa']} MPa", f"SF {p2['SF_pinned']} -> {p['SF_pinned']}"),
            ("Float drag 1.5 m/s", f"{V2['loads']['float_drag_N']} N", f"{hd['float_drag_N']} N", "frontal area from CAD"),
            ("STEP files", "header only, no solid", "B-rep solids", "67/67 read by OpenCASCADE")]
hdr = ["Item", "v2", "R3", "Why"]
xs = [0.53, 0.635, 0.745, 0.835]
for x, t in zip(xs, hdr):
    fig.text(x, 0.305, t, fontsize=9.5, weight="bold", color=MUTED)
for j, r in enumerate(rows):
    y = 0.278 - j * 0.026
    for x, t in zip(xs, r):
        fig.text(x, y, t, fontsize=9.3, color=INK)
fig.savefig(os.path.join(ROOT, "checks", "AquaSentinel_R3_Design_Check_Sheet.png"), dpi=150, facecolor=SURF)
print("saved")
