from datetime import datetime, timezone
from uuid import uuid4

import pytest
from orchestration.graph import OrchestrationEngine
from orchestration.state import Phase, ProjectState


@pytest.mark.asyncio
async def test_orchestration_full_flow():
    """Test the full orchestration flow from discovery to completion."""
    engine = OrchestrationEngine()
    project_state = ProjectState(
        project_id=uuid4(),
        name="Test E-Commerce Platform",
        description="Build an e-commerce platform with auth, products, cart, and checkout.",
        phase=Phase.DISCOVERY,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )

    result = await engine.run(project_state)

    assert result["phase"] == "completed"
    assert "requirements" in result
    assert "architecture" in result
    assert len(result.get("tasks", [])) > 0
    assert len(result.get("decisions", [])) > 0


@pytest.mark.asyncio
async def test_orchestration_state_transitions():
    """Test that state transitions happen in the correct order."""
    engine = OrchestrationEngine()
    project_state = ProjectState(
        project_id=uuid4(),
        name="Test Project",
        description="A test project.",
        phase=Phase.DISCOVERY,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )

    result = await engine.run(project_state)
    history = [h["phase"] for h in result.get("phase_history", [])]

    assert "discovery" in history
    assert "planning" in history
    assert "architecture" in history
    assert "task_decomposition" in history
    assert result["phase"] == "completed"


@pytest.mark.asyncio
async def test_orchestration_includes_tasks():
    """Test that tasks are properly decomposed."""
    engine = OrchestrationEngine()
    project_state = ProjectState(
        project_id=uuid4(),
        name="Test Project",
        description="A test project with multiple components.",
        phase=Phase.DISCOVERY,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )

    result = await engine.run(project_state)
    tasks = result.get("tasks", [])

    assert len(tasks) > 0
    for task in tasks:
        assert "id" in task
        assert "title" in task
        assert "agent" in task
        assert "priority" in task
