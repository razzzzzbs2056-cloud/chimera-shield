# First Market Selection: ChimeraShield

**Author:** market-researcher agent · **Date:** 2026-09-24 · **Status:** Draft for founder decision

> **Research-method warning (read first).** Web *search* worked, but the web *fetch* tool and direct downloads were blocked by this session's network egress policy for every domain tried (census.gov, api.census.gov, data.census.gov, bls.gov, fred.stlouisfed.org, irs.gov, ada.org, infosecurity-magazine.com, naicslist.com). So:
> - I could **not** pull County Business Patterns (CBP) tables by employee-size class. Business counts below come from search-result summaries of the listed pages, not from opening the Census tables myself.
> - Every number has a URL, but I did not open the page to check it. **Check the top 10 numbers against the primary source before they appear in any deck or outreach.**
> - Size-class splits (share of firms with 5–49 employees) are **my assumptions** and are labeled as such.

Labels used: **Fact** (sourced), **Assumption** (mine, explained), **Inference** (my reasoning from facts). **Stale** means the data is more than 2 years old (before Sept 2024).

---

## 1. Verdict

**Start with US accounting, CPA and independent tax-prep firms with 5–50 employees (score 44/50).** They have a federal rule that already requires what we sell. The FTC Safeguards Rule covers them at any size and requires MFA, encryption, monitoring and a written security program. Every PTIN holder must also certify a written security plan (WISP) each year.
They are easy to find through public preparer and CPA directories, the owner usually decides alone, and the October–December PTIN renewal window gives us a yearly deadline to sell against.
**US dental practices (41/50) are the runner-up** and the larger market. Keep them as segment #2 and test both in the first 10 interviews (6 accounting, 4 dental).

---

## 2. Scoring table

Rubric from `market-hunting` skill. Weights: Pain ×3, Willingness to pay ×2, Reachability ×2, Sales speed ×1, Competition gap ×1, Founder access ×1. Maximum 50; 38 or more is a strong first market. **Founder access is unknown and scored 3 for every segment.** Note: `docs/company/README.md` mentions "a founder in Nepal". If that's right, South Asia's founder-access score could rise to 5 (+2), which still wouldn't change the ranking.

| Rank | Segment | Pain ×3 | WTP ×2 | Reach ×2 | Speed ×1 | Gap ×1 | Founder ×1 | **Total** |
|---|---|---|---|---|---|---|---|---|
| 1 | **US accounting / CPA / tax-prep (5–50 emp.)** | 5 | 4 | 5 | 4 | 4 | 3 | **44** |
| 2 | **US dental practices (independent, non-DSO)** | 5 | 4 | 4 | 4 | 3 | 3 | **41** |
| 3 | US small law firms (2–49 attorneys) | 4 | 4 | 5 | 3 | 3 | 3 | **39** |
| 4 | US medical (physician) clinics | 5 | 3 | 3 | 3 | 3 | 3 | **36** |
| 5 | Small MSPs (as a channel) | 3 | 4 | 5 | 3 | 1 | 3 | **34** |
| 6 | US e-commerce SMBs | 3 | 3 | 4 | 5 | 2 | 3 | **33** |
| 7 | South Asia (Nepal/India banks, co-ops, clinics) | 4 | 2 | 3 | 2 | 4 | 3 | **31** |

### One-line reasons per score

