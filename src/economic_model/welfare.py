"""National welfare dashboard — measured separately from GDP.

The 12 mandatory objectives are tracked with their own indicators. A strategy
or scenario reports its expected direction of effect on each; `tradeoffs()`
flags every case where GDP improves while another objective worsens, so that
GDP is never optimised at the expense of everything else.
"""

from __future__ import annotations

from dataclasses import dataclass, field

OBJECTIVES: dict[str, dict] = {
    "growth": {"label": "Sustainable productivity and economic growth", "indicators": ["real GDP growth", "labour productivity growth"], "owner": "01"},
    "jobs_income": {"label": "Job creation and household income", "indicators": ["employment rate", "median household income"], "owner": "10"},
    "poverty_inclusion": {"label": "Poverty reduction and regional inclusion", "indicators": ["poverty headcount (national line)", "provincial poverty dispersion"], "owner": "14"},
    "fiscal_financial": {"label": "Fiscal sustainability and financial stability", "indicators": ["public debt/GDP", "NPL ratio", "reserve cover (months)"], "owner": "02"},
    "exports_investment": {"label": "Export development and investment", "indicators": ["exports/GDP", "GFCF/GDP", "FDI realisation rate"], "owner": "12"},
    "energy_infrastructure": {"label": "Energy and infrastructure development", "indicators": ["per-capita electricity consumption", "supply reliability"], "owner": "05"},
    "technology_science": {"label": "Technology adoption and scientific capability", "indicators": ["ICT services exports", "R&D/GDP"], "owner": "08"},
    "human_development": {"label": "Education, health and human development", "indicators": ["learning-adjusted years of schooling", "stunting prevalence", "HDI"], "owner": "09"},
    "institutions": {"label": "Effective, accountable institutions", "indicators": ["capital budget execution rate", "audit irregularities"], "owner": "11"},
    "resilience": {"label": "Resilience to geopolitical and environmental shocks", "indicators": ["reserve cover", "essential-import concentration", "annual average disaster loss"], "owner": "13"},
    "diaspora": {"label": "Economic opportunities for Nepal's diaspora", "indicators": ["remittance cost", "diaspora investment uptake"], "owner": "23"},
    "rights_accountability": {"label": "Protection of human rights and democratic accountability", "indicators": ["safeguard compliance", "grievance resolution"], "owner": "14"},
}

DIRECTIONS = {"+", "-", "0", "?"}  # improve, worsen, neutral, unknown


@dataclass
class ObjectiveAssessment:
    subject_id: str
    effects: dict[str, str] = field(default_factory=dict)  # objective -> direction
    evidence: dict[str, list[str]] = field(default_factory=dict)  # objective -> observation ids

    def __post_init__(self) -> None:
        unknown = set(self.effects) - set(OBJECTIVES)
        if unknown:
            raise ValueError(f"unknown objectives: {sorted(unknown)}")
        bad = {v for v in self.effects.values() if v not in DIRECTIONS}
        if bad:
            raise ValueError(f"invalid directions: {bad}")

    def completed(self) -> dict[str, str]:
        """Every objective, defaulting to '?' (unknown) when not assessed."""
        return {k: self.effects.get(k, "?") for k in OBJECTIVES}

    def tradeoffs(self) -> list[str]:
        eff = self.completed()
        if eff["growth"] != "+":
            return []
        return [k for k, v in eff.items() if v == "-"]

    def unassessed(self) -> list[str]:
        return [k for k, v in self.completed().items() if v == "?"]
