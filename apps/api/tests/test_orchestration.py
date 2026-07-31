from datetime import datetime, timezone
from uuid import uuid4

import pytest
from orchestration.graph import OrchestrationEngine
from orchestration.llm import LLMProvider
from orchestration.state import Phase, ProjectState


def _make_engine() -> OrchestrationEngine:
    return OrchestrationEngine(llm=LLMProvider(api_key=""))


@pytest.mark.asyncio
async def test_orchestration_full_flow():
    """Test the full orchestration flow from discovery to completion."""
    engine = _make_engine()
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
    engine = _make_engine()
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
    engine = _make_engine()
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


@pytest.mark.asyncio
async def test_approve_and_reject():
    """Test approval flow: create pending approvals, then approve/reject."""
    engine = _make_engine()
    project_state = ProjectState(
        project_id=uuid4(),
        name="Approval Test",
        description="Test project for approval flow.",
        phase=Phase.DISCOVERY,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )

    result = await engine.run(project_state)
    assert result["phase"] == "completed"

    state_copy = dict(result)
    state_copy["tasks"] = [
        {"id": "t1", "title": "Critical Task", "description": "Needs approval",
         "agent": "backend_engineer", "priority": "critical", "status": "pending"}
    ]

    approved = engine.approve_all(state_copy)
    assert approved["human_approval_needed"] is False
    for a in approved["pending_approvals"]:
        assert a["status"] == "approved"

    state_copy["pending_approvals"] = [
        {"id": "a1", "action": "test", "description": "", "risk_level": "high",
         "proposed_by": "ceo", "status": "pending", "created_at": datetime.now(timezone.utc).isoformat()}
    ]
    state_copy["human_approval_needed"] = True
    rejected = engine.reject_all(state_copy, reason="Not ready")
    assert rejected["human_approval_needed"] is False
    for a in rejected["pending_approvals"]:
        assert a["status"] == "rejected"
        assert a.get("reason") == "Not ready"


@pytest.mark.asyncio
async def test_rollback():
    """Test phase rollback restores previous state."""
    engine = _make_engine()
    history = [
        {"phase": "discovery", "timestamp": "2026-01-01T00:00:00"},
        {"phase": "planning", "timestamp": "2026-01-01T00:01:00"},
        {"phase": "architecture", "timestamp": "2026-01-01T00:02:00"},
    ]
    state: dict = {
        "phase": "architecture",
        "phase_history": list(history),
        "errors": [{"phase": "architecture", "error": "test"}],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    rolled = engine.rollback_phase(state)
    assert rolled["phase"] == "planning"
    assert len(rolled["phase_history"]) == 2
    assert len(rolled["errors"]) == 0

    rolled2 = engine.rollback_phase(state, "discovery")
    assert rolled2["phase"] == "discovery"
    assert len(rolled2["phase_history"]) == 1
