from datetime import datetime, timezone
from uuid import uuid4

import pytest
from orchestration.agents.backend_engineer import BackendEngineerAgent
from orchestration.agents.frontend_engineer import FrontendEngineerAgent
from orchestration.agents.testing_engineer import TestingEngineerAgent
from orchestration.llm import LLMProvider
from orchestration.state import Phase, ProjectState, TaskItem
from orchestration.tools.file_system import FileSystemTool


@pytest.fixture
def project_state():
    return ProjectState(
        project_id=uuid4(),
        name="Test API",
        description="A test API project",
        phase=Phase.TASK_DECOMPOSITION,
        requirements={
            "product_name": "Test API",
            "functional_requirements": ["CRUD operations"],
            "non_functional_requirements": ["Performance"],
        },
        architecture={
            "technology_stack": {"backend": "FastAPI", "database": "PostgreSQL"},
            "api_design": {"endpoints": ["/api/v1/items"]},
        },
        tasks=[
            TaskItem(
                id="task-1", title="Build API", description="Build the API",
                agent="backend_engineer", priority="high", status="pending",
            ),
        ],
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )


@pytest.mark.asyncio
async def test_backend_engineer_plan(project_state):
    llm = LLMProvider()
    agent = BackendEngineerAgent(llm)
    plan = await agent.generate_backend(project_state, "Build CRUD API endpoints")
    assert len(plan.files_to_create) > 0
    f = plan.files_to_create[0]
    assert f.path
    assert f.content
    assert f.description
    assert isinstance(plan.packages, list)
    assert plan.summary


@pytest.mark.asyncio
async def test_frontend_engineer_plan(project_state):
    llm = LLMProvider()
    agent = FrontendEngineerAgent(llm)
    plan = await agent.generate_frontend(project_state, "Build React UI")
    assert len(plan.components) > 0
    assert isinstance(plan.pages, list)
    assert isinstance(plan.hooks, list)
    c = plan.components[0]
    assert c.path
    assert c.content
    assert c.description
    assert plan.summary


@pytest.mark.asyncio
async def test_testing_engineer_plan(project_state):
    llm = LLMProvider()
    agent = TestingEngineerAgent(llm)
    plan = await agent.generate_tests(project_state, "Write tests", ["src/main.py"])
    assert len(plan.test_files) > 0
    tf = plan.test_files[0]
    assert tf.path
    assert tf.content
    assert tf.description
    assert plan.summary


def test_file_system_tool(tmp_path):
    fs = FileSystemTool(str(tmp_path))

    result = fs.write_file("test.txt", "hello world")
    assert "Written" in result

    content = fs.read_file("test.txt")
    assert content == "hello world"

    result = fs.append_file("test.txt", "\nline 2")
    assert "Appended" in result
    assert fs.read_file("test.txt") == "hello world\nline 2"

    entries = fs.list_dir(".")
    assert "test.txt" in entries

    assert fs.file_exists("test.txt")
    assert not fs.file_exists("nonexistent.txt")


def test_file_system_sandbox(tmp_path):
    fs = FileSystemTool(str(tmp_path))
    with pytest.raises(PermissionError):
        fs.read_file("../outside.txt")


def test_file_system_write_nested(tmp_path):
    fs = FileSystemTool(str(tmp_path))
    fs.write_file("sub/dir/file.txt", "nested")
    assert fs.file_exists("sub/dir/file.txt")
    assert fs.read_file("sub/dir/file.txt") == "nested"


def test_file_system_delete(tmp_path):
    fs = FileSystemTool(str(tmp_path))
    fs.write_file("to_delete.txt", "delete me")
    assert fs.file_exists("to_delete.txt")
    fs.delete_file("to_delete.txt")
    assert not fs.file_exists("to_delete.txt")


def test_file_system_list_by_extension(tmp_path):
    fs = FileSystemTool(str(tmp_path))
    fs.write_file("a.py", "py")
    fs.write_file("b.tsx", "tsx")
    fs.write_file("sub/c.py", "py2")
    py_files = fs.list_files_by_extension(".py")
    assert len(py_files) == 2
    assert "a.py" in py_files
    assert "sub/c.py" in py_files
