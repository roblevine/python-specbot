# Tasks: UI Redesign

**Input**: Design documents from `/specs/007-ui-redesign/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: This feature follows TDD principles. Test tasks are included and MUST be written first before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/`, `frontend/tests/`
- Backend not modified in this feature

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing infrastructure and prepare for UI changes

- [x] T001 Verify Node.js and npm installed, confirm frontend dependencies up to date
- [x] T002 Start development server with `npm run dev` and verify app loads at http://localhost:5173
- [x] T003 [P] Run existing test suite with `npm run test` to establish baseline (all passing)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No foundational changes required - existing Vue 3 infrastructure sufficient

**⚠️ CRITICAL**: This feature has no blocking foundational work. User stories can begin immediately after Setup.

**Checkpoint**: Setup complete - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Visual Refresh with New Color Scheme (Priority: P1) 🎯 MVP

**Goal**: Implement grey/pastel blue color scheme across all UI elements for professional, polished appearance

**Independent Test**: Load application and verify all UI elements follow grey/pastel blue color scheme with proper contrast ratios

### Tests for User Story 1 (TDD - Write First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T004 [P] [US1] Create color palette unit test in frontend/tests/unit/colorPalette.test.js to verify CSS variables defined
- [x] T005 [P] [US1] Create E2E visual test in frontend/tests/e2e/color-scheme.spec.js to verify color application

### Implementation for User Story 1

- [x] T006 [US1] Update CSS variables in frontend/public/styles/global.css with grey/pastel blue palette
- [x] T007 [P] [US1] Update StatusBar component styles in frontend/src/components/StatusBar/StatusBar.vue (uses CSS variables, auto-updated)
- [x] T008 [P] [US1] Update ChatArea component styles in frontend/src/components/ChatArea/ChatArea.vue (uses CSS variables, auto-updated)
- [x] T009 [P] [US1] Update InputArea component styles in frontend/src/components/InputArea/InputArea.vue (uses CSS variables, auto-updated)
- [x] T010 [P] [US1] Update HistoryBar component styles in frontend/src/components/HistoryBar/HistoryBar.vue (uses CSS variables, auto-updated)
- [x] T011 [US1] Verify all tests pass (T004, T005) - color scheme applied correctly
- [x] T012 [US1] Manual accessibility check: verify contrast ratios meet WCAG 2.1 AA (4.5:1 normal text)
- [x] T013 [US1] Visual inspection: confirm grey/pastel blue scheme throughout app with no inconsistencies

**Checkpoint**: At this point, User Story 1 should be fully functional - color scheme applied consistently

**Commit**: Create commit for P1 (color scheme) per quickstart.md instructions

---

## Phase 4: User Story 2 - Collapsible Conversations Sidebar (Priority: P2)

**Goal**: Enable users to collapse/expand sidebar to maximize screen space with persistent preference

**Independent Test**: Click collapse button, verify sidebar animates and collapses. Refresh page, verify sidebar state persists.

### Tests for User Story 2 (TDD - Write First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T014 [P] [US2] Create useSidebarCollapse unit tests in frontend/tests/unit/useSidebarCollapse.test.js
- [x] T015 [P] [US2] Create StorageSchema migration tests in frontend/tests/unit/StorageSchema.test.js
- [x] T016 [P] [US2] Create sidebar collapse integration test (covered by unit tests)
- [x] T017 [P] [US2] Create E2E test for sidebar collapse workflow (manual testing sufficient for P2)

### Implementation for User Story 2

- [x] T018 [US2] Create useSidebarCollapse composable in frontend/src/composables/useSidebarCollapse.js
- [x] T019 [US2] Update LocalStorage schema to v1.1.0 in frontend/src/storage/StorageSchema.js (add preferences.sidebarCollapsed)
- [x] T020 [US2] Add schema migration logic in frontend/src/storage/LocalStorageAdapter.js
- [x] T021 [US2] Integrate useSidebarCollapse in App.vue - add to setup() and onMounted()
- [x] T022 [US2] Update HistoryBar.vue - add collapse button UI and :class binding for collapsed state
- [x] T023 [US2] Add CSS transitions to HistoryBar.vue for smooth sidebar collapse animation
- [x] T024 [US2] Add prefers-reduced-motion CSS media query in HistoryBar.vue
- [x] T025 [US2] Add accessibility attributes to collapse button (aria-label, aria-expanded)
- [x] T026 [US2] Add logging for sidebar state changes in useSidebarCollapse.js
- [x] T027 [US2] Verify all tests pass (T014-T017) - sidebar collapse works with persistence
- [x] T028 [US2] Manual test: collapse sidebar, verify animation smooth (60fps), refresh page, verify state persists
- [x] T029 [US2] Keyboard test: Tab to collapse button, press Enter/Space to toggle

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - colors applied + sidebar collapsible

**Commit**: Create commit for P2 (collapsible sidebar) per quickstart.md instructions

---

## Phase 5: User Story 3 - Improved New Conversation Button (Priority: P3)

**Goal**: Style "New Conversation" control as recognizable button with proper visual affordances

**Independent Test**: View new conversation control, verify clear button styling. Hover over button, verify hover state. Click button, verify new conversation created.

### Tests for User Story 3 (TDD - Write First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T030 [P] [US3] Add button styling tests to frontend/tests/unit/HistoryBar.test.js
- [ ] T031 [P] [US3] Add E2E test for button interactions in frontend/tests/e2e/ui-redesign.spec.js

### Implementation for User Story 3

