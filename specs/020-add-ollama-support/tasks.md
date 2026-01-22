# Tasks: Add Ollama Model Support

**Input**: Design documents from `/specs/020-add-ollama-support/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Unit tests included per constitution (III. Test-First Development)

**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`
- Paths follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add new dependency and prepare configuration

- [x] T001 Add `langchain-ollama>=0.2.0` to backend/requirements.txt

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure changes that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 [P] Extend `provider` Literal type to include `"ollama"` in backend/src/config/models.py
- [x] T003 [P] Add `"ollama"` entry to `PROVIDERS` dict in backend/src/config/models.py
- [x] T004 [P] Add `"ollama": "OLLAMA_MODELS"` to `PROVIDER_ENV_VARS` dict in backend/src/config/models.py
- [x] T005 Make `api_key_env` optional in `ProviderConfig` (allow `None`) in backend/src/services/providers/base.py
- [x] T006 Update `check_provider_enabled()` to handle providers with no API key in backend/src/config/models.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Use Local Ollama Models (Priority: P1) 🎯 MVP

**Goal**: Users can select Ollama models and chat with locally-hosted LLMs

**Independent Test**: Configure Ollama models in env, start local Ollama server, select model in UI, send message and verify streamed response

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T007 [P] [US1] Unit test for OllamaProvider initialization in backend/tests/unit/test_ollama_provider.py
- [x] T008 [P] [US1] Unit test for OllamaProvider.create_llm() in backend/tests/unit/test_ollama_provider.py
- [x] T009 [P] [US1] Unit test for Ollama model configuration loading in backend/tests/unit/test_model_config.py

### Implementation for User Story 1

- [x] T010 [US1] Create OllamaProvider class extending AbstractProvider in backend/src/services/providers/ollama.py
- [x] T011 [US1] Implement `provider_id` property returning `"ollama"` in backend/src/services/providers/ollama.py
- [x] T012 [US1] Implement `get_config()` method returning Ollama ProviderConfig in backend/src/services/providers/ollama.py
- [x] T013 [US1] Implement `create_llm()` method returning ChatOllama instance in backend/src/services/providers/ollama.py
- [x] T014 [US1] Register OllamaProvider in provider registry in backend/src/services/providers/__init__.py
- [x] T015 [US1] Add Ollama configuration example to backend/.env.example
- [x] T016 [US1] Add structured logging for Ollama provider initialization in backend/src/services/providers/ollama.py

**Checkpoint**: User Story 1 complete - can select and use Ollama models for chat

---

## Phase 4: User Story 2 - Handle Ollama Server Unavailable (Priority: P2)

**Goal**: Clear error messages when Ollama server is unreachable

**Independent Test**: Configure Ollama models, stop Ollama server, send message, verify appropriate error message

### Tests for User Story 2

- [x] T017 [P] [US2] Unit test for `map_ollama_error()` connection error mapping in backend/tests/unit/test_ollama_provider.py
- [x] T018 [P] [US2] Unit test for `map_ollama_error()` timeout error mapping in backend/tests/unit/test_ollama_provider.py
- [x] T019 [P] [US2] Unit test for `map_ollama_error()` model not found error mapping in backend/tests/unit/test_ollama_provider.py

### Implementation for User Story 2

- [x] T020 [US2] Create `map_ollama_error()` function in backend/src/services/providers/errors.py
- [x] T021 [US2] Map `httpx.ConnectError` to `LLMConnectionError` with Ollama-specific message in backend/src/services/providers/errors.py
- [x] T022 [US2] Map `httpx.TimeoutException` to `LLMTimeoutError` in backend/src/services/providers/errors.py
- [x] T023 [US2] Map `httpx.HTTPStatusError` (404) to `LLMBadRequestError` for model not found in backend/src/services/providers/errors.py
- [x] T024 [US2] Update `map_provider_error()` to route `"ollama"` to `map_ollama_error()` in backend/src/services/providers/errors.py
- [x] T025 [US2] Implement `map_error()` method in OllamaProvider using `map_ollama_error()` in backend/src/services/providers/ollama.py

**Checkpoint**: User Story 2 complete - Ollama connection errors show clear messages

---

## Phase 5: User Story 3 - Configure Custom Ollama Server URL (Priority: P3)

**Goal**: Support `OLLAMA_BASE_URL` for non-default Ollama server locations

**Independent Test**: Run Ollama on custom port, configure OLLAMA_BASE_URL, verify connection to custom URL

### Tests for User Story 3

- [x] T026 [P] [US3] Unit test for default base URL (`http://localhost:11434`) in backend/tests/unit/test_ollama_provider.py
- [x] T027 [P] [US3] Unit test for custom base URL from `OLLAMA_BASE_URL` env var in backend/tests/unit/test_ollama_provider.py

### Implementation for User Story 3

- [x] T028 [US3] Read `OLLAMA_BASE_URL` from environment in OllamaProvider.__init__() in backend/src/services/providers/ollama.py
- [x] T029 [US3] Default to `http://localhost:11434` when `OLLAMA_BASE_URL` not set in backend/src/services/providers/ollama.py
- [x] T030 [US3] Pass base_url to ChatOllama in create_llm() in backend/src/services/providers/ollama.py
- [x] T031 [US3] Add `OLLAMA_BASE_URL` example to backend/.env.example

**Checkpoint**: User Story 3 complete - can connect to custom Ollama server URLs

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and validation

- [x] T032 [P] Update CLAUDE.md with Ollama provider information
- [x] T033 [P] Run all unit tests and verify passing: `pytest backend/tests/unit/ -v`
- [x] T034 Validate quickstart.md instructions work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - MVP delivery point
- **User Story 2 (Phase 4)**: Depends on Foundational - can parallel with US1 if needed
- **User Story 3 (Phase 5)**: Depends on Foundational - can parallel with US1/US2 if needed
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: Core functionality - no dependencies on other stories
- **User Story 2 (P2)**: Error handling - integrates with US1's OllamaProvider but independently testable
- **User Story 3 (P3)**: Custom URL - extends US1's OllamaProvider but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Create provider before registering
- Error mapping before using in provider

### Parallel Opportunities

```
Phase 2 (Foundational):
  T002, T003, T004 can run in parallel (different dicts/types)
  T005, T006 must be sequential (depend on each other)

Phase 3 (US1):
  T007, T008, T009 can run in parallel (test files)
  T010-T016 mostly sequential (building provider)

Phase 4 (US2):
  T017, T018, T019 can run in parallel (test functions)
  T020-T025 sequential (building error mapping)

Phase 5 (US3):
  T026, T027 can run in parallel (test functions)
  T028-T031 sequential (extending provider)
```

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all US1 tests together:
Task: "T007 Unit test for OllamaProvider initialization"
Task: "T008 Unit test for OllamaProvider.create_llm()"
Task: "T009 Unit test for Ollama model configuration loading"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002-T006)
3. Complete Phase 3: User Story 1 (T007-T016)
4. **STOP and VALIDATE**: Test with local Ollama server
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **MVP Ready!**
3. Add User Story 2 → Test independently → Better error handling
4. Add User Story 3 → Test independently → Custom URL support
5. Polish → Documentation updated

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Setup | 1 | Add dependency |
| Foundational | 5 | Config & base changes |
| US1 (P1) | 10 | Core Ollama support |
| US2 (P2) | 9 | Error handling |
| US3 (P3) | 6 | Custom URL |
| Polish | 3 | Documentation |
| **Total** | **34** | |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story independently testable after Foundational phase
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
