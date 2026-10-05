"""Division 4 (Earthquake): dynamic analysis of the 30-storey reference tower (concept feasibility).

Pipeline (architecture/seismic/pipeline.py house style)
  Agent A    : OpenSeesPy 3-D stick model of the RC core (ElasticTimoshenkoBeam, zone-varying section,
               31 lumped masses with X, Y and plan-rotational inertia), eigen solution, modal response per unit Sa.
  Hand model : exact stepped-cantilever flexibility (analytic integration) + numpy eigen solve, and a
               closed-form uniform cantilever (flexure 1.875^2 eigenvalue, shear 4L sqrt(m/GA), Southwell sum).
  Interpreter: plausibility checks (mass sums, period ordering, units, equilibrium, sanity values).
  Agent B    : Rayleigh quotient (one Stodola step from an assumed (z/H)^1.5 inertial pattern) with section
               properties rebuilt from verification/structure_inputs_for_B.json, numerical moment-area deflection.
  Agent C    : tools/verify_compare.py -> PROCEED / INVESTIGATE.

Units: kN, m, t, s (so t*m/s2 = kN; kPa = kN/m2). g = 9.81 m/s2.
Hazard, site class and jurisdiction are UNKNOWN: every demand is per unit spectral acceleration Sa (g)
(5 %-damped elastic, no behaviour/response-modification factor, no code procedure). Illustrations at
Sa = 0.1 / 0.2 / 0.4 g only. Not a code check. Not for construction.

Run:  python architecture/tower/calcs/seismic_tower.py   -> architecture/tower/data/seismic.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

TOWER = Path(__file__).resolve().parent.parent            # architecture/tower
ARCH = TOWER.parent                                        # architecture
sys.path.insert(0, str(ARCH / "tools"))
from verify_compare import compare  # noqa: E402

G_ACC = 9.81
STRUCT = json.loads((TOWER / "data" / "structure.json").read_text())
B_INPUTS = json.loads((TOWER / "verification" / "structure_inputs_for_B.json").read_text())

Z = np.array(STRUCT["levels"]["z_m"], dtype=float)         # 31 levels, L1 .. L30 roof slab, plant
H_STOREY = np.diff(np.concatenate([[0.0], Z]))
M_LEVEL = np.array(STRUCT["mass_t_per_level"], dtype=float)
W_LEVEL = np.array(STRUCT["W_level_kN"], dtype=float)
E_KPA = STRUCT["E_concrete_MPa"] * 1000.0
NU = STRUCT["assumptions"]["poisson"]
G_KPA = E_KPA / (2 * (1 + NU))
CRACK = STRUCT["cracked_factor"]
PLATE = STRUCT["plate_m"]                                  # [30, 24]
CORE_OUT = STRUCT["core"]["outer_dims_m"]                  # [12, 8]
CORE_BOX = STRUCT["core"]["box_m"]                         # [x0, y0, x1, y1]
CORE_C = ((CORE_BOX[0] + CORE_BOX[2]) / 2, (CORE_BOX[1] + CORE_BOX[3]) / 2)
SA_ILLUSTRATIVE = [0.1, 0.2, 0.4]
# direction -> (section key for bending, shear-area key). I_x (about x) resists sway in Y (structure.json axis_note)
DIRS = {"X": ("I_y_m4", "A_shear_X_m2"), "Y": ("I_x_m4", "A_shear_Y_m2")}
TOL = {"default": {"rel": 0.05}, "T1_X_s": {"rel": 0.10}, "T1_Y_s": {"rel": 0.10}}  # as pipeline.py
ASSUMED = {
    "base": "fixed at ground slab z = 0 (as Division 3); basement box, foundation and soil flexibility (SSI) ignored",
    "core": "closed 12 x 8 m tube, openings ignored, internal cross walls excluded from stiffness (Division 3 sections)",
    "cracked_factor": "0.5 on EI, GA and GJ of the core walls (generic; sensitivity 0.35 / 0.5 / 0.7 and gross 1.0)",
    "torsion_J": "Bredt closed thin-walled tube J = 4 A0^2 t / p on wall centrelines (upper bound: openings ignored)",
    "mass": "Division 3 seismic mass (dead + 0.3 live), lumped at the 31 levels at plan centre (15, 12) m",
    "rotational_mass": "I_theta = m (Lx^2 + Ly^2)/12 per level (uniform plate; plant level uses the 12 x 8 core footprint)",
    "diaphragm": "rigid in plane (single stick node per level)",
    "spectrum": "constant Sa for all modes of the SRSS (a real spectrum descends at long period: Sa(T1~4.5 s) << plateau)",
    "damping": "5 % implied by the (unknown) design spectrum; no damping in the eigen solution",
    "gravity_for_p_delta": "W_level (dead + 0.3 live) from Division 3, applied as axial load on the stick",
}


# ----------------------------------------------------------------------------------------------- inputs
def zone_of(level: int) -> str:
    for k in STRUCT["core"]["section_by_zone"]:
        a, b = (int(v) for v in k.split("-"))
        if a <= level <= b:
            return k
    raise ValueError(level)


def bredt_J(t: float, bx: float = CORE_OUT[0], by: float = CORE_OUT[1]) -> float:
    a0 = (bx - t) * (by - t); p = 2 * ((bx - t) + (by - t))
    return 4 * a0 ** 2 * t / p


def element_props(cracked: float = CRACK) -> list[dict]:
    """Element k (k = 1..31) spans level k-1 -> k and takes the section of level k's zone (as Division 3)."""
    out = []
    for lv in range(1, len(Z) + 1):
        s = STRUCT["core"]["section_by_zone"][zone_of(lv)]
        out.append({
            "zone": zone_of(lv), "t": s["t_m"], "A": s["A_m2"],
            "EI": {d: cracked * E_KPA * s[DIRS[d][0]] for d in DIRS},
            "GA": {d: cracked * G_KPA * s[DIRS[d][1]] for d in DIRS},
            "GJ": cracked * G_KPA * bredt_J(s["t_m"]),
        })
    return out


