"""Deterministic mock content builder for the orchestration agent models.

When no (or an unusable) API key is present, ``LLMProvider`` falls back to
this module instead of the generic schema-filler. The goal is that mock mode
produces the same *shape* a real LLM would: a coherent project spec, a task
list assigned to agents the graph can actually implement, and runnable backend
+ frontend + test files for a small CRUD service.

The generated project is deliberately a simple, self-contained FastAPI app
(SQLAlchemy + SQLite, JWT auth) with a pytest suite that passes against it.
Everything here is deterministic: same prompt -> same output.
"""

from __future__ import annotations

import re
from typing import Any

# Resource vocabulary used to infer a CRUD resource from the prompt.
_RESOURCE_LIBRARY = {
    "todo": ("Todo", "todos"),
    "todos": ("Todo", "todos"),
    "blog": ("Post", "posts"),
    "post": ("Post", "posts"),
    "posts": ("Post", "posts"),
    "product": ("Product", "products"),
    "products": ("Product", "products"),
    "note": ("Note", "notes"),
    "notes": ("Note", "notes"),
    "task": ("Task", "tasks"),
    "tasks": ("Task", "tasks"),
    "item": ("Item", "items"),
    "items": ("Item", "items"),
    "user": ("User", "users"),
    "users": ("User", "users"),
}

_AUTH_KEYWORDS = ("jwt", "auth", "login", "token", "register", "signup", "password", "user")
_FRONTEND_KEYWORDS = ("frontend", "react", "ui", "web", "dashboard", "spa", "vite")
_AUTH_NEGATIONS = ("no auth", "without auth", "no authentication", "without authentication",
                   "no login", "no jwt", "no signup", "no registration", "no password",
                   "no token", "no users", "no user", "single-user", "single user", "public")
_FRONTEND_NEGATIONS = ("no ui", "no frontend", "no react", "no web", "no dashboard",
                       "no spa", "no vite", "backend only")


def _word(kw: str, text: str) -> bool:
    """True when ``kw`` appears as a word or word-prefix in ``text``.

    Uses \\b so ``ui`` does not match inside "build", and ``post`` does not
    match inside "postgresql" or a bare HTTP-method list.
    """
    return re.search(r"\b" + re.escape(kw) + r"\w*", text) is not None


def _spec(prompt: str) -> dict[str, Any]:
    """Derive the CRUD spec from the *project description* embedded in an
    agent prompt, ignoring prior-agent scaffold text.

    Every agent prompt embeds ``Description: <original prompt>``; scanning the
    whole prompt is unstable because serialized earlier-agent outputs contain
    words like "post" (HTTP method) and "PostgreSQL" that collide with the
    resource vocabulary. Restricting the scan to the description line keeps all
    downstream agents on the same spec as the original request.
    """
    low = prompt.lower()
    m = re.search(r"^description:[ \t]*(.+)$", low, flags=re.MULTILINE)
    text = m.group(1).strip() if m else low

    model_cls: str = "Item"
    table: str = "items"
    for key, (cls_, tbl) in _RESOURCE_LIBRARY.items():
        if _word(key, text):
            model_cls, table = cls_, tbl
            break
    has_auth = any(_word(k, text) for k in _AUTH_KEYWORDS) and not any(
        n in text for n in _AUTH_NEGATIONS)
    has_frontend = any(_word(k, text) for k in _FRONTEND_KEYWORDS) and not any(
        n in text for n in _FRONTEND_NEGATIONS)
    return {
        "model_cls": model_cls,
        "table": table,
        "has_auth": has_auth,
        "has_frontend": has_frontend,
        "project_type": "REST API" if ("api" in text or "backend" in text or "rest" in text)
        else "Full-stack application" if ("frontend" in text or "web" in text) else "Application",
    }


