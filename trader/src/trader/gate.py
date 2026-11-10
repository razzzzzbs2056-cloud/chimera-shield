"""Trade gate: code decides whether a REFLEX judgement may become an order.

The REFLEX only supplies a typed opinion. These rules, and the numbers in the policy,
are the whole of the decision to take new risk.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from trader.policy import Policy
from trader.types import Direction, ReflexDecision, Regime, RiskState, worst_risk


class GateAction(StrEnum):
    ENTER = "enter"
    HOLD = "hold"
    PAUSE = "pause"  # stop taking new risk and escalate to the BRAIN / human


@dataclass(frozen=True)
class GateResult:
    action: GateAction
    reasons: tuple[str, ...]
    escalate: bool = False
    global_pause: bool = False


def evaluate(decision: ReflexDecision, code_risk: RiskState, bias: Direction, policy: Policy,
             paused: bool) -> GateResult:
    # Escalation checks first: these pause new risk whatever else is true.
    if decision.regime is Regime.CRISIS:
        return GateResult(GateAction.PAUSE, ("regime_crisis",), escalate=True, global_pause=True)
    if decision.direction_confidence < policy.pause_confidence:
        return GateResult(GateAction.PAUSE, ("confidence_below_pause_floor",), escalate=True)

    reasons: list[str] = []
    if paused:
        reasons.append("paused")
    if decision.direction is Direction.NEUTRAL:
        reasons.append("direction_neutral")
    elif decision.direction is not bias:
        reasons.append("direction_against_thesis")
    if decision.setup_quality < policy.min_setup_quality:
        reasons.append("setup_quality_below_min")
    if not decision.direction_confidence > policy.min_confidence:
        reasons.append("confidence_below_min")
    if worst_risk(decision.risk_state, code_risk) is not RiskState.SAFE:
        reasons.append("risk_state_not_safe")
    if decision.toxic_flow is True:
        reasons.append("toxic_flow")
    return GateResult(GateAction.HOLD if reasons else GateAction.ENTER, tuple(reasons))
