from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID

from langgraph.graph import END, StateGraph
from langgraph.types import Command
from typing_extensions import TypedDict

from orchestration.agents.architect import ArchitectAgent
from orchestration.agents.ceo import CEOAgent
from orchestration.agents.product_manager import ProductManagerAgent
from orchestration.llm import LLMProvider
from orchestration.state import ApprovalRequest, Decision, Phase, ProjectState, TaskItem


class GraphState(TypedDict):
    project_id: str
    name: str
    description: str
    phase: str
    phase_history: list
    requirements: Any
    architecture: Any
    tasks: list
    decisions: list
    errors: list
    pending_approvals: list
    agent_outputs: dict
    created_at: str
    updated_at: str
    human_approval_needed: bool


def _project_to_graph(state: ProjectState) -> GraphState:
    return state.model_dump()


def _graph_to_project(data: GraphState) -> ProjectState:
    tasks = [TaskItem(**t) if isinstance(t, dict) else t for t in data.get("tasks", [])]
    decisions = [Decision(**d) if isinstance(d, dict) else d for d in data.get("decisions", [])]
    approvals = [
        ApprovalRequest(**a) if isinstance(a, dict) else a
        for a in data.get("pending_approvals", [])
    ]
    return ProjectState(
        project_id=data["project_id"] if isinstance(data["project_id"], UUID) else UUID(data["project_id"]),
        name=data.get("name", ""),
        description=data.get("description", ""),
        phase=Phase(data.get("phase", "discovery")),
        phase_history=data.get("phase_history", []),
        requirements=data.get("requirements"),
        architecture=data.get("architecture"),
        tasks=tasks,
        decisions=decisions,
        errors=data.get("errors", []),
        pending_approvals=approvals,
        agent_outputs=data.get("agent_outputs", {}),
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", ""),
        human_approval_needed=data.get("human_approval_needed", False),
    )


