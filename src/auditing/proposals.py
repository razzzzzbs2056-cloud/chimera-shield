"""Build audit proposals from platform artifacts.

These adapters describe an artifact honestly to the auditors: anything not
yet evidenced is submitted as a `pending` claim, so the auditors can reach
their own verdict. They never pre-fill a verdict.
"""

from __future__ import annotations

from src.common import CONFIG_DIR, load_yaml
from src.economic_model.growth import implied_real_growth, nominal_usd_growth, required_cagr
from src.scenario_engine.engine import Scenario


def _roundtrip_checks() -> list[dict]:
    """Self-consistency of the growth arithmetic used by the target tables."""
    r = required_cagr(45e9, 3e12, 25)
    real = implied_real_growth(r, 0.05, 0.03)
    back = nominal_usd_growth(real, 0.05, 0.03)
    end = 45e9 * (1 + r) ** 25
    return [
        {"name": "usd_growth_roundtrip", "passed": abs(back - r) < 1e-12},
        {"name": "cagr_reaches_target", "passed": abs(end / 3e12 - 1) < 1e-9},
    ]


def target_arithmetic_proposal() -> dict:
    cfg = load_yaml(CONFIG_DIR / "model_config.yaml")
    t = cfg["target_arithmetic"]
    assumptions = [{"id": v["id"], "text": f"{k} = {v['value']}", "basis": v["basis"]}
                   for k, v in t.items() if isinstance(v, dict) and "id" in v]
    assumptions += [{"id": c["id"], "text": c["name"], "basis": c["basis"]} for c in t["price_fx_cases"]]
    return {
        "id": "TGT-ARITH-001",
        "title": "US$3T required-growth arithmetic (parametric)",
        "owner": "01C",
        "kind": "finding",
        "claims": [
            {"text": "Nepal base-year nominal GDP in USD", "type": "pending", "value": None, "unit": "USD_current"},
            {"text": "Nepal population in milestone years", "type": "pending", "value": None, "unit": "persons"},
            {"text": "Historical frequency of growth spells at the required rates", "type": "pending",
             "value": None, "unit": "ratio"},
        ],
        "assumptions": assumptions,
        "identity_checks": _roundtrip_checks(),
        "uncertainty": "Results are parametric in a hypothetical base value; no empirical inputs are verified.",
        "legal_requirements": [],
        "distribution": {},
        "environment": {},
        "welfare_effects": {},
        "international_assumptions": [],
        "regional_dependencies": [],
        "treaty_constraints_checked": False,
        "probabilities": [],
        "cross_border_environment": "",
        "compound_shock_tested": False,
    }


def scenario_proposal(s: Scenario) -> dict:
    claims = [{"text": f"{sh.id}: {sh.channel} shock to {sh.variable}", "type": "pending" if sh.magnitude is None
               else ("estimate" if sh.evidence else "assumption"), "value": sh.magnitude, "unit": "percent",
               "observation_ids": sh.evidence} for sh in s.shocks]
    return {
        "id": f"SCN-{s.id}",
        "title": s.raw["title"],
        "owner": "16C",
        "kind": "scenario",
        "claims": claims,
        "assumptions": [{"id": f"{s.id}-trigger", "text": s.raw["trigger"], "basis": "assumption"}],
        "identity_checks": [],
        "uncertainty": s.raw.get("uncertainty", ""),
        "legal_requirements": [],
        "distribution": {k: None for k in ("by_income", "by_province")},
        "environment": {},
        "welfare_effects": {},
        "international_assumptions": [{"text": c, "source_ids": [], "observation_ids": []}
                                      for c in s.raw.get("countries", [])],
        "regional_dependencies": s.raw.get("exposure_refs", []),
        "treaty_constraints_checked": False,
        "probabilities": [],
        "cross_border_environment": "",
        "compound_shock_tested": s.raw.get("category") == "compound",
    }