def _discovery(spec_: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_type": spec_["project_type"],
        "complexity": "medium",
        "key_objectives": [
            "Provide CRUD operations on %s" % spec_["table"],
            "Secure access with authentication" if spec_["has_auth"] else "Keep the API simple and documented",
            "Ship with tests covering success and error paths",
        ],
        "risks": ["Scope creep beyond MVP", "Auth correctness" if spec_["has_auth"] else "Minimal risk — well-scoped CRUD service"],
        "recommended_approach": "Implement a FastAPI service with SQLAlchemy, expose a REST CRUD router, "
        "and verify with an automated pytest suite.",
        "reasoning": "The request describes a well-bounded API with clear entities; a single service with "
        "a CRUD router and a test suite is the lowest-risk path to a working deliverable.",
    }


def _requirements(spec_: dict[str, Any]) -> dict[str, Any]:
    name = spec_["table"].title()
    return {
        "product_name": "%s Service" % name,
        "vision": "A small, reliable API for managing %s." % spec_["table"],
        "target_users": ["API consumers", "Frontend clients"],
        "functional_requirements": [
            {"id": "FR-1", "title": "List %s" % spec_["table"], "description": "Return all %s with pagination." % spec_["table"], "priority": "high"},
            {"id": "FR-2", "title": "Create %s" % spec_["table"], "description": "Create a new %s from a JSON body." % spec_["table"].rstrip("s"), "priority": "high"},
            {"id": "FR-3", "title": "Update %s" % spec_["table"], "description": "Partially update a %s by id." % spec_["table"].rstrip("s"), "priority": "medium"},
            {"id": "FR-4", "title": "Delete %s" % spec_["table"], "description": "Delete a %s by id." % spec_["table"].rstrip("s"), "priority": "medium"},
            {"id": "FR-5", "title": "Authentication", "description": "Register and log in with JWT tokens." if spec_["has_auth"] else "No authentication required for MVP.", "priority": "critical" if spec_["has_auth"] else "low"},
        ],
        "non_functional_requirements": ["10ms p95 for local reads", "Schema-validated request/response payloads"],
        "user_stories": [
            {"id": "US-1", "as_a": "client", "i_want": "to create and list %s" % spec_["table"], "so_that": "I can manage data through a clean API", "acceptance_criteria": ["POST returns 201", "GET returns a list"]},
            {"id": "US-2", "as_a": "client", "i_want": "to authenticate" if spec_["has_auth"] else "to use the API without setup", "so_that": "only authorized callers can write data" if spec_["has_auth"] else "I can start immediately", "acceptance_criteria": ["login returns a token"] if spec_["has_auth"] else ["no auth headers required"]},
        ],
        "mvp_features": ["CRUD on %s" % spec_["table"], "JWT auth" if spec_["has_auth"] else "Open endpoints"],
        "future_features": ["Search", "Soft delete"],
        "open_questions": ["Rate limits", "Multi-tenancy"],
    }


