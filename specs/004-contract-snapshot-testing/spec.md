# Feature Specification: Consumer-Driven Contract Testing with Snapshot Validation

**Feature Branch**: `004-contract-snapshot-testing`
**Created**: 2025-12-29
**Status**: Draft
**Input**: User description: "Implement consumer-driven contract testing with automatic snapshot capture and validation to prevent client-server contract mismatches between frontend and backend"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic Contract Snapshot Capture (Priority: P1 MVP)

As a frontend developer, when I make changes to API client code, I need the system to automatically capture the exact request format my code generates, so that any contract mismatches with the backend are detected immediately without manual verification.

**Why this priority**: This is the foundation of the entire contract testing system. Without automatic snapshot capture, we fall back to manual contract verification which is error-prone and was the root cause of the recent `conversationId` format mismatch bug.

**Independent Test**: Can be fully tested by modifying frontend API client code, running tests, and verifying that fresh snapshots are generated in `specs/contract-snapshots/` with the correct request format. Delivers value by providing executable contract documentation that reflects actual frontend behavior.

**Acceptance Scenarios**:

1. **Given** the frontend test suite runs, **When** API client code executes during tests, **Then** the system captures the exact HTTP request (method, path, headers, body) and writes it to a snapshot file in JSON format
2. **Given** a contract snapshot exists from a previous test run, **When** frontend tests run again, **Then** the snapshot file is overwritten with the latest request format
3. **Given** frontend code sends an invalid request format, **When** snapshot generation runs, **Then** the test fails with clear validation errors showing what part of the request doesn't match the OpenAPI specification
4. **Given** multiple API operations exist (e.g., send message, delete message), **When** tests run, **Then** each operation generates its own separate snapshot file with a descriptive name

---

### User Story 2 - Backend Contract Replay Validation (Priority: P1 MVP)

As a backend developer, I need the backend test suite to automatically load and replay the exact requests captured from frontend tests, so that I can verify the backend correctly handles the actual request format the frontend sends.

**Why this priority**: Contract validation is only complete when both sides are verified. This story ensures the backend can process frontend's actual requests, preventing the backend from unknowingly breaking compatibility.

**Independent Test**: Can be fully tested by running backend contract tests which load frontend snapshots and replay them to the backend API. Delivers value by catching backend changes that would break frontend integration before code is merged.

**Acceptance Scenarios**:

1. **Given** frontend has generated contract snapshots, **When** backend contract tests run, **Then** the tests load each snapshot file and replay the captured request to the backend API
2. **Given** backend successfully processes a replayed request, **When** the test validates the response, **Then** the response matches the expected structure defined in the OpenAPI specification
3. **Given** backend cannot process a frontend snapshot request, **When** the contract test runs, **Then** the test fails with a clear error message showing exactly what field or format the backend rejected
4. **Given** no frontend snapshots exist, **When** backend contract tests run, **Then** the tests fail with a clear message instructing developers to run frontend tests first to generate snapshots

---

### User Story 3 - CI Pipeline Contract Enforcement (Priority: P2)

As a DevOps engineer, I need the CI pipeline to automatically verify that contract snapshots are fresh and that both frontend and backend can handle each other's formats, so that no pull request can merge with contract mismatches.

**Why this priority**: Automation in CI ensures contract validation happens on every change without relying on developer discipline. This prevents contract drift from reaching production.

**Independent Test**: Can be fully tested by creating a PR with intentional contract changes and verifying that CI fails with actionable error messages when snapshots are stale or incompatible. Delivers value by preventing broken integrations from being merged.

**Acceptance Scenarios**:

1. **Given** a pull request modifies frontend API client code, **When** CI runs, **Then** CI regenerates snapshots, validates them against OpenAPI spec, replays them to backend, and fails the build if any step fails
2. **Given** contract snapshots have changed but are not committed, **When** CI runs, **Then** the build fails with a diff showing what changed and instructions to commit the updated snapshots
3. **Given** frontend snapshots exist and backend can handle them, **When** CI runs, **Then** the build passes and reports which contract scenarios were successfully validated
4. **Given** backend contract tests fail on replayed snapshots, **When** CI runs, **Then** the build fails showing the exact request that failed and the backend's error response

