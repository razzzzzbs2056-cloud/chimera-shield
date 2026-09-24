# Terms of Service, Privacy Policy and DPA: outlines

> **Draft for discussion. Not legal advice. Review with a qualified lawyer in your jurisdiction.**

**As of:** 2026-09-24 · **Owner:** legal-ops agent · **Status:** outlines plus draft key clauses. Not ready to publish.

These are **outlines** for a lawyer to turn into final documents, not finished documents. The bracketed placeholders `[ENTITY]`, `[DOMAIN]`, `[JURISDICTION]`, `[ADDRESS]` stay until step 3 of `launch-checklist.md` is done. The scanning rules follow `.claude/skills/authorized-scanning/SKILL.md`.

**Customers this must work for:** US tax preparers and CPA firms (FTC Safeguards Rule), dental and medical practices (HIPAA), and small law firms (ABA confidentiality duties). See `docs/company/interviews/recruiting-kit.md`.

---

## Part A: Terms of Service (B2B SaaS)

| # | Section | What goes in it |
|---|---|---|
| A1 | Parties and acceptance | `[ENTITY]`, a `[state/country]` company. Business customers only (no consumers). Whoever accepts confirms authority to bind their organization. |
| A2 | The service | Plain description: passive domain and email-security checks, AI analysis of emails the customer submits, prioritized recommendations, and (later) light active checks on **verified** assets. Features may change. |
| A3 | Accounts and security | Customer keeps credentials safe and uses MFA. One account per organization. Customer is responsible for its users. |
| **A4** | **Authorization to scan** | See **clauses A4.1–A4.6** below. **Non-negotiable.** |
| A5 | Acceptable use | No scanning of third-party assets, no testing of competitors, no phishing of people who haven't consented, no attempts to bypass verification, no submitting data you have no right to share, no reverse engineering, no resale without an MSP agreement. |
| **A6** | **Customer data and pasted emails** | See **clause A6** below. |
| A7 | Fees and billing | Monthly plans ($49 / $99 / $149, draft). Auto-renewal with cancel-anytime. Taxes. Refund policy. Price changes with 30 days' notice. Founding-member pricing terms. |
| **A8** | **No guarantee / disclaimer** | See **clause A8**. |
| **A9** | **Limitation of liability** | See **clause A9**. |
| A10 | Indemnities | **Customer indemnifies us** for scans of assets it wasn't authorized to submit, and for data it had no right to submit. **We indemnify the customer** for third-party IP claims about our software (lawyer to scope). |
| A11 | Confidentiality | Findings are both parties' confidential information. We don't publish customer findings. Anonymized, aggregated statistics are allowed (lawyer to confirm, given HIPAA de-identification rules for health customers). |
| A12 | AI features | Outputs may be wrong. They are recommendations, not instructions, and are never auto-executed. A human decides. We do **not** train models on customer content (matches the product rule). We name our LLM subprocessors in the subprocessor list. |
| A13 | Suspension and termination | We may suspend immediately for suspected unauthorized scanning or abuse. Data export for 30 days after termination, then deletion. |
| A14 | Regulated data | The service is not designed to store PHI, card data, SSNs or tax-return data **except as expressly agreed** (e.g. under a BAA, Part D). Customer must not submit such data otherwise. |
| A15 | Governing law and disputes | `[JURISDICTION]`, **FLAG**: depends on entity location. For US customers, a US state (e.g. Delaware) is expected. A Nepal entity choosing Nepali law may put off US buyers. |
| A16 | Changes, notices, assignment, entire agreement, export control, force majeure | Standard boilerplate (lawyer). |

### A4. Authorization to scan (draft clauses)

**A4.1 Representation.** "By adding a domain, email address, IP address or other asset to the Service, you represent and warrant that you own the asset or are authorized in writing by its owner to have it tested, and you authorize ChimeraShield to perform the checks described for that asset's tier. You understand the results may include sensitive security information."
*This matches the consent wording in the authorized-scanning skill, which must also appear as an in-product checkbox.*

**A4.2 Tiers.** "Passive checks use public information only (e.g. DNS, SPF, DKIM, DMARC and certificate records). **Light active checks** (e.g. port and service checks, known-vulnerability checks) run only after you verify control of the asset by DNS TXT record or file upload, and after you give checkbox consent, which we record with a timestamp. **Intrusive testing** (penetration tests, phishing simulations, credential testing) is not part of the Service and needs a separate signed statement of work."

