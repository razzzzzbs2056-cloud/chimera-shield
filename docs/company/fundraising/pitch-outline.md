# Pitch Outline (10 slides) + the Traction Slide We Need by 15 Dec 2026

**Owner:** fundraising-advisor · **Date:** 2026-09-24 · **Status:** draft for advisors and accelerator applications, **not for investor meetings yet** (see `verdict.md`)

**Rules for this deck**
- Pre-traction and says so on slide 1 and slide 9. No invented customers, logos, quotes or certifications.
- Every number is labeled **Fact** (sourced), **Assumption**, or **Projection** (from `finance/model-24mo.csv`). Keep the labels on the slides in small type.
- Don't use the old `01-problem-statement.md` stats ("43% of attacks target SMBs", "60% close within 6 months", "$50k–$500k enterprise tools"). No current primary source was found (`market/first-market-selection.md` §4). Don't use "the only AI security for SMBs" either; it's false (`competitors/smb-landscape-2026.md`).
- Placeholders stay visible: `[FOUNDER_NAME]`, `[DOMAIN]`.

---

## Slide 1: Title
**ChimeraShield: security evidence small tax firms can actually sign.**

- The plain-English security advisor for 5–50 person professional firms with no IT staff.
- First market: US accounting, CPA and tax-prep firms.
- Stage: pre-revenue, pre-launch. First sales window: 15 Oct – 15 Dec 2026.
- `[FOUNDER_NAME]`, Founder · `hello@[DOMAIN]`

**Speaker notes:** "I'll be upfront: we have no customers yet. What I'm showing you is a sharp wedge, a dated buying trigger, and a plan that's default-alive on about a thousand dollars. I'm here for [feedback / an intro / a place in the batch], and I'll tell you exactly what numbers would make this worth investing in." Say the stage in the first 30 seconds; investors respect it and it disarms the obvious question.

---

## Slide 2: Problem
**Every paid tax preparer signs a security promise each year that most small firms can't back up.**

