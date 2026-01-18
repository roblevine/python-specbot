# Tasks: Delete Conversation

**Input**: Design documents from `/specs/016-delete-conversation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per Constitution (Test-First Development principle)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Paths use web app structure: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup

**Purpose**: Verify existing infrastructure and prepare for implementation

- [ ] T001 Verify backend DELETE endpoint works at `/api/v1/conversations/{id}` (manual test or existing tests)
- [ ] T002 Verify existing deleteConversation method in `frontend/src/state/useConversations.js` works
- [ ] T003 Verify existing TitleMenu component structure in `frontend/src/components/TitleMenu/TitleMenu.vue`

**Checkpoint**: Existing infrastructure verified - user story implementation can begin

---

## Phase 2: User Story 1 - Delete Historical Conversation (Priority: P1) 🎯 MVP

**Goal**: Users can delete non-active conversations via the context menu. Deletion is immediate (no confirmation in this story).

**Independent Test**: Create multiple conversations, click ellipsis menu on non-active conversation, click Delete, verify conversation removed from list and persists after refresh.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T004 [P] [US1] Unit test: TitleMenu emits 'delete' event when Delete clicked in `frontend/tests/unit/TitleMenu.spec.js`
- [ ] T005 [P] [US1] Unit test: TitleMenu shows Delete option by default in `frontend/tests/unit/TitleMenu.spec.js`
- [ ] T006 [P] [US1] Integration test: Delete flow removes conversation from list in `frontend/tests/integration/delete-conversation.spec.js`

### Implementation for User Story 1

- [ ] T007 [US1] Add 'delete' emit definition to TitleMenu component in `frontend/src/components/TitleMenu/TitleMenu.vue`
- [ ] T008 [US1] Add "Delete" menu item to TitleMenu template in `frontend/src/components/TitleMenu/TitleMenu.vue`
- [ ] T009 [US1] Add @delete handler to TitleMenu in HistoryBar that emits 'delete-conversation' in `frontend/src/components/HistoryBar/HistoryBar.vue`
- [ ] T010 [US1] Add 'delete-conversation' emit definition to HistoryBar in `frontend/src/components/HistoryBar/HistoryBar.vue`
- [ ] T011 [US1] Add @delete-conversation handler in App.vue that calls deleteConversation() in `frontend/src/components/App/App.vue`
- [ ] T012 [US1] Add error handling with setError() for failed deletions in `frontend/src/components/App/App.vue`
- [ ] T013 [US1] Run US1 tests and verify they pass

**Checkpoint**: User Story 1 complete - users can delete conversations (immediate deletion, no confirmation)

---

## Phase 3: User Story 2 - Deletion Confirmation (Priority: P2)

**Goal**: A confirmation dialog appears before deletion, preventing accidental data loss. Shows conversation title, has Cancel/Delete buttons, supports keyboard navigation.

**Independent Test**: Click Delete on any conversation, verify dialog appears with title, cancel closes dialog without deletion, confirm performs deletion.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [US2] Unit test: DeleteConfirmationDialog renders with conversationTitle prop in `frontend/tests/unit/DeleteConfirmationDialog.spec.js`
- [ ] T015 [P] [US2] Unit test: DeleteConfirmationDialog emits 'confirm' when Delete clicked in `frontend/tests/unit/DeleteConfirmationDialog.spec.js`
- [ ] T016 [P] [US2] Unit test: DeleteConfirmationDialog emits 'cancel' when Cancel clicked in `frontend/tests/unit/DeleteConfirmationDialog.spec.js`
- [ ] T017 [P] [US2] Unit test: DeleteConfirmationDialog emits 'cancel' on Escape key in `frontend/tests/unit/DeleteConfirmationDialog.spec.js`
- [ ] T018 [P] [US2] Unit test: DeleteConfirmationDialog emits 'cancel' on overlay click in `frontend/tests/unit/DeleteConfirmationDialog.spec.js`
- [ ] T019 [P] [US2] Integration test: Confirmation dialog flow in `frontend/tests/integration/delete-conversation.spec.js`

### Implementation for User Story 2

- [ ] T020 [US2] Create DeleteConfirmationDialog directory at `frontend/src/components/DeleteConfirmationDialog/`
- [ ] T021 [US2] Create DeleteConfirmationDialog component with template (overlay, dialog box, title, message, buttons) in `frontend/src/components/DeleteConfirmationDialog/DeleteConfirmationDialog.vue`
- [ ] T022 [US2] Add props (conversationTitle) and emits (confirm, cancel) to DeleteConfirmationDialog in `frontend/src/components/DeleteConfirmationDialog/DeleteConfirmationDialog.vue`
- [ ] T023 [US2] Add keyboard support (Escape to cancel) to DeleteConfirmationDialog in `frontend/src/components/DeleteConfirmationDialog/DeleteConfirmationDialog.vue`
- [ ] T024 [US2] Add overlay click-outside to cancel in DeleteConfirmationDialog in `frontend/src/components/DeleteConfirmationDialog/DeleteConfirmationDialog.vue`
- [ ] T025 [US2] Style Delete button as destructive (red/danger) in DeleteConfirmationDialog in `frontend/src/components/DeleteConfirmationDialog/DeleteConfirmationDialog.vue`
- [ ] T026 [US2] Add delete dialog state (showDeleteDialog, deletingConversationId, deletingConversationTitle) to App.vue in `frontend/src/components/App/App.vue`
- [ ] T027 [US2] Import and render DeleteConfirmationDialog conditionally in App.vue in `frontend/src/components/App/App.vue`
- [ ] T028 [US2] Modify delete handler to show dialog instead of immediate deletion in `frontend/src/components/App/App.vue`
- [ ] T029 [US2] Add handleDeleteConfirm and handleDeleteCancel handlers in `frontend/src/components/App/App.vue`
- [ ] T030 [US2] Run US2 tests and verify they pass

**Checkpoint**: User Story 2 complete - confirmation dialog prevents accidental deletions

---

## Phase 4: User Story 3 - Protected Active Conversation (Priority: P3)

**Goal**: The Delete option is hidden for the currently active conversation, preventing users from deleting what they're working on.

**Independent Test**: Select a conversation (making it active), open its ellipsis menu, verify Delete option is NOT visible. Switch to another conversation, verify Delete now appears on the previously active one.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T031 [P] [US3] Unit test: TitleMenu hides Delete when showDelete=false in `frontend/tests/unit/TitleMenu.spec.js`
- [ ] T032 [P] [US3] Integration test: Delete option hidden for active conversation in `frontend/tests/integration/delete-conversation.spec.js`

### Implementation for User Story 3

- [ ] T033 [US3] Add showDelete prop (Boolean, default: true) to TitleMenu in `frontend/src/components/TitleMenu/TitleMenu.vue`
- [ ] T034 [US3] Conditionally render Delete menu item based on showDelete prop in `frontend/src/components/TitleMenu/TitleMenu.vue`
- [ ] T035 [US3] Pass showDelete prop to TitleMenu in HistoryBar based on `conversation.id !== activeConversationId` in `frontend/src/components/HistoryBar/HistoryBar.vue`
- [ ] T036 [US3] Run US3 tests and verify they pass

**Checkpoint**: User Story 3 complete - active conversation protected from deletion

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [ ] T037 Run full test suite with `./scripts/test-all.sh`
- [ ] T038 Verify all acceptance scenarios from spec.md manually
- [ ] T039 Run quickstart.md verification checklist
- [ ] T040 [P] Code cleanup: Remove any debug statements or console.logs

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **User Story 1 (Phase 2)**: Depends on Setup - delivers MVP
- **User Story 2 (Phase 3)**: Depends on Setup only - can run parallel with US1 if needed, but sequentially recommended
- **User Story 3 (Phase 4)**: Depends on Setup only - can run parallel with US1/US2 if needed
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

```
Setup (Phase 1)
    │
    ├──► User Story 1 (P1) ──► MVP COMPLETE
    │
    ├──► User Story 2 (P2) ──► Confirmation added
    │
    └──► User Story 3 (P3) ──► Active protection added
                                    │
                                    ▼
                              Polish (Phase 5)
