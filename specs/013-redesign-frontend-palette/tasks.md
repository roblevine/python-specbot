# Tasks: Frontend Palette and Layout Redesign

**Input**: Design documents from `/specs/013-redesign-frontend-palette/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: No test tasks included (not explicitly requested in spec). Visual verification steps provided at each checkpoint.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/`, `frontend/public/`
- All paths relative to repository root

---

## Phase 1: Setup

**Purpose**: Verify current state and prepare for styling changes

- [x] T001 Verify frontend dev server runs without errors: `cd frontend && npm run dev`
- [x] T002 [P] Review current color variables in frontend/public/styles/global.css
- [x] T003 [P] Take screenshots of current UI for before/after comparison

**Checkpoint**: Development environment ready, baseline established

---

## Phase 2: Foundational (CSS Variables)

**Purpose**: Add new CSS variables that all user stories depend on

**⚠️ CRITICAL**: User stories 1-6 depend on these variables being defined first

- [x] T004 Add warm palette color variables to :root in frontend/public/styles/global.css
- [x] T005 Add --chat-max-width: 768px variable in frontend/public/styles/global.css
- [x] T006 Add --font-size-xs: 0.75rem variable in frontend/public/styles/global.css
- [x] T007 Add --collapsed-sidebar-margin: 12px variable in frontend/public/styles/global.css

**Checkpoint**: All new CSS variables defined - user story implementation can begin

---

## Phase 3: User Story 1 - Visual Refresh with Warm Color Palette (Priority: P1) 🎯 MVP

