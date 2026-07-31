import pytest

from orchestration.prompt_registry import PromptTemplate, PromptTemplateRegistry


@pytest.fixture
def registry():
    reg = PromptTemplateRegistry()
    reg.register(PromptTemplate(
        name="test",
        template="Hello {name}",
        variables=["name"],
        version="1.0",
        description="First version",
    ))
    reg.register(PromptTemplate(
        name="test",
        template="Hi {name}!",
        variables=["name"],
        version="2.0",
        description="Second version",
    ))
    return reg


def test_get_version_history(registry):
    history = registry.get_version_history("test")
    assert len(history) == 2
    assert history[0]["version"] == "1.0"
    assert history[1]["version"] == "2.0"
    assert "diff_from_previous" in history[1]


def test_diff_versions(registry):
    diff = registry.diff("test", "1.0", "2.0")
    assert "Hello" in diff
    assert "Hi" in diff


def test_diff_nonexistent_version(registry):
    diff = registry.diff("test", "1.0", "99.0")
    assert "Cannot diff" in diff


def test_rollback(registry):
    rolled = registry.rollback("test", "1.0")
    assert rolled is not None
    assert rolled.version == "2.1"
    assert "rollback" in rolled.tags
    assert "Hello {name}" in rolled.template


def test_rollback_nonexistent():
    reg = PromptTemplateRegistry()
    result = reg.rollback("nonexistent", "1.0")
    assert result is None


def test_tag_and_get_by_tag(registry):
    result = registry.tag_version("test", "1.0", "stable")
    assert result
    tmpl = registry.get_by_tag("test", "stable")
    assert tmpl is not None
    assert tmpl.version == "1.0"


def test_tag_nonexistent_version():
    reg = PromptTemplateRegistry()
    result = reg.tag_version("test", "1.0", "stable")
    assert not result


def test_list_tags(registry):
    registry.tag_version("test", "1.0", "stable")
    registry.tag_version("test", "2.0", "latest")
    tags = registry.list_tags("test")
    assert tags["stable"] == "1.0"
    assert tags["latest"] == "2.0"


def test_delete_removes_tags(registry):
    registry.tag_version("test", "1.0", "stable")
    registry.delete("test")
    assert registry.list_tags("test") == {}
    assert registry.get_latest("test") is None


def test_update_auto_bumps_version(registry):
    updated = registry.update(PromptTemplate(
        name="test",
        template="New template {name}",
        variables=["name"],
    ))
    assert updated.version == "2.1"
    latest = registry.get_latest("test")
    assert latest.version == "2.1"
