# Implementation Plan: Backend API Loopback

**Branch**: `003-backend-api-loopback` | **Date**: 2025-12-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-backend-api-loopback/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a backend API server that replaces the client-side message loopback with server-side processing. The backend will accept message requests from the Vue.js frontend and return responses prefixed with "api says: ". This establishes the foundational client-server architecture before adding LLM integrations. Technical approach will use Python with a lightweight web framework, JSON REST API, and integration with the existing Vue.js frontend.

## Technical Context

**Language/Version**: Python 3.13 (confirmed in devcontainer)
**Primary Dependencies**: FastAPI 0.115.0, uvicorn (ASGI server), Pydantic (validation)
**Storage**: N/A (backend is stateless for loopback; frontend LocalStorage persists conversations)
**Testing**: pytest + FastAPI TestClient (contract/integration tests), openapi-core (schema validation)
**Target Platform**: Local development (uvicorn), Python 3.13 devcontainer
**Project Type**: Web (backend API server to complement existing frontend SPA)
**Performance Goals**: <2s response time for loopback (per FR-006), support 10+ concurrent requests
**Constraints**: <10s timeout for requests (per FR-009), messages limited to 10,000 characters (per FR-007)
**Scale/Scope**: Single user initially, 100+ messages in sequence without errors (per SC-002)

**Technology Decisions** (see research.md for detailed rationale):
- FastAPI chosen for API-first design, automatic OpenAPI docs, built-in CORS, async support
- Port 8000 for backend (standard Python API convention), Port 5173 for frontend (Vite)
- Python venv + requirements.txt for dependency management (simplicity over Poetry/Pipenv)
- openapi-core for contract testing, FastAPI TestClient for integration testing
- python-dotenv for environment configuration (.env files)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: API-First Design ✅ PASS

**Status**: COMPLIANT

- API contract MUST be defined before implementation (request/response schemas)
- Endpoint: POST /api/messages with message payload
- Response schema includes status, echoed message with "api says: " prefix, error handling
- Error codes and scenarios documented (connection errors, timeouts, validation failures)

**Action**: Define OpenAPI/JSON Schema contract in Phase 1 (contracts/)

### Principle II: Modular Architecture ✅ PASS

**Status**: COMPLIANT

- Backend API will be self-contained module separate from frontend
- Clear boundary: Frontend sends HTTP requests, backend returns JSON responses
- Backend can be independently tested via API contract tests
- Frontend integration via HTTP client abstraction (can mock for testing)

**Action**: Document backend module structure in Phase 1 design

### Principle III: Test-First Development (NON-NEGOTIABLE) ✅ PASS

**Status**: COMPLIANT

- API contract tests will be written first (TDD workflow)
- Unit tests for message processing logic
- Integration tests for full request-response cycle
- Tests must fail before implementation, then pass after implementation

**Action**: Write failing tests for P1 acceptance scenarios before coding

### Principle IV: Integration & Contract Testing ✅ PASS

**Status**: COMPLIANT

- Contract tests verify API request/response schemas match specification
- Integration tests verify frontend → backend → frontend flow works end-to-end
- Tests cover error scenarios (backend unavailable, timeouts, malformed requests)
- Frontend integration tests will use real backend (not mocks) for E2E validation

**Action**: Define contract test suite in Phase 1

### Principle V: Observability & Debuggability ✅ PASS

**Status**: COMPLIANT

- Backend will log all incoming requests and outgoing responses (per FR-014)
- Structured logging with request IDs for tracing
- Error responses include actionable context (validation errors, server errors)
- Log levels: DEBUG (request/response details), INFO (operations), ERROR (failures)

**Action**: Implement logging from day 1 of development

### Principle VI: Simplicity & YAGNI ✅ PASS

**Status**: COMPLIANT

- Start with simplest solution: single endpoint, stateless loopback, no database
- No authentication, sessions, or complex middleware for P1
- Use lightweight framework (avoid heavy ORMs, unnecessary abstractions)
- No WebSocket/streaming for simple loopback (HTTP request-response is sufficient)

**Action**: Research phase will select simplest viable framework

### Principle VII: Versioning & Breaking Changes ⚠️ ATTENTION

**Status**: COMPLIANT (with note)

- API version should be included in endpoint path (e.g., /api/v1/messages)
- Initial version: v1 (allows future breaking changes via v2)
- Response schema includes version field for client compatibility checks

**Note**: This is the first backend API - establish versioning pattern from the start.

**Action**: Include API versioning in contract design (Phase 1)

### Principle VIII: Incremental Delivery & Thin Slices (NON-NEGOTIABLE) ✅ PASS

