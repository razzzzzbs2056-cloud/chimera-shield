# Launch checklist: from zero to able to take money (Australia-resident founder)

> **Draft for discussion. Not legal advice. Review with a qualified lawyer in your jurisdiction.**

**As of:** 2026-09-26 · **Owner:** legal-ops agent · **Company status:** no entity, no domain, no email, pre-revenue. Founder lives in **Australia**; first customers are **US** tax and accounting firms (Australian firms possibly later).
**Path:** Australian **Pty Ltd** now; a Delaware flip only if a US investor requires it (`entity-options.md` §0). Details on US selling, GST, privacy, grants and insurance are in `australia-founder.md`. Outreach rules are in `spam-act-cold-email.md`.

**Status key:** `[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked on a lawyer, accountant or decision
**(S)** = from a search-result summary; the official page was blocked on 2026-09-26, so check before relying on it.

**Dates that drive this list:** cold sends start **12 Oct**, the Readiness Check goes live **15 Oct**, first paid pack late Oct (`sales/playbook.md` §2 and §5.3).

---

## Stage 0: Decisions (this week, free or cheap)

- [ ] **0.1 Confirm the entity** with a 1-hour **Australian accountant** consult: Pty Ltd now (recommended), and whether you already hold an ABN as a sole trader. Budget about A$0–400 (estimate).
- [ ] **0.2 Fundraising intent.** If a US investor needs a Delaware C-corp **now**, stop and get a cross-border tax opinion first (`entity-options.md` §2). Otherwise continue.
- [ ] **0.3 Co-founders?** Before registering, agree in writing: the equity split, **4-year vesting with a 1-year cliff**, leaver and buy-back terms, roles, decision-making, time commitment and **IP assignment**. A lawyer reviews the final shareholders' agreement.
- [ ] **0.4 Tell me your state** (NSW, Vic, Qld and so on) so grants (`australia-founder.md` §3) and governing law can be narrowed down.

## Stage 1: Name, domain and email (days 1–3)

- [ ] **1.1 Name screen** (15 min, free): the **ASIC** company and business-name register, **IP Australia** trade marks ([ATMOSS / IP Australia search](https://search.ipaustralia.gov.au/trademarks/search/quick)), and the **USPTO** ([tmsearch.uspto.gov](https://tmsearch.uspto.gov/)), for "ChimeraShield", "Chimera Shield" and "Chimera" in classes **9 and 42**. Also check Google, LinkedIn and GitHub. If "Chimera" is crowded in security, **rename now**.
- [ ] **1.2 Register the domain** (`.com`; optionally `.com.au`, which needs an ABN or ACN). Turn on registrar lock, privacy and MFA. Transfer it to the company after step 3.
- [ ] **1.3 Business email** (Google Workspace) with `hello@`, `[FOUNDER_NAME]@` and `security@`. Use hardware keys or passkeys on the admin account.
- [ ] **1.4 SPF, DKIM and DMARC** on the main and secondary sending domains (`marketing/ads/cold-email-launch-kit.md` Steps 1–3).
- [ ] **1.5 Postal address for CAN-SPAM** (still required for US recipients). A **US virtual mailbox** is the safer choice. Whether an Australian address or PO box is valid for CAN-SPAM is flagged for the lawyer (`spam-act-cold-email.md` §4).

## Stage 2: Keep pre-launch activity legal

- [ ] **2.1 No sales and no scanning of prospects' assets** without written authorization (authorized-scanning skill). Interviews need no entity.
- [ ] **2.2 Spam Act readiness before the first cold send (12 Oct).** Apply the consent tests, evidence columns, identity footer with ABN, and the "unsubscribe" wording in `spam-act-cold-email.md` §3–§5. **Blocks cold email.**
- [ ] **2.3 Keep receipts** for all pre-registration spending; the accountant decides how the company reimburses them.

## Stage 3: Company (target: registered by Fri 2 Oct, so the ABN appears in cold emails from 12 Oct)

- [ ] **3.1 Director ID** for each director (free, online with myID; required before appointment, S).
- [ ] **3.2 Register ChimeraShield Pty Ltd** with ASIC, online or through a provider or the accountant. **A$636** (from 1 Jul 2026, S: [ASIC fee indexation](https://www.asic.gov.au/for-business-and-companies/forms-and-fees/all-fees/fee-indexation)). Choose a constitution with share-class flexibility (`entity-options.md` §3). Use the accountant's or a provider's address as the registered office if possible.
- [ ] **3.3 ABN and TFN** for the company (free). Record the **ACN** and **ABN**. They go in email footers, invoices, the ToS and the privacy policy.
- [ ] **3.4 GST decision.** Register once GST turnover is likely to reach **A$75k** (GST-free exports count towards it, S), or voluntarily earlier if the accountant advises. US sales are generally GST-free exports (`australia-founder.md` §1.4).
- [ ] **3.5 Share issue** to the founder(s) with vesting terms in the shareholders' agreement, and the share register updated. (No 83(b): that's US-only and not relevant to a Pty Ltd.)
- [ ] **3.6 IP assignment** from each founder and contractor to the company (code, docs, domain, brand). Contractors sign before writing code.
- [ ] **3.7 Move the domain and accounts** (GitHub org, cloud, Workspace, registrar) into the company's name.
- [ ] **3.8 Compliance calendar:** ASIC **annual review fee A$342** within 2 months of each review date (S); company tax return; BAS if GST-registered; keep records for 5 years (**FLAG**).

## Stage 4: Bank (week 1–2 after registration)

- [ ] **4.1 Business transaction account** at an Australian bank, in the company's name. **Never mix personal and company money** (Division 7A risk, `entity-options.md` §1).
- [ ] **4.2 USD receiving option** if needed: a multi-currency account with US ACH details (e.g. Wise Business, Airwallex; **FLAG**, check fees and terms) for customers who pay invoices by bank transfer.
- [ ] **4.3 Document the founder's capital contribution** (share subscription money, or a loan from the founder with a simple written loan agreement).

## Stage 5: Payments and public terms (before the first paid pack)

- [ ] **5.1 Stripe Australia** in the company's name. Prices in **USD**. Budget **~3.5% + A$0.30** for US cards, plus ~2% if currency is converted (S). Finance's 2.9% + US$0.30 is too low. **Ask Stripe about USD settlement**, which is available only to a limited number of Australian businesses (S). Turn on **Stripe Tax monitoring** for US state thresholds only; don't register in any state yet (`australia-founder.md` §1.1).
- [ ] **5.2 Invoice template:** entity name, **ABN**, USD amount, "GST-free export" wording where relevant, and payment details.
- [ ] **5.3 W-8BEN-E** filled in and kept ready for any US customer that asks. **Never sign a W-9.**
- [ ] **5.4 Publish the ToS, privacy policy (APP-style), refund terms and the P1 engagement letter** (`terms-outline.md`), updated for an Australian entity (`australia-founder.md` §5). **Lawyer review required before taking money.**

## Stage 6: Bookkeeping (from the first transaction)

- [ ] **6.1 Xero or MYOB** (Australian standards; Xero is the most common with accountants), connected to the bank and Stripe. Track USD sales and conversion.
- [ ] **6.2 A monthly 30-minute close:** categorize, keep receipts, reconcile.
- [ ] **6.3 Engage the accountant for the FY2026–27 company return** (the income year ends 30 June 2027). Ask about R&DTI record-keeping (timesheets and experiment notes) from day one.

## Stage 7: Insurance (before the first paid pack or first customer scan)

- [ ] **7.1 Tech PI / E&O** with **worldwide jurisdiction including the USA and Canada.** Many Australian PI policies exclude US claims by default. **This is the key question to ask the broker.**
- [ ] **7.2 Cyber liability** (first and third party), often bundled with 7.1. Check it covers US breach-notification costs.
- [ ] **7.3 Public liability** (cheap, lower priority for a remote business).
- [ ] **7.4 Get 2–3 broker quotes.** **Estimate:** A$3,500–8,000 a year combined with US jurisdiction. That's **unverified**; quotes decide (`australia-founder.md` §4). Do the security basics in `compliance-roadmap.md` first, because the insurer will ask.
- [ ] **7.5 Read the exclusions:** US/Canada jurisdiction, unauthorized access or intentional acts, contractual liability, and fines and penalties.

## Stage 8: Trade marks (month 2–3, before spending on brand)

- [ ] **8.1 Full clearance search** in Australia and the US by a trade mark attorney.
- [ ] **8.2 File in Australia** with IP Australia (classes 9 and 42). **FLAG:** check the current IP Australia fees; not verified today.
- [ ] **8.3 US filing:** USPTO **US$350 per class** base fee ([USPTO fees](https://www.uspto.gov/trademarks/trademark-fee-information)). **Foreign-domiciled applicants must be represented by a US-licensed attorney** (**FLAG**, confirm the rule). The Madrid Protocol, filed through IP Australia, is an alternative. Ask the attorney.

## Stage 9: Australian support (optional, doesn't block launch)

- [ ] **9.1** Ask the accountant whether R&DTI records are worth keeping from now (companies only; minimum A$20k spend, S).
- [ ] **9.2** Check EMDG Tier 1 availability (Austrade) and your state's program (`australia-founder.md` §3).
- [ ] **9.3** Consider the Stone & Chalk cyber scholarships (formerly AustCyber) and Startmate if you decide to raise.

---

## First 5 steps (this week)

1. **Accountant consult** (0.1) to confirm the Pty Ltd, and tell legal-ops your state (0.4).
2. **Name screen** in Australia and the US (1.1), then **register the domain and set up email with SPF, DKIM and DMARC** (1.2–1.4).
3. **Director ID, then register ChimeraShield Pty Ltd, ABN and TFN** by about **2 Oct** (3.1–3.3).
4. **Make the Spam Act changes to the cold-email kit** (2.2) and set up the US virtual mailbox (1.5), both before **12 Oct**.
5. **Request 2–3 insurance quotes with USA/Canada jurisdiction** (7.1–7.4), and **book a lawyer** to review the ToS, privacy policy and engagement letter (5.4).

## Current status (2026-09-26)

| Step | Status |
|---|---|
| 0.1 Entity confirmation (accountant) | `[!]` needs an accountant, about 1 hr |
| 0.2 Fundraising intent | `[ ]` founder |
| 0.4 Founder's state | `[!]` waiting on founder |
| 1.1–1.5 Name, domain, email, auth, postal address | `[ ]` |
| 2.2 Spam Act changes to the kit | `[ ]` draft rules ready (`spam-act-cold-email.md`) |
| 3.x Company, ABN, shares, IP assignment | `[ ]` |
| 4.x Bank | `[ ]` |
| 5.x Stripe AU, invoices, W-8BEN-E, public terms | `[ ]` terms need updating for an AU entity, then a lawyer |
| 6.x Bookkeeping | `[ ]` |
| 7.x Insurance with US jurisdiction | `[ ]` |
| 8.x Trade marks | `[ ]` |
| 9.x Grants and R&DTI | `[ ]` optional |
