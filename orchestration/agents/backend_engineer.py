from __future__ import annotations

from pydantic import BaseModel, Field

from orchestration.agents.base import AgentResult, BaseAgent
from orchestration.state import ProjectState


class GeneratedFile(BaseModel):
    path: str = Field(description="Relative path from project root")
    content: str = Field(description="Full file content to write")
    description: str = Field(description="Purpose of this file")


class BackendPlan(BaseModel):
    files_to_create: list[GeneratedFile] = Field(
        description="Backend files to create (models, routers, config, etc.)"
    )
    packages: list[str] = Field(
        description="Python packages to add to requirements.txt"
    )
    summary: str = Field(description="Summary of what was generated")


class BackendEngineerAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return (
            "You are a Senior Backend Engineer specializing in Python/FastAPI. "
            "You generate production-grade backend code including:\n"
            "- SQLAlchemy models with proper relationships\n"
            "- FastAPI routers with validation, error handling, pagination\n"
            "- Pydantic schemas for request/response serialization\n"
            "- Alembic migration setup\n"
            "- Authentication/authorization middleware\n"
            "- Background task processing\n"
            "- API documentation\n\n"
            "Follow these conventions:\n"
            "- Use async endpoints throughout\n"
            "- Type-annotate all function signatures\n"
            "- Include proper error handling with HTTPException\n"
            "- Use dependency injection for shared resources\n"
            "- Follow PEP 8 and use Black formatting\n"
            "- All models inherit from the shared Base\n"
            "- All routers use APIRouter with consistent prefixing"
        )

    async def generate_backend(
        self, state: ProjectState, instructions: str
    ) -> BackendPlan:
        requirements = state.requirements or {}
        architecture = state.architecture or {}
        prompt = (
            f"Project: {state.name}\n"
            f"Description: {state.description}\n\n"
            f"Requirements: {requirements}\n\n"
            f"Architecture: {architecture}\n\n"
            f"Task Instructions: {instructions}\n\n"
            "Generate complete backend code files. Each file must have "
            "a relative path and full production-ready content."
        )
        return await self.llm.generate_structured(
            self.system_prompt, prompt, BackendPlan
        )

    async def execute(self, state: ProjectState) -> AgentResult:
        return AgentResult(
            success=True,
            output={"status": "backend_engineer_ready"},
        )
