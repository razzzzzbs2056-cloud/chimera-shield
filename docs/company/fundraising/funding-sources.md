# Funding Sources: Credits, Accelerators, Security Investors, Non-US Options

**Owner:** fundraising-advisor · **Researched:** 2026-09-24 · **Status:** research draft
**Pair with:** `verdict.md` (bootstrap now; revisit Jan–Apr 2027)

> **Evidence note.** Web search worked; direct page fetches were blocked for most domains (ycombinator.com, technext24.com and others). One primary page was fetched directly: **claude.com/programs/startups** (2026-09-24). Everything else comes from search-result summaries and is labeled:
> - **Verified** = read on the official page today.
> - **3P** = reported by a third-party site or an official page seen only as a search snippet. **Check the official page before relying on it.**
> - **Unverified** = inferred, conflicting, or not found. Treat as a lead only.
>
> Programs change terms often. Re-check every deadline the week you apply.

**Our actual stack** (`engineering/adr-001-mvp-architecture.md`): Render + Supabase + Resend + Anthropic API + Stripe. Pre-revenue running cost is **under $10/mo plus LLM testing**. So big-cloud credits (AWS, Google, Azure) are worth little unless we move hosting. Don't re-architect to chase credits.

---

## 0. Priority list (what to do and when)

| Priority | Source | When | Why |
|---|---|---|---|
| **1. Now** | **Your own cash + customer revenue** (founding packs) | Oct–Dec 2026 | Peak need $1.1k base / $3.5k conservative. This is the funding plan. |
| **2. Now (1 hour, after the website and company email exist)** | **Cloud credits you'd actually use:** Cloudflare for Startups bootstrapped tier; optionally AWS Activate Founders or Google Cloud "Start" tier | Rolling | Small but free. Most need a live website and a matching company email domain. |
| **3. Optional, 2 Nov 2026** | **YC Winter 2027** | On-time deadline **2 Nov 2026, 8pm PT** (3P) | Batch runs Jan–Mar 2027, during the tax-season sales freeze. Low odds pre-traction. Only if legally able to accept a US SAFE. Cap at 4 h. |
| **Conditional (Nepal-resident)** | **IEDI Startup Enterprise Loan** (Nepal) | Next call unverified | Up to NPR 20 lakh at 3%, collateral-free (3P). Roughly covers the $12.9k salary gap without dilution or outward-investment issues. Needs a Nepal-registered startup. |
| **Jan–Apr 2027** | YC Spring/Summer 2027, security angels, RSAC Launch Pad (if milestones in `verdict.md` §4 are met) | See §2–3 | Apply with a full Q4 of real data. |
| **Skip this cycle** | Techstars Spring 2027 (closes 18 Nov 2026), CrowdStrike/AWS/NVIDIA accelerator, Antler | — | Wrong timing or eligibility; see below. |

---

## 1. Startup credit programs (cloud and AI API)

