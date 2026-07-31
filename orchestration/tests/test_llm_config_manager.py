from orchestration.llm_config_manager import LLMIntegrationConfig


class TestLLMIntegrationConfig:
    def test_default_config(self, tmp_path):
        config = LLMIntegrationConfig(
            config_path=str(tmp_path / "llm_config.json")
        )
        assert config.get("provider") == "openai"
        assert config.get("model") == "gpt-4o"
        assert config.get("mock_mode") is True

    def test_set_and_get(self, tmp_path):
        config = LLMIntegrationConfig(
            config_path=str(tmp_path / "llm_config.json")
        )
        config.set("temperature", 0.5)
        assert config.get("temperature") == 0.5

    def test_save_and_reload(self, tmp_path):
        config_path = tmp_path / "llm_config.json"
        config = LLMIntegrationConfig(config_path=str(config_path))
        config.set("temperature", 0.3)
        config.save()

        config2 = LLMIntegrationConfig(config_path=str(config_path))
        assert config2.get("temperature") == 0.3

    def test_reset_to_defaults(self, tmp_path):
        config = LLMIntegrationConfig(
            config_path=str(tmp_path / "llm_config.json")
        )
        config.set("temperature", 0.9)
        config.reset_to_defaults()
        assert config.get("temperature") == 0.7