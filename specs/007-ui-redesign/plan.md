# Implementation Plan: UI Redesign

**Branch**: `007-ui-redesign` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-ui-redesign/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature implements a visual refresh of the chat interface with a professional grey/pastel blue color scheme, a collapsible conversations sidebar with persistent state, and improved button styling for the "New Conversation" control. The implementation is primarily CSS-based with minimal JavaScript for sidebar collapse functionality, leveraging existing Vue 3 composables patterns and LocalStorage for preference persistence.

## Technical Context

**Language/Version**: JavaScript ES6+ (Frontend only, no backend changes)
**Primary Dependencies**: Vue 3.4.0, CSS3 (CSS Variables, Flexbox, Transitions)
**Storage**: Browser LocalStorage (via existing StorageAdapter) for sidebar collapse preference
**Testing**: Vitest (unit tests), Playwright (E2E tests) - existing test infrastructure
**Target Platform**: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Web application (frontend-only changes)
**Performance Goals**: CSS transitions <16ms for 60fps, sidebar toggle <100ms perceived delay
**Constraints**: WCAG 2.1 AA contrast ratios (4.5:1 normal text, 3:1 large text), no breaking changes to existing functionality
**Scale/Scope**: Single-page application, ~5 components affected, ~200 lines CSS changes, minimal JS additions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: API-First Design
✅ **PASS** - No API changes required. This is a frontend-only visual redesign.

### Principle II: Modular Architecture
✅ **PASS** - Changes isolated to CSS files and one new composable for sidebar state. Existing component boundaries preserved.

### Principle III: Test-First Development (NON-NEGOTIABLE)
✅ **PASS** - Will write tests for:
  - Sidebar collapse/expand functionality
  - Preference persistence
  - Visual regression (contrast ratios)
  - Component rendering with new styles

### Principle IV: Integration & Contract Testing (NON-NEGOTIABLE)
✅ **PASS** - No API contracts affected. Existing contract tests remain valid. No contract changes required.

### Principle V: Observability & Debuggability
✅ **PASS** - Will add logging for sidebar state changes and preference persistence failures.

### Principle VI: Simplicity & YAGNI
✅ **PASS** - Minimal complexity: CSS variables for theming, simple boolean state for collapse. No speculative features.

### Principle VII: Versioning & Breaking Changes
✅ **PASS** - No breaking changes. All existing functionality preserved. CSS-only changes are backward compatible.

### Principle VIII: Incremental Delivery & Thin Slices (NON-NEGOTIABLE)
✅ **PASS** - Implementation plan follows priority order:
  - **Slice 1 (P1)**: Color scheme CSS changes → immediate visual value
  - **Slice 2 (P2)**: Collapsible sidebar → interactive functionality
  - **Slice 3 (P3)**: Button styling refinements → polish

Each slice is independently testable and deployable.

### Principle IX: Living Architecture Documentation
✅ **PASS** - No architectural changes. This is a styling/UI layer change. No architecture.md update needed.

**GATE STATUS**: ✅ **ALL GATES PASS** - Proceed to Phase 0

