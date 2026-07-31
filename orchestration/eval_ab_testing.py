from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Any

from orchestration.eval_dataset import EvalCase, EvalDataset, EvalResult


@dataclass
class ABTestResult:
    model_a: str
    model_b: str
    total_cases: int
    a_wins: int
    b_wins: int
    ties: int
    a_avg_latency: float
    b_avg_latency: float
    a_avg_score: float
    b_avg_score: float
    a_total_cost: float
    b_total_cost: float
    a_results: list[EvalResult] = field(default_factory=list)
    b_results: list[EvalResult] = field(default_factory=list)

    @property
    def winner(self) -> str:
        if self.a_wins > self.b_wins:
            return self.model_a
        if self.b_wins > self.a_wins:
            return self.model_b
        return "tie"

    @property
    def confidence(self) -> float:
        total = self.a_wins + self.b_wins + self.ties
        if total == 0:
            return 0.0
        margin = abs(self.a_wins - self.b_wins) / total
        return min(1.0, margin * 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_a": self.model_a,
            "model_b": self.model_b,
            "total_cases": self.total_cases,
            "a_wins": self.a_wins,
            "b_wins": self.b_wins,
            "ties": self.ties,
            "winner": self.winner,
            "confidence": round(self.confidence, 4),
            "a_avg_latency_ms": round(self.a_avg_latency, 2),
            "b_avg_latency_ms": round(self.b_avg_latency, 2),
            "a_avg_score": round(self.a_avg_score, 4),
            "b_avg_score": round(self.b_avg_score, 4),
            "a_total_cost": round(self.a_total_cost, 6),
            "b_total_cost": round(self.b_total_cost, 6),
        }


class ABTestFramework:
    def __init__(self, dataset: EvalDataset):
        self.dataset = dataset

    async def run(
        self,
        provider_a: Any,
        provider_b: Any,
        model_a_name: str = "model_a",
        model_b_name: str = "model_b",
    ) -> ABTestResult:
        a_results: list[EvalResult] = []
        b_results: list[EvalResult] = []

        for case in self.dataset.cases:
            result_a = await self._eval_case(provider_a, case)
            result_b = await self._eval_case(provider_b, case)
            a_results.append(result_a)
            b_results.append(result_b)

        a_wins = sum(
            1 for a, b in zip(a_results, b_results) if a.score > b.score
        )
        b_wins = sum(
            1 for a, b in zip(a_results, b_results) if b.score > a.score
        )
        ties = sum(
            1 for a, b in zip(a_results, b_results) if a.score == b.score
        )

        a_latencies = [r.latency_ms for r in a_results]
        b_latencies = [r.latency_ms for r in b_results]
        a_scores = [r.score for r in a_results]
        b_scores = [r.score for r in b_results]

        return ABTestResult(
            model_a=model_a_name,
            model_b=model_b_name,
            total_cases=len(self.dataset.cases),
            a_wins=a_wins,
            b_wins=b_wins,
            ties=ties,
            a_avg_latency=statistics.mean(a_latencies) if a_latencies else 0,
            b_avg_latency=statistics.mean(b_latencies) if b_latencies else 0,
            a_avg_score=statistics.mean(a_scores) if a_scores else 0,
            b_avg_score=statistics.mean(b_scores) if b_scores else 0,
            a_total_cost=sum(r.cost for r in a_results),
            b_total_cost=sum(r.cost for r in b_results),
            a_results=a_results,
            b_results=b_results,
        )

    async def _eval_case(
        self, provider: Any, case: EvalCase
    ) -> EvalResult:
        import time

        start = time.monotonic()
        try:
            if case.response_model:
                output = await provider.generate_structured(
                    system_prompt=case.system_prompt,
                    user_prompt=case.prompt,
                    response_model=case.response_model,
                )
                actual = output.model_dump() if hasattr(output, "model_dump") else output
            else:
                output = await provider.generate_text(
                    system_prompt=case.system_prompt,
                    user_prompt=case.prompt,
                )
                actual = output

            expected = case.expected
            passed = self._compare(expected, actual) if expected is not None else True
            score = 1.0 if passed else 0.0
            error = None
        except Exception as exc:
            actual = None
            passed = False
            score = 0.0
            error = str(exc)

        latency = (time.monotonic() - start) * 1000

        return EvalResult(
            case=case,
            passed=passed,
            score=score,
            latency_ms=round(latency, 2),
            actual=actual,
            error=error,
            tokens_used=0,
            cost=0.0,
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
            return all(self._compare(e, a) for e, a in zip(expected, actual))
        return expected == actual
