"""Wind assessment, 30-storey residential tower (Division 7), parametric in basic speed.

CONCEPT / FEASIBILITY ONLY. Site, terrain, jurisdiction and code are UNKNOWN. All profile, gust and
coefficient forms below are generic textbook-type ASSUMPTIONS; verify against the applicable wind standard.
Units: m, s, N/Pa, kN, kNm.
Writes architecture/tower/data/wind.json.
"""
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

# ---- ASSUMPTIONS (all labelled in the return) ----
RHO = 1.25            # kg/m3 air density (1.2-1.25 typical)
SPEEDS = [35.0, 45.0, 55.0]   # m/s basic speed at 10 m (parametric; averaging time/return period UNKNOWN)
ALPHA = 0.25          # power-law exponent, urban/suburban-type terrain
Z_REF = 10.0
Z_MIN = 10.0          # profile held constant below 10 m
Z0 = 1.0              # roughness length for turbulence intensity I(z)=1/ln(z/z0)
CF = 1.3              # net along-wind force coefficient (0.8 windward + 0.5 leeward suction), rectangular
ZETA = 0.015          # critical damping ratio, strength-level wind (ASSUMPTION)
ST = 0.12             # Strouhal number, rectangular section (range 0.08-0.15)
ST_RANGE = [0.08, 0.12, 0.15]
L_SCALE_REF = (300.0, 200.0, 0.5)   # integral length scale L(z)=300 (z/200)^0.5
COMFORT_SPEED_FRAC = 0.7            # serviceability-wind speed as fraction of V_basic (ASSUMPTION)
DRIFT_LIMIT_DENOM = 500.0           # JUDGMENT order of magnitude, H/500 (verify)
PLANT_WIDTH = {"Y": 12.0, "X": 8.0}  # plant footprint = core 12 x 8 (ASSUMPTION), width facing wind
H_ROOF, H_TOP = 94.4, 99.4


def q_of_v(v, rho=RHO):
    """Velocity pressure q = 0.5 rho V^2 [Pa]."""
    return 0.5 * rho * v * v


def v_profile(v_ref, z, alpha=ALPHA):
    z = np.maximum(np.asarray(z, float), Z_MIN)
    return v_ref * (z / Z_REF) ** alpha


def q_profile(v_ref, z, alpha=ALPHA):
    return q_of_v(v_profile(v_ref, z, alpha))


def v_crit(period_s, width_m, st=ST):
    """Vortex-shedding critical speed V_cr = f1 b / St, f1 = 1/T1."""
    return width_m / (period_s * st)


def peak_factor(n0, t_avg=600.0):
    k = math.sqrt(2.0 * math.log(max(n0 * t_avg, 1.0001)))
    return k + 0.577 / k


def gust_factor(v_ref, period_s, b, h=H_TOP, zeta=ZETA, alpha=ALPHA):
    """Davenport-type gust factor G = 1 + 2 g I sqrt(B^2 + R^2) at z_s = 0.6 h. Returns dict."""
    zs = max(0.6 * h, Z_MIN)
    vh = float(v_profile(v_ref, zs, alpha))
    iz = 1.0 / math.log(zs / Z0)
    ls = L_SCALE_REF[0] * (zs / L_SCALE_REF[1]) ** L_SCALE_REF[2]
    b2 = 1.0 / (1.0 + 0.9 * ((b + h) / ls) ** 0.63)
    n = 1.0 / period_s
    fr = n * ls / vh
    e = 6.8 * fr / (1.0 + 10.2 * fr) ** (5.0 / 3.0)
    s = 1.0 / ((1.0 + 3.5 * n * h / vh) * (1.0 + 4.0 * n * b / vh))
    r2 = math.pi / (4.0 * zeta) * s * e
    gb, gr = 3.5, peak_factor(n)
    g = 1.0 + 2.0 * iz * math.sqrt(gb ** 2 * b2 + gr ** 2 * r2)
    return {"G": g, "I_zs": iz, "L_zs_m": ls, "B2": b2, "R2": r2, "g_R": gr, "g_B": gb,
            "V_zs_m_s": vh, "zs_m": zs}


def load_structure():
    return json.loads((DATA / "structure.json").read_text())