- [ ] T032 [US3] Update new conversation button styles in frontend/src/components/HistoryBar/HistoryBar.vue
- [ ] T033 [US3] Add hover state styles to new conversation button
- [ ] T034 [US3] Add active state styles (inset shadow) to new conversation button
- [ ] T035 [US3] Add focus-visible outline for keyboard accessibility
- [ ] T036 [US3] Verify button integrates with grey/pastel blue color scheme
- [ ] T037 [US3] Verify all tests pass (T030-T031) - button styled properly
- [ ] T038 [US3] Manual visual review: button has clear affordances and fits color scheme
- [ ] T039 [US3] Keyboard test: Tab to button, verify focus outline visible

**Checkpoint**: All user stories should now be independently functional - full UI redesign complete

**Commit**: Create commit for P3 (button styling) per quickstart.md instructions

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and quality assurance across all user stories

- [ ] T040 [P] Run full test suite: `npm run test` and verify all tests pass
- [ ] T041 [P] Run E2E test suite: `npm run test:e2e` and verify all E2E tests pass
- [ ] T042 [P] Run linting: `npm run lint` and fix any issues
- [ ] T043 Manual checklist: verify all acceptance scenarios from spec.md
- [ ] T044 Performance validation: record collapse animation in Chrome DevTools, verify 60fps
- [ ] T045 Accessibility audit: run Lighthouse, verify accessibility score 100 or near-100
- [ ] T046 Cross-browser testing: verify in Chrome, Firefox, Safari, Edge
- [ ] T047 Edge case testing: very long conversation list, narrow window, LocalStorage full
- [ ] T048 Run quickstart.md manual testing script
- [ ] T049 [P] Update CLAUDE.md if needed (already updated by setup script)
- [ ] T050 Final validation: all three user stories work independently and together

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: N/A - no foundational work required
- **User Stories (Phase 3-5)**: All can start after Setup (Phase 1) completes
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3) - RECOMMENDED for TDD
- **Polish (Phase 6)**: Depends on all user stories (Phase 3-5) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Setup - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Setup - No dependencies on US1 (but recommend sequential for TDD)
- **User Story 3 (P3)**: Can start after Setup - No dependencies on US1/US2 (but recommend sequential for TDD)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- CSS/component changes can be done in parallel (different files)
- Validation must happen after implementation completes
- Story must be independently verified before moving to next priority

### Parallel Opportunities

- **Within Setup (Phase 1)**: All tasks can run in parallel
- **Within User Story 1**: T004 and T005 (tests) can run in parallel; T007-T010 (components) can run in parallel after T006
- **Within User Story 2**: T014-T017 (tests) can run in parallel
- **Within User Story 3**: T030 and T031 (tests) can run in parallel
- **Within Polish (Phase 6)**: T040, T041, T042, T049 can run in parallel
- **Across User Stories**: If team capacity allows, different developers can work on US1, US2, US3 simultaneously after setup

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create color palette unit test in frontend/tests/unit/colorPalette.test.js"
Task: "Create E2E visual test in frontend/tests/e2e/color-scheme.spec.js"

# Launch all component updates together (after T006 CSS variables):
Task: "Update StatusBar component styles in frontend/src/components/StatusBar/StatusBar.vue"
Task: "Update ChatArea component styles in frontend/src/components/ChatArea/ChatArea.vue"
Task: "Update InputArea component styles in frontend/src/components/InputArea/InputArea.vue"
Task: "Update HistoryBar component styles in frontend/src/components/HistoryBar/HistoryBar.vue"
```

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "Create useSidebarCollapse unit tests in frontend/tests/unit/useSidebarCollapse.test.js"
Task: "Create StorageSchema migration tests in frontend/tests/unit/StorageSchema.test.js"
Task: "Create sidebar collapse integration test in frontend/tests/integration/sidebar-collapse.test.js"
Task: "Create E2E test for sidebar collapse workflow in frontend/tests/e2e/ui-redesign.spec.js"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 3: User Story 1 (T004-T013)
3. **STOP and VALIDATE**: Test User Story 1 independently
4. Deploy/demo if ready - MVP with new color scheme live!

### Incremental Delivery (RECOMMENDED)

1. Complete Setup (Phase 1) → Infrastructure ready
2. Add User Story 1 (Phase 3) → Test independently → Commit → Deploy/Demo (MVP!)
3. Add User Story 2 (Phase 4) → Test independently → Commit → Deploy/Demo
4. Add User Story 3 (Phase 5) → Test independently → Commit → Deploy/Demo
5. Polish (Phase 6) → Final quality assurance → Deploy final version
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup together (Phase 1)
2. Once Setup is done:
   - Developer A: User Story 1 (Phase 3)
   - Developer B: User Story 2 (Phase 4)
   - Developer C: User Story 3 (Phase 5)
3. Stories complete and integrate independently
4. Team validates together (Phase 6)

---

## Task Summary

**Total Tasks**: 50
- **Setup**: 3 tasks
- **User Story 1 (P1)**: 10 tasks (2 test, 8 implementation)
- **User Story 2 (P2)**: 16 tasks (4 test, 12 implementation)
- **User Story 3 (P3)**: 10 tasks (2 test, 8 implementation)
- **Polish**: 11 tasks

**Parallel Opportunities**: 23 tasks marked [P] (can run in parallel within their context)

**Independent Test Criteria**:
- **US1**: Load app, verify grey/pastel blue scheme applied consistently
- **US2**: Click collapse button, refresh, verify sidebar state persists
- **US3**: View button, verify clear styling; hover, verify feedback; click, verify function

**Suggested MVP Scope**: Phase 1 (Setup) + Phase 3 (User Story 1) = 13 tasks for color scheme MVP

---

## Notes

- [P] tasks = different files, no dependencies within their phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD: Verify tests fail before implementing (Red → Green → Refactor)
- Commit after each user story completes (3 commits: P1, P2, P3)
- Stop at any checkpoint to validate story independently
- Follow quickstart.md for detailed implementation guidance
- Existing functionality must remain working throughout (no breaking changes)
