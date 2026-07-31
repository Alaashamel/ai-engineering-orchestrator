from orchestration.llm_serializer import (
    LLMIntegrationSerializer,
    LLMIntegrationSerializerManager,
)


class TestLLMIntegrationSerializerManager:
    def test_register_and_serialize(self):
        manager = LLMIntegrationSerializerManager()
        manager.register(
            LLMIntegrationSerializer(
                name="json",
                serialize_fn=lambda d: str(d),
                deserialize_fn=lambda s: s,
            )
        )
        result = manager.serialize("json", {"key": "value"})
        assert result == "{'key': 'value'}"

    def test_unregister(self):
        manager = LLMIntegrationSerializerManager()
        manager.register(
            LLMIntegrationSerializer(
                name="json",
                serialize_fn=lambda d: str(d),
            )
        )
        assert manager.unregister("json") is True

    def test_deserialize(self):
        manager = LLMIntegrationSerializerManager()
        manager.register(
            LLMIntegrationSerializer(
                name="json",
                deserialize_fn=lambda s: s,
            )
        )
        result = manager.deserialize("json", "hello")
        assert result == "hello"

    def test_list_serializers(self):
        manager = LLMIntegrationSerializerManager()
        manager.register(
            LLMIntegrationSerializer(
                name="json",
                serialize_fn=lambda d: str(d),
            )
        )
        manager.register(
            LLMIntegrationSerializer(
                name="text",
                serialize_fn=lambda d: str(d),
            )
        )
        assert len(manager.list_serializers()) == 2