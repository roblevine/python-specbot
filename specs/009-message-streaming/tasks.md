# Implementation Tasks: Message Streaming for Real-Time LLM Responses

**Feature**: 009-message-streaming
**Branch**: `009-message-streaming`
**Generated**: 2026-01-13
**Implementation Approach**: Test-Driven Development (TDD) with thin vertical slices

## Overview

This document breaks down the message streaming feature into atomic, executable tasks organized by user story priority. Each user story represents an independently testable slice that delivers value.

**Constitutional Requirements**:
- ✅ Test-First Development (NON-NEGOTIABLE): Tests written before implementation
- ✅ Thin Vertical Slices: Each user story is independently testable and deployable
- ✅ Incremental Delivery: MVP (User Story 1) delivers core value, subsequent stories enhance

**Technology Stack**:
- Backend: Python 3.13, FastAPI 0.115.0, LangChain, langchain-openai, Pydantic 2.10.0, pytest
- Frontend: JavaScript ES6+, Vue 3.4.0 (Composition API), Vite 5.0.0, Vitest, Playwright
- Protocol: Server-Sent Events (SSE) via EventSource API

---

## Task Summary

| Phase | Story | Task Count | Parallel Tasks | Status |
|-------|-------|------------|----------------|--------|
| Setup | - | 2 | 0 | Pending |
| Foundational | - | 3 | 0 | Pending |
| User Story 1 (P1) | Real-Time Response Streaming | 20 | 8 | Pending |
| User Story 2 (P2) | Streaming Status Indicators | 8 | 4 | Pending |
| User Story 3 (P3) | Handling Streaming Interruptions | 10 | 4 | Pending |
| Polish & Documentation | - | 3 | 2 | Pending |
| **Total** | **3 stories** | **46 tasks** | **18 parallel** | **Pending** |

---

## Implementation Strategy

### MVP Scope (Recommended First Deployment)
**User Story 1 (P1) Only** - Real-Time Response Streaming
- Delivers core streaming functionality
- Independently testable and demonstrable
- Provides immediate user value (perceived performance improvement)
- **Demo**: Send message → see response stream token-by-token

### Incremental Enhancements
- **+User Story 2 (P2)**: Adds visual indicators (streaming status, cursor animation)
- **+User Story 3 (P3)**: Adds robust error handling and partial response preservation

### Success Criteria per Story
- **US1**: Users see first token within 1s, smooth token-by-token display, completed messages saved
- **US2**: Users see streaming indicator during generation, clear state transitions
- **US3**: Partial responses preserved on errors, error messages displayed, retry available

---

## Phase 1: Setup

**Goal**: Prepare development environment and review design artifacts

**Tasks**:

- [x] T001 Review feature specification in specs/009-message-streaming/spec.md
  - Understand 3 user stories with priorities (P1, P2, P3)
  - Note acceptance scenarios for each story
  - Identify success criteria (first token <1s, 95% success rate)

- [x] T002 Review technical design documents in specs/009-message-streaming/
  - Read plan.md for technical approach (SSE, LangChain astream, EventSource)
  - Read data-model.md for entities (StreamingMessage, StreamEvent, StreamingState)
  - Read contracts/streaming-api.yaml for API specification
  - Read research.md for implementation patterns and best practices
  - Read quickstart.md for testing approach

---

## Phase 2: Foundational Tasks

**Goal**: Set up testing infrastructure and shared utilities (blocking prerequisites for all user stories)

**Prerequisites**: Phase 1 complete

**Tasks**:

- [x] T003 Verify pytest configuration supports async tests in backend/pytest.ini
  - Confirm pytest-asyncio plugin installed
  - Add async test markers if needed
  - Document async test conventions

- [x] T004 Verify Vitest configuration supports async tests in frontend/vitest.config.js
  - Confirm async test support enabled
  - Add EventSource mock utilities if needed
  - Document frontend test conventions

