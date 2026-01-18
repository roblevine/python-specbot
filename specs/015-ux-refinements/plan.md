# Implementation Plan: UX Refinements

**Branch**: `015-ux-refinements` | **Date**: 2026-01-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/015-ux-refinements/spec.md`

## Summary

This feature implements five UX improvements to the chat interface:
1. **P1**: Fix non-deterministic conversation ordering (sort by updatedAt, most recent first)
2. **P2**: Add clear visual distinction for enabled/disabled button states
3. **P3**: Display datetime metadata on messages in "Sun 18-Jan-26 09:58am" format
4. **P4**: Relocate model selector into the input area component
5. **P5**: Remove the status indicator from the interface

All changes are frontend-only; no backend or API modifications required.

## Technical Context

**Language/Version**: JavaScript ES6+ (Frontend), Python 3.13 (Backend - no changes)
**Primary Dependencies**: Vue 3.4.0, Vite 5.0.0
**Storage**: File-based JSON (backend), Browser localStorage (frontend) - no schema changes needed
**Testing**: Vitest (frontend unit tests)
**Target Platform**: Web browser (desktop/mobile)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: UI updates should be instantaneous (<100ms perceived)
**Constraints**: None specific to this feature
**Scale/Scope**: Single-user chat application

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | N/A | No API changes - frontend-only feature |
| II. Modular Architecture | ✅ PASS | Changes are contained within existing component boundaries |
| III. Test-First Development | ✅ REQUIRED | Unit tests for datetime formatting, sorting logic |
| IV. Contract Testing | N/A | No API changes - no contract tests needed |
| V. Observability | ✅ PASS | Existing logging patterns sufficient |
| VI. Simplicity & YAGNI | ✅ PASS | Minimal changes, no new abstractions |
| VII. Versioning | N/A | No breaking changes to interfaces |
| VIII. Incremental Delivery | ✅ REQUIRED | Each user story is a thin vertical slice |
| IX. Living Architecture | N/A | No architectural changes |

**Architecture Update Required**: No - these are UI refinements within existing components.

## Project Structure

### Documentation (this feature)

```text
specs/015-ux-refinements/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output (implementation notes)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   ├── App/
│   │   │   └── App.vue              # Remove ModelSelector, update StatusBar usage
│   │   ├── ChatArea/
│   │   │   └── MessageBubble.vue    # Update datetime format, model indicator layout
│   │   ├── HistoryBar/
│   │   │   └── HistoryBar.vue       # Sorted conversations (via computed property)
│   │   ├── InputArea/
│   │   │   └── InputArea.vue        # Add ModelSelector, update button styling
│   │   ├── ModelSelector/
│   │   │   └── ModelSelector.vue    # Minor styling adjustments for new location
│   │   └── StatusBar/
│   │       └── StatusBar.vue        # Remove status indicator elements
│   ├── state/
│   │   └── useConversations.js      # Add sorting when loading conversations
│   └── utils/
│       └── dateFormatter.js         # NEW: Datetime formatting utility
└── tests/
    └── unit/
        └── utils/
            └── dateFormatter.test.js # NEW: Tests for datetime formatting
```

**Structure Decision**: Web application structure with separate frontend/backend. All changes in this feature are frontend-only.

## Complexity Tracking

No constitution violations requiring justification.

## Implementation Approach

### Phase Summary

| Story | Priority | Scope | Key Files |
|-------|----------|-------|-----------|
| Deterministic Ordering | P1 | Frontend | useConversations.js, HistoryBar.vue |
| Button State Visibility | P2 | Frontend | InputArea.vue, HistoryBar.vue, global.css |
| Datetime Display | P3 | Frontend | MessageBubble.vue, dateFormatter.js (new) |
| Model Selector Relocation | P4 | Frontend | App.vue, InputArea.vue |
| Remove Status Indicator | P5 | Frontend | StatusBar.vue |

### Key Technical Decisions

1. **Datetime Formatting**: Create a reusable `dateFormatter.js` utility that returns the format "Sun 18-Jan-26 09:58am" using JavaScript's `Intl.DateTimeFormat` and string manipulation.

2. **Conversation Sorting**: Sort in `useConversations.js` after fetching from API to ensure deterministic order. Use `updatedAt` as primary sort key, `id` as secondary for tie-breaking.

3. **Button Styling**: Define CSS classes for enabled/disabled states using the existing warm color palette. Enabled buttons will have a solid background color; disabled buttons will be muted/grayed.

4. **Model Selector Relocation**: Move `<ModelSelector />` from App.vue into InputArea.vue, positioned above the textarea/button container.

5. **Status Indicator Removal**: Remove the status indicator dot and text from StatusBar.vue, keeping only the conversation title and rename functionality.
