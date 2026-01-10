# Data Model: LLM Backend Integration

**Feature**: 005-llm-integration
**Created**: 2025-12-30
**Status**: Design Phase

## Overview

This document defines the data entities, relationships, validation rules, and state transitions for the LLM backend integration feature. The model supports streaming AI conversations with multiple LLM providers, conversation context management, and model selection persistence.

## Entities

### 1. Message

Represents a single message in a conversation (user input or AI response).

**Fields**:
- `id`: string, required, pattern: `^msg-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`
  - Unique identifier for the message
  - Format: "msg-" prefix + UUID v4
  - Generated client-side for user messages, server-side for AI responses

- `text`: string, required, 1-50,000 characters
  - Message content (user input or AI response)
  - User messages: 1-10,000 chars (enforced by existing FR from feature 003)
  - AI responses: 1-50,000 chars (allow longer AI responses)
  - Empty/whitespace-only messages rejected

- `sender`: enum, required, values: `"user"` | `"assistant"` | `"system"`
  - Message sender type
  - `"user"`: Human user input
  - `"assistant"`: AI-generated response
  - `"system"`: System messages (errors, interruptions, status updates)

- `timestamp`: string, required, ISO-8601 format
  - When the message was created
  - Format: `YYYY-MM-DDTHH:mm:ss.sssZ` (UTC)
  - Generated at creation time

- `status`: enum, required, values: `"pending"` | `"streaming"` | `"completed"` | `"error"` | `"interrupted"`
  - Message lifecycle state
  - `"pending"`: User message waiting to be sent
  - `"streaming"`: AI response being streamed
  - `"completed"`: Message fully sent/received
  - `"error"`: Message failed to send/receive
  - `"interrupted"`: Streaming interrupted by user

- `model`: string, optional, enum values: `"gpt-5"` | `"gpt-5-codex"`
  - LLM model that generated this response (AI messages only)
  - null for user/system messages
  - Used for display and audit purposes

- `error`: object, optional
  - Error details if status is "error"
  - Structure: `{ code: string, message: string, details?: any }`
  - Only present when status = "error"

**Validation Rules**:
1. `id` must match UUID pattern with "msg-" prefix
2. `text` must not be empty or whitespace-only
3. `text` length: 1-10,000 for user, 1-50,000 for assistant/system
4. `sender` must be one of the enum values
5. `timestamp` must be valid ISO-8601 datetime
6. `status` must be one of the enum values
7. `model` required if sender = "assistant", null otherwise
8. `error` required if status = "error", null otherwise

**State Transitions**:
```
User Message Lifecycle:
  pending → completed (success)
  pending → error (send failed)

AI Message Lifecycle:
  streaming → completed (full response received)
  streaming → interrupted (user clicked stop)
  streaming → error (LLM API error or network failure)

System Message Lifecycle:
  completed (no transitions - terminal state)
```

---

### 2. Conversation

Represents a chat session with message history and context.

**Fields**:
- `id`: string, required, pattern: `^conv-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`
  - Unique identifier for the conversation
  - Format: "conv-" prefix + UUID v4
  - Generated client-side when conversation created

- `title`: string, required, 1-100 characters
  - Human-readable conversation title
  - Default: "New Conversation" or first user message preview
  - User can edit

- `createdAt`: string, required, ISO-8601 format
  - When the conversation was created
  - Format: `YYYY-MM-DDTHH:mm:ss.sssZ` (UTC)

- `messages`: array of Message objects, required
  - Ordered list of messages in chronological order
  - Minimum: 0 messages (new conversation)
  - Maximum: No hard limit (handled by LLM context window limits)
  - Oldest messages first, newest last

- `selectedModel`: string, optional, enum values: `"gpt-5"` | `"gpt-5-codex"`
  - LLM model selected for this conversation
  - Defaults to user's global model preference
  - Can be overridden per conversation (future enhancement)

**Validation Rules**:
1. `id` must match UUID pattern with "conv-" prefix
2. `title` must not be empty or whitespace-only
3. `title` length: 1-100 characters
4. `createdAt` must be valid ISO-8601 datetime
5. `messages` must be an array (can be empty)
6. Each message in `messages` must validate per Message entity rules
7. Messages must be ordered by timestamp (ascending)
8. `selectedModel` must be one of the enum values if present

