import pytest
from orchestration.llm_events import (
    LLMIntegrationEvent,
    LLMIntegrationEventListener,
)


class TestLLMIntegrationEventListener:
    def test_on_and_emit(self):
        listener = LLMIntegrationEventListener()
        called = []

        def handler(event):
            called.append(event)

        listener.on("request", handler)
        event = LLMIntegrationEvent(
            event_type="request",
            model="gpt-4o",
            data={"prompt": "hello"},
        )
        listener.emit(event)
        assert len(called) == 1
        assert called[0].model == "gpt-4o"

    def test_off(self):
        listener = LLMIntegrationEventListener()
        called = []

        def handler(event):
            called.append(event)

        listener.on("request", handler)
        listener.off("request", handler)
        event = LLMIntegrationEvent(
            event_type="request",
            model="gpt-4o",
            data={},
        )
        listener.emit(event)
        assert len(called) == 0

    def test_multiple_listeners(self):
        listener = LLMIntegrationEventListener()
        called1 = []
        called2 = []

        def handler1(event):
            called1.append(event)

        def handler2(event):
            called2.append(event)

        listener.on("request", handler1)
        listener.on("request", handler2)
        event = LLMIntegrationEvent(
            event_type="request",
            model="gpt-4o",
            data={},
        )
        listener.emit(event)
        assert len(called1) == 1
        assert len(called2) == 1

    def test_clear(self):
        listener = LLMIntegrationEventListener()
        listener.on("request", lambda e: None)
        listener.clear()
        assert listener.get_listeners("request") == []