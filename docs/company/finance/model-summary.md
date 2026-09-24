# ChimeraShield 24-Month Model: Summary

**Owner:** finance-modeler (CFO) · **Date:** 2026-09-24 · **Currency:** USD · **Period:** M1 = Oct 2026 to M24 = Sep 2028
**Files:** `model-24mo.csv` (Block 1 = every assumption with its label; Block 2 = monthly rows for 3 scenarios) · `pricing.md` · `90-day-budget.md`

> This is planning support, not tax or accounting advice. Before any filing, entity or sales-tax decision, use a local accountant (a cross-border accountant if you're outside the US).

**How to open:** import `model-24mo.csv` into Google Sheets or Excel. The assumptions are the rows above the `# BLOCK 2` line. Filter Block 2 on the `scenario` column. Customer counts are fractional expected values. Cash is on a collection basis: annual prepay is counted when collected, and `watch_mrr` spreads it over the year.

---

## 1. The three numbers that matter

1. **27 Watch subscribers** at blended list price cover all running costs **plus a $2,000/mo founder salary**. The base case reaches that level at **month 15 (Dec 2027)** on subscriptions alone, and sooner if pack revenue is counted.
2. **About 5 packs by 15 Dec 2026** (base; conservative 2.6, aggressive 8.4). That meets the "3 paying customers" north star, and it's demand-bound, not capacity-bound. One founder could deliver ~17.
3. **$1,150 peak cash need** before founder pay (base; conservative $3,550). The company is default-alive on a shoestring **if the founder takes no salary**. Paying $2,000/mo from day one needs about **$12,900** of starting cash (base).

---

## 2. Scenario results

| Metric (USD) | Conservative | Base | Aggressive |
|---|---|---|---|
| Dental segment starts | M8 (May 2027) | **M4 (Jan 2027)** | M4 (Jan 2027) |
| Packs sold by 15 Dec 2026 | 2.6 | **4.9** | 8.4 |
| Packs sold, 24 months | 31 | **77** | 165 |
| Watch subscribers, M12 (Sep 2027) | 4.3 | **16.2** | 35.2 |
| Watch subscribers, M24 (Sep 2028) | 13.3 | **45.1** | 119.5 |
| Watch MRR, M12 | $201 | **$1,180** | $3,136 |
| Watch MRR, M24 (ARR) | $1,040 ($12.5k) | **$4,309 ($51.7k)** | $11,877 ($142.5k) |
| Cash collected, year 1 / year 2 | $7.8k / $28.4k | **$25.2k / $85.9k** | $52.3k / $208.1k |
| Pack share of year-1 cash | 82% | **75%** | 67% |
| Peak cumulative cash need (no founder pay) | −$3,546 | **−$1,148** | −$632 |
| Net cash positive every month from | M8 | **M6** | M2 |
| Net cash > $2,000 every month from | M23 | **M8** | M7 |
| Net cash > $5,000 every month from | never in 24 mo | **M20** | M8 |
| Cumulative cash at M24 (no founder pay) | +$18.7k | **+$90.1k** | +$231.8k |
| Peak founder delivery hours/month | 18 | **51** | 129 (over the ~96 h ceiling from Aug 2028; hire) |

**Seasonality built in** (accounting new-sales index): Oct 1.2 (×0.6 in Oct 2026 because S5 launches mid-month), Nov 1.5, Dec 0.9, Jan 0.05, Feb 0, Mar 0, Apr 0.2, May–Sep 0.5–0.8. Dental is flat (0.6–1.0). Accounting monthly Watch subscribers also get a **May churn spike** (+6 pts in the base case) when the tax season ends. The base-case net cash dips from $8.0k in Nov 2027 to $3.5k in Feb 2028; dental and Watch keep it positive.

---

## 3. Unit economics (base)

| Metric | Value | Note |
|---|---|---|
| Watch blended ARPA | **$103.55/mo** | List mix 10% Solo / 60% Standard / 30% Plus, 30% annual |
| Watch cash COGS | **$6.07/mo** | LLM $0.61 avg, infra + email $1.00, Stripe ~$4.46 |
| Watch cash gross margin | **94%** | 77% if founder review time is costed at $35/h |
| Pack gross profit (avg list $875) | **$843** | After Stripe, Stripe Tax and ~$2 LLM. Founder time is not deducted |
| Effective monthly churn (monthly + annual payers) | 5.0% / **3.5%** / 2.4% | cons / base / agg |
| Watch customer lifetime | 20 / **28** / 42 months | |
| **Watch LTV (cash contribution)** | $1,933 / **$2,768** / $4,076 | Aggressive is $3,509 if capped at 36 months |
| **LTV per acquired pack buyer** (pack + 45% Watch attach + refresh) | **$2,173** | Base |

### CAC by channel (per paying pack buyer, founder time at $35/h, all Assumption)

| Channel | Funnel assumption per month | Cash CAC | Loaded CAC | Founder h per customer | LTV / loaded CAC | Payback |
|---|---|---|---|---|---|---|
| **LinkedIn + cold email** (IRS/CPA directories) | 150 touches, 8% reply, 6 calls, 25% close → 1.5 | **$67** | **$347** | 8.0 | **6.3×** | Immediate: the pack's $843 gross profit covers it. Watch-only: 0.7 months (cash), 4.3 (loaded) |
| **Partners** (insurance brokers, bookkeepers, IT shops) | 6 h relationship time, 3 intros, 40% close → 1.2; 15% of first-year revenue as referral fee | **$198** | **$439** | 6.9 | **4.9×** | Immediate. Watch-only: 2.0 / 5.5 months |
| **Reddit / content / SEO** (r/taxpros, LinkedIn posts, "WISP for tax preparers") | 10 h writing → 0.5 close in year 1 | **$0** | **$752** | 21.5 | **2.9×** | Immediate. Watch-only: 0 / 9.4 months. Slow to build; check subreddit self-promotion rules |

**Read:** because the pack is paid up front, every channel pays back its CAC on day one. The scarce resource is **founder hours, not dollars**. LinkedIn/cold email is the best near-term channel. Partners are best in year 2. Content is a long-term compounding play and shouldn't be the Q4 2026 plan.

---

## 4. Break-even (USD, founder country unknown)

Running costs after launch: **$235/mo** for tools and infra (workspace, domain, hosting, email service, Sales Navigator, other tools) **+ $377/mo** for insurance, accountant and entity upkeep, **= $612/mo**. Contribution is $97.48 per blended Watch subscriber, or $45.08 at $49.

| Target | Monthly cost to cover | **Watch subs at blended list** | Subs if all at $49 | Or packs per month |
|---|---|---|---|---|
| (a) Tools + infra only | $235 | **3** | 6 | 0.3 |
| (a) All non-salary costs (incl. insurance, accountant, entity) | $612 | **7** | 14 | 0.7 |
| (b) + $2,000/mo founder salary | $2,612 | **27** | 58 | 3.1 |
| (c) + $5,000/mo founder salary | $5,612 | **58** | 125 | 6.7 |

The salary is gross, before any payroll tax, self-employment tax or local income tax (ask your accountant). Servicing 58 subscribers takes about 29 founder hours a month, which is feasible for one person.

**When the base case gets there on Watch alone:** 7 subs in M8 (May 2027); 27 subs in M15 (Dec 2027); 58 subs not within 24 months (45 at M24). Counting pack cash, the $2,000 level holds every month from M8 and the $5,000 level from M20.

---

## 5. Default-alive check

**Question:** at the modeled growth rate, does ChimeraShield reach profitability before the money runs out?

- **Starting cash is unknown.** Rather than guess it, the model reports the **peak cash need**: the lowest point of cumulative cash, which is the starting cash the founder has to put in.
- **With no founder salary: default alive in all three scenarios**, provided the founder funds $632 (aggressive), $1,148 (base) or $3,546 (conservative). Costs are tiny, and packs bring in cash within weeks.
- **With a $2,000/mo salary from M1:** base needs **$12,860**; aggressive needs $7,553; **conservative never recovers** (it ends −$29.3k at M24).
- **With a $2,000/mo salary from M13:** base and aggressive never dip below their pre-salary low. Conservative needs about **$6,200**.
- **Verdict:** default alive **only as a no-salary or low-salary side business until about month 8** (base). If the founder needs income before then, it must come from outside (a job, savings or a small raise). The conservative case is a lifestyle business, not a venture. If Dec 2026 ends with fewer than 3 packs, you're tracking conservative. Re-plan in January.

---

## 6. Risks

1. **No willingness-to-pay evidence.** 0 interviews, so every demand input is an assumption. The first 6 accounting interviews can move the base case more than any modeling can. Update `acct_pack_rate` and `watch_attach` after them.
2. **Revenue depends on services.** Packs are 67–82% of year-1 cash, and each one is 4.5–9.5 founder hours. If packs don't templatize (still above 6 h after pack 3), margins and capacity both fail. Log hours from pack 1.
3. **Seasonal cliff.** There are no accounting sales from Jan to mid-Apr. Missing the Oct–Dec 2026 window pushes first real revenue to May 2027 and roughly turns the base case into the conservative one. Dental from Jan 2027 is the hedge, and it needs a no-PHI intake design and a legal-ops review first.
4. **Churn after tax season.** Monthly accounting subscribers may cancel in May. Mitigations: annual prepay in Nov–Dec, and including the Annual WISP Refresh in Watch annual.
5. **Founder's own costs are uncertain.** Insurance (Tech E&O + cyber) is estimated at $3,000/yr, and real quotes may differ by 2–3×. Get quotes before the first paid pack. For a non-US founder, cross-border accounting and Form 5472 filing ($25,000 penalty if missed) raise the fixed costs.
6. **Payments risk for a non-US founder.** Stripe/bank approval is not guaranteed (legal docs note Mercury lists Nepal as prohibited). Without Stripe, fees and cash timing change.
7. **Competitive squeeze.** $29 templates below us, and Guardz/Microsoft could add an owner-facing tier. Watch churn is the metric to watch.
8. **Unverified sources.** Competitor and insurance numbers come from search snippets, not opened pages. Verify before external use.
