# Quickstart: UX Refinements

**Feature**: 015-ux-refinements
**Date**: 2026-01-18

## Overview

This feature is frontend-only with no API or data model changes. Implementation involves modifying existing Vue components and adding one new utility function.

## Prerequisites

- Node.js and npm installed
- Frontend dev server: `cd frontend && npm run dev`
- Tests: `cd frontend && npm test`

## Implementation Order

Follow user stories by priority:

### P1: Deterministic Conversation Ordering

**Files to modify**:
- `frontend/src/state/useConversations.js`

**Steps**:
1. In `loadFromStorage()`, after line 169 (`conversations.value = fullConversations`), add sorting
2. Sort by `updatedAt` descending, then by `id` for tie-breaking
3. Test by creating multiple conversations and restarting the app

### P2: Button State Visibility

**Files to modify**:
- `frontend/src/components/InputArea/InputArea.vue`
- `frontend/src/components/HistoryBar/HistoryBar.vue`
- `frontend/public/styles/global.css` (optional - for shared button classes)

**Steps**:
1. Update `.send-button` styles for clear enabled/disabled distinction
2. Enabled: solid background (`--color-primary`), white text
3. Disabled: transparent background, muted colors, `opacity: 0.5`
4. Apply consistent styling to `.new-conversation-btn` and other buttons

### P3: Datetime Display

**Files to create**:
- `frontend/src/utils/dateFormatter.js`
- `frontend/tests/unit/utils/dateFormatter.test.js`

**Files to modify**:
- `frontend/src/components/ChatArea/MessageBubble.vue`

**Steps**:
1. Create `formatMessageDatetime(isoTimestamp)` utility function
2. Write unit tests for various dates and edge cases (midnight, noon, etc.)
3. Replace `formattedTime` computed property with `formattedDatetime`
4. Update template to show datetime below message text
5. For system messages, stack model indicator below datetime

### P4: Model Selector Relocation

**Files to modify**:
- `frontend/src/components/App/App.vue`
- `frontend/src/components/InputArea/InputArea.vue`

**Steps**:
1. Remove `<ModelSelector />` from App.vue template (line 24)
2. Remove ModelSelector import and component registration from App.vue
3. Add ModelSelector import to InputArea.vue
4. Add `<ModelSelector />` above `.input-container` in InputArea.vue template
5. Adjust InputArea styles to accommodate the selector

### P5: Remove Status Indicator

**Files to modify**:
- `frontend/src/components/StatusBar/StatusBar.vue`
- `frontend/src/components/App/App.vue` (remove status-related props)

**Steps**:
1. Remove `.status-indicator` and `.status-text` from StatusBar template
2. Remove related CSS styles
3. Remove `status` and `statusType` props
4. Update App.vue to not pass these props
5. Consider renaming component to TitleBar if appropriate

## Testing Checklist

- [ ] Conversations appear in same order after multiple app restarts
- [ ] Send button is clearly distinguishable when enabled vs disabled
- [ ] All buttons follow consistent enabled/disabled styling
- [ ] Datetime appears on user messages in correct format
- [ ] Datetime and model appear stacked on system messages
- [ ] Model selector appears above chat input within input pane
- [ ] Status indicator is no longer visible
- [ ] No console errors or warnings
- [ ] Existing tests still pass

## Rollback

All changes are in frontend components with no data migration. Rollback by reverting commits.