| Program | What you get | Eligibility (key points) | Deadline | Fit for us | Link | Status |
|---|---|---|---|---|---|---|
| **Anthropic: Claude for Startups** | Free API credits + priority rate limits (amounts not listed on the page; 3P reports $5k–$100k) | **Credits require equity funding from an institutional investor**, founded within 4 years, no prior Anthropic credits. Bootstrapped founders can join the community (events, Claude Academy) but **don't get credits**. Credits are for the first-party API only, not Bedrock/Vertex. | Rolling | **Not eligible now.** Becomes available after any accelerator or institutional SAFE. Our LLM spend is ~$20–60 for 90 days anyway (`90-day-budget.md`). | [claude.com/programs/startups](https://claude.com/programs/startups) | **Verified** (fetched 2026-09-24) |
| **Cloudflare for Startups** | Bootstrapped tier reported at **$5k** (some sources say $10k); up to $250k–$350k for funded startups; 12-month expiry | Software product, founded ≤5 years, valid matching company email | Rolling | Medium. Useful if we put DNS, the landing page or email routing on Cloudflare (ADR lists Cloudflare Email Routing as an alternative). | [cloudflare.com/startups](https://www.cloudflare.com/startups/) | 3P ([Credit for Startups](https://creditforstartups.com/companies/cloudflare)) |
| **AWS Activate Founders** | **$1,000**, some qualify for up to $5,000 | Self-funded, no VC/accelerator affiliation, <10 staff, <$1M revenue/funding, working website, **AWS account on the Paid plan** | Rolling | Low. Not in our stack. Only if we host there. | [aws.amazon.com/activate](https://aws.amazon.com/activate) | 3P ([Pace Wisdom](https://pacewisdom.com/blog/eligibility-criteria-for-startups-in-aws-activate), [Northflank](https://northflank.com/blog/how-to-get-free-aws-credits-for-your-startup)) |
| **Google for Startups Cloud: "Start" tier (pre-funded)** | **$2,000** Google Cloud credits, 12 months | Tech startup not yet funded by an institutional investor, founded ≤5 years, no prior Google Cloud credits beyond the free trial | Rolling | Low. Not in our stack. | [cloud.google.com/startup/pre-funded](https://cloud.google.com/startup/pre-funded) | 3P ([Google Cloud page via search](https://cloud.google.com/startup/pre-funded), [CloudKompas](https://cloudkompas.com/blog/google-cloud-for-startups-2026-credits-guide)) |
| **Microsoft for Startups** (formerly Founders Hub) | Without an investor: **$1,000 Azure for 90 days, then $4,000 for 180 days** after verification. With a partner referral: ~$100k. Covers OpenAI models on Azure, **not Claude**. | New to Azure; business verification | Rolling | Low. Not in our stack. | [startups.microsoft.com](https://startups.microsoft.com) | 3P ([CloudKompas](https://cloudkompas.com/blog/microsoft-for-startups-2026), [SquareOps](https://squareops.com/blog/why-startups-are-looking-for-azure-credits-in-2026/)) |
| Render / Supabase / Resend startup perks | Unknown | Unknown | — | High fit if they exist | — | **Unverified.** Not researched; check each vendor's site. |

**Rule:** apply only to programs for tools already in the ADR. Credits expire in 12 months, and we won't use $2k of GCP.

---

## 2. Accelerators (pre-revenue, solo founders, current deadlines after Sep 2026)

| Program | Terms | Solo / pre-revenue / non-US? | Next deadline | Fit and advice | Link | Status |
|---|---|---|---|---|---|---|
| **Y Combinator, Winter 2027** | **$500k**: $125k for 7% + $375k uncapped MFN SAFE (unchanged since 2022, 3P) | Solo founders accepted on the same terms, but held to a higher bar; ~10% of YC companies are solo-founded (3P). Idea-stage applications accepted. Global founders accepted; batch is in San Francisco. | **On-time: 2 Nov 2026, 8pm PT**; decisions by 11 Dec 2026. Late applications reviewed without a promised date. Batch **Jan–Mar 2027**. | **Optional, low odds.** Timing fits our dead season. Apply only if you can legally hold US shares. Cap at 4 h. | [ycombinator.com/apply](https://www.ycombinator.com/apply) | 3P ([Round Funded](https://www.roundfunded.com/en/blogs/yc-batches-2026-dates-acceptance-rate), [YC Roaster](https://www.ycroaster.com/tools/yc-application-deadline), [Zyner on solo founders](https://zyner.io/blog/yc-solo-founders)). ycombinator.com blocked from this session. |
| **Y Combinator, Spring 2027** | Same deal | Same | **Not announced.** Projected ~Feb 2027 based on past pattern | **Best realistic YC target** if `verdict.md` §4-B/C milestones are met by Feb. | [ycombinator.com/apply](https://www.ycombinator.com/apply) | **Unverified** ([Round Funded](https://www.roundfunded.com/en/blogs/yc-application-deadlines-2026-2027)) |
| **Techstars, Spring 2027 programs** | **$220k**: $200k uncapped MFN SAFE + $20k for 5% via a Convertible Equity Agreement (terms since fall 2025) | Multiple city and vertical programs, each with its own focus; there's also Techstars Anywhere (remote) | Applications opened 24 Aug 2026, **close 18 Nov 2026**. Programs start **8 Mar 2027**, Demo Day 3 Jun 2027 (3P) | **Skip this cycle.** The program runs Mar–Jun, which overlaps the end of tax season and the May sales window, and we'd have only ~5 weeks of sales data at the deadline. Target a Fall 2027 program if §4-C is met. | [techstars.com/investment-terms](https://www.techstars.com/investment-terms), [Techstars Anywhere](https://www.techstars.com/accelerators/anywhere) | 3P ([TechCrunch 2025 on terms](https://techcrunch.com/2025/04/18/techstars-increases-startup-funding-to-220000-mirroring-yc-structure/), [Innovation Village](https://innovation-village.com/techstars-opens-spring-2027-applications-with-220k/)) |
| **Antler** (residencies) | Singapore: up to $400k, starting with a $150k ticket after 6 weeks (3P). India: INR 2 crore for 9% (3P). | Open to solo and pre-idea founders. In-person residency. | Singapore residency starts **5 Oct 2026** (3P). India dates vary. | **Poor fit.** Antler is designed for team formation and VC-scale ideas; we already have a direction and a solo founder. For a Nepal-resident founder, the outward-investment question applies to Singapore/India entities too. | [antler.co/location/singapore](https://www.antler.co/location/singapore) | 3P |
| **Founder Institute (Nepal chapter)** | Pre-seed program; typically equity pool + fee (terms not checked) | Idea-stage, part-time, local | **Unverified** | Low-medium. Network and structure, not money. Check the fee and equity terms before joining. | [fi.co](https://fi.co/), [Founder Institute Nepal (LinkedIn)](https://www.linkedin.com/company/finepal) | **Unverified** |

---

## 3. Cybersecurity-focused programs, funds and angels

| Source | What it is | Stage / cheque | Deadline | Fit and advice | Link | Status |
|---|---|---|---|---|---|---|
| **RSAC Launch Pad** | 5-minute pitch to a VC panel at RSAC Conference (San Francisco) | Early-stage | RSAC opened Innovation Sandbox and Launch Pad submissions on **14 October** in a recent year (likely 2025, for RSAC 2026). The 2027 date is **not confirmed**. | Medium, **later**. Visibility with security VCs. Worth it only with the §4-C milestones. Check in mid-October. | [RSAC Innovation Sandbox](https://www.rsaconference.com/rsac-programs/innovation/innovation-sandbox), [press release](https://www.rsaconference.com/library/press-release/rsac-conference-open-annual-isb-and-lp-contest) | **Unverified** for 2027 |
| **RSAC Innovation Sandbox** | Top-10 finalist contest | Usually post-seed, product-led | As above | **Not a fit.** Finalists are funded, product-heavy companies. | same | Unverified |
| **CrowdStrike / AWS / NVIDIA Cybersecurity Startup Accelerator** | Free 8-week program; winner eligible for Falcon Fund investment | Pre-Series A. **Requires a full-time technical lead, a working MVP and demonstrable traction.** Focus areas: cloud, identity, AppSec, GenAI in security, data security, SecOps. | 2026 cohort applications closed **15 Nov 2025**. The 2027 cohort is **not announced**; the pattern suggests Oct–Nov 2026. | **Skip 2027.** We won't have an MVP or traction by then, and our wedge (owner-facing compliance evidence) is outside their categories. | [AWS program page](https://aws.amazon.com/startups/programs/aws-and-crowdstrike-cybersecurity-accelerator), [CrowdStrike press](https://www.crowdstrike.com/en-us/press-releases/crowdstrike-aws-nvidia-2026-cybersecurity-startup-accelerator/) | 3P; 2027 **unverified** |
| **CyberForge Accelerator** | Reported: Cohort 4 opening Sep 2026, $150k, 16 weeks | Unknown | Reported Sep 2026 | **Treat as a lead only.** The domain did not resolve when fetched on 2026-09-24. Verify it exists before spending time. | [cyberforgeaccelerator.com/apply](https://cyberforgeaccelerator.com/apply) | **Unverified** (listed on [IncubatorList](https://incubatorlist.com/best-cybersecurity-startup-accelerators-incubators-and-vcs)) |
| **Tech4Trust (Switzerland)** | 6-month digital-trust/cyber program | Early-stage | "Applications close by 26 February" (year unclear) | Low. Swiss-focused. | via [IncubatorList](https://incubatorlist.com/best-cybersecurity-startup-accelerators-incubators-and-vcs) | Unverified |
| **UK CyberASAP** | Academic cyber startup programme | **Academic teams only** | Y10 in progress | **Not eligible.** Listed so nobody wastes time on it. | [IUK Business Connect](https://iuk-business-connect.org.uk/opportunities/cyber-security-academic-startup-accelerator-programme-year-10-phase-1/) | 3P |
| **Silicon Valley CISO Investments (SVCI)** | Angel syndicate of 60+ CISOs | Asks startups to allocate **≥$350k** to SVCI (3P). Portfolio is mostly enterprise security (Drata, Island, Tines). | Rolling | **Later, and only if the story goes upmarket.** Valuable as advisors/validators; our buyer isn't a CISO. | [svci.io](https://www.svci.io/), [FAQ](https://www.svci.io/faq) | 3P |
| **Cyber Mentor Fund** | Security-founder-led seed fund | Pre-seed to Series B; min ~$100k, sweet spot ~$1.5M (3P) | Rolling | Later (§4-C). Focus areas skew enterprise/industrial. | [cybermentorfund.com](https://cybermentorfund.com/) | 3P ([OpenVC](https://www.openvc.app/fund/Cyber%20Mentor%20Fund)) |
| **Angels from the accounting world** (practice-management/tax-software operators, CPA-firm owners, cyber-insurance brokers) | Individual angels | $5k–$50k typical (assumption) | — | **Best-fit angels for this wedge**, better than security VCs: they understand the buyer and can open distribution. Build these relationships through the monthly update, not a pitch. | — | Assumption |

---

## 4. Non-dilutive grants and loans

| Source | What | Eligibility | Deadline | Fit | Link | Status |
|---|---|---|---|---|---|---|
| **US SBIR/STTR ("America's Seed Fund")** | Federal R&D grants | Company must be **≥51% owned by US citizens or permanent residents** | Agency-specific | **Poor fit** even for a US founder: SBIR funds R&D with technical risk, and ours is go-to-market risk. **Not available** to a Nepal-owned company. | [SBIR eligibility tutorial](https://www.sbir.gov/tutorials/program-basics/tutorial-2) | 3P (official page via search) |
| **Emergent Ventures** (Mercatus Center) | Fast, small grants to individuals/projects; 3P reports typical $1k–$50k | Global; "bold, scalable ideas for improving society" | **Rolling** | **Long shot.** A commercial compliance service isn't their usual profile. Only worth it if you frame a public-good component (e.g., free open WISP guidance for small tax preparers). | [Application form](https://mercatus.tfaforms.net/5099527) | 3P |

---

## 5. Options for a non-US founder (including Nepal)

**First, the blocker.** Per `legal/entity-options.md`, a Nepal-resident Nepali citizen may need a government exemption to own shares in a foreign company (Act Restricting Investment Abroad, 1964; the 2025 FERA §10A route opens outward investment for **Nepali IT companies**, not clearly for individuals). That affects **every US accelerator and SAFE above**. Get a written opinion from a Nepali corporate/FX lawyer **before** any application where acceptance means taking US equity money. (FLAG from legal-ops; not legal advice.)

### Nepal-specific programs

| Program | What | Eligibility / notes | Deadline | Link | Status |
|---|---|---|---|---|---|
| **Startup Enterprise Loan (IEDI, Ministry of Industry, Commerce and Supplies)** | **Collateral-free loan up to NPR 20 lakh at 3%/yr** (roughly USD 15k at an assumed ~135 NPR/USD; check the rate) | Nepal-registered startup; IT is an eligible sector and IT applicants now lead the program. A Jan 2026 ministry release said the scheme would be "recalibrated" with an NPR 500M envelope; details not yet in the Gazette (3P). | FY 2082/83 round **closed**; next call **unverified** | [application.startupnepal.gov.np](https://application.startupnepal.gov.np/), [iedi.gov.np](https://iedi.gov.np) | 3P ([Nepal Database](https://www.nepaldatabase.com/nepal-startup-funding-in-2026-whats-verified-whats-pending-and-where-founders-should-look), [Entrepreneur Loop](https://entrepreneurloop.com/nepal-it-startup-loan-applications-2025/)) |
| **US Embassy Nepal entrepreneurship programs** | The embassy ran a **Capstone Accelerator** (20 founders, concluded Aug 2026) and issued a NOFO for an implementer of a **"U.S.-Linked Entrepreneurship Accelerator and Innovation Challenge Program"** ($10k–$50k award to the *implementer*, deadline 11 Jun 2026, project start ~1 Oct 2026) | The NOFO funds an organization, not founders. A founder call from the chosen implementer **may** follow in FY27. Its stated aim (US–Nepal commercial ties) fits a Nepal founder selling to US firms. | Watch for a founder call from Oct 2026 (**unverified**) | [NOFO PDF](https://np.usembassy.gov/wp-content/uploads/sites/27/2026/05/NOFO-Nepal-U.S.-Linked-Entrepreneurship-Accelerator-Program-1.pdf), [Embassy grants page](https://np.usembassy.gov/contract-grant-opportunities/), [OnlineKhabar on Capstone](https://english.onlinekhabar.com/us-embassy-capstone-accelerator.html) | 3P |
| **Idea Studio Nepal** | Incubator/accelerator, Lalitpur | Reported 180 ideas incubated, 68 startups running | **Unverified** | via [IncubatorList Nepal](https://incubatorlist.com/top-startup-accelerators-incubators-and-vcs-in-nepal) | Unverified |
| **Founder Institute Nepal** | See §2 | — | Unverified | [LinkedIn](https://www.linkedin.com/company/finepal) | Unverified |
| **Nepal IT-export tax incentives** | Not funding, but material: reported 5% final tax on individual IT-export income up to NPR 4M, and company-level export rebates (sources conflict) | Needs a Nepali tax advisor | — | See `legal/entity-options.md` | FLAG |

### Other non-US founder notes
- **Stripe Atlas / US C-corp from abroad:** possible in principle, but for Nepal residents banking is the first wall (Mercury lists Nepal as prohibited) and Stripe's position is unclear (`entity-options.md`).
- **India/Singapore programs** (Antler, Google for Startups Accelerator India) raise the same outward-investment question for a Nepal resident and are built for local companies.
- **Remote-friendly options that don't need equity:** credits (§1), Emergent Ventures (§4), and customer revenue.

---

## 6. Calendar (all dates to re-check)

| Date | Item | Action |
|---|---|---|
| ~Oct 2026 (after domain + site live) | Cloudflare / other credits in our stack | Apply (1 h) |
| mid-Oct 2026 | RSAC 2027 Launch Pad / Sandbox submissions may open (unverified) | Note the deadline; don't apply yet |
| **2 Nov 2026, 8pm PT** | YC W27 on-time deadline (3P) | Optional, conditions in `verdict.md` §1 |
| 18 Nov 2026 | Techstars Spring 2027 closes (3P) | Skip |
| 11 Dec 2026 | YC W27 decisions (3P) | — |
| 15 Dec 2026 | Traction checkpoint | Fill slide 9B, pick path A/B/C |
| ~Feb 2027 | YC Spring 2027 deadline (projected, unverified) | Apply if §4-B/C met |
| Unverified | IEDI Startup Enterprise Loan next call (Nepal) | Monitor monthly |
