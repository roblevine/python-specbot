# Tasks: LLM-Generated Conversation Titles

**Input**: Design documents from `/specs/019-llm-conversation-titles/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Included per constitution (Test-First Development is NON-NEGOTIABLE)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Configuration and schema updates for title model support

- [ ] T001 Add OPENAI_TITLE_MODEL and ANTHROPIC_TITLE_MODEL to backend/.env.example with documentation
- [ ] T002 [P] Create Pydantic schemas for title generation request/response in backend/src/schemas.py
- [ ] T003 [P] Add title generation route registration in backend/main.py

---

## Phase 2: Foundational - Title Generation Endpoint (US3) (Priority: P1)

**Purpose**: Backend title generation service and endpoint - MUST complete before frontend integration

**Goal**: Provide an API endpoint that generates conversation titles using LLM

**Independent Test**: Can be tested by calling `POST /api/v1/titles/generate` with messages and model ID

**⚠️ CRITICAL**: US1 (frontend integration) cannot begin until this phase is complete

### Tests for US3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T004 [P] [US3] Unit test for title prompt construction and truncation in backend/tests/unit/test_title_service.py
- [ ] T005 [P] [US3] Unit test for title model config loading in backend/tests/unit/test_model_config.py
- [ ] T006 [P] [US3] Integration test for POST /api/v1/titles/generate (valid request) in backend/tests/integration/test_titles_api.py
- [ ] T007 [P] [US3] Integration test for POST /api/v1/titles/generate (invalid model) in backend/tests/integration/test_titles_api.py
- [ ] T008 [P] [US3] Integration test for POST /api/v1/titles/generate (empty messages) in backend/tests/integration/test_titles_api.py

### Implementation for US3

- [ ] T009 [US3] Implement title generation service with prompt and post-processing in backend/src/services/title_service.py
- [ ] T010 [US3] Add load_title_model_config() to read OPENAI_TITLE_MODEL and ANTHROPIC_TITLE_MODEL in backend/src/config/models.py
- [ ] T011 [US3] Implement POST /api/v1/titles/generate endpoint in backend/src/api/routes/titles.py
- [ ] T012 [US3] Add titleModel field to /api/v1/models response in backend/src/api/routes/models.py
- [ ] T013 [US3] Add structured logging for title generation operations in backend/src/services/title_service.py

**Checkpoint**: At this point, `POST /api/v1/titles/generate` should work and return generated titles. Verify with:
```bash
curl -X POST http://localhost:8000/api/v1/titles/generate \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"sender": "user", "text": "Hello"}, {"sender": "system", "text": "Hi there!"}], "model": "gpt-3.5-turbo"}'
```

---

## Phase 3: User Story 1 - Automatic Title Generation (Priority: P1) 🎯 MVP

**Goal**: After first message exchange, automatically generate a meaningful title without user action

**Independent Test**: Send a first message in a new conversation, verify title changes from "New Conversation" to LLM-generated summary after response

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [US1] Unit test for generateTitle API client function in frontend/tests/unit/apiClient.test.js
- [ ] T015 [P] [US1] Unit test for getTitleModel helper (provider-based selection) in frontend/tests/unit/useConversations.test.js
- [ ] T016 [P] [US1] Unit test for title generation trigger logic in frontend/tests/unit/useConversations.test.js
- [ ] T017 [P] [US1] Unit test for fallback to first message text on error in frontend/tests/unit/useConversations.test.js

### Implementation for User Story 1

- [ ] T018 [US1] Add generateTitle(messages, model) function to frontend/src/services/apiClient.js
- [ ] T019 [US1] Add getTitleModel(currentModelId, models) helper function to frontend/src/state/useConversations.js
- [ ] T020 [US1] Modify addMessage() to track when title generation should trigger in frontend/src/state/useConversations.js
- [ ] T021 [US1] Implement async title generation call after streaming completes in frontend/src/components/App/App.vue
- [ ] T022 [US1] Add fallback to first message text when title generation fails in frontend/src/state/useConversations.js
- [ ] T023 [US1] Ensure title is NOT regenerated for conversations with existing non-default titles in frontend/src/state/useConversations.js

**Checkpoint**: At this point, starting a new conversation and sending a message should result in an LLM-generated title appearing in the sidebar after the assistant responds.

---

## Phase 4: User Story 2 - Provider-Specific Title Model Configuration (Priority: P2)

**Goal**: Allow administrators to configure which model is used for title generation per provider

**Independent Test**: Configure OPENAI_TITLE_MODEL, verify title generation uses the configured model instead of the conversation model

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T024 [P] [US2] Unit test for titleModel field in /api/v1/models response in backend/tests/unit/test_model_config.py
- [ ] T025 [P] [US2] Integration test for /api/v1/models with titleModel field in backend/tests/integration/test_models_api.py
- [ ] T026 [P] [US2] Unit test for frontend title model selection by provider in frontend/tests/unit/useConversations.test.js

### Implementation for User Story 2

- [ ] T027 [US2] Implement get_title_model_for_provider() function in backend/src/config/models.py
- [ ] T028 [US2] Add titleModel boolean field to ModelInfo response schema in backend/src/api/routes/models.py
- [ ] T029 [US2] Update frontend getTitleModel() to use titleModel field from /api/v1/models in frontend/src/state/useConversations.js
- [ ] T030 [US2] Add integration test: verify correct title model used per provider in backend/tests/integration/test_titles_api.py

**Checkpoint**: At this point, configuring `OPENAI_TITLE_MODEL=gpt-3.5-turbo` should result in title generation using GPT-3.5 Turbo even when chatting with GPT-4.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and validation

- [ ] T031 [P] Update backend/.env.example with complete title model configuration examples
- [ ] T032 [P] Add title generation section to backend/README.md
- [ ] T033 [P] Verify all edge cases: long titles truncated, empty response fallback, network timeout
- [ ] T034 Run quickstart.md validation to verify end-to-end flow
- [ ] T035 [P] Add error logging tests for title generation failures in backend/tests/unit/test_title_service.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational/US3 (Phase 2)**: Depends on Setup - BLOCKS US1 (frontend needs endpoint)
- **US1 (Phase 3)**: Depends on US3 completion (needs working endpoint)
- **US2 (Phase 4)**: Can start after US3 (enhances config), but recommended after US1
- **Polish (Phase 5)**: Depends on US1 completion (core feature working)

### User Story Dependencies

```
Setup (T001-T003)
       │
       ▼
