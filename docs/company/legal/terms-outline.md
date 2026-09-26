# Terms of Service, Privacy Policy and DPA: outlines

> **Draft for discussion. Not legal advice. Review with a qualified lawyer in your jurisdiction.**

**As of:** 2026-09-26 · **Owner:** legal-ops agent · **Status:** outlines plus draft key clauses. Not ready to publish.
**Changed on 2026-09-26:** the founder is in Australia and the entity is an **Australian Pty Ltd** (`australia-founder.md`, company-context). The earlier Nepal-entity and US-entity (Atlas/Delaware) paths are **withdrawn** from this document. `entity-options.md` keeps them only as history. Added: governing law for a Pty Ltd selling to US and AU customers (A15), the Australian Consumer Law and unfair contract terms (A17), the Privacy Act (Part B), TFN handling (Part F) and the AU "Client Data Security Pack" disclaimer and engagement terms (Part G).

These are **outlines** for a lawyer to turn into final documents. The placeholders `[ABN]`, `[STATE]`, `[DOMAIN]` and `[ADDRESS]` stay until the company is registered (`launch-checklist.md` Stage 3). The scanning rules follow `.claude/skills/authorized-scanning/SKILL.md`.

**Evidence note.** Australian government sites were blocked by the proxy on 2026-09-24/26. Australian facts come from **search summaries** of the linked pages, accessed 2026-09-26, and are marked **(S)**. **FLAG** means a lawyer must confirm.

**Customers this must work for:**
- **Sell (US):** tax preparers and CPA firms (FTC Safeguards Rule). Later: dental and medical practices (HIPAA) and small law firms (ABA duties).
- **Pilot (AU, 3 Nov to 11 Dec 2026):** tax and accounting practices (Tax Agent Services Act 2009, TPB Code, TFN Rule, Privacy Act). See `docs/company/market/australia-vs-us.md`.

---

## Part A: Terms of Service (B2B SaaS)

| # | Section | What goes in it |
|---|---|---|
| A1 | Parties and acceptance | **ChimeraShield Pty Ltd (ABN `[ABN]`), a company registered in `[STATE]`, Australia.** Business customers only. Whoever accepts confirms authority to bind their organization. **Note:** "business customers only" does **not** switch off the Australian Consumer Law for AU buyers (see A17). |
| A2 | The service | Plain description: passive domain and email-security checks, AI analysis of emails the customer submits, prioritized recommendations, and (later) light active checks on **verified** assets. Features may change (see A17 on variation). |
| A3 | Accounts and security | Customer keeps credentials safe and uses MFA. One account per organization. Customer is responsible for its users. |
| **A4** | **Authorization to scan** | See **clauses A4.1–A4.6** below. **Non-negotiable.** |
| A5 | Acceptable use | No scanning of third-party assets, no testing of competitors, no phishing of people who haven't consented, no attempts to bypass verification, no submitting data you have no right to share, **no submitting tax file numbers (Part F)**, no reverse engineering, no resale without an MSP agreement. |
| **A6** | **Customer data and pasted emails** | See **clause A6** below. |
| A7 | Fees and billing | **US customers:** prices in **USD**; services to non-residents outside Australia are expected to be **GST-free exports** (accountant to confirm, `australia-founder.md` §1.4). **AU customers:** prices in **A$, shown GST-inclusive or clearly "+ GST"**; tax invoices once GST-registered. Monthly plans (US$49 / $99 / $149, draft). Auto-renewal with cancel-anytime. Refunds per A17.3. **Price changes:** 30 days' notice **plus the right to cancel without penalty before the change applies** (needed for UCT, see A17.2). Founding-member pricing terms. |
| **A8** | **No guarantee / disclaimer** | See **clause A8**. Now includes an ACL savings sentence. |
| **A9** | **Limitation of liability** | See **clause A9**. Now includes an ACL s 64A clause. |
| A10 | Indemnities | **Customer indemnifies us** for scans of assets it wasn't authorized to submit, and for data it had no right to submit. **We indemnify the customer** for third-party IP claims about our software. **UCT note:** keep the customer indemnity **narrow** (limited to their own unauthorized submissions) and mutual where possible; a broad one-way indemnity is a classic unfair term (A17.2). |
| A11 | Confidentiality | Findings are both parties' confidential information. We don't publish customer findings. Anonymized, aggregated statistics are allowed (lawyer to confirm, given HIPAA de-identification rules and Australian "de-identified" guidance). |
| A12 | AI features | Outputs may be wrong. They are recommendations, not instructions, and are never auto-executed. A human decides. We do **not** train models on customer content. We name our LLM subprocessors (and **the countries they process in**) in the subprocessor list. |
| A13 | Suspension and termination | We may suspend immediately for suspected unauthorized scanning or abuse. **UCT note:** give the customer a matching right to terminate, refund prepaid fees for unused periods when we terminate without customer fault, and limit immediate suspension to genuine risk (legitimate-interest test). Data export for 30 days after termination, then deletion. |
| A14 | Regulated data | The service is not designed to store PHI, card data, SSNs, **Australian TFNs**, or tax-return data **except as expressly agreed** (e.g. under a BAA, Part D). Customer must not submit such data otherwise. |
| **A15** | **Governing law and disputes** | See **A15 options** below. |
| A16 | Changes, notices, assignment, entire agreement, export control, force majeure | Standard boilerplate (lawyer). **UCT note:** "we may change these terms at any time" is a high-risk term; use notice plus a right to exit (A17.2). |
| **A17** | **Australian Consumer Law (ACL) and unfair contract terms** | See **A17** below. |

### A4. Authorization to scan (draft clauses)

