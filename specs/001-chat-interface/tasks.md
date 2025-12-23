# Tasks: Chat Interface (P1 MVP Only)

**Feature**: Chat Interface - Send and View Message Loopback
**Input**: Design documents from `/specs/001-chat-interface/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Scope**: This task list implements ONLY User Story 1 (P1 - Send and View Message Loopback) following Principle VIII (Incremental Delivery & Thin Slices). After P1 is complete, tested, demoed, and committed, P2 and P3 tasks will be generated separately.

**Tests**: Following TDD approach per Principle III - tests written FIRST, verified to FAIL, then implementation.

**Organization**: Tasks organized to deliver complete vertical slice (tests → utils → storage → state → components → integration).

## Format: `- [ ] [TaskID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[US1]**: Belongs to User Story 1 (P1 MVP)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend project**: `frontend/src/`, `frontend/tests/`
- **Project root**: `/workspaces/python-specbot/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize Vue.js 3 project with Vite and testing infrastructure

- [ ] T001 Create frontend directory at /workspaces/python-specbot/frontend
- [ ] T002 Initialize Node.js project with package.json in frontend/
- [ ] T003 [P] Install Vue.js 3 dependency (npm install vue@^3.4.0)
- [ ] T004 [P] Install Vite and Vue plugin dependencies (npm install -D vite@^5.0.0 @vitejs/plugin-vue@^5.0.0)
- [ ] T005 [P] Install Vitest and testing dependencies (npm install -D vitest@^1.0.0 @vue/test-utils@^2.4.0 @testing-library/vue@^9.0.0)
- [ ] T006 [P] Install Playwright for E2E testing (npm install -D playwright@^1.40.0 @playwright/test@^1.40.0)
- [ ] T007 [P] Install ESLint and Prettier dependencies (npm install -D eslint@^8.56.0 eslint-plugin-vue@^9.19.0 prettier@^3.1.0)
- [ ] T008 Create vite.config.js with Vue plugin and test environment configuration
- [ ] T009 [P] Create .eslintrc.json with Vue 3 recommended rules
- [ ] T010 [P] Create .prettierrc.json with project code style
- [ ] T011 [P] Create playwright.config.js with browser test configuration
- [ ] T012 Add npm scripts to package.json (dev, build, test, test:watch, test:e2e, lint, format)
- [ ] T013 Create directory structure (src/components, src/state, src/storage, src/utils, tests/unit, tests/integration, tests/e2e, public/styles)
- [ ] T014 Create public/index.html entry point
- [ ] T015 Create public/styles/global.css with CSS variables and reset
- [ ] T016 Create src/index.js entry point

**Checkpoint**: Project initialized, `npm run dev` should start empty app

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities and schemas needed by ALL user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T017 [P] Create frontend/src/utils/idGenerator.js with generateId() function (UUID v4 with prefix)
- [ ] T018 [P] Create frontend/src/utils/validators.js with message and conversation validation functions
- [ ] T019 [P] Create frontend/src/utils/logger.js with console logging wrapper (DEBUG, INFO, ERROR levels)
- [ ] T020 Create frontend/src/storage/StorageSchema.js defining v1.0.0 schema structure and validation
- [ ] T021 Create frontend/tests/unit/idGenerator.test.js testing UUID generation and prefixes
- [ ] T022 [P] Create frontend/tests/unit/validators.test.js testing validation rules
- [ ] T023 [P] Create frontend/tests/unit/StorageSchema.test.js testing schema validation

**Checkpoint**: Foundation ready - User Story 1 implementation can now begin

---

## Phase 3: User Story 1 - Send and View Message Loopback (Priority: P1) 🎯 MVP

**Goal**: User can type message, click send, see user message and system loopback response in chat area

**Independent Test**: Open app, type "Hello world", click Send → see "Hello world" displayed twice (user message + system loopback)

### Tests for User Story 1 (TDD - Write FIRST) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T024 [P] [US1] Create frontend/tests/e2e/send-message.test.js for complete loopback workflow
- [ ] T025 [P] [US1] Create frontend/tests/integration/message-flow.test.js testing message creation and loopback
- [ ] T026 [P] [US1] Create frontend/tests/integration/conversation-persistence.test.js testing single conversation save/load
- [ ] T027 [P] [US1] Create frontend/tests/unit/LocalStorageAdapter.test.js testing storage operations

### Implementation for User Story 1

#### Storage Layer

- [ ] T028 [US1] Implement frontend/src/storage/LocalStorageAdapter.js with saveConversations() method
- [ ] T029 [US1] Implement loadConversations() method in frontend/src/storage/LocalStorageAdapter.js
- [ ] T030 [US1] Implement clearAllData() method in frontend/src/storage/LocalStorageAdapter.js

**Checkpoint**: Storage layer complete, tests T027 should pass

#### State Management (Composables)

- [ ] T031 [US1] Create frontend/src/state/useConversations.js composable with conversations ref and active conversation management
- [ ] T032 [US1] Implement createConversation() in useConversations composable
- [ ] T033 [US1] Implement addMessage() in useConversations composable
- [ ] T034 [US1] Implement loadFromStorage() in useConversations composable
- [ ] T035 [US1] Implement saveToStorage() in useConversations composable
- [ ] T036 [P] [US1] Create frontend/src/state/useMessages.js composable with currentMessages computed ref
- [ ] T037 [US1] Implement sendUserMessage() in useMessages composable (creates user message + loopback)
- [ ] T038 [P] [US1] Create frontend/src/state/useAppState.js composable managing isProcessing and status
- [ ] T039 [P] [US1] Create frontend/tests/unit/useConversations.test.js testing conversation operations
- [ ] T040 [P] [US1] Create frontend/tests/unit/useMessages.test.js testing message operations

**Checkpoint**: State management complete, unit tests T039-T040 should pass

#### UI Components (Bottom-Up: Leaves First)

**MessageBubble Component** (Leaf):
- [ ] T041 [P] [US1] Create frontend/src/components/ChatArea/MessageBubble.vue with props (message)
- [ ] T042 [US1] Style MessageBubble.vue: user messages right-aligned blue, system messages left-aligned gray
- [ ] T043 [P] [US1] Create frontend/tests/unit/MessageBubble.test.js testing user and system message rendering

**InputArea Component** (Leaf):
- [ ] T044 [P] [US1] Create frontend/src/components/InputArea/InputArea.vue with textarea and Send button
- [ ] T045 [US1] Implement InputArea.vue: emit send-message event with trimmed text, clear input after send
- [ ] T046 [US1] Add InputArea.vue validation: disable Send if empty, handle Enter key (Shift+Enter for newline)
- [ ] T047 [P] [US1] Create frontend/tests/unit/InputArea.test.js testing send event and validation

**ChatArea Component** (Container):
- [ ] T048 [US1] Create frontend/src/components/ChatArea/ChatArea.vue with props (messages, isProcessing)
- [ ] T049 [US1] Implement ChatArea.vue: render MessageBubble for each message, auto-scroll to bottom
- [ ] T050 [US1] Add ChatArea.vue: show empty state when no messages, show loading indicator when isProcessing
- [ ] T051 [P] [US1] Create frontend/tests/unit/ChatArea.test.js testing message display and auto-scroll

**StatusBar Component** (Minimal - P1 needs basic status):
- [ ] T052 [P] [US1] Create frontend/src/components/StatusBar/StatusBar.vue with props (status, statusType)
- [ ] T053 [US1] Style StatusBar.vue: green for ready, yellow for processing, red for error
- [ ] T054 [P] [US1] Create frontend/tests/unit/StatusBar.test.js testing status display

**HistoryBar Component** (Minimal - P1 shows single conversation):
- [ ] T055 [P] [US1] Create frontend/src/components/HistoryBar/HistoryBar.vue with props (conversations, activeConversationId)
- [ ] T056 [US1] Implement HistoryBar.vue: display single conversation title (P1 only has one conversation)
- [ ] T057 [P] [US1] Create frontend/tests/unit/HistoryBar.test.js testing single conversation display

**App Component** (Root - Orchestrates Everything):
- [ ] T058 [US1] Create frontend/src/components/App/App.vue importing all child components
- [ ] T059 [US1] Implement App.vue: use useConversations, useMessages, useAppState composables
- [ ] T060 [US1] Implement App.vue layout: CSS Grid with 4 areas (status-bar top, history-bar left, chat-area center, input-area bottom)
- [ ] T061 [US1] Wire App.vue: on mount load storage, create initial conversation if none exists
- [ ] T062 [US1] Wire App.vue: handleSendMessage calls sendUserMessage, updates state, saves to storage
- [ ] T063 [US1] Add App.vue error handling: try-catch around storage operations, show errors in status bar
- [ ] T064 [P] [US1] Create frontend/tests/unit/App.test.js testing app initialization and message flow

**Checkpoint**: All components implemented, unit tests should pass

#### Integration & E2E

- [ ] T065 [US1] Run integration test T025 (message-flow): Verify user message creation triggers loopback
- [ ] T066 [US1] Run integration test T026 (conversation-persistence): Verify messages persist across page reload
- [ ] T067 [US1] Run E2E test T024 (send-message): Verify complete workflow in real browser
- [ ] T068 [US1] Fix any failing integration or E2E tests

**Checkpoint**: All tests passing - P1 MVP is COMPLETE

---

## Phase 4: Polish & Verification

**Purpose**: Final touches and validation before commit

- [ ] T069 Run all tests (npm run test && npm run test:e2e) and verify 100% passing
- [ ] T070 Run linting (npm run lint) and fix any issues
- [ ] T071 Run formatting (npm run format) to ensure code style consistency
- [ ] T072 Build production bundle (npm run build) and verify size < 5MB
- [ ] T073 Test P1 acceptance scenarios manually in dev server (npm run dev):
  - Scenario 1: Type "Hello world", click Send → verify user message + loopback appear
  - Scenario 2: Send multiple messages → verify chronological order
  - Scenario 3: After sending → verify input cleared
- [ ] T074 Test in multiple browsers (Chrome, Firefox, Safari if available)
- [ ] T075 Verify LocalStorage persistence: send messages, refresh page, verify messages still there
- [ ] T076 Document any known limitations or issues in comments

**Final Checkpoint**: P1 MVP ready for demo and commit

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS User Story 1
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **Polish (Phase 4)**: Depends on User Story 1 completion

### Within User Story 1

**Sequential Dependencies**:
1. Tests T024-T027 written FIRST (must fail initially)
2. Storage layer (T028-T030) → State management (T031-T038) → UI Components (T041-T064)
3. Components built bottom-up: MessageBubble/InputArea → ChatArea → StatusBar/HistoryBar → App
4. Integration tests (T065-T068) run after all components complete

**Parallel Opportunities**:
- All Setup tasks T003-T011 can run in parallel (different config files)
- All Foundational util tasks T017-T019 can run in parallel
- Test files T021-T023, T039-T040, T043, T047, T051, T054, T057, T064 can run in parallel
- MessageBubble (T041-T043) and InputArea (T044-T047) can be built in parallel
- StatusBar (T052-T054) and HistoryBar (T055-T057) can be built in parallel

---

## Parallel Execution Example: User Story 1

```bash
# After Foundational phase complete, these can run in parallel:

# Team Member 1: Storage Layer
Task T028-T030: Implement LocalStorageAdapter methods

# Team Member 2: State Management
Task T031-T038: Implement composables (useConversations, useMessages, useAppState)

# Team Member 3: UI Components (Leaves)
Task T041-T043: Implement MessageBubble component
Task T044-T047: Implement InputArea component

# Once leaves done, Team Member 3 continues:
Task T048-T051: Implement ChatArea component (uses MessageBubble)
Task T052-T054: Implement StatusBar component
Task T055-T057: Implement HistoryBar component

# Team Member 4: Tests
Task T039-T040, T043, T047, T051, T054, T057, T064: Write unit tests

# All team members converge:
Task T058-T064: Integrate App component (needs all above complete)
Task T065-T068: Run integration and E2E tests
```

---

## Implementation Strategy

### MVP First (P1 ONLY - This Task List)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Send and View Message Loopback)
4. Complete Phase 4: Polish
5. **STOP, TEST, DEMO, COMMIT**

**At this point you have working software**:
- ✅ User can send messages
- ✅ User sees loopback responses
- ✅ Messages persist across page refreshes
- ✅ Single conversation works end-to-end
- ✅ All tests passing
- ✅ Production bundle built

### After P1 is Committed

**Next Steps** (NOT in this task list):
1. Run `/speckit.tasks` again to generate P2 tasks (Navigate Conversation History)
2. Implement P2 as separate thin slice
3. Test, demo, commit P2
4. Repeat for P3, P4 if needed

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[US1] label** = belongs to User Story 1 for traceability
- **TDD**: Tests T024-T027 MUST be written first and fail before implementation
- **Vertical Slice**: P1 is complete end-to-end feature (not horizontal layers)
- **Commit After P1**: Do NOT proceed to P2 until P1 is tested, demoed, and committed
- **Constitution Compliance**: Follows Principle VIII (Incremental Delivery & Thin Slices)
- **File Paths**: All paths are exact - ready for implementation
- **Empty for P2/P3**: This task list ONLY covers P1 MVP per user request

**Total P1 Tasks**: 76 tasks
**Estimated Parallelization**: ~20-25 tasks can run in parallel at various points
**MVP Definition**: Working chat interface with message loopback and persistence
