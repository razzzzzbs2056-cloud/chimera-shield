# PRD: Client Data Security Pack (TPB & TFN ready), Australian pilot (AU-P1)

**Owner:** product-manager · **Date:** 2026-09-26 · **Status:** draft, v0 concierge pilot
**Plan:** Option C (company-context skill). US stays the revenue market. Australia is a **learning pilot**: interviews now, **1–2 paid pilots from 3 Nov to 11 Dec 2026**, decision gate **15 Feb 2027**.
**Segment:** Australian tax agent and accounting practices with 5–50 staff (`docs/company/market/australia-vs-us.md` §2b, score 35/50).
**Sibling PRD:** `docs/company/product/prd-wisp-evidence-pack.md` (US P1). This PRD reuses its delivery engine and changes the content.
**Catalog entry:** `docs/company/product/catalog.md` §10 (Australia).
**Implementation:** v0 is documents and process. The code changes (AU mode of the readiness check) go to the `tech-lead` agent (§12).

---

## 0. Copy rules (apply to every AU artefact, checked by AC-C1 to AC-C3)
- **Never use:** "WISP", "certified", "compliant", "compliance guaranteed", "TPB-approved", "ATO-endorsed", "Essential Eight assessment", "Essential Eight compliant" (market doc §6).
- **Never claim** that the Privacy Act small-business exemption ends, or is removed, in December 2026 or on any date. The Aug 2026 Tranche 2 exposure draft does **not** remove it (market doc T8). The 10 Dec 2026 change is about automated-decision transparency for APP entities only. Don't mention it in sales copy.
- **Use:** "information security policy", "data breach response plan", "Essential Eight snapshot", "structured on the TFN Rule and TPB guidance", "TFN information", "myID", "Online services for agents".
- AU English spelling, A$ prices **ex GST** (GST treatment still to be confirmed by legal-ops), dates written as "3 Nov 2026".
- Calm, no fear. Threat numbers only from market doc T13, with the source cited.

## 1. Problem
Every registered tax agent receives TFN information. The **Privacy (Tax File Number) Rule 2015** requires them to protect it, restrict access and dispose of it securely, and breaches of TFN information fall under the **Notifiable Data Breaches (NDB) scheme regardless of turnover**. The A$3M small-business exemption does not cover it (market doc T1). On top of that:
- the **TPB Code** (s 30-10(6) TASA) requires confidentiality, and since **1 Jul 2025** practices with ≤100 staff need a quality management system "appropriate to size and nature" (T2, T3);
- since **1 Jul 2024** tax practitioners must report **significant** Code breaches to the TPB within **30 days**. Whether a data breach is "significant" depends on the facts (T4);
- the **ATO** requires MFA and a myID per user for Online services for agents, and wants to hear **immediately** if access is compromised (T6);
- practices over about A$3M turnover (roughly 14+ staff, inference) are full APP entities, so APP 11 and the NDB scheme cover all personal information, and ransomware payments must be reported within 72 hours (T9).

