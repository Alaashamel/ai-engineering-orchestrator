from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.middleware import RateLimitMiddleware, RequestIDMiddleware
from src.models.database import engine
from src.routers import audit as audit_router
from src.routers import health, projects, workflows

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
    logger.info("Starting AI Software Engineering API")
    try:
        async with engine.begin() as conn:
            from src.models.database import Base
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.warning("Database not available at startup", error=str(e))
    yield
    await engine.dispose()
    logger.info("Shut down AI Software Engineering API")


app = FastAPI(
    title="AI Software Engineering Company",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
if settings.environment == "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.web_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


if settings.environment == "production":
    app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    import structlog
    structlog.get_logger().warning("HTTP exception", status_code=exc.status_code, detail=exc.detail)
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    import structlog
    structlog.get_logger().error("Unhandled exception", exc_info=exc)
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(health.router)
app.include_router(projects.router)
app.include_router(workflows.router)
app.include_router(audit_router.router)


@app.get("/")
async def root():
    return {"message": "AI Software Engineering Company API", "version": "0.1.0"}