US3: Title Endpoint (T004-T013) ◄─── FOUNDATIONAL
       │
       ▼
US1: Auto Title Gen (T014-T023) ◄─── MVP
       │
       ▼
US2: Provider Config (T024-T030) ◄─── Enhancement
       │
       ▼
Polish (T031-T035)
```

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Service/config before endpoints
3. Backend before frontend (for US1)
4. Core implementation before integration
5. Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002 and T003 can run in parallel after T001

**Phase 2 (US3)**:
- All test tasks (T004-T008) can run in parallel
- T009, T010 can run in parallel (service, config)
- T011 depends on T009 (endpoint needs service)
- T012 can run in parallel with T011

**Phase 3 (US1)**:
- All test tasks (T014-T017) can run in parallel
- T018, T019 can run in parallel
- T020-T023 must be sequential (depend on each other)

**Phase 4 (US2)**:
- All test tasks (T024-T026) can run in parallel
- T027, T028 can run in parallel
- T029 depends on T028

---

## Parallel Example: Phase 2 (US3)

```bash
# Launch all US3 tests together:
Task: "T004 [P] [US3] Unit test for title prompt construction"
Task: "T005 [P] [US3] Unit test for title model config loading"
Task: "T006 [P] [US3] Integration test for valid request"
Task: "T007 [P] [US3] Integration test for invalid model"
Task: "T008 [P] [US3] Integration test for empty messages"

# After tests written and failing, launch service/config in parallel:
Task: "T009 [US3] Implement title generation service"
Task: "T010 [US3] Add load_title_model_config()"
```

---

## Implementation Strategy

### MVP First (US3 + US1)

1. Complete Phase 1: Setup
2. Complete Phase 2: US3 (Title Generation Endpoint)
3. **VALIDATE**: Test endpoint directly with curl
4. Complete Phase 3: US1 (Automatic Title Generation)
5. **STOP and VALIDATE**: Test full flow - new conversation → message → title generated
6. Deploy/demo if ready - MVP complete!

### Incremental Delivery

1. Setup + US3 → Backend title generation working
2. Add US1 → Frontend integration → **MVP complete**
3. Add US2 → Provider-specific configuration → Enhanced feature
4. Polish → Documentation and edge case handling

### Task Summary

| Phase | User Story | Tasks | Parallel Opportunities |
|-------|------------|-------|------------------------|
| 1. Setup | - | T001-T003 | T002, T003 |
| 2. Foundational | US3 | T004-T013 | T004-T008, T009-T010, T011-T012 |
| 3. MVP | US1 | T014-T023 | T014-T017, T018-T019 |
| 4. Enhancement | US2 | T024-T030 | T024-T026, T027-T028 |
| 5. Polish | - | T031-T035 | T031-T033, T035 |

**Total Tasks**: 35
**MVP Tasks** (US3 + US1): 23
**Enhancement Tasks** (US2): 7
**Polish Tasks**: 5

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Test-First Development: All test tasks must FAIL before implementation
- US3 is foundational - must complete before US1 can start
- US1 completion = MVP (automatic title generation working)
- US2 is optional enhancement (provider-specific config)
- Commit after each task or logical group
