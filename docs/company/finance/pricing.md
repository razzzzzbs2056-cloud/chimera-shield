# ChimeraShield Pricing (v1)

**Owner:** finance-modeler (CFO) · **Date:** 2026-09-24 · **Status:** recommendation for founder decision · **Currency:** USD
**Inputs:** `product/catalog.md`, `product/prd-wisp-evidence-pack.md`, `market/first-market-selection.md`, `competitors/smb-landscape-2026.md`, `legal/launch-checklist.md`. No `engineering/adr-001-mvp-architecture.md` exists, so LLM and infra costs are **CFO estimates** (labeled).
**Model:** `model-24mo.csv` (assumptions block at the top) · **Summary:** `model-summary.md` · **Cash plan:** `90-day-budget.md`

> **Evidence status.** There are 0 customer interviews, so **no price below is backed by customer willingness-to-pay data**. Labels used: **Evidence** = a public price or rule found by search (vendor pages mostly not opened, so verify before quoting); **Estimate** = my estimate; **Assumption** = unvalidated; **Decision** = recommended price.

---

## 1. Recommended prices

| Offer | Price | Who | Label |
|---|---|---|---|
| Free Readiness Check (S5) | $0 | Anyone with a work email on their own domain | Decision |
| **WISP & Evidence Pack: Founding** | **$495 one-time** | First 10 packs **or** until 31 Dec 2026, whichever comes first | Decision |
| **WISP & Evidence Pack: Standard (list)** | **$795 one-time** | 5–15 staff | Decision |
| **WISP & Evidence Pack: Plus (list)** | **$1,195 one-time** | 16–50 staff (more systems, more providers, longer intake) | Decision |
| Pack Lite (optional, not modeled) | $295 | 1–4 staff solo preparers, only if interviews pull for it | Assumption |
| **Annual WISP Refresh** | **$395/yr** | Pack customers **not** on Watch, before the next PTIN window. **Included free in Watch annual.** | Decision |
| **Watch: Founding** | **$49/mo** (or $490/yr) | First 10 Watch subscribers. Price locked for 24 months. | Decision |
| **Watch: Solo** | **$49/mo** / $490/yr | 1–4 staff | Decision |
| **Watch: Standard** | **$99/mo** / $990/yr | 5–15 staff | Decision |
| **Watch: Plus** | **$149/mo** / $1,490/yr | 16–50 staff | Decision |
| MSP / reseller | **Deferred.** Placeholder: 30% off list, wholesale | After 3 MSP conversations | Assumption |
| "Is this safe?" helpdesk (A2) | Included in every Watch tier | Not sold alone | Decision |

**Value metric: per firm, banded by staff count.** Not per seat.
- Every competitor charges per user or device: Coro about $9.50/user, Business Premium $22/user, Verito $129/user plus a $500 setup fee, managed IT $125–200/user. A flat firm price is easy to understand and becomes the comparison point for owners ("less than one user of managed IT").
- Staff bands capture more value from larger firms without seat counting. Our cost per customer barely changes with firm size (§4), but the value and the helpdesk volume do.
- Not per domain: almost every ICP firm has one domain, so pricing by domain would earn nothing extra.

**Annual prepay: pay for 10 months, get 12 (about 17% off).** Push annual hard from mid-October to December. A firm that pays in November is covered through tax season (Jan–Apr), which is when it's most likely to cancel a monthly plan without noticing and most likely to be phished. The model assumes 50% of Oct–Dec accounting subscribers choose annual (base) and 25% in other months.

**Pack fee credit toward Watch: yes, partial and time-boxed.**
- **$300** off Watch *annual* for list-price pack buyers, **$150** for founding pack buyers.
- Only if Watch annual starts within **30 days of the debrief**.
- Not applied to monthly plans, and not refundable as cash.
- **Why not credit the full pack fee?** A full $795 credit on a $990 Standard annual plan means the firm pays $195 for its first Watch year, and the 5–10 founder hours spent on the pack go unpaid. A fixed $300 gives a clear bundle: Pack + Standard annual is **$1,485 instead of $1,785**, which is 17% off. That's enough to tip the decision while keeping the pack profitable. The model includes these credits.

**Founding Watch price lock: 24 months, not lifetime.** The roadmap says "$49/month (lifetime)". Locking 10 subscribers at $49 instead of $99 costs about **$6,000/yr** in lost revenue, every year, forever. A 24-month lock is still generous. **Founder decision.** If you keep "lifetime", nothing else in the model changes.

**Note for `company-context`:** the draft tiers there are "Starter $49, Pro $99, MSP $149". I recommend **Solo $49 / Standard $99 / Plus $149**, sized by staff count, and deferring the MSP tier (first market is owner-direct; the landscape doc shows MSP channels are crowded). I have not edited the skill file; update it if you accept this.

---

## 2. Why these prices: anchors and value

### 2a. Competitor and substitute anchors

