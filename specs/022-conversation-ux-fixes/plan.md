# Implementation Plan: Conversation UX Fixes

**Branch**: `022-conversation-ux-fixes` | **Date**: 2026-01-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/022-conversation-ux-fixes/spec.md`

## Summary

This feature implements four frontend UX improvements for the conversation interface:

1. **Conversation Ordering Fix (P1)**: Ensure new/updated conversations appear at top of sidebar list
2. **Chat Input Focus Retention (P1)**: Maintain keyboard focus in message input after response completes
3. **Timestamps in Conversation List (P2)**: Display last activity date/time below each conversation title
4. **Compact Styling (P2)**: Reduce font size and vertical spacing to show more conversations

All changes are **frontend-only** with no API modifications. The existing data model already includes the required `updatedAt` timestamp field.

## Technical Context

**Language/Version**: JavaScript ES6+ (Frontend only)
**Primary Dependencies**: Vue 3.4.0, Vite 5.0.0
**Storage**: N/A (no storage changes - uses existing `updatedAt` field from server)
**Testing**: Vitest (unit tests), manual visual testing for styling
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend changes only)
**Performance Goals**: Instant UI response (<16ms for 60fps), no perceptible lag on list reorder
**Constraints**: Must work with existing conversation data model, no breaking changes
**Scale/Scope**: Single-user chat application, typical ~50-100 conversations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance | Notes |
|-----------|------------|-------|
| I. API-First Design | N/A | No API changes in this feature |
| II. Modular Architecture | PASS | Changes isolated to existing components |
| III. Test-First Development | PASS | Unit tests for sorting, focus tracking |
| IV. Integration & Contract Testing | N/A | No API changes, no contract tests needed |
| V. Observability & Debuggability | PASS | Console logging for focus state changes |
| VI. Simplicity & YAGNI | PASS | Minimal changes to existing code |
| VII. Versioning & Breaking Changes | PASS | No breaking changes, backward compatible |
| VIII. Incremental Delivery | PASS | Four independent thin slices (one per user story) |
| IX. Living Architecture Documentation | N/A | No architectural changes |

**Architecture Update**: Not required - no new modules, data flows, or technology choices.

## Project Structure

### Documentation (this feature)

```text
specs/022-conversation-ux-fixes/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (minimal - uses existing model)
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   ├── HistoryBar/
│   │   │   └── HistoryBar.vue      # Conversation list - ordering, timestamps, styling
│   │   └── InputArea/
│   │       └── InputArea.vue       # Chat input - focus retention
│   ├── state/
│   │   └── useConversations.js     # Sorting logic verification
│   └── utils/
│       └── dateFormatter.js        # NEW: Timestamp formatting utility
└── tests/
    └── unit/
        ├── dateFormatter.test.js   # NEW: Timestamp formatting tests
        └── useConversations.test.js # Existing: Add sorting verification tests
```

**Structure Decision**: Web application - frontend only. All changes confined to existing Vue components and state management. One new utility module for date formatting.

## Complexity Tracking

> No violations - this feature follows all constitution principles with minimal complexity.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Date formatting | New utility module | Reusable, testable, follows modular architecture |
| Focus tracking | Component-local state | Simplest approach, no global state needed |
| Styling changes | CSS-in-component | Follows existing pattern in codebase |
