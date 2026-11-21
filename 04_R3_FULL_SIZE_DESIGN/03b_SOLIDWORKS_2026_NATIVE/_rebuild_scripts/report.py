import os, json, csv, pythoncom, win32com.client
from win32com.client import VARIANT
sw = win32com.client.Dispatch("SldWorks.Application")
D = r"C:\Users\dell\OneDrive\Desktop\AquaSentinel\04_R3_FULL_SIZE_DESIGN\03b_SOLIDWORKS_2026_NATIVE"
rep = {x["pid"]: x for x in json.load(open(os.path.join(D, "_build_report.json")))}
e = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0); w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
rows = []
for pid in sorted(rep):
    x = rep[pid]
    d = sw.OpenDoc6(os.path.join(D, x["file"]), 1, 1 | 2, "", e, w)
    mp = d.Extension.CreateMassProperty
    mat = (d.MaterialIdName or "").split("|")
    nfeat = 0; f = d.FirstFeature
    while f is not None:
        if f.GetTypeName2 in ("Extrusion", "Revolution", "Blend", "Sweep", "Fillet", "MoveCopyBody", "BodyOperation", "ProfileFeature", "3DProfileFeature", "RefPlane"):
            nfeat += 1
        f = f.GetNextFeature
    n, r = x["native"], x["ref"] or {}
    nb, rb = n["bbox_mm"], r.get("bbox_mm") or [0] * 6
    rows.append(dict(PartNo=pid, File=x["file"], Material=mat[1] if len(mat) > 1 else "", Mass_kg=round(mp.Mass, 3),
                     Volume_cm3=round(mp.Volume * 1e6, 2), Original_volume_cm3=r.get("volume_cm3"),
                     Faces_native=n["faces"], Faces_original=r.get("faces"), Features=nfeat,
                     Max_bbox_diff_mm=round(max(abs(a - b) for a, b in zip(nb, rb)), 1), Bodies=n["bodies"]))
    sw.CloseDoc(d.GetTitle)
with open(os.path.join(D, "_Native_rebuild_check.csv"), "w", newline="", encoding="utf-8") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
print("parts", len(rows), "no material:", [r["PartNo"] for r in rows if not r["Material"]])
print("faces", sum(r["Faces_native"] for r in rows), "vs", sum(r["Faces_original"] or 0 for r in rows))
print("features", sum(r["Features"] for r in rows))
