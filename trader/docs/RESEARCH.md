# Research: regime and finalists (2026-11-10)

**Headline: none of the eight candidates is a clean asymmetric setup today.** One is a
reasonable small short (XRP), one is a weak long that needs a catalyst with no date (AAVE),
the rest are neutral or worse. The market backdrop is risk-off. The system therefore
treats every finalist as a *conditional* setup: it may only trade in the researched
direction, and only when the REFLEX and the code gate both agree on a given candle.

How to read the labels:

- **Measured**: pulled by me from a live API on 2026-11-10 (OKX, Binance public data,
  CoinGecko, DefiLlama), and re-pulled a second time to confirm. Reproducible.
- **Secondary**: from web search summaries gathered by research subagents. Page fetching
  was blocked in this session, so no primary document was opened. Treat as unconfirmed.
- **Estimate**: my arithmetic on the above.

## 1. Market regime

| Measure (measured 2026-11-10) | Value | Reading |
|---|---|---|
| BTC price | $75.4k | Below its 50-day average ($81.7k), just above the 200-day ($73.2k) |
| BTC change | -9% in 30 days, -28% in 1 year, about -40% from the ~$126k high | Downtrend |
| ETH price | $2,135, below both averages; ETH/BTC 0.0283 and falling | Weaker than BTC |
| BTC dominance | 59.6% | Money hiding in BTC, not rotating into smaller coins |
| Total stablecoin supply | $292.0B, down 4.6% in 30 days | Liquidity leaving. USDT -$7.8B and USDC -$2.8B in 30 days |
| OKX BTC perp funding | about +0.007% per 8h (roughly 7% a year) | Mildly long-biased |
| OKX BTC open interest | $3.85B, up from $3.30B a month ago while price fell | Leverage being added into weakness |

Macro and flows (all **secondary**, verify before relying on them): the Fed reportedly
held at 3.75-4.00% on 2026-10-28 after a 25bp hike in September; US 10-year yield near
4.9%; October payrolls +165k; US spot BTC ETFs had net outflows in early November
(-$398.6M on 2026-11-02); 2B USDT was burned on 2026-10-31. Equities were near highs on
2026-11-04, so the weakness looks crypto-specific.

**Regime call (opinion):** trend down, liquidity contracting, leverage crowded on the
long side, risk appetite off. What would flip it: a daily BTC close below $73.2k with
continued USDT redemptions confirms the bear case; stablecoin supply and ETF flows both
turning positive plus a reclaim of $81.7k would turn it.

**What this means for the system:** long setups need BTC above its slow average before
the rule REFLEX will pass them, so in this regime the system should mostly sit in cash.
That is intended.

## 2. Universe and screen

Top 50 by market cap, excluding stablecoins, wrapped and tokenised-fund tokens, and your
off-limits list (tokenised stocks, memecoins, privacy coins, low-caps). I read your
"all stocks and all" as all four categories; tell me if that is wrong. Pump.fun (PUMP)
screened as the cheapest token on revenue but is memecoin infrastructure, so I excluded it.

Screen: market cap against protocol revenue and revenue that reaches token holders
(DefiLlama), supply still to unlock (CoinGecko), then tradability on OKX.

## 3. Finalists

Multiples are market cap divided by annualised revenue. "Holders revenue" is the part of
revenue that reaches the token (buybacks, burns, fee share), as DefiLlama classifies it.

| Setup | Direction | Market cap | Revenue multiple | Verdict |
|---|---|---|---|---|
| XRP | Short (perp) | $69.3B | about 244,000x chain fees | Attractive short, small size |
| AAVE | Long | $1.95B | 22x revenue; buybacks paused | Neutral, leaning long |
| HYPE | Long | $17.9B (FDV $71B) | 22-26x; all revenue buys tokens | Neutral |
| UNI | Long | $4.21B | 43x | Neutral |
| TRX | Long | $30.1B | about 90x | Neutral |
| SKY | Long | $1.43B | 9x revenue, 22-26x holders revenue | Neutral, leaning avoid |
| LINK | Long | $8.12B | about 140x | Neutral, leaning avoid |
| ADA | Short (perp) | $6.69B | about 7,100x chain fees | Neutral / avoid |

### XRP — short, small size
- **Thesis:** the most expensive large coin on fundamentals. XRPL earned about $0.28M in
  fees over the last year (measured) against a $69B market cap; fees are burned, so
  almost nothing accrues to holders. 36.5% of supply is not yet circulating (measured).
- **Confirmed catalysts (secondary):** Ripple releases up to 1B XRP from escrow on the
  1st of each month and re-locks roughly 60-80%. Spot XRP ETFs hold about 1.2B XRP;
  October inflows were reportedly the smallest in seven months.
