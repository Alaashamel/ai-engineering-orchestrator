from orchestration.llm_hooks import (
    LLMIntegrationHookManager,
)


class TestLLMIntegrationHookManager:
    def test_register_and_fire(self):
        manager = LLMIntegrationHookManager()
        called = []

        def callback(data):
            called.append(data)

        manager.register("pre_process", callback, priority=0)
        manager.fire("pre_process", {"prompt": "hello"})
        assert len(called) == 1
        assert called[0]["prompt"] == "hello"

    def test_unregister(self):
        manager = LLMIntegrationHookManager()
        callback = lambda data: data
        manager.register("pre_process", callback)
        assert manager.unregister("pre_process", callback) is True
        assert manager.unregister("pre_process", callback) is False

    def test_priority_sorting(self):
        manager = LLMIntegrationHookManager()
        order = []

        def callback1(data):
            order.append(1)

        def callback2(data):
            order.append(2)

        manager.register("pre_process", callback1, priority=10)
        manager.register("pre_process", callback2, priority=5)
        manager.fire("pre_process", {})
        assert order == [2, 1]

    def test_clear(self):
        manager = LLMIntegrationHookManager()
        manager.register("pre_process", lambda data: data)
        manager.clear()
        assert manager.get_hooks("pre_process") == []