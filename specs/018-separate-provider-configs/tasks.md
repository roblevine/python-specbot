# Tasks: Separate Provider Configurations

**Input**: Design documents from `/specs/018-separate-provider-configs/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete)

**Tests**: Included per Constitution requirement (Test-First Development)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`
- Frontend unchanged (API response format preserved)

---

## Phase 1: Setup (Configuration Files)

**Purpose**: Update test configuration files to use new env var format

- [x] T001 Update test configuration in backend/.env.test to use new provider-specific format
- [x] T002 [P] Update example configuration in backend/.env.example with new format and migration guide

**Checkpoint**: Test and example configurations ready for new format

---

## Phase 2: Foundational (Core Model Changes)

**Purpose**: Create new Pydantic models and update loading infrastructure

**⚠️ CRITICAL**: These changes must be complete before user story implementation

- [x] T003 Create ProviderModelConfig Pydantic model (simplified, no provider/default fields) in backend/src/config/models.py
- [x] T004 Add PROVIDER_ENV_VARS constant mapping provider IDs to env var names in backend/src/config/models.py
- [x] T005 Create helper function to load models from a single provider env var in backend/src/config/models.py

**Checkpoint**: Foundation ready - core models and helpers in place

---

## Phase 3: User Story 1 - Separate Provider Model Collections (Priority: P1) 🎯 MVP

**Goal**: Support separate `OPENAI_MODELS` and `ANTHROPIC_MODELS` environment variables

**Independent Test**: Configure separate provider env vars and verify models load with correct provider association

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T006 [P] [US1] Unit test for loading OPENAI_MODELS only in backend/tests/unit/test_model_config.py
- [x] T007 [P] [US1] Unit test for loading ANTHROPIC_MODELS only in backend/tests/unit/test_model_config.py
- [x] T008 [P] [US1] Unit test for loading both provider configs in backend/tests/unit/test_model_config.py
- [x] T009 [P] [US1] Unit test for provider filtering when API key not set in backend/tests/unit/test_model_config.py
- [x] T010 [P] [US1] Unit test for duplicate model ID validation across providers in backend/tests/unit/test_model_config.py
- [x] T011 [P] [US1] Unit test for invalid JSON error messages identifying provider in backend/tests/unit/test_model_config.py
- [x] T012 [P] [US1] Unit test for empty provider array handling in backend/tests/unit/test_model_config.py
- [x] T013 [US1] Contract test verifying /api/v1/models response format unchanged in backend/tests/contract/test_models_api_contract.py

### Implementation for User Story 1

- [x] T014 [US1] Implement load_provider_models() function to parse single provider env var in backend/src/config/models.py
- [x] T015 [US1] Update load_model_configuration() to iterate over all providers and merge configs in backend/src/config/models.py
- [x] T016 [US1] Add provider ID to each model when merging (provider field computed from source) in backend/src/config/models.py
- [x] T017 [US1] Implement duplicate model ID validation across all provider configs in backend/src/config/models.py
- [x] T018 [US1] Update error messages to identify which provider config has issues in backend/src/config/models.py
- [x] T019 [US1] Remove support for legacy MODELS env var (silently ignore if present) in backend/src/config/models.py
- [x] T020 [US1] Update integration test env setup to use new format in backend/tests/integration/test_model_selection.py

**Checkpoint**: User Story 1 complete - separate provider configs working, tests passing

---

## Phase 4: User Story 2 - Single Default Model Reference (Priority: P1)

**Goal**: Support `DEFAULT_MODEL` environment variable for specifying default model by ID

**Independent Test**: Set DEFAULT_MODEL to various model IDs and verify correct default selection

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T021 [P] [US2] Unit test for DEFAULT_MODEL set to valid OpenAI model in backend/tests/unit/test_model_config.py
- [x] T022 [P] [US2] Unit test for DEFAULT_MODEL set to valid Anthropic model in backend/tests/unit/test_model_config.py
- [x] T023 [P] [US2] Unit test for DEFAULT_MODEL not set (fallback to first available) in backend/tests/unit/test_model_config.py
- [x] T024 [P] [US2] Unit test for DEFAULT_MODEL referencing invalid model ID (error) in backend/tests/unit/test_model_config.py
- [x] T025 [P] [US2] Unit test for DEFAULT_MODEL provider disabled (fallback with warning) in backend/tests/unit/test_model_config.py
- [x] T026 [US2] Integration test for default model selection flow in backend/tests/integration/test_model_selection.py

