# Landing page: Free WISP & Safeguards Readiness Check

**Owner:** head-of-growth · **Date:** 2026-09-24 · **Status:** draft copy. Legal-ops review required before publishing.
**URL (proposed):** `[DOMAIN]/check` · **Goal:** a completed readiness check with consent recorded. **Secondary goal:** book a Pack call from the result email.
**Go-live target:** 15 Oct 2026 (catalog §7). Messaging and facts: `docs/company/marketing/messaging.md`.
**US only. Do not reuse in Australia. See `docs/company/market/australia-vs-us.md` §6.** Legal review edits M2, M3, M5–M8, M13 (compliance-roadmap §5) applied 2026-09-26.

Notes for the builder (tech-lead) are in `> Builder:` blocks. Everything in `[BRACKETS]` is a placeholder and must stay visible until it's filled with a real value.

---

## Hero

**Headline:**
# Before you renew your PTIN, find the 3 gaps in your security plan.

**Sub-headline:**
A free readiness check for tax and accounting firms. Answer 12 plain-English questions and we'll run a passive check of your email domain. You get **3 gaps to close before you sign your W-12**, emailed to you within one business day.

**Primary button:** `Start the free check`
**Under the button (small):** About 10 minutes. No payment details. No passwords or client data.

> Builder: "About 10 minutes" is an estimate. Time the first 10 completions and correct it. "Within one business day" reflects concierge delivery (catalog §7). It's a future promise, so it needs reasonable grounds (ACL s 4, compliance-roadmap §5 M13): keep it only while the founder's capacity plan supports it, and pause ads or change the wording if the backlog passes one day. Change it to "in minutes" only once results are automated.

**Trust strip (only true statements):**
- Structured on IRS Publication 5708 and the FTC Safeguards Rule
- Passive checks only: we read public records, we never log in or probe your systems
- Not affiliated with the IRS or the FTC

---

## The problem

**Heading:** One checkbox, a lot behind it

Every time you renew your PTIN, Form W-12 asks you to confirm you know that paid preparers are required by law to create and maintain a written information security plan (a WISP). [Source: IRS Form W-12, line 11]

Behind that checkbox is the FTC Safeguards Rule. It treats tax preparers as financial institutions and expects things like a named person in charge of security, multi-factor authentication (a second step when you log in), encryption, and staff training. [Source: FTC]

Most small firms aren't ignoring this. They're busy. Maybe you downloaded the IRS template and never finished it. Maybe you bought one and filled in the firm name. Maybe your plan was accurate three years ago.

The check tells you, in about 10 minutes, where you actually stand.

> Builder: link "[Source: …]" to the primary URLs in `messaging.md` §6a (F1, F3). Don't use any number that isn't in that table.

---

## How it works

**1. Answer 12 questions.**
Plain English, about your firm, not about technology. For example: "Who in your firm is responsible for security?" and "Do staff use a second step to log into email?"

**2. We check your email domain, with your permission.**
We read public records that anyone can see (your SPF, DKIM and DMARC settings, which help stop people sending fake email as you) plus your website's certificate. Nothing is installed and nothing is tested against your systems.

**3. Get your 3 gaps.**
Within one business day, we email you a short, plain-English result: the 3 gaps most worth closing before you sign your W-12, why each one matters, and what to do about it.

---

## What you get

- **Your 3 priority gaps**, ranked, each with a one-sentence "why" and a first step
- **Your email-domain result** in plain English: what's set up, what's missing, and whether someone could more easily send email pretending to be you
- **Which Safeguards items may not apply to you.** Firms that hold information on fewer than 5,000 consumers (everyone whose records you keep, including past years) may be excused from four items under 16 CFR 314.6; we tell you which ones
- **A short list of free official resources** (IRS Pub 5708, Pub 4557, the FTC guide)

What you **won't** get: a score out of 100, a sales call you didn't ask for, or a claim that you're "compliant".

---

## The form

**Heading:** Start your free check

