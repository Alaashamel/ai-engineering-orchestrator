from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMUsageReport(BaseModel):
    report_id: str
    model: str
    total_requests: int
    total_tokens: int
    total_cost: float
    avg_latency_ms: float
    success_rate: float
    period_start: str
    period_end: str


class LLMUsageReporter:
    def __init__(self) -> None:
        self._reports: list[LLMUsageReport] = []

    def generate_report(
        self,
        model: str,
        metrics: dict[str, Any],
    ) -> LLMUsageReport:
        from datetime import datetime, timezone

        total_requests = metrics.get("total_requests", 0)
        total_tokens = metrics.get("total_tokens", 0)
        total_cost = metrics.get("total_cost", 0.0)
        avg_latency = metrics.get("avg_latency_ms", 0.0)
        success_rate = metrics.get("success_rate", 0.0)

        report = LLMUsageReport(
            report_id=f"rpt_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            model=model,
            total_requests=total_requests,
            total_tokens=total_tokens,
            total_cost=total_cost,
            avg_latency_ms=avg_latency,
            success_rate=success_rate,
            period_start=metrics.get("period_start", ""),
            period_end=metrics.get("period_end", ""),
        )
        self._reports.append(report)
        return report

    def get_reports(self) -> list[LLMUsageReport]:
        return list(self._reports)

    def get_report(self, report_id: str) -> LLMUsageReport | None:
        for report in self._reports:
            if report.report_id == report_id:
                return report
        return None

    def export_report(self, report_id: str, format: str = "json") -> str:
        report = self.get_report(report_id)
        if report is None:
            raise ValueError(f"Report {report_id} not found")

        if format == "json":
            return report.model_dump_json()
        if format == "text":
            return self._format_text(report)
        if format == "csv":
            return self._format_csv(report)
        raise ValueError(f"Unsupported format: {format}")

    def _format_text(self, report: LLMUsageReport) -> str:
        return (
            f"LLM Usage Report\n"
            f"================\n"
            f"Model: {report.model}\n"
            f"Total Requests: {report.total_requests}\n"
            f"Total Tokens: {report.total_tokens}\n"
            f"Total Cost: ${report.total_cost:.4f}\n"
            f"Avg Latency: {report.avg_latency_ms:.2f}ms\n"
            f"Success Rate: {report.success_rate:.2%}\n"
        )

    def _format_csv(self, report: LLMUsageReport) -> str:
        return (
            "report_id,model,total_requests,total_tokens,total_cost,"
            "avg_latency_ms,success_rate,period_start,period_end\n"
            f"{report.report_id},{report.model},{report.total_requests},"
            f"{report.total_tokens},{report.total_cost},"
            f"{report.avg_latency_ms},{report.success_rate},"
            f"{report.period_start},{report.period_end}\n"
        )