"""International exposure register.

An entry states *what* Nepal is exposed to, through which channel, which
metric measures it, and where that metric must come from. A value may only
be filled in by linking a retrieved or verified observation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.common import RESEARCH_DIR, load_json, utc_now, write_json
from src.research.observations import Observation

from .channels import CHANNELS

REGISTER_PATH = RESEARCH_DIR / "global_exposure" / "exposure_register.json"


@dataclass
class ExposureEntry:
    id: str
    title: str
    channel: str
    counterparties: list[str]
    metric: str
    unit: str
    owner: str
    source_ids: list[str]
    scenarios: list[str]
    status: str = "pending"  # pending | measured
    value: float | None = None
    period: str | None = None
    observation_id: str | None = None
    notes: str = ""
    concentration_question: str = ""
    updated_at: str = field(default_factory=utc_now)


def validate_entry(e: ExposureEntry, observations: dict[str, Observation] | None = None) -> list[str]:
    problems = []
    if e.channel not in CHANNELS:
        problems.append(f"{e.id}: unknown channel {e.channel}")
    if e.status == "pending" and e.value is not None:
        problems.append(f"{e.id}: pending entry carries a value")
    if e.status == "measured":
        if e.value is None or not e.observation_id:
            problems.append(f"{e.id}: measured entry needs value and observation_id")
        elif observations is not None:
            o = observations.get(e.observation_id)
            if o is None or o.status not in {"retrieved", "verified"}:
                problems.append(f"{e.id}: observation {e.observation_id} missing or not retrieved/verified")
    return problems


def load_register(path: Path = REGISTER_PATH) -> list[ExposureEntry]:
    data = load_json(path)
    return [ExposureEntry(**e) for e in data["entries"]]


def save_register(entries: list[ExposureEntry], path: Path = REGISTER_PATH) -> None:
    write_json(path, {"generated_at": utc_now(), "entries": [asdict(e) for e in entries]})
