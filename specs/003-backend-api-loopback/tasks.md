# Tasks: Backend API Loopback

**Input**: Design documents from `/specs/003-backend-api-loopback/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/message-api.yaml
**Feature Branch**: `003-backend-api-loopback`
**Generated**: 2025-12-28

**Tests**: This feature uses Test-Driven Development (TDD) per Constitution Principle III (NON-NEGOTIABLE). Tests are written FIRST and must FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **Checkbox**: `- [ ]` for task tracking
- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with separate backend and frontend:
- **Backend**: `/workspaces/python-specbot/backend/`
- **Frontend**: `/workspaces/python-specbot/frontend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize backend project structure and install dependencies

**Duration Estimate**: ~15-30 minutes

- [x] T001 Create backend directory structure (backend/src/api/routes, backend/src/services, backend/src/middleware, backend/src/utils, backend/tests/contract, backend/tests/integration, backend/tests/unit)
- [x] T002 Create backend/requirements.txt with FastAPI 0.115.0, uvicorn[standard] 0.32.0, pydantic 2.10.0, pytest 8.3.0, httpx 0.28.0, pytest-asyncio 0.24.0, pytest-cov 4.1.0, openapi-core 0.18.2, pyyaml 6.0.1, python-dotenv 1.0.0
- [x] T003 [P] Create backend/.env.example file with API_HOST, API_PORT, FRONTEND_URL, LOG_LEVEL
- [x] T004 [P] Create backend/.gitignore with venv/, .env, __pycache__/, *.pyc, .pytest_cache/, htmlcov/, .coverage
- [x] T005 Create backend/venv and install dependencies (python -m venv venv && pip install -r requirements.txt)
- [x] T006 [P] Create backend/pytest.ini with test configuration (testpaths, markers for unit/integration/contract)
- [x] T007 [P] Create backend/README.md with setup instructions and quickstart commands

**Checkpoint**: Backend project structure ready, dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core backend infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Duration Estimate**: ~45-60 minutes

- [x] T008 Create backend/main.py with FastAPI app initialization, CORS middleware, and uvicorn runner
- [x] T009 [P] Create backend/src/__init__.py (empty package marker)
- [x] T010 [P] Create backend/src/api/__init__.py (empty package marker)
- [x] T011 [P] Create backend/src/api/routes/__init__.py (empty package marker)
- [x] T012 [P] Create backend/src/services/__init__.py (empty package marker)
- [x] T013 [P] Create backend/src/middleware/__init__.py (empty package marker)
- [x] T014 [P] Create backend/src/utils/__init__.py (empty package marker)
- [x] T015 Create backend/src/utils/logger.py with structured logging setup (DEBUG, INFO, ERROR levels)
- [x] T016 [P] Create backend/src/middleware/logging_middleware.py with request/response logging
- [x] T017 Create backend/tests/conftest.py with shared pytest fixtures (openapi_spec, client)
- [x] T018 Add health check endpoint (GET /health) in backend/main.py for monitoring
- [x] T019 Configure CORS middleware in backend/main.py to allow http://localhost:5173, http://127.0.0.1:5173, http://0.0.0.0:5173
- [x] T020 Verify backend starts successfully and health check returns 200 OK

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Send Message to Backend and Receive Loopback Response (Priority: P1) 🎯 MVP

**Goal**: Users can send messages through the chat interface and receive responses from the backend server with "api says: " prefix

**Independent Test**: Send message "Hello world" via POST /api/v1/messages and verify response contains "api says: Hello world"

**Acceptance Criteria** (from spec.md):
1. User types "Hello world" and clicks Send → chat displays "api says: Hello world"
2. Response received within 2 seconds
3. Multiple messages in sequence → each response has "api says: " prefix with exact text
4. Special characters (emoji, line breaks) → preserved in loopback

**Duration Estimate**: ~2-3 hours (TDD workflow)

### Tests for User Story 1 (TDD - Write FIRST) ⚠️

> **CRITICAL**: Write these tests FIRST, ensure they FAIL before implementation