**US accounting / CPA / tax-prep: 44**
- Pain 5: **Fact.** The FTC Safeguards Rule treats tax preparers, CPAs, EAs and bookkeepers as "financial institutions" regardless of size. It has been enforceable since June 2023, and a 30-day FTC breach notice has been required since 13 May 2024 for breaches of 500 or more consumers ([FTC](https://www.ftc.gov/business-guidance/resources/ftc-safeguards-rule-what-your-business-needs-know); [Venable, 2023](https://www.venable.com/insights/publications/2023/11/data-breach-notice-requirement-added)). The IRS logged nearly 300 tax-practice data breaches in H1 2025 ([Carry, 2025](https://carry.com/news/irs-wraps-2025-security-summit-tax-identity-theft)).
- WTP 4: **Fact/Inference.** The WISP is required for PTIN renewal, and today it's bought as a $29–$999 template or as managed services priced per user ([Bellator Cyber, 2026](https://bellatorcyber.com/blog/cybersecurity-provider-for-tax-practice); [writtensecurityplan.com](https://www.writtensecurityplan.com/)). That leaves a gap between "cheap PDF" and "expensive MSP". Not a 5 because small firms are price-sensitive.
- Reach 5: **Fact/Inference.** 870,679 PTIN holders in 2025 ([IRS RPO stats, 2025–26](https://www.irs.gov/node/3635)). The IRS Directory of Federal Tax Return Preparers with Credentials, state CPA society "find a CPA" directories, and r/taxpros and r/accounting are all public.
- Speed 4: **Inference.** The owner-partner decides. Minus 1 because selling is close to impossible during filing season (Jan–Apr 15).
- Gap 4: **Inference.** Incumbents sell either WISP documents or full MSP/hosting. We found no AI-native, plain-English product at $49–$149/month.

**US dental practices: 41**
- Pain 5: **Fact.** HIPAA applies. Hacking caused more than 80% of large 2025 breaches on the OCR portal ([HIPAA Journal, 2025](https://www.hipaajournal.com/2025-healthcare-data-breach-report/)). There were several dental breaches in 2025, such as True Dental Care's ransomware incident, which affected 17,640 patients ([Becker's Dental, 2025](https://www.beckersdental.com/dentists/15-data-breaches-that-impacted-dentistry-in-2025/)). The proposed HIPAA Security Rule would require MFA and encryption with no small-practice exemption ([Medcurity, 2026](https://medcurity.com/hipaa-security-rule-2026/)).
- WTP 4: **Inference.** Practices already pay for practice-management software and IT vendors, and patient-data loss has clear notification costs.
- Reach 4: **Inference.** ADA Find-a-Dentist, state dental societies, Google Maps categories, Dentaltown and r/Dentistry.
- Speed 4: **Inference.** The owner-dentist decides, but often defers to the existing dental IT vendor.
- Gap 3: **Inference.** Crowded with dental-specific IT MSPs and HIPAA-compliance vendors. DSOs, which employ 16.1% of dentists (2024), buy centrally ([ADA HPI, 2024](https://www.ada.org/resources/research/health-policy-institute/dental-practice-research/practice-modalities-among-us-dentists)).

**US small law firms: 39**
- Pain 4: **Fact.** 29% of firms reported a breach, and firms with 10–49 attorneys had the highest rate ([ABA TechReport 2023/2025 via search](https://www.americanbar.org/groups/law_practice/resources/tech-report/2023/2023-cybersecurity-techreport/); 2023 figure is **stale**). The duty comes from ABA Model Rule 1.6(c) and Opinion 483, which is ethics guidance, not an audited regulation. That makes it softer than FTC/HIPAA, so 4.
- WTP 4: **Fact.** 68% of 10–49 attorney firms and 55% of small firms budget for technology ([ABA 2024 Solo & Small Firm TechReport](https://www.americanbar.org/groups/law_practice/resources/tech-report/2024/2024-solo-and-small-firm-techreport/)).
- Reach 5: **Fact/Inference.** State bar directories are public. There were 165,491 employer law offices in 2023 ([Census CBP 2023, via search](https://data.census.gov/profile/541110_-_Offices_of_Lawyers?n=541110); 2023 data, borderline **stale**).
- Speed 3: **Inference.** Partners are skeptical and decide by consensus.
- Gap 3: **Inference.** Legal-focused MSPs and practice-management vendors (e.g., Clio) already cover some security.

**US medical clinics: 36**
- Pain 5: same HIPAA drivers as dental.
- WTP 3: **Fact.** Only 42.2% of physicians work in physician-owned practices, and 47.4% work in practices of 10 or fewer physicians (2024). More are hospital-owned and don't buy on their own ([AMA Benchmark 2024](https://www.ama-assn.org/practice-management/private-practices/smaller-share-doctors-private-practice-ever)).
- Reach 3, Speed 3, Gap 3: **Inference.** Practice managers are gatekeepers, EHR vendors hold the relationship, and the space is crowded with compliance vendors.

**Small MSPs (channel): 34**
- Pain 3: **Inference.** Their clients' insurance questionnaires create pain, but MSPs already have tools.
- WTP 4: **Fact.** They already buy per-endpoint tools. Huntress Managed EDR lists at $8.99 per endpoint per month, and partner rates run about $2–4.50 ([MDRCost, 2026](https://mdrcost.com/huntress-pricing)).
- Reach 5: **Fact.** About 40–50k US MSPs, most with fewer than 25 staff ([Infrascale, 2025](https://www.infrascale.com/msp-statistics-usa/); vendor estimate). r/msp is very active.
- Speed 3: **Inference.** They need PSA/RMM integrations and multi-tenant features before they'll adopt.
- Gap 1: **Fact.** Many tools are built MSP-first: Guardz, Coro ($6.99–$8.99 per user per month), Huntress, and others ([Capterra/Coro, 2026](https://www.capterra.com/p/182368/Coronet/pricing/); [Guardz pricing](https://guardz.com/pricing/)).

**US e-commerce SMBs: 33**
- Pain 3: **Fact/Inference.** PCI DSS 4.0.1 anti-skimming requirements 6.4.3 and 11.6.1 took effect 31 Mar 2025, but SAQ A merchants (most hosted Shopify stores) got an eligibility criterion instead of those requirements ([PCI SSC blog, 2025](https://blog.pcisecuritystandards.org/coffee-with-the-council-podcast-guidance-for-pci-dss-e-commerce-requirements-effective-after-31-march-2025)). The platform carries most of the risk.
- WTP 3, Reach 4, Speed 5: **Inference.** Founders buy apps by credit card in minutes, but security value is hard to see for them.
- Gap 2: **Inference.** Shopify, Stripe and fraud-tool vendors already cover the main pain. The count of stores is fuzzy: 2.7–3.5M "online stores" ([Clearly Payments, 2025](https://www.clearlypayments.com/blog/how-many-online-stores-are-in-the-usa-in-2025/)).

**South Asia (Nepal/India): 31**
- Pain 4: **Fact.** NRB Cyber Resilience Guidelines (2023) apply to all licensed institutions ([ICTFrame](https://ictframe.com/nrbs-cyber-resilience-guidelines/)). Nepal recorded Rs 1.79B in cyber-enabled financial fraud in FY2081/82 (2024/25) ([ICTFrame, 2025](https://ictframe.com/nepals-cybersecurity-crisis-2025/)). India's DPDP Rules were notified 13 Nov 2025 with full compliance by May 2027 ([India Briefing, 2025](https://www.india-briefing.com/news/dpdp-rules-2025-india-data-protection-law-compliance-40769.html/)). 47% of Indian small businesses lost time or money to a cyber incident ([BW Businessworld, 2025](https://www.businessworld.in/article/survey-reveals-nearly-half-of-indian-smes-faced-cyber-incidents-in-2025-608641)).
- WTP 2: **Inference.** $49–$149 a month is high relative to local SMB budgets, and cost is the top barrier.
- Reach 3: **Fact/Inference.** There are about 34,000 Nepali co-ops ([Kathmandu Post, 2025](https://kathmandupost.com/province-no-3/2025/01/22/bagmati-province-has-highest-number-of-cooperatives-but-no-dedicated-monitoring-body)), reachable through federations such as NEFSCUN. Banks are reached through relationships.
- Speed 2: **Inference.** Banks run formal procurement, and co-op purchases need committee approval. Banks also fall outside our 5–50 employee ICP.
- Gap 4: **Inference, not verified.** Few AI-native local offerings.

---

## 3. Market size, top 2 segments (bottom-up)

Formula (skill): `# businesses in ICP × % reachable × annual price`. Price points: $49 / $99 / $149 per month = $588 / $1,188 / $1,788 per year.

### 3a. US accounting, CPA and tax-prep firms

| Step | Value | Label / Source |
|---|---|---|
| CPA firms with employees | 52,200 firms (~55,000 locations) | Fact: [CPA Trendlines Almanac, 2024](https://cpatrendlines.com/2024/01/01/cornerstone-cpa-trendlines-almanac-key-data-points-for-the-tax-accounting-and-finance-profession/) (Census-derived) |
| Non-employer solo CPA practices | 34,900 (excluded from ICP) | Fact: same source |
| Tax-prep establishments (NAICS 541213) | 33,293 | Fact, **stale (2020)**, via [naicslist](https://naicslist.com/naics/541213). Includes H&R Block/Jackson Hewitt franchise offices |
| Share of CPA firms with 5–49 employees | 35% | **Assumption.** About 85% of CPA firms have fewer than 10 employees ([ipassthecpaexam, citing AICPA; year unclear](https://ipassthecpaexam.com/number-of-cpa/)), so most are 1–4. I assume 35% fall in 5–49 |
| Share of tax-prep establishments that are independent with 5–49 staff | 20% | **Assumption.** Excludes franchise chains and seasonal micro-shops |
| **ICP firms** | 52,200×0.35 + 33,293×0.20 = **≈24,900** | Calculation |
| % reachable (public email/website via PTIN/CPA directories) | 60% | **Assumption** |
| **Reachable ICP firms** | **≈14,960** | Calculation |

| Price | SAM (reachable ICP × price × 12) | Broader: all 85,493 employer firms |
|---|---|---|
| $49/mo | 14,960 × $588 = **$8.8M** | $50.3M |
| $99/mo | 14,960 × $1,188 = **$17.8M** | $101.6M |
| $149/mo | 14,960 × $1,788 = **$26.7M** | $152.9M |

**SOM (3-year, assumption):** 1–2% of reachable ICP = **150–300 customers**, or **$178K–$355K ARR** at $99. There's upside from 34,900 solo CPAs and 870,679 individual PTIN holders on a cheaper tier. That's not counted here.

### 3b. US dental practices (independent)

| Step | Value | Label / Source |
|---|---|---|
| Dental office establishments (NAICS 621210) | 135,665 | Fact: Census CBP 2023 via [search summary / Census profile](https://data.census.gov/profile/621210_-_Offices_of_dentists?n=621210) (2023 data, borderline **stale**) |
| Exclude DSO-affiliated | × (1 − 0.161) | Fact: 16.1% of dentists DSO-affiliated, 2024 ([ADA HPI](https://www.ada.org/resources/research/health-policy-institute/dental-practice-research/practice-modalities-among-us-dentists)). **Assumption:** the dentist share works as a proxy for the establishment share |
| Share with 5–49 employees | 70% | **Assumption.** A typical office has a dentist plus hygienists, assistants and front desk. CBP size-class table not retrieved (blocked) |
| **ICP practices** | 135,665 × 0.839 × 0.70 = **≈79,700** | Calculation |
| % reachable | 60% | **Assumption** |
| **Reachable ICP practices** | **≈47,800** | Calculation |

| Price | SAM | Broader: all 135,665 establishments |
|---|---|---|
| $49/mo | 47,800 × $588 = **$28.1M** | $79.8M |
| $99/mo | 47,800 × $1,188 = **$56.8M** | $161.2M |
| $149/mo | 47,800 × $1,788 = **$85.5M** | $242.6M |

**SOM (3-year, assumption):** 1–2% = **480–960 practices**, or **$568K–$1.14M ARR** at $99.

**Inference:** dental's SAM is about 3× larger, but it's more crowded and has no single hard deadline like PTIN renewal. Accounting is the better *first* market (faster proof, 3 customers by day 90). Dental is the better *second* market for scale.

---

## 4. Why now (2024–2026 evidence)

| Trend | Evidence | Label |
|---|---|---|
| SMBs are hit hardest by ransomware | Ransomware was in 88% of SMB breaches vs 39% at large enterprises. Median ransom was $115K ([Verizon DBIR 2025](https://www.verizon.com/about/news/2025-data-breach-investigations-report); [SMB snapshot](https://www.verizon.com/business/resources/infographics/2025-dbir-smb-snapshot.pdf)) | Fact, 2025 |
| Ransomware and human error are rising | Ransomware was in 48% of breaches (up from 44%), and the human element in 62% ([Verizon DBIR 2026 via Help Net Security](https://www.helpnetsecurity.com/2026/05/25/lessons-from-verizon-dbir-2026-findings/); [Abnormal](https://abnormal.ai/blog/blog-verizon-2026-dbir-key-takeaways)) | Fact, 2026 |
| SMB attack prevalence | 43% of 800 US SMBs attacked in the past 5 years. 27% have no cyber insurance. 16% spend under $50 per user per year ([Guardz 2025 report](https://www.prnewswire.com/news-releases/guardz-2025-smb-cybersecurity-report--nearly-50-of-us-small-businesses-have-been-hit-by-cyber-attack-302644681.html)) | Fact (vendor survey), 2025 |
| AI-driven phishing | AI-assisted phishing reported at 82.6% of detected phishing emails, up 53.5% YoY (Sept 2024–Feb 2025) ([StationX, 2026](https://app.stationx.net/articles/phishing-statistics)). Microsoft saw an IRS-themed phishing wave hit 29,000 users at 10,000 orgs in Feb 2026, aimed at accountants and tax preparers ([ERP Today, 2026](https://erp.today/tax-season-scams-2026-irs-impersonation-ai-fraud-businesses/)) | Fact (secondary sources, check primary) |
| Cyber insurance now requires controls | Insurers treat MFA as non-negotiable. Coalition found 82% of claimants lacked MFA ([Coalition 2024 via Clark Hill/Petronella](https://petronellatech.com/blog/cybersecurity-law-firms-compliance/)). Carriers expect EDR and documented proof ([Todyl, 2026](https://www.todyl.com/blog/how-cyber-insurance-requirements-are-changing)). Only 40% of law firms carry cyber insurance ([ABA 2025 via Rev](https://www.rev.com/blog/cybersecurity-for-law-firms)) | Fact (secondary), 2024–2026. The 41% first-submission denial rate on [beancount.io](https://beancount.io/blog/2026/05/09/cyber-insurance-small-business-2026-mfa-requirements-ransomware-coverage-premium-benchmarks) is unverified, so don't quote it |
| Regulation: tax and accounting | FTC Safeguards breach notice in force since May 2024. WISP certification on PTIN renewal (Form W-12) ([Bellator, 2026](https://bellatorcyber.com/blog/irs-publication-5708-sample-wisp); [IRS](https://www.irs.gov/newsroom/tax-professional-tips-for-creating-a-data-security-plan)). Firms with fewer than 5,000 consumers are exempt only from the written risk assessment, pen testing, IR plan and board report. MFA, encryption, monitoring and training still apply ([FTC §314.6 via Flamingo](https://www.flamingo.run/blog/ftc-safeguards-rule-checklist)) | Fact |
| Regulation: healthcare | HIPAA Security Rule NPRM (6 Jan 2025) would require MFA and encryption. **Still not final as of Aug 2026. OMB target is July 2027** ([Medcurity, 2026](https://medcurity.com/hipaa-security-rule-2026/)) | Fact |
| Regulation: e-commerce | PCI DSS 4.0.1 future-dated requirements became mandatory 31 Mar 2025 ([Feroot](https://www.feroot.com/blog/pci-4-0-1-has-arrived/)) | Fact |
| Regulation: South Asia | India DPDP Rules phased in Nov 2025 → May 2027. Nepal NRB Cyber Resilience Guidelines 2023 | Fact |

**Caution on our own docs.** `01-problem-statement.md` cites "43% of attacks target SMBs" and "60% of SMBs close within 6 months". I couldn't find a current primary source for either. The 43% figure traces to older DBIR editions (**stale**). Replace both with the 2025/2026 DBIR figures above before external use.

---

## 5. Buying triggers and where to find buyers

### Accounting / tax (segment #1)
- **Triggers:**
  - PTIN renewal window (mid-Oct to 31 Dec), when the preparer certifies a WISP on Form W-12
  - Post-tax-season (May–Sept), when there's time for projects
  - IRS "Dirty Dozen" and Security Summit warnings
  - A peer's breach
  - Cyber-insurance renewal
- **Directories:**
  - IRS Directory of Federal Tax Return Preparers with Credentials and Select Qualifications (public, searchable)
  - State CPA society "Find a CPA" pages
  - AICPA PCPS member firms
  - NAEA (enrolled agents) and NATP member directories
- **Communities:** r/taxpros, r/accounting, r/Bookkeeping, LinkedIn "Managing Partner" + "CPA firm" at 2–50 employees
- **Events:** IRS Nationwide Tax Forums (summer), state CPA society CPE sessions, local chamber events
- **Partners:**
  - Tax/practice software ecosystems (Drake, Intuit ProConnect, TaxDome, Canopy): verify partner programs
  - Cyber-insurance brokers
  - Bookkeeper networks

### Dental (segment #2)
- **Triggers:** HIPAA risk assessment due, cyber-insurance renewal, a local dental breach, adding a second location, moving to cloud practice management
- **Directories:** ADA Find-a-Dentist, state dental associations, Google Maps "dentist"
- **Communities:** Dentaltown, r/Dentistry, dental study clubs, practice-manager Facebook groups
- **Events:** state dental meetings, Chicago Midwinter, ADA SmileCon
- **Partners:** Dentrix/Henry Schein, Open Dental and Eaglesoft ecosystems; dental IT MSPs (as resellers, not rivals)

---

## 6. Risks and what would change the verdict

1. **Unverified numbers.** Egress blocked all government sources, so the business counts are second-hand and the 5–49 employee splits are assumptions. If CBP size-class data shows fewer than 15% of CPA firms have 5+ employees, accounting SAM drops below $5M at $99, and dental becomes #1.
2. **Compliance vs. security product fit.** Accounting buyers pay for *proof of compliance* (WISP, MFA evidence, monitoring log). If ChimeraShield's MVP is only a phishing analyzer and domain scan, it won't meet the "must-have" bar. We may need a WISP generator and evidence report in v0.1.
3. **Seasonality and enforcement reality.** Tax firms go dark Jan–Apr. FTC enforcement against *small* tax firms appears rare (Inference: the vendor blogs claiming "active enforcement" had no named cases). If interviews show owners treat the WISP as a $29 checkbox, willingness to pay falls to 2–3 and law or dental moves ahead.
4. **Incumbent MSPs.** Many 10–50 person firms already have an MSP. If most interviewees say "my IT guy handles it", pivot to selling *through* those MSPs.
5. **HIPAA rule delay.** Dental urgency depends partly on a rule now targeted for July 2027. If it's finalized earlier, dental's urgency jumps.
6. **Founder access** (scored 3 everywhere) could reshuffle the close scores between #2 and #3.

---

## 7. Top 3 implications for ChimeraShield

1. **Lead with "Safeguards Rule + WISP ready, in plain English", not "AI security".** Build the first offer around what an accounting firm must prove: MFA on, encryption on, monitoring running, staff phishing-tested, WISP current. Add a one-page evidence report they can hand to the IRS, the FTC or their insurer.
2. **Time the go-to-market to the calendar.** Interviews now (late Sept). Founding-member offer launched before the PTIN renewal window (mid-Oct to 31 Dec 2026). Avoid Jan–Apr for new sales; use that time for product.
3. **Pricing at $99/month fits the market.** It sits between $29–$999 WISP templates and managed MSP services charged per user ([Bellator, 2026](https://bellatorcyber.com/blog/cybersecurity-provider-for-tax-practice)). Keep $49 for founding members and solo preparers. Keep dental as the expansion segment with a HIPAA-flavored version of the same evidence report.

---

## 8. Questions to validate in customer interviews

1. When you renewed your PTIN last year and certified a WISP on the W-12, what did you actually have? Who wrote it, and when was it last updated?
2. Has your cyber insurer or a client ever asked for proof of MFA, EDR or a security plan? What did you send them?
3. Has your firm had a phishing email, account takeover or suspicious IRS/e-Services notice in the last 12 months? What did it cost in time or money?
4. Who handles IT and security today (you, a staff member, an MSP)? What do you pay per month?
5. If a breach hit 500+ clients, do you know you'd have 30 days to notify the FTC? What would you do first?
6. What would make you switch or add a tool between May and December, and who else would need to approve it?
7. (Dental variant) When was your last HIPAA risk assessment, who did it, and what did it cost?

---

## 9. Sources

All accessed via web search on 2026-09-24. Pages were **not** opened directly (fetch blocked), so treat summaries as needing verification.

- Verizon, 2025 DBIR news release (2025): https://www.verizon.com/about/news/2025-data-breach-investigations-report
- Verizon, 2025 DBIR SMB snapshot (2025): https://www.verizon.com/business/resources/infographics/2025-dbir-smb-snapshot.pdf
- Help Net Security, Verizon DBIR 2026 lessons (2026): https://www.helpnetsecurity.com/2026/05/25/lessons-from-verizon-dbir-2026-findings/
- Abnormal AI, 2026 DBIR takeaways (2026): https://abnormal.ai/blog/blog-verizon-2026-dbir-key-takeaways
- FTC, Safeguards Rule business guidance: https://www.ftc.gov/business-guidance/resources/ftc-safeguards-rule-what-your-business-needs-know
- Venable, Safeguards breach notice (2023): https://www.venable.com/insights/publications/2023/11/data-breach-notice-requirement-added
- Flamingo, FTC Safeguards checklist / §314.6 exemption (2025–26): https://www.flamingo.run/blog/ftc-safeguards-rule-checklist
- IRS, tips for a data security plan (WISP): https://www.irs.gov/newsroom/tax-professional-tips-for-creating-a-data-security-plan
- IRS, Return Preparer Office statistics (PTIN counts, 2025–26): https://www.irs.gov/node/3635
- Bellator Cyber, IRS Pub 5708 WISP guide (2026): https://bellatorcyber.com/blog/irs-publication-5708-sample-wisp
- Bellator Cyber, cybersecurity provider costs for tax practices (2026): https://bellatorcyber.com/blog/cybersecurity-provider-for-tax-practice
- writtensecurityplan.com, WISP template pricing (2026): https://www.writtensecurityplan.com/
- Carry, IRS 2025 Security Summit recap (2025): https://carry.com/news/irs-wraps-2025-security-summit-tax-identity-theft
- ERP Today, tax season scams 2026 (2026): https://erp.today/tax-season-scams-2026-irs-impersonation-ai-fraud-businesses/
- CPA Trendlines Almanac (2024): https://cpatrendlines.com/2024/01/01/cornerstone-cpa-trendlines-almanac-key-data-points-for-the-tax-accounting-and-finance-profession/
- ipassthecpaexam, CPA statistics (year unclear): https://ipassthecpaexam.com/number-of-cpa/
- naicslist, NAICS 541213 (2020 data, **stale**): https://naicslist.com/naics/541213
- Census, NAICS 621210 profile (CBP 2023): https://data.census.gov/profile/621210_-_Offices_of_dentists?n=621210
- Census, NAICS 541110 profile (CBP 2023): https://data.census.gov/profile/541110_-_Offices_of_Lawyers?n=541110
- ADA HPI, practice modalities (2024): https://www.ada.org/resources/research/health-policy-institute/dental-practice-research/practice-modalities-among-us-dentists
- HIPAA Journal, 2025 healthcare data breach report (2025–26): https://www.hipaajournal.com/2025-healthcare-data-breach-report/
- Becker's Dental Review, 15 dental breaches in 2025 (2025): https://www.beckersdental.com/dentists/15-data-breaches-that-impacted-dentistry-in-2025/
- Medcurity, HIPAA Security Rule 2026 status (2026): https://medcurity.com/hipaa-security-rule-2026/
- AMA, private practice share (2024 data): https://www.ama-assn.org/practice-management/private-practices/smaller-share-doctors-private-practice-ever
- ABA, 2024 Solo & Small Firm TechReport (2024): https://www.americanbar.org/groups/law_practice/resources/tech-report/2024/2024-solo-and-small-firm-techreport/
- ABA, 2023 Cybersecurity TechReport (2023, **stale**): https://www.americanbar.org/groups/law_practice/resources/tech-report/2023/2023-cybersecurity-techreport/
- Rev, cybersecurity for law firms (ABA 2025 figures): https://www.rev.com/blog/cybersecurity-for-law-firms
- Petronella Tech, law firm compliance / Coalition 2024 MFA stat: https://petronellatech.com/blog/cybersecurity-law-firms-compliance/
- Todyl, cyber insurance requirements (2026): https://www.todyl.com/blog/how-cyber-insurance-requirements-are-changing
- Guardz 2025 SMB Cybersecurity Report (2025): https://www.prnewswire.com/news-releases/guardz-2025-smb-cybersecurity-report--nearly-50-of-us-small-businesses-have-been-hit-by-cyber-attack-302644681.html
- StationX, phishing statistics (2026): https://app.stationx.net/articles/phishing-statistics
- PCI SSC blog, e-commerce requirements after 31 Mar 2025 (2025): https://blog.pcisecuritystandards.org/coffee-with-the-council-podcast-guidance-for-pci-dss-e-commerce-requirements-effective-after-31-march-2025
- Feroot, PCI DSS 4.0.1 (2024–25): https://www.feroot.com/blog/pci-4-0-1-has-arrived/
- Clearly Payments, US online stores (2025): https://www.clearlypayments.com/blog/how-many-online-stores-are-in-the-usa-in-2025/
- Infrascale, MSP statistics USA (2025, vendor estimate): https://www.infrascale.com/msp-statistics-usa/
- MDRCost, Huntress pricing (2026): https://mdrcost.com/huntress-pricing
- Capterra, Coro pricing (2026): https://www.capterra.com/p/182368/Coronet/pricing/
- Guardz pricing: https://guardz.com/pricing/
- ICTFrame, NRB Cyber Resilience Guidelines: https://ictframe.com/nrbs-cyber-resilience-guidelines/
- ICTFrame, Nepal cybersecurity crisis (2025): https://ictframe.com/nepals-cybersecurity-crisis-2025/
- Kathmandu Post, Nepal cooperatives count (2025): https://kathmandupost.com/province-no-3/2025/01/22/bagmati-province-has-highest-number-of-cooperatives-but-no-dedicated-monitoring-body
- India Briefing, DPDP Rules 2025 (2025): https://www.india-briefing.com/news/dpdp-rules-2025-india-data-protection-law-compliance-40769.html/
- BW Businessworld, Indian SMEs cyber incidents (2025): https://www.businessworld.in/article/survey-reveals-nearly-half-of-indian-smes-faced-cyber-incidents-in-2025-608641
