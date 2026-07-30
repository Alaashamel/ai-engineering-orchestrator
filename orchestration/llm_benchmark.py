from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class LLMBenchmarkResult:
    model: str
    test_name: str
    latency_ms: float
    tokens_used: int
    cost: float
    passed: bool
    score: float
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            from datetime import datetime, timezone
            self.timestamp = datetime.now(timezone.utc).isoformat()


class LLMBenchmarkSuite:
    def __init__(self):
        self.results: list[LLMBenchmarkResult] = []

    def add_result(self, result: LLMBenchmarkResult) -> None:
        self.results.append(result)

    def get_summary(self) -> dict[str, Any]:
        if not self.results:
            return {"total": 0, "passed": 0, "failed": 0}

        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        avg_latency = sum(r.latency_ms for r in self.results) / total
        total_cost = sum(r.cost for r in self.results)
        total_tokens = sum(r.tokens_used for r in self.results)

        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total,
            "avg_latency_ms": round(avg_latency, 2),
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "results": [
                {
                    "model": r.model,
                    "test_name": r.test_name,
                    "latency_ms": r.latency_ms,
                    "tokens_used": r.tokens_used,
                    "cost": r.cost,
                    "passed": r.passed,
                    "score": r.score,
                }
                for r in self.results
            ],
        }

    def compare_models(
        self, model_a: str, model_b: str
    ) -> dict[str, Any]:
        results_a = [r for r in self.results if r.model == model_a]
        results_b = [r for r in self.results if r.model == model_b]

        avg_a = (
            sum(r.latency_ms for r in results_a) / len(results_a)
            if results_a
            else 0
        )
        avg_b = (
            sum(r.latency_ms for r in results_b) / len(results_b)
            if results_b
            else 0
        )
        cost_a = sum(r.cost for r in results_a)
        cost_b = sum(r.cost for r in results_b)
        pass_rate_a = (
            sum(1 for r in results_a if r.passed) / len(results_a)
            if results_a
            else 0
        )
        pass_rate_b = (
            sum(1 for r in results_b if r.passed) / len(results_b)
            if results_b
            else 0
        )

        return {
            "model_a": model_a,
            "model_b": model_b,
            "avg_latency_a_ms": round(avg_a, 2),
            "avg_latency_b_ms": round(avg_b, 2),
            "total_cost_a": round(cost_a, 4),
            "total_cost_b": round(cost_b, 4),
            "pass_rate_a": round(pass_rate_a, 4),
            "pass_rate_b": round(pass_rate_b, 4),
            "winner": model_a if pass_rate_a >= pass_rate_b else model_b,
        }