"""Run the R3 generator twice: once with the original kernel (to get the solved draft), once with ngeom
(to capture exact feature descriptions). Writes prims.pkl."""
import os, sys, pickle, importlib, importlib.util
SRC = r"E:\AquaSentinel\.claude\worktrees\moisture-sensor-solidworks-29a086\09_SOURCE_CODE_AND_WEBSITE\mechanical\src"
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["R3_GEOM_ORIG"] = os.path.join(SRC, "geom.py")
sys.path.insert(0, SRC)
import parts as P0, analysis as A, geom as G0
fparts, finst, pivots = P0.build_float()
RHO_W = A.RHO_W
rows, Mtot, CG = A.mass_properties(finst)
draft = A.solve_waterplane(A.tri_soup(finst), Mtot / RHO_W * 1e9)
print("draft", draft)
# swap in the native kernel and rebuild
for m in ("parts", "geom"):
    sys.modules.pop(m, None)
spec = importlib.util.spec_from_file_location("geom", os.path.join(HERE, "ngeom.py"))
NG = importlib.util.module_from_spec(spec); sys.modules["geom"] = NG; spec.loader.exec_module(NG)
import parts as P
P.prism, P.hollow_prism, P.window_plate, P.revolve_partial = NG.prism, NG.hollow_prism, NG.window_plate, NG.revolve_partial
fp, fi, _ = P.build_float()
gp, gi, L = P.build_guide(draft)
out = {}
for p in list(fp.values()) + list(gp.values()):
    out[p.pid] = dict(key=p.key, name=p.name, mat=p.mat, desc=p.desc, process=p.process, kind=p.kind,
                      prims=[(q.kind, q.data, q.M) for q in p.shells])
pickle.dump(dict(parts=out, draft=draft), open(os.path.join(HERE, "prims.pkl"), "wb"))
from collections import Counter
print(len(out), "parts")
for pid in sorted(out):
    print(pid, out[pid]["name"][:40], dict(Counter(k for k, _, _ in out[pid]["prims"])))
