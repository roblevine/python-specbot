# Implementation Plan: Frontend Palette and Layout Redesign

**Branch**: `013-redesign-frontend-palette` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/013-redesign-frontend-palette/spec.md`

## Summary

Radically redesign the frontend visual appearance with a warm, earthy color palette (#FFDBBB, #CCBEB1, #997E67, #664930), centered chat layout with system responses as main content (no bubbles), constrained chat width (~768px), refined metadata typography, modest button styling, and improved collapsed sidebar margins. This is a CSS/styling-only change with no backend or API modifications.

## Technical Context

**Language/Version**: JavaScript (ES6+)
**Primary Dependencies**: Vue 3.4.0, Vite 5.0.0
**Storage**: N/A (styling changes only)
**Testing**: Vitest (unit), Playwright (E2E visual tests)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend only for this feature)
**Performance Goals**: N/A (no performance-critical changes)
**Constraints**: WCAG AA contrast compliance (4.5:1 minimum for normal text)
**Scale/Scope**: 7 Vue components affected, 1 global CSS file

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | N/A | No API changes - CSS/styling only |
| II. Modular Architecture | ✅ Pass | Changes isolated to component styles and global CSS |
| III. Test-First Development | ✅ Required | Visual tests to be written before styling changes |
| IV. Integration & Contract Testing | N/A | No API contracts affected |
| V. Observability & Debuggability | N/A | Styling changes don't require logging |
| VI. Simplicity & YAGNI | ✅ Pass | Direct CSS variable updates, no abstractions |
| VII. Versioning & Breaking Changes | ✅ Pass | Visual changes, no breaking API changes |
| VIII. Incremental Delivery & Thin Slices | ✅ Required | Implement by user story priority (P1→P2→P3) |
| IX. Living Architecture Documentation | N/A | No architectural changes |

**Gate Result**: PASS - No violations requiring justification.

**Note**: This feature is CSS/styling-only and does not require architecture.md updates as it doesn't introduce new modules, data flows, or technology choices.

## Project Structure

### Documentation (this feature)

```text
specs/013-redesign-frontend-palette/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: WCAG contrast, CSS variables research
├── data-model.md        # Phase 1: Color variable mappings (no entity changes)
├── quickstart.md        # Phase 1: Implementation quickstart guide
├── contracts/           # N/A - No API changes
└── tasks.md             # Phase 2: Implementation tasks (via /speckit.tasks)
```

### Source Code (repository root)

```text
frontend/
├── public/
│   └── styles/
│       └── global.css           # CSS variables to update (primary target)
├── src/
│   └── components/
│       ├── App/App.vue          # Main layout container
│       ├── ChatArea/
│       │   ├── ChatArea.vue     # Chat container width constraints
│       │   └── MessageBubble.vue # Message styling (remove bubbles for system)
│       ├── HistoryBar/
│       │   └── HistoryBar.vue   # Sidebar colors, collapsed margin fix
│       ├── InputArea/
│       │   └── InputArea.vue    # Input width constraints, button styling
│       ├── ModelSelector/
│       │   └── ModelSelector.vue # Metadata typography
│       └── StatusBar/
│           └── StatusBar.vue    # Metadata typography, button styling
└── tests/
    ├── unit/                    # Component unit tests
    └── e2e/                     # Playwright visual tests
```

**Structure Decision**: Web application structure - frontend-only changes. All modifications contained within `frontend/` directory.

## Complexity Tracking

> No violations to justify - all changes follow constitution principles.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Implementation Approach

### Thin Slices (by Priority)

| Slice | User Story | Deliverable | Test Focus |
|-------|------------|-------------|------------|
| 1 | US1 (P1) | Warm color palette in global.css | Color variable values, contrast ratios |
| 2 | US2 (P1) | Centered system messages, right-aligned user messages | Message alignment, bubble removal |
| 3 | US3 (P2) | Constrained chat width (~768px) | Max-width behavior, centering |
| 4 | US4 (P2) | Refined metadata typography | Font sizes, visual hierarchy |
| 5 | US5 (P2) | Modest button styling | Button appearance, hover states |
| 6 | US6 (P3) | Collapsed sidebar margin | Margin measurement (8px min) |

### Key Files to Modify

1. **global.css** - CSS variables for entire palette
2. **MessageBubble.vue** - Remove bubble for system, restyle user messages
3. **ChatArea.vue** - Add max-width constraint and centering
4. **InputArea.vue** - Width constraint, button styling
5. **HistoryBar.vue** - Sidebar colors, collapsed button margin
6. **StatusBar.vue** - Metadata typography
7. **ModelSelector.vue** - Metadata typography

## Next Steps

1. **Phase 0**: Generate `research.md` with WCAG contrast calculations and CSS best practices
2. **Phase 1**: Generate `data-model.md` (color variable mappings) and `quickstart.md`
3. **Run `/speckit.tasks`**: Generate implementation tasks from this plan
