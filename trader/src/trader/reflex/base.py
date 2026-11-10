"""REFLEX interface. Any implementation (rules, Haiku, Jev) sits behind decide().

A REFLEX sees a Snapshot and returns a ReflexDecision or nothing. timed_decide() enforces
the latency budget: a late or failed decision is treated as "no decision" and the candle
is skipped. Nothing safety-related waits on a REFLEX.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Protocol

from trader.state.engine import Snapshot
from trader.types import ReflexDecision


class Reflex(Protocol):
    name: str
    uses_model: bool  # True => backtests are only valid after the model's training cutoff

    def decide(self, snap: Snapshot, timeout_s: float) -> ReflexDecision: ...


@dataclass(frozen=True)
class ReflexOutcome:
    decision: ReflexDecision | None
    latency_ms: float
    status: str  # "ok" | "late" | "error"
    error: str = ""


def timed_decide(reflex: Reflex, snap: Snapshot, budget_s: float,
                 clock: Callable[[], float] = time.monotonic) -> ReflexOutcome:
    t0 = clock()
    try:
        decision = reflex.decide(snap, budget_s)
    except Exception as e:  # any failure is a skipped candle, never a crash
        return ReflexOutcome(None, (clock() - t0) * 1000, "error", f"{type(e).__name__}: {e}"[:300])
    ms = (clock() - t0) * 1000
    if not isinstance(decision, ReflexDecision):  # a REFLEX that returns anything else is broken
        return ReflexOutcome(None, ms, "error", f"reflex returned {type(decision).__name__}")
    if ms > budget_s * 1000:
        return ReflexOutcome(None, ms, "late")
    return ReflexOutcome(decision, ms, "ok")
