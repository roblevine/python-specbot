# Data Model: Message Streaming

**Feature**: 009-message-streaming
**Date**: 2026-01-13
**Status**: Design Complete

## Overview

This document defines the data entities and state transitions for real-time LLM response streaming. The model extends the existing message structure to support progressive token accumulation and streaming states.

---

## Entities

### 1. StreamingMessage (Frontend State)

Represents a message currently being streamed from the LLM to the frontend.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique message identifier (UUID) |
| `sender` | enum | Yes | Message sender: `"user"` or `"system"` |
| `text` | string | Yes | Accumulated message content (grows as tokens arrive) |
| `streaming` | boolean | Yes | True if actively streaming, false when complete |
| `timestamp` | string | Yes | ISO-8601 timestamp when streaming started |
| `model` | string | No | Model ID used for generation (e.g., "gpt-4") |
| `incomplete` | boolean | No | True if streaming was interrupted with partial content |
| `error` | string | No | Error message if streaming failed |

**Example (Streaming In Progress)**:
```json
{
  "id": "msg-550e8400-e29b-41d4-a716-446655440000",
  "sender": "system",
  "text": "The capital of France is ",
  "streaming": true,
  "timestamp": "2026-01-13T10:30:45.123Z",
  "model": "gpt-4"
}
```

**Example (Completed)**:
```json
{
  "id": "msg-550e8400-e29b-41d4-a716-446655440000",
  "sender": "system",
  "text": "The capital of France is Paris.",
  "streaming": false,
  "timestamp": "2026-01-13T10:30:45.123Z",
  "model": "gpt-4"
}
```

**Example (Interrupted with Error)**:
```json
{
  "id": "msg-550e8400-e29b-41d4-a716-446655440000",
  "sender": "system",
  "text": "The capital of France is Pa",
  "streaming": false,
  "incomplete": true,
  "error": "Connection lost",
  "timestamp": "2026-01-13T10:30:45.123Z",
  "model": "gpt-4"
}
```

**Validation Rules**:
- `id` must be a valid UUID
- `sender` must be `"user"` or `"system"`
- `text` can be empty string during initial streaming
- `streaming` true requires `incomplete` to be false or undefined
- `incomplete` true requires `error` to be present
- `timestamp` must be valid ISO-8601 format

**State Transitions**: See section below

---

### 2. StreamEvent (SSE Protocol)

Represents a single Server-Sent Event in the streaming protocol.

**Event Types**:

| Event Type | Purpose | Payload Fields |
|------------|---------|----------------|
| `token` | Delivers a single token/chunk from LLM | `type`, `content` |
| `complete` | Signals successful stream completion | `type`, `model`, `totalTokens` (optional) |
| `error` | Signals streaming error | `type`, `error`, `code` |

**Token Event**:
```json
{
  "type": "token",
  "content": "Hello"
}
```

**Complete Event**:
```json
{
  "type": "complete",
  "model": "gpt-4",
  "totalTokens": 150
}
```

**Error Event**:
```json
{
  "type": "error",
  "error": "AI service error occurred",
  "code": "LLM_ERROR"
}
```

**SSE Wire Format**:
```
data: {"type": "token", "content": "Hello"}

data: {"type": "token", "content": " world"}

data: {"type": "complete", "model": "gpt-4"}

```

**Error Codes**:
- `TIMEOUT`: Request timed out (504)
- `RATE_LIMIT`: Rate limit exceeded (503)
- `LLM_ERROR`: Generic LLM service error (503)
- `AUTH_ERROR`: Authentication/configuration error (503)
- `CONNECTION_ERROR`: Network/connection error (503)
- `UNKNOWN`: Unexpected error (500)

---

### 3. StreamingState (Frontend Composable State)

Tracks the global streaming state in the frontend application.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `isStreaming` | boolean | Yes | True if any stream is active |
| `streamingMessage` | StreamingMessage | No | Currently streaming message (null if none) |
| `eventSource` | EventSource | No | Active EventSource connection (null if none) |

**Example**:
```javascript
{
  isStreaming: true,
  streamingMessage: {
    id: "msg-abc123",
    sender: "system",
    text: "The capital",
    streaming: true,
    timestamp: "2026-01-13T10:30:45.123Z"
  },
  eventSource: EventSource { readyState: 1, url: "http://..." }
}
```

---

## State Transitions

### StreamingMessage State Machine

```
                                 ┌──────────────┐
                                 │   PENDING    │
                                 │ (not created)│
                                 └──────┬───────┘
                                        │
                          startStreaming()
                                        │
                                        ▼
                           ┌────────────────────┐
                           │     STREAMING      │
                           │ streaming: true    │
                           │ text: accumulating │
                           └─┬────────┬─────────┘
                             │        │
                  appendToken()      error occurs
                    (loop)            │
                             │        │
              ┌──────────────┘        │
              │                       │
              │                       ▼
              │            ┌──────────────────┐
              │            │  INTERRUPTED     │
              │            │ streaming: false │
              │            │ incomplete: true │
              │            │ error: set       │
              │            └──────────────────┘
              │
              ▼
┌─────────────────────────┐
│       COMPLETE          │
│   streaming: false      │
│   text: final content   │
│   saved to messages[]   │
└─────────────────────────┘
```

