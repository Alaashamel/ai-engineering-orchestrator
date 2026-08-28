# Phase 1 — Core Loop Proof: Todo REST API

**Date:** 2026-08-28 · **Mode:** mock LLM (`--force-mock`) · **Model id:** `gpt-4o`
**Evidence:** `phase-log.json` (full state, per-node timing, tree, test output) · `test-results.txt`

## Prompt under test

> Build a REST API for a todo list. Features: create/list/update/delete todos,
> mark complete, and user authentication with JWT tokens. Use FastAPI +
> SQLAlchemy. Include tests.

## Outcome

| Metric | Value |
| --- | --- |
| Final phase | `completed` |
| Phases visited | discovery → planning → architecture → task_decomposition → implementation → completed |
| Errors | 0 |
| Tasks decomposed | 6 (4 backend, 1 qa, 1 frontend) — all completed |
| Approval requests recorded | 3 (one per critical task, no duplicates) |
| Files generated | 14 |
| **Generated project's own test suite** | **6 passed, 0 failed** (exit 0, dedicated venv) |
| LLM calls (mock mode) | 7 (one per agent artifact, 0 tokens, $0.00) |
| Total wall time | 269 ms |

## Generated tree (`examples/todo-api/`)

```
auth.py                     1543 B   JWT hashing/verification + get_current_user
database.py                  410 B   SQLAlchemy engine, session, declarative Base
main.py                      347 B   FastAPI app, create_all, routers, /health
models.py                    972 B   Todo + User models (Mapped annotations)
schemas.py                   835 B   Todo & User Pydantic request/response schemas
routers/__init__.py            0 B
routers/auth.py              1189 B  /auth/register, /auth/login
routers/resources.py         2015 B  Todo CRUD (protected) 
frontend/src/api.ts           176 B  typed fetch client
frontend/src/App.tsx          300 B  list page
tests/conftest.py             862 B  in-memory SQLite fixture (StaticPool)
tests/test_todos.py          1831 B  health, register/login, 401 gating, CRUD roundtrip, 404
README.md / requirements.txt
```

The generated project runs its **own test suite** and passes (auth-gated CRUD
roundtrip, 401-without-token, login, 404 path — see `test-results.txt`).

## Per-node wall time (mock mode)

```
discovery 13.3ms | planning 1.0ms | architecture 0.9ms | task_decomposition 0.7ms
check_approvals 0.5ms | implementation 231.2ms | check_approvals 0.9ms | complete 1.2ms
```

## What was actually proven

- The full pipeline runs end-to-end from prompt → discovery → planning →
  architecture → task decomposition → approval records → implementation and
  reaches `completed` with **zero errors**.
- Tasks emitted by the planner are assigned to the three agent types the
  implementation node can execute (`backend_engineer`, `frontend_engineer`,
  `qa_engineer`); all are handled and marked done.
- Critical-path approvals are **deduplicated** (exactly 3 records for 3 critical
  tasks; the bug where a second pass re-appended them is fixed in
  `orchestration/graph.py`).
- The generated FastAPI + SQLAlchemy + JWT service **imports and passes its own
  tests** on Python 3.13 in a clean project-local venv — the implementation
  output is not just files, it is *running software*.

## Fixes made this phase (so mock output actually works)

| File | Change |
| --- | --- |
| `orchestration/llm_mock.py` (new) | Deterministic, schema-valid mock generator for all six agent artifacts; emits runnable FastAPI/SQLAlchemy/JWT/pytest content. |
| `orchestration/llm_mock.py` | Architecture `api_design` no longer contains `None` entries. |
| `orchestration/llm_mock.py` | SQLAlchemy models use `Mapped['User | None']` forward-ref form; `owner`/`User` only emitted when auth is on. |
| `orchestration/llm_mock.py` | Auth schemas (`UserCreate/Read/Login`, `Token`) generated when auth is on. |
| `orchestration/llm_mock.py` | conftest uses `StaticPool` + shared in-memory engine (SQLite per-connection DBs otherwise break tests). |
| `orchestration/graph.py` | Approval checks only create records for pending critical tasks not already tracked (no duplicates, no stale `human_approval_needed`). |
| `orchestration/llm.py` | `_mock` prefers the realistic builder, falls back to generic filler for unknown models. |
| `scripts/prove_core_loop.py` | Per-node timing, real-token/cost accounting skeleton, full-tree snapshot, generated-test runner, stale-file cleanup. |

## Honest limitations (not yet proven)

- **Mock-only.** Real mode is currently impossible: the `LLM_API_KEY` passes
  `models.list()` (118 models) but every generation call returns HTTP 429
  `insufficient_quota` on `gpt-4o`. A pre-fix real-mode run recorded 4 calls, 0
  real completions, 0 tokens, 0 files.
- **Frontend scaffold is not built or tested** — no Node toolchain is installed
  into the generated project's venv.
- **Approval gate is record-only through the API.** `OrchestrationEngine.run()`
  records approvals but never blocks on them; `start_workflow` does not pause.
- **Token/cost accounting is not wired into the real LLM path** — cost tracking
  exists (`orchestration/llm_provider.py`-adjacent trackers) but only inside the
  eval router/tests.
- Mock content is deterministic and template-driven: it exercises the *orchestra-
  tion*, not the *generation quality*. Phase 2 sweeps many prompts through the
  same harness to bound coverage and catch template regressions.

## How to reproduce

```powershell
$env:PYTHONPATH="<repo-root>"
.venv/Scripts/python scripts/prove_core_loop.py --force-mock
```