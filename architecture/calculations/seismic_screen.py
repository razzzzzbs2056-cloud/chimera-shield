"""Seismic screening of the Chimera Pavilion concept (Level 2-3 of PROTOCOL.md).

SCOPE: configuration and sensitivity screening. NOT a code-compliant seismic design.
No hazard, site class, response-reduction factor or code clause is used, because the
jurisdiction and site are UNKNOWN. Demands are therefore reported per unit of elastic
spectral acceleration Sa (as a fraction of g) so they can be read against any hazard.

Units: kN, m, tonne (t = 1000 kg = kN*s^2/m). Mass in t, stiffness in kN/m.
Every input tagged [A] is an ASSUMPTION that a structural engineer must confirm.
Run:  python architecture/calculations/seismic_screen.py
"""
import csv
import math
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parent.parent / "data"
G = 9.81

# ---------------- inputs ----------------
LEVELS = np.array([5.5, 9.7, 13.9])        # m, floor levels L1, L2, L3(roof) [from design brief]
STOREY_H = np.array([5.5, 4.2, 4.2])       # m
PSI_QP = 0.3                               # [A] fraction of live load counted as seismic mass (code-specific)
LIVE_KPA = 4.0                             # [A] assembly live load (data/live_loads.csv)
FLOOR_AREA_M2 = 4200.0                     # takeoff value; known to be inconsistent with geometry (see report C-01)
E_CONC_KPA = 35e6                          # C40/50 Ecm, data/materials.csv
CRACK = 0.5                                # [A] cracked-section factor on EI
G_CONC_KPA = E_CONC_KPA / 2.4              # G ~ E / 2(1+nu), nu = 0.2
CORE_OUTER, CORE_T = 8.0, 0.4              # [A] m, box core 8 x 8 m, 0.4 m walls
NUM_CORES = 2


def seismic_masses() -> dict:
    """Lump superstructure mass (t) at L1..L3 from the quantity take-off."""
    mats = {r["material"]: r for r in csv.DictReader(open(DATA / "materials.csv", newline=""))}
    tot = {}
    for r in csv.DictReader(open(DATA / "quantity_takeoff.csv", newline="")):
        if r["element"].startswith(("Foundation", "Reinforcement (raft")):
            continue  # below the lateral base
        q = float(r["quantity"])
        kg = q * float(mats[r["material"]]["density_kg_m3"]) if r["unit"] == "m3" else q
        tot[r["element"]] = kg / 1000.0
    core_t = tot["Core walls and slabs"]
    trib = np.array([STOREY_H[0] / 2 + STOREY_H[1] / 2, STOREY_H[1] / 2 + STOREY_H[2] / 2, STOREY_H[2] / 2])
    core_levels = core_t * trib / LEVELS[-1]             # core mass by tributary height; lowest 1/2 storey goes to foundation
    other_t = sum(v for k, v in tot.items() if k != "Core walls and slabs")
    finishes_t = 1.0 * FLOOR_AREA_M2 / G                 # 1.0 kPa screed/finishes/services [A, data brief]
    live_t = PSI_QP * LIVE_KPA * FLOOR_AREA_M2 / G
    per_level = (other_t + finishes_t + live_t) / 3.0    # [A] equal split over 3 levels
    m = core_levels + per_level
    return {"m": m, "core_t": core_levels, "other_t": other_t, "finishes_t": finishes_t,
            "live_t": live_t, "W_kN": float(m.sum() * G)}


def core_properties() -> dict:
    i_box = (CORE_OUTER ** 4 - (CORE_OUTER - 2 * CORE_T) ** 4) / 12.0          # m^4 per core
    a_shear = 2 * CORE_OUTER * CORE_T                                           # two webs parallel to load
    return {"EI": CRACK * E_CONC_KPA * i_box * NUM_CORES, "GA": CRACK * G_CONC_KPA * a_shear * NUM_CORES,
            "I_total": i_box * NUM_CORES, "A_shear_total": a_shear * NUM_CORES}


def flexibility(x: np.ndarray, EI: float, GA: float | None) -> np.ndarray:
    """Tip-loaded cantilever flexibility at lumped points: bending (+ optional shear)."""
    n = len(x)
    F = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            lo, hi = min(x[i], x[j]), max(x[i], x[j])
            F[i, j] = lo ** 2 * (3 * hi - lo) / (6 * EI)
            if GA:
                F[i, j] += lo / GA
    return F


