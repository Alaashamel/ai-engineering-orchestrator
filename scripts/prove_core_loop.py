"""Phase 1 — Prove the core loop works end-to-end.

Runs the full OrchestrationEngine pipeline against one concrete prompt,
capturing per-phase wall-clock timing, real token usage/cost (if in real
mode), the generated file tree, and then executes the *generated* project's
own test suite to verify the output actually runs.

Usage:
    $env:PYTHONPATH="<repo-root>"; .venv/Scripts/python scripts/prove_core_loop.py
"""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from orchestration.graph import OrchestrationEngine
from orchestration.llm import LLMProvider
from orchestration.state import Phase, ProjectState

PROMPT = (
    "Build a REST API for a todo list. Features: create/list/update/delete "
    "todos, mark complete, and user authentication with JWT tokens. "
    "Use FastAPI + SQLAlchemy. Include tests."
)

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = REPO_ROOT / "examples" / "todo-api"

# gpt-4o pricing (USD per 1M tokens) as of 2026
GPT4O_INPUT_1M = 2.50
GPT4O_OUTPUT_1M = 10.00


class InstrumentedProvider(LLMProvider):
    """LLMProvider that records per-call mode, latency, and token usage."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calls: list[dict] = []
        self.fallback_count = 0

    async def generate_structured(self, system_prompt, user_prompt, response_model):
        self._last_user_prompt = user_prompt
        start = time.monotonic()
        mode = "mock"
        result = None
        usage = None
        if self.client:
            try:
                from openai import APIError, RateLimitError
                import orchestration.llm as llm_mod

                completion = await self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format=response_model,
                )
                raw = completion.choices[0].message.content
                if not raw:
                    raise ValueError("Empty LLM response")
                parsed = llm_mod._try_parse(raw, response_model)
                if parsed is None:
                    raise ValueError(f"JSON parsing failed: {raw[:200]}")
                usage = completion.usage
                result = parsed
                mode = "real"
            except (RateLimitError, APIError, ValueError):
                self.fallback_count += 1
                mode = "mock-fallback"

        if mode in ("mock", "mock-fallback"):
            result = self._mock(response_model)

        latency_ms = round((time.monotonic() - start) * 1000, 2)
        self.calls.append({
            "response_model": response_model.__name__,
            "mode": mode,
            "latency_ms": latency_ms,
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
        })
        return result

    @property
    def summary(self) -> dict:
        real = [c for c in self.calls if c["mode"] == "real"]
        total_token = sum(c["total_tokens"] for c in self.calls)
        cost = sum(
            c["prompt_tokens"] / 1_000_000 * GPT4O_INPUT_1M
            + c["completion_tokens"] / 1_000_000 * GPT4O_OUTPUT_1M
            for c in real
        )
        return {
            "total_calls": len(self.calls),
            "real_calls": len(real),
            "mock_fallback_calls": self.fallback_count,
            "total_tokens": total_token,
            "est_cost_usd": round(cost, 6),
            "avg_latency_ms": round(
                sum(c["latency_ms"] for c in self.calls) / len(self.calls), 2
            ) if self.calls else 0.0,
            "per_call": self.calls,
        }


EXCLUDED_ROOT_FILES = {
    "phase-log.json", "phase-log-real-attempt.json", "test-results.txt",
    "RESULT.md", ".gitkeep",
}


def is_runtime_byproduct(rel: str) -> bool:
    return rel.endswith(".db") or rel.endswith(".sqlite") or rel.endswith(".pyc")


def clean_generated(root: Path) -> None:
    """Remove generated files from previous runs, keeping evidence/log dirs."""
    kept_dirs = [root / ".venv"]
    for p in sorted(root.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(root).as_posix()
        if any(rel == (kd.relative_to(root).as_posix()) or rel.startswith((kd.relative_to(root).as_posix() + "/")) for kd in kept_dirs):
            continue
        if ".venv" in p.parts or "__pycache__" in p.parts:
            continue
        if rel in EXCLUDED_ROOT_FILES:
            continue
        p.unlink()


def snapshot_tree(root: Path) -> list[dict]:
    """Enumerate every generated file under root with relative path, size, content."""
    files = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if ".venv" in p.parts or "__pycache__" in p.parts:
            continue
        if rel.endswith(".pyc"):
            continue
        if rel in EXCLUDED_ROOT_FILES:
            continue
        if is_runtime_byproduct(rel):
            continue
        files.append({
            "path": rel,
            "size_bytes": p.stat().st_size,
            "content": p.read_text(encoding="utf-8", errors="replace"),
        })
    return files


def run_generated_tests() -> dict:
    """Run the generated project's own test suite in a dedicated venv."""
    report = {"attempted": False, "command": None, "returncode": None,
              "output": "", "passed": None, "failed": None, "skipped": None}
    req_file = PROJECT_ROOT / "requirements.txt"
    if not req_file.exists():
        report["output"] = ("No requirements.txt found in generated project — "
                            "cannot install runtime deps; skipping test run.")
        return report

    venv_dir = PROJECT_ROOT / ".venv"
    py = venv_dir / "Scripts" / "python.exe" if sys.platform == "win32" else venv_dir / "bin" / "python"
    pip = venv_dir / "Scripts" / "pip.exe" if sys.platform == "win32" else venv_dir / "bin" / "pip"

    report["attempted"] = True
    try:
        if not venv_dir.exists():
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)],
                           check=True, capture_output=True, timeout=120)
        dep_cmd = [
            str(pip), "install", "-q",
            "-r", str(req_file),
            "pytest", "pytest-asyncio", "httpx", "sqlalchemy",
        ]
        subprocess.run(dep_cmd, check=True, capture_output=True, timeout=600)
        report["pip_ok"] = True
    except subprocess.CalledProcessError as e:
        report["pip_ok"] = False
        report["output"] += f"pip install failed:\n{e.stderr.decode(errors='replace')[:2000]}"
        return report
    except subprocess.TimeoutExpired:
        report["pip_ok"] = False
        report["output"] += "pip install timed out."
        return report

    test_cmd = [str(py), "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"]
    report["command"] = " ".join(test_cmd)
    try:
        r = subprocess.run(
            test_cmd, cwd=str(PROJECT_ROOT), capture_output=True, timeout=900,
            env={**__import__("os").environ, "PYTHONPATH": str(PROJECT_ROOT)},
        )
        report["returncode"] = r.returncode
        report["output"] = (r.stdout or b"").decode(errors="replace") + \
                           (r.stderr or b"").decode(errors="replace")
        import re
        m = re.search(r"(\d+) passed(?:\s*, (\d+) skipped)?(?:\s*, (\d+) failed)?",
                      report["output"])
        if m:
            report["passed"] = int(m.group(1))
            report["skipped"] = int(m.group(2)) if m.group(2) else 0
            report["failed"] = int(m.group(3)) if m.group(3) else 0
    except subprocess.TimeoutExpired:
        report["output"] += "\n[test run timed out]"
    return report


