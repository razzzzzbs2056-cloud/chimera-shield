---
name: bld-optimisation-pymoo
description: Single- and multi-objective optimisation with pymoo (GA, NSGA-II) for structural layout, member sizing, carbon, cost, façade and energy, with safety limits as hard constraints and a mandatory cross-check against brute force or physics. Use whenever choosing a "best" design numerically.
---

# Optimisation with pymoo

**Example in repo:** `architecture/calculations/optimise_lateral.py` sizes and places the CR-003 south lateral elements. Objective: minimise added stiffness. Constraints: edge amplification ≤ 1.10, e/B ≤ 0.05, Ω ≥ 1.20 (ASSUMED thresholds). GA optimum s = 0.288 at y = 31 m; brute-force grid s = 0.290 → agree. The optimum sits exactly on the e/B limit, i.e. zero margin, so the proposal keeps s = 0.5 at y = 28 m.

## Rules
1. **Safety is a constraint, never an objective to trade.** Encode code limits (strength, drift, deflection, fire, egress) as `n_ieq_constr` with `G ≤ 0`.
2. Objectives are proxies: say what each stands for (stiffness → material, cost, carbon).
3. Fix `seed` for reproducibility; report population, generations and convergence.
4. Cross-check the optimum: brute-force grid for ≤ 3 variables, or multiple seeds and a local search otherwise.
5. Inspect active constraints: an optimum on a limit has no margin. Choose a design with margin and record why (change record).
6. Optimisers exploit model errors: verify the chosen design with the next analysis level, not only the optimisation model.

## Pattern
```python
class P(ElementwiseProblem):
    def __init__(self): super().__init__(n_var=2, n_obj=1, n_ieq_constr=3, xl=..., xu=...)
    def _evaluate(self, x, out, *a, **k):
        out["F"] = [objective(x)]
        out["G"] = [g1(x), g2(x), g3(x)]          # each <= 0 when safe
res = minimize(P(), GA(pop_size=40), ("n_gen", 80), seed=1)
```
Multi-objective: `NSGA2` with `n_obj > 1`; present the Pareto front, not a single answer.
