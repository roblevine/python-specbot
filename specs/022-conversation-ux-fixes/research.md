# Research: Conversation UX Fixes

**Feature**: 022-conversation-ux-fixes
**Date**: 2026-01-22
**Status**: Complete

## Research Tasks

### 1. Conversation Ordering Implementation

**Question**: How is conversation sorting currently implemented and why might new conversations appear at the bottom?

**Research Findings**:

The sorting logic exists in `frontend/src/state/useConversations.js`:

```javascript
function sortConversationsByRecent(convs) {
  return convs.sort((a, b) => {
    const timeCompare = new Date(b.updatedAt) - new Date(a.updatedAt)
    if (timeCompare !== 0) return timeCompare
    return b.id.localeCompare(a.id)
  })
}
```

**Root Cause Analysis**:
- The `sortConversationsByRecent()` function correctly sorts by `updatedAt` descending
- However, the function is only called in `loadFromStorage()` on initial load
- When new conversations are created or updated, the sort may not be re-applied
- The Vue reactivity system may not trigger a re-sort when array elements are updated

**Decision**: Ensure sorting is applied after every conversation mutation (create, update, message added)

**Alternatives Considered**:
- Computed property with automatic sorting: More Vue-idiomatic but may cause unnecessary re-renders
- Sort on render in component: Adds complexity to component, violates separation of concerns
- **Selected**: Call sort explicitly after mutations in state management

---

### 2. Focus Retention Best Practices

**Question**: What is the best approach for maintaining input focus after async operations in Vue?

**Research Findings**:

Vue 3 provides `ref` for template refs and lifecycle hooks for timing:

```javascript
// Template ref approach
const inputRef = ref(null)

// Restore focus after async operation
async function sendMessage() {
  const hadFocus = document.activeElement === inputRef.value
  await sendMessageAsync()
  if (hadFocus) {
    inputRef.value?.focus()
  }
}
```

**Key Considerations**:
1. Track whether user intentionally moved focus (click elsewhere)
2. Only restore focus if user had focus before operation started
3. Use `nextTick()` to ensure DOM updates complete before focusing
4. Handle streaming responses where multiple updates occur

**Decision**: Track focus state before send, restore after response completion if user didn't click elsewhere

**Implementation Approach**:
1. Add `hadFocusBeforeSend` ref to track focus state
2. On send: capture `document.activeElement === inputRef.value`
3. On click elsewhere: set `hadFocusBeforeSend = false`
4. On response complete: restore focus if `hadFocusBeforeSend` was true

---

### 3. Timestamp Formatting Patterns

**Question**: What is the best approach for relative/smart timestamp formatting?

**Research Findings**:

Common patterns for chat/messaging apps:
- **Today**: Show time only ("3:45 PM")
- **Yesterday**: Show "Yesterday" or "Yesterday 3:45 PM"
- **This week**: Show day name ("Monday")
- **Older**: Show full date ("Jan 20, 2026")

**Options Evaluated**:

| Approach | Pros | Cons |
|----------|------|------|
| Native `Intl.RelativeTimeFormat` | No dependencies, good i18n | Limited formatting options |
| date-fns `formatDistanceToNow` | Flexible, tree-shakeable | New dependency |
| Custom utility | No dependencies, full control | More code to maintain |

**Decision**: Custom utility using native `Intl.DateTimeFormat`

**Rationale**:
- No new dependencies (follows YAGNI principle)
- Native APIs provide good i18n support
- Simple logic for this use case
- Easily testable

**Implementation**:
```javascript
export function formatConversationTimestamp(isoDate) {
  const date = new Date(isoDate)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    // Today: show time only
    return date.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
  } else if (diffDays === 1) {
    // Yesterday
    return 'Yesterday'
  } else if (diffDays < 7) {
    // This week: show day name
    return date.toLocaleDateString(undefined, { weekday: 'long' })
  } else {
    // Older: show date
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
  }
}
```

---

### 4. Compact Styling Approach

**Question**: What CSS values should be used for smaller, more compact conversation entries?

**Research Findings**:

Current HistoryBar.vue styling (estimated from screenshot):
- Font size: ~16px (1rem)
- Line height: ~1.5
- Padding: ~12-16px vertical
- Item spacing: ~8-12px gap

**Recommended Compact Values**:

| Property | Current | Compact | Reduction |
|----------|---------|---------|-----------|
| Font size | 16px | 13px | ~19% |
| Line height | 1.5 | 1.3 | ~13% |
| Padding | 12px | 8px | ~33% |
| Item gap | 8px | 4px | ~50% |

**Decision**: Apply CSS changes to achieve 30-50% more visible entries

**Implementation Notes**:
- Use relative units (rem, em) for accessibility
- Test readability at standard viewing distances
- Maintain ellipsis truncation for long titles
- Add timestamp as smaller subtext (11px / 0.7rem)

---

## Summary of Decisions

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Ordering | Re-sort after mutations | Explicit, predictable, matches existing pattern |
| Focus | Track state, restore conditionally | Respects user intent, works with streaming |
| Timestamps | Custom utility with native Intl | No dependencies, testable, good i18n |
| Styling | CSS adjustments | Simple, no structural changes needed |

## Dependencies

No new npm dependencies required. All implementations use:
- Vue 3 composition API (existing)
- Native JavaScript `Intl.DateTimeFormat`
- Native JavaScript `Date`

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Focus restoration conflicts with accessibility | Low | Medium | Test with screen readers, respect user preference |
| Timestamp timezone issues | Low | Low | Use native APIs which handle timezones |
| CSS changes break mobile layout | Low | Medium | Test on multiple viewport sizes |
