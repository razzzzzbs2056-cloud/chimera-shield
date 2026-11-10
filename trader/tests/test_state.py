import dataclasses

import pandas as pd
import pytest

from tests.conftest import T0, TF, make_candles, snap_for
from trader.state.engine import (
    TOKEN_BUDGET,
    DataFault,
    EngineConfig,
    book_metrics,
    candles_to_frame,
    check_clock,
)
from trader.state.features import FEATURE_COLS, WARMUP, compute_features
from trader.types import Book


def test_snapshot_is_under_token_budget_and_numeric(candles):
    s = snap_for(candles, funding=0.0123, inval=80.0,
                 book=Book(candles[-1].ts_close, ((99.9, 5.0),), ((100.1, 3.0),)))
    assert s.token_estimate() < TOKEN_BUDGET
    assert s.spr is not None and -1 <= s.imb <= 1
    assert s.t == candles[-1].ts_close


def test_features_have_no_lookahead(candles):
    """Row k computed on the full series must equal row k computed on bars 0..k only."""
    df = candles_to_frame(candles)
    full = compute_features(df, 8760)
    for k in (WARMUP, WARMUP + 7, len(df) - 2):
        part = compute_features(df.iloc[: k + 1], 8760).iloc[-1]
        pd.testing.assert_series_equal(full.iloc[k][list(FEATURE_COLS)], part[list(FEATURE_COLS)],
                                       check_names=False)


def test_future_bar_changes_nothing_before_it(candles):
    df = candles_to_frame(candles)
    a = compute_features(df, 8760).iloc[-2]
    df2 = df.copy()
    df2.loc[df2.index[-1], ["open", "high", "low", "close"]] = 9999.0
    b = compute_features(df2, 8760).iloc[-2]
    pd.testing.assert_series_equal(a, b)


def test_rejects_bar_from_the_future(candles):
    from trader.state.engine import validate_candles
    with pytest.raises(DataFault) as e:
        validate_candles(candles, candles[-1].ts_close - 1, EngineConfig(require_book=False), "x")
    assert e.value.kind == "lookahead"


def test_rejects_stale_candles(candles):
    from trader.state.engine import validate_candles
    with pytest.raises(DataFault) as e:
        validate_candles(candles, candles[-1].ts_close + TF, EngineConfig(), "x")
    assert e.value.kind == "stale_data"


def test_rejects_gap_and_short_history_and_bad_bar(candles):
    from trader.state.engine import validate_candles
    cfg, asof = EngineConfig(), candles[-1].ts_close
    with pytest.raises(DataFault) as e:
        validate_candles(candles[:50] + candles[51:], asof, cfg, "x")
    assert e.value.kind == "missing_data"
    with pytest.raises(DataFault) as e:
        validate_candles(candles[-20:], asof, cfg, "x")
    assert e.value.kind == "missing_data"
    bad = list(candles)
    bad[100] = dataclasses.replace(bad[100], close=float("nan"))
    with pytest.raises(DataFault) as e:
        validate_candles(bad, asof, cfg, "x")
    assert e.value.kind == "bad_data"
    bad[100] = dataclasses.replace(candles[100], high=candles[100].low * 0.5)
    with pytest.raises(DataFault) as e:
        validate_candles(bad, asof, cfg, "x")
    assert e.value.kind == "bad_data"


def test_book_checks():
    cfg = EngineConfig()
    with pytest.raises(DataFault) as e:
        book_metrics(Book(T0 + 1, ((1, 1),), ((2, 1),)), T0, cfg)
    assert e.value.kind == "lookahead"
    with pytest.raises(DataFault) as e:
        book_metrics(Book(T0 - 60, ((1, 1),), ((2, 1),)), T0, cfg)
    assert e.value.kind == "stale_data"
    with pytest.raises(DataFault) as e:
        book_metrics(Book(T0, ((2, 1),), ((1, 1),)), T0, cfg)
    assert e.value.kind == "bad_data"
    with pytest.raises(DataFault) as e:
        book_metrics(Book(T0, (), ((1, 1),)), T0, cfg)
    assert e.value.kind == "missing_data"
    mid, spr, imb = book_metrics(Book(T0, ((99.0, 3.0),), ((101.0, 1.0),)), T0, cfg)
    assert mid == 100 and round(spr) == 200 and imb == 0.5


def test_missing_book_is_a_fault_when_required(candles):
    with pytest.raises(DataFault) as e:
        snap_for(candles, cfg=EngineConfig(require_book=True))
    assert e.value.kind == "missing_data"


def test_clock_skew():
    check_clock(1000.0, 1001.0, EngineConfig())
    with pytest.raises(DataFault) as e:
        check_clock(1000.0, 1010.0, EngineConfig())
    assert e.value.kind == "clock_skew"


def test_stale_btc_context_is_a_fault(candles):
    with pytest.raises(DataFault):
        snap_for(candles, btc=make_candles(n=len(candles) - 2))
