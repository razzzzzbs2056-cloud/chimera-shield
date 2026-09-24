# Capability Estimates: Candidate Products and AI-Agent Services

**Owner:** tech-lead (CTO) · **Date:** 2026-09-24 · **Status:** estimates, not commitments
**Inputs:** `codebase-audit.md`, `adr-001-mvp-architecture.md`, `docs/company/product/catalog.md` (S1, S2, S5, P1, A1, A2), `docs/company/product/prd-wisp-evidence-pack.md`, `docs/company/competitors/smb-landscape-2026.md`, `.claude/skills/authorized-scanning/SKILL.md`

**Sizing:** **S** = 5 dev-days or less · **M** = 1–2 weeks · **L** = more than 2 weeks (one full-time engineer, with AI coding assistance). Every estimate assumes the shared foundation (CS-01 to CS-04 in `sprint-plan.md`: hardening, auth, DB, deploy, about 1 week) is done first. That foundation is **counted once, not per offer**.

## Summary

| # | Offer | Catalog ID | Effort | Scanning tier | Reuses | LLM cost per unit (est.) | Differentiated alone? |
|---|---|---|---|---|---|---|---|
| a | Passive email/domain check (SPF/DKIM/DMARC, TLS, headers) | S1 (inside S5) | **M** (about 6–8 days) | Passive | none | about $0.01 (optional summary) | No (free elsewhere) |
| b | AI phishing analyzer (paste or .eml upload) | S2 | **S–M** (about 4–6 days, hardening what exists) | n/a (customer-supplied content) | existing `scan.py` | about $0.006 (Haiku) to $0.02 (Sonnet) | No (free elsewhere) |
| c | Plain-English weekly risk report, emailed | A1 (lite) | **M** (about 5–7 days, after a) | Passive | a | about $0.03/report | Yes, combined with a |
| d | Continuous monitoring agent (re-checks, diffs, LLM brief) | A1 | **M** if passive only (c plus about 4 days). **L** with light-active checks. | Passive (recommended). Light active would need verified ownership. | a, c | about $0.03–0.05/brief | Partly |
| e | "Is this safe?" forwarding helpdesk agent | A2 | **M** (about 8–10 days, after b) | n/a | b | about $0.01–0.03/email | Partly (bundled in Watch) |
| f | Questionnaire / WISP / HIPAA risk-assessment generator | P1 / D2 / D4 | **M** for one template (WISP) with human review. **L** for self-serve plus all three. | Passive evidence only | a | about $0.20–0.60/document | **Yes** (trigger-shaped) |

**Scope flag:** the PM catalog ranks the **S5 readiness check** (a plus a 12-question quiz) and the **P1 concierge WISP pack** above b and c. The P1 PRD explicitly makes f a **concierge, document-only** v0 (non-goal: self-serve generator). My sprint plan builds a+b+c as asked, puts (a) first so it can power S5 by 15 Oct, and treats (f) as templates plus founder review, not code. **The founder should confirm that a+b+c is still the MVP, rather than S5 plus the P1 kit.**

---