**Status**: COMPLIANT

- P1 slice: Basic loopback endpoint (single user story, end-to-end deliverable)
- P2 slice: Error handling enhancements (separate deployable improvement)
- Each slice delivers working functionality: P1 works end-to-end before P2 starts
- Can commit and deploy P1 independently without P2

**Action**: Implement P1 fully (tests + backend + frontend integration) before P2

### Principle IX: Living Architecture Documentation ✅ PASS

**Status**: COMPLIANT

- This feature adds major architectural component (backend API server)
- Must update architecture.md with:
  - Current Architecture: Add backend API server to diagram and component list
  - Technology Stack: Add Python, framework choice, testing tools
  - Data Flow: Update to show frontend → backend → frontend flow
  - ADR: Document framework choice rationale (FastAPI vs Flask, etc.)

**Action**: Update architecture.md after implementation completes

**Note**: If this feature introduces architectural changes (new modules, data flows, integration points, or technology choices), plan to update `architecture.md` with:
- Current architecture changes in the "Current Architecture" section
- Any planned future work in the "Planned Architecture" section with "NOT IMPLEMENTED" labels
- Technology stack updates if new dependencies added
- Architectural decision records (ADRs) for major choices

---

### Post-Phase 1 Re-Evaluation (Design Complete)

**Date**: 2025-12-28
**Status**: All principles remain COMPLIANT after research and design phases

**Completed Actions**:
- ✅ OpenAPI contract defined: `contracts/message-api.yaml`
- ✅ Data model documented: `data-model.md` with Pydantic schemas
- ✅ Testing strategy documented: research.md (openapi-core + pytest + TestClient)
- ✅ Backend module structure designed: See Project Structure section
- ✅ API versioning included: `/api/v1/messages` endpoint
- ✅ Technology decisions finalized: FastAPI, Python 3.13, uvicorn
- ✅ Agent context updated: CLAUDE.md

**Verification**:
- **Principle I (API-First)**: ✅ OpenAPI 3.1 contract complete with examples, validation rules, error codes
- **Principle II (Modular)**: ✅ Clear separation: backend/src, backend/tests, frontend/src/services
- **Principle III (TDD)**: ✅ TDD workflow documented in research.md with red-green-refactor examples
- **Principle IV (Contract Testing)**: ✅ openapi-core for schema validation, TestClient for integration
- **Principle V (Observability)**: ✅ Logging requirements in FR-014, error responses with actionable context
- **Principle VI (Simplicity)**: ✅ FastAPI chosen (lightweight), no database, stateless loopback only
- **Principle VII (Versioning)**: ✅ API versioned as `/api/v1/messages`, schema version 1.0.0
- **Principle VIII (Thin Slices)**: ✅ P1 = loopback only, P2 = error handling (separate slice)
- **Principle IX (Architecture Docs)**: ✅ architecture.md update planned post-implementation

**Conclusion**: All constitution principles satisfied. Ready for Phase 2 (task generation via `/speckit.tasks`).

## Project Structure

### Documentation (this feature)

```text
specs/003-backend-api-loopback/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── message-api.yaml # OpenAPI specification for message endpoint
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/                 # NEW: Backend API server (to be created)
├── src/
│   ├── api/            # API endpoint handlers
│   │   └── routes/     # Route definitions
│   ├── services/       # Business logic (message processing)
│   ├── middleware/     # Request/response middleware (logging, CORS, validation)
│   └── utils/          # Shared utilities (logging, validation helpers)
├── tests/
│   ├── contract/       # API contract tests (OpenAPI schema validation)
│   ├── integration/    # Full request-response cycle tests
│   └── unit/           # Service and utility unit tests
├── requirements.txt    # Python dependencies
└── main.py            # Application entry point

frontend/               # EXISTING: Vue.js SPA (to be modified)
├── src/
│   ├── components/     # Vue components (existing)
│   ├── state/          # State management composables (existing)
│   ├── storage/        # LocalStorage adapter (existing)
│   ├── services/       # NEW: API client for backend communication
│   │   └── apiClient.js  # HTTP client wrapper (fetch/axios)
│   └── utils/          # Shared utilities (existing)
└── tests/
    ├── unit/           # Component and service unit tests
    ├── integration/    # State + storage integration tests
    └── e2e/            # MODIFIED: E2E tests for frontend ↔ backend flow
```

**Structure Decision**: This is a web application with separate frontend and backend. The backend directory will be created for this feature. Frontend exists and will be modified to communicate with the backend API instead of using client-side loopback. This follows the "Option 2: Web application" pattern with clear separation of concerns.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All constitution principles are satisfied.