---

### User Story 4 - Developer Git Hook Assistance (Priority: P3)

As a developer, when I commit changes to API-related code, I need git hooks to automatically regenerate snapshots and prompt me to review changes, so that I don't accidentally commit contract-breaking changes.

**Why this priority**: While helpful, this is less critical than automated CI validation. It provides earlier feedback during development but isn't essential for preventing bad merges since CI will catch issues.

**Independent Test**: Can be fully tested by modifying API client code, attempting to commit, and verifying that the pre-commit hook regenerates snapshots and prompts for review. Delivers value by catching contract issues before code review.

**Acceptance Scenarios**:

1. **Given** I modify frontend API client code, **When** I run `git commit`, **Then** a pre-commit hook regenerates contract snapshots and shows me a diff of any changes
2. **Given** contract snapshots changed during pre-commit, **When** the hook prompts me for action, **Then** I can choose to stage the snapshot changes or abort the commit
3. **Given** I commit changes unrelated to API contracts, **When** the pre-commit hook runs, **Then** it skips snapshot regeneration to avoid slowing down unrelated commits
4. **Given** snapshot generation fails during pre-commit, **When** the hook detects the failure, **Then** the commit is blocked with an error message explaining what validation failed

---

### Edge Cases

- What happens when a frontend snapshot references an API endpoint that no longer exists in the backend?
- How does the system handle snapshots that contain dynamic data (timestamps, UUIDs) that change on every test run?
- What if frontend and backend repositories are separate and snapshots need to be shared across repos?
- How are snapshots versioned when frontend and backend versions diverge (e.g., frontend v2.0 with backend v1.5)?
- What happens when a developer manually edits a snapshot file?
- How does the system handle large request/response bodies in snapshots (e.g., file uploads, base64 encoded data)?
- What if OpenAPI specification is updated but snapshots aren't regenerated?

## Requirements *(mandatory)*

### Functional Requirements

**Snapshot Generation**

- **FR-001**: System MUST automatically capture HTTP request details (method, path, headers, body) when frontend API client code executes during tests
- **FR-002**: System MUST write captured requests to individual JSON files in a shared snapshot directory (`specs/contract-snapshots/`)
- **FR-003**: System MUST validate captured requests against the OpenAPI specification before writing snapshots
- **FR-004**: System MUST overwrite existing snapshot files with fresh captures on every test run (snapshots are generated outputs, not manual artifacts)
- **FR-005**: System MUST generate one snapshot file per API operation with descriptive filenames (e.g., `send-message.json`, `delete-message.json`)
- **FR-006**: System MUST include metadata in snapshots: operation name, capture timestamp, frontend version

**Snapshot Validation**

- **FR-007**: System MUST fail frontend tests immediately if a captured request doesn't match the OpenAPI specification schema
- **FR-008**: System MUST provide clear error messages showing which field failed validation and why
- **FR-009**: System MUST prevent snapshot generation if request validation fails

**Backend Contract Replay**

- **FR-010**: Backend contract tests MUST automatically discover and load all snapshot files from the shared directory
- **FR-011**: Backend tests MUST replay each captured request to the actual backend API endpoints
- **FR-012**: Backend tests MUST validate that the backend returns a successful response (2xx status code) for each replayed request
- **FR-013**: Backend tests MUST validate response structure against the OpenAPI specification
- **FR-014**: Backend tests MUST fail with actionable error messages if the backend cannot handle a frontend snapshot request

**CI/CD Integration**

- **FR-015**: CI pipeline MUST run frontend contract tests to generate fresh snapshots before backend tests
- **FR-016**: CI pipeline MUST fail the build if contract snapshots are missing or cannot be generated
- **FR-017**: CI pipeline MUST detect if snapshot files have changed but are not committed to git
- **FR-018**: CI pipeline MUST fail the build if uncommitted snapshot changes are detected, showing a diff
- **FR-019**: CI pipeline MUST run backend contract replay tests after frontend tests complete
- **FR-020**: CI pipeline MUST report which contract scenarios passed/failed

