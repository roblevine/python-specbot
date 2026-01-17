# Tasks: Conversation Titles

**Input**: Design documents from `/specs/014-conversation-titles/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: No test tasks included (not explicitly requested in spec). Manual verification steps provided at each checkpoint.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/`, `backend/` (no backend changes needed)
- All paths relative to repository root

---

## Phase 1: Setup

**Purpose**: Verify environment and baseline

- [ ] T001 Verify frontend dev server runs: `cd frontend && npm run dev`
- [ ] T002 [P] Verify existing tests pass: `cd frontend && npm test`
- [ ] T003 [P] Review current StatusBar implementation in frontend/src/components/StatusBar/StatusBar.vue
- [ ] T004 [P] Review current HistoryBar implementation in frontend/src/components/HistoryBar/HistoryBar.vue
- [ ] T005 [P] Review current useConversations composable in frontend/src/state/useConversations.js

**Checkpoint**: Development environment ready, current implementation understood

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core changes that enable all user stories

**⚠️ CRITICAL**: User stories 1, 3, 4, 5 depend on these changes

- [ ] T006 Enhance auto-title logic to store full message text (remove .slice(0, 50)) in frontend/src/state/useConversations.js
- [ ] T007 Add renameConversation(id, newTitle) function in frontend/src/state/useConversations.js
- [ ] T008 Export renameConversation from useConversations composable in frontend/src/state/useConversations.js
- [ ] T009 Create validateTitle() function in frontend/src/utils/validators.js (1-500 chars, non-empty)

**Checkpoint**: Auto-title stores full text, rename function available, validation ready

---

## Phase 3: User Story 1 - Display Title in Status Bar (Priority: P1)

**Goal**: Show conversation title in status bar, aligned with chat content area

**Independent Test**: Create conversation, send message, verify status bar displays title aligned with chat content

### Implementation for User Story 1

- [ ] T010 [US1] Add `title` prop to StatusBar component in frontend/src/components/StatusBar/StatusBar.vue
- [ ] T011 [US1] Add title display section to StatusBar template in frontend/src/components/StatusBar/StatusBar.vue
- [ ] T012 [US1] Add CSS for title alignment (max-width: var(--chat-max-width)) in frontend/src/components/StatusBar/StatusBar.vue
- [ ] T013 [US1] Add CSS for title truncation (text-overflow: ellipsis) in frontend/src/components/StatusBar/StatusBar.vue
- [ ] T014 [US1] Create activeConversationTitle computed property in frontend/src/components/App/App.vue
- [ ] T015 [US1] Pass title prop from App to StatusBar in frontend/src/components/App/App.vue

**Checkpoint**: Title displays in status bar. Verify:
- Title shows for active conversation
- Title aligned with chat content area
- Long titles truncate with ellipsis
- Title updates when switching conversations

---

## Phase 4: User Story 3 - Display Titles in Conversation History (Priority: P1)

**Goal**: Replace message preview with title-only display in history sidebar

**Independent Test**: Create multiple conversations, verify sidebar shows only titles (no message previews)

### Implementation for User Story 3

- [ ] T016 [US3] Remove getPreview() function from frontend/src/components/HistoryBar/HistoryBar.vue
- [ ] T017 [US3] Remove conversation-preview div from template in frontend/src/components/HistoryBar/HistoryBar.vue
- [ ] T018 [US3] Update conversation-title CSS for truncation in frontend/src/components/HistoryBar/HistoryBar.vue
- [ ] T019 [US3] Remove conversation-preview CSS styles in frontend/src/components/HistoryBar/HistoryBar.vue

**Checkpoint**: History sidebar shows titles only. Verify:
- Each conversation shows only its title
- No message preview displayed
- Long titles truncate with ellipsis
- Default "New Conversation" displays correctly

---

## Phase 5: User Story 4 - Rename from Status Bar (Priority: P2)

**Goal**: Add ellipsis menu in status bar with rename option

**Independent Test**: Click ellipsis in status bar, select rename, enter new title, verify title updates everywhere

### Implementation for User Story 4

- [ ] T020 [US4] Create TitleMenu directory: frontend/src/components/TitleMenu/
- [ ] T021 [US4] Create TitleMenu.vue component with ellipsis button and dropdown in frontend/src/components/TitleMenu/TitleMenu.vue
- [ ] T022 [US4] Add click-outside-to-close behavior to TitleMenu in frontend/src/components/TitleMenu/TitleMenu.vue
- [ ] T023 [US4] Style TitleMenu with existing CSS variables in frontend/src/components/TitleMenu/TitleMenu.vue
- [ ] T024 [US4] Create RenameDialog directory: frontend/src/components/RenameDialog/
- [ ] T025 [US4] Create RenameDialog.vue modal component in frontend/src/components/RenameDialog/RenameDialog.vue
- [ ] T026 [US4] Add title input with validation in RenameDialog in frontend/src/components/RenameDialog/RenameDialog.vue
- [ ] T027 [US4] Add save/cancel buttons and keyboard handlers (Enter, Escape) in frontend/src/components/RenameDialog/RenameDialog.vue
- [ ] T028 [US4] Style RenameDialog modal overlay and form in frontend/src/components/RenameDialog/RenameDialog.vue
- [ ] T029 [US4] Import and add TitleMenu to StatusBar template in frontend/src/components/StatusBar/StatusBar.vue
- [ ] T030 [US4] Add 'rename' emit and event handler to StatusBar in frontend/src/components/StatusBar/StatusBar.vue
- [ ] T031 [US4] Add rename dialog state (showRenameDialog, renamingConversationId) to App in frontend/src/components/App/App.vue
- [ ] T032 [US4] Add handleRenameRequest and handleRenameSave handlers to App in frontend/src/components/App/App.vue
- [ ] T033 [US4] Import and render RenameDialog conditionally in App template in frontend/src/components/App/App.vue
- [ ] T034 [US4] Wire up StatusBar rename event to App handler in frontend/src/components/App/App.vue

