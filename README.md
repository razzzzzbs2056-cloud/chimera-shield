# NEPAL 3T — National Transformation and Global Intelligence Laboratory

An independent, reproducible research and simulation platform that studies Nepal's development constraints,
simulates domestic and international shocks, compares alternative development strategies, and investigates
**whether, when and under what conditions** Nepal could reach US$3 trillion in annual nominal GDP. It does
not assume the target is achievable.

> This is a research system, not a government. It does not represent any institution, enact policy,
> contact third parties or commit funds. External actions require recorded human approval.

## Status (first run)

| Area | State |
|---|---|
| Architecture | 29 agents and 111 subagent task specifications generated from `config/catalog.yaml`; dependency graph acyclic (10 waves) |
| Code | Units, national-accounts identities, growth/projection, input-output, fiscal, energy, delivery constraints, welfare dashboard, target arithmetic, scenario engine, two independent auditors with hash-chained ledger, reporting |
| Tests | `python -m pytest` — see the latest run output in your terminal; the suite covers identities, units, growth arithmetic, ingestion, scenario dependencies, duplicate/contradictory inputs, missing-source detection, audit execution and report generation |
| Baseline data | **PENDING.** The first run's environment blocked all data-source hosts, so no empirical value has been retrieved or substituted. See `reports/baseline/baseline_report.md` and `docs/implementation/data_access.md` |
| US$3T arithmetic | Parametric tables over *hypothetical* base values: `reports/baseline/target_arithmetic.md` |
| Scenarios | 10 defined and validated; all QUALITATIVE_ONLY until shock magnitudes are evidenced |
| Audits | Every standing artifact audited by Agents 15 and 28: `reports/audits/audit_summary.md` |

## Quick start

```bash
pip install -r requirements.txt
python -m pytest
python -m src.cli first-run        # generate, baseline attempt, scenarios, audits, reports, validation
```

Read `CLAUDE.md` for the rules every agent follows, and `FIRST_RUN_PROMPT.md` to drive the platform with
Claude Code.

## Key outputs

- `docs/architecture/architecture_report.md` — agents, dependency waves, components
- `reports/baseline/baseline_report.md` — baseline requirements, sources and status
- `reports/baseline/target_arithmetic.md` — required growth for US$3T by 2050/2060/2070 and an untargeted continuation
- `reports/baseline/data_gaps.md` — material data gaps and research dependencies
- `research/global_exposure/exposure_register.md` — international exposure register
- `reports/baseline/scenario_status.md`, `reports/strategies/strategy_register.md`, `reports/audits/audit_summary.md`

## Structure

```
CLAUDE.md  FIRST_RUN_PROMPT.md  requirements.txt
.claude/agents/          29 generated agent definitions      .claude/skills/   workflow skills
config/                  catalog.yaml (source of truth), agents.json, subagents.json, model_config.yaml, strategies.yaml
src/                     orchestrator, agents, research, data, economic_model, geopolitical_model,
                         scenario_engine, auditing, reporting, cli.py
data/                    raw/ (hashed originals), metadata/, processed/
research/                sources/ (catalog, observations), findings/, global_exposure/
scenarios/               domestic/, geopolitical/, compound/
reports/                 baseline/, strategies/, audits/
tests/                   pytest suite
docs/                    methodology/, architecture/, implementation/
```

---

The repository also contains an earlier, unrelated prototype, **ChimeraShield**, documented below. NEPAL 3T
does not depend on it.

# 🛡️ ChimeraShield

An AI-powered security scanning tool built with a Next.js frontend and FastAPI backend. ChimeraShield leverages OpenAI and Anthropic models to analyze and identify security threats.

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** v16+
- **Python** 3.9+
- An **OpenAI** API key and/or **Anthropic** API key

### 1. Clone & Install

```bash
git clone https://github.com/your-username/chimera-shield.git
cd chimera-shield
make install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Then open `.env` and fill in your API keys:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Server ports (defaults shown)
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Environment
NODE_ENV=development
```

### 3. Start Both Servers

```bash
make dev
```

This starts:
- **Frontend** at [http://localhost:3000](http://localhost:3000)
- **Backend API** at [http://localhost:8000](http://localhost:8000)

---

## 🧰 Make Commands

| Command | Description |
|---|---|
| `make dev` | Start both frontend and backend |
| `make frontend` | Start Next.js frontend only |
| `make backend` | Start FastAPI backend only |
| `make install` | Install all dependencies (npm + pip) |
| `make setup` | Install dependencies then start both servers |

---

## 🗂️ Project Structure

```
chimera-shield/
├── app/                  # Next.js app directory
│   ├── scan/             # Scan page
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Home page
│   └── globals.css       # Global styles
├── backend/              # FastAPI backend
│   └── main.py           # API entry point
├── docs/                 # Project documentation
├── .env.example          # Environment variable template
├── Makefile              # Dev workflow shortcuts
├── package.json          # Node dependencies
└── requirements.txt      # Python dependencies
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service info and version |
| `GET` | `/health` | Health check |

The API is self-documented via Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🛠️ Tech Stack

**Frontend**
- [Next.js](https://nextjs.org/) — React framework
- [TypeScript](https://www.typescriptlang.org/) — Type safety
- [Tailwind CSS](https://tailwindcss.com/) — Styling

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — Python API framework
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
- [OpenAI](https://platform.openai.com/) — AI model integration
- [Anthropic](https://www.anthropic.com/) — Claude model integration
- [Pydantic](https://docs.pydantic.dev/) — Data validation

---

## ☁️ Running in GitHub Codespaces

This project is Codespaces-ready. After opening in Codespaces:

1. Install dependencies and start both servers:
   ```bash
   make dev
   ```
2. Go to the **PORTS** tab and click the 🌐 globe icon next to port **3000**.

---

## 📄 License

MIT
