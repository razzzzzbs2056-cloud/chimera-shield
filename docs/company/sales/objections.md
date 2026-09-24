# Objection Handling: WISP & Evidence Pack and Watch

**Owner:** head-of-sales · **Date:** 2026-09-24 · **Status:** v1, based on desk research. **No objection here has been heard from a real prospect yet.** After each call, add the prospect's exact words and what worked.

## How to handle any objection
1. **Acknowledge** it sincerely ("That's fair").
2. **Ask one question** to find the real concern.
3. **Answer in 2–4 sentences**, plain English, honest about limits.
4. **Check:** "Does that address it?" Then return to the close or the next step.

**Hard limits in every answer:** no security guarantees, no "compliant/certified/IRS-approved", no invented customers or stats, no legal advice. If we can't honestly beat the objection, agree and move on (or disqualify).

---

### 1. "I'll just buy a $29 WISP template." / "The IRS template is free."
**Behind it:** "Why pay more for the same document?"
**Answer:**
> "A template is a good start, and the IRS one (Pub 5708) is free. What it can't do is fill itself in: your systems, your people, your vendors, what's actually turned on. That's the part that takes owners a weekend and usually doesn't get finished. With the Pack you spend one hour talking, and you get a plan that describes [FIRM], an evidence page showing what's verified vs. what's still a gap, and the 5 fixes to do first. If you'd rather fill in the template yourself, the free readiness check will tell you which sections to focus on."
**Ask:** "If you had the template today, when would you realistically sit down and finish it?"

### 2. "My IT guy handles it."
**Behind it:** Trust in an existing relationship; doesn't want to step on toes.
**Answer:**
> "Good, that makes this easier. Two questions: has your IT person written a WISP that's specific to [FIRM], and does it show what's actually in place? If yes, you're probably covered and I'd tell you so. If not, the Pack gives your IT person a clear, ranked list of fixes, and they do the hands-on work. We don't sell IT services, so we're not competing with them. Happy to include them on the intake call."
**Ask:** "When did you last see the written plan they keep for you?"
**If they have an MSP with a current WISP:** disqualify gracefully, ask for a partner intro (`partners.md`).

### 3. "We use Microsoft 365, so we're covered."
**Behind it:** Assumes buying the product means it's configured.
**Answer:**
> "Microsoft 365 has strong security features. Many of the important ones, like two-step login for everyone, only protect you if they're turned on and set up. A written plan also covers things Microsoft doesn't: who's responsible, your tax software, backups, staff training, and what you'd do after a breach. In the Pack we look at your admin settings with you on a screen-share, you in control, and mark what's verified. Often the fix list is mostly 'turn on what you already pay for.'"
**Ask:** "Do you know if two-step login is on for every account, including the owner's?"

### 4. "We're too small to be a target." / "We're under 5,000 clients, so we're exempt."
**Behind it:** Low perceived risk; partial knowledge of §314.6.
**Answer:**
> "The FTC Safeguards Rule applies to tax preparers regardless of size. Firms with fewer than 5,000 consumers are excused from some parts, like a written risk assessment, penetration testing, a written incident response plan and an annual report, but not from having a written security program, a Qualified Individual, MFA, encryption or training. And the W-12 asks every preparer about a written plan. The Pack applies the small-firm exemptions where they fit, so your plan is shorter, not skipped."
**Ask:** "Would it help to see which parts apply to a firm your size?"
**Note:** §314.6 details come from secondary sources. **Legal-ops must verify this wording against 16 CFR 314.6 before first use (playbook gate G9).** On "not a target": don't argue with fear or stats; say "Small firms hold exactly what attackers want, Social Security numbers and bank details, and the plan is required either way."

### 5. "It's busy season / I don't have time."
**Behind it:** Real capacity constraint (Jan–Apr is off-limits).
**Answer:**
> "That's exactly why the window is now. Your part is one 60-minute call; your office manager does a 15-minute checklist. Everything is delivered within 7 business days, and my last intake slot is December 4, so it's done before January. If this fall is truly full, I'll check back in May."
**Ask:** "Is there a 60-minute slot in the next three weeks that's less crazy than the rest?"
**If no:** `nurture-may`.

