"""Build the Sydney tower 3D page from the divisions' data (single source: architecture/tower/data/*.json).

Run:  python architecture/tower/build_tower_page.py   ->  architecture/tower/tower-sydney-3d.html
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "architecture" / "tools"))
from validate_return import validate  # noqa: E402


def load(name):
    p = HERE / "data" / f"{name}.json"
    return json.loads(p.read_text()) if p.exists() else None


def status():
    rows = []
    for div, title in [("architecture", "Architecture (options A-E)"), ("structure", "Structure"), ("verification-structure", "Independent verification"),
                       ("seismic", "Earthquake (OpenSees)"), ("wind", "Wind"), ("foundation", "Foundations"), ("geotechnical", "Geotechnical"), ("codes", "Codes")]:
        p = HERE / "returns" / f"{div}.md"
        if not p.exists():
            rows.append({"div": title, "state": "running", "valid": None}); continue
        errs = validate(p.read_text())
        rows.append({"div": title, "state": "returned", "valid": not errs})
    return rows


def main():
    s, a, f, c = load("structure"), load("architecture"), load("foundation"), load("codes")
    seis, wind = load("seismic"), load("wind")
    B = json.loads((HERE / "verification" / "B_structure.json").read_text()) if (HERE / "verification" / "B_structure.json").exists() else None
    A = json.loads((HERE / "verification" / "A_structure.json").read_text()) if (HERE / "verification" / "A_structure.json").exists() else None
    cmp = None
    if A and B:
        sys.path.insert(0, str(ROOT / "architecture" / "tools")); from verify_compare import compare
        cmp = compare(A, B, json.loads((HERE / "verification" / "tol_structure.json").read_text()))["decision"]
    data = {
        "basis": json.loads((HERE / "basis.json").read_text()),
        "structure": {"columns": {k: {"x": v["x_m"], "y": v["y_m"], "zones": v["size_by_zone_m"], "N_Ed_kN": v["N_Ed_kN"]} for k, v in s["columns"].items()},
                      "core_box": s["core"]["box_m"], "core_t": s["core"]["wall_t_zones_m"], "slab_t": s["slab_thickness_m"],
                      "z": s["levels"]["z_m"], "W_kN": s["W_kN"], "T1": {"X": s["lateral_cracked"]["X"]["T1_s"], "Y": s["lateral_cracked"]["Y"]["T1_s"]},
                      "G": s["gravity_totals_at_ground_kN"]["G"], "Q": s["gravity_totals_at_ground_kN"]["Q"]},
        "floor": a["typical_floor"], "options": {k: {"objective": v.get("objective", ""), "plate": v.get("plate"), "gfa": v.get("gfa_floor_m2"), "nsa": v.get("nsa_floor_m2"),
                                                       "eff": v.get("efficiency_nsa_gfa"), "mix": v.get("mix")} for k, v in a["options"].items()},
        "reference_option": a.get("reference_option"),
        "foundation": f, "codes_result": (c or {}).get("overall_result"), "verification": cmp,
        "seismic": seis, "wind": wind, "status": status()
    }
    html = (HERE / "tower-sydney-3d.template.html").read_text().replace("/*__DATA__*/{}", json.dumps(data, ensure_ascii=False, default=float).replace("</", "<\\/"))
    out = HERE / "tower-sydney-3d.html"; out.write_text(html)
    return out


if __name__ == "__main__":
    print(main())