def stiffness_profiles(st, direction, cracked, dz):
    """EI(z), GA(z) on grid midpoints. direction 'Y' = wind along Y (sway about section I_x)."""
    zl = [0.0] + list(st["levels"]["z_m"])
    zones = st["core"]["section_by_zone"]
    e = st["E_concrete_MPa"] * 1e3  # kPa
    f = st["cracked_factor"] if cracked else 1.0
    g = e / (2.0 * (1.0 + st["assumptions"]["poisson"]))
    n = int(round(zl[-1] / dz))
    zm = (np.arange(n) + 0.5) * dz
    ei = np.zeros(n)
    ga = np.zeros(n)
    for i, z in enumerate(zm):
        k = int(np.searchsorted(zl, z, side="left"))  # level index 1..31
        k = min(max(k, 1), 31)
        zone = "1-10" if k <= 10 else "11-20" if k <= 20 else "21-31"
        sec = zones[zone]
        ei[i] = f * e * (sec["I_x_m4"] if direction == "Y" else sec["I_y_m4"])
        ga[i] = f * g * (sec["A_shear_Y_m2"] if direction == "Y" else sec["A_shear_X_m2"])
    return zl, zm, ei, ga


def width_profile(zm, face_w, direction):
    return np.where(zm <= H_ROOF, face_w, PLANT_WIDTH[direction])


def cantilever_response(w, zm, ei, ga, dz):
    """Distributed load w (kN/m) on grid -> shear, moment, deflection y at grid nodes (cumulative)."""
    v = np.cumsum(w[::-1])[::-1] * dz               # shear at base of each cell (approx, kN)
    # moment at cell midpoint: M(z)=sum w(s)(s-z) dz for s>z
    m = np.array([np.sum(w[i:] * (zm[i:] - zm[i]) * dz) for i in range(len(zm))])
    kappa = m / ei
    gam = v / ga
    theta = np.cumsum(kappa) * dz
    y = np.cumsum(theta * dz + gam * dz)
    return v, m, theta, y


def analyse_direction(st, direction, face_w, period_s_cracked, period_s_gross, v_ref, cracked=True):
    dz = 0.1
    zl, zm, ei, ga = stiffness_profiles(st, direction, cracked, dz)
    period = period_s_cracked if cracked else period_s_gross
    gf = gust_factor(v_ref, period, face_w)
    wb = width_profile(zm, face_w, direction)
    q = q_profile(v_ref, zm) / 1000.0  # kPa
    w_mean = q * CF * wb                   # kN/m
    w_peak = w_mean * gf["G"]
    out = {"period_s": period, "gust": gf}
    v0 = float(np.sum(w_peak) * dz)
    m0 = float(np.sum(w_peak * zm) * dz)
    out["mean_base_shear_kN"] = float(np.sum(w_mean) * dz)
    out["mean_base_moment_kNm"] = float(np.sum(w_mean * zm) * dz)
    out["base_shear_kN"] = v0
    out["base_moment_kNm"] = m0
    out["moment_arm_m"] = m0 / v0
    _, _, _, y = cantilever_response(w_peak, zm, ei, ga, dz)
    out["top_deflection_mm"] = float(y[-1] * 1000)
    out["top_drift_ratio_H_over"] = float(H_TOP / y[-1]) if y[-1] > 0 else None
    roof_idx = int(round(H_ROOF / dz)) - 1
    out["roof_slab_deflection_mm"] = float(y[roof_idx] * 1000)
    # interstorey drift
    ys = np.concatenate([[0.0], [y[min(int(round(z / dz)) - 1, len(y) - 1)] for z in zl[1:]]])
    hs = np.diff(zl)
    dr = np.diff(ys) / hs
    kmax = int(np.argmax(dr))
    out["max_interstorey_drift_ratio"] = float(dr[kmax])
    out["max_interstorey_drift_1_over"] = float(1.0 / dr[kmax])
    out["max_interstorey_level_index"] = kmax + 1
    # mean-load top deflection (for resonant acceleration)
    _, _, _, ym = cantilever_response(w_mean, zm, ei, ga, dz)
    out["mean_top_deflection_mm"] = float(ym[-1] * 1000)
    return out


def comfort_indication(res, v_ref, face_w):
    """Crude along-wind resonant acceleration at roof for a serviceability speed (JUDGMENT-grade).
    a ~ (2 pi / T)^2 * x_mean(V_serv) * 2 g_R I R. x_mean scales with V^2."""
    f = COMFORT_SPEED_FRAC
    g = res["gust"]
    xm = res["mean_top_deflection_mm"] / 1000.0 * f * f
    gr = g["g_R"]
    sig_ratio = 2.0 * g["I_zs"] * math.sqrt(g["R2"])
    w = 2.0 * math.pi / res["period_s"]
    a = w * w * xm * gr * sig_ratio
    return {"V_serv_m_s": f * v_ref, "peak_accel_m_s2": a, "peak_accel_milli_g": a / 9.81 * 1000.0}


