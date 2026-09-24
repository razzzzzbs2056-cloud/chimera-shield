# ChimeraShield Product and Services Catalog (v0.2)

**Owner:** product-manager · **Date:** 2026-09-24 · **Status:** draft for founder decision
**First market:** US accounting, CPA and tax-prep firms with 5–50 staff (score 44/50). **Runner-up:** US independent dental (41/50). Source: `docs/company/market/first-market-selection.md`.
**Evidence status:** 0 customer interviews (`docs/company/interviews/recruiting-kit.md`); no `synthesis.md` yet. **Every score is a hypothesis.** Confidence is capped at 40%, and that cap is used only where an external buying trigger is verified (a rule or form, such as FTC Safeguards or the W-12 line 11 attestation). It never reflects proven demand.

Inputs: `docs/company/competitors/smb-landscape-2026.md`, `docs/company/market/first-market-selection.md`, `docs/company/interviews/recruiting-kit.md`, `docs/chimera/01–05`, `backend/routers/scan.py`, `app/scan/page.tsx`, `.claude/skills/authorized-scanning/SKILL.md`.

---

## 1. Starting point: what is already built

| Asset | State | Implication |
|---|---|---|
| AI phishing analyzer (`POST /api/scan/email`, `app/scan/page.tsx`) | Works locally. No auth, no retention policy, hardcoded model id, fragile JSON parsing, untrusted email text pasted straight into the prompt (prompt-injection surface), CORS set to localhost. | Engine for the helpdesk agent (A2). **Not sellable alone**: Norton Genie and Bitdefender Scamio are free. |
| Domain/email check | Not built | Needed for the lead magnet. Passive tier only. |
| WISP generator, evidence report, accounts, payments | Not built | Concierge delivery (doc templates, a call, a Stripe payment link) until 5+ packs are sold. |
| Duplicate `app/` and `frontend/app/` trees | Both exist | Tech-lead should pick one before more UI work. |

## 2. Positioning constraints

1. **From the landscape doc:** price is not a moat, "AI-native" is not a moat, and standalone phishing and DMARC checks are free. We win only if the offer is **owner-direct, agentless, plain English, "fix this first", and shaped around a trigger**.
2. **From market selection:** accounting buyers pay for **proof of compliance** (a current WISP, plus evidence of MFA, encryption, monitoring and training), not for "AI security". So lead with "Safeguards Rule + WISP ready, in plain English".
3. **Calendar:** the PTIN renewal window runs **mid-Oct to 31 Dec 2026**, and the W-12 line 11 attestation is part of it. Firms **won't buy Jan to mid-Apr** (filing season). Anything paid must be sellable and deliverable **by mid-December**.
4. **Main risk:** owners may think of a WISP as a **$29 template**. The market includes $29–$999 templates and per-user MSP bundles (Bellator, writtensecurityplan.com, per the market doc). Our paid offer has to contain what a template can't: firm-specific facts, checked evidence, and a ranked fix list.

---

## 3. Candidate offers with one-line specs

Dental carryover: **Direct** = the same offer with swapped regulation content; **Adapt** = a new content pack on the same delivery engine; **No** = accounting-specific.

