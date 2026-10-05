# System Design — ChimeraShield

Status: draft v1 · Owner: `chimera-lead` · Companion to `01`–`05` in this folder.

## 1. Design goals

| Goal | Target |
|---|---|
| Time to first verdict | < 5 s p95 for an email scan |
| Cost per scan | < $0.01 average (cheap triage, escalate only the uncertain) |
| Usability | Non-expert understands verdict + next step in < 10 s |
| Trust | Calibrated confidence, honest about uncertainty |
| Safety | The scanner cannot be steered by the content it scans |

## 2. Current state (observed in code)

- `backend/routers/scan.py`: one endpoint, `POST /api/scan/email`, single prompt to a single model, free-text JSON parsed with `json.loads`.
- Gaps found:
  1. **Prompt injection**: email body is interpolated straight into the prompt; a malicious mail can instruct the model to return LOW risk.
  2. **Fragile parsing**: model may wrap JSON in prose or code fences; `content[0].text` assumed; `KeyError` caught but `pydantic.ValidationError` is not.
  3. **No bounds**: no max body length (cost and DoS), no auth, no rate limit.
  4. **Hardcoded model id**, sync client inside an `async` route (blocks the event loop).
  5. **No signals beyond text**: headers (SPF/DKIM/DMARC), URLs, attachments are ignored.
  6. **No evaluation**: no evidence yet of accuracy; the claims in `01-problem-statement.md` are market claims, not product claims.
  7. The UI exists twice (`app/` and `frontend/app/`).

## 3. Target architecture

```
 Browser (Next.js)
     │  POST /api/v1/scan/email
     ▼
 FastAPI ── validate (size, schema) ── auth + rate limit
     │
     ├─► Feature extractor (deterministic, no LLM)
     │     headers (SPF/DKIM/DMARC, Reply-To ≠ From), URLs (punycode,
     │     lookalike domains, shorteners), attachment types, urgency lexicon
     │
     ├─► Tier 1 triage  (small/fast model, schema-constrained output)
     │       └─ confident? ──► verdict
     │
     ├─► Tier 2 escalation (stronger model) for the uncertain band
     │
     ├─► Fusion + calibration  (rules + LLM score → calibrated probability)
     │
     └─► Verdict { level, calibrated_score, indicators[], action, evidence_ids }
              │
              └─► Ephemeral store (default: nothing persisted; opt-in 30-day history)
```

Key decisions (decision log):

| # | Decision | Why | Trade-off |
|---|---|---|---|
| D1 | Two-tier model cascade | Most mail is clearly benign/obvious; cost and latency drop several-fold | More moving parts; needs eval to set the escalation band |
| D2 | Deterministic features fused with LLM | Headers/URLs are objective evidence the LLM cannot see; makes verdicts explainable and harder to inject | Feature code to maintain |
| D3 | Schema-constrained output (tool use) | Removes parsing failures | Tied to provider feature |
| D4 | Untrusted-content delimiting + injection indicator | Attempts to steer the scanner become a signal | Not a complete defense; layered with D2 |
| D5 | Zero retention by default | SMBs in health/legal/finance; reduces breach and compliance burden | No history unless opted in |
| D6 | Calibrate before display | "87%" must mean ~87% | Needs labeled data (see §6) |

## 4. API contract (v1)

```
POST /api/v1/scan/email
{ "email_content": str (≤ 50k chars), "sender"?: str, "subject"?: str, "raw_headers"?: str }

200 {
  "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "risk_score": int 0–100,            // calibrated
  "confidence": "low" | "medium" | "high",
  "is_phishing": bool,
  "indicators": [{ "id": str, "plain": str, "why_it_matters": str, "source": "header"|"url"|"content"|"model" }],
  "recommendation": str,
  "scan_id": str
}
4xx/5xx { "error": { "code": str, "message": str } }   // generic, never echoes content
```

## 5. Product & visual design

### Users
Office managers and owners of 5–50 person firms. Anxious, busy, non-technical. They paste a suspicious email and want "can I click this?"

### Flow
1. **Paste** (single large field, optional sender/subject, "Scan" primary button; sample email link for first-time users).
2. **Scanning** (skeleton + "Checking links, sender and wording…", no spinner-only state).
3. **Verdict**: large status block → one-sentence action → "What we found" list → "Report to IT / Mark as safe / Scan another".
4. **Detail drawer**: each indicator with "what we saw" and "why it matters".

### Wireframe (verdict screen)

