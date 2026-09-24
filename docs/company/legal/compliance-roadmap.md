# Compliance roadmap: what we need at 0, 10 and 100 customers

> **Draft for discussion. Not legal advice. Review with a qualified lawyer in your jurisdiction.**

**As of:** 2026-09-24 · **Owner:** legal-ops agent · **First market:** US CPA and tax-prep firms (P1 WISP & Evidence Pack, then Watch). Dental (HIPAA) and law firms come later.

**The principle:** we sell security evidence to regulated firms, so **our own house must pass the checklist we hand to customers.** Every item below is something a tax preparer's §314.4(f) vendor review, a clinic's BAA review or an insurer's questionnaire will eventually ask us about.

---

## Stage 0: before the first paying customer (now to about 15 Oct 2026)

### Legal and contracts
- [ ] Entity, bank and payments per `launch-checklist.md`. **The founder's country decides the path. This blocks everything else.**
- [ ] ToS, privacy policy and the P1 engagement letter with the disclaimer (`terms-outline.md` Parts A, B, E) reviewed by a lawyer.
- [ ] **Tech E&O plus cyber insurance bound** before the first pack is delivered.
- [ ] Scanning consent capture (text plus timestamp) live **before** any customer domain is checked (authorized-scanning skill; PRD AC2).
- [ ] Re-verify **16 CFR 314.6** on eCFR and agree the consumer-counting rule with the lawyer (`terms-outline.md` E1).

