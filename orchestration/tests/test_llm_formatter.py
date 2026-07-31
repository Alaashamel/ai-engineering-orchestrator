from orchestration.llm_formatter import (
    LLMIntegrationFormatter,
    LLMIntegrationFormatterManager,
)


class TestLLMIntegrationFormatterManager:
    def test_register_and_format(self):
        manager = LLMIntegrationFormatterManager()
        manager.register(
            LLMIntegrationFormatter(
                name="uppercase",
                format_fn=lambda d: str(d).upper(),
            )
        )
        result = manager.format("uppercase", "hello")
        assert result == "HELLO"

    def test_unregister(self):
        manager = LLMIntegrationFormatterManager()
        manager.register(
            LLMIntegrationFormatter(
                name="upper",
                format_fn=lambda d: str(d),
            )
        )
        assert manager.unregister("upper") is True

    def test_list_formatters(self):
        manager = LLMIntegrationFormatterManager()
        manager.register(
            LLMIntegrationFormatter(
                name="upper",
                format_fn=lambda d: str(d),
            )
        )
        manager.register(
            LLMIntegrationFormatter(
                name="lower",
                format_fn=lambda d: str(d).lower(),
            )
        )
        assert len(manager.list_formatters()) == 2