async def main() -> None:
    force_mock = "--force-mock" in sys.argv
    if force_mock:
        print("WARNING: --force-mock set — will not attempt real LLM calls.")
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)

    provider = InstrumentedProvider()
    if force_mock:
        provider.client = None

    # Preserve evidence from a prior real-mode attempt if one exists.
    prior_log = PROJECT_ROOT / "phase-log.json"
    if prior_log.exists():
        shutil.copy2(prior_log, PROJECT_ROOT / "phase-log-real-attempt.json")
    clean_generated(PROJECT_ROOT)
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    mode = "mock" if not provider.client else "real"
    print(f"Mode: {mode} | model={provider.model}")
    print(f"Prompt: {PROMPT[:80]}...")
    print(f"Writing generated project to: {PROJECT_ROOT}")
    t_start = time.monotonic()

    state = ProjectState(
        project_id=uuid4(),
        name="Todo List REST API",
        description=PROMPT,
        phase=Phase.DISCOVERY,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )

    engine = OrchestrationEngine(llm=provider, project_root=str(PROJECT_ROOT))

    # Walk the graph node-by-node to capture real per-phase timing. This
    # langgraph build does not emit an "__end__" event, so we reconstruct the
    # final state by overlaying each node's returned update in order.
    import orchestration.graph as graph_mod
    final = dict(graph_mod._project_to_graph(state))
    phases: list[dict] = []
    phase_t0 = time.monotonic()
    try:
        async for event in engine.run_stream(state):
            node = next(iter(event.keys()), None)
            if node == "__start__":
                continue
            wall = round((time.monotonic() - phase_t0) * 1000, 2)
            phase_t0 = time.monotonic()
            payload = event.get(node)
            if isinstance(payload, dict):
                final.update(payload)
            if node == "__end__":
                inner = payload.get("__start__", payload) if isinstance(payload, dict) else payload
                if isinstance(inner, dict):
                    final.update(inner)
                continue
            phases.append({"node": node, "wall_ms": wall})
        result = final
    except Exception as e:
        print(f"Pipeline raised: {e}")
        raise

    total_ms = round((time.monotonic() - t_start) * 1000, 2)

    evidence = {
        "prompt": PROMPT,
        "mode": mode,
        "final_phase": result.get("phase"),
        "phase_history": result.get("phase_history", []),
        "phase_timing_ms": phases,
        "total_wall_ms": total_ms,
        "decisions": result.get("decisions", []),
        "tasks": result.get("tasks", []),
        "generated_files": result.get("generated_files", []),
        "errors": result.get("errors", []),
        "implementation_log": result.get("implementation_log", []),
        "human_approval_needed": result.get("human_approval_needed", False),
        "pending_approvals": result.get("pending_approvals", []),
        "requirements": result.get("requirements"),
        "architecture": result.get("architecture"),
        "llm": provider.summary,
    }

    tip = result.get("phase", "?")
    print(f"\nFinal phase: {result.get('phase')}")
    print(f"Phases visited: {[h.get('phase') for h in result.get('phase_history', [])]}")
    print(f"Tasks: {len(result.get('tasks', []))} | Errors: {len(result.get('errors', []))}")

    files = snapshot_tree(PROJECT_ROOT)
    evidence["tree"] = [{"path": f["path"], "size_bytes": f["size_bytes"]} for f in files]
    (PROJECT_ROOT / "phase-log.json").write_text(
        json.dumps(evidence, indent=2, default=str), encoding="utf-8")

    print(f"\nGenerated tree ({len(files)} files):")
    for f in files:
        print(f"  {f['path']}  ({f['size_bytes']} B)")

    print("\n--- Running generated project's own test suite ---")
    test_report = run_generated_tests()
    (PROJECT_ROOT / "test-results.txt").write_text(
        test_report["output"] or "(no output)", encoding="utf-8")
    summary_line = (f"attempted={test_report['attempted']} "
                    f"pip_ok={test_report.get('pip_ok')} "
                    f"returncode={test_report['returncode']} "
                    f"passed={test_report.get('passed')} "
                    f"failed={test_report.get('failed')} "
                    f"skipped={test_report.get('skipped')}")
    print(f"Generated tests: {summary_line}")
    print(test_report["output"][-1200:])

    evidence["generated_test_run"] = test_report
    (PROJECT_ROOT / "phase-log.json").write_text(
        json.dumps(evidence, indent=2, default=str), encoding="utf-8")

    print(f"\nEvidence saved -> examples/todo-api/phase-log.json")
    print(f"Test results    -> examples/todo-api/test-results.txt")


if __name__ == "__main__":
    asyncio.run(main())