**Relationships**:
- **Has Many Messages**: One conversation contains many messages
- **Belongs To User**: Implicit (browser-local data, single-user context)

---

### 3. ModelSelection

Represents the user's global LLM model preference.

**Fields**:
- `selectedModel`: string, required, enum values: `"gpt-5"` | `"gpt-5-codex"`
  - Currently selected LLM model
  - Persisted in browser LocalStorage
  - Default: `"gpt-5"`

- `lastUpdated`: string, required, ISO-8601 format
  - When the model selection was last changed
  - Used for debugging and audit purposes

**Validation Rules**:
1. `selectedModel` must be one of the enum values
2. `lastUpdated` must be valid ISO-8601 datetime

**Persistence**:
- Stored in browser LocalStorage
- Survives browser restarts (FR-005)
- Shared across all conversations (global setting)

---

### 4. StreamingState (Frontend-only, transient)

Represents the current state of an active streaming response.

**Fields**:
- `isStreaming`: boolean, required
  - Whether a response is currently being streamed

- `messageId`: string, optional
  - ID of the message being streamed
  - Pattern: `^msg-[uuid]$`
  - Present only when isStreaming = true

- `partialText`: string, optional
  - Accumulated text received so far during streaming
  - Updated progressively as chunks arrive
  - Becomes final message text when stream completes

- `controller`: AbortController, optional
  - Controller for canceling the stream
  - Used to implement Stop button functionality
  - Present only when isStreaming = true

**Validation Rules**:
1. If `isStreaming` = true, `messageId`, `partialText`, and `controller` must be present
2. If `isStreaming` = false, `messageId`, `partialText`, and `controller` must be null

**State Transitions**:
```
Streaming Lifecycle:
  idle (isStreaming: false)
    → active (isStreaming: true, partialText accumulates)
    → completed (isStreaming: false, partialText → message.text)

  OR

  idle → active → interrupted (user clicks stop, isStreaming: false, partial text preserved)

  OR

  idle → active → error (stream fails, isStreaming: false, error message displayed)
```

---

## Storage Schema Evolution

### Current Schema (v1.0.0)

**LocalStorage Key**: `chatInterface:v1:data`

```json
{
  "version": "1.0.0",
  "conversations": [
    {
      "id": "conv-<uuid>",
      "title": "string",
      "createdAt": "ISO-8601",
      "messages": [
        {
          "id": "msg-<uuid>",
          "text": "string",
          "sender": "user" | "system",
          "timestamp": "ISO-8601",
          "status": "pending" | "sent"
        }
      ]
    }
  ],
  "activeConversationId": "string | null"
}
```

### Target Schema (v2.0.0) - Feature 005

**LocalStorage Key**: `chatInterface:v2:data`

```json
{
  "version": "2.0.0",
  "conversations": [
    {
      "id": "conv-<uuid>",
      "title": "string",
      "createdAt": "ISO-8601",
      "messages": [
        {
          "id": "msg-<uuid>",
          "text": "string",
          "sender": "user" | "assistant" | "system",
          "timestamp": "ISO-8601",
          "status": "pending" | "streaming" | "completed" | "error" | "interrupted",
          "model": "gpt-5" | "gpt-5-codex" | null,
          "error": { "code": "string", "message": "string", "details": "any" } | null
        }
      ],
      "selectedModel": "gpt-5" | "gpt-5-codex" | null
    }
  ],
  "activeConversationId": "string | null",
  "modelSelection": {
    "selectedModel": "gpt-5" | "gpt-5-codex",
    "lastUpdated": "ISO-8601"
  }
}
```

**Migration Strategy** (v1.0.0 → v2.0.0):
1. Read existing `v1:data` from LocalStorage
2. Transform messages:
   - Map `sender: "system"` → `sender: "assistant"` (for AI responses)
   - Map `status: "sent"` → `status: "completed"`
   - Add `model: null` to all messages
   - Add `error: null` to all messages