```
┌──────────────────────────────────────────────┐
│ ⚠  Likely phishing — don't click anything    │  ← status block (icon + text + color)
│    Delete this email and tell your IT person │  ← the one action
│    Confidence: High   Risk 91/100            │
├──────────────────────────────────────────────┤
│ What we found                                │
│ ▸ Link goes to micros0ft-login.co, not       │
│   microsoft.com                              │
│ ▸ Sender address doesn't match "From" name   │
│ ▸ Pressure wording: "within 2 hours"         │
├──────────────────────────────────────────────┤
│ [Report]  [Scan another]        Why this score?│
└──────────────────────────────────────────────┘
```

### Design tokens

| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg` | #FFFFFF | #0B1220 | page |
| `--surface` | #F5F7FA | #131C2E | cards |
| `--text` | #0F172A | #E6EAF2 | body (AA on bg) |
| `--brand` | #1D4ED8 | #7AA2FF | primary actions |
| `--safe` | #15803D | #4ADE80 | LOW |
| `--warn` | #B45309 | #FBBF24 | MEDIUM |
| `--danger` | #B91C1C | #F87171 | HIGH |
| `--critical` | #7F1D1D | #FCA5A5 | CRITICAL |

Type: system UI stack; 16px base, 1.5 line height; scale 14/16/20/28/40. Spacing 4-pt grid. Radius 12 (cards), 8 (inputs). Risk is always conveyed by **icon + word + color**, never color alone. Motion: ≤ 200 ms, respect `prefers-reduced-motion`.

### Microcopy

| Level | Headline | Action |
|---|---|---|
| LOW | Looks safe | Nothing to do, but trust your instincts. |
| MEDIUM | Be careful | Verify with the sender using a number you already know. |
| HIGH | Likely phishing | Don't click or reply. Report it. |
| CRITICAL | Dangerous | Delete it and tell your IT contact now. |

## 6. Scientific value

ChimeraShield can contribute evidence, not just a product, on a live question: **how well do LLM-based detectors handle AI-generated phishing at SMB-tolerable false-positive rates, and can they be made robust to injection?**

### Research questions and hypotheses
- **RQ1** Does LLM triage beat header/URL heuristics and TF-IDF+LR on AI-generated phishing at equal FPR? (H1: yes, by a margin larger than the bootstrap CI.)
- **RQ2** Does fusing deterministic features with the LLM improve precision at fixed recall over either alone? (H2: yes.)
- **RQ3** Are `risk_score`s calibrated, and does isotonic recalibration reduce ECE materially?
- **RQ4** How much does indirect prompt injection in the email body shift verdicts, and does delimiting + feature fusion reduce the attack success rate?
- **RQ5** What is the cost–accuracy frontier of the two-tier cascade vs always-strong-model?

### Experimental design
- **Data**: public phishing and ham corpora (license and provenance recorded), plus synthetic LLM-generated phishing and **hard negatives** (real urgent invoices, password resets). Dedupe, time-based split, no test-set prompt tuning.
- **Metrics**: precision, recall, F1, PR-AUC, FPR@fixed recall, ECE; **95% bootstrap CIs**; repeated runs to quantify LLM nondeterminism.
- **Ablations**: prompt variants, model tiers, with/without features, with/without delimiting.
- **Robustness suite**: injection strings, homoglyphs/punycode, non-English, image-only mail, long-body truncation.
- **Reproducibility**: `eval/` with seeded splits, pinned model ids, one command, results saved to `docs/chimera/eval-reports/`.

### Validity threats (stated up front)
Dataset age and distribution shift; synthetic-vs-real phishing gap; label noise; LLM version drift (pin and re-run on upgrade); SMB mail differs from public corpora, so collect opt-in, anonymised feedback to measure in-domain performance.

### Rules for claims
No accuracy number appears in marketing or the UI unless it is backed by a reported experiment with CI and its limitations. Until then the product says "helps spot likely phishing", not "catches X%".

## 7. Engineering plan (maps to `04-90-day-roadmap.md`)

| Step | Owner agent | Output |
|---|---|---|
| 1 Contract + threat model | `system-architect`, `security-engineer` | API v1, injection mitigations |
| 2 Harden endpoint (schema output, bounds, async, config) | `backend-engineer` | PR |
| 3 Verdict UI per §5 | `product-designer` → `frontend-engineer` | PR |
| 4 Eval harness + baselines | `detection-scientist` | `eval/`, report v0 |
| 5 Feature extractor + fusion + calibration | `backend-engineer`, `detection-scientist` | PR + report v1 |
| 6 Tests + CI | `qa-engineer` | workflow green |
| 7 Review gate on every PR | `code-reviewer` | approvals |

## 8. Open questions
- Which email ingestion path first: paste, forwarding address, or Microsoft 365/Gmail add-in?
- Retention opt-in terms for the target verticals (HIPAA/GLBA review).
- Pricing unit (per seat vs per scan) once cost/scan is measured.
