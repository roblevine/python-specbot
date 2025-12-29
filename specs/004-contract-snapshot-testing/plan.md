# Implementation Plan: Consumer-Driven Contract Testing with Snapshot Validation

**Branch**: `004-contract-snapshot-testing` | **Date**: 2025-12-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-contract-snapshot-testing/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement consumer-driven contract testing to prevent frontend-backend contract mismatches (like the recent `conversationId` format bug). The system will automatically capture actual frontend HTTP requests during tests, validate them against OpenAPI spec, write them as snapshots, and replay them to the backend to verify compatibility. This approach catches contract breaks before code review and provides executable contract documentation.

## Technical Context

**Frontend**:
- **Language/Version**: JavaScript ES6+, Vue 3.4.0
- **Testing Framework**: Vitest 1.0.0 (already in use)
- **Primary Dependencies**: Existing OpenAPI spec from feature 003
- **New Dependencies Needed**: `core-ajv-schema-validator` - OpenAPI request/response validator using AJV (JavaScript equivalent to Python's openapi-core)

**Backend**:
- **Language/Version**: Python 3.13 (confirmed from devcontainer)
- **Testing Framework**: pytest 8.3.0 (already in use)
- **Primary Dependencies**: openapi-core 0.18.2 (already installed for contract validation)
- **New Dependencies Needed**: None - existing tools sufficient

**Shared**:
- **Storage**: File system (`specs/contract-snapshots/`) - JSON files committed to git
- **Target Platform**: Monorepo (frontend + backend in same repository)
- **Project Type**: Web application (frontend + backend)

**Performance Goals**:
- Snapshot generation: < 1 second per API operation
- Contract test execution: < 2 minutes for full suite (frontend + backend combined)
- CI pipeline: < 5 minutes total (including snapshot generation + replay)

**Constraints**:
- Snapshots must be small (< 1MB per file) for git commits
- Dynamic data (timestamps, UUIDs) must be normalized for stable diffs
- Tests must be independently runnable (frontend tests don't require backend to be running)

**Scale/Scope**:
- Initial: 1 API endpoint (POST /api/v1/messages) from feature 003
- Target: All future API operations
- Expected: 5-10 API operations within 2 sprints

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: API-First Design ✅
**Status**: PASS
- Snapshots capture actual API request contracts from frontend
- Validation against existing OpenAPI specification (feature 003)
- No new API endpoints being created, only testing infrastructure

### Principle II: Modular Architecture ✅
**Status**: PASS
- Contract testing is self-contained module in test directories
- Clear boundaries: frontend tests capture, backend tests replay
- Independently testable (can run frontend or backend tests separately)

### Principle III: Test-First Development (NON-NEGOTIABLE) ✅
**Status**: PASS - TDD Workflow Planned
1. Write tests that capture snapshots and validate against OpenAPI (red)
2. Implement snapshot capture mechanism (green)
3. Write backend tests that load/replay snapshots (red)
4. Implement backend replay mechanism (green)
5. Refactor while keeping tests green

### Principle IV: Integration & Contract Testing ✅
**Status**: PASS - This IS Contract Testing
- Core purpose is contract testing between frontend and backend
- Validates actual integration (frontend snapshots replayed to backend)
- Tests both sides of the contract (consumer and provider)

### Principle V: Observability & Debuggability ✅
**Status**: PASS
- Snapshots are human-readable JSON with clear structure
- Test failures include specific field/format errors
- Metadata in snapshots (timestamp, version) aids debugging
- CI reports show exactly which contract scenarios failed

### Principle VI: Simplicity & YAGNI ✅
**Status**: PASS
- Uses existing testing frameworks (Vitest, pytest)
- No new complex abstractions - just capture/replay
- Leverages existing OpenAPI spec validation
- Snapshots are simple JSON files in git

### Principle VII: Versioning & Breaking Changes ✅
**Status**: PASS
- Snapshots are version-controlled artifacts
- Git diff shows exactly what changed in contracts
- CI enforces that snapshot changes are committed
- Breaking changes become explicit through failing tests

### Principle VIII: Incremental Delivery & Thin Slices (NON-NEGOTIABLE) ✅
**Status**: PASS - Clear P1 MVP Defined
- **P1 MVP Slice 1**: Frontend snapshot capture + OpenAPI validation
- **P1 MVP Slice 2**: Backend snapshot replay
- **P2 Slice**: CI enforcement
- **P3 Slice**: Git hooks
Each slice is independently testable and delivers working functionality.

### Principle IX: Living Architecture Documentation 📝
**Status**: REQUIRES UPDATE
- **Action Required**: Update `architecture.md` after implementation
- **Changes to Document**:
  - New test infrastructure module (contract testing)
  - Data flow: frontend tests → snapshots → backend tests
  - New directory: `specs/contract-snapshots/`
  - Integration point: shared snapshot directory between frontend/backend

**Overall Constitution Status**: ✅ **PASS** - Ready for Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/routes/
│   ├── services/
│   ├── middleware/
│   └── utils/
└── tests/
    ├── contract/              # NEW: Backend contract replay tests
    │   ├── test_replay.py     # Replays frontend snapshots
    │   └── helpers/
    │       └── contract.py    # Snapshot loading utilities
    ├── integration/
    └── unit/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/              # API client code (generates requests)
└── tests/
    ├── contract/              # NEW: Frontend contract capture tests
    │   └── messages.test.js   # Captures request snapshots
    └── helpers/
        └── contract.js        # NEW: Snapshot capture utilities

specs/
├── contract-snapshots/        # NEW: Shared snapshot directory
│   ├── sendMessage.json       # POST /api/v1/messages snapshot
│   └── .gitkeep
├── 003-backend-api-loopback/
│   └── openapi.json           # API contract (source of truth)
└── 004-contract-snapshot-testing/
    ├── spec.md
    ├── plan.md (this file)
    ├── research.md
    ├── data-model.md
    └── quickstart.md
```

**Structure Decision**: Monorepo with frontend/backend separation. Contract tests live in each side's test directory (`frontend/tests/contract/`, `backend/tests/contract/`), sharing snapshots via `specs/contract-snapshots/`. This structure allows independent test execution while maintaining shared contract artifacts in version control.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
