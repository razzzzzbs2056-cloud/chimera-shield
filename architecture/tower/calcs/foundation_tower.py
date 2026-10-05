"""Foundation-level load summary and parametric option screening, 30-storey tower (Division 6).

CONCEPT ONLY. No soil data exists: every soil quantity is a PARAMETER, never a capacity.
Run: python architecture/tower/calcs/foundation_tower.py  -> architecture/tower/data/foundation.json
Units: m, kN, kPa, MN.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAMMA_W = 9.81  # kN/m3
GAMMA_RC = 25.0  # kN/m3 (same as structure.json)
GF_EC = (1.35, 1.5)

ASSUME = {
    "basements": 2, "basement_h_m": 3.3,
    "tower_footprint_m": (30.0, 24.0),
    "enlarged_raft_m": (36.0, 30.0),  # 3 m projection each side; site boundary UNKNOWN
    "raft_thickness_m": 2.0,  # ASSUMPTION, not designed (core punching/shear unknown)
    "basement_slab_floor_kPa": 10.0,  # per basement level incl. slab, columns share, SDL; ASSUMPTION
    "basement_wall_t_m": 0.4,  # perimeter retaining wall, ASSUMPTION
    "soil_unit_weights_kN_m3": [16.0, 18.0, 20.0],  # PARAMETERS
    "pile_working_MN": [3.0, 5.0, 8.0, 12.0],  # PARAMETRIC, not capacities
    "raft_share_of_load": [0.0, 0.25, 0.5],  # piled-raft parameter
}


def load_structure():
    return json.loads((ROOT / "data" / "structure.json").read_text())


def basement_weight_kN(size, a=ASSUME):
    L, B = size
    area = L * B
    raft = area * a["raft_thickness_m"] * GAMMA_RC
    floors = a["basements"] * a["basement_slab_floor_kPa"] * area
    walls = 2 * (L + B) * a["basements"] * a["basement_h_m"] * a["basement_wall_t_m"] * GAMMA_RC
    return {"raft": raft, "floors": floors, "walls": walls, "total": raft + floors + walls}


def founding_depth_m(a=ASSUME):
    return a["basements"] * a["basement_h_m"] + a["raft_thickness_m"]


def pressure_kPa(load_kN, area_m2):
    return load_kN / area_m2


def piles_needed(load_MN, pw_MN):
    return math.ceil(load_MN / pw_MN)


def pile_table(load_MN, caps=None):
    caps = caps or ASSUME["pile_working_MN"]
    return [{"Pw_MN": c, "n_piles": piles_needed(load_MN, c)} for c in caps]


def edge_pressures(N_kN, M_kNm, L, B):
    """q = N/A +- M/Z, Z = B L^2/6 (M acting about axis parallel to B, i.e. bending along L).
    No-tension limit: e = M/N <= L/6."""
    A = L * B
    Z = B * L * L / 6.0
    return {"q_avg": N_kN / A, "q_max": N_kN / A + M_kNm / Z, "q_min": N_kN / A - M_kNm / Z,
            "e_m": M_kNm / N_kN, "L_over_6": L / 6.0, "Z_m3": Z}


def run():
    s = load_structure()
    t = s["gravity_totals_at_ground_kN"]
    G, Q = t["G"], t["Q"]
    core_G, core_Q = s["core"]["G_base_kN"], s["core"]["Q_base_kN"]
    col_G = sum(c["G_base_kN"] for c in s["columns"].values())
    col_Q = sum(c["Q_base_kN"] for c in s["columns"].values())
    col_N = [(k, c["G_base_kN"] + c["Q_base_kN"]) for k, c in s["columns"].items()]
    service = G + Q
    factored = GF_EC[0] * G + GF_EC[1] * Q
    out = {"_meta": {"script": "architecture/tower/calcs/foundation_tower.py",
                     "status": "CONCEPT. Soil parameters are UNKNOWN; every soil-dependent figure is parametric.",
                     "units": "kN, kPa, MN, m"},
           "assumptions": {k: v for k, v in ASSUME.items()}}
    out["loads"] = {"G_kN": G, "Q_kN": Q, "service_GQ_kN": service, "factored_EC_kN": factored,
                    "factors_EC": GF_EC, "core_G_kN": core_G, "core_Q_kN": core_Q,
                    "columns_G_kN": col_G, "columns_Q_kN": col_Q,
                    "core_share_service": (core_G + core_Q) / service,
                    "core_N_Ed_kN": s["core"]["N_Ed_kN"],
                    "max_column_service_kN": max(v for _, v in col_N),
                    "max_column": max(col_N, key=lambda x: x[1])[0]}
    rafts = {}
    D = founding_depth_m()
    for name, size in (("tower_footprint", ASSUME["tower_footprint_m"]), ("enlarged", ASSUME["enlarged_raft_m"])):
        area = size[0] * size[1]
        bw = basement_weight_kN(size)
        total = service + bw["total"]
        gross = pressure_kPa(total, area)
        net = {f"gamma_{g:g}": gross - g * D for g in ASSUME["soil_unit_weights_kN_m3"]}
        rafts[name] = {"size_m": size, "area_m2": area, "basement_weight_kN": bw,
                       "total_service_kN": total, "gross_service_kPa": gross,
                       "superstructure_only_kPa": pressure_kPa(service, area),
                       "factored_superstructure_kPa": pressure_kPa(factored, area),
                       "founding_depth_m": D,
                       "net_after_unloading_kPa_by_gamma": net,
                       "Z_long_m3": size[1] * size[0] ** 2 / 6, "Z_short_m3": size[0] * size[1] ** 2 / 6}
    out["raft_pressures"] = rafts
    core_area = 12.0 * 8.0
    core_service = core_G + core_Q
    rest_area = 720.0 - core_area
    out["concentration"] = {
        "core_area_m2": core_area, "core_service_kN": core_service,
        "core_pressure_on_core_footprint_kPa": core_service / core_area,
        "columns_service_kN": col_G + col_Q,
        "columns_pressure_on_rest_kPa": (col_G + col_Q) / rest_area,
        "ratio_core_to_rest": (core_service / core_area) / ((col_G + col_Q) / rest_area)}
    tower_total = rafts["tower_footprint"]["total_service_kN"] / 1000
    enl_total = rafts["enlarged"]["total_service_kN"] / 1000
    # pile cases use superstructure service + basement weight (piles carry the net building load before uplift relief)
    out["pile_counts_parametric"] = {
        "note": "PARAMETRIC working capacity per pile; NOT capacities. n = ceil(P / Pw). Group efficiency, negative skin friction, "
                "overturning and seismic extra loads NOT included.",
        "total_tower_footprint_MN": tower_total, "total_enlarged_MN": enl_total,
        "superstructure_service_MN": service / 1000,
        "core_service_MN": core_service / 1000, "columns_service_MN": (col_G + col_Q) / 1000,
        "all_load_tower_raft": pile_table(tower_total),
        "all_load_enlarged_raft": pile_table(enl_total),
        "core_only": pile_table(core_service / 1000),
        "piled_raft_by_raft_share": {f"raft_carries_{int(f*100)}pct": pile_table((1 - f) * tower_total)
                                      for f in ASSUME["raft_share_of_load"]},
        "isolated_footing_check": [{"column": k, "service_MN": v / 1000, "piles_at_Pw": pile_table(v / 1000)}
                                   for k, v in col_N if k in (out["loads"]["max_column"],)]}
    # uplift: flotation; water head above basement base is a PARAMETER
    uplift = []
    area = 720.0
    resist = rafts["tower_footprint"]["basement_weight_kN"]["total"]
    for h in (0.0, 2.0, 4.0, 6.0, D):
        U = GAMMA_W * h * area
        uplift.append({"head_above_base_m": h, "uplift_kN": U, "uplift_kPa": GAMMA_W * h,
                       "basement_only_weight_kN_stage0": resist,
                       "stage0_ratio_weight_over_uplift": (resist / U) if U else None,
                       "with_tower_ratio": ((resist + service) / U) if U else None})
    out["uplift_parametric"] = {"note": "Stage 0 = basement structure only, no tower; groundwater head UNKNOWN. "
                                        "Code partial factors (verify) not applied.", "cases": uplift}
    out["overturning"] = {"M_wind_kNm": None, "M_seismic_kNm": None,
                          "status": "PENDING from wind and earthquake divisions (placeholder)",
                          "formula": "q_max,min = N/A +- M/Z; Z = B*L^2/6; no-tension if e = M/N <= L/6",
                          "sensitivity_per_100MNm_kPa": {n: 100e3 / r["Z_long_m3"] for n, r in rafts.items()},
                          "sensitivity_note": "bending along the 30 m side (Z_long); short side in raft_pressures Z_short_m3"}
    return out


if __name__ == "__main__":
    r = run()
    (ROOT / "data" / "foundation.json").write_text(json.dumps(r, indent=1))
    print(json.dumps({k: r[k] for k in ("loads", "concentration")}, indent=1))
    for n, v in r["raft_pressures"].items():
        print(n, round(v["gross_service_kPa"]), v["net_after_unloading_kPa_by_gamma"])
    for k in ("all_load_tower_raft", "all_load_enlarged_raft", "core_only"):
        print(k, r["pile_counts_parametric"][k])
    print(r["pile_counts_parametric"]["piled_raft_by_raft_share"])
    print(r["pile_counts_parametric"]["total_tower_footprint_MN"], r["pile_counts_parametric"]["total_enlarged_MN"])
    print(r["overturning"]["sensitivity_per_100MNm_kPa"])
    print(r["uplift_parametric"]["cases"][2])
