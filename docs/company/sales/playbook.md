# Sales Playbook: first paying customers (accounting / tax-prep, PTIN window 2026)

**Owner:** head-of-sales (founder-led) · **Date:** 2026-09-24 · **Updated:** 2026-09-26 (founder is in Australia: Spam Act 2003, consent evidence, Sydney call blocks, revised targets, Australian pilot) · **Status:** draft, ready to run once the gates in §2 are cleared
**Goal:** 3 paid WISP & Evidence Packs by 15 Dec 2026 (floor), 5–6 (plan), 10 (ceiling, capped by founder delivery capacity). **Plus** 1–2 paid Australian pilots, 3 Nov – 11 Dec (`australia-pilot.md`).
**Inputs:** `docs/company/product/catalog.md`, `docs/company/product/prd-wisp-evidence-pack.md`, `docs/company/market/first-market-selection.md`, `docs/company/market/australia-vs-us.md`, `docs/company/legal/spam-act-cold-email.md`, `docs/company/legal/australia-founder.md`, `docs/company/competitors/smb-landscape-2026.md`, `docs/company/interviews/recruiting-kit.md` (discovery outreach lives there; this playbook is for selling only), `.claude/skills/authorized-scanning/SKILL.md`, `.claude/skills/outreach-writing/SKILL.md`.

Companion files:
| File | Use |
|---|---|
| `sequences.md` | Ready-to-send email and LinkedIn sequences (4 touches), with the Spam Act + CAN-SPAM footer |
| `call-script.md` | 20-minute sales call, including the exact close |
| `objections.md` | 16 objections with plain-English answers |
| `partners.md` | MSP, community and insurance-broker partner program |
| `australia-pilot.md` | Plan C: 1–2 paid Australian pilots of the Client Data Security Pack (TPB & TFN ready) |
| `pipeline.csv` | The pipeline (header only; no personal data in the repo) |

**Evidence status:** 0 customer interviews, 0 sales. Every conversion rate below is an **assumption** until week 3 data replaces it.

**What changed on 2026-09-26 (read this first).** The founder sends from Australia, so every email and commercial LinkedIn message to a US firm has an "Australian link" and falls under the **Spam Act 2003** as well as CAN-SPAM (`legal/spam-act-cold-email.md` §1). In practice: (1) email only addresses the firm or person **published themselves**, where the message relates to their role, with evidence saved per address; (2) no Apollo-type databases, enrichment tools, scrapers or guessed addresses; (3) every email carries the **ABN** and an unsubscribe line honoured within 5 business days (our standard: same day); (4) LinkedIn connection notes stay non-commercial and we pitch in DMs only after interest. The emailable list is smaller, so volume shifts to LinkedIn, partners and opt-in leads (§5).

---

## 1. What we sell, in one breath

| Step | Offer | Price | Pitch line |
|---|---|---|---|
| Free | **WISP & Safeguards Readiness Check** (12-question quiz + passive email/domain check) | $0 | "Find the 3 gaps to close before you renew your PTIN." |
| Paid entry | **WISP & Evidence Pack** (concierge, delivered in 7 business days) | `[PACK_PRICE]` one-time (founding price for the first 10 firms) | "A written security plan that describes *your* firm, a one-page evidence report, and your top 5 fixes, in plain English." |
| Recurring | **ChimeraShield Watch** with the "Is this safe?" helpdesk | `[WATCH_PRICE]` (monthly or annual prepay) | "Keeps your evidence current and gives staff a place to forward suspicious emails through tax season." |

**Our wedge (say this, not "AI security"):** a template is a blank form; the Pack is filled in with your firm's facts, checked against what we can actually see, and ends with a short fix list. See `competitors/smb-landscape-2026.md` §3: detection and DMARC scans are free elsewhere, so we never lead with them.

**Never say:** "compliant", "certified", "guaranteed", "IRS-approved", "passes", "you'll never be breached", "continuous monitoring" (Watch is passive outside-in checking only; PRD §7, catalog §5). We don't act as the Qualified Individual and don't give legal advice. **Australian copy** has its own list (`australia-pilot.md` §1): never "WISP", "certified" or "compliant".

