from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LLMIntegrationLogger:
    def __init__(self, log_dir: str = "llm_logs") -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

    def log_request(
        self,
        model: str,
        prompt: str,
        response: str,
        latency_ms: float,
        tokens_used: int,
        success: bool,
    ) -> Path:
        from datetime import datetime, timezone

        timestamp = datetime.now(timezone.utc).strftime(
            "%Y%m%d_%H%M%S_%f"
        )
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "prompt": prompt,
            "response": response,
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
            "success": success,
        }

        log_file = self.log_dir / f"llm_log_{timestamp}.json"
        with open(log_file, "w") as f:
            json.dump(log_entry, f, indent=2)

        return log_file

    def log_error(
        self,
        model: str,
        error: str,
        prompt: str,
    ) -> Path:
        from datetime import datetime, timezone

        timestamp = datetime.now(timezone.utc).strftime(
            "%Y%m%d_%H%M%S_%f"
        )
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "error": error,
            "prompt": prompt,
        }

        log_file = self.log_dir / f"llm_error_{timestamp}.json"
        with open(log_file, "w") as f:
            json.dump(log_entry, f, indent=2)

        return log_file

    def get_recent_logs(self, limit: int = 10) -> list[dict[str, Any]]:
        logs: list[dict[str, Any]] = []
        for log_file in sorted(
            self.log_dir.glob("llm_log_*.json"),
            reverse=True,
        )[:limit]:
            with open(log_file) as f:
                logs.append(json.load(f))
        return logs

    def get_error_logs(self, limit: int = 10) -> list[dict[str, Any]]:
        logs: list[dict[str, Any]] = []
        for log_file in sorted(
            self.log_dir.glob("llm_error_*.json"),
            reverse=True,
        )[:limit]:
            with open(log_file) as f:
                logs.append(json.load(f))
        return logs

    def clear_logs(self) -> None:
        for log_file in self.log_dir.glob("*.json"):
            log_file.unlink()