def _architecture(spec_: dict[str, Any]) -> dict[str, Any]:
    table = spec_["table"]
    model = spec_["model_cls"]
    return {
        "architecture_overview": "Single FastAPI service exposing a REST router backed by SQLAlchemy and SQLite.",
        "technology_stack": [
            {"layer": "API", "technology": "FastAPI", "justification": "Schema-validated endpoints with minimal boilerplate."},
            {"layer": "Data", "technology": "SQLAlchemy + SQLite", "justification": "No external service needed for the MVP."},
            {"layer": "Auth", "technology": "PyJWT (HS256)", "justification": "Stateless bearer tokens."} if spec_["has_auth"] else {"layer": "Data", "technology": "SQLite", "justification": "Zero-setup persistence."},
        ],
        "system_components": ["app.main: FastAPI application", "app.models: SQLAlchemy models",
                              "app.routers.%s: CRUD endpoints" % table, "app.auth: token helpers" if spec_["has_auth"] else "app.config: settings"],
        "api_design": [
            entry for entry in [
                {"endpoint": "/health", "method": "GET", "description": "Liveness check", "request_body": None, "response": "{\"status\": \"ok\"}"},
                {"endpoint": "/auth/register", "method": "POST", "description": "Create a user account", "request_body": "{\"username\": \"x\", \"password\": \"y\"}", "response": "{\"id\": 1, \"username\": \"x\"}"} if spec_["has_auth"] else None,
                {"endpoint": "/auth/login", "method": "POST", "description": "Exchange credentials for a bearer token", "request_body": "{\"username\": \"x\", \"password\": \"y\"}", "response": "{\"access_token\": \"...\"}"} if spec_["has_auth"] else None,
                {"endpoint": "/%s" % table, "method": "GET", "description": "List %s" % table, "request_body": None, "response": "[{\"id\": 1}]"},
                {"endpoint": "/%s" % table, "method": "POST", "description": "Create a %s" % model, "request_body": "{\"title\": \"x\"}", "response": "{\"id\": 1, \"title\": \"x\"}"},
                {"endpoint": "/%s/{id}" % table, "method": "PATCH", "description": "Update by id", "request_body": "{\"title\": \"x\"}", "response": "{\"id\": 1, \"title\": \"x\"}"},
                {"endpoint": "/%s/{id}" % table, "method": "DELETE", "description": "Delete by id", "request_body": None, "response": "204"},
            ] if entry is not None
        ],
        "database_tables": [
            {"name": "users", "columns": [{"name": "id", "type": "int PK"}, {"name": "username", "type": "string unique"}, {"name": "password_hash", "type": "string"}], "indexes": ["username"], "relationships": []},
            {"name": table, "columns": [{"name": "id", "type": "int PK"}, {"name": "title", "type": "string"}, {"name": "description", "type": "text"}, {"name": "completed", "type": "bool"}, {"name": "owner_id", "type": "int FK"}], "indexes": [], "relationships": ["owner -> users"]},
        ],
        "architecture_decisions": [
            {"title": "SQLite for MVP", "decision": "Use SQLite locally", "rationale": "No infrastructure needed; swap later.", "alternatives": ["PostgreSQL", "MySQL"]},
            {"title": "Sync DB access", "decision": "Use sync SQLAlchemy endpoints", "rationale": "Simple and reliable for a small CRUD service.", "alternatives": ["AsyncSQLAlchemy + asyncpg"]},
        ],
        "identified_risks": ["SQLite does not scale to concurrent writes"],
    }


def _task_decomposition(spec_: dict[str, Any]) -> dict[str, Any]:
    model = spec_["model_cls"]
    table = spec_["table"]
    tasks = [
        {"id": "t1", "title": "Build data models", "description": "SQLAlchemy models for %s and users." % table,
         "agent": "backend_engineer", "priority": "critical", "dependencies": [], "acceptance_criteria": ["models exist", "tables create on startup"]},
        {"id": "t2", "title": "Implement REST CRUD router", "description": "FastAPI router with list/create/update/delete for %s." % table,
         "agent": "backend_engineer", "priority": "critical", "dependencies": ["t1"], "acceptance_criteria": ["endpoints respond", "payloads validated"]},
        {"id": "t3", "title": "Add JWT authentication", "description": "Register/login endpoints returning HS256 bearer tokens; protect write routes." if spec_["has_auth"] else "Keep endpoints open for MVP.",
         "agent": "backend_engineer", "priority": "critical" if spec_["has_auth"] else "low", "dependencies": ["t1"], "acceptance_criteria": ["login returns a token"] if spec_["has_auth"] else ["no auth required"]},
        {"id": "t4", "title": "Wire FastAPI application", "description": "main.py app with routers, startup table creation, /health.",
         "agent": "backend_engineer", "priority": "high", "dependencies": ["t2", "t3"], "acceptance_criteria": ["app imports", "health returns 200"]},
        {"id": "t5", "title": "Write pytest suite", "description": "tests for auth and CRUD on %s (conftest with in-memory SQLite)." % model,
         "agent": "qa_engineer", "priority": "high", "dependencies": ["t4"], "acceptance_criteria": ["pytest passes", "auth disabled paths covered" if not spec_["has_auth"] else "401 when token missing"]},
    ]
    if spec_["has_frontend"]:
        tasks.append({"id": "t6", "title": "Build React UI", "description": "Minimal React app listing and creating %s via fetch." % table,
                      "agent": "frontend_engineer", "priority": "medium", "dependencies": ["t4"], "acceptance_criteria": ["vite dev server runs"]})
    return {"tasks": tasks}


