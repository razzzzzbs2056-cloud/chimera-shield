# Compliance roadmap: what we need at 0, 10 and 100 customers

> **Draft for discussion. Not legal advice. Review with a qualified lawyer in your jurisdiction.**

**As of:** 2026-09-26 · **Owner:** legal-ops agent
**Company:** ChimeraShield Pty Ltd (to be registered by ~2 Oct 2026), founder in Australia.
**Markets:** **Sell** to US CPA and tax-prep firms (P1 pack, then Watch), mid-Oct to 15 Dec. **Pilot** with 1–2 Australian tax/accounting practices, 3 Nov to 11 Dec ("Client Data Security Pack"). US dental (HIPAA) and law firms come later. Primary market decided 15 Feb 2027.
**Changed on 2026-09-26:** removed the Nepal-entity, Nepal Privacy Act and US-entity (Atlas) paths. Added Australian law (Spam Act, ACL, unfair contract terms, Privacy Act, TFN Rule) and a marketing-copy review (§5). Details: `terms-outline.md`, `australia-founder.md`, `spam-act-cold-email.md`.

**Evidence note.** Australian government sites were blocked by the proxy; Australian facts are from search summaries accessed 2026-09-26 (**S**). **FLAG** = lawyer to confirm.

**The principle:** we sell security evidence to regulated firms, so **our own house must pass the checklist we hand to customers.**

---

## 1. Stage 0: before the first paying customer (now to about 15 Oct 2026)

### Legal and contracts
- [ ] **Pty Ltd, ABN, bank, Stripe Australia** per `launch-checklist.md` and `australia-founder.md`. Fallback: sole trader under the founder's ABN (`terms-outline.md` E3, entity timing).
- [ ] ToS, privacy policy and the US engagement letter with disclaimer (`terms-outline.md` Parts A, B, E) reviewed by an **Australian commercial lawyer**, including the **governing-law choice (A15)** and **UCT fixes (A17.2)**. The US lawyer reviews the FTC-specific parts.
- [ ] **PI / Tech E&O with US/Canada jurisdiction, plus cyber, bound** before the first pack is delivered (`australia-founder.md` §4).
- [ ] Scanning consent capture (text plus timestamp) live **before** any customer domain is checked.
- [ ] Re-verify **16 CFR 314.6** and agree the consumer-counting rule (`terms-outline.md` E1).
- [ ] **Marketing edits in §5 below** done before the landing pages and ads go live (15 Oct).

