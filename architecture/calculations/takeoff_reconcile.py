"""Reconcile the hand take-off (data/quantity_takeoff.csv) with IFC-derived quantities and re-run embodied carbon.

Finding C-01: the hand take-off assumed 4,200 m2 of CLT floor; the geometry in design-brief.md gives 2,880 m2.
Writes data/quantity_takeoff_v0.2_ifc.csv (hand rows kept for glass, copper, steel, rebar; IFC rows for frame, floors, cores).
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "bim"))
import quickcheck as q  # noqa: E402
import make_ifc  # noqa: E402


def reconcile(tmp_ifc: Path) -> dict:
    res = make_ifc.build(tmp_ifc)
    vol = res["volume_by_material_m3"]
    rows = list(csv.DictReader(open(ROOT / "data" / "quantity_takeoff.csv", newline="")))
    new = []
    for r in rows:
        if r["element"] == "Floor deck CLT 150 mm":
            r = dict(r, quantity=f"{vol['CLT 5-ply']:.1f}", note="from IFC: 3 x 960 m2 x 0.15 m (hall void removed)")
        elif r["element"] == "Glulam beams and columns":
            r = dict(r, quantity=f"{vol['Glulam GL24h']:.1f}", note="from IFC with PLACEHOLDER sections [A]")
        elif r["element"] == "Core walls and slabs":
            r = dict(r, quantity=f"{vol['Concrete C40/50']:.1f}", note="from IFC: two 8x8 m box cores, 0.4 m walls, 0.2 m slabs")
        new.append(r)
    out = ROOT / "data" / "quantity_takeoff_v0.2_ifc.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(new[0].keys())); w.writeheader(); w.writerows(new)
    old = q.embodied_carbon(); upd = q.embodied_carbon(out)
    return {"old": old, "new": upd, "gfa_model": res["gfa_m2"]}


if __name__ == "__main__":
    r = reconcile(ROOT / "bim" / "chimera-pavilion-structure.ifc")
    for tag, gfa in (("v0.1 hand take-off", 4188), ("v0.2 IFC take-off ", 4188), ("v0.2 IFC take-off ", r["gfa_model"])):
        d = r["old"] if tag.startswith("v0.1") else r["new"]
        print(f"{tag}: A1-A3 {d['low_t']:.0f}-{d['high_t']:.0f} tCO2e = {q.per_m2(d['low_t'], gfa):.0f}-{q.per_m2(d['high_t'], gfa):.0f} kgCO2e/m2 on {gfa:.0f} m2; "
              f"biogenic {d['biogenic_t']:.0f} t")
