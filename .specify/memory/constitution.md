<!--
Sync Impact Report:
Version: 1.2.0 → 1.3.0 (strengthened Principle IV - Contract Testing)
Modified Principles:
  - Principle IV: Integration & Contract Testing
    - Marked as NON-NEGOTIABLE
    - Added explicit Contract Test Requirements section
    - Added Contract Test Workflow
    - Added Prohibited Practices
    - Added reference to timestamp bug as rationale
Modified Sections:
  - Quality Gates:
    - Added explicit "Contract Test Gate" as gate #3
    - Added "API changes ADDITIONALLY require" section
    - Strengthened contract testing requirements
Removed Sections: N/A
Templates Status:
  ⏳ To be updated in follow-up:
    - plan-template.md - Add contract testing reminder to Constitution Check
    - tasks-template.md - Ensure contract test tasks included for API features
Rationale for Change:
  Timestamp bug (2025-12-29) proved that incomplete contract testing (only validating
  requests, not responses) allows format mismatches to reach production. This amendment
  makes contract testing requirements explicit and non-negotiable.
Follow-up TODOs:
  - Update CLAUDE.md to emphasize contract testing requirement
  - Ensure all API endpoints have contract tests with response validation
  - Add contract testing to CI pipeline (User Story 3 - P2)
-->

# SpecBot Constitution

## Core Principles

### I. API-First Design

Every feature starts with a defined contract. API contracts MUST be specified before implementation begins. Contracts define:
- Request/response schemas
- Error handling and status codes
- Input validation rules
- Success and failure scenarios

**Rationale**: Contract-first development ensures clear interfaces, enables parallel work (frontend/backend), prevents integration surprises, and serves as living documentation. Contracts enable contract testing and make breaking changes explicit.

### II. Modular Architecture

Features MUST be implemented as self-contained modules with clear boundaries. Each module:
- Has a single, well-defined purpose
- Is independently testable
- Minimizes coupling with other modules
- Exposes functionality through documented interfaces

**Rationale**: Modularity enables independent development and testing, simplifies maintenance, supports code reuse, and makes the system easier to understand and evolve.

### III. Test-First Development (NON-NEGOTIABLE)

Test-Driven Development is mandatory for all feature work. The workflow is:
1. Write tests that capture acceptance criteria
2. Get user approval on test scenarios
3. Verify tests FAIL (red)
4. Implement minimum code to pass tests (green)
5. Refactor while keeping tests green

**Rationale**: TDD enforces design thinking before coding, ensures testability from the start, creates a safety net for refactoring, and produces executable specifications. This is non-negotiable because it fundamentally changes quality outcomes.

### IV. Integration & Contract Testing (NON-NEGOTIABLE)

**Contract tests are MANDATORY and MUST be maintained**. Integration tests are REQUIRED for:
- New API endpoints (contract tests)
- Changes to existing contracts
- Inter-module communication
- External service integrations
- Shared data models

**Contract Test Requirements**:
- **Consumer-driven contract tests** MUST exist for ALL API endpoints
- Contract tests MUST validate BOTH request format (client → server) AND response format (server → client)
- ALL contract tests MUST pass before merging any API-related changes
- Breaking a contract test is a **BLOCKING ISSUE** that MUST be fixed before merge
- Contract snapshots MUST be committed to version control as test artifacts
- When API contracts change, contract tests MUST be updated in the same commit

**Contract Test Workflow**:
1. **Capture**: Frontend tests capture actual HTTP requests as snapshots
2. **Validate**: Snapshots validated against OpenAPI specification
3. **Replay**: Backend tests replay snapshots to verify compatibility
4. **Enforce**: CI pipeline fails if snapshots are stale or tests fail

**Prohibited Practices**:
- Skipping contract tests for "quick fixes"
- Modifying API endpoints without running contract tests
- Committing code that breaks contract tests with intent to "fix later"
- Deleting or disabling contract tests to make tests pass

**Rationale**: Unit tests alone don't catch integration issues. Contract tests verify that modules actually work together as specified and prevent breaking changes from reaching production. The timestamp bug (2025-12-29) proved that response validation is critical - without it, format mismatches reach production and break user-facing features.

### V. Observability & Debuggability

All features MUST include observability mechanisms:
- Structured logging at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Request/response logging for API interactions
- Error contexts include actionable information
- Performance metrics for critical paths

**Rationale**: Production issues are inevitable. Observable systems enable rapid diagnosis and resolution. Text-based logs and clear error messages make debugging accessible without specialized tools.

### VI. Simplicity & YAGNI

Start with the simplest solution that solves the current problem. Complexity MUST be justified.
- No speculative features or abstractions
- No "we might need this later" code
- Choose boring, proven technologies over novel ones
- Optimize for readability over cleverness

**Rationale**: Over-engineering wastes time, increases maintenance burden, and makes systems harder to understand. Simple systems are easier to test, debug, and evolve. Complexity can be added when actually needed.

### VII. Versioning & Breaking Changes

All public interfaces follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes to APIs, contracts, or data models
- **MINOR**: New features, backward-compatible additions
- **PATCH**: Bug fixes, performance improvements, refactoring

Breaking changes REQUIRE:
- Explicit documentation of what breaks and why
- Migration guide for consumers
- Deprecation period when feasible

**Rationale**: Predictable versioning allows consumers to understand impact of updates. Breaking changes are sometimes necessary but must be explicit and planned.

### VIII. Incremental Delivery & Thin Slices (NON-NEGOTIABLE)