def rot_inertia(m: np.ndarray) -> np.ndarray:
    r2 = np.full(len(m), (PLATE[0] ** 2 + PLATE[1] ** 2) / 12.0)
    r2[-1] = (CORE_OUT[0] ** 2 + CORE_OUT[1] ** 2) / 12.0      # plant level sits on the core only
    return m * r2


# ------------------------------------------------------------------- optional perimeter frame (variant)
FRAME = {"slab_eff_width_frac": 0.35, "slab_crack": 0.33, "col_crack": 0.7,
         "note": "VARIANT (JUDGMENT): equivalent slab-beam frame, effective slab width 0.35 x tributary width, "
                 "cracked slab 0.33 Ig, columns 0.7 Ig, Muto D-values; flat-plate frames are flexible and their "
                 "connections are drift-sensitive (punching), so this is an upper-bound-style estimate of stiffening"}


def frame_storey_stiffness() -> dict:
    """Storey lateral stiffness (kN/m) of the 14 perimeter columns + flat-plate slab strips, per direction (Muto D)."""
    t_s = STRUCT["slab_thickness_m"]; cols = STRUCT["columns"]
    Lx, Ly = PLATE
    out = {"X": np.zeros(len(Z)), "Y": np.zeros(len(Z)), "CR": {}}
    kx_sum = ky_sum = 0.0; kx_y = ky_x = 0.0
    for lv in range(1, len(Z)):          # storeys 1..30 (no columns in the plant storey)
        h = H_STOREY[lv - 1]
        for name, c in cols.items():
            b = c["size_by_zone_m"][zone_of(lv)]
            Ic = FRAME["col_crack"] * b ** 4 / 12
            for d in ("X", "Y"):
                on_face_parallel = (c["y_m"] in (0.0, Ly)) if d == "X" else (c["x_m"] in (0.0, Lx))
                if on_face_parallel:
                    pos = c["x_m"] if d == "X" else c["y_m"]
                    line = sorted(cc["x_m"] if d == "X" else cc["y_m"] for cc in cols.values()
                                  if (cc["y_m"] == c["y_m"] if d == "X" else cc["x_m"] == c["x_m"]))
                    i = line.index(pos)
                    spans = [line[j + 1] - line[j] for j in (i - 1, i) if 0 <= j < len(line) - 1]
                    trib_w = (CORE_BOX[1] if d == "X" else CORE_BOX[0])     # distance facade -> core face
                else:   # perpendicular face: slab strip spans to the core face
                    spans = [CORE_BOX[0] if d == "X" else CORE_BOX[1]]
                    trib_w = 7.5 if d == "X" else 8.0
                    if c["type"] == "corner":
                        continue                                         # counted on its parallel face
                bw = FRAME["slab_eff_width_frac"] * trib_w
                Ib = FRAME["slab_crack"] * bw * t_s ** 3 / 12
                Kc = Ic / h; sumKb = sum(Ib / L for L in spans)
                kbar = sumKb / Kc                       # (2 beams at top + 2 at bottom) / (2 Kc)
                a = (0.5 + kbar) / (2 + kbar) if lv == 1 else kbar / (2 + kbar)
                D = a * 12 * E_KPA * Ic / h ** 3
                out[d][lv - 1] += D
                if lv == 1:
                    if d == "X":
                        kx_sum += D; kx_y += D * c["y_m"]
                    else:
                        ky_sum += D; ky_x += D * c["x_m"]
    out["CR"] = {"x": ky_x / ky_sum, "y": kx_y / kx_sum}
    return out


