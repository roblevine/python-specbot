# Tasks: Consumer-Driven Contract Testing with Snapshot Validation

**Feature**: 004-contract-snapshot-testing
**Input**: Design documents from `/specs/004-contract-snapshot-testing/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: TDD approach - tests are included and MUST be written FIRST before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Monorepo structure**: `backend/`, `frontend/`, `specs/` at repository root
- **Backend**: Python 3.13, pytest, FastAPI
- **Frontend**: JavaScript ES6+, Vitest, Vue 3

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for contract testing

- [x] T001 Create contract snapshots directory at specs/contract-snapshots/ with .gitkeep
- [x] T002 [P] Install core-ajv-schema-validator dependency in frontend/package.json
- [x] T003 [P] Verify openapi-core is available in backend virtual environment

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create frontend contract test helper utilities directory at frontend/tests/helpers/
- [x] T005 Create backend contract test helper utilities directory at backend/tests/helpers/
- [x] T006 Create frontend contract tests directory at frontend/tests/contract/
- [x] T007 Create backend contract tests directory at backend/tests/contract/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Automatic Contract Snapshot Capture (Priority: P1 MVP) 🎯

**Goal**: Frontend tests automatically capture actual HTTP request formats and validate them against OpenAPI spec

**Independent Test**: Modify frontend API client code, run frontend tests, verify snapshots are generated in specs/contract-snapshots/ with correct request format. Test passes if snapshots are valid JSON matching OpenAPI schema.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Create failing contract test for sendMessage operation in frontend/tests/contract/sendMessage.test.js
- [x] T009 [P] [US1] Create failing contract test for healthCheck operation in frontend/tests/contract/healthCheck.test.js

### Implementation for User Story 1

- [x] T010 [US1] Implement snapshot capture helper function in frontend/tests/helpers/contract.js (captureSnapshot, normalizeRequest, validateRequest)
- [x] T011 [US1] Implement dynamic data normalization in frontend/tests/helpers/contract.js (UUIDs, timestamps)
- [x] T012 [US1] Implement OpenAPI validation integration using core-ajv-schema-validator in frontend/tests/helpers/contract.js
- [x] T013 [US1] Update sendMessage contract test to use snapshot capture helper in frontend/tests/contract/sendMessage.test.js
- [x] T014 [US1] Update healthCheck contract test to use snapshot capture helper in frontend/tests/contract/healthCheck.test.js
- [x] T015 [US1] Verify frontend tests pass and snapshots are generated in specs/contract-snapshots/

**Checkpoint**: At this point, frontend tests should capture snapshots automatically. Run `cd frontend && npm test tests/contract/` to verify.

---

## Phase 4: User Story 2 - Backend Contract Replay Validation (Priority: P1 MVP)

**Goal**: Backend tests automatically load frontend snapshots and replay them to verify backend can handle actual frontend requests

**Independent Test**: Run backend contract tests which load snapshots from specs/contract-snapshots/ and replay to backend. Test passes if backend successfully processes all frontend request formats.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T016 [US2] Create failing contract replay test in backend/tests/contract/test_replay.py (parametrized test that loads all snapshots)

### Implementation for User Story 2

- [x] T017 [US2] Implement snapshot loading helper in backend/tests/helpers/contract.py (load_snapshots function)
- [x] T018 [US2] Implement snapshot replay helper in backend/tests/helpers/contract.py (replay_snapshot function)
- [x] T019 [US2] Implement OpenAPI response validation in backend/tests/helpers/contract.py using openapi-core
- [x] T020 [US2] Update contract replay test to use helpers in backend/tests/contract/test_replay.py
- [x] T021 [US2] Add error reporting for contract mismatches in backend/tests/contract/test_replay.py
- [x] T022 [US2] Verify backend tests pass and can process all frontend snapshots

**Checkpoint**: At this point, both frontend and backend contract tests should pass. Run `cd backend && PYTHONPATH=/workspaces/python-specbot/backend venv/bin/pytest tests/contract/ -v` to verify.

---

## Phase 5: User Story 3 - CI Pipeline Contract Enforcement (Priority: P2)

**Goal**: CI pipeline automatically verifies snapshots are fresh and both sides can handle each other's formats

**Independent Test**: Create PR with intentional contract changes and verify CI fails with actionable error messages when snapshots are stale or incompatible.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T023 [P] [US3] Create CI workflow file skeleton at .github/workflows/contract-tests.yml
- [ ] T024 [P] [US3] Create snapshot freshness check script at scripts/check-snapshot-freshness.sh

### Implementation for User Story 3

- [ ] T025 [US3] Implement frontend contract test job in .github/workflows/contract-tests.yml (install deps, run tests, upload snapshots)
- [ ] T026 [US3] Implement backend contract replay test job in .github/workflows/contract-tests.yml (download snapshots, run tests)
- [ ] T027 [US3] Implement snapshot freshness check in scripts/check-snapshot-freshness.sh (git diff detection)
- [ ] T028 [US3] Add snapshot freshness validation step in .github/workflows/contract-tests.yml
- [ ] T029 [US3] Add contract test status reporting in .github/workflows/contract-tests.yml
- [ ] T030 [US3] Test CI workflow with intentional contract break to verify failure detection

**Checkpoint**: At this point, CI should enforce contract testing on every PR. Create a test PR to verify.

---

## Phase 6: User Story 4 - Developer Git Hook Assistance (Priority: P3)

**Goal**: Pre-commit hooks automatically regenerate snapshots and prompt developer to review changes

**Independent Test**: Modify API client code, run git commit, verify pre-commit hook regenerates snapshots and shows diff for review.

### Tests for User Story 4 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T031 [P] [US4] Create test script for pre-commit hook at scripts/test-pre-commit.sh
- [ ] T032 [P] [US4] Create pre-commit hook skeleton at .git/hooks/pre-commit or use husky

### Implementation for User Story 4

- [ ] T033 [US4] Implement API file detection in pre-commit hook (frontend/src/services/, backend/src/, specs/003-backend-api-loopback/)
- [ ] T034 [US4] Implement snapshot regeneration trigger in pre-commit hook (run frontend contract tests)
- [ ] T035 [US4] Implement snapshot diff display in pre-commit hook (git diff specs/contract-snapshots/)
- [ ] T036 [US4] Implement user prompt for action in pre-commit hook (stage snapshots or abort)
- [ ] T037 [US4] Add skip logic for non-API commits in pre-commit hook
- [ ] T038 [US4] Test pre-commit hook with API changes and verify snapshot regeneration

**Checkpoint**: At this point, git hooks should assist developers with automatic snapshot management. Test by modifying API code and committing.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T039 [P] Add comprehensive error messages to contract validation failures in frontend/tests/helpers/contract.js
- [ ] T040 [P] Add detailed error reporting to backend contract replay failures in backend/tests/helpers/contract.py
- [ ] T041 [P] Update quickstart.md validation by running all examples from the guide
- [ ] T042 [P] Add contract testing documentation to project README.md
- [ ] T043 [P] Verify performance goals (snapshot generation < 1s, test execution < 2min)
- [ ] T044 Create example of contract testing workflow in developer documentation
- [ ] T045 Add troubleshooting guide for common contract test failures

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - Frontend snapshot capture
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion - Backend needs snapshots to replay
- **User Story 3 (Phase 5)**: Depends on User Stories 1 & 2 completion - CI needs both working
- **User Story 4 (Phase 6)**: Depends on User Story 1 completion - Git hooks use frontend tests
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Frontend Capture)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1 - Backend Replay)**: DEPENDS on User Story 1 - Needs snapshots to exist
- **User Story 3 (P2 - CI Enforcement)**: DEPENDS on User Stories 1 & 2 - Needs both test suites working
- **User Story 4 (P3 - Git Hooks)**: Can start after User Story 1 - Only uses frontend tests

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Helper utilities before test implementations
- Core functionality before error handling
- Verification step at end of each story

### Parallel Opportunities

- **Phase 1 Setup**: All tasks (T001, T002, T003) can run in parallel
- **Phase 2 Foundational**: All tasks (T004-T007) can run in parallel
- **User Story 1 Tests**: T008 and T009 can run in parallel (different files)
- **User Story 3 Tests**: T023 and T024 can run in parallel (different files)
- **User Story 4 Tests**: T031 and T032 can run in parallel (different files)
- **Polish Phase**: T039, T040, T041, T042, T043 can all run in parallel (different files)

**CRITICAL**: User Story 2 CANNOT start until User Story 1 is complete (needs snapshots to exist)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create failing contract test for sendMessage operation in frontend/tests/contract/sendMessage.test.js"
Task: "Create failing contract test for healthCheck operation in frontend/tests/contract/healthCheck.test.js"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T007) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T008-T015) - Frontend snapshot capture
4. **STOP and VALIDATE**: Run frontend tests, verify snapshots generated
5. Complete Phase 4: User Story 2 (T016-T022) - Backend replay
6. **STOP and VALIDATE**: Run backend tests, verify snapshots replayed successfully
7. **MVP COMPLETE**: Contract testing working locally for both frontend and backend

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **Demo: Frontend captures contracts**
3. Add User Story 2 → Test independently → **Demo: End-to-end contract validation** (MVP!)
4. Add User Story 3 → Test independently → **Demo: CI enforcement**
5. Add User Story 4 → Test independently → **Demo: Developer experience with git hooks**
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T007)
2. Once Foundational is done:
   - Developer A: User Story 1 (T008-T015) - Frontend capture
   - Must complete before Developer B can proceed
3. After User Story 1 complete:
   - Developer B: User Story 2 (T016-T022) - Backend replay
   - Developer C: User Story 4 (T031-T038) - Git hooks (can start in parallel)
4. After User Stories 1 & 2 complete:
   - Developer D: User Story 3 (T023-T030) - CI enforcement
5. All developers: Polish phase in parallel (T039-T045)

---

## Task Count Summary

- **Total Tasks**: 45
- **Setup Phase**: 3 tasks
- **Foundational Phase**: 4 tasks
- **User Story 1 (P1)**: 8 tasks
- **User Story 2 (P1)**: 7 tasks
- **User Story 3 (P2)**: 8 tasks
- **User Story 4 (P3)**: 8 tasks
- **Polish Phase**: 7 tasks

**Parallel Opportunities Identified**: 15 tasks marked [P] can run in parallel with other tasks

**MVP Scope** (User Stories 1 & 2): 19 tasks total (Setup + Foundational + US1 + US2)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- User Story 2 has HARD DEPENDENCY on User Story 1 (needs snapshots)
- User Story 3 has HARD DEPENDENCY on User Stories 1 & 2 (needs both test suites)
- User Story 4 can run after User Story 1 only (independent of backend)
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Contract snapshots are committed to git as test artifacts
