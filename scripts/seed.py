"""Seed the database with sample projects for development."""
import asyncio
import uuid
from datetime import datetime

async def seed():
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from src.models.database import Base
    from src.models.project import Project

    engine = create_async_engine("postgresql+asyncpg://app:app_password@localhost:5432/ai_software_company")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        projects = [
            Project(
                id=uuid.uuid4(), name="E-Commerce Platform",
                description="Full e-commerce with auth, cart, checkout",
                status="discovery",
            ),
            Project(
                id=uuid.uuid4(), name="Blog Engine",
                description="Markdown blog with CMS and comments",
                status="planning",
            ),
            Project(
                id=uuid.uuid4(), name="Task Manager API",
                description="REST API for task management with real-time updates",
                status="completed",
            ),
        ]
        for p in projects:
            session.add(p)
        await session.commit()
        print(f"Seeded {len(projects)} projects")

asyncio.run(seed())