| Field | Notes |
|---|---|
| Your name | required |
| Firm name | required |
| Work email | required. Must be on your firm's own domain for the domain check. |
| Your role | Owner / Partner · Office or firm manager · Staff · IT provider working for the firm |
| Staff count | 1–4 · 5–10 · 11–25 · 26–50 · 50+ |
| Roughly how many people's records do you keep, including past years? | Fewer than 5,000 · 5,000 or more · Not sure. Helper text: "Count everyone whose information you hold, including past years' clients, spouses and dependents." |
| Consent checkbox (required for the domain check) | *"I confirm I own or am authorized by the owner to test [domain], and I authorize ChimeraShield to perform the passive checks described. I understand results may include sensitive security information."* |
| Optional checkbox | "Send me occasional plain-English notes about security for tax firms. Unsubscribe anytime." (unchecked by default) |
| Line above the submit button (not a checkbox) | "We'll email your result and one follow-up about it." |

**Under the form:** We'll send your result only to this email address. We don't sell your details. We use them only to run your check, with the service providers listed in our privacy policy. `[LINK: Privacy policy, legal-ops]`

> Builder: store the "We'll email your result and one follow-up about it" line shown, with the timestamp, in the same consent record as the domain-check consent. Under the Spam Act we carry the burden of proving consent for the follow-up (compliance-roadmap §5 M7). The newsletter box stays unticked by default and is recorded separately.

**If the email is Gmail, Yahoo, Outlook.com or similar:**
> Using a personal-style email for the firm is common. We can't run the domain part of the check on a shared email service, but you can still answer the 12 questions and get your 3 gaps. (Tip: a firm domain with proper email settings makes it harder for someone to impersonate you. We'll explain in your result.)

> Builder: the catalog says to reject free-mail domains **for the domain check** (authorization). Don't block the quiz. Many small preparers use free email, and that fact is itself a gap to report. Store the consent text, domain, name, email and UTC timestamp before any check runs (PRD AC2). Results go only to an address on the scanned domain. No active checks of any kind.

---

## Social proof

> **[TESTIMONIAL PLACEHOLDER: DO NOT PUBLISH.]** Replace only with a real quote from a real firm owner, in their own words, with written permission to use their name, firm and city. If there's no real quote at launch, **delete this section**. Don't fill it with invented or "representative" quotes.

> **[PROOF PLACEHOLDER: "Used by [N] tax and accounting firms".]** Show only once N is a real count above 25. Hide it until then.

---

## FAQ

**Is it really free?**
Yes. No payment details. After your result, we'll mention our paid WISP & Evidence Pack once. If you're not interested, that's the end of it.

**What exactly do you check on my domain?**
Public DNS records (MX, SPF, DKIM for selectors you name, DMARC), your website's TLS certificate, and security headers from one normal visit to your homepage. That's the same information anyone on the internet can see. We don't scan ports, try logins, or send test phishing emails.

**Do you need passwords, system access or client data?**
No. Never. Please don't send us any taxpayer information.

**Is this legal advice?**
No. It's a plain-English readiness check from a security company. It doesn't tell you whether you're compliant, and it isn't a substitute for advice from your attorney or CPA.

**Are you connected to the IRS?**
No. ChimeraShield is an independent company. The IRS publishes a free WISP template (Publication 5708), and we link to it in your result.

**We're a small firm. Does the whole Safeguards Rule apply?**
Most of it does. Firms that hold information on fewer than 5,000 consumers (everyone whose records you keep, including past years) may be excused from four items: a written risk assessment, continuous monitoring or annual penetration testing, a written incident response plan, and an annual report to a board. The written security program, MFA, encryption and training still apply. [Source: 16 CFR 314.6]

**Who sees my results?**
You, and the ChimeraShield person who reviews it. Our service providers (hosting, email and AI) process it under contract, and we never sell it. Results are stored encrypted and sent only to the email address you gave us. `[LINK: Subprocessor list]`

**Do you use AI?**
Yes, to help turn technical results into plain English. A person reviews your result before it's sent, and nothing is changed in your systems.

**What happens after I get my result?**
If you want help closing the gaps, you can book a call about the WISP & Evidence Pack. If not, the result is yours to keep and use however you like.

