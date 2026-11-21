"""Apply generator mass rules (shell / catalogue kg) as SOLIDWORKS mass overrides on the native parts."""
import os, sys, json, pythoncom, win32com.client
from win32com.client import VARIANT, gencache
mod = gencache.EnsureModule("{83A33D31-27C5-11CE-BFD4-00400513BB57}", 0, 34, 0)
sw = win32com.client.Dispatch("SldWorks.Application")
D = r"C:\Users\dell\OneDrive\Desktop\AquaSentinel\04_R3_FULL_SIZE_DESIGN\03b_SOLIDWORKS_2026_NATIVE"
G = json.load(open("gen_masses.json"))["parts"]
files = {f.split("_")[0]: f for f in os.listdir(D) if f.endswith(".SLDPRT")}
only = sys.argv[1:]
e = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0); w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
NOTH = VARIANT(pythoncom.VT_DISPATCH, None)
T = lambda cls, o: cls(o._oleobj_ if hasattr(o, "_oleobj_") else o)
for pid, g in sorted(G.items()):
    if g["rule"] == "solid" or (only and pid not in only):
        continue
    d = sw.OpenDoc6(os.path.join(D, files[pid]), 1, 1, "", e, w)
    ext = d.Extension
    mp = T(mod.IMassProperty2, ext.CreateMassProperty2)
    before = mp.Mass
    oo = T(mod.IMassPropertyOverrideOptions, mp.GetOverrideOptions())
    oo.OverrideMass = True
    oo.SetOverrideMassValue(max(g["kg"], 1e-4))
    ok = mp.SetOverrideOptions(oo, 1, NOTH)
    cpm = ext.CustomPropertyManager("")
    cpm.Add3("Mass_basis", 30, g["basis"], 2)
    d.ForceRebuild3(False)
    after = T(mod.IMassProperty2, ext.CreateMassProperty2).Mass
    ext.SaveAs3(os.path.join(D, files[pid]), 0, 1, NOTH, NOTH, e, w)
    print(pid, g["rule"], round(before, 3), "->", round(after, 3), "target", round(g["kg"], 3), "ok", ok, "save", e.value)
    sw.CloseDoc(d.GetTitle)
