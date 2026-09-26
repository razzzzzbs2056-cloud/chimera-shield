# 🛡️ ChimeraShield

An AI-powered security tool built with a Next.js frontend and FastAPI backend. ChimeraShield uses Anthropic Claude models to analyze and explain security threats. Today it ships one feature: a paste-an-email phishing analyzer.

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** v18.18+ (Next.js 15)
- **Python** 3.10+
- An **Anthropic** API key

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

Then open `.env` and set `ANTHROPIC_API_KEY`. The other variables have safe defaults and are documented in `.env.example`:

| Variable | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | none | Required. Without it, `/api/scan/email` returns 503 with a clear message. |
| `TRIAGE_MODEL` | `claude-haiku-4-5-20251001` | Model used by the phishing analyzer |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Comma-separated CORS allowlist |
| `SCAN_RATE_LIMIT` | `10/minute` | Per-IP limit on the scan endpoint |
| `MAX_EMAIL_BYTES` | `51200` | Email body size cap (413 above it) |
| `ENV` | `development` | `production` disables `/docs` |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend URL used by the browser |

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
| `make test` | Run backend tests (Anthropic client mocked, no key needed) |

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
│   ├── main.py           # API entry point (CORS, size guard, rate-limit handler)
│   ├── config.py         # Settings read from env / .env
│   ├── routers/scan.py   # Phishing analyzer endpoint
│   └── tests/            # pytest suite
├── docs/                 # Project documentation
├── .env.example          # Environment variable template
├── Makefile              # Dev workflow shortcuts
├── package.json          # Node dependencies
├── requirements.txt      # Python dependencies
└── requirements-dev.txt  # Python dev/test dependencies
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service info and version |
| `GET` | `/health` | Health check |
| `POST` | `/api/scan/email` | Phishing analysis of a pasted email (`email_content`, optional `sender`, `subject`). Rate-limited per IP; bodies over 50 KB get 413. Email bodies are not stored or logged. |

In development the API is self-documented via Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs) (disabled when `ENV=production`).

---

## 🛠️ Tech Stack

**Frontend**
- [Next.js](https://nextjs.org/) — React framework
- [TypeScript](https://www.typescriptlang.org/) — Type safety
- [Tailwind CSS](https://tailwindcss.com/) — Styling

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — Python API framework
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
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

## 🏢 AI Company Team

The repo includes Claude Code sub-agents that act as a startup team (market research, competitors, customer discovery, product, engineering, finance, marketing, sales, legal, fundraising), plus a `/company-hq` orchestrator skill. See [docs/company/README.md](docs/company/README.md).

---

## 📄 License

MIT
