# AI Engineering Orchestrator

A multi-agent AI system that autonomously transforms high-level software ideas into complete, tested, documented, and deployable projects. Built with LangGraph, FastAPI, React, and PostgreSQL.

## Architecture

```
User Input → CEO Agent → Product Manager → Architect → Engineering Agents → QA → Deploy
                │             │               │             │              │
                ▼             ▼               ▼             ▼              ▼
           Discovery     Requirements    Architecture    Code Gen      Tests/CI
```

### Agent Pipeline

| Agent | Responsibility | Output |
|-------|---------------|--------|
| **CEO** | Analyzes requests, decomposes tasks, delegates work | Project plan, task list |
| **Product Manager** | Defines requirements, user stories, MVP scope | PRD document |
| **Architect** | Designs system architecture, tech stack, API schema | Architecture spec |
| **Backend Engineer** | Generates FastAPI models, routers, middleware | Production Python code |
| **Frontend Engineer** | Generates React components, hooks, pages | Production TypeScript code |
| **Testing Engineer** | Generates pytest + Vitest suites, fixtures | Test files |

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Orchestration** | LangGraph (state machine with cycles, checkpointing, streaming) |
| **Backend** | FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| **Frontend** | React 19, TypeScript, React Router, Tailwind CSS |
| **Database** | PostgreSQL + pgvector, Redis |
| **AI/LLM** | OpenAI structured outputs (with mock fallback for development) |
| **Infrastructure** | Docker Compose, GitHub Actions CI |

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+

### Setup

```bash
# Clone the repository
git clone https://github.com/Alaashamel/ai-engineering-orchestrator.git
cd ai-engineering-orchestrator

# Install dependencies
make api-deps        # Python backend
make web-deps        # Node frontend

# Configure environment
cp .env.example .env
# Edit .env with your LLM_API_KEY (optional — mock mode works without it)

# Start infrastructure (requires Docker)
make db-up           # PostgreSQL + Redis

# Run the application (two terminals)
make dev-api         # http://localhost:8000
make dev-web         # http://localhost:5173
```

### Run Tests

```bash
make test            # 13 tests — orchestration, agents, tools, health
make lint            # Ruff + TypeScript type checking
```

### Without Docker

If Docker isn't available, the API starts without database dependencies:

```bash
make dev-api         # Runs in degraded mode — project/workflow endpoints work
make dev-web         # Full frontend experience
```

## Project Structure

```
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── src/
│   │   │   ├── models/         # SQLAlchemy models
│   │   │   ├── routers/        # REST + WebSocket endpoints
│   │   │   └── main.py         # App entry point
│   │   └── tests/              # Backend test suite
│   └── web/                    # React frontend
│       └── src/
│           ├── api/            # API client
│           ├── components/     # Shared components
│           └── pages/          # Route pages
├── orchestration/              # AI orchestration engine
│   ├── agents/                 # Agent implementations (6 agents)
│   ├── tools/                  # Sandboxed tool layer
│   ├── graph.py               # LangGraph state machine
│   ├── llm.py                 # LLM provider abstraction
│   └── state.py               # Typed state models
├── infrastructure/            # Terraform / Pulumi IaC
├── .github/workflows/        # CI pipeline
└── docker-compose.yml        # Local development services
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health check |
| `GET` | `/` | Root welcome |
| `GET` | `/projects` | List all projects |
| `POST` | `/projects` | Create a project |
| `GET` | `/projects/{id}` | Get project details |
| `PATCH` | `/projects/{id}` | Update project |
| `DELETE` | `/projects/{id}` | Delete project |
| `POST` | `/workflows/{id}/start` | Start AI orchestration |
| `GET` | `/workflows/{id}/status` | Get workflow state |
| `WS` | `/workflows/ws/{id}` | Real-time workflow stream |

## Milestones

| # | Status | Description |
|---|--------|-------------|
| 1 | ✅ Done | Monorepo scaffold, FastAPI + React + Docker + CI |
| 2 | ✅ Done | LangGraph orchestration engine, 4 planning agents, streaming |
| 3 | ✅ Done | Engineering agents (Backend/Frontend/QA), file I/O tools |
| 4 | 🔲 Planned | Human-in-the-loop approvals, observability (OpenTelemetry) |
| 5 | 🔲 Planned | Real LLM integration, evaluation harness, regression tests |
| 6 | 🔲 Planned | Security audit, vulnerability scanning, secret management |
| 7 | 🔲 Planned | Production deployment, monitoring, auto-scaling |

## Contributing

1. Create a feature branch from `develop`: `git checkout -b feature/your-feature`
2. Commit changes with conventional commits (`feat:`, `fix:`, `docs:`, etc.)
3. Run `make lint && make test` to verify
4. Open a pull request to `develop`

## License

MIT
