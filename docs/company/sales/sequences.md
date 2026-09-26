# Sales Outreach Sequences: PTIN renewal window 2026

**Owner:** head-of-sales · **Date:** 2026-09-24 · **Updated:** 2026-09-26 (Spam Act 2003 footer, ABN, unsubscribe wording, `[US_POSTAL_ADDRESS]`, non-commercial LinkedIn opener) · **Status:** ready to send once gates G1–G4, G3a–G3c and G8 in `playbook.md` §2 are cleared
**Follows:** `.claude/skills/outreach-writing/SKILL.md` (short, one ask, real sender, opt-out) and `docs/company/legal/spam-act-cold-email.md` §4 and §8. Discovery (research) outreach is in `docs/company/interviews/recruiting-kit.md`; do not send both to the same person in the same month. If someone already did a discovery interview, use the warm sequence W instead. Australian pilot copy is in `australia-pilot.md`, not here.

## Rules before you hit send
- **Consent first (Spam Act).** Only email a contact whose evidence row (`playbook.md` §3.5) shows `inferred: conspicuous publication`, `express: …` or `inferred: existing relationship`. **No evidence, no send.** Rows marked `none: LinkedIn only` never go into the mail tool.
- **Cadence:** Touch 1 → +3 days → +5 days → +7 days. **Stop on any reply or opt-out**, including "not now" (move to `nurture-may`).
- **Touch 1 is plain text with no links.** Links (the Readiness Check URL) only from touch 3.
- **The personal first line must be true, specific and 12 words or fewer.** If you can't write one in 2 minutes, skip the prospect or send LinkedIn only. Line bank at the bottom.
- **No stats, no customer claims, no findings about their domain.** We haven't looked at their domain and we say nothing about it.
- **Placeholders stay visible until real:** `[FOUNDER_NAME]`, `[DOMAIN]`, `[ABN]`, `[US_POSTAL_ADDRESS]`, `[SOURCE]`, `[READINESS_CHECK_URL]`, `[PACK_PRICE]`, `[WATCH_PRICE]`, `[FIRM]`, `[FIRST_NAME]`, `[PERSONAL_LINE]`. **Don't send while `[ABN]` or `[US_POSTAL_ADDRESS]` is still a placeholder.**
- **Dates:** "PTINs expire Dec 31" and "renewal opens mid-October" are per IRS guidance; re-check irs.gov when renewal opens and update if needed. "Last intake Dec 4" is our own capacity limit, so it's true.
- **Times:** always give the prospect's time zone first (we're in Sydney; `playbook.md` §5.6). Schedule sends for 08:00–11:00 recipient time.
- US business addresses only. Log every send in `pipeline.csv` (`sequence`, `touch_step`, `last_touch_date`).
- **Unsubscribes:** action the same day (legal maximum 5 business days). Remove the person from all our marketing on every channel, and suppress the firm.

## Standard footer (every email; do not trim it)

Pick the footer that matches the contact's `consent_basis`. The footer is required by law (Spam Act sender identification and unsubscribe; CAN-SPAM postal address and advertisement disclosure), so it is **never** cut to save words. Instead, keep each **body** (greeting to ask) **at 65 words or fewer**, so the whole email stays at about 100 words. Legal-ops approves the final wording (G3c).

**F1. Cold, owner or partner (`inferred: conspicuous publication`)**
```
[FOUNDER_NAME], Founder, ChimeraShield Pty Ltd (ABN [ABN])
[FOUNDER_NAME]@[DOMAIN] · [US_POSTAL_ADDRESS]
I found your address on [SOURCE] and am writing because you run a tax practice.
Not relevant? Reply "unsubscribe" (or just "no") and I won't email you again.
```

