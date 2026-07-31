# Changelog

All notable changes to the AI Engineering Orchestrator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-30

### Added
- Milestone 1: Monorepo scaffold with FastAPI, React, Docker Compose, CI
- Milestone 2: Multi-agent orchestration with LangGraph (6 agents: CEO, PM, Architect, Backend, Frontend, QA)
- Milestone 3: Sandboxed file system tool and real LLM integration (OpenAI)
- Milestone 4: Human-in-the-loop approvals, audit logging, OpenTelemetry, webhooks
  - AuditLog model and migration (PostgreSQL)
  - Approve/reject/rollback REST endpoints
  - OpenTelemetry tracing instrumentation
  - Webhook notification service
  - Approval dashboard UI with approve/reject buttons
- Milestone 5: LLM integration layer (50+ modules)
  - Provider, factory, registry, retry handler, streaming
  - Cost tracking, metrics, benchmarking, eval harness
  - Pipeline management, scheduler, transformer pipeline
  - Plugin system, middleware chain, event system
  - 50+ managers (adapter, analyzer, auditor, cache, debugger, enforcer, filter, formatter, etc.)
  - Full test coverage (170+ tests)

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
