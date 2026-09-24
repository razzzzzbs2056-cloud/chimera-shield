# 🤖 Chimera Agency — an AI content creation company run by agents

A CEO agent takes a business goal, breaks it into assignments, and delegates them to
specialist sub-agents. Every agent works from one shared **board**, so marketing (and the CEO)
can see every campaign, piece of content, email and code file the company has produced.

```
                    ┌──────────────┐
      your goal ──► │     CEO      │ ── executive summary
                    └──────┬───────┘
          delegate(agent, task)   view_board()
   ┌───────────┬───────────┼────────────┬──────────────┐
   ▼           ▼           ▼            ▼              │
Marketing   Content      Email       Engineer          │
post_       publish_     send_       write_file        │
campaign    content      email                         │
   └───────────┴─────┬─────┴────────────┘              │
                     ▼                                 │
            Shared board (board.json) ◄────────────────┘
```

| Agent | Job | Tools |
|---|---|---|
| **CEO** | Plans the work, delegates, reviews, reports | `delegate`, `view_board` |
| **Marketing** | Audience, positioning, channels, schedule | `view_board`, `post_campaign` |
| **Content** | Blog posts, social posts, video scripts, newsletters | `view_board`, `publish_content` |
| **Email** | Writes and sends marketing email | `view_board`, `send_email` |
| **Engineer** | Landing pages, scripts, integrations | `view_board`, `write_file` |

Each agent is a Claude tool-use loop (`agency/agent.py`). The CEO's `delegate` tool runs a
sub-agent to completion and hands its report back, so sub-agents are just tools to the CEO.

## Quick start

```bash
pip install -r agency/requirements.txt

# Try it offline first — scripted agents, no API key needed
python -m agency "Launch our AI newsletter service" --mock

# Run it for real with Claude
export ANTHROPIC_API_KEY=sk-ant-...
python -m agency "Launch our AI newsletter service"
```

Output lands in `agency_output/`:

```
agency_output/
├── board.json      # everything every agent produced
├── content/        # blog posts, social posts, scripts (markdown)
├── outbox/         # every email, as .eml files
└── site/ ...       # code written by the engineer
```

Or from Python:

```python
from agency import Company

company = Company()
print(company.run("Grow our YouTube channel for small-business owners"))
print(company.board.summary("campaign"))
```

## Sending real email

Email is a **dry run by default**: each message is saved to `agency_output/outbox/` and nothing
leaves your machine. To deliver through SMTP, set these in `.env` (or pass `--send-emails`):

```env
AGENCY_SEND_EMAILS=true
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=you@example.com
SMTP_PASSWORD=app-password
EMAIL_FROM=Your Company <you@example.com>
AGENCY_EMAIL_ALLOWLIST=@yourcompany.com,friend@example.com   # optional
AGENCY_MAX_EMAILS=10
```

Guard rails: the email agent is told to only email recipients named in its task, addresses are
validated, the optional allowlist is enforced, and each run is capped at `AGENCY_MAX_EMAILS`.
Only email people who have opted in. Anti-spam law (CAN-SPAM, GDPR, CASL) applies to your agents too.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `AGENCY_COMPANY_NAME` | `Chimera Content Co.` | Name the agents use |
| `AGENCY_MODEL` | `claude-opus-5` | Claude model for every agent |
| `AGENCY_EFFORT` | `high` | `low` / `medium` / `high` / `xhigh` / `max` |
| `AGENCY_FALLBACKS` | `true` | Server-side refusal fallback (retries a declined request on another model) |
| `AGENCY_MOCK` | `false` | Scripted offline agents |
| `AGENCY_WORKSPACE` | `agency_output` | Output directory |
| `AGENCY_MAX_TURNS` | `12` | Tool-loop limit per agent |

## Adding a new agent

1. Add a role to `TEAM` in `agency/company.py` (title and instructions).
2. Give it tools in `Company._hire` — a `Tool(name, description, schema, handler)`.
3. The CEO automatically learns about the new agent through the `delegate` tool's enum.

## Tests

```bash
python -m pytest tests -q
```
