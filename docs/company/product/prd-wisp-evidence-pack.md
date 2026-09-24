# PRD: Safeguards-Ready WISP & Evidence Pack (P1)

**Owner:** product-manager · **Date:** 2026-09-24 · **Status:** draft, v0 concierge
**Segment:** US accounting, CPA and tax-prep firms with 5–50 staff (`docs/company/market/first-market-selection.md`)
**Catalog entry:** `docs/company/product/catalog.md` (P1, the recommended paid entry offer)
**Implementation:** almost entirely documents and process for v0. The code pieces (S5 readiness check, findings store) go to the `tech-lead` agent.

---

## 1. Problem
Every paid tax preparer attests on Form W-12, line 11, at each PTIN renewal that they know they must "create and maintain a written information security plan". The FTC Safeguards Rule (16 CFR Part 314) treats tax preparers and CPA firms as financial institutions regardless of size. It requires a Qualified Individual and safeguards including MFA, encryption, training, service-provider oversight and monitoring, and since 13 May 2024 an FTC notice within 30 days for breaches affecting 500+ consumers.

Small firms have two options today:
- a free IRS template (Pub 5708) or a $29–$999 generic template, which the firm has to fill in itself and which proves nothing about what is actually in place;
- an MSP bundle priced per user.

**The gap:** a firm-specific plan, evidence that the plan reflects reality, and a short list of what to fix first, delivered in words the owner understands, before the renewal deadline.

## 2. Target user
- **Buyer and primary user:** the owner or managing partner of a 5–50 person tax, CPA or EA firm who renews a PTIN and has **no in-house IT and ideally no MSP**. They decide alone (market doc: Speed 4).
- **Secondary user:** the office manager or firm administrator who gathers the intake facts.
- **Not for:** firms whose MSP already maintains a WISP. They get routed to the free S5 check only. Also not for franchise offices (H&R Block, Jackson Hewitt), which follow corporate policy.

