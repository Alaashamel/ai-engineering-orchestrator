from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from orchestration.audit import get_audit_logger
from orchestration.graph import OrchestrationEngine
from orchestration.state import Phase, ProjectState
from orchestration.webhooks import WebhookNotifier
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.database import get_db
from src.models.project import Project
from src.websocket_manager import manager

router = APIRouter(prefix="/workflows", tags=["workflows"])

_state_store: dict[str, ProjectState] = {}


def _get_engine() -> OrchestrationEngine:
    return OrchestrationEngine()


def _get_webhook() -> WebhookNotifier:
    return WebhookNotifier(webhook_url=settings.webhook_url or None)


def _build_project_state(project: Project) -> ProjectState:
    state = ProjectState(
        project_id=project.id,
        name=project.name,
        description=project.description or "",
        phase=Phase.DISCOVERY,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    _state_store[str(project.id)] = state
    return state


class ApproveBody(BaseModel):
    rollback_to: str | None = None


class RejectBody(BaseModel):
    reason: str = ""
    rollback_to: str | None = None


@router.post("/{project_id}/start")
async def start_workflow(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    engine = _get_engine()
    project_state = _build_project_state(project)

    try:
        result_state = await engine.run(project_state)
        await manager.broadcast(
            str(project_id),
            {"type": "workflow_complete", "state": result_state},
        )
        webhook = _get_webhook()
        await webhook.notify("workflow.completed", str(project_id), {
            "name": project.name,
            "phase": result_state.get("phase"),
            "tasks_count": len(result_state.get("tasks", [])),
            "has_approvals": result_state.get("human_approval_needed", False),
        })
        return {"status": "completed", "state": result_state}
    except Exception as e:
        await manager.broadcast(
            str(project_id),
            {"type": "workflow_error", "error": str(e)},
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/approve")
async def approve_workflow(
    project_id: UUID,
    body: ApproveBody = Body(default=ApproveBody()),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_state = _state_store.get(str(project_id))
    if not project_state:
        raise HTTPException(status_code=400, detail="No workflow in progress for this project")

    engine = _get_engine()
    try:
        result_state = await engine.resume(project_state, approved=True, rollback_to=body.rollback_to)
        get_audit_logger().log(str(project_id), "human", "approve", "workflow",
                                phase=result_state.get("phase"))
        await manager.broadcast(
            str(project_id),
            {"type": "approval_resolved", "approved": True, "state": result_state},
        )
        return {"status": "approved", "state": result_state}
    except Exception as e:
        get_audit_logger().log(str(project_id), "human", "approve", "workflow",
                                outcome="error", details={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/reject")
async def reject_workflow(
    project_id: UUID,
    body: RejectBody = Body(default=RejectBody()),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_state = _state_store.get(str(project_id))
    if not project_state:
        raise HTTPException(status_code=400, detail="No workflow in progress for this project")

    engine = _get_engine()
    try:
        result_state = await engine.resume(project_state, approved=False,
                                            rollback_to=body.rollback_to)
        get_audit_logger().log(str(project_id), "human", "reject", "workflow",
                                details={"reason": body.reason},
                                phase=result_state.get("phase"))
        await manager.broadcast(
            str(project_id),
            {"type": "approval_resolved", "approved": False, "state": result_state},
        )
        return {"status": "rejected", "state": result_state}
    except Exception as e:
        get_audit_logger().log(str(project_id), "human", "reject", "workflow",
                                outcome="error", details={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/rollback")
async def rollback_workflow(
    project_id: UUID,
    body: dict = Body(default={}),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_state = _state_store.get(str(project_id))
    if not project_state:
        raise HTTPException(status_code=400, detail="No workflow in progress for this project")

    target = body.get("rollback_to")
    engine = _get_engine()
    initial = engine.rollback_phase(
        {"phase_history": project_state.phase_history, "phase": project_state.phase.value,
         "errors": [], "updated_at": project_state.updated_at},
        target,
    )
    get_audit_logger().log(str(project_id), "human", "rollback", "workflow",
                            details={"from_phase": project_state.phase.value, "to_phase": initial["phase"]})
    return {"status": "rolled_back", "phase": initial["phase"],
            "phase_history": initial["phase_history"]}


@router.post("/{project_id}/start-stream")
async def start_workflow_stream(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    engine = _get_engine()
    project_state = _build_project_state(project)

    try:
        result_state = await engine.run(project_state)
        tasks = result_state.get("tasks", [])
        return {
            "status": "completed",
            "phase": result_state.get("phase"),
            "tasks_count": len(tasks),
            "decisions_count": len(result_state.get("decisions", [])),
            "errors_count": len(result_state.get("errors", [])),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/status")
async def get_workflow_status(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project_state = _state_store.get(str(project_id))
    return {
        "project_id": str(project.id),
        "name": project.name,
        "status": project.status,
        "description": project.description,
        "workflow_phase": project_state.phase.value if project_state else None,
        "pending_approvals": len(project_state.pending_approvals) if project_state else 0,
    }


@router.websocket("/ws/{project_id}")
async def workflow_websocket(websocket: WebSocket, project_id: str):
    await manager.connect(project_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("action") == "start":
                try:
                    pid = UUID(project_id)
                except ValueError:
                    await manager.broadcast(project_id, {"type": "error", "detail": "Invalid project ID"})
                    continue
                engine = _get_engine()
                project_state = ProjectState(
                    project_id=pid,
                    name=msg.get("name", "Untitled"),
                    description=msg.get("description", ""),
                    phase=Phase.DISCOVERY,
                    created_at=datetime.now(timezone.utc).isoformat(),
                    updated_at=datetime.now(timezone.utc).isoformat(),
                )
                _state_store[project_id] = project_state
                try:
                    result_state = await engine.run(project_state)
                    await manager.broadcast(project_id, {
                        "type": "workflow_complete",
                        "state": result_state,
                    })
                except Exception as e:
                    await manager.broadcast(project_id, {
                        "type": "workflow_error",
                        "error": str(e),
                    })
            elif msg.get("action") == "ping":
                await manager.broadcast(project_id, {"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(project_id, websocket)
    except Exception:
        manager.disconnect(project_id, websocket)
