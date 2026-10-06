"""
AquaSentinel R3 - one-command build:   python src/build.py

Builds every part, computes the engineering checks from the geometry, and writes
  cad/parts/*.step|*.stl          one file per part, in its own local frame
  cad/assembly/*.step             assembly (one PRODUCT per part, placed) at low / mid / high water
  cad/assembly/*.stl              merged meshes at low / mid / high water
  cad/assembly/AquaSentinel_R3.glb   scene for the viewer / animation (node tree + metadata)
  cad/BOM_R3.csv                  BOM linked to part numbers
  checks/design_checks.json       all computed results + pass/fail
"""
import csv
import json
import math
import os
import sys
import time
from collections import Counter, OrderedDict

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import analysis as A
import export as X
import geom as g
from params import *
from analysis import RHO_W, G
from parts import build_float, build_guide, build_environment, guide_levels

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_PARTS = os.path.join(ROOT, "cad", "parts")
OUT_ASM = os.path.join(ROOT, "cad", "assembly")
OUT_CHK = os.path.join(ROOT, "checks")
for d in (OUT_PARTS, OUT_ASM, OUT_CHK):
    os.makedirs(d, exist_ok=True)

STEPS = OrderedDict([
    (1, ("Pier brackets", "Two identical 316L brackets are anchored to the pier face with A4 chemical anchors.")),
    (2, ("Guide pole", "2 in Sch 40S 316L pole drops into both clamps; stop collars, EPDM buffers and the stage target plate fit on.")),
    (3, ("Twin hulls", "Two identical rotomoulded, foam-filled PE hulls (one mould). Signal yellow, IALA special-mark colour.")),
    (4, ("Frame and deck", "Four 6061 crossbeams bolt into moulded-in inserts; the 3 mm tread-plate deck sits on top.")),
    (5, ("Guide carriage", "Fixed half bolts to crossbeam 1. Eight concave UHMW rollers on two tiers 350 mm apart. Front gate swings open to release the pole.")),
    (6, ("Sensor well", "PE pipe sleeve through the deck, 316L guard cage below, V debris deflector ahead of it.")),
    (7, ("Power and control pod", "IP67 pod: LiFePO4 battery, MPPT, ESP32 / RS485 / LTE controller.")),
    (8, ("Solar canopy", "20 W module on four stanchions: it also shades the pod. Hinges up on the aft pair for access.")),
    (9, ("Autosampler", "Insulated cassette: 4 x 250 mL lab bottles on a lift-out carousel, reversible peristaltic pump, purge-to-waste.")),
    (10, ("Beacon, antenna, stage sensor", "Jal-Deep 360 deg status light, LTE antenna, and an upward ultrasonic that reads the river stage.")),
    (11, ("Sensor cartridge", "pH, EC, optical DO and turbidity probes plus wiper and sample intake drop into the well as one cartridge.")),
    (12, ("Harness and handling", "Cables, sampler hoses, four grab handles and four lifting eyes.")),
])