- **Speculative:** ETF outflows; bank or payments adoption (cuts the other way).
- **Case against:** ETFs are a real, regular buyer. Stablecoins on XRPL grew about 4x in
  a year (measured: $215M to $941M). Already -70% from the high and -21% in 30 days, so
  bounces are likely. Funding averaged only +0.0037% per interval over 33 days and was
  negative 26% of the time (measured), so shorts are not reliably paid.
- **Invalidation:** sustained ETF net inflows; XRPL stablecoins above $1.5B with rising
  TVL; escrow re-lock above 90%; funding negative on more than half of intervals.
- **Priced in?** Partly. The premium is narrative and ETF-driven, not fundamental.

### AAVE — long, weak
- **Thesis:** cheapest of the quality DeFi names at 22x trailing revenue, 96.5%
  circulating, $16.3B TVL (all measured). The discount exists because token buybacks
  stopped: holders revenue was $3.9M a month a year ago and has been $0 since May 2026
  (measured).
- **Confirmed (secondary):** buybacks were paused from 2026-04-19 after an rsETH bridge
  incident; the DAO vote passed with 79.1%. Aave V4 went live on mainnet 2026-03-30.
- **Speculative:** a buyback restart. A forum thread exists; no vote is scheduled.
- **Bear case:** fees, revenue and TVL are all about 50% lower than a year ago
  (measured). Even the old buyback was only about 2.6% of market cap a year. Governance
  friction between Aave Labs and the DAO. The catalyst has no date.
- **Invalidation:** no buyback vote posted by 2027-01-31; 30-day revenue below $4M; TVL
  below $13B; a buyback budget below $20M a year.
- **Priced in?** The pause is. A restart is not, but it is only a possibility.

### HYPE — long, neutral
- **Thesis:** the strongest value accrual in the screen. Revenue was $681M over the last
  year and $69M in October (measured), and DefiLlama counts all of it as token buybacks.
  Organic, not paid for with emissions.
- **Confirmed (secondary):** spot HYPE ETFs exist; a USDC reserve-yield deal feeds the
  buyback fund.
- **Bear case:** only 25% of supply circulates (measured). Team vesting is reportedly
  about 9.9M HYPE a month, roughly ten times what buybacks absorb at today's price
  (estimate), though reported actual claims have been far lower. FDV is 87-104x revenue.
  Revenue is flat year on year. Perp-DEX fees are cyclical.
- **Invalidation:** monthly revenue below $45M; a confirmed full monthly team claim;
  TVL below $5B; a daily close below $60 (my level; wired into the schema).
- **Priced in?** More likely than not. The ETF news drove the 2026-09-23 high of $97.96.
- **Data limit:** OKX has listed HYPE spot only since 2025-11-04, so one year of history.

### UNI — long, neutral
- **Thesis:** the fee switch is live and all protocol revenue burns UNI: $8.5M in October
  (measured).
- **Bear case:** 43x revenue with TVL down a third in a year. The catalysts (fee switch,
  100M UNI burn) landed in late 2025 and price is roughly flat since, so the market gave
  little credit. 31% of supply is non-circulating (measured).
- **Invalidation:** 30-day revenue below $5M for two months; TVL below $3B; fee-switch
  coverage cut by governance.
- **Priced in?** Largely yes.

### TRX — long, neutral
- **Thesis:** the dominant USDT settlement chain ($93.6B of stablecoins, +21% in a year,
  measured), with $334M of fees burned in a year. It held up while the market fell.
- **Bear case:** about 90x revenue, and revenue is falling (from about $30M a month to
  about $24M, measured) even as usage grows, after the August 2025 fee cut. Supply is
  growing on net: burns reportedly offset about 65% of issuance (secondary). Heavy
  founder control. It may be a crowded safe harbour.
- **Invalidation:** monthly revenue below $25M for two more months; Tron stablecoin
  supply below $90B; net issuance still positive through Q4 2026.
- **Priced in?** Mostly yes.

### SKY — long, leaning avoid
- **Thesis:** lowest revenue multiple in the screen (9x) and about 100% circulating.
- **Bear case:** shrinking. Revenue fell from $22.5M to $13.8M a month over the year and
  TVL fell 30% in 30 days (measured). Buybacks are set by governance, which cut them in
  March 2026 (holders revenue fell to about $1.1M a month before recovering to $5.8M,
  measured). Staking yield is paid in new tokens.
- **Invalidation:** 30-day holders revenue below $4M; TVL below $4B; any new buyback cut;
  a daily close below $0.0358 (wired into the schema).
