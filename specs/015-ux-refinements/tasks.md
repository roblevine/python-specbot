# Tasks: UX Refinements

**Input**: Design documents from `/specs/015-ux-refinements/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, quickstart.md

**Tests**: Unit tests included for datetime formatting utility per constitution Test-First Development requirement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for source, `frontend/tests/` for tests
- All changes are frontend-only; no backend modifications required

---

## Phase 1: Setup

**Purpose**: No setup tasks needed - this feature modifies existing components only

*No tasks - proceed directly to user stories*

---

## Phase 2: Foundational

**Purpose**: No foundational/blocking tasks - user stories are independent UI changes

*No tasks - proceed directly to user stories*

---

## Phase 3: User Story 1 - Deterministic Conversation Ordering (Priority: P1) 🎯 MVP

**Goal**: Fix non-deterministic conversation list ordering so conversations appear in consistent order (most recent first) across app restarts

**Independent Test**: Create 3+ conversations, close and reopen the app multiple times, verify the order is always the same (most recently active at top)

### Implementation for User Story 1

- [ ] T001 [US1] Add sorting logic after fetching conversations in `frontend/src/state/useConversations.js` - sort by `updatedAt` descending with `id` as secondary key for tie-breaking
- [ ] T002 [US1] Verify sorting is applied in both `loadFromStorage()` success path (line ~169) and localStorage fallback path (line ~192) in `frontend/src/state/useConversations.js`

**Checkpoint**: Conversations now appear in deterministic order across app restarts

---

## Phase 4: User Story 2 - Clear Button State Visibility (Priority: P2)

**Goal**: Make enabled/disabled button states visually distinct so users can immediately see when buttons are clickable

**Independent Test**: With empty chat input, send button should appear muted/disabled; with text entered, send button should appear prominent/clickable. Same pattern for all buttons.

### Implementation for User Story 2

- [ ] T003 [P] [US2] Update `.send-button` styles in `frontend/src/components/InputArea/InputArea.vue` - enabled state: solid `--color-primary` background with white text; disabled state: transparent with muted colors
- [ ] T004 [P] [US2] Update `.new-conversation-btn` styles in `frontend/src/components/HistoryBar/HistoryBar.vue` to match the enabled button pattern (solid background when clickable)
- [ ] T005 [US2] Review other buttons (collapse-button, error-toggle, dialog buttons) and ensure consistent enabled/disabled styling across the application

**Checkpoint**: All buttons clearly show enabled vs disabled states

---

## Phase 5: User Story 3 - Message Datetime Display (Priority: P3)

**Goal**: Display datetime metadata on all messages in the format "Sun 18-Jan-26 09:58am" with model indicator stacked below datetime on system messages

**Independent Test**: Send a message and verify datetime appears in correct format; receive a response and verify datetime and model indicator are stacked vertically

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T006 [P] [US3] Create unit tests for `formatMessageDatetime()` in `frontend/tests/unit/utils/dateFormatter.test.js` - test various dates, times (midnight, noon, PM times), edge cases

### Implementation for User Story 3

- [ ] T007 [US3] Create `formatMessageDatetime(isoTimestamp)` utility function in `frontend/src/utils/dateFormatter.js` that returns format "Sun 18-Jan-26 09:58am"
- [ ] T008 [US3] Verify unit tests pass for the datetime formatter
- [ ] T009 [US3] Update `MessageBubble.vue` to import and use `formatMessageDatetime` - replace `formattedTime` computed with `formattedDatetime` in `frontend/src/components/ChatArea/MessageBubble.vue`
- [ ] T010 [US3] Update `MessageBubble.vue` template to wrap datetime and model indicator in a `.message-metadata` container with vertical stacking in `frontend/src/components/ChatArea/MessageBubble.vue`
- [ ] T011 [US3] Update CSS styles in `MessageBubble.vue` for `.message-metadata`, `.message-datetime` (replacing `.message-timestamp`), and adjust `.model-indicator` to remove right-alignment

**Checkpoint**: All messages display datetime in correct format, model indicator stacked below datetime on system messages

---

## Phase 6: User Story 4 - Model Selector Relocation (Priority: P4)

**Goal**: Move model selector from main chat area to directly above the chat input within the input pane

**Independent Test**: Model selector should appear above the chat input textarea, within the input area component, not in the main chat/message display area

### Implementation for User Story 4

- [ ] T012 [P] [US4] Remove `<ModelSelector />` component from template (line 24) in `frontend/src/components/App/App.vue`
- [ ] T013 [P] [US4] Remove ModelSelector import (line 47) and component registration (line 62) from `frontend/src/components/App/App.vue`
- [ ] T014 [US4] Add ModelSelector import and component registration to `frontend/src/components/InputArea/InputArea.vue`
- [ ] T015 [US4] Add `<ModelSelector />` to InputArea.vue template above the `.input-container` div in `frontend/src/components/InputArea/InputArea.vue`
- [ ] T016 [US4] Adjust InputArea.vue styles to accommodate the model selector (may need padding/margin adjustments) in `frontend/src/components/InputArea/InputArea.vue`

**Checkpoint**: Model selector appears within the input pane, above the chat input

---

## Phase 7: User Story 5 - Remove Status Indicator (Priority: P5)

**Goal**: Remove the status indicator (dot and text) from the StatusBar, keeping only the title and rename functionality

**Independent Test**: No status indicator dot or status text should be visible in the header; title and rename button should still work

### Implementation for User Story 5

- [ ] T017 [P] [US5] Remove `.status-section` containing `.status-indicator` and `.status-text` elements from template in `frontend/src/components/StatusBar/StatusBar.vue`
- [ ] T018 [P] [US5] Remove `status` and `statusType` props definitions from `frontend/src/components/StatusBar/StatusBar.vue`
- [ ] T019 [P] [US5] Remove related CSS styles (`.status-section`, `.status-indicator`, `.status-text`, `.indicator-*` classes) from `frontend/src/components/StatusBar/StatusBar.vue`
- [ ] T020 [US5] Remove `:status` and `:status-type` prop bindings from StatusBar in `frontend/src/components/App/App.vue` (line 5-6)
- [ ] T021 [US5] Remove unused `status` and `statusType` variables from App.vue setup if no longer needed elsewhere in `frontend/src/components/App/App.vue`

**Checkpoint**: Status indicator removed, StatusBar shows only title with rename functionality

---

## Phase 8: Polish & Verification

**Purpose**: Final verification and cleanup

- [ ] T022 Run all frontend tests to verify no regressions: `cd frontend && npm test`
- [ ] T023 Manual verification per quickstart.md testing checklist
- [ ] T024 [P] Remove any dead code or unused imports across modified files

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: N/A - no setup tasks
- **Foundational (Phase 2)**: N/A - no foundational tasks
- **User Stories (Phases 3-7)**: All independent - can proceed in any order or in parallel
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - modifies only useConversations.js
- **User Story 2 (P2)**: Independent - modifies only button CSS styles
- **User Story 3 (P3)**: Independent - creates new utility and modifies MessageBubble.vue
- **User Story 4 (P4)**: Independent - moves component between App.vue and InputArea.vue
- **User Story 5 (P5)**: Independent - modifies only StatusBar.vue and removes props from App.vue

### Within Each User Story

- For US3: Tests (T006) MUST be written and FAIL before implementation (T007)
- Tasks within a story that modify the same file should be done sequentially
- Tasks marked [P] can run in parallel (different files)

### Parallel Opportunities

- US1, US2, US4, US5 can all be worked on in parallel (different files)
- US3 tasks T006-T008 (formatter) can run parallel to T009-T011 prep work
- T003 and T004 (button styling) can run in parallel
- T012 and T013 (App.vue cleanup) can run in parallel
- T017, T018, T019 (StatusBar changes) can run in parallel

---

## Parallel Example: All User Stories

```bash
# All user stories can start simultaneously after spec review:
# Developer A: User Story 1 (conversation ordering)
# Developer B: User Story 2 (button styling)
# Developer C: User Story 3 (datetime display)
# Developer D: User Story 4 (model selector relocation)
# Developer E: User Story 5 (status indicator removal)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 3: User Story 1 (Deterministic Ordering)
2. **STOP and VALIDATE**: Test conversation ordering independently
3. Deploy/demo if ready - fixes the most visible bug

### Incremental Delivery

1. Add User Story 1 → Test independently → Commit (MVP - fixes ordering bug)
2. Add User Story 2 → Test independently → Commit (better button UX)
3. Add User Story 3 → Test independently → Commit (datetime metadata)
4. Add User Story 4 → Test independently → Commit (model selector position)
5. Add User Story 5 → Test independently → Commit (cleaner UI)
6. Complete Polish phase → Final verification → Ready for PR

### Single Developer Strategy

Follow priority order: P1 → P2 → P3 → P4 → P5

Each story is a complete increment that can be committed and demonstrated independently.

---

## Notes

- All changes are frontend-only - no backend or API modifications
- No schema migrations required
- Each user story is independently testable and deployable
- Commit after each user story for clean git history
- T006 (tests) must fail before T007-T008 implementation per TDD
