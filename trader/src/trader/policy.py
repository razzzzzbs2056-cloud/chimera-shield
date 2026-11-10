"""Versioned trading policy: every threshold the code gates on lives here.

Policies are immutable JSON files in policies/. One pointer file (ACTIVE.json) names the
version in force per stage ("paper", "live"). Nothing changes the pointer except
promote()/rollback(), which require a named approver and append to history.jsonl.
The nightly review writes CANDIDATES only; it cannot promote.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from trader.risk.calibration import Calibrator

STAGES = ("paper", "live")


@dataclass(frozen=True)
class RuleParams:
    """Parameters of the deterministic rule REFLEX (the code-only baseline)."""

    er_full: float = 0.45  # efficiency ratio that earns the full trend bonus
    trend_min: float = 2.0  # % distance from the slow mean to call a trend
    breakout_band: float = 4.0  # % from the 168-bar extreme that counts as "near"
    rsi_cap: float = 78.0
    hv_ratio: float = 1.8  # vol ratio that marks high_vol
    crisis_btc_drop: float = 8.0  # BTC 24-bar % drop that marks crisis
    toxic_imbalance: float = 0.6


@dataclass(frozen=True)
class Policy:
    version: str
    min_setup_quality: int = 2
    min_confidence: float = 0.88
    pause_confidence: float = 0.60
    pause_bars: int = 12
    kelly_mult: float = 0.25
    rr: float = 2.0  # target distance / stop distance
    stop_atr_mult: float = 2.5
    time_stop_bars: int = 96
    calibrator: Calibrator = field(default_factory=Calibrator)
    rule: RuleParams = field(default_factory=RuleParams)
    parent: str | None = None
    note: str = ""

    def __post_init__(self) -> None:
        if not (0 <= self.min_setup_quality <= 3):
            raise ValueError("min_setup_quality must be 0..3")
        if not (0.5 <= self.min_confidence <= 1.0):
            raise ValueError("min_confidence must be in [0.5, 1]")
        if not (0 < self.kelly_mult <= 0.25):
            raise ValueError("kelly_mult must be in (0, 0.25]: quarter Kelly is the ceiling")
        if self.rr <= 0 or self.stop_atr_mult <= 0 or self.time_stop_bars <= 0:
            raise ValueError("rr, stop_atr_mult and time_stop_bars must be positive")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["calibrator"] = self.calibrator.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Policy":
        d = dict(d)
        d["calibrator"] = Calibrator.from_dict(d.get("calibrator", {}))
        d["rule"] = RuleParams(**d.get("rule", {}))
        return cls(**d)


class PolicyStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "candidates").mkdir(exist_ok=True)

    def _path(self, version: str, candidate: bool = False) -> Path:
        return (self.root / "candidates" if candidate else self.root) / f"{version}.json"

    def save(self, policy: Policy, candidate: bool = False) -> Path:
        p = self._path(policy.version, candidate)
        if p.exists():
            raise FileExistsError(f"policy {policy.version} already exists; versions are immutable")
        p.write_text(json.dumps(policy.to_dict(), indent=2) + "\n")
        return p

    def load(self, version: str) -> Policy:
        for cand in (False, True):
            p = self._path(version, cand)
            if p.exists():
                return Policy.from_dict(json.loads(p.read_text()))
        raise FileNotFoundError(f"no policy {version}")

    def _pointer(self) -> dict:
        p = self.root / "ACTIVE.json"
        return json.loads(p.read_text()) if p.exists() else {}

    def active_version(self, stage: str) -> str:
        v = self._pointer().get(stage)
        if not v:
            raise FileNotFoundError(f"no active policy for stage {stage}")
        return v

    def active(self, stage: str) -> Policy:
        return self.load(self.active_version(stage))

    def _write(self, stage: str, version: str, action: str, approved_by: str, note: str) -> None:
        ptr = self._pointer()
        prev = ptr.get(stage)
        ptr[stage] = version
        (self.root / "ACTIVE.json").write_text(json.dumps(ptr, indent=2) + "\n")
        with (self.root / "history.jsonl").open("a") as f:
            f.write(json.dumps({"ts": int(time.time()), "stage": stage, "action": action, "from": prev,
                                "to": version, "approved_by": approved_by, "note": note}) + "\n")

    def promote(self, version: str, stage: str, approved_by: str, note: str = "",
                live_approved: bool = False) -> None:
        if stage not in STAGES:
            raise ValueError(f"stage must be one of {STAGES}")
        if not approved_by.strip():
            raise PermissionError("promotion needs a named approver")
        if stage == "live":
            if not live_approved:
                raise PermissionError("live promotion needs explicit live approval")
            if self._pointer().get("paper") != version:
                raise PermissionError("a policy must be active in paper before it can go live")
        cand = self._path(version, candidate=True)
        if cand.exists() and not self._path(version).exists():
            self._path(version).write_text(cand.read_text())
        self.load(version)  # must exist and validate
        self._write(stage, version, "promote", approved_by, note)

    def rollback(self, stage: str, approved_by: str) -> str:
        if not approved_by.strip():
            raise PermissionError("rollback needs a named approver")
        hist = self.root / "history.jsonl"
        rows = [json.loads(x) for x in hist.read_text().splitlines()] if hist.exists() else []
        mine = [r for r in rows if r["stage"] == stage]
        if not mine or not mine[-1]["from"]:
            raise RuntimeError(f"nothing to roll back to for stage {stage}")
        target = mine[-1]["from"]
        self._write(stage, target, "rollback", approved_by, "")
        return target
