import pytest
from orchestration.llm_middleware import LLMIntegrationMiddleware


class TestLLMIntegrationMiddleware:
    def test_add_and_remove(self):
        middleware = LLMIntegrationMiddleware()
        mw = lambda data: data
        middleware.add(mw)
        assert len(middleware._middlewares) == 1
        assert middleware.remove(mw) is True
        assert len(middleware._middlewares) == 0

    def test_remove_nonexistent(self):
        middleware = LLMIntegrationMiddleware()
        mw = lambda data: data
        assert middleware.remove(mw) is False

    def test_process_request(self):
        import asyncio

        middleware = LLMIntegrationMiddleware()
        middleware.add(lambda data: {**data, "processed": True})

        async def run():
            return await middleware.process_request({"prompt": "hello"})

        result = asyncio.run(run())
        assert result["processed"] is True

    def test_process_response(self):
        import asyncio

        middleware = LLMIntegrationMiddleware()
        middleware.add(lambda data: {**data, "logged": True})

        async def run():
            return await middleware.process_response({"result": "ok"})

        result = asyncio.run(run())
        assert result["logged"] is True