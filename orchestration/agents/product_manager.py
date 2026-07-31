from __future__ import annotations

from pydantic import BaseModel

from orchestration.agents.base import AgentResult, BaseAgent
from orchestration.state import ProjectState


class FunctionalRequirement(BaseModel):
    id: str
    title: str
    description: str
    priority: str


class UserStory(BaseModel):
    id: str
    as_a: str
    i_want: str
    so_that: str
    acceptance_criteria: list[str]


class ProductRequirementsOutput(BaseModel):
    product_name: str
    vision: str
    target_users: list[str]
    functional_requirements: list[FunctionalRequirement]
    non_functional_requirements: list[str]
    user_stories: list[UserStory]
    mvp_features: list[str]
    future_features: list[str]
    open_questions: list[str]


class ProductManagerAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return (
            "You are a Product Manager for an AI Software Engineering Company. "
            "Your role is to analyze project requests and produce a comprehensive "
            "Product Requirements Document. Identify functional requirements, "
            "non-functional requirements, user stories with acceptance criteria, "
            "MVP scope, and future features. Flag ambiguous requirements."
        )

    async def execute(self, state: ProjectState) -> AgentResult:
        try:
            state.record_phase(state.phase)
            prompt = (
                f"Project: {state.name}\n"
                f"Description: {state.description}\n\n"
                "Produce a complete Product Requirements Document. "
                "Include product vision, target users, functional requirements, "
                "non-functional requirements, user stories with acceptance criteria, "
                "MVP features, future features, and any open questions."
            )
            output = await self.llm.generate_structured(
                self.system_prompt, prompt, ProductRequirementsOutput
            )
            return AgentResult(success=True, output=output.model_dump())
        except Exception as e:
            return AgentResult(success=False, output={}, error=str(e))