- At PTIN renewal, preparers attest on **Form W-12 (line 11)** that they know they must create and maintain a **written information security plan (WISP)**. (Fact: [IRS W-12](https://www.irs.gov/pub/irs-pdf/fw12.pdf))
- The **FTC Safeguards Rule** treats tax preparers and CPA firms as financial institutions **at any size**: Qualified Individual, MFA, encryption, training, monitoring; FTC notice within 30 days for breaches of 500+ consumers since May 2024. (Fact: [FTC](https://www.ftc.gov/business-guidance/resources/ftc-safeguards-rule-what-your-business-needs-know))
- Today's choices: a free IRS template or a $29–$999 generic template the owner must fill in alone, **or** managed IT priced per user (e.g. $129/user/mo + $500 setup). (Fact, vendor pages via search: `finance/pricing.md` §2a)
- **Hypothesis, not yet validated:** most 5–15 person firms downloaded a template and never finished it.

**Speaker notes:** Keep it about the owner's Tuesday afternoon, not fear. "The owner-partner has to tick this box every year. They have no IT person. They have a template they haven't opened since last October." Say explicitly that the "never finished it" line is what our first 10 interviews test. Don't quote FTC penalty figures as a threat; enforcement against small firms looks rare, and a sharp investor will know it.

---

## Slide 3: Why now
**The rule is enforceable, the attacks are aimed at tax firms, and insurers want proof.**

- Safeguards Rule enforceable since June 2023; breach-notice requirement since May 2024. (Fact)
- The IRS logged nearly **300 tax-practice data breaches in H1 2025**. (Fact, secondary: [Carry, 2025](https://carry.com/news/irs-wraps-2025-security-summit-tax-identity-theft))
- Microsoft observed an **IRS-themed phishing wave hitting ~29,000 users at 10,000 orgs in Feb 2026**, aimed at accountants and tax preparers. (Fact, secondary: [ERP Today, 2026](https://erp.today/tax-season-scams-2026-irs-impersonation-ai-fraud-businesses/); verify against Microsoft's primary post)
- Ransomware appeared in **88% of SMB breaches** vs 39% at large enterprises. (Fact: [Verizon DBIR 2025 SMB snapshot](https://www.verizon.com/business/resources/infographics/2025-dbir-smb-snapshot.pdf))
- LLMs make a **firm-specific** plan and evidence report cheap to draft; a human still reviews it. That's what makes a $495–$795 done-with-you price possible.

**Speaker notes:** The honest "why now" is the combination of a live rule plus cheap LLM drafting, not "AI attacks are new". Keep secondary-source figures labeled; verify the top ones against primary sources before any external send (`first-market-selection.md` warns fetch was blocked).

---

## Slide 4: Solution
**A firm-specific WISP, an evidence page, and the 5 fixes to do first, in a week.**

- **Free Readiness Check:** 12 questions + a passive check of the firm's own email domain → "3 gaps to close before you sign your W-12".
- **WISP & Evidence Pack** (done-with-you, $495 founding / $795–$1,195 list): 60-minute intake → (a) WISP mapped to IRS Pub 5708 and 16 CFR 314.4; (b) one-page Evidence Report where every control is **Verified**, **Owner-stated** or **Gap**; (c) Fix-First plan, top 5 gaps in plain English. Delivered in ≤7 business days.
- **Watch** ($49–$149/mo per firm): monthly evidence refresh, compliance calendar, and an "Is this safe?" forwarding helpdesk for staff during tax season. A human reviews every high-risk verdict.
- What we never do: promise compliance, act as the Qualified Individual, touch client taxpayer data, or run intrusive scans.

**Speaker notes:** Demo idea (once built): show the Evidence Report for a fictional firm on a company-owned demo domain. The differentiator is the **Verified / Owner-stated / Gap** labeling: a template can't verify anything. Be explicit that v0 is concierge: "I deliver the first 10 by hand to learn what to automate." Current code is a prototype phishing checker that isn't deployable yet (`engineering/codebase-audit.md`); don't imply a finished product.

---

## Slide 5: Market (bottom-up)
**~15,000 reachable US tax and accounting firms; dental is the second, larger market on the same engine.**

| | Accounting / tax (first) | Dental (second) |
|---|---|---|
| ICP firms (5–49 staff) | ≈24,900 | ≈79,700 |
| Reachable (60%, assumption) | ≈14,960 | ≈47,800 |
| SAM at $49 / $99 / $149 per month | $8.8M / $17.8M / $26.7M | $28.1M / $56.8M / $85.5M |

- Counts: CPA Trendlines 2024 (Census-derived), NAICS 541213 (2020, **stale**), Census CBP 2023. Size-band shares and reach % are **assumptions** (`first-market-selection.md` §3).
- 3-year SOM (assumption): 1–2% of reachable accounting ICP = 150–300 firms = **$178k–$355k ARR** at $99.
- Expansion (not sized, not validated): law firms (ABA duties), small medical, and an MSP channel; ~870k individual PTIN holders on a cheaper tier.

**Speaker notes:** Say the quiet part: "Accounting alone is a great small business, not a venture market. The venture case depends on the same evidence engine carrying to dental and other regulated verticals, and that's untested." That honesty buys credibility for everything else. Don't show a top-down "SMB cybersecurity is $X billion" number.

---

## Slide 6: Competition
**Well-funded platforms protect SMBs through MSPs. Nobody explains security to the owner who has no MSP.**

| | Needs MSP / IT operator | Owner-facing plan | Compliance evidence (WISP) | Price for 15 staff |
|---|---|---|---|---|
| Guardz ($84M raised) | Yes (MSP-first) | No | No | Not public |
| Coro (~$280M raised) | Mostly | No | No | ~$143/mo (3P) |
| Huntress | Mostly MSP | No | No | ~$450+/mo min (3P) |
| Microsoft Business Premium | IT operator | No | No | $330/mo (often already paid) |
| WISP templates / IRS Pub 5708 | No | No | Generic, unverified | $0–$999 |
| Tax-firm MSPs (e.g. Verito) | They *are* the MSP | Partial | Bundled | ~$645/mo + $500 setup (5 users) |
| **ChimeraShield** | **No** | **Yes** | **Firm-specific, evidence-labeled** | **$495–$1,195 once + $49–$149/mo** |

Sources: `competitors/smb-landscape-2026.md`, `finance/pricing.md` (3P = third-party estimate).

**Speaker notes:** Lead with the admission: "AI-native SMB security at SMB prices already exists: Guardz, Coro. We are not competing on detection." Then: "We integrate with what they already pay for (M365) and translate it into evidence an owner can sign." The main risk (Guardz or Microsoft adding an owner tier) is on slide 10 and in the Q&A; don't hide it. WISP-template vendors and tax-focused MSPs have **not** been fully torn down yet (`prd` §12.4); say so if asked.

---

## Slide 7: Business model and unit economics (projections)
**Paid up front, high margin, seasonal. Founder hours are the constraint, not cash.**

- Pack: $495 founding → $795 / $1,195 list. Blended list ~$875, **gross profit ~$843** before founder time. (Projection)
- Watch: blended ARPA **$103.55/mo**; cash COGS ~$6/mo; **~94% cash gross margin**, ~77% with founder time costed at $35/h. (Estimate)
- Base-case LTV per pack buyer **~$2,173**; loaded CAC via LinkedIn + cold email **~$347** → **6.3× LTV/CAC**. (Projection; all funnel inputs are assumptions)
- Peak cash need **~$1.1k** (no founder salary); default-alive in all three scenarios on a no-salary basis. (Projection)
- Base case: ~27 Watch subscribers cover costs + a $2k/mo founder salary around **month 15 (Dec 2027)**. M24 Watch ARR **$51.7k** base / $12.5k conservative / $142.5k aggressive. (Projection)

**Speaker notes:** Stress that these are model outputs with **zero** willingness-to-pay data behind them. Show the three scenarios, not just base. Point out the two things that break the model: packs that don't templatize (>6 h each after pack 3) and May churn after tax season. Investors will respect you naming them before they do.

---

## Slide 8: Go-to-market
**Sell into the PTIN renewal window; retain through tax season with annual prepay.**

- **Calendar:** sell 15 Oct – 15 Dec (PTIN window); no new accounting sales Jan – mid-Apr; sell again May – Sep; dental from Jan 2027 as a hedge (no-PHI intake).
- **Channel 1 (now):** LinkedIn + cold email to owners found through public IRS preparer and state CPA directories. Assumed funnel: 150 touches/mo → 8% reply → 6 calls → 25% close. (Assumption)
- **Channel 2 (2027):** partners: cyber-insurance brokers, bookkeepers, small IT shops, with a 15% first-year referral fee. (Assumption)
- **Channel 3 (slow):** content for "WISP for tax preparers", r/taxpros (check self-promotion rules).
- **Retention mechanics:** annual Watch prepay pushed Nov–Dec (covers the Jan–Apr blackout); Annual WISP Refresh included in Watch annual; helpdesk used most in tax season.

**Speaker notes:** The insight to land: "The regulation gives us a deadline to sell against every October, and tax season gives us a reason to be useful every February." Admit the cost: one founder can sell and deliver about 17 packs in the window full-time (`pricing.md` §3c), so year 1 is capped by founder hours.

---

## Slide 9A: Traction (honest, as of today)
**Where we are on 24 Sep 2026.**

- Customer interviews: **0** (plan: 10 by mid-Oct; 6 accounting, 4 dental)
- Paying customers: **0** · Revenue: **$0** · Pipeline: **empty**
- Built: prototype AI phishing analyzer (not deployable yet). Specs done: Readiness Check, Pack PRD with 15 testable acceptance criteria, pricing, 24-month model, legal checklist.
- Not yet done: entity, domain, bank, payments, insurance.

**Speaker notes:** Don't dress this up. The strongest thing you can say pre-traction is a specific, dated commitment: "By 15 December I will have X, and here's what I'll do if I don't." Then show slide 9B.

---

## Slide 9B: The traction slide we need by 15 Dec 2026
**Fill in with actuals on 15 Dec. If a number is missed, show it anyway with the reason.**

| Metric | Minimum (north star) | Target (base case) | Stretch | Actual on 15 Dec |
|---|---|---|---|---|
| Discovery interviews completed (accounting / dental) | 10 (6/4) | 15 | 20 | `[ ]` |
| Outreach touches sent | 100 | 250 | 400 | `[ ]` |
| Qualified conversations (calls with an owner) | 15 | 30 | 45 | `[ ]` |
| Free Readiness Checks completed | 20 | 40 | 80 | `[ ]` |
| **Paid WISP & Evidence Packs** | **3** | **5** | **8+** | `[ ]` |
| Packs sold at list price ($795+), not founding | 0 | 1 | 3 | `[ ]` |
| **Watch subscribers** (and % on annual prepay) | 1 | 2–3 (≥50% annual) | 5 | `[ ]` |
| Cash collected (net of Stripe) | ~$1.4k | ~$2.3k | ~$4k+ | `[ ]` |
| Founder hours per pack (pack 1 → latest) | logged | ≤6 h by pack 3 | ≤4 h | `[ ]` |
| Owner "understanding test" pass rate (PRD AC12) | 100% | 100% | 100% | `[ ]` |
| Buyers who completed ≥1 Fix-First item within 14 days | 2 of 3 | 60% | 80% | `[ ]` |
| Price anchors heard ("what did your last WISP cost you?") | 6 | 10 | 15 | `[ ]` |
| Customer quotes usable **with written permission** | 1 | 2 | 3 | `[ ]` |
| Referrals / intros from customers or partners | 0 | 1 | 3 | `[ ]` |

**What 9B must prove, in one line each:**
1. Owners pay **hundreds of dollars** for something they could get as a $29 template (packs sold, price anchors).
2. The pack leads to a **relationship**, not a one-off (Watch attach, annual share).
3. Delivery **gets cheaper** with each pack (hours trend).
4. Customers **act on** the plan (Fix-First completion), which is the seed of a retention story.

**Speaker notes (for use in Jan–Feb 2027):** Lead with the one metric that surprised you, good or bad. Then the full table. Then the next checkpoint: churn through May 2027.

---

## Slide 10: Team, risks and the ask
**Solo founder; honest risks; a small, specific ask.**

- **Team:** `[FOUNDER_NAME]`: `[TODO: verifiable background: security, compliance, accounting or software experience, with links]`. Location: `[TODO]`. Advisors: `[TODO: aim for 1 accounting-firm owner or practice-management operator, and 1 security practitioner]`.
- **Top risks we're watching:** (1) willingness to pay vs. $29 templates; (2) May churn after tax season; (3) Guardz or Microsoft adding an owner-facing tier; (4) services-heavy delivery; (5) founder structure (entity and, if applicable, Nepal outward-investment rules).
- **The ask (today):** not money. **Introductions** to 5 small tax/CPA firm owners and 1 cyber-insurance broker; **feedback** on the Evidence Report; one **advisor** from the accounting world.
- **The ask (if 15 Dec milestones hit):** `[TODO after 15 Dec: e.g. $25k–$75k angel SAFE for founder salary through tax season and the dental pilot]`. No amount before there's data.

**Speaker notes:** Solo founders get asked "who else?" every time. Have an answer: who you'd hire first (a part-time compliance writer or a dental-vertical seller), and which advisor covers your biggest blind spot. If you're Nepal-based, be ready to explain the timezone plan (US-morning calls in the Nepal evening, 2 per night max) and the legal path.

---

## Appendix slides (build only if asked)
- A1: Three-scenario model table (`finance/model-summary.md` §2)
- A2: Evidence Report sample for a fictional firm (company-owned demo domain)
- A3: Regulatory map: W-12 line 11, 16 CFR 314.4 elements, §314.6 small-firm exemptions (legal-ops must verify against the primary text first)
- A4: Data handling and scanning scope (passive only, written consent, no client data)