**F2. Cold, operations lead (only if the firm's site shows they handle operations or IT)**
```
[FOUNDER_NAME], Founder, ChimeraShield Pty Ltd (ABN [ABN])
[FOUNDER_NAME]@[DOMAIN] · [US_POSTAL_ADDRESS]
I found your address on [SOURCE], which lists you as running operations at [FIRM].
Not relevant? Reply "unsubscribe" (or just "no") and I won't email you again.
```

**F3. Warm or express consent (Readiness Check opt-in, partner intro, interviewee, reply asking for info)**
```
[FOUNDER_NAME], Founder, ChimeraShield Pty Ltd (ABN [ABN])
[FOUNDER_NAME]@[DOMAIN] · [US_POSTAL_ADDRESS]
You're getting this because [REASON, e.g. "you asked for your Readiness Check results" / "[PARTNER_NAME] introduced us"].
Not relevant? Reply "unsubscribe" (or just "no") and I won't email you again.
```

`[SOURCE]` is a short, true description of the evidenced page, e.g. "your firm's website" or "your NATP profile". It must match `published_source_url`. If we're still a sole trader when sending starts, replace line 1 with `[FOUNDER_NAME], Founder, ChimeraShield (ABN [ABN])` using the founder's own ABN.

---

## Sequence A: cold email, firm owner / managing partner (footer F1; A1-ADMIN uses F2)

### A1. Touch 1 (day 0), pick the Touch 1 variant that matches the trigger

**A1-CPA (CPA firm owner, website/directory trigger)**
> **Subject:** [FIRM] and the w-12 security plan
>
> Hi [FIRST_NAME],
>
> [PERSONAL_LINE, e.g. "I saw on your site that [FIRM] opened a second office."]
>
> At PTIN renewal, W-12 line 11 asks you to confirm you know you need a written security plan. A template covers the form, not your firm.
>
> We write the plan around your actual setup, with a one-page evidence report and a short fix list.
>
> Worth 15 minutes next week?
>
> *(footer F1)*

**A1-EA (EA / tax-prep firm owner)**
> **Subject:** security plan before your ptin renewal
>
> Hi [FIRST_NAME],
>
> [PERSONAL_LINE, e.g. "Your firm's site says [FIRM] has [N] enrolled agents in [CITY]."]
>
> Renewal means the W-12 question about a written security plan. A template leaves the hard part, your own systems, blank.
>
> We do that part with you in one call: the plan, a one-page evidence report and your top 5 fixes.
>
> Open to 15 minutes next week?
>
> *(footer F1)*

**A1-EVENT (attending NATP Las Vegas 21–22 Oct, a state CPE session, or posted about it)**
> **Subject:** after [EVENT]
>
> Hi [FIRST_NAME],
>
> Saw you're heading to [EVENT]. Good timing, just before PTIN renewal and the W-12 line 11 question.
>
> If "update the WISP" lands on your list afterward, we offer small firms a done-with-you version: a plan that describes your firm, a one-page evidence report and a 5-item fix list.
>
> Worth 15 minutes the week after?
>
> *(footer F1)*

**A1-ADMIN (firm administrator / office manager whose role on the firm's site covers operations or IT; ask for the right person, not a demo)**
> **Subject:** who owns the wisp at [FIRM]?
>
> Hi [FIRST_NAME],
>
> [PERSONAL_LINE]
>
> Quick question: who at [FIRM] keeps the written security plan current? PTIN renewal asks every preparer about it on the W-12.
>
> Our plans match how the office actually runs; the office manager's part is a 15-minute checklist.
>
> Is that you, or should I reach [OWNER_ROLE]?
>
> *(footer F2)*

### A2. Touch 2 (+3 days): short bump with one new piece of value
> **Subject:** re: [original subject]
>
> Hi [FIRST_NAME],
>
> One thing I left out. Under the FTC Safeguards Rule, a breach of unencrypted data affecting 500+ consumers has to be reported to the FTC within 30 days. A plan that already names who does what makes those 30 days far calmer.
>
> Would Tuesday or Wednesday afternoon, your time, work for 15 minutes?
>
> *(same footer as touch 1)*

### A3. Touch 3 (+5 days): helpful resource (first link allowed)
> **Subject:** free readiness check for [FIRM]
>
> Hi [FIRST_NAME],
>
> If a call is too much right now, try our free WISP & Safeguards Readiness Check: 12 questions plus a public-records check of your firm's email settings, run only after you say OK.
>
> You get your top 3 gaps before you renew, sent to your work address:
> [READINESS_CHECK_URL]
>
> *(same footer as touch 1)*

*Fallback if the check isn't live (playbook §6): replace the link line with "Reply 'check' from your work email and I'll send the 12 questions."*

### A4. Touch 4 (+7 days): closing the loop
> **Subject:** closing the loop
>
> Hi [FIRST_NAME],
>
> I'll stop here. PTINs expire Dec 31, and my last intake calls are on Dec 4 so plans land before the holidays.
>
> If a written plan for [FIRM] is on this year's list, reply "yes" and I'll send two times. If not, good luck with the season.
>
> *(same footer as touch 1)*

---

## Sequence L: LinkedIn (run alongside or instead of email, never both on the same day)

LinkedIn messages are very likely "electronic messages" under the Spam Act (`spam-act-cold-email.md` §8). So: **the connection note and the first DM carry no offer, no price and no link.** We pitch only after the person asks what we do or shows interest. **No automation tools** (auto-connect, auto-DM).

**L1. Connection note (non-commercial, under 300 characters)**
> Hi [FIRST_NAME], [SHORT_PERSONAL_LINE, max 80 characters]. I'm the founder of ChimeraShield and I'm learning how small tax and CPA firms handle their written security plan before PTIN renewal. Glad to connect. [FOUNDER_NAME]

**L2. After they accept (+1–2 days): one non-commercial question**
> Thanks for connecting, [FIRST_NAME]. One question if you have a minute: when you reach the W-12 security-plan question at renewal, what do you point to today? A template, something your IT provider wrote, or nothing yet? I'm collecting answers from small firms.

*No reply to L2: stop DMs. Comment genuinely on their posts (no pitch in comments). Don't send L3.*

**L3. Only if they reply or ask what we do (commercial DM, now with interest shown)**
> Thanks, that's useful. Since you asked: I help 5–50 person firms with a done-with-you WISP before renewal. One 60-minute call, then within 7 business days a plan that describes your firm, a one-page evidence report and your top 5 fixes. Worth 15 minutes to see if it fits [FIRM]?
> [FOUNDER_NAME], ChimeraShield Pty Ltd (ABN [ABN]) · [FOUNDER_NAME]@[DOMAIN]
> If you'd rather I didn't message you about this, say so and I won't.

**L4. +5 days after L3 with no answer: resource and close (last DM)**
> [FIRST_NAME], if a call is too much during renewal season, our free Readiness Check takes about 10 minutes: 12 questions plus a public-records email security check (only with your OK), and you get your top 3 gaps. [READINESS_CHECK_URL]. My last intake calls are Dec 4. This is my last note on it.
> [FOUNDER_NAME], ChimeraShield Pty Ltd (ABN [ABN]) · [FOUNDER_NAME]@[DOMAIN]
> If you'd rather I didn't message you about this, say so and I won't.

**If they give you an email address in the chat and ask for details:** record `consent_basis = express: LinkedIn request, [date]` and send by email with footer F3.

---

## Sequence W: warm follow-ups (footer F3)

### W1. Completed the Readiness Check, no call booked (sent only to the consenting work address)
*W1-1 is the result they asked for. Send W1-2 and W1-3 **only** if they ticked the marketing opt-in box on the check or replied to W1-1; otherwise stop after W1-1.*

**W1-1 (same day as result, part of the result email)**
> **Subject:** your readiness check: 3 gaps before renewal
>
> Hi [FIRST_NAME],
>
> Your results are below. The short version: [GAP_1_PLAIN_ENGLISH] is the one I'd fix first, and it's usually [TIME_ESTIMATE] of work.
>
> Want 20 minutes to go through all three and what a written plan would say about them? Pick a time: [BOOKING_URL]
>
> *(footer F3: "you asked for your Readiness Check results")*

**W1-2 (+3 days)**
> Hi [FIRST_NAME], did the results make sense? If anything in them was unclear, reply with the item number and I'll explain it in two sentences. No call needed.
>
> *(footer F3)*

**W1-3 (+7 days)**
> Hi [FIRST_NAME], last note on your check. I have [N] intake slots left before Dec 4. If you'd like the full plan, evidence report and 5-item fix list before renewal, reply "slot" and I'll send the details. Otherwise I'll leave it here.
>
> *(footer F3)*

### W2. Call held, no decision
**W2-1 (same day)**
> **Subject:** recap for [FIRM]
>
> Hi [FIRST_NAME], thanks for today. As discussed: the WISP & Evidence Pack is [PACK_PRICE], one 60-minute intake, delivered within 7 business days. Your top gap was [GAP_1]. I'm holding [DAY] at [TIME, prospect's time zone] for your intake until [HOLD_DATE]. Reply "go" and I'll send the engagement letter and payment link.
>
> *(footer F3: "we spoke on [DATE]")*

**W2-2 (+4 days)**
> Hi [FIRST_NAME], I'll release the [DAY] slot tomorrow unless you'd like it. If the timing is wrong, reply "May" and I'll check back after April 15.
>
> *(footer F3)*

### W3. Partner-referred intro
*Only after the partner has made the introduction (ideally an email to both of us) and the prospect agreed to hear from us. Record `consent_basis = express: partner intro [PARTNER_CODE], [date]`.*
> **Subject:** [PARTNER_NAME] suggested I reach out
>
> Hi [FIRST_NAME],
>
> [PARTNER_NAME] at [PARTNER_FIRM] mentioned you're updating [FIRM]'s written security plan before PTIN renewal.
>
> That's what we do: one 60-minute call, then a plan that describes your firm, a one-page evidence report and your top 5 fixes. [PARTNER_NAME] stays in the loop on anything that needs hands-on IT work.
>
> Would 15 minutes this week work?
>
> *(footer F3: "[PARTNER_NAME] introduced us")*
> *Disclosure line when a referral fee applies: "Transparency note: [PARTNER_FIRM] may receive a referral fee if you buy."*

### W4. Nurture (May 2027, for `nurture-may`; they asked us to check back)
> Hi [FIRST_NAME], you asked me to check back after tax season. Is now a better time to get [FIRM]'s written security plan and evidence in shape, well before the next renewal? 15 minutes to see if it fits? *(footer F3: "you asked me to check back after April 15")*

---

## Personal first-line bank (only if true, checked and 12 words or fewer)
| Trigger | Example line |
|---|---|
| New office / move | "Congrats on the new [CITY] office; I saw it on your site." |
| Hiring | "Saw [FIRM] is hiring a [ROLE] for the season." |
| Directory | "Your NATP profile says [FIRM] focuses on [SPECIALTY]." |
| LinkedIn post | "Your post last week on [TOPIC] stuck with me." |
| Event | "Saw you're speaking at [EVENT]." |
| Software change | "Noticed [FIRM] now offers a client portal for uploads." |
| Referral | "[NAME] suggested I get in touch." (only with the referrer's permission) |

**Banned first lines:** anything about their domain, DMARC, website security, "I noticed your email setup", breach news about a named peer, flattery without specifics.

## Word-count check
Each **body** (greeting to ask) above is 65 words or fewer with a 12-word personal line. With the fixed legal footer (about 37 words), each email is about 100 words. If you add a longer personal line, cut the body, never the footer.
