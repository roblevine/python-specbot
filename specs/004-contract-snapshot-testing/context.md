# Resume Context: Feature 004 Contract Snapshot Testing

**Branch**: `004-contract-snapshot-testing`
**Current Command**: `/speckit.plan` (in progress)
**Status**: Phase 1 - Design Artifacts (in progress)

## Completed Work

### Phase 0: Research ✅
- **Decision**: Use `core-ajv-schema-validator` for JavaScript OpenAPI validation
- **Rationale**: JavaScript equivalent to Python's openapi-core, uses AJV, framework-agnostic
- **File**: `research.md` created with full analysis
- **Updated**: `plan.md` Technical Context section (removed NEEDS CLARIFICATION)

### Constitution Check ✅
- All 9 principles: PASS
- Action required: Update architecture.md after implementation

### Technical Stack ✅
**Frontend**:
- JavaScript ES6+, Vue 3.4.0, Vitest 1.0.0
- New dep: `core-ajv-schema-validator`

**Backend**:
- Python 3.13, pytest 8.3.0
- Existing: `openapi-core==0.18.2` (already installed)

**Storage**: `specs/contract-snapshots/` (JSON files in git)

## Next Steps (Phase 1)

1. **Create data-model.md** ⏭️ NEXT
   - Entities: Contract Snapshot, API Request Format, OpenAPI Specification
   - Use pattern from `specs/003-backend-api-loopback/data-model.md`

2. **Create quickstart.md**
   - Developer workflow: capture snapshots, validate, replay
   - CI integration steps
   - Git hook setup (optional)

3. **Skip contracts/** (no new API endpoints - testing existing ones)

4. **Update plan.md Project Structure section**
   - Remove unused options
   - Document actual monorepo structure

5. **Update agent context**
   - Run: `.specify/scripts/bash/update-agent-context.sh claude`

## After /speckit.plan Complete

1. Run `/speckit.tasks` to generate tasks.md
2. Implement P1 MVP:
   - Slice 1: Frontend snapshot capture + OpenAPI validation
   - Slice 2: Backend snapshot replay
3. Update architecture.md per Principle IX

## Key Files

- `spec.md` ✅ (committed: ab72570)
- `checklists/requirements.md` ✅
- `plan.md` 🔄 (partial: Summary, Technical Context, Constitution Check done)
- `research.md` ✅
- `data-model.md` ❌ (next to create)
- `quickstart.md` ❌
- `tasks.md` ❌ (generated after plan complete)

## Problem Context

Original bug: Frontend sent `conv-{uuid}`, backend expected `{uuid}` - tests passed but app broken. Contract testing will prevent this by:
1. Capturing actual frontend requests during tests
2. Validating against OpenAPI spec
3. Replaying to backend to verify compatibility

## Resume Command

Continue with: Create data-model.md following the structure in `specs/003-backend-api-loopback/data-model.md`
