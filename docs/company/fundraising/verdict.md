# Fundraising Verdict: Raise, Bootstrap, or Accelerator?

**Owner:** fundraising-advisor · **Date:** 2026-09-24 · **Status:** recommendation for founder decision
**Inputs:** `docs/chimera/01–05`, `market/first-market-selection.md`, `competitors/smb-landscape-2026.md`, `product/catalog.md`, `product/prd-wisp-evidence-pack.md`, `finance/model-summary.md`, `finance/pricing.md`, `finance/90-day-budget.md`, `legal/entity-options.md`, `legal/launch-checklist.md`, `engineering/codebase-audit.md`, `sales/pipeline.csv` (empty)
**Evidence status:** 0 interviews, 0 customers, 0 revenue, no entity, no domain. `interviews/synthesis.md` does not exist. Every demand number in this folder is an **assumption** or a **projection** from `model-24mo.csv`.

---

## 1. Verdict (3 lines)

1. **Bootstrap through 15 December 2026. Do not raise, and do not spend October–November preparing to raise.** You need about **$1.1k** (base) to **$3.5k** (conservative) of your own cash, with no salary. No investor writes a cheque that small, and there is nothing yet to price a round on.
2. **The Oct 15 – Dec 15 PTIN window is the whole game this year.** Every hour spent on decks in that window is an hour not spent on the 100 touches and ~30 conversations that decide whether this is a business. Missing the window pushes first real revenue to May 2027 (`model-summary.md` §6.3).
3. **Revisit in the Jan–Apr 2027 dead season** with real numbers. That's when you have time to write applications, and it lines up with YC's Spring/Summer 2027 cycles and the RSAC timeline. If Dec 15 shows the milestones in §4, apply to an accelerator then. If not, stay a profitable side business, which is a perfectly good outcome.

**One optional exception:** YC Winter 2027 (on-time deadline reported as **2 Nov 2026, 8pm PT**, third-party sources; ycombinator.com was blocked from this session). Its batch runs **Jan–Mar 2027, exactly the tax-season dead period**, so the timing is unusually good. Odds are low (solo, 0 traction, services-heavy wedge, niche market). Only apply if (a) you are US-resident **or** a Nepali lawyer has cleared you to own US shares, and (b) you cap the effort at **4 hours**, reusing `one-pager.md`. Don't prep for an interview until someone invites you.

---

## 2. Why not raise now

| Factor | What the evidence says | Implication |
|---|---|---|
| **Capital need** | Peak cash need **$1,148 base / $3,546 conservative** with no founder pay. **$12,860** with a $2,000/mo salary from month 1 (`model-summary.md` §5) | The need is too small for equity. Dilution to fund $1–13k is expensive. |
| **Traction** | 0 interviews, 0 paying firms, empty pipeline | Nothing for an investor to underwrite except the founder. Pre-traction solo founders raise mostly on track record, which we haven't documented (see §5). |
| **What money would buy** | Founder hours are the constraint, not dollars. The best channel (LinkedIn + cold email) costs **$67 cash CAC** and paybacks are immediate because the pack is paid up front (`model-summary.md` §3). | More money would not speed up the first 10 sales. It would only pay the founder. |
| **Venture scale** | Accounting SAM (reachable ICP) **$8.8M–$26.7M/yr**, 3-year SOM **$178k–$355k ARR** (assumptions, `first-market-selection.md` §3). Adding dental: SAM **$28M–$86M**. Base case M24 ARR **$51.7k** (projection). | As written, this is a strong **small business**, not yet a venture story. A VC needs a credible path to $10M+ ARR, which means multi-vertical and/or an MSP channel. That story is untested. |
| **Competition** | Guardz ($84M raised, SentinelOne-backed), Coro (~$280M raised), Huntress ($250M+ ARR). Our white space is narrow: owner-direct, no MSP, plain-English, trigger-shaped (`smb-landscape-2026.md`). | Investors will ask "why won't Guardz do this" before they ask anything else. We need customer evidence, not an argument (see `investor-qa.md` Q1). |
| **Founder/legal** | Country unknown. If Nepal-resident, the **Act Restricting Investment Abroad (1964)** may bar a Nepali citizen from holding Delaware shares without an exemption; Mercury won't bank Nepal residents; Stripe is unclear (`entity-options.md`). | If you're in Nepal, you **may not be legally able to accept a US SAFE** today. Get the lawyer's written opinion before any accelerator application. |
| **Seasonality** | No accounting sales Jan–mid-Apr; May churn spike on monthly subscribers | Investors will want to see a **full cycle**: sell in Q4, retain through tax season, survive May. That data exists by **June 2027** at the earliest. |