def main():
    t0 = time.time()
    fparts, finst, pivots = build_float()

    # ---------------- mass + draft from geometry -------------------------
    rows, M, CG = A.mass_properties(finst)
    tris = A.tri_soup(finst)
    vol = M / RHO_W * 1e9                       # mm3
    draft = A.solve_waterplane(tris, vol)
    L = guide_levels(draft)
    gparts, ginst, L = build_guide(draft)
    eparts, einst = build_environment(L)

    res = OrderedDict()
    res["status"] = "DESIGN ESTIMATE from the R3 CAD geometry - not measured. Replace catalogue masses with weighed values."
    res["mass"] = dict(total_kg=round(M, 2), cg_mm=[round(float(c), 1) for c in CG],
                       by_group={k: round(sum(r["kg"] for r in rows if r["group"] == k), 2) for k in sorted(set(r["group"] for r in rows))},
                       basis_counts=dict(Counter(r["basis"] for r in rows)))
    # dry / transport case: cartridge out, bottles empty
    dry_M = M - sum(r["kg"] for r in rows if r["group"] == "cartridge") - 4 * 0.25

    # ---------------- hydrostatics -----------------------------------------
    hull_inst = [i for i in finst if i.part.key == "pontoon"]
    hull_tris = A.tri_soup(hull_inst)
    hull_vol = sum(abs(s.signed_volume()) for i in hull_inst for s in A.inst_shells(i)[:1])
    _, cb = A.submerged(tris, draft)
    dv = 1.0
    v1, c1 = A.submerged(tris, draft + dv)
    v0, c0 = A.submerged(tris, draft)
    awp = (v1 - v0) / dv                        # mm2
    lcf = (v1 * c1[0] - v0 * c0[0]) / (v1 - v0)
    small = 2.0
    gz_small = A.gz_curve(tris, CG, vol, [small])[0]
    gm_t = gz_small / math.sin(math.radians(small))
    angles = list(range(0, 61, 5))
    gz = A.gz_curve(tris, CG, vol, angles)
    # longitudinal: free-floating trim (detached from the pole)
    p_, R_ = A.rotate_y(tris, 1.0, (CG[0], CG[2]))
    gg = R_ @ (CG - np.array([CG[0], 0, CG[2]])) + np.array([CG[0], 0, CG[2]])
    d1 = A.solve_waterplane(p_, vol)
    _, cb1 = A.submerged(p_, d1)
    gm_l = (cb1[0] - gg[0]) / math.sin(math.radians(1.0))
    trim_moment = M * G * (CG[0] - cb[0]) / 1000.0           # N.m (mass x lever)
    free_trim_deg = math.degrees(math.atan((CG[0] - cb[0]) / gm_l)) if gm_l > 0 else float("nan")
    freeboard = PONT_H - draft
    res["hydrostatics"] = dict(
        draft_mm=round(draft, 1), freeboard_mm=round(freeboard, 1),
        displaced_L=round(vol / 1e6, 2), hull_volume_L=round(hull_vol / 1e6, 1),
        reserve_buoyancy_sf=round(hull_vol / vol, 2),
        dry_transport_mass_kg=round(dry_M, 1),
        waterplane_area_m2=round(awp / 1e6, 4), LCF_from_pole_mm=round(lcf, 1),
        LCB_mm=round(float(cb[0]), 1), LCG_mm=round(float(CG[0]), 1), KG_mm=round(float(CG[2]), 1),
        KB_mm=round(float(cb[2]), 1), GM_T_m=round(gm_t / 1000, 3), GM_L_m=round(gm_l / 1000, 2),
        trim_moment_Nm=round(trim_moment, 2), free_trim_if_detached_deg=round(free_trim_deg, 2),
        GZ_curve_mm={str(a): round(v, 1) for a, v in zip(angles, gz)},
        GZ_max_mm=round(max(gz), 1), angle_of_GZ_max_deg=angles[int(np.argmax(gz))],
        deck_edge_immersion_deg=round(math.degrees(math.atan(freeboard / (PONT_YC + PONT_W / 2))), 1))

    # ---------------- drag / areas ------------------------------------------
    afront, fy, fz = A.projected_area(tris, draft, "yz", 2.0)
    alat, lx, lz = A.projected_area(tris, draft, "xz", 2.0)
    V_FLOOD, DEBRIS_N, CD_FLOAT, CD_CYL = 1.5, 500.0, 1.05, 1.2       # same load case as v2
    f_float = 0.5 * RHO_W * CD_FLOAT * (afront / 1e6) * V_FLOOD ** 2
    res["hydrodynamics"] = dict(
        design_velocity_m_s=V_FLOOD, debris_snag_N=DEBRIS_N, Cd_float=CD_FLOAT,
        frontal_area_m2=round(afront / 1e6, 4), frontal_centroid_z_mm=round(fz, 1),
        lateral_area_m2=round(alat / 1e6, 4), centre_of_lateral_resistance_x_mm=round(lx, 1),
        float_drag_N=round(f_float, 1),
        weathervane_stable=bool(lx > 0),
        note="The float pivots on the pole at its bow; its lateral area centre is aft of the pole, so it trails "
             "downstream like a vane and turns no torque into the guide.")

    # ---------------- pole --------------------------------------------------
    OD, WALL = POLE_OD / 1000, POLE_WALL / 1000
    ID = OD - 2 * WALL
    I = math.pi / 64 * (OD ** 4 - ID ** 4)
    Z = I / (OD / 2)
    SY, E = 170e6, 193e9
    span = (L["zb_up"] - L["zb_low"]) / 1000
    w = 0.5 * RHO_W * CD_CYL * OD * V_FLOOD ** 2
    P = f_float + DEBRIS_N
    Mp = P * span / 4 + w * span ** 2 / 8
    Mf = P * span / 8 + w * span ** 2 / 12
    defl = P * span ** 3 / (48 * E * I) + 5 * w * span ** 4 / (384 * E * I)
    res["pole"] = dict(section="2 in Sch 40S SS316L", length_mm=round(L["pole_z1"] - L["pole_z0"]),
                       bracket_span_mm=round(span * 1000), load_at_float_N=round(P, 1), pole_drag_N_per_m=round(w, 1),
                       stress_pinned_MPa=round(Mp / Z / 1e6, 1), SF_pinned=round(SY / (Mp / Z), 2),
                       stress_fixed_MPa=round(Mf / Z / 1e6, 1), SF_fixed=round(SY / (Mf / Z), 2),
                       deflection_pinned_mm=round(defl * 1000, 1), bracket_reaction_N=round(P / 2 + w * span / 2, 1),
                       yield_MPa=170, note="v2 method; span set by the R3 stage geometry")

    # ---------------- carriage ----------------------------------------------
    s_rol = (TIER_Z[1] - TIER_Z[0]) / 1000
    z_mid = (TIER_Z[0] + TIER_Z[1]) / 2 + TIER_T + 31
    h_load = (z_mid - fz) / 1000
    e = abs(lcf) / 1000

    def carriage(mu):
        couple = P * h_load / s_rol
        r1, r2 = P / 2 + couple, abs(P / 2 - couple)
        trim_N = abs(trim_moment) / s_rol
        fr = mu * (r1 + r2)
        fr_static = mu * 2 * trim_N
        return dict(roller_loads_N=[round(r1, 1), round(r2, 1)], friction_N=round(fr, 1),
                    float_lag_mm=round(fr / (RHO_W * G * awp / 1e6) * 1000, 1),
                    static_trim_roller_N=round(trim_N, 1), static_lag_mm=round(fr_static / (RHO_W * G * awp / 1e6) * 1000, 2),
                    jam_eccentricity_limit_m=round(s_rol / (2 * mu), 2), jam_margin=round(s_rol / (2 * mu) / e, 2))

    res["carriage"] = dict(roller_tier_spacing_mm=round(s_rol * 1000), eccentricity_LCF_mm=round(e * 1000, 1),
                           load_height_below_carriage_mid_mm=round(h_load * 1000, 1),
                           rollers_mu_0_05=carriage(0.05), seized_rollers_sliding_mu_0_25=carriage(0.25),
                           rule="drawer rule: no self-locking while e < s / (2 mu)")

    # ---------------- clearances -------------------------------------------
    clear = OrderedDict()
    corridor = []
    for i in finst:
        tr = A.tri_soup([i])
        dmin = float(A.min_dist_xy_to_origin(tr).min())
        corridor.append((dmin, i.name, i.part.key))
    rollers = [c for c in corridor if c[2] == "roller"]
    others = sorted([c for c in corridor if c[2] != "roller"])
    clear["pole_corridor"] = dict(pole_radius_mm=POLE_R, required_clearance_mm=5.0,
                                  closest_parts=[dict(instance=n, radial_mm=round(d, 1), gap_mm=round(d - POLE_R, 1))
                                                 for d, n, _ in others[:6]],
                                  roller_contact_radius_mm=round(min(r[0] for r in rollers), 2),
                                  pass_=bool(others[0][0] - POLE_R >= 5.0))
    # float vs fixed hardware over the whole travel (XY overlap + z interval)
    lo_xy, hi_xy = np.array([-500.0, -500.0]), np.array([1100.0, 500.0])
    fixed_xy = {}
    for gi in ginst:
        if gi.part.key == "pole":
            continue
        tr = A.tri_soup([gi])
        fixed_xy[gi.name] = (A.xy_occupancy(tr, lo_xy, hi_xy), tr[:, :, 2].min(), tr[:, :, 2].max())
    hits = []
    for fi in finst:
        tr = A.tri_soup([fi])
        occ = A.xy_occupancy(tr, lo_xy, hi_xy)
        z0r, z1r = tr[:, :, 2].min(), tr[:, :, 2].max()
        for name, (focc, fz0, fz1) in fixed_xy.items():
            if not (occ & focc).any():
                continue
            # swept z-interval of the float part over the design travel
            if (z1r + L["keel_high"] > fz0) and (z0r + L["keel_low"] < fz1):
                hits.append(dict(float_part=fi.name, fixed_part=name))
    clear["float_vs_fixed_over_travel"] = dict(conflicts=hits, pass_=len(hits) == 0)
    # yaw: only the hull rub rails may touch the pier
    above = [i for i in finst if i.part.key not in ("pontoon", "bumper")]
    ymax_eq = max(np.abs(A.tri_soup([i])[:, :, 1]).max() for i in above)
    rail = PONT_YC + PONT_W / 2 - 3 + RUBRAIL_R
    clear["yaw_contact"] = dict(outermost_equipment_y_mm=round(float(ymax_eq), 1), rub_rail_y_mm=round(rail, 1),
                                pass_=bool(ymax_eq < rail))

    # part-to-part interference (voxels, 2 mm), skipping fasteners/harness and enclosure contents
    skip_kinds = {"fastener", "harness"}
    cand = [i for i in finst if i.part.kind not in skip_kinds]
    boxes = {i.name: A.bbox(A.inst_shells(i)) for i in cand}
    hollow = [i for i in cand if i.part.hollow]
    interf = []
    checked = 0
    for a_i in range(len(cand)):
        for b_i in range(a_i + 1, len(cand)):
            A_, B_ = cand[a_i], cand[b_i]
            la, ha = boxes[A_.name]
            lb, hb = boxes[B_.name]
            lo = np.maximum(la, lb)
            hi = np.minimum(ha, hb)
            if (hi - lo <= 0.5).any():
                continue
            def inside_box(x, H):
                return (boxes[x.name][0] >= boxes[H.name][0] - 1).all() and (boxes[x.name][1] <= boxes[H.name][1] + 1).all()
            if (A_.part.hollow and inside_box(B_, A_)) or (B_.part.hollow and inside_box(A_, B_)):
                continue
            checked += 1
            oa = A.voxel_inside(A.inst_shells(A_), lo, hi, 2.0)
            if not oa.any():
                continue
            ob = A.voxel_inside(A.inst_shells(B_), lo, hi, 2.0)
            n = int((oa & ob).sum())
            if n > 2:
                interf.append(dict(a=A_.name, b=B_.name, overlap_mm3=n * 8))
    clear["part_interference"] = dict(pairs_checked=checked, voxel_mm=2.0, interferences=interf, pass_=len(interf) == 0,
                                      excluded="fasteners and cables (designed penetrations); contents inside the pod and sampler")
    res["clearances"] = clear

    # ---------------- stage / install levels --------------------------------
    res["levels_world_mm"] = {k: round(v, 1) for k, v in L.items()}
    res["levels_world_mm"]["water_low"] = W_LOW
    res["levels_world_mm"]["water_high"] = W_HIGH

    # ---------------- checks summary ------------------------------------------
    h = res["hydrostatics"]
    checks = OrderedDict([
        ("Reserve buoyancy >= 2.0", h["reserve_buoyancy_sf"] >= 2.0),
        ("Freeboard >= 100 mm", h["freeboard_mm"] >= 100),
        ("GM_T >= 0.15 m (IMO reference only)", h["GM_T_m"] >= 0.15),
        ("GZ positive to 60 deg", all(v > 0 for k, v in h["GZ_curve_mm"].items() if k != "0")),
        ("Pole SF (pinned) >= 2.0", res["pole"]["SF_pinned"] >= 2.0),
        ("Pole deflection <= span/200", res["pole"]["deflection_pinned_mm"] <= span * 1000 / 200),
        ("No jamming with rollers (mu 0.05)", res["carriage"]["rollers_mu_0_05"]["jam_margin"] > 1),
        ("No jamming even with seized rollers (mu 0.25)", res["carriage"]["seized_rollers_sliding_mu_0_25"]["jam_margin"] > 1),
        ("Float lag under full design load <= 30 mm", res["carriage"]["rollers_mu_0_05"]["float_lag_mm"] <= 30),
        ("Weathervane stable (CLR aft of pole)", res["hydrodynamics"]["weathervane_stable"]),
        ("Pole corridor clearance >= 5 mm", clear["pole_corridor"]["pass_"]),
        ("No float/fixed clash over 2 m travel", clear["float_vs_fixed_over_travel"]["pass_"]),
        ("Only rub rails can touch the pier", clear["yaw_contact"]["pass_"]),
        ("No part-to-part interference", clear["part_interference"]["pass_"]),
    ])
    res["checks"] = checks

    # ---------------- BOM ------------------------------------------------------
    allinst = finst + ginst
    allparts = OrderedDict()
    for i in allinst:
        allparts.setdefault(i.part.key, i.part)
    qty = Counter(i.part.key for i in allinst)
    bom = []
    for k, p in sorted(allparts.items(), key=lambda kv: kv[1].pid):
        bom.append(OrderedDict(part_no=p.pid, description=p.name, qty=qty[k], material=MATERIALS[p.mat]["label"],
                               process=p.process, type=p.kind, mass_each_kg=round(p.mass_kg(), 3),
                               mass_basis=p.mass_basis(), cad_file=f"{p.pid}_{_fname(p.name)}.step",
                               unit_cost_inr="TO QUOTE", note=p.note))
    with open(os.path.join(ROOT, "cad", "BOM_R3.csv"), "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(bom[0].keys()))
        wri.writeheader()
        wri.writerows(bom)
    res["mass_table"] = [dict(instance=r["instance"], part_no=r["pid"], kg=round(r["kg"], 3), basis=r["basis"],
                              group=r["group"]) for r in rows]
    with open(os.path.join(OUT_CHK, "design_checks.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, default=_json)
    print_summary(res)
    print(f"[analysis] {time.time() - t0:.1f}s")

    # ---------------- exports ------------------------------------------------
    if "--no-export" in sys.argv:
        return res
    export_all(fparts, finst, gparts, ginst, eparts, einst, pivots, L, draft, res)
    print(f"[done] {time.time() - t0:.1f}s")
    return res


def _json(o):
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def _fname(s):
    keep = "".join(c if c.isalnum() else "_" for c in s)
    while "__" in keep:
        keep = keep.replace("__", "_")
    return keep.strip("_")[:48]


def print_summary(res):
    h, p, c = res["hydrostatics"], res["pole"], res["carriage"]
    print(f"mass {res['mass']['total_kg']} kg  CG {res['mass']['cg_mm']}")
    print(f"draft {h['draft_mm']} mm  freeboard {h['freeboard_mm']} mm  reserve {h['reserve_buoyancy_sf']}x  "
          f"GM_T {h['GM_T_m']} m  GM_L {h['GM_L_m']} m  LCB {h['LCB_mm']} LCG {h['LCG_mm']} LCF {h['LCF_from_pole_mm']}")
    print(f"trim moment {h['trim_moment_Nm']} N.m  free trim {h['free_trim_if_detached_deg']} deg  GZmax {h['GZ_max_mm']} mm @ {h['angle_of_GZ_max_deg']}")
    print(f"frontal {res['hydrodynamics']['frontal_area_m2']} m2  drag {res['hydrodynamics']['float_drag_N']} N  "
          f"CLR x {res['hydrodynamics']['centre_of_lateral_resistance_x_mm']}")
    print(f"pole span {p['bracket_span_mm']}  stress {p['stress_pinned_MPa']}/{p['stress_fixed_MPa']} MPa  SF {p['SF_pinned']}/{p['SF_fixed']}  defl {p['deflection_pinned_mm']}")
    print(f"carriage e {c['eccentricity_LCF_mm']} mm  rollers {c['rollers_mu_0_05']}  seized {c['seized_rollers_sliding_mu_0_25']['jam_margin']}")
    cl = res["clearances"]
    print("corridor", cl["pole_corridor"]["closest_parts"][:3], "roller r", cl["pole_corridor"]["roller_contact_radius_mm"])
    print("float vs fixed", cl["float_vs_fixed_over_travel"]["conflicts"][:6])
    print("yaw", cl["yaw_contact"])
    print("interference", cl["part_interference"]["pairs_checked"], cl["part_interference"]["interferences"][:12])
    for k, v in res["checks"].items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")


# ---------------------------------------------------------------------------
# exports
# ---------------------------------------------------------------------------
def export_all(fparts, finst, gparts, ginst, eparts, einst, pivots, L, draft, res):
    t0 = time.time()
    allparts = OrderedDict()
    for i in finst + ginst:
        allparts.setdefault(i.part.key, i.part)
    # per-part STEP + STL (local frame)
    for k, p in allparts.items():
        base = os.path.join(OUT_PARTS, f"{p.pid}_{_fname(p.name)}")
        X.write_stl(base + ".stl", p.shells, p.name)
        X.write_step_part(base + ".step", p.pid, p.name, p.shells, MATERIALS[p.mat]["color"], p.desc)
    print(f"[export] {len(allparts)} parts -> STEP + STL  ({time.time() - t0:.1f}s)")

    # float instance matrices with the hinge groups closed
    def placed(i, keel):
        return T_(0, 0, keel) @ i.M if i.group not in ("guide", "env") else i.M

    for stage, keel in (("Low", L["keel_low"]), ("Mid", L["keel_mid"]), ("High", L["keel_high"])):
        specs = {}
        instances = []
        for i in finst + ginst:
            specs.setdefault(i.part.key, dict(pid=i.part.pid, name=i.part.name, shells=i.part.shells,
                                              rgb=MATERIALS[i.part.mat]["color"], desc=i.part.desc))
            instances.append((i.part.key, placed(i, keel), i.name))
        X.write_step_assembly(os.path.join(OUT_ASM, f"AquaSentinel_R3_Assembly_{stage}Water.step"),
                              f"AquaSentinel_R3_{stage}Water", specs, instances)
        shells = []
        for i in finst + ginst:
            shells += [s.transformed(placed(i, keel)) for s in i.part.shells]
        X.write_stl(os.path.join(OUT_ASM, f"AquaSentinel_R3_Assembly_{stage}Water.stl"), shells, f"assembly {stage}")
    print(f"[export] assemblies ({time.time() - t0:.1f}s)")

    # GLB scene
    w = X.GLBWriter()
    for name, spec in MATERIALS.items():
        w.material(name, spec)

    def node_for(i, M):
        mi = w.material(i.part.mat, MATERIALS[i.part.mat])
        mesh = w.mesh(i.part.key, i.part.shells, mi)
        ex = dict(pid=i.part.pid, part=i.part.name, label=i.label, desc=i.part.desc, process=i.part.process,
                  material=MATERIALS[i.part.mat]["label"], kg=round(i.part.mass_kg(), 3), kind=i.part.kind,
                  step=i.step, explode=[round(float(v), 1) for v in i.explode], group=i.group)
        return w.node(i.name, M, mesh, extras=ex)

    env_nodes = [node_for(i, i.M) for i in einst]
    guide_nodes = [node_for(i, i.M) for i in ginst]
    float_children = []
    piv_nodes = {}
    for gname, pv in pivots.items():
        o = np.array(pv["origin"], float)
        kids = [node_for(i, T_(*(-o)) @ i.M) for i in finst if i.group == gname]
        piv_nodes[gname] = w.node(f"PIVOT_{gname}", T_(*o), children=kids,
                                  extras=dict(pivot=gname, axis=list(pv["axis"]), open_deg=pv["open_deg"],
                                              lift=pv.get("lift", 0.0), origin=o.tolist()))
    for i in finst:
        if i.group == "float":
            float_children.append(node_for(i, i.M))
    float_children += list(piv_nodes.values())
    float_node = w.node("FLOAT", T_(0, 0, L["keel_mid"]), children=float_children,
                        extras=dict(keel_low=L["keel_low"], keel_high=L["keel_high"], keel_mid=L["keel_mid"], draft=draft))
    env_node = w.node("ENV", None, children=env_nodes)
    guide_node = w.node("GUIDE", None, children=guide_nodes)
    root_M = np.diag([0.001, 0.001, 0.001, 1.0]) @ g.Rx(-90)
    root = w.node("AquaSentinel_R3", root_M, children=[env_node, guide_node, float_node])
    meta = dict(steps=[dict(step=k, title=v[0], caption=v[1]) for k, v in STEPS.items()],
                levels=res["levels_world_mm"], draft=draft, units="mm, Z-up model under a Y-up root",
                checks={k: bool(v) for k, v in res["checks"].items()},
                key_numbers=dict(mass_kg=res["mass"]["total_kg"], draft_mm=res["hydrostatics"]["draft_mm"],
                                 freeboard_mm=res["hydrostatics"]["freeboard_mm"],
                                 reserve=res["hydrostatics"]["reserve_buoyancy_sf"], gm_t=res["hydrostatics"]["GM_T_m"],
                                 pole_sf=res["pole"]["SF_pinned"], jam=res["carriage"]["rollers_mu_0_05"]["jam_margin"]))
    size = w.write(os.path.join(OUT_ASM, "AquaSentinel_R3.glb"), [root], meta)
    print(f"[export] GLB {size / 1e6:.1f} MB ({time.time() - t0:.1f}s)")


def T_(x, y, z):
    return g.T(x, y, z)


if __name__ == "__main__":
    main()
