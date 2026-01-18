# Research: Delete Conversation Feature

**Date**: 2026-01-18
**Branch**: `016-delete-conversation`

## Overview

This research documents the technical decisions for implementing the delete conversation feature. Since the backend DELETE endpoint already exists and the frontend follows established patterns, the research focuses on confirming the approach and documenting key decisions.

---

## Research Topic 1: Existing DELETE API Compatibility

### Question
Does the existing DELETE `/api/v1/conversations/{id}` endpoint meet the feature requirements?

### Findings

**Endpoint Analysis** (from `backend/src/api/routes/conversations.py:259-301`):
- Route: `DELETE /api/v1/conversations/{conversation_id}`
- Success response: HTTP 204 No Content
- Error responses: 404 (not found), 500 (server error)
- Implementation removes conversation from storage and state

**API Client Analysis** (from `frontend/src/services/apiClient.js:725-776`):
- Function `deleteConversation(conversationId)` exists
- Returns `Promise<void>`
- Proper error handling for 404 and network errors

**State Management** (from `frontend/src/state/useConversations.js:338-364`):
- `deleteConversation(conversationId)` method exists
- Removes from local state after successful API call
- Handles active conversation switching if deleted conversation was active
- Exposes `saveError` for error state

### Decision
**Use existing API and state management as-is.** No backend or service changes required.

### Rationale
The existing implementation already handles:
- Permanent deletion from storage
- State synchronization
- Error propagation
- Active conversation management

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Add soft delete | Not required by spec; adds complexity |
| Add undo functionality | Not in scope; spec requires permanent deletion |
| Create new endpoint | Existing endpoint meets all requirements |

---

## Research Topic 2: Modal Dialog Pattern

### Question
How should the confirmation dialog be implemented to match existing patterns?

### Findings

**RenameDialog Pattern Analysis** (from `frontend/src/components/RenameDialog/RenameDialog.vue`):
- Props: Accepts data needed for display (e.g., `currentTitle`)
- Emits: `save` and `cancel` events
- Structure: Fixed overlay, centered dialog box, header, content, footer with buttons
- Styling: Uses CSS variables for theming
- Keyboard: Enter to confirm, Escape to cancel
- Focus: Manages focus appropriately

**App.vue Integration Pattern**:
- State variable controls dialog visibility (e.g., `showRenameDialog`)
- Handler functions for save/cancel emits
- Error handling via `setError()` from `useAppState`

### Decision
**Create DeleteConfirmationDialog following RenameDialog pattern** with:
- Props: `conversationTitle` (to display what will be deleted)
- Emits: `confirm` and `cancel`
- Styling: Reuse modal overlay pattern, add danger styling for delete button
- Keyboard: Escape to cancel, Enter to confirm

### Rationale
Following established patterns ensures:
- Consistent user experience
- Code maintainability
- Easier review and testing

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Browser native confirm() | Doesn't match app styling; blocks thread |
| Toast with undo | Spec requires confirmation before delete |
| Inline confirmation | Context menu too small; poor UX |

---

## Research Topic 3: TitleMenu Extension Strategy

### Question
How should the TitleMenu component be extended to support delete functionality?

### Findings

**Current TitleMenu Structure** (from `frontend/src/components/TitleMenu/TitleMenu.vue`):
- No props currently
- Single emit: `rename`
- Menu items rendered inline

**Usage in HistoryBar** (from `frontend/src/components/HistoryBar/HistoryBar.vue:46-49`):
```vue
<TitleMenu
  class="conversation-menu"
  @rename="$emit('rename-conversation', conversation.id)"
/>
```

### Decision
**Extend TitleMenu with:**
1. New prop: `showDelete` (Boolean, default: true) - controls Delete option visibility
2. New emit: `delete` - fires when Delete is clicked
3. Add "Delete" menu item with danger styling (red text)

**HistoryBar changes:**
1. Pass `showDelete` prop based on `conversation.id !== activeConversationId`
2. Handle `@delete` emit to bubble up `delete-conversation` event

### Rationale
- Prop-based control allows parent to decide visibility (separation of concerns)
- Adding emit follows existing pattern
- Minimal changes to existing component

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Create separate DeleteMenu component | Duplicates menu logic; harder to maintain |
| Pass isActive to TitleMenu | Couples TitleMenu to conversation logic |
| Always show Delete, disable for active | Spec says "not visible", not "disabled" |

---

## Research Topic 4: Error Handling Strategy

### Question
How should deletion errors be displayed to users?

### Findings

**Existing Error Pattern** (from App.vue rename handler):
```javascript
} catch (error) {
  logger.error('Failed to rename conversation', error)
  setError('Failed to rename conversation')
}
```

**useAppState provides:**
- `setError(message)` - sets error in status bar
- Status bar displays error with appropriate styling

### Decision
**Follow existing pattern:**
1. Close dialog on error (don't keep it open)
2. Call `setError('Failed to delete conversation')` for user feedback
3. Log detailed error via `logger.error()`
4. Conversation remains in list (state not modified on failure)

### Rationale
- Consistent with existing error handling
- Non-blocking feedback (status bar, not modal)
- Preserves data integrity on failure

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Show error in dialog | Inconsistent with rename pattern |
| Retry mechanism | Not in scope; YAGNI |
| Toast notifications | Not implemented in app; would require new component |

---

## Research Topic 5: Active Conversation Protection

### Question
How is "active conversation" determined and how should protection be implemented?

### Findings

**Active Conversation State** (from useConversations.js):
- `activeConversationId` reactive ref tracks currently selected conversation
- Passed to HistoryBar as prop
- Used for CSS styling (`.active` class)

**HistoryBar Active Check** (line ~34):
```vue
:class="{ active: conversation.id === activeConversationId }"
```

### Decision
**Implement protection in HistoryBar:**
```vue
<TitleMenu
  :show-delete="conversation.id !== activeConversationId"
  @rename="..."
  @delete="..."
/>
```

### Rationale
- HistoryBar already has access to both `conversation.id` and `activeConversationId`
- Logic stays in component that owns the context
- TitleMenu remains generic (just responds to props)

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Check in TitleMenu | Would require passing activeId to TitleMenu |
| Check in App.vue handler | Delete event would fire unnecessarily |
| CSS hide only | Still emits event; not truly hidden |

---

## Summary of Decisions

| Topic | Decision |
|-------|----------|
| Backend API | Use existing DELETE endpoint (no changes) |
| Dialog pattern | Follow RenameDialog pattern with danger styling |
| TitleMenu extension | Add `showDelete` prop and `delete` emit |
| Error handling | Use `setError()` for status bar feedback |
| Active protection | Conditional `showDelete` prop in HistoryBar |

## No Outstanding Clarifications

All technical decisions are resolved. Implementation can proceed to Phase 1 design artifacts.