# --------------------------------------------------------------------------------------- OpenSees (A)
def stick_modal(z, m, props, Itheta=None, nmodes=None, frame_k=None, gravity=None, pdelta=False,
                static_loads=None, element="timoshenko") -> dict:
    """3-D lumped-mass stick in OpenSeesPy. Vertical axis = Z. Core nodes 1..n+1 (1 = fixed base).
    props: list of dicts with EI{X,Y}, GA{X,Y}, GJ, A per element. frame_k: optional {"X": k[], "Y": k[]} storey
    stiffnesses added in parallel (separate translational stick tied by equalDOF). gravity: kN per level (axial).
    static_loads: optional {"X": f[], "Y": f[]} lateral nodal loads -> displacements and base reactions.
    element: "timoshenko" (ElasticTimoshenkoBeam, reference) or "eb" (elasticBeamColumn, flexure only). Note: in
    OpenSeesPy 3.7 ElasticTimoshenkoBeam does not add the PDelta geometric stiffness (tested: T unchanged), so
    P-Delta eigen runs use the "eb" pair (Linear vs PDelta transformation) and report the ratio."""
    import openseespy.opensees as ops
    z = np.asarray(z, float); m = np.asarray(m, float); n = len(z)
    Itheta = np.zeros(n) if Itheta is None else np.asarray(Itheta, float)
    ops.wipe(); ops.model("basic", "-ndm", 3, "-ndf", 6)
    xs, ys = CORE_C
    zs = np.concatenate([[0.0], z])
    for i, zi in enumerate(zs):
        ops.node(i + 1, xs, ys, float(zi))
    ops.fix(1, 1, 1, 1, 1, 1, 1)
    for i in range(n):
        ops.mass(i + 2, m[i], m[i], 0.0, 0.0, 0.0, max(Itheta[i], 0.0))
        if Itheta[i] <= 0:
            ops.fix(i + 2, 0, 0, 0, 0, 0, 1)
    # local x = global Z; vecxz = global X  ->  local y = -global Y, local z = global X
    # bending with displacement along local z (global X) uses Iy; along local y (global Y) uses Iz
    ops.geomTransf("PDelta" if pdelta else "Linear", 1, 1.0, 0.0, 0.0)
    E = E_KPA; Gm = G_KPA
    for k, p in enumerate(props):
        Iy = p["EI"]["X"] / E; Iz = p["EI"]["Y"] / E
        Avz = p["GA"]["X"] / Gm; Avy = p["GA"]["Y"] / Gm
        J = p["GJ"] / Gm
        if element == "eb":
            ops.element("elasticBeamColumn", k + 1, k + 1, k + 2, p["A"], E, Gm, J, Iy, Iz, 1)
        else:
            ops.element("ElasticTimoshenkoBeam", k + 1, k + 1, k + 2, E, Gm, p["A"], J, Iy, Iz, Avy, Avz, 1)
    if frame_k is not None:
        ops.geomTransf("Linear", 2, 1.0, 0.0, 0.0)
        base_f = 1001
        ops.node(base_f, xs, ys, 0.0); ops.fix(base_f, 1, 1, 1, 1, 1, 1)
        for i in range(n):
            nf = base_f + i + 1
            ops.node(nf, xs, ys, float(z[i])); ops.fix(nf, 0, 0, 1, 1, 1, 1)
            ops.equalDOF(i + 2, nf, 1, 2)
        for i in range(n):
            h = zs[i + 1] - zs[i]
            kX = max(frame_k["X"][i], 1e-6); kY = max(frame_k["Y"][i], 1e-6)
            Iy = kX * h ** 3 / (12 * E); Iz = kY * h ** 3 / (12 * E)
            ops.element("elasticBeamColumn", 2000 + i, base_f + i, base_f + i + 1, 1.0, E, Gm, 1.0, Iy, Iz, 2)
    ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("FullGeneral")
    ops.test("NormDispIncr", 1e-10, 10); ops.algorithm("Linear")
    if gravity is not None:
        ops.timeSeries("Constant", 1); ops.pattern("Plain", 1, 1)
        for i in range(n):
            ops.load(i + 2, 0.0, 0.0, -float(gravity[i]), 0.0, 0.0, 0.0)
        ops.integrator("LoadControl", 1.0); ops.analysis("Static"); ops.analyze(1)
        ops.loadConst("-time", 0.0)
    ndof = 2 * n + int(np.count_nonzero(Itheta > 0))
    nm = ndof if nmodes is None else min(nmodes, ndof)
    lam = np.array(ops.eigen("-fullGenLapack", nm))
    modes = []
    for k in range(nm):
        if not (0 < lam[k] < 1e12):
            continue
        phi = np.array([[ops.nodeEigenvector(i + 2, k + 1, d) for d in (1, 2, 6)] for i in range(n)])
        modes.append({"omega2": float(lam[k]), "phi": phi})
    out = {"modes": modes}
    if static_loads is not None:
        ops.wipe()                      # static case rebuilt below to keep the eigen model clean
        out["static"] = {}
        for d, f in static_loads.items():
            res = stick_static(z, props, d, f, frame_k)
            out["static"][d] = res
    ops.wipe()
    return out


def stick_static(z, props, d, f, frame_k=None) -> dict:
    """Linear static OpenSees run: lateral loads f (kN) in direction d at the levels -> u (m), base shear/moment."""
    import openseespy.opensees as ops
    z = np.asarray(z, float); n = len(z)
    ops.wipe(); ops.model("basic", "-ndm", 3, "-ndf", 6)
    xs, ys = CORE_C; zs = np.concatenate([[0.0], z])
    for i, zi in enumerate(zs):
        ops.node(i + 1, xs, ys, float(zi))
    ops.fix(1, 1, 1, 1, 1, 1, 1)
    ops.geomTransf("Linear", 1, 1.0, 0.0, 0.0)
    for k, p in enumerate(props):
        ops.element("ElasticTimoshenkoBeam", k + 1, k + 1, k + 2, E_KPA, G_KPA, p["A"], p["GJ"] / G_KPA,
                    p["EI"]["X"] / E_KPA, p["EI"]["Y"] / E_KPA, p["GA"]["Y"] / G_KPA, p["GA"]["X"] / G_KPA, 1)
    if frame_k is not None:
        ops.geomTransf("Linear", 2, 1.0, 0.0, 0.0)
        ops.node(1001, xs, ys, 0.0); ops.fix(1001, 1, 1, 1, 1, 1, 1)
        for i in range(n):
            ops.node(1002 + i, xs, ys, float(z[i])); ops.fix(1002 + i, 0, 0, 1, 1, 1, 1)
            ops.equalDOF(i + 2, 1002 + i, 1, 2)
            h = zs[i + 1] - zs[i]
            ops.element("elasticBeamColumn", 2000 + i, 1001 + i, 1002 + i, 1.0, E_KPA, G_KPA, 1.0,
                        max(frame_k["X"][i], 1e-6) * h ** 3 / (12 * E_KPA),
                        max(frame_k["Y"][i], 1e-6) * h ** 3 / (12 * E_KPA), 2)
    ops.timeSeries("Linear", 1); ops.pattern("Plain", 1, 1)
    dof = 1 if d == "X" else 2
    for i in range(n):
        v = [0.0] * 6; v[dof - 1] = float(f[i]); ops.load(i + 2, *v)
    ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("FullGeneral")
    ops.test("NormDispIncr", 1e-10, 10); ops.algorithm("Linear"); ops.integrator("LoadControl", 1.0)
    ops.analysis("Static"); ops.analyze(1); ops.reactions()
    u = np.array([ops.nodeDisp(i + 2, dof) for i in range(n)])
    R = -ops.nodeReaction(1, dof) - (ops.nodeReaction(1001, dof) if frame_k is not None else 0.0)
    Mb = ops.nodeReaction(1, 5 if d == "X" else 4) + (ops.nodeReaction(1001, 5 if d == "X" else 4) if frame_k is not None else 0.0)
    ops.wipe()
    return {"u": u, "V_base": float(R), "M_base_reaction": float(abs(Mb))}


