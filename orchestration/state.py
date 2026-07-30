from __future__ import annotations

from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class Phase(str, Enum):
    DISCOVERY = "discovery"
    PLANNING = "planning"
    ARCHITECTURE = "architecture"
    TASK_DECOMPOSITION = "task_decomposition"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    REVIEW = "review"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"
    FAILED = "failed"


class Decision(BaseModel):
    agent: str
    action: str
    reasoning: str
    timestamp: str


class ApprovalRequest(BaseModel):
    id: str
    action: str
    description: str
    risk_level: str
    proposed_by: str
    status: str = "pending"
    created_at: str


class TaskItem(BaseModel):
    id: str
    title: str
    description: str
    agent: str
    priority: str
    dependencies: list[str] = Field(default_factory=list)
    status: str = "pending"
    acceptance_criteria: list[str] = Field(default_factory=list)


class ProjectState(BaseModel):
    project_id: UUID
    name: str
    description: str
    phase: Phase = Phase.DISCOVERY
    phase_history: list[dict[str, Any]] = Field(default_factory=list)

    requirements: dict[str, Any] | None = None
    architecture: dict[str, Any] | None = None
    tasks: list[TaskItem] = Field(default_factory=list)

    decisions: list[Decision] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    pending_approvals: list[ApprovalRequest] = Field(default_factory=list)
    agent_outputs: dict[str, Any] = Field(default_factory=dict)

    created_at: str = ""
    updated_at: str = ""
    human_approval_needed: bool = False

    def record_phase(self, phase: Phase) -> None:
        from datetime import datetime, timezone
        self.phase_history.append({
            "phase": phase.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.phase = phase
        self.updated_at = datetime.now(timezone.utc).isoformat()
