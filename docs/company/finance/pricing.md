# ChimeraShield Pricing (v2: US + Australia)

**Owner:** finance-modeler (CFO) · **Date:** 2026-09-26 (v1 was 2026-09-24) · **Status:** recommendation for founder decision
**Currency:** US prices in **USD**, Australian prices in **AUD ex GST**. Company books are in **AUD** (ChimeraShield Pty Ltd).
**FX used everywhere:** **US$1 = A$1.4286 (AUD/USD 0.70)**, rounded from the **0.7027 spot on 25 Sep 2026** ([Trading Economics](https://tradingeconomics.com/australia/currency), search summary, page not opened). The earlier planning rate of A$1.53 (0.65) is ~2 months stale. It's used below only as a sensitivity.
**Inputs:** `product/catalog.md`, `product/prd-wisp-evidence-pack.md`, `product/prd-au-client-data-pack.md`, `market/first-market-selection.md`, `market/australia-vs-us.md`, `legal/australia-founder.md`, `legal/entity-options.md`, `competitors/smb-landscape-2026.md`.
**Model:** `model-24mo.csv` (assumptions block at the top) · **Summary:** `model-summary.md` · **Cash plan:** `90-day-budget.md`

> **Evidence status.** 0 customer interviews in either country, so **no price below is backed by willingness-to-pay data**. Labels: **Evidence** = public price or rule found by search (pages mostly not opened; **S** = search summary); **Estimate** = my estimate; **Assumption** = unvalidated; **Decision** = recommended price.
> Planning support only, not tax or accounting advice. GST registration and export treatment must be confirmed by an Australian accountant.

---

## 1. Recommended prices

### 1a. United States (USD, unchanged from v1)

| Offer | Price | Who | Label |
|---|---|---|---|
| Free WISP & Safeguards Readiness Check (S5) | $0 | Work email on the firm's own domain | Decision |
| **WISP & Evidence Pack: Founding** | **$495 one-time** | First 10 packs **or** until 31 Dec 2026 | Decision |
| **WISP & Evidence Pack: Standard** | **$795** | 5–15 staff | Decision |
| **WISP & Evidence Pack: Plus** | **$1,195** | 16–50 staff | Decision |
| Annual WISP Refresh | $395/yr | Pack-only customers. Included in Watch annual | Decision |
| **Watch: Founding** | **$49/mo** ($490/yr) | First 10 US subscribers, locked 24 months | Decision |
| **Watch: Solo / Standard / Plus** | **$49 / $99 / $149 per month** ($490 / $990 / $1,490 per year) | 1–4 / 5–15 / 16–50 staff | Decision |
| Pack credit toward Watch annual | $300 (list pack) / $150 (founding pack), within 30 days of debrief | | Decision |

**US prices are not raised for the higher Australian Stripe fees.** The extra ~2.1 points of fees cost about US$2 a month on a $99 plan (§4). That's not worth a price change before any customer has paid. Do reduce the fee (§4c).
Invoices and ToS must say **prices are in USD**. Invoices show **GST 0% (GST-free export)** if we are GST-registered (`legal/australia-founder.md` §1.4, **FLAG** accountant under GSTR 2025/2).

### 1b. Australia (AUD, ex GST): Client Data Security Pack (TPB & TFN ready) and Watch (AU)

**Reconciled with `product/prd-au-client-data-pack.md`:** the Pack founding price is **A$750** and Watch is **A$79 / A$149 / A$229**, the same as the PRD. I added the list and Plus Pack prices, the founding caps and the staff bands (1–4 / 5–14 / 15–50, taken from the PRD intake). **The PRD's A$1,200 list becomes A$1,195.** The only reason is the price-ending convention. **Product should now take AU prices from this table.**

| Offer | Ex GST (the price) | Incl. GST, shown only once we're GST-registered | Who | Label |
|---|---|---|---|---|
| Free Tax Practice Data Security Check (S5-AU) | A$0 | A$0 | Work email on the practice's own domain | Decision |
| **Client Data Security Pack: Founding (pilot)** | **A$750 one-time** | A$825 | First **5** AU packs **or** until **31 Mar 2027**, whichever is first. Covers the Nov–Dec 2026 pilots and the Feb–Mar 2027 window | Decision |
| **Client Data Security Pack: Standard** | **A$1,195** | A$1,314.50 | 5–14 staff | Decision |
| **Client Data Security Pack: Plus** | **A$1,795** | A$1,974.50 | 15–50 staff (likely above A$3M turnover, so a full APP entity: more scope) | Decision |
| Annual Policy Refresh | A$595/yr | A$654.50 | Pack-only customers. Included in Watch annual | Decision |
| **Watch (AU): Founding** | **A$79/mo** (A$790/yr) | A$86.90 (A$869) | First **5** AU subscribers, any size, locked 24 months | Decision |
| **Watch (AU): Solo** | **A$79/mo** (A$790/yr) | A$86.90 | 1–4 staff | Decision |
| **Watch (AU): Standard** | **A$149/mo** (A$1,490/yr) | A$163.90 | 5–14 staff | Decision |
| **Watch (AU): Plus** | **A$229/mo** (A$2,290/yr) | A$251.90 | 15–50 staff | Decision |
| Pack credit toward Watch annual | A$450 (list) / A$225 (founding), within 30 days of debrief | same (credit is ex GST) | | Decision |
| Annual prepay | 10 months for 12 (~17% off) | | | Decision |

**Why these AU numbers**
- **Not straight FX conversions.** At 0.70, US$795 is A$1,136 and US$99 is A$141. I set AU a little above parity because **our Stripe cost is lower in AU** (1.7% domestic vs 5.5% for US cards with conversion) and there's no US-style sales-tax risk. I also kept them at **"A$…9 / A$…5"** points AU buyers expect. The A$79/149/229 grid also matches the market doc's SAM math (`market/australia-vs-us.md` §4).
- **Founding A$750 (≈US$525)** is close to the US founding $495. It sits **under the A$1,000 mental line** and far below vendor Essential Eight assessments at **A$3k–8k** (Evidence (S), CISO Advisory via market doc §5). The PRD's pilot price signal is "≥3 of 6 interviewees name ≥A$500". A$750 tests just above that.
- **The Practice Protect anchor.** It is listed "from $17/month" (third-party, unit unclear). It's per-user infrastructure, not a plan plus evidence. Our A$149 Standard for a 5–14 person firm is about **A$11–30 per staff member**, so we compare on the owner's total, not per user.
- **Stale 2019 data says half of small firms spend under A$500 a year on cyber.** That's the biggest risk to A$1,195 list. **Kill/adjust rule (PRD):** if 3 or more of the first 6 principals anchor under A$300, drop to a **A$395 Lite** Pack and put the value into Watch.
- **The founding cap is 5, not 10.** Australia is a ~A$7.9M SAM pilot (vs ≈A$27M US). We need a price signal, not volume.

**GST display rule (Assumption; FLAG accountant + legal-ops)**
- Our buyers are businesses. Show **"A$149/month + GST"** with the GST-inclusive figure next to it ("A$163.90 incl. GST"). My understanding is that the ACL single-price rule has a business-to-business carve-out; **legal-ops to confirm** before the AU pricing page goes live. Never show only an ex-GST price where a sole-practitioner or consumer could read it as the total.
- **Until ChimeraShield is GST-registered, don't add GST or write "+ GST".** The ex-GST number is then the whole price, and invoices say "No GST has been charged". Registration is **required** only once GST turnover reaches **A$75k** (which counts GST-free exports), so we're far below it. My recommendation is to **register voluntarily before the first AU invoice (~3 Nov)**. It costs nothing to register. We then claim back GST on AU and offshore costs (about A$50/month plus ~A$850 on the comfortable 90-day budget, see `90-day-budget.md`), and US sales stay GST-free. The price is quarterly BAS lodgement. **Accountant decides.**
- AU tax invoices over A$82.50 incl. GST to GST-registered buyers need the full tax-invoice fields (**FLAG** threshold).

### 1c. Value metric and annual discount (both markets)
- **Per firm, banded by staff count. Not per seat and not per domain.** Competitors charge per user or device (Coro ~$9.50/user, Business Premium $22/user, Verito $129/user + $500 setup, managed IT $125–200/user). A flat firm price is easy to understand. Almost every ICP firm has exactly one domain.
- **Annual = 10 months for 12.** In the US, push it hard Oct–Dec so firms are covered through tax season. In AU, push it in the Nov–Dec pilots and the Feb–Mar window, before the AU peak season (Jul–Oct) when owners stop reading vendor email.
- **Founding Watch price lock: 24 months, not lifetime** (v1 reasoning unchanged).

---

## 2. Why these prices: anchors and value

### 2a. Competitor and substitute anchors

| Anchor | Price | What it means for us | Label |
|---|---|---|---|
| IRS Pub 5708 sample WISP (US) | Free | The floor: a template the firm fills in itself | Evidence ([IRS](https://www.irs.gov/newsroom/written-information-security-plans-are-essential-for-tax-pros)) |
| WISP templates (US) | $29/yr up to $999 | The "$29 template" risk. We sell firm-specific facts + verified evidence + a fix plan | Evidence (market doc) |
| Verito VeritComplete (US tax-firm managed IT incl. WISP) | $129/user/mo + $500 setup | ~$7,700/yr for 5 users. Our $795 + $990/yr is about a quarter of that | Evidence (S, [Verito](https://verito.com/blog/managed-it-pricing-accounting-firms/)) |
| Managed IT for accounting firms (US) | $125–200/user/mo | We serve the firms without it | Evidence (S) |
| Coro / M365 Business Premium / Huntress | ~$9.50/user · $22/user · ~$450/mo floor | Tools the owner can't run alone | Evidence (3P, landscape doc) |
| **Practice Protect (AU)** | "from $17/month" (unit and currency unclear) | Incumbent for AU accountants, ~1,500 firms, insurer discount. We sell a plan + breach plan + evidence, not infrastructure | Evidence (S, third-party; market doc §5) |
| **Essential Eight assessments (AU vendors)** | A$3k–8k | Our A$1,195 Pack is a *snapshot*, not an assessment, at a fraction of the price. Never call it an assessment | Evidence (S, vendor) |
| **ASD Cyber Health Check / IDCARE service (AU)** | Free | The AU free floor, like IRS Pub 5708 | Evidence (market doc) |

### 2b. Value to the buyer
US (v1, unchanged): 10–15 owner hours at $150/h is **$1,500–2,250**; staying insurable, with an MFA premium effect of ~20%, is worth about **$240/yr**. Penalties don't justify the price on their own because enforcement against small firms is thin.
AU (**Assumption**, ask in interviews): 10–12 principal hours at ~A$150–200/h is **A$1,500–2,400**. The TFN/NDB duties apply regardless of turnover, and a written data breach response plan is what the principal reaches for on the day a laptop is stolen. The pitch is calm: "know what you'd do on the day", not fines.

### 2c. What would change these prices
- US kill/pivot: 3+ of the first 6 US interviews anchor WISP value under $100 → self-serve $79–149 generator.
- US raise: interviewees paid $500+ for their last WISP → list $995 / $1,495.
- AU: 3+ of 6 anchor under A$300 → A$395 Lite. 3+ say Practice Protect/MSP "already covers it" → re-point AU to dental (market doc risk 5).
- Either market: founder time above 6 h per pack after pack 3 → raise list or cut scope.

---

## 3. Founder time per Pack and effective hourly rate (AUD)

The time model is unchanged from v1: 9.5 h for packs 1–3, 6.0 h for packs 4–10, 4.5 h from pack 11. The **AU Pack has its own learning curve** because the content is new (PRD AC-D2 target ≤6 h, flag if >8 h).

| Pack | Price | **Net to us (A$)** after fees + ~US$2 LLM | A$/h at 9.5 h | at 6.0 h | at 4.5 h |
|---|---|---|---|---|---|
| US Founding | US$495 | **A$665** (US$466; v1 US$476) | A$70 | A$111 | A$148 |
| US Standard | US$795 | A$1,070 (US$749; v1 US$766) | A$113 | A$178 | A$238 |
| US Plus | US$1,195 | A$1,610 | A$169 | A$268 | A$358 |
| **AU Founding (pilot)** | A$750 | **A$734** | A$77 | A$122 | A$163 |
| AU Standard | A$1,195 | A$1,172 | A$123 | A$195 | A$260 |
| AU Plus | A$1,795 | A$1,761 | A$185 | A$294 | A$391 |

Fee drag on a US pack paid by card is about **5.8%** (3.5% international card + 2% conversion + A$0.30). An AU pack by card costs **~2.1%** (1.7% + A$0.30).
**Capacity by 15 Dec 2026 is unchanged** (~17 packs if the founder is full-time). **Time zones change:** intake and debrief calls with US firms fit **07:00–10:00 Sydney = 12:00–15:00 PT / 15:00–18:00 ET**. Cap it at 2 US calls per morning. AU pilot calls go in local business hours, avoiding 18–25 Nov (BAS week).

---

## 4. Unit economics per customer (Stripe AU fees, AUD reporting)

### 4a. Payment fees: what changed

| | v1 (assumed US Stripe) | **v2 (Stripe Australia account)** | Label |
|---|---|---|---|
| US card, charged in USD | 2.9% + US$0.30 | **3.5% + A$0.30 (≈US$0.21)** | Evidence (S, [Stripe AU pricing](https://stripe.com/au/pricing), [Wise summary](https://wise.com/au/blog/stripe-fees)) |
| USD → AUD payout conversion | none | **+~2%** (0 if Stripe grants a USD settlement account, which is "limited" for AU) | Evidence (S) |
| AU card, charged in AUD | n/a | **1.7% + A$0.30** (reported 1.65% from 1 Oct 2026) | Evidence (S) |
| Stripe Billing (subscriptions) | 0.7% | 0.7% (verify AU rate) | Evidence |
| Stripe Tax | 0.5% | **0%**: monitoring only, no US registrations (legal-ops §1.1) | Assumption |
| **All-in on a US$99 monthly charge** | US$4.36 (4.4%) | **US$6.35 = A$9.07 (6.4%)** | Calculation |
| All-in on an A$149 AU monthly charge | n/a | **A$3.88 (2.6%)** | Calculation |

International card fees are reported to fall to **2.8% from 1 Apr 2027**. That's not modeled; if it happens it's upside of ~0.7 points.

### 4b. Watch COGS and margin (per customer per month)

LLM: Sonnet-class, US$3 in / US$15 out per M tokens. A2 scan (3,500 in + 700 out) = **US$0.021**. US accounting customers use 12 scans a month normally and 30 in Jan–Apr, plus a US$0.09 monthly brief, ×1.3 overhead, giving **US$0.61/mo** on average. AU customers use 12 scans a month (no US tax season): **US$0.45/mo**. Infra + email US$1.00/mo. All **Estimate**.

| Tier (monthly billing) | Revenue (A$) | Stripe (A$) | LLM + infra (A$) | **Cash COGS (A$)** | **Cash GM** | Loaded GM (founder at A$50/h) |
|---|---|---|---|---|---|---|
| US Founding/Solo US$49 | 70.00 | 4.64 | 2.30 | **6.94** | **90%** (v1 92%) | 54% |
| US Standard US$99 | 141.43 | 9.07 | 2.30 | **11.37** | **92%** (v1 94%) | 74% |
| US Plus US$149 | 212.86 | 13.50 | 2.30 | 15.79 | 93% | 81% |
| **US blended** (10/60/30 mix, 30% annual) | **147.93** (US$103.55) | | | **11.69** | **92%** | ~75% |
| AU Founding/Solo A$79 | 79.00 | 2.20 | 2.06 | 4.26 | 95% | 69% |
| AU Standard A$149 | 149.00 | 3.88 | 2.06 | 5.94 | **96%** | 83% |
| AU Plus A$229 | 229.00 | 5.80 | 2.06 | 7.86 | 97% | 88% |
| **AU blended** (10/60/30, 25% annual) | **159.08** | | | **6.11** | **96%** | ~84% |

**Contribution per blended subscriber: US A$136.24 (US$95.37, v1 US$97.48); AU A$152.97.** An AU subscriber is worth ~12% more to us than a US one after fees and FX.

### 4c. How to cut the US fee drag (in order)
1. **Ask Stripe for USD settlement** after activation. This saves the 2% conversion.
2. **Offer bank transfer for Packs** via a multi-currency account with US receiving details (Wise Business / Airwallex, **FLAG** fees and eligibility). That's ~0.5% instead of ~5.8% on a US$795 Pack, about **US$40 saved per Pack**.
3. **Push annual prepay.** One fixed fee instead of 12, and the conversion hits once.
4. AU customers: offer **BECS Direct Debit** for Watch (cheaper than cards; verify the current Stripe AU rate).

### 4d. LTV and CAC (AUD, base)
| Metric | US | AU | Label |
|---|---|---|---|
| Watch customer lifetime | 28 months | 31 months (no May tax-season churn spike) | Assumption |
| Watch LTV (cash contribution) | **A$3,869** | **A$4,755** | Calculation |
| LTV per Pack buyer (Pack + 45% Watch attach + refresh) | **A$3,037** (US$2,126) | **A$3,558** | Calculation |

| Channel | Cash CAC (A$) | Loaded CAC (A$50/h) | Founder h / customer | LTV ÷ loaded CAC | Pack GP covers CAC on day 1? |
|---|---|---|---|---|---|
| US LinkedIn + cold email | 95 | 495 | 8.0 | **6.1×** | Yes |
| US partners (15% referral fee) | 288 | 632 | 6.9 | 4.8× | Yes |
| US Reddit / content / SEO | 0 | 1,075 | 21.5 | 2.8× | Yes (barely) |
| **US Google Search test, US$300** (ads plan: 3–15 checks, 5% → packs) | **571–2,857** (0.75–0.15 packs) | 888–4,240 | 6–28 | 0.7–3.4× | **Only at the optimistic end** |
| **AU in-person / local calls (pilots)** | ~150 (coffee, parking, event) | ~650 | ~10 | 5.5× | Yes |

**Read:** the US$300 Google test is a **learning spend**, not a profitable channel at this scale. Judge it by cost per completed check (≤US$25 is a win, per `marketing/ads/ads-plan.md` §3), not by Pack CAC. Founder hours, not dollars, remain the scarce input.
