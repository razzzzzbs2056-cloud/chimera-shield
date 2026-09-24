# Sales Playbook: first paying customers (accounting / tax-prep, PTIN window 2026)

**Owner:** head-of-sales (founder-led) · **Date:** 2026-09-24 · **Status:** draft, ready to run once the gates in §2 are cleared
**Goal:** 3 paid WISP & Evidence Packs by 15 Dec 2026 (floor), 5–6 (plan), 10 (ceiling, capped by founder delivery capacity).
**Inputs:** `docs/company/product/catalog.md`, `docs/company/product/prd-wisp-evidence-pack.md`, `docs/company/market/first-market-selection.md`, `docs/company/competitors/smb-landscape-2026.md`, `docs/company/interviews/recruiting-kit.md` (discovery outreach lives there; this playbook is for selling only), `.claude/skills/authorized-scanning/SKILL.md`, `.claude/skills/outreach-writing/SKILL.md`.

Companion files:
| File | Use |
|---|---|
| `sequences.md` | Ready-to-send email and LinkedIn sequences (4 touches) |
| `call-script.md` | 20-minute sales call, including the exact close |
| `objections.md` | 16 objections with plain-English answers |
| `partners.md` | MSP, community and insurance-broker partner program |
| `pipeline.csv` | The pipeline (header only; no personal data in the repo) |

**Evidence status:** 0 customer interviews, 0 sales. Every conversion rate below is an **assumption** until week 3 data replaces it.

---

## 1. What we sell, in one breath

| Step | Offer | Price | Pitch line |
|---|---|---|---|
| Free | **WISP & Safeguards Readiness Check** (12-question quiz + passive email/domain check) | $0 | "Find the 3 gaps to close before you renew your PTIN." |
| Paid entry | **WISP & Evidence Pack** (concierge, delivered in 7 business days) | `[PACK_PRICE]` one-time (founding price for the first 10 firms) | "A written security plan that describes *your* firm, a one-page evidence report, and your top 5 fixes, in plain English." |
| Recurring | **ChimeraShield Watch** with the "Is this safe?" helpdesk | `[WATCH_PRICE]` (monthly or annual prepay) | "Keeps your evidence current and gives staff a place to forward suspicious emails through tax season." |

**Our wedge (say this, not "AI security"):** a template is a blank form; the Pack is filled in with your firm's facts, checked against what we can actually see, and ends with a short fix list. See `competitors/smb-landscape-2026.md` §3: detection and DMARC scans are free elsewhere, so we never lead with them.

**Never say:** "compliant", "certified", "guaranteed", "IRS-approved", "passes", "you'll never be breached", "continuous monitoring" (Watch is passive outside-in checking only; PRD §7, catalog §5). We don't act as the Qualified Individual and don't give legal advice.

