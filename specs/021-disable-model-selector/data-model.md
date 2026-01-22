# Data Model: Disable Model Selector After Conversation Starts

**Feature**: 021-disable-model-selector
**Date**: 2026-01-22

## Overview

This feature does not introduce new data entities. It leverages existing data structures to derive model selector state. This document describes the relevant existing data models and how they are used.

## Existing Entities (No Changes Required)

### Conversation

**Location**: `backend/src/schemas.py` (Conversation class)

```
Conversation
├── id: string              # Unique identifier (conv-...)
├── title: string           # Display title
├── createdAt: string       # ISO-8601 timestamp
├── updatedAt: string       # ISO-8601 timestamp
└── messages: Message[]     # Array of conversation messages
```

**Usage for Feature 021**:
- `messages.length` determines if selector should be disabled (> 0 = disabled)
- First system message's `model` field provides the conversation's model

### ConversationMessage

**Location**: `backend/src/schemas.py` (ConversationMessage class)

```
ConversationMessage
├── id: string                              # Unique identifier (msg-...)
├── text: string                            # Message content
├── sender: 'user' | 'system'               # Message origin
├── timestamp: string                       # ISO-8601 timestamp
├── status: 'pending' | 'sent' | 'error'    # Delivery status
├── model: string | null                    # Model that generated response (system messages)
├── errorMessage: string | null             # Error details if status='error'
├── errorType: string | null
└── errorCode: number | null
```

**Usage for Feature 021**:
- `model` field on system messages stores which model generated the response
- First system message with non-null `model` determines conversation's model

### Model

**Location**: `backend/src/config/models.py` (ModelConfig class)

```
ModelConfig
├── id: string                                      # Unique identifier (e.g., 'gpt-4')
├── name: string                                    # Display name (e.g., 'GPT-4')
├── description: string                             # Model description
├── provider: 'openai' | 'anthropic' | 'ollama'     # Provider identifier
└── default: boolean                                # Is this the default model?
```

**Usage for Feature 021**:
- `id` is compared against conversation's model to check availability
- `default` identifies fallback model for legacy conversations

## Frontend State (Minor Additions)

### useModels Composable

**Location**: `frontend/src/state/useModels.js`

**Existing State**:
```javascript
{
  availableModels: Model[],        // From GET /api/v1/models
  selectedModelId: string | null,  // Currently selected model
  isLoading: boolean,              // Fetch in progress
  error: string | null             // Error message
}
```

**Modification Required**:
- `setSelectedModel(modelId, persist = true)` - Add optional `persist` parameter
  - When `persist = true` (default): Save to SettingsStorage
  - When `persist = false`: Update state only (for conversation model restoration)

### App Component Computed Properties

**Location**: `frontend/src/components/App/App.vue`

**New Computed Properties**:
```javascript
// Whether model selector should be disabled
const isModelSelectorDisabled = computed(() =>
  activeConversation.value?.messages?.length > 0
)

// Get model ID from conversation's first system message
const conversationModelId = computed(() => {
  if (!activeConversation.value?.messages?.length) return null
  const systemMsg = activeConversation.value.messages.find(
    m => m.sender === 'system' && m.model
  )
  return systemMsg?.model || null
})
```

## Data Flow

### New Conversation Flow

```
User clicks "New Conversation"
    ↓
createConversation() called
    ↓
activeConversation.messages = []
    ↓
isModelSelectorDisabled = false (messages.length === 0)
    ↓
ModelSelector ENABLED
    ↓
User can select model
```

### First Message Flow

```
User sends first message
    ↓
sendUserMessage() → API call
    ↓
System response received with model field
    ↓
Message added to conversation
    ↓
activeConversation.messages.length > 0
    ↓
isModelSelectorDisabled = true
    ↓
ModelSelector DISABLED
```

### Load Previous Conversation Flow

```
User clicks conversation in list
    ↓
setActiveConversation(id)
    ↓
activeConversation loaded with messages
    ↓
conversationModelId computed from first system message
    ↓
setSelectedModel(conversationModelId, persist=false)
    ↓
isModelSelectorDisabled = true (has messages)
    ↓
ModelSelector shows conversation's model, DISABLED
```

## Validation Rules

| Rule | Description | Implementation |
|------|-------------|----------------|
| Model selector enabled | Only when messages.length === 0 | Computed property check |
| Model displayed | Must match conversation's model | Derive from first system message |
| Legacy fallback | Use default model if no model field | Check for null, use getDefaultModel() |
| Unavailable model | Display model ID with indicator | Check against availableModels list |

## No Schema Changes Required

This feature operates entirely on existing data structures:
- ✅ Conversation schema unchanged
- ✅ Message schema unchanged
- ✅ Model schema unchanged
- ✅ API contracts unchanged