def classify(modes: list[dict], m: np.ndarray, Ith: np.ndarray) -> dict:
    """Generalised mass, participation and direction of each mode."""
    Mtot = m.sum(); Itot = Ith.sum()
    out = []
    for md in modes:
        phi = md["phi"]
        Mn = float(np.sum(m * phi[:, 0] ** 2) + np.sum(m * phi[:, 1] ** 2) + np.sum(Ith * phi[:, 2] ** 2))
        L = {"X": float(np.sum(m * phi[:, 0])), "Y": float(np.sum(m * phi[:, 1])), "RZ": float(np.sum(Ith * phi[:, 2]))}
        ratio = {"X": L["X"] ** 2 / Mn / Mtot, "Y": L["Y"] ** 2 / Mn / Mtot,
                 "RZ": (L["RZ"] ** 2 / Mn / Itot) if Itot > 0 else 0.0}
        energy = {"X": np.sum(m * phi[:, 0] ** 2), "Y": np.sum(m * phi[:, 1] ** 2), "RZ": np.sum(Ith * phi[:, 2] ** 2)}
        dom = max(energy, key=energy.get)
        T = 2 * math.pi / math.sqrt(md["omega2"])
        out.append({"T": T, "omega2": md["omega2"], "phi": phi, "Mn": Mn, "L": L, "ratio": ratio, "dir": dom})
    out.sort(key=lambda r: -r["T"])
    return {"all": out, **{d: [r for r in out if r["dir"] == d] for d in ("X", "Y", "RZ")}}


# -------------------------------------------------------------------------------- hand model (exact)
def flexibility_exact(z, EI, GA) -> np.ndarray:
    """Stepped Timoshenko cantilever, fixed at 0. EI, GA per element (constant between levels).
    delta_ij = sum over segments [a,b] below min(zi,zj) of int (zi-s)(zj-s)/EI ds + (b-a)/GA (analytic)."""
    z = np.asarray(z, float); zs = np.concatenate([[0.0], z]); n = len(z)
    F = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            zm = min(z[i], z[j]); f = 0.0
            for k in range(n):
                a, b = zs[k], min(zs[k + 1], zm)
                if b <= a:
                    break
                P = lambda s: z[i] * z[j] * s - (z[i] + z[j]) * s ** 2 / 2 + s ** 3 / 3
                f += (P(b) - P(a)) / EI[k] + (b - a) / GA[k]
            F[i, j] = F[j, i] = f
    return F


def hand_modal(m, props, d) -> dict:
    EI = [p["EI"][d] for p in props]; GA = [p["GA"][d] for p in props]
    F = flexibility_exact(Z, EI, GA)
    K = np.linalg.inv(F)
    Mh = np.diag(1 / np.sqrt(m))
    w2, v = np.linalg.eigh(Mh @ K @ Mh)
    phi = Mh @ v
    T = 2 * math.pi / np.sqrt(w2)
    L = phi.T @ m; Mn = np.einsum("ij,i,ij->j", phi, m, phi)
    ratio = L ** 2 / Mn / m.sum()
    return {"T": T, "ratio": ratio, "F": F}


def closed_form(m, props, d) -> dict:
    """Uniform cantilever with height-averaged EI, GA and total mass smeared over H (textbook)."""
    H = Z[-1]; h = H_STOREY
    EI = float(np.sum([p["EI"][d] * hk for p, hk in zip(props, h)]) / H)
    GA = float(np.sum([p["GA"][d] * hk for p, hk in zip(props, h)]) / H)
    mbar = m.sum() / H
    Tf = 2 * math.pi / 1.875104 ** 2 * math.sqrt(mbar * H ** 4 / EI)
    Ts = 4 * H * math.sqrt(mbar / GA)
    return {"Tf": Tf, "Ts": Ts, "T_southwell": math.sqrt(Tf ** 2 + Ts ** 2), "EI_avg": EI, "GA_avg": GA, "mbar": mbar}


# ------------------------------------------------------------------------------ response per unit Sa
def mode_response(md: dict, d: int, m: np.ndarray) -> dict:
    """Mode md in direction column d (0 = X, 1 = Y), per unit Sa = 1 g. Returns floor u (m), storey drift ratios,
    storey shears (kN), base shear and moment."""
    phi = md["phi"][:, d]; key = "X" if d == 0 else "Y"
    Gam = md["L"][key] / md["Mn"]
    Sa = 1.0 * G_ACC
    Sd = Sa / md["omega2"]
    u = Gam * phi * Sd
    f = m * Gam * phi * Sa                         # kN
    Vst = np.cumsum(f[::-1])[::-1]                 # storey shear, storey k carries levels >= k
    drift = np.diff(np.concatenate([[0.0], u])) / H_STOREY
    M = float(np.sum(f * Z))
    return {"T": md["T"], "Gamma": Gam, "Sd_per_g_m": Sd, "u": u, "f": f, "Vst": Vst, "drift": drift,
            "V": float(f.sum()), "M": M, "roof": float(u[29]), "top": float(u[-1])}


