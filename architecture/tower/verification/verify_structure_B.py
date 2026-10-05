"""Agent B (Division 25): independent recalculation of the tower structural concept.

Method (deliberately different from a per-column tributary takedown):
  * Whole-building weight: per-level floor AREAS x unit loads (zoned into core floor,
    corridor band and residential area) + element-by-element self-weight of every
    column and core-wall segment (storey by storey, by zone).
  * Core section properties: numerical integration over a 0.05 m pixel grid of the
    box section (own geometry routine), checked against the closed-form box formula.
  * Period: Timoshenko (flexure + shear) cantilever stiffness matrix assembled from
    31 storey elements, rotations condensed, lumped masses, generalised eigen solution
    (numpy); cross-checked by a Rayleigh quotient on the static deflected shape.
  * Corner column: tributary panel (half-bay x half-bay, simple-span assumption) is the
    only practical concept-stage method; reported with stated simplifications.
Inputs: architecture/tower/verification/structure_inputs_for_B.json (shared with A).
Units: kN, m, s, kPa = kN/m2.
"""
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
inp = json.loads((HERE / "structure_inputs_for_B.json").read_text())
A = inp["assumptions"]
g = 9.81
gam = A["gamma_rc_kN_m3"]
Lx, Ly = inp["plate_m"]
plate = Lx * Ly
x0, y0, x1, y1 = inp["core"]["box_m"]
cx, cy = x1 - x0, y1 - y0                      # 12 x 8
z = [0.0] + inp["levels_z_m"]                  # level 0 = ground slab
nlev = len(z) - 1                              # 31 (30 = roof slab 94.4, 31 = plant top 99.4)
ROOF, PLANT = 30, 31


def zone(i):
    return "1-10" if i <= 10 else ("11-20" if i <= 20 else "21-31")


def t_core(i):
    return A["core_wall_t_zones_m"][zone(i)]


# ---------------- floor zoning ----------------
core_area = cx * cy
core_floor = A["core_floor_fraction"] * core_area
b = A["corridor_band_m"]
corridor = (cx + 2 * b) * (cy + 2 * b) - core_area
resid = plate - core_area - corridor
slab_area = plate - core_area + core_floor
perim = 2 * (Lx + Ly)
hs = A["slab_thickness_m"] * gam              # kPa

# ---------------- storey element self-weights ----------------
def core_wall_volume(i):
    h = z[i] - z[i - 1]; t = t_core(i)
    ring = core_area - (cx - 2 * t) * (cy - 2 * t)
    internal = A["core_internal_wall_count"] * A["core_internal_wall_t_m"] * (cy - 2 * t)  # ASSUMPTION: span short way
    return (ring + internal) * h


def column_volume(i, only=None):
    if i > ROOF:          # ASSUMPTION: perimeter columns stop at roof slab; plant storey is over the core
        return 0.0
    h = z[i] - z[i - 1]
    cols = inp["columns"].values() if only is None else [inp["columns"][only]]
    return sum(c["size_by_zone_m"][zone(i)] ** 2 * h for c in cols)


# ---------------- level loads (G, Q) ----------------
G_lev = np.zeros(nlev + 1); Q_lev = np.zeros(nlev + 1)
for L in range(1, nlev + 1):
    if L < ROOF:
        G = slab_area * hs + slab_area * (A["sdl_kPa"] + A["partitions_kPa"]) + perim * A["facade_kN_m"]
        Q = resid * A["live_res_kPa"] + corridor * A["live_corridor_kPa"] + core_floor * A["core_live_kPa"]
    elif L == ROOF:
        G = slab_area * hs + slab_area * (A["roof_sdl_kPa"] + A["roof_plant_kPa"]) + perim * A["facade_kN_m"]
        Q = slab_area * A["roof_live_kPa"]
    else:  # plant roof over core footprint
        G = core_area * hs + core_area * A["core_roof_plant_kPa"]
        Q = core_area * A["roof_live_kPa"]
    G_lev[L] = G; Q_lev[L] = Q

storey_self = np.zeros(nlev + 1)   # self-weight of vertical elements in storey i (between L i-1 and i)
for i in range(1, nlev + 1):
    storey_self[i] = gam * (core_wall_volume(i) + column_volume(i))

G_total = G_lev.sum() + storey_self.sum()
Q_total = Q_lev.sum()
W = G_total + A["psi_live_seismic"] * Q_total   # all weight above the ground slab, incl. full ground storey

# ---------------- core section by pixel integration ----------------
def box_props(t, d=A["grid_resolution_m"] / 2):
    xs = np.arange(-cx / 2 + d / 2, cx / 2, d); ys = np.arange(-cy / 2 + d / 2, cy / 2, d)
    X, Y = np.meshgrid(xs, ys)
    solid = (np.abs(X) > cx / 2 - t) | (np.abs(Y) > cy / 2 - t)
    dA = d * d
    Ax = solid.sum() * dA
    Ix = (Y[solid] ** 2).sum() * dA      # about x axis -> resists sway in Y
    Iy = (X[solid] ** 2).sum() * dA      # about y axis -> resists sway in X
    return Ax, Ix, Iy

t0 = t_core(1)
Abase, Ix_base, Iy_base = box_props(t0)
Ix_cf = (cx * cy ** 3 - (cx - 2 * t0) * (cy - 2 * t0) ** 3) / 12
Iy_cf = (cy * cx ** 3 - (cy - 2 * t0) * (cx - 2 * t0) ** 3) / 12