### 6. "Is AI safe with our client data?"
**Behind it:** Confidentiality duty; fear of client data going into AI tools.
**Answer:**
> "Good question to ask any vendor. The Pack doesn't use or need client data at all. We ask about your systems and processes, never about clients. Where we use AI to help draft your plan, I review every word before you see it, and nothing is changed in your systems automatically. For the Watch helpdesk, where staff forward suspicious emails, we'd be a service provider you list in your plan, and I'll give you in writing how forwarded emails are handled: how long they're kept, who can see them, and that they're not used to train models."
**Before saying the last sentence:** confirm with tech-lead that retention, access control and no-training terms are actually in place (catalog §7 item 4). If not yet: "The helpdesk isn't live yet; I'll show you the data terms before you turn it on."

### 7. "Is AI reliable? What if it gets something wrong?"
**Answer:**
> "AI can be wrong, so we don't let it decide anything on its own. In the Pack, a person (me) reviews everything, and every item on your evidence page says whether we saw it or you told us. In the helpdesk, a person reviews every high-risk verdict. The honest answer is that no tool catches everything; our job is to make your risks clear and your plan accurate."

### 8. "Too expensive."
**Behind it:** Price vs. a $29 template, or no budget clarity.
**Answer:**
> "Compared with what? If it's the template, the difference is the hours: you'd be doing the Pack's work yourself. If it's an IT company, they often bundle a plan into a per-user monthly contract; this is a one-time fee with no contract. And you get an evidence page you can reuse for your insurer and clients."
**Ask:** "What were you expecting to spend on this, including your own time?"
**Don't:** discount on the first objection. If price is the #1 loss reason after 6 calls, bring it to finance-modeler (playbook §5.4).

### 9. "We already have a WISP."
**Answer:**
> "Great. Two quick checks: does it name your actual systems and vendors, and has it been updated in the last 12 months? If both are yes, you may only need the free check to confirm your email settings. If not, the Pack updates what you have instead of starting from zero."
**Ask:** "Who wrote it, and when was it last opened?"

### 10. "We have antivirus / we're protected."
**Answer:**
> "Antivirus is one important piece. The written plan covers the rest: who's responsible, two-step login, encryption, backups, training, your vendors, and what happens after an incident. The evidence page will show antivirus as verified if we see it, and point out what's still missing."

### 11. "Nobody enforces this. The FTC isn't going after small tax shops."
**Behind it:** Low perceived enforcement risk (the market doc agrees enforcement against small firms looks rare).
**Answer:**
> "You may be right that enforcement against small firms is rare; I won't pretend otherwise. The reasons owners do it anyway are practical: you confirm the W-12 question every year, insurers and larger clients increasingly ask for proof, and if something does happen, a plan and a fix list make the first 30 days far less chaotic."
**Don't:** invent enforcement cases or fines.

### 12. "We have cyber insurance."
**Answer:**
> "That's smart. Insurers usually ask about controls like MFA and backups at renewal, and the answers need to be true for a claim to go smoothly. The evidence page helps you answer those questions accurately; you always answer the insurer yourself, we don't. When is your renewal?"
**Don't:** claim anything about coverage or claim outcomes.

### 13. "Just send me some information."
**Behind it:** Polite brush-off, or genuine interest with no time.
**Answer:**
> "Happy to. So I send the right thing: is your main question the price, what's in the plan, or whether it's needed for a firm your size?" Send a 5-line recap with the specific answer, plus one proposed intake time.

### 14. "Who are you? I've never heard of ChimeraShield." / "How many firms have you done?"
**Answer (honest):**
> "Fair question. We're new. You'd be one of our first 10 firms, which is why it's at founding pricing and why I do each intake personally. I'll show you a sample plan and evidence page for a fictional firm so you can see exactly what you'd get, and the engagement letter spells out what we do and don't do."
**Never:** imply existing customers, logos or certifications.

### 15. "Will this make us compliant?" / "Can you be our Qualified Individual?"
**Answer:**
> "No one can honestly promise compliance from a document. The Pack gives you a written plan that reflects your firm, evidence of what's in place, and a clear list of what to fix. Compliance comes from actually doing those things. And the Qualified Individual has to be someone at your firm, usually you; we help you understand the role, we can't take it on."

### 16. "Can you just fix everything for us?"
**Answer:**
> "We don't do hands-on IT work; that keeps us neutral and keeps costs down. Each fix in your plan says who can do it, often you in 15 minutes, sometimes your IT provider. I'll answer questions by email while you work through them."

### 17. "Let me talk to my partner." (See `call-script.md` close section.)
Offer a 10-minute three-way call; otherwise send a forwardable one-paragraph recap and ask "What will your partner ask first?"

---

## Objection log (add after every call)
| Date | Objection (their exact words) | Answer used | Result (moved on / lost / won) |
|---|---|---|---|
