# Tasks: Conversation UX Fixes

**Input**: Design documents from `/specs/022-conversation-ux-fixes/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Unit tests included per plan.md constitution check ("Unit tests for sorting, focus tracking")

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for source, `frontend/tests/unit/` for tests
- All changes are frontend-only per plan.md

---

## Phase 1: Setup

**Purpose**: Verify development environment and understand existing code

- [x] T001 Verify frontend development server starts with `npm run dev` in frontend/
- [x] T002 [P] Review existing HistoryBar.vue component structure in frontend/src/components/HistoryBar/HistoryBar.vue
- [x] T003 [P] Review existing InputArea.vue component structure in frontend/src/components/InputArea/InputArea.vue
- [x] T004 [P] Review existing useConversations.js state management in frontend/src/state/useConversations.js

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create shared utilities needed by multiple user stories

**⚠️ CRITICAL**: US3 (Timestamps) depends on the date formatter utility

- [x] T005 Create dateFormatter.js utility module in frontend/src/utils/dateFormatter.js with formatConversationTimestamp function
- [x] T006 Write unit tests for dateFormatter in frontend/tests/unit/dateFormatter.test.js

**Checkpoint**: Date formatter ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Conversation History Ordering (Priority: P1) 🎯 MVP

**Goal**: New/updated conversations appear at top of sidebar list

**Independent Test**: Create new conversation → verify it appears at top. Send message in older conversation → verify it moves to top.

### Tests for User Story 1

- [x] T007 [P] [US1] Write unit test for sortConversationsByRecent function in frontend/tests/unit/useConversations.test.js
- [x] T008 [P] [US1] Write unit test for sort being called after createConversation in frontend/tests/unit/useConversations.test.js
- [x] T009 [P] [US1] Write unit test for sort being called after addMessage in frontend/tests/unit/useConversations.test.js

### Implementation for User Story 1

- [x] T010 [US1] Verify sortConversationsByRecent exists and sorts by updatedAt descending in frontend/src/state/useConversations.js
- [x] T011 [US1] Add sortConversationsByRecent call after createConversation mutation in frontend/src/state/useConversations.js
- [x] T012 [US1] Add sortConversationsByRecent call after addMessage mutation in frontend/src/state/useConversations.js
- [x] T013 [US1] Add sortConversationsByRecent call after any conversation update (title change, etc) in frontend/src/state/useConversations.js
- [x] T014 [US1] Manual verification: create conversation, verify at top; send message in old conversation, verify moves to top

**Checkpoint**: User Story 1 complete - conversations now sort correctly by recency

---

## Phase 4: User Story 2 - Maintain Chat Input Focus (Priority: P1)

**Goal**: Focus stays in message input after AI response completes (keyboard-only workflow)

**Independent Test**: Type message → press Enter → wait for response → verify cursor still in input box without clicking

### Tests for User Story 2

- [x] T015 [P] [US2] Write unit test for focus state tracking (hadFocusBeforeSend) in frontend/tests/unit/InputArea.test.js
- [x] T016 [P] [US2] Write unit test for focus restoration after response complete in frontend/tests/unit/InputArea.test.js

### Implementation for User Story 2

- [x] T017 [US2] Add inputRef template ref for textarea element in frontend/src/components/InputArea/InputArea.vue
- [x] T018 [US2] Add hadFocusBeforeSend reactive ref to track focus state before send in frontend/src/components/InputArea/InputArea.vue
- [x] T019 [US2] Capture focus state in handleSend function (document.activeElement === inputRef.value) in frontend/src/components/InputArea/InputArea.vue
- [x] T020 [US2] Add blur event handler to detect when user clicks elsewhere in frontend/src/components/InputArea/InputArea.vue
- [x] T021 [US2] Restore focus after response complete using nextTick if hadFocusBeforeSend was true in frontend/src/components/InputArea/InputArea.vue
- [x] T022 [US2] Manual verification: send 5 consecutive messages using keyboard only without clicking input

**Checkpoint**: User Story 2 complete - focus retention enables keyboard-only workflow

---

## Phase 5: User Story 3 - Add Timestamps to Conversation List (Priority: P2)

**Goal**: Display last activity date/time below each conversation title

**Independent Test**: View sidebar → each conversation shows timestamp (time for today, "Yesterday" for yesterday, date for older)

### Implementation for User Story 3

- [x] T023 [US3] Import formatConversationTimestamp from dateFormatter.js in frontend/src/components/HistoryBar/HistoryBar.vue
- [x] T024 [US3] Add timestamp display element below conversation title in template in frontend/src/components/HistoryBar/HistoryBar.vue
- [x] T025 [US3] Add CSS styling for timestamp subtext (smaller font, muted color) in frontend/src/components/HistoryBar/HistoryBar.vue
- [x] T026 [US3] Manual verification: check timestamp displays correctly for today/yesterday/older conversations

**Checkpoint**: User Story 3 complete - timestamps visible in conversation list

---

## Phase 6: User Story 4 - Compact Conversation List Styling (Priority: P2)

**Goal**: Reduce font size and spacing to show 30-50% more conversations

**Independent Test**: Count visible conversations before/after → verify at least 30% increase

### Implementation for User Story 4

- [x] T027 [US4] Reduce font-size for conversation title (target: ~13px from ~16px) in frontend/src/components/HistoryBar/HistoryBar.vue
- [x] T028 [US4] Reduce padding/margin for conversation list items in frontend/src/components/HistoryBar/HistoryBar.vue
- [x] T029 [US4] Reduce gap/spacing between conversation entries in frontend/src/components/HistoryBar/HistoryBar.vue
- [x] T030 [US4] Verify ellipsis truncation still works for long titles in frontend/src/components/HistoryBar/HistoryBar.vue
- [x] T031 [US4] Manual verification: count visible conversations and verify 30%+ increase

**Checkpoint**: User Story 4 complete - compact styling increases visible conversations

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and cleanup

- [x] T032 [P] Run full test suite to ensure no regressions with `npm run test` in frontend/
- [x] T033 [P] Test all edge cases from spec.md (empty list, very old timestamps, rapid messages, errors)
- [x] T034 Verify all acceptance scenarios from spec.md pass
- [x] T035 Run quickstart.md verification checklist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - creates dateFormatter utility needed by US3
- **User Stories (Phase 3-6)**: All depend on Phase 2 completion
  - US1 and US2 can run in parallel (different files)
  - US3 depends on dateFormatter from Phase 2
  - US4 can run in parallel with US1, US2, US3
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 - modifies useConversations.js only
- **User Story 2 (P1)**: Can start after Phase 2 - modifies InputArea.vue only
- **User Story 3 (P2)**: Can start after Phase 2 - modifies HistoryBar.vue, uses dateFormatter.js
- **User Story 4 (P2)**: Can start after Phase 2 - modifies HistoryBar.vue CSS only

**Note**: US3 and US4 both modify HistoryBar.vue, but US3 modifies template/imports while US4 modifies CSS only, so they can be done in sequence within the same file.

### Within Each User Story

- Tests FIRST, verify they FAIL before implementation
- Implementation in logical order
- Manual verification at end of each story

### Parallel Opportunities

```
Phase 1 (Setup):
  T002, T003, T004 can run in parallel (reading different files)