3. Add `selectedModel: null` to each conversation
4. Add top-level `modelSelection` object with default "gpt-5"
5. Write transformed data to `v2:data` key
6. Update version marker to "2.0.0"
7. Keep `v1:data` for rollback safety (can delete after 1 week)

---

## API Request/Response Models

### ChatStreamRequest (Backend)

Pydantic model for initiating a streaming chat response.

```python
class ChatStreamRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's message text"
    )
    conversationId: str = Field(
        ...,
        pattern=r"^conv-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        description="Conversation ID"
    )
    conversationHistory: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Previous messages for context (role/content pairs)"
    )
    model: Literal["gpt-5", "gpt-5-codex"] = Field(
        default="gpt-5",
        description="LLM model to use"
    )

    @validator('message')
    def message_not_empty(cls, v):
        if not v or v.strip() == '':
            raise ValueError('Message cannot be empty or whitespace-only')
        return v

    @validator('conversationHistory')
    def validate_history(cls, v):
        for msg in v:
            if 'role' not in msg or 'content' not in msg:
                raise ValueError('Each history message must have role and content')
            if msg['role'] not in ['user', 'assistant', 'system']:
                raise ValueError(f"Invalid role: {msg['role']}")
        return v
```

### ChatStreamEvent (Server-Sent Event)

SSE event format for streaming responses.

```
event: message
data: {"type": "start", "messageId": "msg-<uuid>"}

event: message
data: {"type": "chunk", "content": "Hello"}

event: message
data: {"type": "chunk", "content": " world"}

event: message
data: {"type": "done", "messageId": "msg-<uuid>", "model": "gpt-5"}

event: error
data: {"type": "error", "code": "rate_limit", "message": "The AI service is temporarily busy. Please try again in a moment.", "details": {...}}
```

**Event Types**:
- `start`: Stream beginning, provides messageId
- `chunk`: Partial content chunk (accumulate on client)
- `done`: Stream completed successfully
- `error`: Stream failed with error details

---

## Validation Summary

### Frontend Validation (Pre-request)
- Message text: 1-10,000 chars, not empty/whitespace
- Conversation ID: Valid UUID pattern
- Model selection: One of allowed enum values
- Message history: Valid array of role/content objects

### Backend Validation (Pydantic)
- All request fields per ChatStreamRequest schema
- Conversation history structure and role values
- Message length limits
- UUID pattern matching

### Runtime Validation
- Stream interruption: Verify messageId matches active stream
- Error state transitions: Only valid state changes allowed
- LocalStorage schema: Validate version and structure on load

---

## Error Handling Patterns

### LLM API Errors
- **Authentication Error**: 401 from OpenAI API
  - User Message: "Unable to connect to AI service. Please check your configuration."
  - Status Bar: Red error indicator
  - Log: API key validation failure

- **Rate Limit Error**: 429 from OpenAI API
  - User Message: "The AI service is temporarily busy. Please try again in a moment."
  - Status Bar: Yellow warning indicator
  - Log: Rate limit exceeded, retry-after header

- **Network Timeout**: No response within timeout
  - User Message: "Connection lost. Please check your network and try again."
  - Status Bar: Red error indicator
  - Log: Network timeout after N seconds

- **Model Unavailable**: 503 from OpenAI API
  - User Message: "The selected AI model is temporarily unavailable. Please try again later."
  - Status Bar: Yellow warning indicator
  - Log: Model service unavailable

### Streaming Errors
- **Connection Interrupted**: EventSource closes unexpectedly
  - Preserve partial response received so far
  - Display system message: "Connection was interrupted. Partial response preserved."
  - Status Bar: Yellow warning indicator

- **User Interruption**: Stop button clicked
  - Abort streaming request
  - Display system message: "conversation interrupted by user"
  - Status Bar: Normal state

- **Malformed Chunk**: Invalid JSON in SSE event
  - Log error, skip chunk, continue streaming
  - If critical, abort stream and show error

---

## Future Enhancements (Not in Scope)

- Conversation summarization for long contexts
- Multiple LLM providers (Anthropic, local models)
- Per-conversation model selection
- Message editing and regeneration
- Conversation branching
- Export/import conversation history
- Voice input/output
- Image generation support
