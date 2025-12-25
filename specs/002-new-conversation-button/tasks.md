# Tasks: New Conversation Button

**Input**: Design documents from `/specs/002-new-conversation-button/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test-First Development is REQUIRED per Constitution Principle III. All tests MUST be written and verified to FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/`, `frontend/tests/`
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify development environment is ready

- [X] T001 Verify Node.js 18+ and npm are installed
- [X] T002 Verify all dependencies are installed (npm install in frontend/)
- [ ] T003 [P] Verify development server runs (npm run dev in frontend/)
- [X] T004 [P] Verify existing test suite passes (npm test in frontend/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before user story implementation

**⚠️ CRITICAL**: This feature has NO foundational tasks - it integrates with existing infrastructure from 001-chat-interface

**Checkpoint**: Foundation ready (already exists) - user story implementation can begin immediately

---

## Phase 3: User Story 1 - Starting a Fresh Conversation (Priority: P1) 🎯 MVP

**Goal**: Add a "New Conversation" button at the top of the message history bar that allows users to start a fresh conversation with a single click

**Independent Test**: Can be fully tested by clicking the new conversation button and verifying that the message input area is cleared and ready for a new conversation, while the previous conversation remains accessible in the history.

**Acceptance Scenarios**:
1. User clicks button → message input area is cleared
2. User clicks button → previous conversation is preserved in history
3. User has unsaved message → clicks button → unsaved message is discarded

### Tests for User Story 1 (REQUIRED - TDD Mandatory) ⚠️

> **CRITICAL**: Write these tests FIRST, ensure they FAIL before implementation

**Unit Tests** (frontend/src/components/HistoryBar/HistoryBar.test.js):

- [X] T005 [P] [US1] Create unit test file at frontend/src/components/HistoryBar/HistoryBar.test.js
- [X] T006 [P] [US1] Write unit test: button renders with correct label in frontend/src/components/HistoryBar/HistoryBar.test.js
- [X] T007 [P] [US1] Write unit test: button emits new-conversation event on click in frontend/src/components/HistoryBar/HistoryBar.test.js
- [X] T008 [P] [US1] Write unit test: rapid clicks prevented by debounce in frontend/src/components/HistoryBar/HistoryBar.test.js
- [X] T009 [P] [US1] Write unit test: button has accessibility attributes in frontend/src/components/HistoryBar/HistoryBar.test.js

**E2E Tests** (frontend/tests/e2e/new-conversation.spec.js):

- [X] T010 [P] [US1] Create E2E test file at frontend/tests/e2e/new-conversation.spec.js
- [X] T011 [P] [US1] Write E2E test: user can start new conversation in frontend/tests/e2e/new-conversation.spec.js
- [X] T012 [P] [US1] Write E2E test: unsaved message is discarded in frontend/tests/e2e/new-conversation.spec.js
- [X] T013 [P] [US1] Write E2E test: rapid clicks create only one conversation in frontend/tests/e2e/new-conversation.spec.js
- [X] T014 [P] [US1] Write E2E test: button is keyboard accessible in frontend/tests/e2e/new-conversation.spec.js

**Test Verification** (MUST FAIL):

- [X] T015 [US1] Run unit tests and verify they FAIL (npm test -- HistoryBar.test.js in frontend/)
- [X] T016 [US1] Run E2E tests and verify they FAIL (npm run test:e2e -- new-conversation.spec.js in frontend/)

### Implementation for User Story 1

**HistoryBar Component** (frontend/src/components/HistoryBar/HistoryBar.vue):

- [X] T017 [US1] Add new-conversation to emits array in frontend/src/components/HistoryBar/HistoryBar.vue
- [X] T018 [US1] Add handleNewConversation function with debounce guard in frontend/src/components/HistoryBar/HistoryBar.vue
- [X] T019 [US1] Add button element to template in .history-header in frontend/src/components/HistoryBar/HistoryBar.vue
- [X] T020 [US1] Add button CSS styles (.new-conversation-btn) in frontend/src/components/HistoryBar/HistoryBar.vue
- [X] T021 [US1] Update .history-header CSS for flexbox layout in frontend/src/components/HistoryBar/HistoryBar.vue

**App Component** (frontend/src/components/App/App.vue):

- [X] T022 [US1] Add @new-conversation event handler to HistoryBar in template in frontend/src/components/App/App.vue
- [X] T023 [US1] Implement handleNewConversation function with error handling in frontend/src/components/App/App.vue
- [X] T024 [US1] Add handleNewConversation to component return statement in frontend/src/components/App/App.vue
- [X] T025 [US1] Add logging for new conversation creation in frontend/src/components/App/App.vue

**Test Verification** (MUST PASS):

- [X] T026 [US1] Run unit tests and verify they PASS (npm test -- HistoryBar.test.js in frontend/)
- [ ] T027 [US1] Run E2E tests and verify they PASS (npm run test:e2e -- new-conversation.spec.js in frontend/)
- [X] T028 [US1] Run full test suite and verify no regressions (npm test && npm run test:e2e in frontend/)

**Manual Testing**:

- [ ] T029 [US1] Manual test: Click button and verify new conversation is created
- [ ] T030 [US1] Manual test: Verify previous conversation is preserved in history
- [ ] T031 [US1] Manual test: Type unsaved message, click button, verify message discarded
- [ ] T032 [US1] Manual test: Click button rapidly, verify only one conversation created
- [ ] T033 [US1] Manual test: Tab to button and press Enter, verify keyboard accessibility

**Integration Verification**:

- [ ] T034 [US1] Verify button appears in correct location (top of history bar)
- [ ] T035 [US1] Verify button styling matches design (primary color, hover state)
- [ ] T036 [US1] Verify createConversation() is called when button clicked
- [ ] T037 [US1] Verify LocalStorage is updated with new conversation
- [ ] T038 [US1] Verify UI updates reactively (chat area clears, history updates)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [X] T039 [P] Run linter and fix any issues (npm run lint in frontend/)
- [X] T040 [P] Run formatter on modified files (npm run format in frontend/)
- [X] T041 Verify all tests pass (npm test && npm run test:e2e in frontend/)
- [ ] T042 Review browser console for errors during manual testing
- [ ] T043 Verify accessibility with screen reader (test ARIA labels)
- [ ] T044 Verify responsive design on narrow screens
- [ ] T045 [P] Update CLAUDE.md if needed (already updated by planning phase)
- [ ] T046 Test button performance (click response < 200ms)
- [ ] T047 Verify success criteria SC-001: Users can start conversation with single click
- [ ] T048 Verify success criteria SC-002: 100% of conversations preserved
- [ ] T049 Verify success criteria SC-003: Button locatable within 3 seconds
- [ ] T050 Verify success criteria SC-004: Button responds within 200ms

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: N/A - no foundational tasks (uses existing infrastructure)
- **User Story 1 (Phase 3)**: Depends on Setup completion only
- **Polish (Phase 4)**: Depends on User Story 1 completion

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies - can start after Setup phase
  - This is the ONLY user story for this feature (single thin slice)
  - Delivers complete end-to-end value independently

### Within User Story 1

**Test-First Workflow (TDD - REQUIRED)**:
1. T005-T014: Write ALL tests first (can be parallelized)
2. T015-T016: Verify tests FAIL (sequential, depends on T005-T014)
3. T017-T025: Implement code to pass tests (some can be parallelized)
4. T026-T028: Verify tests PASS (sequential, depends on T017-T025)
5. T029-T038: Manual and integration testing (sequential)

**Dependencies within implementation**:
- HistoryBar changes (T017-T021) can be done in parallel with each other
- App component changes (T022-T025) can be done in parallel with each other
- HistoryBar must be complete before App component event handler will work
- All implementation must be complete before test verification

### Parallel Opportunities

**Tests can be written in parallel**:
- All unit test tasks (T006-T009) - different test cases
- All E2E test tasks (T011-T014) - different test scenarios
- Unit tests and E2E tests can be written concurrently (different files)

**Implementation can be partially parallelized**:
- HistoryBar template changes (T019) parallel with CSS changes (T020-T021)
- HistoryBar script changes (T017-T018) can be done independently
- App component changes (T022-T025) can be done independently once HistoryBar is complete

**Polish tasks are mostly parallel**:
- Linting (T039), formatting (T040), accessibility (T043), responsive design (T044) all independent

---

## Parallel Example: User Story 1

```bash
# Phase 1: Write all unit tests in parallel
Parallel:
  Task: "Write unit test: button renders with correct label in frontend/src/components/HistoryBar/HistoryBar.test.js"
  Task: "Write unit test: button emits new-conversation event on click in frontend/src/components/HistoryBar/HistoryBar.test.js"
  Task: "Write unit test: rapid clicks prevented by debounce in frontend/src/components/HistoryBar/HistoryBar.test.js"
  Task: "Write unit test: button has accessibility attributes in frontend/src/components/HistoryBar/HistoryBar.test.js"

# Phase 2: Write all E2E tests in parallel
Parallel:
  Task: "Write E2E test: user can start new conversation in frontend/tests/e2e/new-conversation.spec.js"
  Task: "Write E2E test: unsaved message is discarded in frontend/tests/e2e/new-conversation.spec.js"
  Task: "Write E2E test: rapid clicks create only one conversation in frontend/tests/e2e/new-conversation.spec.js"
  Task: "Write E2E test: button is keyboard accessible in frontend/tests/e2e/new-conversation.spec.js"

# Phase 3: Implement HistoryBar changes in parallel
Parallel:
  Task: "Add new-conversation to emits array in frontend/src/components/HistoryBar/HistoryBar.vue"
  Task: "Add handleNewConversation function with debounce guard in frontend/src/components/HistoryBar/HistoryBar.vue"
  Task: "Add button element to template in .history-header in frontend/src/components/HistoryBar/HistoryBar.vue"
  Task: "Add button CSS styles (.new-conversation-btn) in frontend/src/components/HistoryBar/HistoryBar.vue"

# Phase 4: Polish tasks in parallel
Parallel:
  Task: "Run linter and fix any issues (npm run lint in frontend/)"
  Task: "Run formatter on modified files (npm run format in frontend/)"
  Task: "Verify accessibility with screen reader (test ARIA labels)"
  Task: "Verify responsive design on narrow screens"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

This feature IS the MVP - it consists of a single user story (P1) that delivers complete value.

1. Complete Phase 1: Setup (verify environment)
2. Skip Phase 2: Foundational (no foundational tasks needed)
3. Complete Phase 3: User Story 1 (TDD workflow)
   - Write tests FIRST → Verify FAIL → Implement → Verify PASS
4. Complete Phase 4: Polish
5. **DONE**: Feature is complete and deployable

### Incremental Delivery

This feature follows Principle VIII (Incremental Delivery):
- Single thin vertical slice (P1 user story)
- Delivers end-to-end value: Button → Event → State Update → UI Refresh
- Independently testable and demonstrable
- Can be committed and deployed without dependencies

**Timeline Estimate**:
- Phase 1 (Setup): 5-10 minutes
- Phase 3 (User Story 1): 1-2 hours (per quickstart.md)
  - Tests: 30-45 minutes
  - Implementation: 20-30 minutes
  - Verification: 10-15 minutes
- Phase 4 (Polish): 10-15 minutes
- **Total**: ~1.5-2.5 hours

### Test-Driven Development Workflow

**CRITICAL**: Follow TDD strictly (Constitution Principle III - NON-NEGOTIABLE)

1. **RED**: Write tests that FAIL
   - T005-T014: Write all tests
   - T015-T016: Run tests, verify FAIL
   - If tests pass at this stage → tests are wrong, fix them

2. **GREEN**: Write minimum code to PASS
   - T017-T025: Implement feature
   - T026-T028: Run tests, verify PASS
   - If tests fail → debug and fix

3. **REFACTOR**: Clean up code (keep tests green)
   - T039-T040: Lint and format
   - T026-T028: Re-run tests, verify still PASS

4. **VALIDATE**: Manual testing and verification
   - T029-T050: Manual testing, integration checks, success criteria

---

## Notes

- [P] tasks = different files, no dependencies
- [US1] label maps task to User Story 1 for traceability
- This feature is a single user story (one thin slice)
- Tests MUST fail before implementation (TDD requirement)
- Verify tests pass after implementation
- Commit after logical groups of tasks
- Stop at checkpoint to validate independently
- Total: 50 tasks (including test verification and manual testing)

---

## Task Summary

**Total Tasks**: 50

**Task Breakdown by Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 0 tasks (uses existing infrastructure)
- Phase 3 (User Story 1): 34 tasks
  - Tests: 12 tasks (10 write + 2 verify fail)
  - Implementation: 9 tasks
  - Test Verification: 3 tasks (verify pass)
  - Manual Testing: 5 tasks
  - Integration Verification: 5 tasks
- Phase 4 (Polish): 12 tasks

**Parallel Opportunities**:
- 18 tasks marked [P] can run in parallel with others
- Tests can be written concurrently (8 parallel opportunities)
- Implementation has 4-5 parallel opportunities
- Polish has 4 parallel opportunities

**Independent Test Criteria**:
- User Story 1: Click button → verify chat clears + history preserves + unsaved discarded

**Suggested MVP Scope**:
- This entire feature IS the MVP (single P1 story)
- All 50 tasks deliver one complete, deployable increment

**Format Validation**: ✅ All tasks follow checklist format with:
- Checkbox: `- [ ]`
- Task ID: `T001` through `T050`
- [P] marker where applicable
- [US1] label for User Story 1 tasks
- File paths in descriptions