def srss(rs: list[dict], key: str):
    return np.sqrt(np.sum([np.asarray(r[key]) ** 2 for r in rs], axis=0))


def p_delta_theta(r_drift, r_Vst, W) -> np.ndarray:
    """theta_k = P_k Delta_k / (V_k h_k), elastic (independent of Sa). P_k = gravity above storey k."""
    P = np.cumsum(W[::-1])[::-1]
    Delta = np.asarray(r_drift) * H_STOREY
    return P * Delta / (np.asarray(r_Vst) * H_STOREY)


# --------------------------------------------------------------------------------- agent B (Rayleigh)
def agent_b() -> dict:
    """Independent of A's eigen solution and section table: rebuild the closed-tube section from the B inputs
    (outer dims and wall thickness zones), deflect under an assumed inertial pattern m g (z/H)^1.5 by numerical
    moment-area integration (curvature M/EI twice + V/GA once), then Rayleigh quotient on that deflection.
    Masses are Division 3's (shared input)."""
    bx, by = B_INPUTS["core"]["outer_dims_m"]; tz = B_INPUTS["core"]["wall_t_zones_m"]
    zl = np.array(B_INPUTS["levels_z_m"]); cr = B_INPUTS["cracked_factor"]
    E = B_INPUTS["E_concrete_MPa"] * 1e3; Gm = E / 2.4
    m = M_LEVEL

    def t_at(s):
        lv = int(np.searchsorted(zl, s - 1e-9)) + 1
        for k, v in tz.items():
            a, b = (int(q) for q in k.split("-"))
            if a <= lv <= b:
                return v
    out = {}
    s = np.linspace(0.0, zl[-1], 20001); ds = s[1] - s[0]
    tt = np.array([t_at(v) for v in s])
    I_about_x = (bx * by ** 3 - (bx - 2 * tt) * (by - 2 * tt) ** 3) / 12      # sway Y
    I_about_y = (by * bx ** 3 - (by - 2 * tt) * (bx - 2 * tt) ** 3) / 12      # sway X
    for d, I, Av in (("X", I_about_y, 2 * bx * tt), ("Y", I_about_x, 2 * by * tt)):
        EI = cr * E * I; GA = cr * Gm * Av
        F = m * G_ACC * (zl / zl[-1]) ** 1.5
        V = np.array([F[zl > v].sum() for v in s])
        Mo = np.array([np.sum(F[zl > v] * (zl[zl > v] - v)) for v in s])
        kappa = Mo / EI; gam = V / GA
        rot = np.concatenate([[0.0], np.cumsum((kappa[1:] + kappa[:-1]) / 2) * ds])
        sh = np.concatenate([[0.0], np.cumsum((gam[1:] + gam[:-1]) / 2) * ds])
        defl = np.concatenate([[0.0], np.cumsum((rot[1:] + rot[:-1]) / 2) * ds]) + sh
        u = np.interp(zl, s, defl)
        w2 = (F @ u) / ((m * u) @ u)
        L = (m * u).sum(); Mk = (m * u * u).sum()
        out[f"T1_{d}_s"] = 2 * math.pi / math.sqrt(w2)
        out[f"mode1_mass_ratio_{d}"] = L * L / Mk / m.sum()
        out[f"V1_{d}_kN_per_g"] = L * L / Mk * G_ACC
    out["total_mass_t"] = float(m.sum())
    return out


# ----------------------------------------------------------------------------------------------- run
def analyse(cracked=CRACK, mass_factor=1.0, frame=False, pdelta=False, element="timoshenko") -> dict:
    props = element_props(cracked)
    m = M_LEVEL * mass_factor; Ith = rot_inertia(m)
    fk = frame_storey_stiffness() if frame else None
    os_ = stick_modal(Z, m, props, Ith, frame_k=fk, gravity=(W_LEVEL * mass_factor) if pdelta else None, pdelta=pdelta,
                      element=element)
    cl = classify(os_["modes"], m, Ith)
    return {"props": props, "m": m, "Ith": Ith, "cl": cl, "frame_k": fk}


def summarise_modes(cl, n=3):
    return {d: [{"T_s": r["T"], "mass_ratio": r["ratio"][d]} for r in cl[d][:n]] for d in ("X", "Y", "RZ")}


