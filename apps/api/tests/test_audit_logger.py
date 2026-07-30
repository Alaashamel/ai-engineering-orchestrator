from uuid import uuid4
from orchestration.audit import AuditLogger

def test_audit_logger_buffers_entries():
    logger = AuditLogger()
    logger.log(uuid4(), "test", "action", "resource")
    assert len(logger.entries) == 1
    assert logger.entries[0]["actor"] == "test"
    assert logger.entries[0]["outcome"] == "success"

def test_audit_logger_stores_details():
    logger = AuditLogger()
    logger.log(uuid4(), "test", "action", "resource", details={"key": "val"})
    assert logger.entries[0]["details"]["key"] == "val"

def test_audit_logger_flush_without_session():
    import pytest
    logger = AuditLogger()
    logger.log(uuid4(), "test", "action", "resource")
    import asyncio
    asyncio.run(logger.flush())
    assert len(logger.entries) == 1  # no session factory = no flush