def _generated_file(path: str, content: str, description: str) -> dict[str, str]:
    return {"path": path, "content": content, "description": description}


def _backend(spec_: dict[str, Any]) -> dict[str, Any]:
    model = spec_["model_cls"]
    table = spec_["table"]
    needs_auth = spec_["has_auth"]

    schemas = (
        "from pydantic import BaseModel, Field, ConfigDict\n"
        "from datetime import datetime\n\n"
        "\n"
        "class %(Model)sBase(BaseModel):\n"
        "    title: str\n"
        "    description: str | None = None\n"
        "\n"
        "class %(Model)sCreate(%(Model)sBase):\n"
        "    pass\n\n"
        "class %(Model)sRead(%(Model)sBase):\n"
        "    model_config = ConfigDict(from_attributes=True)\n"
        "    id: int\n"
        "    completed: bool = False\n"
        "    created_at: datetime\n\n"
        "class %(Model)sUpdate(BaseModel):\n"
        "    title: str | None = None\n"
        "    description: str | None = None\n"
        "    completed: bool | None = None\n"
    ) % {"Model": f"{model}"}
    if needs_auth:
        schemas += (
            "\n"
            "class UserBase(BaseModel):\n"
            "    username: str\n\n"
            "class UserCreate(UserBase):\n"
            "    password: str\n\n"
            "class UserRead(UserBase):\n"
            "    model_config = ConfigDict(from_attributes=True)\n"
            "    id: int\n\n"
            "class UserLogin(BaseModel):\n"
            "    username: str\n"
            "    password: str\n\n"
            "class Token(BaseModel):\n"
            "    access_token: str\n"
            "    token_type: str = 'bearer'\n"
        )

    models = (
        "from datetime import datetime\n"
        "from sqlalchemy import String, Text, DateTime, Boolean, Integer, func, ForeignKey\n"
        "from sqlalchemy.orm import Mapped, mapped_column, relationship\n"
        "from database import Base\n\n"
        "class %(Model)s(Base):\n"
        "    __tablename__ = %(table)r\n"
        "    id: Mapped[int] = mapped_column(primary_key=True)\n"
        "    title: Mapped[str] = mapped_column(String(255))\n"
        "    description: Mapped[str | None] = mapped_column(Text, nullable=True)\n"
        "    completed: Mapped[bool] = mapped_column(Boolean, default=False)\n"
        "    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())\n"
    ) % {"Model": f"{model}", "table": table}
    if needs_auth:
        models += (
            "    owner_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)\n"
            "    owner: Mapped['User | None'] = relationship()\n\n"
            "class User(Base):\n"
            "    __tablename__ = 'users'\n"
            "    id: Mapped[int] = mapped_column(primary_key=True)\n"
            "    username: Mapped[str] = mapped_column(String, unique=True)\n"
            "    password_hash: Mapped[str] = mapped_column(String(255))\n"
        )

    if needs_auth:
        resource_router = (
            "from fastapi import APIRouter, Depends, HTTPException, status\n"
            "from sqlalchemy.orm import Session\n"
            "from database import get_db\n"
            "from models import %(Model)s\n"
            "from schemas import %(Model)sCreate, %(Model)sRead, %(Model)sUpdate\n"
            "from auth import get_current_user\n\n"
            "router = APIRouter(prefix='/' + %(table)r, tags=[%(table)r])\n\n"
            "@router.post('', response_model=%(Model)sRead, status_code=status.HTTP_201_CREATED)\n"
            "def create_item(payload: %(Model)sCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):\n"
            "    row = %(Model)s(title=payload.title, description=payload.description, owner_id=user.id)\n"
            "    db.add(row); db.commit(); db.refresh(row)\n"
            "    return row\n\n"
            "@router.get('', response_model=list[%(Model)sRead])\n"
            "def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user=Depends(get_current_user)):\n"
            "    return db.query(%(Model)s).filter(%(Model)s.owner_id == user.id).offset(skip).limit(limit).all()\n\n"
            "@router.get('/{item_id}', response_model=%(Model)sRead)\n"
            "def get_item(item_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):\n"
            "    row = db.get(%(Model)s, item_id)\n"
            "    if not row or row.owner_id != user.id:\n"
            "        raise HTTPException(status_code=404, detail='not found')\n"
            "    return row\n\n"
            "@router.patch('/{item_id}', response_model=%(Model)sRead)\n"
            "def update_item(item_id: int, payload: %(Model)sUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):\n"
            "    row = db.get(%(Model)s, item_id)\n"
            "    if not row or row.owner_id != user.id:\n"
            "        raise HTTPException(status_code=404, detail='not found')\n"
            "    for k, v in payload.model_dump(exclude_unset=True).items():\n"
            "        setattr(row, k, v)\n"
            "    db.commit(); db.refresh(row)\n"
            "    return row\n\n"
            "@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)\n"
            "def delete_item(item_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):\n"
            "    row = db.get(%(Model)s, item_id)\n"
            "    if not row or row.owner_id != user.id:\n"
            "        raise HTTPException(status_code=404, detail='not found')\n"
            "    db.delete(row); db.commit()\n"
            "    return None\n"
        ) % {"Model": f"{model}", "table": table}
    else:
        resource_router = (
            "from fastapi import APIRouter, Depends, HTTPException, status\n"
            "from sqlalchemy.orm import Session\n"
            "from database import get_db\n"
            "from models import %(Model)s\n"
            "from schemas import %(Model)sCreate, %(Model)sRead, %(Model)sUpdate\n\n"
            "router = APIRouter(prefix='/' + %(table)r, tags=[%(table)r])\n\n"
            "@router.post('', response_model=%(Model)sRead, status_code=status.HTTP_201_CREATED)\n"
            "def create_item(payload: %(Model)sCreate, db: Session = Depends(get_db)):\n"
            "    row = %(Model)s(title=payload.title, description=payload.description)\n"
            "    db.add(row); db.commit(); db.refresh(row)\n"
            "    return row\n\n"
            "@router.get('', response_model=list[%(Model)sRead])\n"
            "def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):\n"
            "    return db.query(%(Model)s).offset(skip).limit(limit).all()\n\n"
            "@router.get('/{item_id}', response_model=%(Model)sRead)\n"
            "def get_item(item_id: int, db: Session = Depends(get_db)):\n"
            "    row = db.get(%(Model)s, item_id)\n"
            "    if not row:\n"
            "        raise HTTPException(status_code=404, detail='not found')\n"
            "    return row\n\n"
            "@router.patch('/{item_id}', response_model=%(Model)sRead)\n"
            "def update_item(item_id: int, payload: %(Model)sUpdate, db: Session = Depends(get_db)):\n"
            "    row = db.get(%(Model)s, item_id)\n"
            "    if not row:\n"
            "        raise HTTPException(status_code=404, detail='not found')\n"
            "    for k, v in payload.model_dump(exclude_unset=True).items():\n"
            "        setattr(row, k, v)\n"
            "    db.commit(); db.refresh(row)\n"
            "    return row\n\n"
            "@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)\n"
            "def delete_item(item_id: int, db: Session = Depends(get_db)):\n"
            "    row = db.get(%(Model)s, item_id)\n"
            "    if not row:\n"
            "        raise HTTPException(status_code=404, detail='not found')\n"
            "    db.delete(row); db.commit()\n"
            "    return None\n"
        ) % {"Model": f"{model}", "table": table}

    if needs_auth:
        auth_router = (
            "from fastapi import APIRouter, Depends, HTTPException\n"
            "from sqlalchemy.orm import Session\n"
            "from database import get_db\n"
            "from models import User\n"
            "from schemas import UserCreate, UserRead, UserLogin, Token\n"
            "from auth import hash_password, verify_password, create_access_token\n\n"
            "router = APIRouter(prefix='/auth', tags=['auth'])\n\n"
            "@router.post('/register', response_model=UserRead, status_code=201)\n"
            "def register(payload: UserCreate, db: Session = Depends(get_db)):\n"
            "    if db.query(User).filter(User.username == payload.username).first():\n"
            "        raise HTTPException(status_code=409, detail='username taken')\n"
            "    user = User(username=payload.username, password_hash=hash_password(payload.password))\n"
            "    db.add(user); db.commit(); db.refresh(user)\n"
            "    return user\n\n"
            "@router.post('/login', response_model=Token)\n"
            "def login(payload: UserLogin, db: Session = Depends(get_db)):\n"
            "    user = db.query(User).filter(User.username == payload.username).first()\n"
            "    if not user or not verify_password(payload.password, user.password_hash):\n"
            "        raise HTTPException(status_code=401, detail='bad credentials')\n"
            "    return Token(access_token=create_access_token(user.id), token_type='bearer')\n"
        )
        auth_module = (
            "import hashlib, hmac, os, secrets, time\n"
            "import jwt\n"
            "from fastapi import Depends, HTTPException, Header\n"
            "from sqlalchemy.orm import Session\n"
            "from database import get_db\n"
            "from models import User\n\n"
            "SECRET_KEY = os.getenv('JWT_SECRET', 'dev-secret-change-me')\n"
            "ALGORITHM = 'HS256'\n\n"
            "def hash_password(password: str) -> str:\n"
            "    salt = secrets.token_hex(8)\n"
            "    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100_000).hex()\n"
            "    return f'{salt}${digest}'\n\n"
            "def verify_password(password: str, stored: str) -> bool:\n"
            "    salt, digest = stored.split('$')\n"
            "    test = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100_000).hex()\n"
            "    return hmac.compare_digest(test, digest)\n\n"
            "def create_access_token(user_id: int) -> str:\n"
            "    payload = {'sub': str(user_id), 'exp': int(time.time()) + 3600, 'iat': int(time.time())}\n"
            "    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)\n\n"
            "def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):\n"
            "    if not authorization or not authorization.lower().startswith('bearer '):\n"
            "        raise HTTPException(status_code=401, detail='missing token')\n"
            "    token = authorization.split(' ', 1)[1]\n"
            "    try:\n"
            "        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])\n"
            "    except Exception:\n"
            "        raise HTTPException(status_code=401, detail='invalid token')\n"
            "    user = db.get(User, int(data['sub']))\n"
            "    if not user:\n"
            "        raise HTTPException(status_code=401, detail='invalid token')\n"
            "    return user\n"
        )

    main_py = (
        "from fastapi import FastAPI\n"
        "from database import Base, engine\n"
        "import routers.resources\n"
    )
    if needs_auth:
        main_py += "import routers.auth\n"
    main_py += (
        "\n"
        "app = FastAPI(title='%(Name)s Service')\n"
        "Base.metadata.create_all(bind=engine)\n"
        "app.include_router(routers.resources.router)\n"
    )
    if needs_auth:
        main_py += "app.include_router(routers.auth.router)\n"
    main_py += (
        "\n"
        "@app.get('/health')\n"
        "def health():\n"
        "    return {'status': 'ok'}\n"
    ) % {"Name": f"{model} Crud"}

    files = [
        _generated_file("requirements.txt",
                        "fastapi\nuvicorn\nsqlalchemy\npyjwt\npytest\nhttpx\n", "Runtime and test dependencies"),
        _generated_file("README.md",
                        "# %(Name)s Service\n\nA small FastAPI CRUD service generated by the AI Engineering Orchestrator "
                        "(mock mode).\n\n```bash\npip install -r requirements.txt\nuvicorn main:app --reload\n```\n" % {"Name": f"{model} Crud"}, "Project readme"),
        _generated_file("database.py",
                        "from sqlalchemy import create_engine\n"
                        "from sqlalchemy.orm import DeclarativeBase, sessionmaker\n\n"
                        "engine = create_engine('sqlite:///./app.db', connect_args={'check_same_thread': False})\n"
                        "SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)\n\n"
                        "class Base(DeclarativeBase):\n    pass\n\n"
                        "def get_db():\n"
                        "    db = SessionLocal()\n"
                        "    try:\n"
                        "        yield db\n"
                        "    finally:\n"
                        "        db.close()\n", "SQLAlchemy engine, session and declarative base"),
        _generated_file("models.py", models, "SQLAlchemy models"),
        _generated_file("schemas.py", schemas, "Pydantic request/response schemas"),
        _generated_file("auth.py", auth_module, "Password hashing and JWT helpers") if needs_auth else None,
        _generated_file("routers/__init__.py", "", "Router package marker"),
        _generated_file("routers/resources.py", resource_router, "CRUD router for %s" % table),
        _generated_file("routers/auth.py", auth_router, "Register/login endpoints") if needs_auth else None,
        _generated_file("main.py", main_py, "FastAPI application entrypoint"),
    ]
    files = [f for f in files if f is not None]
    return {
        "files_to_create": files,
        "packages": ["fastapi", "uvicorn", "sqlalchemy", "pyjwt", "pytest", "httpx"],
        "summary": "Generated a FastAPI %s CRUD service with SQLAlchemy models, a REST router%s and a health check."
                   % (model, " and JWT auth" if needs_auth else ""),
    }


