"""Division 2 (Architecture): concept options for the 30-storey residential tower.

Produces architecture/tower/data/architecture.json with keys
  options            name -> {description, geometry inputs, metrics (flat, so tools/pareto.py can read them)}
  objective_senses   metric -> "min" / "max" (the metrics an optimiser should use)
  typical_floor      list of {name, type, x0, y0, x1, y1, area_m2} for the reference option (x east 0..30, y north 0..24)
  reference_option   name of the option closest to basis.json
  lift_check         concept lift estimate per option (method below)
  evidence           metric -> evidence tag (PROTOCOL.md section 1)

Proxy definitions (all per typical residential floor unless stated; units m, m2, s)
  GFA_floor         = plate area measured to the outer face of the envelope                      [CALCULATION]
  core_area         = Lc * Wc                                                                     [CALCULATION]
  corridor_area     = ring corridor of width w around the core = (Lc+2w)(Wc+2w) - Lc*Wc          [CALCULATION]
  NSA_floor         = GFA_floor - core_area - corridor_area (envelope, party walls, columns and
                      shafts inside apartments NOT deducted; this is an upper-bound proxy)         [CALCULATION]
  efficiency        = NSA_floor / GFA_floor                                                       [CALCULATION]
  facade_per_gfa    = perimeter * typical floor-to-floor / GFA_floor  (m2 facade per m2 GFA)       [CALCULATION]
  max_depth_facade_to_core = max over plate axes of (plate dim - core dim) / 2  (daylight proxy)  [CALCULATION]
  apartment_depth_max      = max_depth_facade_to_core - w (facade to corridor wall)                [CALCULATION]
  core_area_ratio   = core_area / GFA_floor                                                       [CALCULATION]
  slenderness       = height to roof slab / least plate dimension                                 [CALCULATION]
  cost_proxy_index  = [(c_s * GFA + K_FC * facade_area) / NSA] / same for reference option        [CALCULATION on JUDGMENT weights]
  carbon_proxy_index= [(e_s * GFA + K_FE * facade_area) / NSA] / same for reference option        [CALCULATION on JUDGMENT weights]
  identity_score    = 1..5 design judgement                                                       [JUDGMENT]
No currency and no kgCO2e: the cost and carbon divisions own those numbers and must replace these proxies.

Lift check (concept estimate; replace with a lift consultant's traffic analysis / simulation)
  Up-peak round trip, conventional single-entrance method:
    S   = N (1 - (1 - 1/N)^P)                    probable stops, N residential floors served, P passengers per trip
    RTT = 2 * rise / v + (S + 1) * t_stop + 2 P t_pass   (conservative: car assumed to travel to the top floor every trip)
    HC5 per lift = 300 P / RTT ;  lifts required = max(2, ceil(HC_target * population / HC5 per lift))
Run: python architecture/tower/calcs/architecture_options.py
"""
import json
import math
from itertools import combinations
from pathlib import Path

TOWER = Path(__file__).resolve().parents[1]
BASIS = json.loads((TOWER / "basis.json").read_text())
OUT = TOWER / "data" / "architecture.json"

G = BASIS["geometry"]
STOREYS = G["storeys_above_grade"]                 # 30 (FACT: brief)
RES_FLOORS = STOREYS - 1                           # ASSUMPTION: ground floor is lobby/amenity/retail (basis.json use)
H_GF = G["ground_floor_to_floor_m"]                # 4.5 ASSUMPTION (basis)
H_TYP = G["typical_floor_to_floor_m"]              # 3.1 ASSUMPTION (basis)
HEIGHT = H_GF + (STOREYS - 1) * H_TYP              # 94.4 m to roof slab
REF_PLATE = tuple(G["floor_plate_m"])              # (30, 24)

# Proxy weights: JUDGMENT, to be replaced by the cost and carbon divisions
K_FC = 1.5   # facade m2 relative to floor m2 in the cost proxy
K_FE = 0.5   # facade m2 relative to floor m2 in the carbon proxy