**A4.3 Re-verification.** "We re-verify ownership at least every 90 days and may pause checks until you re-verify."

**A4.4 Third-party infrastructure.** "We only check records and systems you control. We do not test shared hosting, CDN, email-provider or cloud-provider infrastructure beyond your own records, and we rate-limit all checks."

**A4.5 Our right to refuse.** "We may refuse, pause or stop any check we reasonably believe is unauthorized, and may report abuse to the affected party or to authorities where the law requires."

**A4.6 Customer responsibility.** "You are responsible for any check run on an asset you were not authorized to submit and will indemnify ChimeraShield for resulting claims (see Indemnities)."

*Why this matters:* Unauthorized access or testing is a crime under the US **Computer Fraud and Abuse Act, 18 U.S.C. §1030** ([DOJ CFAA manual](https://www.justice.gov/jm/jm-9-48000-computer-fraud)), Nepal's **Electronic Transactions Act 2063, §45** ([summary](https://www.lawimperial.com/highlights-of-electronic-transactions-act-2006/), 3P), and similar laws elsewhere. The contract doesn't protect us if we scan without verification. **Product controls come first; the clause backs them up.**

### A6. Pasted emails and personal data (draft clause)

"The phishing analyzer lets you submit emails. Emails may contain personal data of the sender, the recipient or other people. You confirm you may share that content with us for security analysis. We process submitted emails **in memory for analysis**, we **do not use them to train AI models**, and we **delete them within 30 days** unless you choose to save the result to your account. Saved results are encrypted at rest and visible only to your account. Please **redact** patient, client or financial details that aren't needed to judge whether the email is malicious. Do not submit emails containing protected health information unless you have signed our Business Associate Agreement (see [link])."

*Product must match the words:* auto-redaction hints in the UI, a 30-day purge job, no-training contract terms with the LLM provider, and a "save" toggle that is off by default. **Never promise in the ToS what the code doesn't do.**

### A8. No guarantee (draft clause)

"ChimeraShield helps you find and prioritize security issues. **No security product can find every vulnerability or stop every attack.** The Service, its findings and AI-generated recommendations are provided 'as is' and 'as available'. We do not warrant that the Service will detect all threats, that any email marked safe is safe, or that following our recommendations will prevent a breach or make you compliant with any law or standard (including HIPAA, the FTC Safeguards Rule, or ABA rules). You remain responsible for your own security program and compliance decisions. The Service is not legal advice."

This matches the brand rule "No security guarantees" in `.claude/skills/company-context/SKILL.md`. **Marketing copy must not contradict it** (no "fully protected", "HIPAA compliant in minutes", and so on).

### A9. Limitation of liability (draft clause)

"To the extent the law allows: (a) neither party is liable for indirect, incidental, special, consequential or punitive damages, or for lost profits, revenue, data or business, including losses from a security incident the Service did not detect; and (b) each party's total liability is capped at **the fees you paid in the 12 months before the claim**. The caps don't apply to your payment obligations, your indemnity for unauthorized scanning, or either party's fraud or wilful misconduct."

**FLAG:** Healthcare, legal and financial customers may push for a **higher separate cap for data-breach and confidentiality claims** (a "super-cap", often a multiple of fees). Decide the fallback position with a lawyer and **match it to your insurance limits** (launch checklist 7.1–7.2). Consumer-protection and state laws may limit disclaimers. Lawyer to confirm enforceability in the chosen jurisdiction.

---

## Part B: Privacy Policy (for the website and product)

| # | Section | Contents |
|---|---|---|
| B1 | Who we are | `[ENTITY]`, `[ADDRESS]`, `privacy@[DOMAIN]` |
| B2 | Our two roles | **Controller** for account, billing, website and marketing data. **Processor / service provider** for content customers submit (domains, pasted emails, findings), which is governed by the DPA (Part C). |
| B3 | What we collect | Account data, billing data (handled by Stripe or Paddle; we don't store card numbers), usage logs, submitted assets and findings, pasted emails, support messages, cookies and analytics |
| B4 | Why and legal basis | Provide the service, security and fraud prevention, billing, support, product improvement **using aggregated or de-identified data only**, marketing with opt-out. GDPR legal bases if EU/UK visitors are served. |
| B5 | AI processing | Which features use LLMs, that submitted content goes to named LLM providers under no-training and no-retention terms (**verify each provider's actual terms**), and that output is advisory only |
| B6 | Sharing | Subprocessors (hosting, LLM, email, payments, analytics) with a public list, plus legal requests and business transfers. **We do not sell or "share" personal data** in the CCPA sense. |
| B7 | Retention | Pasted emails: 30 days unless saved. Findings: for the life of the account plus 30 days. Billing: as tax law requires. Logs: `[N]` days. |
| B8 | Security | Encryption in transit and at rest, MFA, least privilege, logging. A **short** description; don't overpromise. |
| B9 | International transfers | Data stored in `[region]`. **FLAG:** if the team is in Nepal and accesses US customer data, disclose it. Health and legal customers may ask. |
| B10 | Your rights | Access, deletion, correction and opt-out. Methods and response times. California and other US state rights as they apply. Nepal Privacy Act 2075 rights if Nepali users are served ([ADB summary](https://lpr.adb.org/resource/privacy-act-2075-2018-nepal)). |
| B11 | Children | Not directed to children. |
| B12 | Changes and contact | Standard. |

**Applicability notes (as of 2026-09-24):**
- **CCPA/CPRA** applies only above **$26,625,000 annual revenue** (2025–26 adjusted figure), **100,000+ California consumers or households**, or 50%+ of revenue from selling or sharing data ([CPPA, monetary thresholds](https://www.cppa.ca.gov/regulations/cpi_adjustment.html)). We are well below all of these for now. Still write the policy CCPA-style, because customers expect it and other state laws have lower thresholds (**FLAG:** state-by-state check at around 100 customers).
- **GDPR** applies if we offer the service to people in the EU or UK or monitor them (GDPR Art. 3(2), [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2016/679/oj)). The US-focused plan avoids this at first. Don't market in the EU until the DPA has SCCs and an Art. 27 representative has been considered.

---

## Part C: Data Processing Agreement (DPA) outline

Offer one standard DPA to every customer. Tax preparers in particular **need** contract terms with us. Under the FTC Safeguards Rule, **16 CFR 314.4(f)**, a financial institution must choose capable service providers, **require them by contract** to maintain safeguards, and assess them periodically ([eCFR 16 CFR 314.4](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314/section-314.4); [FTC guide](https://www.ftc.gov/business-guidance/resources/ftc-safeguards-rule-what-your-business-needs-know)). Law firms need something similar to meet their confidentiality duties (ABA Formal Op. 477R; see the recruiting kit).

| # | Section | Contents |
|---|---|---|
| C1 | Roles and scope | Customer is controller/business; ChimeraShield is processor/service provider. Scope: submitted assets, pasted emails, findings. |
| C2 | Instructions | We process only to provide the service and follow the customer's documented instructions. **No training on customer data. No selling.** |
| C3 | Confidentiality | Staff with access are under confidentiality obligations. Access follows least privilege. |
| C4 | Security measures (annex) | Encryption at rest and in transit, MFA, logging, backups, vulnerability management, access reviews, incident response. **Only list measures that actually exist.** |
| C5 | Subprocessors | Public list, 30 days' notice of changes, and the customer's right to object |
| C6 | Breach notification | We notify the customer **without undue delay, target within 72 hours** of confirming a breach affecting their data, with the details they need. This helps tax preparers meet the FTC's **30-day** notice to the FTC for events affecting 500+ consumers ([FTC, May 2024](https://www.ftc.gov/business-guidance/blog/2024/05/safeguards-rule-notification-requirement-now-effect)), and law firms meet ABA Op. 483 duties. |
| C7 | Assistance | Help with data-subject requests, risk assessments and customer audits (by questionnaire first; on-site audits only at the customer's cost) |
| C8 | Deletion and return | Pasted emails within 30 days. All customer data within 30 days of termination. Certificate of deletion on request. |
| C9 | International transfers | **FLAG:** SCCs/UK addendum only if EU/UK data is ever processed. Disclose where staff access data from. |
| C10 | CCPA service-provider terms | The required statutory restrictions (no selling or sharing, no use outside the business purpose) |
| C11 | Order of precedence | DPA over ToS for data matters; BAA over both for PHI |

---

## Part D: When a HIPAA Business Associate Agreement becomes necessary

**Rule:** A **business associate** is a person who, on behalf of a covered entity, **creates, receives, maintains or transmits protected health information (PHI)** ([45 CFR 160.103](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-160/subpart-A/section-160.103)). The covered entity must have a written contract meeting **45 CFR 164.504(e)** ([HHS business associates FAQ](https://www.hhs.gov/hipaa/for-professionals/faq/business-associates/index.html)). HHS says a cloud provider that maintains ePHI is a business associate **even if it can't view the data** because it is encrypted ([HHS cloud guidance](https://www.hhs.gov/hipaa/for-professionals/special-topics/health-information-technology/cloud-computing/index.html)).

| ChimeraShield activity for a clinic | Touches PHI? | BAA needed? |
|---|---|---|
| Passive DNS / SPF / DKIM / DMARC scan of the clinic's domain | No, public records | **Probably no** |
| Owner and office-manager account info, billing | No | No |
| Clinic pastes a suspicious email that **mentions a patient** (name plus appointment, insurance or diagnosis) | **Yes, likely PHI** | **Yes, if this is allowed** |
| Future: reading the clinic's M365/Google mailbox or logs | Yes | **Yes** |

**Recommended stance (decision for founder plus lawyer):**
1. **MVP, before a BAA is ready:** for healthcare accounts, the ToS and UI **prohibit submitting PHI**. Add a visible warning on the paste box ("Remove patient details before submitting"), with automatic PHI-pattern detection and a redaction prompt. **FLAG:** a contractual prohibition lowers the risk but may not settle it if PHI arrives anyway. The lawyer should confirm how to handle accidental receipt.
2. **Before selling to any clinic that will paste real emails:** sign BAAs **downstream** with every subprocessor that would touch PHI (cloud host, LLM provider, email provider), and use only HIPAA-eligible services. Have a standard ChimeraShield BAA ready. Complete our own **HIPAA Security Rule risk analysis** and policies, because a business associate must comply with the Security Rule directly.
3. **Don't claim "HIPAA compliant"** in marketing. Say "we sign BAAs" only once you really can.
4. Watch the **proposed HIPAA Security Rule update** (NPRM Dec 27, 2024). A final rule is not expected before July 2027 ([HHS NPRM fact sheet](https://www.hhs.gov/hipaa/for-professionals/security/hipaa-security-rule-nprm/factsheet/index.html)).

---

## Part E: P1 "Safeguards-Ready WISP & Evidence Pack" (first paid offer)

Source spec: `docs/company/product/prd-wisp-evidence-pack.md`. First market: US CPA and tax-prep firms.

### E1. Regulatory check: the FTC Safeguards Rule small-firm exception (16 CFR 314.6)

**Verified text (2026-09-24).** The proxy blocked direct fetches of eCFR, govinfo and ftc.gov, so this text comes from search snippets of the official eCFR page. **Re-read it on [eCFR §314.6](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314/section-314.6) before the first sale.**
> "Section 314.4(b)(1), (d)(2), (h), and (i) do not apply to financial institutions that maintain customer information concerning fewer than five thousand consumers."

**What that removes and what stays**, per [16 CFR 314.4](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314/section-314.4) and [314.3](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314/section-314.3):

| Element | Under 5,000 consumers | Note |
|---|---|---|
| §314.3(a): a **written** information security program ("in one or more readily accessible parts") | **Still required** | This is the WISP. The exception does **not** remove it. |
| §314.4(a): a Qualified Individual | Still required | |
| §314.4(b): risk assessment | **Still required**, but **not** the formal written-assessment criteria in **(b)(1)** | The firm still has to identify and assess risks. The WISP should record them briefly. |
| §314.4(c): safeguards (access controls, data inventory, **encryption**, secure development, **MFA**, disposal, change management, logging) | Still required | |
| §314.4(d)(1): regularly test or monitor safeguards | Still required | |
| §314.4(d)(2): continuous monitoring **or** periodic penetration testing and vulnerability assessments | **Exempt** | P1 doesn't offer pen testing anyway (PRD §8). |
| §314.4(e): staff training and qualified security personnel | Still required | |
| §314.4(f): service-provider oversight | Still required | This applies to us if we ever access customer information (see E3.6). |
| §314.4(g): evaluate and adjust the program | Still required | |
| §314.4(h): **written** incident response plan | **Exempt** | Still **recommended**, and insurers ask for it. Label it "recommended, not required for your size". |
| §314.4(i): annual written report to the board or senior officer | **Exempt** | |
| §314.4(j): **notify the FTC** within 30 days of an event affecting 500+ consumers | **Still required**: §314.6 does not list (j) | [FTC, May 2024](https://www.ftc.gov/business-guidance/blog/2024/05/safeguards-rule-notification-requirement-now-effect) |

**FLAG, needs a lawyer: how to count "fewer than five thousand consumers."** The Rule counts *consumers whose customer information the firm maintains*, not clients served this year. A firm that keeps several years of returns, including spouses and dependents, may pass 5,000 even with about 1,000 returns a year. **This is my inference and is not verified.** The intake should ask for "individuals whose records you keep, including past years" and must **not** tell a firm it is exempt. The firm decides, and a lawyer should give us a counting rule.

**How this changes the pitch for small preparers:**
1. **Don't sell fear of pen tests or board reports** to small firms. Those elements are exempt, and saying otherwise is inaccurate.
2. **The core message gets stronger:** "Even the smallest firm must have a **written** security program, a named Qualified Individual, MFA, encryption, training and vendor oversight, and must tell the FTC about a breach affecting 500+ people. Line 11 of your W-12 asks you to confirm you know that."
3. **Sell "right-sized", not "full enterprise":** "Your plan applies the small-firm exception where it fits, so you don't carry paperwork the rule doesn't require." That is a real advantage over generic templates, which include everything.
4. **Never state a firm's exemption status as fact.** Say "if you maintain information on fewer than 5,000 consumers, these elements are not required", and let the owner confirm their count in writing at intake.

### E2. Disclaimer wording for the pack (draft for lawyer review)

**Short form (footer of every page of the WISP, Evidence Report and Fix-First plan):**
> Prepared with [FIRM NAME] from information the firm provided and passive public checks run on [DATE]. Not legal advice and not a compliance certification or audit. [FIRM NAME] remains responsible for its information security program and for its IRS Form W-12 / PTIN attestation.

**Long form (cover page and engagement letter):**
> **About this document.** ChimeraShield helped [FIRM NAME] prepare this written information security plan (WISP), Evidence Report and Fix-First plan. We based them on information the firm gave us during intake, screenshots and screen-shares the firm chose to show us, and passive checks of public records for [DOMAIN] on [DATE].
>
> **What this is not.** This is **not legal, tax or insurance advice**. It is **not an audit, certification, attestation or guarantee** that [FIRM NAME] complies with the FTC Safeguards Rule (16 CFR Part 314), IRS requirements, state law or any other standard, and ChimeraShield is not a law firm or a CPA firm. Controls marked **"Owner-stated"** were reported by the firm and not checked by us. Controls marked **"Verified"** were observed only on the date shown and may have changed since. No review can find every weakness or prevent every incident.
>
> **The firm's responsibility.** [FIRM NAME] and its Qualified Individual, [NAME], decide what the firm's security program contains. They are responsible for adopting it, putting it in place, keeping it current, and answering truthfully on **IRS Form W-12 (including line 11)**, to insurers, clients and regulators. Whether the small-firm exception in 16 CFR 314.6 applies depends on the firm's own count of consumers, which the firm confirmed as [BAND] on [DATE]. If you have legal questions about your obligations, consult a qualified attorney.

**Wording rules (matches PRD AC7 and AC10):** never use "compliant", "certified", "passes", "approved" or "guaranteed". "Safeguards-Ready" is a product name. **FLAG:** the lawyer should confirm that "Safeguards-Ready" doesn't imply certification under FTC Act §5 (deceptive claims). A safer fallback is "Safeguards WISP & Evidence Pack".

### E3. Engagement terms outline for the one-time P1 service

A short **engagement letter** (2–3 pages), accepted by click-through before payment or signed by e-signature. It references the ToS and adds:

| # | Section | Contents |
|---|---|---|
| E3.1 | Parties and authority | `[ENTITY]` and the firm. The signer confirms authority to bind the firm. |
| E3.2 | Scope (what's included) | 60-min intake, passive checks on **one** domain, three deliverables (WISP, one-page Evidence Report, Fix-First top 5), and a 30-min debrief. Delivery within **7 business days** of the intake **and** receipt of the owner's intake facts. One round of factual corrections within 14 days. |
| E3.3 | Out of scope | Legal, tax or insurance advice. Acting as the firm's Qualified Individual. Pen tests, vulnerability scans, phishing simulations or any active testing. Logging into the firm's systems. Fixing the gaps. Filling in insurer, client or regulator forms. Responding to incidents. Anything about taxpayer data. |
| E3.4 | Firm responsibilities | Provide accurate facts. Confirm its consumer-count band in writing. Name the Qualified Individual. Review, adopt and sign the WISP. Decide which recommendations to implement. Keep the plan current (annual review date in the WISP). |
| E3.5 | Authorization to check | The consent text from PRD §7 and clause A4.1, **passive tier only**, for the listed domain. Recorded with name, email and UTC timestamp **before** any check. |
| E3.6 | **No taxpayer data** | The firm must not share taxpayer or client information with us, including during screen-shares (close client files first; we stop the session if client data appears). The intake collects only information about the firm itself. **Purpose:** to keep us out of "customer information" under the Safeguards Rule and IRS rules. **FLAG:** if accidental exposure happens anyway, we may be a **service provider under §314.4(f)**. Offer the DPA (Part C) as a fallback, and have the lawyer confirm. |
| E3.7 | Confidentiality and data | Intake notes, screenshots and findings are encrypted at rest and shared only with named firm contacts. Retained for 12 months (for the annual-review upsell) unless the firm asks for earlier deletion, then deleted. No AI training on firm data. LLM-drafted text is reviewed by a human before delivery. |
| E3.8 | Fees and payment | One-time fee `[$495 founding / $795 list]`, paid upfront through Stripe (or Paddle, depending on the entity path). **Refund:** full refund before the intake call; after delivery, a refund only if we miss the 7-business-day delivery (lawyer and founder to decide). Optional credit toward Watch if started within 30 days (PRD §10). |
| E3.9 | Ownership and licence | On payment, the firm owns its completed WISP and reports and may share them with insurers, clients and regulators **with the disclaimer intact**. ChimeraShield keeps its templates, methods and anonymized know-how. |
| E3.10 | Disclaimer | The E2 long form, incorporated in full |
| E3.11 | Limitation of liability | Total liability capped at **the fee paid for the pack**. No indirect or consequential damages, including regulatory penalties, breach costs or lost clients. Carve-outs for fraud, wilful misconduct and our confidentiality breach (lawyer to set a cap for the latter). **FLAG:** check enforceability and match to Tech E&O coverage. **Buy E&O before the first pack is sold** (launch checklist 7.1). |
| E3.12 | Reliance | The deliverables are for the firm's own use. No third party (insurer, client, regulator) may rely on them as our representation. |
| E3.13 | Term and termination | Ends on delivery plus the correction window. Either party may cancel before intake. |
| E3.14 | Governing law | `[JURISDICTION]` (see A15) |

**Timing conflict to resolve (for the coordinator):** the PRD wants a **live Stripe link by 8 Oct 2026** and sales from 15 Oct. Stripe requires a legal entity, and **no entity exists and the founder's country is still unknown.** US-resident path: Atlas can finish in days, so it is feasible if started this week. Nepal-resident path: **not feasible by 8 Oct** without the Nepal lawyer's clearance (see `entity-options.md`). Interim options for a lawyer to weigh: sell as a sole proprietor in the founder's own name (US only), or delay paid sales and run S5 plus interviews first.

---

## Needs a real lawyer
- **P1:** re-verify §314.6 on eCFR, set the consumer-counting rule, approve the E2 disclaimer and the E3 engagement letter, confirm that "Safeguards-Ready" isn't misleading, and consider whether preparing a WISP for a client raises any unauthorized-practice-of-law concern in the states we sell to (**FLAG**, not researched).
- Final drafting of the ToS, privacy policy, DPA and BAA, plus governing law once the entity location is known.
- Enforceability of the disclaimer and liability cap, and our negotiating fallback (super-cap) matched to insurance.
- Handling of accidental PHI under a "no PHI" clause.
- Whether the authorization clauses plus product controls adequately reduce CFAA and ETA risk for light active checks.
