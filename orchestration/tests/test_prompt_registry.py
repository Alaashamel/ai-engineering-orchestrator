import pytest
from orchestration.prompt_registry import (
    PromptTemplate,
    PromptTemplateRegistry,
)


class TestPromptTemplate:
    def test_render(self):
        template = PromptTemplate(
            name="greeting",
            template="Hello {name}, welcome to {platform}!",
            variables=["name", "platform"],
        )
        result = template.render(name="Alice", platform="AI Studio")
        assert result == "Hello Alice, welcome to AI Studio!"

    def test_render_with_missing_variable(self):
        template = PromptTemplate(
            name="greeting",
            template="Hello {name}!",
            variables=["name"],
        )
        result = template.render()
        assert result == "Hello {name}!"


class TestPromptTemplateRegistry:
    def test_register_and_get_latest(self):
        registry = PromptTemplateRegistry()
        template = PromptTemplate(
            name="greeting",
            template="Hello {name}!",
            variables=["name"],
        )
        registry.register(template)
        latest = registry.get_latest("greeting")
        assert latest is not None
        assert latest.name == "greeting"

    def test_list_templates(self):
        registry = PromptTemplateRegistry()
        registry.register(
            PromptTemplate(
                name="greeting",
                template="Hello!",
                variables=[],
            )
        )
        registry.register(
            PromptTemplate(
                name="farewell",
                template="Goodbye!",
                variables=[],
            )
        )
        assert "greeting" in registry.list_templates()
        assert "farewell" in registry.list_templates()

    def test_get_version(self):
        registry = PromptTemplateRegistry()
        t1 = PromptTemplate(
            name="greeting",
            template="Hello!",
            variables=[],
            version="1.0",
        )
        t2 = PromptTemplate(
            name="greeting",
            template="Hello there!",
            variables=[],
            version="1.1",
        )
        registry.register(t1)
        registry.register(t2)
        v1 = registry.get_version("greeting", "1.0")
        v2 = registry.get_version("greeting", "1.1")
        assert v1 is not None
        assert v2 is not None
        assert v1.template == "Hello!"
        assert v2.template == "Hello there!"

    def test_delete(self):
        registry = PromptTemplateRegistry()
        registry.register(
            PromptTemplate(
                name="greeting",
                template="Hello!",
                variables=[],
            )
        )
        assert registry.delete("greeting") is True
        assert registry.get_latest("greeting") is None