- [x] T021 [P] [US1] Create backend/tests/contract/test_message_api_contract.py with test_loopback_request_matches_contract (validate MessageRequest against OpenAPI schema)
- [x] T022 [P] [US1] Add test_loopback_response_matches_contract to backend/tests/contract/test_message_api_contract.py (validate MessageResponse against OpenAPI schema)
- [x] T023 [P] [US1] Create backend/tests/integration/test_message_loopback_flow.py with test_send_message_receives_loopback_response (POST /api/v1/messages → verify 200 and "api says: " prefix)
- [x] T024 [P] [US1] Add test_loopback_preserves_special_characters to backend/tests/integration/test_message_loopback_flow.py (test emoji, newlines, special chars)
- [x] T025 [P] [US1] Add test_loopback_response_time_under_2_seconds to backend/tests/integration/test_message_loopback_flow.py (verify FR-006 performance requirement)
- [x] T026 [P] [US1] Add test_multiple_messages_in_sequence to backend/tests/integration/test_message_loopback_flow.py (verify FR-005 message order)
- [x] T027 [P] [US1] Create backend/tests/unit/test_message_service.py with test_loopback_message_adds_api_prefix (unit test for service logic)
- [x] T028 [P] [US1] Add test_loopback_preserves_content to backend/tests/unit/test_message_service.py (verify no truncation/modification)
- [x] T029 Run pytest backend/tests/ -v and confirm ALL tests FAIL (expected RED phase)

### Implementation for User Story 1 (Make tests GREEN)

- [x] T030 [P] [US1] Create backend/src/schemas.py with MessageRequest Pydantic model (message: str, conversationId: Optional[str], timestamp: Optional[str])
- [x] T031 [P] [US1] Add MessageResponse Pydantic model to backend/src/schemas.py (status: "success", message: str, timestamp: str)
- [x] T032 [P] [US1] Add ErrorResponse Pydantic model to backend/src/schemas.py (status: "error", error: str, detail: Optional[Dict], timestamp: str)
- [x] T033 [US1] Create backend/src/services/message_service.py with create_loopback_message(user_message: str) -> str function
- [x] T034 [US1] Add message validation to backend/src/services/message_service.py (empty check, length check <10,000 chars)
- [x] T035 [US1] Create backend/src/api/routes/messages.py with POST /api/v1/messages endpoint using MessageRequest/MessageResponse schemas
- [x] T036 [US1] Add error handling to backend/src/api/routes/messages.py (400 for empty/too long, 422 for schema validation, 500 for server errors)
- [x] T037 [US1] Add request/response logging to backend/src/api/routes/messages.py using logger from utils (per FR-014)
- [x] T038 [US1] Register messages router in backend/main.py
- [x] T039 Run pytest backend/tests/ -v and confirm ALL User Story 1 tests PASS (GREEN phase)

### Frontend Integration for User Story 1

- [x] T040 [US1] Create frontend/src/services/apiClient.js with sendMessage(messageText) function using fetch to POST localhost:8000/api/v1/messages
- [x] T041 [US1] Add error handling to frontend/src/services/apiClient.js (network errors, timeouts, HTTP errors)
- [x] T042 [US1] Add 10-second timeout to frontend/src/services/apiClient.js (per FR-009)
- [x] T043 [US1] Update frontend/src/state/useMessages.js to import and call apiClient.sendMessage() instead of local loopback
- [x] T044 [US1] Update frontend/src/state/useMessages.js to handle API response format (status, message, timestamp)
- [x] T045 [US1] Add loading indicator support to frontend/src/state/useAppState.js (per FR-013)
- [x] T046 [US1] Update frontend tests to mock apiClient for unit tests (frontend/tests/unit/)
- [x] T047 [US1] Update frontend E2E tests to run against real backend (frontend/tests/e2e/send-message.test.js)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can send messages to backend and receive "api says: " responses.

---

## Phase 4: User Story 2 - Handle Backend Connection Errors Gracefully (Priority: P2)

**Goal**: Users receive clear feedback when backend is unavailable or experiencing errors

**Independent Test**: Stop backend server, send message → verify error message "Cannot connect to server" appears in status bar

**Acceptance Criteria** (from spec.md):
1. Backend not running → status bar shows "Error: Cannot connect to server"
2. Request timeout (>10s) → displays "Error: Request timed out. Please try again."
3. Server error (500) → status bar shows "Error: Server error occurred"
4. Connection fails mid-request → message remains in input area for retry

**Duration Estimate**: ~1-2 hours

### Tests for User Story 2 (TDD - Write FIRST) ⚠️

> **CRITICAL**: Write these tests FIRST, ensure they FAIL before implementation

- [x] T048 [P] [US2] Add test_backend_unavailable_shows_error to frontend/tests/integration/ (mock network error → verify error message)
- [x] T049 [P] [US2] Add test_timeout_shows_error to frontend/tests/integration/ (mock delay >10s → verify timeout error)
- [x] T050 [P] [US2] Add test_server_error_500_shows_error to frontend/tests/integration/ (mock 500 response → verify error message)
- [x] T051 [P] [US2] Add test_message_preserved_on_error to frontend/tests/integration/ (error occurs → input field retains message)
- [x] T052 [P] [US2] Add test_empty_message_rejected_by_backend to backend/tests/integration/test_error_handling.py (POST empty message → verify 400 error)
- [x] T053 [P] [US2] Add test_too_long_message_rejected to backend/tests/integration/test_error_handling.py (POST >10,000 chars → verify 400 error)
- [x] T054 [P] [US2] Add test_malformed_json_rejected to backend/tests/integration/test_error_handling.py (POST invalid JSON → verify 422 error)
- [x] T055 Run pytest -v and confirm User Story 2 tests FAIL (expected RED phase)

