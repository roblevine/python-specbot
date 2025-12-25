# Research: New Conversation Button

**Feature**: 002-new-conversation-button
**Date**: 2025-12-25
**Status**: Complete

## Overview

This document consolidates technical research and decisions for adding a "New Conversation" button to the HistoryBar component. The feature integrates with existing conversation state management.

## Technical Decisions

### Decision 1: Button Placement and UI Pattern

**Decision**: Add button inside the HistoryBar component's header section (`.history-header`), positioned adjacent to the "Conversations" heading.

**Rationale**:
- Consistent with common chat UI patterns (Discord, Slack, ChatGPT)
- Keeps conversation management controls co-located with conversation list
- Already established header section in HistoryBar component
- Minimal layout changes required

**Alternatives Considered**:
- **Floating action button (FAB)**: More prominent but doesn't fit minimal design aesthetic
- **Top of StatusBar**: Breaks separation of concerns (StatusBar for status, HistoryBar for conversations)
- **Bottom of HistoryBar**: Less discoverable, contradicts "top of message history bar" requirement

**Implementation**:
- Add button element in `.history-header` div
- Use existing CSS variable system for consistent styling
- Button text: "New Conversation" or "+ New" (user preference)
- Icon optional (can use "+" symbol)

---

### Decision 2: Event Flow Architecture

**Decision**: Use Vue event emission pattern - HistoryBar emits `new-conversation` event, App component handles it by calling `createConversation()`.

