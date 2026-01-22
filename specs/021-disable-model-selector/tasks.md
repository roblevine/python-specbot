# Tasks: Disable Model Selector After Conversation Starts

**Input**: Design documents from `/specs/021-disable-model-selector/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Test-First Development is REQUIRED per constitution. Tests must be written and verified to FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`, `frontend/tests/`
- This is a frontend-focused feature - no backend changes required

---

## Phase 1: Setup

**Purpose**: Verify existing infrastructure supports the feature

- [x] T001 Verify ModelSelector component accepts disabled prop in frontend/src/components/ModelSelector/ModelSelector.vue
- [x] T002 Verify useModels composable exports setSelectedModel in frontend/src/state/useModels.js
- [x] T003 Verify useConversations composable exports activeConversation in frontend/src/state/useConversations.js

---

## Phase 2: Foundational (Shared State Enhancement)

**Purpose**: Core state management changes that support ALL user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational Phase

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T004 [P] Write test for setSelectedModel with persist=false in frontend/tests/unit/useModels.test.js

### Implementation for Foundational Phase

- [x] T005 Add optional persist parameter to setSelectedModel function in frontend/src/state/useModels.js
- [x] T006 Verify tests pass after implementation

**Checkpoint**: Foundation ready - setSelectedModel(modelId, persist=false) works correctly

---

## Phase 3: User Story 1 - Lock Model After First Message (Priority: P1) 🎯 MVP

**Goal**: Disable model selector immediately after user sends first message in a conversation

**Independent Test**: Start new conversation → verify selector enabled → send message → verify selector disabled and shows correct model

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T007 [P] [US1] Write test: selector enabled when conversation has no messages in frontend/tests/unit/components/App.spec.js
- [x] T008 [P] [US1] Write test: selector disabled when conversation has messages in frontend/tests/unit/components/App.spec.js
- [x] T009 [P] [US1] Write test: selector shows correct model from conversation in frontend/tests/unit/components/App.spec.js

### Implementation for User Story 1

- [x] T010 [US1] Add isModelSelectorDisabled computed property in frontend/src/components/App/App.vue
- [x] T011 [US1] Add getConversationModelId helper function in frontend/src/components/App/App.vue
- [x] T012 [US1] Add modelSelectorDisabled prop to InputArea component in frontend/src/components/InputArea/InputArea.vue
- [x] T013 [US1] Pass modelSelectorDisabled prop from App.vue to InputArea in frontend/src/components/App/App.vue
- [x] T014 [US1] Pass disabled prop from InputArea to ModelSelector in frontend/src/components/InputArea/InputArea.vue
- [x] T015 [US1] Verify all US1 tests pass

**Checkpoint**: User Story 1 complete - model selector locks after first message sent

---

## Phase 4: User Story 2 - Show Locked Model for Previous Conversations (Priority: P1)

**Goal**: When loading a previous conversation, display its model in disabled selector

**Independent Test**: Create conversation with messages → navigate away → return → verify selector shows correct model and is disabled

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T016 [P] [US2] Write test: model restored when switching to conversation with messages in frontend/tests/unit/components/App.spec.js
- [x] T017 [P] [US2] Write test: default model used for legacy conversations without model field in frontend/tests/unit/components/App.spec.js

### Implementation for User Story 2

- [x] T018 [US2] Add watch on activeConversation to restore model in frontend/src/components/App/App.vue
- [x] T019 [US2] Implement legacy conversation fallback to default model in frontend/src/components/App/App.vue
- [x] T020 [US2] Verify all US2 tests pass

**Checkpoint**: User Story 2 complete - previous conversations show correct locked model

---

## Phase 5: User Story 3 - Enable Selector for New Conversations (Priority: P2)

**Goal**: Model selector is enabled when starting a new conversation (before any messages)

**Independent Test**: While viewing conversation with messages → click New Conversation → verify selector is enabled

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T021 [P] [US3] Write test: selector enabled after creating new conversation in frontend/tests/unit/components/App.spec.js
- [x] T022 [P] [US3] Write test: model selection works in new conversation in frontend/tests/unit/components/App.spec.js

