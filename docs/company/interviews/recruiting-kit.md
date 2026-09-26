# Recruiting kit: 10 discovery interviews in 14 days

**Owner:** customer-discovery · **Prepared:** 2026-09-24 · **Status:** ready to use · **Interviews completed so far:** 0. No interview data exists yet, and nothing in this kit is customer evidence.

The first segment isn't chosen yet, so this kit covers the three leading candidates in parallel:

| # | Segment | Primary contact titles | Main verified trigger |
|---|---------|------------------------|------------------------|
| A | US accounting, CPA and tax-prep firms (2–50 staff) | Owner, Managing Partner, EA, Firm Administrator | FTC Safeguards Rule + PTIN renewal WISP attestation (Form W-12 line 11) |
| B | US dental and medical practices (5–50 staff) | Practice Owner (DDS/DMD/MD), Office Manager, Practice Administrator | HIPAA Security Rule risk analysis + OCR enforcement on small practices |
| C | US small law firms (1–30 lawyers) | Managing Partner, Solo Attorney, Firm Administrator, Office Manager | ABA Formal Opinions 477R, 483, 512 + tech-competence duty (Rule 1.1 cmt. 8) |

**Target split:** ~4 interviews in A, ~3 in B, ~3 in C. After 6 interviews, shift the remaining effort toward whichever segment scores highest on the 14-point rubric.

**Maths for 10 interviews:** Expect roughly 10–20% of warm/personal research requests to turn into a call, and less for cold ones (**Assumption**, not measured yet; track it in the funnel table below). So plan on **~80–100 personalized touches** across all channels, and lean on referrals ("who else should I talk to?") at the end of every call.

---

## 0. Rules for every channel (read once)

- **You are doing research, not selling.** No product pitch, no link, no pricing in the first touch. Mention the idea only at the very end of a call, if at all.
- **Consent:** ask before recording ("Is it okay if I record this so I can take fewer notes? It stays with me."). If they say no, take notes only.
- **No client or patient data.** If someone starts describing a specific client or patient, stop them politely. You only want their own process and experience.
- **No scanning** of anyone's domain, email or systems unless they authorize it in writing.
- **Email compliance (CAN-SPAM + Australian Spam Act 2003, since we send from Australia):** accurate sender and subject; `ChimeraShield Pty Ltd (ABN [ABN])`; a physical postal address (`[US_POSTAL_ADDRESS]`); a working unsubscribe, honoured within 5 business days. Only email addresses the firm or person published themselves, where the message relates to their role, and record the source URL as consent evidence. Never buy lists, scrape or guess addresses. See `docs/company/legal/spam-act-cold-email.md`.
- **Company email doesn't exist yet.** Use `[FOUNDER_NAME]@[DOMAIN]` in drafts. Don't send cold email until the domain has SPF, DKIM and DMARC set up. Until then, **LinkedIn, warm intros and communities are the main channels.** Once email is live, warm up at 5–10 emails/day in week 1.
- **Follow-up cadence:** touch 1 → +3 days short bump → +5 days helpful resource → +7 days "closing the loop". Stop on any reply or opt-out.
- **Log everything** in the funnel table (section 6) and write notes with `raw/_TEMPLATE.md` within an hour of each call.

---

## A. US accounting, CPA and tax-prep firms

### A1. Why now: verified buying triggers

