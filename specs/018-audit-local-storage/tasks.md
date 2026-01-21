# Tasks: Audit and Simplify Local Storage

**Input**: Design documents from `/specs/018-audit-local-storage/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: TDD REQUIRED per plan.md constitution check - write tests first, verify they fail, then implement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app (frontend-only feature)**: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup

**Purpose**: Verify preconditions and plan review

- [x] T001 Review data-model.md for schema v2.0.0 structure in specs/018-audit-local-storage/data-model.md
- [x] T002 Review quickstart.md implementation guide in specs/018-audit-local-storage/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create new SettingsStorage module that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests (TDD - Write First, Must Fail)

- [x] T003 [P] Create unit tests for SettingsSchema validation in frontend/tests/unit/SettingsSchema.test.js
- [x] T004 [P] Create unit tests for SettingsStorage load/save operations in frontend/tests/unit/SettingsStorage.test.js
- [x] T005 Run tests to verify they fail (no implementation yet)

### Implementation

- [x] T006 [P] Create SettingsSchema.js with v2.0.0 schema, SETTINGS_KEY, DEFAULT_SETTINGS, and validation in frontend/src/storage/SettingsSchema.js
- [x] T007 Create SettingsStorage.js with loadSettings(), saveSetting(), getSetting() functions in frontend/src/storage/SettingsStorage.js
- [x] T008 Run tests to verify SettingsSchema tests pass
- [x] T009 Run tests to verify SettingsStorage tests pass

**Checkpoint**: New storage module ready - user story implementation can now begin

---

## Phase 3: User Stories 1 & 2 - Settings Persistence (Priority: P1) 🎯 MVP

**Goal**: User settings (sidebar state, model selection) persist across sessions and save immediately on change

**Independent Test**:
1. Change sidebar collapsed state → refresh browser → sidebar state persists
2. Select a model → refresh browser → model selection persists
3. Force-close browser after change → reopen → settings persist

### User Story 1: Settings Persist Across Sessions

- [x] T010 [US1] Update useSidebarCollapse.js to load initial state from SettingsStorage in frontend/src/composables/useSidebarCollapse.js
- [x] T011 [US1] Update useModels.js to load selectedModelId from SettingsStorage on initialization in frontend/src/state/useModels.js
- [x] T012 [US1] Add default value handling when no settings exist in useSidebarCollapse.js
- [x] T013 [US1] Add model ID validation against available models with fallback to default in useModels.js

### User Story 2: Settings Update Immediately on Change

- [x] T014 [US2] Update useSidebarCollapse.js to save to SettingsStorage when isCollapsed changes in frontend/src/composables/useSidebarCollapse.js
- [x] T015 [US2] Update useModels.js to save to SettingsStorage when selectedModelId changes in frontend/src/state/useModels.js
- [x] T016 [US2] Remove direct localStorage.getItem/setItem calls from useSidebarCollapse.js
- [x] T017 [US2] Remove LocalStorageAdapter imports from useModels.js

### Integration Tests for US1 & US2

- [x] T018 [P] [US1] Update useSidebarCollapse.test.js to test loading from new SettingsStorage in frontend/tests/unit/useSidebarCollapse.test.js
- [x] T019 [P] [US2] Update useSidebarCollapse.test.js to test saving on change in frontend/tests/unit/useSidebarCollapse.test.js
- [x] T020 [P] [US1] Update useModels.test.js to test loading from new SettingsStorage in frontend/tests/unit/useModels.test.js
- [x] T021 [P] [US2] Update useModels.test.js to test saving on change in frontend/tests/unit/useModels.test.js
- [x] T022 Run all tests to verify US1 and US2 pass

**Checkpoint**: At this point, settings persistence should be fully functional. Test manually:
- Collapse sidebar → refresh → still collapsed
- Select model → refresh → still selected

---

## Phase 4: User Stories 3 & 4 - Remove Legacy Code (Priority: P2)

**Goal**: Remove all conversation-related localStorage code; ensure unified storage architecture

**Independent Test**:
1. Grep codebase for "LocalStorageAdapter" - should find zero imports in src/
2. Grep codebase for conversation migration code - should find none
3. Application works correctly with server-only conversations

### User Story 3: Remove Legacy Conversation Storage

- [x] T023 [US3] Remove localStorage imports from useConversations.js in frontend/src/state/useConversations.js
- [x] T024 [US3] Remove migrateFromLocalStorage function from useConversations.js
- [x] T025 [US3] Remove hasMigrated ref and related code from useConversations.js
- [x] T026 [US3] Remove localStorage fallback in loadFromStorage catch block in useConversations.js
- [x] T027 [US3] Remove localStorage fallback in saveToStorage catch block in useConversations.js
- [x] T028 [US3] Simplify loadFromStorage to server-only with error display in useConversations.js

### User Story 4: Unified Settings Storage Architecture

- [x] T029 [US4] Delete LocalStorageAdapter.js file in frontend/src/storage/LocalStorageAdapter.js
- [x] T030 [US4] Delete StorageSchema.js file in frontend/src/storage/StorageSchema.js
- [x] T031 [US4] Delete LocalStorageAdapter.test.js file in frontend/tests/unit/LocalStorageAdapter.test.js
- [x] T032 [US4] Delete StorageSchema.test.js file in frontend/tests/unit/StorageSchema.test.js
- [x] T033 [US4] Search for and remove any remaining imports of deleted files
- [x] T034 [US4] Run all tests to verify no broken imports

**Checkpoint**: At this point, all legacy localStorage code should be removed. Verify:
- `grep -r "LocalStorageAdapter" frontend/src/` returns no results
- `grep -r "StorageSchema" frontend/src/` returns no results (except new SettingsSchema)
- `grep -r "migrateFromLocalStorage" frontend/src/` returns no results

---

## Phase 5: Polish & Verification

**Purpose**: Final verification and documentation

- [x] T035 [P] Run full test suite to verify all tests pass
- [x] T036 [P] Manual test: Settings persist across browser sessions
- [x] T037 [P] Manual test: Application works correctly with server-only conversations
- [x] T038 Verify schema in browser dev tools shows specbot:settings:v2 key
- [x] T039 Run quickstart.md verification checklist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **US1 & US2 (Phase 3)**: Depends on Foundational completion
- **US3 & US4 (Phase 4)**: Depends on Foundational completion (can run parallel to Phase 3)
- **Polish (Phase 5)**: Depends on Phases 3 and 4 completion

### User Story Dependencies

- **US1 (P1)**: Depends on Foundational (T003-T009) - Settings load on startup
- **US2 (P1)**: Depends on Foundational (T003-T009) - Settings save on change
- **US3 (P2)**: Independent of US1/US2 - Can be done after Foundational
- **US4 (P2)**: Depends on US1 & US2 completion (to ensure imports are migrated before deletion)

### Within Each Phase

- Tests MUST be written and FAIL before implementation (TDD)
- Schema before storage adapter
- Storage adapter before composables
- Composables before test updates
- Deletions after all migrations complete

### Parallel Opportunities

**Phase 2 (Foundational)**:
- T003 and T004 can run in parallel (different test files)
- T006 can start after T003 passes

**Phase 3 (US1 & US2)**:
- T018, T019, T020, T021 can run in parallel (different test files)
- US1 tasks (T010-T013) and US2 tasks (T014-T017) can be interleaved as they modify same files

**Phase 4 (US3 & US4)**:
- T029, T030, T031, T032 can run in parallel (different files to delete)

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch both test files together:
Task: "Create unit tests for SettingsSchema in frontend/tests/unit/SettingsSchema.test.js"
Task: "Create unit tests for SettingsStorage in frontend/tests/unit/SettingsStorage.test.js"

# After tests written, launch implementations together:
Task: "Create SettingsSchema.js in frontend/src/storage/SettingsSchema.js"
# (SettingsStorage.js depends on SettingsSchema.js, so must wait)
```

