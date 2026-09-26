"""Scenario engine.

Scenarios are hypothetical stress tests, never forecasts. A scenario is a
YAML file under scenarios/{domestic,geopolitical,compound}/. Shock
magnitudes are `null` until an evidence-backed estimate exists; the engine
then reports the scenario as QUALITATIVE_ONLY rather than inventing numbers.

A magnitude may be supplied without evidence only if the shock is marked
`illustrative: true`; results are then labelled ILLUSTRATIVE (a sensitivity
exercise, not an estimate).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from src.common import SCENARIOS_DIR, load_yaml
from src.economic_model.projection import ProjectionAssumptions, project
from src.geopolitical_model.channels import CHANNELS, projection_variable

REQUIRED_FIELDS = (
    "id", "title", "category", "not_a_forecast", "trigger", "countries", "institutions", "exposure_refs",
    "channels", "shocks", "responses", "second_order_effects", "impact_dimensions", "uncertainty",
    "limitations", "audits_required",
)
IMPACT_DIMENSIONS = ("household", "regional", "sectoral", "fiscal")


@dataclass
class Shock:
    id: str
    channel: str
    variable: str
    unit: str
    magnitude: float | None = None
    start_offset_years: int = 1
    duration_years: int = 1
    evidence: list[str] = field(default_factory=list)
    illustrative: bool = False
    note: str = ""

    @property
    def key(self) -> tuple:
        return (self.channel, self.variable, self.start_offset_years, self.duration_years)

    @property
    def quantified(self) -> bool:
        return self.magnitude is not None


@dataclass
class Scenario:
    raw: dict
    path: Path | None = None

    @property
    def id(self) -> str:
        return self.raw["id"]

    @property
    def shocks(self) -> list[Shock]:
        return [Shock(**s) for s in self.raw.get("shocks", [])]

    @property
    def components(self) -> list[str]:
        return list(self.raw.get("components", []))

    @property
    def depends_on(self) -> list[str]:
        return list(self.raw.get("depends_on", []))


def load_scenarios(root: Path = SCENARIOS_DIR) -> dict[str, Scenario]:
    out: dict[str, Scenario] = {}
    for path in sorted(root.glob("*/*.yaml")):
        raw = load_yaml(path)
        if raw["id"] in out:
            raise ValueError(f"duplicate scenario id {raw['id']} in {path}")
        out[raw["id"]] = Scenario(raw, path)
    return out


def validate_scenario(s: Scenario, exposure_ids: set[str], all_ids: set[str]) -> list[str]:
    p = []
    missing = [f for f in REQUIRED_FIELDS if f not in s.raw]
    if missing:
        p.append(f"{s.id}: missing fields {missing}")
        return p
    if s.raw["not_a_forecast"] is not True:
        p.append(f"{s.id}: must declare not_a_forecast: true")
    if not {"15", "28"} <= set(s.raw["audits_required"]):
        p.append(f"{s.id}: must be submitted to both Agent 15 and Agent 28")
    for ch in s.raw["channels"]:
        if ch not in CHANNELS:
            p.append(f"{s.id}: unknown channel {ch}")
    for ref in s.raw["exposure_refs"]:
        if ref not in exposure_ids:
            p.append(f"{s.id}: unknown exposure ref {ref}")
    dims = s.raw["impact_dimensions"]
    for d in IMPACT_DIMENSIONS:
        if d not in dims:
            p.append(f"{s.id}: impact dimension {d} not addressed")
    seen = set()
    for sh in s.shocks:
        if sh.id in seen:
            p.append(f"{s.id}: duplicate shock id {sh.id}")
        seen.add(sh.id)
        if sh.channel not in s.raw["channels"]:
            p.append(f"{s.id}/{sh.id}: channel {sh.channel} not declared in scenario channels")
        if sh.quantified and not sh.evidence and not sh.illustrative:
            p.append(f"{s.id}/{sh.id}: magnitude given without evidence and not marked illustrative")
        if sh.duration_years < 1 or sh.start_offset_years < 0:
            p.append(f"{s.id}/{sh.id}: invalid timing")
    for ref in s.components + s.depends_on:
        if ref not in all_ids:
            p.append(f"{s.id}: references unknown scenario {ref}")
    if s.raw["category"] == "compound" and len(s.components) < 2:
        p.append(f"{s.id}: compound scenario needs at least two components")
    return p


def dependency_order(scenarios: dict[str, Scenario]) -> list[str]:
    """Topological order over depends_on + components; raises on cycles."""
    order, state = [], {}

    def visit(sid: str, stack: tuple) -> None:
        if state.get(sid) == "done":
            return
        if state.get(sid) == "active":
            raise ValueError(f"scenario dependency cycle: {' -> '.join(stack + (sid,))}")
        state[sid] = "active"
        s = scenarios[sid]
        for dep in s.depends_on + s.components:
            visit(dep, stack + (sid,))
        state[sid] = "done"
        order.append(sid)

    for sid in sorted(scenarios):
        visit(sid, ())
    return order


def compose(s: Scenario, scenarios: dict[str, Scenario]) -> dict:
    """Merge component shocks, applying each (channel, variable, timing) once.

    Identical shocks shared by components are counted once. Overlapping
    shocks with different magnitudes are NOT summed; they are reported as
    unresolved overlaps for Agent 16C / 00C to reconcile.
    """
    merged: dict[tuple, Shock] = {}
    origin: dict[tuple, str] = {}
    overlaps = []
    sources = [(c, scenarios[c].shocks) for c in s.components] + [(s.id, s.shocks)]
    for sid, shocks in sources:
        for sh in shocks:
            if sh.key not in merged:
                merged[sh.key], origin[sh.key] = sh, sid
                continue
            prev = merged[sh.key]
            kind = "duplicate_counted_once" if prev.magnitude == sh.magnitude else "conflicting_magnitudes"
            overlaps.append({"key": list(sh.key), "first": f"{origin[sh.key]}/{prev.id}", "second": f"{sid}/{sh.id}",
                             "kind": kind})
            if kind == "conflicting_magnitudes":
                merged[sh.key] = Shock(prev.id, prev.channel, prev.variable, prev.unit, None,
                                       prev.start_offset_years, prev.duration_years, [], False,
                                       "magnitude unresolved: components disagree")
    return {"shocks": list(merged.values()), "overlaps": overlaps}


def run_scenario(s: Scenario, scenarios: dict[str, Scenario], baseline: ProjectionAssumptions | None,
                 end_year: int) -> dict:
    shocks = compose(s, scenarios)["shocks"] if s.components else s.shocks
    result: dict = {"scenario": s.id, "title": s.raw["title"], "not_a_forecast": True, "shocks": []}
    applied: dict[str, dict[int, float]] = {}
    any_illustrative = False
    for sh in shocks:
        pv = projection_variable(sh.channel)
        if not sh.quantified:
            status = "PENDING_EVIDENCE"
        elif pv is None:
            status = "NOT_MODELLED_IN_PROJECTION"  # transmission recorded; needs sector/BoP module
        elif baseline is None:
            status = "NO_BASELINE"
        else:
            status = "APPLIED_ILLUSTRATIVE" if sh.illustrative and not sh.evidence else "APPLIED"
            any_illustrative |= status == "APPLIED_ILLUSTRATIVE"
            for k in range(sh.duration_years):
                year = baseline.base_year + sh.start_offset_years + k
                applied.setdefault(pv, {})
                applied[pv][year] = applied[pv].get(year, 0.0) + sh.magnitude
        result["shocks"].append({"id": sh.id, "channel": sh.channel, "status": status})
    if not applied:
        result["status"] = "QUALITATIVE_ONLY"
        return result
    shocked = ProjectionAssumptions(
        base_year=baseline.base_year,
        base_nominal_gdp_lcu=baseline.base_nominal_gdp_lcu,
        base_fx_lcu_per_usd=baseline.base_fx_lcu_per_usd,
        base_population=baseline.base_population,
        real_growth=baseline.real_growth.shifted(applied.get("real_growth", {})),
        deflator_growth=baseline.deflator_growth.shifted(applied.get("deflator_growth", {})),
        fx_depreciation=baseline.fx_depreciation.shifted(applied.get("fx_depreciation", {})),
        population_growth=baseline.population_growth,
        provenance=baseline.provenance,
    )
    base_rows, shock_rows = project(baseline, end_year), project(shocked, end_year)
    result["deltas"] = [
        {
            "year": b.year,
            "real_gdp_pct": (s_.real_gdp_lcu_base_prices / b.real_gdp_lcu_base_prices - 1.0) * 100.0,
            "nominal_gdp_usd_pct": (s_.nominal_gdp_usd / b.nominal_gdp_usd - 1.0) * 100.0,
        }
        for b, s_ in zip(base_rows, shock_rows)
    ]
    pending = any(x["status"] != "APPLIED" and not x["status"].startswith("APPLIED") for x in result["shocks"])
    result["status"] = "ILLUSTRATIVE" if any_illustrative else ("PARTIAL" if pending else "QUANTIFIED")
    return result
