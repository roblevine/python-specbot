# Implementation Plan: Conversation Titles

**Branch**: `014-conversation-titles` | **Date**: 2026-01-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/014-conversation-titles/spec.md`

## Summary

Implement conversation titles feature where each conversation has a title (initially set to the first user message), displayed in the status bar (aligned with chat content) and history sidebar (replacing message previews). Users can rename conversations via ellipsis menus in both locations. **Good news:** Backend already supports titles, auto-title generation is partially implemented, API endpoints exist - this is primarily a frontend UI feature.

## Technical Context

**Language/Version**: JavaScript (ES6+) for frontend, Python 3.13 for backend
**Primary Dependencies**: Vue 3.4.0, Vite 5.0.0, FastAPI 0.115.0
**Storage**: Browser LocalStorage (frontend), File-based JSON (backend) - both already support title field
**Testing**: Vitest (unit), Playwright (E2E) for frontend; pytest for backend
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend focus - backend already complete)
**Performance Goals**: Title updates reflect within 100ms across all UI locations
**Constraints**: Title max 500 characters; 1 non-whitespace character minimum
**Scale/Scope**: 4 Vue components affected (StatusBar, HistoryBar, new TitleMenu, new RenameDialog)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | ✅ Pass | Backend API already exists (`PUT /api/v1/conversations/{id}` supports title) |
| II. Modular Architecture | ✅ Pass | New components (TitleMenu, RenameDialog) are self-contained |
| III. Test-First Development | ✅ Required | Write tests for title display, rename flow before implementation |
| IV. Integration & Contract Testing | ✅ Pass | Existing contract tests cover conversation updates; no new endpoints |
| V. Observability & Debuggability | ✅ Pass | Frontend console logging for title operations |
| VI. Simplicity & YAGNI | ✅ Pass | Reuse existing infrastructure; minimal new components |
| VII. Versioning & Breaking Changes | ✅ Pass | No API changes; backward compatible (titles default to "New Conversation") |
| VIII. Incremental Delivery & Thin Slices | ✅ Required | Implement by user story priority (P1→P2) |
| IX. Living Architecture Documentation | N/A | No architectural changes (UI-only feature) |

**Gate Result**: PASS - No violations requiring justification.

**Note**: This feature does NOT require architecture.md updates - it's a UI enhancement using existing infrastructure with no new modules, data flows, or technology choices.

## Project Structure

### Documentation (this feature)

```text
specs/014-conversation-titles/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0: Existing infrastructure analysis
├── data-model.md        # Phase 1: Title field mapping (minimal - already exists)
├── quickstart.md        # Phase 1: Implementation guide
├── contracts/           # Phase 1: No new contracts needed
├── checklists/
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Phase 2: Implementation tasks (via /speckit.tasks)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   ├── App/App.vue                    # Wire up title display and rename
│   │   ├── StatusBar/StatusBar.vue        # MODIFY: Add title display aligned with chat
│   │   ├── HistoryBar/HistoryBar.vue      # MODIFY: Remove preview, add ellipsis menu
│   │   ├── TitleMenu/                     # NEW: Shared ellipsis menu component
│   │   │   └── TitleMenu.vue
│   │   └── RenameDialog/                  # NEW: Modal for title editing
│   │       └── RenameDialog.vue
│   ├── state/
│   │   └── useConversations.js            # MODIFY: Add renameConversation()
│   └── utils/
│       └── validators.js                  # NEW: Title validation helpers
└── tests/
    ├── unit/
    │   ├── TitleMenu.test.js              # NEW
    │   ├── RenameDialog.test.js           # NEW
    │   └── useConversations.test.js       # MODIFY: Add rename tests
    └── e2e/
        └── conversation-titles.spec.js    # NEW: E2E title flow tests

backend/
└── (No changes required - API already supports titles)
```

**Structure Decision**: Web application structure. Backend is complete for this feature. All modifications are in `frontend/` directory.

## Complexity Tracking

> No violations to justify - all changes follow constitution principles using existing infrastructure.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Implementation Approach

### Existing Infrastructure (No Changes Needed)

1. **Backend API** - `PUT /api/v1/conversations/{id}` already accepts `{ title: string }`
2. **Data Model** - `Conversation.title` field exists in both frontend and backend schemas
3. **Storage** - Title persisted in localStorage (frontend) and JSON file (backend)
4. **Auto-title** - `useConversations.addMessage()` already sets title to first message (50 chars)

### Thin Slices (by Priority)

| Slice | User Story | Deliverable | Test Focus |
|-------|------------|-------------|------------|
| 1 | US2 (P1) | Enhance auto-title (full text, not truncated storage) | First message becomes full title |
| 2 | US1 (P1) | Title display in StatusBar aligned with chat | Title shows, truncates, updates |
| 3 | US3 (P1) | Title-only display in HistoryBar | No preview, just title |
| 4 | US4 (P2) | Rename from StatusBar (ellipsis menu) | Menu opens, rename saves |
| 5 | US5 (P2) | Rename from HistoryBar (ellipsis menu) | Menu on hover, rename saves |

### Key Files to Modify

1. **useConversations.js** - Add `renameConversation(id, newTitle)`, enhance auto-title logic
2. **StatusBar.vue** - Add title display with truncation, ellipsis menu
3. **HistoryBar.vue** - Remove `getPreview()`, add ellipsis menu on conversation items
4. **New: TitleMenu.vue** - Reusable menu with "Rename" option
5. **New: RenameDialog.vue** - Modal with title input, validation, save/cancel

### Frontend Component Changes

**StatusBar.vue** changes:
- Add `activeConversationTitle` prop
- Display title aligned with chat content (use `--chat-max-width`)
- Add TitleMenu component (ellipsis icon → rename option)
- Truncate long titles with CSS `text-overflow: ellipsis`

**HistoryBar.vue** changes:
- Remove `conversation-preview` div and `getPreview()` function
- Add ellipsis menu icon on conversation items (show on hover)
- Add TitleMenu component to each conversation item
- Emit `rename-conversation` event when rename selected

**App.vue** changes:
- Pass `activeConversationTitle` computed prop to StatusBar
- Handle `rename-conversation` event from both StatusBar and HistoryBar
- Show RenameDialog modal when rename triggered

### Title Display Rules

1. **Storage**: Store full title text (no truncation in data)
2. **StatusBar**: Truncate display at available width (CSS ellipsis)
3. **HistoryBar**: Truncate display at sidebar width (CSS ellipsis)
4. **Default**: "New Conversation" until first message sent
5. **Auto-generation**: First user message text becomes title (full text stored)
6. **Validation**: 1-500 characters, non-whitespace required

## Next Steps

1. **Phase 0**: Generate `research.md` documenting existing infrastructure findings
2. **Phase 1**: Generate `data-model.md` (title field mapping) and `quickstart.md`
3. **Run `/speckit.tasks`**: Generate implementation tasks from this plan
