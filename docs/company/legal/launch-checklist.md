# Launch checklist: from zero to able to take money

> **Draft for discussion. Not legal advice. Review with a qualified lawyer in your jurisdiction.**

**As of:** 2026-09-24 · **Owner:** legal-ops agent · **Company status:** no entity, no domain, no email, pre-revenue

Work through the list top to bottom. Each step unblocks the next. Paths: **US** = US-resident founder, **NP-US** = Nepal-resident founder with a US entity, **NP** = Nepal Pvt. Ltd. See `entity-options.md`.

**Status key:** `[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked on a lawyer or decision

---

## Stage 0: Decisions (this week, free)

- [!] **0.1 Tell legal-ops your country of residence and whether you plan to raise.** Everything below depends on this.
- [!] **0.2 Nepal residents only: book a Nepali corporate/FX lawyer** before step 3 to confirm whether you may own a US entity (Act Restricting Investment Abroad 1964; FERA §10A as amended in 2025). See `entity-options.md` §4.
- [ ] **0.3 Co-founders?** If there is more than one founder, agree on these in writing *before* incorporation: equity split, roles, **4-year vesting with a 1-year cliff**, what happens if someone leaves (buyback of unvested shares), decision-making, IP assignment, and time commitment. A lawyer should review the final version.

## Stage 1: Domain and email (days 1–3, about $15–30/yr + $6–7/user/mo)

These can happen before the entity exists and they unblock outreach (see `docs/company/interviews/recruiting-kit.md`).

- [ ] **1.1 Name checks before you buy anything** (15 minutes, free). This is only a first screen; the full search is step 7.
  - USPTO trademark search for "ChimeraShield", "Chimera Shield" and "Chimera" in classes **9** (software) and **42** (SaaS/security services) ([USPTO trademark search](https://tmsearch.uspto.gov/)).
  - Search for existing businesses: Google, LinkedIn, GitHub, app stores, and Delaware or your state's entity search.
  - If "Chimera" is crowded in security, rename **now** while it costs nothing.
- [ ] **1.2 Register the domain** (e.g. `chimerashield.com` or an alternative). Turn on registrar lock, WHOIS privacy and **MFA**. Register it to the founder personally for now, and **transfer it to the company** in writing after incorporation (step 3.5).
- [ ] **1.3 Business email** (Google Workspace or Microsoft 365). Create `hello@`, `[FOUNDER_NAME]@`, and `security@` for vulnerability reports. Use MFA with hardware keys or passkeys on the admin account.
- [ ] **1.4 Email authentication** before any cold email: **SPF, DKIM, DMARC** (start at `p=none` with reporting, then move to `quarantine`). As a security company, our own domain must pass our own scan.
- [ ] **1.5 Postal address** for CAN-SPAM footers (`[POSTAL_ADDRESS]` in the recruiting kit). Use a virtual mailbox or registered-agent address. Don't use your home address if you can avoid it ([FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)).

## Stage 2: Keep discovery legal before the entity exists

- [ ] **2.1 No sales, no scanning of prospects' assets** without written authorization (see `.claude/skills/authorized-scanning/SKILL.md`). Interviews need no entity.
- [ ] **2.2 Keep receipts** for every expense from today. Pre-formation costs can often be reimbursed by or contributed to the company later (**FLAG:** ask your accountant how).

## Stage 3: Entity (week 2–4, after 0.1–0.2)

- [ ] **3.1 Form the entity:**
  - **US, raising:** Delaware C-corp via **Stripe Atlas** ($500) or Firstbase ($399 + $299/yr registered agent).
  - **US, bootstrapping:** LLC in your home state.
  - **NP-US:** only after the lawyer's green light in 0.2. Check first that a bank (step 4) will onboard you, because Mercury does not accept Nepal residents.
  - **NP:** Pvt. Ltd. at the Office of the Company Registrar ([ocr.gov.np](https://ocr.gov.np/)). Consider IT-industry registration for export incentives.
- [ ] **3.2 Tax ID.** **US/NP-US:** EIN (IRS SS-4; online for US residents, phone or fax for foreign applicants: [IRS SS-4 instructions](https://www.irs.gov/instructions/iss4)). **NP:** PAN/VAT with the Inland Revenue Department.
- [ ] **3.3 Founder stock and 83(b).** C-corp only: issue founder shares with vesting, then **file the 83(b) within 30 days**. There is no extension and missing it can be very costly. Atlas files it for you, but keep the proof.
- [ ] **3.4 IP assignment.** Every founder signs an **IP assignment / CIIAA** transferring all prior ChimeraShield code, designs, domain and brand to the company. Contractors sign one too before writing code.
- [ ] **3.5 Transfer the domain and accounts** (GitHub org, cloud, Workspace) into the company's name.
- [ ] **3.6 State registration.** US founders: register the Delaware company as a foreign entity in the state where you work, and get any local business license. California has an $800/yr minimum tax ([CA FTB](https://www.ftb.ca.gov/file/business/types/corporations/index.html)).
- [ ] **3.7 Compliance calendar.** Delaware C-corp: franchise tax and annual report by **March 1**. Delaware LLC: $300 by **June 1** ([Delaware](https://corp.delaware.gov/frtax/)). Foreign-owned US LLC: **Form 5472 + pro forma 1120** every year ($25,000 penalty if missed: [IRS](https://www.irs.gov/instructions/i5472)). NP: OCR annual return, audit and IRD returns.

## Stage 4: Bank account (week 3–5)

- [ ] **4.1 Open a business bank account** in the company's name only. **Never mix personal and company money.**
  - US: Mercury, Relay or a local bank.
  - NP-US: Mercury **lists Nepal as prohibited** ([Mercury](https://support.mercury.com/hc/en-us/articles/28771710754580-Prohibited-countries)). Check alternatives' eligibility before forming.
  - NP: a Nepali commercial bank, plus a foreign-currency account if eligible.
- [ ] **4.2 Founder capital contribution** documented (a small wire from founder to company, with a note).

## Stage 5: Payments (week 4–6)

- [ ] **5.1 Stripe** (US and NP-US). Create the account in the company's name. Turn on Stripe Billing for $49/$99/$149 plans and **Stripe Tax** to monitor where you owe SaaS sales tax. **FLAG:** SaaS sales-tax treatment differs by state; review it with a CPA once you have customers in several states.
- [ ] **5.2 NP path:** Paddle (merchant of record, which handles tax; verify it accepts Nepal sellers), Payoneer, or SWIFT invoices. Confirm the NRB documentation your bank needs for each inbound payment.
- [ ] **5.3 Publish ToS, privacy policy and refund terms** before taking the first payment (see `terms-outline.md`). Stripe and Paddle both require public policies.

## Stage 6: Bookkeeping (from the first transaction)

- [ ] **6.1 Accounting software** (e.g. QuickBooks, Xero, or Wave for very early) connected to the bank and Stripe.
- [ ] **6.2 A monthly 30-minute close:** categorize transactions, save receipts, reconcile.
- [ ] **6.3 An accountant engaged before the first tax deadline.** NP-US needs a **cross-border** accountant familiar with Form 5472 and Nepali tax.

## Stage 7: Insurance (before the first paying customer or first scan of a customer asset)

- [ ] **7.1 Technology E&O** (errors and omissions / professional liability). This covers claims that our advice or scan missed something and the customer suffered a loss. It is **essential for a security advisor.**
- [ ] **7.2 Cyber liability** (first- and third-party). This covers a breach of *our* systems that exposes customer findings or pasted emails. It is often bundled with Tech E&O in one policy.
- [ ] **7.3 General liability**, which is cheap and often requested in contracts.
- [ ] **7.4 Get 2–3 quotes through a broker** who writes tech startups (US and NP-US paths). Expect questions about MFA, backups and EDR, so do the security basics in `compliance-roadmap.md` first. **FLAG:** premiums vary a lot. I have no reliable 2026 price range, so get quotes. **FLAG (NP):** US-grade E&O for a Nepal entity may be hard to get; ask a broker.
- [ ] **7.5 Read the exclusions:** unauthorized-scanning / "intentional acts" exclusions, contractual-liability exclusions, and sub-limits for regulatory fines (HIPAA, FTC).

## Stage 8: Trademark for "ChimeraShield" (month 2–3, before public launch or spending on brand)

- [ ] **8.1 Full clearance search** by a trademark attorney or a professional search service. Cover USPTO, state registrations, common-law uses, domains, and look-alike names ("Chimera", "*Shield" marks are common in security software).
- [ ] **8.2 File a US application** if the name is clear. The base fee is **$350 per class** (since Jan 18, 2025), plus a $200/class surcharge for free-text descriptions ([USPTO fee information](https://www.uspto.gov/trademarks/trademark-fee-information), [Federal Register, Nov 18 2024](https://www.federalregister.gov/documents/2024/11/18/2024-26644/setting-and-adjusting-trademark-fees-during-fiscal-year-2025)). Likely classes are 9 and 42, so about $700 using ID-Manual descriptions. **Foreign-domiciled applicants must use a US-licensed attorney** at the USPTO (**FLAG:** confirm the current rule).
- [ ] **8.3 NP path:** consider Nepal registration at the Department of Industry. **FLAG:** process not researched.

---

## Current status (2026-09-24)

| Step | Status |
|---|---|
| 0.1 Location and fundraising decision | `[!]` waiting on founder |
| 0.2 Nepal lawyer (if applicable) | `[!]` waiting on 0.1 |
| 1.1 Name screen | `[ ]` |
| 1.2–1.5 Domain, email, SPF/DKIM/DMARC, postal address | `[ ]` |
| 3.x Entity, EIN, 83(b), IP assignment | `[ ]` blocked on 0.1 |
| 4.x Bank | `[ ]` |
| 5.x Stripe/Paddle, public policies | `[ ]` drafts in `terms-outline.md` |
| 6.x Bookkeeping | `[ ]` |
| 7.x Insurance | `[ ]` |
| 8.x Trademark | `[ ]` |
