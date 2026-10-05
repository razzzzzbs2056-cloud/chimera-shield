"""30-storey residential tower: structural concept, gravity takedown and lateral sanity properties.

Division 3 (Structural Engineering), analysis hierarchy Level 1-2 (load path + hand calculations as script).
Reference scheme: RC central core + perimeter RC columns + post-tensioned (PT) flat plate.

Every numerical input that is not in architecture/tower/basis.json or architecture/data/*.csv is an
ASSUMPTION and is collected in the dict `A` below.  Site, jurisdiction, wind/seismic hazard and soil are
UNKNOWN; nothing here depends on them.  Load factors are generic (EN 1990 6.10 form and ASCE 7 LRFD form
taken from architecture/data/load_combinations.csv) and are used only as ASSUMPTIONS until the
jurisdiction is known.  Not a design: final sizes need a licensed engineer's analysis.

Units: m, kN, kPa, t (tonne), s, MPa.
Usage:  python architecture/tower/calcs/structure_gravity.py   -> writes architecture/tower/data/structure.json
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TOWER = HERE.parent
ARCH = TOWER.parent
sys.path.insert(0, str(ARCH / "tools"))
from quickcheck import factored_load_ec  # noqa: E402  (1.35G + 1.5Q)

BASIS = json.loads((TOWER / "basis.json").read_text())
G_ACC = 9.81  # m/s2

with open(ARCH / "data" / "materials.csv", newline="") as f:
    _MAT = {r["material"]: r for r in csv.DictReader(f)}
CONC = _MAT["Concrete C40/50"]          # FACT (repo data pack): fck 40 MPa, E 35 GPa, 2450 kg/m3

# ---------------------------------------------------------------- ASSUMPTIONS (all to be confirmed)
A = {
    "gamma_rc_kN_m3": 25.0,              # reinforced concrete unit weight incl. rebar
    "slab_thickness_m": 0.25,            # PT flat plate, from span/depth (see slab_design())
    "slab_span_governing_m": 9.0,        # core face (x=9) to perimeter column line (x=0)
    "pt_span_depth_ratio_range": [35, 45],   # textbook range for PT flat plates (verify)
    "rc_span_depth_ratio_range": [26, 30],   # textbook range for non-PT RC flat plates (verify)
    "sdl_kPa": BASIS["loads_assumed"]["superimposed_dead_kPa"],      # 1.0
    "partitions_kPa": BASIS["loads_assumed"]["partitions_kPa"],      # 0.5
    "facade_kN_m": BASIS["loads_assumed"]["facade_line_load_kN_per_m"],  # 6.0 per floor edge
    "live_res_kPa": max(BASIS["loads_assumed"]["residential_live_kPa_range"]),  # 2.0 (upper bound)
    "live_corridor_kPa": BASIS["loads_assumed"]["corridor_live_kPa"],  # 3.0
    "corridor_band_m": 1.5,              # corridor ring around the core
    "roof_live_kPa": BASIS["loads_assumed"]["roof_live_kPa"],        # 1.5
    "roof_sdl_kPa": 1.5,                 # roofing, insulation, falls (replaces SDL+partitions at roof)
    "roof_plant_kPa": 2.0,               # plant allowance smeared over roof slab outside core
    "core_floor_fraction": 0.6,          # fraction of 12x8 core interior that has slab (rest = shafts)
    "core_live_kPa": 3.0,                # stairs/lobby inside core
    "core_roof_plant_kPa": 5.0,          # tanks / lift machinery on core roof (plant level, +5 m)
    "core_internal_wall_t_m": 0.25,      # two internal cross walls (weight only, not in stiffness)
    "core_internal_wall_count": 2,
    "core_wall_t_zones_m": {"1-10": 0.60, "11-20": 0.50, "21-31": 0.40},
    "column_min_m": 0.45,                # minimum column size (fire / punching / buildability)
    "column_round_m": 0.05,
    "column_stress_limit_frac_fck": 0.45,  # factored N / (Ac fck) limit: margin for moment, slenderness, ductility
    "psi_live_seismic": 0.3,             # live fraction in seismic weight (generic; code-dependent)
    "load_factors_EC_form": [1.35, 1.5], # 1.35G + 1.5Q   (architecture/data/load_combinations.csv)
    "load_factors_LRFD_form": [1.2, 1.6],# 1.2D + 1.6L    (architecture/data/load_combinations.csv)
    "live_load_reduction": "none (conservative)",
    "cracked_factor": 0.5,               # walls, applied to both EI and GA (generic range 0.35-0.7)
    "poisson": 0.2,
    "base_fixity": "fixed at ground slab (z=0); basement box and soil flexibility ignored",
    "grid_resolution_m": 0.05,           # tributary-area raster cell
}

PLATE = tuple(BASIS["geometry"]["floor_plate_m"])        # (30, 24)
CORE = tuple(BASIS["geometry"]["core_m"])                # (12, 8)
CORE_BOX = ((PLATE[0] - CORE[0]) / 2, (PLATE[1] - CORE[1]) / 2,
            (PLATE[0] + CORE[0]) / 2, (PLATE[1] + CORE[1]) / 2)   # (9, 8, 21, 16)
FCK = float(CONC["strength_MPa"])                        # 40
E_MPA = float(CONC["E_GPa"]) * 1000                      # 35000
N_LEVELS = BASIS["geometry"]["storeys_above_grade"]      # 30 slab levels (L1..L30, L30 = roof slab)


# ---------------------------------------------------------------- geometry
def levels() -> list[float]:
    """z of suspended levels above ground slab: L1..L30 (L30 = roof slab at 94.4 m) + plant level."""
    g = BASIS["geometry"]
    z = [g["ground_floor_to_floor_m"]]
    for _ in range(N_LEVELS - 1):
        z.append(z[-1] + g["typical_floor_to_floor_m"])
    z.append(z[-1] + g["rooftop_plant_m"])
    return [round(v, 6) for v in z]


def column_grid() -> dict[str, tuple[float, float]]:
    """14 perimeter columns: long faces at x = 0, 7.5, 15, 22.5, 30; short faces at y = 0, 8, 16, 24.
    Short-face intermediate columns align with the core faces (y = 8, 16). No interior columns."""
    xs = [0.0, 7.5, 15.0, 22.5, 30.0]
    ys = [0.0, 8.0, 16.0, 24.0]
    cols = {}
    for x in xs:
        for y in (0.0, PLATE[1]):
            cols[(x, y)] = None
    for y in ys:
        for x in (0.0, PLATE[0]):
            cols[(x, y)] = None
    out = {}
    for (x, y) in sorted(cols):
        corner = x in (0.0, PLATE[0]) and y in (0.0, PLATE[1])
        tag = "C" if corner else "E"
        out[f"{tag}_{x:g}_{y:g}"] = (x, y)
    return out


def _dist_to_box(px, py, box):
    x0, y0, x1, y1 = box
    dx = np.maximum(np.maximum(x0 - px, 0), px - x1)
    dy = np.maximum(np.maximum(y0 - py, 0), py - y1)
    return np.hypot(dx, dy)


def tributary(cols: dict, h: float | None = None) -> dict:
    """Nearest-support (Voronoi-type) tributary areas on a raster: each slab cell outside the core goes
    to the nearest column point or to the core perimeter (core treated as a continuous wall support).
    Returns per-support total area and the part lying in the corridor band (for live load)."""
    h = h or A["grid_resolution_m"]
    nx, ny = round(PLATE[0] / h), round(PLATE[1] / h)
    xc = (np.arange(nx) + 0.5) * h
    yc = (np.arange(ny) + 0.5) * h
    X, Y = np.meshgrid(xc, yc, indexing="ij")
    x0, y0, x1, y1 = CORE_BOX
    inside_core = (X > x0) & (X < x1) & (Y > y0) & (Y < y1)
    b = A["corridor_band_m"]
    in_corr = (~inside_core) & (X > x0 - b) & (X < x1 + b) & (Y > y0 - b) & (Y < y1 + b)
    names = list(cols)
    d = np.stack([np.hypot(X - cols[n][0], Y - cols[n][1]) for n in names]
                 + [_dist_to_box(X, Y, CORE_BOX)])
    owner = np.argmin(d, axis=0)
    cell = h * h
    area, corr = {}, {}
    for i, n in enumerate(names + ["core"]):
        m = (owner == i) & ~inside_core
        area[n] = float(m.sum() * cell)
        corr[n] = float((m & in_corr).sum() * cell)
    return {"area_m2": area, "corridor_m2": corr, "core_interior_m2": float(inside_core.sum() * cell)}


def facade_lengths(cols: dict, h: float | None = None) -> dict:
    """Perimeter edge length assigned to the nearest column (facade line load)."""
    h = h or A["grid_resolution_m"]
    pts = []
    for L, fixed, axis in ((PLATE[0], 0.0, "x"), (PLATE[0], PLATE[1], "x"),
                           (PLATE[1], 0.0, "y"), (PLATE[1], PLATE[0], "y")):
        s = (np.arange(round(L / h)) + 0.5) * h
        pts += [(v, fixed) if axis == "x" else (fixed, v) for v in s]
    P = np.array(pts)
    names = list(cols)
    d = np.stack([np.hypot(P[:, 0] - cols[n][0], P[:, 1] - cols[n][1]) for n in names])
    owner = np.argmin(d, axis=0)
    return {n: float((owner == i).sum() * h) for i, n in enumerate(names)}


# ---------------------------------------------------------------- slab
def slab_design() -> dict:
    L = A["slab_span_governing_m"]
    lo, hi = A["pt_span_depth_ratio_range"]
    rlo, rhi = A["rc_span_depth_ratio_range"]
    return {
        "governing_span_m": L,
        "pt_thickness_range_m": [round(L / hi, 3), round(L / lo, 3)],
        "rc_thickness_range_m": [round(L / rhi, 3), round(L / rlo, 3)],
        "selected_pt_m": A["slab_thickness_m"],
        "selected_span_depth": round(L / A["slab_thickness_m"], 1),
    }


# ---------------------------------------------------------------- core section
def zone_of(level: int) -> str:
    for k in A["core_wall_t_zones_m"]:
        a, b = (int(v) for v in k.split("-"))
        if a <= level <= b:
            return k
    raise ValueError(level)


def core_wall_t(level: int) -> float:
    return A["core_wall_t_zones_m"][zone_of(level)]


def core_section(t: float, bx: float = CORE[0], by: float = CORE[1]) -> dict:
    """Closed hollow rectangle (openings ignored). bx along X (12 m), by along Y (8 m).
    I_x: about the x-axis (resists sway in Y).  I_y: about the y-axis (resists sway in X).
    A_shear_X: webs parallel to X (two walls of length bx); A_shear_Y: two walls of length by."""
    ix = (bx * by ** 3 - (bx - 2 * t) * (by - 2 * t) ** 3) / 12
    iy = (by * bx ** 3 - (by - 2 * t) * (bx - 2 * t) ** 3) / 12
    area = bx * by - (bx - 2 * t) * (by - 2 * t)
    return {"t_m": t, "A_m2": area, "I_x_m4": ix, "I_y_m4": iy,
            "A_shear_X_m2": 2 * bx * t, "A_shear_Y_m2": 2 * by * t}


def core_wall_area_total(t: float) -> float:
    """Plan area of core walls incl. internal cross walls (weight)."""
    ti = A["core_internal_wall_t_m"]
    return core_section(t)["A_m2"] + A["core_internal_wall_count"] * (CORE[1] - 2 * t) * ti


# ---------------------------------------------------------------- loads per level
def storey_heights(z: list[float]) -> list[float]:
    return [z[0]] + [z[i] - z[i - 1] for i in range(1, len(z))]


def level_area_loads(level: int) -> dict:
    """Dead (kPa) and live (kPa) on the slab outside the core at suspended level 1..30."""
    g_slab = A["slab_thickness_m"] * A["gamma_rc_kN_m3"]
    if level == N_LEVELS:  # roof slab
        return {"G": g_slab + A["roof_sdl_kPa"] + A["roof_plant_kPa"],
                "Q": A["roof_live_kPa"], "Qcorr": A["roof_live_kPa"]}
    return {"G": g_slab + A["sdl_kPa"] + A["partitions_kPa"],
            "Q": A["live_res_kPa"], "Qcorr": A["live_corridor_kPa"]}


def column_size(n_ed_kN: float) -> float:
    sig = A["column_stress_limit_frac_fck"] * FCK * 1000  # kPa
    b = math.sqrt(n_ed_kN / sig)
    r = A["column_round_m"]
    return round(max(A["column_min_m"], math.ceil(b / r - 1e-9) * r), 3)


def factored(G: float, Q: float) -> dict:
    ec = factored_load_ec(G, Q)
    a, b = A["load_factors_LRFD_form"]
    lr = a * G + b * Q
    return {"EC_form": ec, "LRFD_form": lr, "governing": max(ec, lr)}


def takedown() -> dict:
    z = levels()
    hs = storey_heights(z)
    cols = column_grid()
    trib = tributary(cols)
    fac = facade_lengths(cols)
    zones = list(A["core_wall_t_zones_m"])
    # iterate column sizes per zone (self-weight depends on size)
    size = {n: {zk: A["column_min_m"] for zk in zones} for n in cols}
    for _ in range(6):
        per = {n: {"G": [0.0] * N_LEVELS, "Q": [0.0] * N_LEVELS} for n in cols}
        for n in cols:
            a, ac = trib["area_m2"][n], trib["corridor_m2"][n]
            for lv in range(1, N_LEVELS + 1):
                ld = level_area_loads(lv)
                b = size[n][zone_of(lv)]
                g = ld["G"] * a + A["facade_kN_m"] * fac[n] + b * b * hs[lv - 1] * A["gamma_rc_kN_m3"]
                q = ld["Q"] * (a - ac) + ld["Qcorr"] * ac
                per[n]["G"][lv - 1], per[n]["Q"][lv - 1] = g, q
        new = {}
        for n in cols:
            new[n] = {}
            for zk in zones:
                lo = int(zk.split("-")[0])
                G = sum(per[n]["G"][lo - 1:]); Q = sum(per[n]["Q"][lo - 1:])
                new[n][zk] = column_size(factored(G, Q)["governing"])
        if new == size:
            break
        size = new

    columns = {}
    for n in cols:
        G, Q = sum(per[n]["G"]), sum(per[n]["Q"])
        f = factored(G, Q)
        b = size[n][zones[0]]
        columns[n] = {
            "x_m": cols[n][0], "y_m": cols[n][1], "type": "corner" if n.startswith("C") else "edge",
            "trib_area_m2": round(trib["area_m2"][n], 4), "facade_length_m": round(fac[n], 4),
            "G_base_kN": G, "Q_base_kN": Q, "N_EC_kN": f["EC_form"], "N_LRFD_kN": f["LRFD_form"],
            "N_Ed_kN": f["governing"], "size_by_zone_m": size[n],
            "base_size_m": b, "base_stress_ratio": f["governing"] / (b * b * FCK * 1000),
        }

    # core: walls, core interior floors, core tributary slab, core-roof plant level
    core_G = [0.0] * (N_LEVELS + 1)
    core_Q = [0.0] * (N_LEVELS + 1)
    a_core, ac_core = trib["area_m2"]["core"], trib["corridor_m2"]["core"]
    a_int = trib["core_interior_m2"] * A["core_floor_fraction"]
    g_slab = A["slab_thickness_m"] * A["gamma_rc_kN_m3"]
    for lv in range(1, N_LEVELS + 2):
        t = core_wall_t(lv)
        walls = core_wall_area_total(t) * hs[lv - 1] * A["gamma_rc_kN_m3"]
        if lv <= N_LEVELS:
            ld = level_area_loads(lv)
            slab = ld["G"] * a_core
            interior = (g_slab + A["sdl_kPa"]) * a_int
            q = ld["Q"] * (a_core - ac_core) + ld["Qcorr"] * ac_core + A["core_live_kPa"] * a_int
        else:  # plant level on core roof: full 12x8 roof slab + tanks
            slab = 0.0
            interior = (g_slab + A["roof_sdl_kPa"] + A["core_roof_plant_kPa"]) * CORE[0] * CORE[1]
            q = A["roof_live_kPa"] * CORE[0] * CORE[1]
        core_G[lv - 1], core_Q[lv - 1] = walls + slab + interior, q
    cG, cQ = sum(core_G), sum(core_Q)
    t0 = core_wall_t(1)
    core_f = factored(cG, cQ)
    core = {
        "outer_dims_m": list(CORE), "box_m": list(CORE_BOX),
        "wall_t_zones_m": A["core_wall_t_zones_m"], "wall_t_range_m": [min(A["core_wall_t_zones_m"].values()),
                                                                       max(A["core_wall_t_zones_m"].values())],
        "trib_slab_area_m2": a_core, "interior_floor_area_m2": a_int,
        "G_base_kN": cG, "Q_base_kN": cQ, "N_Ed_kN": core_f["governing"],
        "wall_area_base_m2": core_wall_area_total(t0),
        "base_axial_stress_MPa": core_f["governing"] / core_wall_area_total(t0) / 1000,
        "per_level_G_kN": core_G, "per_level_Q_kN": core_Q,
    }
    return {"z": z, "hs": hs, "cols": cols, "trib": trib, "facade": fac, "columns": columns,
            "core": core, "col_per_level": per}


# ---------------------------------------------------------------- seismic weight per level
def seismic_weights(td: dict) -> dict:
    """Lumped weight at each of the 31 levels: slab/SDL/partitions/facade/plant at the level,
    + half of columns and core walls of the storeys below and above, + psi * live.
    Lower half of the ground storey (0 - 4.5 m) goes to the base and is excluded from W."""
    z, hs = td["z"], td["hs"]
    nL = len(z)
    psi = A["psi_live_seismic"]
    floor_area = PLATE[0] * PLATE[1] - CORE[0] * CORE[1]
    perim = 2 * (PLATE[0] + PLATE[1])
    a_int = td["core"]["interior_floor_area_m2"]
    g_slab = A["slab_thickness_m"] * A["gamma_rc_kN_m3"]
    # vertical elements weight per storey (storey k spans z[k-1]..z[k], k = 1..nL)
    vert = []
    for k in range(1, nL + 1):
        w = core_wall_area_total(core_wall_t(k)) * hs[k - 1] * A["gamma_rc_kN_m3"]
        if k <= N_LEVELS:
            w += sum(c["size_by_zone_m"][zone_of(k)] ** 2 for c in td["columns"].values()) \
                * hs[k - 1] * A["gamma_rc_kN_m3"]
        vert.append(w)
    W = []
    Qcorr_area = sum(td["trib"]["corridor_m2"].values())
    for lv in range(1, nL + 1):
        w = vert[lv - 1] / 2 + (vert[lv] / 2 if lv < nL else 0.0)
        if lv <= N_LEVELS:
            ld = level_area_loads(lv)
            q = ld["Q"] * (floor_area - Qcorr_area) + ld["Qcorr"] * Qcorr_area + A["core_live_kPa"] * a_int
            w += ld["G"] * floor_area + A["facade_kN_m"] * perim + (g_slab + A["sdl_kPa"]) * a_int + psi * q
        else:
            w += (g_slab + A["roof_sdl_kPa"] + A["core_roof_plant_kPa"]) * CORE[0] * CORE[1] \
                + psi * A["roof_live_kPa"] * CORE[0] * CORE[1]
        W.append(w)
    return {"W_level_kN": W, "mass_t": [w / G_ACC for w in W], "W_kN": sum(W),
            "W_lower_half_ground_storey_to_base_kN": vert[0] / 2}


# ---------------------------------------------------------------- lateral: cantilever flexibility
def flexibility(z: np.ndarray, EI_fn, GA_fn, nseg: int = 4000) -> np.ndarray:
    """Cantilever fixed at z=0: delta_ij = int_0^min (zi-s)(zj-s)/EI ds + int_0^min 1/GA ds."""
    H = float(z.max())
    s = (np.arange(nseg) + 0.5) * H / nseg
    ds = H / nseg
    ei, ga = np.array([EI_fn(v) for v in s]), np.array([GA_fn(v) for v in s])
    n = len(z)
    F = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            zm = min(z[i], z[j])
            m = s < zm   # midpoint rule; level heights fall on/near segment boundaries
            f = np.sum((z[i] - s[m]) * (z[j] - s[m]) / ei[m]) * ds + np.sum(1.0 / ga[m]) * ds
            F[i, j] = F[j, i] = f
    return F


def periods(mass_t: np.ndarray, F: np.ndarray) -> np.ndarray:
    """Eigen-periods (s) of lumped-mass system: (F M) phi = (1/w2) phi. mass in t, F in m/kN."""
    lam = np.linalg.eigvals(F @ np.diag(mass_t)).real   # = 1/w^2 (s^2)
    lam = np.sort(lam[lam > 0])[::-1]
    return 2 * math.pi * np.sqrt(lam)


def closed_form_flexure_T(mbar_t_m: float, L: float, EI: float) -> float:
    return 2 * math.pi / 1.875104 ** 2 * math.sqrt(mbar_t_m * L ** 4 / EI)


def closed_form_shear_T(mbar_t_m: float, L: float, GA: float) -> float:
    return 4 * L * math.sqrt(mbar_t_m / GA)


def lateral(td: dict, sw: dict, cracked: float | None = None) -> dict:
    cr = A["cracked_factor"] if cracked is None else cracked
    z = np.array(td["z"])
    E = E_MPA * 1000.0                       # kPa
    G = E / (2 * (1 + A["poisson"]))
    bounds = [0.0] + list(z)

    def lvl_at(s):
        for k in range(1, len(bounds)):
            if s <= bounds[k] + 1e-12:
                return k
        return len(bounds) - 1

    out = {}
    m = np.array(sw["mass_t"])
    for d, ikey, akey in (("X", "I_y_m4", "A_shear_X_m2"), ("Y", "I_x_m4", "A_shear_Y_m2")):
        EI = lambda s, ik=ikey: cr * E * core_section(core_wall_t(lvl_at(s)))[ik]
        GA = lambda s, ak=akey: cr * G * core_section(core_wall_t(lvl_at(s)))[ak]
        F = flexibility(z, EI, GA)
        Fb = flexibility(z, EI, lambda s: 1e30)
        T = periods(m, F)
        # top deflection under 1 kN/m uniform load (tributary lumping) -> for wind division scaling
        hs = np.array(td["hs"])
        trib_h = np.array([(hs[i] + (hs[i + 1] if i + 1 < len(hs) else 0)) / 2 for i in range(len(hs))])
        u = F @ trib_h
        out[d] = {"T1_s": float(T[0]), "T2_s": float(T[1]), "T1_flexure_only_s": float(periods(m, Fb)[0]),
                  "top_defl_mm_per_kN_per_m": float(u[-2] * 1000),  # at roof slab (94.4 m)
                  "EI_base_kNm2": EI(0.1), "GA_base_kN": GA(0.1)}
    return out


def unit_weight_check(sw: dict) -> float:
    return sw["W_kN"] / (PLATE[0] * PLATE[1] * N_LEVELS)


def options() -> list[dict]:
    """Qualitative + first-order quantitative system comparison (JUDGMENT, numbers are indicative)."""
    return [
        {"id": "A", "name": "RC core + perimeter RC columns + PT flat plate (250 mm)",
         "slab_dead_kPa": 0.25 * A["gamma_rc_kN_m3"], "floor_zone_m": 0.25,
         "notes": "thinnest floor zone, flat soffit, inherent fire resistance, formwork repetition; "
                  "lateral by core only (slender 8 m core in Y); PT specialist needed; punching at edge/corner columns"},
        {"id": "B", "name": "Option A + outrigger/belt walls at roof plant or mid-height (e.g. L15/L30)",
         "slab_dead_kPa": 0.25 * A["gamma_rc_kN_m3"], "floor_zone_m": 0.25,
         "notes": "engages perimeter columns in overturning; reduces drift and core base moment; "
                  "costs a usable or plant floor; differential shortening core vs columns at outrigger"},
        {"id": "C", "name": "RC core + steel/composite beams and columns + composite deck (~130 mm)",
         "slab_dead_kPa": 0.13 * A["gamma_rc_kN_m3"] * 0.85 + 0.5, "floor_zone_m": 0.6,
         "notes": "~25-30% lighter floors (lower seismic mass/foundations), faster erection; "
                  "deeper floor zone (+~0.35 m/storey or reduced ceiling), fire protection to steel, "
                  "residential acoustics/vibration of light floors, higher steel carbon"},
    ]


# ---------------------------------------------------------------- main
def run() -> dict:
    td = takedown()
    sw = seismic_weights(td)
    lat = lateral(td, sw)
    lat_gross = lateral(td, sw, cracked=1.0)
    t0 = core_wall_t(1)
    cs = core_section(t0)
    governing_dir = max(lat, key=lambda d: lat[d]["T1_s"])
    cols = td["columns"]
    corner = max((c for c in cols.values() if c["type"] == "corner"), key=lambda c: c["N_Ed_kN"])
    edge = max((c for c in cols.values() if c["type"] == "edge"), key=lambda c: c["N_Ed_kN"])
    total_G = sum(c["G_base_kN"] for c in cols.values()) + td["core"]["G_base_kN"]
    total_Q = sum(c["Q_base_kN"] for c in cols.values()) + td["core"]["Q_base_kN"]
    return {
        "_meta": {"script": "architecture/tower/calcs/structure_gravity.py", "level": "L1-L2 hand calc",
                  "status": "CONCEPT. Not for construction. Licensed engineer's analysis required.",
                  "units": "m, kN, kPa, t, s, MPa"},
        "assumptions": A,
        "concrete": {"grade": CONC["material"], "fck_MPa": FCK, "source": "architecture/data/materials.csv"},
        "grid": {name: [c[0], c[1]] for name, c in td["cols"].items()},
        "plate_m": list(PLATE),
        "floor_area_m2": PLATE[0] * PLATE[1],
        "floor_area_outside_core_m2": PLATE[0] * PLATE[1] - CORE[0] * CORE[1],
        "slab_thickness_m": A["slab_thickness_m"],
        "slab": slab_design(),
        "columns": cols,
        "governing_columns": {"corner": corner, "edge": edge},
        "core": {**{k: v for k, v in td["core"].items() if not k.startswith("per_level")},
                 "wall_thickness_m": t0,
                 "I_x_m4": cs["I_x_m4"], "I_y_m4": cs["I_y_m4"], "A_m2": cs["A_m2"],
                 "A_shear_m2": {"X": cs["A_shear_X_m2"], "Y": cs["A_shear_Y_m2"]},
                 "section_by_zone": {zk: core_section(t) for zk, t in A["core_wall_t_zones_m"].items()},
                 "axis_note": "I_x about x-axis resists sway in Y (8 m depth); I_y about y-axis resists sway in X (12 m depth). Gross, closed tube, openings ignored."},
        "gravity_totals_at_ground_kN": {"G": total_G, "Q": total_Q,
                                        "core_share_G": td["core"]["G_base_kN"] / total_G},
        "levels": {"z_m": td["z"], "storey_height_m": td["hs"],
                   "labels": [f"L{i}" for i in range(1, N_LEVELS)] + ["L30 roof slab", "plant (core roof)"]},
        "mass_t_per_level": sw["mass_t"],
        "W_level_kN": sw["W_level_kN"],
        "W_kN": sw["W_kN"],
        "W_note": "seismic weight above ground slab = dead + psi*live (psi assumed); lower half of ground storey to base",
        "unit_weight_kPa_per_floor": unit_weight_check(sw),
        "E_concrete_MPa": E_MPA,
        "cracked_factor": A["cracked_factor"],
        "lateral_cracked": lat,
        "lateral_gross": lat_gross,
        "T1_sanity_s": lat[governing_dir]["T1_s"],
        "T1_sanity_direction": governing_dir,
        "T1_note": "SANITY value only: core-alone flexure+shear cantilever, fixed at ground, frame action of slab-column ignored. Earthquake division owns dynamic analysis.",
        "core_slenderness_H_over_depth": {"X": levels()[N_LEVELS - 1] / CORE[0], "Y": levels()[N_LEVELS - 1] / CORE[1]},
        "options": options(),
    }


def _json_default(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    raise TypeError(type(o))


if __name__ == "__main__":
    r = run()
    out = TOWER / "data" / "structure.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=1, default=_json_default))
    print(f"wrote {out}")
    print(f"W = {r['W_kN']:.0f} kN ({r['W_kN']/G_ACC:.0f} t); unit weight {r['unit_weight_kPa_per_floor']:.2f} kPa/floor")
    print(f"gravity at ground: G {r['gravity_totals_at_ground_kN']['G']:.0f} kN, Q {r['gravity_totals_at_ground_kN']['Q']:.0f} kN, core share G {r['gravity_totals_at_ground_kN']['core_share_G']:.2f}")
    for n, c in r["columns"].items():
        print(f"  {n:10s} A={c['trib_area_m2']:6.2f} fac={c['facade_length_m']:5.2f} G={c['G_base_kN']:7.0f} Q={c['Q_base_kN']:6.0f} "
              f"NEd={c['N_Ed_kN']:7.0f} (EC {c['N_EC_kN']:.0f} / LRFD {c['N_LRFD_kN']:.0f}) size {c['size_by_zone_m']} ratio {c['base_stress_ratio']:.2f}")
    k = r["core"]
    print(f"core: trib {k['trib_slab_area_m2']:.1f} m2, G {k['G_base_kN']:.0f} Q {k['Q_base_kN']:.0f} NEd {k['N_Ed_kN']:.0f} kN, "
          f"stress {k['base_axial_stress_MPa']:.1f} MPa, t {k['wall_t_zones_m']}, Ix {k['I_x_m4']:.1f} Iy {k['I_y_m4']:.1f} m4")
    for d in ("X", "Y"):
        a, b = r["lateral_cracked"][d], r["lateral_gross"][d]
        print(f"  {d}: T1 cracked {a['T1_s']:.2f} s (flex only {a['T1_flexure_only_s']:.2f}), T2 {a['T2_s']:.2f}; gross {b['T1_s']:.2f} s; "
              f"top defl {a['top_defl_mm_per_kN_per_m']:.2f} mm per kN/m")
    print("slab", r["slab"])
    print("masses", [round(m) for m in r["mass_t_per_level"]])
