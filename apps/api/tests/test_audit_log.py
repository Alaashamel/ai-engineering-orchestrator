from uuid import uuid4
from datetime import datetime
from src.models.audit_log import AuditLog

def test_audit_log_creation():
    log = AuditLog(
        project_id=uuid4(),
        actor="test",
        action="test_action",
        resource_type="project",
        phase="discovery",
    )
    assert log.actor == "test"
    assert log.action == "test_action"
    assert log.outcome is None  # DB default, not set at Python level
