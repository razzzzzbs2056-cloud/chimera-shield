"""Market data through ccxt: closed candles, order books, funding, exchange time, and a
cached history downloader for backtests. Public endpoints only; no keys are needed here."""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from trader.exec.broker import MarketView
from trader.types import Book, Candle

TF_SECONDS = {"15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}


def make_exchange(name: str = "okx", sandbox: bool = False, api_key: str | None = None,
                  secret: str | None = None, password: str | None = None):
    import ccxt

    params: dict = {"enableRateLimit": True, "timeout": 15000}
    if api_key:
        params.update(apiKey=api_key, secret=secret, password=password)
    ex = getattr(ccxt, name)(params)
    # Honour HTTPS_PROXY / REQUESTS_CA_BUNDLE when the host routes traffic through a proxy.
    # ccxt reads its trust_env flag before applying config, so set it on the session directly.
    ex.session.trust_env = True
    if sandbox:
        ex.set_sandbox_mode(True)
    return ex


def rows_to_candles(rows: list[list], tf_seconds: int, now_s: float) -> list[Candle]:
    """ccxt OHLCV rows -> closed candles only. The still-forming bar is dropped."""
    out = []
    for ts_ms, o, h, lo, c, v in rows:
        t0 = int(ts_ms // 1000)
        if t0 + tf_seconds <= now_s:
            out.append(Candle(t0, t0 + tf_seconds, float(o), float(h), float(lo), float(c), float(v or 0.0)))
    return out


class CcxtData:
    def __init__(self, exchange, tf: str = "1h"):
        self.ex = exchange
        self.tf = tf
        self.tf_seconds = TF_SECONDS[tf]

    def exchange_time(self) -> float:
        return self.ex.fetch_time() / 1000

    def candles(self, symbol: str, limit: int = 300) -> list[Candle]:
        rows = self.ex.fetch_ohlcv(symbol, self.tf, limit=limit)
        return rows_to_candles(rows, self.tf_seconds, self.exchange_time())

    def book(self, symbol: str, depth: int = 20) -> Book:
        ob = self.ex.fetch_order_book(symbol, depth)
        ts = int((ob.get("timestamp") or self.ex.milliseconds()) / 1000)
        return Book(ts, tuple((float(p), float(q)) for p, q, *_ in ob["bids"]),
                    tuple((float(p), float(q)) for p, q, *_ in ob["asks"]))

    def funding_pct(self, symbol: str) -> float | None:
        if ":" not in symbol:
            return None
        fr = self.ex.fetch_funding_rate(symbol)
        return None if fr.get("fundingRate") is None else float(fr["fundingRate"]) * 100

    def contract_size(self, symbol: str) -> float:
        return float(self.ex.market(symbol).get("contractSize") or 1.0)


def view_from_book(symbol: str, book: Book, band: float = 0.005, contract_size: float = 1.0) -> MarketView:
    bid, ask = book.bids[0][0], book.asks[0][0]
    mid = (bid + ask) / 2
    bid_depth = sum(p * q for p, q in book.bids if p >= mid * (1 - band)) * contract_size
    ask_depth = sum(p * q for p, q in book.asks if p <= mid * (1 + band)) * contract_size
    return MarketView(symbol, bid, ask, min(bid_depth, ask_depth), book.ts)


def download_history(exchange, symbol: str, tf: str, start_s: int, end_s: int, cache_dir: Path,
                     page: int = 100) -> pd.DataFrame:
    """Download closed candles [start, end) with a CSV cache. Returns columns ts, open..volume."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{exchange.id}_{symbol.replace('/', '-').replace(':', '_')}_{tf}.csv"
    step = TF_SECONDS[tf]
    df = pd.read_csv(path) if path.exists() else pd.DataFrame(
        columns=["ts", "open", "high", "low", "close", "volume"])
    have_from = int(df["ts"].min()) if len(df) else None
    cursor = int(df["ts"].max()) + step if len(df) else start_s
    if have_from is not None and have_from > start_s + step:
        cursor, df = start_s, df.iloc[0:0]  # cache starts too late: refetch from the start
    rows: list[list] = []
    empty = 0
    while cursor < end_s:
        batch = exchange.fetch_ohlcv(symbol, tf, since=cursor * 1000, limit=page)
        batch = [r for r in batch if cursor <= r[0] // 1000 < end_s]
        if not batch:
            empty += 1
            cursor += step * page  # nothing listed in this window (pre-listing); move on
            if empty > 400:
                break
            continue
        rows.extend(batch)
        cursor = int(batch[-1][0] // 1000) + step
    if rows:
        new = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "volume"])
        new["ts"] = (new["ts"] // 1000).astype("int64")
        df = pd.concat([df, new]).drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    df = df[df["ts"] + step <= time.time()]  # never cache a bar that has not closed
    df.to_csv(path, index=False)
    return df[(df["ts"] >= start_s) & (df["ts"] < end_s)].reset_index(drop=True)
