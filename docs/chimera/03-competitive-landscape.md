# Competitive Landscape — ChimeraShield

## The Market Map

### Tier 1: Enterprise AI Security (NOT direct competitors — too expensive)
| Company | Focus | Price | Why SMBs Can't Use It |
|---------|-------|-------|----------------------|
| CrowdStrike | EDR / threat intelligence | $150K+/yr | Enterprise contracts only |
| Darktrace | AI network monitoring | $50K+/yr | Requires on-site deployment |
| Vega Security | AI threat detection | $120M Series B | Enterprise-only |
| RunSybil | AI penetration testing | $40M raise | Enterprise focus |
| Onyx Security | AI agent security | $40M raise | Enterprise-only |

### Tier 2: SMB Security Tools (Legacy — NOT AI-native)
| Company | Focus | Price | Gap |
|---------|-------|-------|-----|
| Malwarebytes | Antivirus | $4–8/user/mo | Reactive, not AI |
| Webroot | DNS filtering | $3–5/user/mo | No AI threat analysis |
| KnowBe4 | Phishing training | $25/user/yr | Training only, not detection |
| 1Password | Password manager | $4/user/mo | Single feature |

### Tier 3: Compliance Tools (Adjacent)
| Company | Focus | Price | Gap |
|---------|-------|-------|-----|
| Drata | SOC 2 compliance | $10K+/yr | Compliance theater, not security |
| Vanta | Compliance automation | $10K+/yr | Same — compliance, not defense |

### Tier 2b: AI-branded SMB security platforms (DIRECT competitors, added 2026-09-24)
Full detail and sources: `docs/company/competitors/smb-landscape-2026.md`.
| Company | Focus | Price | Channel | Gap vs. us |
|---------|-------|-------|---------|------------|
| Guardz | "AI-native" unified SMB security (email, identity, endpoint, MDR); $56M Series B, 2025 ([source](https://fintech.global/2025/06/09/guardz-bags-56m-to-expand-ai-native-cybersecurity-for-smbs/)) | Not public ([source](https://guardz.com/pricing/)) | MSP | Needs an MSP; no owner-facing plain-English plan |
| Coro ("Coro AI") | AI-driven modular SMB security ([source](https://channelbuzz.ca/2025/09/smb-focused-coro-leverages-ai-into-unified-platform-44408/)) | ~$9.50/user/mo Essentials, third-party figure ([source](https://www.g2.com/products/coro-cybersecurity/pricing)) | Direct trial; shifting to partners | IT-operator dashboard |
| Huntress | "Agentic Security Platform", SOC-backed ([source](https://www.huntress.com/blog/ai-attackers-machine-speed-huntress-athena)) | $8.99/endpoint/mo, 50-unit floor, third-party figure ([source](https://underdefense.com/blog/huntress-pricing-guide/)) | Mostly MSP | Minimum ~$450/mo; built for MSPs |
| Microsoft Defender for Business / M365 Business Premium | Endpoint and email protection | $3/user/mo; Business Premium $22 ([source](https://www.microsoft.com/en-us/security/pricing/small-medium-business)) | Direct | Security Copilot is E5-only; no owner-level guidance |
| SentinelOne Singularity | EDR; Purple AI on Complete+ | ~$5.83–15/endpoint/mo, third-party figure ([source](https://www.cynet.com/security-foundations/endpoint-security/sentinelone-pricing-packages-core-control-and-complete/)) | Direct / MSP | IT-operator tool |

Free substitutes for our individual features also exist: AI scam checkers ([Norton Genie](https://us.norton.com/products/genie-scam-detector), [Bitdefender Scamio](https://www.bitdefender.com/solutions/scamio.html)), DMARC/SPF scanners ([Valimail](https://www.valimail.com/blog/free-dmarc-record-checker/), [PowerDMARC](https://powerdmarc.com/domain-analyzer/)), and [Coalition Control](https://www.coalitioninc.com/control).

## The Gap (Your Opportunity)
~~There is NO AI-native security product priced for SMBs.~~ **Corrected 2026-09-24: this claim is false.** Guardz and Coro sell AI-native or AI-branded security at SMB prices, and Huntress, SentinelOne, and Microsoft all sell AI-assisted protection to SMBs (sources above).

The real, narrower white space: **direct to the owner (no MSP, no agent) + plain-English, prioritized "fix this first" guidance + trigger-shaped outputs (insurance questionnaire, HIPAA, FTC Safeguards).** The incumbents detect threats. None of them explains security to a non-technical owner.

Positioning: *For owners of 5–50 person professional firms with no IT staff or MSP, who can't tell whether they're actually protected, ChimeraShield is the plain-English security advisor that checks your email, domain, and suspicious messages and tells you exactly what to fix first, unlike MSP-sold platforms like Guardz and Huntress, which need an IT partner to run them, or free scanners, which give you a score but no plan.*

## Competitive Advantages to Build
1. **Price:** $49–$149/month vs. $50K–$500K enterprise tools. *Note (2026-09-24): SMB competitors cost about the same or less (e.g. Defender for Business $3/user/mo), so price alone is not an advantage against Tier 2b.*
2. **Setup:** Under 10 minutes, no IT team required
3. **AI-native:** Built on modern LLMs (not retrofitted rule-based systems)
4. **Plain-English reports:** "You have 3 critical risks. Here's how to fix them."
5. **Agentic monitoring:** Runs continuously in background, alerts on anomalies

## Key Insight
The winners in SMB software are always the companies that take enterprise complexity and make it "stupid simple." Examples: Gusto (vs. ADP), Stripe (vs. traditional payment processors), Notion (vs. enterprise wikis). ChimeraShield is that play for AI security.
