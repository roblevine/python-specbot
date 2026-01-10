# Tasks: LLM Backend Integration

**Input**: Design documents from `/specs/005-llm-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-streaming-api.yaml

**Tests**: Tests are included per constitution Principle III (Test-First Development NON-NEGOTIABLE)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Backend tests: `backend/tests/`
- Frontend tests: `frontend/tests/`
- Contract snapshots: `tests/contract/snapshots/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and LangChain dependency setup

- [X] T001 Add LangChain dependencies to backend/requirements.txt (langchain~=0.3.0, langchain-openai~=0.3.0, langchain-core~=0.3.0, langchain-anthropic~=0.3.0, langchain-community~=0.3.0, openai>=1.0.0)
- [X] T002 Create backend/src/config.py with LLM configuration (API keys, model mappings, streaming settings)
- [X] T003 [P] Create backend/.env.example with OPENAI_API_KEY, DEFAULT_LLM_MODEL, AVAILABLE_MODELS, STREAM_TIMEOUT, MAX_TOKENS, TEMPERATURE
- [X] T004 [P] Update backend/.gitignore to exclude .env file
- [X] T005 Install backend dependencies (pip install -r backend/requirements.txt)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create backend/src/schemas.py with ChatStreamRequest, HistoryMessage, StreamEvent schemas (Pydantic models)
- [X] T007 [P] Create backend/src/services/llm_service.py skeleton with LLMService class and model initialization
- [X] T008 [P] Create backend/src/api/routes/chat.py skeleton with streaming endpoint stub
- [X] T009 [P] Create frontend/src/services/streamingClient.js with StreamingClient class skeleton
- [X] T010 [P] Create frontend/src/state/useModelSelection.js with model selection state management
- [X] T011 Register chat router in backend/main.py (app.include_router(chat.router))
- [X] T012 [P] Update backend/tests/conftest.py with LLM mocks and fixtures
- [X] T013 [P] Implement LocalStorage schema migration v1.0.0 → v2.0.0 in frontend/src/storage/LocalStorageAdapter.js

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Send Message and Receive AI Response (Priority: P1) 🎯 MVP

**Goal**: User can send a message and receive a real-time streamed response from the selected AI model (GPT-5 or GPT-5 Codex), seeing words appear progressively.

**Independent Test**: Send any message to the chatbot and verify a streamed response appears in real-time from the currently selected LLM model.

### Tests for User Story 1 (TDD - Write FIRST, ensure FAIL)

- [ ] T014 [P] [US1] Contract test for /api/v1/chat/stream endpoint in backend/tests/contract/test_chat_streaming_contract.py
- [ ] T015 [P] [US1] Unit test for LLMService.stream_chat_response in backend/tests/unit/test_llm_service.py
- [ ] T016 [P] [US1] Unit test for StreamingClient.streamChat in frontend/tests/unit/streamingClient.test.js
- [ ] T017 [P] [US1] Integration test for streaming chat flow in backend/tests/integration/test_streaming_chat.py
- [ ] T018 [P] [US1] E2E test for sending message and receiving streamed response in frontend/tests/e2e/llm-integration.spec.js

### Implementation for User Story 1

#### Backend Implementation

- [ ] T019 [US1] Implement LLMService.stream_chat_response in backend/src/services/llm_service.py (LangChain ChatOpenAI streaming with SSE event generation)
- [ ] T020 [US1] Implement LLMService._classify_error in backend/src/services/llm_service.py (map exceptions to error codes)
- [ ] T021 [US1] Implement LLMService._get_user_friendly_message in backend/src/services/llm_service.py (user-friendly error messages)
- [ ] T022 [US1] Implement POST /api/v1/chat/stream endpoint in backend/src/api/routes/chat.py (request validation, call LLMService, return StreamingResponse)
- [ ] T023 [US1] Add request validation with Pydantic in backend/src/api/routes/chat.py (message length, conversationId pattern, model enum)
- [ ] T024 [US1] Add structured logging for LLM requests in backend/src/services/llm_service.py (log request start, chunks, completion, errors)

#### Frontend Implementation

- [ ] T025 [P] [US1] Implement StreamingClient.streamChat in frontend/src/services/streamingClient.js (fetch with ReadableStream, SSE parsing, event callbacks)
- [ ] T026 [P] [US1] Implement StreamingClient.stopStream in frontend/src/services/streamingClient.js (AbortController to cancel stream)
- [ ] T027 [US1] Extend useMessages composable in frontend/src/state/useMessages.js (add streaming state: isStreaming, messageId, partialText, controller)
- [ ] T028 [US1] Add sendStreamingMessage function to useMessages in frontend/src/state/useMessages.js (create user message, call StreamingClient, accumulate chunks, handle callbacks)
- [ ] T029 [US1] Extend ChatArea.vue in frontend/src/components/ChatArea.vue (render streaming messages with progressive text updates, visual streaming indicator)
- [ ] T030 [US1] Transform Send button to Stop button in InputArea.vue during streaming in frontend/src/components/InputArea.vue (toggle based on isStreaming state, wire Stop to stopStream)
- [ ] T031 [US1] Display "conversation interrupted by user" system message on stream interruption in frontend/src/components/ChatArea.vue