class OrchestrationEngine:
    def __init__(self, llm: LLMProvider | None = None):
        self.llm = llm or LLMProvider()
        self.ceo = CEOAgent(self.llm)
        self.pm = ProductManagerAgent(self.llm)
        self.architect = ArchitectAgent(self.llm)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(GraphState)

        builder.add_node("discovery", self._discovery_node)
        builder.add_node("planning", self._planning_node)
        builder.add_node("architecture", self._architecture_node)
        builder.add_node("task_decomposition", self._task_decomposition_node)
        builder.add_node("check_approvals", self._check_approvals_node)
        builder.add_node("complete", self._complete_node)
        builder.add_node("fail", self._fail_node)

        builder.add_conditional_edges("discovery", self._route_after_discovery)
        builder.add_conditional_edges("planning", self._route_after_planning)
        builder.add_conditional_edges("architecture", self._route_after_architecture)
        builder.add_conditional_edges("task_decomposition", self._route_after_decomposition)
        builder.add_conditional_edges("check_approvals", self._route_after_approvals)

        builder.set_entry_point("discovery")

        return builder.compile()

    def _add_decision(self, state: GraphState, agent: str, action: str, reasoning: str) -> None:
        state.setdefault("decisions", [])
        state["decisions"].append({
            "agent": agent,
            "action": action,
            "reasoning": reasoning,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def _sync_phase(self, state: GraphState, phase: Phase) -> None:
        history = state.get("phase_history", [])
        history.append({
            "phase": phase.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        state["phase_history"] = history
        state["phase"] = phase.value
        state["updated_at"] = datetime.now(timezone.utc).isoformat()

    async def _discovery_node(self, state: GraphState) -> Command[Literal["planning", "fail"]]:
        try:
            self._sync_phase(state, Phase.DISCOVERY)
            ps = _graph_to_project(state)
            result = await self.ceo.discovery_phase(ps)
            self._add_decision(state, "ceo", "discovery_analysis", result.reasoning)
            state["agent_outputs"] = state.get("agent_outputs", {})
            state["agent_outputs"]["discovery"] = result.model_dump()
            return Command(update=state, goto="planning")
        except Exception as e:
            state.setdefault("errors", [])
            state["errors"].append({"phase": "discovery", "error": str(e)})
            return Command(update=state, goto="fail")

    async def _planning_node(self, state: GraphState) -> Command[Literal["architecture", "fail"]]:
        try:
            self._sync_phase(state, Phase.PLANNING)
            ps = _graph_to_project(state)
            result = await self.pm.execute(ps)
            if not result.success:
                raise ValueError(result.error or "Planning failed")
            state["requirements"] = result.output
            state["agent_outputs"]["requirements"] = result.output
            self._add_decision(state, "product_manager", "requirements_defined",
                               "Product requirements have been documented")
            return Command(update=state, goto="architecture")
        except Exception as e:
            state.setdefault("errors", [])
            state["errors"].append({"phase": "planning", "error": str(e)})
            return Command(update=state, goto="fail")

    async def _architecture_node(self, state: GraphState) -> Command[Literal["task_decomposition", "fail"]]:
        try:
            self._sync_phase(state, Phase.ARCHITECTURE)
            ps = _graph_to_project(state)
            result = await self.architect.execute(ps)
            if not result.success:
                raise ValueError(result.error or "Architecture failed")
            state["architecture"] = result.output
            state["agent_outputs"]["architecture"] = result.output
            self._add_decision(state, "architect", "architecture_designed",
                               "System architecture has been designed")
            return Command(update=state, goto="task_decomposition")
        except Exception as e:
            state.setdefault("errors", [])
            state["errors"].append({"phase": "architecture", "error": str(e)})
            return Command(update=state, goto="fail")

    async def _task_decomposition_node(self, state: GraphState) -> Command[Literal["check_approvals", "fail"]]:
        try:
            self._sync_phase(state, Phase.TASK_DECOMPOSITION)
            ps = _graph_to_project(state)
            result = await self.ceo.decompose_tasks(ps)
            tasks = result.tasks
            state["tasks"] = [t.model_dump() for t in tasks]
            state["agent_outputs"]["tasks"] = [t.model_dump() for t in tasks]
            self._add_decision(state, "ceo", "tasks_decomposed",
                               f"Decomposed into {len(tasks)} engineering tasks")
            return Command(update=state, goto="check_approvals")
        except Exception as e:
            state.setdefault("errors", [])
            state["errors"].append({"phase": "task_decomposition", "error": str(e)})
            return Command(update=state, goto="fail")

    async def _check_approvals_node(self, state: GraphState) -> Command[Literal["complete", "fail"]]:
        critical_tasks = [t for t in state.get("tasks", []) if t.get("priority") == "critical"]
        if critical_tasks:
            approvals = state.get("pending_approvals", [])
            for t in critical_tasks:
                approvals.append({
                    "id": f"approval_{t['id']}",
                    "action": f"Execute task: {t['title']}",
                    "description": t.get("description", ""),
                    "risk_level": "medium",
                    "proposed_by": "ceo",
                    "status": "pending",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })
            state["pending_approvals"] = approvals
            state["human_approval_needed"] = True

        state["phase"] = Phase.TASK_DECOMPOSITION.value
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        return Command(update=state, goto="complete")

    def _complete_node(self, state: GraphState) -> Command[Literal[END]]:
        state["phase"] = Phase.COMPLETED.value
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        return Command(update=state, goto=END)

    def _fail_node(self, state: GraphState) -> Command[Literal[END]]:
        state["phase"] = Phase.FAILED.value
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        return Command(update=state, goto=END)

    def _route_after_discovery(self, state: GraphState) -> str:
        errors = state.get("errors", [])
        if any(e.get("phase") == "discovery" for e in errors):
            return "fail"
        return "planning"

    def _route_after_planning(self, state: GraphState) -> str:
        errors = state.get("errors", [])
        if any(e.get("phase") == "planning" for e in errors):
            return "fail"
        return "architecture"

    def _route_after_architecture(self, state: GraphState) -> str:
        errors = state.get("errors", [])
        if any(e.get("phase") == "architecture" for e in errors):
            return "fail"
        return "task_decomposition"

    def _route_after_decomposition(self, state: GraphState) -> str:
        errors = state.get("errors", [])
        if any(e.get("phase") == "task_decomposition" for e in errors):
            return "fail"
        return "check_approvals"

    def _route_after_approvals(self, state: GraphState) -> str:
        return "complete"

    async def run(self, project_state: ProjectState) -> GraphState:
        initial = _project_to_graph(project_state)
        result = await self.graph.ainvoke(initial)
        return result

    async def run_stream(self, project_state: ProjectState):
        initial = _project_to_graph(project_state)
        async for event in self.graph.astream(initial):
            yield event