- [x] T005 Review existing test utilities in backend/tests/ and frontend/tests/
  - Identify reusable fixtures (API client, mock responses)
  - Document test helper functions
  - Plan SSE test mocking strategy

---

## Phase 3: User Story 1 (P1) - Real-Time Response Streaming

**Story Goal**: Users see LLM responses stream token-by-token in real-time

**Independent Test**: Send any message and observe that the response appears progressively as tokens are generated, with first token visible within 1-2 seconds.

**Success Criteria**:
- ✅ First token visible within 1 second
- ✅ Each token appears immediately (<100ms after receipt)
- ✅ Completed messages saved to conversation history
- ✅ Message ordering maintained during streaming

**Prerequisites**: Phase 2 complete

### Backend - Streaming Event Schemas (Test-First)

- [x] T006 [P] [US1] Write tests for StreamEvent schemas in backend/tests/unit/test_streaming_schemas.py
  - Test TokenEvent validation (type="token", content required)
  - Test CompleteEvent validation (type="complete", model field)
  - Test ErrorEvent validation (type="error", error+code required)
  - Test SSE JSON serialization format
  - **Result**: 18 tests created, all FAILED as expected

- [x] T007 [P] [US1] Implement StreamEvent schemas in backend/src/schemas.py
  - Add TokenEvent(BaseModel) with type and content fields
  - Add CompleteEvent(BaseModel) with type, model, totalTokens fields
  - Add ErrorEvent(BaseModel) with type, error, code fields
  - Add SSE serialization helper: to_sse_format()
  - **Result**: All 18 tests PASS

### Backend - LLM Streaming Service (Test-First)

