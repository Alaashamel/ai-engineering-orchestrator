import pytest
from datetime import datetime, timezone
from uuid import uuid4
from orchestration.state import ProjectState, Phase

@pytest.fixture
def sample_project_state():
    return ProjectState(
        project_id=uuid4(),
        name="Test Project",
        description="A test project.",
        phase=Phase.DISCOVERY,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