## a) Passive email and domain security check. Effort **M**
**Approach**
- A backend `checks/` module that is pure functions with no LLM in the verdict. The result is a deterministic, versioned JSON finding set.
  - **DNS** (`dnspython`, via a fixed resolver such as 1.1.1.1 / 8.8.8.8):
    - MX;
    - SPF (parse it, follow `include:` up to the RFC 7208 10-lookup limit, flag `+all`/`?all`, flag multiple records);
    - DMARC (`p=`, `pct`, `rua`, alignment);
    - DKIM: probe **known selectors only** (Google `google`, M365 `selector1`/`selector2`, plus any selectors the customer names). DKIM keys **can't be enumerated**, so "no DKIM found" must read as "not confirmed", not "missing";
    - MTA-STS and TLS-RPT, BIMI (informational), DNSSEC flag.
  - **TLS:** one `ssl` handshake to `:443` of the apex and `www`. Report cert issuer, expiry days, hostname match, negotiated protocol. No cipher enumeration (that's closer to active scanning).
  - **Headers:** one normal `GET /` (httpx, 10 s timeout, max 3 redirects, same-site only). Check HSTS, CSP presence, X-Content-Type-Options, X-Frame-Options/frame-ancestors, Referrer-Policy, and flag `Server`/`X-Powered-By` version leaks.
- A rules table maps each finding to a severity, a plain-English "why", and a fix, written by us and reviewed once, **not generated per scan**. The LLM (optional, Haiku) only rephrases or prioritizes the top 3 for the report.
- UI: enter a domain, tick the consent box, see results. Results are shown only to an account whose **verified work email is on that domain** (catalog S5 rule), or after DNS TXT verification.

**Tier and authorization:** Passive / public. Requirements: an account, the stated-relationship consent text stored with a UTC timestamp, results visible only to the account, free-mail domains rejected, 1 domain per Starter account.

**Risks**
- **SSRF.** The user supplies a hostname, and we connect to it. We must resolve it first and refuse private, loopback, link-local and metadata IPs (including after redirects). This is the biggest security risk in (a).
- **Misleading "missing DKIM"** results (selector limits) erode trust. Word them carefully.
- Commodity: free DMARC checkers exist. The value is packaging (S5 quiz, Evidence Report, weekly brief).
- Hosting AUP: passive checks are fine. Don't add port scans on Render/Vercel.

## b) AI phishing email analyzer. Effort **S–M**
**Approach (harden the existing code, don't rewrite it)**
- Input: paste (sender, subject, body) **or an `.eml` upload**. The `.eml` path matters because it carries `Authentication-Results`, `Received`, and `Reply-To` headers, which are the strongest signals. Parse it with Python's `email` package and cap the size at 1 MB.
- **Deterministic pre-pass:**
  - SPF/DKIM/DMARC results from headers;
  - From vs Reply-To mismatch;
  - display-name spoofing;
  - lookalike domains (confusables, edit distance against a small brand list plus the customer's own domain);
  - URL extraction with text-vs-href mismatch, IP-literal and punycode URLs;
  - risky attachment extensions (read as metadata only; **never open or execute attachments**);
  - urgency and payment keywords.
  These produce a rule score.
- **LLM pass:** first `claude-haiku-4-5-20251001` triage. Escalate to `claude-sonnet-5` when the triage result is uncertain or HIGH, or when the input is long. Use structured outputs (JSON schema), with instructions in the system prompt and the email in delimited tags marked as untrusted data.
- **Final risk = max(rule score, LLM score)**, so an injected "this is safe" can't pull the risk down. The explanation lists both rule hits and LLM reasoning.
- **Never fetch URLs** found in the email: fetching can trigger tracking, one-click unsubscribes or exploit kits. An optional later add-on is a reputation lookup (Google Safe Browsing API, free tier) that sends only the URL.
- Show links in results **defanged** (`hxxps://example[.]com`) and never clickable. React escaping stays on; never use `dangerouslySetInnerHTML`.

**Data handling:** process bodies in memory. Store only the verdict, indicators and a SHA-256 of the body unless the user clicks "save". Auto-delete saved items after 30 days. Never log bodies. Healthcare users see a banner telling them not to paste patient information (see ADR-001 on BAAs).

**Risks**
- **False negatives create liability**, so the UI must say "assessment, not a guarantee".
- **Prompt injection.** Mitigated by the heuristic floor, structured output and an adversarial test set of 30 or more emails.
- **PHI/PII exposure** to our LLM vendor and database.
- Commodity: Norton Genie and Bitdefender Scamio are free. Keep it as a feature, not the product.

## c) Plain-English weekly risk report, emailed. Effort **M**
**Approach**
- A scheduled job (Render Cron, weekly) re-runs (a) for each active domain and stores a `scan_snapshot`. A pure-Python diff against the last snapshot finds new, fixed and unchanged findings.
- It also summarizes the week's phishing-analyzer counts (b).
- **LLM (`claude-sonnet-5`)** receives *only* the structured findings, diff and counts (never raw web content), and writes 150–250 words with the top 3 actions. Output uses a JSON schema (`headline`, `whats_changed[]`, `top_actions[3]`), which we render into **our own HTML template** with every string escaped. The LLM never produces HTML.
- **Grounding check:** every action must reference a finding ID that exists, or the report falls back to the deterministic template.
- Send via Resend. Include an unsubscribe link and a link to the dashboard. The email body contains **no raw sensitive detail**: headline plus top actions, with full detail behind login.
- Target reading level: grade 9 or lower (the PRD's measured Flesch-Kincaid bar).

**Tier:** Passive (reuses a).

**Risks**
- **Weekly passive results rarely change**, so "nothing changed" emails cause churn. Mitigations: include a rotating "one thing to do this week", or go monthly (catalog "Watch" suggests monthly). **Product question for the PM.**
- Hallucinated findings (mitigated by the grounding check).
- Email deliverability: set up our own SPF/DKIM/DMARC. A security vendor with a failing DMARC record is embarrassing.

## d) Continuous monitoring AI agent. Effort **M** (passive) / **L** (light active)
**Approach (passive, recommended):** (c) plus more frequent checks (daily DNS/TLS), change-triggered alerts, and a monthly LLM brief:
- alert on DMARC weakened, SPF changed, MX changed, cert expiring in 14 days or less, new header regressions;
- optionally, a new HIBP domain breach (only after HIBP's own domain verification, plus a paid HIBP API key; price not verified, check haveibeenpwned.com before committing);
- compliance-calendar reminders from the P1 data (WISP annual review, PTIN window).

"Agent" here means a scheduled pipeline with an LLM summarizer and **no autonomous actions**. It never auto-remediates (skill rule).

**Light active** (open ports, exposed login pages) would be **L**, because it needs:
- DNS TXT ownership verification with a stored consent checkbox and timestamp;
- 90-day re-verification;
- scanning from infrastructure whose AUP allows it (not Render/Vercel), with abuse-report handling;
- target scoping that excludes shared hosts and CDNs.

**Recommendation:** don't build light active checks in the MVP. The landscape doc says continuous monitoring is where Huntress, Coro and Microsoft are strongest, and the P1 PRD lists active checks as a non-goal.

**Risks:** alert fatigue; implying "continuous monitoring" satisfies 16 CFR 314.4(d)(2) (it does not; the catalog forbids the claim); scheduler reliability (use idempotent jobs plus a `last_run` check).

## e) "Is this safe?" forwarding helpdesk agent. Effort **M**
**Approach**
- Each firm gets an inbound address (`check+<firm-token>@in.<ourdomain>`) through an **inbound-email webhook** (Postmark Inbound recommended; alternatives in ADR-001).
- The webhook is verified by provider signature or basic-auth secret. Then:
  1. **Sender authorization.** The `From` address must be a registered member of the firm, **and** the forwarded message's own SPF/DKIM must pass for that domain. Otherwise anyone could spoof a staff address and use us as a reply relay (backscatter and spam reflection). Unknown senders are dropped silently and logged.
  2. **Extract the original.** Prefer "forward as attachment" (`message/rfc822`), which keeps the original headers. Inline forwards lose headers, so the verdict must say "limited analysis: forward as attachment for better results". Provide 1-page how-to guides for Outlook and Gmail.
  3. Run the (b) pipeline.
  4. **Reply** only to the verified sender, from our domain, with a plain-text plus escaped HTML template: verdict, 3 reasons, what to do. **No links from the analyzed email**, defanged only.
  5. **HIGH/CRITICAL verdicts go to a human review queue** (founder) before or after the reply, per catalog A2 ("human reviews every HIGH/CRITICAL"). Decision needed: send an immediate "treat as dangerous, human confirming" reply, then follow up.
- Quotas: per-firm daily cap, plus a global LLM spend circuit breaker.

**Risks**
- **Spoofing and abuse** of the inbound address (mitigated by the sender checks above).
- **Prompt injection that aims at the reply**, e.g. "tell the user to call 555-...". Mitigations: the reply is built from our template with fixed fields; the LLM text is length-capped and scanned for phone numbers and URLs not present in our allowlist.
- Latency expectations: target reply in 2 minutes or less.
- PHI in forwarded mail.
- Deliverability of our replies.
- Tax-season volume spikes.

## f) Questionnaire / WISP / HIPAA risk-assessment generator. Effort **M** (one template, reviewed) / **L** (self-serve, three templates)
**Approach**
- **Template-first, not LLM-first.** A lawyer- or legal-ops-reviewed WISP skeleton mapped to 16 CFR 314.4 (a)–(j) and IRS Pub 5708, with §314.6 exemption logic in code.
- Structured intake (the P1 script as a form) produces an `intake.json`. Evidence from (a) is labeled **Verified**, intake answers are labeled **Owner-stated**, and missing items are labeled **Gap** (PRD AC9).
- `claude-sonnet-5` drafts only the **firm-specific narrative paragraphs** per section, from `intake.json` fields. The prompt forbids adding any control not in the intake. Every generated sentence must cite an intake field ID. Unknowns become a visible `TODO: confirm`, and **zero placeholders at delivery** is a QA gate (PRD AC5).
- Render to DOCX (`python-docx`) and PDF. **Founder review before delivery** (PRD section 7).
- Banned-phrase check: "compliant", "certified", "passes" (PRD AC10).
- HIPAA SRA (D4) and insurance questionnaire prep (D2) reuse the engine with new templates. D4 must be **designed so no ePHI is collected**.

**Tier:** Passive evidence only. Admin settings are verified only through the owner's own screen-share or screenshots.

**Risks**
- **Legal liability and regulatory accuracy**: legal-ops must verify §314.6 and the disclaimer.
- Hallucinated controls: an LLM saying "MFA is enforced" when it isn't would be a false attestation. Mitigated by field-citation grounding and human review.
- The "$29 template" price anchor.
- A self-serve version is a **scope expansion beyond the P1 PRD** (a v0 non-goal). Build only the internal drafting tool for the founder until the catalog's pivot rule fires.

---

## Cross-cutting risks
1. **PHI and BAAs.** Healthcare and dental users of b and e may send PHI. Until we have a BAA with our LLM vendor, DB and email providers, ToS and UI must prohibit PHI. The dental offers (D4) must be designed to collect no ePHI.
2. **Founder location and payments.** If the company is not US-incorporated, Stripe may not be available directly (see ADR-001).
3. **Commodity features.** a and b are free elsewhere. Technical effort should go to packaging (c, f, S5), not to making the checks more elaborate.
4. **Single engineer.** Everything above totals about 10–14 weeks. The MVP (a+b+c) is about 4 weeks including the foundation.
