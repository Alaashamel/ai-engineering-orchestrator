from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from orchestration.graph import OrchestrationEngine
from orchestration.state import Phase, ProjectState
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import get_db
from src.models.project import Project
from src.websocket_manager import manager

router = APIRouter(prefix="/workflows", tags=["workflows"])

_engines: dict[UUID, OrchestrationEngine] = {}


def _get_engine() -> OrchestrationEngine:
    return OrchestrationEngine()


@router.post("/{project_id}/start")
async def start_workflow(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    engine = _get_engine()
    project_state = ProjectState(
        project_id=project.id,
        name=project.name,
        description=project.description or "",
        phase=Phase.DISCOVERY,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )

    try:
        result_state = await engine.run(project_state)
        await manager.broadcast(
            str(project_id),
            {"type": "workflow_complete", "state": result_state},
        )
        return {"status": "completed", "state": result_state}
    except Exception as e:
        await manager.broadcast(
            str(project_id),
            {"type": "workflow_error", "error": str(e)},
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/start-stream")
async def start_workflow_stream(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    engine = _get_engine()
    project_state = ProjectState(
        project_id=project.id,
        name=project.name,
        description=project.description or "",
        phase=Phase.DISCOVERY,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )

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
    return {
        "project_id": str(project.id),
        "name": project.name,
        "status": project.status,
        "description": project.description,
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
