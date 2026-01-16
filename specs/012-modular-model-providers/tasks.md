# Tasks: Modular Model Providers

**Input**: Design documents from `/specs/012-modular-model-providers/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Included per constitution requirement (Test-First Development ✅ REQUIRED)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: Unchanged (no frontend changes for this feature)

---

## Phase 1: Setup

**Purpose**: Create provider module structure

- [x] T001 Create providers module directory at `backend/src/services/providers/`
- [x] T002 Create providers test directory at `backend/tests/unit/providers/`
- [x] T003 Run existing contract tests to establish baseline: `cd backend && pytest tests/contract/ -v`
- [x] T004 Run existing unit tests to establish baseline: `cd backend && pytest tests/unit/ -v`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create base provider protocol/interface in `backend/src/services/providers/base.py`
- [x] T006 Create empty provider registry in `backend/src/services/providers/__init__.py`

**Checkpoint**: Provider module structure ready - user story implementation can begin

---

## Phase 3: User Story 1 - Unified Provider Configuration (Priority: P1) 🎯 MVP

**Goal**: Define all model providers in a single consolidated configuration structure

**Independent Test**: Configure a new provider entry and verify it appears in the models list without code changes to provider-specific loading functions

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T007 [P] [US1] Create ProviderConfig unit tests in `backend/tests/unit/providers/test_base.py` - test id validation, enabled computation
- [x] T008 [P] [US1] Create ProviderRegistry unit tests in `backend/tests/unit/providers/test_base.py` - test register, get, get_enabled
- [x] T009 [P] [US1] Update config tests in `backend/tests/unit/test_model_config.py` - test consolidated provider loading

### Implementation for User Story 1

- [x] T010 [US1] Implement ProviderConfig Pydantic model in `backend/src/services/providers/base.py`
- [x] T011 [US1] Implement ProviderRegistry class in `backend/src/services/providers/__init__.py`
- [x] T012 [US1] Refactor `backend/src/config/models.py` to use ProviderRegistry for consolidated model loading
- [x] T013 [US1] Add provider logging for disabled providers (missing API key) in `backend/src/config/models.py`
- [x] T014 [US1] Verify all models endpoint contract tests pass: `cd backend && pytest tests/contract/test_models_api_contract.py -v`

**Checkpoint**: ProviderRegistry infrastructure is in place. Provider metadata can be accessed programmatically.

---

## Phase 3b: User Story 1 - Unified MODELS Configuration (Priority: P1) ✅ COMPLETE

**Goal**: Consolidate OPENAI_MODELS and ANTHROPIC_MODELS into a single MODELS environment variable

**Independent Test**: Configure a single `MODELS` variable with models from multiple providers and verify they all appear correctly

### Tests for Unified Configuration

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T046 [P] [US1] Create unit tests for unified MODELS loading in `backend/tests/unit/test_model_config.py` - test single MODELS env var
- [x] T047 [P] [US1] Create unit tests for backward compatibility in `backend/tests/unit/test_model_config.py` - test fallback to legacy vars
- [x] T048 [P] [US1] Create unit tests for provider filtering in `backend/tests/unit/test_model_config.py` - test models filtered when API key missing

### Implementation for Unified Configuration

- [x] T049 [US1] Add `load_unified_models()` function in `backend/src/config/models.py` to load from single MODELS env var
- [x] T050 [US1] Update `load_model_configuration()` in `backend/src/config/models.py` to prefer MODELS, fallback to legacy vars
- [x] T051 [US1] Filter models by enabled provider (API key present) in `backend/src/config/models.py`
- [x] T052 [US1] Update `backend/.env.example` with unified MODELS configuration format
- [x] T053 [US1] Update `backend/.env.test` to use unified MODELS format
- [x] T054 [US1] N/A - `.devcontainer/.env_devcontainer.example` only contains SSH config, not model config
- [x] T055 [US1] Verify models endpoint shows all enabled providers: `cd backend && pytest tests/contract/test_models_api_contract.py -v`

**Checkpoint**: Model configuration is truly consolidated. All models defined in a single MODELS variable, filtered by enabled providers.

---

## Phase 4: User Story 2 - Consolidated Error Handling (Priority: P2)

**Goal**: Handle provider-specific errors through a unified error mapping system

**Independent Test**: Trigger various provider errors (authentication, rate limit, timeout) and verify consistent error responses regardless of provider

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T015 [P] [US2] Create error mapping unit tests in `backend/tests/unit/providers/test_errors.py` - test all OpenAI exception mappings
- [x] T016 [P] [US2] Create error mapping unit tests in `backend/tests/unit/providers/test_errors.py` - test all Anthropic exception mappings
- [x] T017 [P] [US2] Create error mapping unit tests in `backend/tests/unit/providers/test_errors.py` - test Anthropic-specific errors (NotFoundError, PermissionDeniedError, InternalServerError)

### Implementation for User Story 2

- [x] T018 [US2] Create unified error mapping module in `backend/src/services/providers/errors.py`
- [x] T019 [US2] Implement OpenAI error mapping function in `backend/src/services/providers/errors.py`
- [x] T020 [US2] Implement Anthropic error mapping function in `backend/src/services/providers/errors.py`
- [x] T021 [US2] Create generic `map_provider_error()` function that routes to correct provider mapper in `backend/src/services/providers/errors.py`
- [x] T022 [US2] Verify error response consistency: `cd backend && pytest tests/contract/test_messages_api_contract.py -v`

**Checkpoint**: Error handling is consolidated. All provider errors map to consistent LLMServiceError categories.

---

## Phase 5: User Story 3 - Provider Factory Pattern (Priority: P2)

**Goal**: Implement provider interface for adding new providers without modifying existing code

**Independent Test**: Create a mock provider implementation and verify it integrates correctly without modifying existing provider code

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T023 [P] [US3] Create OpenAI provider unit tests in `backend/tests/unit/providers/test_openai.py` - test create_llm, map_error, get_config
- [x] T024 [P] [US3] Create Anthropic provider unit tests in `backend/tests/unit/providers/test_anthropic.py` - test create_llm, map_error, get_config
- [x] T025 [P] [US3] Update LLM service tests in `backend/tests/unit/test_llm_service.py` - test provider abstraction integration

### Implementation for User Story 3

- [x] T026 [US3] Implement OpenAIProvider class in `backend/src/services/providers/openai.py` - implements BaseProvider protocol
- [x] T027 [US3] Implement AnthropicProvider class in `backend/src/services/providers/anthropic.py` - implements BaseProvider protocol
- [x] T028 [US3] Register providers in `backend/src/services/providers/__init__.py` at module import
- [x] T029 [US3] Refactor `backend/src/services/llm_service.py` to use provider registry instead of if/elif chains
- [x] T030 [US3] Remove duplicate exception handling from `get_ai_response()` in `backend/src/services/llm_service.py` - use provider.map_error()
- [x] T031 [US3] Remove duplicate exception handling from `stream_ai_response()` in `backend/src/services/llm_service.py` - use provider.map_error()
- [x] T032 [US3] Run integration tests: `cd backend && pytest tests/integration/test_model_selection.py -v`

**Checkpoint**: Provider factory pattern is complete. New providers can be added by implementing BaseProvider without modifying core code.

---

## Phase 6: User Story 4 - Test Consolidation (Priority: P3)

**Goal**: Establish consistent test patterns for providers

**Independent Test**: Verify test coverage reports show provider-agnostic test patterns alongside provider-specific tests

### Tests for User Story 4

- [x] T033 [US4] Create provider test template/base class in `backend/tests/unit/providers/__init__.py`
- [x] T034 [US4] Refactor OpenAI provider tests to use test template in `backend/tests/unit/providers/test_openai.py`
- [x] T035 [US4] Refactor Anthropic provider tests to use test template in `backend/tests/unit/providers/test_anthropic.py`

### Verification for User Story 4

- [x] T036 [US4] Run full test suite to verify all existing tests pass: `cd backend && pytest tests/ -v`
- [x] T037 [US4] Generate coverage report: `cd backend && pytest tests/ --cov=src --cov-report=html`
- [x] T038 [US4] Verify at least 40% reduction in exception handling code (SC-002) - compare line counts

**Checkpoint**: Test patterns are consolidated. All existing tests pass with the new provider structure.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final validation

- [x] T039 [P] Update `docs/architecture.md` with new providers module structure
- [x] T040 [P] Add ADR (Architectural Decision Record) for provider abstraction pattern
- [x] T041 [P] Update quickstart guide in `specs/012-modular-model-providers/quickstart.md` if needed
- [x] T042 Run full backend test suite: `cd backend && pytest tests/ -v`
- [ ] T043 Run full frontend test suite (verify no regressions): `cd frontend && npm test`
- [x] T044 Verify all contract tests pass (backward compatibility): `cd backend && pytest tests/contract/ -v`
- [ ] T045 Manual verification: Test chat with both OpenAI and Anthropic models

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational (Phase 2) completion
  - US1 (P1): Can start immediately after Foundational
  - US2 (P2): Can start after Foundational, no dependency on US1
  - US3 (P2): Can start after US1 and US2 (uses their components)
  - US4 (P3): Can start after US3 (tests the provider implementations)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1: Setup
    │
    ▼
Phase 2: Foundational
    │
    ├──────────────────┬────────────────────┐
    ▼                  ▼                    │
Phase 3: US1       Phase 4: US2            │
(P1 Config)        (P2 Errors)             │
    │                  │                    │
    └────────┬─────────┘                    │
             ▼                              │
        Phase 5: US3 ◄──────────────────────┘
        (P2 Factory)
             │
             ▼
        Phase 6: US4
        (P3 Tests)
             │
             ▼
        Phase 7: Polish
```

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Implement to make tests pass
3. Verify checkpoint before moving to next story

