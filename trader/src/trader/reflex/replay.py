"""Replays logged REFLEX decisions. Lets a candidate policy (thresholds, calibration) be
tested against what the live model actually said, without calling the model again.
Logged decisions are by construction from after the model's training cutoff."""

from __future__ import annotations

from trader.state.engine import Snapshot
from trader.types import ReflexDecision


class ReplayReflex:
    name = "replay"
    uses_model = False  # it replays recorded output; it cannot remember the future

    def __init__(self, decisions: list[dict]):
        self.by_key = {(d["symbol"], d["ts"]): ReflexDecision(**d["decision"])
                       for d in decisions if d.get("decision")}

    def decide(self, snap: Snapshot, timeout_s: float = 0.0) -> ReflexDecision:
        return self.by_key[(snap.sym, snap.t)]  # KeyError => candle skipped, as it was live