| Anchor | Price | What it means for us | Label |
|---|---|---|---|
| IRS Pub 5708 sample WISP | Free | The floor. It's a template the firm fills in itself, with no evidence and no plan | Evidence ([IRS](https://www.irs.gov/newsroom/written-information-security-plans-are-essential-for-tax-pros)) |
| WISP templates | $29/yr (templates) up to $999 | The "$29 template" risk. We must sell firm-specific facts + verified evidence + a fix plan, not a document | Evidence ([2025irswisp.com](https://2025irswisp.com/), [irsptin.com](https://irsptin.com/blog/IRSWISP2025.html); range from market doc) |
| Verito VeritComplete (tax-firm managed IT incl. WISP docs) | $129/user/mo + **$500 setup** (5 users ≈ $645/mo) | A done-for-you WISP bundled into managed IT costs **$500 setup plus ~$7,700/yr**. Our $795 pack + $990/yr Watch is about a quarter of that | Evidence, vendor blog via search ([Verito](https://verito.com/blog/managed-it-pricing-accounting-firms/)) |
| Managed IT for accounting firms | $125–200/user/mo | A 10-person firm pays $15k–24k/yr. We are not replacing this; we're for firms without it | Evidence, vendor benchmark ([Verito](https://verito.com/blog/managed-it-pricing-accounting-firms/)) |
| Coro Essentials | ~$9.50/user/mo (~$143 for 15 users) | Our Plus tier ($149) is about the same money as one IT-grade tool the owner can't run alone | Evidence (3P), landscape doc |
| M365 Business Premium | $22/user/mo | Many ICP firms already pay for it. Watch explains and checks it; it doesn't replace it | Evidence (landscape doc) |
| Huntress EDR | ~$450/mo minimum (50-unit floor) | Direct-buy IT tools are out of reach for 5–15 person firms | Evidence (3P), landscape doc |

**Read:** $795 sits clearly above templates (which is where the done-with-you work justifies it) and far below the $500 setup + $645/mo MSP route. $99/mo is under one user of managed IT.

### 2b. Value to the buyer (why $795 is cheap *if* the pain is real)

| Value driver | Number | Label |
|---|---|---|
| Owner time to do it themselves: 10–15 h to finish the IRS template properly, at a $150/h billable rate during PTIN season | **$1,500–2,250** of owner time | Assumption (hours and rate are mine; ask in interviews) |
| FTC civil penalty exposure (FTC Act §5, inflation-adjusted) | up to **~$51,744 per violation, per day** | Evidence, secondary sources ([Bellator](https://bellatorcyber.com/blog/ftc-safeguards-rule-tax-preparers), [Strategic Micro](https://www.stmicro.net/blog/ftc-safeguards-rule-2026-compliance/)); verify against the FTC's current adjustment. Enforcement against *small* firms looks rare (market doc §6), so don't lead with fear |
| Tax-practice breaches reported to the IRS | ~300 in H1 2025 | Evidence (market doc, secondary) |
| Small-business cyber insurance premium, $1M limit | ~$999–1,550/yr | Evidence, secondary ([MoneyGeek](https://www.moneygeek.com/insurance/business/cyber/cost/), [Insureon](https://www.insureon.com/small-business-insurance/cyber-liability/cost)) |
| MFA premium effect | Discounts of ~18–22% with MFA; +25% or no coverage without it | Evidence, secondary, **unverified** ([beancount.io](https://beancount.io/blog/2026/05/09/cyber-insurance-small-business-2026-mfa-requirements-ransomware-coverage-premium-benchmarks); market doc flags this source) |
| Implied insurance value of the Evidence Report | 20% × $1,200 ≈ **$240/yr** saved, **plus** being insurable at all | Inference from the two rows above |

**Honest read:** the pack pays for itself if it saves the owner about 5–6 billable hours, or if it keeps them insurable. It doesn't pay for itself on penalty avoidance alone, because enforcement against small firms is thin. The pitch should be "sign your W-12 honestly, done in a week", not "avoid a $51k fine".

### 2c. What would change these prices
- **Kill/pivot rule (catalog/PRD):** if 3 or more of the first 6 accounting interviews anchor WISP value under $100, drop the pack to a self-serve $79–149 generator and move the value into Watch.
- If interviewees say they paid an MSP or consultant $500+ for their last WISP, **raise list to $995 / $1,495**.
- If founder time stays above 6 h per pack after pack 3 (PRD AC14), raise list or cut scope. See §3.
- Test $795 against $995 on alternate prospects after the first 10 founding packs.

---

## 3. Founder time per Pack and effective hourly rate

### 3a. Time model (Assumption: nothing has been delivered yet, so log real hours)

| Step | Packs 1–3 (h) | Packs 4–10 (h) | Pack 11+ (h) |
|---|---|---|---|
| Admin: payment, engagement letter, scheduling, intake checklist | 0.50 | 0.25 | 0.25 |
| Intake call (60 min) + prep | 1.25 | 1.25 | 1.00 |
| Passive checks + storing evidence artifacts | 0.75 | 0.50 | 0.25 |
| WISP draft (LLM-assisted from template) + founder edit | 3.00 | 1.75 | 1.25 |
| Evidence Report | 1.00 | 0.50 | 0.40 |
| Fix-First plan | 1.00 | 0.50 | 0.40 |
| QA against PRD AC4–AC11 | 1.00 | 0.50 | 0.30 |
| Debrief call (30 min) + prep | 0.75 | 0.50 | 0.50 |
| 14-day check-in + follow-up email | 0.25 | 0.25 | 0.15 |
| **Delivery total** | **9.5** | **6.0** | **4.5** |
| Selling time per closed pack (not included above; from §5 CAC) | ~7–8 via LinkedIn/cold email, ~7 via partners, ~21 via content | same | same |

### 3b. Effective hourly rate (USD, net of Stripe 2.9% + $0.30, Stripe Tax 0.5% and ~$2 LLM per pack)

| Pack price | Net per pack | $/h at 9.5 h | $/h at 6.0 h | $/h at 4.5 h | $/h incl. ~5 h selling, at 6.0 h |
|---|---|---|---|---|---|
| Founding $495 | $476 | **$50** | $79 | $106 | $43 |
| Standard $795 | $766 | $81 | **$128** | $170 | $70 |
| Plus $1,195 | $1,152 | $121 | $192 | $256 | $105 |
| Blended list ($875 avg) | $843 | $89 | $140 | **$187** | $77 |

The founding price earns about $50/h while the templates are still being built, which is acceptable for 10 learning packs. At list price with a mature process, it's $130–190/h. **Rule:** if delivery is still above 6 h after pack 3, the $795 list price is too low for the work.

### 3c. How many Packs can one founder deliver by 15 Dec 2026?

The window runs 15 Oct (S5 live) to 15 Dec, minus Thanksgiving week, which is about 7.7 working weeks. The last intake call is about 5 Dec (PRD).

| Founder availability | Hours available | Packs deliverable |
|---|---|---|
| Full-time, 20 h/wk on delivery (the rest on selling and product) | 154 | **28** (delivery-only ceiling) |
| Full-time, 40 h/wk total, 20% kept for product/S5, ~8 h selling per close | 246 | **~17** (sell **and** deliver) |
| Part-time, 20 h/wk total, same split | 123 | **~8** |
| Part-time, 8 h/wk on delivery only | 62 | **8** |

**Capacity is not the constraint; demand is.** The base case sells about 5 packs by December (conservative 2.6, aggressive 8.4). A full-time founder could handle about 17 end to end. One real limit: intake and debrief calls must happen in US business hours. From Nepal (UTC+5:45), 9am–5pm US Eastern is about 7:45pm–3:45am local time. Batch calls to US mornings (evening in Nepal) and cap it at 2 calls per night.

---

## 4. Watch COGS per customer (per month, USD)

LLM prices are Sonnet-class list prices ($3 in / $15 out per million tokens; [Anthropic pricing via search](https://www.finout.io/blog/anthropic-api-pricing)). Token counts are **my estimates**. Note that `backend/routers/scan.py` currently hardcodes `claude-opus-4-6`.

| Item | Normal month | Tax season (Jan–Apr, accounting) | Label |
|---|---|---|---|
| A2 helpdesk: 3,500 in + 700 out tokens per email | $0.021 per email × 12 | × 30 | Estimate |
| Monthly brief + evidence refresh: 15k in + 3k out | $0.09 | $0.09 | Estimate |
| LLM subtotal (× 1.3 for retries and evals) | **$0.44** | **$0.94** | Estimate |
| Same on an Opus-class model ($5/$25) | $0.73 | $1.56 | Estimate. Not material, but switch A2 to Sonnet or Haiku ($0.007/email) anyway |
| Infra (DB, storage, compute share) + email in/out | $1.00 | $1.00 | Estimate |
| Stripe card 2.9% + $0.30, Billing 0.7%, Stripe Tax 0.5% | $4.36 at $99 monthly; $3.41 at $990/yr | same | Evidence (Stripe list prices, [via search](https://flexprice.io/blog/stripe-pricing-breakdown-2026)); Tax is an assumption |
| **Cash COGS at $99 monthly** | **~$6.0** | **~$6.5** | |
| Founder review time (HIGH verdicts, brief QA, quarterly check-in) | 0.4 h | 0.7 h | Assumption |

| Tier | Price | Cash COGS | Cash gross margin | Loaded margin (founder time at $35/h) |
|---|---|---|---|---|
| $49 (Founding/Solo) monthly | $49.00 | $3.92 | **92%** | 56% |
| $99 Standard monthly | $99.00 | $5.97 | **94%** | 76% |
| $149 Plus monthly | $149.00 | $8.02 | **95%** | 83% |
| Blended list, 30% annual | $103.55 effective | $6.07 | **94%** | 77% |

**Read:** tokens are a rounding error. The real cost of Watch is **founder attention**: at $49, the human review eats nearly half the margin. That's the strongest argument against a lifetime $49 lock and for the $99 Standard default.
