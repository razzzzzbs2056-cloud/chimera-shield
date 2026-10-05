"""Division 12 Fire Engineering: geometry-only egress checks for the 30-storey tower, option A.

Reads typical_floor rectangles from data/architecture.json. All distances in metres.
CONCEPT ONLY. No code numeric limits are used or stated here: every limit is INSUFFICIENT INFORMATION
until the Codes division retrieves and cites the NCC / NSW text.

Assumptions (labelled ASSUMPTION in the return):
  * Apartment entry door at midpoint of the longest edge shared with a corridor rectangle.
  * Stair doors: Stair 1 on its west face (x=9, mid-y), onto Corridor W; Stair 2 on its east face (x=21, mid-y),
    onto Corridor E (this reproduces the 13.1 m separation flagged by the architects).
  * Corridor travel is along the ring centreline (rectangle through the corridor mid-lines).
  * In-apartment distance is straight line door -> furthest corner (a lower bound); ROUTING_FACTOR scales it.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARCH = HERE.parent / "data" / "architecture.json"
OUT = HERE.parent / "data" / "fire.json"

ROUTING_FACTOR = 1.3          # ASSUMPTION: furniture / internal walls vs straight line
PERSONS_PER_BEDROOM = {"base": 1.5, "high": 2.0}   # base = architecture division basis; high = sensitivity
BEDROOMS = {"1B": 1, "2B": 2, "3B": 3}
FLOW_P_PER_S_PER_M = 1.0      # ASSUMPTION (parametric, textbook-order stair flow); NOT a code value
WIDTHS = [1.0, 1.2, 1.5]      # candidate effective stair widths, m (parametric)


def load():
    return json.loads(ARCH.read_text())["options"]["A_cheapest"], json.loads(ARCH.read_text())["typical_floor"]


def rect_by_name(floor):
    return {r["name"]: r for r in floor}


def shared_edge(a, b, tol=1e-9):
    """Return (p0, p1) of the shared boundary segment between rectangles a,b or None."""
    # vertical shared edge
    for xa, xb in ((a["x1"], b["x0"]), (a["x0"], b["x1"])):
        if abs(xa - xb) < tol:
            lo, hi = max(a["y0"], b["y0"]), min(a["y1"], b["y1"])
            if hi - lo > tol:
                return (xa, lo), (xa, hi)
    for ya, yb in ((a["y1"], b["y0"]), (a["y0"], b["y1"])):
        if abs(ya - yb) < tol:
            lo, hi = max(a["x0"], b["x0"]), min(a["x1"], b["x1"])
            if hi - lo > tol:
                return (lo, ya), (hi, ya)
    return None


def ring_from_corridors(floor):
    c = {r["name"]: r for r in floor if r["type"] == "corridor"}
    xw = (c["Corridor W"]["x0"] + c["Corridor W"]["x1"]) / 2
    xe = (c["Corridor E"]["x0"] + c["Corridor E"]["x1"]) / 2
    ys = (c["Corridor S"]["y0"] + c["Corridor S"]["y1"]) / 2
    yn = (c["Corridor N"]["y0"] + c["Corridor N"]["y1"]) / 2
    return xw, xe, ys, yn


def ring_param(pt, ring):
    """Project pt onto the ring rectangle; return (arc position s, offset distance). s runs ccw from (xw,ys)."""
    xw, xe, ys, yn = ring
    w, h = xe - xw, yn - ys
    cands = []
    x, y = pt
    # bottom edge
    cx = min(max(x, xw), xe); cands.append((abs(y - ys) + abs(x - cx), cx - xw, (cx, ys)))
    # right edge
    cy = min(max(y, ys), yn); cands.append((abs(x - xe) + abs(y - cy), w + (cy - ys), (xe, cy)))
    # top edge
    cx = min(max(x, xw), xe); cands.append((abs(y - yn) + abs(x - cx), w + h + (xe - cx), (cx, yn)))
    # left edge
    cy = min(max(y, ys), yn); cands.append((abs(x - xw) + abs(y - cy), 2 * w + h + (yn - cy), (xw, cy)))
    best = min(cands, key=lambda t: t[0])
    off = math.hypot(pt[0] - best[2][0], pt[1] - best[2][1])
    return best[1], off, 2 * (w + h)


def ring_dists(s1, s2, perim):
    d = abs(s1 - s2)
    return min(d, perim - d), max(d, perim - d)       # (shorter way, longer way)


def stair_doors(floor):
    r = rect_by_name(floor)
    s1, s2 = r["Stair 1"], r["Stair 2"]
    d1 = (s1["x0"], (s1["y0"] + s1["y1"]) / 2)   # west face
    d2 = (s2["x1"], (s2["y0"] + s2["y1"]) / 2)   # east face
    return d1, d2


def apartment_door(apt, corridors):
    best = None
    for c in corridors:
        e = shared_edge(apt, c)
        if e:
            L = math.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1])
            if best is None or L > best[0]:
                best = (L, ((e[0][0] + e[1][0]) / 2, (e[0][1] + e[1][1]) / 2), c["name"])
    return best


def corners(r):
    return [(r["x0"], r["y0"]), (r["x1"], r["y0"]), (r["x1"], r["y1"]), (r["x0"], r["y1"])]


def egress(floor):
    ring = ring_from_corridors(floor)
    corridors = [r for r in floor if r["type"] == "corridor"]
    d1, d2 = stair_doors(floor)
    sd = []
    for d in (d1, d2):
        s, off, perim = ring_param(d, ring)
        sd.append((s, off))
    perim = perim
    apts = []
    for r in floor:
        if r["type"] not in BEDROOMS:
            continue
        L, door, cname = apartment_door(r, corridors)
        s, off, _ = ring_param(door, ring)
        inside = max(math.hypot(door[0] - cx, door[1] - cy) for cx, cy in corners(r))
        routes = {}
        for k, (ss, so) in enumerate(sd, 1):
            a, b = ring_dists(s, ss, perim)
            routes[f"stair{k}"] = {"short": a + off + so, "long": b + off + so}
        nearest = min(routes[k]["short"] for k in routes)
        # farthest of the two stairs by the shorter way (both stairs reachable in either direction)
        # worst case: nearest stair route blocked, use the other stair by its shorter way
        best_k = min(routes, key=lambda k: routes[k]["short"])
        other = [k for k in routes if k != best_k][0]
        alt = routes[other]["short"]
        apts.append({
            "name": r["name"], "type": r["type"], "area_m2": r["area_m2"], "door": door, "corridor": cname,
            "inside_straight_m": inside, "inside_routed_m": inside * ROUTING_FACTOR,
            "corridor_to_nearest_stair_door_m": nearest,
            "total_to_nearest_stair_m": inside * ROUTING_FACTOR + nearest,
            "corridor_to_other_stair_m": alt,
            "total_to_other_stair_m": inside * ROUTING_FACTOR + alt,
            "routes": routes,
            "dead_end_m": 0.0,  # ring: two directions from every door (continuity ASSUMED)
        })
    sep = math.dist(d1, d2)
    diag = math.hypot(30.0, 24.0)
    sa, sb = ring_dists(sd[0][0], sd[1][0], perim)
    return {
        "ring": {"x_w": ring[0], "x_e": ring[1], "y_s": ring[2], "y_n": ring[3], "perimeter_m": perim},
        "stair_doors": {"stair1": d1, "stair2": d2},
        "stair_separation": {
            "straight_line_m": sep, "floor_diagonal_m": diag, "fraction_of_diagonal": sep / diag,
            "ring_path_short_m": sa + sd[0][1] + sd[1][1], "ring_path_long_m": sb + sd[0][1] + sd[1][1],
            "third_of_diagonal_m": diag / 3.0,   # reference ratio quoted by architects, NOT a code value
            "stair_centre_distance_m": math.dist(((9 + 14.5) / 2, 9.4), ((15.5 + 21) / 2, 14.6)),
        },
        "apartments": apts,
        "max_total_to_nearest_stair_m": max(a["total_to_nearest_stair_m"] for a in apts),
        "max_total_to_other_stair_m": max(a["total_to_other_stair_m"] for a in apts),
        "max_total_straight_inside_m": max(a["inside_straight_m"] + a["corridor_to_nearest_stair_door_m"] for a in apts),
        "max_corridor_only_to_nearest_stair_m": max(a["corridor_to_nearest_stair_door_m"] for a in apts),
    }


def occupancy(opt):
    mix = opt["mix"]
    bed = sum(BEDROOMS[k] * n for k, n in mix.items())
    out = {"bedrooms_per_floor": bed, "residential_floors": opt["residential_floors"]}
    for tag, p in PERSONS_PER_BEDROOM.items():
        pf = bed * p
        out[tag] = {"persons_per_bedroom": p, "per_floor": pf, "total": pf * opt["residential_floors"]}
    # ground floor / basements: area known, density and use UNKNOWN -> parametric only
    out["ground_floor_area_m2"] = opt["gfa_floor_m2"]
    out["ground_floor_parametric"] = {f"1 person per {a} m2": opt["gfa_floor_m2"] / a for a in (1.0, 3.0, 5.0)}
    return out


def stair_flow(occ):
    res = {}
    for tag in ("base", "high"):
        n_all = occ[tag]["total"]
        res[tag] = {"total_persons": n_all, "per_stair_both_available": n_all / 2, "per_stair_one_lost": n_all}
        rows = []
        for w in WIDTHS:
            rows.append({
                "eff_width_m": w,
                "t_both_min": n_all / 2 / (FLOW_P_PER_S_PER_M * w) / 60,
                "t_one_lost_min": n_all / (FLOW_P_PER_S_PER_M * w) / 60,
            })
        res[tag]["rows"] = rows
    res["flow_assumption_p_per_s_per_m"] = FLOW_P_PER_S_PER_M
    res["note"] = "Full simultaneous evacuation, flow-limited at stair base, no merging losses: lower bound on time."
    return res


def run():
    opt, floor = load()
    eg = egress(floor)
    occ = occupancy(opt)
    # geometry facts for compartmentation
    r = rect_by_name(floor)
    fire = {
        "division": "12 Fire Engineering",
        "status": "concept geometry checks (not for construction); code limits NOT retrieved",
        "routing_factor_assumption": ROUTING_FACTOR,
        "occupancy": occ,
        "egress": eg,
        "stair_flow": stair_flow(occ),
        "exits_per_floor": 2,
        "firefighting_lift_candidate": "Lift 2 (adjacent to Stair 1 side of core; in core with 4 lifts sharing one lobby)",
        "stair_core_distance_to_facade_m": {
            "stair1_min_to_external_wall": min(r["Stair 1"]["x0"], r["Stair 1"]["y0"]),
            "stair2_min_to_external_wall": min(30 - r["Stair 2"]["x1"], 24 - r["Stair 2"]["y1"]),
        },
        "verdicts": {},
    }
    return fire


if __name__ == "__main__":
    f = run()
    OUT.write_text(json.dumps(f, indent=1, default=lambda o: list(o) if isinstance(o, tuple) else str(o)))
    e = f["egress"]
    print("occupants/floor", f["occupancy"]["base"]["per_floor"], "total", f["occupancy"]["base"]["total"])
    print("stair sep", e["stair_separation"])
    for a in e["apartments"]:
        print(a["name"], a["type"], round(a["inside_straight_m"], 2), round(a["corridor_to_nearest_stair_door_m"], 2),
              round(a["total_to_nearest_stair_m"], 2), round(a["total_to_other_stair_m"], 2))
    print("max", e["max_total_to_nearest_stair_m"], e["max_total_to_other_stair_m"])
