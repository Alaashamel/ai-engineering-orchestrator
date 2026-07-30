from __future__ import annotations

import asyncio
import time
from typing import Any, Optional

from pydantic import BaseModel


class LLMMetricsCollector:
    def __init__(self) -> None:
        self._metrics: dict[str, list[dict[str, Any]]] = {}

    def record(
        self,
        model: str,
        operation: str,
        latency_ms: float,
        tokens_used: int,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        entry: dict[str, Any] = {
            "model": model,
            "operation": operation,
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
            "success": success,
            "timestamp": time.time(),
        }
        if error:
            entry["error"] = error

        if model not in self._metrics:
            self._metrics[model] = []
        self._metrics[model].append(entry)

    def get_model_stats(self, model: str) -> dict[str, Any]:
        entries = self._metrics.get(model, [])
        if not entries:
            return {"model": model, "requests": 0}

        total = len(entries)
        successes = sum(1 for e in entries if e["success"])
        latencies = [e["latency_ms"] for e in entries]
        tokens = [e["tokens_used"] for e in entries]

        return {
            "model": model,
            "requests": total,
            "successes": successes,
            "failures": total - successes,
            "success_rate": successes / total,
            "avg_latency_ms": round(sum(latencies) / total, 2),
            "min_latency_ms": round(min(latencies), 2),
            "max_latency_ms": round(max(latencies), 2),
            "total_tokens": sum(tokens),
            "avg_tokens_per_request": round(sum(tokens) / total, 2),
        }

    def get_all_stats(self) -> dict[str, Any]:
        return {
            model: self.get_model_stats(model)
            for model in self._metrics
        }

    def get_summary(self) -> dict[str, Any]:
        all_stats = self.get_all_stats()
        total_requests = sum(
            s["requests"] for s in all_stats.values()
        )
        total_successes = sum(
            s["successes"] for s in all_stats.values()
        )
        return {
            "total_requests": total_requests,
            "total_successes": total_successes,
            "total_failures": total_requests - total_successes,
            "overall_success_rate": (
                total_successes / total_requests
                if total_requests > 0
                else 0.0
            ),
            "models": len(all_stats),
            "per_model": all_stats,
        }