def run() -> dict:
    base = analyse()
    m, cl, props = base["m"], base["cl"], base["props"]
    res = {"_meta": {
        "script": "architecture/tower/calcs/seismic_tower.py", "level": "L4 (linear modal / response-spectrum style, parametric)",
        "status": "SIMULATION (verified against hand model, closed form and independent Rayleigh; see checks). "
                  "CONCEPT. Not for construction. Hazard UNKNOWN: per unit Sa only.",
        "units": "m, kN, t, s; Sa in g", "opensees": _ops_version(), "assumptions": ASSUMED}}
    res["inputs"] = {"z_m": Z.tolist(), "mass_t": m.tolist(), "total_mass_t": float(m.sum()),
                     "W_kN": float(W_LEVEL.sum()), "E_MPa": E_KPA / 1e3, "G_MPa": G_KPA / 1e3, "cracked_factor": CRACK,
                     "section_by_zone": STRUCT["core"]["section_by_zone"],
                     "J_bredt_m4_by_zone": {k: bredt_J(v["t_m"]) for k, v in STRUCT["core"]["section_by_zone"].items()}}
    # modal
    res["modal"] = {d: [{"T_s": r["T"], "mass_ratio": r["ratio"][d], "Gamma": r["L"][d] / r["Mn"],
                         "shape": (r["phi"][:, {"X": 0, "Y": 1, "RZ": 2}[d]] /
                                   r["phi"][-1, {"X": 0, "Y": 1, "RZ": 2}[d]]).tolist()} for r in cl[d][:3]]
                    for d in ("X", "Y", "RZ")}
    res["modal"]["first_6_overall"] = [{"T_s": r["T"], "dir": r["dir"], "ratio_X": r["ratio"]["X"],
                                        "ratio_Y": r["ratio"]["Y"], "ratio_RZ": r["ratio"]["RZ"]} for r in cl["all"][:6]]
    res["modal"]["sum_all_modes"] = {d: float(sum(r["ratio"][d] for r in cl["all"])) for d in ("X", "Y", "RZ")}
    res["modal"]["sum_first3"] = {d: float(sum(r["ratio"][d] for r in cl[d][:3])) for d in ("X", "Y", "RZ")}
    res["modal"]["mode_shape_nodes"] = "normalised to 1.0 at the plant level (z = 99.4 m); index = level L1..plant"
    # hand + closed form
    res["hand"] = {}
    for d in ("X", "Y"):
        h = hand_modal(m, props, d); c = closed_form(m, props, d)
        res["hand"][d] = {"T_s": h["T"][:3].tolist(), "ratio": h["ratio"][:3].tolist(), "closed_form": c,
                          "structure_sanity_T1_s": STRUCT["lateral_cracked"][d]["T1_s"],
                          "structure_sanity_T2_s": STRUCT["lateral_cracked"][d]["T2_s"]}
    # sensitivity
    sens = {"cracked": {}, "mass": {}}
    for cf in (0.35, 0.5, 0.7, 1.0):
        c2 = analyse(cracked=cf)["cl"]; sens["cracked"][str(cf)] = {d: c2[d][0]["T"] for d in ("X", "Y", "RZ")}
    for mf in (0.9, 1.0, 1.1):
        c2 = analyse(mass_factor=mf)["cl"]; sens["mass"][str(mf)] = {d: c2[d][0]["T"] for d in ("X", "Y", "RZ")}
    res["sensitivity_T1_s"] = sens
    # frame variant
    fv = analyse(frame=True)
    fk = fv["frame_k"]
    res["frame_variant"] = {"note": FRAME["note"], "params": {k: v for k, v in FRAME.items() if k != "note"},
                            "storey_k_kN_per_m_L1_L11_L21": {d: [float(fk[d][0]), float(fk[d][10]), float(fk[d][20])] for d in ("X", "Y")},
                            "modes": summarise_modes(fv["cl"])}
    # response per unit Sa (core-only, reference)
    resp = {}
    for d, col in (("X", 0), ("Y", 1)):
        rs = [mode_response(r, col, m) for r in cl[d][:3]]
        r1 = rs[0]
        V_s = srss(rs, "Vst"); dr_s = srss(rs, "drift"); u_s = srss(rs, "u")
        M_s = float(np.sqrt(sum(r["M"] ** 2 for r in rs)))
        th1 = p_delta_theta(np.abs(r1["drift"]), np.abs(r1["Vst"]), W_LEVEL)
        ths = p_delta_theta(dr_s, V_s, W_LEVEL)
        resp[d] = {
            "per_mode_per_g": [{"T_s": r["T"], "Gamma": r["Gamma"], "Sd_m_per_g": r["Sd_per_g_m"], "V_kN": abs(r["V"]),
                                "M_kNm": abs(r["M"]), "roof_m": abs(r["roof"]), "max_drift": float(np.max(np.abs(r["drift"]))),
                                "max_drift_storey": int(np.argmax(np.abs(r["drift"]))) + 1} for r in rs],
            "mode1_per_g": {"V_kN": abs(r1["V"]), "V_over_W": abs(r1["V"]) / W_LEVEL.sum(), "M_kNm": abs(r1["M"]),
                            "roof_m": abs(r1["roof"]), "max_drift": float(np.max(np.abs(r1["drift"]))),
                            "max_drift_storey": int(np.argmax(np.abs(r1["drift"]))) + 1,
                            "roof_m_per_m_Sd": abs(r1["roof"]) / r1["Sd_per_g_m"],
                            "max_drift_per_m_Sd": float(np.max(np.abs(r1["drift"]))) / r1["Sd_per_g_m"]},
            "srss3_const_Sa_per_g": {"V_kN": float(V_s[0]), "V_over_W": float(V_s[0]) / W_LEVEL.sum(), "M_kNm": M_s,
                                     "roof_m": float(u_s[29]), "max_drift": float(dr_s.max()),
                                     "max_drift_storey": int(np.argmax(dr_s)) + 1},
            "drift_profile_mode1_per_g": np.abs(r1["drift"]).tolist(),
            "storey_shear_srss_per_g_kN": V_s.tolist(),
            "p_delta_theta": {"mode1_max": float(th1.max()), "mode1_storey": int(np.argmax(th1)) + 1,
                              "srss_max": float(ths.max()), "srss_storey": int(np.argmax(ths)) + 1,
                              "note": "elastic theta = P Delta / (V h); independent of Sa in a linear analysis; "
                                      "code formats use design drift (amplified) over design shear (reduced): verify"},
            "illustrative": [{"Sa_g": sa, "V1_MN": abs(r1["V"]) * sa / 1e3, "M1_MNm": abs(r1["M"]) * sa / 1e3,
                              "roof1_m": abs(r1["roof"]) * sa, "drift1": float(np.max(np.abs(r1["drift"]))) * sa,
                              "Vsrss_MN": float(V_s[0]) * sa / 1e3, "drift_srss": float(dr_s.max()) * sa}
                             for sa in SA_ILLUSTRATIVE],
        }
        # equilibrium: OpenSees static under mode-1 force pattern must reproduce u1 and base shear
        st = stick_static(Z, props, d, r1["f"])
        resp[d]["equilibrium_mode1"] = {"V_applied_kN": float(r1["f"].sum()), "V_reaction_kN": st["V_base"],
                                        "M_applied_kNm": abs(r1["M"]), "M_reaction_kNm": st["M_base_reaction"],
                                        "roof_static_m": float(st["u"][29]), "roof_modal_m": float(r1["roof"])}
    res["response_per_unit_Sa"] = resp
    # P-Delta via OpenSees geometric stiffness (gravity applied, PDelta transformation)
    pdl = analyse(pdelta=True, element="eb")["cl"]; lin = analyse(element="eb")["cl"]
    res["p_delta_opensees"] = {d: {"T1_PDelta_s": pdl[d][0]["T"], "T1_linear_s": lin[d][0]["T"],
                                   "T1_timoshenko_s": cl[d][0]["T"],
                                   "period_elongation": pdl[d][0]["T"] / lin[d][0]["T"] - 1,
                                   "theta_equiv": 1 - (lin[d][0]["T"] / pdl[d][0]["T"]) ** 2,
                                   "note": "flexure-only elasticBeamColumn pair (Linear vs PDelta transf) under W_level; "
                                           "theta_equiv = 1 - (T_lin/T_PD)^2 is a global (mode-1) stability index"}
                               for d in ("X", "Y")}
    # torsion screening
    fkb = frame_storey_stiffness()
    rm2 = (PLATE[0] ** 2 + PLATE[1] ** 2) / 12
    tors = {"CM_m": [float(np.sum(m[:-1] * (PLATE[0] / 2)) / m[:-1].sum()), float(PLATE[1] / 2)],
            "CR_core_m": list(CORE_C), "CR_frame_m": [fkb["CR"]["x"], fkb["CR"]["y"]],
            "e_m": [abs(CORE_C[0] - PLATE[0] / 2), abs(CORE_C[1] - PLATE[1] / 2)],
            "T_torsion_s": cl["RZ"][0]["T"], "r_mass_m": math.sqrt(rm2)}
    for d, Lp, c_edge in (("Y", PLATE[0], PLATE[0] / 2), ("X", PLATE[1], PLATE[1] / 2)):
        e_acc = 0.05 * Lp
        Om = cl[d][0]["T"] / cl["RZ"][0]["T"]            # omega_theta / omega_d
        rk2 = Om ** 2 * rm2
        tors[f"accidental_{d}"] = {"e_acc_m (5 % of plan dim, verify vs code)": e_acc, "Omega_theta": Om,
                                   "edge_amplification_static": 1 + e_acc * c_edge / rk2}
    res["torsion"] = tors
    # agent B and C
    a = {"T1_X_s": cl["X"][0]["T"], "T1_Y_s": cl["Y"][0]["T"],
         "mode1_mass_ratio_X": cl["X"][0]["ratio"]["X"], "mode1_mass_ratio_Y": cl["Y"][0]["ratio"]["Y"],
         "V1_X_kN_per_g": resp["X"]["mode1_per_g"]["V_kN"], "V1_Y_kN_per_g": resp["Y"]["mode1_per_g"]["V_kN"],
         "total_mass_t": float(m.sum())}
    b = agent_b()
    cmp = compare(a, b, TOL)
    res["verification"] = {"A": a, "B": b, "tolerances": TOL, "compare": cmp,
                           "independence": "method-independent (Rayleigh/moment-area vs OpenSees eigen); sections rebuilt "
                                           "from B inputs; masses shared with A (Division 3), so a wrong mass agrees twice"}
    res["checks"] = interpret(res, cl)
    return res