Phase 2 (Foundational):
  T005 → T006 (sequential: create utility, then test)

Phase 3 (US1):
  T007, T008, T009 can run in parallel (different test cases)
  T010 → T011 → T012 → T013 → T014 (sequential: verify, then modify)

Phase 4 (US2):
  T015, T016 can run in parallel (different test cases)
  T017 → T018 → T019 → T020 → T021 → T022 (sequential: build up feature)

Phase 5 (US3):
  T023 → T024 → T025 → T026 (sequential: single file modifications)

Phase 6 (US4):
  T027 → T028 → T029 → T030 → T031 (sequential: CSS refinement)

Phase 7 (Polish):
  T032, T033 can run in parallel
  T034 → T035 (sequential: verify then run checklist)
```

---

## Parallel Example: User Stories 1 and 2

Since US1 modifies `useConversations.js` and US2 modifies `InputArea.vue`, they can be worked on in parallel:

```bash
# Developer A: User Story 1
Task: "Write unit test for sortConversationsByRecent in useConversations.test.js"
Task: "Add sortConversationsByRecent call after createConversation in useConversations.js"

# Developer B: User Story 2 (simultaneously)
Task: "Write unit test for focus state tracking in InputArea.test.js"
Task: "Add inputRef template ref for textarea in InputArea.vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T006)
3. Complete Phase 3: User Story 1 (T007-T014)
4. **STOP and VALIDATE**: Test ordering independently
5. Deploy/demo if ready - ordering fix provides immediate value

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy (ordering fixed!)
3. Add User Story 2 → Test independently → Deploy (focus retention!)
4. Add User Story 3 → Test independently → Deploy (timestamps visible!)
5. Add User Story 4 → Test independently → Deploy (compact styling!)
6. Each story adds value without breaking previous stories

### Recommended Order

Given that US1 and US2 are both P1 (highest priority):
1. **US1 first** - it's a bug fix affecting core usability
2. **US2 second** - enhances keyboard workflow
3. **US3 third** - adds visual information
4. **US4 fourth** - visual polish

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All changes are frontend-only - no backend modifications needed

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 35 |
| Setup Tasks | 4 |
| Foundational Tasks | 2 |
| US1 Tasks | 8 |
| US2 Tasks | 8 |
| US3 Tasks | 4 |
| US4 Tasks | 5 |
| Polish Tasks | 4 |
| Parallel Opportunities | 12 tasks marked [P] |
| MVP Scope | US1 only (8 tasks after setup/foundational) |
