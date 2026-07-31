from orchestration.llm_optimizer import (
    LLMIntegrationOptimizer,
    LLMIntegrationOptimizerManager,
)


class TestLLMIntegrationOptimizerManager:
    def test_register_and_optimize(self):
        manager = LLMIntegrationOptimizerManager()
        manager.register(
            LLMIntegrationOptimizer(
                name="compress",
                optimize_fn=lambda d: str(d)[:100],
            )
        )
        result = manager.optimize("compress", "x" * 200)
        assert len(result) == 100

    def test_unregister(self):
        manager = LLMIntegrationOptimizerManager()
        manager.register(
            LLMIntegrationOptimizer(
                name="opt1",
                optimize_fn=lambda d: d,
            )
        )
        assert manager.unregister("opt1") is True

    def test_list_optimizers(self):
        manager = LLMIntegrationOptimizerManager()
        manager.register(
            LLMIntegrationOptimizer(
                name="o1",
                optimize_fn=lambda d: d,
            )
        )
        manager.register(
            LLMIntegrationOptimizer(
                name="o2",
                optimize_fn=lambda d: d,
            )
        )
        assert len(manager.list_optimizers()) == 2