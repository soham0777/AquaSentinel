import os, shutil, sys
import pythoncom, win32com.client
from win32com.client import VARIANT
sw = win32com.client.Dispatch("SldWorks.Application")
SRC = r"C:\Users\dell\OneDrive\Desktop\AquaSentinel\04_R3_FULL_SIZE_DESIGN\03_SOLIDWORKS_2026_assembly_for_manual"
DST = r"C:\Users\dell\OneDrive\Desktop\AquaSentinel\04_R3_FULL_SIZE_DESIGN\03b_SOLIDWORKS_2026_NATIVE"
A0 = os.path.join(SRC, "AquaSentinel_R3_Assembly.SLDASM")
A1 = os.path.join(DST, "AquaSentinel_R3_Assembly_NATIVE.SLDASM")
print("open docs:", [d.GetTitle for d in (sw.GetDocuments or [])])
shutil.copy2(A0, A1)
deps = sw.GetDocumentDependencies2(A1, False, True, False)
deps = list(deps) if deps else []
print(len(deps) // 2, "direct references")
n = 0
for i in range(0, len(deps), 2):
    old = deps[i + 1]
    new = os.path.join(DST, os.path.basename(old))
    if os.path.exists(new):
        ok = sw.ReplaceReferencedDocument(A1, old, new)
        n += bool(ok)
    else:
        print("no native file for", old)
print("replaced", n)
e = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
d = sw.OpenDoc6(A1, 2, 1, "", e, w)
print("open err", e.value, w.value)
comps = d.GetComponents(False)
paths = {}
for c in comps:
    p = c.GetPathName
    paths[os.path.dirname(p)] = paths.get(os.path.dirname(p), 0) + 1
print(len(comps), "components;", paths)
d.ForceRebuild3(False)
cpm = d.Extension.CustomPropertyManager("")
cpm.Add3("Description", 30, "AquaSentinel R3 full-size float + guide, native feature-based SOLIDWORKS parts", 2)
d.Extension.SaveAs3(A1, 0, 1, VARIANT(pythoncom.VT_DISPATCH, None), VARIANT(pythoncom.VT_DISPATCH, None), e, w)
print("save err", e.value)
