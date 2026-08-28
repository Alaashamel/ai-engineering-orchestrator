"""Phase 5 — 60-second terminal walkthrough of the API scaffold generator.

Runs the canonical Todo List prompt through the full multi-agent pipeline in
mock mode (no API key required), then replays the run as an animated,
step-by-step terminal demo:

    prompt -> phases -> agent decisions -> task plan -> approval gate
            -> generated file tree -> generated project's own test suite

This is the projector-ready version of ``scripts/prove_core_loop.py``:
same engine, same evidence, but paced for a live walkthrough.

Usage:
    $env:PYTHONPATH="<repo-root>"; .venv/Scripts/python scripts/walkthrough.py
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from scripts.eval_sweep import (
    SweepProvider,
    run_generated_tests,
    run_pipeline,
    snapshot_tree,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CASE_DIR = REPO_ROOT / "examples" / "walkthrough"
PROMPT = (
    "Build a REST API for a todo list. Features: create/list/update/delete todos, "
    "mark complete, and user authentication with JWT tokens. "
    "Use FastAPI + SQLAlchemy. Include tests."
)

PHASE_BANNERS = {
    "discovery": "CEO analyzes the request",
    "planning": "Product Manager writes the PRD",
    "architecture": "Architect designs the system",
    "task_decomposition": "CEO decomposes the plan into tasks",
    "check_approvals": "Human-in-the-loop gate",
    "implementation": "Engineering agents write files",
    "complete": "Workflow complete",
    "completed": "Workflow complete",
}


def print_step(text: str) -> None:
    print(f"  {text}")


async def main() -> None:
    print("=" * 72)
    print("AI ENGINEERING ORCHESTRATOR - API SCAFFOLD GENERATOR WALKTHROUGH")
    print("=" * 72)
    print(f"\n[Prompt]\n  {PROMPT}\n")

    provider = SweepProvider()
    provider.client = None  # deterministic mock, zero credentials

    result, phases, total_ms = await run_pipeline(provider, PROMPT, CASE_DIR)

    print("[Pipeline]\n")
    for phase in result.get("phase_history", []):
        name = phase.get("phase", "?")
        banner = PHASE_BANNERS.get(name, name)
        print(f"   > {name:20s}  {banner}")
        await asyncio.sleep(0.45)

    print("\n[Key decisions]")
    for d in result.get("decisions", [])[:3]:
        text = d.get("reasoning") or d.get("title") if isinstance(d, dict) else str(d)
        print_step(f"- {text}")

    await asyncio.sleep(0.3)

    tasks = result.get("tasks", [])
    print(f"\n[Task plan] {len(tasks)} tasks")
    for t in tasks:
        agent = t.get("agent", "?") if isinstance(t, dict) else "?"
        title = t.get("title", "?") if isinstance(t, dict) else str(t)
        print_step(f"- [{agent:18s}] {title}")
    await asyncio.sleep(0.3)

    pending = result.get("pending_approvals", [])
    print(f"\n[Approval gate] {len(pending)} approval record(s) raised for critical tasks")
    for a in pending:
        action = a.get("action", "") if isinstance(a, dict) else str(a)
        action = action.replace("Execute task: ", "")
        print_step(f"- pending approval: {action}")
    await asyncio.sleep(0.3)

    files = snapshot_tree(CASE_DIR)
    print(f"\n[Generated files] {len(files)} written under examples/walkthrough/")
    for f in files[:16]:
        print_step(f"- {f['path']}  ({f['size_bytes']} B)")
    await asyncio.sleep(0.3)

    print("\n[Quality gate] running the generated project's own test suite")
    test_run = run_generated_tests(CASE_DIR)
    summary = (
        f"passed={test_run.get('passed')} failed={test_run.get('failed')} "
        f"skipped={test_run.get('skipped')} returncode={test_run['returncode']}"
    )
    status = "PASS" if (test_run.get("passed") and (test_run.get("failed") or 0) == 0) else "FAIL"
    print(f"  {status} - {summary}")

    evidence = {
        "prompt": PROMPT,
        "mode": "mock",
        "final_phase": result.get("phase"),
        "phase_history": result.get("phase_history", []),
        "tasks": tasks,
        "pending_approvals": pending,
        "generated_test_run": test_run,
        "total_wall_ms": total_ms,
        "llm_calls": len(provider.calls),
    }
    (CASE_DIR / "walkthrough-log.json").write_text(
        json.dumps(evidence, indent=2, default=str), encoding="utf-8")

    print("\n" + "=" * 72)
    print("Full run evidence -> examples/walkthrough/walkthrough-log.json")
    print("Phase 1 report  -> examples/todo-api/RESULT.md")
    print("Eval sweep      -> docs/eval-report-v1.md")
    print("=" * 72)


if __name__ == "__main__":
    asyncio.run(main())