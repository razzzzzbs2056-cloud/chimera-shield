# Australia-resident founder: selling to the US, privacy, support programs and insurance

> **Draft for discussion. Not legal advice. Review with a qualified lawyer in your jurisdiction.**

**As of:** 2026-09-26 · **Owner:** legal-ops agent · **Founder location:** Australia (confirmed 2026-09-26)
**Related:** `entity-options.md` (entity choice), `spam-act-cold-email.md` (outreach), `launch-checklist.md` (order of work), `compliance-roadmap.md`, `terms-outline.md`

**Evidence note.** On 2026-09-26 the proxy blocked ato.gov.au, asic.gov.au, acma.gov.au, oaic.gov.au and business.gov.au. Facts come from **search-result summaries** of the linked pages (accessed 2026-09-26) and are marked **(S)**. Items marked **UNVERIFIED** are ones I couldn't confirm at all. **FLAG** means an accountant or lawyer must confirm. Currency: A$ unless shown as US$. The planning rate is US$1 ≈ A$1.53 (from company-context).

---

## 1. Selling to US customers from Australia

### 1.1 US sales tax
- **Economic nexus** depends on where the **customer** is, not the seller. A foreign seller that crosses a state's threshold must register and collect. The common threshold is **US$100,000 of sales into the state in 12 months**, and some states also count **200 transactions**. States are dropping the transaction count; for example, **Illinois removed it from 1 Jan 2026** (S: [Stripe nexus guide](https://stripe.com/resources/more/sales-tax-nexus-laws); [TaxCloud 2026 chart](https://taxcloud.com/blog/sales-tax-nexus-by-state/)).
- **Our scale:** the 90-day plan is 3–10 packs at US$495–1,195 plus some Watch subscriptions, which is **far below US$100k in any one state**. The 200-transaction test could only matter for monthly Watch billing in a state that still uses it. Even then, 200 charges a year in one state is far from our plan. **We are unlikely to have nexus in 2026–27.**
- **Taxability differs by product:** the WISP & Evidence Pack is a professional service, which most states don't tax. Watch is SaaS, which a minority of states tax (e.g. Texas, New York, Washington, Pennsylvania). **FLAG:** have a US sales-tax adviser confirm the list when revenue in any state passes about US$50k.
- **Action now:** turn on **Stripe Tax monitoring** (threshold tracking) without registering anywhere. Revisit at 100 customers (`compliance-roadmap.md`).

