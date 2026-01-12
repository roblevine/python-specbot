# Tasks: OpenAI Model Selector

**Input**: Design documents from `/specs/008-openai-model-selector/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi-models.yaml

**Tests**: Included (Test-First Development per project constitution)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/`, `frontend/src/`
- **Backend tests**: `backend/tests/`
- **Frontend tests**: `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project structure and prepare for implementation

- [ ] T001 Verify backend/frontend project structure matches plan.md
- [ ] T002 Verify existing dependencies (FastAPI, LangChain, Vue 3, Pydantic) are installed
- [ ] T003 [P] Create backend/src/config/ directory if not exists
- [ ] T004 [P] Create frontend/src/components/ModelSelector/ directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create model configuration schema in backend/src/config/models.py
- [ ] T006 Implement model configuration loader with OPENAI_MODELS env var support in backend/src/config/models.py
- [ ] T007 Add fallback to OPENAI_MODEL env var for single-model configuration in backend/src/config/models.py
- [ ] T008 Implement GET /api/v1/models endpoint in backend/src/api/routes/models.py
- [ ] T009 Register models router in backend/main.py
- [ ] T010 Update StorageSchema.js to add selectedModelId field in frontend/src/storage/StorageSchema.js
- [ ] T011 Add model configuration validation (at least one model, exactly one default) in backend/src/config/models.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Select Model Before Chatting (Priority: P1) 🎯 MVP

**Goal**: Enable users to select an OpenAI model from a dropdown and have their messages use the selected model

**Independent Test**: Open chat interface, select a model from dropdown, send a message, verify response comes from selected model (check API response includes correct model field)

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T012 [P] [US1] Contract test for GET /api/v1/models in backend/tests/contract/test_models_api_contract.py
- [ ] T013 [P] [US1] Contract test for POST /api/v1/messages with model field in backend/tests/contract/test_message_api_contract.py
- [ ] T014 [P] [US1] Unit test for model configuration loader in backend/tests/unit/test_model_config.py
- [ ] T015 [P] [US1] Unit test for LLM service with model selection in backend/tests/unit/test_llm_service.py
- [ ] T016 [P] [US1] Unit test for ModelSelector component in frontend/src/components/ModelSelector/ModelSelector.test.js
- [ ] T017 [US1] Integration test for model selection flow in backend/tests/integration/test_model_selection.py
- [ ] T018 [US1] Frontend integration test for model selection in frontend/tests/integration/model-selection.test.js

### Backend Implementation for User Story 1

- [X] T019 [US1] Extend MessageRequest schema to add optional model field in backend/src/schemas.py
- [X] T020 [US1] Extend MessageResponse schema to add required model field in backend/src/schemas.py
- [X] T021 [US1] Update llm_service.get_ai_response() to accept model parameter in backend/src/services/llm_service.py
- [X] T022 [US1] Update llm_service to validate model against configuration in backend/src/services/llm_service.py
- [X] T023 [US1] Update llm_service to create per-request ChatOpenAI instance with specified model in backend/src/services/llm_service.py
- [X] T024 [US1] Update POST /api/v1/messages endpoint to accept model parameter in backend/src/api/routes/messages.py
- [X] T025 [US1] Update POST /api/v1/messages endpoint to return model in response in backend/src/api/routes/messages.py
- [X] T026 [US1] Add error handling for invalid model selection (400 Bad Request) in backend/src/api/routes/messages.py

### Frontend Implementation for User Story 1

- [X] T027 [P] [US1] Create useModels composable for model state management in frontend/src/state/useModels.js
- [X] T028 [P] [US1] Create ModelSelector.vue component with dropdown UI in frontend/src/components/ModelSelector/ModelSelector.vue
- [X] T029 [US1] Update useAppState to integrate selectedModel state in frontend/src/state/useAppState.js
- [X] T030 [US1] Update apiClient.sendMessage() to pass model parameter in frontend/src/services/apiClient.js
- [X] T031 [US1] Create fetchModels() function in apiClient to call GET /api/v1/models in frontend/src/services/apiClient.js
- [X] T032 [US1] Update App.vue to include ModelSelector component above input area in frontend/src/components/App/App.vue
- [X] T033 [US1] Update Message entity/type to include model field in frontend/src/types/ or relevant location
- [X] T034 [US1] Implement model selection persistence to localStorage in useModels composable
- [X] T035 [US1] Implement model validation on app load (clear if invalid) in useModels composable

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View Model Information (Priority: P2)

**Goal**: Display helpful information (name, description) for each model so users can make informed decisions

**Independent Test**: Open model selector dropdown and verify each model displays its name and description

### Tests for User Story 2

- [ ] T036 [P] [US2] Unit test for ModelSelector displaying model descriptions in frontend/src/components/ModelSelector/ModelSelector.test.js

### Implementation for User Story 2

- [ ] T037 [US2] Update ModelSelector.vue to display model name and description in dropdown options in frontend/src/components/ModelSelector/ModelSelector.vue
- [ ] T038 [US2] Add CSS styling for model descriptions (truncate if needed) in frontend/src/components/ModelSelector/ModelSelector.vue
- [ ] T039 [US2] Add visual distinction between model name and description in ModelSelector.vue

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Change Model Mid-Conversation (Priority: P3)

**Goal**: Allow users to change the selected model during an active conversation and see which model generated each response

**Independent Test**: Start conversation with one model, change to another mid-conversation, verify subsequent messages use new model and message bubbles show which model generated each response

### Tests for User Story 3

- [ ] T040 [P] [US3] Unit test for MessageBubble with model indicator in frontend/src/components/MessageBubble/MessageBubble.test.js
- [ ] T041 [US3] E2E test for mid-conversation model change in frontend/tests/e2e/model-selection.spec.js

### Implementation for User Story 3

- [ ] T042 [US3] Update MessageBubble.vue to display model indicator for system messages in frontend/src/components/MessageBubble/MessageBubble.vue
- [ ] T043 [US3] Add CSS styling for model indicator (subtle, non-intrusive) in frontend/src/components/MessageBubble/MessageBubble.vue
- [ ] T044 [US3] Verify ModelSelector state updates trigger immediate effect on next message in useModels.js
- [ ] T045 [US3] Ensure conversation history preserves model information per message in storage

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T046 [P] Add comprehensive error handling for model configuration errors (empty list, no default, etc.)
- [X] T047 [P] Add logging for model selection events in backend/src/services/llm_service.py
- [ ] T048 [P] Update architecture.md with model selection flow diagram
- [X] T049 [P] Create example OPENAI_MODELS configuration in backend/.env.example
- [X] T050 [P] Add frontend error handling for /api/v1/models endpoint failures
- [X] T051 [P] Add loading states to ModelSelector while fetching models
- [X] T052 Verify all tests pass (backend: pytest, frontend: vitest)
- [ ] T053 Run quickstart.md validation end-to-end
- [X] T054 [P] Update CLAUDE.md with new technologies and recent changes
- [X] T055 [P] Add accessibility attributes to ModelSelector (aria-labels, keyboard navigation)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after US1 (extends ModelSelector component from US1)
- **User Story 3 (P3)**: Can start after US1 (extends MessageBubble and uses model field from US1)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Backend schemas before services
- Backend services before endpoints
- Frontend composables before components
- Frontend components before integration
- Core implementation before visual polish

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- All test tasks within a user story marked [P] can run in parallel
- Backend and frontend implementation for same story can proceed in parallel once tests are written
- Models router (T008) and messages schema updates (T019-T020) can be developed in parallel after config is ready

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for GET /api/v1/models in backend/tests/contract/test_models_api_contract.py"
Task: "Contract test for POST /api/v1/messages with model field in backend/tests/contract/test_message_api_contract.py"
Task: "Unit test for model configuration loader in backend/tests/unit/test_model_config.py"
Task: "Unit test for LLM service with model selection in backend/tests/unit/test_llm_service.py"
Task: "Unit test for ModelSelector component in frontend/src/components/ModelSelector/ModelSelector.test.js"

# After tests fail, launch backend and frontend implementation in parallel:
Backend: "Update llm_service, schemas, messages endpoint"
Frontend: "Create ModelSelector component, useModels composable, update App.vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! ✅)
3. Add User Story 2 → Test independently → Deploy/Demo (Enhanced UX ✅)
4. Add User Story 3 → Test independently → Deploy/Demo (Power user features ✅)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (backend + frontend)
   - Developer B: Can start User Story 2 tests (wait for US1 ModelSelector component)
3. After US1 complete:
   - Developer A: User Story 2 implementation
   - Developer B: User Story 3 preparation
4. Stories complete and integrate incrementally

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (Test-First Development)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Model configuration is environment-based (OPENAI_MODELS env var)
- Backend remains stateless (model selection passed per-request)
- Frontend persists selection in localStorage (session-scoped)
- All API changes are backward-compatible (model field optional with default fallback)
