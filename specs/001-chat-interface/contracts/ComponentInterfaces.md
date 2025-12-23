# Contract: Component Interfaces

**Framework**: Vue.js 3 (Composition API)
**Purpose**: Define props, events, and composable interfaces for all UI components
**Version**: 1.0.0

## Component Hierarchy

```
App
├── StatusBar
├── HistoryBar
│   └── ConversationItem (repeated)
├── ChatArea
│   └── MessageBubble (repeated)
└── InputArea
```

---

## Component: `App`

Root component that orchestrates all child components and manages application state.

### Props

None (root component)

### State (via Composables)

Uses:
- `useConversations()`: Manages conversation list and active conversation
- `useAppState()`: Manages UI state (status, processing flag)

### Events Emitted

None (root component)

### Responsibilities

- Initialize application on mount
- Load conversations from storage
- Coordinate state between child components
- Handle global error boundary

---

## Component: `StatusBar`

Displays application status and system messages.

### Props

```typescript
{
  status: string,          // Status message to display
  statusType: 'ready' | 'processing' | 'error'  // Status severity
}
```

**Validation**:
- `status`: Required, string, max 100 characters
- `statusType`: Required, one of: 'ready', 'processing', 'error'

### Events Emitted

None (display-only component)

### Visual Behavior

- **ready**: Green indicator, normal text
- **processing**: Yellow/blue indicator, italic text, optional spinner
- **error**: Red indicator, bold text

### Example Usage

```vue
<StatusBar
  status="Ready"
  statusType="ready"
/>

<StatusBar
  status="Processing message..."
  statusType="processing"
/>

<StatusBar
  status="Error: Message validation failed"
  statusType="error"
/>
```

---

## Component: `HistoryBar`

Displays list of past conversations with ability to select and create new conversations.

### Props

```typescript
{
  conversations: Conversation[],     // List of all conversations
  activeConversationId: string | null  // Currently selected conversation
}
```

**Validation**:
- `conversations`: Required, array (can be empty)
- `activeConversationId`: Optional, must match a conversation ID or be null

### Events Emitted

```typescript
// User clicked on a conversation
'conversation-selected': (conversationId: string) => void

// User clicked "New Conversation" button
'new-conversation': () => void
```

### Responsibilities

- Display conversations ordered by `updatedAt` (most recent first)
- Highlight active conversation
- Show conversation title (or preview of first message)
- Show conversation timestamp
- Provide "New Conversation" button at top

### Example Usage

```vue
<HistoryBar
  :conversations="conversations"
  :activeConversationId="activeId"
  @conversation-selected="handleSelectConversation"
  @new-conversation="handleNewConversation"
/>
```

---

## Component: `ConversationItem`

Single conversation entry in the history bar (child of HistoryBar).

### Props

```typescript
{
  conversation: Conversation,  // Conversation data
  isActive: boolean            // Whether this conversation is currently selected
}
```

**Validation**:
- `conversation`: Required, must conform to Conversation schema
- `isActive`: Required, boolean

### Events Emitted

```typescript
// User clicked on this conversation
'click': () => void
```

### Visual Behavior

- **Active**: Highlighted background, bold text
- **Inactive**: Normal background, normal text
- **Hover**: Slight highlight

### Display

- **Title**: `conversation.title` or preview of first message
- **Timestamp**: Relative time (e.g., "2 minutes ago", "Yesterday")
- **Preview**: First message text (truncated to 60 chars)

### Example Usage

```vue
<ConversationItem
  :conversation="conv"
  :isActive="conv.id === activeId"
  @click="handleClick"
/>
```

---

## Component: `ChatArea`

Displays messages for the active conversation.

### Props

```typescript
{
  messages: Message[],      // Messages to display (ordered chronologically)
  isProcessing: boolean     // Whether a message is being processed
}
```

**Validation**:
- `messages`: Required, array (can be empty)
- `isProcessing`: Required, boolean

### Events Emitted

None (display-only component)

### Responsibilities

- Render all messages in chronological order
- Auto-scroll to bottom when new message added
- Show loading indicator when `isProcessing=true`
- Display empty state when no messages

### Auto-Scroll Behavior

- On mount: Scroll to bottom
- On new message added: Scroll to bottom
- On user scroll up: Do NOT auto-scroll
- On user near bottom (<100px): Resume auto-scroll

### Example Usage

```vue
<ChatArea
  :messages="currentMessages"
  :isProcessing="isProcessing"
/>
```

---

## Component: `MessageBubble`

Single message display (child of ChatArea).

### Props

```typescript
{
  message: Message  // Message data to display
}
```

**Validation**:
- `message`: Required, must conform to Message schema

### Events Emitted

None (display-only component)

### Visual Behavior

**User Message**:
- Aligned right
- Blue background
- White text
- Timestamp below (light gray, small)

**System Message**:
- Aligned left
- Gray background
- Dark text
- Timestamp below (light gray, small)

