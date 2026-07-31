from __future__ import annotations

from pydantic import BaseModel, Field

from orchestration.agents.base import AgentResult, BaseAgent
from orchestration.state import ProjectState


class APIDesign(BaseModel):
    endpoint: str
    method: str
    description: str
    request_body: str | None = None
    response: str


class DatabaseTable(BaseModel):
    name: str
    columns: list[dict]
    indexes: list[str] = Field(default_factory=list)
    relationships: list[str] = Field(default_factory=list)


class ArchitectureDecision(BaseModel):
    title: str
    decision: str
    rationale: str
    alternatives: list[str]


class ArchitectureOutput(BaseModel):
    architecture_overview: str
    technology_stack: list[dict] = Field(
        description="List of {layer, technology, justification}"
    )
    system_components: list[str]
    api_design: list[APIDesign]
    database_tables: list[DatabaseTable]
    architecture_decisions: list[ArchitectureDecision]
    identified_risks: list[str]


class ArchitectAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return (
            "You are a Software Architect for an AI Software Engineering Company. "
            "Design system architecture based on product requirements. "
            "Select appropriate technologies with justifications. "
            "Design service boundaries, APIs, database schemas, and "
            "identify architectural risks. Always explain tradeoffs."
        )

    async def execute(self, state: ProjectState) -> AgentResult:
        try:
            reqs = state.requirements or {}
            prompt = (
                f"Project: {state.name}\n"
                f"Description: {state.description}\n\n"
                f"Requirements: {reqs}\n\n"
                "Design the complete system architecture. "
                "Include: architecture overview, technology stack with "
                "justifications, system components, API design, database design, "
                "architecture decisions with rationale, and identified risks."
            )
            output = await self.llm.generate_structured(
                self.system_prompt, prompt, ArchitectureOutput
            )
            return AgentResult(success=True, output=output.model_dump())
        except Exception as e:
            return AgentResult(success=False, output={}, error=str(e))
