from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from langgraph.graph import StateGraph
from typing_extensions import TypedDict

from orchestration.agents.architect import ArchitectAgent
from orchestration.agents.backend_engineer import BackendEngineerAgent
from orchestration.agents.ceo import CEOAgent
from orchestration.agents.frontend_engineer import FrontendEngineerAgent
from orchestration.agents.product_manager import ProductManagerAgent
from orchestration.agents.testing_engineer import TestingEngineerAgent
from orchestration.audit import get_audit_logger
from orchestration.llm import LLMProvider
from orchestration.state import (
    ApprovalRequest,
    Decision,
    GeneratedFileRecord,
    Phase,
    ProjectState,
    TaskItem,
)
from orchestration.tools import FileSystemTool
from orchestration.tracing import get_tracer


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
    generated_files: list
    implementation_log: list
    project_root: str


def _project_to_graph(state: ProjectState) -> GraphState:
    return state.model_dump()


def _graph_to_project(data: GraphState) -> ProjectState:
    tasks = [TaskItem(**t) if isinstance(t, dict) else t for t in data.get("tasks", [])]
    decisions = [Decision(**d) if isinstance(d, dict) else d for d in data.get("decisions", [])]
    approvals = [
        ApprovalRequest(**a) if isinstance(a, dict) else a
        for a in data.get("pending_approvals", [])
    ]
    files = [
        GeneratedFileRecord(**f) if isinstance(f, dict) else f
        for f in data.get("generated_files", [])
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
        generated_files=files,
        implementation_log=data.get("implementation_log", []),
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", ""),
        human_approval_needed=data.get("human_approval_needed", False),
    )


