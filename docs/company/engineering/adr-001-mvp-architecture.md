# ADR-001: MVP Architecture

**Status:** Proposed (needs founder sign-off) · **Date:** 2026-09-24 · **Owner:** tech-lead (CTO)
**Related:** `codebase-audit.md`, `capability-estimates.md`, `sprint-plan.md`, `docs/company/product/catalog.md`, `docs/company/product/prd-wisp-evidence-pack.md`

## Context
- Pre-revenue. The north star is **3 paying customers by day 90**, and the PM catalog puts first revenue inside the **mid-Oct to mid-Dec 2026 PTIN window**. We are optimizing for **time to first paying customer**, then **lowest fixed cost**.
- One engineer (the founder, with AI coding help). No ops staff, so managed services only.
- Existing code: Next.js 14 in the root `app/`, and FastAPI in `backend/` with one Anthropic-backed endpoint. There is no DB, auth, billing, scheduler or email.
- MVP scope assumed here: **(a) passive domain check, (b) phishing analyzer, (c) weekly plain-English report**. (e) inbound helpdesk is designed for but not built.
- Constraints:
  - authorized-scanning skill: passive tier only, consent stored with a timestamp, findings visible only to the account, pasted emails deleted within 30 days, LLM output untrusted;
  - the ICP includes healthcare, so PHI exposure is possible.

## Decisions