| ID | Offer | Type | One-line spec | Dental carryover |
|---|---|---|---|---|
| S5 | **Free WISP & Safeguards Readiness Check** | Self-serve | A 12-question owner quiz on the FTC Safeguards elements, plus S1's passive email/domain check, produces a plain-English readiness result emailed to the work address: "3 gaps to close before you sign your W-12". | Adapt ("HIPAA Risk Analysis Readiness Check") |
| S1 | Email & Domain Safety Check (standalone) | Self-serve | Passive SPF/DKIM/DMARC/MX/TLS/header check with a plain-English top 3. S5 uses it as a component. | Direct |
| S2 | AI Phishing Analyzer (paste) | Self-serve | Paste an email and get a risk level, red flags and a next step. Already built. | Direct |
| S3 | Self-serve Security Snapshot | Self-serve | An automated questionnaire plus S1 that produces a ranked 5-item fix list PDF. | Direct |
| S4 | M365 / Google Workspace Posture Translator | Self-serve | Read-only OAuth access that translates existing admin settings into evidence and fixes. | Direct |
| **P1** | **Safeguards-Ready WISP & Evidence Pack** | Done-with-you | A 60-min intake produces three things: a **firm-specific WISP** structured on IRS Pub 5708 / 16 CFR 314.4, a **one-page Evidence Report** (MFA, encryption, email security, training, backups, each marked Verified / Owner-stated / Gap), and a **Fix-First plan** of the top 5 gaps. The owner signs as Qualified Individual. | Adapt (becomes D4 plus the same evidence page) |
| D2 | Cyber-Insurance Questionnaire Prep Pack | Done-with-you | Maps common insurer questions to the P1 Evidence Report. The owner answers the insurer; we never answer for them. | Direct |
| D4 | HIPAA Security Risk Analysis Starter | Done-with-you | A guided walk-through of the HHS SRA tool that produces a documented risk analysis and fix list. No-ePHI intake, so no BAA is needed. | Dental's P1 equivalent |
| D5 | Law-Firm Tech-Competence & Breach-Response Kit | Done-with-you | A checklist against ABA 477R/483/512, a one-page incident-response plan and a client-questionnaire answer sheet. | No |
| A1 | Weekly Plain-English Brief (monitoring agent) | AI agent | Re-runs passive checks, sends breach-domain alerts and compliance-calendar reminders, and summarizes it all as a short brief. | Direct |
| A2 | **"Is this safe?" Forwarding Helpdesk Agent** | AI agent | Staff forward a suspicious email (for example an IRS/e-Services lure or a fake client document) to a firm address and get a plain-English verdict. A human reviews every HIGH/CRITICAL verdict. | Direct |
| A3 | AI Adoption Safety Package | AI agent / service | A shadow-AI staff survey, an AI usage policy and a review of which client data goes into AI tools. | Direct (PHI in AI tools) |

## 4. Scored table (weighted to accounting/tax)

RICE = Reach × Impact × Confidence ÷ Effort.
- **Reach** = accounting/tax owners likely to see the offer by 31 Dec 2026 (about 100 touches, r/taxpros posts, NATP/state-society contacts, 1–2 partners). Dental offers count only the 4 planned dental interviews plus spillover.
- **Impact** = 3 massive, 2 high, 1 medium, 0.5 low, measured against **3 paying customers by day 90**.
- **Confidence** = 40% if the trigger is verified, 30% if inferred, 20% if assumed. No level reflects customer evidence.
- **Effort** = founder-weeks to the first paid delivery, with concierge delivery allowed.

| ID | Offer | R | I | C | E | **RICE** | Differentiation vs. landscape (and WISP market) | Founder can deliver in 30 days? |
|---|---|---|---|---|---|---|---|---|
| S5 | Free WISP & Safeguards Readiness Check | 400 | 1 | 40% | 1 | **160** | **Medium-high.** Free DMARC scanners and Coalition Control score domains but say nothing about Safeguards or the W-12. No landscape vendor offers an owner-facing readiness check. | **Yes.** A form tool plus manual DNS lookups and an emailed result within 24h. Automate in about 1 week. |
| **P1** | **Safeguards-Ready WISP & Evidence Pack** | 200 | 3 | 40% | 2 | **120** | **Medium-high.** Guardz, Coro and Huntress don't produce WISPs, and MSPs bundle them into per-user contracts. Templates ($29–$999) are generic, with no evidence and no plan. **Weakness:** the IRS Pub 5708 template is free, and competitors in the WISP market are **not yet researched** by competitor-analyst. | **Yes**, fully concierge: WISP template, intake script, evidence-page template, Stripe link. |
| S1 | Email & Domain Check (standalone) | 300 | 0.5 | 40% | 1 | 60 | Low. The scan is free elsewhere. | Yes |
| D2 | Insurance Prep Pack | 150 | 2 | 30% | 1.5 | 60 | High. Coalition shows insurer-driven demand but offers no plan. | Yes. Reuses the P1 Evidence Report. |
| S2 | AI Phishing Analyzer (paste) | 300 | 0.25 | 30% | 0.5 | 45 | Low (Genie and Scamio are free). | Yes (built; needs hardening) |
| S3 | Self-serve Snapshot | 200 | 1 | 30% | 3 | 20 | Medium | Partial |
| D4 | HIPAA SRA Starter (dental) | 40 | 2 | 40% | 2 | 16 | Medium. Crowded with HIPAA-compliance vendors (not researched), and the HHS SRA tool is free. | Partial: needs a no-ePHI design and legal-ops review |
| A2 | "Is this safe?" Helpdesk Agent | 60 | 1 | 30% | 1.5 | 12 | **Low-medium.** Free checkers exist, and Microsoft's triage agent is E5-only. The edge is firm context and a human on HIGH verdicts during tax season. | Yes, as concierge: a shared inbox triaged by the founder using the analyzer |
| A1 | Weekly Brief Agent | 60 | 2 | 20% | 3 | 8 | Medium. Continuous monitoring is owned by MSP platforms, but none produces an owner brief. | Partial (manual for 10 customers) |
| A3 | AI Adoption Safety | 60 | 1 | 20% | 1.5 | 8 | **High.** No landscape vendor has it, but demand in accounting is unproven. | Yes |
| S4 | M365/Workspace Posture Translator | 150 | 2 | 20% | 8 | 3.8 | High | **No.** Needs OAuth app verification. Use a P1 screen-share instead. |
| D5 | Law-Firm Ethics Kit | 20 | 1 | 30% | 1.5 | 4 | Medium-high | Yes, but it's the wrong segment for now |

