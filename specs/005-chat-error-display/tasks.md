# Tasks: Chat Error Display

**Input**: Design documents from `/workspaces/python-specbot/specs/005-chat-error-display/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md, quickstart.md

**Tests**: This feature follows Test-Driven Development (TDD) as specified in the constitution (Principle III). All tests must be written FIRST and FAIL before implementation.

**Organization**: Tasks are grouped by user story (P1, P2, P3) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `frontend/src/`, `backend/src/`
- Frontend tests: `frontend/tests/unit/`, `frontend/tests/integration/`, `frontend/tests/e2e/`
- Backend: No changes required for this feature

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create file structure and initialize composables/utilities

**Note**: This is a frontend-only feature. Backend requires no changes.

- [ ] T001 Create sensitive data redactor utility skeleton in frontend/src/utils/sensitiveDataRedactor.js
- [ ] T002 Create collapsible composable skeleton in frontend/src/composables/useCollapsible.js
- [ ] T003 Create test file skeletons: frontend/tests/unit/sensitiveDataRedactor.test.js, frontend/tests/unit/useCollapsible.test.js
- [ ] T004 Add CSS variables for error styling to frontend/public/styles/global.css (--color-error-light, --color-error-background)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities and composables that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational (TDD - Write FIRST, Verify FAIL)

- [ ] T005 [P] Write failing unit tests for sensitiveDataRedactor.redactSensitiveData() in frontend/tests/unit/sensitiveDataRedactor.test.js
- [ ] T006 [P] Write failing unit tests for sensitiveDataRedactor.containsSensitiveData() in frontend/tests/unit/sensitiveDataRedactor.test.js
- [ ] T007 [P] Write failing unit tests for sensitiveDataRedactor.detectSensitivePatterns() in frontend/tests/unit/sensitiveDataRedactor.test.js
- [ ] T008 [P] Write failing unit tests for useCollapsible composable (toggle, expand, collapse, ARIA attrs) in frontend/tests/unit/useCollapsible.test.js
- [ ] T009 Verify all foundational tests FAIL (run npm test and confirm red state)

### Implementation for Foundational

- [ ] T010 [P] Implement SENSITIVE_PATTERNS array with 15+ regex patterns in frontend/src/utils/sensitiveDataRedactor.js
- [ ] T011 [P] Implement redactSensitiveData() function in frontend/src/utils/sensitiveDataRedactor.js
- [ ] T012 [P] Implement containsSensitiveData() function in frontend/src/utils/sensitiveDataRedactor.js
- [ ] T013 [P] Implement detectSensitivePatterns() function in frontend/src/utils/sensitiveDataRedactor.js
- [ ] T014 Implement useCollapsible composable with state management and ARIA attributes in frontend/src/composables/useCollapsible.js
- [ ] T015 Verify all foundational tests PASS (run npm test and confirm green state)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Display Client-Side Error in Chat (Priority: P1) 🎯 MVP

**Goal**: When client-side errors occur (network failure, CORS, timeout), users see clearly marked error messages in the chat interface

**Independent Test**: Simulate network failure or CORS error and verify error message appears in chat window, visually distinct from normal messages

### Tests for User Story 1 (TDD - Write FIRST, Verify FAIL)

- [ ] T016 [P] [US1] Write failing test: MessageBubble renders error section when status='error' in frontend/tests/unit/MessageBubble.test.js
- [ ] T017 [P] [US1] Write failing test: MessageBubble applies .message-error styling in frontend/tests/unit/MessageBubble.test.js
- [ ] T018 [P] [US1] Write failing test: MessageBubble does NOT render error section for non-error messages in frontend/tests/unit/MessageBubble.test.js
- [ ] T019 [P] [US1] Write failing test: useMessages creates error message on API failure in frontend/tests/unit/useMessages.test.js
- [ ] T020 [P] [US1] Write failing test: useMessages populates errorMessage, errorType, errorTimestamp fields in frontend/tests/unit/useMessages.test.js
- [ ] T021 [US1] Verify all US1 tests FAIL (run npm test MessageBubble.test.js useMessages.test.js)

### Implementation for User Story 1

- [ ] T022 [P] [US1] Extend Message schema validation in frontend/src/components/ChatArea/MessageBubble.vue to accept optional error fields
- [ ] T023 [US1] Add error section to MessageBubble template with error icon and summary in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T024 [US1] Add error section styles (.error-section, .error-summary, .error-icon, .error-message) in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T025 [US1] Add hasError computed property in MessageBubble setup() in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T026 [US1] Implement categorizeError() helper function in frontend/src/state/useMessages.js
- [ ] T027 [US1] Implement updateMessageWithError() helper in frontend/src/state/useMessages.js
- [ ] T028 [US1] Update sendUserMessage() catch block to populate error fields in frontend/src/state/useMessages.js
- [ ] T029 [US1] Verify all US1 tests PASS (run npm test and confirm green state)

**Checkpoint**: At this point, User Story 1 should be fully functional - client-side errors display in chat with visual distinction

---

## Phase 4: User Story 2 - Display Server-Side Error in Chat (Priority: P2)

**Goal**: When server returns error responses (400, 422, 500 series), users see the server's error message displayed in the chat interface

**Independent Test**: Trigger server validation error (e.g., send empty message) and verify server's error response appears in chat window

### Tests for User Story 2 (TDD - Write FIRST, Verify FAIL)

- [ ] T030 [P] [US2] Write failing integration test: 422 validation error displays in chat in frontend/tests/integration/errorDisplay.test.js
- [ ] T031 [P] [US2] Write failing integration test: 500 server error displays in chat in frontend/tests/integration/errorDisplay.test.js
- [ ] T032 [P] [US2] Write failing integration test: 400 bad request displays in chat in frontend/tests/integration/errorDisplay.test.js
- [ ] T033 [P] [US2] Write failing test: apiClient.ApiError includes statusCode and details properties in frontend/tests/unit/apiClient.test.js
- [ ] T034 [US2] Verify all US2 tests FAIL (run npm test errorDisplay.test.js apiClient.test.js)

### Implementation for User Story 2

- [ ] T035 [US2] Enhance ApiError class to ensure statusCode and details are always populated in frontend/src/services/apiClient.js
- [ ] T036 [US2] Update sendMessage() to extract error message and details from server response JSON in frontend/src/services/apiClient.js
- [ ] T037 [US2] Update sendMessage() to throw ApiError with correct statusCode for 400/422/500 responses in frontend/src/services/apiClient.js
- [ ] T038 [US2] Update categorizeError() to correctly map 400/422 to Validation Error, 500+ to Server Error in frontend/src/state/useMessages.js
- [ ] T039 [US2] Update updateMessageWithError() to include errorCode field from ApiError.statusCode in frontend/src/state/useMessages.js
- [ ] T040 [US2] Verify all US2 tests PASS (run npm test and confirm green state)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - client and server errors display in chat

---

## Phase 5: User Story 3 - View Full Error Details (Priority: P3)

**Goal**: Users can expand error messages to see technical details (error codes, stack traces, timestamps) with sensitive data redacted by default

**Independent Test**: Trigger any error, click to expand it, verify additional technical details appear with sensitive data redacted

### Tests for User Story 3 (TDD - Write FIRST, Verify FAIL)

- [ ] T041 [P] [US3] Write failing test: MessageBubble renders Details button when errorDetails present in frontend/tests/unit/MessageBubble.test.js
- [ ] T042 [P] [US3] Write failing test: Clicking Details button expands error details section in frontend/tests/unit/MessageBubble.test.js
- [ ] T043 [P] [US3] Write failing test: Clicking Details button again collapses error details in frontend/tests/unit/MessageBubble.test.js
- [ ] T044 [P] [US3] Write failing test: Expanded error details display errorType, errorCode, redacted errorDetails in frontend/tests/unit/MessageBubble.test.js
- [ ] T045 [P] [US3] Write failing test: Error details are redacted by default (sensitive data hidden) in frontend/tests/unit/MessageBubble.test.js
- [ ] T046 [P] [US3] Write failing test: Keyboard navigation (Enter/Space) works on Details button in frontend/tests/unit/MessageBubble.test.js
- [ ] T047 [US3] Verify all US3 tests FAIL (run npm test MessageBubble.test.js)

### Implementation for User Story 3

- [ ] T048 [US3] Import useCollapsible composable in MessageBubble.vue setup() in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T049 [US3] Import redactSensitiveData from sensitiveDataRedactor in MessageBubble.vue in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T050 [US3] Add errorCollapsible instance with useCollapsible(false) in MessageBubble setup() in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T051 [US3] Add hasErrorDetails computed property in MessageBubble setup() in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T052 [US3] Add redactedErrorDetails computed property using redactSensitiveData() in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T053 [US3] Add Details toggle button to error section template with errorCollapsible.triggerAttrs in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T054 [US3] Add expandable error details section with <transition name="expand"> in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T055 [US3] Add error details content showing errorType, errorCode, redactedErrorDetails in <pre> tag in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T056 [US3] Add styles for .error-toggle button (border, hover, focus states) in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T057 [US3] Add styles for .error-details section (background, border, padding) in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T058 [US3] Add styles for .error-stack <pre> tag (monospace font, max-height, scrollbar) in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T059 [US3] Add .expand-enter-active/.expand-leave-active transition styles in frontend/src/components/ChatArea/MessageBubble.vue
- [ ] T060 [US3] Update updateMessageWithError() to populate errorDetails field with JSON.stringify(error.details) in frontend/src/state/useMessages.js
- [ ] T061 [US3] Verify all US3 tests PASS (run npm test and confirm green state)

**Checkpoint**: All user stories should now be independently functional - errors display, expand, and redact sensitive data

---

## Phase 6: End-to-End Testing & Edge Cases

**Purpose**: E2E validation and edge case coverage

### E2E Tests (Playwright)

- [ ] T062 [P] Write E2E test: Simulate network failure, verify error appears in chat in frontend/tests/e2e/error-scenarios.spec.js
- [ ] T063 [P] Write E2E test: Stop backend, send message, verify "Cannot connect to server" error in frontend/tests/e2e/error-scenarios.spec.js
- [ ] T064 [P] Write E2E test: Send empty message, verify 422 validation error displays in frontend/tests/e2e/error-scenarios.spec.js
- [ ] T065 [P] Write E2E test: Click Details button, verify error expands with technical details in frontend/tests/e2e/error-scenarios.spec.js
- [ ] T066 [P] Write E2E test: Verify keyboard navigation (Tab, Enter, Space) works on Details button in frontend/tests/e2e/error-scenarios.spec.js
- [ ] T067 Write E2E test: Verify error with API key shows redacted version by default in frontend/tests/e2e/error-scenarios.spec.js

### Edge Case Implementation

- [ ] T068 Add max-height and overflow handling for extremely long error messages (>10,000 chars) in MessageBubble.vue styles
- [ ] T069 Add word-break and white-space handling for error details with long tokens/URLs in MessageBubble.vue styles
- [ ] T070 Test multiple rapid errors in succession and verify all display in chronological order
- [ ] T071 Test error that occurs before chat interface fully loads and verify it displays correctly

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect the overall feature quality

- [ ] T072 [P] Update architecture.md with error display component architecture (if file exists)
- [ ] T073 [P] Add accessibility tests: verify ARIA attributes with axe DevTools
- [ ] T074 [P] Add accessibility tests: verify screen reader compatibility (aria-live, role attributes)
- [ ] T075 [P] Test color contrast ratios meet WCAG AA standards (4.5:1 minimum)
- [ ] T076 Run full test suite: npm test (unit + integration + E2E) and ensure 100% pass rate
- [ ] T077 Manual testing: Test all three user stories in browser with network throttling
- [ ] T078 Manual testing: Test with backend stopped, verify client errors display correctly
- [ ] T079 Manual testing: Test with invalid messages, verify server validation errors display
- [ ] T080 Manual testing: Test expand/collapse behavior with keyboard only (no mouse)
- [ ] T081 Code review: Ensure no XSS vulnerabilities (all error content in text nodes, not v-html)
- [ ] T082 Performance check: Verify error display happens within 2 seconds (SC-001)
- [ ] T083 Performance check: Verify layout stability for 10,000 character errors (SC-004)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Can start once T015 complete
- **User Story 2 (Phase 4)**: Depends on Foundational - Can start once T015 complete (can run parallel with US1)
- **User Story 3 (Phase 5)**: Depends on Foundational AND User Story 1 - Requires US1 complete (T029)
- **E2E Testing (Phase 6)**: Depends on all desired user stories being complete
- **Polish (Phase 7)**: Depends on all user stories and E2E tests complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends ONLY on Foundational (T015) - No dependencies on other stories
- **User Story 2 (P2)**: Depends ONLY on Foundational (T015) - Can run in parallel with US1
- **User Story 3 (P3)**: Depends on Foundational (T015) AND User Story 1 complete (T029) - Extends US1's error display

### Within Each User Story (TDD Workflow)

1. Write ALL tests for the story and verify they FAIL
2. Implement functionality to make tests PASS
3. Refactor while keeping tests green
4. Verify story is independently testable
5. Commit completed story before moving to next

### Parallel Opportunities

- **Setup (Phase 1)**: T001, T002, T003 can run in parallel (different files)
- **Foundational Tests**: T005, T006, T007, T008 can run in parallel (different test files)
- **Foundational Implementation**: T010, T011, T012, T013 can run in parallel (same file, different functions)
- **US1 Tests**: T016, T017, T018, T019, T020 can run in parallel (different test files/functions)
- **US1 Implementation**: T022, T026, T027 can run in parallel (different files)
- **US2 Tests**: T030, T031, T032, T033 can run in parallel (different test files)
- **US3 Tests**: T041-T046 can run in parallel (different test functions)
- **E2E Tests**: T062-T067 can run in parallel (independent test scenarios)
- **Polish Tasks**: T072, T073, T074, T075 can run in parallel (different concerns)
- **User Stories**: US1 (Phase 3) and US2 (Phase 4) can run in parallel once Foundational complete

---

## Parallel Example: User Story 1

```bash
# Step 1: Launch all US1 tests together (write tests first):
Task: "T016 [P] [US1] Write failing test: MessageBubble renders error section"
Task: "T017 [P] [US1] Write failing test: MessageBubble applies error styling"
Task: "T018 [P] [US1] Write failing test: MessageBubble no error for normal messages"
Task: "T019 [P] [US1] Write failing test: useMessages creates error message"
Task: "T020 [P] [US1] Write failing test: useMessages populates error fields"