- **Liquidity:** thin on OKX (about $0.2M a day spot, 10 bps spread). Fine for a $1,000
  account, not for a larger one. History only since 2025-09-11.

### LINK — long, leaning avoid
- **Thesis:** real enterprise traction (CCIP, Swift integration announced September
  2026, secondary) and a reserve that buys LINK with revenue.
- **Bear case:** about 140x revenue with revenue flat near $4.5-5.8M a month (measured).
  23% of supply (233M LINK) is still to be released, reportedly in quarterly sales. The
  Swift news did not hold the price.
- **Invalidation:** monthly revenue below $4M; quarterly releases above 20M LINK;
  reserve purchases stalling.

### ADA — short, avoid for now
- **Thesis:** about $0.9M of fees a year against $6.7B; TVL down 81% in a year to $50M
  (measured). No fee or burn reaches holders.
- **Why not:** already -94% from its high. A spot ETF decision is unresolved (secondary),
  which is binary risk against a short. Funding was negative 39% of the time. No unlock
  overhang to lean on.
- **Invalidation:** a confirmed spot ETF with inflows; stablecoins above $100M with TVL
  stabilising.
- **Priced in?** Mostly yes. Kept in the schema so the system tracks it, but it is the
  weakest of the eight.

## 4. Schemas

Each finalist compiles to one entry in `config/default.yaml`. Example:

```yaml
- id: xrp-short
  base: XRP
  symbol: "XRP/USDT:USDT"   # OKX perpetual swap
  market: swap
  bias: short               # the only direction this setup may trade
  invalidation_price: null  # price that kills the thesis; exits the position if crossed
  bt_spread_bps: 0.9        # backtest assumption, measured on OKX 2026-11-10
  bt_depth_usd: 1000000
```

On every candle the REFLEX returns exactly this, and nothing else (`src/trader/types.py`):

```python
class ReflexDecision:
    regime: "trending" | "mean_reverting" | "high_vol" | "crisis"
    direction: "long" | "short" | "neutral"
    direction_confidence: float   # 0..1
    toxic_flow: bool | None       # None when there is no order book
    setup_quality: int            # 0..3
    risk_state: "safe" | "near_limit" | "reduce"
```

Code then gates it (`src/trader/gate.py`, numbers in `policies/v001.json`):
`setup_quality >= 2`, `direction_confidence > 0.88`, `risk_state == safe` (the worse of
the model's view and the risk layer's), direction equals the setup's bias, and no toxic
flow. Confidence below 0.60 pauses that symbol for 12 candles; a `crisis` reading pauses
all new risk for 72 candles after the last crisis reading. Both raise an alert.

Fundamental invalidation conditions (revenue, TVL, governance votes) are **not**
automated. They are checked in the review loop and need a human or the BRAIN to disable
the setup. Only price invalidation is wired into code.

## 5. Sources

Measured: OKX public API, Binance public data API, CoinGecko API, DefiLlama API
(fees, protocols, chain TVL) and DefiLlama stablecoins API, all pulled 2026-11-10.

Secondary (unverified; search summaries only):
- Aave buyback pause: https://governance.aave.com/t/arfc-pause-aave-buybacks/24686 ;
  restart thread https://governance.aave.com/t/restart-aave-buy-backs/24936
- Aave V4 launch: https://thedefiant.io/news/defi/aave-v4-launches-on-ethereum-mainnet
- HYPE vesting: https://tokenomist.ai/research/hype-tokenomics-330k-or-9-9m-hype-unlocks
- Uniswap burn: https://cointelegraph.com/news/uniswap-executes-100m-uni-burn-after-fee-switch-approval
- Tron fee cut: https://cointelegraph.com/news/tron-proposal-789-transaction-fees-vote ;
  supply balance https://cryptoticker.io/en/tron-trx-supply-burn-balance/
- Chainlink reserve: https://cryptoticker.io/en/chainlink-reserve-six-million-link/
- Sky buyback cut: https://www.kucoin.com/news/flash/sky-protocol-proposes-temporary-sky-buyback-reduction-to-strengthen-usds-capital-buffer
- FOMC October 2026: https://investinglive.com/central-banks/the-full-statement-from-the-october-2026-fomc-rate-decision/
- BTC ETF flows: https://www.tftc.io/bitcoin-etf-flows/november-2026
- USDT burn: https://cryptobriefing.com/tether-burns-2-billion-usdt-treasury/

Not found: active-user counts, primary top-holder tables, official LINK release
schedule, XRP 2026 net sales by Ripple, the outcome of the Grayscale ADA ETF decision.