**Goal**: Replace grey/blue palette with warm earthy colors (#FFDBBB, #CCBEB1, #997E67, #664930)

**Independent Test**: Load application and verify cream background, warm tones throughout, WCAG AA contrast compliance

### Implementation for User Story 1

- [x] T008 [US1] Update --color-background to var(--color-warm-cream) in frontend/public/styles/global.css
- [x] T009 [US1] Update --color-surface to var(--color-warm-cream) in frontend/public/styles/global.css
- [x] T010 [US1] Update --color-border to var(--color-warm-brown) in frontend/public/styles/global.css
- [x] T011 [US1] Update --color-text-secondary to #664930 in frontend/public/styles/global.css
- [x] T012 [US1] Update --color-user-message-bg to var(--color-warm-tan) in frontend/public/styles/global.css
- [x] T013 [US1] Update sidebar background to use --color-warm-brown in frontend/src/components/HistoryBar/HistoryBar.vue
- [x] T014 [US1] Verify text contrast meets WCAG AA (4.5:1) for all color combinations
- [x] T015 [US1] Remove legacy --color-grey-* and --color-blue-* variables in frontend/public/styles/global.css

**Checkpoint**: Application displays warm color palette. Verify:
- Cream background (#FFDBBB)
- Sidebar uses warm brown (#997E67)
- All text is readable

---

## Phase 4: User Story 2 - Centered Chat Layout with System Responses as Main Content (Priority: P1)

**Goal**: System messages centered without bubbles, user messages right-aligned with subtle bubble

**Independent Test**: Send a message, verify system response has no bubble (transparent bg), user message is right-aligned with tan bubble

### Implementation for User Story 2

- [x] T016 [US2] Update --color-system-message-bg to transparent in frontend/public/styles/global.css
- [x] T017 [US2] Remove border-radius from system message styling in frontend/src/components/ChatArea/MessageBubble.vue
- [x] T018 [US2] Remove padding/margin bubble styling from system messages in frontend/src/components/ChatArea/MessageBubble.vue
- [x] T019 [US2] Set system message width to 100% (full container) in frontend/src/components/ChatArea/MessageBubble.vue
- [x] T020 [US2] Ensure user messages remain right-aligned (flex-end) in frontend/src/components/ChatArea/MessageBubble.vue
- [x] T021 [US2] Set user message max-width to 80% in frontend/src/components/ChatArea/MessageBubble.vue
- [x] T022 [US2] Verify user message uses tan bubble background (--color-warm-tan) in frontend/src/components/ChatArea/MessageBubble.vue

**Checkpoint**: Message layout complete. Verify:
- System messages flow as main content (no bubbles)
- User messages are right-aligned with tan background
- Conversation reads naturally

---

## Phase 5: User Story 3 - Constrained Chat Width (Priority: P2)

**Goal**: Constrain chat content area to ~768px centered horizontally

**Independent Test**: Resize browser to wide viewport (>1200px), verify chat content stays centered at 768px max width

### Implementation for User Story 3

- [x] T023 [US3] Add max-width and auto margins to messages container in frontend/src/components/ChatArea/ChatArea.vue
- [x] T024 [US3] Add max-width and auto margins to input container in frontend/src/components/InputArea/InputArea.vue
- [x] T025 [US3] Add horizontal padding for narrow viewport graceful degradation in frontend/src/components/ChatArea/ChatArea.vue
- [x] T026 [US3] Verify responsive behavior on narrow screens (<768px) in frontend/src/components/ChatArea/ChatArea.vue

**Checkpoint**: Width constraints working. Verify:
- Chat content centered on wide screens
- Max-width ~768px maintained
- Input area matches chat width
- Narrow screens still work

---

## Phase 6: User Story 4 - Refined Metadata Typography (Priority: P2)

**Goal**: Smaller, subtle metadata text (timestamps, model indicators)

**Independent Test**: View messages and verify metadata text is visually smaller and less prominent than message content

### Implementation for User Story 4

- [x] T027 [P] [US4] Update timestamp styling to use --font-size-xs in frontend/src/components/ChatArea/MessageBubble.vue
- [x] T028 [P] [US4] Update model indicator styling to use --font-size-xs in frontend/src/components/ModelSelector/ModelSelector.vue
- [x] T029 [P] [US4] Update StatusBar metadata to use --font-size-xs in frontend/src/components/StatusBar/StatusBar.vue
- [x] T030 [US4] Apply --color-text-secondary to all metadata elements for reduced prominence

**Checkpoint**: Metadata typography refined. Verify:
- Timestamps smaller than message text
- Model indicators subtle
- Clear visual hierarchy maintained

---

## Phase 7: User Story 5 - Modest Button Styling (Priority: P2)

**Goal**: Ghost-style buttons with subtle borders and hover states

**Independent Test**: View and interact with buttons, verify subtle appearance with clear but modest hover/focus feedback

### Implementation for User Story 5

- [x] T031 [P] [US5] Update New Conversation button to ghost style in frontend/src/components/HistoryBar/HistoryBar.vue
- [x] T032 [P] [US5] Update collapse/expand button to ghost style in frontend/src/components/HistoryBar/HistoryBar.vue
- [x] T033 [P] [US5] Update send button to ghost style in frontend/src/components/InputArea/InputArea.vue
- [x] T034 [US5] Ensure all buttons have transparent background with subtle border
- [x] T035 [US5] Reduce hover effect intensity (subtle background change)
- [x] T036 [US5] Verify focus indicators meet accessibility requirements (visible outline)

**Checkpoint**: Button styling complete. Verify:
- Buttons appear modest/subtle
- Clear hover state feedback
- Focus indicators visible for accessibility

---

## Phase 8: User Story 6 - Improved Collapsed Sidebar Margin (Priority: P3)

**Goal**: Fix expand button margin when sidebar is collapsed (minimum 8px from right edge)

**Independent Test**: Collapse sidebar and verify expand button has visible margin from right edge, easy to click

### Implementation for User Story 6

- [x] T037 [US6] Add right padding/margin to collapsed sidebar expand button in frontend/src/components/HistoryBar/HistoryBar.vue
- [x] T038 [US6] Use --collapsed-sidebar-margin (12px) for consistent spacing
- [x] T039 [US6] Verify clickable area remains reasonable (min 32px tap target)
- [x] T040 [US6] Test collapsed/expanded transition animation for smooth behavior

**Checkpoint**: Sidebar margin fixed. Verify:
- Expand button has visible margin from edge
- Easy to click/tap
- Transition remains smooth

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and validation

- [x] T041 [P] Run frontend test suite: `cd frontend && npm test`
- [x] T042 [P] Run E2E visual tests if available: `cd frontend && npm run test:e2e`
- [x] T043 Verify all WCAG AA contrast requirements met (use browser dev tools)
- [x] T044 Test in multiple browsers (Chrome, Firefox, Safari, Edge)
- [x] T045 Take after screenshots for comparison with T003 baseline
- [x] T046 Verify streaming indicator displays correctly in new layout
- [x] T047 Verify error messages display correctly with new color scheme
- [x] T048 Final code cleanup - remove any unused CSS

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 - can run in parallel if desired
  - US3, US4, US5 are all P2 - can run in parallel after US1/US2
  - US6 is P3 - lowest priority, can run anytime after Foundational
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - Independent of US1
- **User Story 3 (P2)**: Can start after Foundational - Independent of US1/US2
- **User Story 4 (P2)**: Can start after Foundational - Independent
- **User Story 5 (P2)**: Can start after Foundational - Independent
- **User Story 6 (P3)**: Can start after Foundational - Independent

### Within Each User Story

- CSS variable changes in global.css before component-specific changes
- Component styling after variables are defined
- Verification after implementation

### Parallel Opportunities

- T002, T003 (Setup) can run in parallel
- T027, T028, T029 (US4 metadata) can run in parallel - different files
- T031, T032, T033 (US5 buttons) can run in parallel - different components
- T041, T042 (testing) can run in parallel
- All user stories can be worked on in parallel after Foundational phase

---

## Parallel Example: User Story 4

```bash
# Launch all metadata styling tasks together (different files):
Task: "Update timestamp styling in MessageBubble.vue"
Task: "Update model indicator in ModelSelector.vue"
Task: "Update StatusBar metadata in StatusBar.vue"
```

---

## Parallel Example: User Story 5

```bash
# Launch all button styling tasks together (different components):
Task: "Update New Conversation button in HistoryBar.vue"
Task: "Update collapse/expand button in HistoryBar.vue"
Task: "Update send button in InputArea.vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CSS variables)
3. Complete Phase 3: User Story 1 (warm color palette)
4. **STOP and VALIDATE**: Visual inspection of color scheme
5. Deploy/demo if ready - app looks different but functional

### Incremental Delivery

1. Setup + Foundational → CSS variables ready
2. Add US1 (Color Palette) → Warm colors visible → Demo
3. Add US2 (Message Layout) → Chat feels like Claude → Demo
4. Add US3 (Width Constraint) → Better readability → Demo
5. Add US4 (Metadata) → Cleaner typography → Demo
6. Add US5 (Buttons) → Polished UI → Demo
7. Add US6 (Sidebar) → Final polish → Complete

### Recommended Order (Solo Developer)

1. Phase 1-2: Setup + Foundational (~15 min)
2. Phase 3: US1 Color Palette (~20 min)
3. Phase 4: US2 Message Layout (~30 min)
4. Phase 5: US3 Width Constraints (~15 min)
5. Phase 6: US4 Metadata Typography (~15 min)
6. Phase 7: US5 Button Styling (~20 min)
7. Phase 8: US6 Sidebar Margin (~10 min)
8. Phase 9: Polish (~20 min)

**Total estimated time**: ~2.5 hours

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and verifiable
- No tests explicitly requested - visual verification at checkpoints
- Commit after each phase or user story for easy rollback
- WCAG contrast research in research.md - white on #997E67 FAILS (use dark text)