- [x] T008 [P] [US1] Write tests for stream_ai_response() in backend/tests/unit/test_llm_service.py
  - Test async generator yields token chunks
  - Test LangChain astream integration with mock
  - Test conversation history passed correctly
  - Test model selection (default + custom)
  - Test empty response handling
  - **Result**: 9 tests created, all FAILED as expected (ImportError: function doesn't exist)

- [x] T009 [US1] Implement stream_ai_response() in backend/src/services/llm_service.py
  - Create async generator function using LangChain astream()
  - Convert AIMessageChunk to token strings
  - Filter empty chunks
  - Handle conversation history (same as existing get_ai_response)
  - Support model parameter
  - **Result**: All 9 tests PASS

- [ ] T010 [US1] Add streaming logging to backend/src/utils/logger.py
  - Add log_stream_start(message_id, model) function
  - Add log_stream_token(message_id, token_count) function
  - Add log_stream_complete(message_id, duration, total_tokens) function
  - Use existing structured logging format
  - **Expected**: Logging functions available for streaming routes

### Backend - Streaming API Endpoint (Test-First)

- [ ] T011 [US1] Write contract tests for streaming endpoint in backend/tests/contract/test_message_api_contract.py
  - Test POST /api/v1/messages with Accept: text/event-stream header
  - Test SSE event sequence: multiple tokens → complete
  - Test SSE format: "data: {...}\n\n" structure
  - Test backward compatibility (Accept: application/json still works)
  - Capture SSE stream snapshot for regression testing
  - **Expected**: Tests FAIL (streaming not implemented yet)

- [ ] T012 [US1] Implement streaming support in backend/src/api/routes/messages.py
  - Check Accept header (text/event-stream vs application/json)
  - If streaming: Return StreamingResponse with event generator
  - If not streaming: Keep existing synchronous behavior
  - Event generator: call stream_ai_response(), yield SSE events
  - Set SSE headers: Content-Type, Cache-Control, Connection, X-Accel-Buffering
  - Handle request validation (reuse existing MessageRequest schema)
  - **Expected**: Contract tests PASS

- [ ] T013 [US1] Write integration tests for backend streaming in backend/tests/integration/test_streaming_flow.py
  - Test end-to-end streaming: request → LLM → SSE response
  - Test with conversation history (context preserved)
  - Test with custom model selection
  - Test concurrent streams (at least 10 simultaneous)
  - Measure performance: first token latency, throughput
  - **Expected**: Integration tests PASS, <1s first token latency

### Frontend - Streaming API Client (Test-First)

- [ ] T014 [P] [US1] Write tests for streamMessage() in frontend/tests/unit/apiClient.spec.js
  - Test EventSource creation with correct URL and headers
  - Test token event handling (call onToken callback)
  - Test complete event handling (call onComplete callback)
  - Test connection close on complete
  - Mock EventSource API
  - **Expected**: Tests FAIL (function doesn't exist yet)

- [ ] T015 [P] [US1] Implement streamMessage() in frontend/src/services/apiClient.js
  - Create EventSource with POST /api/v1/messages URL
  - Note: EventSource GET only - workaround via URL params or use fetch with ReadableStream
  - Use fetch() with ReadableStream for POST support (EventSource limitation)
  - Parse SSE format: "data: {...}\n\n"
  - Handle token events → call onToken(content)
  - Handle complete events → call onComplete(metadata)
  - Return cleanup function to close connection
  - **Expected**: Tests PASS

- [ ] T016 [US1] Add streaming logging to frontend/src/utils/logger.js
  - Add logStreamStart(messageText) function
  - Add logTokenReceived(tokenCount) function
  - Add logStreamComplete(duration, totalTokens) function
  - Use existing console logging utilities
  - **Expected**: Logging available for streaming state

### Frontend - Streaming State Management (Test-First)

- [ ] T017 [P] [US1] Write tests for streaming state in frontend/tests/unit/useMessages.spec.js
  - Test startStreaming(messageId) - creates streamingMessage
  - Test appendToken(token) - accumulates text
  - Test completeStreaming() - moves to messages array
  - Test isStreaming flag transitions
  - Test EventSource cleanup on complete
  - **Expected**: Tests FAIL (streaming state doesn't exist yet)

- [ ] T018 [P] [US1] Add streaming state to frontend/src/state/useMessages.js
  - Add streamingMessage ref (null | StreamingMessage)
  - Add isStreaming ref (boolean)
  - Add eventSource ref (null | EventSource/ReadableStream)
  - Add startStreaming(messageId, model) function
  - Add appendToken(token) function (concatenate to streamingMessage.text)
  - Add completeStreaming() function (move to messages, save to localStorage)
  - Integrate with existing sendMessage() function
  - **Expected**: Tests PASS

### Frontend - UI Components (Test-First)

- [ ] T019 [P] [US1] Write tests for streaming message display in frontend/tests/unit/MessageBubble.spec.js
  - Test displays streamingMessage when streaming=true
  - Test text updates reactively as tokens append
  - Test shows completed message when streaming=false
  - **Expected**: Tests FAIL (streaming support doesn't exist yet)

- [ ] T020 [P] [US1] Update MessageBubble in frontend/src/components/ChatArea/MessageBubble.vue
  - Accept streaming prop (boolean)
  - Render message.text reactively (updates on each token)
  - Apply streaming-specific CSS class when streaming=true
  - **Expected**: Tests PASS, tokens appear progressively

- [ ] T021 [US1] Update ChatArea in frontend/src/components/ChatArea/ChatArea.vue
  - Display streamingMessage from useMessages composable
  - Show streamingMessage below regular messages
  - Implement auto-scroll: watch streamingMessage.text, scroll to bottom on change
  - Use nextTick() for DOM update before scrolling
  - **Expected**: Chat scrolls to show latest tokens

- [ ] T022 [US1] Write integration test for frontend streaming in frontend/tests/integration/streaming-flow.test.js
  - Mock SSE stream with multiple token events
  - Test message sending triggers streaming
  - Test tokens accumulate in UI
  - Test completed message saved and displayed
  - Test auto-scroll behavior
  - **Expected**: Integration tests PASS

### End-to-End Testing

- [ ] T023 [US1] Write e2e test for streaming flow in frontend/tests/e2e/streaming-e2e.test.js
  - Start backend server (or use test server)
  - Open browser with Playwright
  - Send message via UI
  - Wait for first token (within 1s)
  - Verify tokens appear progressively
  - Verify completed message in conversation history
  - Measure end-to-end latency
  - **Expected**: E2E test PASS, <1s first token

- [ ] T024 [US1] Manual testing using quickstart.md guide
  - Follow curl commands to test SSE endpoint
  - Test via browser UI
  - Verify DevTools Network tab shows EventSource
  - Check console logs for streaming events
  - Validate against acceptance scenarios in spec.md
  - **Expected**: All acceptance scenarios PASS

- [ ] T025 [US1] Update architecture.md with streaming data flow
  - Add SSE streaming endpoint to API Routes Layer section
  - Update data flow diagram: synchronous + streaming paths
  - Document EventSource usage in frontend API Client
  - Add streaming state management to State Management section
  - Add ADR for SSE over WebSockets choice
  - **Expected**: Architecture doc reflects streaming implementation

**User Story 1 Complete**: ✅ MVP ready for deployment - users can see real-time streaming responses

---

## Phase 4: User Story 2 (P2) - Streaming Status Indicators

**Story Goal**: Users clearly see when a response is streaming vs complete

**Independent Test**: Observe visual indicators during streaming (animated cursor, "generating" label) and confirm they disappear when streaming completes.

**Success Criteria**:
- ✅ Streaming indicator visible during active streaming
- ✅ Indicator removed on completion
- ✅ Error indicator shown on streaming failure
- ✅ Users can distinguish states within 1 second

**Prerequisites**: User Story 1 (Phase 3) complete

### Frontend - Streaming Indicators (Test-First)

- [ ] T026 [P] [US2] Write tests for streaming indicator in frontend/tests/unit/MessageBubble.spec.js
  - Test animated cursor (▊) appears when streaming=true
  - Test cursor removed when streaming=false
  - Test CSS animation applied to cursor
  - **Expected**: Tests FAIL (indicator doesn't exist yet)

- [ ] T027 [P] [US2] Add streaming indicator to frontend/src/components/ChatArea/MessageBubble.vue
  - Add <span class="cursor">▊</span> after message text when streaming=true
  - Add CSS animation for cursor blink/pulse
  - Style streaming message differently (e.g., lighter opacity)
  - **Expected**: Tests PASS, visual indicator visible

- [ ] T028 [P] [US2] Write tests for status bar streaming state in frontend/tests/unit/StatusBar.spec.js
  - Test shows "Streaming..." text when isStreaming=true
  - Test shows "Ready" when isStreaming=false
  - Test shows streaming icon/animation
  - **Expected**: Tests FAIL (streaming status doesn't exist yet)

- [ ] T029 [US2] Update StatusBar in frontend/src/components/StatusBar/StatusBar.vue
  - Import isStreaming from useAppState
  - Display "Streaming..." text when isStreaming=true
  - Add streaming animation icon (e.g., spinning dots)
  - Revert to "Ready" when isStreaming=false
  - **Expected**: Tests PASS, status bar reflects streaming state

- [ ] T030 [P] [US2] Add streaming status to frontend/src/state/useAppState.js
  - Add isStreaming computed property (derived from useMessages)
  - Expose globally for StatusBar component
  - **Expected**: Status bar can access streaming state

### Frontend - Input Disabling (Test-First)

- [ ] T031 [US2] Write tests for input disabling in frontend/tests/unit/InputArea.spec.js
  - Test input disabled when isStreaming=true
  - Test send button disabled when isStreaming=true
  - Test input enabled when isStreaming=false
  - **Expected**: Tests FAIL (input disabling doesn't exist yet)

- [ ] T032 [US2] Update InputArea in frontend/src/components/InputArea/InputArea.vue
  - Import isStreaming from useMessages
  - Bind :disabled="isStreaming" to input field
  - Bind :disabled="isStreaming" to send button
  - Show tooltip: "Wait for response to complete"
  - **Expected**: Tests PASS, input disabled during streaming

- [ ] T033 [US2] Manual testing of streaming indicators
  - Send message, verify "Streaming..." appears in status bar
  - Verify animated cursor appears in message bubble
  - Verify input field disabled during streaming
  - Verify all indicators removed on completion
  - **Expected**: All visual indicators work correctly

**User Story 2 Complete**: ✅ Users clearly see streaming status with visual indicators

---

## Phase 5: User Story 3 (P3) - Handling Streaming Interruptions

**Story Goal**: Users receive feedback and recovery options when streaming is interrupted

**Independent Test**: Simulate network interruptions or errors during streaming and verify appropriate error messages and partial response preservation.

**Success Criteria**:
- ✅ Partial responses preserved in 100% of interruption cases
- ✅ Error messages displayed to users
- ✅ Users can retry or continue conversation after errors
- ✅ Error states distinguishable within 1 second

**Prerequisites**: User Story 2 (Phase 4) complete

### Backend - Error Handling (Test-First)

- [ ] T034 [P] [US3] Write tests for streaming error events in backend/tests/unit/test_llm_service.py
  - Test LLM timeout → ErrorEvent with code=TIMEOUT
  - Test rate limit error → ErrorEvent with code=RATE_LIMIT
  - Test authentication error → ErrorEvent with code=AUTH_ERROR
  - Test generic error → ErrorEvent with code=LLM_ERROR
  - Test error event sent before stream close
  - **Expected**: Tests FAIL (error handling doesn't exist yet)

- [ ] T035 [P] [US3] Add error handling to backend/src/services/llm_service.py
  - Wrap astream() in try/except block
  - Catch LangChain exceptions: APIError, RateLimitError, AuthenticationError
  - Yield ErrorEvent before closing generator
  - Log errors with correlation ID
  - **Expected**: Tests PASS, errors sent as SSE events

- [ ] T036 [US3] Update streaming endpoint error handling in backend/src/api/routes/messages.py
  - Ensure event generator catches all exceptions
  - Send error event before closing SSE stream
  - Log errors with request context
  - Don't leak sensitive error details to client
  - **Expected**: Errors gracefully sent to frontend

- [ ] T037 [US3] Write contract tests for error scenarios in backend/tests/contract/test_message_api_contract.py
  - Test streaming with simulated LLM timeout
  - Test SSE error event format
  - Test partial tokens + error event sequence
  - Capture error stream snapshot
  - **Expected**: Error contract tests PASS

### Frontend - Error Handling (Test-First)

- [ ] T038 [P] [US3] Write tests for error event handling in frontend/tests/unit/apiClient.spec.js
  - Test error event → call onError callback
  - Test connection close on error
  - Test partial content preserved before error
  - Mock error events in SSE stream
  - **Expected**: Tests FAIL (error handling doesn't exist yet)

- [ ] T039 [P] [US3] Add error handling to frontend/src/services/apiClient.js
  - Handle error events → call onError(errorMessage, errorCode)
  - Close EventSource/stream on error
  - Log error events
  - **Expected**: Tests PASS

- [ ] T040 [US3] Write tests for partial response preservation in frontend/tests/unit/useMessages.spec.js
  - Test interruptStreaming(error) - sets incomplete=true
  - Test partial streamingMessage moved to messages array
  - Test error message stored in message object
  - **Expected**: Tests FAIL (error state doesn't exist yet)

- [ ] T041 [US3] Add error state to frontend/src/state/useMessages.js
  - Add interruptStreaming(error) function
  - Set streamingMessage.streaming = false
  - Set streamingMessage.incomplete = true
  - Set streamingMessage.error = error message
  - Move to messages array (preserve partial content)
  - Close EventSource
  - **Expected**: Tests PASS, partial responses preserved

- [ ] T042 [US3] Update MessageBubble for error display in frontend/src/components/ChatArea/MessageBubble.vue
  - Show error icon/badge when message.incomplete=true
  - Display error message tooltip or inline
  - Style incomplete messages differently (e.g., red border)
  - Show "Partial response - connection interrupted" message
  - **Expected**: Error states visible to users

- [ ] T043 [US3] Manual testing of error scenarios
  - Simulate network interruption (DevTools offline mode)
  - Verify partial response preserved and displayed
  - Verify error message shown
  - Test retry by sending new message
  - Test with different error types (timeout, rate limit)
  - **Expected**: All error scenarios handled gracefully

**User Story 3 Complete**: ✅ Robust error handling with partial response preservation

---

## Phase 6: Polish & Documentation

**Goal**: Finalize implementation, update documentation, ensure production readiness

**Prerequisites**: All user stories complete

**Tasks**:

- [ ] T044 [P] Update CLAUDE.md with streaming implementation notes
  - Add streaming endpoints to Recent Changes section
  - Document SSE usage and EventSource patterns
  - Note any gotchas or best practices discovered
  - **Expected**: Agent context updated for future features

- [ ] T045 [P] Create release notes in specs/009-message-streaming/RELEASE.md
  - Summarize implemented user stories (US1, US2, US3)
  - List new endpoints and API changes
  - Document breaking changes (none expected)
  - Add migration guide for existing clients (none needed)
  - Include performance benchmarks (first token latency, throughput)
  - **Expected**: Clear release communication

- [ ] T046 Run full test suite and verify all tests pass
  - Backend: pytest backend/tests/ -v
  - Frontend: npm test in frontend/
  - E2E: playwright test in frontend/
  - Verify >95% streaming success rate
  - Verify <1s first token latency
  - **Expected**: All tests PASS, performance targets met

---

## Dependency Graph

### Story Completion Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (User Story 1 - P1) ← MVP Deployment Point
    ↓
Phase 4 (User Story 2 - P2)
    ↓
Phase 5 (User Story 3 - P3)
    ↓
Phase 6 (Polish)
```

### Story Dependencies

- **User Story 1 (P1)**: No dependencies (can implement first)
- **User Story 2 (P2)**: Depends on User Story 1 (needs streaming state)
- **User Story 3 (P3)**: Depends on User Story 2 (extends error states)

### Within-Story Dependencies

**User Story 1 (P1)**:
```
Backend Schemas (T006-T007)
    ↓
Backend Service (T008-T010) ← depends on schemas
    ↓
Backend Endpoint (T011-T013) ← depends on service
    ↓
Frontend Client (T014-T016) ← depends on backend endpoint
    ↓
Frontend State (T017-T018) ← depends on client
    ↓
Frontend UI (T019-T022) ← depends on state
    ↓
E2E Tests (T023-T025) ← depends on full stack
```

**Parallel Opportunities** (tasks with [P] marker can run simultaneously):
- Backend schemas, service, logging (T006-T010) - independent modules
- Frontend client, state, logging (T014-T018) - independent modules
- Frontend UI components (T019-T020) - different files
- User Story 2 indicators (T026-T030) - independent components

---

## Parallel Execution Examples

### User Story 1 - Parallelizable Tasks

**Backend Track** (can run in parallel):
```bash
# Developer A: Schemas
T006 → T007 (StreamEvent schemas + tests)

# Developer B: LLM Service
T008 → T009 → T010 (stream_ai_response + logging)

# Developer C: API Endpoint (after A+B complete)
T011 → T012 → T013 (streaming endpoint + tests)
```

**Frontend Track** (can run in parallel with backend):
```bash
# Developer D: API Client
T014 → T015 → T016 (streamMessage + logging)

# Developer E: State Management
T017 → T018 (streaming state)

# Developer F: UI Components (after D+E complete)
T019 → T020 → T021 (MessageBubble + ChatArea)
```

**Integration Track** (after both tracks complete):
```bash
# Developer G: End-to-End
T022 → T023 → T024 (integration + e2e + manual)
```

### User Story 2 - Parallelizable Tasks

```bash
# Can run in parallel:
T026 → T027 (MessageBubble indicator)
T028 → T029 → T030 (StatusBar + app state)
T031 → T032 (InputArea disabling)

# Then:
T033 (Manual testing after all complete)
```

---

## Testing Strategy

### Test-First Development (TDD) Workflow

For each feature task:
1. **Write test** (T0XX: Write tests for...)
   - Define expected behavior
   - Run test → verify it FAILS
   - Commit failing test
2. **Implement** (T0YY: Implement...)
   - Write minimal code to pass test
   - Run test → verify it PASSES
   - Commit implementation
3. **Refactor** (if needed)
   - Improve code quality
   - Verify tests still PASS

### Test Coverage Requirements

- **Unit Tests**: All new functions (stream_ai_response, appendToken, etc.)
- **Integration Tests**: Backend SSE flow, frontend streaming flow
- **Contract Tests**: SSE event format snapshots
- **E2E Tests**: Full user journey (send message → stream → save)
- **Target**: >80% code coverage for streaming modules

### Test Execution

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=src --cov-report=html

# Frontend tests
cd frontend
npm test -- --coverage

# E2E tests
cd frontend
npx playwright test
```

---

## Success Criteria Validation

After completing all tasks, verify:

- [ ] **SC-001**: First token visible within 1 second (measure with e2e tests)
- [ ] **SC-002**: Each token appears within 100ms of receipt (measure in integration tests)
- [ ] **SC-003**: Users perceive responses as "instant" (subjective feedback after demo)
- [ ] **SC-004**: System handles 100 concurrent streams (load test)
- [ ] **SC-005**: 95% streaming success rate (measure over 100 test runs)
- [ ] **SC-006**: Partial responses preserved in 100% of interruption cases (error tests)
- [ ] **SC-007**: State changes visible within 1 second (measure UI updates)

---

## Notes

### Task Format Conventions

All tasks follow strict checklist format:
```
- [ ] T### [P] [US#] Description with file path
```

Where:
- `T###`: Sequential task ID
- `[P]`: Optional parallelizable marker (different files, no dependencies)
- `[US#]`: User story label (US1, US2, US3) - required for story phases
- Description: Clear action with exact file path

### Estimated Effort

- **User Story 1 (P1)**: 20 tasks × ~30 min = ~10 hours (MVP)
- **User Story 2 (P2)**: 8 tasks × ~20 min = ~2.5 hours
- **User Story 3 (P3)**: 10 tasks × ~20 min = ~3.5 hours
- **Total**: 46 tasks × ~22 min avg = ~16-20 hours

With parallelization (3-4 developers):
- **User Story 1**: ~4-5 hours
- **User Story 2**: ~1 hour
- **User Story 3**: ~1.5 hours
- **Total**: ~6-8 hours

### Risk Mitigation

**Highest Risk Areas**:
1. SSE connection stability (browser limits, network issues)
   - Mitigation: Extensive integration tests, error handling
2. LangChain astream compatibility (API changes)
   - Mitigation: Version pinning, integration tests with real LLM
3. Performance (first token latency >1s)
   - Mitigation: Performance benchmarks in tests, monitoring

**Rollback Plan**:
- Streaming is opt-in via Accept header
- Existing synchronous API unchanged
- Can disable streaming by removing header check
- No data migration needed

---

**Task Generation Complete**: 46 tasks across 3 user stories, ready for TDD implementation
**MVP Ready After**: Phase 3 (User Story 1) - 25 tasks total
**Full Feature Complete After**: Phase 5 (User Story 3) - 43 tasks total
