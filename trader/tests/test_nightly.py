import json

from tests.test_backtest import KW, POL, SETUPS, T0, TF, N, world
from trader.backtest.engine import run_backtest
from trader.exec.broker import CostModel
from trader.policy import Policy, PolicyStore
from trader.reflex.replay import ReplayReflex
from trader.review.nightly import resolve_outcome, review
from trader.risk.engine import RiskLimits


def logged(series):
    return run_backtest(series, SETUPS, policy_at=lambda t: POL, cost_of=lambda s: CostModel(),
                        **{**KW, "journal_all": True})


def test_outcome_uses_only_later_bars_and_waits_when_unknown():
    series, _ = world()
    S = series["AAA/USDT"]
    d = {"ts": int(S.ts[300]), "px": float(S.c[299]), "atr": 1.0, "decision": {"direction": "long"}}
    o = resolve_outcome(d, S, POL, TF)
    assert o in (0, 1)
    S.h = S.h.copy()
    S.h[:300] *= 100  # rewriting the past must not change the outcome
    assert resolve_outcome(d, S, POL, TF) == o
    last = {**d, "ts": int(S.ts[-2])}
    wide = Policy(version="w", stop_atr_mult=50.0)
    assert resolve_outcome(last, S, wide, TF) is None  # not enough future yet: unresolved, not a loss
    assert resolve_outcome({**d, "ts": 1}, S, POL, TF) is None


def test_replay_reproduces_the_original_run():
    series, _ = world()
    base = logged(series)
    again = run_backtest(series, SETUPS, policy_at=lambda t: POL, cost_of=lambda s: CostModel(),
                         reflex_for=lambda p: ReplayReflex(base.decisions), **KW)
    assert again.trades == base.trades


def run_review(tmp_path, series, res, tests_ok=True, min_samples=20):
    store = PolicyStore(tmp_path / "policies")
    store.save(POL)
    store.promote(POL.version, "paper", approved_by="test")
    rep = review(decisions=res.decisions, trades=res.trades, fills=res.fills, events=[], series=series,
                 setups=SETUPS, store=store, stage="paper", limits=RiskLimits(), cost_of=lambda s: CostModel(),
                 spread={"AAA/USDT": 4.0}, depth={"AAA/USDT": 500_000.0}, tf="1h", tf_seconds=TF,
                 balance=1000.0, now=T0 + N * TF, out_dir=tmp_path / "reports",
                 run_tests=lambda: (tests_ok, "stub"), min_samples=min_samples)
    return rep, store


def test_review_scores_calibration_and_never_promotes(tmp_path):
    series, _ = world()
    res = logged(series)
    rep, store = run_review(tmp_path, series, res)
    c = rep["calibration"]
    assert c["resolved"] > 30 and 0 <= c["brier_calibrated"] <= 1 and c["reliability"]
    assert rep["proposals"] and all("gates" in p for p in rep["proposals"])
    assert store.active_version("paper") == POL.version  # proposing is not promoting
    assert list((tmp_path / "policies" / "candidates").glob("*.json"))
    assert not (tmp_path / "policies" / "history.jsonl").read_text().count("\n") > 1
    saved = json.loads(next((tmp_path / "reports").glob("nightly-*.json")).read_text())
    assert saved["active_policy"] == POL.version and "manual only" in saved["promotion"]
    m = rep["misses"]
    assert m["taken_won"] + m["taken_lost"] + m["blocked_that_would_have_won"] + \
        m["blocked_that_would_have_lost"] == c["resolved"]


def test_failing_regression_tests_block_every_recommendation(tmp_path):
    series, _ = world()
    rep, _ = run_review(tmp_path, series, logged(series), tests_ok=False)
    assert rep["proposals"] and not any(p["recommended"] for p in rep["proposals"])


def test_review_with_no_data_reports_and_proposes_nothing(tmp_path):
    series, _ = world()
    empty = type("R", (), {"decisions": [], "trades": [], "fills": []})()
    rep, _ = run_review(tmp_path, series, empty)
    assert rep["calibration"] == {"resolved": 0} and rep["proposals"] == [] and rep["notes"]
