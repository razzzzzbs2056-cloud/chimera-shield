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

---

## 🤖 Agent Team

Project subagents live in `.claude/agents/` (lead, architect, backend, frontend, designer, security, detection scientist, QA, reviewer). Start the lead with `claude --agent chimera-lead`. Architecture, design system and scientific plan: [`docs/chimera/06-system-design.md`](docs/chimera/06-system-design.md).

### Choosing a model (including open-source)

ChimeraShield defaults to Anthropic but runs on any open-weight model served through an OpenAI-compatible API:

```env
LLM_PROVIDER=ollama          # or vllm, llamacpp, lmstudio, tgi, sglang, huggingface, openrouter, together, groq, fireworks, openai_compat
LLM_MODEL=qwen2.5:7b
```

`GET /api/models?role=triage|escalation|guard|classifier` lists a curated catalog (`backend/llm/catalog.py`). It's a starting list, not every model; any model your server exposes works. Project skills are in `.claude/skills/`. Run tests with `make test`.
