from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from orchestration.llm_config import LLMCostConfig


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class LLMCostRecord:
    model: str
    usage: TokenUsage
    cost: float
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class LLMCostTracker:
    def __init__(self, config: LLMCostConfig):
        self.config = config
        self.records: list[LLMCostRecord] = []
        self.total_cost: float = 0.0
        self.total_tokens: int = 0

    def record(self, model: str, usage: TokenUsage) -> LLMCostRecord:
        cost = (usage.total_tokens / 1000) * self.config.cost_per_1k_tokens
        record = LLMCostRecord(model=model, usage=usage, cost=cost)
        self.records.append(record)
        self.total_cost += cost
        self.total_tokens += usage.total_tokens

        if self.config.log_costs:
            self._log_cost(record)

        if self.total_cost >= self.config.alert_threshold:
            self._alert_threshold_reached()

        return record

    def _log_cost(self, record: LLMCostRecord) -> None:
        from orchestration.audit import AuditLogger
        logger = AuditLogger.get_instance()
        logger.info(
            "llm_cost_recorded",
            model=record.model,
            tokens=record.usage.total_tokens,
            cost=record.cost,
            total_cost=self.total_cost,
        )

    def _alert_threshold_reached(self) -> None:
        from orchestration.audit import AuditLogger
        logger = AuditLogger.get_instance()
        logger.warning(
            "llm_cost_threshold_reached",
            total_cost=self.total_cost,
            threshold=self.config.alert_threshold,
        )

    def get_summary(self) -> dict[str, object]:
        return {
            "total_cost": round(self.total_cost, 4),
            "total_tokens": self.total_tokens,
            "total_requests": len(self.records),
            "records": [
                {
                    "model": r.model,
                    "tokens": r.usage.total_tokens,
                    "cost": round(r.cost, 6),
                    "timestamp": r.timestamp,
                }
                for r in self.records
            ],
        }