def interpret(res, cl) -> list:
    c = []
    s = res["modal"]["sum_all_modes"]
    c.append(("effective mass ratios over all modes sum to 1 (X, Y, RZ)", all(abs(v - 1) < 1e-6 for v in s.values())))
    s3 = res["modal"]["sum_first3"]
    c.append(("first 3 modes per direction capture >= 90 % mass (X, Y)", s3["X"] >= 0.9 and s3["Y"] >= 0.9))
    T = [r["T"] for r in cl["all"]]
    c.append(("periods strictly decreasing T1 > T2 > T3", T[0] > T[1] > T[2]))
    for d in ("X", "Y"):
        Tl = [r["T"] for r in cl[d]]
        c.append((f"{d}: T1 > T2 > T3 and ratios plausible for flexural cantilever (T1/T2 4-6.3)",
                  Tl[0] > Tl[1] > Tl[2] and 4.0 < Tl[0] / Tl[1] < 6.5))
        h = res["hand"][d]
        c.append((f"{d}: OpenSees T1 within 0.5 % of exact hand stepped-cantilever", abs(Tl[0] - h["T_s"][0]) / h["T_s"][0] < 0.005))
        c.append((f"{d}: OpenSees T1 within 2 % of Division 3 sanity value", abs(Tl[0] - h["structure_sanity_T1_s"]) / h["structure_sanity_T1_s"] < 0.02))
        c.append((f"{d}: closed-form uniform cantilever within 15 % (stepped section and plant mass differ)",
                  abs(h["closed_form"]["T_southwell"] - Tl[0]) / Tl[0] < 0.15))
        eq = res["response_per_unit_Sa"][d]["equilibrium_mode1"]
        c.append((f"{d}: equilibrium, base reaction = applied mode-1 forces (1e-6) and static roof = modal roof (0.1 %)",
                  abs(eq["V_reaction_kN"] - eq["V_applied_kN"]) / eq["V_applied_kN"] < 1e-6
                  and abs(eq["roof_static_m"] - abs(eq["roof_modal_m"])) / abs(eq["roof_modal_m"]) < 1e-3))
        c.append((f"{d}: units, base shear per g = M_eff x 9.81 within 1e-9 relative",
                  abs(res["response_per_unit_Sa"][d]["mode1_per_g"]["V_kN"] - cl[d][0]["ratio"][d] * res["inputs"]["total_mass_t"] * G_ACC)
                  < 1e-9 * res["inputs"]["total_mass_t"] * G_ACC))
        c.append((f"{d}: OpenSees P-Delta theta_equiv within 30 % of hand storey theta (mode 1)",
                  abs(res["p_delta_opensees"][d]["theta_equiv"] - res["response_per_unit_Sa"][d]["p_delta_theta"]["mode1_max"])
                  < 0.3 * res["response_per_unit_Sa"][d]["p_delta_theta"]["mode1_max"] + 0.005))
    sc = res["sensitivity_T1_s"]["cracked"]
    c.append(("T1 decreases monotonically with cracked factor 0.35 -> 1.0",
              all(sc["0.35"][d] > sc["0.5"][d] > sc["0.7"][d] > sc["1.0"][d] for d in ("X", "Y"))))
    sm = res["sensitivity_T1_s"]["mass"]
    c.append(("T1 scales with sqrt(mass) (+-10 % mass -> T ratio sqrt(1.1), sqrt(0.9) within 1e-6)",
              all(abs(sm["1.1"][d] / sm["1.0"][d] - math.sqrt(1.1)) < 1e-6 and abs(sm["0.9"][d] / sm["1.0"][d] - math.sqrt(0.9)) < 1e-6
                  for d in ("X", "Y"))))
    c.append(("total mass in model = Division 3 W / g", abs(res["inputs"]["total_mass_t"] * G_ACC - res["inputs"]["W_kN"]) / res["inputs"]["W_kN"] < 1e-3))
    t = res["torsion"]
    c.append(("torsion: static eccentricity CM-CR below 1 % of plan dimension", max(t["e_m"]) < 0.01 * PLATE[1]
              and abs(t["CR_frame_m"][0] - PLATE[0] / 2) < 0.3 and abs(t["CR_frame_m"][1] - PLATE[1] / 2) < 0.3))
    fr = res["frame_variant"]["modes"]
    c.append(("frame variant shortens T1 (stiffer) in X and Y", all(fr[d][0]["T_s"] < cl[d][0]["T"] for d in ("X", "Y"))))
    c.append(("independent check (verify_compare.py) decision PROCEED", res["verification"]["compare"]["decision"] == "PROCEED"))
    return [{"check": k, "pass": bool(v)} for k, v in c]