**Checkpoint**: Rename from status bar works. Verify:
- Ellipsis menu appears in status bar (not for "New Conversation")
- Menu opens on click with "Rename" option
- Rename dialog shows with current title pre-filled
- Title validation prevents empty titles
- Save updates title in status bar and history sidebar
- Cancel preserves original title

---

## Phase 6: User Story 5 - Rename from History Sidebar (Priority: P2)

**Goal**: Add ellipsis menu on conversation items in history sidebar with rename option

**Independent Test**: Hover conversation in sidebar, click ellipsis, rename, verify title updates

### Implementation for User Story 5

- [ ] T035 [US5] Import TitleMenu component in frontend/src/components/HistoryBar/HistoryBar.vue
- [ ] T036 [US5] Add TitleMenu to conversation-item template (show on hover) in frontend/src/components/HistoryBar/HistoryBar.vue
- [ ] T037 [US5] Add CSS for ellipsis menu positioning within conversation items in frontend/src/components/HistoryBar/HistoryBar.vue
- [ ] T038 [US5] Add CSS for show-on-hover behavior for ellipsis icon in frontend/src/components/HistoryBar/HistoryBar.vue
- [ ] T039 [US5] Add 'rename-conversation' emit with conversation.id in frontend/src/components/HistoryBar/HistoryBar.vue
- [ ] T040 [US5] Handle rename-conversation event from HistoryBar in App in frontend/src/components/App/App.vue

**Checkpoint**: Rename from history sidebar works. Verify:
- Ellipsis appears on hover over conversation items
- Menu opens with "Rename" option
- Rename dialog shows current title
- Saving updates title everywhere
- Works for both active and inactive conversations

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [ ] T041 [P] Run frontend test suite: `cd frontend && npm test`
- [ ] T042 [P] Verify all acceptance scenarios from spec.md manually
- [ ] T043 Test title truncation with very long titles (>200 characters)
- [ ] T044 Test special characters in titles (emojis, newlines, quotes)
- [ ] T045 Test rapid conversation switching (title updates correctly)
- [ ] T046 Verify CSS uses existing design system variables consistently
- [ ] T047 Remove any unused imports or dead code
- [ ] T048 Test in multiple browsers (Chrome, Firefox, Safari, Edge)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (T006 for auto-title)
- **User Story 3 (Phase 4)**: Depends on Foundational - Can run parallel with US1
- **User Story 4 (Phase 5)**: Depends on Foundational (T007-T009 for rename function)
- **User Story 5 (Phase 6)**: Depends on User Story 4 (reuses TitleMenu, RenameDialog)
- **Polish (Phase 7)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - Independent
- **User Story 3 (P1)**: Can start after Foundational - Can run parallel with US1
- **User Story 4 (P2)**: Can start after Foundational - Creates shared rename components
- **User Story 5 (P2)**: Depends on US4 components (TitleMenu, RenameDialog)

### Within Each User Story

- Template changes before style changes
- Parent component changes after child component creation
- App.vue wiring after component implementation

### Parallel Opportunities

- T002, T003, T004, T005 (Setup) can run in parallel
- T010-T013 (US1 StatusBar) can run in parallel - same file but independent sections
- US1 (Phase 3) and US3 (Phase 4) can run in parallel after Foundational
- T041, T042 (testing) can run in parallel

---

## Parallel Example: Setup Phase

```bash
# Launch all setup verification tasks together:
Task: "Verify existing tests pass"
Task: "Review current StatusBar implementation"
Task: "Review current HistoryBar implementation"
Task: "Review current useConversations composable"
```

---

## Parallel Example: User Story 1 & 3

```bash
# After Foundational phase, these can run in parallel:
# Developer A: User Story 1 (StatusBar title display)
# Developer B: User Story 3 (HistoryBar title-only)
```

---

## Implementation Strategy

### MVP First (User Story 1 + 3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (auto-title enhancement)
3. Complete Phase 3: User Story 1 (StatusBar title display)
4. Complete Phase 4: User Story 3 (HistoryBar title-only)
5. **STOP and VALIDATE**: Titles display correctly everywhere
6. Deploy/demo - basic title feature complete

### Full Feature (Add Rename)

1. Complete MVP (above)
2. Complete Phase 5: User Story 4 (Rename from StatusBar)
3. Complete Phase 6: User Story 5 (Rename from HistoryBar)
4. Complete Phase 7: Polish
5. Full feature complete with rename capability

### Recommended Order (Solo Developer)

1. Phase 1-2: Setup + Foundational (~30 min)
2. Phase 3: US1 StatusBar title (~30 min)
3. Phase 4: US3 HistoryBar title-only (~20 min)
4. Phase 5: US4 Rename from StatusBar (~1 hour) - includes creating shared components
5. Phase 6: US5 Rename from HistoryBar (~30 min) - reuses US4 components
6. Phase 7: Polish (~30 min)

**Total estimated time**: ~3.5 hours

---

## Notes

- [P] tasks = different files or independent sections, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable after Foundational phase
- No tests explicitly requested - manual verification at checkpoints
- Commit after each phase for easy rollback
- Backend already complete - no API changes needed
- All styling should use existing CSS variables (--chat-max-width, --color-*, etc.)