```

**Note**: While US2 and US3 can technically start after Setup, the recommended order is US1 → US2 → US3 to build incrementally.

### Within Each User Story

1. Tests FIRST - write and verify they FAIL
2. Implementation tasks in order
3. Run tests to verify they PASS
4. Story complete

### Parallel Opportunities

**Within Phase 2 (US1):**
- T004, T005, T006 can run in parallel (all test files)

**Within Phase 3 (US2):**
- T014, T015, T016, T017, T018, T019 can run in parallel (all test files)

**Within Phase 4 (US3):**
- T031, T032 can run in parallel (test files)

---

## Parallel Example: User Story 2 Tests

```bash
# Launch all US2 tests together:
Task: "Unit test: DeleteConfirmationDialog renders with conversationTitle prop"
Task: "Unit test: DeleteConfirmationDialog emits 'confirm' when Delete clicked"
Task: "Unit test: DeleteConfirmationDialog emits 'cancel' when Cancel clicked"
Task: "Unit test: DeleteConfirmationDialog emits 'cancel' on Escape key"
Task: "Unit test: DeleteConfirmationDialog emits 'cancel' on overlay click"
Task: "Integration test: Confirmation dialog flow"
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
2. Add User Story 1 → Test independently → Deploy (MVP!)
3. Add User Story 2 → Test independently → Deploy (safer with confirmation)
4. Add User Story 3 → Test independently → Deploy (fully protected)
5. Each story adds value without breaking previous stories

### Recommended Execution

For single developer, execute in order: T001 → T002 → ... → T040

Each user story can be committed separately after its checkpoint.

---

## Notes

- Backend already has DELETE endpoint - no backend tasks needed
- Frontend apiClient.deleteConversation() already exists
- useConversations.deleteConversation() already exists
- Follow RenameDialog pattern for DeleteConfirmationDialog styling
- All CSS should use existing CSS variables for consistency
- Commit after each user story checkpoint
