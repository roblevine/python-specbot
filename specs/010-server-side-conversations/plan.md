# Implementation Plan: Server-Side Conversation Storage

**Branch**: `010-server-side-conversations` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-server-side-conversations/spec.md`

## Summary

Migrate conversation storage from browser localStorage to server-side file-based persistence. This feature implements a CRUD API for conversations with an abstracted storage layer that supports future database migration. The frontend will be updated to use the new API endpoints instead of localStorage for all conversation operations.

## Technical Context

**Language/Version**: Python 3.11 (backend), JavaScript ES6+ (frontend)
**Primary Dependencies**: FastAPI 0.115.0, Pydantic 2.10.0, Vue 3.4.0, Vite 5.0.0
**Storage**: File-based JSON storage with abstraction layer for future database migration
**Testing**: pytest 8.3.0 (backend), Vitest 1.0.0 (frontend), openapi-core 0.18.2 (contracts)
**Target Platform**: Web application (backend server + browser client)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Conversations load within 2 seconds, save within 1 second
**Constraints**: File locking for concurrent access, single-user (no auth required)
**Scale/Scope**: Hundreds of conversations, single-user application

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | ✅ PASS | Contracts defined before implementation (this plan) |
| II. Modular Architecture | ✅ PASS | Storage layer abstracted, clear module boundaries |
| III. Test-First Development | ✅ PLAN | Tests will be written before implementation |
| IV. Integration & Contract Testing | ✅ PLAN | Contract tests for all new endpoints required |
| V. Observability & Debuggability | ✅ PLAN | Structured logging for storage operations |
| VI. Simplicity & YAGNI | ✅ PASS | File storage is simplest solution; abstraction justified for stated DB migration |
| VII. Versioning & Breaking Changes | ✅ PASS | New endpoints, no breaking changes to existing API |
| VIII. Incremental Delivery | ✅ PLAN | P1 stories first (retrieve/save), then P2 (manage) |
| IX. Living Architecture Documentation | ✅ PLAN | architecture.md will be updated with storage layer |

**Architecture Update Required**: This feature introduces:
- New storage service module in backend
- New API routes for conversations
- New frontend API client methods
- Changes to data flow (localStorage → server API)

## Project Structure

### Documentation (this feature)

```text
specs/010-server-side-conversations/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI specs)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/routes/
│   │   ├── messages.py      # Existing - chat endpoint
│   │   ├── models.py        # Existing - model selection
│   │   └── conversations.py # NEW - conversation CRUD
│   ├── services/
│   │   ├── llm_service.py       # Existing
│   │   ├── message_service.py   # Existing
│   │   └── storage_service.py   # NEW - storage abstraction
│   ├── storage/                  # NEW - storage implementations
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract storage interface
│   │   └── file_storage.py      # File-based implementation
│   └── schemas.py               # UPDATE - add conversation schemas
├── tests/
│   ├── contract/
│   │   └── conversations/       # NEW - contract tests
│   ├── integration/
│   │   └── test_conversations.py # NEW
│   └── unit/
│       ├── test_storage_service.py  # NEW
│       └── test_file_storage.py     # NEW
└── data/                        # NEW - storage directory
    └── conversations.json       # Runtime data file

frontend/
├── src/
│   ├── services/
│   │   └── apiClient.js         # UPDATE - add conversation methods
│   ├── state/
│   │   └── useConversations.js  # UPDATE - use API instead of localStorage
│   └── storage/
│       └── LocalStorageAdapter.js # DEPRECATE - keep for migration only
├── tests/
│   └── unit/
│       └── useConversations.test.js # UPDATE - test API integration
└── tests/
    └── contract/
        └── conversations.contract.test.js # NEW
```

**Structure Decision**: Web application pattern with backend/frontend directories. New storage module added to backend with abstract interface for future extensibility.

## Complexity Tracking

> No violations - file storage with abstraction is the simplest solution for stated requirements.

| Decision | Justification |
|----------|---------------|
| Storage abstraction layer | Explicitly required by spec (FR-012) for future DB migration |
| File locking | Required by spec (FR-011) for concurrent request handling |
