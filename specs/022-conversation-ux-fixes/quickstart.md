# Quickstart: Conversation UX Fixes

**Feature**: 022-conversation-ux-fixes
**Date**: 2026-01-22

## Overview

This feature makes four UX improvements to the conversation interface:

1. **Fix conversation ordering** - New/updated conversations appear at top
2. **Maintain chat input focus** - Focus stays in input after response completes
3. **Add timestamps** - Show last activity time below conversation titles
4. **Compact styling** - Smaller text and spacing to show more conversations

## Prerequisites

- Node.js 18+ installed
- Repository cloned and dependencies installed

## Quick Setup

```bash
# Install dependencies (if not already done)
cd frontend
npm install

# Start development server
npm run dev
```

## File Locations

| Component | File | Purpose |
|-----------|------|---------|
| Conversation List | `frontend/src/components/HistoryBar/HistoryBar.vue` | Ordering, timestamps, styling |
| Chat Input | `frontend/src/components/InputArea/InputArea.vue` | Focus retention |
| State Management | `frontend/src/state/useConversations.js` | Sorting logic |
| Date Formatter | `frontend/src/utils/dateFormatter.js` | NEW: Timestamp formatting |

## Implementation Order (Thin Slices)

### Slice 1: Conversation Ordering (P1)

**Goal**: New conversations appear at top of list

**Files to modify**:
- `frontend/src/state/useConversations.js`

**Test**:
1. Create new conversation
2. Verify it appears at top of sidebar
3. Send message in older conversation
4. Verify that conversation moves to top

### Slice 2: Chat Input Focus (P1)

**Goal**: Focus stays in input after AI response

**Files to modify**:
- `frontend/src/components/InputArea/InputArea.vue`

**Test**:
1. Click in message input, type message
2. Press Enter to send
3. Wait for response to complete
4. Verify cursor is still in input (no need to click)
5. Type and send another message immediately

### Slice 3: Timestamps (P2)

**Goal**: Show last activity time below conversation titles

**Files to create**:
- `frontend/src/utils/dateFormatter.js`

**Files to modify**:
- `frontend/src/components/HistoryBar/HistoryBar.vue`

**Test**:
1. View conversation sidebar
2. Verify each entry shows timestamp
3. Today's conversations show time (e.g., "3:45 PM")
4. Yesterday's show "Yesterday"
5. Older show date (e.g., "Jan 20")

### Slice 4: Compact Styling (P2)

**Goal**: 30-50% more conversations visible

**Files to modify**:
- `frontend/src/components/HistoryBar/HistoryBar.vue` (CSS only)

**Test**:
1. Count visible conversations before changes
2. Apply styling changes
3. Count visible conversations after
4. Verify at least 30% more visible

## Running Tests

```bash
# Run unit tests
cd frontend
npm run test

# Run specific test file
npm run test -- dateFormatter.test.js

# Run tests in watch mode
npm run test -- --watch
```

## Key Implementation Notes

### Sorting After Mutations

```javascript
// In useConversations.js - ensure sort is called after mutations
function createConversation(title) {
  const newConv = { /* ... */ }
  conversations.value.push(newConv)
  sortConversationsByRecent(conversations.value)  // ← Add this
  return newConv
}
```

### Focus Tracking

```javascript
// In InputArea.vue
const hadFocusBeforeSend = ref(false)
const inputRef = ref(null)

function handleSend() {
  hadFocusBeforeSend.value = document.activeElement === inputRef.value
  // ... send message
}

function onResponseComplete() {
  if (hadFocusBeforeSend.value) {
    nextTick(() => inputRef.value?.focus())
  }
}
```

### Timestamp Formatting

```javascript
// In dateFormatter.js
export function formatConversationTimestamp(isoDate) {
  const date = new Date(isoDate)
  const now = new Date()
  const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return date.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
  } else if (diffDays === 1) {
    return 'Yesterday'
  } else if (diffDays < 7) {
    return date.toLocaleDateString(undefined, { weekday: 'long' })
  } else {
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
  }
}
```

## Verification Checklist

- [ ] New conversations appear at top of list
- [ ] Updated conversations move to top
- [ ] Ordering persists after page reload
- [ ] Focus stays in input after response
- [ ] Focus NOT restored if user clicked elsewhere
- [ ] Timestamps display correctly for today/yesterday/older
- [ ] Font size is smaller but readable
- [ ] More conversations visible in same viewport
- [ ] Long titles still truncate with ellipsis