**Git Hook Integration**

- **FR-021**: Pre-commit hook MUST detect when API-related files are being committed (frontend API client, backend schemas, OpenAPI spec)
- **FR-022**: Pre-commit hook MUST regenerate contract snapshots when API-related files changed
- **FR-023**: Pre-commit hook MUST show a diff of snapshot changes and prompt developer for action
- **FR-024**: Pre-commit hook MUST allow developer to stage snapshot changes or abort commit
- **FR-025**: Pre-commit hook MUST skip snapshot regeneration for commits not touching API-related code

**Snapshot Format**

- **FR-026**: Snapshots MUST be stored as JSON files for easy version control diffing
- **FR-027**: Snapshots MUST normalize dynamic data (timestamps, UUIDs) to stable values for version control
- **FR-028**: Snapshots MUST be human-readable with proper indentation (2 spaces)

### Key Entities

- **Contract Snapshot**: A JSON file containing a captured HTTP request from frontend tests
  - Attributes: operation name, HTTP method, path, headers, request body, metadata (timestamp, version)
  - Relationships: Maps to specific OpenAPI operation, can be replayed by backend tests

- **API Request Format**: The actual structure of HTTP requests sent by frontend
  - Attributes: method, URL path, headers, JSON body structure
  - Relationships: Must conform to OpenAPI specification, captured in snapshots

- **OpenAPI Specification**: The single source of truth for API contract
  - Attributes: operations, request/response schemas, validation rules
  - Relationships: Used to validate both frontend snapshots and backend responses

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Contract mismatch bugs (like the recent `conversationId` format issue) are caught by automated tests before code review, with zero such bugs reaching production
- **SC-002**: Developers receive feedback on contract violations within 30 seconds of running tests locally
- **SC-003**: CI pipeline detects 100% of contract-breaking changes and prevents them from merging
- **SC-004**: Contract snapshot files are automatically regenerated on every test run without manual intervention
- **SC-005**: Backend contract replay tests cover 100% of frontend API operations within 2 sprints of feature completion
- **SC-006**: Time spent debugging integration issues between frontend and backend is reduced by 80% within 3 months
- **SC-007**: Contract test execution completes in under 2 minutes for the full test suite (frontend + backend)
- **SC-008**: Zero false positives in contract tests (tests only fail when there's a real contract mismatch)

## Assumptions

- Frontend and backend repositories share the same git repository (monorepo structure) allowing shared `specs/contract-snapshots/` directory
- Frontend tests use JavaScript/TypeScript with Vitest or Jest testing framework
- Backend tests use Python with pytest testing framework
- OpenAPI specification already exists and is kept up to date (from feature 003)
- CI pipeline uses GitHub Actions or similar with access to run both frontend and backend tests
- Developers have git hooks enabled (via husky or similar) though this is optional (CI will catch issues regardless)
- Contract snapshots are small enough to commit to git (< 1MB per file) - large payloads need special handling
- Team agrees to commit contract snapshots to version control as test artifacts

## Dependencies

- OpenAPI specification must be accurate and complete (dependency on feature 003)
- Frontend must have working test infrastructure (already exists)
- Backend must have working test infrastructure (already exists)
- Shared directory structure between frontend/backend (already exists in monorepo)

## Scope

### In Scope

- Automatic snapshot generation from frontend tests
- OpenAPI validation of frontend requests
- Backend replay of frontend snapshots
- CI pipeline integration
- Git pre-commit hooks
- Documentation and developer workflow guides

### Out of Scope

- Contract testing for websocket connections (HTTP only)
- Performance testing or load testing
- Contract versioning across multiple API versions (v1, v2, etc.)
- Cross-repository snapshot sharing (assumes monorepo)
- Automatic API mock generation from snapshots
- Contract testing for third-party API integrations (only internal frontend-backend)