# Occupancy and lift assumptions: ASSUMPTION (verify against the jurisdiction's code and a lift consultant)
BEDROOMS = {"1B": 1, "2B": 2, "3B": 3}
PERSONS_PER_BEDROOM = 1.5
HC5_TARGET = 0.07          # 5-minute handling capacity as a fraction of population
CAR_RATED_PERSONS = 13     # about 1000 kg car
P_TRIP = 10                # passengers per up-peak trip (about 80 % of rated, rounded down)
SPEED = 2.5                # m/s
T_STOP = 10.0              # s lost per stop (accel/decel + door cycle)
T_PASS = 1.2               # s per passenger transfer

OPTIONS = {
    "A_cheapest": {
        "objective": "cheapest (lowest construction-cost proxy within the reference 30 x 24 m footprint)",
        "description": "Reference compact rectangle 30 x 24 m, central 12 x 8 m RC core, 1.5 m ring corridor, "
                       "8 apartments per floor, maximum repetition, regular 7.5 x 8 m column grid, flat slab.",
        "plate": {"shape": "rectangle", "L": 30.0, "W": 24.0},
        "core_m": [12.0, 8.0], "core_position": "central", "corridor_width_m": 1.5,
        "mix": {"1B": 2, "2B": 4, "3B": 2}, "dual_aspect_apartments": 4,
        "lifts_provided": 4, "stairs": 2,
        "structural_system_intent": "RC shear-wall core + RC columns on 7.5 x 8.0 m grid (x 0/7.5/15/22.5/30, y 0/8/16/24), RC flat slab",
        "cost_factor": 1.00, "carbon_factor": 1.00, "identity_score": 1,
    },
    "B_lowest_carbon": {
        "objective": "lowest embodied-carbon proxy",
        "description": "Same compact plate and core as A (form efficiency kept), but hybrid structure: RC core with "
                       "timber-concrete composite / CLT floors on glulam or steel beams; low glazing ratio.",
        "plate": {"shape": "rectangle", "L": 30.0, "W": 24.0},
        "core_m": [12.0, 8.0], "core_position": "central", "corridor_width_m": 1.5,
        "mix": {"1B": 2, "2B": 4, "3B": 2}, "dual_aspect_apartments": 4,
        "lifts_provided": 4, "stairs": 2,
        "structural_system_intent": "RC core + mass-timber/composite floors on 7.5 x 8.0 m grid with secondary beams; "
                                    "fire and code feasibility at 94 m UNKNOWN (jurisdiction)",
        "cost_factor": 1.15, "carbon_factor": 0.65, "identity_score": 3,
    },
    "C_max_nsa": {
        "objective": "maximum net saleable area",
        "description": "Enlarged 34 x 26 m plate (core dilution), 13 x 8 m core, 10 apartments per floor, "
                       "deeper units; exceeds the reference footprint (site fit UNKNOWN).",
        "plate": {"shape": "rectangle", "L": 34.0, "W": 26.0},
        "core_m": [13.0, 8.0], "core_position": "central", "corridor_width_m": 1.5,
        "mix": {"1B": 2, "2B": 6, "3B": 2}, "dual_aspect_apartments": 4,
        "lifts_provided": 4, "stairs": 2,
        "structural_system_intent": "RC core + RC columns, post-tensioned flat slab for spans up to about 10.5 m",
        "cost_factor": 1.03, "carbon_factor": 0.95, "identity_score": 1,
    },
    "D_best_daylight": {
        "objective": "best daylight (shallowest plan, highest dual-aspect share)",
        "description": "Shallow 27 x 21 m plate around the same 12 x 8 m core, 6 apartments per floor, "
                       "apartment depth at most 6.0 m, four corner dual-aspect units.",
        "plate": {"shape": "rectangle", "L": 27.0, "W": 21.0},
        "core_m": [12.0, 8.0], "core_position": "central", "corridor_width_m": 1.5,
        "mix": {"1B": 2, "2B": 4}, "dual_aspect_apartments": 4,
        "lifts_provided": 3, "stairs": 2,
        "structural_system_intent": "RC core + RC columns, flat slab spans 6.5-7.5 m; slenderness about 4.5 so wind/drift "
                                    "and core stiffness to be checked by structure",
        "cost_factor": 1.00, "carbon_factor": 1.00, "identity_score": 2,
    },
    "E_identity": {
        "objective": "strongest architectural identity",
        "description": "30 x 24 m plate with 4.5 m 45-degree chamfered corners (octagonal plan) wrapped by corner "
                       "balconies that rotate position every three floors, giving a carved, faceted silhouette.",
        "plate": {"shape": "chamfered_rectangle", "L": 30.0, "W": 24.0, "chamfer": 4.5},
        "core_m": [12.0, 8.0], "core_position": "central", "corridor_width_m": 1.5,
        "mix": {"1B": 2, "2B": 4, "3B": 2}, "dual_aspect_apartments": 4,
        "lifts_provided": 4, "stairs": 2,
        "structural_system_intent": "RC core + RC columns set back from chamfers, cantilevered balcony slabs with "
                                    "thermal breaks, RC flat slab",
        "cost_factor": 1.08, "carbon_factor": 1.05, "identity_score": 5,
    },
}
REFERENCE = "A_cheapest"