### Implementation for User Story 2

- [x] T056 [US2] Enhance frontend/src/services/apiClient.js with detailed error parsing (network, timeout, HTTP status codes)
- [x] T057 [US2] Add error message mapping in frontend/src/services/apiClient.js (connection → "Cannot connect to server", timeout → "Request timed out", 500 → "Server error occurred")
- [x] T058 [US2] Update frontend/src/state/useMessages.js to preserve message text in input on error (don't clear on failure)
- [x] T059 [US2] Update frontend/src/state/useMessages.js to set appropriate error status for different failure types
- [x] T060 [US2] Update frontend/src/components/StatusBar.vue to display different error messages based on error type
- [x] T061 [US2] Add retry button/logic to frontend when errors occur (optional enhancement)
- [x] T062 Run pytest backend/tests/ frontend/tests/ and confirm User Story 2 tests PASS (GREEN phase)

**Checkpoint**: At this point, User Story 2 should be fully functional. Users receive clear error feedback when backend issues occur.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements, documentation, and architecture updates

**Duration Estimate**: ~1-2 hours

- [x] T063 [P] Run backend linting and formatting (if configured: black, flake8, isort)
- [x] T064 [P] Run frontend linting and formatting (npm run lint && npm run format)
- [x] T065 [P] Generate test coverage report (pytest --cov=backend/src --cov-report=html)
- [x] T066 [P] Verify all Success Criteria from spec.md are met (SC-001 through SC-007)
- [x] T067 Update /workspaces/python-specbot/architecture.md with Backend API Server section in Current Architecture
- [x] T068 Add ADR (Architectural Decision Record) to architecture.md documenting FastAPI choice vs Flask
- [x] T069 Update architecture.md Technology Stack table with Python 3.13, FastAPI, uvicorn, pytest
- [x] T070 Add backend data flow diagram to architecture.md (Frontend → POST /api/v1/messages → Backend → Response)
- [x] T071 Update /workspaces/python-specbot/README.md with backend setup instructions and quickstart
- [x] T072 [P] Create backend/CHANGELOG.md documenting feature 003 implementation
- [x] T073 Run full test suite (backend + frontend) and verify 100% pass rate
- [x] T074 Manual smoke test: Start backend, start frontend, send message "Hello world", verify "api says: Hello world" appears
- [x] T075 Manual smoke test: Stop backend, send message, verify error message appears
- [x] T076 Manual smoke test: Send message with emoji 🚀, verify emoji preserved in response

**Checkpoint**: Feature complete, documented, and ready for commit

---

## Dependencies & Parallel Execution

### User Story Completion Order

```
Phase 1 (Setup) → Phase 2 (Foundation) → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (Polish)
                                            ↓
                                     MVP Delivery Point
```

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only)
- Delivers core functionality: backend loopback working end-to-end
- Independently testable and deployable
- Can ship without Phase 4 (error handling) for internal testing

**Full Feature**: All phases (US1 + US2)
- Production-ready with error handling
- Recommended for external release

### Parallel Execution Opportunities

**Within Phase 1 (Setup)**: T003, T004, T006, T007 can run in parallel after T001-T002

**Within Phase 2 (Foundation)**: T009-T014, T016 can run in parallel after T008

**Within Phase 3 - Tests** (US1): T021-T028 can ALL run in parallel (different test files)

**Within Phase 3 - Implementation** (US1): T030-T032, T034, T037 can run in parallel

**Within Phase 4 - Tests** (US2): T048-T054 can ALL run in parallel

**Within Phase 5 (Polish)**: T063-T065, T067-T072 can run in parallel

**Example Parallel Workflow** (User Story 1):
```bash
# Terminal 1: Contract tests
cd backend && pytest tests/contract/test_message_api_contract.py -v

# Terminal 2: Integration tests
cd backend && pytest tests/integration/test_message_loopback_flow.py -v

# Terminal 3: Unit tests
cd backend && pytest tests/unit/test_message_service.py -v

# Terminal 4: Schemas implementation
# Edit backend/src/schemas.py (T030-T032)

# All 4 can work simultaneously without conflicts
```

---

## Independent Test Criteria

### User Story 1 (P1 - MVP)