def modal(m: np.ndarray, F: np.ndarray) -> dict:
    """Eigen solution of K phi = w^2 M phi with K = F^-1. Returns periods, shapes, participation."""
    K = np.linalg.inv(F)
    M = np.diag(m)
    w2, phi = np.linalg.eig(np.linalg.inv(M) @ K)
    idx = np.argsort(w2.real)
    w2, phi = w2.real[idx], phi.real[:, idx]
    T = 2 * np.pi / np.sqrt(w2)
    ones = np.ones(len(m))
    gam, eff = [], []
    for k in range(len(m)):
        p = phi[:, k]
        L = p @ M @ ones
        Mk = p @ M @ p
        gam.append(L / Mk)
        eff.append(L ** 2 / Mk / m.sum())
    phi = phi / np.abs(phi[-1, :])                       # normalise roof = 1
    return {"T": T, "phi": phi, "gamma": np.array(gam), "eff_mass_ratio": np.array(eff), "K": K}


def demand_per_sa(res: dict, m: np.ndarray, x: np.ndarray, core: dict, sa_g: float) -> dict:
    """Elastic first-mode demand for spectral acceleration Sa (fraction of g). No force reduction."""
    p = res["phi"][:, 0]
    gam = (p @ m) / (p @ (m * p))
    f = gam * m * p * sa_g * G                            # kN storey forces
    V = f.sum()
    Mb = float(f @ x)
    drifts = np.diff(np.concatenate([[0.0], gam * p * sa_g * G / (2 * np.pi / res["T"][0]) ** 2])) / np.array(STOREY_H)
    web_area = core["A_shear_total"]
    return {"Sa_g": sa_g, "V_kN": float(V), "V_over_W": float(V / (m.sum() * G)), "M_base_kNm": Mb,
            "roof_disp_m": float(gam * p[-1] * sa_g * G / (2 * np.pi / res["T"][0]) ** 2),
            "max_drift_ratio": float(np.max(np.abs(drifts))), "core_shear_stress_MPa": float(V / web_area / 1000.0)}


def plan_torsion(elements: list[tuple[float, float, float, float]], cm: tuple[float, float],
                 mass: float, lx: float, ly: float, edge_y: float) -> dict:
    """Rigid-diaphragm plan check for loading in x. elements = (x, y, kx, ky) positions in m, stiffness in k-units.
    Returns centre of rigidity, eccentricity, rotational/translational frequency ratio and the
    edge displacement amplification at y = edge_y versus the average (at CM)."""
    kx = sum(e[2] for e in elements); ky = sum(e[3] for e in elements)
    xr = sum(e[0] * e[3] for e in elements) / ky
    yr = sum(e[1] * e[2] for e in elements) / kx
    ktheta = sum(e[2] * (e[1] - yr) ** 2 + e[3] * (e[0] - xr) ** 2 for e in elements)
    ex, ey = cm[0] - xr, cm[1] - yr
    Ij_cm = mass * (lx ** 2 + ly ** 2) / 12.0
    # 3-dof (ux, uy, theta about CM)
    K = np.zeros((3, 3))
    for (x, y, kxi, kyi) in elements:
        dx, dy = x - cm[0], y - cm[1]
        T = np.array([[1, 0, -dy], [0, 1, dx]])
        K += T.T @ np.diag([kxi, kyi]) @ T
    Mm = np.diag([mass, mass, Ij_cm])
    w2 = np.sort(np.linalg.eigvals(np.linalg.inv(Mm) @ K).real)
    periods = 2 * np.pi / np.sqrt(w2)
    # static force F=1 in x through CM
    u = np.linalg.solve(K, np.array([1.0, 0.0, 0.0]))
    d_edge = u[0] - u[2] * (edge_y - cm[1])
    d_avg = u[0]
    om = math.sqrt(ktheta / (Ij_cm + mass * (ex ** 2 + ey ** 2))) / math.sqrt(kx / mass)
    return {"CR": (xr, yr), "e_y": ey, "e_over_B": abs(ey) / ly, "omega_ratio": om,
            "periods_rel": periods / periods.max(), "edge_amplification": abs(d_edge / d_avg)}


