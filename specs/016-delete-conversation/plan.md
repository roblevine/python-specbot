# Implementation Plan: Delete Conversation

**Branch**: `016-delete-conversation` | **Date**: 2026-01-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/016-delete-conversation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add a "Delete" option to the conversation context menu (ellipsis) in the history sidebar, allowing users to permanently remove conversations. The delete option is hidden for the currently active conversation to prevent accidental deletion. A confirmation dialog ensures users don't accidentally delete conversations. The backend DELETE endpoint already exists; this feature primarily requires frontend UI changes.

## Technical Context

**Language/Version**: Python 3.13 (backend), JavaScript ES6+ (frontend)
**Primary Dependencies**: FastAPI 0.115.0, Pydantic 2.10.0 (backend); Vue 3.4.0, Vite 5.0.0 (frontend)
**Storage**: File-based JSON storage (backend); existing storage layer handles delete
**Testing**: pytest 8.3.0 with pytest-asyncio (backend); Vitest 1.0.0 with @testing-library/vue (frontend)
**Target Platform**: Linux server (backend), Modern browsers (frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Delete operation completes < 1 second; UI feedback is immediate
**Constraints**: Confirmation required before destructive action; active conversation protected
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
| VIII. Incremental Delivery | ✅ PLANNED | P1 (basic delete) → P2 (confirmation) → P3 (active protection) as thin slices |
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
│   │   │   └── TitleMenu.vue       # Add 'delete' emit, conditionally show option
│   │   ├── DeleteConfirmationDialog/
│   │   │   └── DeleteConfirmationDialog.vue  # NEW: Confirmation modal
│   │   ├── HistoryBar/
│   │   │   └── HistoryBar.vue      # Add delete-conversation emit, pass isActive prop
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
