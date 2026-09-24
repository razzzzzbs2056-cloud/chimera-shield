# Paid ads plan: Readiness Check, PTIN window 2026

**Owner:** growth-marketer (paid) · **Date:** 2026-09-24 · **Status:** plan only, for founder decision. Nothing has been bought, created or launched.
**Offer:** the free WISP & Safeguards Readiness Check at `https://[DOMAIN]/check` (`../landing-readiness-check.md`). **Copy:** `ad-copy.md`. **Images:** `png/`.
**Audience:** owners and managers of US tax, CPA and accounting firms with 5–50 staff (`../../market/first-market-selection.md`).
**Window:** Oct 1 to Dec 15, 2026. PTINs expire Dec 31, and renewal normally opens mid-October ([IRS PTIN FAQ](https://www.irs.gov/tax-professionals/frequently-asked-questions-ptin-application-renewal-assistance), `../messaging.md` F2).

> **Heads-up: this conflicts with the channel plan.** `../channel-plan.md` (being written in parallel) puts Google Ads under "not now" because "we can't budget ads without cost data". This plan agrees that paid ads are **not** a core channel this season. It proposes a small, capped test that exists mainly to **produce that cost data** while the renewal intent is live. The founder decides whether to run it (see §10).

---

## 1. Recommendation in one paragraph

**At $300, run Google Search only**, on about 20 high-intent phrase and exact-match keywords, from the day `/check` goes live (target Oct 15) to Dec 12. Expect roughly 30–75 clicks and 3–15 completed checks (estimates, §3). The real return is learning: actual CPCs, the actual search terms, and a landing-page conversion rate. **At $1,000, add a 3-week LinkedIn test** (owners and partners at 2–50 person accounting firms) in the weeks renewal opens, plus a $100 retargeting reserve that only gets spent if the audiences reach the platform minimums. **Skip Meta.** Its B2B targeting is too weak for a 25,000-firm niche (§5). No ad spend before `/check` is live and conversion tracking has been tested.

## 2. Budget and flight

Oct 1–14 is setup (accounts, verification, tags, tests) at **$0 spend**, because the landing page isn't live until about Oct 15 (`../landing-readiness-check.md`). Ads stop on **Dec 12**, which leaves Dec 13–15 for the wrap-up report. Our last Pack intake call is Dec 4 (`../../sales/sequences.md`), so from Dec 5 the ads only feed checks and next season's nurture list.

| Line | $300 level | $1,000 level | Dates | Daily setting |
|---|---|---|---|---|
| Google Search | $295 | $650 | Oct 15 – Dec 12 (59 days) | $5/day ($300) · $11/day ($1,000) |
| LinkedIn single-image | – | $250 | Oct 20 – Nov 9 (21 days) | $12/day (LinkedIn's minimum is $10/day: [Stackmatix, 2026](https://www.stackmatix.com/blog/linkedin-ads-minimum-daily-budget-2026)) |
| Retargeting reserve (Google and/or LinkedIn) | – | $100 | Nov 17 – Dec 5, **only if** audiences reach the minimum | Otherwise give it to Google Search from Nov 17 |
| **Total cap** | **$295** | **$1,000** | | |

**Hard caps the founder sets on day 1:** an end date on every campaign; a LinkedIn campaign-group total budget; and a daily budget on Google. Google can spend up to 2× the daily budget on a single day but it won't charge more than 30.4× the daily budget in a calendar month ([Google Ads Help: average daily budgets](https://support.google.com/google-ads/answer/6385083?hl=en)). That's why every campaign also gets an end date.

## 3. What the money probably buys (all estimates)

No ad account exists, so we have no real bid data. These are **planning ranges built from published benchmarks, not quotes**. The founder should replace them with Keyword Planner's "top of page bid" ranges on the day the account is created (§4, table column "Planner bid").

| Input | Planning value | Basis |
|---|---|---|
| Google CPC, our niche keywords | **$4–$10, midpoint $6** (estimate) | 2025 average across all industries: $5.26; legal and finance terms often $8+ ([WordStream 2025 benchmarks, via search summary](https://www.wordstream.com/blog/2025-google-ads-benchmarks)); tax-related terms $4.50–$15 ([Uncle Kam, 2026](https://unclekam.com/tax-pro-tools/marketing-software/google-ads-tax-firms-guide/)). WISP terms are long-tail B2B, but template sellers bid on them. |
| LinkedIn CPC, owner/partner titles | **$8–$15, midpoint $12** (estimate) | Sponsored Content mostly $5–$12, senior titles $15+ ([Stackmatix, 2026](https://www.stackmatix.com/blog/linkedin-ads-cost); [The B2B House, 2026](https://www.theb2bhouse.com/linkedin-ad-benchmarks/)). |
| LinkedIn CTR | 0.44%–0.65% | Sponsored Content average ([Stackmatix, 2026](https://www.stackmatix.com/blog/linkedin-ads-benchmarks-cpc-ctr-2026)) |
| Click → completed check, Google | **10–20%** (assumption) | High-intent search, a free offer, a 12-question form. No benchmark we trust. |
| Click → completed check, LinkedIn | **5–12%** (assumption) | Colder audience, feed placement. |
| Completed check → paid Pack | 5% (assumption) | Same figure as `../channel-plan.md`. |

| | Clicks | Completed checks | Packs (at 5%) |
|---|---|---|---|
| $300: Google $295 | 30–75 (about 50) | 3–15 (about 7) | 0–1 |
| $1,000: Google $650 | 65–160 (about 108) | 6–32 (about 16) | about 1 |
| $1,000: LinkedIn $250 | 17–31 (about 21) | 1–4 (about 2) | about 0 |
| $1,000: retargeting $100 | 8–25 | 1–3 | about 0 |

**Unit economics (why the thresholds in §7 are what they are).** At the $495 founding Pack price the catalog tests, with 5% of checks becoming Packs, a completed check is worth about **$25** in first-order revenue ($495 × 5%). Watch ($49–$149/mo, catalog §4) adds value later, so we accept up to **$60 per completed check** during this learning season and call anything **≤ $25** a clear win. Price and conversion are both unvalidated, so re-run this math after the first 3 Packs.

## 4. Google Search setup

**Campaign:** `wisp-check-q4-2026` · Search network only (**untick Search Partners and Display**) · Location: United States, **"Presence: people in or regularly in"** (not "interest") · Language: English · All devices · All days.
**Bidding:** Maximize clicks with a **max CPC cap of $8** for the first 3 weeks. Switch to Maximize conversions only if the campaign reaches 15 or more conversions in 30 days (unlikely at this budget).
**Match types:** phrase and exact only. **No broad match**, because at $5–$11/day a broad keyword spends the budget on the wrong "WISP".
**Ads:** 1 RSA per ad group, with assets from `ad-copy.md` §1. **Landing URL:** `[DOMAIN]/check` with UTMs.

### Ad groups and keywords
`"…"` means phrase match and `[…]` means exact match. **Planner bid** is left blank on purpose: fill it from Keyword Planner and don't guess it. If most keywords show "low search volume", add the phrase variants of the same idea. Don't widen to broad.

| Ad group | Level | Keywords | Planner bid (founder fills) |
|---|---|---|---|
| **AG1 WISP for tax firms** (highest intent) | $300 and $1,000 | "wisp for tax preparers" · [wisp for tax preparers] · "wisp template for tax preparers" · "written information security plan for tax preparers" · "written information security plan tax practice" · "wisp for accountants" · "wisp for cpa firm" · "tax practice wisp" · "wisp requirement for tax preparers" · "irs wisp requirement" · "irs written information security plan" · [irs wisp] | |
| **AG2 Safeguards Rule for tax firms** | $300 and $1,000 | "ftc safeguards rule tax preparer" · "ftc safeguards rule tax preparers" · "ftc safeguards rule accountants" · "ftc safeguards rule cpa" · "safeguards rule tax professionals" · "glba tax preparer" · "gramm leach bliley tax preparer" | |
| **AG3 Pub 5708 and W-12** (template seekers, lower bid: cap $5) | $1,000 only | "publication 5708" · "irs pub 5708" · "pub 5708 wisp" · "w-12 wisp" · "w12 security plan" · "ptin wisp" · "ptin security plan" | |

**Don't bid on:** competitor or template-seller brand names; plain "ptin renewal" (people who want to renew their PTIN on irs.gov, not our audience); or anything that makes the ad look like a PTIN service. Google tightens its "Government documents and services" policy from **5 Oct 2026** ([Google Ads policy update](https://support.google.com/adspolicy/answer/17260489?hl=en)). We don't provide any government service, and the copy says so, but keep PTIN wording as context only.

### Negative keywords (campaign level, phrase match unless marked)
| Why | Negatives |
|---|---|
| The other WISPs (hair, internet, a ski resort, a telehealth brand, games) | hair · bangs · wispy · lashes · eyelash · wireless · internet · isp · broadband · tower · resort · ski · deep creek · health · telehealth · birth control · pharmacy · std · will o · game · roblox |
| Other industries under the Safeguards Rule or GLBA | dealer · dealership · auto · car · automotive · mortgage · bank · credit union · university · college · higher education · financial aid · student aid · school |
| Other frameworks | hipaa · dental · soc 2 · iso 27001 · nist · cmmc · pci |
| Jobs and education | job · jobs · career · salary · hiring · resume · course · class · training · cpe · ceu · certification · exam · quiz answers |
| Wrong intent (taxpayers, PTIN admin) | [ptin renewal] (exact) · [renew ptin] (exact) · ptin lookup · ptin login · ptin number · ptin application · ptin fee · efin · refund · where's my refund · stimulus · irs phone · irs login · file taxes · free tax · turbotax · h&r block |
| File downloaders (they want the free IRS PDF) | pdf · download · docx · word document · doc · sample · example |

Review the **search terms report twice a week** and add negatives. That's the single most important routine at this budget.

## 5. LinkedIn setup ($1,000 level only)

**Objective:** Website visits (paid per click, sends people to `/check`, where consent is recorded). **Not** Lead Gen Forms: the check needs the domain-authorization consent recorded on our own page (`../landing-readiness-check.md`, form section).
**Format:** single image, the 3 variants in `ad-copy.md` §2 (images `png/li-1-deadline.png`, `png/li-2-template.png`, `png/li-3-steps.png`).
**Bidding:** manual CPC at the low end of LinkedIn's suggested range, **capped at $12**. **Audience Expansion off. LinkedIn Audience Network off** (keeps spend in the feed, where our title targeting holds).

| Setting | Value |
|---|---|
| Location | United States (permanent location) |
| Company industry | Accounting |
| Company size | 2–10 and 11–50 employees (excludes "Myself only" and 51+) |
| Job titles (any of) | Owner · Co-Owner · Founder · Partner · Managing Partner · Principal · President · CEO · Managing Director · Firm Administrator · Practice Manager · Office Manager · Operations Manager |
| Exclusions | Job function: Information Technology (the MSP-staff audience isn't our buyer this season); our own company's employees |
| Audience size check | LinkedIn needs at least 300 members ([Stackmatix, 2026](https://www.stackmatix.com/blog/linkedin-ads-audience-size)). Aim for 20,000–150,000. Below 20,000, add the skill "Tax Preparation". Above 150,000, drop Office and Operations Manager. **Record the real forecast here:** `[AUDIENCE_SIZE]` |

Why LinkedIn at all, given the higher CPC? It's the only paid channel where we can pick "owner of a 2–50 person accounting firm" directly. It also reinforces the founder's organic LinkedIn channel (`../channel-plan.md` channel 1) with the same faces and messages. Why only $250? At an estimated $12 CPC that's about 21 clicks, enough to compare three hooks by CTR but not to prove conversion. Treat it as a creative test.

## 6. Retargeting ($1,000 level, $100 reserve)

- **Tags:** Google tag and LinkedIn Insight Tag on every page from day one (they're free). The privacy policy and cookie notice must disclose them before they go live (legal-ops).
- **Minimums:** Google needs 100 active users in the list ([Google Ads Help](https://support.google.com/google-ads/answer/7558048?hl=en); change reported by [Search Engine Land](https://searchengineland.com/google-lowers-audience-size-limits-across-ads-466816)). LinkedIn needs 300 matched members ([LinkedIn Help](https://www.linkedin.com/help/lms/answer/a427551)). At the traffic in §3 (roughly 100–200 paid visitors plus organic), **Google will probably qualify and LinkedIn probably won't.**
- **Audiences and copy:** R1–R3 in `ad-copy.md` §3. On Google, use a Display campaign with responsive display ads (square image `png/sq-*.png`, 1200×627 image `png/li-*.png`), frequency cap 3 per week, US only.
- **Release rule:** on **Nov 17**, spend the reserve on retargeting only if a list has reached its minimum. Otherwise move it to Google Search. Stop retargeting on **Dec 5**.
- Retargeting never mentions a visitor's result, domain or gap.

## 7. Conversion goal and tracking

| Event | Definition | Use |
|---|---|---|
| **Primary: `check_completed`** | Form submitted **with the consent box ticked and stored** → `/check/thanks` | The only conversion Google or LinkedIn optimizes toward. Count: one per click. |
| Secondary: `check_started` | First question answered | Observation only. It separates an ad problem from a form problem. |
| Secondary: `pack_call_booked` | Booking confirmation page `/book/thanks` | Observation only. The real business outcome, but too rare to optimize toward. |

- **Test before spending:** complete a test check from an ad preview link and confirm the conversion shows in both platforms (it can take hours). Then exclude your own IP in GA4 if it's used, and delete test leads.
- **No personal data in URLs or tags.** Never put email, name or domain in the thank-you URL or in any tag parameter. No enhanced conversions or customer-list uploads this season.
- **UTMs:** `utm_source=google|linkedin`, `utm_medium=cpc|paid-social`, `utm_campaign=wisp-check-q4`, `utm_content=<ad group or variant>`. Store the UTM source with each check record so paid checks can be counted in `../channel-plan.md` §7 tracking.
- **Weekly (Friday):** add a "Paid" row to the channel-plan tracking sheet with spend, clicks, CPC, checks started, checks completed, cost per completed check and Pack calls.

## 8. Kill and scale rules

Small numbers are noisy, so these are thresholds for decisions, not statistical tests.

**Google Search**
| Trigger | Action |
|---|---|
| Day 3: under 50 impressions total | Keywords are too narrow or showing "low search volume". Add phrase variants from Planner. Don't add broad match. |
| 25 clicks or $100 spent, **0 checks started** | Pause. The problem is the page or the traffic, not the bid. Read the search terms, load the page on a phone, then fix and resume once. |
| Any keyword: $25 spent, 0 completed checks | Pause that keyword. |
| Ad group: CTR under 3% after 500 impressions (our rule of thumb) | Rewrite that group's pinned headline 1 to repeat its main keyword. |
| **$150 spent, cost per completed check over $60** | **Kill** Google. At the $300 level, leave the rest unspent. At the $1,000 level, hold the rest pending a founder decision. |
| Cost per completed check **$25 or less**, and "Search lost IS (budget)" over 40% | **Scale:** raise the daily budget 50%. At the $300 level that means going over $300, so it's a founder decision. At $1,000, use the retargeting reserve. |

**LinkedIn**
| Trigger | Action |
|---|---|
| About 1,500 impressions per variant | Pause the variant with the lowest CTR. |
| $125 spent, overall CTR under 0.40% | Swap in one new hook or image (e.g. `sq-2-w12.png` cropped for the feed) once. |
| Average CPC over $15 after $100 | Narrow titles to Owner, Partner, Managing Partner and Principal, or lower the bid cap. |
| **$200 spent, 0 completed checks** | **Kill** LinkedIn. Move the remaining ~$50 to Google Search if Google's cost per check is $60 or less. Otherwise leave it unspent. |

**Everything**
- Pause all ads at once if `/check` or the form breaks, conversions stop recording, a policy disapproval arrives, or the founder can't deliver results within one business day. That last one matters: ads can't outrun concierge capacity.
- Stop everything on **Dec 12**. Write a one-page result by Dec 15 with real CPCs, CTR, cost per check and the top 20 search terms. That's the input for next October's plan.

## 9. Meta (Facebook and Instagram) and others: not this season

- **Meta: no.** Meta removed job-title, industry and company-size targeting for B2B in 2022, and removed detailed-targeting exclusions in March 2025 ([ContactLevel, 2026](https://www.contactlevel.com/playbooks/meta-job-title-targeting); [Bind Media](https://bind.media/insights/metas-new-b2b-targeting-options-on-facebook-ads); both secondary sources). What's left is broad "business decision-maker" and interest audiences. For about 25,000 target firms (market doc §3a) that means paying mostly to reach people who aren't tax-firm owners, and we have no customer list or site traffic to seed a lookalike. Reconsider only as retargeting next season, if site traffic is large.
- **Microsoft Ads:** could import the Google campaign later and add LinkedIn-profile targeting. Not now: it adds setup work for small volume. Revisit after Google has real data.
- **Reddit ads:** no. `../channel-plan.md` treats r/taxpros as value-first participation, and ads there would undercut that.

## 10. Account control and pre-flight checklist (founder does all of this)

I'm only planning. The founder owns and operates every account.

- [ ] **Founder decision:** run the test at all? At which level: $0, $300 or $1,000? (§11)
- [ ] Domain registered and `/check` live, and a test check completes end to end (gate for any spend).
- [ ] Google Ads account created **by the founder**, signed in with a company address on `[DOMAIN]` (not a personal Gmail). 2-step verification on. Billing on the company card. Time zone set to the founder's local time.
- [ ] Google **advertiser verification** started on Oct 1. It can take several business days, so start early.
- [ ] LinkedIn Campaign Manager ad account created from the founder's profile and linked to a ChimeraShield Company Page. The founder is the only Account Manager. Anyone helping later gets "Campaign manager" or "Viewer" access, removable at any time, and never billing admin.
- [ ] Privacy policy and cookie notice mention the Google tag and the LinkedIn Insight Tag (legal-ops).
- [ ] Legal-ops has approved every regulatory line in `ad-copy.md` and the disclaimer on the images.
- [ ] Conversion `check_completed` has been tested and appears in both platforms.
- [ ] Budgets, end dates and bid caps set exactly as in §2, §4 and §5.
- [ ] Calendar reminders: search-terms review every Mon and Thu (15 min), the Friday tracking row, Nov 17 (reserve decision), Dec 5 (stop retargeting), Dec 12 (stop everything).

## 11. Decisions for the founder

1. **Run paid at all this season?** My recommendation is **yes at $300, Google Search only**, as a cost-data probe that doesn't compete for founder time (about 30 min/week). Go to $1,000 only if `/check` is live by **Oct 20** and conversion tracking is proven.
2. **Resolve the conflict with `../channel-plan.md`**, which lists Google Ads as "not now". Either accept this as a capped learning test outside the two core channels, or decline it.
3. **Unit-economics threshold:** keep the $60 maximum cost per completed check, or tighten it to $25 (breakeven on the first order)?
4. **Pack price** ($495 founding vs. $795 list) changes the math in §3. Tell me which one to use.

## Sources
- IRS PTIN renewal FAQ: https://www.irs.gov/tax-professionals/frequently-asked-questions-ptin-application-renewal-assistance
- WordStream, Google Ads benchmarks 2025 (via search summary; direct fetch blocked by this session's proxy): https://www.wordstream.com/blog/2025-google-ads-benchmarks
- Uncle Kam, Google Ads for tax firms (2026): https://unclekam.com/tax-pro-tools/marketing-software/google-ads-tax-firms-guide/
- Stackmatix, LinkedIn Ads cost (2026): https://www.stackmatix.com/blog/linkedin-ads-cost
- Stackmatix, LinkedIn benchmarks (2026): https://www.stackmatix.com/blog/linkedin-ads-benchmarks-cpc-ctr-2026
- Stackmatix, LinkedIn minimum daily budget (2026): https://www.stackmatix.com/blog/linkedin-ads-minimum-daily-budget-2026
- Stackmatix, LinkedIn audience size: https://www.stackmatix.com/blog/linkedin-ads-audience-size
- The B2B House, LinkedIn ad benchmarks (2026): https://www.theb2bhouse.com/linkedin-ad-benchmarks/
- LinkedIn Help, retargeting with Matched Audiences: https://www.linkedin.com/help/lms/answer/a427551
- Google Ads Help, audience segments: https://support.google.com/google-ads/answer/7558048?hl=en
- Search Engine Land, Google lowers audience size limits: https://searchengineland.com/google-lowers-audience-size-limits-across-ads-466816
- Google Ads Help, average daily budgets: https://support.google.com/google-ads/answer/6385083?hl=en
- Google Ads policy update, Government documents and services (Oct 2026): https://support.google.com/adspolicy/answer/17260489?hl=en
- ContactLevel, Meta job-title targeting (2026): https://www.contactlevel.com/playbooks/meta-job-title-targeting
- Bind Media, Meta B2B targeting options: https://bind.media/insights/metas-new-b2b-targeting-options-on-facebook-ads

All benchmark figures come from search-result summaries of secondary sources on 2026-09-24. Page fetches were blocked by this session's network proxy. Treat every cost figure as an estimate until the founder's own accounts show real numbers.