---

## Implementation Strategy

### MVP First (US1 & US2 Only)

1. Complete Phase 1: Setup (review docs)
2. Complete Phase 2: Foundational (new storage module with TDD)
3. Complete Phase 3: US1 & US2 (settings persistence)
4. **STOP and VALIDATE**: Test settings persistence manually
5. Deploy/demo if ready - users get working settings persistence!

### Incremental Delivery

1. Setup + Foundational → New storage module ready
2. Add US1 & US2 → Settings work with new module → **MVP Complete!**
3. Add US3 & US4 → Legacy code removed → **Technical debt cleared**
4. Polish → All tests pass, verification complete

### Single Developer Strategy

Recommended order:
1. T001-T009 (Foundational with TDD)
2. T010-T022 (US1 & US2 with tests)
3. T023-T034 (US3 & US4 cleanup)
4. T035-T039 (Polish)

---

## Notes

- [P] tasks = different files, no dependencies, can parallelize
- [Story] label maps task to specific user story for traceability
- TDD is REQUIRED: Write tests first (T003, T004), verify they fail (T005), then implement
- The separate `sidebar.collapsed` localStorage key will be consolidated into the new schema
- Old localStorage data under `chatInterface:v1:data` will be ignored (no migration)
- After completion, only one localStorage key should exist: `specbot:settings:v2`