### Implementation for User Story 2

- [x] T027 [US2] Add DEFAULT_MODEL env var loading in backend/src/config/models.py
- [x] T028 [US2] Implement resolve_default_model() function with fallback logic in backend/src/config/models.py
- [x] T029 [US2] Update ModelsConfiguration validation to remove "exactly one default" requirement in backend/src/config/models.py
- [x] T030 [US2] Set default=True on the resolved default model when building final config in backend/src/config/models.py
- [x] T031 [US2] Add warning log when DEFAULT_MODEL provider is disabled and fallback used in backend/src/config/models.py
- [x] T032 [US2] Add clear error for invalid DEFAULT_MODEL reference in backend/src/config/models.py

**Checkpoint**: User Story 2 complete - DEFAULT_MODEL working, tests passing

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [x] T033 [P] Update backend/.env.example with complete migration guide in comments
- [x] T034 [P] Remove old ModelConfig.default field validator that required exactly one default in backend/src/config/models.py
- [x] T035 [P] Remove old ModelConfig.provider field requirement (now computed) in backend/src/config/models.py
- [x] T036 Clean up any deprecated code paths in backend/src/config/models.py
- [x] T037 Run full test suite and verify all tests pass
- [ ] T038 Run quickstart.md validation scenarios manually
- [x] T039 [P] Update CLAUDE.md with 018 feature summary in Active Technologies section

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion (can run parallel to US1)
- **Polish (Phase 5)**: Depends on both user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - Independent
- **User Story 2 (P1)**: Can start after Foundational - Independent (but builds on US1 loading logic)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Infrastructure (helpers) before feature implementation
- Validation before error handling
- Story complete before moving to next

### Parallel Opportunities

**Phase 1 (Setup)**:
- T001 and T002 can run in parallel

**Phase 2 (Foundational)**:
- T003, T004, T005 are sequential (build on each other)

**Phase 3 (US1 Tests)**:
- T006, T007, T008, T009, T010, T011, T012 can all run in parallel
- T013 (contract test) can run in parallel with unit tests

**Phase 4 (US2 Tests)**:
- T021, T022, T023, T024, T025 can all run in parallel

**Phase 5 (Polish)**:
- T033, T034, T035, T039 can run in parallel

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all unit tests for User Story 1 together:
Task: "Unit test for loading OPENAI_MODELS only in backend/tests/unit/test_model_config.py"
Task: "Unit test for loading ANTHROPIC_MODELS only in backend/tests/unit/test_model_config.py"
Task: "Unit test for loading both provider configs in backend/tests/unit/test_model_config.py"
Task: "Unit test for provider filtering when API key not set in backend/tests/unit/test_model_config.py"
Task: "Unit test for duplicate model ID validation across providers in backend/tests/unit/test_model_config.py"
Task: "Unit test for invalid JSON error messages identifying provider in backend/tests/unit/test_model_config.py"
Task: "Unit test for empty provider array handling in backend/tests/unit/test_model_config.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T005)
3. Complete Phase 3: User Story 1 Tests (T006-T013) - verify they FAIL
4. Complete Phase 3: User Story 1 Implementation (T014-T020)
5. **STOP and VALIDATE**: Run tests, verify US1 works independently
6. Deploy/demo if ready

### Full Feature Delivery

1. Complete MVP (User Story 1)
2. Add User Story 2 (T021-T032)
3. Complete Polish phase (T033-T039)
4. Final validation

### Parallel Team Strategy

With two developers after Foundational phase:
- Developer A: User Story 1 (provider loading)
- Developer B: User Story 2 (default model) - starts T021-T026, waits for US1 loading to be ready for T027-T032

---

## Task Summary

| Phase | Task Count | Parallel Tasks |
|-------|------------|----------------|
| Setup | 2 | 2 |
| Foundational | 3 | 0 |
| User Story 1 | 15 | 8 (tests) |
| User Story 2 | 12 | 6 (tests) |
| Polish | 7 | 4 |
| **Total** | **39** | **20** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- API contract unchanged - frontend needs no changes
- Legacy MODELS env var silently ignored (no deprecation warnings)