#### Error Handling

- [ ] T032 [US1] Extend useAppState composable in frontend/src/state/useAppState.js (add error state for status bar indicator: errorState, setError, clearError)
- [ ] T033 [US1] Display error state indicator in StatusBar.vue in frontend/src/components/StatusBar.vue (red/yellow indicator based on error type)
- [ ] T034 [US1] Display error messages in ChatArea.vue in frontend/src/components/ChatArea.vue (show user-friendly error messages in chat area when errors occur)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can send messages, receive streamed responses, interrupt streams, and see errors in both status bar and chat area.

---

## Phase 4: User Story 2 - Switch Between LLM Models (Priority: P2)

**Goal**: User can select different LLM models (GPT-5 or GPT-5 Codex) from the status bar, and subsequent messages are routed to the newly selected model.

**Independent Test**: Select a model from the status bar, send a message, verify it routes to the correct model, switch models, and confirm the next message routes to the new model.

### Tests for User Story 2 (TDD - Write FIRST, ensure FAIL)

- [ ] T035 [P] [US2] Unit test for ModelPicker component in frontend/tests/unit/ModelPicker.test.js
- [ ] T036 [P] [US2] Unit test for useModelSelection composable in frontend/tests/unit/useModelSelection.test.js
- [ ] T037 [P] [US2] Integration test for model switching flow in frontend/tests/integration/model-switching.test.js
- [ ] T038 [P] [US2] E2E test for model picker interaction in frontend/tests/e2e/model-picker.spec.js

### Implementation for User Story 2

- [ ] T039 [P] [US2] Create ModelPicker.vue component in frontend/src/components/ModelPicker.vue (dropdown with GPT-5 and GPT-5 Codex options, emit selection events)
- [ ] T040 [US2] Integrate ModelPicker into StatusBar.vue in frontend/src/components/StatusBar.vue (display current model, handle selection changes)
- [ ] T041 [US2] Wire selectedModel from useModelSelection to sendStreamingMessage in frontend/src/state/useMessages.js (pass selectedModel to StreamingClient)
- [ ] T042 [US2] Verify model routing in LLMService in backend/src/services/llm_service.py (ensure model parameter selects correct ChatOpenAI instance)
- [ ] T043 [US2] Add model persistence validation in frontend/src/state/useModelSelection.js (ensure saveModelSelection and loadModelSelection work across browser sessions)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can send messages, switch models, and see model changes persist.

---

## Phase 5: User Story 3 - Maintain Conversation Context (Priority: P3)

**Goal**: The system maintains conversation history and context, allowing the AI to reference previous messages and provide contextually relevant responses across multiple exchanges.

**Independent Test**: Have a multi-turn conversation where later messages reference earlier context, and verify the AI's responses demonstrate awareness of the conversation history.

### Tests for User Story 3 (TDD - Write FIRST, ensure FAIL)

- [ ] T044 [P] [US3] Unit test for conversation history management in backend/tests/unit/test_llm_service.py
- [ ] T045 [P] [US3] Integration test for multi-turn conversation flow in backend/tests/integration/test_conversation_context.py
- [ ] T046 [P] [US3] E2E test for conversation context awareness in frontend/tests/e2e/conversation-context.spec.js

### Implementation for User Story 3

#### Backend Implementation

- [ ] T047 [US3] Implement conversation history conversion in backend/src/services/llm_service.py (convert conversationHistory dicts to LangChain message objects: HumanMessage, AIMessage, SystemMessage)
- [ ] T048 [US3] Add conversation history to LangChain stream call in backend/src/services/llm_service.py (prepend history messages before current user message)
- [ ] T049 [US3] Add logging for conversation context in backend/src/services/llm_service.py (log history length, context window usage)

#### Frontend Implementation

- [ ] T050 [US3] Build conversationHistory array from current conversation messages in frontend/src/state/useMessages.js (map messages to {role, content} format)
- [ ] T051 [US3] Pass conversationHistory to StreamingClient in sendStreamingMessage in frontend/src/state/useMessages.js
- [ ] T052 [US3] Verify conversation persistence in LocalStorage in frontend/src/storage/LocalStorageAdapter.js (ensure messages persist and load correctly for context)