**W-12 wording:** line 11 asks the preparer to confirm they know they are *required by law to create and maintain* a written information security plan ([Form W-12, Rev. Oct 2025](https://www.irs.gov/pub/irs-pdf/fw12.pdf)). Describe it that way. Don't say "the IRS makes you submit your WISP" or "the IRS checks your WISP". **When renewal opens (expected mid-October), re-read the live W-12 and update copy if the line number or wording changed.** Several template vendors claim the 2027 cycle "changed"; that is unverified, so don't repeat it.

---

## 2. Gates: do not take money until these are done

| # | Gate | Owner | Needed for |
|---|---|---|---|
| G1 | Domain + mailbox + SPF/DKIM/DMARC passing (our own domain must pass our own check) | founder / tech-lead | Any cold email |
| G2 | Secondary sending domain registered and warming (e.g. `get[DOMAIN]`), same auth | founder | Cold email volume without risking the main domain |
| G3 | `[POSTAL_ADDRESS]` (virtual mailbox) | founder | CAN-SPAM footer |
| G4 | Readiness Check live (target 15 Oct), or the concierge fallback in §6 | tech-lead | Touch 3 of every sequence |
| G5 | Engagement letter, disclaimer, consent text approved | legal-ops | Taking payment |
| G6 | Entity, bank, Stripe payment link, public ToS/privacy/refund terms | founder / legal-ops | Taking payment |
| G7 | Tech E&O / cyber liability quote bound (`legal/launch-checklist.md` 7.1–7.2) | founder | First paid delivery |
| G8 | `[PACK_PRICE]` and `[WATCH_PRICE]` set | finance-modeler | Every offer message |
| G9 | Legal-ops verifies §314.6 (<5,000 consumers) wording against 16 CFR 314.6 | legal-ops | Objection answers and WISP template |

**If G5–G7 slip past 23 Oct:** keep selling, but take verbal/written intent ("reserve an intake slot") and invoice only when the gates clear. Never take money we can't legally deliver against.

---

## 3. Who we sell to

### 3.1 Target account
- US independent accounting, CPA, EA and tax-prep firms with **5–50 staff**.
- Buyer: **owner / managing partner** (signs, pays, acts as Qualified Individual).
- Helper: **firm administrator / office manager** (gathers intake facts; good entry point, not the decision-maker).

### 3.2 Exact job titles (LinkedIn and directories)
- **Buyer:** Owner, Founder, Managing Partner, Partner (in firms of 5–15), Principal, President, CEO (small firms), "Enrolled Agent" + Owner, "CPA" + Owner.
- **Helper:** Firm Administrator, Practice Manager, Office Manager, Operations Manager, Director of Operations.
- **Exclude:** Staff Accountant, Senior Associate, Tax Associate, students, anyone at a Big 4 / top-100 firm, franchise office staff.

### 3.3 Qualification criteria

**Must have (all):**
1. US-based firm; prepares federal returns for pay (at least one PTIN holder).
2. Independent: not an H&R Block, Jackson Hewitt, Liberty Tax or other franchise office.
3. 5–50 staff (from the website team page, LinkedIn headcount band, or directory "size of practice" filter).
4. Owner or managing partner identifiable by role.
5. A **business** email published by the firm (website contact page, directory listing marked as business contact) or a LinkedIn profile. Otherwise LinkedIn only.

**Priority score (0–10, work highest first):**
| Signal | Points |
|---|---|
| 5–15 staff (owner decides alone; catalog: fastest buyers) | 2 |
| Specific trigger in the last 60 days: posted about PTIN/WISP/security, attending NATP/state CPE event, new office, hiring, merger, new tax software | 2 |
| No MSP / IT provider named on website or LinkedIn | 2 |
| Owner active on LinkedIn in last 30 days | 1 |
| Multiple credentialed preparers (EA/CPA) on the IRS directory in the same firm | 1 |
| In a focus state (`[STATE_1]`, `[STATE_2]`, `[STATE_3]`) | 1 |
| Warm path (mutual connection, partner referral, interviewee referral) | 1 |

**Disqualify or reroute:**
| Situation | Action |
|---|---|
| MSP already maintains their WISP | Offer the free check only; ask for an intro to the MSP (partner lead, `partners.md`) |
| In-house IT staff | Low priority; route to free check |
| 51+ staff | Not now |
| Solo seasonal preparer | Park for a lighter tier (catalog: $195–$295 hypothesis) |
| Canada or EU address | Exclude from cold email (CASL / GDPR) |
| Opted out anywhere | Never contact again; mark `opted_out = Y` |

**Note on prospect research:** do **not** run DNS, MX, DMARC or any other lookup on a prospect's domain before they consent, even though the data is public. Our authorized-scanning rule is "only with explicit permission", and we don't want a prospect to learn we looked. Qualify from what the firm publishes about itself.

### 3.4 Data sources (verified 2026-09-24)

| Source | What it gives | How to use | Verified |
|---|---|---|---|
| **IRS Directory of Federal Tax Return Preparers with Credentials and Select Qualifications** ([irs.gov/chooseataxpro](https://irs.treasury.gov/rpo/rpo.jsf), [FAQ](https://www.irs.gov/tax-professionals/faqs-directory-of-federal-tax-return-preparers-with-credentials-and-select-qualifications)) | Name, city, state, ZIP, credential (CPA, EA, attorney, AFSP record of completion). **No firm size, no email.** Only credentialed/AFSP preparers, not all PTIN holders. | Search by ZIP; clusters of credentialed preparers at the same city/firm suggest a 5+ firm. Then find the firm website for a business contact. | Yes (exists, public) |
| **IRS PTIN FOIA extract** ([IRS page](https://www.irs.gov/tax-professionals/ptin-information-and-the-freedom-of-information-act)) | CSV of PTIN holders who didn't opt out of certain fields: name, business name, business mailing address, phone, website, email, credential. Updated about twice a year. | Use **only** to find firm names and websites. **Do not email addresses from this file**: many are personal addresses preparers entered for IRS contact, and cold-emailing a bulk government extract looks like a purchased list. Also: WISP template vendors appear to mine this file heavily, so prospects are already getting template spam; our first line must be visibly specific. | Yes (exists) |
| **NAEA Find a Tax Expert** ([taxexperts.naea.org](https://taxexperts.naea.org/)) | Enrolled agents by location, often with firm name and website | EA-owned firms; check website for team size | Yes (recruiting kit) |
| **NATP Find a Tax Pro** ([natptax.com/directory](https://www.natptax.com/directory/)) | Members who made profiles public: business info, contact details, specialties | Business contact details are published by the member for that purpose, so usable for relevant B2B outreach; still prefer the firm website address | Yes |
| **State CPA society "Find a CPA" directories** (e.g. [Louisiana](https://www.louisiana.cpa/find-a-cpa) has a *size of practice* filter; [Arizona](https://www.ascpa.com/find-a-cpa), [Illinois](https://www.icpas.org/Find_A_CPA/CPA_Search.aspx), [Massachusetts](https://www.masscpas.org/find-a-cpa), [Connecticut](https://www.ctcpas.org/find-a-cpa), [CalCPA](https://findcpa.calcpa.org/), [Washington](https://www.wscpa.org/find-a-cpa)) | Member firms by city, services, sometimes size | Pick focus states whose directory filters by size. Read each directory's terms of use first; some prohibit commercial solicitation. If so, use it for research only and contact via LinkedIn. | Yes (directories exist; terms not checked) |
| **LinkedIn / Sales Navigator** | Titles above; Industry = Accounting; Headcount 2–10 and 11–50; Geography = focus states; "Posted in last 30 days" | Primary channel before email is warm. **Free accounts get very few personalized invitation notes per month (verify current limit); budget for Sales Navigator or Premium for the 10 selling weeks.** | Filters: per recruiting kit |
| **Google Maps** ("CPA" / "tax preparation" + city) | Firm website, reviews, office count | Cross-check size from website team page | n/a |
| **Events**: NATP Tax Forums Las Vegas (21–22 Oct 2026); state CPA society CPE calendars | Attendee posts on LinkedIn = trigger | Sequence B in `sequences.md` | Dates per recruiting kit |

**Not a source:** purchased lists, scraped personal emails, data-broker "CPA email lists", Canadian/EU contacts.

---

## 4. Pipeline

### 4.1 Stages (`stage` column)
| Stage | Definition | Exit criteria |
|---|---|---|
| `0-identified` | Firm found, not yet checked | Qualification done |
| `1-qualified` | Meets must-haves; priority score recorded | First touch sent |
| `2-sequenced` | In an email/LinkedIn sequence | Reply, check completed, or sequence ends |
| `3-engaged` | Replied positively or started the Readiness Check | Consent recorded or call booked |
| `4-check-done` | Readiness Check completed, consent recorded, result sent to work address | Call booked |
| `5-call-booked` | 20-min sales call scheduled | Call held |
| `6-call-held` | Call held, Pack offered | Payment link sent or lost/nurture |
| `7-link-sent` | Engagement letter + payment link sent | Paid |
| `8-won-paid` | Paid | Intake held |
| `9-delivered` | WISP, Evidence Report, Fix-First plan delivered; debrief held | Watch decision |
| `10-watch` | Watch started | n/a |
| `lost` | Said no (record `lost_reason`) | n/a |
| `nurture-may` | "Not now, ask me after April 15" | Re-contact in May 2027 |
| `opted-out` | Asked not to be contacted | Never contact again |

### 4.2 `pipeline.csv` columns
`id, firm_name, firm_website, city_state, firm_type, staff_band, contact_role, source, priority_score, trigger, has_msp, email_platform, channel, sequence, touch_step, stage, last_touch_date, next_step, next_step_date, readiness_check, consent_recorded_date, call_date, offer, amount, watch_status, partner_ref, lost_reason, opted_out, notes`

Rules:
- **No personal data in the repo.** No contact names, personal emails, phone numbers, or findings. Keep names and email addresses in the CRM/mail tool (outside git) and join on `id`.
- `firm_type`: `CPA`, `EA`, `tax-prep`, `mixed`. `staff_band`: `5-15`, `16-30`, `31-50`.
- `has_msp` and `email_platform` come **only** from what the owner tells us (or post-consent checks), never from pre-consent lookups.
- `notes`: no findings, no client data, no security weaknesses. Write "3 gaps shared on call" not the gaps themselves. Findings live in the encrypted findings store (PRD AC15).
- Dates in ISO format (`2026-10-12`).

---

## 5. Weekly activity targets (working backward)

### 5.1 Assumed conversion rates (all assumptions, replace with actuals weekly)
| Step | Rate | Why this number |
|---|---|---|
| Qualified prospect sequenced → engaged (positive reply or check started) | **8%** blended | Cold email alone may be 3–5%; LinkedIn, warm paths, event triggers and partners pull the blend up. Recruiting kit assumes 10–20% for warm research asks; a sales ask is harder. |
| Engaged → sales call held | **50%** | Many will take the free check and stop. |
| Call held → Pack purchased | **25%** | Deadline-driven, owner decides alone, but we're unknown with no testimonials. PRD kill signal is 0 from 30 calls. |
| **Prospects needed per customer** | **≈100** | 1 ÷ (0.08 × 0.5 × 0.25) |
| Partner-referred lead → purchase | 40% | Trust transfers from partner (assumption) |

**Plan:** 6 customers (buffer above the 3 floor) → ~24 calls → ~48 engaged → **~500 qualified prospects sequenced** over 8 selling weeks, plus 1–2 partner-referred closes.

### 5.2 Capacity limits
- Email warm-up (outreach-writing skill): 5–10 sends/day in week 1, ~30/day by week 4. Sends include follow-ups (each prospect gets up to 4 touches).
- Delivery: ≤6 founder hours per pack for the first 3, ≤4 after (PRD AC14). **Max 3 intake calls per week.** That makes "limited intake slots" in the close true.
- Last intake call **Fri 4 Dec** so delivery lands by 15 Dec. Closes on 7–11 Dec only if an intake slot exists and delivery can land before 23 Dec.

### 5.3 Week-by-week targets

| Week (Mon) | Focus | New prospects sequenced (email / LinkedIn / warm+partner) | Email sends/day cap | Calls held | Packs closed (cum.) | Partner actions |
|---|---|---|---|---|---|---|
| **Prep 1** 28 Sep | Gates G1–G3; register sending domain; build list of 150 qualified firms; Sales Nav on | 0 (discovery interviews continue per recruiting kit) | 0 (warm-up only) | 0 | 0 | Pick 10 target partners |
| **Prep 2** 5 Oct | List to 300; write personalization lines for first 60; G5–G8 chase | 15 LinkedIn (warm, soft) | 0–5 | 0 | 0 | Pitch 3 partners |
| **S1** 12 Oct | Renewal window opens; check live 15 Oct | 40 (20 / 15 / 5) | 10 | 1 | 0 | Pitch 3 |
| **S2** 19 Oct | NATP Las Vegas trigger (Seq B) | 60 (35 / 20 / 5) | 15 | 2 | 0 | Pitch 2; 1 partner call |
| **S3** 26 Oct | Full cadence | 75 (45 / 20 / 10) | 25 | 3 | 1 | 1 partner live |
| **S4** 2 Nov | **Checkpoint 1** (§5.4) | 80 (50 / 20 / 10) | 30 | 4 | 2 | Partner webinar/post |
| **S5** 9 Nov | Full cadence | 80 (50 / 20 / 10) | 30 | 4 | 3 | 2nd partner live |
| **S6** 16 Nov | **Checkpoint 2** | 80 (50 / 20 / 10) | 30 | 4 | 4 | Partner referrals |
| **S7** 23 Nov | Thanksgiving (26 Nov): Mon–Wed only | 40 (25 / 10 / 5) | 30 | 2 | 5 | n/a |
| **S8** 30 Nov | Last new prospects; "last intake slots before 4 Dec" | 50 (30 / 10 / 10) | 30 | 4 | 6 | Thank partners, pay fees |
| **S9** 7 Dec | No new cold prospects; finish sequences; debriefs; Watch offers | 0 | follow-ups only | 1–2 | 6–7 | n/a |
| **S10** 14–15 Dec | Close out; move open deals to `nurture-may` | 0 | 0 | 0 | **Target 6 (floor 3)** | n/a |
| **Total** | | **~505** | | **~25** | **6** | |

**Daily rhythm (selling weeks):** 60 min list building and personalization (next day's 12–16 prospects), 45 min sends and follow-ups, 20 min LinkedIn comments on target owners' posts, calls in two fixed blocks (Tue/Thu 10–12 local to the prospect), 30 min pipeline update. Fridays: delivery work and the weekly review.

### 5.4 Checkpoints and pivot rules
| When | If | Then |
|---|---|---|
| End of S2 (23 Oct) | Engaged rate < 4% on 100 sequenced | Rewrite touch 1 (sharper trigger lines); shift volume to LinkedIn + partners |
| **Checkpoint 1**, end of S4 (6 Nov) | < 6 calls held, or 0 closes from ≥ 6 calls | Review call recordings/notes for the #1 objection; test price (founding vs list) with finance-modeler; push partner channel |
| **Checkpoint 2**, end of S6 (20 Nov) | < 2 closes | Offer a lighter tier (solo/small, catalog §5) and a "WISP only" option; ask every "no" what they'd pay |
| 1 Dec | 0 sales from 30+ qualified conversations, **or** 3+ of first 6 interviews anchor WISP value < $100 | PRD kill/pivot rule: move to self-serve $79–$149 generator (catalog §5) |
| Any week | A close rate > 40% | Raise price for the next 5 (finance-modeler), keep founding promise to existing buyers |

### 5.5 Metrics to report every Friday
Sequenced, engaged, checks completed, calls held, links sent, packs paid, revenue, Watch starts, opt-outs, bounces (> 3% = pause and clean list), top objection, partner referrals.

---

## 6. Readiness Check fallback (if G4 slips)

Run it concierge, still passive-only and consented:
1. Prospect replies from an address **on their firm's domain** asking for the check.
2. Send them the consent text (PRD §7) and the 12 questions as a reply-able list. Consent must come back **in writing from that work address**, with the domain named.
3. Log consent (domain, role, UTC time) outside the repo, set `consent_recorded_date` in the pipeline.
4. Run only passive checks: MX, SPF, DKIM (selectors they name), DMARC, TLS certificate, headers from one normal homepage load. Nothing else.
5. Send the plain-English result **only** to the consenting work address within 24h, ending with a call invite.

Never send results to a free-mail address, a different domain, or anyone who didn't consent.

---

## 7. Compliance rules for every message

- Real sender: `[FOUNDER_NAME]`, Founder, ChimeraShield, `[FOUNDER_NAME]@[DOMAIN]`, `[POSTAL_ADDRESS]`. Accurate, non-deceptive subject lines.
- Every email has the opt-out line; honor it immediately (legal max: 10 business days) and mark `opted_out = Y`.
- US business addresses only. No Canadian (CASL) or EU/UK (GDPR/PECR) prospects in cold email.
- No purchased lists; no emails from the PTIN FOIA file; no scraped personal addresses.
- No unsolicited findings about a prospect's domain. Demos use a company-owned demo domain unless the prospect consented.
- No invented customers, testimonials, logos, stats or certifications. Until we have customers, say so plainly: "You'd be one of our first 10 firms."
- Stats allowed in copy only after the source is opened and checked (market doc warning). Default: no stats.
- Stop a sequence on any reply, including "not now".

---

## 8. After the sale

1. Payment → confirmation with intake checklist and booking link (PRD AC1).
2. Intake (60 min) → deliverables within 7 business days → debrief (30 min) with the AC12 understanding test.
3. At debrief: offer Watch (`call-script.md` §6) and ask for 2 referrals: "Which other firm owner would want this before their renewal?"
4. Day 14: check-in email on the #1 fix.
5. Ask for a testimonial **only** after delivery, in the customer's words, with written permission to use their name. Never paraphrase into claims we can't back.
