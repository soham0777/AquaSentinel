import os, sys, json
SRC = r"E:\AquaSentinel\.claude\worktrees\moisture-sensor-solidworks-29a086\09_SOURCE_CODE_AND_WEBSITE\mechanical\src"
sys.path.insert(0, SRC)
import parts as P0, analysis as A
fp, fi, _ = P0.build_float()
rows, Mtot, CG = A.mass_properties(fi)
draft = A.solve_waterplane(A.tri_soup(fi), Mtot / A.RHO_W * 1e9)
gp, gi, L = P0.build_guide(draft)
out = {}
for p in list(fp.values()) + list(gp.values()):
    out[p.pid] = dict(kg=p.mass_kg(), rule=p.mass_rule, basis=p.mass_basis(), hollow=p.hollow)
cnt = {}
for i in fi: cnt[i.part.pid] = cnt.get(i.part.pid, 0) + 1
json.dump(dict(parts=out, float_total=Mtot, float_count=cnt), open("gen_masses.json", "w"), indent=1)
print("float total", round(Mtot, 2), "kg")
print({k: (round(v["kg"], 3), v["rule"]) for k, v in out.items() if v["rule"] != "solid" or v["hollow"]})
