# ChimeraShield 24-Month Model: Summary (v2, Australian Pty Ltd, plan C)

**Owner:** finance-modeler (CFO) · **Date:** 2026-09-26 (v1 2026-09-24) · **Period:** M1 = Oct 2026 to M24 = Sep 2028
**Currency:** **AUD** (the reporting currency of ChimeraShield Pty Ltd), **ex GST**. US prices are set in USD and converted. Key numbers also shown in USD.
**FX:** **US$1 = A$1.4286 (AUD/USD 0.70)**, rounded from the **0.7027 spot on 25 Sep 2026** ([Trading Economics](https://tradingeconomics.com/australia/currency), search summary). It's one cell in the CSV (`fx_usd_per_aud`).
**Files:** `model-24mo.csv` (Block 1 = every assumption with its label; Block 2 = monthly rows × 3 scenarios) · `pricing.md` · `90-day-budget.md`

> This is planning support, not tax or accounting advice. Before registering for GST, choosing how the founder is paid (wages + super vs dividends; Division 7A) or filing anything, use an Australian accountant, ideally one with US–AU experience for W-8BEN-E.

**How to open:** import `model-24mo.csv` into Google Sheets or Excel. The assumptions are the rows above `# BLOCK 2`, grouped by `##` headers. Filter Block 2 on `scenario`. Customer counts are fractional expected values. Cash basis: annual prepay is counted when collected, and `watch_mrr_aud` spreads it.

**What changed from v1:** (1) Stripe **Australia** fees: US cards 3.5% + A$0.30 plus ~2% conversion, AU cards 1.7% + A$0.30; Stripe Tax dropped to 0. (2) Costs in AUD: Pty Ltd A$636 + A$342/yr, accountant A$1.5k–4k/yr + A$300–500 consult, **insurance A$3.5k–8k/yr** (conservative A$8k / base A$5.5k / aggressive A$3.5k), US mailbox, Xero. (3) **US$300 Google Ads** Oct–Dec. (4) **AU segment:** pilots in Nov–Dec 2026 (cons 1 / base 2 / agg 2) at A$750, then gated AU sales from Feb 2027 at A$ prices. (5) **US dental moved later** (base M4 → **M8, May 2027**; cons M10; agg M6), because plan C spends Feb–Apr 2027 founder time on the AU window. (6) Founder pay targets are now **A$3,000 and A$7,500 a month plus 12% super**.

---

## 1. The three numbers that matter

1. **Break-even moves from 7 to 8 Watch subscribers** for all non-salary costs (A$1,040/mo ≈ US$728, was US$612). To pay the founder **A$3,000/mo + super**, you need **33 subscribers** (the v1 target of US$2,000/mo needed 27; the same US$2,000 at today's FX and costs needs 29). The base case gets to 33 in **M20 (May 2028)**, five months later than v1's M15.
2. **90-day budget: ≈ A$3,090 minimum / ≈ A$13,070 comfortable** (US$2,160 / US$9,150). Insurance paid upfront is A$5,750 of the comfortable figure.
3. **Peak cash need (no founder pay): A$2,173 base** (≈US$1,520; v1 US$1,148), **A$9,132 conservative** (v1 US$3,546). Default alive on a shoestring in base and aggressive; conservative is fragile (§5).

---

## 2. Scenario results (AUD unless noted)

| Metric | Conservative | Base | Aggressive |
|---|---|---|---|
| Packs by mid-Dec 2026 (US + AU pilots) | 2.6 + 1 | **4.9 + 2** | 8.4 + 2 |
| Packs sold, 24 months (all) | 33 | **75** | 168 |
| US dental starts | M10 (Jul 2027) | **M8 (May 2027)** | M6 (Mar 2027) |
| Watch subscribers M12 (Sep 2027) | 4.5 | **13.7** | 34.1 |
| Watch subscribers M24 (of which AU) | 13.9 (1.4) | **44.7 (4.5)** | 122.8 (11.3) |
| Watch MRR M12 | A$302 | **A$1,127** | A$3,987 |
| Watch MRR M24 (ARR) | A$1,457 (A$17.5k ≈ US$12.2k) | **A$5,831 (A$70.0k ≈ US$49.0k)** | A$17,285 (A$207k ≈ US$145k) |
| Cash collected, year 1 / year 2 | A$11.6k / A$41.8k | **A$28.8k / A$119.0k** | A$68.9k / A$303.8k |
| Pack share of year-1 cash (AU packs' share) | 81% (17%) | **76% (14%)** | 69% (9%) |
| **Peak cumulative cash need (no founder pay)** | **−A$9,132** | **−A$2,173** | −A$851 |
| Net cash positive every month from | M11 (Aug 2027) | **M7 (Apr 2027)** | M5 |
| Net cash > A$2,000 every month from | M20 | **M11** | M7 |
| Cumulative cash at M24 (no founder pay) | +A$14.4k | **+A$111.5k (≈US$78k)** | +A$327.6k |
| Peak founder delivery hours/month | 19 | **51** | 130 (over ~96 h in Aug–Sep 2028: hire) |

**Seasonality (Assumption):** US accounting new sales Oct 1.2 (×0.6 in Oct 2026), Nov 1.5, Dec 0.9, Jan 0.05, Feb–Mar 0, Apr 0.2, May–Sep 0.5–0.8, with a May churn spike for US monthly payers. **AU accounting:** Jan 0, **Feb 0.8, Mar 1.0, Apr 0.6**, May–Oct 0.2–0.3 (lodgment peak), **Nov 1.0**, Dec 0.4. The two calendars complement each other: AU fills the US Jan–Apr gap, but only after the 15 Feb 2027 gate.

**What the AU pilot does to the numbers (base):** the 2 pilots add A$1,470 net in Nov–Dec 2026. That's about a quarter of 90-day cash, and it also tests the price. Gated AU sales from Feb 2027 add ~8 more packs (≈10 AU packs in total) and 4.5 subscribers by M24. AU is **~14% of year-1 cash**: a learning market, not the revenue plan, as the market doc intends.

---

## 3. Unit economics (base; details in `pricing.md` §4)

| Metric | US (USD price) | AU (AUD price) | Note |
|---|---|---|---|
| Blended ARPA | A$147.93 (US$103.55) | A$159.08 | 10/60/30 tier mix; 30% (US) / 25% (AU) annual |
| Stripe fees, all-in | ~6.2–6.4% | ~2.6% | US: 3.5% intl + 2% FX + 0.7% Billing + A$0.30 |
| Cash COGS per sub per month | A$11.69 | A$6.11 | LLM A$0.64–0.87, infra A$1.43, rest Stripe |
| **Cash gross margin** | **92%** (v1 94%) | **96%** | ~75% / ~84% with founder time at A$50/h |
| Contribution per sub per month | A$136.24 (US$95.37; v1 US$97.48) | A$152.97 | |
| Watch lifetime / LTV | 28 mo / A$3,869 | 31 mo / A$4,755 | Base churn 3.5%/mo, 75% annual renewal |
| LTV per Pack buyer | A$3,037 (US$2,126) | A$3,558 | Pack + 45% attach + refresh |
| Pack net, founding | A$665 (US$466; v1 US$476) | A$734 | ~5.8% fee drag on US cards |

**CAC (loaded, A$50/h):** US LinkedIn/cold email **A$495** (6.1× LTV/CAC), partners A$632 (4.8×), content A$1,075 (2.8×), AU in-person pilots ~A$650 (5.5×). The **US$300 Google test works out to A$571–2,857 cash per pack**, so judge it on cost per completed check, not Pack CAC. **Payback:** every channel except the Google test is paid back by the Pack's gross profit on day one.

---

## 4. Break-even (AUD, base cost levels)

**Running costs after launch: A$1,040/mo (≈US$728)** = tools and infra A$345 (Workspace, domains, Xero, hosting, email service, Sales Navigator, US mailbox, other tools) + insurance A$458 (A$5.5k/yr) + accountant A$208 + ASIC A$28.50. **The range is A$790–1,374/mo** across the insurance (A$3.5k–8k) and accountant (A$1.5k–4k) estimates. v1 was US$612 = A$874.

| Target | Monthly cost | **US Watch subs (blended)** | Subs at US$49 | AU subs (blended) | Or US packs/mo | **v1 (USD)** |
|---|---|---|---|---|---|---|
| (a) Tools + infra only | A$345 | **3** | 6 | 3 | 0.3 | 3 |
| (a) All non-salary costs | A$1,040 | **8** | 17 | 7 | 0.9 | 7 |
| (b) + A$3,000/mo founder pay + 12% super | A$4,400 | **33** | 70 | 29 | 3.7 | 27 (at +US$2,000) |
| (b′) like-for-like: + US$2,000 (A$2,857), no super | A$3,898 | 29 | 62 | 26 | 3.3 | 27 |
| (c) + A$7,500/mo founder pay + 12% super | A$9,440 | **70** | 150 | 62 | 8.0 | 58 (at +US$5,000) |

**Why break-even rose:** about +A$165/mo of fixed costs (mostly insurance with US cover, the accountant and Xero) and ~A$3 less contribution per US subscriber from fees. On top of that, super is added to founder pay. The FX move (0.65 → 0.70) *helps* on USD costs but *hurts* on USD revenue, and nets out small.
**When base reaches it on Watch alone:** 8 subs in **M9 (Jun 2027)** (v1: 7 in M8). 33 subs in **M20 (May 2028)** (v1: 27 in M15). 70 not within 24 months (44.7 at M24). **Counting Pack cash**, A$3,000 + super is covered every month from **M12 (Sep 2027)** and A$7,500 + super from **M20**.
Servicing 70 subscribers takes ~35 founder hours a month, which one person can do.

---

## 5. Runway and default-alive check

- **Zero-revenue burn: ~A$1,040/mo** plus ~A$2,040 of one-offs in October (ASIC, accountant consult, legal review, base levels). A$5,000 of founder cash is about **3 months** of runway with no sales. A$10,000 is about **8 months**.
- **Starting cash is unknown**, so the model reports the **peak cash need** (the lowest point of cumulative cash), which is the amount the founder must put in.

| Founder pay | Conservative | Base | Aggressive |
|---|---|---|---|
| None | need **A$9,132**; positive from M11 | need **A$2,173**; positive from M7 | need A$851 |
| A$3,000 + super **from M1** | never recovers (−A$66k at M24) | need **A$29,409** | need A$13,986 |
| A$3,000 + super **from M13** | need A$26,042; ends −A$25.9k | need A$2,173 (no deeper dip) | need A$851 |

**Verdict:** **default alive in base and aggressive, as a no-salary business until about M12**, if the founder can put in ~A$2,200 (plus a buffer: plan on A$5,000). **Conservative is not default alive with any salary.** Even with no pay, it needs ~A$9,100 because A$8k insurance and slower dental eat the thin revenue. **Tripwires:** fewer than 3 packs (US + AU) by 15 Dec 2026 means you're tracking conservative, so re-plan in January. An insurance quote above A$6k/yr adds ~A$40/mo to break-even per extra A$500 (~0.3 subs), so it's worth shopping.

---

## 6. Risks

1. **No willingness-to-pay evidence in either country.** 0 interviews. The AU pilot prices (A$750, A$79–229) and the US prices are assumptions. The first 6 interviews per market matter more than any modeling.
2. **Insurance is the biggest unknown cost.** A$3.5k–8k/yr is unverified, and US/Canada jurisdiction may be excluded or heavily loaded. The A$3.5k–8k range alone moves break-even by ~3 subscribers and peak cash need by ~A$2–3k. **Get 2–3 broker quotes this week.**
3. **FX exposure.** Revenue is mostly USD, costs mostly AUD. At 0.65 (AUD weaker), US revenue is worth ~8% more in AUD. At 0.75 it's worth ~7% less. It's one cell in the CSV, so re-run when it moves more than 5%.
4. **Payments.** Stripe AU approval, the 2% conversion (USD settlement is "limited") and the 5.8% drag on US Packs. Mitigate with bank-transfer invoices via a multi-currency account (`pricing.md` §4c).
5. **Founder bandwidth across two countries and time zones.** 07:00–10:00 Sydney US calls plus AU daytime pilots. Moving dental to M8 is the price of plan C. If the founder runs both anyway, base is optimistic on hours.
6. **Seasonal cliff (US).** No US accounting sales Jan–mid-Apr. The AU Feb–Apr window only helps if the 15 Feb gate passes.
7. **GST/tax setup.** Unregistered, offshore SaaS GST costs ~A$50/mo extra. Wrong export treatment or Division 7A on founder draws are the tax traps. **Accountant consult before the first invoice.**
8. **Unverified sources.** Stripe AU fees, ASIC fees, FX and competitor prices come from search summaries. Verify before external use.