## 3. Evidence
| Claim | Type | Source |
|---|---|---|
| The W-12 line 11 WISP attestation happens at every PTIN renewal | **Fact** | [IRS Form W-12](https://www.irs.gov/pub/irs-pdf/fw12.pdf), via `interviews/recruiting-kit.md` A1 |
| The Safeguards Rule applies to tax preparers at any size, and FTC breach notice has been in force since May 2024 | **Fact** | [FTC guide](https://www.ftc.gov/business-guidance/resources/ftc-safeguards-rule-what-your-business-needs-know), [FTC blog](https://www.ftc.gov/business-guidance/blog/2024/05/safeguards-rule-notification-requirement-now-effect) |
| Firms with fewer than 5,000 consumers are exempt from some elements (written risk assessment, pen testing/continuous monitoring, IR plan, annual report) but not MFA, encryption or training | **Fact (secondary source)** | Market doc §4, [Flamingo on §314.6](https://www.flamingo.run/blog/ftc-safeguards-rule-checklist). **Legal-ops must verify against 16 CFR 314.6.** |
| WISPs are sold as $29–$999 templates or inside MSP contracts | **Fact (vendor pages, unopened)** | Market doc §2 |
| Small firms downloaded the IRS template but never finished it | **Inference, unvalidated** | Recruiting kit A1 |
| Owners will pay $300+ for a done-with-you version | **Assumption, no evidence** | Validate with interview Q1 in catalog §9 |
| No landscape vendor (Guardz, Coro, Huntress, Microsoft) produces an owner-facing WISP or evidence page | **Inference** | `competitors/smb-landscape-2026.md` §3 |

**Customer quotes:** none yet (0 interviews). Link quotes from `docs/company/interviews/synthesis.md` here once it exists. **This PRD should be revisited after the first 6 accounting interviews.**

## 4. The offer (v0, concierge)
1. **Buy:** Stripe payment link, engagement letter with disclaimer, consent to passive checks (§7).
2. **Intake (60 min, video call):** a structured script covering people and roles, systems (email provider, tax software, portal, devices, backups), approximate consumer-record count (<5,000 or ≥5,000), service providers, MFA and encryption status, training, and incident history. **No client data is collected.**
3. **Passive checks:** S1 checks on the firm's own domain (§7).
4. **Deliverables within 7 business days:**
   - **(a) Firm-specific WISP**, structured on IRS Pub 5708 and mapped section by section to 16 CFR 314.4, with §314.6 exemptions applied where they fit. The owner signs as Qualified Individual.
   - **(b) One-page Evidence Report.** Each control carries one of three statuses: **Verified** (we observed it: a DNS check, a screen-shared admin setting), **Owner-stated** (reported but not observed), or **Gap**. The page can be reused for insurers and clients.
   - **(c) Fix-First plan:** the top 5 gaps ranked by risk and effort. Each has a plain-English "why", "who does it" and "how long".
5. **Debrief (30 min):** walk through the plan, confirm the owner understands their #1 fix, and offer Watch.

## 5. User stories
1. As an owner about to renew my PTIN, I want a WISP that describes *my* firm so I can sign W-12 line 11 honestly.
2. As an owner, I want one page that shows what is actually in place, so I can hand it to my insurer or a client who asks.
3. As an owner with no IT person, I want the 5 things to fix first in plain English, so I know what to do this month.
4. As an office manager, I want an intake checklist before the call so I can collect facts without technical knowledge.
5. As an owner, I want to know that ChimeraShield only ran permitted, non-intrusive checks on my domain, and that my data stays private.

## 6. Acceptance criteria (testable)
**Sale and onboarding**
- AC1. A buyer can pay through a Stripe link and gets a confirmation email with a booking link and the intake checklist within 5 minutes (test: a live test-mode purchase).
- AC2. No passive check runs until the engagement letter is accepted and the consent text in §7 is recorded with the domain, the name, the email and a UTC timestamp. An audit log shows consent written before the first check.
- AC3. The intake checklist is readable by a non-technical person. In a hallway test with 2 non-IT people, both complete it in **15 minutes or less** without asking for help.

**WISP (deliverable a)**
- AC4. The WISP has a section for every element of 16 CFR 314.4 (a)–(j). Each section is either filled with firm-specific content or explicitly marked "exempt under §314.6 because <reason>". The tech-lead/QA checklist can check all 10 elements.
- AC5. At least **15 firm-specific facts** from the intake appear in the WISP: firm name, Qualified Individual, systems, providers, record count band, MFA status, and so on. Zero `[PLACEHOLDER]` tokens remain (test: grep).
- AC6. The WISP includes a signature block naming the owner as Qualified Individual and an annual-review date no later than 12 months from delivery.
- AC7. Every WISP carries a disclaimer: "Prepared with you from information you provided. Not legal advice. You remain responsible for your compliance." Legal-ops approves the wording before the first sale.

**Evidence Report (deliverable b)**
- AC8. It fits on one page (US Letter PDF) and lists at least 8 controls: MFA on email, MFA on tax software/remote access, device encryption, email authentication (SPF/DKIM/DMARC), backups, security training, service-provider oversight, and the incident-response contact.
- AC9. Every control is labeled **Verified**, **Owner-stated** or **Gap**. "Verified" appears only where there is a stored artifact: a check result, or a screenshot taken by the owner during screen-share. A QA check matches each Verified label to its artifact.
- AC10. The report contains no statement that the firm "is compliant" or "passes" anything (test: search for "compliant", "certified", "passes").

**Fix-First plan (deliverable c)**
- AC11. Exactly 5 ranked items, each with: what, why (one sentence, no unexplained jargon), who can do it, estimated time, and a link to a vendor-neutral how-to. Target: Flesch-Kincaid grade 9 or lower, measured.
- AC12. **Understanding test (MVP guardrail):** at the debrief, after no more than 10 minutes with the plan, the owner can say in their own words what their #1 fix is and why. Record pass/fail for every customer. The target pass rate is 100%, and any failure triggers a rewrite of the template.

**Delivery and data**
- AC13. All three deliverables reach the customer within **7 business days** of the intake call. Log the timestamps.
- AC14. Founder time per pack is **4 hours or less** after the third pack (logged). If it's over 6 hours, the price or scope must be revisited with finance-modeler.
- AC15. Findings and intake notes are stored encrypted and shared only with the customer's named contacts. No findings are sent to anyone else.

## 7. Scanning scope (per `.claude/skills/authorized-scanning/SKILL.md`)
- **Passive / public tier only:** DNS lookups (MX, SPF, DKIM selectors the customer names, DMARC), TLS certificate info, and security headers from one normal homepage load. HIBP domain search only after HIBP's own domain verification.
- **No light-active or intrusive checks** in P1: no port scans, vulnerability probes, login testing or phishing simulations. Admin settings are "Verified" only through the **owner's own screen-share or screenshots**; we never log into their systems.
- **Only the customer's own domain.** Never third-party infrastructure (hosting provider, tax-software vendor, portal vendor) beyond reading the customer's own DNS records.
- **Consent text** (recorded with timestamp): *"I confirm I own or am authorized by the owner to test [domain], and I authorize ChimeraShield to perform the passive checks described. I understand results may include sensitive security information."*
- Findings are confidential, encrypted at rest and visible only to the account. LLM-drafted text is reviewed by the founder before delivery and is never used to auto-execute changes.
- **Sales:** never send prospects unsolicited findings. Demos use a company-owned demo domain.

## 8. Non-goals (v0)
- A self-serve WISP generator (revisit only if the pivot rule in catalog §5 fires, or after 10 packs).
- Being the firm's Qualified Individual, or giving legal, tax or insurance advice.
- Filling in insurance applications or answering regulators on the firm's behalf.
- Active scanning, penetration testing, phishing simulations, pen-test evidence for §314.4(d)(2).
- Remediating the fixes ourselves (hand-holding by email is fine; hands-on-keyboard work is not).
- Dental/HIPAA content (that's D4, later).
- Handling client (taxpayer) data of any kind.

## 9. Success metric
- **Primary:** **3 paid packs by 15 Dec 2026** (from about 100 touches and S5 leads). This meets the roadmap's north star of 3 paying customers.
- **Leading:** S5-to-P1 conversion of at least 5% of completed readiness checks. At least 2 of the first 3 buyers complete 1 or more Fix-First items within 14 days, confirmed at a 14-day check-in email.
- **Upgrade:** at least 1 of the first 3 buyers starts Watch (monthly or annual) within 30 days.
- **Guardrails:** AC12 pass rate of 100%, AC13 on time, AC14 under 4 hours of founder time.
- **Kill/pivot signals:** 0 sales from 30 or more qualified conversations by 1 Dec 2026, **or** 3 or more of the first 6 accounting interviews anchor WISP value under $100. Either triggers the self-serve $79–$149 pivot in catalog §5.

## 10. Price hypothesis (finance-modeler sets final)
$300–$900 one-time. Test **$495 founding** against **$795 list**, and consider a solo-preparer tier at $195–$295. This anchors between the $29–$999 templates and per-user MSP bundles. Hypothesis: the fee is credited toward Watch annual prepay if the customer starts within 30 days.

## 11. Timeline
| Date | Milestone |
|---|---|
| by 8 Oct 2026 | Legal-ops approves the engagement letter, disclaimer and consent text. WISP and Evidence Report templates finished. Stripe link live. |
| by 15 Oct 2026 | S5 readiness check live (tech-lead). First outreach mentions the PTIN window. |
| 15 Oct – 15 Dec 2026 | Sell and deliver. Last intake call about 5 Dec so delivery lands before the holidays. |
| Jan – mid-Apr 2027 | No new P1 sales. Serve Watch customers, turn packs into product. |

## 12. Open risks
1. **"$29 template" perception** (market doc risk #3). Mitigation: the evidence plus Fix-First plan is the differentiator, and the pivot rule is defined above.
2. **Regulatory accuracy.** The §314.6 exemption and the W-12 wording come from secondary sources. Legal-ops must verify both against the primary text before the first sale. Misstating the rule is a reputational risk.
3. **Liability.** A customer might present the WISP or Evidence Report as proof of compliance after a breach. Mitigations: AC7, AC10, the "Owner-stated" label, engagement-letter limits on liability, and legal-ops checking whether E&O insurance is needed.
4. **Competitors not researched:** WISP template vendors and tax-focused MSPs (Bellator, writtensecurityplan.com, others). Ask competitor-analyst for a teardown before pricing is final.
5. **Founder capacity.** At more than 4 hours per pack, about 10 packs a month is the ceiling. That's acceptable for v0 but caps revenue.
6. **Seasonality.** Missing the mid-Oct to mid-Dec window pushes first revenue to May 2027.
7. **MSP overlap.** If most prospects have an MSP, P1 might need an MSP-partner variant (market doc risk #4).
