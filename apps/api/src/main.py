from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.models.database import engine
from src.routers import health, projects

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
    logger.info("Starting AI Software Engineering API")
    try:
        async with engine.begin() as conn:
            from src.models.database import Base
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:  # noqa: BLE001
        logger.warning("Database not available at startup", error=str(e))
    yield
    await engine.dispose()
    logger.info("Shut down AI Software Engineering API")


app = FastAPI(
    title="AI Software Engineering Company",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(projects.router)


@app.get("/")
async def root():
    return {"message": "AI Software Engineering Company API", "version": "0.1.0"}
