# Quickstart Guide: Chat Error Display

**Feature**: 005-chat-error-display
**Audience**: Developers implementing this feature
**Prerequisites**: Familiarity with Vue 3 Composition API, Vitest, and the existing codebase

## Overview

This guide helps you implement error display in the chat interface following Test-Driven Development (TDD). You'll add three capabilities:

1. **P1 (Slice 1)**: Display client-side errors in chat with visual distinction
2. **P2 (Slice 2)**: Display server-side errors in chat
3. **P3 (Slice 3)**: Expandable error details with sensitive data redaction

Each slice is independently testable and deliverable.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Chat Interface                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ChatArea.vue                                        │  │
│  │  ┌─────────────────────────────────────────────┐    │  │
│  │  │  MessageBubble.vue                          │    │  │
│  │  │                                              │    │  │
│  │  │  [User message]                             │    │  │
│  │  │  10:30 AM                                    │    │  │
│  │  │                                              │    │  │
│  │  │  ┌──────────────────────────────────────┐   │    │  │
│  │  │  │ ⚠️ Message failed to send  [Details]│   │    │  │
│  │  │  │                                      │   │    │  │
│  │  │  │ ┌─ Error Details ──────────────┐    │   │    │  │
│  │  │  │ │ Type: Network Error          │    │   │    │  │
│  │  │  │ │ Timestamp: 10:30:05 AM       │    │   │    │  │
│  │  │  │ │ Cannot connect to server     │    │   │    │  │
│  │  │  │ └──────────────────────────────┘    │   │    │  │
│  │  │  └──────────────────────────────────────┘   │    │  │
│  │  └─────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Development Setup

### 1. Verify Current Codebase

```bash
# Ensure you're on the feature branch
git branch --show-current  # Should show: 005-chat-error-display

# Check existing project structure
ls -la frontend/src/components/ChatArea/
# Should see: ChatArea.vue, MessageBubble.vue

# Run existing tests to ensure baseline
cd frontend
npm test
# All tests should pass before starting
```

### 2. Create New Files (Skeleton Only)

```bash
# Create utilities
touch frontend/src/utils/sensitiveDataRedactor.js
touch frontend/src/composables/useCollapsible.js

# Create test files
touch frontend/tests/unit/sensitiveDataRedactor.test.js
touch frontend/tests/unit/useCollapsible.test.js
touch frontend/tests/integration/errorDisplay.test.js
```

## Implementation Guide

### Slice 1 (P1): Basic Error Display

**Goal**: Display client-side errors in chat with visual distinction

#### Step 1: Write Failing Tests

**File**: `frontend/tests/unit/MessageBubble.test.js`

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MessageBubble from '@/components/ChatArea/MessageBubble.vue'

describe('MessageBubble - Error Display', () => {
  it('should display error section when message status is error', () => {
    const errorMessage = {
      id: 'msg-1',
      text: 'Failed message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'error',
      errorMessage: 'Message failed to send',
      errorType: 'Network Error'
    }

    const wrapper = mount(MessageBubble, {
      props: { message: errorMessage }
    })

    expect(wrapper.find('.error-section').exists()).toBe(true)
    expect(wrapper.find('.error-message').text()).toBe('Message failed to send')
  })

  it('should apply error styling to error messages', () => {
    const errorMessage = {
      id: 'msg-1',
      text: 'Failed message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'error',
      errorMessage: 'Network error'
    }

    const wrapper = mount(MessageBubble, {
      props: { message: errorMessage }
    })

    expect(wrapper.classes()).toContain('message-error')
  })

  it('should not display error section for non-error messages', () => {
    const normalMessage = {
      id: 'msg-1',
      text: 'Normal message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'sent'
    }

    const wrapper = mount(MessageBubble, {
      props: { message: normalMessage }
    })

    expect(wrapper.find('.error-section').exists()).toBe(false)
  })
})
```

**Run tests** (they should FAIL):
```bash
npm test MessageBubble.test.js
# Expected: Tests fail because error section not implemented
```

#### Step 2: Implement Minimum Code to Pass

**File**: `frontend/src/components/ChatArea/MessageBubble.vue`

```vue
<script>
import { computed } from 'vue'

