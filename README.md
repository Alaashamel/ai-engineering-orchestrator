<div align="center">

# 🤖 AI Engineering Orchestrator

### Autonomous Multi-Agent Software Development System

<br>

> **Describe a project in plain language — a fleet of specialized AI agents designs, builds, tests, and prepares it for deployment — while you stay in control through approval gates and rollbacks.**

<br>

[![Live Demo](https://img.shields.io/badge/Live_Demo-Coming_Soon-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://github.com/Alaashamel/ai-engineering-orchestrator)
[![Documentation](https://img.shields.io/badge/Documentation-8A2BE2?style=for-the-badge&logo=readthedocs&logoColor=white)](docs/architecture.md)
[![Swagger API](https://img.shields.io/badge/API_Docs-Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](http://localhost:8000/docs)

<br>

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL_16_+_pgvector-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis_7-DC382D?style=flat-square&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI_Structured_Outputs-412991?style=flat-square&logo=openai&logoColor=white)

<br>

[![Tests](https://img.shields.io/badge/tests-224_passing-brightgreen?style=flat-square)](orchestration/tests)
[![Test Time](https://img.shields.io/badge/test_time-~10s-blue?style=flat-square)](#testing)
[![Lint](https://img.shields.io/badge/lint-ruff_%2B_tsc-4B32C3?style=flat-square)](#testing)
[![Security](https://img.shields.io/badge/security-bandit_audited-ff5722?style=flat-square)](#testing)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

</div>

---

## 📑 Table of Contents

- [✨ Overview](#-overview)
- [🎯 Problem](#-problem)
- [💡 Solution](#-solution)
- [🏗️ Architecture](#-architecture)
- [⚙️ Core Features](#-core-features)
- [🧰 Tech Stack](#-tech-stack)
- [🔄 System Workflow](#-system-workflow)
- [📸 Screenshots / Demo](#-screenshots--demo)
- [🚀 Getting Started](#-getting-started)
- [🧪 Testing & Evaluation](#-testing--evaluation)
- [📦 Deployment](#-deployment)
- [🗺️ Roadmap](#-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Overview

The **AI Engineering Orchestrator** is a production-grade autonomous software factory. Instead of one-shot "prompt-to-code" generators, it runs a **deterministic, auditable pipeline of six specialized AI agents** — guided by a LangGraph state machine — that takes a natural-language project description all the way to generated, tested, and deployment-ready code.

**What it does in one sentence:** you describe a project, and a coordinated team of AI agents (CEO, Product Manager, Architect, Backend/Frontend/QA Engineers) analyzes it, plans it, designs it, builds it, tests it, and presents the result for your approval.

**No API key? No problem.** The system runs in **mock mode** — the LLM provider automatically detects a missing key or exhausted quota and returns schema-valid deterministic responses. Every feature works for development, testing, and CI with zero external credentials.

---

## 🎯 Problem

Traditional AI code generators fail in the real world because of three fundamental flaws:

| Flaw | Consequence |
|------|-------------|
| **One-shot prompting** | A single prompt produces a single dump of code with no analysis, no architecture, and no requirements traceability |
| **No process** | There is no separation of concerns — no planning phase, no design review, no QA, no human oversight |
| **No quality gates** | Output is unvalidated, untested, and unmeasured — you can't prove it works, let alone measure how well |

The result: AI-generated code that looks impressive in a screenshot but is **unmaintainable, untestable, and risky to ship**.

---

## 💡 Solution

The Orchestrator treats AI software development as an **engineering process**, not a prompt:

- **A strict, reviewable state machine** — LangGraph nodes for discovery, planning, architecture, task decomposition, and implementation, with conditional routing and failure handling
- **Six specialized agents, each with one job** — and every agent returns *typed Pydantic models*, so outputs are programmatically consumable, not free-form prose
- **Human-in-the-loop gates** — critical tasks raise approval requests; workflows pause until a human approves, rejects (with reason), or rolls back to an earlier phase
- **Full observability** — every decision, phase transition, and generated file is written to an audit log and exposed through the API
- **Built-in quality measurement** — an evaluation harness with datasets, A/B model comparison, prompt versioning, and cost tracking ships in the box
- **Graceful degradation** — a 40+ module LLM abstraction layer with automatic mock fallback means the system works before, during, and after you add real model credentials

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│                              USER (Web Dashboard / API)                             │
└──────────────────────────────────┬─────────────────────────────────────────────────┘
                                   │  natural-language project request
                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│                        LANGGRAPH ORCHESTRATION ENGINE (state machine)               │
│                                                                                    │
│   ┌────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│   │  discovery │ ───▶ │   planning   │ ───▶ │ architecture │ ───▶ │  task_       │ │
│   │  CEO Agent │      │ Product Mgr. │      │ Architect    │      │ decomposition│ │
│   └────────────┘      └──────────────┘      └──────────────┘      │  CEO Agent   │ │
│        │                     │                     │              └──────────────┘ │
│        ▼                     ▼                     ▼                     ▼        │
│   project analysis      requirements PRD      architecture spec    task list       │
│                                                                                    │
│        ┌────────────────────────────────────────────────────────────────────────┐  │
│        │                     check_approvals (human gate)                       │  │
│        └────────────────────────────────┬───────────────────────────────────────┘  │
│                                         │ approved                                │
│                                         ▼                                         │
│        ┌────────────────────────────────────────────────────────────────────────┐  │
│        │                         implementation (loop)                           │  │
│        │   ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐   │  │
│        │   │ Backend Eng. │   │ Frontend Eng.│   │ Testing / QA Engineer    │   │  │
│        │   │  .py files   │   │ .tsx files   │   │ pytest + vitest suites   │   │  │
│        │   └──────────────┘   └──────────────┘   └──────────────────────────┘   │  │
│        │        files written to disk via sandboxed FileSystemTool              │  │
│        └────────────────────────────────┬────────────────────────────────────────┘  │
│                                         │ all tasks complete                        │
│                                         ▼                                           │
│                                   ┌──────────────┐                                  │
│                                   │   complete   │◀── (fail on any phase error)     │
│                                   └──────────────┘                                  │
│                                                                                    │
└──────────────────────────────────┬─────────────────────────────────────────────────┘
                                   │
              ┌────────────────────┼─────────────────────┐
              ▼                    ▼                     ▼
      ┌─────────────┐      ┌───────────────┐     ┌──────────────┐
      │ PostgreSQL  │      │   Audit Log   │     │  Webhooks +  │
      │  + pgvector │      │  (every agent │     │  WebSocket   │
      │ (projects)  │      │   decision)   │     │  streaming   │
      └─────────────┘      └───────────────┘     └──────────────┘
```

### Agent Pipeline

| Agent | Responsibility | Typed output (Pydantic) |
|-------|----------------|------------------------|
| **CEO Agent** | Analyzes requests, breaks scope, delegates work, ensures quality | `DiscoveryOutput` — project type, complexity, objectives, risks, approach; `TaskDecompositionOutput` — prioritized task list with dependencies |
| **Product Manager** | Defines requirements, user stories, MVP scope | Requirements document with user stories |
| **Architect** | Designs system architecture, tech stack, API schema | Architecture specification |
| **Backend Engineer** | Generates production FastAPI code | `BackendPlan` — files with path + content |
| **Frontend Engineer** | Generates production React/TypeScript code | `FrontendPlan` — components, pages, hooks |
| **Testing Engineer** | Generates pytest + Vitest suites and fixtures | `TestPlan` — test files, fixtures |

### The LLM Layer

Between the agents and the model provider sits a **40+ module abstraction layer** — the largest subsystem in the repository — covering provider abstraction, auto mock-fallback, caching, retry with backoff, streaming, routing, scheduling, parsing, validation, enforcement, cost tracking, metrics, monitoring, profiling, debugging, prompt versioning, and evaluation.

---

## ⚙️ Core Features

| Feature | Details |
|---------|---------|
| 🤖 **Six-agent orchestration** | CEO → PM → Architect → Engineering agents, driven by a deterministic LangGraph state machine |
| 🧠 **Structured LLM output** | Every agent must return a valid Pydantic model — schema-guaranteed, never free-form |
| 🔄 **Automatic mock fallback** | Missing API key or `insufficient_quota` → graceful, logged switch to deterministic mock mode |
| 👤 **Human-in-the-loop** | Approval gates for critical tasks; reject with reason; roll back to any earlier phase |
| 📊 **Evaluation harness** | `EvalDataset` (JSON/CSV), markdown `EvalReport`s, and an `ABTestFramework` for model comparison |
| 📝 **Prompt versioning** | Semantic `major.minor` versions, unified diffs, tags, and rollback via `PromptRegistry` |
| 💰 **Cost & metrics tracking** | Per-request `TokenUsage`, cumulative cost, request/latency metrics, exposed via `/eval/*` API |
| 🔐 **Audit trail** | Every phase, decision, and generated file is logged via the structured audit logger |
| 🌐 **Real-time streaming** | WebSocket broadcasts of `workflow_complete` / `approval_resolved` / `workflow_error` |
| 🔔 **Webhook notifications** | `workflow.completed` events pushed to configured webhook URLs |
| 🛡️ **Security hardening** | Sandboxed file tools, secret management, rate limiting (prod), CORS, bandit audit in CI |
| 📦 **Containerized** | Docker Compose for dev (hot reload) and production, GHCR image publishing |

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Orchestration** | [LangGraph](https://langchain-ai.github.io/langgraph/) · Pydantic v2 · TypedDict state |
| **Backend API** | FastAPI 0.111 · SQLAlchemy 2.0 (async) · Alembic · Uvicorn |
| **Frontend** | React 18 · TypeScript 5 · React Router 6 · Tailwind CSS 3 · Vite 5 |
| **Database** | PostgreSQL 16 + pgvector · Redis 7 |
| **AI / LLM** | OpenAI 1.30 structured outputs · custom 40+ module provider layer with mock fallback |
| **Observability** | Structlog · Request-ID middleware · OpenTelemetry-style tracing · metrics collector · audit logger |
| **Security** | Bandit · sandboxed file tools · secret management · rate limiting · CORS |
| **CI/CD** | GitHub Actions — `ci.yml` (lint + test + docker build) · `lint.yml` · `deploy.yml` (GHCR + SSH) |
| **Quality** | Ruff · pytest · pytest-asyncio · tsc · pre-commit · markdownlint · yamllint |

---

## 🔄 System Workflow

Every project moves through a **deterministic, auditable lifecycle**:

```
discovery → planning → architecture → task_decomposition → [human gate] → implementation → completed
                                                                               │
                                                          any phase error ─────▶ failed
```

| # | Phase | Who | What happens |
|---|-------|-----|--------------|
| 1 | **discovery** | CEO Agent | Analyzes the request → project type, complexity, key objectives, risks, recommended approach |
| 2 | **planning** | Product Manager | Produces the PRD — requirements, user stories, MVP scope |
| 3 | **architecture** | Architect | Designs the system — tech stack, API schema, component layout |
| 4 | **task_decomposition** | CEO Agent | Breaks the plan into engineering tasks (agent, priority, dependencies, acceptance criteria) |
| 5 | **check_approvals** | Human gate | Critical tasks raise approval requests and **pause the workflow** |
| 6 | **implementation** | Backend · Frontend · QA | Engineering agents generate files; written via the sandboxed file tool; loops until all tasks complete |
| 7 | **complete** | Orchestrator | Marks the workflow `completed` with full phase history and audit trail |

**Rollback** — roll back to any earlier phase at any time; the engine truncates the phase history and re-enters the graph at that node. **Approvals** — approve all pending actions, or reject with a reason and optional rollback target.

---

## 📸 Screenshots / Demo

> ⚡ The project includes a full **web control center** — a React dashboard for managing projects and monitoring workflows.

| View | What you'll see |
|------|-----------------|
| **Dashboard** | Live system status cards (API / projects / agents / database), recent projects, quick-start guide, system panel |
| **Projects** | Create/list/manage projects with status badges, descriptions, and one-click workflow access |
| **Workflow** | Live phase timeline with rollback buttons, approval cards, task list, generated files, decisions, errors, and implementation log |

**Run it locally** (no API key required) and see the whole pipeline work:

```bash
make dev-api && make dev-web    # http://localhost:8000  ·  http://localhost:5173
```

---

## 🚀 Getting Started

### Prerequisites

| Tool | Version | Required? |
|------|---------|-----------|
| Python | 3.13+ | ✅ Yes |
| Node.js | 20+ | ✅ Yes |
| Docker | Latest | ⚠️ Optional — for infra + production |
| PostgreSQL 16 + pgvector | 16+ | ⚠️ Optional — degraded mode without it |
| Redis | 7+ | ⚠️ Optional — degraded mode without it |

### 1 — Clone & install

```bash
git clone https://github.com/Alaashamel/ai-engineering-orchestrator.git
cd ai-engineering-orchestrator

make api-deps    # creates .venv and installs backend dependencies
make web-deps    # installs frontend dependencies
```

### 2 — Configure

```bash
cp .env.example .env
```

The only variable you *must* set for real LLM generation is `LLM_API_KEY`. **Leave it blank to run in mock mode** — the system automatically falls back and everything still works.

### 3 — (Optional) Start infrastructure

```bash
make db-up       # PostgreSQL 16 (pgvector) + Redis 7 via Docker
```

### 4 — Run

Open **two terminals**:

```bash
# Terminal 1 — API → http://localhost:8000  (Swagger at /docs)
make dev-api

# Terminal 2 — Web UI → http://localhost:5173
make dev-web
```

Create a project in the dashboard, open it, and click **Start Workflow** to watch the agents work.

---

## 🧪 Testing & Evaluation

### Test suites

```bash
make test              # full suite: apps/api/tests + orchestration/tests
make test-coverage     # with coverage report
make lint              # ruff (Python) + tsc (TypeScript)
```

| Suite | Count | Status |
|-------|-------|--------|
| Orchestration tests | 181 | ✅ all passing |
| API tests | 43 | ✅ all passing |
| Skipped (require live DB) | 3 | ⏭️ expected |

**Current status: `224 passed · 3 skipped · 0 failed` in ~10s.**

### The end-to-end evaluation suite

The eval harness exercises the **entire LLM stack without a real API key**:

```bash
$env:PYTHONPATH="<repo-root>" ; .venv/Scripts/python orchestration/tests/test_eval_comprehensive.py
```

It covers provider auto-fallback, A/B model comparison (wins/ties/confidence), markdown report generation, prompt versioning with diffs/tags/rollback, and metrics collection.

---

## 📦 Deployment

### Continuous deployment (GitHub Actions)

Pushing to `main` triggers [`deploy.yml`](.github/workflows/deploy.yml), which:

1. **Builds** Docker images for `apps/api` and `apps/web`
2. **Publishes** them to **GitHub Container Registry** (tagged `latest` + commit SHA)
3. **SSH-deploys** to the production server (`appleboy/ssh-action`):
   ```bash
   cd /opt/ai-engineering-orchestrator && docker compose pull && docker compose up -d --force-recreate
   ```

### Production stack

```bash
# Local production-style run
docker compose -f docker-compose.prod.yml up -d --build
```

| Service | Image / Build | Exposed |
|---------|---------------|---------|
| **web** | `./apps/web` (multi-stage) | `:80` |
| **api** | `./apps/api` (multi-stage) | via web |
| **postgres** | `postgres:16-alpine` | internal, healthchecked |

### CI quality gates

Every push/PR runs `ci.yml` — **ruff + bandit** security scan, **tsc** type-checking, backend and orchestration test suites, and a Docker build verification.

---

## 🗺️ Roadmap

| # | Milestone | Status |
|---|-----------|--------|
| 1 | Monorepo scaffold — FastAPI + React + Docker + CI | ✅ Done |
| 2 | LangGraph orchestration engine — planning agents, streaming | ✅ Done |
| 3 | Engineering agents — Backend/Frontend/QA + file I/O tools | ✅ Done |
| 4 | Human-in-the-loop — approvals, rollback, observability | ✅ Done |
| 5 | Real LLM integration — provider layer, eval harness, A/B testing | ✅ Done |
| 6 | Security audit — vulnerability scanning, secret management | ✅ Done |
| 7 | Production deployment — Docker Compose, monitoring, auto-scaling | ✅ Done |

**Next up:** multi-provider support (Anthropic / Gemini) through the existing factory, persistent workflow checkpointing to PostgreSQL, vector-similarity task retrieval with pgvector, and a live workflow timeline in the dashboard.

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md) first.

1. **Branch** — create a feature branch from `develop`: `git checkout -b feature/your-feature`
2. **Commit** — use [conventional commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `chore:`
3. **Verify** — run `make lint && make test`; both must pass
4. **PR** — open a pull request against `develop`

Every PR is gated by the CI pipeline. See [docs/architecture.md](docs/architecture.md) for design details.

---

## 📄 License

Distributed under the [MIT License](LICENSE). Report security issues per our [SECURITY.md](SECURITY.md) policy.

---

<div align="center">

**Built with LangGraph, FastAPI, React — and a fleet of autonomous agents.**

⭐ If this project helped you, consider giving it a star!

</div>
