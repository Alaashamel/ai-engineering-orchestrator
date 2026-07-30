# Changelog

All notable changes to the AI Engineering Orchestrator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-15

### Added
- Monorepo scaffold with FastAPI + React + Docker + CI
- LangGraph orchestration engine with 6 AI agents (CEO, PM, Architect, Backend, Frontend, QA)
- FastAPI backend with SQLAlchemy 2.0, Alembic migrations, and Pydantic v2 schemas
- React 19 frontend with TypeScript, React Router, and Tailwind CSS
- PostgreSQL with pgvector and Redis infrastructure via Docker Compose
- LLM provider abstraction with mock mode for development
- Task decomposition and project state management via LangGraph
- File system tools for sandboxed code generation
- WebSocket streaming for real-time workflow updates
- Health check and project CRUD API endpoints
- Comprehensive test suite (pytest for backend)
- GitHub Actions CI pipeline
- Development Makefile with common commands
- Ruff configuration for Python linting
- Markdown and YAML linting configurations

### Changed
- N/A (initial release)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A