Reach for A1, A2 and D4 is low by design, because these are retention or second-segment offers. The lineup below is chosen by role, not by raw RICE.

---

## 5. Recommended starting lineup

| Slot | Offer | Type | Price hypothesis (finance-modeler sets final) | Dental carryover |
|---|---|---|---|---|
| Free lead magnet | **S5 Free WISP & Safeguards Readiness Check** | Self-serve (concierge until automated) | $0 | Adapt: HIPAA Readiness Check |
| Paid entry | **P1 Safeguards-Ready WISP & Evidence Pack** | Done-with-you, concierge | **$300–$900 one-time.** Test $495 founding against $795 list. Solo preparers could get a lighter tier at $195–$295. | Adapt: HIPAA Risk Analysis & Evidence Pack (D4) |
| Recurring subscription | **ChimeraShield Watch (Safeguards edition)**: monthly evidence refresh (re-runs passive checks, updates the Evidence Report), gap-plan tracker, compliance calendar (annual WISP review, PTIN window, insurance renewal, the 30-day FTC breach-notice clock), plain-English monthly brief (A1, manual at first), quarterly 20-min check-in | Subscription | **$49–$149/mo per firm.** $99 standard and $49 founding/solo, per the market doc. Test **annual prepay** billed in Nov–Dec, since firms go dark Jan–Apr. | Direct |
| AI agent (max 1) | **A2 "Is this safe?" Helpdesk Agent**, **bundled in Watch**, not sold alone | AI agent | Included. Hypothesis: it justifies $99 over $49. | Direct |

### Why each was picked
- **S5 lead magnet.** It speaks the buyer's language ("Can you sign line 11 of your W-12 honestly?") instead of "free DMARC scan", which is the commodity the landscape doc warns about. It is timed to the PTIN window. It also creates the authorization moment we need anyway: a work email on the domain plus the consent text. Passive tier only (authorized-scanning skill).
- **P1 paid entry.** It is the only offer that combines high impact on the 3-customers goal, a verified legal trigger that falls in the next 90 days, and full concierge delivery by the founder. It directly addresses market-selection risk #2 (we need a WISP plus evidence in v0.1). **Answer to the "$29 template" risk:** P1 sells the *done-with-you, firm-specific, evidenced* version. The evidence page is reusable for the insurer (D2) and clients, and the Fix-First plan is the bridge to Watch. **Kill/pivot rule:** if 3 or more of the first 6 accounting interviews anchor WISP value under $100, turn P1 into a self-serve generator at $79–$149 and move the value into Watch.
- **Watch subscription.** The Safeguards obligations are ongoing (MFA, monitoring, training, annual WISP review), so the evidence goes stale. Annual prepay in Nov–Dec also covers the Jan–Apr blackout, which is when IRS-themed phishing peaks (Feb 2026 wave, per the market doc). **Don't claim Watch satisfies 16 CFR 314.4(d)(2) continuous monitoring**: it is passive, outside-in checking only.
- **A2 as the only agent.** It reuses the one working piece of code. It gives staff a daily action during the season when they are most targeted, which is Watch's anti-churn feature. Standalone, it competes with free tools, so it is bundled. A3 is the reserve agent/service if interviews surface AI-tool confidentiality worries.

