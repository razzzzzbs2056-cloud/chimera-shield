import pytest
from pydantic import ValidationError

from tests.conftest import StubReflex, good_decision, make_candles, snap_for
from trader import gate
from trader.gate import GateAction
from trader.policy import Policy, RuleParams
from trader.reflex.base import timed_decide
from trader.reflex.haiku import MODEL, SYSTEM, HaikuReflex
from trader.reflex.rule import RuleReflex
from trader.types import Direction, ReflexDecision, Regime, RiskState

P = Policy(version="t")
L, S = Direction.LONG, RiskState.SAFE


def test_default_gate_numbers_match_the_brief():
    assert (P.min_setup_quality, P.min_confidence, P.pause_confidence, P.kelly_mult) == (2, 0.88, 0.60, 0.25)


def test_gate_passes_a_clean_decision():
    assert gate.evaluate(good_decision(), S, L, P, False).action is GateAction.ENTER


@pytest.mark.parametrize("kw,reason", [
    (dict(setup_quality=1), "setup_quality_below_min"),
    (dict(direction_confidence=0.88), "confidence_below_min"),  # must be strictly above
    (dict(risk_state=RiskState.NEAR_LIMIT), "risk_state_not_safe"),
    (dict(risk_state=RiskState.REDUCE), "risk_state_not_safe"),
    (dict(direction=Direction.NEUTRAL), "direction_neutral"),
    (dict(direction=Direction.SHORT), "direction_against_thesis"),
    (dict(toxic_flow=True), "toxic_flow"),
])
def test_gate_blocks(kw, reason):
    g = gate.evaluate(good_decision(**kw), S, L, P, False)
    assert g.action is GateAction.HOLD and reason in g.reasons


def test_model_cannot_talk_the_risk_state_down():
    g = gate.evaluate(good_decision(risk_state=RiskState.SAFE), RiskState.NEAR_LIMIT, L, P, False)
    assert g.action is GateAction.HOLD and "risk_state_not_safe" in g.reasons


def test_paused_blocks_and_null_toxic_flow_is_allowed():
    assert gate.evaluate(good_decision(), S, L, P, True).action is GateAction.HOLD
    assert gate.evaluate(good_decision(toxic_flow=None), S, L, P, False).action is GateAction.ENTER


def test_low_confidence_and_crisis_escalate():
    g = gate.evaluate(good_decision(direction_confidence=0.59), S, L, P, False)
    assert g.action is GateAction.PAUSE and g.escalate and not g.global_pause
    g = gate.evaluate(good_decision(regime=Regime.CRISIS), S, L, P, False)
    assert g.action is GateAction.PAUSE and g.global_pause


def test_decision_schema_is_strict():
    for bad in (dict(setup_quality=4), dict(direction_confidence=1.2), dict(regime="bullish"),
                dict(direction="buy"), dict(risk_state="fine")):
        with pytest.raises(ValidationError):
            good_decision(**bad)
    with pytest.raises(ValidationError):
        ReflexDecision(**{**good_decision().model_dump(), "size": 5})  # no extra fields: it cannot size
    with pytest.raises(ValidationError):
        ReflexDecision(regime="trending", direction="long", direction_confidence=0.9, setup_quality=2,
                       risk_state="safe")  # toxic_flow must be present (nullable, not optional)


def test_timed_decide_skips_late_and_failed_decisions():
    snap = snap_for(make_candles())
    ticks = iter([0.0, 9.0])
    out = timed_decide(StubReflex(good_decision()), snap, 5.0, clock=lambda: next(ticks))
    assert out.decision is None and out.status == "late" and out.latency_ms == 9000
    out = timed_decide(StubReflex(raises=TimeoutError("slow")), snap, 5.0)
    assert out.decision is None and out.status == "error" and "TimeoutError" in out.error
    out = timed_decide(StubReflex(good_decision()), snap, 5.0)
    assert out.status == "ok" and out.decision is not None


