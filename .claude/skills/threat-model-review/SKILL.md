---
name: threat-model-review
description: Security review of ChimeraShield itself (prompt injection, abuse, privacy, secrets, dependencies). Use before shipping an endpoint, prompt, or model/provider change.
---

# Threat-model review

Owner: `security-engineer`. Defensive review only.

1. Map data flow: client → API → provider (local vs third-party) → response. Mark trust boundaries. Note that a self-hosted open model keeps email content in-house; a hosted provider does not.
2. Walk the checklist: prompt injection (delimiting, schema output, verdict that fails safe), output handling (no HTML, no URL fetching), abuse (auth, rate limit, size caps, token budget), privacy/retention/logging, secrets/CORS, dependencies (`pip-audit`, `npm audit`).
3. For model changes: re-run the injection set from the eval harness against the new model; models differ widely in resistance.
4. Output a ranked findings table: severity, `file:line`, scenario, fix. List what was not checked.