export default {
  name: 'MessageBubble',
  props: {
    message: {
      type: Object,
      required: true,
      validator: msg => {
        return (
          msg.id &&
          msg.text &&
          ['user', 'system'].includes(msg.sender) &&
          msg.timestamp &&
          ['pending', 'sent', 'error'].includes(msg.status)
        )
      },
    },
  },
  setup(props) {
    const messageClass = computed(() => ({
      'message-user': props.message.sender === 'user',
      'message-system': props.message.sender === 'system',
      'message-pending': props.message.status === 'pending',
      'message-error': props.message.status === 'error',
    }))

    const formattedTime = computed(() => {
      const date = new Date(props.message.timestamp)
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
      })
    })

    const hasError = computed(() => {
      return props.message.status === 'error' && props.message.errorMessage
    })

    return {
      messageClass,
      formattedTime,
      hasError
    }
  },
}
</script>

<template>
  <div
    class="message-bubble"
    :class="messageClass"
    :data-sender="message.sender"
    :data-message-id="message.id"
  >
    <div class="message-text">
      {{ message.text }}
    </div>

    <!-- NEW: Error Section -->
    <div v-if="hasError" class="error-section">
      <div class="error-summary">
        <svg class="error-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path fill="currentColor" d="M12 2L1 21h22L12 2zm0 3.5L19.5 19h-15L12 5.5zM11 10v4h2v-4h-2zm0 6v2h2v-2h-2z"/>
        </svg>
        <span class="error-message">{{ message.errorMessage }}</span>
      </div>
    </div>

    <div class="message-timestamp">
      {{ formattedTime }}
    </div>
  </div>
</template>

<style scoped>
/* Existing styles... */

/* NEW: Error Section Styles */
.error-section {
  margin-top: var(--spacing-sm);
  border-top: 1px solid rgba(220, 38, 38, 0.2);
  padding-top: var(--spacing-sm);
}

.error-summary {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: #DC2626;
  font-weight: 600;
  font-size: 0.875rem;
}

.error-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.error-message {
  flex: 1;
}
</style>
```

**Run tests** (they should PASS):
```bash
npm test MessageBubble.test.js
# Expected: All tests pass
```

#### Step 3: Update useMessages to Create Error Messages

**File**: `frontend/tests/unit/useMessages.test.js` (add new test)

```javascript
it('should create error message when API call fails', async () => {
  // Mock API client to throw error
  vi.mocked(apiClient.sendMessage).mockRejectedValue(
    new apiClient.ApiError('Cannot connect to server', null, {})
  )

  const { sendUserMessage } = useMessages()
  await sendUserMessage('Test message')

  const messages = useConversations().getActiveConversation().value.messages
  const errorMessage = messages[messages.length - 1]

  expect(errorMessage.status).toBe('error')
  expect(errorMessage.errorMessage).toBe('Cannot connect to server')
  expect(errorMessage.errorType).toBe('Network Error')
})
```

**Implement in** `frontend/src/state/useMessages.js`:

```javascript
// Extend sendUserMessage to add error details
const sendUserMessage = async (messageText) => {
  // ... existing validation ...

  const messageId = generateId()
  const userMessage = {
    id: messageId,
    text: messageText,
    sender: 'user',
    timestamp: new Date().toISOString(),
    status: 'pending',
  }

  addMessageToConversation(activeConversationId.value, userMessage)

  try {
    const response = await apiClient.sendMessage(messageText)
    // Update to 'sent' on success
    updateMessageStatus(messageId, 'sent')
    // ... handle system response ...
  } catch (error) {
    logger.error('API error sending message', error)

    // NEW: Populate error fields
    updateMessageWithError(messageId, {
      status: 'error',
      errorMessage: error.message || 'Message failed to send',
      errorType: categorizeError(error),
      errorCode: error.statusCode || null,
      errorDetails: error.details ? JSON.stringify(error.details) : error.message,
      errorTimestamp: new Date().toISOString()
    })

    setError(error.message || 'Cannot connect to server')
  }
}

// NEW: Helper to update message with error details
const updateMessageWithError = (messageId, errorData) => {
  const activeConversation = getActiveConversation()
  if (!activeConversation.value) return

  const messageIndex = activeConversation.value.messages.findIndex(
    m => m.id === messageId
  )
  if (messageIndex === -1) return

  Object.assign(activeConversation.value.messages[messageIndex], errorData)
  saveConversations()
}

