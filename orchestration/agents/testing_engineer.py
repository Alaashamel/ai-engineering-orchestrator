from __future__ import annotations

from pydantic import BaseModel, Field

from orchestration.agents.base import AgentResult, BaseAgent
from orchestration.state import ProjectState


class TestFile(BaseModel):
    path: str = Field(description="Relative path from project root")
    content: str = Field(description="Full test file content")
    description: str = Field(description="What this test covers")


class TestPlan(BaseModel):
    test_files: list[TestFile] = Field(
        description="Test files to create"
    )
    fixtures: list[TestFile] = Field(
        description="Test fixtures and conftest files"
    )
    packages: list[str] = Field(
        description="Testing packages to add"
    )
    summary: str = Field(description="Summary of testing strategy")


class TestingEngineerAgent(BaseAgent):
    __test__ = False  # not a pytest test class — name just starts with "Test"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a Senior QA/Testing Engineer specializing in pytest "
            "and frontend testing. You generate comprehensive test suites including:\n"
            "- Unit tests for API endpoints (using TestClient)\n"
            "- Integration tests for database operations\n"
            "- Frontend component tests (Vitest + Testing Library)\n"
            "- Test fixtures and factories\n"
            "- Mock configurations\n"
            "- Edge case and error scenario coverage\n\n"
            "Follow these conventions:\n"
            "- Use async test functions with pytest-asyncio\n"
            "- Include docstrings explaining each test's purpose\n"
            "- Test success, error, and edge cases\n"
            "- Use factories or fixtures for test data\n"
            "- Mock external services (LLM, email, etc.)\n"
            "- Tests go in tests/ directories mirroring source structure\n"
            "- Backend tests use pytest, frontend tests use Vitest"
        )

    async def generate_tests(
        self, state: ProjectState, instructions: str, existing_files: list[str]
    ) -> TestPlan:
        requirements = state.requirements or {}
        architecture = state.architecture or {}
        prompt = (
            f"Project: {state.name}\n"
            f"Description: {state.description}\n\n"
            f"Requirements: {requirements}\n\n"
            f"Architecture: {architecture}\n\n"
            f"Existing files: {existing_files}\n\n"
            f"Task Instructions: {instructions}\n\n"
            "Generate comprehensive test files. Cover happy paths, "
            "error scenarios, and edge cases."
        )
        return await self.llm.generate_structured(
            self.system_prompt, prompt, TestPlan
        )

    async def execute(self, state: ProjectState) -> AgentResult:
        return AgentResult(
            success=True,
            output={"status": "testing_engineer_ready"},
        )
