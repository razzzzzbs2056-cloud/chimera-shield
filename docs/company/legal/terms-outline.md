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

## Needs a real lawyer
- Final drafting of the ToS, privacy policy, DPA and BAA, plus governing law once the entity location is known.
- Enforceability of the disclaimer and liability cap, and our negotiating fallback (super-cap) matched to insurance.
- Handling of accidental PHI under a "no PHI" clause.
- Whether the authorization clauses plus product controls adequately reduce CFAA and ETA risk for light active checks.
