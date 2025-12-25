# Component Interface Contract: HistoryBar

**Feature**: 002-new-conversation-button
**Date**: 2025-12-25
**Contract Version**: 1.0.0
**Component**: HistoryBar.vue

## Overview

This contract defines the modified interface for the HistoryBar component after adding the "New Conversation" button feature. It specifies the component's props, events, and behavioral contracts.

## Component Contract

### Component Name
`HistoryBar`

### File Location
`frontend/src/components/HistoryBar/HistoryBar.vue`

---

## Props

### Input Properties

| Prop Name | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `conversations` | `Array<Conversation>` | No | `[]` | Array of conversation objects to display in the history list |
| `activeConversationId` | `String` | No | `null` | ID of the currently active conversation (for highlighting) |

#### Conversation Object Schema

```typescript
interface Conversation {
  id: string                // Unique conversation identifier
  title: string             // Display title for the conversation
  messages: Message[]       // Array of messages in the conversation
  createdAt: string         // ISO 8601 timestamp
  updatedAt: string         // ISO 8601 timestamp
}

interface Message {
  id: string                // Unique message identifier
  role: 'user' | 'assistant' // Message sender
  text: string              // Message content
  timestamp: string         // ISO 8601 timestamp
}
```

---

## Events

### Emitted Events

| Event Name | Payload Type | Description | When Emitted |
|------------|--------------|-------------|--------------|
| `select-conversation` | `string` (conversationId) | User clicked on a conversation in the history list | When user clicks any conversation item |
| `new-conversation` | `void` (no payload) | **[NEW]** User clicked the "New Conversation" button | When user clicks the new conversation button |

---

## Event Contracts

### Event: `select-conversation`

**Purpose**: Notify parent component that user wants to switch to a different conversation

**Payload**:
```javascript
conversationId: string  // ID of the conversation that was clicked
```

**Contract**:
- MUST be emitted when user clicks on a conversation item
- Payload MUST be a valid conversation ID that exists in the `conversations` prop
- MAY be emitted for the currently active conversation (no-op in parent)
- MUST NOT be emitted if conversations list is empty

**Parent Handler Expectations**:
- Parent SHOULD update `activeConversationId` to match the emitted ID
- Parent SHOULD load messages for the selected conversation
- Parent MAY ignore if conversationId matches current active conversation

**Example**:
```javascript
// Component emits
emit('select-conversation', 'conv_1735135200000_a1b2c3')

// Parent handles
function handleSelectConversation(conversationId) {
  activeConversationId.value = conversationId
  loadMessagesForConversation(conversationId)
}
```

---

### Event: `new-conversation` ✨ NEW

**Purpose**: Notify parent component that user wants to start a new conversation

**Payload**: None (void)

**Contract**:
- MUST be emitted when user clicks the "New Conversation" button
- MUST NOT emit multiple times for rapid clicks (debounced internally)
- MUST be emitted regardless of current conversation state (empty or not)
- MUST be emitted even if user has unsaved message typed

**Parent Handler Expectations**:
- Parent MUST create a new conversation object
- Parent MUST set the new conversation as active
- Parent SHOULD clear the message input area (automatic via conversation switch)
- Parent SHOULD persist the new conversation to storage
- Parent MAY discard any unsaved user input without confirmation

**Example**:
```javascript
// Component emits
emit('new-conversation')

// Parent handles
function handleNewConversation() {
  const { createConversation, saveToStorage } = useConversations()
  createConversation()  // Creates new conversation and sets as active
  saveToStorage()       // Persist to LocalStorage
}
```

**Error Handling**:
- If parent's `createConversation()` fails, parent SHOULD display error in StatusBar
- Component SHOULD NOT handle errors (parent responsibility)

**Debouncing**:
- Component implements 300ms guard to prevent multiple rapid emissions
- Parent does NOT need additional debouncing logic

---

## Visual Contract

### UI Elements

#### New Conversation Button

**Location**: Inside `.history-header` div, after the `<h2>Conversations</h2>` heading

