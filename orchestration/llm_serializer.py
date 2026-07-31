from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationSerializer(BaseModel):
    name: str
    serialize_fn: Any = None
    deserialize_fn: Any = None


class LLMIntegrationSerializerManager:
    def __init__(self) -> None:
        self._serializers: dict[str, LLMIntegrationSerializer] = {}

    def register(self, serializer: LLMIntegrationSerializer) -> None:
        self._serializers[serializer.name] = serializer

    def unregister(self, name: str) -> bool:
        if name in self._serializers:
            del self._serializers[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationSerializer | None:
        return self._serializers.get(name)

    def serialize(
        self, name: str, data: Any
    ) -> str:
        serializer = self._serializers.get(name)
        if serializer is None:
            raise ValueError(
                f"Serializer '{name}' not found"
            )
        if serializer.serialize_fn is not None:
            return serializer.serialize_fn(data)
        import json
        return json.dumps(data)

    def deserialize(
        self, name: str, data: str
    ) -> Any:
        serializer = self._serializers.get(name)
        if serializer is None:
            raise ValueError(
                f"Serializer '{name}' not found"
            )
        if serializer.deserialize_fn is not None:
            return serializer.deserialize_fn(data)
        import json
        return json.loads(data)

    def list_serializers(self) -> list[str]:
        return list(self._serializers.keys())