// NEW: Helper to categorize errors
const categorizeError = (error) => {
  if (!error.statusCode) return 'Network Error'
  if (error.statusCode >= 500) return 'Server Error'
  if (error.statusCode === 400 || error.statusCode === 422) return 'Validation Error'
  if (error.statusCode >= 400) return 'Client Error'
  return 'Unknown Error'
}
```

**Run tests** (they should PASS):
```bash
npm test useMessages.test.js
```

#### Step 4: Manual Testing

```bash
# Start backend
cd backend && python main.py

# Start frontend
cd frontend && npm run dev

# Test scenarios:
# 1. Stop backend → send message → should see "Cannot connect to server" error
# 2. Start backend → send empty message → should see validation error
# 3. Send valid message → should work normally
```

**Deliverable**: ✅ Slice 1 complete - Client errors display in chat

---

### Slice 2 (P2): Server Error Integration

**Goal**: Display server-side errors (400, 422, 500) in chat

#### Step 1: Write Failing Tests

**File**: `frontend/tests/integration/errorDisplay.test.js`

```javascript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useMessages } from '@/state/useMessages'
import { useConversations } from '@/state/useConversations'
import * as apiClient from '@/services/apiClient'

vi.mock('@/services/apiClient')

describe('Error Display Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('should display 422 validation error in chat', async () => {
    const validationError = new apiClient.ApiError(
      'Message validation failed',
      422,
      { field: 'text', issue: 'String should have at least 1 character' }
    )
    vi.mocked(apiClient.sendMessage).mockRejectedValue(validationError)

    const { sendUserMessage } = useMessages()
    await sendUserMessage('test')

    const messages = useConversations().getActiveConversation().value.messages
    const errorMessage = messages.find(m => m.status === 'error')

    expect(errorMessage).toBeDefined()
    expect(errorMessage.errorType).toBe('Validation Error')
    expect(errorMessage.errorCode).toBe(422)
    expect(errorMessage.errorMessage).toBe('Message validation failed')
  })

  it('should display 500 server error in chat', async () => {
    const serverError = new apiClient.ApiError(
      'Server error occurred',
      500,
      { message: 'Internal server error' }
    )
    vi.mocked(apiClient.sendMessage).mockRejectedValue(serverError)

    const { sendUserMessage } = useMessages()
    await sendUserMessage('test')

    const messages = useConversations().getActiveConversation().value.messages
    const errorMessage = messages.find(m => m.status === 'error')

    expect(errorMessage.errorType).toBe('Server Error')
    expect(errorMessage.errorCode).toBe(500)
  })
})
```

**Run tests** (they should PASS if Slice 1 implemented correctly):
```bash
npm test errorDisplay.test.js
```

#### Step 2: Enhance apiClient Error Handling

**File**: `frontend/src/services/apiClient.js`

```javascript
// Ensure ApiError includes all necessary fields
export class ApiError extends Error {
  constructor(message, statusCode = null, details = null) {
    super(message)
    this.name = 'ApiError'
    this.statusCode = statusCode
    this.details = details
  }
}