OBJECTIVE_SENSES = {
    "cost_proxy_index": "min",
    "carbon_proxy_index": "min",
    "nsa_total_m2": "max",
    "max_depth_facade_to_core_m": "min",
    "identity_score": "max",
}

EVIDENCE = {
    "gfa_floor_m2": "CALCULATION", "core_area_m2": "CALCULATION", "corridor_area_m2": "CALCULATION",
    "nsa_floor_m2": "CALCULATION", "efficiency_nsa_gfa": "CALCULATION", "perimeter_m": "CALCULATION",
    "facade_area_floor_m2": "CALCULATION", "facade_per_gfa": "CALCULATION",
    "max_depth_facade_to_core_m": "CALCULATION", "apartment_depth_max_m": "CALCULATION",
    "core_area_ratio": "CALCULATION", "apartments_total": "CALCULATION", "nsa_total_m2": "CALCULATION",
    "gfa_above_grade_m2": "CALCULATION", "dual_aspect_share": "CALCULATION (count is JUDGMENT for options without a drawn layout)",
    "slenderness_h_over_b": "CALCULATION", "height_to_roof_slab_m": "CALCULATION",
    "cost_proxy_index": "CALCULATION on JUDGMENT weights (cost division to replace)",
    "carbon_proxy_index": "CALCULATION on JUDGMENT weights (carbon division to replace)",
    "identity_score": "JUDGMENT", "mix": "JUDGMENT", "lifts_provided": "JUDGMENT informed by lift_check (CALCULATION)",
    "fits_reference_footprint": "CALCULATION (reference footprint itself is an ASSUMPTION; site UNKNOWN)",
}

# Reference typical floor (option A). x east 0..30, y north 0..24, metres.
TYPICAL_FLOOR = [
    # apartments
    ("A01 SW corner", "2B", 0.0, 0.0, 7.5, 9.0),
    ("A02 W", "1B", 0.0, 9.0, 7.5, 15.0),
    ("A03 NW corner", "2B", 0.0, 15.0, 7.5, 24.0),
    ("A04 N", "3B", 7.5, 17.5, 22.5, 24.0),
    ("A05 NE corner", "2B", 22.5, 15.0, 30.0, 24.0),
    ("A06 E", "1B", 22.5, 9.0, 30.0, 15.0),
    ("A07 SE corner", "2B", 22.5, 0.0, 30.0, 9.0),
    ("A08 S", "3B", 7.5, 0.0, 22.5, 6.5),
    # ring corridor (1.5 m)
    ("Corridor S", "corridor", 7.5, 6.5, 22.5, 8.0),
    ("Corridor N", "corridor", 7.5, 16.0, 22.5, 17.5),
    ("Corridor W", "corridor", 7.5, 8.0, 9.0, 16.0),
    ("Corridor E", "corridor", 21.0, 8.0, 22.5, 16.0),
    # core 12 x 8 (x 9..21, y 8..16)
    ("Stair 1", "stair", 9.0, 8.0, 14.5, 10.8),
    ("Lift 1", "lift", 14.5, 8.0, 17.0, 10.8),
    ("Lift 2 (firefighting candidate)", "lift", 17.0, 8.0, 19.5, 10.8),
    ("Riser 1", "riser", 19.5, 8.0, 21.0, 10.8),
    ("Lift lobby", "lobby", 9.0, 10.8, 21.0, 13.2),
    ("Lift 3", "lift", 9.0, 13.2, 11.5, 16.0),
    ("Lift 4", "lift", 11.5, 13.2, 14.0, 16.0),
    ("Riser 2", "riser", 14.0, 13.2, 15.5, 16.0),
    ("Stair 2", "stair", 15.5, 13.2, 21.0, 16.0),
]
APT_TYPES = set(BEDROOMS)
CORE_TYPES = {"stair", "lift", "riser", "lobby"}


