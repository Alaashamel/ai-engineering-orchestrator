from orchestration.llm_cache_mgr import (
    LLMIntegrationCache,
    LLMIntegrationCacheManager,
)


class TestLLMIntegrationCacheManager:
    def test_register_and_get_cached(self):
        manager = LLMIntegrationCacheManager()
        manager.register(
            LLMIntegrationCache(
                name="redis",
                cache_fn=lambda k: f"cached_{k}",
            )
        )
        result = manager.get_cached("redis", "key1")
        assert result == "cached_key1"

    def test_unregister(self):
        manager = LLMIntegrationCacheManager()
        manager.register(
            LLMIntegrationCache(
                name="c1",
                cache_fn=lambda k: k,
            )
        )
        assert manager.unregister("c1") is True

    def test_list_caches(self):
        manager = LLMIntegrationCacheManager()
        manager.register(
            LLMIntegrationCache(
                name="c1",
                cache_fn=lambda k: k,
            )
        )
        manager.register(
            LLMIntegrationCache(
                name="c2",
                cache_fn=lambda k: k,
            )
        )
        assert len(manager.list_caches()) == 2