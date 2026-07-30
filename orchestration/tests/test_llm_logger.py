import pytest
from orchestration.llm_logger import LLMIntegrationLogger


class TestLLMIntegrationLogger:
    def test_log_request(self, tmp_path):
        logger = LLMIntegrationLogger(log_dir=str(tmp_path / "logs"))
        log_file = logger.log_request(
            model="gpt-4o",
            prompt="Hello",
            response='{"result": "world"}',
            latency_ms=100.0,
            tokens_used=50,
            success=True,
        )
        assert log_file.exists()
        assert "llm_log_" in log_file.name

    def test_log_error(self, tmp_path):
        logger = LLMIntegrationLogger(log_dir=str(tmp_path / "logs"))
        log_file = logger.log_error(
            model="gpt-4o",
            error="Timeout",
            prompt="Hello",
        )
        assert log_file.exists()
        assert "llm_error_" in log_file.name

    def test_get_recent_logs(self, tmp_path):
        logger = LLMIntegrationLogger(log_dir=str(tmp_path / "logs"))
        logger.log_request(
            model="gpt-4o",
            prompt="Hello",
            response='{"result": "world"}',
            latency_ms=100.0,
            tokens_used=50,
            success=True,
        )
        logs = logger.get_recent_logs(limit=5)
        assert len(logs) == 1
        assert logs[0]["model"] == "gpt-4o"

    def test_clear_logs(self, tmp_path):
        logger = LLMIntegrationLogger(log_dir=str(tmp_path / "logs"))
        logger.log_request(
            model="gpt-4o",
            prompt="Hello",
            response='{"result": "world"}',
            latency_ms=100.0,
            tokens_used=50,
            success=True,
        )
        logger.clear_logs()
        assert len(logger.get_recent_logs()) == 0