**How to verify independently**:
1. Start backend: `cd backend && python main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open http://localhost:5173
4. Type "Hello world" and click Send
5. ✅ **PASS**: Chat displays "api says: Hello world"
6. ✅ **PASS**: Response appears within 2 seconds
7. Send "Test 🚀" with emoji
8. ✅ **PASS**: Response is "api says: Test 🚀" (emoji preserved)

**Automated test**:
```bash
cd backend
pytest tests/integration/test_message_loopback_flow.py -v
# All tests should PASS
```

### User Story 2 (P2 - Error Handling)

**How to verify independently**:
1. Start frontend: `cd frontend && npm run dev`
2. **Do NOT start backend** (simulates server down)
3. Open http://localhost:5173
4. Type "Test" and click Send
5. ✅ **PASS**: Status bar shows "Error: Cannot connect to server"
6. ✅ **PASS**: Message "Test" remains in input field
7. Start backend: `cd backend && python main.py`
8. Click Send again (same message)
9. ✅ **PASS**: Message now works, displays "api says: Test"

**Automated test**:
```bash
cd frontend
npm run test  # Unit/integration tests with mocked errors
# All error handling tests should PASS
```

---

## Implementation Strategy

### TDD Workflow (Constitution Principle III - MANDATORY)

For each user story:

1. **RED**: Write failing tests first (T021-T029, T048-T055)
   - Contract tests validate OpenAPI schemas
   - Integration tests validate full request-response cycle
   - Unit tests validate business logic
   - Run `pytest -v` → confirm ALL tests FAIL

2. **GREEN**: Implement minimum code to pass tests (T030-T039, T056-T062)
   - Pydantic schemas for request/response
   - Service layer for business logic
   - API route handlers
   - Frontend integration
   - Run `pytest -v` → confirm ALL tests PASS

3. **REFACTOR**: Improve code while keeping tests green
   - Extract common validation logic
   - Improve error messages
   - Add logging and observability
   - Run `pytest -v` → tests still PASS

### Incremental Delivery (Constitution Principle VIII)

**Milestone 1** (MVP): Phases 1-3 (User Story 1)
- **Deliverable**: Basic loopback working end-to-end
- **Value**: Proves backend-frontend integration works
- **Duration**: ~4-5 hours
- **Commit**: "feat: implement backend API loopback (003-US1)"

**Milestone 2** (Production): Add Phase 4 (User Story 2)
- **Deliverable**: Error handling complete
- **Value**: Production-ready with graceful degradation
- **Duration**: +1-2 hours
- **Commit**: "feat: add error handling for backend API (003-US2)"

**Milestone 3** (Polish): Phase 5
- **Deliverable**: Documentation and architecture updates
- **Duration**: +1-2 hours
- **Commit**: "docs: update architecture for backend API (003)"

---

## Task Summary

**Total Tasks**: 76
- **Phase 1 (Setup)**: 7 tasks (~15-30 min)
- **Phase 2 (Foundation)**: 13 tasks (~45-60 min)
- **Phase 3 (US1 - MVP)**: 29 tasks (~2-3 hours)
  - Tests: 9 tasks (T021-T029)
  - Backend Implementation: 10 tasks (T030-T039)
  - Frontend Integration: 8 tasks (T040-T047)
  - Verification: 2 tasks (T029, T039)
- **Phase 4 (US2)**: 15 tasks (~1-2 hours)
  - Tests: 8 tasks (T048-T055)
  - Implementation: 7 tasks (T056-T062)
- **Phase 5 (Polish)**: 14 tasks (~1-2 hours)

**Parallel Opportunities**: 35 tasks marked with [P]

**User Stories**:
- **US1** (P1 - MVP): 29 tasks - Basic backend loopback
- **US2** (P2): 15 tasks - Error handling

**Suggested MVP Scope**: Phases 1-3 (User Story 1 only) = 49 tasks

**Estimated Total Duration**: 6-9 hours for full feature (MVP = 4-5 hours)

---

## Validation Checklist

✅ **Format**: All 76 tasks follow `- [ ] [ID] [P?] [Story?] Description with file path`
✅ **Organization**: Tasks grouped by user story (US1, US2)
✅ **Independent Testing**: Each user story has clear test criteria
✅ **TDD Workflow**: Tests written before implementation for each story
✅ **Parallel Opportunities**: 35 tasks marked [P] for concurrent execution
✅ **File Paths**: All tasks include specific file paths
✅ **Dependencies**: Clear phase order and story dependencies documented
✅ **MVP Defined**: Phase 1+2+3 delivers working backend loopback

---

**Ready to Begin**: Start with Phase 1 (Setup) and work through phases sequentially. Each phase builds on the previous one.

**Constitution Compliance**: Tasks follow TDD (Principle III), Incremental Delivery (Principle VIII), and API-First Design (Principle I).
