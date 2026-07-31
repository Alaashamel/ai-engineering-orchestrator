from uuid import uuid4

from orchestration.state import (
    ApprovalRequest,
    Decision,
    GeneratedFileRecord,
    Phase,
    ProjectState,
    TaskItem,
)


def test_phase_enum_values():
    assert Phase.DISCOVERY.value == "discovery"
    assert Phase.COMPLETED.value == "completed"
    assert Phase.FAILED.value == "failed"

def test_project_state_defaults():
    state = ProjectState(project_id=uuid4(), name="Test", description="Test project")
    assert state.phase == Phase.DISCOVERY
    assert state.tasks == []
    assert state.decisions == []
    assert state.errors == []
    assert state.pending_approvals == []

def test_task_item_defaults():
    task = TaskItem(id="t1", title="Test", description="Desc", agent="ceo", priority="high")
    assert task.status == "pending"
    assert task.dependencies == []
    assert task.acceptance_criteria == []

def test_decision_creation():
    d = Decision(agent="ceo", action="analyze", reasoning="test", timestamp="now")
    assert d.agent == "ceo"

def test_approval_request_defaults():
    a = ApprovalRequest(id="a1", action="test", description="", risk_level="low", proposed_by="ceo", created_at="now")
    assert a.status == "pending"

def test_generated_file_defaults():
    f = GeneratedFileRecord(path="/test.py", agent="backend", task_id="t1")
    assert f.status == "pending"
    assert f.content_preview == ""
