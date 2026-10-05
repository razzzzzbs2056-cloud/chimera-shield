"""Reference earthquake pipeline in the organisation's format (ORG.md, division 4).

  Earthquake agent (A)  -> builds the model from the design basis (seismic_screen.py, numpy eigen solution)
  OpenSees simulation   -> same model in OpenSeesPy
  Results interpreter   -> plausibility checks (mass ratios, period range, ordering, sensitivity)
  Independent check (B) -> Rayleigh quotient on a different trial shape, no access to A's numbers
  Comparator (C)        -> tools/verify_compare.py: PROCEED or INVESTIGATE
Writes reports/seismic-pipeline-return.md in the mandatory 10-section format and validates it.
Run:  python architecture/seismic/pipeline.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "calculations")); sys.path.insert(0, str(ROOT / "tools"))
import seismic_screen as ss  # noqa: E402
from validate_return import validate  # noqa: E402
from verify_compare import compare  # noqa: E402

TOL = {"default": {"rel": 0.05}, "T1_s": {"rel": 0.10}}   # Rayleigh with an assumed shape is approximate: 10 % on T1


def agent_a():
    r = ss.run()
    m = r["masses"]["m"]; res = r["flexure + shear"]
    return r, {"T1_s": float(res["T"][0]), "W_kN": float(r["masses"]["W_kN"]), "mode1_mass_ratio": float(res["eff_mass_ratio"][0])}


def opensees(r):
    try:
        v = ss.verify_with_opensees(r["masses"]["m"], r["core"]["EI"], r["core"]["GA"])
        return {"T1_s": float(v["Timoshenko"][0])}
    except Exception as e:  # tool missing or failed: reported, never hidden
        return {"error": f"{type(e).__name__}: {e}"}


def agent_b():
    """Independent: rebuild inputs from the take-off and use a Rayleigh quotient with a shape of the
    form phi = (z/H)^1.5 (between shear and flexural cantilever shapes). Uses flexibility only to get
    the static deflection under the inertial loads, so it is a different method from an eigen solve."""
    ms = ss.seismic_masses(); m = ms["m"]; core = ss.core_properties()
    F = ss.flexibility(ss.LEVELS, core["EI"], core["GA"])
    phi = (ss.LEVELS / ss.LEVELS[-1]) ** 1.5
    loads = m * phi * ss.G                     # inertial force pattern, kN
    u = F @ loads                              # static deflection, m
    # Rayleigh from the deflected shape u (one Stodola step)
    w2r = (loads @ u) / ((m * u) @ u)
    T_rayleigh = 2 * math.pi / math.sqrt(w2r)
    W = float(m.sum() * ss.G)
    L = (m * u).sum(); Mk = (m * u * u).sum()
    return {"T1_s": float(T_rayleigh), "W_kN": W, "mode1_mass_ratio": float(L * L / Mk / m.sum())}


def interpret(r, a, os_res):
    checks = []
    eff = r["flexure + shear"]["eff_mass_ratio"]
    checks.append(("effective masses sum to 1", abs(eff.sum() - 1) < 1e-6))
    checks.append(("T1 in plausible range for a squat core building (0.03-1.0 s)", 0.03 < a["T1_s"] < 1.0))
    T = r["flexure + shear"]["T"]; checks.append(("periods ordered T1 > T2 > T3", bool(T[0] > T[1] > T[2])))
    checks.append(("shear deformation lengthens period", r["flexure + shear"]["T"][0] > r["flexure only"]["T"][0]))
    if "T1_s" in os_res:
        checks.append(("OpenSees T1 within 1 % of hand model", abs(os_res["T1_s"] - a["T1_s"]) / a["T1_s"] < 0.01))
    else:
        checks.append(("OpenSees run available", False))
    return checks


def report(r, a, os_res, checks, b, cmp):
    fails = [c for c, ok in checks if not ok] + [row["key"] for row in cmp["rows"] if not row["pass"]]
    t = r["torsion_A"]
    text = f"""# Seismic screening return: Chimera Pavilion (division 4, pipeline run)

## INPUTS USED
- Design basis: levels 5.5 / 9.7 / 13.9 m; two 8 x 8 m RC box cores, 0.4 m walls (design-brief.md, seismic_screen.py)
- Quantity take-off v0.1 (data/quantity_takeoff.csv) for seismic mass; materials.csv for densities and E

## ASSUMPTIONS
- [A] Cracked stiffness factor 0.5; seismic mass = dead + 0.3 x live; masses split equally to levels
- [A] Fixed base (no soil-structure interaction); rigid diaphragm for plan torsion
- [A] No hazard, site class or code applied: jurisdiction UNKNOWN

## METHOD
- Agent A: lumped-mass cantilever, flexure + shear flexibility, eigen solution (numpy)
- Simulation: same model in OpenSeesPy (ElasticTimoshenkoBeam, fullGenLapack)
- Results interpretation: plausibility checks listed under RESULTS
- Agent B (independent): Rayleigh quotient from the static deflection under an assumed inertial pattern (z/H)^1.5
- Independence: B uses a different method but the same input functions as A (method independence only); input data still need an independent check
- Agent C: tools/verify_compare.py with tolerances {json.dumps(TOL)}

## CALCULATIONS
- Agent A: T1 = {a['T1_s']:.4f} s; W = {a['W_kN']:.0f} kN; mode-1 mass ratio = {a['mode1_mass_ratio']:.3f}
- OpenSees: {('T1 = %.4f s' % os_res['T1_s']) if 'T1_s' in os_res else os_res.get('error')}
- Agent B: T1 = {b['T1_s']:.4f} s; W = {b['W_kN']:.0f} kN; mode-1 mass ratio = {b['mode1_mass_ratio']:.3f}
- Plan torsion (cores only): e/B = {t['e_over_B']:.2f}, edge amplification = {t['edge_amplification']:.2f}

## RESULTS
- Comparator decision: {cmp['decision']}
""" + "\n".join(f"- {'PASS' if ok else 'FAIL'}: {c}" for c, ok in checks) + f"""
- Configuration: torsionally irregular as drawn (CR-003 proposed); demand per unit Sa only

## CODE / STANDARD
- None applied: jurisdiction UNKNOWN. Method follows general structural dynamics (textbook level), not a code procedure.

## UNCERTAINTIES
- B and A share inputs, so a wrong input would agree in both
- Cracking factor (T1 0.09-0.18 s across 1.0-0.25), soil flexibility, diaphragm flexibility of CLT floors, mass distribution

## FAILED CHECKS
""" + ("\n".join("- " + f for f in fails) if fails else "None") + """

## RECOMMENDATIONS
- Adopt CR-003 before further seismic design; build the L3 3-D model with flexible diaphragms
- Obtain the site hazard and site class before any demand or capacity statement

## REQUIRED HUMAN REVIEW
- A licensed structural/earthquake engineer must review the model, assumptions and every conclusion before use
"""
    return text


def run():
    r, a = agent_a(); os_res = opensees(r); b = agent_b()
    cmp = compare(a, b, TOL)
    checks = interpret(r, a, os_res)
    text = report(r, a, os_res, checks, b, cmp)
    out = ROOT / "reports" / "seismic-pipeline-return.md"; out.write_text(text)
    return {"a": a, "b": b, "opensees": os_res, "compare": cmp, "checks": checks, "errors": validate(text), "path": str(out)}


if __name__ == "__main__":
    res = run()
    print("A:", res["a"]); print("B:", res["b"]); print("OpenSees:", res["opensees"])
    print("Comparator:", res["compare"]["decision"]); print("Format:", "VALID" if not res["errors"] else res["errors"])