**Visual Specifications**:
- **Label**: "New Conversation" or "+ New" (implementation choice)
- **Styling**:
  - Background: `var(--color-primary)`
  - Text color: `white`
  - Padding: `var(--spacing-sm) var(--spacing-md)`
  - Border radius: `4px`
  - Font size: `var(--font-size-sm)`
- **Hover state**: Background changes to `var(--color-primary-dark)`
- **Cursor**: `pointer`

**Accessibility**:
- MUST have `aria-label="Start new conversation"`
- MUST be keyboard accessible (native `<button>` element)
- MUST have visible focus indicator

**Responsive Behavior**:
- MUST remain visible at all screen sizes
- MAY use abbreviated text ("+ New") on narrow screens (optional)

---

## Behavioral Contracts

### Invariants

The following conditions MUST always hold:

1. **Button Always Visible**: The "New Conversation" button MUST always be rendered and clickable
2. **Event Emission**: Clicking the button MUST emit `new-conversation` event (except during debounce window)
3. **No Side Effects**: Component MUST NOT directly modify conversations state or LocalStorage
4. **Stateless**: Component MUST NOT maintain conversation creation state (guard flag is internal implementation detail)

### Preconditions

Before rendering:
- `conversations` prop (if provided) MUST be an array
- `activeConversationId` prop (if provided) MUST be a string or null
- All conversation objects MUST have `id`, `title`, `messages`, `createdAt`, `updatedAt` fields

### Postconditions

After button click:
- `new-conversation` event MUST be emitted exactly once (per actual click, accounting for debounce)
- Component state MUST remain unchanged (stateless)
- UI MUST not show any loading or disabled state (instant response)

---

## Performance Contract

### Response Time Requirements

| Action | Target | Maximum | Measurement Point |
|--------|--------|---------|-------------------|
| Button click to event emission | < 50ms | 100ms | `@click` handler to `emit()` call |
| Button hover state transition | < 50ms | 100ms | CSS transition duration |
| Button render time | < 10ms | 50ms | Vue component render cycle |

### Resource Constraints

- Button event handler MUST NOT block UI thread > 16ms
- Debounce timer MUST use native `setTimeout` (no heavy libraries)
- CSS transitions MUST use GPU-accelerated properties only

---

## Testing Contracts

### Unit Test Requirements

The following test scenarios MUST pass:

1. **Button Rendering**:
   - Button is rendered in the DOM
   - Button has correct label text
   - Button has correct ARIA attributes

2. **Event Emission**:
   - Clicking button emits `new-conversation` event
   - Event has no payload (undefined or void)

3. **Debouncing**:
   - Rapid clicks (< 300ms apart) only emit one event
   - Clicks > 300ms apart each emit separate events

4. **Styling**:
   - Button has correct CSS classes
   - Hover state applies correct styles

### Integration Test Requirements

1. **Event Flow**:
   - HistoryBar emits `new-conversation` → App receives event
   - App creates new conversation → HistoryBar receives new conversation in props
   - New conversation appears in history list

2. **State Synchronization**:
   - New conversation becomes active (highlighted)
   - Previous conversation remains in list
   - LocalStorage is updated

### E2E Test Requirements

1. **User Workflow**:
   - User clicks "New Conversation" button
   - Chat area clears
   - New conversation appears in history
   - Previous conversation is still accessible

2. **Edge Cases**:
   - Clicking button with unsaved message → message is discarded
   - Clicking button on empty conversation → new empty conversation created
   - Rapid button clicks → only one new conversation created

---

## Breaking Changes

### Version History

#### v1.0.0 (This Version)
- **Added**: `new-conversation` event emission
- **Added**: "New Conversation" button in header
- **Modified**: Component template (added button element)
- **No breaking changes**: Existing events and props unchanged

### Backward Compatibility

✅ **Fully backward compatible**

- Existing `select-conversation` event unchanged
- Existing props unchanged
- No removed functionality
- New event is additive (parent can ignore if not handled)

### Upgrade Path

If parent component doesn't handle `new-conversation`:
- No errors thrown
- Button still renders and is clickable
- Event is emitted but ignored (Vue behavior)
- Application continues to function normally