**Will you email me a lot?**
No. You get your result and one follow-up. Anything more only if you tick the box for occasional notes. Every email tells you how to unsubscribe, and we stop within 5 business days at most (usually the same day).

---

## Final CTA

**Heading:** Renewal opens in mid-October. Know your 3 gaps before then.
**Button:** `Start the free check`
**Under the button:** About 10 minutes · No payment · Result within one business day

> Builder: after the IRS announces the 2027 renewal opening, change the heading to "PTIN renewal is open. Know your 3 gaps before you sign." Don't publish an exact date before the IRS does.

---

## Footer disclaimer (verbatim, legal-ops to approve)

> ChimeraShield is not affiliated with the IRS or the FTC. The readiness check is general information, not legal, tax or insurance advice, and it doesn't determine whether your firm complies with any law. Results are based on your answers and on publicly visible records for the domain you authorized. You remain responsible for your firm's compliance.
> ChimeraShield Pty Ltd · ABN `[ABN]` · `[POSTAL_ADDRESS]` · `hello@[DOMAIN]` · `[LINK: Privacy]` · `[LINK: Terms]`

> Builder: **FLAG (legal-ops):** whether Corporations Act s 153 (name and ACN/ABN on public documents) covers web pages. Showing the entity and ABN is safe either way. If the Pty Ltd isn't registered at go-live, use the founder's name and sole-trader ABN instead (`spam-act-cold-email.md` §4).

---

## Result email (template, what the check produces)

**Subject:** Your 3 gaps before you sign your W-12
**From:** `[FOUNDER_NAME]` at ChimeraShield `<[FOUNDER_NAME]@[DOMAIN]>`

> Hi [FIRST_NAME],
>
> Thanks for taking the readiness check for [FIRM]. Here are the 3 gaps most worth closing before you renew your PTIN:
>
> **1. [GAP_1_TITLE].** [ONE-SENTENCE WHY]. First step: [ACTION].
> **2. [GAP_2_TITLE].** [ONE-SENTENCE WHY]. First step: [ACTION].
> **3. [GAP_3_TITLE].** [ONE-SENTENCE WHY]. First step: [ACTION].
>
> **Your email domain ([DOMAIN_CHECKED]):** [PLAIN-ENGLISH SUMMARY].
> **Items that may not apply to you:** [314.6 NOTE based on consumer-count answer, always worded "may be excused"].
>
> Free resources: IRS Pub 5708 (WISP template), IRS Pub 4557, FTC Safeguards Rule guide. [LINKS]
>
> If you'd like help, our WISP & Evidence Pack builds a plan around how [FIRM] actually works, marks what's verified, and ranks your top 5 fixes, in about two hours of your time. [Book a 15-minute call](BOOKING_LINK). If not, no problem. This result is yours.
>
> [FOUNDER_NAME], Founder
> ChimeraShield Pty Ltd (ABN [ABN])
> [FOUNDER_NAME]@[DOMAIN] · [POSTAL_ADDRESS]
>
> Not legal advice. We aren't affiliated with the IRS or the FTC.
> Reply "unsubscribe" (or "stop") and we won't email you again.

**One follow-up only**, 4 business days later, if they haven't booked: "Did gap #1 make sense? Happy to answer questions by reply." It carries the **same signature and unsubscribe footer** as the result email. Then stop.

**Why the footer matters:** this email promotes the Pack, so under Australia's Spam Act 2003 it's a commercial electronic message (compliance-roadmap §5 M6; `spam-act-cold-email.md` §4). It must name the authorising entity and ABN and include a working unsubscribe.

> Builder, unsubscribe and suppression handling:
> - Treat any reply containing "unsubscribe", "stop", "no" or "remove" as an unsubscribe. Add the address to the suppression list **the same day** (legal maximum: 5 business days).
> - Check the suppression list before sending the follow-up, and before any newsletter or future email to that address, from either domain.
> - Keep the reply mailbox working for at least 30 days after the last email sent.
> - No fee, login or questions to unsubscribe.
> - If the Pty Ltd isn't registered yet, sign with the founder's name and sole-trader ABN. Don't send with `[ABN]` still a placeholder.
