"""Phase 2 — Eval sweep across prompt variants using the deterministic mock.

Runs the full OrchestrationEngine pipeline against 10 concrete prompt variants
(maintaining GROWING project breadth:
   auth on/off, frontend on/off, CRUD resource naming variety),
captures per-phase wall-clock timing + generated-tree shape for each variant,
then executes each *generated* project's own pytest suite (using the repo venv,
which already has the runtime deps) to prove the output runs.

Shapes the results into an ``EvalDataset`` / ``EvalReport`` and writes:
    docs/eval-report-v1.{md,json}   — the Phase 2 deliverable
    docs/eval-dataset-v1.json       — the dataset used, for reproducibility
    docs/eval-sweep-raw.json        — per-case evidence (trees, timing, tests)

Usage:
    $env:PYTHONPATH="<repo-root>"; .venv/Scripts/python scripts/eval_sweep.py
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from orchestration.eval_dataset import EvalCase, EvalDataset, EvalResult
from orchestration.eval_reporting import EvalReport
from orchestration.graph import OrchestrationEngine
from orchestration.llm import LLMProvider
from orchestration.state import Phase, ProjectState

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRATCH_ROOT = REPO_ROOT / "examples" / "eval-sweep"
DOCS_DIR = REPO_ROOT / "docs"

MODEL_LABEL = "gpt-4o (mock)"
PROVIDER_LABEL = "deterministic-mock"
MODE = "mock"
GPT4O_INPUT_1M = 2.50
GPT4O_OUTPUT_1M = 10.00


class SweepProvider(LLMProvider):
    """Deterministic-mock provider identical to the Phase 1 instrumented one."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calls: list[dict] = []

    async def generate_structured(self, system_prompt, user_prompt, response_model):
        self._last_user_prompt = user_prompt
        start = time.monotonic()
        result = self._mock(response_model)
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        self.calls.append({
            "response_model": response_model.__name__,
            "mode": MODE,
            "latency_ms": latency_ms,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        })
        return result

    @property
    def summary(self) -> dict:
        return {
            "total_calls": len(self.calls),
            "mode": MODE,
            "total_tokens": 0,
            "est_cost_usd": 0.0,
            "avg_latency_ms": round(
                sum(c["latency_ms"] for c in self.calls) / len(self.calls), 2
            ) if self.calls else 0.0,
        }


def clean_dir(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)


def snapshot_tree(root: Path) -> list[dict]:
    files = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if ".venv" in p.parts or "__pycache__" in p.parts or rel.endswith((".pyc", ".db")):
            continue
        files.append({
            "path": rel,
            "size_bytes": p.stat().st_size,
        })
    return files


