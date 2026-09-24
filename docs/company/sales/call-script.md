# 20-Minute Sales Call Script: WISP & Evidence Pack

**Owner:** head-of-sales · **Date:** 2026-09-24 · **Use for:** every booked sales call, 12 Oct – 11 Dec 2026
**Offer details:** `docs/company/product/prd-wisp-evidence-pack.md` · **Scanning rules:** `.claude/skills/authorized-scanning/SKILL.md` · **Objections:** `objections.md`

## Before the call (5 minutes)
- [ ] Check `pipeline.csv`: stage, source, trigger, whether the Readiness Check is done and `consent_recorded_date` is set.
- [ ] If the check is done: open their result (findings store, not email). Pick the **one** gap you'll lead with.
- [ ] If the check is **not** done: **do not look up anything about their domain.** You'll ask permission on the call (§3b).
- [ ] Have ready: the company-owned demo domain result (fallback), sample Evidence Report and WISP pages (demo firm, fictional), payment link, engagement letter, intake calendar with real open slots.
- [ ] Know today's true number of remaining intake slots before Dec 4 (max 3 per week).

**Tone:** calm, plain English, no fear. We explain risk; we don't sell it. Talk 30% of the time or less in the first 10 minutes.

---

## 0:00–2:00 · Open and set the agenda
> "Thanks for making time, [FIRST_NAME]. Here's what I'd suggest for our 20 minutes: I'll ask a few questions about how [FIRM] runs today, then we'll look at your readiness check results together, and if it looks like a fit I'll explain the Evidence Pack and what it costs. If it's not a fit, I'll tell you, and you'll still leave with your top gaps. Sound OK?"
>
> "One thing before we start: please don't share any client names or client details. I only need to know about your firm's own setup."

If recording: "Is it OK if I record this so I can take fewer notes? It stays with me." No = notes only.

---

## 2:00–8:00 · Discovery (pick 6–7; listen for their words and write them down)