def run() -> dict:
    ms = seismic_masses()
    m = ms["m"]
    core = core_properties()
    out = {"masses": ms, "core": core}
    for name, ga in (("flexure only", None), ("flexure + shear", core["GA"])):
        F = flexibility(LEVELS, core["EI"], ga)
        out[name] = modal(m, F)
    res = out["flexure + shear"]
    out["demand"] = [demand_per_sa(res, m, LEVELS, core, s) for s in (0.1, 0.2, 0.4, 0.8)]
    # sensitivity of T1 to cracking and mass
    sens = {}
    for c in (0.25, 0.5, 1.0):
        co = core_properties(); co["EI"] *= c / CRACK; co["GA"] *= c / CRACK
        sens[c] = modal(m, flexibility(LEVELS, co["EI"], co["GA"]))["T"][0]
    out["T1_vs_crack"] = sens
    # plan torsion: A = cores only (north corners); B = + two south lateral elements (half a core each)
    k = 1.0
    cores_xy = [(4.0, 4.0, k, k), (44.0, 4.0, k, k)]
    total_mass = float(m.sum())
    core_mass = float(ms["core_t"].sum())
    cm_y = (core_mass * 4.0 + (total_mass - core_mass) * 16.0) / total_mass
    cm = (24.0, cm_y)
    out["torsion_A"] = plan_torsion(cores_xy, cm, total_mass, 48.0, 32.0, 32.0)
    south = [(4.0, 28.0, 0.5 * k, 0.5 * k), (44.0, 28.0, 0.5 * k, 0.5 * k)]
    out["torsion_B"] = plan_torsion(cores_xy + south, cm, total_mass + 0.0, 48.0, 32.0, 32.0)
    out["cm"] = cm
    return out


def verify_with_opensees(m: np.ndarray, EI: float, GA: float) -> dict:
    """Independent check: the same cantilever in OpenSeesPy (elastic Timoshenko beam, lumped masses)."""
    import openseespy.opensees as ops
    results = {}
    for label, shear in (("EB", False), ("Timoshenko", True)):
        ops.wipe(); ops.model("basic", "-ndm", 2, "-ndf", 3)
        ys = [0.0] + list(LEVELS)
        for i, y in enumerate(ys):
            ops.node(i + 1, 0.0, y)
        ops.fix(1, 1, 1, 1)
        for i, mi in enumerate(m):
            ops.mass(i + 2, mi, 0.0, 0.0)       # horizontal translational mass only; tangent is vertical beam
        for i in range(2, 5):
            ops.fix(i, 0, 1, 0)                  # axial rigid: only lateral dofs carry mass
        ops.geomTransf("Linear", 1)
        E = 1.0e7; I = EI / E; A = 1.0e3        # EI fixed; A large so axial is rigid
        for i in range(3):
            if shear:
                # transverse is local y; set Avy so that G*Avy = GA
                ops.element("ElasticTimoshenkoBeam", i + 1, i + 1, i + 2, E, E / 2.4, A, I, GA / (E / 2.4), 1)
            else:
                ops.element("elasticBeamColumn", i + 1, i + 1, i + 2, A, E, I, 1)
        lam = ops.eigen("-fullGenLapack", 6)     # dense solver; massless rotational dofs give inf eigenvalues
        results[label] = sorted(2 * math.pi / math.sqrt(l) for l in lam if 0 < l < 1e12)[-3:][::-1]
        ops.wipe()
    return results


if __name__ == "__main__":
    r = run()
    ms = r["masses"]
    print(f"Seismic mass by level (t): {np.round(ms['m'],0)}  total {ms['m'].sum():.0f} t, W = {ms['W_kN']/1000:.1f} MN")
    print(f"Core: EI = {r['core']['EI']:.3e} kN.m2 (cracked x{CRACK}), GA = {r['core']['GA']:.3e} kN")
    for k in ("flexure only", "flexure + shear"):
        print(f"{k}: T = {np.round(r[k]['T'],3)} s; eff. mass ratio = {np.round(r[k]['eff_mass_ratio'],2)}")
    print("T1 vs cracking factor:", {c: round(t, 3) for c, t in r["T1_vs_crack"].items()})
    print("Elastic first-mode demand per Sa (no force reduction, no code):")
    for d in r["demand"]:
        print(f"  Sa={d['Sa_g']:.1f}g  V={d['V_kN']/1000:5.1f} MN  V/W={d['V_over_W']:.2f}  Mbase={d['M_base_kNm']/1000:6.1f} MN.m  "
              f"drift={d['max_drift_ratio']*100:.2f}%  core shear stress={d['core_shear_stress_MPa']:.2f} MPa")
    print(f"Mass centre y = {r['cm'][1]:.1f} m")
    for k in ("torsion_A", "torsion_B"):
        t = r[k]
        print(f"{k}: CR=({t['CR'][0]:.1f},{t['CR'][1]:.1f}) e_y={t['e_y']:.1f} m ({t['e_over_B']*100:.0f}% of 32 m) "
              f"omega_theta/omega_x={t['omega_ratio']:.2f} south-edge amplification={t['edge_amplification']:.2f}")
    try:
        ver = verify_with_opensees(ms["m"], r["core"]["EI"], r["core"]["GA"])
        print("OpenSeesPy T (s): EB", np.round(ver["EB"], 4), " Timoshenko", np.round(ver["Timoshenko"], 4))
    except Exception as e:
        print("OpenSeesPy verification skipped:", type(e).__name__, e)
