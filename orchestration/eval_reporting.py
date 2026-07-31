from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from orchestration.eval_dataset import EvalDataset, EvalResult


class EvalReport:
    def __init__(
        self,
        dataset: EvalDataset,
        results: list[EvalResult],
        model: str = "unknown",
        provider_name: str = "unknown",
    ):
        self.dataset = dataset
        self.results = results
        self.model = model
        self.provider_name = provider_name
        self.timestamp = datetime.now(timezone.utc).isoformat()

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total > 0 else 0.0

    @property
    def avg_latency(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.latency_ms for r in self.results) / len(self.results)

    @property
    def total_cost(self) -> float:
        return sum(r.cost for r in self.results)

    @property
    def total_tokens(self) -> int:
        return sum(r.tokens_used for r in self.results)

    def get_failures(self) -> list[EvalResult]:
        return [r for r in self.results if not r.passed]

    def get_by_tag(self, tag: str) -> list[EvalResult]:
        return [r for r in self.results if tag in r.case.tags]

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": {
                "model": self.model,
                "provider": self.provider_name,
                "timestamp": self.timestamp,
                "total": self.total,
                "passed": self.passed,
                "failed": self.failed,
                "pass_rate": round(self.pass_rate, 4),
                "avg_latency_ms": round(self.avg_latency, 2),
                "total_cost": round(self.total_cost, 6),
                "total_tokens": self.total_tokens,
            },
            "results": [r.to_dict() for r in self.results],
        }

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def to_markdown(self) -> str:
        lines = [
            f"# Eval Report: {self.dataset.name}",
            "",
            f"- **Model:** {self.model}",
            f"- **Provider:** {self.provider_name}",
            f"- **Timestamp:** {self.timestamp}",
            f"- **Total tests:** {self.total}",
            f"- **Passed:** {self.passed}",
            f"- **Failed:** {self.failed}",
            f"- **Pass rate:** {self.pass_rate:.1%}",
            f"- **Avg latency:** {self.avg_latency:.1f}ms",
            f"- **Total cost:** ${self.total_cost:.6f}",
            f"- **Total tokens:** {self.total_tokens}",
            "",
        ]
        if self.failed > 0:
            lines.append("## Failures")
            lines.append("")
            for r in self.get_failures():
                lines.append(f"- **{r.case.name}**: {r.error or 'assertion failed'}")
                lines.append(f"  - Expected: {r.case.expected}")
                lines.append(f"  - Actual: {r.actual}")
                lines.append("")
        lines.append("## Per-Test Results")
        lines.append("")
        lines.append("| Test | Status | Score | Latency (ms) | Tokens | Cost |")
        lines.append("|------|--------|-------|--------------|--------|------|")
        for r in self.results:
            status = "✓" if r.passed else "✗"
            lines.append(
                f"| {r.case.name} | {status} | {r.score} | {r.latency_ms} | "
                f"{r.tokens_used} | ${r.cost:.6f} |"
            )
        return "\n".join(lines)


class ReportComparison:
    def __init__(self, reports: list[EvalReport]):
        self.reports = reports

    def compare(self) -> dict[str, Any]:
        best_pass_rate = max(r.pass_rate for r in self.reports)
        best_latency = min(r.avg_latency for r in self.reports)
        lowest_cost = min(r.total_cost for r in self.reports)

        comparisons = []
        for r in self.reports:
            comparisons.append({
                "model": r.model,
                "provider": r.provider_name,
                "pass_rate": round(r.pass_rate, 4),
                "avg_latency_ms": round(r.avg_latency, 2),
                "total_cost": round(r.total_cost, 6),
                "total_tokens": r.total_tokens,
                "is_best_pass_rate": r.pass_rate >= best_pass_rate,
                "is_best_latency": r.avg_latency <= best_latency,
                "is_lowest_cost": r.total_cost <= lowest_cost,
            })

        return {
            "comparisons": comparisons,
            "best_pass_rate": round(best_pass_rate, 4),
            "best_latency_ms": round(best_latency, 2),
            "lowest_cost": round(lowest_cost, 6),
        }

    def to_markdown(self) -> str:
        comp = self.compare()
        lines = [
            "# Model Comparison Report",
            "",
            "## Summary",
            "",
            "| Model | Provider | Pass Rate | Avg Latency | Cost | Best? |",
            "|-------|----------|-----------|-------------|------|-------|",
        ]
        for c in comp["comparisons"]:
            badges = []
            if c["is_best_pass_rate"]:
                badges.append("🏆 pass rate")
            if c["is_best_latency"]:
                badges.append("⚡ latency")
            if c["is_lowest_cost"]:
                badges.append("💰 cost")
            badge_str = ", ".join(badges) if badges else ""
            lines.append(
                f"| {c['model']} | {c['provider']} | {c['pass_rate']:.1%} | "
                f"{c['avg_latency_ms']}ms | ${c['total_cost']:.6f} | {badge_str} |"
            )
        lines.extend([
            "",
            f"**Best pass rate:** {comp['best_pass_rate']:.1%}",
            f"**Best latency:** {comp['best_latency_ms']}ms",
            f"**Lowest cost:** ${comp['lowest_cost']:.6f}",
        ])
        return "\n".join(lines)