export async function sendMessage(messageText) {
  try {
    const response = await fetch(`${API_BASE_URL}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: messageText }),
      signal: AbortSignal.timeout(10000),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))

      // Extract error message and details from response
      const errorMessage = errorData.error || `HTTP ${response.status}`
      const errorDetails = errorData.detail || errorData

      throw new ApiError(errorMessage, response.status, errorDetails)
    }

    return await response.json()
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }

    // Network errors, timeouts, etc.
    throw new ApiError(
      error.name === 'TimeoutError'
        ? 'Request timed out. Please try again.'
        : 'Cannot connect to server',
      null,
      { originalError: error.message }
    )
  }
}
```

#### Step 3: Manual Testing

```bash
# Test with backend running:

# 1. Send empty message (should trigger 422 validation error)
# 2. Modify backend to throw 500 error
# 3. Verify errors display in chat with correct type and code
```

**Deliverable**: ✅ Slice 2 complete - Server errors display in chat

---

### Slice 3 (P3): Expandable Details + Redaction

**Goal**: Add expand/collapse UI with sensitive data redaction

#### Step 1: Implement Sensitive Data Redactor (TDD)

**File**: `frontend/tests/unit/sensitiveDataRedactor.test.js`

```javascript
import { describe, it, expect } from 'vitest'
import {
  redactSensitiveData,
  containsSensitiveData,
  detectSensitivePatterns
} from '@/utils/sensitiveDataRedactor'

describe('sensitiveDataRedactor', () => {
  it('should redact AWS API keys', () => {
    const text = 'Error: API key AKIAIOSFODNN7EXAMPLE failed'
    const redacted = redactSensitiveData(text)

    expect(redacted).not.toContain('AKIAIOSFODNN7EXAMPLE')
    expect(redacted).toContain('***REDACTED_AWS_KEY***')
  })

  it('should redact JWT tokens', () => {
    const text = 'Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U'
    const redacted = redactSensitiveData(text)

    expect(redacted).toContain('***REDACTED_JWT***')
  })

  it('should detect if text contains sensitive data', () => {
    const textWithSecret = 'API key: AKIAIOSFODNN7EXAMPLE'
    const textWithoutSecret = 'Normal error message'

    expect(containsSensitiveData(textWithSecret)).toBe(true)
    expect(containsSensitiveData(textWithoutSecret)).toBe(false)
  })

  it('should identify which patterns were detected', () => {
    const text = 'AWS key: AKIAIOSFODNN7EXAMPLE, JWT: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
    const patterns = detectSensitivePatterns(text)

    expect(patterns).toContain('AWS API Key')
    expect(patterns).toContain('JWT Token')
  })
})
```

**Implement**: See `research.md` for full implementation of `sensitiveDataRedactor.js`

```javascript
// frontend/src/utils/sensitiveDataRedactor.js
export const SENSITIVE_PATTERNS = [
  {
    name: 'AWS API Key',
    pattern: /AKIA[0-9A-Z]{16}/g,
    replacement: '***REDACTED_AWS_KEY***'
  },
  // ... add more patterns from research.md
]

export function redactSensitiveData(text, showPatternNames = false) {
  if (!text || typeof text !== 'string') return text

  let redactedText = text
  for (const { name, pattern, replacement } of SENSITIVE_PATTERNS) {
    const finalReplacement = showPatternNames
      ? `[${name.toUpperCase()}_REDACTED]`
      : replacement
    redactedText = redactedText.replace(pattern, finalReplacement)
  }

  return redactedText
}

export function containsSensitiveData(text) {
  if (!text || typeof text !== 'string') return false
  return SENSITIVE_PATTERNS.some(({ pattern }) => {
    pattern.lastIndex = 0
    return pattern.test(text)
  })
}

export function detectSensitivePatterns(text) {
  if (!text || typeof text !== 'string') return []
  return SENSITIVE_PATTERNS
    .filter(({ pattern }) => {
      pattern.lastIndex = 0
      return pattern.test(text)
    })
    .map(({ name }) => name)
}
```

#### Step 2: Implement useCollapsible Composable (TDD)

**File**: `frontend/tests/unit/useCollapsible.test.js`

```javascript
import { describe, it, expect } from 'vitest'
import { useCollapsible } from '@/composables/useCollapsible'

describe('useCollapsible', () => {
  it('should initialize with collapsed state by default', () => {
    const { isExpanded } = useCollapsible()
    expect(isExpanded.value).toBe(false)
  })

  it('should initialize with expanded state when specified', () => {
    const { isExpanded } = useCollapsible(true)
    expect(isExpanded.value).toBe(true)
  })

  it('should toggle state', () => {
    const { isExpanded, toggle } = useCollapsible()

    expect(isExpanded.value).toBe(false)
    toggle()
    expect(isExpanded.value).toBe(true)
    toggle()
    expect(isExpanded.value).toBe(false)
  })

  it('should provide correct ARIA attributes', () => {
    const { isExpanded, triggerAttrs, contentAttrs } = useCollapsible()

    expect(triggerAttrs.value['aria-expanded']).toBe(false)
    expect(triggerAttrs.value['type']).toBe('button')
    expect(contentAttrs.value['role']).toBe('region')
    expect(contentAttrs.value['aria-hidden']).toBe(true)
  })
})
```

**Implement**: See `research.md` for full implementation

#### Step 3: Add Expand/Collapse to MessageBubble

**Update**: `frontend/src/components/ChatArea/MessageBubble.vue`

```vue
<script>
import { computed } from 'vue'
import { useCollapsible } from '@/composables/useCollapsible'
import { redactSensitiveData } from '@/utils/sensitiveDataRedactor'

export default {
  // ... existing props ...

  setup(props) {
    // ... existing computed properties ...

    const errorCollapsible = useCollapsible(false)

    const redactedErrorDetails = computed(() => {
      if (!props.message.errorDetails) return ''
      return redactSensitiveData(props.message.errorDetails)
    })

    const hasErrorDetails = computed(() => {
      return props.message.status === 'error' && props.message.errorDetails
    })

    return {
      messageClass,
      formattedTime,
      hasError,
      errorCollapsible,
      redactedErrorDetails,
      hasErrorDetails
    }
  }
}
</script>

<template>
  <!-- ... existing template ... -->

  <div v-if="hasError" class="error-section">
    <div class="error-summary">
      <svg class="error-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path fill="currentColor" d="M12 2L1 21h22L12 2zm0 3.5L19.5 19h-15L12 5.5zM11 10v4h2v-4h-2zm0 6v2h2v-2h-2z"/>
      </svg>
      <span class="error-message">{{ message.errorMessage }}</span>

      <!-- NEW: Details toggle button -->
      <button
        v-if="hasErrorDetails"
        v-bind="errorCollapsible.triggerAttrs.value"
        class="error-toggle"
        @click="errorCollapsible.toggle"
      >
        {{ errorCollapsible.isExpanded.value ? 'Hide' : 'Details' }}
      </button>
    </div>

    <!-- NEW: Expandable error details -->
    <transition name="expand">
      <div
        v-if="errorCollapsible.isExpanded.value && hasErrorDetails"
        v-bind="errorCollapsible.contentAttrs.value"
        class="error-details"
      >
        <div class="error-details-content">
          <p v-if="message.errorType"><strong>Type:</strong> {{ message.errorType }}</p>
          <p v-if="message.errorCode"><strong>Code:</strong> {{ message.errorCode }}</p>
          <pre class="error-stack">{{ redactedErrorDetails }}</pre>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* ... existing styles ... */

/* NEW: Expand/collapse styles (see research.md for complete CSS) */
.error-toggle {
  background: transparent;
  border: 1px solid #DC2626;
  color: #DC2626;
  padding: 2px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.error-toggle:hover {
  background: #DC2626;
  color: white;
}

.error-details {
  margin-top: var(--spacing-xs);
  background: rgba(220, 38, 38, 0.05);
  border-left: 3px solid #DC2626;
  padding: var(--spacing-sm);
  border-radius: 4px;
}

/* Transition animation */
.expand-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.expand-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 1, 1);
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 300px;
  opacity: 1;
}
</style>
```

**Deliverable**: ✅ Slice 3 complete - Expandable error details with redaction

---

## Testing Checklist

### Unit Tests
- [ ] MessageBubble renders error section
- [ ] MessageBubble applies error styling
- [ ] useMessages creates error messages on API failure
- [ ] sensitiveDataRedactor redacts all pattern types
- [ ] useCollapsible manages state correctly

### Integration Tests
- [ ] Full error flow from API error to chat display
- [ ] Different error types (network, validation, server) display correctly
- [ ] Expand/collapse works with keyboard navigation

### E2E Tests (Playwright)
- [ ] User sees error when backend is down
- [ ] User sees validation error for empty message
- [ ] User can expand error details
- [ ] Sensitive data is redacted by default

### Accessibility Tests
- [ ] Screen reader announces errors
- [ ] Keyboard navigation works (Enter/Space on toggle)
- [ ] Focus indicators visible
- [ ] ARIA attributes correct

## Common Issues & Solutions

### Issue: Tests fail with "Cannot find module"
**Solution**: Ensure path aliases in `vite.config.js`:
```javascript
resolve: {
  alias: {
    '@': fileURLToPath(new URL('./src', import.meta.url))
  }
}
```

### Issue: LocalStorage not persisting error messages
**Solution**: Ensure `saveConversations()` called after updating message with error

### Issue: Redaction not working
**Solution**: Check regex patterns have global flag `/g` and reset `lastIndex` before use

### Issue: Animation janky
**Solution**: Ensure `overflow: hidden` during transition

## Next Steps

After completing all three slices:

1. **Run full test suite**: `npm test`
2. **Manual testing**: Test all error scenarios
3. **Accessibility audit**: Use axe DevTools
4. **Update architecture.md**: Document error display components
5. **Create PR**: Include test results and screenshots

## Resources

- **Research**: See `research.md` for detailed patterns and examples
- **Data Model**: See `data-model.md` for schema definitions
- **Constitution**: See `.specify/memory/constitution.md` for TDD requirements
- **Existing Code**: Review `frontend/src/components/ChatArea/MessageBubble.vue`