### Our own security basics (free or cheap; these are also the baseline in CISA Cyber Essentials: [CISA](https://www.cisa.gov/resources-tools/resources/cyber-essentials))
- [ ] **Phishing-resistant MFA** (passkeys or hardware keys) on email, registrar, DNS, cloud, GitHub, Stripe and the password manager.
- [ ] A **password manager** for every secret. No secrets in the repo. Rotate any key that was ever hardcoded.
- [ ] **Full-disk encryption** and auto-updates on the founder's laptop. A separate browser profile for admin work.
- [ ] Our own domain passes our own check: **SPF, DKIM, DMARC** (moving to quarantine/reject), TLS, security headers.
- [ ] **Findings and consent store:** encrypted at rest, access limited to the account, audit log of consent before checks (catalog §7 item 3).
- [ ] **Phishing analyzer hardening** before any customer uses it: in-memory processing, **30-day deletion**, no-training terms confirmed with the LLM provider in writing, delimited untrusted input, auth (catalog §7 item 4).
- [ ] **Backups** of the findings store and document templates, with a test restore once.
- [ ] `security@[DOMAIN]` plus a `security.txt` file ([RFC 9116](https://www.rfc-editor.org/rfc/rfc9116)) so researchers can report bugs.
- [ ] A one-page **incident response plan for ChimeraShield itself**: who decides, who notifies customers (the DPA target is 72 hours), plus our insurer's hotline number.
- [ ] A one-page **data inventory**: what we hold, where it lives, how long we keep it, and which subprocessors touch it. This becomes the subprocessor list.

### Rules we apply to ourselves
- **FTC Act §5.** Our marketing and privacy claims must be true. Never say "compliant", "certified", "SOC 2", "HIPAA compliant" or "bank-grade" unless it's true and documented (company-context hard rules).
- **CAN-SPAM** for outreach: honest sender, postal address, opt-out honored within 10 business days ([FTC guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)).
- **No PHI, no taxpayer data** in any intake, screen-share or pasted email until the matching agreement exists (`terms-outline.md` D and E3.6).

---

## Stage 10: about 10 customers (roughly Dec 2026 to spring 2027)

### Contracts
- [ ] A standard **DPA** (Part C) offered to every customer. Expect tax preparers' §314.4(f) vendor questions ([eCFR 314.4](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314/section-314.4)).
- [ ] A public **subprocessor list** and a **security page** (what we do, without overclaiming).
- [ ] A **standard security questionnaire answer set** (a short SIG-Lite / CAIQ-style document) so the founder doesn't rewrite answers each time.

### Security program ("eat our own cooking")
- [ ] Write **ChimeraShield's own WISP-style security policy set**: access control, acceptable use, incident response, vendor management, data retention, change management. Use NIST CSF 2.0 as the frame ([NIST CSF](https://www.nist.gov/cyberframework)).
- [ ] **Quarterly access review.** Offboarding checklist for any contractor.
- [ ] **Contractor paperwork:** NDA plus IP assignment plus a security addendum for anyone who touches code or customer data. **Nepal-based team:** also check the Nepal Privacy Act 2075 duties ([ADB summary](https://lpr.adb.org/resource/privacy-act-2075-2018-nepal)) and disclose cross-border access in the privacy policy.
- [ ] **Logging and alerting** on production (auth events, admin actions, data export).
- [ ] **Dependency and secret scanning** in CI.
- [ ] Our own **annual risk assessment**, written (we'd be a hypocrite without one).

### Segment triggers
- [ ] **Before the first dental or medical sale (D4):** design the intake so **no PHI** is collected. Only after BAAs are signed with every subprocessor that could touch PHI (cloud, LLM, email) and our own HIPAA Security Rule risk analysis is written may we accept PHI and sign customer BAAs (`terms-outline.md` Part D; [HHS business associates](https://www.hhs.gov/hipaa/for-professionals/faq/business-associates/index.html)).
- [ ] **Before the first law-firm sale:** a confidentiality addendum. Expect ABA 477R/512-style questions about AI tools and client data.

### SOC 2: not yet
- **Don't pay for a SOC 2 audit at 10 SMB customers.** Small CPA, dental and law firms rarely ask for one, and a first-year Type 1 or Type 2 is commonly quoted at **$15k–$80k all-in** (3P: [Vanta](https://www.vanta.com/collection/soc-2/soc-2-for-startups), [Thoropass](https://www.thoropass.com/blog/soc-2-audit-cost-a-guide)). SOC 2 is an AICPA attestation framework and can only be issued by a licensed CPA firm.
- **Do** build the policies and evidence above in a SOC 2-shaped way, so the later audit is cheap.

---

## Stage 100: about 100 customers (late 2027+)

### SOC 2 decision point
Start a **SOC 2 Type 2** (a 3–12 month observation window, audited by a CPA firm) when **any** of these happens:
1. **MSP partners** (the $149 tier) or larger firms ask for it in writing.
2. We add **S4 (read-only M365/Workspace OAuth access)** or the **A2 forwarding helpdesk** at scale. Holding mailbox access or large volumes of forwarded email moves us into "critical vendor" territory.
3. Lost or stalled deals attributable to "no SOC 2" reach roughly 2–3 per quarter.
4. Fundraising diligence asks for it.

Consider a compliance-automation tool (Vanta, Drata, Secureframe, etc.) about 3 months before the audit window. Budget for it in the finance model.

### Privacy law
- **CCPA/CPRA** applies above **$26,625,000 revenue**, **100,000+ California consumers or households**, or 50%+ revenue from selling or sharing data ([CPPA](https://www.cppa.ca.gov/regulations/cpi_adjustment.html)). At 100 SMB customers we are almost certainly below all of these, but **verify annually**. Other state laws have different thresholds (**FLAG:** a state-by-state check by a lawyer at this stage).
- **GDPR/UK GDPR** only if we target or monitor EU/UK residents ([GDPR Art. 3(2)](https://eur-lex.europa.eu/eli/reg/2016/679/oj)). If we do: SCCs in the DPA and an Art. 27 representative.
- **Nepal:** if we sell to Nepali or South Asian SMBs, check the Privacy Act 2075 and any newer data-protection bill (**FLAG:** not researched).

### HIPAA at scale (if dental or medical becomes segment #2)
- A signed BAA template, downstream BAAs, an annual HIPAA risk analysis, workforce HIPAA training, breach-notification procedures (a business associate notifies the covered entity without unreasonable delay and no later than 60 days after discovery, under 45 CFR 164.410; the customer BAA may set a shorter deadline, so the lawyer should confirm), and a watch on the **Security Rule NPRM**, whose final rule is not expected before July 2027 ([HHS NPRM fact sheet](https://www.hhs.gov/hipaa/for-professionals/security/hipaa-security-rule-nprm/factsheet/index.html)).

### Company hygiene
- [ ] Revisit **insurance limits** (Tech E&O and cyber) against customer contracts and liability caps.
- [ ] **Annual penetration test** of our own app by a third party (customers will ask).
- [ ] SaaS **sales-tax nexus** review across states (Stripe Tax data plus a CPA).
- [ ] Trademark registered (launch checklist 8) and monitored.
- [ ] Board or advisor reporting on security, if we've raised money.

---

## What needs a real lawyer or professional

| Item | Who | When |
|---|---|---|
| Entity path, especially **Nepal outward-investment clearance** and cross-border tax | Nepali corporate/FX lawyer plus a cross-border CPA | **Now**, before forming anything |
| ToS, privacy policy, DPA, P1 engagement letter and disclaimer, liability caps | US tech/SaaS lawyer | Before the first sale |
| §314.6 consumer-counting rule; whether "Safeguards-Ready" is a misleading claim; unauthorized practice of law when drafting WISPs | US lawyer with FTC/GLBA experience | Before the first sale |
| Tech E&O and cyber insurance | Insurance broker | Before the first sale |
| Trademark clearance for "ChimeraShield" | Trademark attorney | Before spending on the brand |
| BAA and HIPAA program | Healthcare privacy lawyer | Before the first clinic that could send PHI |
| SOC 2 | CPA audit firm | At the Stage 100 triggers |