# Step 2: Verify all tests FAIL
Task: "T021 [US1] Verify all US1 tests FAIL"

# Step 3: Launch parallel implementation tasks:
Task: "T022 [P] [US1] Extend Message schema validation in MessageBubble.vue"
Task: "T026 [US1] Implement categorizeError() in useMessages.js"
Task: "T027 [US1] Implement updateMessageWithError() in useMessages.js"

# Step 4: Sequential dependent tasks:
Task: "T023-T025 [US1] Add error section to MessageBubble (depends on T022)"
Task: "T028 [US1] Update sendUserMessage() catch (depends on T026, T027)"

# Step 5: Verify all tests PASS
Task: "T029 [US1] Verify all US1 tests PASS"
```

---

## Parallel Example: User Story 2 & User Story 1 (Concurrent)

```bash
# Two developers can work simultaneously:

# Developer A: User Story 1
Phase 3 tasks (T016-T029)

# Developer B: User Story 2
Phase 4 tasks (T030-T040)

# Both start after Foundational (T015) complete
# Both are independently testable
# Both can be committed separately
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T015) - **CRITICAL**
3. Complete Phase 3: User Story 1 (T016-T029)
4. **STOP and VALIDATE**: Manual test client errors appear in chat
5. Deploy/demo MVP if ready