These duties are spread across the OAIC, the TPB and the ATO. **No rule requires a written security plan and no annual form asks the owner to attest to one** (T5, §5), so there's no W-12-style deadline. The pain is quieter: the owner doesn't know what they would do on the day a laptop is stolen or a staff login is phished, and has nothing written to show an insurer, a client or the TPB. Only 20% of Australian small businesses had a formal cyber policy or staff training in 2025 ([Cyber Wardens Pulse Check 2025](https://cyberwardens.com.au/research-report/small-business-cyber-security-pulse-check-report/)), and the free Cyber Wardens training ended on 11 Sep 2026 (T12).

**The gap:** a policy and a breach plan written for *this* practice, a one-page snapshot of what is actually in place in the Essential Eight language that insurers and MSPs use, and the 5 things to fix first, in plain English.

## 2. Target user
- **Buyer and primary user:** the principal of a 5–50 person tax or accounting practice registered with the TPB, **no in-house IT**, either no MSP or an MSP that doesn't cover policy and breach planning.
- **Secondary user:** the practice manager who gathers the intake facts.
- **Not for (v0):** franchise or network offices that follow head-office policy; practices already fully managed by Practice Protect **and** an MSP that supplies a breach plan (route to the free check only); sole BAS agents and bookkeepers (possible cheaper tier later, market doc §4a).

## 3. Evidence
All sources are from `docs/company/market/australia-vs-us.md`. **Pages were found by web search but not opened** (market doc warning). Legal-ops must verify the starred (*) rows against the primary source before any AU copy or deliverable ships.

| Claim | Type | Source |
|---|---|---|
| *TFN Rule 2015 applies to every TFN recipient; TFN breaches are notifiable regardless of turnover | Fact | [OAIC TFN Rule](https://www.oaic.gov.au/privacy/privacy-guidance-for-organisations-and-government-agencies/handling-personal-information/the-privacy-tax-file-number-rule-2015-and-the-protection-of-tax-file-number-information); [TPB NDB page](https://www.tpb.gov.au/notifiable-data-breaches-scheme) |
| *NDB: assess a suspected eligible breach within 30 days; notify OAIC and affected people if eligible | Fact | [OAIC NDB Part 4](https://www.oaic.gov.au/privacy/notifiable-data-breaches/preventing-preparing-for-and-responding-to-data-breaches/data-breach-preparation-and-response/part-4-notifiable-data-breach-ndb-scheme) |
| *TPB breach reporting: significant Code breaches within 30 days, since 1 Jul 2024 | Fact | [TPB breach reporting](https://www.tpb.gov.au/breach-reporting-obligations) |
| *TPB QMS obligations apply to ≤100-staff practices from 1 Jul 2025. **No QMS requirement found that names cyber controls** | Fact | [TPB FAQs](https://www.tpb.gov.au/faqs-code-determination); [TPB(GS) 53/2024](https://www.tpb.gov.au/tpb-gs-53-2024-supervision-competency-and-quality-management-under-tax-agent-services-act-2009) |
| *TPB advises against emailing sensitive documents and recommends secure portals and MFA | Fact (guidance) | [TPB Keeping it secure](https://www.tpb.gov.au/keeping-it-secure); [TPB(GS) 26/2014](https://www.tpb.gov.au/tpb-gs-26-2014-confidentiality-client-information) (base guidance 2014, **stale**) |
| *ATO: MFA mandatory, own myID per user, tell the ATO immediately if compromised (Client Identity Support Centre 1800 467 033) | Fact | [ATO OSfA](https://www.ato.gov.au/tax-and-super-professionals/digital-services/online-services-for-agents); [ATO data-breach guidance for tax professionals](https://www.ato.gov.au/online-services/scams-cyber-safety-and-identity-protection/help-with-data-breaches/data-breach-guidance-for-tax-professionals) |
| *Ransomware payment reporting within 72 h for businesses above A$3M turnover | Fact | [Home Affairs factsheet](https://www.homeaffairs.gov.au/cyber-security-subsite/files/factsheet-ransomware-payment-reporting.pdf) |
| *Privacy Act small-business exemption is **not** removed by the Aug 2026 exposure draft | Fact | [Aitken](https://www.aitken.com.au/news/privacy-act-reforms-tranche2); [G+T](https://www.gtlaw.com.au/insights/one-giant-leap-tranche-2-of-privacy-act-reform) |
| Essential Eight ML1 is the common SMB vocabulary. "Insurers expect ML1" is **vendor-blog only, unverified** | Fact / unverified | [cyber.gov.au E8](https://www.cyber.gov.au/about-us/news/essential-eight-assessment-guidance-package); [Technovate](https://technovateit.com.au/the-small-business-cybersecurity-guide-implementing-the-essential-eight-maturity-level-one/) |
| 81 NDB notifications from legal, accounting and management services in 2025 | Fact | [OAIC 2025](https://www.oaic.gov.au/news/media-centre/data-breach-notifications-increase-to-all-time-high-in-2025,-new-ndb-stats-show) |
| Practice Protect: ~1,500 firms, 23k+ accountants, insurer discount | Fact (vendor) | [Practice Protect](https://practiceprotect.com/overview/); [Accountancy Insurance](https://www.accountancyinsurance.com.au/practice-protect/) |
| Free substitutes exist (ASD Cyber Health Check; IDCARE service for ≤19 staff) | Fact | [cyber.gov.au](https://www.cyber.gov.au/cyberhealthcheck); [business.gov.au](https://business.gov.au/grants-and-programs/small-business-cyber-resilience-service) |
| Nobody sells "policy + breach plan + evidence + fix list" mapped to TPB/TFN duties | Inference | Market doc §2b Gap |
| Principals will pay ~A$750 for this | **Assumption, no evidence** | Market doc §6 pricing. Finance-modeler has not set AU prices |
| Half of small firms spend under A$500 a year on cyber | Fact, **stale (2019)** | [ACSC survey](https://www.cyber.gov.au/sites/default/files/2023-03/2023_ACSC_Cyber%20Security%20and%20Australian%20Small%20Businesses%20Survey%20Results_D1.pdf) |

**Customer quotes:** none (0 AU interviews, no `docs/company/interviews/synthesis.md`). Link quotes here after the November interviews. Use market doc §10 questions 1–8.

## 4. Deliverables (v0, concierge)
Flow: buy → intake (60 min, in person or video) → passive checks → deliver within **7 business days** → debrief (30 min).

**(a) Information security policy** (practice-specific). Sections: scope and roles (principal, privacy/security contact); TFN information (collection, storage, who can access, secure disposal, per the TFN Rule); client document intake and sharing (portal over email, per TPB guidance); ATO access (own myID per person, MFA, removing leavers); devices and encryption; email and accounts (MFA everywhere); backups; software updates; staff training; suppliers and cloud software; supervision and records (links to the practice's own QMS, without claiming it satisfies the QMS obligation); annual review. The principal signs it.

**(b) Data breach response plan** (OAIC's term). One page of first steps plus the detail:
1. Contain (disconnect, reset passwords, revoke sessions).
2. **Tell the ATO immediately** if Online services for agents access, myID or client TFN data may be affected (Client Identity Support Centre, 1800 467 033, to be verified before delivery).
3. **NDB assessment:** start the 30-day assessment clock. Decide whether it is an eligible data breach. If yes, notify the OAIC and affected individuals. Applies to TFN information regardless of turnover, and to all personal information if the practice is an APP entity.
4. **TPB check:** decide, with the practice's own adviser, whether it is a **significant** breach of the Code to report to the TPB within 30 days. The plan does **not** say it always is.
5. If turnover is over A$3M and a ransom was paid: report within 72 hours (Cyber Security Act 2024).
6. Tell the insurer (policy number field), IT provider and software vendors.
7. Record-keeping log (who, what, when) and a lessons-learned review.
Contact table: principal, IT/MSP, insurer, lawyer, ATO, OAIC, TPB, IDCARE. Every "must notify" line carries "confirm with your adviser".

**(c) Evidence page: "Essential Eight snapshot"** (one A4 page). The eight strategies in ASD order: patch applications, patch operating systems, MFA, restrict admin privileges, application control, restrict Microsoft Office macros, user application hardening, regular backups. Then a **"Practice-specific"** block: own myID + MFA for each staff member, TFN storage and disposal, client document intake method, email authentication (SPF/DKIM/DMARC from the passive check), device encryption, breach plan in place. Each line is **Verified**, **Owner-stated** or **Gap**. Footer: "This is a snapshot, not an Essential Eight assessment or maturity rating."

**(d) Fix-First 5.** Exactly 5 ranked gaps, each with what, why, who, how long, and a vendor-neutral how-to link (cyber.gov.au first).

**Included:** the AU free check (TFN & client-data check, S5-AU) as the lead magnet, and a **Watch (AU edition)** offer at the debrief (§6).

## 5. Intake questions
Sent as a checklist 3 days before the call, confirmed live. **We never collect TFNs, client names or client documents.** If the owner starts to share any, stop and redirect.

**Practice**
1. Legal name, ABN, TPB registration type(s) (tax agent / BAS agent), number of registered practitioners and their renewal months.
2. Staff count (bands: 1–4, 5–14, 15–50) and locations. Anyone working from home?
3. Turnover band: under or over A$3M (decides APP-entity status and ransomware reporting). Owner-stated only; we don't ask for figures.
4. Is the principal a CPA / CA ANZ / IPA member (APES 320 applies to members)?
5. Who is the privacy / security contact? Who is the IT provider (MSP, freelancer, nobody)? Do you use Practice Protect?

**TFN information and client data**
6. How do clients send documents and TFNs today (portal, email, paper, in person)? Which portal?
7. Where are TFNs and client files stored (practice software, file server, SharePoint/Google Drive, paper)? Who can open them?
8. How do you dispose of TFN information and paper files (shredding service, retention period)?
9. Do you send documents to clients by email? Password-protected, portal link, or plain attachment?

**Access**
10. Does every staff member log in to Online services for agents with their **own** myID? Has a login ever been shared?
11. Is MFA on for email, practice software, the portal and remote access? Which ones?
12. Who has admin rights on computers and on Microsoft 365 / Google Workspace? How are leavers removed, and how fast?

**Devices, software, backups**
13. Laptops/desktops: count, operating system, disk encryption on? Automatic updates on?
14. Backups: what is backed up, where, how often, and when was a restore last tested?
15. Office macros blocked? Any software that staff can install themselves?

**People and incidents**
16. Staff security training in the last 12 months? What kind?
17. Any incident, suspicious ATO/myGov/myID email, or lost device in the last 2 years? What happened next?
18. Cyber insurance: insurer, renewal month, and has it asked about MFA, backups or Essential Eight?
19. Email domain(s) to check, and any DKIM selectors you know (for the passive check).

## 6. Watch (AU edition) and free check
- **Free check (S5-AU, "TFN & client-data check"):** 12 questions from market doc §6 plus the passive domain check. Result headline: "3 things to tighten in how your practice protects client data". Emailed only to a verified work address on the domain. The pilot can run it concierge (form + manual DNS lookups, result within 24 h) if the AU mode of the code isn't ready.
- **Watch (AU edition):** same as US Watch (monthly passive re-check, updated snapshot, fix tracker, A2 helpdesk with ATO/myGov/myID lure examples), with an **Australian lodgment calendar**: 2 Nov 2026 (individuals), 25 Nov 2026 (Q1 BAS via agent), 1 Mar 2027 (Q2 BAS), 15 May and 5 Jun 2027 (main agent dates); plus each practitioner's **TPB renewal month**, insurer renewal, the annual policy and breach-plan review, and a "what to do in the first 30 days" NDB clock that starts when the owner reports an incident. Calendar dates must be re-checked against the ATO program each year.
- **Prices (Assumption, finance-modeler to set):** Pack A$750 founding / A$1,200 list; Watch A$79 / A$149 / A$229 per month ex GST (market doc §4, §6). Not in `docs/company/finance/pricing.md` yet.

## 7. User stories
1. As a practice principal, I want a breach plan that tells me who to call first (ATO, OAIC, TPB, insurer), so I'm not guessing on the worst day.
2. As a principal, I want a security policy that describes how *my* practice handles TFNs, so I can show staff, my insurer or the TPB what we do.
3. As a principal, I want one page in Essential Eight language, so I can answer my insurer or MSP without jargon.
4. As a principal with no IT person, I want the 5 things to fix first, so I can act in November before the Christmas break.
5. As a practice manager, I want a plain checklist before the intake call, so I can gather facts without technical knowledge.
6. As a principal, I want to be sure ChimeraShield never sees my clients' TFNs and only ran permitted, passive checks on my domain.

## 8. Acceptance criteria (testable)
**Copy and legal safety**
- AC-C1. No AU artefact (checklist, policy, breach plan, snapshot, Fix-First, emails, landing copy, check results) contains "WISP", "certified", "compliant", "TPB-approved", "ATO-endorsed" or "Essential Eight assessment". Test: case-insensitive grep across the AU template folder and the rendered deliverable; 0 hits. (The phrase "not an Essential Eight assessment" in the snapshot footer is the one allow-listed exception.)
- AC-C2. No AU artefact states or implies an end date for the small-business exemption. Test: grep for "exemption" returns only allow-listed sentences approved by legal-ops.
- AC-C3. Every deliverable carries the disclaimer (legal-ops to approve wording before the first pilot): "Prepared with you from information you provided. General information only, not legal, tax or privacy advice. Confirm notification decisions with your own adviser. You remain responsible for your obligations."
- AC-C4. Every regulatory statement in the templates has a source link, and legal-ops has ticked each starred row in §3 as checked against the primary source. Logged in the template's review table.

**Sale, consent and data**
- AC-S1. No passive check runs until the engagement letter is accepted and the consent text (authorized-scanning skill) is stored with domain, name, email and UTC timestamp. The audit log shows consent before the first check.
- AC-S2. Intake notes contain **zero** TFNs or client names. Test: before storage, a regex check for 8–9 digit number patterns and a manual review; any hit is deleted and logged.
- AC-S3. The intake checklist is completed by 2 non-IT people in ≤15 minutes without help (hallway test).
- AC-S4. Any outreach email meets the Spam Act: sent only to conspicuously published work addresses, sender identified, ABN shown (or `[ABN]` placeholder until registered), unsubscribe honoured within 5 business days.

**Policy (a)**
- AC-P1. Contains every section listed in §4(a). A QA checklist confirms each is present and filled.
- AC-P2. At least 15 practice-specific facts from the intake appear (practice name, contact, portal, storage, disposal method, MFA status, and so on). Zero `[PLACEHOLDER]` tokens (grep).
- AC-P3. Signature block for the principal and a review date no more than 12 months after delivery.

**Breach plan (b)**
- AC-B1. Includes all 7 steps in §4(b), in that order, and the contact table with every row filled or marked "owner to add".
- AC-B2. The TPB step says "decide whether this is a significant breach" and never states that every data breach must be reported to the TPB. The NDB step names the 30-day assessment. The ATO step says "immediately". Checked by QA.
- AC-B3. The ransomware 72-hour line appears only if the owner reported turnover over A$3M; otherwise it's shown as "applies if your turnover is over A$3M".
- AC-B4. The first-steps page fits on one A4 page.

**Snapshot (c)**
- AC-E1. One A4 page. All 8 Essential Eight strategies in ASD order, plus the 6 practice-specific lines in §4(c).
- AC-E2. Every line is Verified, Owner-stated or Gap. "Verified" only with a stored artefact (check result or owner screenshot). QA matches each one.
- AC-E3. No maturity level is claimed or implied ("ML1 achieved" etc. is forbidden; grep "maturity level" returns 0 outside the footer).

**Fix-First (d) and understanding**
- AC-F1. Exactly 5 items with what, why, who, time and a link; Flesch-Kincaid grade ≤9.
- AC-F2. **Understanding test:** at the debrief, within 10 minutes, the principal explains their #1 fix and the first 2 steps of their breach plan in their own words. Pass/fail recorded; target 100%.

**Delivery**
- AC-D1. All deliverables within 7 business days of intake, and every pilot delivered by **11 Dec 2026**. Timestamps logged.
- AC-D2. Founder time per pack logged. Pilot target ≤6 hours (content is new); flag to finance-modeler if over 8.

## 9. Non-goals (pilot)
- Legal, tax, privacy or insurance advice, including deciding for the practice whether a breach is notifiable or "significant". We give the steps and the questions; the practice and its adviser decide.
- Notifying the OAIC, TPB, ATO or insurer on the practice's behalf.
- An Essential Eight assessment or maturity rating, SMB1001 certification, or any certificate.
- Claiming the pack satisfies the TPB QMS obligation, APES 320, APP 11 or the TFN Rule.
- Handling TFNs or any client data. Active scanning, pen testing, phishing simulations.
- Remediating fixes hands-on. Self-serve generator. Dental/GP variants (later, market doc §6).
- Paid AU ads in 2026 (market doc §7). Selling AU before 3 Nov (peak season).

## 10. Pilot success metrics (read at the 15 Feb 2027 gate)
- **Primary:** **2 paid pilots delivered by 11 Dec 2026** (minimum 1).
- **Learning:** 6 AU principal interviews held 3 Nov–11 Dec (avoid 18–25 Nov), logged in `docs/company/interviews/raw/`, feeding `synthesis.md`.
- **Price signal:** at least 3 of 6 interviewees name a one-off value ≥A$500 for this pack.
- **Understanding:** AC-F2 passes for 100% of pilots.
- **Action:** each pilot completes ≥1 Fix-First item within 14 days (check-in email).
- **Upgrade:** ≥1 pilot says yes to Watch (AU) or a Feb 2027 start.
- **Effort:** founder time per pack ≤6 h; total AU time ≤20% of founder week (market doc §7).
- **Kill / re-point signals:** 3+ of the first 6 principals say Practice Protect or their MSP "already covers it" (switch AU lead to dental, market doc risk 5); or 0 pilots from 6 interviews; or 3+ anchor value under A$300.

## 11. Reuse from the US Pack
| US asset (prd-wisp-evidence-pack.md) | AU reuse |
|---|---|
| Delivery flow: pay link → intake → passive checks → 7-day delivery → debrief → Watch offer | **Reuse as is** |
| Engagement letter, disclaimer, consent text | **Adapt:** Australian law and ABN, AU disclaimer (AC-C3); consent text unchanged. Legal-ops review |
| Intake script structure and non-technical checklist, hallway test | **Adapt:** questions in §5 replace the Safeguards/consumer-count questions |
| Evidence Report (Verified / Owner-stated / Gap, one page, artefact matching QA) | **Reuse method;** new layout in E8 order, A4 |
| Fix-First 5 template, readability rule, understanding test | **Reuse as is**, AU how-to links |
| S1 passive check output feeding the evidence page | **Reuse as is** |
| Findings store, audit log, encryption | **Reuse as is** |
| WISP template (Pub 5708 / 16 CFR 314.4) | **Do not reuse.** New policy + breach plan templates |
| W-12 / PTIN / FTC 30-day notice messaging and calendar | **Do not reuse.** AU calendar in §6 |
| Stripe link | Reuse account; new A$ price (GST to confirm) |

## 12. Readiness-check changes for the tech lead (AU mode)
Hand to `tech-lead`. Builds on sprint plan CS-05 to CS-08 (`docs/company/engineering/sprint-plan.md`). Not needed before the US launch; target **30 Oct 2026**, else run concierge.
1. **Registrable domain via the Public Suffix List** (e.g. `tldextract` or `publicsuffix2`). `.com.au`, `.net.au`, `.org.au`, `.id.au`, `.asn.au` and direct `.au` must work: `smithtax.com.au` is the registrable domain, never `com.au`. Applies to the "login email on the domain" rule (CS-05 AC1) and the "same registrable domain" redirect rule (CS-06 AC2). Tests: `mail.smithtax.com.au` user can add `smithtax.com.au`; a user on `other.com.au` cannot; `com.au` is rejected.
2. **AU free-mail and ISP domains rejected:** bigpond.com, bigpond.net.au, telstra.com, optusnet.com.au, iinet.net.au, tpg.com.au, internode.on.net, dodo.com.au, westnet.com.au, outlook.com.au, hotmail.com.au, live.com.au, yahoo.com.au (keep the list in config).
3. **Market/locale field per org** (`US` | `AU`), set at signup (by domain suffix default, user can change). It selects question set, copy, rules text, currency, paper size and calendar.
4. **AU question set** (12 questions from §5 subset / market doc §6) loaded from content, not hard-coded. Product authors it; CS-08 does not.
5. **AU copy pack:** result headline, rules-table "why" and fix text with cyber.gov.au links, en-AU spelling. No US terms (W-12, PTIN, IRS, FTC, Safeguards, WISP).
6. **Banned-phrase lint in CI** over AU content files: fails on the AC-C1 words and on "exemption" sentences not on the allow-list (AC-C2).
7. **Formats:** A$ ex GST, dates "3 Nov 2026", emails scheduled in Australia/Sydney time, PDFs on A4.
8. **Email footer** for AU results: ABN (placeholder until registered) and unsubscribe honoured within 5 business days (Spam Act).
9. **Passive checks unchanged** (same engine, same passive tier, same consent). No new network actions.
10. **Open for legal-ops:** hosting region of intake/findings data and whether APP 8 cross-border disclosure wording is needed.

## 13. Risks
1. **Giving legal/tax/privacy advice.** Deciding whether a breach is "eligible" or "significant" is legal judgement. Mitigation: AC-B2, AC-C3, non-goals, "confirm with your adviser" on every notification line, engagement-letter limits, legal-ops review of templates, and a check on whether professional indemnity / E&O cover is needed before the first pilot.
2. **Regulatory accuracy from unopened sources.** Every AU fact came from search summaries. Mitigation: AC-C4. Nothing ships until legal-ops ticks the starred rows.
3. **Presented as proof of compliance** after a breach. Mitigation: banned words, the snapshot footer, Owner-stated labels.
4. **Practice Protect and MSPs already cover it.** Mitigation: position as policy + breach plan + evidence (which a login-security platform doesn't write); watch the kill signal in §10.
5. **Price sensitivity** (stale 2019 A$500 spend data; free ASD/IDCARE options). Mitigation: test A$750 in interviews; fallback lighter tier.
6. **Seasonality.** Only 3 Nov–11 Dec works in 2026, minus 18–25 Nov. A late legal review kills the pilot. Mitigation: templates and legal review done by 30 Oct.
7. **Founder split.** AU must not eat US PTIN-window time. Cap at 20% (§10).
8. **Collecting TFNs by accident** would make us a TFN recipient. Mitigation: AC-S2, intake script warning.
9. **Exemption misinformation** in the market (vendor blogs). Prospects may repeat it; we correct calmly and never echo it (§0).
