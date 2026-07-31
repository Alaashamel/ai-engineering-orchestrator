<div align="center">

# 🤖 AI Engineering Orchestrator

### Autonomous Multi-Agent Software Development System

**Describe a project in plain language — a fleet of specialized AI agents designs, builds, tests, and prepares it for deployment — while you stay in control through approval gates and rollbacks.**

<br>

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.11x-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+pgvector-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

<br>

[![Tests](https://img.shields.io/badge/tests-224%20passing-brightgreen?style=flat-square)](orchestration/tests)
[![Skipped](https://img.shields.io/badge/skipped-3%20(require%20DB)-lightgrey?style=flat-square)](#testing)
[![Lint](https://img.shields.io/badge/lint-ruff%20%2B%20tsc-4B32C3?style=flat-square)](#testing)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

</div>

---

## 📖 Table of Contents

- [✨ Overview](#-overview)
- [🏗️ System Architecture](#️-system-architecture)
  - [The Workflow Lifecycle](#the-workflow-lifecycle)
  - [Agent Pipeline Deep Dive](#agent-pipeline-deep-dive)
  - [The LLM Layer](#the-llm-layer)
  - [Evaluation & A/B Testing](#evaluation--ab-testing)
- [⚙️ Tech Stack](#️-tech-stack)
- [🚀 Getting Started](#-getting-started)
- [🔧 Configuration](#-configuration)
- [📡 API Reference](#-api-reference)
- [🧪 Testing & Evaluation](#-testing--evaluation)
- [📂 Project Structure](#-project-structure)
- [🗺️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Overview

The **AI Engineering Orchestrator** is a production-grade autonomous software factory. You provide a natural-language description — *"Build a customer portal with a FastAPI backend, React frontend, and PostgreSQL persistence"* — and a pipeline of **six specialized AI agents** collaborates through a deterministic LangGraph state machine to produce:

1. A structured **project analysis** (type, complexity, risks, approach)
2. A complete **product requirements document** with user stories
3. A **system architecture** specification (tech stack, API schema)
4. A decomposed set of **engineering tasks** with priorities and dependencies
5. **Production code** — backend (Python), frontend (TypeScript), and tests
6. **Human review gates** for critical operations, with **phase rollback**

> **No API key? No problem.** Every feature works in **mock mode** — the LLM provider automatically detects a missing key or exhausted quota and returns realistic deterministic responses. Development, testing, and CI all run without credentials.

### Why this project exists

Most "AI code generators" are one-shot prompt-to-output tools. They produce code with no requirements analysis, no architecture, no tests, and no oversight. The Orchestrator is the opposite:

- **Process over prompting** — a strict, reviewable state machine (not a single prompt)
- **Separation of concerns** — six agents, each with one responsibility and a typed output
- **Human-in-the-loop** — no irreversible actions happen without approval
- **Measurable quality** — a built-in eval harness, A/B model comparison, and cost tracking
- **Degrade gracefully** — mock mode means the entire pipeline runs with zero dependencies

---

## 🏗️ System Architecture

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
│        │                     │                     │                     │        │
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

### The Workflow Lifecycle

Every project moves through a **deterministic, auditable state machine** driven by LangGraph. Each node represents a phase; conditional edges route execution — a failure in any phase routes to the `fail` state, and the `implementation` phase loops until all tasks are complete.

| # | Phase | Node | What happens |
|---|-------|------|--------------|
| 1 | **discovery** | `CEO Agent` | Analyzes the request → project type, complexity, objectives, risks, recommended approach |
| 2 | **planning** | `Product Manager` | Produces the PRD — requirements, user stories, MVP scope |
| 3 | **architecture** | `Architect` | Designs the system — tech stack, API schema, component layout |
| 4 | **task_decomposition** | `CEO Agent` | Breaks the plan into concrete tasks with agent assignment, priority, and dependencies |
| 5 | **check_approvals** | *Orchestrator* | **Human gate** — critical tasks raise approval requests and pause the workflow |
| 6 | **implementation** | `Engineering Agents` | Backend, Frontend, and QA agents generate files; written via the sandboxed file tool |
| 7 | **complete** | *Orchestrator* | Marks the workflow `completed` with a full phase history and audit trail |

**Phase rollback** — at any point you can roll back to an earlier phase; the engine truncates the phase history and re-enters the graph at that node. **Approvals/rejections** — when a human gate is reached, the workflow waits for `approve` or `reject` (with an optional reason and rollback target) via the API.

### Agent Pipeline Deep Dive

Each agent is a `BaseAgent` subclass with a **system prompt** and **typed Pydantic output** — the LLM must return data matching the schema, or the response is rejected. This is what makes agent outputs *programmatically consumable* instead of free-form prose.

| Agent | System persona | Typed output (Pydantic) |
|-------|---------------|------------------------|
| **CEO Agent** | Analyzes requests, delegates work, ensures quality | `DiscoveryOutput` — project_type, complexity, key_objectives[], risks[], recommended_approach, reasoning |
| | | `TaskDecompositionOutput` — tasks[] of `TaskItem` (id, title, description, agent, priority, dependencies) |
| **Product Manager** | Defines requirements, user stories, MVP scope | Requirements document with user stories |
| **Architect** | Designs architecture, tech stack, API schema | Architecture specification |
| **Backend Engineer** | Generates production Python/FastAPI code | `BackendPlan` — files_to_create[] (path + content) |
| **Frontend Engineer** | Generates production React/TypeScript code | `FrontendPlan` — components[], pages[], hooks[] |
| **Testing Engineer** | Generates pytest + Vitest suites and fixtures | `TestPlan` — test_files[], fixtures[] |

> The `TaskItem` model also carries `acceptance_criteria` and a `status` lifecycle (`pending → completed`), which the orchestration graph uses to route the implementation loop.

### The LLM Layer

Sitting between the agents and the model provider is a **40+ module abstraction layer** — the largest subsystem in the repository:

```
                        ┌─────────────────────────────────────────────┐
                        │            LLM LAYER (orchestration/)       │
                        │                                             │
   agents ─────────────▶│  LLMProvider ──▶ real API (OpenAI)          │
                        │      │  └── quota/missing key?              │
                        │      ▼        └──▶ mock mode (auto)        │
                        │  LLMFactory (provider registry)             │
                        │  LLMAdapter (unified interface)             │
                        │  LLMPipeline (system+user+structured)       │
                        │  LLMCacheMgr (response caching)             │
                        │  LLMRetry (backoff + retries)               │
                        │  LLMCost (token/cost tracking)              │
                        │  LLMMetrics (collector)                     │
                        │  LLMMonitor, LLMProfiler, LLMDebugger       │
                        │  LLMRouter, LLMScheduler, LLMParser         │
                        │  PromptRegistry (versioning, diff, rollback)│
                        │  LLMStreaming, LLMValidator, LLMEnforcer    │
                        │  ... and 20+ more focused modules           │
                        └─────────────────────────────────────────────┘
```

**The star feature: automatic mock fallback.** When `LLM_API_KEY` is missing — or the provider returns `insufficient_quota` — the provider flips to mock mode *mid-flight*, logs a warning, and returns schema-valid deterministic responses. No crash, no partial state, no code changes needed when you add billing later.

### Evaluation & A/B Testing

Because the LLM layer is fully abstracted, the same provider interface powers a rigorous **evaluation framework**:

| Module | Purpose |
|--------|---------|
| `eval_dataset.py` | `EvalCase` / `EvalDataset` — structured test cases with expected outputs, JSON/CSV import/export, tag filtering |
| `eval_reporting.py` | `EvalReport` — pass rates, failure analysis, markdown export; `ReportComparison` for multi-model comparison |
| `eval_ab_testing.py` | `ABTestFramework` — runs the same suite against two providers, computes wins/ties, latency, cost, and confidence |
| `prompt_registry.py` | Versioned prompt templates with `major.minor` semantics, unified diffs, tags, and rollback |
| `llm_cost.py` | Per-request `TokenUsage` → cost records, cumulative totals |
| `llm_metrics.py` | `LLMMetricsCollector` — request counts, latency, token usage summaries |

These feed the `/eval/*` API endpoints, so the whole evaluation workflow is available through the control center.

---

## ⚙️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Orchestration** | [LangGraph](https://langchain-ai.github.io/langgraph/) | Deterministic state machine with conditional edges, checkpointing, streaming |
| **Backend** | FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic v2 | Typed, async, auto-documented API |
| **Frontend** | React 18 + TypeScript 5 + React Router 6 + Tailwind CSS + Vite | Fast, typed control-center dashboard |
| **Database** | PostgreSQL 16 + pgvector, Redis 7 | Relational persistence + vector search-ready |
| **LLM** | OpenAI structured outputs | JSON-schema-guaranteed agent responses |
| **Observability** | Structlog, request ID middleware, custom metrics, tracing, audit logger | Full traceability of every agent decision |
| **Security** | Sandboxed file tools, secret management, rate limiting, CORS, `.env`-based secrets | Production hardening |
| **Infrastructure** | Docker Compose (dev + prod), GitHub Actions (CI/lint/deploy) | Reproducible deploys, automated quality gates |
| **Quality** | Ruff, mypy, pytest, tsc, pre-commit, markdownlint, yamllint | 224 passing tests, zero lint errors |

---

## 🚀 Getting Started

### Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.13+ | Required for the API and orchestration engine |
| Node.js | 20+ | Required for the React control center |
| PostgreSQL | 16+ | **Optional** — app runs in degraded mode without it |
| Redis | 7+ | **Optional** — app runs in degraded mode without it |
| Docker | Latest | Optional — for one-command infra + production deploy |

### 1. Clone & install

```bash
git clone https://github.com/Alaashamel/ai-engineering-orchestrator.git
cd ai-engineering-orchestrator

# Python backend (creates .venv)
make api-deps

# Node frontend
make web-deps
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` — the only variable you *must* set is `LLM_API_KEY` if you want real generation. Leave it blank to use mock mode:

```dotenv
ENVIRONMENT=development
LOG_LEVEL=INFO
LLM_API_KEY=sk-...          # optional — leave blank for mock mode
LLM_MODEL=gpt-4o
DATABASE_URL=postgresql+asyncpg://app:app_password@localhost:5432/ai_software_company
```

### 3. Start the infrastructure (optional, requires Docker)

```bash
make db-up        # PostgreSQL 16 (pgvector) + Redis 7
```

### 4. Run the application

Open **two terminals**:

```bash
# Terminal 1 — API  (http://localhost:8000, Swagger at /docs)
make dev-api

# Terminal 2 — Web UI (http://localhost:5173)
make dev-web
```

Then open **http://localhost:5173**, create a project, and start its workflow. Watch the agents work through discovery → planning → architecture → implementation in the Workflow view.

### Without Docker / without a database

The API detects a missing database at startup, logs a warning, and keeps serving health, project, and eval endpoints with in-memory state. The Web UI shows a clear "Database: Unavailable" status card rather than failing.

---

## 🔧 Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | `development` / `production` | `development` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `API_HOST` / `API_PORT` | API bind address/port | `0.0.0.0` / `8000` |
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `JWT_SECRET` | Signing secret for tokens | `change-this-...` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRATION_HOURS` | Token lifetime | `24` |
| `LLM_API_KEY` | OpenAI key — **blank = mock mode** | — |
| `LLM_MODEL` | Default generation model | `gpt-4o` |
| `WEB_ORIGIN` | CORS origin in production | `http://localhost:5173` |

---

## 📡 API Reference

All routes are auto-documented in Swagger UI at **`/docs`**. Rate limiting (100 req/min) and request-ID tracing activate in `production`.

### Health & System

| Method | Path | Description | Example |
|--------|------|-------------|---------|
| `GET` | `/health` | Health check | `curl http://localhost:8000/health` |
| `GET` | `/` | Root welcome + version | `curl http://localhost:8000/` |

### Projects

| Method | Path | Description | Example |
|--------|------|-------------|---------|
| `GET` | `/projects` | List all projects | `curl http://localhost:8000/projects` |
| `POST` | `/projects` | Create a project | `curl -X POST http://localhost:8000/projects -H "Content-Type: application/json" -d '{"name":"My API","description":"A REST service"}'` |
| `GET` | `/projects/{id}` | Project details | `curl http://localhost:8000/projects/<id>` |
| `PATCH` | `/projects/{id}` | Update a project | `curl -X PATCH ... -d '{"status":"active"}'` |
| `DELETE` | `/projects/{id}` | Delete a project | `curl -X DELETE http://localhost:8000/projects/<id>` |

### Workflows (the core)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/workflows/{id}/start` | **Run the full agent pipeline** — returns the final graph state (phase history, decisions, tasks, generated files) |
| `POST` | `/workflows/{id}/start-stream` | Run and return a lightweight completion summary |
| `POST` | `/workflows/{id}/approve` | Approve pending human-gate actions (`rollback_to` optional) |
| `POST` | `/workflows/{id}/reject` | Reject pending actions (`reason`, `rollback_to` optional) |
| `POST` | `/workflows/{id}/rollback` | Roll back to a prior phase |
| `GET` | `/workflows/{id}/status` | Current phase, pending approvals, project state |
| `WS` | `/workflows/ws/{id}` | Real-time streaming — broadcast `workflow_complete`, `approval_resolved`, `workflow_error` events |

**Example — run the full pipeline:**

```bash
curl -X POST http://localhost:8000/workflows/<project-id>/start
```

```json
{
  "status": "completed",
  "state": {
    "phase": "completed",
    "phase_history": [
      {"phase": "discovery", "timestamp": "..."},
      {"phase": "planning", "timestamp": "..."},
      {"phase": "architecture", "timestamp": "..."},
      {"phase": "task_decomposition", "timestamp": "..."},
      {"phase": "implementation", "timestamp": "..."},
      {"phase": "completed", "timestamp": "..."}
    ],
    "tasks": [ { "id": "t1", "title": "...", "agent": "backend_engineer", "priority": "high", "status": "completed" } ],
    "generated_files": [ { "path": "app/main.py", "agent": "backend_engineer", "status": "written" } ],
    "decisions": [ { "agent": "ceo", "action": "discovery_analysis", "reasoning": "..." } ]
  }
}
```

### Evaluation, Prompts & Cost (the `/eval` family)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/eval/run` | Run a model evaluation (model, dataset, test count) → pass/fail summary + per-case results |
| `GET` | `/eval/cost` | Cumulative cost summary (total cost, tokens, requests, per-record breakdown) |
| `POST` | `/eval/cost/record` | Record token usage for a model |
| `GET` | `/eval/metrics` | Model metrics summary from the collector |
| `GET` | `/eval/models` | Available model IDs + recommended default |
| `POST` | `/eval/prompts` | Register a versioned prompt template |
| `GET` | `/eval/prompts` | List templates + their tags |
| `GET` | `/eval/prompts/{name}` | Fetch latest (or `?version=`) template |
| `POST` | `/eval/prompts/{name}/rollback` | Roll a template back to a prior version |

**Example — run an evaluation:**

```bash
curl -X POST http://localhost:8000/eval/run \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","dataset_name":"smoke","test_count":3}'
```

```json
{
  "summary": { "model": "gpt-4o", "total": 3, "passed": 3, "failed": 0 },
  "results": [ { "name": "test_0", "passed": true, "score": 1.0, "latency_ms": 0, "error": null } ]
}
```

---

## 🧪 Testing & Evaluation

### Test suites

```bash
make test              # Full pytest suite (orchestration + API)
make test-coverage     # With coverage report
make lint              # ruff (Python) + tsc (TypeScript)
```

**Current status:** `224 passed, 3 skipped, 0 failed` in ~10s. The 3 skips require a live PostgreSQL instance.

### The end-to-end evaluation suite

```bash
$env:PYTHONPATH="<repo-root>" ; .venv/Scripts/python orchestration/tests/test_eval_comprehensive.py
```

This single script exercises the **entire LLM stack without a real API key**:

1. Real `LLMProvider` instantiation → auto-fallback to mock
2. Structured generation against `DiscoveryOutput`-style schemas
3. A/B comparison of two providers (`ABTestFramework` → wins/ties/confidence)
4. Markdown report generation + failure analysis
5. Prompt versioning — register, diff, tag, rollback, history
6. Cost + metrics collection

---

## 📂 Project Structure

```
ai-engineering-orchestrator/
│
├── apps/
│   ├── api/                          # FastAPI backend
│   │   ├── src/
│   │   │   ├── main.py               # App entry, middleware, routers, lifespan
│   │   │   ├── config.py             # Pydantic-settings configuration
│   │   │   ├── logger.py             # Structlog setup
│   │   │   ├── middleware/           # RequestID + rate-limit middleware
│   │   │   ├── models/               # SQLAlchemy models (Project, database)
│   │   │   ├── routers/              # health · projects · workflows · eval · audit
│   │   │   └── websocket_manager.py  # Per-project WebSocket broadcasting
│   │   └── tests/                    # API test suite
│   │
│   └── web/                          # React control center
│       └── src/
│           ├── api/client.ts         # Typed API client (NetworkError/ApiError)
│           ├── components/           # Layout, ErrorBoundary, Loading
│           ├── pages/                # Dashboard · Projects · Workflow · NotFound
│           └── types/                # Shared TypeScript models
│
├── orchestration/                    # THE AI ENGINE
│   ├── agents/                       # CEO · Product Manager · Architect
│   │                                 # Backend · Frontend · Testing engineers
│   ├── tools/                        # Sandboxed file-system tools
│   ├── graph.py                      # LangGraph state machine + orchestration
│   ├── state.py                      # Phase, TaskItem, ApprovalRequest, ProjectState
│   ├── llm.py · llm_provider.py      # Provider abstraction + auto mock-fallback
│   ├── llm_*.py                      # 40+ module LLM layer
│   │   ├── cache · cost · metrics · monitor · profiler · debugger
│   │   ├── router · scheduler · streaming · retry · parser · normalizer
│   │   ├── validator · enforcer · filter · middleware · hooks
│   │   └── factory · registry · config · secrets · events
│   ├── eval_dataset.py               # EvalCase / EvalDataset (JSON+CSV)
│   ├── eval_reporting.py             # EvalReport / ReportComparison (markdown)
│   ├── eval_ab_testing.py            # ABTestFramework
│   ├── prompt_registry.py            # Versioned, diffable, rollback-able prompts
│   ├── audit.py                      # Structured audit logging
│   ├── tracing.py · webhooks.py      # OpenTelemetry spans · webhook notifications
│   └── tests/                        # Orchestration + LLM test suite
│
├── infrastructure/                   # Infrastructure-as-code
├── .github/workflows/                # ci.yml · lint.yml · deploy.yml
├── docker-compose.yml                # Local dev (postgres + redis + api + web)
├── docker-compose.prod.yml           # Production profile
├── docker-compose.override.yml       # Dev overrides (hot reload)
├── Makefile                          # Dev workflow commands
└── docs/architecture.md              # Detailed design notes
```

---

## 🗺️ Roadmap

| # | Status | Description |
|---|--------|-------------|
| 1 | ✅ Done | Monorepo scaffold — FastAPI + React + Docker + CI |
| 2 | ✅ Done | LangGraph orchestration engine — planning agents, streaming |
| 3 | ✅ Done | Engineering agents — Backend/Frontend/QA + file I/O tools |
| 4 | ✅ Done | Human-in-the-loop — approvals, rollback, observability |
| 5 | ✅ Done | Real LLM integration — provider layer, eval harness, A/B testing |
| 6 | ✅ Done | Security audit — vulnerability scanning, secret management |
| 7 | ✅ Done | Production deployment — Docker Compose, monitoring, auto-scaling |

**Post-MVP ideas:** multi-provider support (Anthropic/Gemini) through the existing factory, persistent workflow checkpointing to PostgreSQL, vector-similarity task retrieval with pgvector, and a live workflow timeline in the dashboard.

---

## 🤝 Contributing

We welcome contributions! Please start by reading [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md).

1. **Branch** — create a feature branch from `develop`: `git checkout -b feature/your-feature`
2. **Commit** — use [conventional commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `chore:`
3. **Verify** — run `make lint && make test`; both must pass
4. **PR** — open a pull request against `develop`

Every PR is gated by the CI pipeline (lint + tests). See [docs/architecture.md](docs/architecture.md) for design details.

---

## 📄 License

Distributed under the [MIT License](LICENSE). Report security issues per our [SECURITY.md](SECURITY.md) policy.

<sub>Built with LangGraph, FastAPI, React — and a fleet of autonomous agents.</sub>
