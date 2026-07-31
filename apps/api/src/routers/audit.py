from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit_log import AuditLog
from src.models.database import get_db

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("/")
async def list_audit_logs(
    project_id: UUID | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(AuditLog).order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
    if project_id:
        query = query.where(AuditLog.project_id == project_id)
    result = await db.execute(query)
    logs = result.scalars().all()
    return [
        {
            "id": str(log.id),
            "project_id": str(log.project_id),
            "actor": log.actor,
            "action": log.action,
            "resource_type": log.resource_type,
            "phase": log.phase,
            "outcome": log.outcome,
            "details": log.details,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