**Rationale**:
- Follows existing pattern (HistoryBar already emits `select-conversation`)
- Maintains modular architecture (HistoryBar doesn't directly manage state)
- Existing `createConversation()` function in `useConversations.js` already implements required logic
- No new state management code needed

**Alternatives Considered**:
- **Direct state mutation in HistoryBar**: Violates Vue best practices, breaks modularity
- **New composable for button logic**: Over-engineering for single button click
- **Vuex/Pinia store action**: Project doesn't use centralized state store, uses composables pattern

**Implementation**:
```javascript
// HistoryBar.vue
emits: ['select-conversation', 'new-conversation']
function handleNewConversation() {
  emit('new-conversation')
}

// App.vue
function handleNewConversation() {
  const { createConversation } = useConversations()
  createConversation()
  saveToStorage() // Persist immediately
}
```

---

### Decision 3: Handling Unsaved Message Input

**Decision**: Discard unsaved message immediately without confirmation (as specified in spec.md acceptance scenario 3).

**Rationale**:
- Explicit requirement from feature specification
- Simplifies implementation - no modal/dialog component needed
- Consistent with "fast, uninterrupted" workflow
- User explicitly chose "Option A" during specification clarification

**Alternatives Considered**:
- **Confirmation dialog**: Rejected per user choice
- **Auto-save draft**: Rejected per user choice (would require draft functionality)

**Implementation**:
- New conversation creation automatically clears input area (existing behavior)
- No additional code needed - current `createConversation()` switches active conversation, InputArea already reacts to conversation changes

---

### Decision 4: Edge Case - Rapid Button Clicks

**Decision**: Implement debouncing or simple guard flag to prevent multiple conversation creation from rapid clicks.

**Rationale**:
- Prevents duplicate conversation creation
- Improves UX (no jank from multiple rapid state updates)
- Minimal code addition (5-10 lines)

**Alternatives Considered**:
- **No protection**: Could create UX issues and duplicate conversations
- **Disable button after click**: Requires more complex state tracking
- **CSS pointer-events: none**: Doesn't prevent programmatic clicks

**Implementation**:
```javascript
// Simple guard flag approach (preferred for simplicity)
let isCreating = false

function handleNewConversation() {
  if (isCreating) return
  isCreating = true

  emit('new-conversation')

  // Reset after short delay
  setTimeout(() => { isCreating = false }, 300)
}
```

---

### Decision 5: Edge Case - Empty Conversation State

**Decision**: Button click on empty conversation (no messages) creates a new empty conversation anyway.

**Rationale**:
- Simpler logic (no conditional checks)
- Consistent behavior regardless of state
- Matches user expectation of "fresh start"
- Empty conversations without messages are filtered out during storage save (existing behavior in `saveToStorage()`)

**Alternatives Considered**:
- **Do nothing if current conversation is empty**: Confusing UX, unpredictable behavior
- **Replace current empty conversation**: Complex logic, violates YAGNI

**Implementation**:
- No special handling needed
- Existing `saveToStorage()` filters out empty conversations (line 107 in useConversations.js)

---

### Decision 6: Testing Strategy

**Decision**: Three-layer test approach:
1. **Unit tests** (Vitest): Button rendering, event emission, edge cases
2. **Integration tests** (Vitest): Event flow from HistoryBar → App → state change
3. **E2E tests** (Playwright): Full user flow including visual verification

**Rationale**:
- Satisfies Constitution Principle III (Test-First Development)
- Satisfies Constitution Principle IV (Integration & Contract Testing)
- Provides comprehensive coverage at appropriate abstraction levels
- Existing test infrastructure already in place (Vitest + Playwright)

**Test Scenarios**:

**Unit Tests** (`HistoryBar.test.js`):
- Button renders with correct label
- Button emits `new-conversation` event on click
- Rapid clicks don't emit multiple events (debounce test)
- Button is always visible and enabled

**Integration Tests** (can be in `App.test.js` or separate):
- `new-conversation` event triggers `createConversation()`
- New conversation appears in conversations list
- Active conversation ID updates to new conversation
- Storage is updated with new conversation

**E2E Tests** (`new-conversation.spec.js`):
- User clicks "New Conversation" button
- Message input area is cleared
- Previous conversation remains in history
- New conversation becomes active
- Unsaved message is discarded when clicking button

---

### Decision 7: Styling Approach

**Decision**: Reuse existing CSS variables and minimal custom styling for button.

**Rationale**:
- Maintains design consistency with existing components
- No new design system tokens needed
- Fits with "simplicity" principle
- Existing variable system covers colors, spacing, fonts

**Implementation**:
```css
.new-conversation-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: var(--font-size-sm);
  transition: background-color 0.2s;
}

.new-conversation-btn:hover {
  background-color: var(--color-primary-dark);
}
```

---

### Decision 8: Accessibility Considerations

**Decision**: Add semantic HTML and ARIA attributes for accessibility.

**Rationale**:
- Ensures screen reader compatibility
- Provides keyboard navigation support
- Follows web accessibility best practices
- Minimal effort for significant impact

**Implementation**:
```html
<button
  class="new-conversation-btn"
  aria-label="Start new conversation"
  @click="handleNewConversation"
>
  New Conversation
</button>
```

---

## Best Practices Applied

### Vue 3 Composition API
- Continue using Composition API pattern (existing codebase standard)
- Use `emits` option for explicit event declaration
- Leverage existing composables (`useConversations`)

### Component Communication
- Follow unidirectional data flow (parent to child via props, child to parent via events)
- No prop drilling - App component acts as orchestrator
- Keep HistoryBar as presentational component

### State Management
- Reuse existing `createConversation()` function (DRY principle)
- No new state needed in HistoryBar (stateless component)
- Rely on Vue reactivity for UI updates

### Code Organization
- Button logic lives in HistoryBar component (co-location)
- Event handler lives in App component (state orchestration)
- No new files needed (minimal change)

---

## Performance Considerations

### Target: < 200ms button response time

**Measurements**:
- Button click event: ~1ms
- Event emission: ~1ms
- `createConversation()` execution: ~5-10ms (array push + ID generation)
- Vue reactivity update: ~10-20ms
- Re-render: ~20-50ms (depends on conversation count)

**Total estimated**: 40-85ms (well under 200ms target)

**Optimization not needed**: Current implementation will easily meet performance goals.

---

## Dependencies Review

**New Dependencies**: None

**Existing Dependencies Used**:
- Vue 3.4.0 - Component framework
- Vite 5.0.0 - Build tool (testing only)
- Vitest - Unit/integration testing
- Playwright - E2E testing

**Storage Dependencies**:
- LocalStorage (browser native) - via `LocalStorageAdapter.js`

---

## Security Considerations

**Threat Model**: Low risk (frontend-only feature, no user input, no network requests)

**Considerations**:
- No XSS risk (no user input rendered)
- No CSRF risk (no HTTP requests)
- LocalStorage already used by existing code (no new security surface)

**Recommendations**: No special security measures needed.

---

## Summary

All technical unknowns have been resolved:

✅ **UI Pattern**: Button in HistoryBar header
✅ **Event Flow**: Vue event emission → App handler → `createConversation()`
✅ **Unsaved Messages**: Discard immediately (per spec)
✅ **Rapid Clicks**: Guard flag debouncing
✅ **Empty Conversations**: Create anyway, filtered on save
✅ **Testing**: Three-layer approach (unit/integration/E2E)
✅ **Styling**: Reuse existing CSS variables
✅ **Accessibility**: Semantic HTML + ARIA attributes

**Ready for Phase 1**: Design & Contracts