**Recommended upgrade**:
```javascript
// Add new event handler to App.vue
<HistoryBar
  :conversations="conversations"
  :active-conversation-id="activeConversationId"
  @select-conversation="handleSelectConversation"
  @new-conversation="handleNewConversation"  // Add this line
/>
```

---

## Error Handling Contract

### Component Error Handling

The component MUST:
- NOT throw errors for invalid props (Vue validation warnings only)
- NOT throw errors during event emission
- Gracefully handle missing `conversations` prop (default to empty array)
- Gracefully handle missing `activeConversationId` prop (no highlighting)

### Parent Error Handling

The parent component MUST:
- Handle errors from `createConversation()` (e.g., validation failures)
- Display user-friendly error messages if conversation creation fails
- NOT crash if HistoryBar emits unexpected events

---

## Accessibility Contract

### WCAG 2.1 Level AA Compliance

The component MUST meet:

1. **Keyboard Navigation**:
   - Button is focusable via Tab key
   - Button is activatable via Enter or Space key
   - Focus indicator is visible (outline or highlight)

2. **Screen Reader Support**:
   - Button has meaningful `aria-label`
   - Button role is implicit (`<button>` element)
   - Event emission does NOT cause unexpected screen reader announcements

3. **Visual Accessibility**:
   - Text contrast ratio ≥ 4.5:1 (normal text)
   - Button is visible in Windows High Contrast mode
   - Focus indicator has ≥ 3:1 contrast

---

## Example Usage

### Minimal Example

```vue
<template>
  <HistoryBar
    :conversations="conversations"
    :active-conversation-id="activeConversationId"
    @new-conversation="handleNewConversation"
  />
</template>

<script>
import { useConversations } from '@/state/useConversations'

export default {
  setup() {
    const { conversations, activeConversationId, createConversation, saveToStorage } = useConversations()

    function handleNewConversation() {
      createConversation()
      saveToStorage()
    }

    return {
      conversations,
      activeConversationId,
      handleNewConversation
    }
  }
}
</script>
```

### Full Example (with error handling)

```vue
<template>
  <HistoryBar
    :conversations="conversations"
    :active-conversation-id="activeConversationId"
    @select-conversation="handleSelectConversation"
    @new-conversation="handleNewConversation"
  />
</template>

<script>
import { useConversations } from '@/state/useConversations'
import { useAppState } from '@/state/useAppState'
import * as logger from '@/utils/logger'

export default {
  setup() {
    const { conversations, activeConversationId, createConversation, saveToStorage } = useConversations()
    const { setError } = useAppState()

    function handleNewConversation() {
      try {
        logger.info('Creating new conversation')
        createConversation()
        saveToStorage()
        logger.info('New conversation created successfully')
      } catch (error) {
        logger.error('Failed to create conversation', error)
        setError('Failed to create new conversation')
      }
    }

    function handleSelectConversation(conversationId) {
      logger.info('Conversation selected', { conversationId })
      // Implementation for P2 feature
    }

    return {
      conversations,
      activeConversationId,
      handleNewConversation,
      handleSelectConversation
    }
  }
}
</script>
```

---

## Contract Verification

### How to Verify Compliance

1. **Props Contract**: Run unit tests with various prop combinations
2. **Events Contract**: Run integration tests verifying event payloads
3. **Visual Contract**: Run E2E tests with visual regression checks
4. **Performance Contract**: Run performance profiling during tests
5. **Accessibility Contract**: Run automated accessibility tests (axe, pa11y)

### Contract Testing

Contract tests MUST verify:
- ✅ Button click emits correct event
- ✅ Event has no payload (void)
- ✅ Debouncing prevents duplicate emissions
- ✅ Parent can handle event successfully
- ✅ State synchronization works correctly

---

## Summary

**Contract Type**: Component Interface Contract (Frontend)
**Breaking Changes**: None (additive only)
**Version**: 1.0.0
**Compliance**: Follows Vue 3 best practices and Constitution Principle I (API-First Design)

This contract ensures:
- Clear interface for component consumers
- Testable and verifiable behavior
- Backward compatibility
- Accessibility compliance
- Performance guarantees
