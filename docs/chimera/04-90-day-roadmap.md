# 90-Day Execution Roadmap — ChimeraShield

## North Star Metric
**Goal by Day 90:** 3 paying customers at any price point.
(Revenue is secondary. Validation is everything at this stage.)

---

## Phase 1: Validation (Days 1–30)
**Goal:** Confirm people will pay before you build anything.

### Week 1–2: Customer Discovery
- [ ] Complete 10 customer conversations (use The Mom Test framework)
  - Target: SMB owners in healthcare, legal, or finance
  - Ask about their current security situation, not about your product
  - Record the exact words they use to describe the pain
- [ ] Build a simple "Problem Scorecard": rate each interview on pain intensity (1–10)
- [ ] Identify your top 3 most painful customer segments

### Week 3–4: Offer Design
- [ ] Define your first offer using the $100M Offers framework:
  - **Dream outcome:** "Never worry about a cyber breach again"
  - **Perceived likelihood:** Show real AI catching real threats
  - **Time to value:** First scan results in under 5 minutes
  - **Effort/sacrifice:** No IT team needed, no complex setup
- [ ] Create a 1-page landing page (can use Carrd or Framer — no-code)
- [ ] Write 3 cold outreach messages for LinkedIn/email
- [ ] Target: 50 outreach messages sent, 5 demo calls booked

---

## Phase 2: MVP Build (Days 31–60)
**Goal:** Build the minimum product that delivers the core promise.

### Core MVP Features (v0.1)
- [ ] **AI Phishing Email Analyzer** — paste an email, get a risk score + explanation
- [ ] **Basic Vulnerability Scanner** — scan a domain for common exposed issues
- [ ] **Plain-English Risk Report** — weekly summary of findings, human-readable
- [ ] **Simple Dashboard** — last scan date, risk score, top 3 actions to take

### Technical Stack
- Frontend: Next.js (already scaffolded)
- Backend: FastAPI (already scaffolded)
- AI: Claude API (Anthropic) or OpenAI GPT-4
- Auth: Clerk or Supabase Auth
- Payments: Stripe

### Done When
- A non-technical SMB owner can sign up, run a scan, and understand the results in under 10 minutes

---

## Phase 3: First Revenue (Days 61–90)
**Goal:** Convert demo calls into paying customers.

### Sales Process
- [ ] Offer a "Founding Member" deal: $49/month (lifetime) to first 10 customers
- [ ] Do white-glove onboarding — get on a call, walk them through setup
- [ ] Collect testimonials and case studies from first customers
- [ ] Ask every customer: "Who else do you know who needs this?" (referral loop)

### Marketing Channels to Test (pick 1–2 max)
- LinkedIn content: Post 3x/week about AI threats hitting SMBs (educate, don't sell)
- Cold email: 20 targeted SMB owners/day in your ICP vertical
- Reddit: Answer security questions in r/smallbusiness, r/legaladvice — add value first

### Success Metrics by Day 90
| Metric | Target |
|--------|--------|
| Customer interviews completed | 15+ |
| Demo calls held | 10+ |
| Paying customers | 3+ |
| MRR | $150+ |
| NPS from early users | 7+ |

---

## The Golden Rule for This Phase
> **Talk to customers before writing code. Sell before you build. Validate before you scale.**

The biggest mistake at the idea stage is spending 3 months building something no one wants. Your job in the next 30 days is NOT to build — it's to find 3 people who say "yes, I would pay for that."
