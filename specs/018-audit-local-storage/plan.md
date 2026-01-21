# Implementation Plan: Audit and Simplify Local Storage

**Branch**: `018-audit-local-storage` | **Date**: 2026-01-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/018-audit-local-storage/spec.md`

## Summary

Clean up localStorage code by removing all conversation-related storage (now server-side) and creating a simplified, unified settings storage mechanism for user preferences (sidebar state, model selection). The new architecture uses a clean v2.0.0 schema with a single storage key and adapter.

## Technical Context

**Language/Version**: JavaScript ES6+
**Primary Dependencies**: Vue 3.4.0, Vite 5.0.0
**Storage**: Browser localStorage (settings only)
**Testing**: Vitest
**Target Platform**: Web browser (all modern browsers)
**Project Type**: Web application (frontend change only)
**Performance Goals**: Instant save/load (<10ms)
**Constraints**: Must work in private browsing (graceful degradation)
**Scale/Scope**: 2 settings initially (sidebar, model), extensible

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | N/A | No API changes - frontend-only feature |
| II. Modular Architecture | ✅ PASS | Single consolidated storage module |
| III. Test-First Development | ✅ REQUIRED | Tests for new SettingsStorage before implementation |
| IV. Contract Testing | N/A | No API changes |
| V. Observability | ✅ PASS | Debug logging for save/load operations |
| VI. Simplicity & YAGNI | ✅ PASS | Removing complexity (conversation fallback), simple schema |
| VII. Versioning | ✅ PASS | Schema v2.0.0 with version field for future migrations |
| VIII. Thin Slices | ✅ PASS | Slice 1: Settings, Slice 2: Cleanup |
| IX. Living Architecture | ℹ️ INFO | No architectural changes needed - this is cleanup |

**Gate Status**: ✅ PASS - No violations, no complexity tracking needed

## Project Structure

### Documentation (this feature)

```text
specs/018-audit-local-storage/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: Technical decisions
├── data-model.md        # Phase 1: Settings schema
├── quickstart.md        # Phase 1: Implementation guide
└── checklists/
    └── requirements.md  # Spec validation checklist
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── storage/
│   │   ├── SettingsSchema.js    # NEW: v2.0.0 schema definition
│   │   ├── SettingsStorage.js   # NEW: Unified settings adapter
│   │   ├── LocalStorageAdapter.js  # DELETE
│   │   └── StorageSchema.js        # DELETE
│   ├── composables/
│   │   └── useSidebarCollapse.js   # MODIFY: Use SettingsStorage
│   └── state/
│       ├── useModels.js            # MODIFY: Use SettingsStorage
│       └── useConversations.js     # MODIFY: Remove localStorage code
└── tests/
    └── unit/
        ├── SettingsStorage.test.js     # NEW
        ├── SettingsSchema.test.js      # NEW
        ├── useSidebarCollapse.test.js  # UPDATE
        ├── useModels.test.js           # UPDATE
        ├── LocalStorageAdapter.test.js # DELETE
        └── StorageSchema.test.js       # DELETE
```

**Structure Decision**: Frontend-only changes. No backend modifications required. Storage module is being simplified, not expanded.

## Complexity Tracking

> No violations to justify - this feature reduces complexity.

| Area | Before | After |
|------|--------|-------|
| Storage files | 2 | 2 |
| Schema fields | 5 | 3 |
| Lines of code | ~260 | ~100 (est.) |
| localStorage keys | 2 | 1 |
| Migration paths | v1.0.0→v1.1.0 | None (clean start) |

## Implementation Slices

### Slice 1: Settings Persistence (P1)

**User Stories**: 1 (Settings Persist), 2 (Update on Change)

**Tasks**:
1. Create `SettingsSchema.js` with v2.0.0 schema definition
2. Create `SettingsStorage.js` with save/load API
3. Write unit tests for new storage module (TDD)
4. Update `useSidebarCollapse.js` to use new adapter
5. Update `useModels.js` to use new adapter
6. Verify end-to-end: settings persist across browser refresh

**Deliverable**: Working settings persistence with new architecture

### Slice 2: Remove Legacy Code (P2)

**User Stories**: 3 (Remove Legacy), 4 (Unified Architecture)

**Tasks**:
1. Remove all localStorage code from `useConversations.js`:
   - Delete migration function
   - Delete fallback logic
   - Remove localStorage imports
2. Delete `LocalStorageAdapter.js`
3. Delete `StorageSchema.js`
4. Delete associated test files
5. Update any remaining tests
6. Verify app works with server-only conversations

**Deliverable**: Clean codebase with no conversation localStorage code

## Key Decisions (from research.md)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Schema version | v2.0.0 (major) | Breaking change - removing conversations |
| Storage key | `specbot:settings:v2` | Clean break from old data |
| Migration | None | Complexity not worth it for simple settings |
| API surface | saveSetting/getSetting | Minimal, easy to use |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Old settings lost | Medium | Low | Users re-select model once; acceptable |
| Import errors after delete | Low | Medium | grep for old imports before merge |
| Private browsing issues | Low | Low | Graceful degradation already planned |

## Testing Strategy

1. **Unit Tests** (TDD - write first):
   - SettingsStorage: save, load, defaults, corruption handling
   - SettingsSchema: validation, defaults

2. **Integration Tests**:
   - Settings persist across page refresh
   - Invalid model ID falls back to default

3. **Manual Verification**:
   - Collapse sidebar → refresh → still collapsed
   - Select model → refresh → still selected
   - Private browsing → app works with defaults

## Definition of Done

- [ ] New SettingsStorage module created and tested
- [ ] useSidebarCollapse uses new adapter
- [ ] useModels uses new adapter
- [ ] useConversations has no localStorage code
- [ ] Old storage files deleted
- [ ] All tests pass
- [ ] Settings persist across browser sessions
- [ ] App works normally with server-only conversations