def plate_area(p: dict) -> float:
    if p["shape"] == "rectangle":
        return p["L"] * p["W"]
    if p["shape"] == "chamfered_rectangle":
        return p["L"] * p["W"] - 2.0 * p["chamfer"] ** 2          # four triangles c^2/2
    raise ValueError(p["shape"])


def plate_perimeter(p: dict) -> float:
    if p["shape"] == "rectangle":
        return 2.0 * (p["L"] + p["W"])
    if p["shape"] == "chamfered_rectangle":
        c = p["chamfer"]
        return 2.0 * (p["L"] - 2 * c) + 2.0 * (p["W"] - 2 * c) + 4.0 * c * math.sqrt(2.0)
    raise ValueError(p["shape"])


def lift_check(pop_floor: float, lifts_provided: int) -> dict:
    n = RES_FLOORS
    rise = H_GF + (n - 1) * H_TYP                          # main terminal to top residential floor (91.3 m)
    s = n * (1.0 - (1.0 - 1.0 / n) ** P_TRIP)
    rtt = 2.0 * rise / SPEED + (s + 1.0) * T_STOP + 2.0 * P_TRIP * T_PASS
    hc_lift = 300.0 * P_TRIP / rtt
    population = pop_floor * n
    demand = HC5_TARGET * population
    required = max(2, math.ceil(demand / hc_lift))
    return {
        "label": "CALCULATION (concept estimate, not a traffic simulation)",
        "residential_floors_served": n, "rise_m": round(rise, 2), "probable_stops": round(s, 2),
        "round_trip_time_s": round(rtt, 2), "hc5_per_lift_persons": round(hc_lift, 2),
        "population_per_floor": pop_floor, "population_total": population,
        "demand_5min_persons": round(demand, 2), "lifts_required": required, "lifts_provided": lifts_provided,
        "interval_s": round(rtt / lifts_provided, 2),
        "hc5_provided_pct": round(100.0 * lifts_provided * hc_lift / population, 2),
        "pass": lifts_provided >= required,
    }


def raw_metrics(o: dict) -> dict:
    gfa = plate_area(o["plate"])
    lc, wc = o["core_m"]
    w = o["corridor_width_m"]
    core = lc * wc
    corridor = (lc + 2 * w) * (wc + 2 * w) - core
    nsa = gfa - core - corridor
    per = plate_perimeter(o["plate"])
    facade = per * H_TYP
    depth = max((o["plate"]["L"] - lc) / 2.0, (o["plate"]["W"] - wc) / 2.0)
    apts = sum(o["mix"].values())
    return {"gfa": gfa, "core": core, "corridor": corridor, "nsa": nsa, "per": per, "facade": facade,
            "depth": depth, "w": w, "apts": apts,
            "cost_raw": (o["cost_factor"] * gfa + K_FC * facade) / nsa,
            "carbon_raw": (o["carbon_factor"] * gfa + K_FE * facade) / nsa}


