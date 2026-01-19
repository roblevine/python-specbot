# Tasks: Markdown Support

**Input**: Design documents from `/specs/017-markdown-support/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Included per constitution requirement (Test-First Development - Principle III)

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and create foundational utilities

- [x] T001 Install markdown dependencies: `cd frontend && npm install marked dompurify highlight.js`
- [x] T002 [P] Import highlight.js theme CSS in frontend/src/index.js

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core markdown rendering utility that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Create markdownRenderer.js utility with renderMarkdown() and escapeHtml() functions in frontend/src/utils/markdownRenderer.js
- [x] T004 [P] Write unit tests for markdownRenderer (sanitization, malformed markdown handling) in frontend/tests/unit/markdownRenderer.test.js
- [x] T005 Verify markdownRenderer tests FAIL before implementation, then implement to make them pass

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View Formatted AI Responses (Priority: P1) 🎯 MVP

**Goal**: Render markdown formatting in AI assistant messages including headers, bold, italic, inline code, code blocks, lists, links, and tables

**Independent Test**: Send a message that triggers AI response with markdown (e.g., "Show me a Python hello world example") and verify the response displays formatted code blocks, bold text, and lists correctly

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T006 [P] [US1] Unit test for MessageBubble markdown rendering (system messages render HTML, user messages render plain text) in frontend/tests/unit/MessageBubble.test.js
- [x] T007 [P] [US1] Integration test for streaming markdown rendering (no flicker, progressive formatting) in frontend/tests/integration/markdown-streaming.test.js

### Implementation for User Story 1

- [x] T008 [US1] Update MessageBubble.vue to use v-html with renderedContent computed property for system messages in frontend/src/components/ChatArea/MessageBubble.vue
- [x] T009 [US1] Add conditional rendering: markdown for sender='system', plain text for sender='user' in frontend/src/components/ChatArea/MessageBubble.vue
- [x] T010 [P] [US1] Add markdown element styles (.markdown-content h1-h6, p, ul, ol, code, pre, table, blockquote, a) in frontend/public/styles/global.css
- [x] T011 [US1] Add horizontal scrolling styles for code blocks and tables (overflow-x: auto) in frontend/public/styles/global.css
- [x] T012 [US1] Verify all US1 tests pass and manually test with streaming responses

**Checkpoint**: User Story 1 complete - basic markdown rendering works independently

---

## Phase 4: User Story 2 - View Syntax-Highlighted Code (Priority: P2)

**Goal**: Apply language-specific syntax highlighting to code blocks in AI responses

**Independent Test**: Ask AI for code in a specific language (e.g., "Write a JavaScript function") and verify the response shows color highlighting for keywords, strings, and comments

**Dependency**: Can start after Phase 2 (Foundational). Does NOT depend on US1 completion but enhances it.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T013 [P] [US2] Unit test for syntax highlighting (specified language highlights correctly, unspecified language shows plain code) in frontend/tests/unit/markdownRenderer.test.js

### Implementation for User Story 2

- [x] T014 [US2] Configure highlight.js with language imports (javascript, typescript, python, bash, json, css, xml, sql, markdown) in frontend/src/utils/markdownRenderer.js
- [x] T015 [US2] Register language aliases (js→javascript, ts→typescript, py→python, sh→bash, md→markdown, html→xml) in frontend/src/utils/markdownRenderer.js
- [x] T016 [US2] Configure marked.setOptions with highlight callback using hljs.highlight() for specified languages and hljs.highlightAuto() fallback in frontend/src/utils/markdownRenderer.js
- [x] T017 [P] [US2] Add syntax highlighting color styles or import highlight.js theme (vs2015.css for dark theme) in frontend/src/index.js
- [x] T018 [US2] Verify all US2 tests pass and manually test with code blocks in multiple languages

**Checkpoint**: User Stories 1 AND 2 work - markdown renders with syntax highlighting

---

## Phase 5: User Story 3 - Copy Code from Responses (Priority: P3)

**Goal**: Provide one-click copy functionality for code blocks with visual feedback

**Independent Test**: View an AI response containing a code block, click the copy button, verify code is copied to clipboard and visual feedback confirms success

**Dependency**: Can start after Phase 2 (Foundational). Does NOT depend on US1/US2 but integrates with them.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T019 [P] [US3] Unit test for CodeBlock component (copy button visible on hover, clipboard API called, success feedback shown) in frontend/tests/unit/CodeBlock.test.js

### Implementation for User Story 3

- [x] T020 [US3] Create CodeBlock.vue component with props: code (string), language (string|null) in frontend/src/components/ChatArea/CodeBlock.vue
- [x] T021 [US3] Add copy button that appears on hover with clipboard API integration in frontend/src/components/ChatArea/CodeBlock.vue
- [x] T022 [US3] Add copied state with visual feedback (checkmark icon or "Copied!" text for 2 seconds) in frontend/src/components/ChatArea/CodeBlock.vue
- [x] T023 [US3] Add CodeBlock component styles (position relative for button, hover states, button styling) in frontend/src/components/ChatArea/CodeBlock.vue or frontend/public/styles/global.css
- [x] T024 [US3] Update markdownRenderer.js to use custom renderer that wraps code blocks with CodeBlock component integration point in frontend/src/utils/markdownRenderer.js
- [x] T025 [US3] Verify all US3 tests pass and manually test copy functionality

**Checkpoint**: All user stories complete - full markdown support with copy functionality

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [x] T026 [P] Update architecture.md with markdown rendering dependencies (marked, DOMPurify, highlight.js) if architecture.md exists
- [x] T027 [P] Run all tests: `cd frontend && npm test`
- [x] T028 Run quickstart.md validation: verify all test prompts render correctly
- [x] T029 Manual E2E test: full conversation with streaming, code blocks, tables, and copy functionality

---

## Bug Fixes

**Purpose**: Post-implementation fixes discovered during testing

- [x] T030 [BUG] Fix double-newline spacing: Change marked `breaks: true` to `breaks: false` in frontend/src/utils/markdownRenderer.js (see plan.md Technical Decisions)
- [x] T031 [BUG] Run all tests to verify fix doesn't break existing functionality (407 tests passing)
- [ ] T032 [BUG] Manual verification: AI responses render with proper single-spacing between elements

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──► Phase 2 (Foundational) ──┬──► Phase 3 (US1 - P1) ──► Phase 6 (Polish)
                                             ├──► Phase 4 (US2 - P2) ──►
                                             └──► Phase 5 (US3 - P3) ──►
```

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phases 3-5)**: All depend on Foundational phase
  - Can proceed in parallel OR sequentially by priority
  - Each story is independently testable
