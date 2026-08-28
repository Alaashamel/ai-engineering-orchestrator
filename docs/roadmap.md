# Roadmap & Honest Status

> What is actually **proven by running the system** vs. what is **declared in the
> codebase / covered by unit tests but not yet demonstrated end-to-end**.
>
> Evidence for the "proven" tier:
> - Phase 1: [`examples/todo-api/RESULT.md`](../examples/todo-api/RESULT.md) — full
>   pipeline run, generated project, its own test suite green.
> - Phase 2: [`docs/eval-report-v1.md`](eval-report-v1.md) — 10-prompt sweep,
>   every generated project's tests pass, outputs byte-deterministic.
> - Unit/API suites: 224 passing across `orchestration/tests` + `apps/api/tests`
>   (see README "Testing & Evaluation").

## ✅ Proven by executing this repo (mock mode)

- Six-agent pipeline: discovery → planning → architecture → task decomposition →
  approval gate → implementation → complete (LangGraph state machine).
- Typed, schema-valid agent outputs (Pydantic) consumed programmatically.
- Automatic mock fallback when no API key / quota is exhausted.
- Backend file generation (FastAPI + SQLAlchemy + SQLite) that **compiles and
  passes its own pytest suite** (in-memory DB fixtures).
- Frontend scaffold generation (React/TS files) — generated but not built/run
  (no Node toolchain exercised).
- Approval records raised for critical tasks (create-only; see note below).
- Determinism: identical prompt + provider → byte-identical generated tree.
- Prompt registry (versions, diffs, tags, rollback) — unit-tested.
- Eval harness (`EvalDataset`, `EvalReport`, `ABTestFramework`) — unit-tested,
  and used to produce the Phase 2 report.
- HTTP API surface + middleware (request-id, CORS, rate limit) — unit-tested.

## 🧪 Declared / implemented but only unit-tested (not demonstrated live)

These exist as code with passing unit tests, but **no end-to-end run this
session proved them** under real conditions:

- **Real-LLM generation** — blocked in this workspace: the configured key passes
  `models.list()` but every completion returns HTTP 429 `insufficient_quota`.
  All pipeline runs in this repo's evidence are mock mode. `$` cost and token
  figures in reports are therefore **0 / not real**.
- **PostgreSQL 16 + pgvector persistence** — docker-compose defines it; tests
  that exercise it are skipped when no live DB is present (3 skipped in the API
  suite). Mock/e2e evidence above runs on SQLite in-memory/on-disk.
- **Redis 7** — defined in compose; degraded mode otherwise. No live run.
- **Webhooks** — `WebhookNotifier` + signature validation exist and are
  unit-tested; no real workflow run pushed an event to an external URL.
- **WebSocket streaming** — manager + endpoints are unit-tested; no live engine
  run broadcast `workflow_*` events end-to-end.
- **Cost & metrics tracking** — `LLMCostTracker` exists and is wired on the eval
  route; the engine path reports 0 tokens in mock mode, and there is no live
  real-mode run to populate it.
- **Approval "pause"** — the graph raises approval records; the API records and
  exposes them. Human-in-the-loop *pause/rollback* flows are API/schema-level and
  unit-tested, not exercised in a live dashboard session.
- **Security hardening** — `FileSystemTool` writes are constrained to the project
  root and edge cases are unit-tested; a full sandbox/privilege audit is not done.
- **Multi-provider (Anthropic / Gemini)**, **persistent workflow checkpointing**
  and **vector-similarity task retrieval** — noted in README as "next up";
  not implemented as demonstrated features yet.

## 🗺️ Proposed next milestones

| # | Milestone | Depends on |
|---|-----------|------------|
| 1 | Real-LLM pass: quota-backed key, run Phase 1 + Phase 2 sweeps, publish real token/cost/latency numbers | API key with quota |
| 2 | Postgres-backed persistence for projects/audit + healthcheck-gated API tests un-skip | Milestone 1 |
| 3 | Live demonstration: webhook delivery + WebSocket broadcasts during a mock run | — |
| 4 | Human approval loop E2E: pause → approve/reject with rollback through the dashboard | — |
| 5 | Multi-provider (Anthropic/Gemini) through the existing factory | Milestone 1 |
| 6 | Node-toolchain build of generated frontends (typecheck + build) | Node available |
| 7 | Checkpointing + pgvector task retrieval | Milestone 2 |

Everything above is tracked honestly: features ship to the README only when the
corresponding milestone above moves from "declared" to "proven".