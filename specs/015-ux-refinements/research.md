# Research: UX Refinements

**Feature**: 015-ux-refinements
**Date**: 2026-01-18

## Overview

This document captures research findings for implementing the UX refinements. All technical context was resolved through codebase exploration; no external research was required.

---

## 1. Datetime Formatting

**Decision**: Create a dedicated `dateFormatter.js` utility function

**Rationale**:
- JavaScript's native `Date.toLocaleString()` cannot produce the exact required format "Sun 18-Jan-26 09:58am"
- A utility function allows reuse across components and enables comprehensive unit testing
- The function will use `Intl.DateTimeFormat` for locale-aware parts and manual string assembly for the specific format

**Implementation Approach**:
```javascript
// Example output: "Sun 18-Jan-26 09:58am"
export function formatMessageDatetime(isoTimestamp) {
  const date = new Date(isoTimestamp)
  const dayName = date.toLocaleDateString('en-US', { weekday: 'short' }) // "Sun"
  const day = date.getDate().toString().padStart(2, '0') // "18"
  const month = date.toLocaleDateString('en-US', { month: 'short' }) // "Jan"
  const year = date.getFullYear().toString().slice(-2) // "26"
  const hours = date.getHours()
  const minutes = date.getMinutes().toString().padStart(2, '0')
  const ampm = hours >= 12 ? 'pm' : 'am'
  const hour12 = hours % 12 || 12

  return `${dayName} ${day}-${month}-${year} ${hour12}:${minutes}${ampm}`
}
```

**Alternatives Considered**:
- Using a library like `date-fns` or `dayjs` - Rejected as overkill for a single format function
- Inline formatting in component - Rejected for testability and reusability reasons

---

## 2. Conversation Ordering

**Decision**: Sort conversations in `useConversations.js` after fetching from API

**Rationale**:
- The backend already sorts by `updatedAt` descending in `list_conversations()` (file_storage.py:123-124)
- However, the frontend fetches full conversations individually, which may not preserve order
- Sorting on the frontend after all conversations are loaded guarantees deterministic order
- Using `id` as secondary sort key ensures stability when timestamps are identical

**Implementation Approach**:
```javascript
// In useConversations.js, after fetching all conversations:
fullConversations.sort((a, b) => {
  // Primary: updatedAt descending (most recent first)
  const timeCompare = new Date(b.updatedAt) - new Date(a.updatedAt)
  if (timeCompare !== 0) return timeCompare
  // Secondary: id for stability
  return b.id.localeCompare(a.id)
})
```

**Alternatives Considered**:
- Sorting only in HistoryBar component - Rejected because the sort should happen once at data load, not on every render
- Relying solely on backend ordering - Rejected because individual fetch calls don't preserve list order

---

## 3. Button Styling

**Decision**: Use solid background for enabled buttons, muted appearance for disabled

**Rationale**:
- Current styling uses `opacity: 0.5` for disabled state, which is visually subtle
- The warm color palette provides suitable colors for clear state distinction
- Enabled buttons will use `--color-primary` (warm-brown #997E67) as background
- Disabled buttons will remain transparent with reduced opacity and a distinct cursor

**Implementation Approach**:
```css
/* Enabled state - prominent and clickable */
.send-button:not(:disabled) {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.send-button:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

/* Disabled state - muted and non-interactive */
.send-button:disabled {
  background-color: transparent;
  color: var(--color-text-secondary);
  border-color: var(--color-border);
  opacity: 0.5;
  cursor: not-allowed;
}
```

**Alternatives Considered**:
- Using icons to indicate state - Rejected as unnecessary complexity
- Different colors for disabled (gray) - Could be considered but warm palette muted state is sufficient

---

## 4. Model Selector Relocation

**Decision**: Move ModelSelector from App.vue into InputArea.vue

**Rationale**:
- Currently ModelSelector sits between ChatArea and InputArea in App.vue (line 24)
- Moving it inside InputArea groups related input controls together
- Position it above the textarea/button container, still within the input pane

**Implementation Approach**:
- Remove `<ModelSelector />` from App.vue template
- Remove ModelSelector import and component registration from App.vue
- Add ModelSelector import and component to InputArea.vue
- Position above the existing `.input-container` div

**Alternatives Considered**:
- Keeping in App.vue but repositioning with CSS - Rejected because logical component grouping is preferred
- Embedding selector inline with send button - Rejected as it would clutter the input row

---

## 5. Status Indicator Removal

**Decision**: Remove status indicator elements from StatusBar.vue, keep title and rename functionality

**Rationale**:
- User feedback indicates the status indicator doesn't add value
- The StatusBar will retain the conversation title display and TitleMenu for renaming
- Removes visual noise and simplifies the header

**Implementation Approach**:
- Remove `.status-indicator` element and related CSS
- Remove `.status-text` element and related CSS
- Remove `statusType` prop usage and related computed styles
- Keep `title` prop and TitleMenu component
- May simplify or rename component if it becomes just a title bar

**Alternatives Considered**:
- Hiding indicator with CSS toggle - Rejected because unused code should be removed
- Moving indicator elsewhere - Rejected per user's explicit request to remove it

---

## 6. Message Metadata Layout

**Decision**: Stack datetime and model indicator vertically on response messages

**Rationale**:
- Currently model indicator is positioned with `text-align: right` on its own line
- Spec requires datetime above model indicator, both vertically stacked
- For user messages: show only datetime (no model indicator)
- For system messages: show datetime, then model indicator below it

**Implementation Approach**:
```html
<!-- In MessageBubble.vue -->
<div class="message-metadata">
  <div class="message-datetime">{{ formattedDatetime }}</div>
  <div v-if="message.sender === 'system' && message.model" class="model-indicator">
    {{ message.model }}
  </div>
</div>
```

```css
.message-metadata {
  margin-top: var(--spacing-xs);
}

.message-datetime {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  opacity: 0.7;
}

.model-indicator {
  font-size: var(--font-size-xs);
  opacity: 0.5;
  font-style: italic;
}
```

**Alternatives Considered**:
- Inline datetime and model on same line - Rejected per spec requirement for vertical stacking
- Datetime on right side - Rejected per spec to have consistent left-aligned metadata

---

## Summary

All research items resolved. No external dependencies or technology choices required. Implementation can proceed with the approaches documented above.