**A4.1 Representation.** "By adding a domain, email address, IP address or other asset to the Service, you represent and warrant that you own the asset or are authorized in writing by its owner to have it tested, and you authorize ChimeraShield to perform the checks described for that asset's tier. You understand the results may include sensitive security information."
*This matches the consent wording in the authorized-scanning skill, which must also appear as an in-product checkbox.*

**A4.2 Tiers.** "Passive checks use public information only (e.g. DNS, SPF, DKIM, DMARC and certificate records). **Light active checks** (e.g. port and service checks, known-vulnerability checks) run only after you verify control of the asset by DNS TXT record or file upload, and after you give checkbox consent, which we record with a timestamp. **Intrusive testing** (penetration tests, phishing simulations, credential testing) is not part of the Service and needs a separate signed statement of work."

**A4.3 Re-verification.** "We re-verify ownership at least every 90 days and may pause checks until you re-verify."

**A4.4 Third-party infrastructure.** "We only check records and systems you control. We do not test shared hosting, CDN, email-provider or cloud-provider infrastructure beyond your own records, and we rate-limit all checks."

**A4.5 Our right to refuse.** "We may refuse, pause or stop any check we reasonably believe is unauthorized, and may report abuse to the affected party or to authorities where the law requires."

**A4.6 Customer responsibility.** "You are responsible for any check run on an asset you were not authorized to submit and will indemnify ChimeraShield for resulting claims (see Indemnities)."