- **Polish (Phase 6)**: After desired user stories complete

### User Story Dependencies

| Story | Depends On | Can Start After | Independent Test |
|-------|------------|-----------------|------------------|
| US1 (P1) | Phase 2 only | Foundational complete | Yes - basic rendering |
| US2 (P2) | Phase 2 only | Foundational complete | Yes - highlighting works without US1 changes |
| US3 (P3) | Phase 2 only | Foundational complete | Yes - copy works independently |

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Utility/model changes before component changes
3. Component logic before styles
4. Core implementation before integration
5. Verify all tests pass before marking story complete

### Parallel Opportunities

**Phase 1:**
- T001, T002 can run in parallel

**Phase 2:**
- T003 (utility) and T004 (tests) can run in parallel
- T005 depends on both T003 and T004

**Phase 3 (US1):**
- T006, T007 (tests) can run in parallel
- T008, T009 must be sequential (same file)
- T010, T011 (styles) can run in parallel with T008/T009

**Phase 4 (US2):**
- T013 (test) can run in parallel with other setup
- T014, T015, T016 must be sequential (same file)
- T017 (theme import) can run in parallel

**Phase 5 (US3):**
- T019 (test) first
- T020-T023 (CodeBlock component) sequential
- T024 (renderer integration) after component ready

---

## Parallel Example: User Story 1

```bash
# Launch tests first (parallel):
Task: "Unit test for MessageBubble markdown rendering in frontend/tests/unit/MessageBubble.test.js"
Task: "Integration test for streaming markdown in frontend/tests/integration/markdown-streaming.test.js"

# Then implementation (after tests exist):
Task: "Update MessageBubble.vue to use v-html"
# Parallel with:
Task: "Add markdown element styles in global.css"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T005)
3. Complete Phase 3: User Story 1 (T006-T012)
4. **STOP and VALIDATE**: Basic markdown rendering works
5. Deploy/demo MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → **MVP: Basic markdown rendering**
3. Add US2 → **Enhanced: Syntax highlighting**
4. Add US3 → **Complete: Copy functionality**
5. Each story adds value without breaking previous

### Recommended Sequence

For a single developer, execute in priority order:
```
T001 → T002 → T003 → T004 → T005 → [US1: T006-T012] → [US2: T013-T018] → [US3: T019-T025] → T026-T029
```

---

## Task Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|------------------------|
| Setup | 2 | 2 parallel |
| Foundational | 3 | 2 parallel |
| US1 (P1) | 7 | 4 parallel |
| US2 (P2) | 6 | 2 parallel |
| US3 (P3) | 7 | 1 parallel |
| Polish | 4 | 2 parallel |
| **Total** | **29** | |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story
- Tests follow TDD: write test → verify FAIL → implement → verify PASS
- Commit after each task or logical group
- Each user story checkpoint = working, independently testable increment
- XSS sanitization (FR-002, SC-006) is built into markdownRenderer utility