**Checkpoint**: All user stories should now be independently functional - users can have multi-turn conversations with full context awareness.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T053 [P] Create contract snapshots for streaming endpoint in tests/contract/snapshots/chat-streaming/
- [ ] T054 [P] Run all backend tests (pytest backend/tests/ -v --cov=backend/src --cov-report=term-missing)
- [ ] T055 [P] Run all frontend tests (npm --prefix frontend test)
- [ ] T056 [P] Run E2E tests (npm --prefix frontend run test:e2e)
- [ ] T057 [P] Update architecture.md with LLM integration layer, streaming SSE pattern, LangChain provider abstraction
- [ ] T058 [P] Create ADR for LLM library choice (LangChain vs OpenAI SDK) in docs/architecture/decisions/
- [ ] T059 [P] Validate quickstart.md examples work end-to-end in specs/005-llm-integration/quickstart.md
- [ ] T060 [P] Code cleanup and remove debug logging from backend/src/services/llm_service.py and frontend/src/services/streamingClient.js
- [ ] T061 [P] Security audit: verify API key not logged, error messages don't leak sensitive data
- [ ] T062 Run full integration test suite (backend + frontend together)
- [ ] T063 Manual smoke test: send message, switch models, interrupt stream, trigger errors

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable

### Within Each User Story

1. Tests MUST be written and FAIL before implementation (TDD)
2. Backend implementation before frontend integration
3. Core streaming before error handling
4. Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1**: All tasks marked [P] can run in parallel
- **Phase 2**: All tasks marked [P] can run in parallel (within Phase 2)
- **Within User Stories**: All test tasks marked [P] can run in parallel, all implementation tasks marked [P] can run in parallel
- **Across User Stories**: Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD):
Task: "Contract test for /api/v1/chat/stream in backend/tests/contract/test_chat_streaming_contract.py"
Task: "Unit test for LLMService.stream_chat_response in backend/tests/unit/test_llm_service.py"
Task: "Unit test for StreamingClient.streamChat in frontend/tests/unit/streamingClient.test.js"
Task: "Integration test for streaming chat flow in backend/tests/integration/test_streaming_chat.py"
Task: "E2E test for sending message in frontend/tests/e2e/llm-integration.spec.js"

# Launch parallelizable implementation tasks together:
Task: "Implement StreamingClient.streamChat in frontend/src/services/streamingClient.js"
Task: "Implement StreamingClient.stopStream in frontend/src/services/streamingClient.js"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T013) - CRITICAL checkpoint
3. Complete Phase 3: User Story 1 (T014-T034)
4. **STOP and VALIDATE**: Test User Story 1 independently - send messages, receive streams, interrupt streams, trigger errors
5. Deploy/demo MVP if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T013)
2. Add User Story 1 → Test independently → Deploy/Demo (T014-T034) - **MVP!**
3. Add User Story 2 → Test independently → Deploy/Demo (T035-T043)
4. Add User Story 3 → Test independently → Deploy/Demo (T044-T052)
5. Complete Polish → Final validation → Production ready (T053-T063)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T013)
2. Once Foundational is done:
   - Developer A: User Story 1 (T014-T034)
   - Developer B: User Story 2 (T035-T043) - can start in parallel if desired
   - Developer C: User Story 3 (T044-T052) - can start in parallel if desired
3. Stories complete and integrate independently
4. Team converges on Polish phase (T053-T063)

---

## Success Criteria Validation

**After completing all tasks, verify**:

- ✅ **SC-001**: First word appears within 3 seconds of sending message
- ✅ **SC-002**: Response text streams progressively, not all at once
- ✅ **SC-003**: Model switching works in 2 clicks or less
- ✅ **SC-004**: Model selection persists across browser sessions 100% of the time
- ✅ **SC-005**: 95% of messages receive complete responses without errors (normal conditions)
- ✅ **SC-006**: Errors show feedback within 5 seconds in both status bar and chat area
- ✅ **SC-007**: Multi-turn conversations maintain context for at least 5 exchanges
- ✅ **SC-008**: Send → Stop button transition within 1 second
- ✅ **SC-009**: Stop button halts stream within 500ms, shows interruption message
- ✅ **SC-010**: Stream interruptions don't crash, preserve all messages sent/received

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD Workflow**: Write failing tests → implement → verify tests pass
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- LangChain chosen to support imminent multi-provider, RAG, and MCP features (see research.md)
- Contract tests follow existing pattern with snapshots in tests/contract/snapshots/
- All tasks follow constitution principles: API-first, modular, test-first, contract testing, observability