Features MUST be implemented as thin vertical slices that deliver end-to-end value. Each slice:
- Implements ONE complete user story or workflow (P1/MVP first)
- Is independently testable, demonstrable, and deployable
- Delivers working functionality from UI to storage/backend
- Can be committed and deployed without depending on future slices

**Implementation Workflow**:
1. **Plan**: Identify the thinnest valuable slice (usually P1/MVP user story)
2. **Implement**: Build complete vertical slice (tests → UI → logic → storage)
3. **Test**: Verify slice works end-to-end
4. **Demo**: Show working functionality to stakeholders
5. **Commit**: Commit completed slice to version control
6. **Repeat**: Move to next slice (P2, P3, etc.)

**What Qualifies as a Thin Slice**:
- ✅ "User can send message and see loopback response" (P1 story)
- ✅ "User can view conversation history" (P2 story - adds to P1)
- ❌ "Implement all UI components" (horizontal layer, not deliverable)
- ❌ "Build entire feature with all stories" (too thick, can't demo incrementally)

**Prohibited Practices**:
- Implementing multiple user stories before testing/committing
- Building horizontal layers (all UI, then all logic, then all storage)
- "I'll commit when the whole feature is done" approach
- Deferring integration testing until end

**Rationale**: Thin slices enable rapid feedback, reduce integration risk, provide early value, and make progress visible. Working software after each slice proves the system works and builds confidence. This approach prevents "90% done" syndrome where integration happens late and reveals major issues.

### IX. Living Architecture Documentation

The project MUST maintain an up-to-date `architecture.md` document that describes both current and planned architecture. This document:
- Describes the **current implemented architecture** with clear component diagrams and relationships
- Documents **planned future architecture** with explicit markers indicating what is NOT yet implemented
- Is updated on **every architectural change** or feature addition that affects system structure
- Clearly distinguishes between "what exists now" vs "what we plan to build"
- Includes rationale for major architectural decisions and technology choices
- Documents integration points, data flows, and module boundaries

**Required Sections**:
- **Current Architecture**: What is actually implemented today
- **Planned Architecture**: Future changes with clear "NOT IMPLEMENTED" labels
- **Technology Stack**: Current and planned technologies with adoption status
- **Data Flow**: How data moves through the system
- **Module Boundaries**: Clear interface contracts between components
- **Architectural Decisions**: Why key choices were made (ADRs)

**Update Triggers**:
- New feature added (update Current Architecture section)
- Architectural refactoring (update both Current and Planned sections)
- Technology changes (update Technology Stack)
- Module boundaries change (update Module Boundaries)
- New architectural decisions made (add to ADRs)

**Rationale**: Architecture documentation prevents knowledge silos and ensures all contributors understand system structure. Clearly marking planned vs implemented architecture prevents confusion and sets realistic expectations. Living documentation (updated with every change) stays accurate, unlike static docs that become stale. This practice enables faster onboarding, better architectural decisions, and reduces "surprise" integrations.

## Development Standards

### Code Quality
- All code MUST pass linting and formatting checks
- Type hints required for Python functions (public interfaces)
- Functions have clear, descriptive names
- Magic numbers extracted to named constants

### Documentation
- README.md explains project purpose and quickstart
- API contracts documented in OpenAPI/JSON Schema format
- Complex algorithms include inline comments explaining "why"
- Public modules include docstrings
- **architecture.md** maintained and updated with every architectural change

### Security
- No credentials or secrets in source code or version control
- Input validation at all system boundaries
- Dependency vulnerabilities addressed within 30 days of disclosure
- Authentication and authorization for all non-public endpoints

## Quality Gates

All pull requests MUST pass:
1. **Constitution Compliance**: Code review verifies adherence to principles I-IX
2. **Test Gate**: All tests pass (unit, integration, contract)
3. **Contract Test Gate**: ALL contract tests MUST pass for API changes (NON-NEGOTIABLE)
4. **Test-First Verification**: Tests existed and failed before implementation
5. **Code Quality**: Linting, formatting, type checking pass
6. **Documentation**: Contracts, APIs, and complex logic documented
7. **Thin Slice Verification**: PR implements complete vertical slice (one user story)
8. **Architecture Documentation**: architecture.md updated if architectural changes made

New features MUST include:
- Contract definition (if adding/modifying API)
- Consumer-driven contract tests (request AND response validation)
- Contract snapshots committed to version control
- Integration tests for inter-module communication
- Update to relevant documentation
- Evidence that tests were written first and initially failed
- Demonstration that slice is independently testable and deployable
- Update to architecture.md if feature changes system architecture

API changes ADDITIONALLY require:
- Running contract tests and verifying they pass
- Updating contract snapshots if request/response format changed
- Committing updated snapshots in same PR as API changes
- Evidence that contract tests failed before fix (for bug fixes)

## Governance

This constitution is a **living document** that evolves with the project.

### Amendment Process
1. Propose change with rationale (GitHub issue or PR)
2. Discuss impact on existing code and practices
3. Update constitution with version bump
4. Update affected templates and documentation
5. Communicate changes to all contributors

### Version Bumping
- **MAJOR**: Removing or fundamentally changing a core principle
- **MINOR**: Adding new principle or expanding scope significantly
- **PATCH**: Clarifications, wording improvements, typo fixes

### Compliance
- All PRs/reviews verify compliance with current principles
- Exceptions allowed but MUST be documented with justification
- Constitution takes precedence over individual preferences
- When principles conflict, discuss and clarify (don't ignore)

### Review Schedule
- Constitution reviewed quarterly for relevance
- Templates (plan, spec, tasks) updated when constitution changes
- Team retrospectives can propose amendments

**Version**: 1.3.0 | **Ratified**: 2025-12-23 | **Last Amended**: 2025-12-29