### Our own security basics (CISA Cyber Essentials / ACSC Essential Eight ML1 as the baseline)
- [ ] **Phishing-resistant MFA** on email, registrar, DNS, cloud, GitHub, Stripe and the password manager.
- [ ] Password manager for every secret. No secrets in the repo.
- [ ] Full-disk encryption and auto-updates on the founder's laptop. Separate admin browser profile.
- [ ] Our own domain passes our own check: SPF, DKIM, DMARC, TLS, security headers.
- [ ] Encrypted findings and consent store with an audit log.
- [ ] Phishing analyzer hardening: in-memory processing, 30-day deletion, written no-training terms, **TFN and PHI pattern detection**.
- [ ] Backups with one test restore.
- [ ] `security@[DOMAIN]` and `security.txt` ([RFC 9116](https://www.rfc-editor.org/rfc/rfc9116)).
- [ ] One-page **incident response plan** built to **NDB standard** (assess within 30 days; customer notice target 72 hours) even while exempt.
- [ ] One-page **data inventory** with the **country** of each subprocessor (feeds APP 8 wording).

### Rules we apply to ourselves
- **Truthful marketing, in both countries.** **FTC Act §5** for US claims, and the **ACL** (s 18 misleading or deceptive conduct, s 29 false representations) for claims by an Australian company, possibly including claims aimed at US buyers (CCA s 5; **FLAG**). Never say "compliant", "certified", "SOC 2", "HIPAA compliant", "bank-grade", "TPB-approved" or "ATO-endorsed". Future promises (delivery times) need reasonable grounds (ACL s 4).
- **Spam Act 2003 plus CAN-SPAM** for every commercial email and DM, including to US recipients: consent (express or conspicuous publication) evidenced per address, **entity name and ABN**, a working unsubscribe honoured within **5 business days** (our standard: same day), no harvested lists (`spam-act-cold-email.md`). CAN-SPAM adds the postal address ([FTC guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)).
- **Privacy Act:** operate to the APPs now even if exempt (`terms-outline.md` Part B).
- **No PHI, no taxpayer data and no TFNs** in any intake, screen-share or pasted email (`terms-outline.md` D, E3.6, Part F).

### AU pilot gate (before the first AU paid pilot, target 3 Nov 2026)
- [ ] **Decide the s 6EA opt-in** with the privacy lawyer (`terms-outline.md` Part B). Default: operate to APPs, don't opt in, unless a pilot customer or its insurer requires it.
- [ ] **TFN controls live** (`terms-outline.md` Part F): intake asks about process only; stop-the-share rule; accidental-receipt procedure written.
- [ ] **AU engagement terms and disclaimer** (Part G) reviewed: UCT-safe, ACL savings sentence, s 64A clause, "not TPB or ATO endorsed", no "no refunds".
- [ ] **Product name decision:** "Client Data Security Pack (TPB & TFN ready)" vs. "Practice Security Policy & Evidence Pack" (G1, ACL s 29(1)(g)/(h) risk).
- [ ] **GST:** decide on voluntary registration with the accountant; A$ prices shown clearly as GST-inclusive or "+ GST" (**FLAG**).
- [ ] **PI covers Australian claims** and the "tax/accounting security consulting" occupation description.
- [ ] Separate **AU copy** only. None of the US ad or landing copy is reused in Australia (no "WISP", "Safeguards", "compliant", "certified"; no claim the small-business exemption ends in Dec 2026).
- [ ] AU prospecting follows the Spam Act conspicuous-publication tests (`spam-act-cold-email.md` §9). No AU paid ads in 2026.

---

## 2. Stage 10: about 10 customers (roughly Dec 2026 to spring 2027)

### Contracts
- [ ] Standard **DPA** (Part C) for every customer, with the AU APP 8 and NDB wording and US §314.4(f) terms.
- [ ] Public **subprocessor list (with countries)** and a **security page** without overclaiming.
- [ ] A short **security questionnaire answer set**.
- [ ] **UCT re-check** of every standard-form term against real customer pushback (A17.2).
- [ ] Revisit **governing law** (A15): if US buyers push back, adopt the US-law rider.

### Security program ("eat our own cooking")
- [ ] Our own policy set (access control, acceptable use, incident response, vendor management, retention, change management), framed on NIST CSF 2.0 ([NIST](https://www.nist.gov/cyberframework)) with an Essential Eight mapping for AU buyers.
- [ ] Quarterly access review; offboarding checklist.
- [ ] **Contractor paperwork:** NDA, **IP assignment** (under Australian law, a contractor owns copyright in what they create unless assigned in writing, **FLAG**), and a security addendum. If a contractor is overseas, disclose cross-border access (APP 1/APP 8 wording).
- [ ] Logging and alerting; dependency and secret scanning in CI.
- [ ] Our own written annual risk assessment.

### Segment and privacy triggers
- [ ] **Revisit the s 6EA opt-in** at the 1st AU paying customer or 10 customers total, whichever comes first.
- [ ] **10 Dec 2026:** the APP 1.7–1.9 automated-decision disclosures start for APP entities. If we have opted in by then, update the privacy policy (S: [Gilbert + Tobin](https://www.gtlaw.com.au/insights/automated-decision-making-transparency-under-the-privacy-act)).
- [ ] **Before the first US dental or medical sale:** no-PHI intake; BAAs downstream and our own HIPAA risk analysis before accepting PHI ([HHS](https://www.hhs.gov/hipaa/for-professionals/faq/business-associates/index.html)).
- [ ] **Before the first law-firm sale:** confidentiality addendum.

### SOC 2: not yet
- Don't pay for SOC 2 at 10 SMB customers (commonly quoted **US$15k–80k** first year, 3P: [Vanta](https://www.vanta.com/collection/soc-2/soc-2-for-startups), [Thoropass](https://www.thoropass.com/blog/soc-2-audit-cost-a-guide)). Build policies and evidence in a SOC 2-shaped way. AU buyers may instead ask about the **Essential Eight** or **SMB1001**; don't claim either.

---

## 3. Stage 100: about 100 customers (late 2027+)

### SOC 2 decision point
Start a **SOC 2 Type 2** when any of these happens: MSP partners or larger firms ask in writing; we add mailbox OAuth access or the forwarding helpdesk at scale; 2–3 deals a quarter stall on "no SOC 2"; fundraising diligence asks. Consider a compliance-automation tool 3 months before.

### Privacy law
- **Australian Privacy Act:** we become an APP entity **automatically if annual turnover passes A$3M** (turnover includes US sales; **FLAG** on how the test is measured) or if we opted in earlier. Then the full APP list, APP 8/s 16C for US subprocessors, the NDB scheme and the penalty regime apply (`terms-outline.md` Part B table). **Watch for a later tranche of reform removing the small-business exemption.** As of 2026-09-26 it has **not** been removed.
- **Cyber Security Act 2024 ransomware-payment reporting** applies above A$3M turnover (S; **FLAG**).
- **CCPA/CPRA** thresholds (US$26,625,000 revenue, 100,000+ California consumers, or 50%+ revenue from data) ([CPPA](https://www.cppa.ca.gov/regulations/cpi_adjustment.html)): verify annually; state-by-state check with a US lawyer.
- **GDPR/UK GDPR** only if we target EU/UK residents ([Art. 3(2)](https://eur-lex.europa.eu/eli/reg/2016/679/oj)).

### HIPAA at scale (if US dental or medical becomes segment #2)
BAA template, downstream BAAs, annual risk analysis, training, breach procedures (45 CFR 164.410: no later than 60 days; customer BAAs may be shorter), and the Security Rule NPRM ([HHS](https://www.hhs.gov/hipaa/for-professionals/security/hipaa-security-rule-nprm/factsheet/index.html)).

### Company hygiene
- [ ] Revisit PI and cyber limits against contract caps.
- [ ] Annual third-party pen test of our own app.
- [ ] **US sales-tax nexus** review (Stripe Tax monitoring, `australia-founder.md` §1.1) and **GST** position.
- [ ] Trademark registered (IP Australia, and USPTO if the US stays primary) and monitored.
- [ ] Board or advisor security reporting if we've raised money.

---

## 4. What needs a real lawyer or professional

| Item | Who | When |
|---|---|---|
| Company setup, GST, W-8BEN-E, US PE check | Australian accountant (US–AU experience) | **Now** |
| ToS, DPA, engagement letters (US and AU), **governing law (A15)**, **UCT review (A17.2)**, ACL wording, "TPB & TFN ready" and "Safeguards-Ready" names | Australian commercial lawyer (ideally with US experience) | Before the first sale (US ~15 Oct; AU 3 Nov) |
| s 6EA opt-in, APP 8, ADM disclosures, TFN Rule and accidental receipt | Australian privacy lawyer | Before 3 Nov |
| Spam Act footer, consent sources, LinkedIn DMs | Australian lawyer (`spam-act-cold-email.md`) | Before 12 Oct |
| §314.6 counting rule; FTC §5 review of US claims; unauthorized practice of law | US lawyer with FTC/GLBA experience | Before the first US sale |
| PI with US/Canada jurisdiction; cyber | Insurance broker | Before the first sale |
| Trademark clearance for "ChimeraShield" (AU and US) | Trademark attorney | Before spending on the brand |
| BAA and HIPAA program | US healthcare privacy lawyer | Before the first clinic that could send PHI |
| SOC 2 | CPA audit firm | At the Stage 100 triggers |

---

## 5. Marketing copy review: Spam Act and ACL conflicts (edits needed; files NOT edited)

Reviewed 2026-09-26: `docs/company/marketing/ads/ad-copy.md`, `landing-readiness-check.md`, `landing-pack.md`. **Owner:** growth-marketer / head-of-growth. **Deadline:** before go-live (15 Oct). Paid ads and web pages are not "electronic messages" under the Spam Act; the Spam Act items below are about the **emails** the pages send. ACL items apply because the publisher is an Australian company (**FLAG** on reach to US-only audiences; FTC §5 applies either way).

| # | File and location | Current text | Problem | Needed edit |
|---|---|---|---|---|
| M1 | `ad-copy.md` sitelink "Who Sees My Results?" | "Only you, at your work email" / "Stored encrypted, never shared" | Untrue: a person at ChimeraShield reviews every result, and hosting, email and AI subprocessors process it. Misleading (ACL s 18, FTC §5). | Line 1: "You and our reviewer only". Line 2: "Encrypted. Never sold." (≤35 chars; re-run `check_copy.py`). |
| M2 | `landing-readiness-check.md` FAQ "Who sees my results?" | "Only you… aren't shared with anyone else." | Same as M1; also contradicts the "Do you use AI? A person reviews your result" FAQ. | "You, and the ChimeraShield person who reviews it. Our service providers (hosting, email and AI) process it under contract, and we never sell it. [Subprocessor list]" |
| M3 | `landing-readiness-check.md` under the form | "We don't sell or share your details." | "Share" is too broad given subprocessors. | "We don't sell your details. We use them only to run your check, with the service providers listed in our privacy policy." |
| M4 | `ad-copy.md` LinkedIn Variant 3 intro | "Fewer than 5,000 clients? Four FTC Safeguards Rule items don't apply to you." | States exemption status as fact and swaps "consumers" for "clients" (the count includes past years, spouses and dependents). Contradicts `terms-outline.md` E1 rule. | "Hold data on fewer than 5,000 consumers? Four Safeguards items may not apply. The rest, like MFA, encryption and staff training, still do…" |
| M5 | `landing-pack.md` and `landing-readiness-check.md` FAQs "We have fewer than 5,000 clients…" | "clients" | Same as M4. | Use "consumers (everyone whose records you keep, including past years)" and "may be excused". Readiness form question: add "including past years". |
| M6 | `landing-readiness-check.md` result email (and the one follow-up) | Signature "[FOUNDER_NAME], Founder, ChimeraShield / [POSTAL_ADDRESS]"; "Reply 'stop' and we won't email again." | It promotes the Pack, so it's a **commercial electronic message**. Needs the authorising entity and **ABN**, and an unsubscribe that works for 30+ days and is honoured within 5 business days. | Use the `spam-act-cold-email.md` §4 footer: "ChimeraShield Pty Ltd (ABN [ABN])", contact email, [POSTAL_ADDRESS], "Reply 'unsubscribe' (or 'stop') and we won't email you again." Add suppression-list handling. |
| M7 | `landing-readiness-check.md` form | Only the optional newsletter box covers marketing | The follow-up email needs a consent basis the sender can prove. | Add a line above the submit button: "We'll email your result and one follow-up about it." Store it with the consent record (Spam Act evidential burden). Keep the newsletter box unticked by default. |
| M8 | Footers in both landing pages | "ChimeraShield · [POSTAL_ADDRESS] · hello@[DOMAIN]" | Doesn't identify the legal entity. | "ChimeraShield Pty Ltd · ABN [ABN] · [POSTAL_ADDRESS] · hello@[DOMAIN]". **FLAG:** whether Corporations Act s 153 (name and ACN/ABN on public documents) covers web pages. |
| M9 | `landing-pack.md` product name and hero | "Safeguards-Ready WISP & Evidence Pack" | May imply certification (FTC §5; ACL s 29(1)(g)/(h), **FLAG**). | Pending lawyer: fallback "Safeguards WISP & Evidence Pack". |
| M10 | `landing-pack.md` "Deadline" vs. `ad-copy.md` R3 | Pack: "~5 Dec 2026, confirm"; ads: "Last intake calls Dec 4" | Inconsistent dates in a deadline claim. | Use one date (**4 Dec**, per `australia-vs-us.md` §7) everywhere. |
| M11 | `landing-pack.md` pricing placeholders | Founding offer and refund placeholders | Future risk: a "list $795" shown as a was/now saving must be a genuine price (ACL s 18/s 29(1)(i), **FLAG**); "no refunds" wording would misstate ACL rights. | Show the founding price with its **real** limit ("first 10 packs or until 31 Dec 2026") and enforce it. Refund text from `terms-outline.md` E3.8 / A17.3. |
| M12 | `landing-pack.md` hero small print | "No client data, ever." | An absolute promise we can't fully control (screen-share accidents). | "We never ask for client data." |
| M13 | `landing-pack.md` and readiness page delivery promises | "Delivered within 7 business days"; "within one business day" | Future representations need reasonable grounds (ACL s 4). | Keep only while the founder's capacity plan supports them; add "of the intake call and receipt of your checklist" to the 7-day promise, to match E3.2. |
| M14 | All three files (general) | US-only copy using "WISP", "Safeguards" and the IRS/FTC framing | Fine for the US, but must never appear in AU channels. | Add a line to each file header: "US only. Do not reuse in Australia. See australia-vs-us.md §6." Keep Google Ads geo-targeted to the US. |

**No conflicts found in:** the ad rules section (no "certified"/"compliant", no fear, no fake proof), the IRS/FTC non-affiliation disclaimers, the passive-check descriptions, the unticked newsletter box, and the testimonial and "Used by [N] firms" placeholders (keep them hidden until real).
