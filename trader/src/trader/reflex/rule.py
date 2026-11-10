"""Deterministic rule REFLEX: the code-only baseline behind the same interface.

It is the fallback when no model key is configured, and the only REFLEX that may be
backtested on data from before a model's training cutoff. Its confidence numbers are a
hand-set scoring rule (a hypothesis), which is why sizing goes through the calibrator.
"""

from __future__ import annotations

from trader.policy import RuleParams
from trader.state.engine import Snapshot
from trader.types import Direction, ReflexDecision, Regime


class RuleReflex:
    name = "rule-v1"
    uses_model = False

    def __init__(self, params: RuleParams):
        self.p = params

    def decide(self, snap: Snapshot, timeout_s: float = 0.0) -> ReflexDecision:
        p = self.p
        if snap.btc_r24 <= -p.crisis_btc_drop or (snap.btc_volr >= 3.0 and snap.btc_r24 <= -5.0):
            regime = Regime.CRISIS
        elif snap.volr >= p.hv_ratio:
            regime = Regime.HIGH_VOL
        elif snap.er >= 0.3 and abs(snap.ma_s) >= p.trend_min:
            regime = Regime.TRENDING
        else:
            regime = Regime.MEAN_REVERTING

        sign = 1.0 if snap.bias is Direction.LONG else -1.0
        trend = sign * snap.ma_f > 0 and sign * snap.ma_s >= p.trend_min
        market = sign * snap.btc_ma_s > 0
        near = (snap.hi >= -p.breakout_band) if sign > 0 else (snap.lo <= p.breakout_band)
        momentum = sign * snap.r24 > 0 and near
        rsi_ok = snap.rsi < p.rsi_cap if sign > 0 else snap.rsi > 100 - p.rsi_cap
        not_stressed = regime in (Regime.TRENDING, Regime.MEAN_REVERTING)
        n = sum((trend, market, momentum, rsi_ok and not_stressed))

        toxic: bool | None = None
        if snap.imb is not None:
            toxic = sign * snap.imb <= -p.toxic_imbalance

        if trend and snap.bias is not Direction.NEUTRAL:
            conf = 0.50 + 0.09 * n + 0.09 * min(1.0, snap.er / p.er_full)
            direction = snap.bias
        else:
            conf = max(0.60, 0.95 - 0.10 * n)
            direction = Direction.NEUTRAL
        return ReflexDecision(
            regime=regime,
            direction=direction,
            direction_confidence=round(min(0.95, conf), 3),
            toxic_flow=toxic,
            setup_quality=min(3, sum((trend, market, momentum))),
            risk_state=snap.rs,
        )
