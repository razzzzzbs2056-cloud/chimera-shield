# Mock Investor Q&A: the 12 Hardest Questions

**Owner:** fundraising-advisor · **Date:** 2026-09-24 · **Status:** practice doc. Rehearse out loud; update answers after every real conversation.

**How to use this.** Each question has: the **honest answer** (what to say today, pre-traction), the **evidence we have**, the **evidence gap**, and **what closes it**. Answers are short on purpose: 30–60 seconds spoken. If an answer relies on something we don't have yet, say so. An investor who catches one inflated claim discounts everything else.

Sources are the company docs cited in brackets. "3P" = third-party figure, not verified on the vendor's page.

---

### Q1. "Why won't Guardz or Microsoft just do this?"

**Honest answer:** "They could, and I watch for it every quarter. Today their business model points the other way. Guardz calls itself a platform 'purpose-built for MSPs', and it doesn't publish prices so it won't undercut how MSPs value their services. Huntress and Coro are moving deeper into the MSP channel too. Microsoft sells Business Premium at $22 per user, and its Security Copilot agents sit in E5, not the small-business tier. None of them produces an owner-signed WISP with evidence labels, because their buyer is an IT operator, not a tax-firm owner. Our bet is that owner-direct compliance evidence for one regulated niche at a time is too small and too content-heavy for them to prioritise. If Microsoft shipped an owner-facing 'Safeguards evidence' report inside Business Premium tomorrow, our Watch product would be in trouble. The pack, and the relationship around the W-12 deadline, less so."

- **Evidence we have:** channel and pricing research on 8+ vendors (`competitors/smb-landscape-2026.md`); Microsoft's SMB pricing page fetched directly.
- **Evidence gap:** no customer has told us why they'd pick us over their existing Microsoft setup or an MSP. Guardz's roadmap is unknown.
- **What closes it:** in interviews and sales calls, log how many prospects already pay for Business Premium or an MSP, and why the buyers chose us anyway. Target: 3+ buyers who already had Business Premium.

---

### Q2. "Isn't a WISP a $29 template? The IRS one is free."

**Honest answer:** "The document is cheap. Filling it in honestly isn't. A template doesn't know your systems, your vendors, or whether MFA is actually on. Our pack is a 60-minute call, and out come a plan that names the firm's real systems, a one-page report where every control is marked Verified, Owner-stated or Gap, and the five fixes to do first. We're pricing against the owner's time and the $500-setup, per-user MSP alternative, not against the PDF. But this is our number-one risk, and I don't have proof yet. We've set a kill rule: if three of the first six accounting owners value a WISP under $100, we turn the pack into a $79–$149 self-serve product."

- **Evidence we have:** the anchor range ($0 IRS Pub 5708, $29–$999 templates, $129/user/mo + $500 setup managed IT), all from vendor pages via search (`finance/pricing.md` §2a). Kill rule written into the PRD.
- **Evidence gap:** **zero** willingness-to-pay data. We don't know what owners paid, or how many hours they spent, last year.
- **What closes it:** interview question 1 ("what WISP did you have at your last PTIN renewal, who wrote it, what did it cost?") across 6+ accounting owners; then packs sold at $795 list, not just $495 founding.

---

### Q3. "What happens January to April? And in May?"

**Honest answer:** "We stop selling to accounting firms, deliberately. They're in filing season and won't take a call. We plan for it three ways. First, we push annual Watch prepay in November and December, so Q4 buyers are paid through tax season. Second, Watch is designed to be most useful in February: the 'Is this safe?' helpdesk is for exactly the IRS-themed phishing that peaks then. Third, dental starts in January as a non-seasonal second segment, and I use the quiet months to turn the first packs into product. May is the real test: the model assumes a churn spike on monthly subscribers when the season ends. I'll report May churn to you whether it's good or bad."

- **Evidence we have:** a seasonality index and May churn spike built into the model; base-case net cash dips from $8.0k (Nov 2027) to $3.5k (Feb 2028) but stays positive (`finance/model-summary.md` §2). Feb 2026 IRS-themed phishing wave (secondary source).
- **Evidence gap:** no data on annual-prepay uptake, helpdesk usage or post-season churn. Dental is unvalidated and needs a no-PHI design and legal review.
- **What closes it:** Q4 annual-prepay share (target ≥50% of Watch sales in Nov–Dec), helpdesk usage per firm in Feb–Mar 2027, actual May 2027 churn, and 3 paying dental practices.

---

### Q4. "You have zero customer interviews. Why should I believe anyone will pay?"

