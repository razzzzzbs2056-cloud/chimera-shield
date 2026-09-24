# ChimeraShield AI Company Team

A virtual startup team built from Claude Code sub-agents. Each agent owns one function of the company, reads the strategy in `docs/chimera/`, and writes its work into `docs/company/<area>/`.

```
                        ┌──────────────────────────┐
                        │   YOU (Founder / CEO)    │
                        └────────────┬─────────────┘
                                     │  /company-hq
                        ┌────────────▼─────────────┐
                        │  company-hq (orchestrator)│
                        └────────────┬─────────────┘
     ┌──────────────┬───────────────┼────────────────┬─────────────────┐
  RESEARCH        PRODUCT         MONEY          GO-TO-MARKET        COMPANY
  market-researcher product-manager finance-modeler growth-marketer   legal-ops
  competitor-analyst tech-lead                     sales-lead        fundraising-advisor
  customer-discovery
```

## How to use it

**Let the CEO coordinate (easiest):**
```
/company-hq Validate whether dental clinics in the US are a good first market
/company-hq What should I do this week?
/company-hq Get me ready to launch the founding-member offer
```

**Call one specialist directly:**
```
Use the market-researcher agent to size the SMB cybersecurity market in the US and India
Use the competitor-analyst agent to tear down Huntress and Coro
Use the customer-discovery agent to write an interview script for accounting firms
Use the finance-modeler agent to build a 24-month model at $49/$99/$149 pricing
Use the growth-marketer agent to write landing page copy
Use the sales-lead agent to write a 4-step cold email sequence for law firms
Use the legal-ops agent to compare company registration options for a founder in Nepal
Use the fundraising-advisor agent to tell me whether I should raise or bootstrap
Use the tech-lead agent to implement the phishing email analyzer PRD
```

Type `/agents` in Claude Code to see and edit the team.

## Where the work goes

| Folder | Owner |
|--------|-------|
| `docs/company/STATUS.md` | company-hq (the live company dashboard) |
| `docs/company/market/` | market-researcher |
| `docs/company/competitors/` | competitor-analyst |
| `docs/company/interviews/` (`raw/` for your notes) | customer-discovery |
| `docs/company/product/` | product-manager |
| `docs/company/engineering/` | tech-lead |
| `docs/company/finance/` | finance-modeler |
| `docs/company/marketing/` | growth-marketer |
| `docs/company/sales/` | sales-lead |
| `docs/company/legal/` | legal-ops |
| `docs/company/fundraising/` | fundraising-advisor |

## The recommended first 4 weeks

| Week | Run | You do |
|------|-----|--------|
| 1 | `market-researcher` + `competitor-analyst`: rank 5 segments and pick 1 | Choose the segment |
| 1–2 | `customer-discovery`: script and recruiting plan for that segment | **Do 10 interviews** and drop notes in `interviews/raw/` |
| 3 | `customer-discovery` synthesis → `product-manager` MVP PRD → `finance-modeler` pricing | Decide: persevere, narrow, or pivot |
| 4 | `growth-marketer` landing page + `sales-lead` outreach | Send 50 messages and book 5 demos |

The agents can research, draft, and build. Only you can talk to customers and collect money, and that's what decides whether the company works.
