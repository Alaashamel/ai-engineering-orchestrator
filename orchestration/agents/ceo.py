from __future__ import annotations

from pydantic import BaseModel, Field

from orchestration.agents.base import AgentResult, BaseAgent
from orchestration.state import Phase, ProjectState, TaskItem


class DiscoveryOutput(BaseModel):
    project_type: str = Field(description="Type of software project")
    complexity: str = Field(description="Low, medium, or high")
    key_objectives: list[str] = Field(description="Main objectives")
    risks: list[str] = Field(description="Identified risks")
    recommended_approach: str = Field(description="Suggested development approach")
    reasoning: str = Field(description="CEO reasoning for the analysis")


class TaskDecompositionOutput(BaseModel):
    tasks: list[TaskItem] = Field(description="List of engineering tasks")


class CEOAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return (
            "You are the CEO of an AI Software Engineering Company. "
            "You analyze project requests, break them down into phases, "
            "delegate work to specialized agents, and ensure quality. "
            "Always reason step by step before making decisions."
        )

    async def discovery_phase(self, state: ProjectState) -> DiscoveryOutput:
        prompt = (
            f"Project: {state.name}\n"
            f"Description: {state.description}\n\n"
            "Analyze this project request. Identify the project type, "
            "complexity, key objectives, risks, and recommended approach."
        )
        return await self.llm.generate_structured(
            self.system_prompt, prompt, DiscoveryOutput
        )

    async def decompose_tasks(
        self, state: ProjectState
    ) -> TaskDecompositionOutput:
        requirements = state.requirements or {}
        architecture = state.architecture or {}
        prompt = (
            f"Project: {state.name}\n"
            f"Description: {state.description}\n\n"
            f"Requirements: {requirements}\n\n"
            f"Architecture: {architecture}\n\n"
            "Break this project into concrete engineering tasks. "
            "Each task must have: id, title, description, agent "
            "(backend_engineer, frontend_engineer, database_engineer, "
            "ai_engineer, qa_engineer, security_engineer, devops_engineer, "
            "documentation), priority (critical, high, medium, low), "
            "and dependencies (list of task ids this depends on)."
        )
        return await self.llm.generate_structured(
            self.system_prompt, prompt, TaskDecompositionOutput
        )

    async def decide_next_phase(self, state: ProjectState) -> Phase:
        history = state.phase_history
        last_phase = history[-1]["phase"] if history else None

        phase_order = [
            Phase.DISCOVERY,
            Phase.PLANNING,
            Phase.ARCHITECTURE,
            Phase.TASK_DECOMPOSITION,
            Phase.IMPLEMENTATION,
            Phase.TESTING,
            Phase.REVIEW,
            Phase.DOCUMENTATION,
            Phase.DEPLOYMENT,
            Phase.COMPLETED,
        ]

        if last_phase is None:
            return Phase.DISCOVERY

        for i, p in enumerate(phase_order):
            if p.value == last_phase and i + 1 < len(phase_order):
                next_phase = phase_order[i + 1]
                if next_phase == Phase.IMPLEMENTATION and state.errors:
                    return Phase.FAILED
                return next_phase

        return Phase.COMPLETED

    async def execute(self, state: ProjectState) -> AgentResult:
        return AgentResult(success=True, output={
            "decision": "delegate",
            "next_phase": (await self.decide_next_phase(state)).value,
        })