class OrchestrationEngine:
    def __init__(self, llm: LLMProvider | None = None, project_root: str | None = None):
        self.llm = llm or LLMProvider()
        self.ceo = CEOAgent(self.llm)
        self.pm = ProductManagerAgent(self.llm)
        self.architect = ArchitectAgent(self.llm)
        self.backend_engineer = BackendEngineerAgent(self.llm)
        self.frontend_engineer = FrontendEngineerAgent(self.llm)
        self.testing_engineer = TestingEngineerAgent(self.llm)
        self.project_root = project_root or str(Path.cwd())
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(GraphState)

        builder.add_node("discovery", self._discovery_node)
        builder.add_node("planning", self._planning_node)
        builder.add_node("architecture", self._architecture_node)
        builder.add_node("task_decomposition", self._task_decomposition_node)
        builder.add_node("check_approvals", self._check_approvals_node)
        builder.add_node("implementation", self._implementation_node)
        builder.add_node("complete", self._complete_node)
        builder.add_node("fail", self._fail_node)

        builder.add_conditional_edges("discovery", self._route_after_discovery)
        builder.add_conditional_edges("planning", self._route_after_planning)
        builder.add_conditional_edges("architecture", self._route_after_architecture)
        builder.add_conditional_edges("task_decomposition", self._route_after_decomposition)
        builder.add_conditional_edges("check_approvals", self._route_approvals)
        builder.add_conditional_edges("implementation", self._route_implementation)

        builder.set_entry_point("discovery")

        return builder.compile()

    def _enter_phase(self, state: GraphState, phase: Phase) -> dict:
        history = list(state.get("phase_history", []))
        history.append({
            "phase": phase.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return {
            "phase": phase.value,
            "phase_history": history,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _add_decision(self, state: GraphState, agent: str, action: str, reasoning: str) -> dict:
        decisions = list(state.get("decisions", []))
        decisions.append({
            "agent": agent,
            "action": action,
            "reasoning": reasoning,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return {"decisions": decisions}

    async def _discovery_node(self, state: GraphState) -> dict:
        tracer = get_tracer()
        pid = state.get("project_id", "unknown")
        with tracer.start_as_current_span("phase.discovery", attributes={"project_id": pid}):
            try:
                updates = self._enter_phase(state, Phase.DISCOVERY)
                ps = _graph_to_project(state)
                result = await self.ceo.discovery_phase(ps)
                updates.update(self._add_decision(state, "ceo", "discovery_analysis", result.reasoning))
                agent_outputs = dict(state.get("agent_outputs", {}))
                agent_outputs["discovery"] = result.model_dump()
                updates["agent_outputs"] = agent_outputs
                get_audit_logger().log(pid, "ceo", "discovery_analysis", "project", phase="discovery")
                return updates
            except Exception as e:
                errors = list(state.get("errors", []))
                errors.append({"phase": "discovery", "error": str(e)})
                get_audit_logger().log(pid, "ceo", "discovery_analysis", "project", phase="discovery", outcome="error", details={"error": str(e)})
                return {"errors": errors}

    async def _planning_node(self, state: GraphState) -> dict:
        tracer = get_tracer()
        pid = state.get("project_id", "unknown")
        with tracer.start_as_current_span("phase.planning", attributes={"project_id": pid}):
            try:
                updates = self._enter_phase(state, Phase.PLANNING)
                ps = _graph_to_project(state)
                result = await self.pm.execute(ps)
                if not result.success:
                    raise ValueError(result.error or "Planning failed")
                updates["requirements"] = result.output
                agent_outputs = dict(state.get("agent_outputs", {}))
                agent_outputs["requirements"] = result.output
                updates["agent_outputs"] = agent_outputs
                updates.update(self._add_decision(state, "product_manager", "requirements_defined",
                                                    "Product requirements have been documented"))
                get_audit_logger().log(pid, "product_manager", "requirements_defined", "requirements", phase="planning")
                return updates
            except Exception as e:
                errors = list(state.get("errors", []))
                errors.append({"phase": "planning", "error": str(e)})
                get_audit_logger().log(pid, "product_manager", "requirements_defined", "requirements", phase="planning", outcome="error", details={"error": str(e)})
                return {"errors": errors}

    async def _architecture_node(self, state: GraphState) -> dict:
        tracer = get_tracer()
        pid = state.get("project_id", "unknown")
        with tracer.start_as_current_span("phase.architecture", attributes={"project_id": pid}):
            try:
                updates = self._enter_phase(state, Phase.ARCHITECTURE)
                ps = _graph_to_project(state)
                result = await self.architect.execute(ps)
                if not result.success:
                    raise ValueError(result.error or "Architecture failed")
                updates["architecture"] = result.output
                agent_outputs = dict(state.get("agent_outputs", {}))
                agent_outputs["architecture"] = result.output
                updates["agent_outputs"] = agent_outputs
                updates.update(self._add_decision(state, "architect", "architecture_designed",
                                                    "System architecture has been designed"))
                get_audit_logger().log(pid, "architect", "architecture_designed", "architecture", phase="architecture")
                return updates
            except Exception as e:
                errors = list(state.get("errors", []))
                errors.append({"phase": "architecture", "error": str(e)})
                get_audit_logger().log(pid, "architect", "architecture_designed", "architecture", phase="architecture", outcome="error", details={"error": str(e)})
                return {"errors": errors}

    async def _task_decomposition_node(self, state: GraphState) -> dict:
        tracer = get_tracer()
        pid = state.get("project_id", "unknown")
        with tracer.start_as_current_span("phase.task_decomposition", attributes={"project_id": pid}):
            try:
                updates = self._enter_phase(state, Phase.TASK_DECOMPOSITION)
                ps = _graph_to_project(state)
                result = await self.ceo.decompose_tasks(ps)
                tasks = result.tasks
                updates["tasks"] = [t.model_dump() for t in tasks]
                agent_outputs = dict(state.get("agent_outputs", {}))
                agent_outputs["tasks"] = [t.model_dump() for t in tasks]
                updates["agent_outputs"] = agent_outputs
                updates.update(self._add_decision(state, "ceo", "tasks_decomposed",
                                                    f"Decomposed into {len(tasks)} engineering tasks"))
                get_audit_logger().log(pid, "ceo", "tasks_decomposed", "tasks", phase="task_decomposition", details={"task_count": len(tasks)})
                return updates
            except Exception as e:
                errors = list(state.get("errors", []))
                errors.append({"phase": "task_decomposition", "error": str(e)})
                get_audit_logger().log(pid, "ceo", "tasks_decomposed", "tasks", phase="task_decomposition", outcome="error", details={"error": str(e)})
                return {"errors": errors}

    async def _check_approvals_node(self, state: GraphState) -> dict:
        updates: dict = {}
        critical_tasks = [t for t in state.get("tasks", []) if t.get("priority") == "critical"]
        if critical_tasks:
            approvals = list(state.get("pending_approvals", []))
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
            updates["pending_approvals"] = approvals
            updates["human_approval_needed"] = True
        return updates

    def _get_pending_tasks(self, state: GraphState, agent_type: str) -> list[dict]:
        return [
            t for t in state.get("tasks", [])
            if t.get("agent") == agent_type and t.get("status") == "pending"
        ]

    def _mark_tasks_done(self, state: GraphState, task_ids: list[str]) -> list:
        tasks = list(state.get("tasks", []))
        for t in tasks:
            if t.get("id") in task_ids:
                t["status"] = "completed"
        return tasks

    async def _implementation_node(self, state: GraphState) -> dict:
        tracer = get_tracer()
        pid = state.get("project_id", "unknown")
        with tracer.start_as_current_span("phase.implementation", attributes={"project_id": pid}):
            try:
                updates = self._enter_phase(state, Phase.IMPLEMENTATION)
                updates["generated_files"] = list(state.get("generated_files", []))
                impl_log = list(state.get("implementation_log", []))

                fs = FileSystemTool(state.get("project_root", self.project_root))

                backend_tasks = self._get_pending_tasks(state, "backend_engineer")
                frontend_tasks = self._get_pending_tasks(state, "frontend_engineer")
                testing_tasks = self._get_pending_tasks(state, "qa_engineer")

                handled_ids: list[str] = []

                if not (backend_tasks or frontend_tasks or testing_tasks):
                    all_pending = [t for t in state.get("tasks", []) if t.get("status") == "pending"]
                    for t in all_pending:
                        handled_ids.append(t["id"])
                    impl_log.append({
                        "phase": "implementation",
                        "action": "no_pending_tasks",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
                    updates["tasks"] = self._mark_tasks_done(state, handled_ids)
                    updates["implementation_log"] = impl_log
                    return updates

                if backend_tasks:
                    instructions = "\n".join(
                        f"- {t['title']}: {t['description']}" for t in backend_tasks
                    )
                    ps = _graph_to_project(state)
                    plan = await self.backend_engineer.generate_backend(ps, instructions)
                    for f in plan.files_to_create:
                        try:
                            fs.write_file(f.path, f.content)
                            updates["generated_files"].append({
                                "path": f.path, "agent": "backend_engineer",
                                "task_id": backend_tasks[0]["id"], "status": "written",
                                "content_preview": f.content[:100],
                            })
                        except Exception as e:
                            updates["generated_files"].append({
                                "path": f.path, "agent": "backend_engineer",
                                "task_id": backend_tasks[0]["id"], "status": "error",
                                "content_preview": str(e),
                            })
                    handled_ids.extend(t["id"] for t in backend_tasks)
                    impl_log.append({
                        "phase": "implementation",
                        "action": "backend_files_created",
                        "count": len(plan.files_to_create),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })

                if frontend_tasks:
                    instructions = "\n".join(
                        f"- {t['title']}: {t['description']}" for t in frontend_tasks
                    )
                    ps = _graph_to_project(state)
                    plan = await self.frontend_engineer.generate_frontend(ps, instructions)
                    all_components = plan.components + plan.pages + plan.hooks
                    for c in all_components:
                        try:
                            fs.write_file(c.path, c.content)
                            updates["generated_files"].append({
                                "path": c.path, "agent": "frontend_engineer",
                                "task_id": frontend_tasks[0]["id"], "status": "written",
                                "content_preview": c.content[:100],
                            })
                        except Exception as e:
                            updates["generated_files"].append({
                                "path": c.path, "agent": "frontend_engineer",
                                "task_id": frontend_tasks[0]["id"], "status": "error",
                                "content_preview": str(e),
                            })
                    handled_ids.extend(t["id"] for t in frontend_tasks)
                    impl_log.append({
                        "phase": "implementation",
                        "action": "frontend_files_created",
                        "count": len(all_components),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })

                if testing_tasks:
                    existing_files = fs.list_files_by_extension(".py")
                    existing_files += fs.list_files_by_extension(".tsx")
                    instructions = "\n".join(
                        f"- {t['title']}: {t['description']}" for t in testing_tasks
                    )
                    ps = _graph_to_project(state)
                    plan = await self.testing_engineer.generate_tests(ps, instructions, existing_files)
                    for tf in plan.test_files + plan.fixtures:
                        try:
                            fs.write_file(tf.path, tf.content)
                            updates["generated_files"].append({
                                "path": tf.path, "agent": "qa_engineer",
                                "task_id": testing_tasks[0]["id"], "status": "written",
                                "content_preview": tf.content[:100],
                            })
                        except Exception as e:
                            updates["generated_files"].append({
                                "path": tf.path, "agent": "qa_engineer",
                                "task_id": testing_tasks[0]["id"], "status": "error",
                                "content_preview": str(e),
                            })
                    handled_ids.extend(t["id"] for t in testing_tasks)
                    impl_log.append({
                        "phase": "implementation",
                        "action": "test_files_created",
                        "count": len(plan.test_files) + len(plan.fixtures),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })

                updates["tasks"] = self._mark_tasks_done(state, handled_ids)
                updates["implementation_log"] = impl_log

                get_audit_logger().log(pid, "orchestrator", "implementation_complete", "project", phase="implementation", details={"files_created": len(updates["generated_files"])})
                return updates
            except Exception as e:
                errors = list(state.get("errors", []))
                errors.append({"phase": "implementation", "error": str(e)})
                get_audit_logger().log(pid, "orchestrator", "implementation_complete", "project", phase="implementation", outcome="error", details={"error": str(e)})
                return {"errors": errors}

    def _complete_node(self, state: GraphState) -> dict:
        pid = state.get("project_id", "unknown")
        get_audit_logger().log(pid, "orchestrator", "workflow_complete", "project", phase="completed")
        return self._enter_phase(state, Phase.COMPLETED)

    def _fail_node(self, state: GraphState) -> dict:
        return self._enter_phase(state, Phase.FAILED)

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

    def _route_approvals(self, state: GraphState) -> str:
        pending_tasks = [t for t in state.get("tasks", []) if t.get("status") == "pending"]
        if pending_tasks:
            return "implementation"
        return "complete"

    def _route_implementation(self, state: GraphState) -> str:
        errors = state.get("errors", [])
        if any(e.get("phase") == "implementation" for e in errors):
            return "fail"
        pending_tasks = [t for t in state.get("tasks", []) if t.get("status") == "pending"]
        if pending_tasks:
            return "implementation"
        return "check_approvals"

    def rollback_phase(self, state: dict[str, Any], target_phase: str | None = None) -> dict[str, Any]:
        history = list(state.get("phase_history", []))
        if not history:
            return state
        if target_phase:
            idx = next((i for i, h in enumerate(history) if h["phase"] == target_phase), -1)
            if idx == -1:
                return state
            history = history[: idx + 1]
            new_phase = target_phase
        else:
            history = history[:-1]
            new_phase = history[-1]["phase"] if history else "discovery"
        cleaned = dict(state)
        cleaned["phase"] = new_phase
        cleaned["phase_history"] = history
        cleaned["errors"] = [e for e in cleaned.get("errors", [])
                             if e.get("phase") != state.get("phase")]
        cleaned["updated_at"] = datetime.now(timezone.utc).isoformat()
        return cleaned

    def approve_all(self, state: dict[str, Any]) -> dict[str, Any]:
        approvals = list(state.get("pending_approvals", []))
        for a in approvals:
            a["status"] = "approved"
            a["resolved_at"] = datetime.now(timezone.utc).isoformat()
        state["pending_approvals"] = approvals
        state["human_approval_needed"] = False
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        return state

    def reject_all(self, state: dict[str, Any], reason: str = "") -> dict[str, Any]:
        approvals = list(state.get("pending_approvals", []))
        for a in approvals:
            a["status"] = "rejected"
            a["reason"] = reason
            a["resolved_at"] = datetime.now(timezone.utc).isoformat()
        state["pending_approvals"] = approvals
        state["human_approval_needed"] = False
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        return state

    async def resume(
        self, project_state: ProjectState, approved: bool = True, rollback_to: str | None = None
    ) -> GraphState:
        initial = _project_to_graph(project_state)
        if rollback_to:
            initial = self.rollback_phase(initial, rollback_to)
        if approved:
            initial = self.approve_all(initial)
        else:
            initial = self.reject_all(initial)
        return await self.graph.ainvoke(initial)

    async def run(self, project_state: ProjectState) -> GraphState:
        initial = _project_to_graph(project_state)
        result = await self.graph.ainvoke(initial)
        return result

    async def run_stream(self, project_state: ProjectState):
        initial = _project_to_graph(project_state)
        async for event in self.graph.astream(initial):
            yield event
