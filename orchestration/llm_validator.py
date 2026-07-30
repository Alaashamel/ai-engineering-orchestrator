from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LLMConfigValidator:
    @staticmethod
    def validate_provider_config(config: Any) -> dict[str, Any]:
        errors: list[str] = []
        warnings: list[str] = []

        if not hasattr(config, "provider"):
            errors.append("Missing required field: provider")
        if not hasattr(config, "model"):
            errors.append("Missing required field: model")

        if hasattr(config, "temperature"):
            if config.temperature < 0 or config.temperature > 2:
                errors.append("Temperature must be between 0 and 2")
            elif config.temperature > 1.0:
                warnings.append("High temperature may produce less deterministic results")

        if hasattr(config, "max_tokens"):
            if config.max_tokens < 1:
                errors.append("Max tokens must be positive")
            elif config.max_tokens > 128000:
                warnings.append("Very high max tokens may increase latency and cost")

        if hasattr(config, "timeout"):
            if config.timeout < 1:
                errors.append("Timeout must be at least 1 second")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    @staticmethod
    def validate_api_key(api_key: str | None, provider: str = "openai") -> dict[str, Any]:
        if api_key is None:
            return {
                "valid": False,
                "error": f"API key is required for {provider} provider",
            }
        if not api_key.strip():
            return {
                "valid": False,
                "error": "API key cannot be empty",
            }
        if provider == "openai" and not api_key.startswith("sk-"):
            return {
                "valid": False,
                "error": "OpenAI API key must start with 'sk-'",
            }
        return {"valid": True, "error": None}

    @staticmethod
    def validate_environment() -> dict[str, Any]:
        import os

        issues: list[str] = []
        required_vars = ["LLM_API_KEY", "LLM_MODEL", "DATABASE_URL"]
        for var in required_vars:
            if var not in os.environ:
                issues.append(f"Missing environment variable: {var}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }