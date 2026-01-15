# Tasks: Server-Side Conversation Storage

**Input**: Design documents from `/specs/010-server-side-conversations/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Storage files: `backend/src/storage/`
- API routes: `backend/src/api/routes/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [x] T001 Add `filelock>=3.0.0` to backend/requirements.txt for concurrent file access
- [x] T002 Create backend/data/ directory for conversation storage with .gitkeep
- [x] T003 [P] Add STORAGE_PATH environment variable to backend/.env.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create Pydantic schemas for Message in backend/src/schemas.py (add to existing file)
- [x] T005 Create Pydantic schemas for Conversation and ConversationSummary in backend/src/schemas.py
- [x] T006 Create Pydantic schemas for API request/response types in backend/src/schemas.py (CreateConversationRequest, UpdateConversationRequest, ConversationResponse, ConversationListResponse)
- [x] T007 [P] Create abstract storage interface in backend/src/storage/base.py with ConversationStorage ABC
- [x] T008 Create file-based storage implementation in backend/src/storage/file_storage.py with FileStorage class
- [x] T009 Create storage service in backend/src/services/storage_service.py that initializes and provides storage instance
- [x] T010 [P] Create backend/src/storage/__init__.py with exports

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Retrieve Conversations from Server (Priority: P1) 🎯 MVP

**Goal**: Users can load their conversation history from the server when opening the application

**Independent Test**: Create test conversation data on server, verify fresh browser session displays conversations correctly

### Implementation for User Story 1

- [x] T011 [US1] Implement GET /api/v1/conversations endpoint in backend/src/api/routes/conversations.py (list all)
- [x] T012 [US1] Implement GET /api/v1/conversations/{id} endpoint in backend/src/api/routes/conversations.py (get single)
- [x] T013 [US1] Register conversations router in backend/main.py
- [x] T014 [P] [US1] Add getConversations() function to frontend/src/services/apiClient.js
- [x] T015 [P] [US1] Add getConversation(id) function to frontend/src/services/apiClient.js
- [x] T016 [US1] Update useConversations.js loadFromStorage() to call server API instead of localStorage in frontend/src/state/useConversations.js
- [x] T017 [US1] Add loading state and error handling for conversation retrieval in frontend/src/state/useConversations.js
- [x] T018 [US1] Add structured logging for conversation retrieval operations in backend/src/api/routes/conversations.py

**Checkpoint**: User Story 1 complete - conversations load from server on app open

---

## Phase 4: User Story 2 - Save Conversations to Server (Priority: P1) 🎯 MVP

**Goal**: Conversations are automatically saved to the server after each message exchange

**Independent Test**: Send messages, close browser, reopen and verify messages persist

### Implementation for User Story 2

- [x] T019 [US2] Implement POST /api/v1/conversations endpoint in backend/src/api/routes/conversations.py (create new)
- [x] T020 [US2] Implement PUT /api/v1/conversations/{id} endpoint in backend/src/api/routes/conversations.py (update existing)
- [x] T021 [P] [US2] Add createConversation() function to frontend/src/services/apiClient.js
- [x] T022 [P] [US2] Add updateConversation(id, data) function to frontend/src/services/apiClient.js
- [x] T023 [US2] Update useConversations.js saveToStorage() to call server API in frontend/src/state/useConversations.js
- [x] T024 [US2] Update useConversations.js createConversation() to persist to server in frontend/src/state/useConversations.js
- [x] T025 [US2] Update useMessages.js to trigger save after message send/receive in frontend/src/state/useMessages.js
- [x] T026 [US2] Add save error handling with user feedback in frontend/src/state/useConversations.js
- [x] T027 [US2] Add structured logging for save operations in backend/src/api/routes/conversations.py

**Checkpoint**: User Story 2 complete - conversations persist to server automatically

---

## Phase 5: User Story 3 - Manage Conversations (Priority: P2)

**Goal**: Users can delete conversations and create new ones with server persistence

**Independent Test**: Create conversation, delete it, refresh page, confirm it no longer appears

### Implementation for User Story 3

- [x] T028 [US3] Implement DELETE /api/v1/conversations/{id} endpoint in backend/src/api/routes/conversations.py
- [x] T029 [P] [US3] Add deleteConversation(id) function to frontend/src/services/apiClient.js
- [x] T030 [US3] Update useConversations.js deleteConversation() to call server API in frontend/src/state/useConversations.js
- [x] T031 [US3] Add delete confirmation and error handling in frontend/src/state/useConversations.js
- [x] T032 [US3] Add structured logging for delete operations in backend/src/api/routes/conversations.py

**Checkpoint**: User Story 3 complete - conversation management works with server persistence

---

## Phase 6: User Story 4 - Graceful Degradation (Priority: P3)

**Goal**: Application provides clear feedback when server is unavailable without losing user data

**Independent Test**: Simulate server unavailability, verify error messages appear and typed text is preserved

### Implementation for User Story 4

- [x] T033 [US4] Add connection error detection and retry logic in frontend/src/services/apiClient.js
- [x] T034 [US4] Add user-friendly error messages for server unavailability in frontend/src/state/useConversations.js
- [x] T035 [US4] Preserve user-entered text on send failure in frontend/src/state/useMessages.js
- [x] T036 [US4] Add retry button/action when operations fail in frontend/src/state/useConversations.js
- [x] T037 [US4] Add connection status indicator support in frontend/src/state/useAppState.js

**Checkpoint**: User Story 4 complete - graceful error handling implemented

---

## Phase 7: Migration & Polish

**Purpose**: One-time localStorage migration and cross-cutting improvements

- [x] T038 Implement one-time localStorage migration logic in frontend/src/state/useConversations.js
- [x] T039 Add migration status check (server empty + localStorage has data) in frontend/src/state/useConversations.js
- [x] T040 Clear localStorage after successful migration in frontend/src/state/useConversations.js
- [x] T041 [P] Update architecture.md with storage layer documentation
- [x] T042 [P] Run quickstart.md validation to verify feature works end-to-end
- [x] T043 Code review and cleanup across all modified files

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 priority and can proceed in parallel
  - US3 depends on US1/US2 being complete (needs CRUD foundation)
  - US4 can proceed after US1/US2 (adds error handling layer)
- **Migration & Polish (Phase 7)**: Depends on US1 and US2 being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - Retrieve conversations
- **User Story 2 (P1)**: Can start after Foundational - Save conversations (parallel with US1)
- **User Story 3 (P2)**: Can start after US1/US2 - Delete/manage conversations
- **User Story 4 (P3)**: Can start after US1/US2 - Error handling

### Within Each User Story

- Backend endpoints before frontend integration
- API client methods before state management updates
- Core implementation before error handling
- Logging as final step

### Parallel Opportunities

- T003 can run parallel with T001, T002
- T007 can run parallel with T004-T006
- T014, T015 can run parallel (different functions in same file)
- T021, T022 can run parallel
- T041, T042 can run parallel

---

## Parallel Example: User Story 1 Backend

```bash
# After Foundational phase completes, launch US1 backend tasks:
Task: T011 - "Implement GET /conversations endpoint"
Task: T012 - "Implement GET /conversations/{id} endpoint"

# Then frontend tasks can run in parallel:
Task: T014 - "Add getConversations() to apiClient.js"
Task: T015 - "Add getConversation(id) to apiClient.js"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T010)
3. Complete Phase 3: User Story 1 (T011-T018)
4. Complete Phase 4: User Story 2 (T019-T027)
5. **STOP and VALIDATE**: Test both stories work together
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 + 2 → Test together → Deploy/Demo (MVP!)
3. Add User Story 3 → Test independently → Deploy/Demo
4. Add User Story 4 → Test independently → Deploy/Demo
5. Migration & Polish → Final validation

### Suggested MVP Scope

**Minimum Viable Product**: User Stories 1 + 2 (both P1)
- Users can retrieve conversations from server
- Users can save conversations to server
- This provides core value: conversations persist across browsers/devices

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Total tasks: 43
- Tasks per story: Setup=3, Foundational=7, US1=8, US2=9, US3=5, US4=5, Polish=6
