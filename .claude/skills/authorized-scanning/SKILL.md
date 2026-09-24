---
name: authorized-scanning
description: Rules for what ChimeraShield may scan or test and how to prove authorization. Covers passive vs. active checks, domain-ownership verification, consent wording, data handling, and what to refuse. Load when designing, building, selling, or writing legal terms for any scan, audit, or AI-agent service.
---

# Authorized scanning rules

ChimeraShield is a security company. Scanning something without permission is illegal in most countries (e.g. the US CFAA, UK Computer Misuse Act, Nepal Electronic Transactions Act) and would end the company. These rules are non-negotiable.

## Tiers of checks
| Tier | Examples | Authorization needed |
|------|----------|----------------------|
| **Passive / public** | DNS lookups, SPF/DKIM/DMARC records, TLS certificate info, public breach databases (e.g. HIBP domain search needs verification), security headers from a normal page load | Customer account + stated relationship to the domain. Still show results only to verified owners. |
| **Light active** | Port and service scan, known-vulnerability checks, login-page exposure | **Verified domain ownership** (DNS TXT record or file upload) + checkbox consent with a timestamp stored |
| **Intrusive** | Penetration testing, phishing simulations, credential testing | Signed written authorization (scope, dates, contacts). Human-run only. Not in the MVP. |

## Consent wording (in product and ToS)
"I confirm I own or am authorized by the owner to test [domain/assets], and I authorize ChimeraShield to perform the checks described. I understand results may include sensitive security information."

## Product rules
- Verify ownership before any active check; re-verify every 90 days.
- Rate-limit scans and never target third-party infrastructure (shared hosts, CDNs) beyond the customer's own records.
- Pasted emails in the phishing analyzer may contain personal data: process in memory, don't train on it, and delete it within 30 days unless the customer saves it.
- Treat all LLM output as untrusted. Never auto-execute remediation.
- Findings are confidential: encrypted at rest, visible only to the account.

## Sales rules
- Demos run on the prospect's domain **only with their explicit permission**, or on a company-owned demo domain.
- Never send a prospect an unsolicited report on "vulnerabilities we found on your site". It's a trust and legal risk. Passive email-security (DMARC) observations are acceptable only if framed as public-record checks.

## Refuse
Any request to scan assets the customer doesn't own, test competitors, run phishing against people who haven't consented, or bypass the verification step.