def _frontend(spec_: dict[str, Any]) -> dict[str, Any]:
    table = spec_["table"]
    component = _generated_file(
        "frontend/src/api.ts",
        "export interface Item { id: number; title: string }\n\n"
        "export async function listItems(): Promise<Item[]> {\n"
        "  const res = await fetch('/api/%s');\n"
        "  return res.json();\n"
        "}\n" % table,
        "Typed API client for %s" % table,
    )
    return {
        "components": [component],
        "pages": [_generated_file("frontend/src/App.tsx",
                                   "import { useEffect, useState } from 'react';\n"
                                   "import { Item, listItems } from './api';\n\n"
                                   "export default function App() {\n"
                                   "  const [items, setItems] = useState<Item[]>([]);\n"
                                   "  useEffect(() => { listItems().then(setItems); }, []);\n"
                                   "  return <ul>{items.map(i => <li key={i.id}>{i.title}</li>)}</ul>;\n"
                                   "}", "List page for %s" % table)],
        "hooks": [],
        "packages": ["react", "react-dom", "vite", "typescript"],
        "summary": "Generated a minimal React scaffold listing %s." % table,
    }


def _tests(spec_: dict[str, Any]) -> dict[str, Any]:
    model = spec_["model_cls"]
    table = spec_["table"]
    needs_auth = spec_["has_auth"]

    conftest = (
        "import pytest\n"
        "from fastapi.testclient import TestClient\n"
        "from sqlalchemy import create_engine\n"
        "from sqlalchemy.orm import sessionmaker\n"
        "from sqlalchemy.pool import StaticPool\n"
        "from database import Base, get_db\n"
        "import main as app_module\n\n"
        "engine = create_engine(\n"
        "    'sqlite://',\n"
        "    connect_args={'check_same_thread': False},\n"
        "    poolclass=StaticPool,\n"
        ")\n"
        "TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)\n\n"
        "def override_get_db():\n"
        "    db = TestingSessionLocal()\n"
        "    try:\n"
        "        yield db\n"
        "    finally:\n"
        "        db.close()\n\n"
        "@pytest.fixture()\n"
        "def client():\n"
        "    Base.metadata.create_all(bind=engine)\n"
        "    app_module.app.dependency_overrides[get_db] = override_get_db\n"
        "    with TestClient(app_module.app) as c:\n"
        "        yield c\n"
        "    app_module.app.dependency_overrides.clear()\n"
        "    Base.metadata.drop_all(bind=engine)\n"
    )

    if needs_auth:
        tests = (
            "from fastapi.testclient import TestClient\n\n"
            "def _register(client):\n"
            "    client.post('/auth/register', json={'username': 'alice', 'password': 'secret123'})\n\n"
            "def _token(client) -> str:\n"
            "    r = client.post('/auth/login', json={'username': 'alice', 'password': 'secret123'})\n"
            "    assert r.status_code == 200, r.text\n"
            "    return r.json()['access_token']\n\n"
            "def _headers(token):\n"
            "    return {'Authorization': 'Bearer ' + token}\n\n"
            "def test_health(client):\n"
            "    r = client.get('/health')\n"
            "    assert r.status_code == 200\n"
            "    assert r.json() == {'status': 'ok'}\n\n"
            "def test_register_and_login(client):\n"
            "    _register(client)\n"
            "    token = _token(client)\n"
            "    assert token\n\n"
            "def test_login_rejects_bad_password(client):\n"
            "    _register(client)\n"
            "    r = client.post('/auth/login', json={'username': 'alice', 'password': 'wrong'})\n"
            "    assert r.status_code == 401\n\n"
            "def test_crud_requires_token(client):\n"
            "    r = client.get('/%(table)s')\n"
            "    assert r.status_code == 401\n\n"
            "def test_crud_roundtrip(client):\n"
            "    _register(client)\n"
            "    headers = _headers(_token(client))\n"
            "    created = client.post('/%(table)s', json={'title': 'buy milk'}, headers=headers)\n"
            "    assert created.status_code == 201\n"
            "    item_id = created.json()['id']\n"
            "    listed = client.get('/%(table)s', headers=headers)\n"
            "    assert listed.status_code == 200\n"
            "    assert any(i['id'] == item_id for i in listed.json())\n"
            "    updated = client.patch(f'/%(table)s/{item_id}', json={'completed': True}, headers=headers)\n"
            "    assert updated.status_code == 200\n"
            "    assert updated.json()['completed'] is True\n"
            "    deleted = client.delete(f'/%(table)s/{item_id}', headers=headers)\n"
            "    assert deleted.status_code == 204\n\n"
            "def test_crud_404_for_missing(client):\n"
            "    _register(client)\n"
            "    headers = _headers(_token(client))\n"
            "    assert client.get('/%(table)s/9999', headers=headers).status_code == 404\n"
        ) % {"table": table}
    else:
        tests = (
            "def test_health(client):\n"
            "    r = client.get('/health')\n"
            "    assert r.status_code == 200\n"
            "    assert r.json() == {'status': 'ok'}\n\n"
            "def test_crud_roundtrip(client):\n"
            "    created = client.post('/%(table)s', json={'title': 'buy milk'})\n"
            "    assert created.status_code == 201\n"
            "    item_id = created.json()['id']\n"
            "    assert client.get('/%(table)s').status_code == 200\n"
            "    listed = client.get('/%(table)s').json()\n"
            "    assert any(i['id'] == item_id for i in listed)\n"
            "    updated = client.patch('/%(table)s/' + str(item_id), json={'completed': True})\n"
            "    assert updated.status_code == 200\n"
            "    assert updated.json()['completed'] is True\n"
            "    assert client.delete('/%(table)s/' + str(item_id)).status_code == 204\n\n"
            "def test_crud_404_for_missing(client):\n"
            "    assert client.get('/%(table)s/9999').status_code == 404\n"
        ) % {"table": table}

    return {
        "test_files": [_generated_file("tests/test_%s.py" % table, tests,
                                       "Functional tests for the %s CRUD service" % model)],
        "fixtures": [_generated_file("tests/conftest.py", conftest, "In-memory SQLite test fixtures")],
        "packages": ["pytest", "httpx", "pytest-asyncio"],
        "summary": "Generated a pytest suite covering health, auth and %s CRUD against an in-memory database." % model,
    }


def build_mock(model_class, prompt: str = "") -> dict[str, Any]:
    """Return a deterministic dict matching ``model_class`` based on ``prompt``."""
    spec_ = _spec(prompt)
    name = model_class.__name__
    if name == "DiscoveryOutput":
        return _discovery(spec_)
    if name == "ProductRequirementsOutput":
        return _requirements(spec_)
    if name == "ArchitectureOutput":
        return _architecture(spec_)
    if name == "TaskDecompositionOutput":
        return _task_decomposition(spec_)
    if name == "BackendPlan":
        return _backend(spec_)
    if name == "FrontendPlan":
        return _frontend(spec_)
    if name == "TestPlan":
        return _tests(spec_)
    return None