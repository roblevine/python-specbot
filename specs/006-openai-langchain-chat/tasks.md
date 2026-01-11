# Tasks: OpenAI LangChain Chat Integration

**Input**: Design documents from `/specs/006-openai-langchain-chat/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test-First Development is REQUIRED per Constitution Principle III. Contract Testing is REQUIRED per Principle IV.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Backend tests: `backend/tests/`
- Frontend unchanged for this feature

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency configuration

- [ ] T001 Add LangChain dependencies to backend/requirements.txt (langchain>=0.3.0, langchain-openai>=0.2.0)
- [ ] T002 Add OPENAI_API_KEY and OPENAI_MODEL to backend/.env.example
- [ ] T003 [P] Copy updated OpenAPI contract to specs/003-backend-api-loopback/contracts/message-api.yaml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core LLM infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundation

- [ ] T004 [P] Unit test skeleton for LLM service in backend/tests/unit/test_llm_service.py (test ChatOpenAI initialization, mock config loading)
- [ ] T005 [P] Integration test skeleton for OpenAI integration in backend/tests/integration/test_openai_integration.py (with response mocking)

### Implementation for Foundation

- [ ] T006 Create LLM service module in backend/src/services/llm_service.py with ChatOpenAI initialization
- [ ] T007 Implement config loading from environment (OPENAI_API_KEY, OPENAI_MODEL with gpt-3.5-turbo default) in backend/src/services/llm_service.py
- [ ] T008 Add LLM logging utilities (llm_request_start, llm_request_complete, llm_request_error) to backend/src/utils/logger.py

**Checkpoint**: LLM service infrastructure ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Send Message to AI and Receive Response (Priority: P1) 🎯 MVP

**Goal**: Route user messages through OpenAI ChatGPT and display AI responses in the chat interface

**Independent Test**: Send "Hello, how are you?" and verify an intelligent AI response is displayed

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T009 [P] [US1] Contract test for POST /api/v1/messages AI response format in backend/tests/contract/test_message_api_contract.py (verify response.message contains AI text, not "api says:" prefix)
- [ ] T010 [P] [US1] Unit test for get_ai_response() basic invocation in backend/tests/unit/test_llm_service.py (mock ChatOpenAI.ainvoke)
- [ ] T011 [P] [US1] Integration test for single message AI response in backend/tests/integration/test_openai_integration.py (mock external API, verify full flow)

### Implementation for User Story 1

- [ ] T012 [US1] Implement convert_to_langchain_messages() in backend/src/services/llm_service.py (single message, no history)
- [ ] T013 [US1] Implement async get_ai_response(message: str) in backend/src/services/llm_service.py using ChatOpenAI.ainvoke()
- [ ] T014 [US1] Update send_message() in backend/src/api/routes/messages.py to call llm_service instead of loopback
- [ ] T015 [US1] Add request/response logging for LLM calls in backend/src/api/routes/messages.py
- [ ] T016 [US1] Verify contract tests pass with new AI response format

**Checkpoint**: User can send a message and receive AI response - MVP complete

---

## Phase 4: User Story 2 - Maintain Conversation Context (Priority: P2)

**Goal**: Include conversation history in LLM requests for multi-turn conversations

**Independent Test**: Send "My name is Alice", then "What is my name?" and verify AI recalls "Alice"

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T017 [P] [US2] Contract test for history field in MessageRequest in backend/tests/contract/test_message_api_contract.py
- [ ] T018 [P] [US2] Unit test for convert_to_langchain_messages() with history array in backend/tests/unit/test_llm_service.py
- [ ] T019 [P] [US2] Integration test for context-aware response in backend/tests/integration/test_openai_integration.py (verify history is sent to LLM)

### Implementation for User Story 2

- [ ] T020 [US2] Add optional history field to MessageRequest in backend/src/schemas.py (list of {sender, text} objects)
- [ ] T021 [US2] Add history validation (sender must be user/system, text non-empty) in backend/src/schemas.py
- [ ] T022 [US2] Extend convert_to_langchain_messages() to handle history array in backend/src/services/llm_service.py
- [ ] T023 [US2] Update get_ai_response() to accept and process history in backend/src/services/llm_service.py
- [ ] T024 [US2] Update send_message() to pass history to LLM service in backend/src/api/routes/messages.py
- [ ] T025 [US2] Update frontend apiClient.sendMessage() to include history from conversation in frontend/src/services/apiClient.js
- [ ] T026 [US2] Update useMessages.sendUserMessage() to gather and send history in frontend/src/state/useMessages.js
- [ ] T027 [US2] Verify context is maintained for 10+ message exchanges (SC-002)

**Checkpoint**: Multi-turn conversations work with context - User Stories 1 AND 2 complete

---

## Phase 5: User Story 3 - Handle API Errors Gracefully (Priority: P3)

**Goal**: Map OpenAI exceptions to user-friendly error messages without exposing sensitive data

**Independent Test**: Simulate invalid API key and verify user sees "AI service configuration error" (not raw error)

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T028 [P] [US3] Contract test for 503 error responses in backend/tests/contract/test_message_api_contract.py
- [x] T029 [P] [US3] Contract test for 504 timeout response in backend/tests/contract/test_message_api_contract.py
- [x] T030 [P] [US3] Unit test for error mapping (AuthenticationError → 503) in backend/tests/unit/test_llm_service.py
- [x] T031 [P] [US3] Unit test for error mapping (RateLimitError → 503) in backend/tests/unit/test_llm_service.py
- [x] T032 [P] [US3] Unit test for error mapping (Timeout → 504) in backend/tests/unit/test_llm_service.py
- [x] T033 [P] [US3] Integration test verifying no sensitive data in error responses in backend/tests/integration/test_openai_integration.py

### Implementation for User Story 3

- [x] T034 [US3] Implement error handler for AuthenticationError → 503 "AI service configuration error" in backend/src/services/llm_service.py
- [x] T035 [US3] Implement error handler for RateLimitError → 503 "AI service is busy" in backend/src/services/llm_service.py
- [x] T036 [US3] Implement error handler for APIConnectionError → 503 "Unable to reach AI service" in backend/src/services/llm_service.py
- [x] T037 [US3] Implement error handler for timeout → 504 "Request timed out" in backend/src/services/llm_service.py
- [x] T038 [US3] Implement error handler for BadRequestError → 400 "Message could not be processed" in backend/src/services/llm_service.py
- [x] T039 [US3] Add try/catch in send_message() to catch and re-raise LLM errors as HTTPException in backend/src/api/routes/messages.py
- [x] T040 [US3] Add ERROR level logging for all LLM failures (sanitized) in backend/src/services/llm_service.py
- [x] T041 [US3] Verify no API keys or raw errors exposed in any error response (SC-003)

**Checkpoint**: All error scenarios handled gracefully - All user stories complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and architecture updates

- [x] T042 [P] Update architecture.md with LLM service layer diagram and data flow
- [x] T043 [P] Update contract snapshots in contract-snapshots/ directory
- [x] T044 [P] Run all tests and verify 100% pass rate
- [ ] T045 [P] Run quickstart.md validation (manual test with real API key)
- [x] T046 Review and update CLAUDE.md if needed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories should proceed sequentially in priority order (P1 → P2 → P3)
  - P2 extends P1 functionality (history support)
  - P3 is independent but benefits from P1/P2 context
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 (extends message handling) - Adds history support
- **User Story 3 (P3)**: Can start after Foundational but recommended after US1 - Adds error handling

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Service layer before API layer
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Within Phase 2 (Foundational):**
- T004 and T005 can run in parallel (different test files)

**Within User Story 1:**
- T009, T010, T011 can run in parallel (test files)

**Within User Story 2:**
- T017, T018, T019 can run in parallel (test files)

**Within User Story 3:**
- T028-T033 can all run in parallel (test files)

**Within Phase 6 (Polish):**
- T042, T043, T044, T045 can run in parallel

---

## Parallel Example: User Story 3 Tests

```bash
# Launch all error handling tests together:
Task: "Contract test for 503 error responses in backend/tests/contract/test_message_api_contract.py"
Task: "Contract test for 504 timeout response in backend/tests/contract/test_message_api_contract.py"
Task: "Unit test for error mapping (AuthenticationError → 503) in backend/tests/unit/test_llm_service.py"
Task: "Unit test for error mapping (RateLimitError → 503) in backend/tests/unit/test_llm_service.py"
Task: "Unit test for error mapping (Timeout → 504) in backend/tests/unit/test_llm_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T008)
3. Complete Phase 3: User Story 1 (T009-T016)
4. **STOP and VALIDATE**: Test sending a message and receiving AI response
5. Deploy/demo if ready - Basic AI chat works!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **Deploy/Demo (MVP!)**
3. Add User Story 2 → Test context retention → Deploy/Demo (multi-turn chat)
4. Add User Story 3 → Test error scenarios → Deploy/Demo (production-ready)
5. Polish phase → Final documentation and validation

---

## Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|------------------------|
| Phase 1: Setup | 3 | 1 |
| Phase 2: Foundational | 5 | 2 |
| Phase 3: User Story 1 | 8 | 3 |
| Phase 4: User Story 2 | 11 | 3 |
| Phase 5: User Story 3 | 14 | 6 |
| Phase 6: Polish | 5 | 4 |
| **Total** | **46** | **19** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD required per Constitution)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Frontend changes only needed for US2 (history support)
