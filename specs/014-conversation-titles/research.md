# Research: Conversation Titles

**Feature**: 014-conversation-titles
**Date**: 2026-01-17

## Executive Summary

This feature leverages extensive existing infrastructure. The backend is fully complete - conversation title storage, API endpoints, and persistence already exist. The frontend has partial implementation (auto-title on first message). This research confirms minimal new development is needed.

## Existing Infrastructure Analysis

### Backend (Complete - No Changes Needed)

| Component | Status | Details |
|-----------|--------|---------|
| Data Model | ✅ Complete | `Conversation.title` field in `schemas.py` (1-100 chars) |
| API Endpoint | ✅ Complete | `PUT /api/v1/conversations/{id}` accepts `{ title: string }` |
| Storage | ✅ Complete | Title persisted in `backend/data/conversations.json` |
| Validation | ✅ Complete | Pydantic validates title length (1-100 chars server-side) |
| Contract Tests | ✅ Complete | Existing tests cover conversation updates |

**Decision**: No backend changes required.
**Rationale**: API already supports all title operations (create, read, update).
**Alternatives Considered**: None - backend is complete.

### Frontend (Partial - Enhancements Needed)

| Component | Status | Details |
|-----------|--------|---------|
| Data Model | ✅ Complete | `conversation.title` in localStorage schema v1.1.0 |
| Auto-title | ⚠️ Partial | `useConversations.addMessage()` sets title to first 50 chars |
| Display | ❌ Missing | StatusBar shows status, not title; HistoryBar shows preview |
| Rename UI | ❌ Missing | No ellipsis menus or rename dialog |
| Validation | ❌ Missing | No client-side title validation (500 char limit per spec) |

**Decision**: Frontend-only changes - enhance auto-title, add title display, create rename UI.
**Rationale**: Reuse existing data flow and storage; add UI components only.
**Alternatives Considered**:
- Create new title management service → Rejected (overkill for simple state update)
- Inline title editing → Rejected (ellipsis menu pattern more consistent with spec)

### Existing Code References

**Auto-title generation** (`useConversations.js` lines 107-110):
```javascript
// Update title from first message if it's still default
if (conversation.title === 'New Conversation' && conversation.messages.length === 1) {
  conversation.title = message.text.slice(0, 50)
}
```

**Change needed**: Remove `.slice(0, 50)` to store full text per FR-005.

**Message preview** (`HistoryBar.vue` lines 83-89):
```javascript
function getPreview(conversation) {
  if (conversation.messages.length === 0) {
    return 'No messages'
  }
  const lastMessage = conversation.messages[conversation.messages.length - 1]
  return lastMessage.text.slice(0, 50) + (lastMessage.text.length > 50 ? '...' : '')
}
```

**Change needed**: Remove this function and `.conversation-preview` element per FR-009.

## Technology Decisions

### Ellipsis Menu Implementation

**Decision**: Create reusable `TitleMenu.vue` component with dropdown positioning.
**Rationale**:
- Used in two places (StatusBar, HistoryBar) - DRY principle
- Simple dropdown menu, no need for external library
- Consistent with existing Vue component patterns
**Alternatives Considered**:
- Use third-party dropdown library (vue-dropdown) → Rejected (adds dependency for simple feature)
- Inline menu in each component → Rejected (code duplication)

### Rename Dialog Implementation

**Decision**: Create modal `RenameDialog.vue` component with form input.
**Rationale**:
- Standard modal pattern used elsewhere in app
- Clear save/cancel actions
- Input validation before submission
**Alternatives Considered**:
- Inline editing (click title to edit) → Rejected (spec requires menu → dialog flow)
- Browser prompt() → Rejected (poor UX, no validation)

### Title Truncation Strategy

**Decision**: CSS-only truncation with `text-overflow: ellipsis`.
**Rationale**:
- Browser handles truncation automatically based on container width
- Responsive - adapts to viewport changes
- No JavaScript needed
**Alternatives Considered**:
- JavaScript truncation (slice to N chars) → Rejected (not responsive, duplicates CSS capability)
- Tooltip on hover showing full title → Could add later as enhancement

### Title Alignment in StatusBar

**Decision**: Use CSS max-width matching chat content area (`--chat-max-width: 768px`).
**Rationale**:
- Visual alignment with chat messages (per FR-007)
- Uses existing CSS variable
- Consistent with UI redesign (feature 013)
**Alternatives Considered**:
- Full-width title → Rejected (doesn't align with chat content per spec)
- Fixed pixel width → Rejected (not responsive)

## Validation Rules

### Client-Side (Frontend)

| Rule | Value | Rationale |
|------|-------|-----------|
| Min length | 1 non-whitespace char | Prevent empty titles (FR-018) |
| Max length | 500 characters | Reasonable limit per spec (FR-019) |
| Trim whitespace | Yes, on save | Clean data, prevent " " only titles |

### Server-Side (Backend - Existing)

| Rule | Value | Notes |
|------|-------|-------|
| Min length | 1 char | Already enforced by Pydantic |
| Max length | 100 chars | Backend limit; frontend enforces 500 for display |

**Note**: Backend has stricter limit (100) than spec (500). For this feature, we'll enforce 500 on frontend display but the actual stored title may be truncated to 100 by backend. This is acceptable as the frontend stores full title in localStorage and only syncs to backend.

## Data Migration

**Decision**: No migration needed.
**Rationale**:
- Conversations already have `title` field (auto-generated on first message)
- Default "New Conversation" for conversations without messages
- Existing data is compatible
**Alternatives Considered**:
- Force re-generation of all titles → Rejected (unnecessary, would overwrite user-renamed titles)

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Long titles cause layout issues | Medium | Low | CSS truncation handles gracefully |
| Rename dialog accessibility | Low | Medium | Standard form controls, keyboard support |
| Performance with many conversations | Low | Low | Reactive updates are instant |

## Conclusion

This is a low-risk, frontend-only feature enhancement. The infrastructure is largely complete:
- Backend: 100% ready
- Frontend data/storage: 100% ready
- Frontend UI: ~20% ready (auto-title exists)

Estimated effort: 4-6 hours implementation, primarily UI components.