**Status Indicator**:
- `pending`: Spinner icon
- `sent`: No indicator (default)
- `error`: Red exclamation icon

### Example Usage

```vue
<MessageBubble :message="message" />
```

---

## Component: `InputArea`

Text input and send button for composing messages.

### Props

```typescript
{
  isDisabled: boolean,    // Whether input is disabled (during processing)
  maxLength: number       // Maximum characters allowed (default: 10000)
}
```

**Validation**:
- `isDisabled`: Required, boolean
- `maxLength`: Optional, number (default 10000)

### Events Emitted

```typescript
// User clicked Send button or pressed Enter
'send-message': (text: string) => void
```

**Event Data**:
- `text`: Trimmed message text (guaranteed non-empty)

### Responsibilities

- Provide textarea for message input
- Provide Send button
- Disable input and button when `isDisabled=true`
- Validate input before emitting event:
  - Trim whitespace
  - Check not empty
  - Check length <= maxLength
- Clear input after successful send
- Handle Enter key to send (Shift+Enter for newline)
- Show character count when approaching limit (>9000 chars)

### Validation Behavior

- If empty (after trim): Disable Send button, show subtle hint
- If exceeds max length: Prevent typing, show error
- If valid: Enable Send button

### Example Usage

```vue
<InputArea
  :isDisabled="isProcessing"
  :maxLength="10000"
  @send-message="handleSendMessage"
/>
```

---

## Composables

### `useConversations()`

Manages conversation state and operations.

**Returns**:
```typescript
{
  conversations: Ref<Conversation[]>,
  activeConversationId: Ref<string | null>,
  activeConversation: ComputedRef<Conversation | null>,

  createConversation: () => void,
  selectConversation: (id: string) => void,
  addMessage: (conversationId: string, message: Message) => void,
  loadFromStorage: () => Promise<void>,
  saveToStorage: () => Promise<void>
}
```

**Methods**:

- `createConversation()`: Create new empty conversation, set as active
- `selectConversation(id)`: Change active conversation to specified ID
- `addMessage(conversationId, message)`: Add message to conversation, update timestamp
- `loadFromStorage()`: Load conversations from LocalStorage
- `saveToStorage()`: Save conversations to LocalStorage

**Validation**:
- Ensures activeConversationId always matches existing conversation or null
- Validates message structure before adding
- Handles storage errors gracefully

---

### `useMessages()`

Manages message operations for the active conversation.

**Returns**:
```typescript
{
  currentMessages: ComputedRef<Message[]>,

  sendUserMessage: (text: string) => Promise<void>,
  createLoopbackResponse: (originalText: string) => Message
}
```

**Methods**:

- `currentMessages`: Computed ref returning messages for active conversation
- `sendUserMessage(text)`: Create user message, add to conversation, trigger loopback
- `createLoopbackResponse(text)`: Create system message with same text

**Validation**:
- Validates message text (not empty, max length)
- Throws error if validation fails
- Updates message status based on operation result

---

### `useAppState()`

Manages global UI state.

**Returns**:
```typescript
{
  status: Ref<string>,
  statusType: Ref<'ready' | 'processing' | 'error'>,
  isProcessing: Ref<boolean>,

  setReady: () => void,
  setProcessing: (message?: string) => void,
  setError: (message: string) => void
}
```

**Methods**:

- `setReady()`: Set status to "Ready", type to 'ready', isProcessing to false
- `setProcessing(message)`: Set status to message (default "Processing..."), type to 'processing', isProcessing to true
- `setError(message)`: Set status to message, type to 'error', isProcessing to false (auto-clear after 5s)

---

## Contract Tests

### Component Contract Tests

Each component MUST have tests verifying:

1. **Props Validation**:
   - Component renders with valid props
   - Component rejects invalid props (type mismatch)
   - Required props throw error if missing

2. **Events**:
   - Events emit with correct payload
   - Events emit at correct times (e.g., on button click)

3. **Visual States**:
   - Component renders correctly for each state (active/inactive, empty/full, etc.)

4. **Accessibility**:
   - ARIA labels present
   - Keyboard navigation works
   - Focus management correct

### Composable Contract Tests

Each composable MUST have tests verifying:

1. **Initial State**: Returns correct default values
2. **State Updates**: Methods update state correctly
3. **Computed Values**: Derived values compute correctly
4. **Side Effects**: Storage operations execute correctly
5. **Error Handling**: Errors handled gracefully

---

## Implementation Notes

- All components use `<script setup>` syntax (Vue 3 Composition API)
- Props use `defineProps()` with type validation
- Events use `defineEmits()` with type annotations
- Composables follow `use*` naming convention
- All reactive state uses `ref()` or `computed()`

---

## Versioning

**Current Version**: 1.0.0

**Breaking Changes** (require MAJOR version bump):
- Changing prop types
- Removing props or events
- Changing event payload structure

**Non-Breaking Changes** (allow MINOR version bump):
- Adding optional props
- Adding new events
- Extending functionality