def build() -> dict:
    ref = raw_metrics(OPTIONS[REFERENCE])
    options, lifts = {}, {}
    for name, o in OPTIONS.items():
        r = raw_metrics(o)
        pop = sum(PERSONS_PER_BEDROOM * BEDROOMS[t] * k for t, k in o["mix"].items())
        lifts[name] = lift_check(pop, o["lifts_provided"])
        rec = {k: v for k, v in o.items() if k not in ("cost_factor", "carbon_factor")}
        rec["proxy_factors"] = {"cost_structure_factor": o["cost_factor"], "carbon_structure_factor": o["carbon_factor"]}
        rec.update({
            "storeys_above_grade": STOREYS, "residential_floors": RES_FLOORS,
            "height_to_roof_slab_m": round(HEIGHT, 2),
            "gfa_floor_m2": round(r["gfa"], 2), "core_area_m2": round(r["core"], 2),
            "corridor_area_m2": round(r["corridor"], 2), "nsa_floor_m2": round(r["nsa"], 2),
            "efficiency_nsa_gfa": round(r["nsa"] / r["gfa"], 3),
            "perimeter_m": round(r["per"], 2), "facade_area_floor_m2": round(r["facade"], 2),
            "facade_per_gfa": round(r["facade"] / r["gfa"], 3),
            "max_depth_facade_to_core_m": round(r["depth"], 2),
            "apartment_depth_max_m": round(r["depth"] - r["w"], 2),
            "core_area_ratio": round(r["core"] / r["gfa"], 3),
            "apartments_per_floor": r["apts"], "apartments_total": r["apts"] * RES_FLOORS,
            "nsa_total_m2": round(r["nsa"] * RES_FLOORS, 2),
            "gfa_above_grade_m2": round(r["gfa"] * STOREYS, 2),
            "dual_aspect_share": round(o["dual_aspect_apartments"] / r["apts"], 3),
            "slenderness_h_over_b": round(HEIGHT / min(o["plate"]["L"], o["plate"]["W"]), 3),
            "fits_reference_footprint": o["plate"]["L"] <= REF_PLATE[0] and o["plate"]["W"] <= REF_PLATE[1],
            "cost_proxy_index": round(r["cost_raw"] / ref["cost_raw"], 3),
            "carbon_proxy_index": round(r["carbon_raw"] / ref["carbon_raw"], 3),
            "population_per_floor": pop,
        })
        options[name] = rec
    floor = [{"name": n, "type": t, "x0": x0, "y0": y0, "x1": x1, "y1": y1, "area_m2": round((x1 - x0) * (y1 - y0), 2)}
             for (n, t, x0, y0, x1, y1) in TYPICAL_FLOOR]
    self_check(floor, options[REFERENCE])
    return {
        "division": "architecture", "status": "concept options v1 (not for construction)",
        "reference_option": REFERENCE, "options": options, "objective_senses": OBJECTIVE_SENSES,
        "typical_floor": floor, "lift_check": lifts, "evidence": EVIDENCE,
        "proxy_weights": {"K_FC_facade_cost": K_FC, "K_FE_facade_carbon": K_FE, "label": "JUDGMENT"},
        "lift_assumptions": {"hc5_target_fraction": HC5_TARGET, "car_rated_persons": CAR_RATED_PERSONS,
                             "passengers_per_trip": P_TRIP, "speed_m_s": SPEED, "t_stop_s": T_STOP,
                             "t_pass_s": T_PASS, "persons_per_bedroom": PERSONS_PER_BEDROOM, "label": "ASSUMPTION"},
    }


def self_check(floor: list, ref: dict) -> None:
    def a(r):
        return (r["x1"] - r["x0"]) * (r["y1"] - r["y0"])
    lx, ly = REF_PLATE
    assert abs(sum(a(r) for r in floor) - lx * ly) < 1e-6
    for p, q in combinations(floor, 2):
        ox = min(p["x1"], q["x1"]) - max(p["x0"], q["x0"])
        oy = min(p["y1"], q["y1"]) - max(p["y0"], q["y0"])
        assert not (ox > 1e-9 and oy > 1e-9), (p["name"], q["name"])
    assert abs(sum(a(r) for r in floor if r["type"] in APT_TYPES) - ref["nsa_floor_m2"]) < 1e-6
    assert abs(sum(a(r) for r in floor if r["type"] in CORE_TYPES) - ref["core_area_m2"]) < 1e-6
    assert abs(sum(a(r) for r in floor if r["type"] == "corridor") - ref["corridor_area_m2"]) < 1e-6
    assert sum(1 for r in floor if r["type"] in APT_TYPES) == ref["apartments_per_floor"]


if __name__ == "__main__":
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    for n, o in data["options"].items():
        print(f"{n:16s} GFA {o['gfa_floor_m2']:6.1f} NSA {o['nsa_floor_m2']:6.1f} eff {o['efficiency_nsa_gfa']:.3f} "
              f"depth {o['max_depth_facade_to_core_m']:4.1f} cost {o['cost_proxy_index']:.3f} carbon {o['carbon_proxy_index']:.3f} "
              f"lifts {data['lift_check'][n]['lifts_required']}/{o['lifts_provided']}")
    print("wrote", OUT)