### 1.2 US income tax and Form W-8BEN-E
- An Australian company (or sole trader) that performs services **entirely outside the US** earns **foreign-source income**, which is generally not subject to US withholding. Under the US–Australia treaty, business profits are taxed in the US only if we have a **US permanent establishment** (no US office and no dependent agent in the US means none) (S: [Andrew Mitchel, payments to foreign contractor entities](https://www.andrewmitchel.com/blog/2014_09_payments-to-foreign-contractor-entities-form-w-8ben-e/); [IRS treaty technical explanation](https://www.irs.gov/pub/irs-trty/austtech.pdf)).
- **US customers may ask for a W-9.** Don't sign one. We aren't a US person. Instead:
  - **Pty Ltd:** give them **Form W-8BEN-E** ([IRS About Form W-8BEN-E](https://www.irs.gov/forms-pubs/about-form-w-8-ben-e)). For payments for services performed outside the US, practitioners say only a few parts are needed: Part I, lines 1–4, 6–7, possibly 9b, and the final certification part. The part number varies by form revision. **FLAG:** confirm the current revision and lines with the accountant, and keep one filled-in template on file (S: [King & Wood Mallesons guide](https://www.mallesons.com/au/en/insights/latest-thinking/what-is-a-w-8ben-e-form-and-how-do-i-fill-it-out-guidance-for-australian-entities.html)).
  - **Sole trader:** **Form W-8BEN** (individual).
  - A form is generally valid until the end of the third calendar year after it's signed (S).
- **Don't create a US PE by accident:** no US office, no US employee or agent who habitually signs contracts. **FLAG:** check before hiring any US-based salesperson or partner who signs deals for us.

### 1.3 Stripe Australia, currencies and payouts
- **Stripe is fully available to Australian businesses** (sole traders and companies). It needs an ABN (or ACN) and an Australian bank account ([Stripe global availability](https://stripe.com/global)).
- **Pricing (S, check at signup):** domestic cards about 1.7% + A$0.30 (reported to drop to **1.65% from 1 Oct 2026**); **international cards 3.5% + A$0.30** (reported to fall to 2.8% from 1 Apr 2027), plus **about 2% if currency conversion happens** ([Wise summary](https://wise.com/au/blog/stripe-fees); [Stripe AU pricing](https://stripe.com/au/pricing)). **US customers pay with US cards, so budget ~3.5% (plus 2% if converted).** Finance's 2.9% + US$0.30 assumption is too low. Tell finance-modeler.
- **Charge in USD** (the price is quoted in USD; US buyers expect it). Stripe converts to AUD for payout unless you have a **USD settlement account**. Stripe says **USD payouts for Australian accounts are available to only a "limited number" of businesses** (S: [Stripe support: USD/NZD payouts for Australia](https://support.stripe.com/questions/receiving-usd-nzd-payouts-for-australia-users); [multi-currency settlement docs](https://docs.stripe.com/payouts/multi-currency-settlement)). Ask Stripe after activation. Otherwise accept AUD payouts at Stripe's conversion rate.
- **Alternatives for USD invoices paid by bank transfer:** a multi-currency business account with US ACH receiving details (e.g. Wise Business or Airwallex; **FLAG:** check fees and eligibility). Some US firms prefer paying invoices by ACH, which is cheaper than card fees.
- **Watch subscriptions:** use Stripe Billing in USD. Our ToS must say prices are in USD.

### 1.4 Invoices
- **Pty Ltd details:** the invoice shows `ChimeraShield Pty Ltd`, the **ABN**, the address, the date, a description, and the amount in **USD**.
- **If registered for GST:** services to a **non-resident who is not in Australia** are generally **GST-free exports** (GST Act s 38-190, item 2). Show GST as **0% (GST-free export)**. A **tax invoice** is required only for taxable supplies; an ordinary invoice is fine for GST-free ones (S: [ATO exports and GST](https://www.ato.gov.au/businesses-and-organisations/international-tax-for-business/australians-doing-business-overseas/exports-and-gst)). **FLAG:** the ATO replaced its main ruling on services to non-residents in **July 2025** (now **GSTR 2025/2** and related rules, S: [ATO GSTR 2025/2](https://www.ato.gov.au/law/view/document?DocID=GST/GSTR20252/NAT/ATO/00001&PiT=99991231235958)). The accountant should confirm the item-2 conditions (e.g. whether the service is "provided to" someone in Australia) against the new ruling.
- **Australian customers** (if the market agent picks them): **10% GST applies** once we're registered. Invoices over A$82.50 (GST-inclusive) to GST-registered buyers must be **tax invoices** (**FLAG:** confirm the threshold).
- **Records:** keep them for **5 years** (ATO standard record-keeping period; **FLAG:** confirm for companies).

### 1.5 Time zones (practical)
Sydney and Melbourne are on **AEDT (UTC+11) from 4 Oct 2026**. US Eastern is UTC−4 until 1 Nov, then UTC−5. **10:00 ET is 01:00–02:00 the next day in Sydney.** The playbook's "Tue/Thu 10–12 prospect time" call blocks don't work. Suggested blocks: **US afternoons, 3–6 pm ET, which is 6–10 am AEDT the next day** (and 12–3 pm PT). Tell head-of-sales.

---

## 2. Australian Privacy Act 1988, the NDB scheme and the small-business exemption

### 2.1 Does the Privacy Act bind us?
- The Australian Privacy Principles (APPs) apply to "APP entities". A business with **annual turnover of A$3M or less is generally exempt** (s 6D), **unless** it (among other things) provides a **health service** and holds health information, **trades in personal information**, is a **contracted service provider to the Commonwealth**, is a credit reporting body, is a TFN recipient, or **opts in** (s 6EA) (S: [OAIC via ComplianceKit](https://compliancekit.co/blog/oaic-small-business-exemption-removed); [Artificer Legal](https://artificer.legal/changes-to-small-business-privacy-obligations)).
- **Our position (my reading, FLAG):** we're under A$3M, we don't trade in personal information, and we don't provide a health service, so we're **probably exempt today**. Two points need checking:
  1. **Pasted emails** in the phishing analyzer and intake notes contain personal information about third parties. This doesn't create coverage by itself, but it is exactly what the NDB scheme protects.
  2. **Australian customers:** if we sell to Australian accounting firms that became AML/CTF reporting entities on **1 July 2026** (the "Tranche 2" AML reforms, which reportedly bring those businesses under the Privacy Act, S: [HWL Ebsworth](https://hwlebsworth.com.au/small-businesses-big-change-privacy-obligations-under-tranche-2-of-the-aml-ctf-reforms/)), those customers will expect us to meet APP-level standards by contract. This is also a possible **selling point** for the market agent. **FLAG:** confirm the scope of Tranche 2.
- **Status of the exemption in 2026:** it has **not been removed**. The Government agreed "in principle" to remove it (Privacy Act Review response, 2023). The **Exposure Draft Privacy Amendment (Personal Data Protection) Bill 2026** (released **31 Aug 2026**; consultation closed **18 Sep 2026**) reportedly **does not remove** it (S: [Lexology, Tranche 2 arrives](https://www.lexology.com/library/detail.aspx?g=8aca0f2c-6ce9-4a6c-954e-3228c2d96eef); [Ashurst Perkins Coie](https://www.ashurstperkinscoie.com/en/insights/australias-2026-privacy-reforms-a-first-look-at-pivotal-new-changes/)). **Watch for a later tranche.**
- **Already in force regardless of size:** the **statutory tort for serious invasions of privacy** (Privacy and Other Legislation Amendment Act 2024, reportedly in force from **10 June 2025**; **FLAG:** confirm the date and scope). Mishandling someone's pasted email could in theory be actionable.
- **Extraterritorial reach:** the Privacy Act covers an Australian company's handling of information about **overseas** people (e.g. US staff in pasted emails) once the company is an APP entity. **US state breach-notification laws** can also apply to data about their residents, whatever the size of the business (**FLAG**, `compliance-roadmap.md`).

### 2.2 Recommendation
- **Operate to the APPs now** even if exempt: an APP-style privacy policy (`terms-outline.md` Part B), APP 11 security, collection limits, and 30-day deletion of pasted emails. Customers and insurers will ask, and the exemption may go.
- **Formally opting in (s 6EA) is a decision for the founder and lawyer.** The upside is a trust signal and a clear framework. The downside is regulator exposure and penalties (up to the greater of A$50M, 3× the benefit or 30% of turnover for serious breaches by bodies corporate, S). **My view:** don't opt in yet. Revisit with the first Australian customer or at 10 customers.

### 2.3 Notifiable Data Breaches (NDB) scheme
- Applies to APP entities (and TFN recipients). An **eligible data breach** is unauthorised access, disclosure or loss that is **likely to result in serious harm**, where remedial action hasn't prevented that risk. The entity must **assess a suspected breach within 30 days** and then **notify the OAIC and affected individuals as soon as practicable** (S: [OAIC, NDB scheme, Part 4](https://www.oaic.gov.au/privacy/notifiable-data-breaches/preventing-preparing-for-and-responding-to-data-breaches/data-breach-preparation-and-response/part-4-notifiable-data-breach-ndb-scheme)).
- **Even if exempt**, build the incident plan to NDB standard: the DPA already promises customers **notice within 72 hours** (`terms-outline.md` C6), and US tax-preparer customers have their own FTC 30-day duty.
- **Cyber Security Act 2024 ransomware-payment reporting** applies to businesses with turnover **above A$3M** (S; **FLAG**), so it's not us yet.

---

## 3. Australian government and ecosystem support

| Program | What | Fit for us now | Status (checked 2026-09-26) |
|---|---|---|---|
| **R&D Tax Incentive (RDTI)**, [business.gov.au overview](https://business.gov.au/grants-and-programs/research-and-development-tax-incentive/overview-of-rd-tax-incentive); [ATO offset rates](https://www.ato.gov.au/businesses-and-organisations/income-deductions-and-concessions/incentives-and-concessions/research-and-development-tax-incentive/r-d-tax-incentive-rates-and-entitlements/rates-of-r-d-tax-incentive-offset) | **Refundable offset** = company tax rate **+ 18.5%** (so **43.5%** for a 25% base-rate entity) if aggregated turnover is **under A$20M**. **Companies only** (sole traders can't claim). Minimum **A$20,000** of eligible spending a year (unless through a registered Research Service Provider). Register activities with AusIndustry **within 10 months after the income year ends**. | **Low for FY2026–27.** Our spend is well below A$20k, and a concierge WISP service isn't "core R&D" (which needs experiments with an unknown outcome). Some future work (e.g. LLM phishing-analysis accuracy experiments) might qualify. **Keep timesheets and experiment notes from now** so later claims are possible. | S. **2026 Budget** proposed lifting the minimum to **A$50k**, the refundability ceiling to **A$50M**, and a ~48% core rate, **from 1 July 2028** (S: [SmartCompany](https://www.smartcompany.com.au/federal-budget-2026/budget-2026-massive-rd-tax-incentive-changes-benefit-startups/); [Startup Daily](https://www.startupdaily.net/topic/politics-news-analysis/budget-2026-rd-tax-incentive-startups/)). **Not law yet. FLAG.** |
| **Export Market Development Grants (EMDG), Tier 1**, [Austrade Tier 1](https://www.austrade.gov.au/en/how-we-can-help-you/grants/export-market-development-grants/check-eligibility/criteria/tier-1) | Reimburses part of export marketing spend for new exporters: **A$20k–30k a year** for 2025–26 and 2026–27. Requires export training or the Export Readiness Test first. | **Medium.** We are a services exporter to the US. But the Round 4 funding was allocated on demand and may be closed. | S. **UNVERIFIED** whether any 2026–27 funding is still open. Email EMDG.help@austrade.gov.au. |
| **Industry Growth Program** (Early-Stage Commercialisation A$50k–250k, matched), [business.gov.au](https://business.gov.au/grants-and-programs/industry-growth-program) | Grants for SME commercialisation. Requires Advisory Service first. | Would fit later. | S: reportedly **paused to new applications since May 2026**. **UNVERIFIED** when it reopens. |
| **Victoria: LaunchVic → Innovation Victoria** | LaunchVic's grants went to Invest Victoria and its equity to Breakthrough Victoria. The new **Innovation Victoria** starts in H2 2026. Existing grants continue; future rounds are TBD. ([LaunchVic: Innovation Victoria](https://launchvic.org/innovation-victoria/); [Startup Daily](https://www.startupdaily.net/topic/other-tech/innovation-victoria-launchvic-breakthrough-victoria/)) | Only if the founder is in Victoria. Most LaunchVic grants went to programs and investors, not directly to founders. | S. **"Launch Victoria" as a named grant: UNVERIFIED.** No direct founder grant is currently confirmed. |
| **NSW: MVP Ventures** (Investment NSW), [Round 3 page](https://www.nsw.gov.au/grants-and-funding/mvp-ventures-2025-2026-round-3) | **A$20k–75k** matched grants for NSW startups to take a product to market (TRL 3–9). Stream 2 (under-represented founders, regional) up to A$75k at a 25% co-contribution. | **Medium, if the founder is in NSW** and has an ABN/company. | S. Round 3 ran 9 Mar–10 Apr 2026 (**closed**). **UNVERIFIED** whether a later round is scheduled. |
| **"Jobs for Tomorrow"** | Not found | n/a | **UNVERIFIED: I could not find a current program by this name.** Tell me the state or source and I'll check. |
| **Other states** (Queensland: Advance Queensland; SA, WA, Tasmania, ACT programs) | Various | Depends on the founder's state | **Not researched.** Tell me the state. |
| **AustCyber (now part of Stone & Chalk)**, [Stone & Chalk Cyber](https://www.stoneandchalk.com.au/cyber-security) | AustCyber became a wholly owned subsidiary of Stone & Chalk (merger announced 2021, fully integrated since). It now runs as Stone & Chalk cyber: **Cyber Growth Scholarship** (12 months of desks and support) and the **AWSN x Stone & Chalk scholarship** for female and First Nations cyber founders ([AWSN](https://www.awsn.org.au/initiatives/women-in-leadership/founder-bootcamp/stone-chalk-program/)). The old AustCyber Projects Fund has ended. | **Medium:** network, credibility, and introductions to cyber buyers and investors. Not cash. | S. **UNVERIFIED** whether 2026–27 intakes are open. |
| **Startmate accelerator**, [investment terms](https://www.startmate.com/writing/startmate-accelerator-investment-terms-101) | **A$120k** on a SAFE at a **A$1.5M post-money cap** for first-time raisers. For ANZ founders; at least one co-founder full-time. | Good fit **if** the founder wants to raise and validation succeeds. **An Australian Pty Ltd is the normal entity.** | S. **FLAG:** confirm the current cohort dates and terms. |

**Also worth one look:** the [business.gov.au grants finder](https://business.gov.au/grants-and-programs), which is maintained by the federal government and filters by state and industry.

---

## 4. Insurance in Australia

**Why:** a security advisor selling written plans to regulated US firms is exactly the business PI claims come from ("your plan missed X, and we were breached"). The playbook gate G7 requires cover **before the first paid delivery**.

| Cover | What it pays for | Typical cost (**estimates**; S, for general IT and consultants, not security firms) | Notes for us |
|---|---|---|---|
| **Professional indemnity (PI) / Tech E&O** | Claims that our advice, deliverables or software were wrong or negligent | IT consultants and software developers: about **A$800–2,500 a year for a A$1M limit** (S: [BizCover](https://www.bizcover.com.au/it-professional-professional-indemnity-cost/); [Upcover](https://www.upcover.com/blog/professional-indemnity-insurance-cost)) | **The critical point: US/Canada jurisdiction.** Many Australian PI policies **exclude claims brought in the US or Canada** or add a large loading. **Our customers are American, so we need worldwide jurisdiction including USA/Canada.** Expect a much higher premium than the headline ranges. **My estimate, UNVERIFIED: A$2,500–6,000 a year** for A$1–2M with US jurisdiction and a cyber-security services occupation. Get quotes. |
| **Cyber liability** (first and third party) | A breach of *our* systems exposing customer findings or pasted emails: response costs, notification, third-party claims | Small businesses typically **A$900–2,100 a year** (S: [Upcover](https://www.upcover.com/blog/how-much-does-cyber-insurance-cost)) | Security vendors are rated higher. Often **bundled with Tech PI** in one "tech" policy. Check it covers US notification costs. |
| **Public and products liability** | Physical injury or property damage | Often **A$400–1,000 a year** (**estimate**) | Cheap; sometimes asked for in contracts. Lower priority for a remote business. |
| **Management liability / D&O** | Claims against directors | **Estimate** A$1,000+ a year | **Not needed until we raise** money or have staff. |

**Actions:**
1. Use a **broker who places tech PI with US exposure**. Online quote tools often exclude US/Canada by default. Ask for 2–3 quotes.
2. Read the exclusions (`launch-checklist.md` 7.5): US/Canada jurisdiction, contractual liability, "intentional acts / unauthorized access", and fines and penalties.
3. **Match limits to the contract caps.** The engagement letter caps liability at the fee (`terms-outline.md` E3.11). US courts may not enforce it in full, which is why the insurance matters.
4. **Update the finance budget:** it assumed ~US$3k a year. With US jurisdiction, **A$3,500–8,000 a year combined (≈ US$2,300–5,200) is my rough estimate**, and many insurers want it paid upfront or in monthly instalments. **UNVERIFIED; quotes decide.**

---

## 5. Contract updates caused by the move to Australia (for `terms-outline.md`)

- **A1/E3.1 Parties:** "ChimeraShield Pty Ltd (ABN `[ABN]`), a company registered in `[STATE]`, Australia."
- **A15/E3.14 Governing law:** options are the founder's Australian state (the simplest for us) or a US state (easier for US buyers to accept). **FLAG:** the lawyer should advise. A common compromise is Australian law with a clause that doesn't force US customers to litigate in Australia for small claims. Enforcing an Australian judgment in the US, or the reverse, is slow.
- **B/C Privacy and DPA:** disclose that data is **accessed from Australia**, name hosting regions, and add APP-style wording (§2.2).
- **Prices in USD, GST-free export** (for US customers) wording in the billing section.
- **Australian Consumer Law** guarantees can apply to services under A$100,000 even for business customers (**FLAG**, S not checked). The lawyer should check the disclaimer (A8) and liability cap (A9) against the ACL for **Australian** customers.

## Needs a lawyer or accountant
| Item | Who |
|---|---|
| GST-free treatment under GSTR 2025/2, and whether to register for GST voluntarily | Australian accountant |
| W-8BEN-E completion and US PE check | Accountant with US–AU experience |
| Privacy Act opt-in decision; statutory tort exposure; ACL for Australian customers | Australian privacy and commercial lawyer |
| Governing law and dispute clause for US customers | Commercial lawyer (AU, ideally with US experience) |
| PI with US/Canada jurisdiction; cyber | Insurance broker |
| R&DTI eligibility of future product work | R&D tax adviser (later) |
