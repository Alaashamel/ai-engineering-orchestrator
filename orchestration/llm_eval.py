from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional

from pydantic import BaseModel


@dataclass
class EvalResult:
    test_name: str
    passed: bool
    expected: Any
    actual: Any
    score: float
    latency_ms: float
    error: Optional[str] = None


@dataclass
class EvalSuiteConfig:
    name: str
    test_cases: list[dict[str, Any]] = field(default_factory=list)
    baseline_model: str = "gpt-4o"
    comparison_model: Optional[str] = None
    tolerance: float = 0.95
    output_dir: str = "eval_results"


class LLEvalHarness:
    def __init__(self, config: EvalSuiteConfig):
        self.config = config
        self.results: list[EvalResult] = []

    def add_test_case(
        self,
        name: str,
        prompt: str,
        expected_output: Any,
        response_model: type[BaseModel],
    ) -> None:
        self.config.test_cases.append(
            {
                "name": name,
                "prompt": prompt,
                "expected": expected_output,
                "response_model": response_model,
            }
        )

    async def run(
        self, llm_provider: Any
    ) -> list[EvalResult]:
        self.results = []
        for tc in self.config.test_cases:
            result = await self._run_test_case(llm_provider, tc)
            self.results.append(result)
        return self.results

    async def _run_test_case(
        self, llm_provider: Any, tc: dict[str, Any]
    ) -> EvalResult:
        import time

        start = time.monotonic()
        try:
            output = await llm_provider.generate_structured(
                system_prompt="You are a helpful assistant.",
                user_prompt=tc["prompt"],
                response_model=tc["response_model"],
            )
            actual = output.model_dump() if hasattr(output, "model_dump") else output
            expected = tc["expected"]
            passed = self._compare(expected, actual)
            score = 1.0 if passed else 0.0
            error = None
        except Exception as exc:
            actual = None
            expected = tc.get("expected")
            passed = False
            score = 0.0
            error = str(exc)

        latency = (time.monotonic() - start) * 1000

        return EvalResult(
            test_name=tc["name"],
            passed=passed,
            expected=expected,
            actual=actual,
            score=score,
            latency_ms=round(latency, 2),
            error=error,
        )

    def _compare(self, expected: Any, actual: Any) -> bool:
        if expected is None or actual is None:
            return expected == actual
        if isinstance(expected, dict) and isinstance(actual, dict):
            for key in expected:
                if key not in actual:
                    return False
                if not self._compare(expected[key], actual[key]):
                    return False
            return True
        if isinstance(expected, list) and isinstance(actual, list):
            if len(expected) != len(actual):
                return False
            return all(
                self._compare(e, a) for e, a in zip(expected, actual)
            )
        return expected == actual

    def get_summary(self) -> dict[str, Any]:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        return {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0.0,
            "avg_latency_ms": (
                sum(r.latency_ms for r in self.results) / total
                if total > 0
                else 0.0
            ),
            "results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "score": r.score,
                    "latency_ms": r.latency_ms,
                    "error": r.error,
                }
                for r in self.results
            ],
        }