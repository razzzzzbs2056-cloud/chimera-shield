# Partner Program (v0): MSPs, tax/bookkeeping communities, cyber-insurance brokers

**Owner:** head-of-sales · **Date:** 2026-09-24 · **Status:** hypothesis. Fees and terms need finance-modeler (economics) and legal-ops (agreement, disclosures, insurance-law check) before anything is signed or paid.
**Why partners:** one trusted partner can introduce more qualified firms than weeks of cold email (recruiting kit §5), and partner-referred leads are assumed to close at ~40% vs. ~25% cold (playbook §5.1, assumption). Target for this window: **10 partners pitched by 6 Nov, 2 active, 3–5 referred calls, 1–2 Packs sold.**

Discovery-phase partner asks ("introduce me for research") are in the recruiting kit. This file is the **commercial** program.

---

## 1. Program at a glance (hypotheses)

| Partner type | What they do | What they get | Fee hypothesis |
|---|---|---|---|
| **MSPs** serving accounting/tax firms | Refer clients who lack a firm-specific WISP; join the intake; do the hands-on fixes | Billable remediation work from our Fix-First plan; a client who can finally explain what they have; no competition (we don't sell managed services) | **20% of the Pack fee** + **10% of first-year Watch revenue** per referred firm. Later option: MSP co-delivery/wholesale price `[PARTNER_PACK_PRICE]` once 5 Packs are delivered. |
| **Tax-software, practice-management and bookkeeping communities** (group admins, user-group leads, bookkeeper networks, practice-management consultants) | Host a 30-minute educational session or post; share the free Readiness Check | Useful, non-salesy content for members during renewal season; members get the founding price | **Admins/consultants:** same 20% / 10%, or a flat `[COMMUNITY_FEE]` per paid Pack. **No payments to community platforms themselves** without their written program terms. |
| **Cyber-insurance brokers** writing small professional-services policies | Suggest the Pack to clients who struggle with security questions on applications/renewals | Clients who can answer control questions accurately and with evidence; fewer back-and-forth rounds | **Default: no cash fee.** Value exchange only (co-branded checklist, priority intake slots) until legal-ops clears producer compensation and anti-rebating rules state by state. |
| **Customer referrals** (after delivery) | Introduce another firm owner | One month of Watch credited (`[WATCH_PRICE]`) per referred firm that buys | Credit, not cash |

**Common terms (all partners):**
- Fee is paid **30 days after** the referred customer's payment clears and any refund window has passed (`[REFUND_TERMS]`, from legal-ops); no fee on refunded sales.
- A referral counts if the partner **introduced** the firm (W3 intro email in `sequences.md` or a tracked link) and the firm buys within **90 days**; first introducer wins; firms already in `pipeline.csv` at `3-engaged` or later don't count.
- **Disclosure:** every referred firm is told in writing that the partner may receive a fee (line in W3 intro email).
- **No data sharing** beyond the fact of a sale: partners never see a customer's findings, WISP or Evidence Report **unless the customer gives written permission** (e.g. an MSP invited to the debrief).
- Partners may not make claims we can't back: no "makes you compliant", no guarantees, no invented results. They use our approved one-pager and email copy only.
- Partners follow the same anti-spam rules: no cold-blasting their lists with our offer; they introduce people they already have a relationship with.
- Either side can end the arrangement with 30 days' notice; fees for sales already made are still paid.
- Track partner-sourced deals in `pipeline.csv` via `partner_ref` (partner code, never a person's name).

---

## 2. Compliance flags (legal-ops to confirm before first fee)

1. **CPAs receiving referral fees (AICPA Code ET 1.520).** A CPA in public practice can't accept a commission for referring a product to a client for whom they perform attest work (audit, review, compilation, prospective financial statements), and must **disclose in writing** any permitted referral fee. If a CPA or CPA-owned bookkeeping firm is a partner, they must check this themselves; our agreement will require them to confirm compliance. ([PwC Viewpoint, ET 1.520](https://viewpoint.pwc.com/dt/us/en/aicpav2/ps/ps/code_of_professional_conduct_revised/et-cod_part1/et-cod1_500/et-cod1-520-d4463aAaC.html); [Journal of Accountancy](https://www.journalofaccountancy.com/issues/2020/nov/cpa-referrals-unintended-consequences/))
2. **Insurance brokers.** State insurance laws regulate producer compensation and "rebating" (giving clients value to induce a policy purchase). The NAIC amended its model act to allow some loss-mitigation value-added services, but only where states adopted it, and rules vary ([NAIC, Journal of Insurance Regulation 2025](https://content.naic.org/sites/default/files/cipr-jir-2025-3.pdf); [Mayer Brown](https://www.mayerbrown.com/en/insights/resource-centers/insurtech/anti-rebating-laws)). Until legal-ops clears it: no cash to brokers, no discount framed as tied to buying a policy, and we never fill in insurance applications (PRD §8).
3. **Partner agreement:** a 1–2 page referral agreement (fees, disclosure, no-claims clause, confidentiality, termination) from legal-ops. Nothing is paid on a handshake.
4. **1099 reporting:** US partners paid $600+ in a year need a W-9 on file (finance-modeler/accountant to confirm threshold for 2026).

---

## 3. Pitches

### 3.1 MSP pitch (talk track, 5 minutes)
> "We do one thing: a written information security plan and one-page evidence report for small accounting and tax firms, finished in a week, in plain English. We don't sell endpoint tools, monitoring or IT support, and we never will for your clients.
>
> Here's why that helps you: every Pack ends with a ranked list of 5 fixes, each saying who does it. For your clients, that's you. You get a clear, client-approved scope of work instead of chasing them about MFA. You can join the intake call so the plan reflects what you've actually set up, and it shows your work as *Verified* on the evidence page.
>
> If you already write WISPs for your accounting clients, we're probably not a fit, and that's fine. If you don't, or they're generic, we'd pay a referral fee on each Pack and on the first year of Watch."

**Ask:** "Which 2–3 of your accounting clients are renewing PTINs and don't have a firm-specific plan? Would you ask them if they'd like an intro?"

**Cold email to an MSP (under 100 words):**
> **Subject:** wisps for your accounting clients
>
> Hi [FIRST_NAME],
>
> [PERSONAL_LINE, e.g. "Your site lists accounting firms as a core vertical."]
>
> PTIN renewal means your tax clients will be asked about a written security plan. We write firm-specific plans and a one-page evidence report, and every fix list points hands-on work back to the client's IT provider. We don't sell managed services.
>
> Open to 15 minutes on a referral arrangement?
>
> [FOUNDER_NAME], Founder, ChimeraShield
> [FOUNDER_NAME]@[DOMAIN] · [POSTAL_ADDRESS]
>
> If this isn't relevant, just reply "no" and I won't follow up.

**Where to find them:** MSP websites listing "accounting" or "CPA" as a vertical (search "IT services for CPA firms [STATE]"); r/msp (read rules; contribute before asking); local MSP peer groups; MSPs named by interviewees.
**Watch-outs:** Some tax-focused MSPs sell their own WISP bundles (market doc names Bellator); they're competitors, not partners. Qualify by asking "Do you write WISPs for clients today?"

### 3.2 Tax-software / practice-management / bookkeeping community pitch
Targets (verify each exists and read its rules on vendor posts before contacting):
- Admins of active Facebook/LinkedIn groups for tax preparers and EAs
- Tax-software user groups and resellers (Drake, UltraTax, Lacerte, ProSeries, CrossLink: user groups **unverified**)
- Practice-management communities (TaxDome, Canopy, Karbon). Note: TaxDome runs its own partner program that pays affiliates for referring firms **to TaxDome** ([TaxDome partner terms](https://taxdome.com/policies/partner-program-terms)); that's a channel for them, not a referral route for us. Approach community leads and consultants, not the vendor, unless the vendor offers a marketplace listing.
- Bookkeeper networks and bookkeeping-firm owners (they're also covered by the Safeguards Rule, so they can be customers as well as referrers)
- State CPA society chapter CPE organizers and small-firm section leads

**Talk track:**
> "Your members will all hit the W-12 line 11 question at renewal this fall. I'd like to offer a free 30-minute session: 'The W-12 security-plan question in plain English: what the FTC Safeguards Rule asks of a small firm, and the parts of Pub 5708 that small firms tend to skip.' No pitch in the session beyond one closing slide with a free readiness check. Members who want help get the founding price. If it's useful and your rules allow it, we'd pay a disclosed referral fee on any Pack that results; if your group doesn't allow that, the session is free anyway."

**Cold message to a community admin (under 100 words):**
> **Subject:** free session for [GROUP] before ptin renewal
>
> Hi [FIRST_NAME],
>
> [PERSONAL_LINE, e.g. "I've been reading [GROUP]'s threads on renewal season."]
>
> Would a free 30-minute session help your members this fall? Topic: the W-12 written security plan question and the FTC Safeguards Rule, in plain English, with a short checklist. Educational, one closing slide about us, and I'll follow your group's rules.
>
> Worth a quick call to see if it fits?
>
> [FOUNDER_NAME], Founder, ChimeraShield
> [FOUNDER_NAME]@[DOMAIN] · [POSTAL_ADDRESS]
>
> If this isn't relevant, just reply "no" and I won't follow up.

### 3.3 Cyber-insurance broker pitch
> "When your small accounting clients renew, they're asked about MFA, backups, training and a written plan, and many aren't sure what's actually in place. Our Pack produces a one-page evidence report that marks each control as verified, owner-stated or a gap, plus a fix list. Your client answers the application themselves, but with facts instead of guesses. We're not asking for a fee; we'd like to be the resource you point clients to when they get stuck on security questions."

**Ask:** "When a small professional-services client struggles with the security section, what happens today? Would a one-page checklist we co-write for your clients be useful?"

**Cold email to a broker (under 100 words):**
> **Subject:** security questions on your clients' applications
>
> Hi [FIRST_NAME],
>
> [PERSONAL_LINE, e.g. "Your agency lists professional-services cyber coverage for firms in [STATE]."]
>
> Small accounting clients often can't say for sure whether MFA, backups or training are in place. We produce a one-page evidence report that marks each control verified, owner-stated or gap, so they can answer accurately. They answer the insurer themselves.
>
> Worth 15 minutes to see if it helps your renewals?
>
> [FOUNDER_NAME], Founder, ChimeraShield
> [FOUNDER_NAME]@[DOMAIN] · [POSTAL_ADDRESS]
>
> If this isn't relevant, just reply "no" and I won't follow up.

**Never:** say the Pack lowers premiums or improves claim outcomes; we have no evidence of that.

---

## 4. Partner timeline (fits `playbook.md` §5.3)
| Week | Action |
|---|---|
| 28 Sep – 9 Oct | List 20 candidates (8 MSPs, 8 community leads, 4 brokers). Pitch 6. Ask legal-ops for the referral agreement and the ET 1.520 / broker checks. |
| 12–23 Oct | Pitch 4 more. First partner call(s). Draft the co-branded broker checklist and the 30-minute session deck (educational). |
| 26 Oct – 6 Nov | 1 partner live; first session or group post. Checkpoint: if 0 partners engaged, drop brokers and focus on MSPs + one community. |
| 9–20 Nov | 2nd partner live; W3 intros flowing. |
| 23 Nov – 11 Dec | Close referred deals before Dec 4 intake cutoff; thank partners; pay earned fees per terms. |
| May 2027 | Re-activate partners for off-season and next renewal cycle. |

## 5. What to learn from partners (feed back to product and finance)
- Do MSPs want referral fees, or a co-delivery/wholesale Pack they resell? (Decides the $149 MSP tier.)
- What share of their accounting clients have a firm-specific WISP today?
- For brokers: which security questions small professional-services firms get stuck on most.