**Transitions**:

1. **PENDING → STREAMING**: `startStreaming()`
   - Create new StreamingMessage with empty `text`
   - Set `streaming: true`
   - Initialize EventSource connection

2. **STREAMING → STREAMING**: `appendToken(token)`
   - Concatenate token to `text`
   - Update timestamp (optional)
   - Trigger Vue reactivity

3. **STREAMING → COMPLETE**: `completeStreaming()`
   - Set `streaming: false`
   - Move message from `streamingMessage` to `messages` array
   - Close EventSource
   - Save to LocalStorage

4. **STREAMING → INTERRUPTED**: Error occurs
   - Set `streaming: false`
   - Set `incomplete: true`
   - Set `error` message
   - Close EventSource
   - Move to `messages` array (preserve partial content)

**Invariants**:
- Only one message can be in STREAMING state at a time (per conversation)
- STREAMING requires active EventSource connection
- COMPLETE and INTERRUPTED are terminal states (no further transitions)
- `text` only grows during STREAMING (never shrinks)
- `incomplete` true implies `streaming` false

---

## Data Flow

### Streaming Flow (Happy Path)

```
Frontend                    Backend                      OpenAI
────────                    ───────                      ──────

1. User sends message
   │
   ├──POST /api/v1/messages──────►│
   │  Accept: text/event-stream    │
   │                                │
2. Create StreamingMessage         ├──astream()───────────►│
   streaming: true                 │                         │
   text: ""                        │                         │
   │                               │                         │
3. Open EventSource                │◄───chunk 1─────────────│
   │                               │                         │
   │◄──data: {"type":"token"}──────│                         │
   │       "content": "Hello"      │                         │
   │                               │                         │
4. appendToken("Hello")            │◄───chunk 2─────────────│
   text: "Hello"                   │                         │
   │                               │                         │
   │◄──data: {"type":"token"}──────│                         │
   │       "content": " world"     │                         │
   │                               │                         │
5. appendToken(" world")           │◄───complete────────────│
   text: "Hello world"             │                         │
   │                               │                         │
   │◄──data: {"type":"complete"}───│                         │
   │       "model": "gpt-4"        │                         │
   │                               │                         │
6. completeStreaming()
   streaming: false
   Save to messages[]
   Close EventSource
```

### Error Flow

```
Frontend                    Backend                      OpenAI
────────                    ───────                      ──────

1. User sends message
   │
   ├──POST /api/v1/messages──────►│
   │  Accept: text/event-stream    │
   │                                │
2. Create StreamingMessage         ├──astream()───────────►│
   streaming: true                 │                         │
   text: ""                        │                         │
   │                               │                         │
3. Open EventSource                │◄───chunk 1─────────────│
   │                               │                         │
   │◄──data: {"type":"token"}──────│                         │
   │       "content": "Hello"      │                         │
   │                               │                         │
4. appendToken("Hello")            │◄───ERROR (timeout)─────│
   text: "Hello"                   │                         │
   │                               │                         │
   │                             catch error                 │
   │                               │                         │
   │◄──data: {"type":"error"}──────│                         │
   │       "error": "Timeout"      │                         │
   │       "code": "TIMEOUT"       │                         │
   │                               │                         │
5. handleStreamError()
   streaming: false
   incomplete: true
   error: "Timeout"
   Save partial to messages[]
   Close EventSource
```

---

## Persistence

### LocalStorage Schema (No Changes Required)

The existing LocalStorage schema (v1.1.0) is sufficient for streaming:

**Completed Streamed Messages**:
```json
{
  "conversations": [
    {
      "id": "conv-123",
      "messages": [
        {
          "id": "msg-456",
          "sender": "user",
          "text": "What is the capital of France?",
          "timestamp": "2026-01-13T10:30:40.000Z"
        },
        {
          "id": "msg-789",
          "sender": "system",
          "text": "The capital of France is Paris.",
          "timestamp": "2026-01-13T10:30:45.123Z",
          "model": "gpt-4"
        }
      ]
    }
  ],
  "selectedModelId": "gpt-4",
  "version": "1.1.0"
}
```

**Key Points**:
- Streaming messages are NOT persisted until complete
- Only completed messages (streaming: false) are saved to LocalStorage
- Interrupted messages (incomplete: true) ARE saved to preserve partial content
- The `streaming`, `incomplete`, and `error` fields are transient (not persisted)
- The `model` field is persisted for completed messages

---

## API Contract Alignment

This data model aligns with the API contracts defined in `contracts/streaming-api.yaml`:
- **StreamEvent** maps to SSE event format
- **StreamingMessage** represents frontend state derived from SSE events
- **Error codes** match HTTP status codes and error events

See `contracts/streaming-api.yaml` for detailed API specification.

---

**Data Model Status**: ✅ COMPLETE
**Next Phase**: Generate API contracts (streaming-api.yaml)