**Note**: No architectural changes introduced. This feature only affects presentation layer (CSS + minimal state management).

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
frontend/
├── public/
│   └── styles/
│       └── global.css              # CSS variables and global theming (MODIFY)
├── src/
│   ├── components/
│   │   ├── App/
│   │   │   └── App.vue             # Main layout container (MODIFY - add collapse state)
│   │   ├── HistoryBar/
│   │   │   └── HistoryBar.vue      # Conversations sidebar (MODIFY - add collapse UI)
│   │   ├── ChatArea/
│   │   │   └── ChatArea.vue        # Message display (MODIFY - style updates)
│   │   ├── InputArea/
│   │   │   └── InputArea.vue       # Message input (MODIFY - style updates)
│   │   └── StatusBar/
│   │       └── StatusBar.vue       # Top status bar (MODIFY - style updates)
│   ├── composables/
│   │   └── useSidebarCollapse.js   # Sidebar collapse state (NEW)
│   ├── storage/
│   │   ├── LocalStorageAdapter.js  # Storage interface (MODIFY - add sidebar pref)
│   │   └── StorageSchema.js        # Schema definition (MODIFY - add sidebar field)
│   └── state/
│       └── useAppState.js          # Global app state (MODIFY - integrate collapse state)
└── tests/
    ├── unit/
    │   ├── useSidebarCollapse.test.js  # Composable tests (NEW)
    │   └── StorageSchema.test.js       # Schema validation (MODIFY)
    ├── integration/
    │   └── sidebar-collapse.test.js    # Sidebar interaction (NEW)
    └── e2e/
        └── ui-redesign.spec.js         # E2E visual tests (NEW)

backend/
└── [NO CHANGES REQUIRED]
```

**Structure Decision**: This is a web application with frontend-only changes. We use the existing Vue 3 component structure and add a new composable for sidebar state management. No backend modifications needed as this is purely presentational.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations identified.** All gates pass without exceptions.

---

## Post-Design Constitution Check

*Re-evaluation after Phase 0 (Research) and Phase 1 (Design & Contracts)*

### Principle I: API-First Design
✅ **PASS** - Confirmed: No API changes. All contracts remain valid (see `contracts/README.md`).

### Principle II: Modular Architecture
✅ **PASS** - Confirmed: New `useSidebarCollapse` composable follows existing patterns. Clear separation of concerns maintained.

### Principle III: Test-First Development (NON-NEGOTIABLE)
✅ **PASS** - Test strategy defined in `quickstart.md`:
  - Unit tests for `useSidebarCollapse` composable
  - Unit tests for color palette validation
  - Integration tests for sidebar collapse workflow
  - E2E tests for visual verification
  - TDD workflow explicitly documented for each slice

### Principle IV: Integration & Contract Testing (NON-NEGOTIABLE)
✅ **PASS** - Confirmed: No API contracts affected. Existing contract tests remain valid. LocalStorage schema change is client-side only and fully backward compatible (v1.0.0 → v1.1.0 migration).

### Principle V: Observability & Debuggability
✅ **PASS** - Logging added for:
  - Sidebar state transitions
  - LocalStorage load/save operations
  - Error cases (storage quota, invalid values)

### Principle VI: Simplicity & YAGNI
✅ **PASS** - Confirmed:
  - Single boolean state for sidebar collapse
  - CSS variables for theming (simplest approach)
  - No speculative features (no dark mode, no theme customization)
  - Minimal JavaScript additions (~50 lines in composable)

### Principle VII: Versioning & Breaking Changes
✅ **PASS** - Confirmed:
  - LocalStorage schema v1.1.0 is backward compatible
  - Migration logic handles v1.0.0 → v1.1.0 automatically
  - No breaking changes to any APIs or components
  - Existing functionality preserved 100%

### Principle VIII: Incremental Delivery & Thin Slices (NON-NEGOTIABLE)
✅ **PASS** - Confirmed: Implementation broken into 3 thin vertical slices:
  - **Slice 1 (P1)**: Color scheme → Visual value, independently testable
  - **Slice 2 (P2)**: Sidebar collapse → Interactive functionality, independently testable
  - **Slice 3 (P3)**: Button styling → Polish, independently testable

Each slice can be committed and deployed separately. Each delivers end-to-end value.

### Principle IX: Living Architecture Documentation
✅ **PASS** - Confirmed: No architectural changes. This is purely presentation layer. No architecture.md update required.

**POST-DESIGN GATE STATUS**: ✅ **ALL GATES PASS**

**Design Validation**: All technical decisions made in Phase 0 (research.md) and Phase 1 (data-model.md) align with constitution principles. Ready for implementation via `/speckit.tasks`.