*Why this matters:* unauthorized access or testing is a crime under the US **Computer Fraud and Abuse Act, 18 U.S.C. §1030** ([DOJ CFAA manual](https://www.justice.gov/jm/jm-9-48000-computer-fraud)) and, because we operate from Australia, under **Part 10.7 of the Commonwealth Criminal Code** (computer offences, e.g. s 478.1 unauthorised access to restricted data) ([Criminal Code Act 1995, Federal Register of Legislation](https://www.legislation.gov.au/C2004A04868/latest/text); **FLAG:** section numbers from memory, not fetched on 2026-09-26) plus state computer-crime laws. The contract doesn't protect us if we scan without verification. **Product controls come first; the clause backs them up.**

### A6. Pasted emails and personal data (draft clause)

"The phishing analyzer lets you submit emails. Emails may contain personal information of the sender, the recipient or other people. You confirm you may share that content with us for security analysis. We process submitted emails **in memory for analysis**, we **do not use them to train AI models**, and we **delete them within 30 days** unless you choose to save the result to your account. Saved results are encrypted at rest and visible only to your account. Please **redact** patient, client, tax file number or financial details that aren't needed to judge whether the email is malicious. Do not submit emails containing protected health information unless you have signed our Business Associate Agreement (see [link]), and never submit tax file numbers."

*Product must match the words:* auto-redaction hints in the UI (add a **TFN pattern**: 8–9 digits with the ATO check-digit algorithm), a 30-day purge job, no-training contract terms with the LLM provider, and a "save" toggle that is off by default. **Never promise in the ToS what the code doesn't do.**

### A8. No guarantee (draft clause)

"ChimeraShield helps you find and prioritize security issues. **No security product can find every vulnerability or stop every attack.** The Service, its findings and AI-generated recommendations are provided 'as is' and 'as available'. We do not warrant that the Service will detect all threats, that any email marked safe is safe, or that following our recommendations will prevent a breach or make you compliant with any law or standard (including HIPAA, the FTC Safeguards Rule, ABA rules, the Privacy Act 1988 (Cth), the TFN Rule or the Tax Agent Services Act 2009). You remain responsible for your own security program and compliance decisions. The Service is not legal or tax advice.

**Nothing in these Terms excludes, restricts or modifies any right or remedy, or any guarantee, warranty or other term or condition, implied or imposed by the Australian Consumer Law or any other law that cannot lawfully be excluded or limited.**"

This matches the brand rule "No security guarantees" in `.claude/skills/company-context/SKILL.md`. **Marketing copy must not contradict it** (no "fully protected", "HIPAA compliant in minutes", "TPB-approved", and so on).

### A9. Limitation of liability (draft clause)

"To the extent the law allows: (a) neither party is liable for indirect, incidental, special, consequential or punitive damages, or for lost profits, revenue, data or business, including losses from a security incident the Service did not detect; and (b) each party's total liability is capped at **the fees you paid in the 12 months before the claim**. The caps don't apply to your payment obligations, your indemnity for unauthorized scanning, or either party's fraud or wilful misconduct.

**(c) Australian Consumer Law.** If the ACL applies and our services are not of a kind ordinarily acquired for personal, domestic or household use, our liability for failing to comply with a consumer guarantee is limited, at our option, to supplying the services again or paying the cost of having them supplied again, unless it is not fair or reasonable for us to rely on this limitation."

**Why (c):** ACL **s 64A** lets a supplier limit remedies this way **only** for services not ordinarily for personal use, and only if reliance is fair and reasonable (S: [DW Fox Tucker, June 2024](https://www.dwfoxtucker.com.au/2024/06/when-are-goods-or-services-acquired-by-a-consumer-when-do-guarantees-under-the-australian-consumer-law-apply-can-suppliers-and-manufacturers-liability-be-limited); [FCW Lawyers](https://fcwlawyers.com.au/insights/perspectives/australian-consumer-law-more-b2b-goods-and-services-now-captured/)). Also note that consequential-loss exclusions may not remove liability for ACL guarantee breaches (S: [HWL Ebsworth](https://hwlebsworth.com.au/you-may-still-be-liable-for-consequential-loss-in-your-b2b-contract-heres-why/)).

**FLAG:** healthcare, legal and financial customers may push for a **higher separate cap for data-breach and confidentiality claims** (a "super-cap"). Decide the fallback with a lawyer and **match it to the PI/Tech E&O and cyber limits** (`australia-founder.md` §4). A **one-sided** cap (only our liability limited) is a UCT risk; keep it mutual.

### A15. Governing law and disputes: options for an Australian Pty Ltd selling to US and AU customers

| Option | How it works | For | Against |
|---|---|---|---|
| **1. `[STATE]` (Australia) law for everyone** | Laws of `[STATE]`, non-exclusive jurisdiction of its courts. Either party may seek urgent injunctive relief anywhere. | One set of terms and one lawyer. It's our home law. It matches the Spam Act, ACL and Privacy Act we already live under. | Some US buyers dislike foreign law. Enforcing an Australian judgment in the US is slow (there is no treaty; it depends on each state's recognition law, **FLAG**). May make it easier for US business buyers to claim ACL consumer guarantees (**FLAG**). |
| **2. Split by customer location** | AU customers: `[STATE]` law. US customers: a US state law (e.g. **New York** or **Delaware**) with that state's courts, or arbitration. | US buyers see familiar law. Easier US sales. | Two contracts to maintain. We'd need US counsel to review a US-law version. A US-law clause does **not** switch off the ACL where it would otherwise apply (**CCA s 67**, which overrides a foreign choice of law if Australian law would otherwise be the proper law, **FLAG**). |
| **3. `[STATE]` law plus arbitration for large claims** | Option 1, plus: disputes over `[A$50,000]` go to arbitration (e.g. ACICA rules, seat in Australia, online hearing). Smaller claims go to court. | Arbitral awards are enforceable in the US under the **New York Convention**, which is more reliable than court judgments. | Arbitration is costly and out of proportion for US$495 contracts. Set the threshold high. |

**Recommendation for discussion (not advice):** start with **Option 1** for the US$495 pack and Watch, with a short escalation step first (**negotiate for 20 business days, then mediation**, then court). Keep an **Option 2 US rider** ready if a US buyer's lawyer objects. Revisit at 10 US customers. **FLAG:** an Australian commercial lawyer (ideally with US experience) decides.

### A17. Australian Consumer Law and unfair contract terms

**A17.1 Consumer guarantees apply to many of our business customers and can't be excluded.**
- A business is a **"consumer"** under ACL s 3 if the services cost **A$100,000 or less** (threshold since 1 July 2021), or are of a kind ordinarily acquired for personal use (S: [FCW Lawyers](https://fcwlawyers.com.au/insights/perspectives/australian-consumer-law-more-b2b-goods-and-services-now-captured/); [DW Fox Tucker](https://www.dwfoxtucker.com.au/2024/06/when-are-goods-or-services-acquired-by-a-consumer-when-do-guarantees-under-the-australian-consumer-law-apply-can-suppliers-and-manufacturers-liability-be-limited)). **Every one of our offers is far below A$100k, so AU buyers are almost always "consumers".**
- The service guarantees are: **due care and skill** (s 60), **fit for any disclosed purpose** (s 61) and **supplied within a reasonable time** (s 62). A term that tries to exclude them is **void** (s 64), and saying customers have no such rights can itself be a **false or misleading representation** (s 29(1)(m)) (**FLAG** on section numbers).
- **What we can do:** limit remedies for business-type services to resupply or its cost (s 64A, clause A9(c)), and keep the "nothing excludes the ACL" sentence (A8).
- **US buyers:** whether the ACL guarantees reach a US customer depends on the governing law and conflict-of-laws rules (CCA s 5 and s 67). **FLAG** for the lawyer. Draft as if they might.

**A17.2 Unfair contract terms (UCT) in small-business standard-form contracts.**
- Since **9 November 2023**, **proposing, using or relying on** an unfair term in a standard-form **consumer or small-business** contract is **prohibited** and attracts penalties. A small business is a party that **employs fewer than 100 people or has turnover under A$10 million**, **whatever the contract value** (S: [ACCC, Contracts](https://www.accc.gov.au/business/selling-products-and-services/contracts); [ACCC media release](https://www.accc.gov.au/media-release/accc-welcomes-new-penalties-and-expansion-of-the-unfair-contract-terms-laws)).
- **Maximum penalty for a company:** the greatest of **A$50 million**, **3× the benefit** obtained, or **30% of adjusted turnover** during the breach period; **A$2.5 million** for an individual (S: ACCC, above).
- **Our click-through ToS, engagement letters and DPA are standard-form contracts, and every target customer (5–50 staff) is a small business.** Applies to contracts made, renewed or varied from 9 Nov 2023.
- **Terms to fix before any AU customer signs (and preferably for US too):**

| Clause | Risk | Fix |
|---|---|---|
| A7/A16 unilateral changes to price or terms | Classic unfair term | Notice (30 days) plus a right to cancel without penalty and a pro-rata refund of prepaid fees |
| A9 liability cap | One-sided caps are suspect | Mutual cap. Keep the s 64A clause |
| A10 customer indemnity | Broad one-way indemnity | Limit it to unauthorized submissions and the customer's breach. Our indemnity stays |
| A13 termination and suspension | Only we can terminate; no refund | Mutual termination for convenience on notice; refund unused prepaid fees if we end it without cause |
| Auto-renewal (Watch annual) | Renewal without notice | Remind 30 days before annual renewal, with an easy cancel |
| "We decide what counts as a breach" | Discretion only for us | Objective tests |

- **Defence:** a term reasonably necessary to protect our **legitimate interests** (e.g. immediate suspension for suspected unauthorized scanning) may survive. Record why each one-sided term is needed. **FLAG:** lawyer to review each term.

**A17.3 Refunds and "no refunds" wording.** Don't say "no refunds" or "refunds at our discretion only" to AU customers; it may misstate ACL rights. Use: "If we fail to meet a consumer guarantee, you have the rights the ACL gives you. Separately, we offer [voluntary policy]."

---

## Part B: Privacy Policy (for the website and product)

| # | Section | Contents |
|---|---|---|
| B1 | Who we are | **ChimeraShield Pty Ltd (ABN `[ABN]`)**, `[ADDRESS]`, `privacy@[DOMAIN]` |
| B2 | Our two roles | **Controller / APP-style collector** for account, billing, website and marketing data. **Processor / service provider** for content customers submit (domains, pasted emails, findings), governed by the DPA (Part C). |
| B3 | What we collect | Account data, billing data (handled by **Stripe**; we don't store card numbers), usage logs, submitted assets and findings, pasted emails, support messages, cookies and analytics (Google tag, LinkedIn Insight Tag if retargeting runs). **We do not ask for or want TFNs** (Part F). |
| B4 | Why and legal basis | Provide the service, security and fraud prevention, billing, support, product improvement **using aggregated or de-identified data only**, marketing only with consent (Spam Act) and with opt-out. GDPR legal bases only if EU/UK visitors are served. |
| B5 | AI processing | Which features use LLMs, that submitted content goes to named LLM providers under no-training and no-retention terms (**verify each provider's actual terms**), and that output is advisory only. **From 10 Dec 2026, APP entities must describe certain automated decisions** in their privacy policy (APP 1.7–1.9). Our AI outputs are advice to a business and probably not "decisions that significantly affect an individual's rights", but **say what the AI does** anyway (S: [Gilbert + Tobin](https://www.gtlaw.com.au/insights/automated-decision-making-transparency-under-the-privacy-act); [OAIC APP 1 guidelines](https://www.oaic.gov.au/privacy/australian-privacy-principles/australian-privacy-principles-guidelines/chapter-1-app-1-open-and-transparent-management-of-personal-information)). **FLAG.** |
| B6 | Sharing | Subprocessors (hosting, LLM, email, payments, analytics) with a public list, legal requests and business transfers. **We do not sell personal data** or "share" it in the CCPA sense. |
| B7 | Retention | Pasted emails: 30 days unless saved. Findings: for the life of the account plus 30 days. Billing: **5 years** (ATO record-keeping; accountant to confirm). Logs: `[N]` days. Any TFN received by mistake: **deleted as soon as found** (Part F). |
| B8 | Security | Encryption in transit and at rest, MFA, least privilege, logging. A **short** description; don't overpromise (APP 11 "reasonable steps"). |
| B9 | Where data is and who accesses it | Data stored in `[region]`. **ChimeraShield staff access data from Australia.** Name the **overseas countries** where subprocessors process data (e.g. the US for LLM and email providers). This is **APP 1.4(f)/(g)** content and, if we are an APP entity, triggers **APP 8** and the s 16C accountability rule for overseas recipients (**FLAG**). |
| B10 | Your rights | Access and correction (**APP 12, 13**), deletion, opt-out of marketing, complaints to us first, then to the **OAIC**. California and other US state rights as they apply. |
| B11 | Children | Not directed to children. |
| B12 | Changes and contact | Standard. |

### Privacy Act 1988 (Cth): are we covered, and should we opt in? (as of 2026-09-26)

- **Default position:** a business with **annual turnover of A$3M or less** is generally exempt (s 6D), unless an exception applies (health service provider, trading in personal information, Commonwealth contractor, **AML/CTF reporting entity**, and others). **TFN handling is regulated separately** (Part F). We are **probably exempt today** (`australia-founder.md` §2.1). **FLAG.**
- **Status of the exemption:** **still in place.** The 2026 exposure draft reportedly does not remove it (`australia-founder.md` §2.1). **Never claim in copy that it ends in December 2026** (company-context rule). The 10 Dec 2026 date is the **ADM transparency** rule for existing APP entities, not the end of the exemption.
- **Opting in (s 6EA):** a small business can apply to the OAIC to be treated as an organisation. After verification, its trading name and ABN go on the **public opt-in register**. Opt-in can later be revoked (S: [OAIC, Opting in to the Privacy Act](https://www.oaic.gov.au/privacy/privacy-guidance-for-organisations-and-government-agencies/organisations/opting-in-to-the-privacy-act); [OAIC opt-in register](https://www.oaic.gov.au/privacy/privacy-registers/privacy-opt-in-register)).

| Opt in now? | For | Against |
|---|---|---|
| **Yes** | A real trust signal for AU tax practices that are themselves covered (e.g. AML/CTF reporting entities from 1 July 2026, **FLAG** on scope). "We're on the OAIC opt-in register" is a **true, checkable** claim. Aligns us with the DPA. | OAIC jurisdiction, NDB duties and penalties (serious interference: greater of A$50M, 3× benefit or 30% of turnover, S). ADM rules from 10 Dec 2026. Work we'd mostly do anyway. |
| **Not yet** (current recommendation) | Keep flexibility during validation. Operate to APP standard by contract. | We can't honestly say "covered by the Privacy Act". |

**Recommendation for discussion:** operate to the APPs now. **Decide on opt-in before the first AU paid pilot signs (target 3 Nov)**, because AU buyers will ask. If a pilot customer's own obligations or its insurer require it, opt in.

**If we exceed A$3M turnover or opt in, we must (at minimum):**
| APP / scheme | What it means for us |
|---|---|
| APP 1 | Clearly expressed, up-to-date privacy policy (this Part B), practices and procedures to comply. **ADM disclosures from 10 Dec 2026** if they apply. |
| APP 3, 5 | Collect only what's reasonably necessary; collection notice at the form and in the analyzer. |
| APP 6 | Use or disclose only for the primary purpose or a permitted secondary purpose. |
| APP 7 | Direct-marketing rules (the Spam Act governs email and SMS). |
| APP 8 + s 16C | Reasonable steps before disclosing overseas (US LLM, email, hosting). We stay accountable for overseas recipients' breaches. |
| APP 10, 11 | Quality and **security**; destroy or de-identify data we no longer need. |
| APP 12, 13 | Access and correction on request, within set timeframes. |
| NDB scheme (Part IIIC) | Assess a suspected breach within **30 days**; notify the OAIC and affected individuals if it's an eligible breach. |

**Other privacy applicability (US):** **CCPA/CPRA** applies only above **US$26,625,000 revenue**, **100,000+ California consumers or households**, or 50%+ revenue from selling or sharing data ([CPPA](https://www.cppa.ca.gov/regulations/cpi_adjustment.html)); we're below all of these. Still write the policy CCPA-style. **GDPR** applies only if we target or monitor EU/UK residents ([GDPR Art. 3(2)](https://eur-lex.europa.eu/eli/reg/2016/679/oj)); don't market there yet.

---

## Part C: Data Processing Agreement (DPA) outline

Offer one standard DPA to every customer. US tax preparers **need** contract terms with us under the FTC Safeguards Rule, **16 CFR 314.4(f)** ([eCFR](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314/section-314.4)). AU practices that are APP entities need us to support their **APP 11** and **NDB** obligations, and all tax agents have a confidentiality duty under the TPB Code (TASA 2009 s 30-10) (**FLAG** on item numbers).

| # | Section | Contents |
|---|---|---|
| C1 | Roles and scope | Customer is controller/business/APP entity; ChimeraShield is processor/service provider. Scope: submitted assets, pasted emails, findings. **TFNs out of scope** (Part F). |
| C2 | Instructions | We process only to provide the service and follow the customer's documented instructions. **No training on customer data. No selling.** |
| C3 | Confidentiality | Staff with access are under confidentiality obligations. Least privilege. |
| C4 | Security measures (annex) | Encryption at rest and in transit, MFA, logging, backups, vulnerability management, access reviews, incident response. **Only list measures that actually exist.** |
| C5 | Subprocessors | Public list with **countries**, 30 days' notice of changes, and the customer's right to object (and to terminate with a pro-rata refund, for UCT balance). |
| C6 | Breach notification | We notify the customer **without undue delay, target within 72 hours** of confirming a breach affecting their data, with the details they need. This supports the **FTC 30-day notice** for US preparers ([FTC, May 2024](https://www.ftc.gov/business-guidance/blog/2024/05/safeguards-rule-notification-requirement-now-effect)) and the **30-day NDB assessment** for AU APP entities. |
| C7 | Assistance | Help with access and correction requests, risk assessments and audits (questionnaire first). |
| C8 | Deletion and return | Pasted emails within 30 days. All customer data within 30 days of termination. Certificate of deletion on request. |
| C9 | International transfers | **Staff access from Australia**; subprocessors in `[countries]`. For AU customers, describe the APP 8 steps we take. SCCs/UK addendum only if EU/UK data is ever processed. |
| C10 | CCPA service-provider terms | Statutory restrictions (US customers). |
| C11 | Order of precedence | DPA over ToS for data matters; BAA over both for PHI. |

---

## Part D: When a HIPAA Business Associate Agreement becomes necessary (US healthcare, later)

**Rule:** a **business associate** creates, receives, maintains or transmits PHI on behalf of a covered entity ([45 CFR 160.103](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-160/subpart-A/section-160.103)). The covered entity needs a contract meeting **45 CFR 164.504(e)** ([HHS FAQ](https://www.hhs.gov/hipaa/for-professionals/faq/business-associates/index.html)). A cloud provider holding ePHI is a business associate **even if it can't view the data** ([HHS cloud guidance](https://www.hhs.gov/hipaa/for-professionals/special-topics/health-information-technology/cloud-computing/index.html)). HIPAA applies to us as a foreign vendor if we handle US PHI.

| ChimeraShield activity for a clinic | Touches PHI? | BAA needed? |
|---|---|---|
| Passive DNS / SPF / DKIM / DMARC scan | No, public records | **Probably no** |
| Owner and office-manager account info, billing | No | No |
| Clinic pastes a suspicious email that **mentions a patient** | **Yes, likely PHI** | **Yes, if allowed** |
| Future: reading the clinic's mailbox or logs | Yes | **Yes** |

**Recommended stance:** (1) MVP: the ToS and UI **prohibit PHI**, with a paste-box warning and PHI-pattern detection (**FLAG:** accidental receipt handling). (2) Before selling to a clinic that will paste real emails: downstream BAAs with every subprocessor, HIPAA-eligible services only, our own Security Rule risk analysis. (3) **Don't claim "HIPAA compliant".** (4) Watch the Security Rule NPRM (final rule not expected before July 2027, [HHS](https://www.hhs.gov/hipaa/for-professionals/security/hipaa-security-rule-nprm/factsheet/index.html)). **AU health customers (later):** the Privacy Act applies to health service providers **regardless of size**; separate review needed.

---

## Part E: US P1 "Safeguards-Ready WISP & Evidence Pack" (first paid offer, US only)

Source spec: `docs/company/product/prd-wisp-evidence-pack.md`. Market: US CPA and tax-prep firms. **Never reuse this Part's wording ("WISP", "Safeguards-Ready") in Australia** (company-context rule); use Part G.

### E1. Regulatory check: the FTC Safeguards Rule small-firm exception (16 CFR 314.6)

**Verified text (2026-09-24, from search snippets of eCFR; re-read [eCFR §314.6](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314/section-314.6) before the first sale):**
> "Section 314.4(b)(1), (d)(2), (h), and (i) do not apply to financial institutions that maintain customer information concerning fewer than five thousand consumers."

| Element | Under 5,000 consumers | Note |
|---|---|---|
| §314.3(a): **written** information security program | **Still required** | This is the WISP. |
| §314.4(a): Qualified Individual | Still required | |
| §314.4(b): risk assessment | **Still required**, but not the formal written criteria in **(b)(1)** | Record risks briefly in the WISP. |
| §314.4(c): safeguards (access controls, inventory, **encryption**, **MFA**, disposal, change management, logging) | Still required | |
| §314.4(d)(1): regularly test or monitor | Still required | |
| §314.4(d)(2): continuous monitoring **or** pen testing and vulnerability assessments | **Exempt** | |
| §314.4(e): training and qualified personnel | Still required | |
| §314.4(f): service-provider oversight | Still required | Applies to us if we access customer information (E3.6). |
| §314.4(g): evaluate and adjust | Still required | |
| §314.4(h): **written** incident response plan | **Exempt** | Still recommended. |
| §314.4(i): annual report to the board | **Exempt** | |
| §314.4(j): notify the FTC within 30 days (500+ consumers) | **Still required** | [FTC, May 2024](https://www.ftc.gov/business-guidance/blog/2024/05/safeguards-rule-notification-requirement-now-effect) |

**FLAG, needs a lawyer: how to count "fewer than five thousand consumers."** It counts consumers whose information the firm **maintains** (including past years, spouses and dependents), not this year's clients. **My inference, not verified.** Intake asks for "individuals whose records you keep, including past years" and must **never** tell a firm it is exempt.

**Pitch rules:** don't sell fear of pen tests or board reports; say "even the smallest firm must have a written program…"; sell "right-sized"; never state a firm's exemption status as fact.

### E2. Disclaimer wording for the US pack

**Short form (footer of every page):**
> Prepared with [FIRM NAME] from information the firm provided and passive public checks run on [DATE]. Not legal advice and not a compliance certification or audit. [FIRM NAME] remains responsible for its information security program and for its IRS Form W-12 / PTIN attestation. ChimeraShield Pty Ltd (ABN [ABN]) is not affiliated with the IRS or the FTC.

**Long form (cover page and engagement letter):**
> **About this document.** ChimeraShield helped [FIRM NAME] prepare this written information security plan (WISP), Evidence Report and Fix-First plan, based on information the firm gave us during intake, screenshots and screen-shares the firm chose to show us, and passive checks of public records for [DOMAIN] on [DATE].
>
> **What this is not.** This is **not legal, tax or insurance advice**. It is **not an audit, certification, attestation or guarantee** that [FIRM NAME] complies with the FTC Safeguards Rule (16 CFR Part 314), IRS requirements, state law or any other standard, and ChimeraShield is not a law firm or a CPA firm. Controls marked **"Owner-stated"** were reported by the firm and not checked by us. Controls marked **"Verified"** were observed only on the date shown. No review can find every weakness or prevent every incident.
>
> **The firm's responsibility.** [FIRM NAME] and its Qualified Individual, [NAME], decide what the firm's security program contains and are responsible for adopting it, keeping it current, and answering truthfully on **IRS Form W-12 (including line 11)**, to insurers, clients and regulators. Whether the small-firm exception in 16 CFR 314.6 applies depends on the firm's own count of consumers, which the firm confirmed as [BAND] on [DATE]. For legal questions, consult a qualified attorney.

**Wording rules:** never "compliant", "certified", "passes", "approved" or "guaranteed". **FLAG:** "Safeguards-Ready" may imply certification (FTC Act §5 and, because we're an Australian company, possibly ACL s 18/s 29). Safer fallback: "Safeguards WISP & Evidence Pack".

### E3. Engagement terms outline for the US one-time pack

| # | Section | Contents |
|---|---|---|
| E3.1 | Parties and authority | **ChimeraShield Pty Ltd (ABN `[ABN]`)** and the firm. Signer confirms authority. |
| E3.2 | Scope | 60-min intake, passive checks on **one** domain, WISP, one-page Evidence Report, Fix-First top 5, 30-min debrief. Delivery within **7 business days** of the intake **and** receipt of intake facts. One round of factual corrections within 14 days. |
| E3.3 | Out of scope | Legal, tax or insurance advice. Acting as Qualified Individual. Any active testing. Logging into the firm's systems. Fixing gaps. Filling in insurer/regulator forms. Incident response. Anything about taxpayer data. |
| E3.4 | Firm responsibilities | Accurate facts; confirm consumer-count band in writing; name the QI; review, adopt and sign the WISP; keep it current. |
| E3.5 | Authorization to check | Consent text (PRD §7, clause A4.1), **passive tier only**, recorded with name, email and UTC timestamp **before** any check. |
| E3.6 | **No taxpayer data** | The firm must not share taxpayer information, including during screen-shares (we stop the session if it appears). **FLAG:** accidental exposure may make us a §314.4(f) service provider; DPA fallback. |
| E3.7 | Confidentiality and data | Encrypted at rest; named contacts only; retained 12 months unless the firm asks for earlier deletion. No AI training. Human review before delivery. **Staff access from Australia** (disclose). |
| E3.8 | Fees and payment | One-time fee in **USD** `[$495 founding / $795 list]`, paid upfront through **Stripe (Australian account)**. GST-free export treatment (accountant to confirm). **Refund:** full refund before intake; after delivery, refund if we miss the 7-business-day delivery. Plus any ACL rights that apply (A17.3). Optional Watch credit (pricing.md). |
| E3.9 | Ownership and licence | Firm owns its completed WISP and reports; may share them **with the disclaimer intact**. We keep templates and know-how. |
| E3.10 | Disclaimer | E2 long form, plus the A8 ACL savings sentence. |
| E3.11 | Limitation of liability | Capped at **the fee paid**, mutual. No indirect or consequential damages. Carve-outs for fraud, wilful misconduct and confidentiality breach. **A9(c) s 64A clause.** **FLAG:** enforceability in the US and match to PI with **US/Canada jurisdiction** (`australia-founder.md` §4). **Bind PI before the first pack is sold.** |
| E3.12 | Reliance | For the firm's own use. No third-party reliance. |
| E3.13 | Term and termination | Ends on delivery plus the correction window. Either party may cancel before intake. |
| E3.14 | Governing law | Per A15 (recommended: Option 1 with a US rider on request). |

**Entity timing (replaces the earlier Nepal/US-entity conflict note):** the PRD wants a **live Stripe link by 8 Oct 2026**. Path: register the **Pty Ltd by ~2 Oct**, then ABN, bank account and Stripe Australia (`australia-founder.md`, `launch-checklist.md`). **Fallback if the company isn't ready:** sell as a **sole trader under the founder's own ABN** and assign contracts to the Pty Ltd later (**FLAG:** accountant on the transfer and lawyer on assignment), or delay paid sales and keep running the free check.

---

## Part F: Tax file numbers (TFNs), if AU tax agents share any

**Short version: we must not request, record, use or disclose TFNs. Our products are designed so we never need one.**

- **Law.** The **Privacy (Tax File Number) Rule 2015** (made under Privacy Act s 17) regulates collection, storage, use, disclosure, security and disposal of **individuals'** TFN information. It binds **TFN recipients regardless of the small-business exemption** (**FLAG** on the exact mechanism). **Taxation Administration Act 1953 ss 8WA and 8WB** make it an **offence** to request, record, use or disclose a TFN except as permitted (S: [OAIC, TFN Rule guidance](https://www.oaic.gov.au/privacy/privacy-guidance-for-organisations-and-government-agencies/handling-personal-information/the-privacy-tax-file-number-rule-2015-and-the-protection-of-tax-file-number-information); [OAIC, Tax file numbers](https://www.oaic.gov.au/privacy/privacy-legislation/the-privacy-act/tax-file-numbers); [TFN Rule on ato.gov.au](https://www.ato.gov.au/law/view/pdf/ldt/tfn2015-001.pdf)). We are **not** a lawful TFN recipient class for our purposes ([OAIC classes register](https://www.oaic.gov.au/privacy/privacy-registers/classes-of-lawful-tax-file-number-recipients)).
- **The tax agent's side.** Sharing client information with us would also need the client's permission under the **TPB Code confidentiality obligation** (TASA 2009 s 30-10) (**FLAG** on item number). So the "no client data" rule protects the practice as well as us.

**Controls (contract plus product):**
1. **Contract:** A5, A14, G3.6: the customer must not submit TFNs or client tax data.
2. **Intake:** questions ask **how** the practice handles TFNs (where stored, who can see them, how they're sent and destroyed), **never for any TFN**. Our Evidence Report records the process, not the data.
3. **Screen-shares:** the practice closes client files first. If a TFN or client record appears, we **stop the share, don't screenshot, and note the event**.
4. **Product:** TFN-pattern detection in the phishing analyzer and upload paths, with a block-and-redact prompt.
5. **If a TFN reaches us anyway:** do not use it; **securely delete** it (including from LLM logs, email and backups where feasible); tell the customer in writing the same business day; keep an incident log entry **without** the TFN. Assess with the lawyer whether the TFN Rule's breach and NDB provisions apply (**FLAG**), and help the practice with its own NDB and TPB assessments.
6. **Never** route TFNs to an LLM or any US subprocessor.

---

## Part G: AU "Client Data Security Pack (TPB & TFN ready)": disclaimer and engagement variant

For the **1–2 paid AU pilots, 3 Nov to 11 Dec 2026** (`australia-vs-us.md` §6–7). Working price **A$750 founding** (finance to confirm). Deliverables: an **information security policy**, a **data breach response plan**, a one-page **Evidence Report** in Essential Eight ML1 order ("snapshot", not an assessment), and a **Fix-First 5**.

### G1. Name check (FLAG before first use)
"**TPB & TFN ready**" could be read as TPB or ATO approval. That risks ACL **s 29(1)(g)/(h)** (false representations about sponsorship, approval or affiliation) and s 18 (**FLAG**). Use it only with the disclaimer on the same page and never with TPB/ATO logos. The safer alternative is "**Practice Security Policy & Evidence Pack**". **Banned in AU copy:** "WISP", "certified", "compliant", "TPB-approved", "ATO-endorsed", "Essential Eight compliant", "Essential Eight assessment", and any claim that the small-business exemption ends in Dec 2026.

### G2. Disclaimer wording (draft for lawyer review)

**Short form (footer of every page):**
> Prepared with [PRACTICE NAME] from information the practice provided and passive public checks run on [DATE]. General information only. Not legal or tax advice, not an audit or certification, and not endorsed by the Tax Practitioners Board or the ATO. [PRACTICE NAME] remains responsible for meeting its own obligations. ChimeraShield Pty Ltd, ABN [ABN].

**Long form (cover page and engagement terms):**
> **About this document.** ChimeraShield Pty Ltd (ABN [ABN]) helped [PRACTICE NAME] prepare this information security policy, data breach response plan, Evidence Report and Fix-First plan. We based them on information the practice gave us during intake, settings the practice chose to show us on screen-share, and passive checks of public records for [DOMAIN] on [DATE]. We did not see or collect any client records or tax file numbers.
>
> **What this is not.** This is **general information, not legal advice, tax advice or a tax agent service**. It is **not an audit, certification, attestation or guarantee** that [PRACTICE NAME] meets the Tax Agent Services Act 2009, the Code of Professional Conduct, the Privacy Act 1988, the Privacy (Tax File Number) Rule 2015, ATO security requirements, the Essential Eight or any other standard. "TPB & TFN ready" is a product name. **It does not mean the Tax Practitioners Board or the ATO has reviewed, approved or endorsed this document or ChimeraShield**, and we are not affiliated with either. The Essential Eight section is a snapshot of selected controls, not an Essential Eight assessment. Items marked **"Owner-stated"** were reported by the practice and not checked by us. Items marked **"Verified"** were observed only on the date shown. No review can find every weakness or prevent every incident.
>
> **The practice's responsibility.** [PRACTICE NAME] and its responsible person, [NAME], decide what the practice's security arrangements contain. They are responsible for adopting and following them, keeping them current, deciding whether a data breach is notifiable, and meeting the practice's obligations to its clients, the TPB, the ATO, the OAIC and its insurers. For legal or tax questions, consult a qualified lawyer or registered tax adviser.
>
> **Your consumer rights.** Nothing in this document or our terms excludes, restricts or modifies any right or remedy you have under the Australian Consumer Law.

### G3. Engagement terms: AU variant (differences from E3)

| # | Section | AU content |
|---|---|---|
| G3.1 | Parties | ChimeraShield Pty Ltd (ABN `[ABN]`) and `[PRACTICE NAME]` (ABN `[CLIENT_ABN]`). Signer confirms authority. |
| G3.2 | Scope | Intake call (60 min, in person or video), passive checks on **one** domain, the four deliverables in Part G, and a 30-min debrief. Delivery within `[7]` business days of the intake and receipt of intake facts. **Pilot:** the practice agrees to a 20-minute feedback call. Testimonial use is a **separate, optional** consent and is never a condition of the price. |
| G3.3 | Out of scope | Legal or tax advice. Tax agent services. Acting as the practice's privacy officer or responsible person. Deciding or lodging any **NDB notification**, ATO report or TPB breach report. A formal Essential Eight assessment. Active testing, logging into systems, fixing gaps, incident response. **Any client data or TFNs.** |
| G3.4 | Practice responsibilities | Accurate facts; name a responsible person; review, adopt and sign the policy and response plan; decide which fixes to do; keep them current; **don't share client data or TFNs** (Part F). |
| G3.5 | Authorization to check | Same as E3.5 (passive tier, recorded consent with timestamp). |
| G3.6 | **No client data or TFNs** | Part F controls, incorporated. Screen-shares stop if client data appears. |
| G3.7 | Privacy and data | We handle practice contacts' information to APP standard (Part B), store notes encrypted, retain 12 months unless deletion is requested, and notify the practice within 72 hours of confirming a breach affecting its data. State whether we are on the OAIC opt-in register (Part B decision). |
| G3.8 | Fees, GST, refunds | **A$`[750]` + GST** (or GST-inclusive, **FLAG:** display rules for AU prices). Tax invoice once GST-registered (`australia-founder.md` §1.4; GST registration is compulsory at A$75k turnover, **FLAG**). **Refunds:** full refund before intake; if we miss the delivery date, the practice may cancel for a full refund; plus ACL rights (A17.3). **No "no refunds" wording.** |
| G3.9 | Ownership | Practice owns its completed documents and may share them with the disclaimer intact. |
| G3.10 | Disclaimer | G2 long form, in full. |
| G3.11 | Liability | Mutual cap at the fee paid; **A9(c) s 64A resupply clause**; ACL savings sentence; carve-outs as E3.11. PI must cover **Australian** claims (standard) as well as US. |
| G3.12 | UCT-safe terms | No unilateral variation; mutual termination before intake; objective breach tests; narrow indemnity (A17.2). |
| G3.13 | Governing law and disputes | Laws of `[STATE]`. Negotiation for 20 business days, then mediation, then courts of `[STATE]`. |

---

## Needs a real lawyer
- **Australian commercial lawyer:** governing-law option (A15) and the CCA s 5/s 67 questions; UCT review of every standard-form term (A17.2); ACL wording and the s 64A clause; the "TPB & TFN ready" name (G1) and the G2/G3 disclaimer and engagement terms; "Safeguards-Ready" under ACL s 18/s 29.
- **Australian privacy lawyer:** s 6EA opt-in decision before 3 Nov; APP 8 cross-border wording; ADM disclosures from 10 Dec 2026; TFN Rule coverage and accidental-receipt procedure (Part F).
- **US lawyer (FTC/GLBA):** re-verify §314.6, the consumer-counting rule, E2/E3, and unauthorized-practice-of-law risk in WISP drafting (**FLAG**, not researched); the US-law rider if Option 2 is used.
- Enforceability of disclaimers and caps in both countries, matched to PI with US/Canada jurisdiction.
- Handling of accidental PHI (Part D) and the Criminal Code Part 10.7 / CFAA view of light active checks.
