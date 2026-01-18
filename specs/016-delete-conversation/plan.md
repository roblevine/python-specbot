# Implementation Plan: Delete Conversation

**Branch**: `016-delete-conversation` | **Date**: 2026-01-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/016-delete-conversation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add a "Delete" option to the conversation context menu (ellipsis) in the history sidebar, allowing users to permanently remove any conversation including the active one. A confirmation dialog ensures users don't accidentally delete conversations. When deleting the active conversation, the system switches to another conversation or creates a new one. The backend DELETE endpoint already exists; this feature primarily requires frontend UI changes.

## Technical Context

**Language/Version**: Python 3.13 (backend), JavaScript ES6+ (frontend)
**Primary Dependencies**: FastAPI 0.115.0, Pydantic 2.10.0 (backend); Vue 3.4.0, Vite 5.0.0 (frontend)
**Storage**: File-based JSON storage (backend); existing storage layer handles delete
**Testing**: pytest 8.3.0 with pytest-asyncio (backend); Vitest 1.0.0 with @testing-library/vue (frontend)
**Target Platform**: Linux server (backend), Modern browsers (frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Delete operation completes < 1 second; UI feedback is immediate
**Constraints**: Confirmation required before destructive action; handle active conversation deletion gracefully
**Scale/Scope**: Single user; conversation list typically < 100 items

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | ✅ PASS | DELETE endpoint already exists at `/api/v1/conversations/{id}` with 204 response |
| II. Modular Architecture | ✅ PASS | New DeleteConfirmationDialog component is self-contained; TitleMenu extended via props |
| III. Test-First Development | ✅ PLANNED | Tests will be written before implementation per TDD workflow |
| IV. Integration & Contract Testing | ✅ PLANNED | Contract tests exist for DELETE endpoint; frontend tests will verify integration |
| V. Observability & Debuggability | ✅ PASS | Existing logging patterns in useConversations and apiClient will be reused |
| VI. Simplicity & YAGNI | ✅ PASS | Minimal changes: extend menu, add dialog, wire events; no new abstractions |
| VII. Versioning & Breaking Changes | ✅ PASS | No API changes; frontend-only feature addition |
| VIII. Incremental Delivery | ✅ PLANNED | P1 (basic delete) → P2 (confirmation) as thin slices |
| IX. Living Architecture Documentation | ✅ N/A | No architectural changes; adding UI component to existing structure |

**Gate Status**: ✅ PASS - All principles satisfied or planned for compliance.

**Architecture Documentation**: Not required - this feature adds a UI component and wires existing functionality without changing system architecture, data flows, or integration points.

## Project Structure

### Documentation (this feature)

```text
specs/016-delete-conversation/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   └── api/
│       └── routes/
│           └── conversations.py    # DELETE endpoint (already implemented)
└── tests/
    ├── contract/                   # Contract tests (existing)
    └── integration/                # Integration tests (existing)

frontend/
├── src/
│   ├── components/
│   │   ├── TitleMenu/
│   │   │   └── TitleMenu.vue       # Add 'delete' emit
│   │   ├── DeleteConfirmationDialog/
│   │   │   └── DeleteConfirmationDialog.vue  # NEW: Confirmation modal
│   │   ├── HistoryBar/
│   │   │   └── HistoryBar.vue      # Add delete-conversation emit
│   │   └── App/
│   │       └── App.vue             # Handle delete event, show dialog, call composable
│   ├── state/
│   │   └── useConversations.js     # deleteConversation method (already implemented)
│   └── services/
│       └── apiClient.js            # deleteConversation function (already implemented)
└── tests/
    ├── unit/
    │   ├── TitleMenu.spec.js       # Test delete option visibility
    │   └── DeleteConfirmationDialog.spec.js  # NEW: Dialog tests
    └── integration/
        └── delete-conversation.spec.js  # NEW: End-to-end delete flow tests
```

**Structure Decision**: Web application structure with frontend/backend separation. This feature primarily modifies frontend components with no backend changes required.

## Complexity Tracking

> No complexity violations. This feature follows existing patterns:
> - Modal dialog pattern from RenameDialog
> - Context menu extension pattern from TitleMenu
> - Event handling pattern from App.vue
> - API integration pattern from apiClient.js

## Testing Strategy

### Frontend Unit Tests

| Component | Test File | Coverage |
|-----------|-----------|----------|
| TitleMenu | `frontend/tests/unit/TitleMenu.test.js` | Delete emit, delete option always visible |
| DeleteConfirmationDialog | `frontend/tests/unit/DeleteConfirmationDialog.test.js` | Props rendering, confirm/cancel emits, keyboard (Escape), overlay click |
| HistoryBar | `frontend/tests/unit/HistoryBar.test.js` | delete-conversation emit |

### Frontend Integration Tests

| Flow | Test File | Scenarios |
|------|-----------|-----------|
| Delete conversation flow | `frontend/tests/integration/delete-conversation.test.js` | Full delete flow, confirmation dialog flow, cancel flow, delete active conversation |

### Frontend Contract Tests

| Contract | Test File | Verification |
|----------|-----------|--------------|
| DELETE /api/v1/conversations/{id} | `frontend/tests/contract/deleteConversation.test.js` | Request format matches contract, snapshot comparison |

### Backend Integration Tests

| Endpoint | Test File | Scenarios |
|----------|-----------|-----------|
| DELETE /api/v1/conversations/{id} | `backend/tests/integration/test_conversations_api.py` | Success (204), Not Found (404), invalid ID format |

### Backend Contract Tests

| Contract | Test File | Verification |
|----------|-----------|--------------|
| DELETE conversation | `backend/tests/contract/test_conversations_contract.py` | Response format matches contract, status codes |

### Test Execution Order

1. **Frontend Unit Tests** - Run in parallel (T037, T038, T039)
2. **Frontend Integration Tests** - After unit tests (T040)
3. **Contract Tests** - Run in parallel (T041, T042, T043)
4. **Full Test Suite** - Final validation via `./scripts/test-all.sh`

### Test Tooling

- **Frontend**: Vitest 1.0.0, @testing-library/vue, happy-dom
- **Backend**: pytest 8.3.0, pytest-asyncio, httpx for async client testing
- **Contract**: JSON snapshot comparison for request/response validation