async def run_pipeline(
    provider: SweepProvider,
    prompt: str,
    case_dir: Path,
) -> tuple[dict, list[dict], float]:
    clean_dir(case_dir)
    state = ProjectState(
        project_id=uuid4(),
        name="Eval case project",
        description=prompt,
        phase=Phase.DISCOVERY,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    engine = OrchestrationEngine(llm=provider, project_root=str(case_dir))
    import orchestration.graph as graph_mod

    final = dict(graph_mod._project_to_graph(state))
    phases: list[dict] = []
    phase_t0 = time.monotonic()
    t_start = time.monotonic()
    async for event in engine.run_stream(state):
        node = next(iter(event.keys()), None)
        if node == "__start__":
            continue
        phases.append({"node": node, "wall_ms": round((time.monotonic() - phase_t0) * 1000, 2)})
        phase_t0 = time.monotonic()
        payload = event.get(node)
        if isinstance(payload, dict):
            final.update(payload)
    total_ms = round((time.monotonic() - t_start) * 1000, 2)
    return final, phases, total_ms


def run_generated_tests(project_dir: Path) -> dict:
    attempt = {"attempted": True, "command": None, "returncode": None,
               "passed": None, "failed": None, "skipped": None, "output_tail": ""}
    cmd = [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"]
    attempt["command"] = " ".join(cmd)
    try:
        r = subprocess.run(
            cmd, cwd=str(project_dir), capture_output=True, timeout=300,
            env={**os.environ, "PYTHONPATH": str(project_dir)},
        )
    except subprocess.TimeoutExpired:
        attempt["output_tail"] = "[test run timed out]"
        return attempt
    attempt["returncode"] = r.returncode
    out = (r.stdout or b"").decode(errors="replace") + (r.stderr or b"").decode(errors="replace")
    attempt["output_tail"] = out[-800:]
    m = re.search(r"(\d+) passed(?:\s*, (\d+) skipped)?(?:\s*, (\d+) failed)?", out)
    if m:
        attempt["passed"] = int(m.group(1))
        attempt["skipped"] = int(m.group(2)) if m.group(2) else 0
        attempt["failed"] = int(m.group(3)) if m.group(3) else 0
    return attempt


def check_spec(metadata: dict, paths: list[str]) -> tuple[bool, list[str]]:
    problems: list[str] = []
    table, has_auth, has_frontend = (
        metadata["table"], metadata["has_auth"], metadata["has_frontend"],
    )
    if not any(p.endswith(f"test_{table}.py") for p in paths):
        problems.append(f"missing tests/test_{table}.py (expected table '{table}')")
    if has_auth:
        if not any(p.endswith("auth.py") for p in paths):
            problems.append("auth = True but no auth.py generated")
    else:
        if any(p.endswith("auth.py") for p in paths):
            problems.append("auth = False but auth.py generated")
    if has_frontend:
        if not any(p.startswith("frontend/") for p in paths):
            problems.append("frontend = True but no frontend/ files generated")
    else:
        if any(p.startswith("frontend/") for p in paths):
            problems.append("frontend = False but frontend/ files generated")
    return (len(problems) == 0, problems)


def tree_hashes(root: Path) -> list[str]:
    return [
        hashlib.sha256(
            p.read_bytes() if p.is_file() else b""
        ).hexdigest() + ":" + p.relative_to(root).as_posix()
        for p in sorted(root.rglob("*"))
        if p.is_file() and ".venv" not in p.parts and "__pycache__" not in p.parts
        and not str(p).endswith((".pyc", ".db"))
    ]


def build_cases() -> list[EvalCase]:
    raw = [
        {
            "name": "todos_auth_fastapi",
            "prompt": (
                "Build a REST API for a todo list. Features: create/list/update/delete todos, "
                "mark complete, and user authentication with JWT tokens. "
                "Use FastAPI + SQLAlchemy. Include tests."
            ),
            "table": "todos", "has_auth": True, "has_frontend": False,
            "tags": ["crud", "auth", "tests"],
        },
        {
            "name": "notes_public_noauth",
            "prompt": (
                "Build a single-user notes app. CRUD for notes, public, no signup, no login "
                "needed. FastAPI backend only. Include tests."
            ),
            "table": "notes", "has_auth": False, "has_frontend": False,
            "tags": ["crud", "noauth", "tests"],
        },
        {
            "name": "products_catalog_backend",
            "prompt": (
                "Build a product catalog REST API using FastAPI. CRUD on products with prices "
                "and stock. Backend only, no auth. Include pytest tests."
            ),
            "table": "products", "has_auth": False, "has_frontend": False,
            "tags": ["crud", "noauth", "tests"],
        },
        {
            "name": "blog_posts_frontend",
            "prompt": (
                "Build a blog platform: REST API for posts and comments plus a React web "
                "frontend listing posts. No user accounts. FastAPI backend. Include tests."
            ),
            "table": "posts", "has_auth": False, "has_frontend": True,
            "tags": ["crud", "noauth", "frontend", "tests"],
        },
        {
            "name": "task_board_fullstack",
            "prompt": (
                "Build a task management web app with React: users log in with password, "
                "tasks have titles and due dates. FastAPI + SQLAlchemy. Include tests."
            ),
            "table": "tasks", "has_auth": True, "has_frontend": True,
            "tags": ["crud", "auth", "frontend", "tests"],
        },
        {
            "name": "inventory_items_noauth",
            "prompt": (
                "Build an inventory REST API to manage items and quantities. API only, "
                "no UI, no authentication. Include a test suite."
            ),
            "table": "items", "has_auth": False, "has_frontend": False,
            "tags": ["crud", "noauth", "tests"],
        },
        {
            "name": "orders_public_fallback",
            "prompt": (
                "Build an orders REST API. Public endpoints, no auth. FastAPI. Include tests."
            ),
            "table": "items", "has_auth": False, "has_frontend": False,
            "tags": ["crud", "noauth", "tests", "resource_fallback"],
        },
        {
            "name": "notes_no_security_gate",
            "prompt": (
                "Generate a FastAPI CRUD service for notes. Single user, no password, "
                "no session login. No automated checks are required for this deliverable."
            ),
            "table": "notes", "has_auth": False, "has_frontend": False,
            "tags": ["crud", "noauth"],
        },
        {
            "name": "todos_api_ui",
            "prompt": (
                "Build a REST API for a todo list plus a simple UI page listing todos. "
                "Public read-only, no login. FastAPI."
            ),
            "table": "todos", "has_auth": False, "has_frontend": True,
            "tags": ["crud", "noauth", "frontend"],
        },
        {
            "name": "products_admin_auth",
            "prompt": (
                "Build a products REST API with admin users, login and JWT protection for "
                "write operations. FastAPI + SQLAlchemy. Write pytest tests."
            ),
            "table": "products", "has_auth": True, "has_frontend": False,
            "tags": ["crud", "auth", "tests"],
        },
    ]
    cases = []
    for r in raw:
        metadata = {k: r[k] for k in ("table", "has_auth", "has_frontend")}
        cases.append(EvalCase(
            name=r["name"],
            prompt=r["prompt"],
            expected={
                "final_phase": "completed",
                "spec": metadata,
                "generated_tests_pass": True,
            },
            tags=r["tags"],
            metadata=metadata,
        ))
    return cases


async def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    dataset = EvalDataset(name="Mock Controller Sweep v1", cases=build_cases())
    dataset.to_json(str(DOCS_DIR / "eval-dataset-v1.json"))

    provider = SweepProvider()
    provider.client = None  # force mock, same as proof run
    print(f"Sweep: {len(dataset)} cases | mode={MODE} | scratch={SCRATCH_ROOT}\n")

    results: list[EvalResult] = []
    raw_evidence: list[dict] = []

    for i, case in enumerate(dataset.cases, 1):
        case_dir = SCRATCH_ROOT / case.name
        t0 = time.monotonic()
        result, phases, total_ms = await run_pipeline(provider, case.prompt, case_dir)
        tree = snapshot_tree(case_dir)
        paths = [f["path"] for f in tree]

        spec_ok, spec_problems = check_spec(case.metadata, paths)

        print(f"[{i:02d}] {case.name}")
        print(f"       final_phase={result.get('phase')} errors={len(result.get('errors', []))} "
              f"tasks={len(result.get('tasks', []))} files={len(tree)} wall={total_ms}ms")
        print(f"       spec_ok={spec_ok} {'| problems: ' + '; '.join(spec_problems) if not spec_ok else ''}")

        test_run = run_generated_tests(case_dir)
        tests_ok = (
            test_run["returncode"] == 0
            and (test_run.get("failed") or 0) == 0
            and (test_run.get("passed") or 0) >= 1
        )
        print(f"       generated tests: passed={test_run.get('passed')} "
              f"failed={test_run.get('failed')} skipped={test_run.get('skipped')} "
              f"rc={test_run['returncode']} trials={round(time.monotonic() - t0, 2)}s")

        completed = result.get("phase") == "completed"
        no_errors = len(result.get("errors", [])) == 0

        score = 0.25 * int(completed) + 0.25 * int(no_errors) \
            + 0.25 * int(tests_ok) + 0.25 * int(spec_ok)
        passed = completed and no_errors and tests_ok and spec_ok

        evidence = {
            "final_phase": result.get("phase"),
            "phase_history": [h.get("phase") for h in result.get("phase_history", [])],
            "phase_timing_ms": phases,
            "pipeline_wall_ms": total_ms,
            "decisions": len(result.get("decisions", [])),
            "tasks": len(result.get("tasks", [])),
            "errors": [e.get("error") if isinstance(e, dict) else str(e) for e in result.get("errors", [])],
            "generated_files": tree,
            "spec_check": {"expected": case.metadata, "ok": spec_ok, "problems": spec_problems},
            "generated_test_run": test_run,
            "llm_calls": len(provider.calls),
            "mode": MODE,
            "cost_usd": 0.0,
            "tokens": 0,
        }
        raw_evidence.append({"case": case.name, "evidence": evidence})
        results.append(EvalResult(
            case=case,
            passed=passed,
            score=round(score, 4),
            latency_ms=round(total_ms, 2),
            actual=evidence,
            tokens_used=0,
            cost=0.0,
        ))
        print("")

    report = EvalReport(dataset, results, model=MODEL_LABEL, provider_name=PROVIDER_LABEL)

    # Determinism check: same prompt + same mock provider -> byte-identical tree.
    det0_dir = SCRATCH_ROOT / "determinism_run1"
    det1_dir = SCRATCH_ROOT / "determinism_run2"
    det_case = dataset.cases[0]
    await run_pipeline(provider, det_case.prompt, det0_dir)
    first_hashes = tree_hashes(det0_dir)
    await run_pipeline(provider, det_case.prompt, det1_dir)
    second_hashes = tree_hashes(det1_dir)
    deterministic = first_hashes == second_hashes
    print(f"Determinism (re-running '{det_case.name}'): "
          f"{'PASS — byte-identical generated tree' if deterministic else 'FAIL — trees differ'}")

    (DOCS_DIR / "eval-sweep-raw.json").write_text(
        json.dumps(raw_evidence, indent=2, default=str), encoding="utf-8")
    report.to_json(str(DOCS_DIR / "eval-report-v1.json"))

    md = report.to_markdown()
    appendix = [
        "",
        "",
        "## Appendix: determinism",
        "",
        f"Ran `{det_case.name}` twice through the pipeline with the identical mock provider "
        f"and compared SHA-256 hashes of every generated file. Result: "
        f"**{('byte-identical' if deterministic else 'DIFFERENT')}**.",
        "",
        "## Appendix: honesty notes",
        "",
        f"- Mode is `{MODE}`: the provider returns deterministic template content, so `cost=$0.00`, "
        "`tokens=0`, and latency reflects mock execution, not a real LLM.",
        "- Real mode is blocked (API key holds no quota; every real call returns HTTP 429) — "
        "no warm-start or real-LLM numbers were attempted for this sweep.",
        "- `tests` are generated unconditionally by the mock controller for every case; "
        "prompts that asked to skip a quality gate still yield a test file.",
        "- The `orders_public_fallback` case exercises resource-model fallback: 'orders' is not "
        "in the mock's resource vocabulary, so the controller falls back to the default "
        "`Item`/`items` model/table.",
        "- Generated-test failures can carry framework warnings (PyJWT key-length, "
        "Starlette deprecation) that are non-fatal and do not fail the suite.",
    ]
    for line in appendix:
        md += line + "\n"

    (DOCS_DIR / "eval-report-v1.md").write_text(md, encoding="utf-8")

    print("\n# Report")
    print(f"pass_rate={report.pass_rate:.1%} passed={report.passed}/{report.total} "
          f"avg_latency={report.avg_latency:.1f}ms cost=${report.total_cost} "
          f"tokens={report.total_tokens}")
    print("Header and per-case table -> docs/eval-report-v1.md")
    print("Wrote -> docs/eval-report-v1.md")
    print("Wrote -> docs/eval-report-v1.json")
    print("Wrote -> docs/eval-dataset-v1.json")
    print("Wrote -> docs/eval-sweep-raw.json")


if __name__ == "__main__":
    asyncio.run(main())