def run():
    st = load_structure()
    lc, lg = st["lateral_cracked"], st["lateral_gross"]
    dirs = {
        # wind on the 30 m face -> blows along Y -> flexible Y sway (T1 4.55 cracked)
        "wind_on_30m_face": {"direction": "Y", "face_w": 30.0, "T_cr": lc["Y"]["T1_s"], "T_gr": lg["Y"]["T1_s"],
                             "across_width_m": 30.0, "crosswind_T_cr": lc["X"]["T1_s"], "crosswind_T_gr": lg["X"]["T1_s"]},
        # wind on the 24 m face -> blows along X -> X sway (T1 3.30 cracked)
        "wind_on_24m_face": {"direction": "X", "face_w": 24.0, "T_cr": lc["X"]["T1_s"], "T_gr": lg["X"]["T1_s"],
                             "across_width_m": 24.0, "crosswind_T_cr": lc["Y"]["T1_s"], "crosswind_T_gr": lg["Y"]["T1_s"]},
    }
    out = {"_meta": {"script": "architecture/tower/calcs/wind_tower.py", "level": "L1-L2 hand calc",
                     "status": "CONCEPT. Not for construction. Site/code UNKNOWN; generic forms; verify against applicable wind standard.",
                     "units": "m, s, kN, kNm, Pa, mm"},
           "assumptions": {"rho": RHO, "alpha": ALPHA, "z0": Z0, "Cf_net": CF, "zeta": ZETA, "St": ST,
                           "St_range": ST_RANGE, "plant_width_m": PLANT_WIDTH,
                           "comfort_speed_fraction": COMFORT_SPEED_FRAC, "drift_limit": "H/%d (JUDGMENT)" % DRIFT_LIMIT_DENOM,
                           "height_m": {"roof_slab": H_ROOF, "top_of_plant": H_TOP},
                           "gust_form": "G = 1 + 2 I sqrt(gB^2 B^2 + gR^2 R^2) Davenport-type, gB=3.5, z_s=0.6H"},
           "q_hand_check_Pa": {}, "profile": {}, "cases": {}, "crosswind": {}}
    zs = [10, 20, 30, 40, 50, 60, 70, 80, 94.4, 99.4]
    for v in SPEEDS:
        out["q_hand_check_Pa"][str(int(v))] = q_of_v(v)
        out["profile"][str(int(v))] = {"z_m": zs, "V_m_s": [float(x) for x in v_profile(v, zs)],
                                       "q_Pa": [float(x) for x in q_profile(v, zs)]}
    for name, d in dirs.items():
        out["cases"][name] = {}
        for v in SPEEDS:
            c = {}
            for tag, cr in (("cracked", True), ("gross", False)):
                r = analyse_direction(st, d["direction"], d["face_w"], d["T_cr"], d["T_gr"], v, cr)
                r["comfort_indicative"] = comfort_indication(r, v, d["face_w"])
                c[tag] = r
            out["cases"][name][str(int(v))] = c
        # period sensitivity at 45 m/s (cracked stiffness, period scaled, loads/EI unchanged -> gust only)
        sens = {}
        for T in (0.7 * d["T_cr"], d["T_cr"], 1.3 * d["T_cr"]):
            sens[f"{T:.2f}"] = gust_factor(45.0, T, d["face_w"])["G"]
        out["cases"][name]["gust_factor_vs_period_45ms"] = sens
        # crosswind
        cw = {}
        for tag, T in (("cracked", d["crosswind_T_cr"]), ("gross", d["crosswind_T_gr"])):
            row = {"T1_cross_s": T, "b_m": d["across_width_m"], "St": {}}
            for stv in ST_RANGE:
                vc = v_crit(T, d["across_width_m"], stv)
                row["St"][str(stv)] = {
                    "V_cr_m_s": vc,
                    "V_basic_at_which_Vcr_reached_at_roof": vc / float((H_TOP / Z_REF) ** ALPHA),
                    "height_where_Vcr_m_for_V35_45_55": [float(Z_REF * (vc / v) ** (1 / ALPHA)) for v in SPEEDS],
                    "V_roof_m_s_for_V35_45_55": [float(v_profile(v, H_TOP)) for v in SPEEDS]}
            cw[tag] = row
        out["crosswind"][name] = cw
    (DATA / "wind.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    o = run()
    for n, c in o["cases"].items():
        for v in ("35", "45", "55"):
            for t in ("cracked", "gross"):
                r = c[v][t]
                print(n, v, t, "G=%.2f" % r["gust"]["G"], "V=%.0f kN" % r["base_shear_kN"],
                      "M=%.0f MNm" % (r["base_moment_kNm"] / 1e3), "top=%.0f mm H/%.0f" % (r["top_deflection_mm"], r["top_drift_ratio_H_over"]),
                      "IDR 1/%.0f" % r["max_interstorey_drift_1_over"], "a=%.1f mg" % r["comfort_indicative"]["peak_accel_milli_g"])