**What bootstrapping costs you:** speed on dental and product automation, and no founder salary before ~month 8 (base). If you need income before then, the honest answer is a job, savings, or a non-dilutive loan (see `funding-sources.md`, Nepal Startup Enterprise Loan), not a seed round.

---

## 3. Decision tree by founder situation

| If you… | Do this |
|---|---|
| **Live in the US, can go 8+ months without salary** | Bootstrap. Optional 4-hour YC W27 application. Form a home-state LLC (convert later) per `entity-options.md`. |
| **Live in the US, need income now** | Keep a job or contract work part-time; the model works part-time (~8 packs deliverable at 20 h/wk, `pricing.md` §3c). Don't raise $13k of equity for salary. |
| **Live in Nepal** | **No US equity of any kind until a Nepali FX/corporate lawyer gives a written opinion** on the Act Restricting Investment Abroad and FERA §10A. Do discovery now; sell via the path legal-ops recommends. Watch for the **IEDI Startup Enterprise Loan** next call (up to NPR 20 lakh at 3%, which is roughly the $12.9k salary gap; unverified timing, needs a Nepal-registered startup). |
| **Nepali citizen living outside Nepal (NRN)** | Probably the US path under your residence country's rules; confirm your status first (`entity-options.md` §3). |

---

## 4. Milestones that would change the answer

All targets are for the founder's own decision-making. Figures in brackets are the base-case **projection** they're compared against.

### A. Kill or re-plan signals (check on 1 Dec and 15 Dec 2026)
- **Fewer than 3 paid packs by 15 Dec** [base 4.9, conservative 2.6] → you're tracking conservative. Don't apply anywhere. Re-plan in January, as `model-summary.md` §5 says.
- **0 sales from 30+ qualified conversations by 1 Dec**, or **3+ of the first 6 accounting interviews anchor WISP value under $100** → trigger the self-serve $79–149 pivot (`prd-wisp-evidence-pack.md` §9). Fundraising is off the table until the new offer sells.

### B. "Stay bootstrapped, but take a small angel/friends cheque if you need salary" (target: 15 Dec 2026 to 31 Mar 2027)
All of these together:
1. **10+ paying firms** (packs), at least half at a price above the $495 founding price or with a repeat referral.
2. **5+ Watch subscribers**, at least half on **annual prepay** [base: ~45% attach].
3. Founder delivery time **≤4 h per pack** after pack 3 (`prd` AC14) [assumption 4.5–6 h].
4. One channel with a measured, repeatable funnel (e.g. cold email: ≥8% reply, ≥20% call-to-close) [assumption 8% / 25%].
5. Entity, bank and payments working in a structure your lawyer has cleared.

At that point a **$25k–$75k angel or friends-and-family SAFE** could fund a founder salary through tax season and the dental build. It still isn't necessary if you're default-alive.

### C. "Apply to an accelerator (YC, Techstars) or raise a real pre-seed" (target: by June 2027)
All of these:
1. **$3,000+ MRR** from Watch (≈29 subscribers at blended $103.55), or **$5k+ MRR** counting annualized pack/refresh revenue [base M12 Watch MRR $1,180, aggressive $3,136].
2. **Retention signal through a full cycle:** Watch monthly logo churn **≤3%** averaged Jan–Jun 2027, **including May** [base effective churn 3.5% with a +6 pt May spike]. This is the single most important number you can bring an investor.
3. **Second segment proof:** **3+ paying dental** practices (or another vertical) on the same engine, showing the "compliance evidence for regulated SMBs" platform, not a one-niche service.
4. **Productization proof:** at least one sale that happened **without a founder call** (self-serve S5 → paid), or delivery under 2 h/pack.
5. **Defensibility evidence:** a quote-level answer from customers on why they chose us over their MSP, a $29 template, or Guardz/Microsoft (see `investor-qa.md`).
6. **Clean cap table and entity** investors can actually invest into (Delaware C-corp, or a lawyer-approved Nepal-parent structure).