**MVP Scope**: Just User Story 1 = Client-side errors display in chat with visual distinction

### Incremental Delivery

1. Setup + Foundational → Foundation ready (T001-T015)
2. Add User Story 1 → Test independently → Deploy/Demo (T016-T029) **MVP!**
3. Add User Story 2 → Test independently → Deploy/Demo (T030-T040)
4. Add User Story 3 → Test independently → Deploy/Demo (T041-T061)
5. Add E2E tests → Validate end-to-end (T062-T071)
6. Polish → Production ready (T072-T083)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T015)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T016-T029)
   - **Developer B**: User Story 2 (T030-T040)
   - **Developer C**: Setup E2E tests skeleton (T062-T067)
3. After US1 complete:
   - **Developer A**: User Story 3 (T041-T061) - depends on US1
   - **Developer B**: Continue US2
   - **Developer C**: Continue E2E tests
4. All converge on Polish (T072-T083)

---

## Task Summary

**Total Tasks**: 83
- **Setup**: 4 tasks
- **Foundational**: 11 tasks (6 tests + 5 implementation)
- **User Story 1 (P1 - MVP)**: 14 tasks (6 tests + 8 implementation)
- **User Story 2 (P2)**: 11 tasks (5 tests + 6 implementation)
- **User Story 3 (P3)**: 21 tasks (7 tests + 14 implementation)
- **E2E Testing**: 10 tasks
- **Polish**: 12 tasks

**Parallel Opportunities**: 35 tasks marked [P] can run in parallel

**Independent Test Criteria**:
- **US1**: Simulate network failure → error appears in chat with distinct styling
- **US2**: Trigger server 422 error → server error message appears in chat
- **US3**: Trigger any error → click Details → expanded view shows redacted technical details

**Suggested MVP Scope**: User Story 1 only (14 tasks after foundational)

**Format Validation**: ✅ All tasks follow checklist format with [ID] [P?] [Story] Description + file path

---

## Notes

- **[P] tasks**: Different files, no dependencies - safe to parallelize
- **[Story] labels**: US1 (User Story 1), US2 (User Story 2), US3 (User Story 3)
- **TDD mandatory**: All tests written FIRST, verified to FAIL before implementation
- **Independent stories**: Each user story should be independently completable and testable
- **Commit strategy**: Commit after each completed user story (T029, T040, T061)
- **Stop at checkpoints**: Validate each story works independently before proceeding
- **No backend changes**: This is a frontend-only feature - backend already provides proper error responses
- **Accessibility**: WCAG AA compliance required (color contrast, ARIA attributes, keyboard navigation)
- **XSS prevention**: All error content displayed in text nodes or <pre> tags, never v-html