### Parallel Opportunities

- **Phase 1**: T003 and T004 can run in parallel
- **Phase 3 (US1)**: T007, T008, T009 tests can run in parallel
- **Phase 4 (US2)**: T015, T016, T017 tests can run in parallel
- **Phase 5 (US3)**: T023, T024, T025 tests can run in parallel; T026 and T027 implementations can run in parallel
- **Phase 7**: T039, T040, T041 can run in parallel

---

## Parallel Example: User Story 3

```bash
# Launch all tests for User Story 3 together:
Task: "Create OpenAI provider unit tests in backend/tests/unit/providers/test_openai.py"
Task: "Create Anthropic provider unit tests in backend/tests/unit/providers/test_anthropic.py"
Task: "Update LLM service tests in backend/tests/unit/test_llm_service.py"

# Launch both provider implementations together:
Task: "Implement OpenAIProvider class in backend/src/services/providers/openai.py"
Task: "Implement AnthropicProvider class in backend/src/services/providers/anthropic.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Unified Configuration)
4. **STOP and VALIDATE**: Test that all providers show in consolidated list
5. Deploy/demo if ready - configuration consolidation is valuable on its own

### Incremental Delivery

1. Setup + Foundational → Module structure ready
2. Add US1 (Configuration) → Test independently → **MVP!**
3. Add US2 (Error Handling) → Test independently → Errors are consistent
4. Add US3 (Factory Pattern) → Test independently → Providers are modular
5. Add US4 (Test Consolidation) → Test independently → Tests follow patterns
6. Polish → Documentation complete

### Sequential Execution (Single Developer)

Follow phases in order: 1 → 2 → 3 → 4 → 5 → 6 → 7

Each phase completes a meaningful increment.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD per constitution)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Run contract tests frequently to ensure backward compatibility (FR-006)
