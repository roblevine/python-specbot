# Tasks: Delete Conversation

**Input**: Design documents from `/specs/016-delete-conversation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per Constitution (Test-First Development principle)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Paths use web app structure: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup

**Purpose**: Verify existing infrastructure and prepare for implementation

- [x] T001 Verify backend DELETE endpoint works at `/api/v1/conversations/{id}` (manual test or existing tests)
- [x] T002 Verify existing deleteConversation method in `frontend/src/state/useConversations.js` works
- [x] T003 Verify existing TitleMenu component structure in `frontend/src/components/TitleMenu/TitleMenu.vue`

**Checkpoint**: Existing infrastructure verified - user story implementation can begin

---

## Phase 2: User Story 1 - Delete Conversation (Priority: P1) 🎯 MVP

**Goal**: Users can delete any conversation via the context menu. Deletion is immediate (no confirmation in this story).

**Independent Test**: Create multiple conversations, click ellipsis menu on any conversation, click Delete, verify conversation removed from list and persists after refresh.

### Tests for User Story 1

> **NOTE: Tests written in Phase 4 (Comprehensive Testing)**

- [x] T004 [P] [US1] Unit test: TitleMenu emits 'delete' event when Delete clicked in `frontend/tests/unit/TitleMenu.test.js`
- [x] T005 [P] [US1] Unit test: TitleMenu shows Delete option by default in `frontend/tests/unit/TitleMenu.test.js`
- [x] T006 [P] [US1] Integration test: Delete flow removes conversation from list in `frontend/tests/integration/delete-conversation.test.js`

### Implementation for User Story 1

- [x] T007 [US1] Add 'delete' emit definition to TitleMenu component in `frontend/src/components/TitleMenu/TitleMenu.vue`
- [x] T008 [US1] Add "Delete" menu item to TitleMenu template in `frontend/src/components/TitleMenu/TitleMenu.vue`
- [x] T009 [US1] Add @delete handler to TitleMenu in HistoryBar that emits 'delete-conversation' in `frontend/src/components/HistoryBar/HistoryBar.vue`
- [x] T010 [US1] Add 'delete-conversation' emit definition to HistoryBar in `frontend/src/components/HistoryBar/HistoryBar.vue`
- [x] T011 [US1] Add @delete-conversation handler in App.vue that calls deleteConversation() in `frontend/src/components/App/App.vue`
- [x] T012 [US1] Add error handling with setError() for failed deletions in `frontend/src/components/App/App.vue`
- [x] T013 [US1] Run US1 tests and verify they pass (depends on Phase 6)

**Checkpoint**: User Story 1 complete - users can delete conversations (immediate deletion, no confirmation)

---

## Phase 3: User Story 2 - Deletion Confirmation (Priority: P2)

**Goal**: A confirmation dialog appears before deletion, preventing accidental data loss. Shows conversation title, has Cancel/Delete buttons, supports keyboard navigation.

**Independent Test**: Click Delete on any conversation, verify dialog appears with title, cancel closes dialog without deletion, confirm performs deletion.

### Tests for User Story 2

> **NOTE: Tests written in Phase 4 (Comprehensive Testing)**

- [x] T014 [P] [US2] Unit test: DeleteConfirmationDialog renders with conversationTitle prop in `frontend/tests/unit/DeleteConfirmationDialog.test.js`
- [x] T015 [P] [US2] Unit test: DeleteConfirmationDialog emits 'confirm' when Delete clicked in `frontend/tests/unit/DeleteConfirmationDialog.test.js`
- [x] T016 [P] [US2] Unit test: DeleteConfirmationDialog emits 'cancel' when Cancel clicked in `frontend/tests/unit/DeleteConfirmationDialog.test.js`
- [x] T017 [P] [US2] Unit test: DeleteConfirmationDialog emits 'cancel' on Escape key in `frontend/tests/unit/DeleteConfirmationDialog.test.js`
- [x] T018 [P] [US2] Unit test: DeleteConfirmationDialog emits 'cancel' on overlay click in `frontend/tests/unit/DeleteConfirmationDialog.test.js`
- [x] T019 [P] [US2] Integration test: Confirmation dialog flow in `frontend/tests/integration/delete-conversation.test.js`

### Implementation for User Story 2

- [x] T020 [US2] Create DeleteConfirmationDialog directory at `frontend/src/components/DeleteConfirmationDialog/`
- [x] T021 [US2] Create DeleteConfirmationDialog component with template (overlay, dialog box, title, message, buttons) in `frontend/src/components/DeleteConfirmationDialog/DeleteConfirmationDialog.vue`
- [x] T022 [US2] Add props (conversationTitle) and emits (confirm, cancel) to DeleteConfirmationDialog in `frontend/src/components/DeleteConfirmationDialog/DeleteConfirmationDialog.vue`
- [x] T023 [US2] Add keyboard support (Escape to cancel) to DeleteConfirmationDialog in `frontend/src/components/DeleteConfirmationDialog/DeleteConfirmationDialog.vue`
- [x] T024 [US2] Add overlay click-outside to cancel in DeleteConfirmationDialog in `frontend/src/components/DeleteConfirmationDialog/DeleteConfirmationDialog.vue`
- [x] T025 [US2] Style Delete button as destructive (red/danger) in DeleteConfirmationDialog in `frontend/src/components/DeleteConfirmationDialog/DeleteConfirmationDialog.vue`
- [x] T026 [US2] Add delete dialog state (showDeleteDialog, deletingConversationId, deletingConversationTitle) to App.vue in `frontend/src/components/App/App.vue`
- [x] T027 [US2] Import and render DeleteConfirmationDialog conditionally in App.vue in `frontend/src/components/App/App.vue`
- [x] T028 [US2] Modify delete handler to show dialog instead of immediate deletion in `frontend/src/components/App/App.vue`
- [x] T029 [US2] Add handleDeleteConfirm and handleDeleteCancel handlers in `frontend/src/components/App/App.vue`
- [x] T030 [US2] Run US2 tests and verify they pass (depends on Phase 6)

**Checkpoint**: User Story 2 complete - confirmation dialog prevents accidental deletions

---

## Phase 4: Comprehensive Testing

**Purpose**: Write all tests for the delete conversation feature

**⚠️ CRITICAL**: Tests must be written to ensure feature quality and prevent regressions

### Frontend Unit Tests

- [x] T037 [P] Create TitleMenu.test.js with delete functionality tests in `frontend/tests/unit/TitleMenu.test.js`
- [x] T038 [P] Create DeleteConfirmationDialog.test.js in `frontend/tests/unit/DeleteConfirmationDialog.test.js`
- [x] T039 [P] Add delete-conversation emit tests to HistoryBar.test.js in `frontend/tests/unit/HistoryBar.test.js`

### Frontend Integration Tests

- [x] T040 Create delete-conversation.test.js with full flow tests in `frontend/tests/integration/delete-conversation.test.js`

### Frontend Contract Tests

- [x] T041 [P] Create deleteConversation.test.js contract snapshot in `frontend/tests/contract/deleteConversation.test.js`

### Backend Integration Tests

- [x] T042 [P] Create test_conversations_api.py with DELETE endpoint tests in `backend/tests/integration/test_conversations_api.py`

### Backend Contract Tests

- [x] T043 [P] Add DELETE conversation contract validation in `backend/tests/contract/test_conversations_contract.py`

**Checkpoint**: All tests written and passing

---

## Phase 5: Polish & Validation

**Purpose**: Final validation and cleanup

- [x] T044 Run full test suite with `./scripts/test-all.sh` and verify all tests pass
- [ ] T045 Verify all acceptance scenarios from spec.md manually
- [ ] T046 Run quickstart.md verification checklist
- [ ] T047 [P] Code cleanup: Remove any debug statements or console.logs
- [x] T048 Update T013, T030 to mark as complete after tests pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **User Story 1 (Phase 2)**: Depends on Setup - delivers MVP
- **User Story 2 (Phase 3)**: Depends on Setup only - can run parallel with US1 if needed, but sequentially recommended
- **Comprehensive Testing (Phase 4)**: Depends on all user stories being complete
- **Polish (Phase 5)**: Depends on Phase 4 tests passing

### User Story Dependencies

```
Setup (Phase 1)
    │
    ├──► User Story 1 (P1) ──► MVP COMPLETE
    │
    └──► User Story 2 (P2) ──► Confirmation added
                                    │
                                    ▼
                         Comprehensive Testing (Phase 4)
                                    │
                                    ▼
                              Polish (Phase 5)
