# Ad copy: Free WISP & Safeguards Readiness Check

**Owner:** growth-marketer (paid) · **Date:** 2026-09-24 · **Status:** draft. Founder approval needed, and legal-ops must check every regulatory line (see "Facts used") before anything goes live.
**Offer:** the free readiness check at `https://[DOMAIN]/check` (`docs/company/marketing/landing-readiness-check.md`). **Plan and budgets:** `ads-plan.md`. **Images:** `png/` (sources in `src/`).
**Character counts:** checked by `src/check_copy.py` (Python `len()`, 2026-09-24). Every item below is within its limit. Re-run the script after any edit.

## Rules this copy follows
- **No fear.** No breaches, hackers or fines. We name the obligation calmly (`messaging.md` §4, §8).
- **No statistics.** The only numbers are facts from the table at the end, or our own offer details (12 questions, 3 gaps, and "about 10 minutes", which is an estimate).
- **No implied government endorsement.** No IRS or FTC logos or seals, and no "official" or "IRS-approved". "Structured on IRS Pub 5708" is the approved wording (`messaging.md` §8). The disclaimer ("Not affiliated with the IRS or the FTC") appears as a headline, as a description and on every image.
- **No "certified", "compliant", "audit-ready" or "guarantee".** We say "readiness check", "gaps" and "helps you".
- **No AI in any ad** (`messaging.md` §4).
- **Placeholders stay visible:** `[DOMAIN]`.

---

## 1. Google responsive search ad (RSA)

Use one RSA per ad group (ad groups are in `ads-plan.md` §4). Keep the same assets across groups at first, then change headline 1 to match each group's keywords once you have data.

**Final URL:** `https://[DOMAIN]/check?utm_source=google&utm_medium=cpc&utm_campaign=wisp-check-q4&utm_content={adgroupid}&utm_term={keyword}`
**Display path:** `[DOMAIN]/wisp-check`

### Headlines (15, 30 characters or fewer)

