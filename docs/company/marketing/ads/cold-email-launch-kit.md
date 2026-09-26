# Cold email launch kit (for the founder)

**Owner:** growth-marketer · **Date:** 2026-09-24 · **Updated:** 2026-09-26 by head-of-sales (Spam Act 2003: steps 1, 2, 4–9) · **Status:** a step-by-step for the founder to carry out. No agent has sent email, bought a domain or created an account.

> **Spam Act 2003 applies (2026-09-26).** The founder sends from Australia, so every cold email to a US firm must meet the Australian Spam Act **and** CAN-SPAM (`docs/company/legal/spam-act-cold-email.md`). Short version: email only addresses the firm or person published themselves, where the message relates to their role, with evidence saved per address; no Apollo-type databases, enrichment tools, scrapers or guessed addresses; the ABN and an unsubscribe line in every email, actioned within 5 business days (our standard: same day). **No ABN, no cold send.**
**Sends:** the sequences in `docs/company/sales/sequences.md`, following `.claude/skills/outreach-writing/SKILL.md`. **Volume targets:** `docs/company/sales/playbook.md` §5.3. **Channel plan:** `docs/company/marketing/channel-plan.md` (channel 2). **Merge file:** `mail-merge-template.csv` (header only).

**Timeline at a glance**

| When | Step |
|---|---|
| By **Sep 28** | Buy the secondary domain, create the mailbox, publish SPF, DKIM and DMARC (steps 1–3) |
| **Sep 28 – Oct 11** | 14-day warm-up (step 4). **No cold email.** |
| Oct 9–10 | Seed test and list check (steps 4 and 7) |
| By **Oct 11** | ABN issued (entity or founder's sole-trader ABN), `[US_POSTAL_ADDRESS]` live, evidence Sheet built (step 7) |
| **Oct 12** | First cold sends, up to 10 a day total (playbook week S1), only to evidenced addresses |
| Oct 12 – Dec 11 | Ramp to at most 25 total sends a day (step 5). Expected volume is lower: ~20–25 new prospects a week |
| **Dec 18** | Stop cold outreach for the year (channel plan) |

Every price below is an **estimate from search-result summaries on 2026-09-24**. Check the vendor's pricing page before you buy.

---

## Step 1. Secondary sending domain

1. **Main domain first.** Pick and register the main domain (e.g. `chimerashield.com`) after the name screen in `docs/company/legal/launch-checklist.md` 1.1. The channel plan §6 lists the options. Don't use anything containing "irs", "ptin", "5708" or "gov".
2. **Buy the secondary domain** at the same registrar, e.g. `get[DOMAIN]` (such as `getchimerashield.com`, if the main domain is `chimerashield.com`). Turn on registrar-account MFA, auto-renew and domain privacy.
3. **Redirect its website** with a 301 redirect to `https://[DOMAIN]`, so anyone who types it lands on the real site.
4. **Use it only for cold email.** Replies, the readiness-check result email and anything customers expect to receive come from the main domain. If the secondary domain's reputation drops, the main domain isn't affected.
5. Every email still says **ChimeraShield Pty Ltd**, gives your real name, the **ABN** and the `[US_POSTAL_ADDRESS]`. A second domain protects reputation. It never hides who is sending. The mailbox must keep working for at least 30 days after the last send (Spam Act and CAN-SPAM).

## Step 2. Mailbox

- **Google Workspace Business Starter**, one user on the secondary domain: `[FOUNDER_NAME]@get[DOMAIN]`. About **$7/user/mo on an annual plan, or $8.40 on the flexible plan** (estimate: [name.com, 2026](https://www.name.com/blog/google-workspace-pricing); [Google pricing page](https://workspace.google.com/pricing)).
- Add free aliases to the same inbox: `dmarc@get[DOMAIN]` (for DMARC reports) and `hello@get[DOMAIN]`.
- Turn on 2-step verification with a security key or authenticator app, not SMS.
- Set a real profile photo and name ("[FOUNDER_NAME] · ChimeraShield") and a plain signature that matches `sequences.md`.
- **One inbox is enough.** The playbook now plans only ~15–25 new email prospects a week (~160 in total), because the Spam Act limits us to evidenced, self-published addresses. One inbox at ≤25 total sends a day covers that easily. Don't add inboxes to raise volume: the constraint is the lawful list, not sending capacity.

## Step 3. SPF, DKIM, DMARC (secondary domain)

Google requires SPF **and** DKIM for everyone sending to Gmail, and DMARC for bulk senders ([Gmail email sender guidelines](https://support.google.com/mail/answer/81126?hl=en)). We set up all three, because ChimeraShield checks these records for customers and ours have to be right.

| Record | Host | Type | Value |
|---|---|---|---|
| MX | `@` | MX | The value the Google Workspace setup wizard shows you. Copy it exactly. |
| SPF | `@` | TXT | `v=spf1 include:_spf.google.com ~all` |
| DKIM | `google._domainkey` | TXT | Generate it in Admin console → Apps → Google Workspace → Gmail → **Authenticate email**, with a **2048-bit** key. Publish the record, wait for DNS, then click **Start authentication**. |
| DMARC | `_dmarc` | TXT | `v=DMARC1; p=none; rua=mailto:dmarc@get[DOMAIN]; adkim=r; aspf=r; pct=100` |

- **Only one SPF record per domain.** If your sending tool asks you to add its own include, **merge** it into this record. Don't add a second one.
- **Don't add a sending tool's own mail servers** if the tool sends through your Google account (GMass, YAMM, Instantly and Smartlead all do when connected to Google). Nothing else changes.
- **Check the records:** send a test to a Gmail address, open it, choose "Show original", and confirm SPF, DKIM and DMARC all say **PASS**. Also run the domain through our own readiness check once it's live.
- **DMARC progression:** stay at `p=none` for the warm-up plus 2 weeks. Once reports show only Google sending for the domain and everything passing, change it to `p=quarantine`. Do the same on the main domain (channel plan §6).
- **Google Postmaster Tools:** add and verify the secondary domain at postmaster.google.com. Its spam-rate chart is the main health signal once volume starts.
- Main domain: the same three records, plus `security@` and `hello@`. That's the tech lead's G1 gate in the playbook.

## Step 4. 14-day warm-up (Sep 28 – Oct 11), no cold email

New domains and mailboxes have no reputation, so start slowly. The goal is a real, two-way mail history.

**Two ways to warm up. Pick one or combine them:**
- **A. Tool warm-up.** Instantly and Smartlead include automatic warm-up: your inbox trades emails with a pool of other inboxes, which open them, reply to them and mark them "not spam". It's cheap and hands-off. The downside is that it's artificial engagement, so treat it as a support and not a substitute for real mail.
- **B. Manual warm-up (always do some).** Real emails to real people who expect to hear from you and will reply: advisers, friends, vendors, your accountant, the co-founder's inbox, and newsletters you actually signed up for. Reply to the replies.

| Day | Date | Warm-up emails/day (tool) | Real emails/day (manual) | Cold emails | Do this too |
|---|---|---|---|---|---|
| 1 | Sep 28 | 5 | 2–3 | 0 | Records pass ("Show original"). Signature set. |
| 2 | Sep 29 | 5 | 2–3 | 0 | |
| 3 | Sep 30 | 8 | 3 | 0 | |
| 4 | Oct 1 | 8 | 3 | 0 | Register Postmaster Tools |
| 5 | Oct 2 | 10 | 3–5 | 0 | |
| 6 | Oct 3 | 10 | 2 | 0 | Weekend: keep it light |
| 7 | Oct 4 | 10 | 2 | 0 | |
| 8 | Oct 5 | 12 | 5 | 0 | Load the first 40 **evidenced** prospects into the tool (not scheduled). Every row has `source_url`, `evidence_file` and `consent_basis` |
| 9 | Oct 6 | 15 | 5 | 0 | |
| 10 | Oct 7 | 15 | 5 | 0 | |
| 11 | Oct 8 | 18 | 5 | 0 | |
| 12 | Oct 9 | 20 | 5 | 0 | **Seed test:** send touch 1 (filled in for a test firm) to 4–6 of your own accounts at Gmail, Outlook.com, Yahoo and a Microsoft 365 work address. Note inbox or spam for each. |
| 13 | Oct 10 | 20 | 3 | 0 | Fix anything the seed test flagged, then re-test |
| 14 | Oct 11 | 20 | 3 | 0 | Go/no-go: all records pass, seeds reach the inbox, no bounces |

**Don't start cold sends if** any seed lands in spam, any record fails, `[ABN]` or `[US_POSTAL_ADDRESS]` is still a placeholder, the unsubscribe line is missing, or any loaded row lacks consent evidence. Keep tool warm-up running at 10–20 a day for as long as you send cold email.

## Step 5. Daily volume caps (per inbox)

The ramp stays inside the outreach skill's warm-up limits (5–10 a day in week 1, about 30 a day by week 4) and the playbook's weekly targets (§5.3), which are now lower because the lawful list is smaller.

These are **ceilings**. The Spam Act-limited list (playbook §5.3) means the real numbers will usually sit well below them.

| Week of (US) | Planned new email prospects / week | New first touches / day (cap) | Total sends / day incl. follow-ups (cap) | Days (recipient time) |
|---|---|---|---|---|
| Oct 12 (S1) | 15 | 5 | 10 | Mon–Fri |
| Oct 19 (S2) | 20 | 6 | 15 | Mon–Fri |
| Oct 26 (S3) | 25 | 8 | 20 | Mon–Fri |
| Nov 2 – Nov 20 (S4–S6) | 25 | **8 (hard cap)** | **25 (hard cap)** | Mon–Fri |
| Nov 23 (S7) | 10 | 8 | 25 | Mon–Wed only (Nov 26 is Thanksgiving) |
| Nov 30 (S8) | 15 | 8 | 25 | Mon–Fri |
| Dec 7 | 0 new | 0 | follow-ups only | |
| Dec 18 | stop | stop | stop | |

**Pause at once** (channel plan §5): bounces over 3% in any week, any spam placement in a weekly seed test, or the Postmaster spam rate climbing toward 0.3% (the Gmail sender guidelines above say to stay below 0.3%). Cut volume in half for a week, clean the list and re-check the records.

- Send Tuesday to Thursday mornings (08:00–11:00) in the recipient's time zone. Use Mondays and Fridays for follow-ups only. Space sends 2–5 minutes apart (every tool below can do this).
- **Sending from Sydney:** US Tue–Thu 08:00–11:00 Pacific is about **02:00–06:00 Sydney, Wed–Fri** (03:00–06:00 after Nov 1). Load and **schedule** the next day's sends in the Sydney late morning; never send by hand overnight. Set the tool's time zone per row from `state`, not from your own clock.
- Plain text, no images, no attachments. **Turn off open tracking and click tracking.** Tracking pixels and redirected links hurt deliverability, and we tell prospects we don't track them covertly.

## Step 6. Sending tool: options

| Option | Rough price (estimate) | Warm-up included | Sequences + stop on reply | Fit |
|---|---|---|---|---|
| **Google Workspace + GMass** | Standard about **$29.95/mo**, Premium about $39.95/mo ([GMass price change note, Jan 2026](https://www.gmass.co/blog/price-changes-jan-2026/); [Clay summary](https://www.clay.com/blog/gmass-pricing)) | No (use manual warm-up, or add a warm-up service) | Yes: auto follow-ups, stop on reply, sends from inside Gmail | **Recommended for one inbox at ≤30 a day.** It's simplest, and every message sits in your normal Gmail Sent folder. |
| **Google Workspace + YAMM** (Yet Another Mail Merge) | Personal about **$25/year**, Professional about $50/year ([Mailmeteor summary](https://mailmeteor.com/blog/yamm-pricing); [YAMM pricing](https://yamm.com/pricing/)) | No | A basic mail merge from Google Sheets. Follow-ups are more manual. | Cheapest. Fine for touch 1, but a 4-touch sequence with stop-on-reply takes manual work. |
| **Instantly** | Growth about **$47/mo**, or $37.60/mo billed annually ([Woodpecker summary](https://woodpecker.co/blog/instantly-ai-pricing/); [Landbase](https://www.landbase.com/blog/instantly-ai-pricing)) | Yes | Yes, with a unified inbox across mailboxes | Pick this if you want built-in warm-up or expect to add inboxes. |
| **Smartlead** | Basic about **$39/mo** ([Smartlead pricing](https://www.smartlead.ai/pricing); [La Growth Machine summary](https://lagrowthmachine.com/smartlead-pricing/)) | Yes | Yes | Similar to Instantly. Choose on UI preference. |
| **Apollo** | Basic about **$59/user/mo**, or $49 billed annually ([Warmly summary](https://www.warmly.ai/p/blog/apollo-pricing); [Landbase](https://www.landbase.com/blog/apollo-pricing)) | Yes | Yes, plus a contact database | **Not recommended.** Its database is **banned as a source** under the Spam Act (addresses not published by the recipient; possibly a harvested-address list). If ever used, it is a **sender only**, with our own evidenced list, and its database and enrichment features must stay off. |

**Suggested setup:** Workspace (about $7–8.40/mo) + GMass Standard (about $30/mo) + manual warm-up, **about $37–38/mo** (estimate). Move to Instantly or Smartlead only if you add inboxes.
**Email verification:** run the list through a verifier before each upload (most tools above include one, or have a paid add-on). Aim for a bounce rate under 3%. A verifier only checks addresses we already evidenced; it must never be used to find or guess addresses.

**Banned tools and features (Spam Act "address-harvesting" risk):** contact databases and enrichment (Apollo, ZoomInfo, RocketReach, Clearbit, Lusha and similar), "email finder" tools (Hunter and similar), pattern guessers, browser extensions or scrapers that collect addresses from websites or LinkedIn, and purchased or rented lists. Any built-in lead database or lead finder in Instantly or Smartlead is also off. Build the list by hand.

## Step 7. Building the list (`mail-merge-template.csv`)

Header only, and no real people in the repo. Keep the working list and the evidence in your own Google Sheet and Drive folder, not in git.

**Rule: no evidence, no send.** Under the Spam Act the burden of showing consent is on us, so every row needs the evidence columns below before it is uploaded. Allowed sources are listed in `docs/company/sales/playbook.md` §3.4: the firm's own website first; a directory profile only if the directory's terms allow solicitation and legal-ops has cleared it; express-consent sources (Readiness Check opt-in, ads opt-in, partner intro). Never the PTIN extract, databases, enrichment tools, scrapers or guesses.

| Column | What goes in it | Rule |
|---|---|---|
| `id` | Pipeline id | Joins to `docs/company/sales/pipeline.csv` |
| `first_name` | The contact's first name, as it appears on the source page | Required |
| `firm_name` | The firm's everyday name (e.g. "Example & Co. CPAs", not "Example & Co. CPAs, LLC") | Required |
| `city` | Office city | Required |
| `state` | Two-letter state code | **US only** in this kit. Drop Canadian rows (CASL). Sets the send time zone. |
| `country` | `US` | AU pilot contacts go in a separate campaign (`docs/company/sales/australia-pilot.md`) |
| `role` | Owner / Managing partner / QI / Ops lead with an IT role / generic inbox | Helpers only if the site shows they handle operations or IT. Prefer the owner's address over `info@`. |
| `trigger` | The **personal first line**, written by hand, true, 12 words or fewer | Must be checked against the source. If you can't write one in 2 minutes, skip the prospect. Never mention their domain, DNS or security settings. |
| `email` | The exact address shown on the source page | **Published by the firm or the person themselves.** Not guessed, not from a database or tool, not from a PDF, not from LinkedIn. |
| `source_label` | Short text for the footer's `[SOURCE]`, e.g. "your firm's website" | Must match `source_url` |
| `source_url` | The exact page showing the address | e.g. `https://example-firm.com/contact` |
| `source_checked_date` | ISO date you checked the page | Re-check if older than 60 days at send time |
| `evidence_file` | Drive link to a saved PDF or screenshot of the page | Required |
| `no_marketing_statement` | `none seen` / `present → excluded` | Any "no solicitation" or "not for marketing" note excludes the row |
| `directory_terms_ok` | `n/a (firm site)` / `yes` / `no → excluded` | Directory terms that ban commercial solicitation exclude the row |
| `consent_basis` | `inferred: conspicuous publication` / `express: [form or intro], [date]` / `inferred: existing relationship` | Never `none: LinkedIn only` in this file |

Before each upload: dedupe against `docs/company/sales/pipeline.csv` (don't sequence anyone already in discovery or opted out), and against the suppression list (step 9). Keep the evidence for at least 2 years after the last message (legal-ops to confirm the period).

## Step 8. Loading `sequences.md` into the tool

1. **One campaign per touch-1 variant:** `A1-CPA`, `A1-EA`, `A1-EVENT`, `A1-ADMIN`. Split the sheet by variant, since the variant depends on who they are and what the trigger is.
2. **Map the placeholders to merge fields** (GMass and YAMM use the sheet's column names, and Instantly and Smartlead use `{{column}}`):

| `sequences.md` placeholder | Merge field |
|---|---|
| `[FIRST_NAME]` | `{first_name}` |
| `[FIRM]` | `{firm_name}` |
| `[CITY]` | `{city}` |
| `[PERSONAL_LINE]` / `[SHORT_PERSONAL_LINE]` | `{trigger}` |
| `[EVENT]` (A1-EVENT only) | Write the event name into `{trigger}` and edit the line so it reads naturally |
| `[SOURCE]` (footer) | `{source_label}` |
| `[FOUNDER_NAME]`, `[DOMAIN]`, `[ABN]`, `[US_POSTAL_ADDRESS]`, `[READINESS_CHECK_URL]` | **Type the real values into the template itself.** They're the same for everyone. |

3. **Steps and waits:** Step 1 = A1 variant (day 0). Step 2 = A2, **3 days** later. Step 3 = A3, **5 days** after step 2. Step 4 = A4, **7 days** after step 3. Send steps 2–4 **as replies in the same thread** (keep the "re:" subject for A2, per sequences.md).
4. **Touch 1 has no links** (sequences.md). The first link is A3's `[READINESS_CHECK_URL]`. If the check isn't live, use the fallback line in sequences.md.
5. **Settings:** plain text; open and click tracking **off**; **stop on reply** (any reply, including "not now"); **stop for the whole firm's domain on reply** if the tool supports it; daily cap from step 5; send window Tue–Thu 08:00–11:00 in recipient time (scheduled, step 5); skip Nov 26–27.
6. **Footer:** paste footer F1 (owners) or F2 (ops leads) from `sequences.md` into every step. It carries the ABN, `[US_POSTAL_ADDRESS]`, the "I found your address on {source_label}" line and the unsubscribe line. Never shorten it.
7. **Pre-send check:** preview 5 random rows. Search each preview for `[` and `{`. If either appears, a placeholder or merge field is unfilled, so don't send. Check each body (greeting to ask) is 65 words or fewer (sequences.md word-count check).
8. **Log it:** each Monday (Sydney), export sends, replies and opt-outs and update `docs/company/sales/pipeline.csv` (`sequence`, `touch_step`, `last_touch_date`, `opted_out`). Check unsubscribes **daily**, not weekly.

## Step 9. CAN-SPAM and Spam Act checklist (check before the first send and monthly)

Based on the [FTC CAN-SPAM Compliance Guide for Business](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) and `docs/company/legal/spam-act-cold-email.md` (Australian Spam Act 2003, which applies because we send from Australia). Both laws apply to B2B email; where they differ, follow the stricter one. This is not legal advice: legal-ops confirms it.

**Consent and sources (Spam Act)**
- [ ] **Consent evidence for every address** (step 7): `source_url`, `source_checked_date`, `evidence_file`, `no_marketing_statement`, `directory_terms_ok`, `consent_basis`. No evidence, no send.
- [ ] **Only self-published addresses** relevant to the recipient's role, or express consent. No guessed addresses, no databases or enrichment tools, no scrapers or extensions, no purchased lists, no PTIN-extract emails (no harvested-address lists).
- [ ] **No consent-request emails** ("can I send you info?"). They are commercial messages themselves.

**Identity and content (both laws)**
- [ ] **Accurate header information:** From name "[FOUNDER_NAME] · ChimeraShield", a real mailbox, and a Reply-To that you read.
- [ ] **Entity name and ABN in every email:** "ChimeraShield Pty Ltd (ABN [ABN])", or the founder's name and sole-trader ABN if the company isn't registered yet. Contact details stay valid for at least 30 days after the last send.
- [ ] **Honest subject lines** that match the body. The sequences.md subjects qualify: no "re:" on a first touch and no fake urgency.
- [ ] **Identify the message as an ad / say why they're getting it.** The footer line "I found your address on [SOURCE] and am writing because you run a tax practice." does both jobs. **Legal-ops confirms the wording** (G3c) before the first send.
- [ ] **Valid physical postal address** in every email: `[US_POSTAL_ADDRESS]`. A registered PO box or a private mailbox at a commercial mail receiving agency is acceptable (FTC guide). A US virtual mailbox is the safer choice; the lawyer confirms whether an Australian address would do. Playbook gate G3.

**Unsubscribe (stricter Spam Act timing)**
- [ ] **Unsubscribe line in every email:** "Not relevant? Reply "unsubscribe" (or just "no") and I won't email you again." (It replaces the old "I won't follow up" line.) Add a one-click unsubscribe link too if the tool supports it.
- [ ] **Action it within 5 business days** (Spam Act; CAN-SPAM allows 10). **Our standard is the same day.** Check replies daily.
- [ ] It removes the person from **all** our marketing on every channel (email and LinkedIn), not just this sequence, and suppresses the whole firm unless someone else there asked to hear from us.
- [ ] The opt-out keeps working for **at least 30 days** after each send, which means keeping the mailbox open after the campaign ends.
- [ ] **No fee, login or extra steps** to opt out, and no asking for anything beyond the email address.
- [ ] **Suppression list:** everyone who opts out goes on a permanent "do not contact" list (a Sheet tab), mark `opted_out` in pipeline.csv. Never sell or transfer those addresses.

**General**
- [ ] **You're responsible** even when a tool sends the email. Check the tool's settings yourself.
- [ ] **Scope:** US business addresses only in this kit. No EU/UK (GDPR/PECR) or Canadian (CASL) contacts this season. Australian pilot contacts follow `docs/company/sales/australia-pilot.md` (same Spam Act rules, no CAN-SPAM).
- [ ] **Gmail sender rules:** SPF and DKIM pass, and the spam rate stays under 0.3% ([Gmail sender guidelines](https://support.google.com/mail/answer/81126?hl=en)). The one-click unsubscribe requirement applies at 5,000+ messages a day to Gmail, which is far above our volume, but add it anyway if the tool makes it easy.

## Step 10. Weekly health routine (15 minutes, Mondays in Sydney = US weekend)

1. Bounce rate (target under 3%), reply rate, opt-outs (all actioned the same day?), positive replies, and any complaint (a complaint means pause and tell legal-ops).
2. Postmaster Tools spam rate and domain reputation.
3. Seed test touch 1 to your 4–6 test accounts.
4. DMARC reports: anything unexpected sending as your domain?
5. Apply the channel plan's pause, kill and scale rules (channel plan §5).
