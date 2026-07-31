from __future__ import annotations

from pydantic import BaseModel, Field

from orchestration.agents.base import AgentResult, BaseAgent
from orchestration.state import ProjectState


class GeneratedComponent(BaseModel):
    path: str = Field(description="Relative path from project root")
    content: str = Field(description="Full component file content")
    description: str = Field(description="Purpose of this component")


class FrontendPlan(BaseModel):
    components: list[GeneratedComponent] = Field(
        description="Frontend components to create"
    )
    pages: list[GeneratedComponent] = Field(
        description="Page-level components (one per route)"
    )
    hooks: list[GeneratedComponent] = Field(
        description="Custom React hooks"
    )
    packages: list[str] = Field(
        description="npm packages to install"
    )
    summary: str = Field(description="Summary of what was generated")


class FrontendEngineerAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return (
            "You are a Senior Frontend Engineer specializing in React/TypeScript. "
            "You generate production-grade frontend code including:\n"
            "- TypeScript React components with proper typing\n"
            "- Custom hooks for data fetching and state management\n"
            "- Page layouts with responsive design\n"
            "- API client integration\n"
            "- Form validation and error handling\n"
            "- Loading and empty states\n\n"
            "Follow these conventions:\n"
            "- Use functional components with hooks throughout\n"
            "- Type-annotate all props and state\n"
            "- Handle loading, error, and empty states\n"
            "- Use CSS modules or Tailwind utility classes\n"
            "- Import types from shared types file\n"
            "- Use the existing API client from src/api/client.ts\n"
            "- Components go in src/components/, pages in src/pages/"
        )

    async def generate_frontend(
        self, state: ProjectState, instructions: str
    ) -> FrontendPlan:
        requirements = state.requirements or {}
        architecture = state.architecture or {}
        prompt = (
            f"Project: {state.name}\n"
            f"Description: {state.description}\n\n"
            f"Requirements: {requirements}\n\n"
            f"Architecture: {architecture}\n\n"
            f"Task Instructions: {instructions}\n\n"
            "Generate complete frontend code files. Each component must have "
            "a relative path and full production-ready content."
        )
        return await self.llm.generate_structured(
            self.system_prompt, prompt, FrontendPlan
        )

    async def execute(self, state: ProjectState) -> AgentResult:
        return AgentResult(
            success=True,
            output={"status": "frontend_engineer_ready"},
        )
