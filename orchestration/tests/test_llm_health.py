from orchestration.llm_health import LLMIntegrationHealthCheck


class TestLLMIntegrationHealthCheck:
    def test_register_and_run(self):
        checker = LLMIntegrationHealthCheck()
        checker.register_check("api_key", lambda: True)
        checker.register_check("model", lambda: "gpt-4o")
        import asyncio
        results = asyncio.run(checker.run_checks())
        assert "api_key" in results
        assert "model" in results
        assert results["api_key"]["status"] == "healthy"

    def test_is_healthy(self):
        checker = LLMIntegrationHealthCheck()
        checker.register_check("api_key", lambda: True)
        assert checker.is_healthy() is True

    def test_unhealthy_check(self):
        checker = LLMIntegrationHealthCheck()
        checker.register_check("api_key", lambda: True)
        checker.register_check("bad", lambda: 1/0)
        import asyncio
        results = asyncio.run(checker.run_checks())
        assert results["bad"]["status"] == "unhealthy"