| Trigger | What it says | Label | Source |
|---------|--------------|-------|--------|
| **FTC Safeguards Rule** (GLBA) | Tax-prep firms count as "financial institutions" and must have a written information security program: a named qualified individual, risk assessment, MFA, encryption, and so on. | Fact | [FTC: Safeguards Rule, what your business needs to know](https://www.ftc.gov/business-guidance/resources/ftc-safeguards-rule-what-your-business-needs-know) |
| **FTC breach notification** (in force since May 13, 2024) | Firms must notify the FTC within 30 days of discovering a breach of unencrypted data affecting 500+ consumers. The FTC plans a public database of these reports. | Fact | [FTC blog, May 2024](https://www.ftc.gov/business-guidance/blog/2024/05/safeguards-rule-notification-requirement-now-effect); [FTC press release, Oct 2023](https://www.ftc.gov/news-events/news/press-releases/2023/10/ftc-amends-safeguards-rule-require-non-banking-financial-institutions-report-data-security-breaches) |
| **PTIN renewal WISP attestation** | Form W-12 (Rev. Oct 2025), line 11: the preparer states they know they are "required by law to create and maintain a written information security plan". Every paid preparer sees this at every PTIN renewal. Renewal season normally opens in mid-October (**Assumption**: check irs.gov when it opens). | Fact | [IRS Form W-12](https://www.irs.gov/pub/irs-pdf/fw12.pdf); [W-12 instructions](https://www.irs.gov/pub/irs-pdf/iw12.pdf) |
| **IRS Pub 5708 / Pub 4557** | The IRS publishes a free WISP template (5708) and a data-safeguarding guide (4557). Many small firms have downloaded the template but never actually finished it (**Inference**: a good thing to ask about). | Fact (the publications exist) | [IRS Pub 4557](https://www.irs.gov/pub/irs-pdf/p4557.pdf) |
| **Filing season** | Tax preparers are overloaded from January to April 15. **Oct–Dec is the window** to interview them, and it overlaps with PTIN renewal. | Inference | - |

**What to say (calm, not fear):** "With PTIN renewal coming up and the W-12 question about having a written security plan, I'm curious how small firms actually handle that."

### A2. Where to find them

**LinkedIn (Sales Navigator free trial or normal search)**
- Titles: `Owner`, `Managing Partner`, `Partner`, `Enrolled Agent`, `EA`, `CPA`, `Firm Administrator`, `Practice Manager`, `Office Manager`, `Tax Manager`
- Filters: Industry = *Accounting*; Company headcount = *2–10* and *11–50*; Geography = United States (start with 2–3 states so you can say "firms in Ohio"); Posted on LinkedIn in the last 30 days (they're more likely to reply)
- Keyword searches: `"tax preparation" owner`, `"enrolled agent" owner`, `"CPA firm" "managing partner"`
- Groups/pages: [NAEA on LinkedIn](https://www.linkedin.com/company/national-association-of-enrolled-agents). Comment usefully on posts about WISP, PTIN and security before you send DMs.

**Associations and directories (verified to exist)**
| Name | Use | Link |
|------|-----|------|
| NAEA "Find a Tax Expert" | Public directory of Enrolled Agents, searchable by location. Most listings are solo or small firms. | [taxexperts.naea.org](https://taxexperts.naea.org/) · [naea.org](https://www.naea.org/) |
| NATP (National Association of Tax Professionals) | Largest small-preparer association, with events and a member community | [natptax.com](https://www.natptax.com/) |
| AICPA PCPS / Small Firms hub | The AICPA's section for small firms. Read its "top issues for small firms" content so you use their language. | [AICPA small firms](https://www.aicpa-cima.com/resources/landing/small-firms) · [top issues](https://www.aicpa-cima.com/professional-insights/article/what-are-the-top-issues-for-small-firms) |
| State CPA societies | Every state has one, and many publish public firm directories. Pick 2–3 states. | [List of state societies (Surgent)](https://www.surgent.com/resources/state-societies-list/) · e.g. [NJCPA](https://njcpa.org/) |
| Google Maps | Search "tax preparation" or "CPA" plus a city. Each firm's website usually lists the owner and a business email. | - |

**Events (verified dates, check registration)**
- NATP Tax Forums & Expo: **Philadelphia, Sep 30–Oct 1, 2026**; **Las Vegas, Oct 21–22, 2026**; a Minneapolis stop is also listed ([Philadelphia](https://www.natptax.com/events-education/catalog/2026-natp-tax-forums-and-expo-event-philadelphia-pa/) · [Las Vegas](https://www.natptax.com/events-education/catalog/2026-natp-tax-forums-and-expo-event-las-vegas-nv/) · [Minneapolis](https://www.natptax.com/events-education/catalog/2026-natp-tax-forums-and-expo-event-minneapolis-mn/)). If you can't attend, message people who post that they're going.
- Local state CPA society chapter meetings and CPE nights, listed on each society's calendar.

**Communities (Reddit rules could not be fetched automatically: open each sidebar and read the rules before posting)**
- r/taxpros (for professional preparers; the best fit), r/Accounting (large, mostly employees, not owners), r/smallbusiness
- Facebook groups for tax preparers and EAs: search "tax preparers", "enrolled agents" and join 2 active ones

**Partners (for referrals, not sales)**
- Small MSPs that serve accounting firms. Ask them: "Which of your clients worry most about the WISP?"
- Tax-software user groups and resellers (Drake, UltraTax, Lacerte, ProSeries, CrossLink). **Assumption**: the user communities exist, so verify each one.
- Cyber-insurance brokers who write small professional-services policies

### A3. Mom Test interview script (10 questions, 20 minutes)

Opening: *"Thanks for making time. I'm researching how small tax and accounting firms handle data security. I'm not selling anything today. Is it okay if I record this for my notes?"*

1. "Walk me through who handles IT and security at your firm today. Is it you, a staff member, or an outside company?"
2. "Tell me about the last time you had to deal with a security question. It could be a client asking, an insurer's form, or the W-12 question at PTIN renewal. What did you actually do?"
3. "Do you have a written information security plan today? Who wrote it, when was it last updated, and how long did that take?"
4. "What's the closest call you've had: a phishing email someone clicked, a fake client, an e-file or EFIN problem, a compromised mailbox? What happened next?"
5. "What did that cost you, in hours, money, or clients? How did you work that out?"
6. "What do you pay for today that touches security: antivirus, an MSP, backups, a portal, cyber insurance? Roughly how much a month?"
7. "Have you looked for something better in the last year? What did you try or look at, and why didn't you go with it?"
8. "When does security work actually happen in your year? Off-season, around renewal, or never?"
9. "Who else has a say when you spend money on IT: a partner, your MSP, your insurer?"
10. "Who's another firm owner I should talk to about this? Would you be willing to introduce me?"

*Only if you have time, at the end:* describe the idea in one sentence and ask "What would have to be true for you to try it?" Record commitments, not compliments.

### A4. Research-request outreach

**Email** (first touch: plain text, no links)
> **Subject:** question about [FIRM]'s wisp
>
> Hi [FIRST_NAME],
>
> I saw [FIRM] on the NAEA directory and noticed you run a [N]-person practice in [CITY]. With PTIN renewal asking every preparer about their written security plan, I'm trying to learn how small firms actually handle it, and where it's a headache.
>
> I'm doing research, not selling. Would you share 15 minutes next week? I'll send you a summary of what I learn from other firms.
>
> [FOUNDER_NAME], Founder, ChimeraShield
> ChimeraShield Pty Ltd (ABN [ABN]) · [FOUNDER_NAME]@[DOMAIN] · [US_POSTAL_ADDRESS]
>
> If this isn't relevant, just reply "no" and I won't follow up.

**LinkedIn** (connection note, under 300 characters)
> Hi [FIRST_NAME], I'm researching how small tax firms handle their WISP and data security, especially around PTIN renewal. No pitch. Would you be open to a 15-min chat? Happy to share what I learn from other firms. [FOUNDER_NAME]

**LinkedIn follow-up after they accept**
> Thanks for connecting, [FIRST_NAME]. My question is simple: when you last updated your WISP (or decided not to), what did that actually involve? 15 minutes any day next week works for me, and I'll share the anonymized findings. If it's not a fit, no worries at all.

### A5. Value-first Reddit post (r/taxpros)
Check the sidebar first. If the rules ban surveys or research requests, post only the value part and don't ask for calls. Answer comments for 48 hours. DM only people who say they're interested.

> **Title:** What I learned reading the W-12 WISP question, Pub 5708 and the FTC breach-notice rule side by side
>
> Body: A plain-English summary of (1) what line 11 on the W-12 actually asks, (2) what the FTC Safeguards Rule requires of a small firm, with links to the FTC and IRS pages, (3) the 30-day FTC notification for breaches of 500+ consumers, and (4) a short, vendor-neutral checklist of the parts of Pub 5708 that small firms tend to skip, framed as questions. End with: *"For those of you who've written a WISP: what part took the longest? I'm trying to understand where the real friction is."* No product name, no link to our site, and say openly that you're researching the topic if anyone asks.

---

## B. US dental and medical practices

### B1. Why now: verified buying triggers

| Trigger | What it says | Label | Source |
|---------|--------------|-------|--------|
| **HIPAA Security Rule risk analysis** | Every covered practice must do a documented risk analysis of its electronic patient data (ePHI) | Fact | [HHS: The Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html) |
| **OCR Risk Analysis Initiative** | Launched Oct 2024. Enforcement has continued through 2025–2026, and reported actions include small and dental practices; ransomware settlements continue. | Fact (the initiative and settlements) | [HHS: OCR settles four ransomware investigations](https://www.hhs.gov/press-room/ocr-settles-four-ransomware-investigations.html) · [Wilson Elser on the initiative](https://www.wilsonelser.com/publications/hhs-ocr-risk-analysis-enforcement-initiative-continues-under-new-administration) · [NYSDA on OCR ransomware action](https://www.nycdentalsociety.org/news-publications/nysda-publications/2025/01/08/ocr-takes-hipaa-action-against-company-for-allowing-ransomware-attack) |
| **Proposed Security Rule update** | The NPRM (Dec 27, 2024) would make every specification required, including MFA and encryption, with written, tested policies. The final rule is now expected **no earlier than July 2027**, and provider groups have asked HHS to withdraw it. | Fact (the NPRM); timing is **uncertain** | [HHS NPRM fact sheet](https://www.hhs.gov/hipaa/for-professionals/security/hipaa-security-rule-nprm/factsheet/index.html) · [Clark Hill: delayed to 2027](https://www.clarkhill.com/news-events/news/hipaa-security-rule-update-delayed-until-2027/) · [HIPAA Journal](https://www.hipaajournal.com/hipaa-security-rule-update-postponed/) |
| **HHS breach portal** | Public list of breaches affecting 500+ people. Use it to find local peer breaches that you can mention factually, never to shame anyone. | Fact | [HHS OCR breach portal](https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf) |

**What to say:** "OCR has been focusing on whether small practices have a current risk analysis. I'm trying to learn how practices your size handle that in real life." Don't claim the proposed rule is final.

### B2. Where to find them

**LinkedIn**
- Titles: `Office Manager` (dental), `Practice Manager`, `Practice Administrator`, `Dental Office Manager`, `Practice Owner`, `DDS`, `DMD`, `Owner Dentist`, `Medical Practice Manager`, `Compliance Officer` (small practice)
- Filters: Industry = *Medical Practices* / *Hospitals and Health Care*; headcount *2–10*, *11–50*; US; keyword `dental` or a specialty (`pediatric`, `orthodontics`, `dermatology`, `physical therapy`)
- Tip: **office managers are the fastest to reply and know the details.** Owners decide on spending. Interview both where you can.

**Associations and directories (verified)**
| Name | Use | Link |
|------|-----|------|
| AADOM (American Association of Dental Office Management) | The association for dental office managers, with regional meetings | [dentalmanagers.com](https://www.dentalmanagers.com/) · [regional meetings](https://www.dentalmanagers.com/about/events/regional-meetings/) |
| ADA Find-a-Dentist | Public directory of member dentists, browsable by state | [findadentist.ada.org](https://findadentist.ada.org/) · [by state](https://findadentist.ada.org/dentists-by-state) |
| MGMA (Medical Group Management Association) | Medical practice administrators, with state affiliate chapters and a state events calendar | [MGMA state events](https://www.mgma.com/state-events-calendar) · [annual conference](https://www.mgma.com/annual-conference) |
| Dentaltown / Hygienetown | Large dental professional forum with practice-management boards | [dentaltown.com](https://www.dentaltown.com/) |
| State dental societies | Example: [NYSDA / NY County Dental Society](https://www.nycdentalsociety.org/) | - |

**Events**
- AADOM Annual Conference 2026 (Orlando, Sep 3–5) **has already happened**. Use the AADOM **regional meetings** instead, and message people who posted about attending the annual conference.
- MGMA Annual Conference: listed for **Sep 27–30, 2026, San Antonio** ([source](https://withorbital.com/conferences/mgma-leaders-conference-2026), check on mgma.com). It's too soon to attend, so message people who post about it.
- MGMA state-affiliate meetings: pick your state from the [calendar](https://www.mgma.com/state-events-calendar).

**Communities (read the sidebar rules first; not auto-verified)**
- r/Dentistry, r/dentalhygiene, r/medicalpractice, r/MedicalBilling (billers know the workflows), Dentaltown forums, and Facebook groups for dental office managers

**Partners**
- Dental and medical IT MSPs (many specialize in one vertical)
- Practice-management software communities: Dentrix / Henry Schein One, Open Dental, Eaglesoft user groups. Henry Schein One lists its [authorized integration partners](https://www.henryscheinone.com/dental-solutions/api-exchange/vendors-list/).
- Dental CPAs and consultants, and malpractice / cyber-insurance brokers

### B3. Mom Test interview script (10 questions)

Opening: *"I'm researching how small practices handle IT security and HIPAA day to day. I'm not selling anything. Please don't share any patient details. Is it okay if I record?"*

1. "Who takes care of IT and security for the practice today? Walk me through a normal month."
2. "When was your last HIPAA security risk analysis? Who did it, how long did it take, and what happened with the findings?"
3. "Tell me about the last suspicious email, fake invoice, or strange login someone on the team ran into. What happened?"
4. "Has the practice, or a practice you know, ever had systems go down from ransomware or a vendor outage? How long were you down, and what did it cost?"
5. "What do you pay for today: an IT company, backups, email security, a compliance service, cyber insurance? Roughly how much per month?"
6. "When you last renewed cyber or malpractice insurance, what security questions did they ask? How did you answer them?"
7. "Have you tried any HIPAA or security tools or services that you stopped using? Why did you stop?"
8. "Who approves spending on IT: the owner, the office manager, or a DSO or group?"
9. "What part of this takes the most staff time today?"
10. "Who else, maybe an office manager at another practice, should I talk to?"

### B4. Research-request outreach

**Email**
> **Subject:** security at small dental practices
>
> Hi [FIRST_NAME],
>
> I saw you manage [PRACTICE] in [CITY]. OCR has been checking whether small practices keep a current HIPAA risk analysis, and I'm trying to learn how office managers actually handle that alongside everything else.
>
> This is research, not a sales call. Could I borrow 15 minutes next week? I'll share an anonymized summary of what other practices told me.
>
> [FOUNDER_NAME], Founder, ChimeraShield
> ChimeraShield Pty Ltd (ABN [ABN]) · [FOUNDER_NAME]@[DOMAIN] · [US_POSTAL_ADDRESS]
>
> If this isn't relevant, just reply "no" and I won't follow up.

**LinkedIn** (connection note)
> Hi [FIRST_NAME], I'm researching how small dental/medical practices handle HIPAA risk analysis and day-to-day IT security. No pitch, just 15 minutes of learning. Happy to share what other practices tell me. [FOUNDER_NAME]

**LinkedIn follow-up**
> Thanks for connecting. My question: the last time the practice did a HIPAA risk analysis (or put it off), who did it and what did it involve? A 15-min chat next week would help a lot. If not, no problem at all.

### B5. Value-first Reddit post (r/Dentistry or r/medicalpractice)
> **Title:** Plain-English summary: what OCR's recent small-practice HIPAA settlements have in common
>
> Body: A neutral summary built from HHS press releases, linked: OCR's Risk Analysis Initiative, the common finding of "no current risk analysis", and where the proposed Security Rule update stands (still proposed, final action expected no earlier than July 2027). Add a short list of free official resources (the HHS/ONC Security Risk Assessment tool, HHS Security Rule guidance). End with: *"Office managers: how do you actually get the risk analysis done each year? In-house, your IT company, or a consultant?"* No product mention and no DM requests in the post.

---

## C. US small law firms

### C1. Why now: verified buying triggers

| Trigger | What it says | Label | Source |
|---------|--------------|-------|--------|
| **ABA Formal Opinion 477R** (2017) | Lawyers must use reasonable efforts to secure client communications, scaled to how sensitive they are | Fact | [LegalClarity summary](https://legalclarity.org/aba-formal-opinion-477r-lawyer-cybersecurity-duties/) |
| **ABA Formal Opinion 483** (2018) | After a data breach, lawyers must act promptly to stop it, notify affected clients, and should have an incident response plan | Fact | [ABA Formal Op. 483 (PDF)](https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/ethics-opinions/aba-formal-op-483.pdf) · [ABA Journal](https://www.abajournal.com/news/article/aba_ethics_opinion_offers_guidance_on_data_breaches) |
| **ABA Formal Opinion 512** (Jul 29, 2024) | Generative AI use triggers Rule 1.6 confidentiality duties, so lawyers must assess the risk before putting client data into AI tools | Fact | [ABA Business Law Today](https://www.americanbar.org/groups/business_law/resources/business-law-today/2024-october/aba-ethics-opinion-generative-ai-offers-useful-framework/) |
| **Tech-competence duty** (Model Rule 1.1, Comment 8) | Adopted by 40 states plus DC and Puerto Rico | Fact | [LawSites tech-competence tracker](https://www.lawnext.com/tech-competence) |
| **Client security questionnaires** | Corporate and insurance clients increasingly send outside-counsel security questionnaires | **Assumption**: ask about it in interviews | - |

**What to say:** "Between Opinion 483's incident-response expectations and Opinion 512 on AI tools, I'm curious how small firms decide what's 'reasonable' security."

### C2. Where to find them

**LinkedIn**
- Titles: `Managing Partner`, `Founding Attorney`, `Owner`, `Principal`, `Solo Practitioner`, `Attorney at Law` (with a small firm), `Firm Administrator`, `Legal Administrator`, `Office Manager`
- Filters: Industry = *Law Practice* / *Legal Services*; headcount *1–10*, *11–50*; US. Practice-area keywords where client data is sensitive: `estate planning`, `family law`, `immigration`, `personal injury`, `real estate closing` (wire-fraud exposure)
- Real-estate closing and estate firms handle wires and personal financial data, so expect sharper pain (**Inference**)

**Associations and directories (verified)**
| Name | Use | Link |
|------|-----|------|
| State bar member directories | Public attorney lookup for every state, with an ABA index of bar directories | [ABA: bar directories and lawyer finders](https://www.americanbar.org/groups/legal_services/flh-home/flh-bar-directories-and-lawyer-finders/) · e.g. [Arizona](https://www.azbar.org/for-legal-professionals/practice-tools-management/member-directory/) |
| State bar **practice management advisors (PMAs)** | Many state bars employ a PMA who advises small firms on technology. They're great partners and connectors. The ABA Law Practice Division has a committee for PMAs. | [ABA LPM overview](https://www.americanbar.org/groups/bar-leadership/resources/bar-leader-magazine/2006-2007/3106/lpm/) |
| ABA Law Practice Division | Small-firm practice management content and community | [americanbar.org](https://www.americanbar.org/) |
| Attorney at Work | Small-firm practice publication, useful for learning their language | [attorneyatwork.com](https://www.attorneyatwork.com/law-firm-reddit-marketing-dos-and-donts/) |

**Events (verified)**
- **ClioCon 2026, Oct 26–27, Boston**: the biggest small-firm legal-tech gathering ([clio.com/events/cliocon](https://www.clio.com/events/cliocon/))
- **ABA TECHSHOW 2027, Mar 3–6, Chicago** ([techshow.com](https://www.techshow.com/)): outside the 14-day window, but good for later sales
- Local and county bar association CLE lunches. A CLE on ethics and cybersecurity is a natural fit, and PMAs often organize them.

**Communities (read the sidebar rules first; not auto-verified)**
- r/LawFirm (law-firm owners and practice management; the best fit), r/Lawyertalk (lawyers only, and strict about non-lawyers, so read the rules and consider lurking only), r/smallbusiness
- Clio community, and Facebook groups for solo and small-firm lawyers ("Lawyers Helping Lawyers" type groups, verify each one)

**Partners**
- Legal-focused MSPs, state bar PMAs, Clio / MyCase / PracticePanther consultants, legal malpractice insurers and brokers (many offer risk-management content)

### C3. Mom Test interview script (10 questions)

Opening: *"I'm researching how small firms handle cybersecurity and client confidentiality in practice. Not selling. Please don't share anything privileged or client-identifying. Okay to record?"*

1. "Who handles IT and security at the firm today? Walk me through what's actually in place."
2. "Tell me about the last time a client, a court, or your malpractice carrier asked about your security. What did they ask, and how did you answer?"
3. "What's the closest call you've had: a spoofed wire instruction, a phishing email, a compromised mailbox, a lost laptop? What happened next?"
4. "If something happened tomorrow, what's your plan? Is anything written down?"
5. "How is the firm using AI tools today, if at all? How did you decide what client information is okay to put in them?"
6. "What do you spend on IT and security today: an MSP, Microsoft 365 add-ons, backups, cyber coverage? Roughly how much a month?"
7. "Have you tried or priced any security service and passed on it? Why?"
8. "What would a breach cost you: notifying clients, lost clients, the insurance deductible? Have you ever worked it out?"
9. "Who decides on IT spending: you alone, the partners, the office manager?"
10. "Which other small-firm lawyer or administrator should I talk to next?"

### C4. Research-request outreach

**Email**
> **Subject:** security at small law firms
>
> Hi [FIRST_NAME],
>
> I saw [FIRM] handles [PRACTICE_AREA] in [CITY]. Between ABA Opinion 483 on breach response and Opinion 512 on AI tools, I'm trying to learn what "reasonable security" looks like day to day at firms your size.
>
> This is research, not a pitch. Would you have 15 minutes next week? I'll share an anonymized summary of what other firms say.
>
> [FOUNDER_NAME], Founder, ChimeraShield
> ChimeraShield Pty Ltd (ABN [ABN]) · [FOUNDER_NAME]@[DOMAIN] · [US_POSTAL_ADDRESS]
>
> If this isn't relevant, just reply "no" and I won't follow up.

**LinkedIn** (connection note)
> Hi [FIRST_NAME], I'm researching how small law firms handle cybersecurity and AI-tool confidentiality (ABA Ops 483/512). No pitch, just 15 minutes to learn how it works in practice. Happy to share findings. [FOUNDER_NAME]

**LinkedIn follow-up**
> Thanks for connecting. One question I'm exploring: has a client or your carrier ever asked about the firm's security, and what did answering involve? A 15-min chat next week would be a huge help. If not, totally fine.

### C5. Value-first Reddit post (r/LawFirm)
> **Title:** A one-page, plain-English map of the ABA opinions on cybersecurity and AI (477R, 483, 512) for small firms
>
> Body: One paragraph per opinion (what it says, with a link to the primary source), plus the note that 40 states have adopted the tech-competence comment. Add a neutral "questions to ask your IT provider" list. End with: *"For small-firm owners: has a client or carrier ever asked you to prove your security? How did you handle it?"* Say clearly that this isn't legal advice. No product mention.

---

## 5. Partners who can introduce you to many people at once
One friendly partner can be worth 20 cold messages. In week 1, contact **2 MSPs, 1 cyber-insurance broker, and 1 state bar PMA**:
> "Hi [FIRST_NAME], I'm researching how small [CPA firms / practices / law firms] handle security. I'm not selling to your clients. Would you share what you see most often, and would you be open to introducing me to 1–2 clients who'd talk for 15 minutes? I'll share the findings with you." Sign with `[FOUNDER_NAME]@[DOMAIN]`, include the ABN, `[US_POSTAL_ADDRESS]` and the unsubscribe line if you send it by email.

## 6. Funnel tracker (copy into a sheet)

| Date | Segment | Channel | Name / firm | Touch # | Replied? | Booked? | Interview date | Score /14 | Referral given? |
|------|---------|---------|-------------|---------|----------|---------|----------------|-----------|-----------------|

Weekly targets: **Week 1:** 60 touches, 8 booked, 3–4 done. **Week 2:** 40 more touches plus referrals, 10 done in total.

## 7. The 14-day plan

| Day | Actions |
|-----|---------|
| 1 | Set up LinkedIn (headline: "Founder, researching small-business cybersecurity"). Build 3 lists of 30 names each (NAEA directory, ADA/AADOM + LinkedIn, state bar + LinkedIn). Message 10 people you already know: "Who do you know who runs a small CPA, dental or law practice?" |
| 2 | Send 15 LinkedIn connection notes (5 per segment). Join r/taxpros, r/LawFirm, r/Dentistry and read the rules. Leave 3 helpful comments. Contact 2 MSPs and 1 insurance broker. |
| 3 | Send 15 more LinkedIn notes. Follow up with everyone who accepted. Draft the r/taxpros post. Register the domain and set up SPF/DKIM/DMARC (with the tech-lead) if it isn't done yet. |
| 4 | Publish the r/taxpros value post (fits the PTIN timing). Send 15 LinkedIn notes. Book calls with anyone who replied. Do calls if any are booked. |
| 5 | Send 3-day bumps. Contact 1 state bar PMA and 1 AADOM/MGMA state chapter contact. Hold calls. Write notes with `_TEMPLATE.md` and score each one within an hour. |
| 6 | Publish the r/LawFirm post. Send 15 LinkedIn notes, favoring the segment that is replying most. Ask every interviewee for 1–2 referrals. |
| 7 | Review: touches, reply rate, booked, done, average score by segment. Adjust the split. Publish the r/Dentistry post if its rules allow. Plan week 2 around the best-performing channel and segment. |
| 8–13 | 10–15 touches a day, including referrals. Send the 5-day resource follow-up (share your plain-English regulation summary). Do 1–2 interviews a day. Once email is warmed up, add 5–10 cold emails a day. |
| 14 | 10 interviews done. Hand the notes to customer-discovery for synthesis (`docs/company/interviews/synthesis.md`). |

## 8. What would count as validation
Commitments count, compliments don't: a second call, a referral, written authorization for a free domain/email check, or asking about founding-member pricing. A segment that averages **8+ on the rubric** and produces **2+ commitments from 3 interviews** is a strong candidate for the first market.

## Sources
- FTC: [Safeguards Rule guide](https://www.ftc.gov/business-guidance/resources/ftc-safeguards-rule-what-your-business-needs-know) · [Notification requirement in effect (2024)](https://www.ftc.gov/business-guidance/blog/2024/05/safeguards-rule-notification-requirement-now-effect) · [Amendment press release (2023)](https://www.ftc.gov/news-events/news/press-releases/2023/10/ftc-amends-safeguards-rule-require-non-banking-financial-institutions-report-data-security-breaches)
- IRS: [Form W-12](https://www.irs.gov/pub/irs-pdf/fw12.pdf) · [W-12 instructions](https://www.irs.gov/pub/irs-pdf/iw12.pdf) · [Pub 4557](https://www.irs.gov/pub/irs-pdf/p4557.pdf)
- HHS: [Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html) · [NPRM fact sheet](https://www.hhs.gov/hipaa/for-professionals/security/hipaa-security-rule-nprm/factsheet/index.html) · [Four ransomware settlements](https://www.hhs.gov/press-room/ocr-settles-four-ransomware-investigations.html) · [Breach portal](https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf) · [Clark Hill: rule delayed to 2027](https://www.clarkhill.com/news-events/news/hipaa-security-rule-update-delayed-until-2027/) · [HIPAA Journal](https://www.hipaajournal.com/hipaa-security-rule-update-postponed/) · [Wilson Elser](https://www.wilsonelser.com/publications/hhs-ocr-risk-analysis-enforcement-initiative-continues-under-new-administration)
- ABA: [Formal Op. 483](https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/ethics-opinions/aba-formal-op-483.pdf) · [Op. 512 overview](https://www.americanbar.org/groups/business_law/resources/business-law-today/2024-october/aba-ethics-opinion-generative-ai-offers-useful-framework/) · [477R summary](https://legalclarity.org/aba-formal-opinion-477r-lawyer-cybersecurity-duties/) · [Bar directories](https://www.americanbar.org/groups/legal_services/flh-home/flh-bar-directories-and-lawyer-finders/) · [LawSites tech competence](https://www.lawnext.com/tech-competence)
- Associations and events: [NAEA directory](https://taxexperts.naea.org/) · [NATP events](https://www.natptax.com/events-education/catalog/2026-natp-tax-forums-and-expo-event-philadelphia-pa/) · [AICPA small firms](https://www.aicpa-cima.com/resources/landing/small-firms) · [State CPA societies list](https://www.surgent.com/resources/state-societies-list/) · [AADOM](https://www.dentalmanagers.com/) · [ADA Find-a-Dentist](https://findadentist.ada.org/) · [MGMA state events](https://www.mgma.com/state-events-calendar) · [Dentaltown](https://www.dentaltown.com/) · [ClioCon](https://www.clio.com/events/cliocon/) · [ABA TECHSHOW](https://www.techshow.com/)
- **Not verified:** subreddit existence and rules. Reddit blocked automated access, so open each sidebar before posting. Tax-software user-group names are also unverified.
