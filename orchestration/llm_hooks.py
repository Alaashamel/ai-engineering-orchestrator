from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationHook(BaseModel):
    hook_type: str
    priority: int = 0
    callback: Any = None


class LLMIntegrationHookManager:
    def __init__(self) -> None:
        self._hooks: dict[str, list[LLMIntegrationHook]] = {}

    def register(
        self,
        hook_type: str,
        callback: Any,
        priority: int = 0,
    ) -> None:
        hook = LLMIntegrationHook(
            hook_type=hook_type,
            priority=priority,
            callback=callback,
        )
        if hook_type not in self._hooks:
            self._hooks[hook_type] = []
        self._hooks[hook_type].append(hook)
        self._hooks[hook_type].sort(key=lambda h: h.priority)

    def unregister(self, hook_type: str, callback: Any) -> bool:
        hooks = self._hooks.get(hook_type, [])
        for hook in hooks:
            if hook.callback is callback:
                hooks.remove(hook)
                return True
        return False

    def fire(self, hook_type: str, *args: Any, **kwargs: Any) -> list[Any]:
        results: list[Any] = []
        hooks = self._hooks.get(hook_type, [])
        for hook in hooks:
            if hook.callback is not None:
                result = hook.callback(*args, **kwargs)
                results.append(result)
        return results

    def get_hooks(self, hook_type: str) -> list[LLMIntegrationHook]:
        return list(self._hooks.get(hook_type, []))

    def clear(self) -> None:
        self._hooks.clear()