def _ops_version() -> str:
    try:
        from importlib.metadata import version
        return "openseespy " + version("openseespy")
    except Exception:  # pragma: no cover
        return "openseespy (version unknown)"


def _json(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.bool_):
        return bool(o)
    raise TypeError(type(o))


if __name__ == "__main__":
    r = run()
    (TOWER / "data" / "seismic.json").write_text(json.dumps(r, indent=1, default=_json))
    for d in ("X", "Y", "RZ"):
        print(d, [(round(q["T_s"], 3), round(q["mass_ratio"], 3)) for q in r["modal"][d]])
    print("first 6:", [(round(q["T_s"], 3), q["dir"]) for q in r["modal"]["first_6_overall"]])
    print("hand:", {d: [round(v, 3) for v in r["hand"][d]["T_s"]] + [round(r["hand"][d]["closed_form"]["T_southwell"], 3)] for d in ("X", "Y")})
    print("sens:", json.dumps(r["sensitivity_T1_s"], default=_json))
    print("frame:", json.dumps(r["frame_variant"]["modes"], default=_json)[:400], r["frame_variant"]["storey_k_kN_per_m_L1_L11_L21"])
    for d in ("X", "Y"):
        q = r["response_per_unit_Sa"][d]
        print(d, "mode1:", {k: round(v, 4) for k, v in q["mode1_per_g"].items()})
        print(d, "srss:", {k: round(v, 4) for k, v in q["srss3_const_Sa_per_g"].items()})
        print(d, "per mode:", [{k: round(v, 4) for k, v in pm.items()} for pm in q["per_mode_per_g"]])
        print(d, "pdelta:", q["p_delta_theta"]["mode1_max"], q["p_delta_theta"]["srss_max"], r["p_delta_opensees"][d])
        print(d, "eq:", q["equilibrium_mode1"])
    print("torsion:", json.dumps(r["torsion"], default=_json))
    print("B:", r["verification"]["B"]); print("A:", r["verification"]["A"]); print("C:", r["verification"]["compare"]["decision"])
    for c in r["checks"]:
        print(("PASS " if c["pass"] else "FAIL ") + c["check"])
