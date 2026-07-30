from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


class LLMSecretManager:
    def __init__(self, secrets_dir: str = ".secrets") -> None:
        self.secrets_dir = Path(secrets_dir)
        self.secrets_dir.mkdir(exist_ok=True)

    def store_secret(
        self, key: str, value: str, encrypt: bool = False
    ) -> None:
        secret_file = self.secrets_dir / f"{key}.secret"
        if encrypt:
            import base64
            value = base64.b64encode(value.encode()).decode()
        with open(secret_file, "w") as f:
            f.write(value)
        secret_file.chmod(0o600)

    def get_secret(self, key: str) -> Optional[str]:
        secret_file = self.secrets_dir / f"{key}.secret"
        if not secret_file.exists():
            return None
        with open(secret_file, "r") as f:
            return f.read().strip()

    def delete_secret(self, key: str) -> bool:
        secret_file = self.secrets_dir / f"{key}.secret"
        if secret_file.exists():
            secret_file.unlink()
            return True
        return False

    def list_secrets(self) -> list[str]:
        return [
            f.stem
            for f in self.secrets_dir.glob("*.secret")
        ]

    def rotate_api_key(self, key: str) -> str:
        import secrets as secrets_module
        new_key = f"sk-{secrets_module.token_urlsafe(32)}"
        self.store_secret(key, new_key)
        return new_key

    def validate_secrets(self) -> dict[str, bool]:
        result: dict[str, bool] = {}
        for secret_file in self.secrets_dir.glob("*.secret"):
            key = secret_file.stem
            value = self.get_secret(key)
            result[key] = value is not None and len(value) > 0
        return result