If A fires, the answer stays "bootstrap". If B is hit, take small money only for salary. If C is hit, the story becomes venture-shaped and YC/Techstars/security angels (`funding-sources.md`) become worth the time.

---

## 5. What an investor would see today (candid)

**Strengths**
- A **real, dated buying trigger**: the W-12 line 11 WISP attestation at PTIN renewal and the FTC Safeguards Rule, which applies to tax preparers at any size (Fact, sourced in `first-market-selection.md`).
- **Capital efficiency:** default-alive on ~$1k, 94% cash gross margin on Watch (estimate), and pack revenue up front.
- **Honest, well-scoped plan:** kill/pivot rules, measurable acceptance criteria, legal risks flagged.

**Weak spots, and the evidence that fixes each**

| Weak spot | Evidence that would fix it |
|---|---|
| No customer evidence at all | 10 interviews logged in `interviews/raw/` with exact quotes; 3+ paid packs |
| "A WISP is a $29 template" | Price anchors from interviews ("I paid $X / spent Y hours last year"); packs sold at $795 list, not just $495 founding |
| Revenue is mostly services (75% of base-case year-1 cash) | Logged hours per pack trending to ≤4 h; % of pack text reused across firms |
| Seasonal cliff Jan–Apr, May churn | Annual-prepay share of Q4 Watch sales; actual May 2027 churn |
| Small first market | Dental pilot results; MSP partner interest (even 2 LOIs) |
| Solo founder, background undocumented | A founder slide with verifiable security/compliance credentials, or an advisor from the accounting world |
| Prototype code is not deployable (`codebase-audit.md`) | S5 readiness check live and passing our own security bar; this matters more for a security company than most |
| Legal structure unknown | Lawyer's opinion (Nepal) or a formed entity with bank + Stripe |

---

## 6. Top 3 gaps to close before pitching anyone

1. **Customer proof.** 0 interviews and 0 paying firms. Close it with 10 interviews (6 accounting, 4 dental) by mid-October and **3+ paid packs by 15 Dec 2026**, with price-anchor quotes. Nothing else in the pitch matters until this exists.
2. **Retention through the season.** No evidence Watch survives Jan–Apr and the May cliff. Close it with Q4 Watch attach (target ≥45% of pack buyers) and the **annual-prepay share**, then report actual churn through June 2027.
3. **Fundable structure and a venture-sized story.** Founder location, entity and (if Nepal) outward-investment clearance are unresolved, and the accounting-only market caps out near $0.2–0.4M ARR at 3 years (assumption). Close it with the lawyer's opinion and a **dental or MSP proof point** showing the engine carries to a second regulated vertical.

---

## 7. Next actions for the founder (fundraising-related only)

| By | Action | Time |
|---|---|---|
| 1 Oct 2026 | Tell legal-ops your country of residence (`launch-checklist.md` 0.1). Everything else depends on it. | 5 min |
| After domain + website exist | Apply to the no-investor cloud credit tiers you'll actually use (see `funding-sources.md` §1). | 1 h total |
| 2 Nov 2026 (optional) | YC W27 application, **only** under the conditions in §1. | ≤4 h |
| 1st of each month | Send the monthly update (`update-template.md`) to 3–5 advisors, even with bad news. It builds the track record investors look for. | 45 min |
| 15 Dec 2026 | Fill in the traction slide (`pitch-outline.md` slide 9B) with actuals. Decide A/B/C from §4. | 1 h |
| Jan–Feb 2027 | If B or C: prepare applications (YC Spring/Summer 2027, security angels). If A: re-plan with finance-modeler. | — |
