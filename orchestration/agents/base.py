from abc import ABC, abstractmethod

from pydantic import BaseModel

from orchestration.llm import LLMProvider
from orchestration.state import ProjectState


class AgentResult(BaseModel):
    success: bool
    output: dict
    error: str | None = None


class BaseAgent(ABC):
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        ...

    @abstractmethod
    async def execute(self, state: ProjectState) -> AgentResult:
        ...