### Implementation for User Story 3

- [x] T023 [US3] Verify isModelSelectorDisabled returns false for conversations with empty messages array
- [x] T024 [US3] Verify model can be changed in new conversation before first message
- [x] T025 [US3] Verify all US3 tests pass

**Checkpoint**: User Story 3 complete - new conversations allow model selection

---

## Phase 6: Edge Cases & Polish

**Purpose**: Handle edge cases and improve robustness

### Tests for Edge Cases

- [x] T026 [P] Write test: unavailable model displays with indicator in frontend/tests/unit/components/App.spec.js
- [x] T027 [P] Write test: single available model still follows enable/disable rules in frontend/tests/unit/components/App.spec.js

### Implementation for Edge Cases

- [x] T028 Add isModelAvailable helper function in frontend/src/components/App/App.vue
- [x] T029 Handle unavailable model by falling back to default model in frontend/src/components/App/App.vue
- [x] T030 Verify edge case tests pass

### Final Validation

- [x] T031 Run full test suite to ensure no regressions
- [x] T032 Manual testing per quickstart.md verification checklist
- [x] T033 Code cleanup and remove any debug statements

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - verification only
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Core MVP
- **User Story 2 (Phase 4)**: Depends on Foundational - Can parallel with US1
- **User Story 3 (Phase 5)**: Depends on Foundational - Can parallel with US1/US2
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent after Foundational - Core locking behavior
- **User Story 2 (P1)**: Independent after Foundational - Integrates naturally with US1's disabled logic
- **User Story 3 (P2)**: Independent after Foundational - Re-enable logic, no dependencies on other stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Computed properties before template changes
- App.vue changes before child component changes
- Verify tests pass after implementation

### Parallel Opportunities

**Phase 1 (Setup):**
```
T001, T002, T003 can run in parallel (read-only verification)
```

**Phase 2 (Foundational):**
```
T004 (test) must complete → T005 (implementation) → T006 (verify)
```

**Phase 3-5 (User Stories):**
```
After Phase 2, all user stories can start in parallel:
- US1: T007, T008, T009 (parallel tests) → T010-T015 (implementation)
- US2: T016, T017 (parallel tests) → T018-T020 (implementation)
- US3: T021, T022 (parallel tests) → T023-T025 (implementation)
```

**Phase 6 (Polish):**
```
T026, T027 can run in parallel (tests for different edge cases)
```

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Write test: selector enabled when conversation has no messages"
Task: "Write test: selector disabled when conversation has messages"
Task: "Write test: selector shows correct model from conversation"

# Verify all tests FAIL

# Then implement sequentially (file dependencies):
Task: "Add isModelSelectorDisabled computed property in App.vue"
Task: "Add getConversationModelId helper function in App.vue"
Task: "Add modelSelectorDisabled prop to InputArea component"
Task: "Pass modelSelectorDisabled prop from App.vue to InputArea"
Task: "Pass disabled prop from InputArea to ModelSelector"

# Verify all tests PASS
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verification)
2. Complete Phase 2: Foundational (setSelectedModel persist param)
3. Complete Phase 3: User Story 1 (lock after first message)
4. **STOP and VALIDATE**: Test US1 independently
5. Demo: New conversation → select model → send message → selector locked

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Demo (MVP!)
3. Add User Story 2 → Test independently → Demo (loads previous conversations correctly)
4. Add User Story 3 → Test independently → Demo (new conversation re-enables)
5. Add Edge Cases → Test → Final polish

### Single Developer Strategy (Recommended)

Follow priority order:
1. Phase 1 + 2: ~15 min
2. Phase 3 (US1): ~30 min - **MVP COMPLETE**
3. Phase 4 (US2): ~20 min
4. Phase 5 (US3): ~15 min
5. Phase 6 (Polish): ~20 min

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each phase completion
- Stop at any checkpoint to validate story independently
- No backend changes required - all tasks are frontend