**Honest answer:** "You shouldn't yet, and I'm not asking you to invest yet. What I have is a verified external trigger (the W-12 attestation and the Safeguards Rule), a buyer who decides alone, and a dated window. What I don't have is a single owner telling me they'll pay. The plan is 10 interviews before the mid-October launch and at least three paid packs by 15 December. I've written down what I'll do if that fails. Can I send you the result in December?"

- **Evidence we have:** regulatory facts (FTC, IRS W-12); segment scoring 44/50 (`market/first-market-selection.md`); interview script and recruiting kit ready.
- **Evidence gap:** everything demand-side. `interviews/synthesis.md` doesn't exist; `sales/pipeline.csv` is empty.
- **What closes it:** the slide 9B table in `pitch-outline.md`, filled in on 15 Dec 2026.

---

### Q5. "Isn't this a consulting business with a subscription stapled on?"

**Honest answer:** "Right now, yes: in the base case packs are about 75% of year-one cash, and each one takes me 6–10 hours by hand. That's on purpose; I'm doing the first 10 manually to learn what to automate. The test is whether delivery time falls. My rule is that if a pack still takes more than six hours after the third one, the price or scope is wrong. The path to software is: the readiness check becomes the intake, passive checks fill the Evidence Report automatically, and the WISP draft comes from structured intake answers. If I can't get a pack under about two hours with software doing the rest, this stays a good services business, not a venture."

- **Evidence we have:** time model per pack (9.5 h → 6 h → 4.5 h, assumption) and effective hourly rates (`finance/pricing.md` §3); PRD acceptance criterion AC14 (≤4 h after pack 3).
- **Evidence gap:** no pack delivered, so no real hours.
- **What closes it:** logged hours for packs 1–5, and the share of WISP text reused unchanged across firms.

---

### Q6. "The market's small. How is this venture-scale?"

**Honest answer:** "Accounting alone isn't. About 15,000 reachable firms at $49–$149 a month is a $9–27 million serviceable market by our own assumptions, and three years of good execution gets maybe $180–$355k ARR. The venture case needs three things to be true: the same evidence engine carries to dental, law and small medical, each of which has its own rule and trigger; an MSP or insurer channel sells it at scale; and self-serve works so each sale doesn't need me. Dental alone roughly triples the serviceable market. None of that is proven. If it doesn't prove out, this is a profitable small company and I won't raise venture money for it."

- **Evidence we have:** bottom-up sizing for accounting and dental (`market/first-market-selection.md` §3); dental carryover analysis (`product/catalog.md` §5).
- **Evidence gap:** size-band shares and reach are assumptions; no primary Census tables were pulled. No second-vertical sales. No channel partner.
- **What closes it:** verify the top 10 counts against Census CBP; 3 paying dental practices; 2+ MSP or insurance-broker partners who've referred paying customers.

---

### Q7. "The FTC doesn't go after small tax shops. Why would they pay?"

**Honest answer:** "You may be right that enforcement against small firms is rare; our own research found no named cases, and I won't sell on fear of fines. The reasons we expect people to pay are more practical: they sign the W-12 every year and would rather do it honestly, cyber insurers increasingly ask for proof of MFA and a plan at renewal, larger clients send security questionnaires, and after an incident, having a plan makes the first 30 days less chaotic. Whether those reasons are strong enough to pay $495–$795 is exactly what the first interviews test."

- **Evidence we have:** regulatory facts; insurer MFA expectations (secondary sources, some flagged unverified) (`finance/pricing.md` §2b); the honest "value" read that the pack doesn't pay for itself on penalty avoidance alone.
- **Evidence gap:** how many owners have actually been asked by an insurer or client for proof.
- **What closes it:** interview question 2 ("has your insurer or a client asked for proof of MFA or a security plan?"). If fewer than a third say yes, the insurance angle is weak.

---

### Q8. "Most 10–50 person firms already have an MSP. Aren't you competing with your own channel?"

**Honest answer:** "For firms whose MSP already maintains a current, specific WISP, we're not the right fit, and we say so and ask for an intro instead. Our target is firms with no MSP, or an MSP that handles devices but not the written plan and the evidence. We don't do hands-on IT, so the Fix-First plan often creates work for their IT provider rather than taking it. I don't yet know what share of the market has no MSP; it's one of the first things we're measuring. If most prospects have one, we'll pivot to selling through MSPs with a partner tier."

