# Entity options for an Australia-resident founder

> **Draft for discussion. Not legal advice. Review with a qualified lawyer in your jurisdiction.**

**As of:** 2026-09-26 · **Owner:** legal-ops agent · **Status:** rewritten for an **Australia-resident founder** (confirmed 2026-09-26). This replaces the 2026-09-24 version, which covered US and Nepal paths.
**Related:** `australia-founder.md` (US selling, GST, privacy, grants, insurance), `spam-act-cold-email.md`, `launch-checklist.md`

**Evidence note.** On 2026-09-26 the proxy blocked asic.gov.au, ato.gov.au and business.gov.au. Fees and rules below come from **search-result summaries** of the linked pages (accessed 2026-09-26) and are marked **(S)**. Delaware and IRS figures are carried over from the 2026-09-24 version, which cited official pages. **FLAG** = an accountant or lawyer must confirm. Currency is A$ unless marked US$. The planning rate is US$1 ≈ A$1.53.

---

## 0. The recommendation (short version)

**Register an Australian proprietary company (Pty Ltd) now. Sell to US customers from it. Flip to a Delaware parent only if and when a US lead investor requires it.**

Why:
1. **Limited liability.** We give security advice to regulated US firms. A sole trader's house and savings are exposed to any claim that exceeds the insurance.
2. **A Delaware company run by you from Australia is probably an Australian tax resident anyway** (§2). You'd pay for two tax systems and gain little until US investors want it.
3. **Australian funding paths want a Pty Ltd:** Startmate, most Australian angels (the ESIC tax incentives need an Australian-incorporated company), the R&D Tax Incentive, EMDG, and state grants.
4. **The flip is routine** and US-savvy Australian VCs (e.g. Blackbird) do it regularly (S: [Blackbird, "Flip Ups: Not As Scary As You Think"](https://www.blackbird.vc/blog/flip-ups-not-as-scary-as-you-think)).
5. **Cost and speed:** about **A$636 plus A$342 a year** to ASIC, and it can be done in 1–3 days, before cold sends start on 12 Oct.

**When the answer changes:** if a US investor or accelerator (e.g. Y Combinator) offers money **now** on the condition of a Delaware C-corp, form the Delaware company first, with cross-border tax advice (§2), rather than flipping later.

---

## 1. The four options compared

| | **(A) Sole trader + ABN** | **(B) Pty Ltd (recommended)** | **(C) Delaware C-corp via Stripe Atlas, owned and run from Australia** | **(D) Pty Ltd now, Delaware flip later** |
|---|---|---|---|---|
| **Set-up cost** | ABN: **free**. Business name "ChimeraShield": **A$47 for 1 yr / A$108 for 3 yrs** from 1 Jul 2026 (S: [ASIC business-name fees](https://www.asic.gov.au/for-business-and-companies/forms-and-fees/all-fees/schedules-of-business-names-fees); [Sleek](https://sleek.com/au/resources/business-name-registration/)) | ASIC registration **A$636** from 1 Jul 2026 (S: [ASIC fee indexation](https://www.asic.gov.au/for-business-and-companies/forms-and-fees/all-fees/fee-indexation); [AusBusinessRegister](https://ausbusinessregister.com.au/asic-fees-australia/)). ABN and TFN free. **Director ID** free (required before you're appointed; apply via ABRS with myID). Optional accountant or online provider set-up: A$0–500 (estimate). | Atlas **US$500** (≈A$765), which covers the Delaware filing, EIN, templates, 83(b) and a year of registered agent; then US$100/yr ([Stripe Atlas](https://stripe.com/atlas)). **Plus Australian advice** on residency (§2): **estimate A$1,000–3,000** for a written opinion. | As (B) now. **Flip later:** commonly quoted at **tens of thousands of dollars** in AU and US legal and tax fees (**estimate, FLAG**); usually paid around the round that needs it. |
| **Annual government and compliance cost** | None beyond the business-name renewal. Personal tax return with business schedule. | ASIC **annual review fee A$342** (from 1 Jul 2026, S), due within 2 months of the review date; late fees A$102/A$428 (S). Company tax return. Accountant **estimate A$1,500–4,000 a year** (company return, financial statements, ASIC). | Delaware franchise tax min **US$175** (authorized-shares method) or **US$400**, plus **US$50** annual report by **1 March** ([Delaware](https://corp.delaware.gov/frtax/)). **Form 1120 + Form 5472** (25%+ foreign-owned; **US$25,000 penalty** per missed 5472: [IRS i5472](https://www.irs.gov/instructions/i5472)). **Plus** an Australian company return if it's Australian-resident (§2), or CFC disclosures on your own return if not. US preparer **US$500–2,000** plus an AU accountant (estimate). **Realistically A$4,000–8,000 a year** (estimate). | (B) now; (C)'s costs after the flip. |
| **Time to form** | ABN online, often issued immediately and within ~28 days at worst (S). Business name: minutes. | Director ID (minutes with myID), then the ASIC registration, often **same day** online or through a provider. ABN and TFN the same day to a few days. | Atlas: incorporation in 1–3 days; EIN for a foreign founder by phone or fax, which can take 1–3 weeks ([IRS SS-4 instructions](https://www.irs.gov/instructions/iss4)). US bank onboarding for an AU resident: **FLAG**, check Mercury's eligibility first. | (B) now. |
| **Liability** | **Unlimited personal liability** | Limited (subject to directors' duties, personal guarantees, insolvent trading) | Limited | Limited |
| **Tax** | Personal marginal rates on profit. Simple. | **25% base-rate-entity company tax** (turnover under A$50M, mostly active income; **FLAG**). Money taken out as salary, director fees or dividends (franked). **Division 7A trap:** taking company cash as a "loan" or paying private costs can be taxed as a deemed dividend. Keep money separate. | US 21% federal tax (plus state tax if nexus) **and possibly** Australian 25–30% if Australian-resident, with foreign tax credits and treaty relief. **Complex. See §2.** | (B) now. The flip should use scrip-for-scrip rollover relief (**FLAG**, needs structuring). |
| **GST** | Register when **GST turnover reaches A$75k** (it includes GST-free exports, S: [ATO exports and GST](https://www.ato.gov.au/businesses-and-organisations/international-tax-for-business/australians-doing-business-overseas/exports-and-gst)); voluntary before that | Same | A US company with no Australian supplies generally doesn't register. But if it's managed in Australia, **FLAG**. | Same as (B) |
| **Selling to US firms** | Works: Stripe AU, W-8BEN. But it looks small, and PI is in your personal name. | Works: Stripe AU, W-8BEN-E, USD pricing. Services to US customers are generally **GST-free exports** (`australia-founder.md` §1). | Strongest "US vendor" signal; Stripe US; US governing law. | As (B) |
| **R&D Tax Incentive** | **Not eligible** (companies only) | **Eligible** (refundable 43.5% offset under A$20M turnover, S) once spending passes A$20k | **FLAG:** a foreign company that is an Australian tax resident may qualify as an R&D entity, but dual residency complicates it. Assume no without advice. | Eligible until the flip. **FLAG:** the structure after the flip affects eligibility. |
| **Fundraising fit** | **None.** You can't sell shares. | **Good in Australia:** Startmate (A$120k SAFE; S: [Startmate terms](https://www.startmate.com/writing/startmate-accelerator-investment-terms-101)), Australian angels (**ESIC** investor offsets need an Australian-incorporated company, **FLAG**), Blackbird, Square Peg, AirTree. **Weak for US-only funds**, which usually ask for a flip. | **Best for US VCs and YC.** Neutral to weaker for Australian angels (no ESIC). Australian VCs invest in Delaware parents routinely. | **Best of both** at the cost of a later flip. Blackbird and other Australian VCs have flipped portfolio companies (S: [Blackbird](https://www.blackbird.vc/blog/flip-ups-not-as-scary-as-you-think); [Standard Ledger](https://www.standardledger.co/article/the-delaware-flip-what-it-is-when-australian-founders-should-think-about-it)). |
| **Switching later** | To a Pty Ltd: transfer the business assets, possibly with small-business CGT rollover (**FLAG**). Clients and contracts must be re-papered. | Flip (D) when needed | Hard to "unflip" | n/a |

---

## 2. Why a Delaware company run from Australia is probably an Australian tax resident

- **The test.** A company **not incorporated in Australia** is an Australian tax resident if it **carries on business in Australia** and **either** (i) its **central management and control (CMC)** is in Australia, **or** (ii) its voting power is controlled by Australian-resident shareholders (ITAA 1936 s 6(1)) (S: [ATO TR 2018/5](https://www.ato.gov.au/law/view/document?docid=TXR%2FTR20185%2FNAT%2FATO%2F00001); [PwC](https://www.pwc.com.au/tax/tax-alerts/residency-of-foreign-incorporated-companies.html)).
- **The ATO's view (TR 2018/5):** if CMC is exercised in Australia, the company is treated as **carrying on business in Australia**, and no trading needs to happen here. CMC is about **where high-level decisions are actually made**, not where board minutes say they were made (S). **PCG 2018/9** gives the ATO's compliance approach (S: [ATO PCG 2018/9](https://www.ato.gov.au/law/view/pdf?DocId=COG%2FPCG20189%2FNAT%2FATO%2F00001&filename=law%2Fview%2Fpdf%2Fcog%2Fpcg2018-009c6.pdf&PiT=99991231235958)).
- **Our facts:** the sole director and shareholder lives in Australia and makes every strategic decision here. **The Delaware company would very likely be an Australian tax resident**, and a US tax resident too because it's incorporated there. **Dual resident.**
- **Treaty tie-breaker.** Commentary says the US–Australia treaty leaves dual-resident companies to the tax authorities to agree case by case (S: [Asena Advisors, US–AU DTA Article 4](https://asenaadvisors.com/blog/us-au-dta-series-article-4/)), which gives **no certainty**. **FLAG, high:** a cross-border adviser must read Article 4 of the 1982 convention as amended ([IRS treaty page](https://www.irs.gov/businesses/international-businesses/australia-tax-treaty-documents)). Neither of us should rely on this summary.
- **If it isn't Australian-resident** (for example, real decisions are made in the US by US directors), it is a **controlled foreign company (CFC)** of the founder. The **US is a "listed country"**, and if the company passes the **active income test** (tainted income under 5% of gross turnover), there's usually **no attribution** to the founder. Services revenue from US customers is generally active (S: [ATO CFC active income test](https://www.ato.gov.au/forms-and-instructions/foreign-income-return-form-guide/chapter-1-attribution-of-the-current-year-profits-of-a-controlled-foreign-company-cfc/part-2-does-the-cfc-satisfy-the-active-income-test); [PwC](https://taxsummaries.pwc.com/australia/corporate/group-taxation)). Reporting obligations still apply. **FLAG.**
- **Practical result:** option C adds a second tax system and uncertain residency for **no gain in trust or payments at our stage**. Stripe Australia, USD pricing and a W-8BEN-E cover what US customers need (`australia-founder.md` §1). **Choose C only for investor reasons, and then with a written cross-border tax opinion before forming.**
- **Stripe Atlas itself** doesn't give tax advice and doesn't file Form 1120 or 5472 for you (S: [Stripe Atlas docs](https://docs.stripe.com/atlas)).

---

## 3. Recommended set-up for the Pty Ltd (option B)

| Decision | Recommendation | Why |
|---|---|---|
| Name | "ChimeraShield Pty Ltd", if the name screen (`launch-checklist.md` 1.1) is clear in **Australia (ASIC and IP Australia) and the US (USPTO)** | Registering a company name doesn't give trademark rights |
| Shareholders | The founder, 100%. **If there's a co-founder:** agree the split, **4-year vesting with a 1-year cliff**, and leaver terms in a shareholders' agreement **before** issuing shares | Vesting protects both founders, and investors expect it |
| Constitution | A simple company constitution with **share-class flexibility** (rather than only the replaceable rules) | Makes SAFEs, ESOP and a later flip easier. **FLAG:** the lawyer picks the template. |
| Director | The founder. **Director ID first.** | Required by law before appointment (**FLAG**, S) |
| Registered office | The accountant's or a provider's address rather than home | Keeps the home address off the public register. **FLAG:** director residential addresses may still be recorded with ASIC. Check suppression options. |
| IP | The founder signs an **IP assignment** to the company for all ChimeraShield code, docs, domain and brand created so far | Investors check this. A flip also needs clean IP. |
| Tax registrations | ABN and TFN at registration. **GST: register when GST turnover is likely to reach A$75k, or earlier if the accountant advises** (it lets you claim GST credits on Australian costs, but adds BAS lodgements) | Exports to US customers are GST-free either way |
| Bank | A business account at an Australian bank, plus a multi-currency USD account if useful (`australia-founder.md` §1.3) | Keep personal and company money separate (Division 7A) |
| Paying the founder | Nothing for now. Later, salary or director fees (PAYG withholding and **super** obligations) or franked dividends. **The accountant sets this up.** | Avoid Division 7A loans |

## 4. Needs an accountant or lawyer
1. **Confirm the Pty Ltd recommendation** against the founder's personal tax position (other income, whether an existing ABN exists), with an Australian accountant. **About 1 hour, before registering.**
2. **Before any Delaware entity** (option C, or the flip): a written **cross-border tax opinion** on CMC residency, the treaty, CFC, R&DTI and ESIC effects.
3. **Constitution and shareholders' agreement** (and co-founder vesting, if relevant): an Australian startup lawyer. Template packs are cheap. Have a lawyer review the one you pick.
4. **GST registration timing** and the **GSTR 2025/2** rules for services to non-residents: accountant.

## Sources
All links are inline, accessed 2026-09-26. Items marked (S) come from search-result summaries because the proxy blocked the government sites. Open them before relying on them.
