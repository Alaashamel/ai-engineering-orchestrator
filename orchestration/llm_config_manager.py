from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LLMIntegrationConfig:
    def __init__(self, config_path: str = "llm_config.json") -> None:
        self.config_path = Path(config_path)
        self.config: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = json.load(f)
        else:
            self.config = self._default_config()

    def _default_config(self) -> dict[str, Any]:
        return {
            "provider": "openai",
            "model": "gpt-4o",
            "api_key_env": "LLM_API_KEY",
            "max_retries": 3,
            "timeout": 30,
            "temperature": 0.7,
            "max_tokens": 4096,
            "cost_tracking": True,
            "cost_per_1k_tokens": 0.005,
            "cost_alert_threshold": 10.0,
            "mock_mode": True,
            "streaming": True,
            "cache_enabled": False,
            "eval_enabled": True,
            "eval_tolerance": 0.95,
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value

    def save(self) -> None:
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def reload(self) -> None:
        self._load()

    def reset_to_defaults(self) -> None:
        self.config = self._default_config()
        self.save()

    def validate(self) -> dict[str, Any]:
        from orchestration.llm_validator import LLMConfigValidator

        return LLMConfigValidator.validate_provider_config(self)