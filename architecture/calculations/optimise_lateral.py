"""Size and place the CR-003 south lateral elements with pymoo, safety limits as hard constraints.

Decision variables: stiffness of each south element as a fraction s of one core's lateral stiffness,
and its y position (m, 0 = north edge) inside the floor wings (x = 4 and 44 m, fixed).
Objective: minimise s (proxy for added material, cost and carbon).
Constraints [A: thresholds are engineering ASSUMPTIONS, replace with the applicable code's limits]:
  max edge displacement / average <= 1.10 (both north and south edges)
  eccentricity / plan depth      <= 0.05
  rotational / translational frequency ratio >= 1.20 (avoid a torsionally flexible plan)
Model limits: rigid diaphragm, single storey-equivalent plan, mass unchanged by the new elements.
The optimum is cross-checked against a brute-force grid (an optimiser can exploit model errors).
Run:  python architecture/calculations/optimise_lateral.py
"""
import numpy as np
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize

import seismic_screen as ss

LIMITS = {"amp": 1.10, "e_over_B": 0.05, "omega": 1.20}
CORES = [(4.0, 4.0, 1.0, 1.0), (44.0, 4.0, 1.0, 1.0)]


def base():
    r = ss.run()
    return r["cm"], float(r["masses"]["m"].sum())


def evaluate(s: float, y: float, cm, mass) -> dict:
    els = CORES + [(4.0, y, s, s), (44.0, y, s, s)]
    south = ss.plan_torsion(els, cm, mass, 48.0, 32.0, 32.0)
    north = ss.plan_torsion(els, cm, mass, 48.0, 32.0, 0.0)
    return {"amp": max(south["edge_amplification"], north["edge_amplification"]),
            "e_over_B": south["e_over_B"], "omega": south["omega_ratio"]}


def feasible(m: dict) -> bool:
    return m["amp"] <= LIMITS["amp"] and m["e_over_B"] <= LIMITS["e_over_B"] and m["omega"] >= LIMITS["omega"]


class LateralProblem(ElementwiseProblem):
    def __init__(self, cm, mass):
        super().__init__(n_var=2, n_obj=1, n_ieq_constr=3, xl=np.array([0.0, 12.0]), xu=np.array([1.5, 31.0]))
        self.cm, self.mass = cm, mass

    def _evaluate(self, x, out, *args, **kwargs):
        m = evaluate(x[0], x[1], self.cm, self.mass)
        out["F"] = [x[0]]
        out["G"] = [m["amp"] - LIMITS["amp"], m["e_over_B"] - LIMITS["e_over_B"], LIMITS["omega"] - m["omega"]]


def optimise(seed: int = 1) -> dict:
    cm, mass = base()
    res = minimize(LateralProblem(cm, mass), GA(pop_size=40), ("n_gen", 80), seed=seed, verbose=False)
    s, y = res.X
    return {"s": float(s), "y": float(y), "metrics": evaluate(s, y, cm, mass)}


def grid(step_s: float = 0.01, step_y: float = 0.25) -> dict:
    cm, mass = base()
    best = None
    for y in np.arange(12.0, 31.0 + 1e-9, step_y):
        for s in np.arange(0.0, 1.5 + 1e-9, step_s):
            m = evaluate(s, y, cm, mass)
            if feasible(m):
                if best is None or s < best["s"]:
                    best = {"s": float(s), "y": float(y), "metrics": m}
                break                       # smallest feasible s at this y
    return best


if __name__ == "__main__":
    o, g = optimise(), grid()
    for tag, r in (("pymoo GA", o), ("grid    ", g)):
        m = r["metrics"]
        print(f"{tag}: s = {r['s']:.3f} x core stiffness at y = {r['y']:.1f} m | amp {m['amp']:.3f}, e/B {m['e_over_B']:.3f}, "
              f"omega {m['omega']:.2f}")
    print("CR-003 as proposed (s = 0.5 at y = 28): ", {k: round(v, 3) for k, v in evaluate(0.5, 28.0, *base()).items()})