| Concern | Decision | Main alternatives considered | Why |
|---|---|---|---|
| **Repo layout** | Keep root `app/` (Next.js) and `backend/` (FastAPI). **Delete the duplicate `frontend/`.** | Monorepo `apps/web` and `apps/api` | Smallest change; matches the Makefile, launch.json and README. |
| **Auth** | **Supabase Auth**: email magic link plus Google sign-in. FastAPI verifies Supabase JWTs against the project JWKS on every `/api/*` call. | Clerk (better UI, but a second vendor and a separate user store); roll our own (no) | Free tier; same vendor as the DB, so user IDs join naturally; row-level security (RLS) available. |
| **Database** | **Supabase Postgres** (US region). Tables: `orgs`, `members`, `domains`, `consents`, `scan_snapshots`, `findings`, `phish_verdicts`, `reports`, `job_runs`, `audit_log`. RLS on by default. Backend uses the service role only server-side. | Neon plus separate auth; SQLite on disk (no, it doesn't fit ephemeral hosts) | Managed, backups on Pro, and encryption at rest by the provider. |
| **Sensitive data** | Store **no email bodies by default**. Keep verdict, indicators and a SHA-256 only. Opt-in "save" auto-deletes after 30 days (daily cron). Findings are app-encrypted (Fernet key in env) for free-text fields. | Store everything | Skill data rules; reduces breach impact and PHI exposure. |
| **Job scheduling** | **Render Cron Job** runs `python -m backend.jobs.<job>` (weekly reports, daily retention purge). Jobs are idempotent via `job_runs(job, period)` unique keys. | Celery plus Redis (overkill); GitHub Actions cron (secrets outside the platform, unreliable timing); Supabase `pg_cron` plus `pg_net` (fine later) | No queue infrastructure; costs cents. |
| **Outbound email** | **Resend**, which also serves as SMTP for Supabase Auth magic links. SPF, DKIM and DMARC (`p=quarantine` at least) on our sending domain before launch. | Postmark (better deliverability reputation, but no free tier), SES (cheapest, more setup) | Free tier covers MVP volume. |
| **Inbound email** (for (e), post-MVP) | **Postmark Inbound** webhook to `POST /api/inbound/postmark` (basic-auth secret plus IP allowlist), when (e) is scheduled. MVP uses `.eml` **upload** instead. | Cloudflare Email Routing plus Workers (free, but a new runtime); Resend inbound (newer) | Mature parsing that keeps `message/rfc822` attachments. Don't pay for it until (e) is built. |
| **LLM provider** | **Anthropic only.** Remove the unused `openai` dependency. Upgrade `anthropic` from 0.28 to ≥1.0 for structured outputs. | OpenAI (GPT); multi-provider abstraction | One vendor, one DPA/BAA conversation, smaller attack surface. |
| **Models** | `TRIAGE_MODEL=claude-haiku-4-5-20251001` ($1/$5 per MTok) for first-pass phishing triage and finding rephrasing. `ANALYSIS_MODEL=claude-sonnet-5` ($2/$10 per MTok) for escalated phishing verdicts, weekly reports and WISP narrative drafts. **Replace the hardcoded `claude-opus-4-6`** ($5/$25). Both models come from env, never hardcoded. | Opus 5.5 ($4/$20) for everything | Sonnet 5 is 2.5x cheaper than the current Opus 4.6 and sufficient for grounded summarization. Prices and IDs were verified on platform.claude.com on 2026-09-24. |
| **LLM safety pattern** | Instructions in the system prompt; untrusted content in delimited tags. **Structured outputs** (`output_config.format` JSON schema), then Pydantic validation with bounds. Deterministic rule score as a **floor** on risk. The LLM never emits HTML. We render into our own escaped templates, with defanged URLs. Every report action must cite an existing finding ID. | Free-text parsing (current) | Treat LLM output as untrusted (security bar). |
| **Hosting** | **Backend:** Render Web Service (Starter, always-on, US). **Frontend:** Next.js `output: "export"` as a **Render Static Site** (free, CDN), calling the API at `NEXT_PUBLIC_API_URL`. | Vercel (Hobby tier is non-commercial only, and Pro is $20/mo); Fly.io; Railway | One vendor and dashboard. The free static tier allows commercial use. Our pages are client-side, so a static export works. Move to Vercel Pro if we need SSR or middleware. |
| **Payments** | **Stripe Checkout plus Customer Portal**, with a webhook to `POST /api/billing/stripe` that sets `orgs.plan`. **Before code exists:** Stripe **Payment Links** for founding members and the P1 pack (no engineering needed). | Paddle or Lemon Squeezy (merchant of record, handles global sales tax, higher fees) | Fastest to first dollar. **Blocker check:** Stripe must support the founder's legal entity country. If the company is not US-incorporated, use Stripe Atlas (US entity) or a merchant of record. `docs/company/legal/entity-options.md` notes Stripe is **not available to Nepal-registered businesses** and that US banking for Nepal residents is uncertain, so Paddle (merchant of record) is the fallback. Keep billing behind a small `billing/` interface so the provider can be swapped. |
| **Rate limiting** | `slowapi` (in-process, single instance) per user and per IP, plus **plan quotas in Postgres** (e.g. Starter: 1 domain, 100 analyses/mo). A global daily LLM-spend circuit breaker, plus the Anthropic console spend limit. | Redis-backed limiter | One instance is enough at MVP scale. |
| **Observability** | JSON logs (request ID, user ID, endpoint, status, latency, verdict; **never bodies, tokens or keys**), Sentry free tier with PII scrubbing, and an `audit_log` table for consent, domain add, login and billing events. | Datadog | Free |
| **CI** | GitHub Actions: lint, tsc, build, pytest, `npm audit --audit-level=high`, `pip-audit`. | none | Catches the issues in the audit automatically. |

## Estimated monthly cost

Anthropic token prices were **verified** on 2026-09-24. **Other vendor prices are from memory and unverified**: the egress proxy blocked render.com, supabase.com, resend.com, postmarkapp.com and vercel.com. Re-check them before budgeting.

**LLM usage assumptions per customer per month:** 1 domain, 4 weekly reports, 40 phishing analyses (a heavy user does 200).
- **Phishing analysis:** 70% resolved by Haiku (about 3k input, 500 output tokens, about $0.0055). 30% escalate to Sonnet 5 (about 4k input, 1.2k output including thinking, about $0.020, plus the Haiku call). **Blended about $0.012/analysis**, so about $0.48/mo.
- **Weekly report:** Sonnet 5, about 6k input and 1.5k output, about $0.027 each, so about $0.11/mo.
- Domain-check rephrasing: under $0.01.
- **Typical total about $0.60 per customer. Budget $1 (heavy user about $2.50).** Prompt caching on system prompts would lower this; not counted.

| Line item | 10 customers | 100 customers |
|---|---|---|
| Render web service (backend) | $7 (Starter) | $25 (Standard) |
| Render cron jobs | about $1 | about $2 |
| Render static site (frontend) | $0 | $0 (bandwidth permitting) |
| Supabase | $25 (Pro, for backups and no auto-pause; Free is acceptable before the first paying customer) | $25 to $35 |
| Resend | $0 (free tier) | about $20 |
| Sentry, GitHub | $0 | $0 to $26 |
| Domain | about $1 | about $1 |
| **Fixed infrastructure** | **about $34** | **about $75 to $110** |
| LLM (Anthropic) | about $10 (up to $25 heavy) | about $100 (up to $250 heavy) |
| **Infra plus LLM total** | **about $44 to $59** | **about $175 to $360** |
| **Per customer (infra plus LLM)** | **about $4.40 to $5.90** | **about $1.75 to $3.60** |
| Stripe fees (2.9% + $0.30 at $49/mo) | about $17 | about $172 |
| **All-in per customer** | **about $6.10 to $7.60** | **about $3.50 to $5.30** |

At $49/mo, gross margin is about 85–88% at 10 customers and about 89–93% at 100. Before revenue, the stack can run on free tiers (Supabase Free, Render free instance, Resend free) for **under $10/mo** plus LLM testing. Set a **$50/mo Anthropic spend limit** in the console until launch.

Excluded from these figures:
- (e) inbound email (Postmark, likely about $15/mo);
- HIBP API (price unverified);
- Stripe Atlas or entity costs;
- any BAA-eligible tiers (see the consequences below).

## Consequences
**Positive**
- Three vendors (Render, Supabase, Resend), plus Anthropic and Stripe.
- No queues or containers to operate.
- About $35/mo fixed until real scale.
- Every LLM path is schema-constrained and grounded.

**Negative / accepted risks**
1. **PHI/HIPAA.** Supabase, Render, Resend and the Anthropic API are **not covered by a BAA on these tiers** (Supabase HIPAA requires a higher plan and add-on; Anthropic BAA availability must be confirmed with Anthropic sales). Until then, the ToS and a UI banner **prohibit PHI**, and dental/healthcare offers must collect no ePHI (as the catalog already requires). This blocks a healthcare-first launch. Accounting-first (per the catalog) is unaffected.
2. **Static export** limits us to client-rendered pages with no Next middleware or SSR auth. That is acceptable for a dashboard app; revisit if SEO pages are needed (the landing page can live elsewhere).
3. **The single-instance rate limiter** resets on deploy. That's acceptable; plan quotas in Postgres are the durable control.
4. **Vendor lock-in** to Supabase Auth is moderate: users are standard Postgres rows, so migrating auth later means JWT verification changes only.
5. **Render cron** is not exactly-once. Idempotency keys in `job_runs` are mandatory.
6. **Payments depend on entity location.** This could delay subscription billing. P1 can be sold with Payment Links, or with a merchant of record as a fallback.

## Follow-ups
- Legal-ops: Stripe eligibility for the founder's entity; privacy notice and data-retention wording; BAA path.
- Founder: register the company domain (company-context `TODO`) and set up SPF/DKIM/DMARC for sending before launch.
- Revisit this ADR when (e) inbound email is scheduled, or at 100 customers.
