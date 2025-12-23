<!--
Sync Impact Report:
Version: 1.0.0 → 1.1.0 (added Principle VIII)
Modified Principles: N/A
Added Sections:
  - Principle VIII: Incremental Delivery & Thin Slices
Removed Sections: N/A
Templates Status:
  ✅ plan-template.md - Reviewed, "Constitution Check" section aligns with principles I-VIII
  ✅ spec-template.md - Reviewed, requirements structure aligns with API-First principle
  ✅ tasks-template.md - Reviewed, test-first workflow aligns with principle III
  ⚠️  tasks-template.md - Will need update to emphasize thin slice approach per Principle VIII
Follow-up TODOs: Update tasks template to emphasize P1/MVP-first approach
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

### IV. Integration & Contract Testing

Integration tests are REQUIRED for:
- New API endpoints (contract tests)
- Changes to existing contracts
- Inter-module communication
- External service integrations
- Shared data models

**Rationale**: Unit tests alone don't catch integration issues. Contract tests verify that modules actually work together as specified and prevent breaking changes from reaching production.

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

### Security
- No credentials or secrets in source code or version control
- Input validation at all system boundaries
- Dependency vulnerabilities addressed within 30 days of disclosure
- Authentication and authorization for all non-public endpoints

## Quality Gates

All pull requests MUST pass:
1. **Constitution Compliance**: Code review verifies adherence to principles I-VIII
2. **Test Gate**: All tests pass (unit, integration, contract)
3. **Test-First Verification**: Tests existed and failed before implementation
4. **Code Quality**: Linting, formatting, type checking pass
5. **Documentation**: Contracts, APIs, and complex logic documented
6. **Thin Slice Verification**: PR implements complete vertical slice (one user story)

New features MUST include:
- Contract definition (if adding/modifying API)
- Contract and integration tests
- Update to relevant documentation
- Evidence that tests were written first and initially failed
- Demonstration that slice is independently testable and deployable

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

**Version**: 1.1.0 | **Ratified**: 2025-12-23 | **Last Amended**: 2025-12-23
