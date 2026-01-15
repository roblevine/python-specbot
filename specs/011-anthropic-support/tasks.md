# Tasks: Anthropic Claude Model Support

**Input**: Design documents from `/specs/011-anthropic-support/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Tests: `backend/tests/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add langchain-anthropic dependency and update configuration schema

- [x] T001 Add langchain-anthropic>=0.2.0 to backend/requirements.txt
- [x] T002 [P] Update backend/.env.example with ANTHROPIC_API_KEY and ANTHROPIC_MODELS examples

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extend model configuration to support provider field - required before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add `provider` field to ModelConfig Pydantic model in backend/src/config/models.py
- [x] T004 Add provider validation (enum: "openai", "anthropic") in backend/src/config/models.py
- [x] T005 Add backward compatibility for OPENAI_MODELS without provider field (default to "openai") in backend/src/config/models.py
- [x] T006 Add PROVIDERS registry constant in backend/src/config/models.py
- [x] T007 Create load_anthropic_models() function in backend/src/config/models.py
- [x] T008 Update load_model_configuration() to merge OpenAI and Anthropic models in backend/src/config/models.py
- [x] T009 Add validation for exactly one default model across all providers in backend/src/config/models.py

**Checkpoint**: Foundation ready - provider configuration working, user story implementation can begin

---

## Phase 3: User Story 1 - Select and Use Anthropic Claude Models (Priority: P1) 🎯 MVP

**Goal**: Users can select Claude models from dropdown and get responses from Anthropic API

**Independent Test**: Open chat, select "Claude 3.5 Sonnet", send message, verify response comes from Claude

### Tests for User Story 1

- [ ] T010 [P] [US1] Unit test for ChatAnthropic instantiation in backend/tests/unit/test_llm_service_anthropic.py
- [ ] T011 [P] [US1] Unit test for provider routing logic in backend/tests/unit/test_llm_service_provider_routing.py
- [ ] T012 [P] [US1] Contract test for models endpoint with provider field in backend/tests/contract/test_models_provider.py

### Implementation for User Story 1

- [x] T013 [US1] Import ChatAnthropic from langchain_anthropic in backend/src/services/llm_service.py
- [x] T014 [US1] Create get_llm_for_model() factory function with provider routing in backend/src/services/llm_service.py
- [x] T015 [US1] Update get_chat_response() to use get_llm_for_model() factory in backend/src/services/llm_service.py
- [x] T016 [US1] Update get_streaming_chat_response() to use get_llm_for_model() factory in backend/src/services/llm_service.py
- [x] T017 [US1] Import Anthropic error types (AuthenticationError, RateLimitError, etc.) in backend/src/services/llm_service.py
- [x] T018 [US1] Add Anthropic exception handling in error mapper in backend/src/services/llm_service.py
- [x] T019 [US1] Update models route to include provider field in response in backend/src/api/routes/models.py

**Checkpoint**: User Story 1 complete - Claude models selectable and functional via API

---

## Phase 4: User Story 2 - Multi-Provider Model Organization (Priority: P2)

**Goal**: Users see models with provider labels for clear identification

**Independent Test**: Open model selector, verify each model shows provider prefix (e.g., "Anthropic: Claude 3.5 Sonnet")

### Tests for User Story 2

- [ ] T020 [P] [US2] Unit test for provider label display in frontend/tests/unit/ModelSelector.test.js

### Implementation for User Story 2

- [ ] T021 [US2] Update ModelSelector.vue to display provider prefix in dropdown options in frontend/src/components/ModelSelector/ModelSelector.vue
- [ ] T022 [US2] Add computed property to format model display with provider in frontend/src/components/ModelSelector/ModelSelector.vue
- [ ] T023 [US2] Update useModels composable to handle provider field in frontend/src/state/useModels.js

**Checkpoint**: User Story 2 complete - models clearly labeled by provider

---

## Phase 5: User Story 3 - Graceful Provider Configuration (Priority: P3)

**Goal**: System adapts to available providers based on API key configuration

**Independent Test**: Start app with only ANTHROPIC_API_KEY set, verify only Claude models appear

### Tests for User Story 3

- [ ] T024 [P] [US3] Unit test for single provider (Anthropic-only) configuration in backend/tests/unit/test_models_config_single_provider.py
- [ ] T025 [P] [US3] Unit test for both providers configured in backend/tests/unit/test_models_config_multi_provider.py
- [ ] T026 [P] [US3] Integration test for provider unavailability error handling in backend/tests/integration/test_provider_errors.py

### Implementation for User Story 3

- [ ] T027 [US3] Add check_provider_enabled() function in backend/src/config/models.py
- [ ] T028 [US3] Filter models list by enabled providers in load_model_configuration() in backend/src/config/models.py
- [ ] T029 [US3] Add startup validation that at least one provider is configured in backend/src/config/models.py
- [ ] T030 [US3] Add logging for provider enablement status in backend/src/config/models.py

**Checkpoint**: User Story 3 complete - flexible provider configuration working

---

## Phase 6: Edge Cases & Model Locking

**Purpose**: Implement model locking after conversation starts (FR-007)

- [ ] T031 [P] Unit test for model selector disabled state in frontend/tests/unit/ModelSelector.disabled.test.js
- [ ] T032 Add hasActiveMessages computed property to conversation state in frontend/src/state/useConversations.js
- [ ] T033 Update ModelSelector.vue to disable selector when hasActiveMessages is true in frontend/src/components/ModelSelector/ModelSelector.vue

**Checkpoint**: Model locking implemented - selector disabled during active conversations

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final validation

- [ ] T034 [P] Update CLAUDE.md with langchain-anthropic in Active Technologies section
- [ ] T035 [P] Add example .env configuration to quickstart.md validation
- [ ] T036 Run full test suite (backend + frontend) to verify no regressions
- [ ] T037 Manual integration test: verify Claude streaming parity with OpenAI

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational completion
- **Edge Cases (Phase 6)**: Can run in parallel with US2/US3
- **Polish (Phase 7)**: Depends on all stories complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses provider field from US1
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Extends configuration from Foundational

### Within Each User Story

- Tests written FIRST (TDD approach per constitution)
- Config/models before services
- Services before API routes
- Backend before frontend

### Parallel Opportunities

**Phase 2 (Foundational)**:
```
T003, T004, T005, T006 can run in parallel (all modify models.py but different sections)
```

**Phase 3 (US1 Tests)**:
```
T010, T011, T012 can run in parallel (different test files)
```

**Phase 4+5 (US2+US3)**:
```
User Story 2 and User Story 3 can run in parallel (different concerns)
```

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for ChatAnthropic instantiation in backend/tests/unit/test_llm_service_anthropic.py"
Task: "Unit test for provider routing logic in backend/tests/unit/test_llm_service_provider_routing.py"
Task: "Contract test for models endpoint with provider field in backend/tests/contract/test_models_provider.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T009)
3. Complete Phase 3: User Story 1 (T010-T019)
4. **STOP and VALIDATE**: Test Claude model selection and responses
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Provider config working
2. Add User Story 1 → Claude models functional (MVP!)
3. Add User Story 2 → Provider labels in UI
4. Add User Story 3 → Flexible configuration
5. Add Edge Cases → Model locking
6. Each increment adds value without breaking previous

### Suggested Order for Solo Developer

```
Phase 1 → Phase 2 → Phase 3 (MVP) → Phase 6 → Phase 4 → Phase 5 → Phase 7
```

This prioritizes core functionality and model locking (critical UX constraint) before polish features.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each user story is independently completable and testable
- Commit after each task or logical group
- Model locking (Phase 6) is a critical constraint from clarifications - prioritize after MVP