### Upgrade path
```
S5 Free Readiness Check (Oct–Dec) ──(result: "3 gaps before you sign your W-12" + offer)──►
P1 WISP & Evidence Pack ($, delivered ≤7 business days) ──(debrief: 90-day Fix-First plan;
      hypothesis: pack fee credited toward Watch annual prepay if started within 30 days)──►
Watch ($/mo or annual, includes A2 helpdesk; runs through tax season) ──(next Oct)──►
Annual WISP review + refreshed Evidence Report before the next PTIN renewal (renewal revenue)
```
Side doors: insurer renewal leads to P1 with the D2 mapping. A phishing incident leads to P1 plus Watch.

### Dental carryover (segment #2, start after 3 accounting packs are sold or in May 2027)
- **Carries over directly:** S1, S2, Watch, A2, A1, D2, A3. The delivery engine, evidence-page format and Fix-First plan are all the same.
- **Needs a new content pack:** S5 becomes a HIPAA Readiness Check, and P1 becomes D4 (the HHS SRA-based risk analysis plus the evidence page). The intake must be **designed so no PHI is collected**, or we'd need a BAA (legal-ops to confirm).
- **Doesn't carry over:** the W-12 and PTIN timing, and the FTC Safeguards mapping. Dental has no hard annual deadline, so its triggers are insurance renewal and OCR risk-analysis enforcement.

## 6. Cut or deferred
- **Roadmap "Basic Vulnerability Scanner": defer.** Active checks need verified domain ownership and add legal risk, and accounting buyers want evidence, not port scans.
- **S2 as a marketed product:** keep it as an in-app feature and as A2's engine.
- **S4 posture translator:** revisit after 5 packs show which M365/Workspace settings matter.
- **D5 law kit:** parked until law becomes a target segment.

## 7. What to build next (hand to tech-lead), in priority order
1. **S5 Readiness Check.** Quiz plus passive S1 checks, results emailed only to a work address on the scanned domain, consent text and timestamp stored, free-mail domains rejected. Target: live by **15 Oct 2026**.
2. **P1 delivery kit (product and legal-ops, mostly docs).** WISP template mapped to Pub 5708 / 16 CFR 314.4 with §314.6 handling for firms under 5,000 consumers, intake script, Evidence Report template, Stripe payment link, engagement letter and disclaimer. The only code needed is feeding S1 output into the Evidence Report.
3. **Findings and consent store.** Encrypted at rest, visible only to the account. Every paid offer depends on it.
4. **Harden the phishing analyzer** for A2. Model id from config, schema-validated output, delimited untrusted input, in-memory processing with 30-day deletion, auth.
5. **A2 inbound forwarding.** Only after 3 packs are sold; target before 1 Jan 2027 for tax season.

## 8. Recommended roadmap changes (not yet applied to `docs/chimera/04-90-day-roadmap.md`)
- Replace the "Never worry about a cyber breach again" dream outcome with "Sign your W-12 honestly: a WISP and evidence you understand, done in a week."
- Phase 2 v0.1: swap the active "Basic Vulnerability Scanner" for the S5 passive check plus the P1 evidence report.
- Phase 3: first revenue is P1 (one-time), with Watch as the upsell. Compress the sales window to **mid-Oct to mid-Dec 2026**.

## 9. Validate in the next interviews (6 accounting, 4 dental)
1. At the last PTIN renewal, what WISP did they actually have, who wrote it, and what did it cost? (This is the P1 price anchor and tests the $29-template risk.)
2. Has an insurer or client asked for proof of MFA or a security plan? What did they send? (D2 and the Evidence Report)
3. Would a signed evidence page be useful to them, and who would they show it to?
4. MSP or no MSP? Business Premium or not? (This decides the S4 and MSP-channel questions.)
5. Last suspicious IRS/e-Services or client-document email: what did staff do? (A2)
6. Dental: last HIPAA risk analysis, who did it and at what cost? (D4)