```

**Note**: While US2 can technically start after Setup, the recommended order is US1 → US2 to build incrementally.

### Within Each User Story

1. Implementation tasks in order (TDD tests deferred to Phase 4)
2. Manual verification of functionality
3. Story complete (tests written in Phase 4)

### Parallel Opportunities

**Within Phase 4 (Comprehensive Testing):**
- T037, T038, T039 can run in parallel (all frontend unit test files)
- T041, T042, T043 can run in parallel (contract tests)
- T040 depends on unit tests completing first

---

## Parallel Example: Phase 4 Tests

```bash
# Launch frontend unit tests in parallel:
Task: "Create TitleMenu.test.js with delete functionality tests"
Task: "Create DeleteConfirmationDialog.test.js"
Task: "Add delete-conversation emit tests to HistoryBar.test.js"

# After unit tests, run integration tests:
Task: "Create delete-conversation.test.js with full flow tests"

# Contract tests can run in parallel:
Task: "Create deleteConversation.test.js contract snapshot"
Task: "Create test_conversations_api.py with DELETE endpoint tests"
Task: "Add DELETE conversation contract validation"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verify existing infrastructure)
2. Complete Phase 2: User Story 1 (basic delete flow)
3. **STOP and VALIDATE**: Test delete works, persists after refresh
4. Deploy/demo if ready - users can delete conversations!

### Incremental Delivery

1. Setup → Verify infrastructure
2. Add User Story 1 → Manual verification → Deploy (MVP!)
3. Add User Story 2 → Manual verification → Deploy (safer with confirmation)
4. Add comprehensive tests → Ensure quality and prevent regressions
5. Each story adds value without breaking previous stories

### Recommended Execution

For single developer, execute in order: T001 → T002 → ... → T048 (skipping removed T031-T036)

Each user story can be committed separately after its checkpoint.
Tests should be committed as a final quality assurance phase.

---

## Notes

- Backend already has DELETE endpoint - no backend tasks needed
- Frontend apiClient.deleteConversation() already exists
- useConversations.deleteConversation() already exists
- Follow RenameDialog pattern for DeleteConfirmationDialog styling
- All CSS should use existing CSS variables for consistency
- Commit after each user story checkpoint