# ---------------- corner column C_0_0 ----------------
trib_a = 7.5 / 2 * 8.0 / 2                 # 15 m2
trib_f = 7.5 / 2 + 8.0 / 2                 # 7.75 m facade
Gc = 0.0; Qc = 0.0
for L in range(1, ROOF + 1):
    if L < ROOF:
        Gc += trib_a * (hs + A["sdl_kPa"] + A["partitions_kPa"]) + trib_f * A["facade_kN_m"]
        Qc += trib_a * A["live_res_kPa"]
    else:
        Gc += trib_a * (hs + A["roof_sdl_kPa"] + A["roof_plant_kPa"]) + trib_f * A["facade_kN_m"]
        Qc += trib_a * A["roof_live_kPa"]
Gc += gam * sum(column_volume(i, "C_0_0") for i in range(1, ROOF + 1))
fEC, fL = A["load_factors_EC_form"], A["load_factors_LRFD_form"]
N_EC = fEC[0] * Gc + fEC[1] * Qc
N_LR = fL[0] * Gc + fL[1] * Qc
N_corner = max(N_EC, N_LR)

# ---------------- period: Timoshenko stiffness + eigen ----------------
E = inp["E_concrete_MPa"] * 1e3 * inp["cracked_factor"]   # kPa
Gm = inp["E_concrete_MPa"] * 1e3 / (2 * (1 + A["poisson"])) * inp["cracked_factor"]
# lumped seismic masses: level loads + half of storey above and below
Wlev = G_lev + A["psi_live_seismic"] * Q_lev
for i in range(1, nlev + 1):
    Wlev[i - 1] += storey_self[i] / 2; Wlev[i] += storey_self[i] / 2
m = Wlev[1:] / g                                         # t (kN s2/m)


def period(direction):
    n = nlev + 1; K = np.zeros((2 * n, 2 * n))
    for i in range(1, nlev + 1):
        L = z[i] - z[i - 1]; t = t_core(i)
        _, Ix, Iy = (None, (cx * cy ** 3 - (cx - 2 * t) * (cy - 2 * t) ** 3) / 12,
                     (cy * cx ** 3 - (cy - 2 * t) * (cx - 2 * t) ** 3) / 12)
        I = Ix if direction == "Y" else Iy
        Av = 2 * t * (cy if direction == "Y" else cx)     # webs parallel to sway
        phi = 12 * E * I / (Gm * Av * L ** 2)
        k = E * I / (L ** 3 * (1 + phi)) * np.array([
            [12, 6 * L, -12, 6 * L],
            [6 * L, (4 + phi) * L ** 2, -6 * L, (2 - phi) * L ** 2],
            [-12, -6 * L, 12, -6 * L],
            [6 * L, (2 - phi) * L ** 2, -6 * L, (4 + phi) * L ** 2]])
        idx = [2 * (i - 1), 2 * (i - 1) + 1, 2 * i, 2 * i + 1]
        K[np.ix_(idx, idx)] += k
    free = list(range(2, 2 * n))
    Kf = K[np.ix_(free, free)]
    u = [j for j in range(len(free)) if j % 2 == 0]; r = [j for j in range(len(free)) if j % 2 == 1]
    Kuu, Kur, Krr = Kf[np.ix_(u, u)], Kf[np.ix_(u, r)], Kf[np.ix_(r, r)]
    Kc = Kuu - Kur @ np.linalg.solve(Krr, Kur.T)          # lateral stiffness
    M = np.diag(m)
    w2 = np.linalg.eigvals(np.linalg.solve(M, Kc)).real
    T_eig = 2 * np.pi / np.sqrt(w2.min())
    # Rayleigh check: static deflection under gravity-weight lateral loads
    F = m * g; d = np.linalg.solve(Kc, F)
    T_ray = 2 * np.pi * np.sqrt((m * d ** 2).sum() / (F * d).sum())
    return T_eig, T_ray

TY, TY_r = period("Y"); TX, TX_r = period("X")

res = {
    "W_kN": round(W, 1),
    "G_ground_kN": round(G_total, 1),
    "Q_ground_kN": round(Q_total, 1),
    "core_I_x_base_m4": round(Ix_base, 2),
    "core_I_y_base_m4": round(Iy_base, 2),
    "N_Ed_corner_kN": round(N_corner, 1),
    "T1_Y_cracked_s": round(TY, 3),
    "T1_X_cracked_s": round(TX, 3),
}
if __name__ == "__main__":
    print(f"areas: slab {slab_area:.1f} core_floor {core_floor:.1f} corridor {corridor:.1f} resid {resid:.1f}")
    print(f"G levels typ {G_lev[1]:.1f} roof {G_lev[ROOF]:.1f} plant {G_lev[PLANT]:.1f}; Q typ {Q_lev[1]:.1f}")
    print(f"storey self-weight: st1 {storey_self[1]:.1f} st15 {storey_self[15]:.1f} st31 {storey_self[31]:.1f} sum {storey_self.sum():.1f}")
    print(f"core base: A {Abase:.3f}  Ix pix {Ix_base:.2f} cf {Ix_cf:.2f}  Iy pix {Iy_base:.2f} cf {Iy_cf:.2f}")
    print(f"corner: G {Gc:.1f} Q {Qc:.1f} EC {N_EC:.1f} LRFD {N_LR:.1f}")
    print(f"periods: Y eig {TY:.3f} Rayleigh {TY_r:.3f}; X eig {TX:.3f} Rayleigh {TX_r:.3f}; total mass {m.sum():.0f} t")
    (HERE / "B_structure.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