**W-12 wording:** line 11 asks the preparer to confirm they know they are *required by law to create and maintain* a written information security plan ([Form W-12, Rev. Oct 2025](https://www.irs.gov/pub/irs-pdf/fw12.pdf)). Describe it that way. Don't say "the IRS makes you submit your WISP" or "the IRS checks your WISP". **When renewal opens (expected mid-October), re-read the live W-12 and update copy if the line number or wording changed.** Several template vendors claim the 2027 cycle "changed"; that is unverified, so don't repeat it.

---

## 2. Gates: do not take money until these are done

| # | Gate | Owner | Needed for |
|---|---|---|---|
| G1 | Domain + mailbox + SPF/DKIM/DMARC passing (our own domain must pass our own check) | founder / tech-lead | Any cold email |
| G2 | Secondary sending domain registered and warming (e.g. `get[DOMAIN]`), same auth | founder | Cold email volume without risking the main domain |
| G3 | `[US_POSTAL_ADDRESS]` (US virtual mailbox preferred; lawyer to confirm whether an Australian address satisfies CAN-SPAM) | founder | CAN-SPAM footer |
| **G3a** | **Entity and `[ABN]`** (ChimeraShield Pty Ltd, target ~2 Oct). If it slips: send as a sole trader with the founder's own ABN and name, or delay cold email. | founder / legal-ops | **Spam Act footer on every email and commercial DM. No ABN, no cold send on 12 Oct.** |
| **G3b** | **Consent-evidence Sheet** set up outside git (columns in §3.5) plus an evidence folder in Drive; suppression list tab | founder | Every cold email ("no evidence, no send") |
| **G3c** | Lawyer sign-off on footer wording and directory sources (`spam-act-cold-email.md` "Needs a lawyer" 1–3) | legal-ops | Using any directory address; final footer |
| G4 | Readiness Check live (target 15 Oct), or the concierge fallback in §6. Sign-up form has an **unticked marketing opt-in box** (express consent) | tech-lead | Touch 3 of every sequence |
| G5 | Engagement letter, disclaimer, consent text approved | legal-ops | Taking payment |
| G6 | Entity, bank, Stripe payment link, public ToS/privacy/refund terms | founder / legal-ops | Taking payment |
| G7 | Tech E&O / cyber liability quote bound, **with US/Canada jurisdiction** (`legal/australia-founder.md` §4) | founder | First paid delivery |
| G8 | `[PACK_PRICE]` and `[WATCH_PRICE]` set | finance-modeler | Every offer message |
| G9 | Legal-ops verifies §314.6 (<5,000 consumers) wording against 16 CFR 314.6 | legal-ops | Objection answers and WISP template |

**If G5–G7 slip past 23 Oct:** keep selling, but take verbal/written intent ("reserve an intake slot") and invoice only when the gates clear. Never take money we can't legally deliver against.
**If G3c is not back by 12 Oct:** email only addresses from **firm websites** (the clearest case) and treat every directory as research-only until the lawyer answers.

---

## 3. Who we sell to

### 3.1 Target account
- US independent accounting, CPA, EA and tax-prep firms with **5–50 staff**, **weighted to Pacific and Mountain states** (e.g. CA, WA, OR, AZ, CO, NV) because their whole afternoon falls inside our Sydney call block (§5.6).
- Buyer: **owner / managing partner** (signs, pays, acts as Qualified Individual).
- Helper: **firm administrator / office manager** (gathers intake facts; good entry point, not the decision-maker). **Email a helper only if the firm's site shows they handle operations or IT**; otherwise email the owner or use LinkedIn.

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
5. **Email only if** there is a business address **published by the firm or by the person themselves** (firm website, or their own directory profile where the directory's terms allow solicitation), **with no "no marketing / no solicitation" statement**, **relevant to their role**, and **evidence saved** (§3.5). Otherwise the prospect is **LinkedIn-only** or waits for a warm path.

**Priority score (0–10, work highest first):**
| Signal | Points |
|---|---|
| 5–15 staff (owner decides alone; catalog: fastest buyers) | 2 |
| Specific trigger in the last 60 days: posted about PTIN/WISP/security, attending NATP/state CPE event, new office, hiring, merger, new tax software | 2 |
| No MSP / IT provider named on website or LinkedIn | 2 |
| Owner active on LinkedIn in last 30 days | 1 |
| Multiple credentialed preparers (EA/CPA) on the IRS directory in the same firm | 1 |
| In a Pacific/Mountain focus state (`[STATE_1]`, `[STATE_2]`, `[STATE_3]`; suggested CA, WA, AZ or CO) | 1 |
| Warm path or express consent (mutual connection, partner referral, interviewee, Readiness Check opt-in) | 1 |

**Disqualify or reroute:**
| Situation | Action |
|---|---|
| MSP already maintains their WISP | Offer the free check only; ask for an intro to the MSP (partner lead, `partners.md`) |
| In-house IT staff | Low priority; route to free check |
| 51+ staff | Not now |
| Solo seasonal preparer | Park for a lighter tier (catalog: $195–$295 hypothesis) |
| Canada or EU address | Exclude from cold email (CASL / GDPR) |
| Address found only via a database, enrichment tool, guess or PDF | Don't email. LinkedIn-only |
| "No solicitation" note on the page, or directory terms ban solicitation | Don't email that address. LinkedIn-only |
| Opted out anywhere (email, LinkedIn, phone) | Never contact again on any channel; mark `opted_out = Y`; suppress the whole firm unless someone else there asked to hear from us |

**Note on prospect research:** do **not** run DNS, MX, DMARC or any other lookup on a prospect's domain before they consent, even though the data is public. Our authorized-scanning rule is "only with explicit permission", and we don't want a prospect to learn we looked. Qualify from what the firm publishes about itself.

### 3.4 Data sources (updated 2026-09-26 for the Spam Act)

| Source | What it gives | Can we email addresses from it? | How to use |
|---|---|---|---|
| **Firm's own website** (contact, team or "about" page) | Owner/staff names, roles, team size, sometimes a named business address | **Yes**, if the address is shown there, there's no "no solicitation" note, and the person's role makes the message relevant. **Best source.** Save a PDF/screenshot. Prefer the owner's published address over `info@` | Primary email source |
| **IRS Directory of Federal Tax Return Preparers** ([irs.gov/chooseataxpro](https://irs.treasury.gov/rpo/rpo.jsf)) | Name, city, state, ZIP, credential. No email, no firm size | **No** (no emails) | Research: clusters of credentialed preparers at one firm suggest 5+ staff. Then find the firm website |
| **IRS PTIN FOIA extract** ([IRS page](https://www.irs.gov/tax-professionals/ptin-information-and-the-freedom-of-information-act)) | Bulk CSV of PTIN holders | **Never.** Research only (firm names and websites) | Many addresses are personal; a bulk government extract is not "published by the person for business enquiries" |
| **NAEA Find a Tax Expert** ([taxexperts.naea.org](https://taxexperts.naea.org/)) | EAs by location, firm name, website | **Only after** the terms are checked and the lawyer confirms (G3c), and the profile has no anti-marketing statement. Until then, research only | Find EA-owned firms, then use the firm website |
| **NATP Find a Tax Pro** ([natptax.com/directory](https://www.natptax.com/directory/)) | Member-published business contact details | Same as NAEA: **only after** terms check and G3c | Prefer the firm website address anyway |
| **State CPA society "Find a CPA"** ([CalCPA](https://findcpa.calcpa.org/), [Washington](https://www.wscpa.org/find-a-cpa), [Arizona](https://www.ascpa.com/find-a-cpa), others in older notes) | Member firms by city, services, sometimes size | **Treat as research only.** Many directory terms prohibit commercial solicitation, and we read that as a "no marketing" statement | Pick Pacific/Mountain focus states; research, then website or LinkedIn |
| **LinkedIn / Sales Navigator** | Titles in §3.2; Industry = Accounting; Headcount 2–10 and 11–50; Geography = focus states; "Posted in last 30 days" | **Don't take email addresses from LinkedIn profiles** (untested as "conspicuous publication") | Non-commercial connection note; pitch only after interest (`sequences.md` L). **No automation tools.** Budget Sales Navigator or Premium for the 10 selling weeks |
| **Google Maps** ("CPA" / "tax preparation" + city) | Firm website, reviews, office count | No (follow through to the website) | Size cross-check |
| **Events**: NATP Tax Forums Las Vegas (21–22 Oct 2026); state CPA society CPE calendars | Attendee posts on LinkedIn = trigger | n/a | Sequence B / A1-EVENT |
| **Express-consent and warm sources** | Readiness Check sign-ups with the marketing box ticked; Google Ads landing-page opt-ins; partner introductions; interviewees who asked to hear more; people who reply to or comment on the founder's posts asking for info | **Yes** (express consent or existing relationship). Record the form, date or intro | **Highest priority.** Converts best and carries the least risk |

**Banned as a source (no exceptions):** Apollo, Hunter, ZoomInfo, RocketReach, Clearbit or any enrichment/"email finder" tool; "CPA email lists" or any purchased list; browser extensions or scrapers that collect addresses; guessed patterns (`firstname@firm.com`); addresses from PDFs, conference attendee lists or the PTIN extract; any "can I send you info?" permission email (a consent request is itself a commercial message). Apollo may only ever be a **sending** tool with our own evidenced list, and GMass is still the recommendation (`cold-email-launch-kit.md` Step 6).

**Expected yield (assumption, measure in Prep 1):** about **40%** of qualified firms will have an owner or ops address that passes all four tests. The other ~60% go to LinkedIn or wait for a warm path. Replace this number with the real share after the first 100 firms are researched.

### 3.5 Per-contact consent evidence

Every emailed contact has one evidence row. **No evidence, no send.** The full record lives in the founder's Google Sheet and Drive folder (outside git, because it contains names and addresses). `pipeline.csv` carries the three columns that contain no personal data: `consent_basis`, `published_source_url` and `country`.

| Column (Sheet) | Content | Also in `pipeline.csv`? |
|---|---|---|
| `id` | Joins to `pipeline.csv` | yes |
| `email` | The exact published address | **no** (personal data) |
| `consent_basis` | `inferred: conspicuous publication` / `express: [form or intro], [date]` / `inferred: existing relationship` / `none: LinkedIn only` | **yes** |
| `published_source_url` | The exact page showing the address (firm page, or own directory profile) | **yes** (firm/directory page URL only; never a personal page) |
| `source_checked_date` | ISO date the page was checked | no |
| `evidence_file` | Drive link to the saved PDF/screenshot | no |
| `no_marketing_statement` | `none seen` / `present → excluded` | no |
| `directory_terms_ok` | `n/a (firm site)` / `yes` / `no → excluded` | no |
| `role` | Owner / Managing partner / QI / Ops lead with IT role / generic inbox | `contact_role` |
| `country` | `US` / `AU` | **yes** |

Keep evidence for at least 2 years after the last message (legal-ops to confirm the period). The burden of showing consent is on us.

---

## 4. Pipeline

### 4.1 Stages (`stage` column)
| Stage | Definition | Exit criteria |
|---|---|---|
| `0-identified` | Firm found, not yet checked | Qualification done |
| `1-qualified` | Meets must-haves; priority score and consent basis recorded | First touch sent |
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
| `nurture-may` | "Not now, ask me after April 15" (AU: `nurture-feb`) | Re-contact in May 2027 (AU: Feb 2027) |
| `opted-out` | Asked not to be contacted | Never contact again |

### 4.2 `pipeline.csv` columns
`id, firm_name, firm_website, city_state, country, firm_type, staff_band, contact_role, source, consent_basis, published_source_url, priority_score, trigger, has_msp, email_platform, channel, sequence, touch_step, stage, last_touch_date, next_step, next_step_date, readiness_check, consent_recorded_date, call_date, offer, amount, watch_status, partner_ref, lost_reason, opted_out, notes`

Rules:
- **No personal data in the repo.** No contact names, personal emails, phone numbers, or findings. Keep names and email addresses in the CRM/mail tool and evidence Sheet (outside git) and join on `id`.
- `country`: `US` or `AU`. `firm_type`: `CPA`, `EA`, `tax-prep`, `mixed` (US); `AU-tax-agent`, `AU-accounting`, `AU-BAS` (AU). `staff_band`: `5-15`, `16-30`, `31-50`.
- `source`: the source type (`firm-site`, `naea`, `natp`, `state-society`, `linkedin`, `partner:[CODE]`, `readiness-check`, `ads-optin`, `event`, `tpb-register`, `cpa-au`, `caanz`, `ipa`, `au-network`).
- `consent_basis`: one of the four values in §3.5. **A row with `none: LinkedIn only` must never be loaded into the mail tool.**
- `published_source_url`: the firm or directory page URL where the address appears; `n/a` for LinkedIn-only and express-consent rows (record the form/intro in `consent_basis`).
- `has_msp` and `email_platform` come **only** from what the owner tells us (or post-consent checks), never from pre-consent lookups.
- `notes`: no findings, no client data, no security weaknesses. Write "3 gaps shared on call" not the gaps themselves. Findings live in the encrypted findings store (PRD AC15).
- Dates in ISO format (`2026-10-12`).

---

## 5. Weekly activity targets (working backward)

### 5.1 Assumed conversion rates (all assumptions, replace with actuals weekly)

The Spam Act shrinks the emailable pool (§3.4 yield ~40%) and slows LinkedIn (no pitch until interest), so rates are now set **per channel**.

| Channel | Qualified prospect → engaged | Why |
|---|---|---|
| Cold email (evidenced, published address) | **5%** | Cold email alone is often 3–5%; strong PTIN trigger and a hand-written first line |
| LinkedIn (non-commercial connect → discovery question → offer on interest) | **7%** | Slower, but the owner chooses to hear the offer |
| Warm / partner / express opt-in (Readiness Check, ads opt-in, intros, interviewees) | **20%** | They asked or were introduced |

| Step | Rate |
|---|---|
| Engaged → sales call held | **50%** |
| Call held → Pack purchased | **25%** (PRD kill signal: 0 from 30 calls) |
| Partner-referred lead → purchase | 40% |

**Plan:** 6 customers → ~24 calls → ~48 engaged. Mix: **160 email × 5% = 8**, **210 LinkedIn × 7% ≈ 15**, **120 warm/partner/opt-in × 20% = 24**, so **~47 engaged from ~490 prospects**. To find 160 emailable firms at ~40% yield, research **~400 qualified firms**; the rest feed LinkedIn.
**What moved:** email down from ~305 to ~160; LinkedIn up from ~130 to ~210; warm/partner/opt-in up from ~65 to ~120. The plan now leans on partners (`partners.md`) and on Readiness Check and Google Ads opt-ins far more than before. If the warm column misses by week S3, the floor (3) is still reachable; the plan (6) is not.

### 5.2 Capacity limits
- **Founder time: about 80% US, 20% Australia** (market plan C). The AU pilot work sits in Sydney business hours, after the US call block (`australia-pilot.md` §6).
- Email sending caps are now **ceilings, not targets**: at ~20–25 new emails a week, expect **≤8 new first touches and ≤25 total sends a day**. Warm-up still follows `cold-email-launch-kit.md` Steps 4–5.
- List building is slower: capturing evidence adds about 3 minutes per emailable contact.
- Delivery: ≤6 founder hours per pack for the first 3, ≤4 after (PRD AC14). **Max 3 intake calls per week across US and AU combined.** That makes "limited intake slots" in the close true.
- Last intake call **Fri 4 Dec (US time)** so delivery lands by 15 Dec. Closes on 7–11 Dec only if an intake slot exists and delivery can land before 23 Dec.

### 5.3 Week-by-week targets (US; AU pilot targets are in `australia-pilot.md` §7)

| Week (Mon) | Focus | New prospects (email / LinkedIn / warm+partner+opt-in) | Firms researched (evidence captured) | Email sends/day cap (total) | Calls held | Packs closed (cum.) | Partner actions |
|---|---|---|---|---|---|---|---|
| **Prep 1** 28 Sep | Gates G1–G3b; ABN; evidence Sheet; Sales Nav on; measure the real email yield | 0 | 100 | 0 (warm-up only) | 0 | 0 | List 20 candidates; pitch 3 (partner emails follow the same rules) |
| **Prep 2** 5 Oct | Research to 200; first 40 personal lines; G3c, G5–G8 chase | 20 (0 / 15 / 5) | 100 | 0 | 0 | 0 | Pitch 3 |
| **S1** 12 Oct | Renewal window opens; check live 15 Oct; first cold sends only if G3a is done | 40 (15 / 20 / 5) | 60 | 10 | 1 | 0 | Pitch 3 |
| **S2** 19 Oct | NATP Las Vegas trigger (A1-EVENT, LinkedIn comments) | 55 (20 / 25 / 10) | 60 | 15 | 2 | 0 | Pitch 2; 1 partner call |
| **S3** 26 Oct | Full cadence | 70 (25 / 30 / 15) | 40 | 20 | 3 | 1 | 1 partner live |
| **S4** 2 Nov | **Checkpoint 1** (§5.4); AU pilot outreach starts 3 Nov | 75 (25 / 30 / 20) | 20 | 25 | 4 | 2 | Partner webinar/post |
| **S5** 9 Nov | Full cadence | 75 (25 / 30 / 20) | 20 | 25 | 4 | 3 | 2nd partner live |
| **S6** 16 Nov | **Checkpoint 2** | 75 (25 / 30 / 20) | 0 | 25 | 4 | 4 | Partner referrals |
| **S7** 23 Nov | Thanksgiving (26 Nov): US Mon–Wed only | 35 (10 / 15 / 10) | 0 | 25 | 2 | 5 | n/a |
| **S8** 30 Nov | Last new prospects; "last intake slots before 4 Dec" | 45 (15 / 15 / 15) | 0 | 25 | 3 | 6 | Thank partners, pay fees |
| **S9** 7 Dec | No new cold prospects; finish sequences; debriefs; Watch offers | 0 | 0 | follow-ups only | 1–2 | 6–7 | n/a |
| **S10** 14–15 Dec | Close out; move open deals to `nurture-may` | 0 | 0 | 0 | 0 | **Target 6 (floor 3)** | n/a |
| **Total** | | **~490 (160 / 210 / 120)** | **~400** | | **~24** | **6** | |

**Daily rhythm (selling weeks, Sydney time; see §5.6):**
- **07:00–10:00 Tue–Fri: US call block** (US Mon–Thu afternoons). Empty slots go to LinkedIn replies and follow-ups while US owners are online.
- 10:30–11:30: list research and evidence capture (next day's 4–6 emailable firms plus 6–8 LinkedIn-only firms).
- 11:30–12:00: load and **schedule** next day's email sends for 08:00–11:00 recipient time (the tool sends overnight Sydney time; never send by hand at night).
- 13:00–15:00 (from 3 Nov): Australian pilot work (`australia-pilot.md`).
- 15:00–15:30: LinkedIn comments on target owners' posts; pipeline update.
- **Monday (Sydney) = US Sunday:** no US calls. Delivery work, the weekly review and the §5.5 metrics. Keep Saturday (US Friday afternoon) free unless a prospect asks for it.
- Stop by 17:00. Early starts every weekday for 9 weeks carry a real burnout risk; protect the afternoons.

### 5.4 Checkpoints and pivot rules
| When | If | Then |
|---|---|---|
| End of Prep 1 (2 Oct) | Emailable yield < 25% of researched firms | Drop email to ~100 total; move 60 into LinkedIn and push partners and opt-ins harder |
| End of S2 (23 Oct) | Engaged rate < 3% on the first 35 emails, or LinkedIn acceptance < 25% | Rewrite touch 1 / connection note (sharper trigger lines); shift volume to partners and the Readiness Check |
| **Checkpoint 1**, end of S4 (6 Nov) | < 6 calls held, or 0 closes from ≥ 6 calls | Review call notes for the #1 objection; test price (founding vs list) with finance-modeler; push partner channel. Market-doc risk 1: if US calls < 6 **and** AU converts 2+ pilots, flag option B for 2027 |
| **Checkpoint 2**, end of S6 (20 Nov) | < 2 closes | Offer a lighter tier (solo/small, catalog §5) and a "WISP only" option; ask every "no" what they'd pay |
| 1 Dec | 0 sales from 30+ qualified conversations, **or** 3+ of first 6 interviews anchor WISP value < $100 | PRD kill/pivot rule: move to self-serve $79–$149 generator (catalog §5) |
| Any week | A close rate > 40% | Raise price for the next 5 (finance-modeler), keep founding promise to existing buyers |
| Any week | Any Spam Act complaint, or an unsubscribe not actioned the same day | Pause cold email, tell legal-ops, review the evidence rows for that source |

### 5.5 Metrics to report every week (Monday, Sydney)
Firms researched, emailable yield %, sequenced (by channel), engaged (by channel), checks completed, calls held, links sent, packs paid, revenue, Watch starts, opt-outs (and time to action), bounces (> 3% = pause and clean list), top objection, partner referrals, AU pilot status.

### 5.6 Time zones (founder in Sydney; adjust if the founder is in Brisbane or Perth)

| Period | Sydney call block | Pacific | Mountain (CO) | Arizona (no DST) | Eastern |
|---|---|---|---|---|---|
| 4 Oct – 1 Nov (AEDT UTC+11; US on daylight time) | **07:00–10:00** | 13:00–16:00 (previous day) | 14:00–17:00 | 13:00–16:00 | 16:00–19:00 (too late; avoid) |
| From 2 Nov (US standard time) | **07:00–10:00** | 12:00–15:00 (previous day) | 13:00–16:00 | 13:00–16:00 | 15:00–18:00 (first hour only) |

- **Prefer Pacific and Mountain firms.** Eastern firms get the 07:00 slot only (15:00–16:00 ET after 1 Nov), or email/LinkedIn follow-up.
- US Tuesday afternoon = Sydney Wednesday morning. When booking, always write both: "Tuesday 1:00 pm PT (Wednesday 7:00 am Sydney)". Put the prospect's time first in every email.
- Booking link: offer only Sydney 07:00–10:00 Tue–Fri slots, shown to the prospect in their own time zone.
- Brisbane (no DST): the same US times fall at 06:00–09:00. Perth: 04:00–07:00, so Perth would need an evening block instead (21:00–23:00 reaches US mornings).
- Thanksgiving week: no US calls on Sydney Fri 27 and Sat 28 Nov.

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

We send from Australia to the US, so **both** the Spam Act 2003 (Australia) and CAN-SPAM (US) apply to every email and commercial DM (`legal/spam-act-cold-email.md`). Where they differ, follow the stricter rule.

- **Consent before the first message (Spam Act).** Email only: (a) people who gave express consent (form with opt-in, reply asking for info, partner intro they agreed to), (b) existing relationships, or (c) addresses **the firm or person published themselves**, with no "no marketing" statement, where the message is **relevant to their role**. Evidence saved per address (§3.5). No evidence, no send.
- **No harvested or guessed addresses.** No Apollo-type databases, enrichment tools, scrapers, browser extensions, purchased lists, PTIN-file emails or pattern guesses.
- **No consent-request emails** ("can I send you info?"). They count as commercial messages.
- **Identify the sender in every email:** `[FOUNDER_NAME]`, Founder, ChimeraShield Pty Ltd (ABN `[ABN]`), `[FOUNDER_NAME]@[DOMAIN]`, `[US_POSTAL_ADDRESS]`, and a line saying where we found the address. Accurate, non-deceptive subject lines. The contact address must keep working for 30+ days after the last send.
- **Unsubscribe in every email:** "Not relevant? Reply "unsubscribe" (or just "no") and I won't email you again." Action it **the same day** (legal maximum: 5 business days under the Spam Act, stricter than CAN-SPAM's 10). It removes the person from **all** our marketing, on every channel; suppress the whole firm unless someone else there asked to hear from us. Mark `opted_out = Y`.
- **LinkedIn:** connection notes are non-commercial (no offer, price or link). Pitch in a DM only after the person asks what we do or shows interest. Every commercial DM names the founder and ChimeraShield and says "If you'd rather I didn't message you about this, say so and I won't." No automation tools.
- US business addresses only for the US campaign. No Canadian (CASL) or EU/UK (GDPR/PECR) prospects in cold email. Australian prospects follow `australia-pilot.md`.
- No unsolicited findings about a prospect's domain. Demos use a company-owned demo domain unless the prospect consented in writing.
- No invented customers, testimonials, logos, stats or certifications. Until we have customers, say so plainly: "You'd be one of our first 10 firms."
- Stats allowed in copy only after the source is opened and checked (market doc warning). Default: no stats.
- Stop a sequence on any reply, including "not now".

---

## 8. After the sale

1. Payment → confirmation with intake checklist and booking link (PRD AC1).
2. Intake (60 min) → deliverables within 7 business days → debrief (30 min) with the AC12 understanding test.
3. At debrief: offer Watch (`call-script.md` §6) and ask for 2 referrals: "Which other firm owner would want this before their renewal?" A referral is an introduction the customer makes (they email both of us), not an address they hand over, so the new contact has agreed to hear from us.
4. Day 14: check-in email on the #1 fix.
5. Ask for a testimonial **only** after delivery, in the customer's words, with written permission to use their name. Never paraphrase into claims we can't back.