| # | Headline | Chars | Pin? |
|---|---|---|---|
| 1 | Free WISP Readiness Check | 25 | Pin to position 1, together with #2 and #6 (Google rotates the 3) |
| 2 | WISP Help for Tax Preparers | 27 | Pin to position 1 (see #1) |
| 3 | Before You Renew Your PTIN | 26 | |
| 4 | Find 3 Gaps in Your WISP | 24 | |
| 5 | FTC Safeguards Rule Check | 25 | |
| 6 | Written Security Plan Check | 27 | Pin to position 1 (see #1) |
| 7 | For 5–50 Person Tax Firms | 25 | |
| 8 | About 10 Minutes, No Cost | 25 | |
| 9 | Plain-English Results | 21 | |
| 10 | No Passwords or Client Data | 27 | |
| 11 | Your 3 Gaps, Emailed to You | 27 | |
| 12 | Structured on IRS Pub 5708 | 26 | |
| 13 | Not Affiliated With the IRS | 27 | |
| 14 | W-12 Asks About Your WISP | 25 | |
| 15 | Know Where Your Plan Stands | 27 | |

### Descriptions (4, 90 characters or fewer)

| # | Description | Chars | Pin? |
|---|---|---|---|
| 1 | Answer 12 plain-English questions. Get the 3 gaps to close before you sign your W-12. | 85 | |
| 2 | For tax and accounting firms with 5–50 staff. Free, no payment details, no client data. | 87 | |
| 3 | Structured on IRS Pub 5708 and FTC Safeguards Rule. Not affiliated with the IRS or FTC. | 87 | **Pin to description position 2**, so the disclaimer shows on every impression. Legal-ops can lift the pin if they're satisfied without it. |
| 4 | PTINs expire Dec 31. Check your written security plan now, not in filing season. | 80 | |

**If Google disapproves an ad over "PTIN":** Google's "Government documents and services" policy covers third parties who sell official documents or services, and Google is tightening it from 5 Oct 2026 ([Google Ads policy update](https://support.google.com/adspolicy/answer/17260489?hl=en)). We don't sell PTIN renewal, but an automated review could still flag the word. If that happens, remove headline 3 and description 4, and appeal with the explanation "independent security-plan readiness check; we do not provide PTIN services". Don't try to rephrase around the policy.

### Assets (extensions)
**Sitelinks** (text 25 or fewer, description lines 35 or fewer):

| Sitelink text | Line 1 | Line 2 | URL |
|---|---|---|---|
| How the Check Works | 12 questions plus a domain check | Passive, with your written OK | `[DOMAIN]/check#how` |
| What You Get | 3 ranked gaps in plain English | Plus your email-domain result | `[DOMAIN]/check#get` |
| Is It Really Free? | No payment details needed | One follow-up email, no more | `[DOMAIN]/check#faq` |
| Who Sees My Results? | Only you, at your work email | Stored encrypted, never shared | `[DOMAIN]/check#faq` |

**Callouts** (25 or fewer): Free, No Payment Details · About 10 Minutes · Passive Checks Only · No Client Data Needed · Plain English · Independent Company

Don't add a price, promotion or review asset. We have no reviews, and the check is free.

---

## 2. LinkedIn single-image ads (3 variants)

LinkedIn shows about the first 150 characters of intro text before "...see more", and recommends headlines of 70 characters or fewer ([LinkedIn single-image ad specs](https://business.linkedin.com/advertise/ads/sponsored-content/single-image-ads-specs)). Each variant's hook finishes before the cut.

**Destination URL:** `https://[DOMAIN]/check?utm_source=linkedin&utm_medium=paid-social&utm_campaign=wisp-check-q4&utm_content=li-v1` (change `li-v1` to `li-v2` or `li-v3` per variant).

### Variant 1: Deadline (image `png/li-1-deadline.png`)
- **Intro text (244 chars):** Renewing your PTIN this fall? Form W-12 asks you to confirm you know you need a written information security plan. Our free readiness check shows the 3 gaps to close first, in plain English. About 10 minutes, no payment details, no client data.
- **Headline (54):** Find the 3 gaps in your security plan before you renew
- **CTA button:** Learn more
- **Facts:** F1, F2.

### Variant 2: Template vs. reality (image `png/li-2-template.png`)
- **Intro text (241 chars):** A WISP template gives you the structure. It doesn't tell you what's true at your firm today. Answer 12 plain-English questions, and with your OK we read your email domain's public settings. You get 3 gaps, ranked, with a first step for each.
- **Headline (52):** Free WISP & Safeguards Readiness Check for tax firms
- **CTA button:** Sign up
- **Facts:** none. This variant describes our offer only.

### Variant 3: What applies to you (image `png/li-3-steps.png`)
- **Intro text (223 chars):** Fewer than 5,000 clients? Four FTC Safeguards Rule items don't apply to you. The rest, like multi-factor login, encryption and staff training, still do. Our free check tells you which is which and the 3 gaps to close first.
- **Headline (53):** Which Safeguards items apply to your firm? Check free
- **CTA button:** Learn more
- **Facts:** F3, F4, F5. **Legal-ops:** "fewer than 5,000 clients" is shorthand for the rule's "fewer than five thousand consumers" (16 CFR 314.6). If that shorthand isn't acceptable, use "Hold data on fewer than 5,000 consumers?" instead (it's 41 characters, so the hook still fits).

**Test plan:** run all 3 at once. After roughly 1,500 impressions each, pause the lowest CTR. Details in `ads-plan.md` §7.

---

## 3. Retargeting (3 variants)

Retargeting runs only after an audience reaches the platform minimum: 100 active users for Google ([Google Ads Help](https://support.google.com/google-ads/answer/7558048?hl=en)), and 300 matched members for LinkedIn ([LinkedIn Help](https://www.linkedin.com/help/lms/answer/a427551)). At our budget that may never happen. See `ads-plan.md` §6.

**Privacy rule:** retargeting ads never mention a person's result, their domain or any specific gap. They talk about the offer only. Retargeting needs the site's privacy policy and cookie notice to disclose the Google tag and the LinkedIn Insight Tag (legal-ops).

| | R1: Started, didn't finish | R2: Finished the check, no call booked | R3: Deadline, all visitors (from Nov 17) |
|---|---|---|---|
| **Audience** | Visited `/check`, didn't reach `/check/thanks`, last 14 days | Reached `/check/thanks`, didn't reach `/book/thanks`, last 30 days | Visited any page, last 60 days, excluding `/book/thanks` |
| **Google short headline (≤30)** | Finish Your Free Check (22) | Want Help Closing the Gaps? (27) | Done Before Filing Season (25) |
| **Google long headline (≤90)** | Pick up your free WISP readiness check where you left off (57) | Want help closing your 3 gaps? Get a WISP that fits your firm (61) | Get your written security plan done before filing season (56) |
| **Google description (≤90)** | You started the free WISP readiness check. It takes about 10 minutes to finish. (79) | A WISP that fits how your firm works, plus your top 5 fixes. About 2 hours of your time. (88) | Last intake calls Dec 4, so your plan is done before the holidays. Book a 15-minute call. (89) |
| **LinkedIn intro text** | You started the free WISP & Safeguards Readiness Check. It takes about 10 minutes to finish, and your 3 gaps arrive by email within one business day. (149) | Got your 3 gaps? If you'd like help, we build a written security plan around how your firm actually works, mark what's verified, and rank your top 5 fixes. About two hours of your time. (185) | Our last intake calls are Dec 4, so plans are delivered before the holidays and you're not thinking about this in filing season. Book a 15-minute call to see if it fits. (169) |
| **LinkedIn headline** | Pick up where you left off (26) | Want help closing your gaps before Dec 31? (42) | Get your WISP done before filing season (39) |
| **CTA** | Learn more | Learn more | Request demo (LinkedIn has no "Book a call"; if "Request demo" feels pushy, use "Learn more") |
| **Destination** | `[DOMAIN]/check` | `[DOMAIN]/wisp-pack` | `[DOMAIN]/wisp-pack` |
| **Image** | `png/sq-3-trust.png` | `png/sq-1-deadline.png` | `png/sq-1-deadline.png` |

- "About two hours" and "top 5 fixes" come from the Pack definition (`messaging.md` §3, §5).
- "Last intake calls Dec 4" is our own capacity limit (`docs/company/sales/sequences.md`, rules). Change it in all three places if the founder moves that date.
- "Within one business day" is the concierge promise on the landing page. Change it if delivery becomes automated.
- Stop R3 on **Dec 5**, the day after the last intake.

---

## 4. Image headlines (what's on each PNG)

| File | Size | On-image text |
|---|---|---|
| `png/li-1-deadline.png` | 1200×627 | "Before you renew your PTIN, find the 3 gaps in your security plan." · CTA "Start the free check" |
| `png/li-2-template.png` | 1200×627 | "A template gives you structure. The check shows what's true at your firm." · illustrative 3-gap result card, labeled "Illustrative example" |
| `png/li-3-steps.png` | 1200×627 | "12 questions. About 10 minutes. 3 gaps, in plain English." · 3 steps |
| `png/sq-1-deadline.png` | 1080×1080 | "PTINs expire Dec 31." · "Know the 3 gaps in your security plan before you renew." |
| `png/sq-2-w12.png` | 1080×1080 | "Your W-12 asks about your security plan. Can you show it?" (approved headline 2, `messaging.md` §4) |
| `png/sq-3-trust.png` | 1080×1080 | "No passwords. No client data. No cost." · check description |

Every image carries "ChimeraShield" and "Not affiliated with the IRS or the FTC." The images use no IRS, FTC or government imagery. The shield mark is our own simple drawing.

---

## Facts used (all from `messaging.md` §6a, confirmed via search summaries on 2026-09-24; legal-ops to open the primary pages before launch)

| # | Fact as used in the ads | Source |
|---|---|---|
| F1 | Form W-12 asks paid preparers to confirm they know they must have a written information security plan. | [IRS Form W-12](https://www.irs.gov/pub/irs-pdf/fw12.pdf) |
| F2 | PTINs expire Dec 31; renewal normally opens mid-October. | [IRS PTIN FAQ](https://www.irs.gov/tax-professionals/frequently-asked-questions-ptin-application-renewal-assistance) |
| F3 | The FTC Safeguards Rule covers tax preparers. | [FTC Safeguards Rule guide](https://www.ftc.gov/business-guidance/resources/ftc-safeguards-rule-what-your-business-needs-know) |
| F4 | The rule's elements include MFA, encryption and staff training. | [16 CFR 314.4](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314) |
| F5 | Firms with information on fewer than 5,000 consumers are excused from four items only. | [16 CFR 314.6](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314/section-314.6) |
| F7 | IRS Publication 5708 is the IRS's free WISP template ("structured on" is our approved wording). | [IRS Pub 5708](https://www.irs.gov/pub/irs-pdf/p5708.pdf) |

Offer facts (12 questions, 3 gaps, about 10 minutes, no payment details, passive checks, one business day) come from `landing-readiness-check.md`. "About 10 minutes" is an estimate until the first 10 completions are timed. If the landing page changes, change the ads.