def test_rule_reflex_is_deterministic_and_respects_bias():
    base = snap_for(make_candles())
    up = dict(ma_f=1.0, ma_s=4.0, btc_ma_s=3.0, r24=2.0, hi=-1.0, lo=9.0, rsi=60.0, er=0.5, volr=1.0,
              btc_r24=1.0, btc_volr=1.0)
    r = RuleReflex(RuleParams())
    s_long = base.model_copy(update={**up, "bias": Direction.LONG})
    d = r.decide(s_long)
    assert d == r.decide(s_long)
    assert d.direction is Direction.LONG and d.direction_confidence > 0.88 and d.setup_quality == 3
    assert d.regime is Regime.TRENDING and d.toxic_flow is None
    d_short = r.decide(base.model_copy(update={**up, "bias": Direction.SHORT}))
    assert d_short.direction is Direction.NEUTRAL and d_short.direction_confidence >= 0.60
    down = dict(ma_f=-1.0, ma_s=-4.0, btc_ma_s=-3.0, r24=-2.0, hi=-9.0, lo=1.0, rsi=40.0, er=0.5)
    assert r.decide(base.model_copy(update={**up, **down, "bias": Direction.SHORT})).direction is Direction.SHORT
    assert r.decide(base.model_copy(update={**up, **down, "bias": Direction.LONG})).direction is Direction.NEUTRAL
    hot = r.decide(s_long.model_copy(update={"rsi": 90.0}))  # overextended: confidence drops below the gate
    assert hot.direction_confidence <= 0.88
    toxic = r.decide(s_long.model_copy(update={"imb": -0.8, "spr": 3.0}))
    assert toxic.toxic_flow is True


def test_rule_reflex_flags_crisis_and_echoes_risk_state():
    import dataclasses

    from tests.conftest import SAFE_VIEW
    crash = make_candles(n=300, seed=5)
    last = crash[-1]
    px = last.open
    for i in range(1, 25):  # BTC falls ~12% over the last 24 bars
        c = crash[-25 + i]
        o = px
        px = px * 0.9947
        crash[-25 + i] = dataclasses.replace(c, open=o, close=px, high=o * 1.0001, low=px * 0.9999)
    d = RuleReflex(RuleParams()).decide(snap_for(crash))
    assert d.regime is Regime.CRISIS
    near = dataclasses.replace(SAFE_VIEW, risk_state=RiskState.NEAR_LIMIT)
    assert RuleReflex(RuleParams()).decide(snap_for(make_candles(), account=near)).risk_state is RiskState.NEAR_LIMIT


class FakeAnthropic:
    """Records the request and returns a canned parse() result, like the SDK client."""

    def __init__(self, parsed, stop_reason="end_turn"):
        self.parsed, self.stop_reason, self.calls, self.opts = parsed, stop_reason, [], []
        self.messages = self

    def with_options(self, **kw):
        self.opts.append(kw)
        return self

    def parse(self, **kw):
        self.calls.append(kw)
        return type("R", (), {"stop_reason": self.stop_reason, "parsed_output": self.parsed})()


def test_haiku_reflex_sends_only_the_snapshot_with_low_effort_and_a_deadline():
    snap = snap_for(make_candles())
    fake = FakeAnthropic(good_decision())
    d = HaikuReflex(client=fake).decide(snap, timeout_s=4.0)
    assert d == good_decision()
    call = fake.calls[0]
    assert call["model"] == MODEL == "claude-haiku-5-5"
    assert call["output_config"] == {"effort": "low"} and call["output_format"] is ReflexDecision
    assert call["messages"] == [{"role": "user", "content": snap.to_prompt()}]
    assert call["system"] == SYSTEM
    assert fake.opts[0] == {"timeout": 4.0, "max_retries": 0}


def test_haiku_reflex_rejects_refusals_and_missing_output():
    snap = snap_for(make_candles())
    with pytest.raises(RuntimeError):
        HaikuReflex(client=FakeAnthropic(good_decision(), "refusal")).decide(snap, 4.0)
    with pytest.raises(RuntimeError):
        HaikuReflex(client=FakeAnthropic(good_decision(), "max_tokens")).decide(snap, 4.0)
    with pytest.raises(RuntimeError):
        HaikuReflex(client=FakeAnthropic(None)).decide(snap, 4.0)
