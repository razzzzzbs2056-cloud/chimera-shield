# Spam Act 2003 (Cth) and our cold email and LinkedIn plan

> **Draft for discussion. Not legal advice. Review with a qualified lawyer in your jurisdiction.**

**As of:** 2026-09-26 · **Owner:** legal-ops agent · **Status:** first draft for an Australian-resident founder
**Changes:** `docs/company/marketing/ads/cold-email-launch-kit.md` (steps 6, 7 and 9), `docs/company/sales/sequences.md` (signature and opt-out line), and `docs/company/sales/playbook.md` §7. The growth-marketer and head-of-sales should make the edits listed in §7 below **before the first cold send (planned 12 Oct)**.

**Evidence note.** On 2026-09-26 the network proxy blocked acma.gov.au, asic.gov.au and legislation.gov.au. Facts below come from **search-result summaries** of the linked pages (ACMA, AustLII and law-firm pages), accessed 2026-09-26. They are marked **(S)**. Before relying on them, open the ACMA page and the Act itself on the [Federal Register of Legislation](https://www.legislation.gov.au/C2004A01214/latest/text). **FLAG** marks anything I'm unsure of.

---

## 1. Why this applies to us, even though the recipients are American

- The Spam Act prohibits sending a **commercial electronic message** that has an **"Australian link"** unless the recipient consented (s 16) (S).
- A message has an Australian link if, among other things, it **originates in Australia**, or the sender is an **individual physically present in Australia** or an **organisation whose central management and control is in Australia** when it is sent ([Spam Act s 7, AustLII](https://classic.austlii.edu.au/au/legis/cth/consol_act/sa200366/s7.html)) (S).
- The founder lives and works in Australia. **Every email and LinkedIn message we send to a US firm has an Australian link**, whatever entity sends it (a sole trader, an Australian Pty Ltd, or a Delaware company run from Australia).
- **CAN-SPAM still applies as well** because the recipients are in the US. **We must meet both laws.** In practice that means the Spam Act's consent rule plus CAN-SPAM's postal-address rule.

## 2. How the Spam Act differs from CAN-SPAM

| Topic | US CAN-SPAM (what the kit was built for) | Australian Spam Act (what now also applies) |
|---|---|---|
| Model | **Opt-out.** You may send a first commercial email without consent if you follow the rules. | **Opt-in.** You need **consent before the first message**: express or inferred. |
| Can the first email ask for permission? | Yes | **No.** A message asking for consent to send marketing is itself a commercial message, so it needs consent too (ACMA view, S). |
| B2B exemption | None, but B2B is practical under opt-out | None. Inferred consent via "conspicuous publication" (§3) is the main B2B route. |
| Identify the sender | Accurate header and "From" | Clearly and accurately identify the individual or organisation that **authorised** the message, with contact details **valid for at least 30 days** after sending. ACMA says an Australian company should include its **ABN** (S: [Corrs](https://www.corrs.com.au/insights/acma-spam-act-enforcement-and-the-implications-for-business)). |
| Postal address | **Required** | Not specifically required, but CAN-SPAM requires it for our US recipients anyway |
| Unsubscribe | Honour within **10 business days**; works for 30 days | Honour within **5 business days**; works for **at least 30 days**; no fee; clear instructions (S: [ACMA unsubscribe fact sheet PDF](https://www.acma.gov.au/sites/default/files/2024-05/Fact%20sheet%20-%20email%20and%20SMS%20unsubscribe%20rules.pdf)) |
| Burden of proof | On the regulator | **On the sender** to show consent (evidential burden). **FLAG:** confirm the subsection. This is why we keep evidence for every address. |
| Harvesting tools | Aggravating factor | Supplying, acquiring or **using address-harvesting software or harvested-address lists** is separately prohibited (Spam Act Part 3). **FLAG:** confirm the sections. |
| Channels | Email | Email, SMS, MMS and **instant or direct messages, including social-media accounts** (S: [Holding Redlich](https://www.holdingredlich.com/the-importance-of-compliance-with-the-spam-act); [Allens, Oct 2025](https://www.allens.com.au/insights-news/insights/2025/10/Push-notifications-links-and-compliance-lessons-for-all-businesses-from-ACMAs-recent-investigations/)) |

## 3. Consent: what we can lawfully rely on

**Express consent.** The person asked for it: they filled in a form, replied "yes, send it", or ticked a box. This is the best basis. It covers inbound leads, Readiness Check sign-ups (with a marketing tick box) and people who replied to a LinkedIn post asking for info.

**Inferred consent from an existing relationship.** For example, a current customer, or an interviewee who later asks to hear about the product. The message must relate to that relationship.

**Inferred consent from "conspicuous publication."** This is the only route for true cold email. **All** of these must be true for each address (S: [ACMA "Avoid sending spam"](https://www.acma.gov.au/avoid-sending-spam); [DW Fox Tucker](https://www.dwfoxtucker.com.au/2023/12/when-can-you-send-unsolicited-electronic-messages); [Ashurst](https://www.ashurst.com/en/insights/acma-goes-ham-on-spam-is-your-business-in-breach-of-the-spam-act/)):

1. The address is **conspicuously published**: easy to find on the firm's own website, or on a professional directory where the person chose to list it as a business contact.
2. It is reasonable to assume it was published **with the account-holder's agreement**. The firm's own site or the person's own directory profile qualifies. A data broker, an enrichment tool or a scraped PDF does not.
3. There is **no statement** with it saying the person doesn't want commercial messages (e.g. "no solicitations", "not for marketing purposes"). **We also treat a directory's terms of use that ban commercial solicitation as such a statement.** That's a conservative reading (**FLAG** for the lawyer).
4. The message is **directly relevant to the recipient's business role or functions.** A WISP and Safeguards message to the owner, managing partner or Qualified Individual of a US tax firm is relevant. The same email to a bookkeeper at a dental clinic is not.

**Enforcement example on point:** ACMA found **Oneflare** couldn't infer consent from numbers in public directories because the messages didn't relate to the recipients' work. Oneflare paid a **A$75,600** infringement notice (Nov 2019) (S: [ACMA](https://www.acma.gov.au/articles/2019-11/oneflare-pays-75600-infringement-notice-spamming); [LegalVision](https://legalvision.com.au/oneflare-spam-act-lessons-for-business-owners/)). "It was public" is not enough.

### What this rules out (changes to the current kit)

| Source or practice | Before (CAN-SPAM view) | Now |
|---|---|---|
| Address on the firm's own website contact or team page, no "no solicitation" note, sent to a relevant role | OK | **OK.** Keep evidence (§5). |
| Address on the person's own NAEA, NATP or state-society directory profile | OK if the terms allow | **OK only if** the directory terms don't prohibit solicitation **and** there's no statement against marketing. Otherwise LinkedIn or the website only. |
| Guessed pattern (`firstname@firm.com`) | Already banned | **Banned.** Not published, so no inferred consent. |
| Addresses from enrichment or database tools (Apollo, Hunter, ZoomInfo, "CPA email lists") | Apollo "sender only" allowed | **Banned as a source.** Not conspicuously published by the recipient, and possibly a harvested-address list. Apollo may be used **only** as a sending tool with our own evidenced list, but GMass is still the recommendation. |
| Scraping tools or browser extensions that collect addresses | Not addressed | **Banned.** Risk of "address-harvesting software". Build the list by hand. |
| IRS PTIN FOIA extract | Research only | Research only (unchanged). **Never email from it.** |
| Generic inbox (`info@`, `office@`) | OK | **OK if** published on the firm's site and the message is about the firm's own security plan. Relevance is weaker than for a named owner, so prefer the owner's published address. |
| Helper roles (office or practice manager) | OK | **Only if** the site shows they handle operations or IT. Otherwise message the owner. |
| "Can I send you info?" permission email | Seen as harmless | **Banned.** Consent requests are commercial messages. |

## 4. Every message must identify us and let people unsubscribe

**Identify (every email and every commercial DM):**
- Sender's name and role: `[FOUNDER_NAME]`, Founder
- Legal entity and ABN: `ChimeraShield Pty Ltd, ABN [ABN]`. **FLAG:** use the founder's own name and ABN if we're still a sole trader when sending starts.
- A working contact email: `[FOUNDER_NAME]@[DOMAIN]`, which must keep working for at least 30 days after the **last** send
- `[POSTAL_ADDRESS]` for CAN-SPAM. **FLAG:** an Australian business address or PO box is probably a "valid physical postal address" under CAN-SPAM, but the FTC guidance is written for US senders. A US virtual mailbox (the finance budget's line 3) is the safer choice. The lawyer should confirm.

**Unsubscribe line (replace the current "Reply 'no' and I won't follow up"):**
> Not relevant? Reply "unsubscribe" (or just "no") and I won't email you again.

- It must remove the person from **all** future marketing messages from us, not just this sequence. Also suppress the whole firm unless another person there asked to hear from us.
- Our standard is **same day**. The legal maximum is **5 business days** under the Spam Act, which is stricter than CAN-SPAM's 10.
- Keep the mailbox and any unsubscribe link working for at least **30 days after the last send**. The kit already says to keep the mailbox open after 18 Dec.
- No fee, no login and no questions to unsubscribe.

**Example footer (for the lawyer to approve):**
```
[FOUNDER_NAME], Founder, ChimeraShield Pty Ltd (ABN [ABN])
[FOUNDER_NAME]@[DOMAIN] · [POSTAL_ADDRESS]
I found your address on [SOURCE, e.g. your firm's website] and I'm writing because you run a tax practice.
Not relevant? Reply "unsubscribe" (or just "no") and I won't email you again.
```
The "why you're getting this" line also serves as CAN-SPAM's advertisement disclosure (kit Step 9). **FLAG:** the lawyer confirms the wording for both laws.

## 5. Evidence we keep for every address

Add these columns to the working list. They stay **outside git**, in the founder's Google Sheet, like the rest of the list.

| Column | Content |
|---|---|
| `source_url` | The exact page showing the address |
| `source_checked_date` | ISO date |
| `evidence_file` | A saved PDF or screenshot of the page (in a Drive folder, not the repo) |
| `no_marketing_statement` | `none seen` / `present → excluded` |
| `directory_terms_ok` | `n/a (firm site)` / `yes` / `no → excluded` |
| `role` | Owner / Managing partner / QI / Ops lead with an IT role / generic inbox |
| `consent_basis` | `inferred: conspicuous publication` / `express: [form, date]` / `inferred: existing relationship` |

**Keep the evidence for at least 2 years after the last message.** That period is my suggestion; **FLAG:** the lawyer sets the retention period. Consent disputes happen after complaints, and the burden of proof is on us.

## 6. Penalties and enforcement

- **Tools ACMA uses:** formal warnings, **infringement notices**, court-enforceable undertakings (often with independent audits), and **Federal Court civil penalty** proceedings (S: [ACMA infringement notices](https://www.acma.gov.au/infringement-notices); [Sparke Helmore](https://www.sparke.com.au/insights/spam-in-the-spotlight-acma-raises-the-stakes-for-business-messaging/)).
- **Maximum civil penalties** (s 25; S). For **two or more contraventions of the consent rule on one day**: a body corporate faces up to **2,000 penalty units per day** with no prior record, and **10,000** with a prior record. At **A$364 per penalty unit** (reported as the value from 1 July 2026; it was A$330 from 7 Nov 2024), that is about **A$728,000 and A$3.64M per day**. Individuals (for example a sole trader) have lower caps. **FLAG:** I haven't verified the individual figures, the per-contravention tiers or the A$364 value against the Act. Check them.
- **Recent examples (all S):**
  | When | Who | What | Outcome |
  |---|---|---|---|
  | Oct 2024 | Commonwealth Bank | 170M+ marketing messages without a working unsubscribe; 34.8M without or after withdrawn consent | **A$7.5M** ([ACMA](https://www.acma.gov.au/articles/2024-10/commonwealth-bank-pays-75m-more-spam-breaches)) |
  | Mar 2026 | Lululemon Athletica Australia | 370,000+ emails without an unsubscribe; "service" emails that were really marketing | **A$702,900** plus a 2-year enforceable undertaking ([ACMA](https://www.acma.gov.au/articles/2026-03/lululemon-penalised-702k-spam-breaches)) |
  | Jul 2026 | Tabcorp (TAB) | 217,000+ emails and SMS to people who had unsubscribed, plus telemarketing breaches | **A$2.7M+** ([ACMA](https://www.acma.gov.au/articles/2026-07/tab-pays-27m-telemarketing-and-spam-breaches)) |
  | Nov 2019 | Oneflare | Messages to numbers from public directories; not relevant to the recipients' work; no unsubscribe | **A$75,600** ([ACMA](https://www.acma.gov.au/articles/2019-11/oneflare-pays-75600-infringement-notice-spamming)) |
  ACMA publishes quarterly results ([Jan–Mar 2026 report](https://www.acma.gov.au/publications/2026-08/report/action-scams-spam-and-telemarketing-january-march-2026)).
- **Realistic risk for us.** At 30 sends a day, the bigger risks are a **formal warning after a complaint** and damage to our reputation (we sell trust) rather than a large fine. **This is my judgment, not legal advice.** US recipients can complain to ACMA, and ACMA has jurisdiction because the messages come from Australia.

## 7. What changes in the cold email and LinkedIn plan

### Compliant approach, in order of preference
1. **Warm and express-consent first** (the lowest risk and the best conversion): referrals from partners (`partners.md`), interviewees, event conversations, people who comment on or reply to the founder's LinkedIn posts, and Readiness Check sign-ups with a marketing tick box. Also a Google Ads landing page with a clear opt-in form; the ads test itself is not a Spam Act issue.
2. **Cold email under conspicuous publication**, only to addresses that pass all 4 tests in §3 and have evidence per §5.
3. **Everything else goes to LinkedIn engagement** (commenting and non-commercial connection requests, §8) until the person opts in.

### Edits to make before 12 Oct (owner: growth-marketer and head-of-sales)
| File | Edit |
|---|---|
| `cold-email-launch-kit.md` Step 7 | Add the §5 evidence columns. `consent_basis` becomes one of the three values in §5, not a fixed phrase. Rule: no evidence, no send. |
| `cold-email-launch-kit.md` Step 6 | Apollo is a sender only and must never be a data source. Ban scraping tools and extensions. |
| `cold-email-launch-kit.md` Step 9 | Rename it "CAN-SPAM **and Spam Act** checklist". Add: consent evidence per address; ABN and entity name in the signature; the unsubscribe wording above; the 5-business-day maximum (our standard stays same day); no consent-request emails; no harvested lists. |
| `sequences.md` signature and opt-out | Use the §4 footer. The unsubscribe wording must say "won't email you again", not "won't follow up". |
| `playbook.md` §3.3 must-have 5 and §7 | "A business email **published by the firm or by the person, with no 'no marketing' statement, evidence saved**." Add the Spam Act line to §7. |
| `playbook.md` §5.1 | **Expect fewer emailable prospects.** Some directories and generic listings will fail the tests, so volume shifts to LinkedIn and partners. The ~500-prospect plan may need a higher LinkedIn share. That's a head-of-sales decision. |

### Timing
- The unsubscribe footer needs the **ABN**. Register the entity and ABN before 12 Oct (`launch-checklist.md` Stage 3). Otherwise send as a sole trader with the founder's own ABN, or delay cold sends.

## 8. LinkedIn direct messages

- **LinkedIn messages and InMail are very likely "electronic messages"** under the Spam Act. Law-firm commentary says the Act covers messages to instant-messaging and social-media accounts (S: [Holding Redlich](https://www.holdingredlich.com/the-importance-of-compliance-with-the-spam-act)). **FLAG:** I found no ACMA decision about LinkedIn specifically, so the lawyer should confirm.
- **Connection requests.** Keep the note **non-commercial**: no offer, no price and no link. For example: "I'm researching how small tax firms handle their security plan before PTIN renewal. I'd like to connect." A purely non-commercial note is probably outside s 16 (**FLAG**). Don't pitch in the note.
- **After they accept**, a commercial DM still needs consent. Accepting a connection is **not clearly** consent to marketing (**FLAG**). Safer patterns:
  - Ask a **non-commercial question** first (discovery), and move to the offer only if they ask what we do or show interest. That's express consent.
  - Or rely on conspicuous publication only if their profile publicly lists the relevant role and has no "no sales pitches" statement. **FLAG:** it's untested whether a LinkedIn profile counts as a "conspicuously published electronic address".
- **Every commercial DM** includes the sender's name, "ChimeraShield" and an opt-out: "If you'd rather I didn't message you about this, say so and I won't." Log opt-outs in the same suppression list.
- **LinkedIn's own rules:** its User Agreement prohibits spam and automation tools. **Don't use** LinkedIn automation tools (auto-connect, auto-DM). They risk a ban as well as Spam Act exposure.
- **Sequence B (event trigger) and comments on posts** are public engagement, not messages, so they are fine.

## 9. If we also target Australian accounting firms

The same Spam Act rules apply, so the §3 tests and §4 footer carry over, but there is **no CAN-SPAM** requirement. Also: the **Do Not Call Register** applies to phone and fax only, so it doesn't affect email; and **Privacy Act** duties may apply to how we handle prospect data (`australia-founder.md` §4). The market agent should factor in that the list-building rules are the same.

## Needs a lawyer

1. Confirm the conspicuous-publication reading for each list source (firm sites, NAEA, NATP, state CPA society directories), including whether directory terms count as a "statement".
2. Approve the footer and unsubscribe wording under both the Spam Act and CAN-SPAM, and confirm whether an Australian postal address satisfies CAN-SPAM.
3. Whether LinkedIn DMs and connection notes are commercial electronic messages, and what consent a DM after acceptance needs.
4. The penalty figures (s 25 tiers, penalty-unit value) and the evidence-retention period.