- **Evidence we have:** landscape research shows nearly all funded vendors sell through MSPs (`competitors/smb-landscape-2026.md` §3); objection handling written (`sales/objections.md` #2).
- **Evidence gap:** share of ICP firms with an MSP is **unvalidated**. No MSP conversations yet.
- **What closes it:** `has_msp` field in `sales/pipeline.csv` filled for every qualified lead; 3 MSP conversations before designing a partner tier.

---

### Q9. "A customer gets breached and waves your Evidence Report at the FTC or a court. Now what?"

**Honest answer:** "That's the scenario we've designed around. The report never says 'compliant' or 'passes'; there's a test that searches for those words. Every control is marked Verified only if we have a stored artifact, otherwise Owner-stated or Gap. The engagement letter says it's not legal advice, the owner is the Qualified Individual, and our liability is limited. And we carry Tech E&O plus cyber insurance before the first paid pack. We can't eliminate the risk, but we can make it honest and insured."

- **Evidence we have:** PRD acceptance criteria AC7, AC9, AC10; scanning scope limited to passive checks with written consent (`product/prd-wisp-evidence-pack.md`); insurance in the launch checklist (`legal/launch-checklist.md` Stage 7).
- **Evidence gap:** no lawyer-reviewed engagement letter yet ($0 in the minimum budget); no insurance quote; §314.6 exemption wording not yet checked against the primary text.
- **What closes it:** lawyer review of the engagement letter and disclaimer; 2–3 real E&O quotes; legal-ops verification of 16 CFR 314.6 before the first sale.

---

### Q10. "Why you? And why solo?"

**Honest answer:** "`[TODO: the founder must write this. What in your background makes you credible to a tax-firm owner and to a security buyer? Link to evidence.]` On solo: I'm solo because the first job is 30 sales conversations, which one person can do. The first hire I'd make is `[TODO: e.g. a part-time compliance writer to templatize packs, or a dental-vertical seller]`. I'm also looking for one advisor who has run or sold to accounting firms."

- **Evidence we have:** a detailed, internally consistent plan across market, product, finance and legal. That shows thinking, not execution.
- **Evidence gap:** founder background isn't documented anywhere in the company docs. No advisors. No execution track record yet.
- **What closes it:** the founder slide with verifiable links; one accounting-world advisor; 3+ months of on-time monthly updates (`update-template.md`).

---

### Q11. "Where is the company, and can we actually invest in it?"

**Honest answer (fill in once known):** "`[If US:]` It will be a `[home-state LLC now, converting to a Delaware C-corp before any priced round / Delaware C-corp via Stripe Atlas]`. `[If Nepal:]` I'm based in Nepal. Under Nepal's outward-investment law, I may need government approval to own shares in a US company, so I'm getting a written legal opinion before I form a US entity or accept a SAFE. There is a route for Nepali IT companies to invest abroad with central bank approval, which could give us a Nepal parent with a US subsidiary that contracts with customers. I won't take your money until the structure is clean."

- **Evidence we have:** entity options, the Nepal outward-investment flag, banking and Stripe constraints (`legal/entity-options.md`).
- **Evidence gap:** founder country unknown; no entity; no lawyer opinion; bank and Stripe eligibility unconfirmed.
- **What closes it:** founder answers `launch-checklist.md` step 0.1; Nepali FX/corporate lawyer's written opinion (if applicable); entity formed with a working bank account and payment processor.

---

### Q12. "LLM drafting is cheap for everyone. What's your moat once this works?"

**Honest answer:** "Not the AI. Our advantages, if we earn them, are: first, owning the annual moment, meaning each firm renews its WISP with us every October before the PTIN renewal, which makes us a habit, not a purchase; second, the evidence history, since every month of Watch adds to a record of what was verified and when, which is annoying to recreate elsewhere; third, distribution through partners who already serve these firms, like insurance brokers and bookkeepers; and fourth, vertical content, one regulated niche at a time, done properly. All four are hypotheses today. Honestly, in year one the moat is speed and focus, which isn't a moat."

- **Evidence we have:** the upgrade path (readiness check → pack → Watch → annual refresh) (`product/catalog.md` §5); partner channel assumptions (`finance/model-summary.md` §3).
- **Evidence gap:** no renewals (the first possible renewal is Oct 2027); no partners; no switching-cost data.
- **What closes it:** Oct 2027 renewal rate of 2026 pack buyers; 2+ partners who've referred paying customers; Watch 12-month retention.

---

## Questions we should expect next (not yet drafted)
- "What's your CAC from real outreach?" (After 250 touches: actual reply, call and close rates.)
- "Why start with accounting, not dental?" (Answer: dated trigger and a single decision-maker; `market/first-market-selection.md` §3 inference.)
- "Show me the product." (After the readiness check is live and passes our own security bar; `engineering/codebase-audit.md` lists the blockers.)
- "Why not just sell the pack and skip the subscription?" (Depends on Watch attach and retention data.)
