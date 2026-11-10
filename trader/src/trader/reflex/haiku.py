"""Claude Haiku 5.5 REFLEX: one structured-output call per candle, low effort.

The model sees only the snapshot JSON (plus a fixed glossary). It returns a ReflexDecision
validated by the SDK against the pydantic schema. Any refusal, truncation, schema failure,
timeout or API error raises, which timed_decide() turns into a skipped candle.
No retries: a retry would blow the latency budget, and skipping a candle is always safe.
"""

from __future__ import annotations

from trader.state.engine import Snapshot
from trader.types import ReflexDecision

MODEL = "claude-haiku-5-5"
# Backtests with this REFLEX are only valid on data after this date (model training cutoff).
TRAINING_CUTOFF = "2026-06-30"

SYSTEM = """You are the reflex of a trading system. You judge one market snapshot and return a typed verdict.
You do not size, place orders, or set limits; code does that and will ignore anything else you say.

The user message is one JSON snapshot. All fields were computed by code at time `t` from closed bars only.
Fields: sym symbol; tf bar length; bias the only direction the researched thesis allows;
px price; spr spread in bps; imb order-book imbalance -1..1 (positive = more bids); r1 r6 r24 % returns over
1, 6, 24 bars; vol realised volatility, annualised %; volr short/long volatility ratio (1 = normal);
atr average true range as % of price; ma_f and ma_s % distance from the 24-bar and 168-bar mean;
er efficiency ratio 0 (chop) to 1 (clean trend); rsi 14-bar RSI; hi % below the 168-bar high; lo % above the
168-bar low; vz volume z-score; fund perp funding % per interval; btc_r24, btc_ma_s, btc_volr the same
measures for BTC; inval % distance to the price that invalidates the thesis; inv this symbol's position as a
share of equity; exp gross exposure / equity; dd drawdown from peak %; dpl today's PnL %; npos open positions;
rs risk state from the risk layer. A null field means the data was not available.

Return:
- regime: trending, mean_reverting, high_vol, or crisis (crisis = disorderly, correlated selling or broken
  market function; use it sparingly and whenever it is true).
- direction: long, short, or neutral. Only `bias` or neutral can lead to a trade. Choose neutral unless the
  snapshot supports the bias direction now.
- direction_confidence: your probability, 0 to 1, that the direction you chose is right over the next ~24
  bars. Be calibrated: 0.9 means you expect to be right 9 times in 10. Most snapshots deserve neutral.
- toxic_flow: true if spread, imbalance and volume suggest informed or one-sided flow against the bias;
  false if not; null if spr and imb are null.
- setup_quality: 0 to 3, how many of these hold: trend agrees with bias; BTC backdrop agrees with bias;
  entry is not extended or chasing.
- risk_state: safe, near_limit, or reduce. Never report a state safer than `rs`."""


class HaikuReflex:
    name = f"{MODEL}-effort-low"
    uses_model = True

    def __init__(self, client=None, max_tokens: int = 1024):
        if client is None:
            import anthropic  # imported lazily so the package works without a key

            client = anthropic.Anthropic(max_retries=0)
        self.client = client
        self.max_tokens = max_tokens

    def decide(self, snap: Snapshot, timeout_s: float) -> ReflexDecision:
        resp = self.client.with_options(timeout=timeout_s, max_retries=0).messages.parse(
            model=MODEL,
            max_tokens=self.max_tokens,
            system=SYSTEM,
            messages=[{"role": "user", "content": snap.to_prompt()}],
            output_config={"effort": "low"},
            output_format=ReflexDecision,
        )
        if resp.stop_reason != "end_turn":
            raise RuntimeError(f"reflex stop_reason={resp.stop_reason}")
        decision = resp.parsed_output
        if not isinstance(decision, ReflexDecision):
            raise RuntimeError("reflex returned no parsed decision")
        return decision