| # | Question | What you're listening for | Pipeline field |
|---|---|---|---|
| 1 | "When do you usually renew your PTIN, and when you get to line 11 on the W-12, what do you have to point to?" | Nothing / an unfinished template / an MSP document / a real plan | `notes` |
| 2 | "If you have a written plan today, who wrote it and when was it last touched?" | Age, author, generic vs. specific | `notes` |
| 3 | "Who handles IT for the firm: you, someone on staff, or an outside company?" | MSP present? Does the MSP maintain the WISP? | `has_msp` |
| 4 | "What do you use for email, and for tax software and client file sharing?" | M365 / Google, desktop vs. cloud tax software, portal | `email_platform` |
| 5 | "Is two-step login turned on for everyone's email and for the tax software?" | Yes / some / not sure (not sure = a gap to verify) | n/a |
| 6 | "Roughly how many clients' records do you keep: under 5,000 or more?" | Decides which §314.6 exemptions may apply (don't give a legal answer) | `notes` |
| 7 | "Has an insurer, a client, or a bank ever asked for proof of your security? What did you send?" | Secondary use for the Evidence Report | `notes` |
| 8 | "Any close calls this year: a phishing email someone clicked, a strange login, an IRS or e-Services lookalike?" | Pain, and the Watch helpdesk hook | `notes` (no client details) |
| 9 | "If you decided this was worth doing, who else would weigh in, and by when would you want it done?" | Decision-maker, timeline | `next_step` |

**Summarize back (always):**
> "So if I've got it right: you renew in [MONTH], the plan you have is [their words], [IT situation], and the thing that worries you most is [their words]. Is that fair?"

**Early exits:**
- MSP already maintains a current, firm-specific WISP with evidence → "Sounds like you're covered on the plan. The free check still gives you an outside view. Would your IT provider be open to a quick intro?" (partner lead, `partners.md`). Stage `lost`, reason `msp-covered`.
- Busy / not the decision-maker → book the decision-maker; don't pitch to the wrong person.

---

## 8:00–13:00 · Readiness Check results (passive only, with permission)

### 3a. They completed the check (consent already recorded)
> "You gave us permission to run the passive checks on [DOMAIN] when you did the readiness check. These are public-record checks, the same information any mail server sees. We didn't log into or probe anything."

Walk through **no more than 3 items**, one at a time:
> "Number one: [GAP_1 in plain English, e.g. 'there's no DMARC record, which is the setting that tells other mail servers to reject emails pretending to be from your firm']. Why it matters for you: [one sentence tied to their answer, e.g. 'clients get emails that look like they're from you asking for documents']. Who fixes it: [whoever manages your domain / your IT provider], about [TIME]."

Label every item honestly:
- **"We observed"**: DNS/email records, certificate, headers from a normal page load.
- **"You told us"**: quiz answers (MFA, backups, training). "We haven't verified this; in the Pack we'd verify it with you on screen-share."

> "What stands out to you?" (Stop and let them talk.)

### 3b. They have not done the check
> "I haven't looked at anything about your firm's domain, because I only do that with permission. If you'd like, you can run the free check now while we're talking. It takes a few minutes and asks you to confirm you're authorized for [DOMAIN]. Results only go to your work address. Want to do that, or should I show you what it looks like on our demo firm instead?"

- **Yes:** send [READINESS_CHECK_URL]; they complete the consent step themselves (checkbox + typed name, stored with timestamp). Wait for the result, then do 3a.
- **No / not now:** show the **demo domain** result and the sample Evidence Report. Don't guess about their setup.

**Never:** run a check they haven't consented to, go beyond passive checks, say "you're vulnerable", or say anything is "compliant" or "failing".

---

## 13:00–17:00 · The Pack offer

Bridge from their words:
> "The check shows you where you stand from the outside. It doesn't give you what line 11 is about: a written plan that describes how *your* firm actually protects client data. That's what the Evidence Pack is."

> "Here's how it works:
> 1. **One 60-minute call** with you (your office manager can fill in a 15-minute checklist beforehand). We never need client data.
> 2. Within **7 business days** you get three things:
>    - **Your written information security plan**, built on the IRS Pub 5708 structure and the FTC Safeguards Rule elements, filled in with [FIRM]'s real systems and people, with the small-firm exemptions applied where they fit. You sign it as the Qualified Individual.
>    - **A one-page Evidence Report**: each control marked *Verified* (we saw it), *Owner-stated* (you told us), or *Gap*. You can hand it to an insurer or a client who asks.
>    - **Your Fix-First plan**: the top 5 things to fix, in order, with who does each one and how long it takes.
> 3. **A 30-minute walkthrough** so you know exactly what your number-one fix is and why."

What it is not (say it; it builds trust):
> "To be clear about limits: this isn't legal advice, it doesn't make you 'compliant' by itself, and we don't log into your systems or fix things for you. You stay in charge; we make it clear and written down."

Price:
> "The Pack is **[PACK_PRICE]**, one-time. That's our founding-member price for the first 10 firms, and you'd be one of them. We're a new company, so I'll be doing your intake personally."

Watch (mention only, don't sell yet):
> "After the Pack, some firms keep it current with Watch at [WATCH_PRICE], which re-checks your evidence monthly and gives your staff an 'Is this safe?' address to forward suspicious emails to during tax season. That's a conversation for the walkthrough, not today."

Pause. Ask:
> "How does that compare with how you were planning to handle it?"

Handle objections with `objections.md`. Give one answer, then check: "Does that address it?"

---

## 17:00–20:00 · Close and next step

### The close (use these words)
> "Based on what you told me, [their gap in their words], and a plan that doesn't describe [FIRM] yet, the Pack gets you a signed plan, the one-page evidence report, and your top 5 fixes before you renew. It's [PACK_PRICE]. I have [N] intake slots left before December 4. **Would you like me to send the engagement letter and payment link now, so we can book your intake for [DAY] at [TIME]?**"

Then stop talking. Wait for the answer.

### If yes
> "Great. I'm sending two things to [their work email] right now: the engagement letter, which covers what we do, our limits, and how we handle your information, and the payment link. Once that's done, you'll get the intake checklist and a confirmation for [DAY] at [TIME]. The checklist takes about 15 minutes; your office manager can do it. Anything that would stop you from completing it by [DATE, 2 business days before intake]?"

Actions within 1 hour: send letter + link, pencil the intake slot, set `stage = 7-link-sent`, `next_step = "confirm payment; intake [DATE]"`. If unpaid after 48h, send W2-2 from `sequences.md`.

### If "I need to think about it"
> "Of course. So I can help: is it the price, the timing, or whether it's worth doing at all?" (Answer the real one from `objections.md`.)
> "I'll hold [DAY] at [TIME] for you until [HOLD_DATE, 2 business days]. After that I'll release it, since slots before December 4 are limited. I'll send a short recap today. Fair?"

`stage = 6-call-held`, `next_step = "decision by [HOLD_DATE]"`; send W2-1.

### If "I need to check with my partner"
> "Makes sense. Would it help if I joined a 10-minute call with the two of you? I can do [DAY_1] or [DAY_2]."
If no: "Then I'll send a one-paragraph recap you can forward. What's the one question your partner will ask first?"

### If "not this year" / busy season
> "Understood. Would it help if I checked back in May, after April 15, so it's done well before next renewal?"
`stage = nurture-may`. Offer to keep their free check results on file.

### If no
> "Thanks for being straight with me. Can I ask what would have made it a yes? It helps me get this right." Record `lost_reason` exactly in their words.

### Always, before hanging up
> "Is there another firm owner you know who's facing the same renewal question? I'd be glad to offer them the free check."

---

## §6. Watch offer at the debrief (not on the sales call)
> "Your plan is signed and you know your number-one fix. The evidence report is accurate today, but it goes stale as people join, laptops change and settings drift. Watch re-checks what we can see every month, updates your evidence report, reminds you of your annual plan review and your next PTIN renewal, and gives your staff an address to forward suspicious emails to. A person reviews every high-risk verdict. It's [WATCH_PRICE]. Would you like to start it now so it's running before tax season?"

**Only say "a person reviews every high-risk verdict" and describe email forwarding once the helpdesk's data handling (retention, no training on forwarded content, access control) is confirmed by tech-lead** (catalog §7 item 4). Until then, describe Watch without the helpdesk and say it's coming.

## After every call (within 1 hour)
- Update `pipeline.csv` (stage, next_step, next_step_date, lost_reason). No findings or client details in the repo.
- Note the exact words they used for the problem; these feed sequences and objections.
- Top objection → tally for the Friday review (`playbook.md` §5.5).
