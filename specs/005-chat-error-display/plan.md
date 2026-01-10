# Implementation Plan: Chat Error Display

**Branch**: `005-chat-error-display` | **Date**: 2026-01-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-chat-error-display/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature enhances error visibility in the chat interface by displaying client-side and server-side errors directly in the chat message area with expandable details. Users will see clearly marked error messages with visual distinction, human-readable summaries, and the ability to expand errors to view technical details (error codes, stack traces, timestamps). Sensitive information (API keys, tokens) will be redacted by default with a toggle to reveal details with security warnings.

## Technical Context

**Language/Version**: JavaScript ES6+ (Frontend), Python 3.13 (Backend)
**Primary Dependencies**:
- Frontend: Vue.js 3.4.0 (Composition API), Vite 5.0.0
- Backend: FastAPI 0.115.0, uvicorn 0.32.0, Pydantic 2.10.0
**Storage**: Browser LocalStorage (versioned schema v1.0.0)
**Testing**:
- Frontend: Vitest 1.0.0, Playwright 1.40.0, Testing Library for Vue
- Backend: pytest, OpenAPI contract tests
**Target Platform**: Web browser (Chrome, Firefox, Safari) + Linux server
**Project Type**: Web (separate frontend + backend)
**Performance Goals**:
- Error display within 2 seconds of occurrence (SC-001)
- Layout stability for messages up to 10,000 characters (SC-004)
**Constraints**:
- No breaking changes to existing message structure
- Maintain existing error handling patterns
- XSS prevention for error content (FR-012)
**Scale/Scope**:
- 6 Vue components (add 1-2 new components)
- Extend existing error handling in useAppState.js, apiClient.js
- Add error message type to message schema

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Initial Check**: ✅ PASSED (2026-01-10 before research)
**Post-Design Check**: ✅ PASSED (2026-01-10 after Phase 1 design)

### ✅ I. API-First Design
**Status**: PASS - No new API endpoints required. Feature extends existing error response handling.
**Rationale**: Backend already returns ErrorResponse schema with status, error, detail, timestamp. Frontend will consume existing error format without API changes.

### ✅ II. Modular Architecture
**Status**: PASS - Feature contained within message display module.
**Rationale**: New ErrorMessage component will be self-contained with clear interface. Changes isolated to ChatArea/MessageBubble components and error state management.

### ✅ III. Test-First Development (NON-NEGOTIABLE)
**Status**: COMMITTED - TDD workflow will be followed.
**Plan**:
1. Write tests for error message display (unit tests)
2. Write tests for expand/collapse behavior (integration tests)
3. Write tests for sensitive data redaction (unit + integration)
4. Verify tests FAIL before implementation
5. Implement minimum code to pass tests
6. Refactor while keeping tests green

### ✅ IV. Integration & Contract Testing (NON-NEGOTIABLE)
**Status**: PASS - No new contracts, extends existing error response consumption.
**Rationale**: Backend ErrorResponse schema already defined and tested. Frontend will add rendering for existing error format. Contract tests already validate error responses (400, 422, 500).
**Note**: Will add frontend integration tests to verify error display with mocked API error responses.

### ✅ V. Observability & Debuggability
**Status**: PASS - Feature enhances observability by surfacing errors to users.
**Rationale**: Existing structured logging remains. Error display adds user-facing observability. Logger.js already captures errors with context (messageId, statusCode, details).

### ✅ VI. Simplicity & YAGNI
**Status**: PASS - Simple error display enhancement, no over-engineering.
**Rationale**:
- Use existing CSS variable system (no new UI library)
- Extend existing message structure (no schema refactor)
- Simple toggle for expand/collapse (no complex state machine)
- Pattern matching for sensitive data (no ML/AI complexity)

### ✅ VII. Versioning & Breaking Changes
**Status**: PASS - Non-breaking change, additive only.
**Rationale**:
- Extends message schema with optional error field
- Backward compatible with existing messages
- No API version bump required

### ✅ VIII. Incremental Delivery & Thin Slices (NON-NEGOTIABLE)
**Status**: COMMITTED - Will implement P1 → P2 → P3 user stories as separate slices.
**Slice Plan**:
1. **Slice 1 (P1)**: Display client-side errors in chat with visual distinction
   - Add error message type to message schema
   - Create ErrorMessage component
   - Display errors in ChatArea
   - Tests: error message rendering, visual distinction
2. **Slice 2 (P2)**: Display server-side errors in chat
   - Extend error parsing in apiClient.js
   - Map HTTP errors to error messages
   - Tests: 400/422/500 error display
3. **Slice 3 (P3)**: Expandable error details with sensitive data redaction
   - Add expand/collapse UI to ErrorMessage
   - Implement sensitive data pattern matching
   - Add toggle for revealing sensitive data
   - Tests: expand/collapse, redaction, toggle

### ✅ IX. Living Architecture Documentation
**Status**: PASS - Will update architecture.md with error display component.
**Plan**: Document error message flow, new component structure, and integration with existing message system in architecture.md.

**Note**: No architectural changes required. Feature extends existing message display architecture without introducing new modules or integration points.

## Project Structure

### Documentation (this feature)

```text
specs/005-chat-error-display/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output - research error display patterns
├── data-model.md        # Phase 1 output - error message schema
├── quickstart.md        # Phase 1 output - developer guide
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Web application (frontend + backend)

frontend/
├── src/
│   ├── components/
│   │   ├── ChatArea/
│   │   │   ├── ChatArea.vue           # MODIFY: render error messages
│   │   │   ├── MessageBubble.vue      # MODIFY: handle error message type
│   │   │   └── ErrorMessage.vue       # NEW: error display component
│   │   ├── StatusBar.vue              # NO CHANGE: existing status indicator
│   │   └── InputArea.vue              # NO CHANGE
│   ├── state/
│   │   ├── useAppState.js             # MODIFY: extend error state
│   │   ├── useMessages.js             # MODIFY: create error messages
│   │   └── useConversations.js        # NO CHANGE
│   ├── services/
│   │   └── apiClient.js               # MODIFY: enrich error details
│   ├── utils/
│   │   ├── errorFormatter.js          # NEW: format errors for display
│   │   └── sensitiveDataRedactor.js   # NEW: redact sensitive patterns
│   └── public/styles/
│       └── global.css                 # MODIFY: add error message styles
├── tests/
│   ├── unit/
│   │   ├── ErrorMessage.test.js       # NEW: component tests
│   │   ├── errorFormatter.test.js     # NEW: utility tests
│   │   └── sensitiveDataRedactor.test.js # NEW: redaction tests
│   ├── integration/
│   │   └── errorDisplay.test.js       # NEW: end-to-end error flow
│   └── e2e/
│       └── error-scenarios.spec.js    # NEW: Playwright E2E tests

backend/
├── src/
│   ├── schemas.py                     # NO CHANGE: ErrorResponse already defined
│   └── api/routes/messages.py         # NO CHANGE: error handling complete
└── tests/
    └── contract/
        └── test_message_api_contract.py # NO CHANGE: contract tests exist
```

**Structure Decision**: Web application pattern (Option 2) confirmed. Frontend and backend are independent projects. This feature is frontend-focused with no backend changes required (error responses already properly structured).

## Complexity Tracking

> **No violations - this section is empty**

All constitution principles are satisfied without exceptions. No complexity justification required.
