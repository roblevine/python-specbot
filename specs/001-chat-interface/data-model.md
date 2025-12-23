# Data Model: Chat Interface

**Feature**: Chat Interface
**Date**: 2025-12-23
**Phase**: 1 - Design & Contracts

## Overview

This document defines the data entities, their attributes, relationships, validation rules, and state transitions for the chat interface feature.

## Entities

### 1. Conversation

Represents a chat session containing multiple messages between the user and the system.

**Attributes**:

| Attribute | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `id` | string (UUID v4) | Yes | Unique identifier | Format: `conv-[uuid]` |
| `createdAt` | string (ISO 8601) | Yes | Timestamp when conversation was created | Must be valid ISO 8601 datetime |
| `updatedAt` | string (ISO 8601) | Yes | Timestamp of last update | Must be >= createdAt |
| `messages` | Message[] | Yes | Ordered list of messages | Can be empty array |
| `title` | string | No | Display title (auto-generated from first message) | Max 50 characters, trimmed |

**Validation Rules**:
- `id` MUST match pattern `/^conv-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i`
- `createdAt` and `updatedAt` MUST be valid ISO 8601 timestamps
- `updatedAt` MUST be greater than or equal to `createdAt`
- `messages` array MUST be ordered chronologically (oldest first)
- `title` defaults to first 50 characters of first user message, or "New Conversation" if empty

**Relationships**:
- One Conversation contains many Messages (1:N)
- Messages belong to exactly one Conversation

**State Transitions**:
```
[Created] → [Active] → [Archived]
   ↓          ↓
   └─────────→ [Empty] (can be deleted if no messages sent)
```

**State Rules**:
- **Created**: New conversation, no messages yet
- **Active**: Has at least one message, currently selected or in history
- **Empty**: No messages, not persisted to storage
- **Archived**: (Future enhancement - not in current scope)

---

### 2. Message

Represents a single message in a conversation, sent by either the user or the system.

**Attributes**:

| Attribute | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `id` | string (UUID v4) | Yes | Unique identifier | Format: `msg-[uuid]` |
| `text` | string | Yes | Message content | Max 10,000 characters |
| `sender` | string (enum) | Yes | Who sent the message | Must be "user" or "system" |
| `timestamp` | string (ISO 8601) | Yes | When message was created | Must be valid ISO 8601 datetime |
| `status` | string (enum) | Yes | Message delivery status | Must be "pending", "sent", or "error" |

**Validation Rules**:
- `id` MUST match pattern `/^msg-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i`
- `text` MUST NOT be empty or only whitespace after trimming
- `text` MUST NOT exceed 10,000 characters
- `sender` MUST be one of: `"user"`, `"system"`
- `timestamp` MUST be valid ISO 8601 timestamp
- `status` MUST be one of: `"pending"`, `"sent"`, `"error"`

**Sender Types**:
- `user`: Message sent by the user via the input area
- `system`: Message sent by the system (loopback response in this phase)

**Status Values**:
- `pending`: Message being processed (brief state before loopback)
- `sent`: Message successfully delivered/stored
- `error`: Message failed validation or processing

**State Transitions**:
```
[User Input] → [Pending] → [Sent]
                   ↓
                [Error] (on validation failure)
```

**Relationships**:
- Each Message belongs to exactly one Conversation
- User messages and system messages alternate in loopback flow

---

### 3. AppState (UI State)

Represents the current state of the application UI (not persisted to storage).

**Attributes**:

| Attribute | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `activeConversationId` | string (UUID) or null | No | ID of currently selected conversation | Must match existing conversation ID or null |
| `inputText` | string | Yes | Current text in input area | Max 10,000 characters |
| `isProcessing` | boolean | Yes | Whether a message is being processed | true or false |
| `status` | string | Yes | Status bar message | Any string, max 100 characters |
| `statusType` | string (enum) | Yes | Status message type | Must be "ready", "processing", "error" |

**Validation Rules**:
- `activeConversationId` MUST be null or match an existing conversation ID
- `inputText` trimmed length MUST be <= 10,000 characters
- `isProcessing` prevents sending messages when true
- `statusType` MUST be one of: `"ready"`, `"processing"`, `"error"`

**Status Types**:
- `ready`: Application is ready for user input
- `processing`: Message is being processed (loopback in progress)
- `error`: An error occurred (e.g., validation failure, storage error)

**State Transitions**:
```
[Ready] ←→ [Processing]
   ↓
[Error] → [Ready] (after timeout or user action)
```

---

## Storage Schema (LocalStorage)

### Schema Version: 1.0.0

**Storage Key**: `chatInterface:v1:data`

**Schema Structure**:

```json
{
  "version": "1.0.0",
  "conversations": [
    {
      "id": "conv-550e8400-e29b-41d4-a716-446655440000",
      "createdAt": "2025-12-23T10:00:00.000Z",
      "updatedAt": "2025-12-23T10:05:00.000Z",
      "title": "Hello world",
      "messages": [
        {
          "id": "msg-660e8400-e29b-41d4-a716-446655440001",
          "text": "Hello world",
          "sender": "user",
          "timestamp": "2025-12-23T10:00:00.000Z",
          "status": "sent"
        },
        {
          "id": "msg-660e8400-e29b-41d4-a716-446655440002",
          "text": "Hello world",
          "sender": "system",
          "timestamp": "2025-12-23T10:00:01.000Z",
          "status": "sent"
        }
      ]
    }
  ],
  "activeConversationId": "conv-550e8400-e29b-41d4-a716-446655440000"
}
```

**Validation on Load**:
1. Check `version` field matches expected version (currently "1.0.0")
2. If version mismatch, run migration (future enhancement)
3. Validate all conversations and messages against schema
4. Remove invalid entries, log errors
5. If activeConversationId doesn't match any conversation, set to null

**Validation on Save**:
1. Validate entire data structure before writing
2. If validation fails, log error and don't overwrite
3. Preserve previous valid state

---

## Data Constraints (from Success Criteria)

### Storage Limits

- **Maximum Conversations**: 500 (SC: Scale/Scope)
- **Maximum Messages per Conversation**: 5,000 (SC: Scale/Scope)
- **Maximum Message Length**: 10,000 characters (Edge Case handling)
- **Estimated Storage Size**: 500 conversations × 5,000 messages × ~200 bytes = ~500MB theoretical max
  - Practical limit: ~50-100 conversations with 100-500 messages each = 2-5MB
  - LocalStorage limit: 5-10MB (varies by browser)

### Performance Constraints

- **Loopback Response Time**: <100ms (SC-001)
- **Conversation Switch Time**: <2s (SC-002)
- **Message Rendering**: Support 1,000 messages without degradation (SC-004)

---

## Validation Rules Summary

### Field-Level Validation

**Conversation**:
- ✅ Valid UUID v4 for `id`
- ✅ Valid ISO 8601 timestamps
- ✅ `updatedAt >= createdAt`
- ✅ `messages` is array
- ✅ `title` max 50 chars (trimmed)

**Message**:
- ✅ Valid UUID v4 for `id`
- ✅ `text` not empty after trim
- ✅ `text` max 10,000 chars
- ✅ `sender` in ["user", "system"]
- ✅ `status` in ["pending", "sent", "error"]
- ✅ Valid ISO 8601 timestamp

**AppState**:
- ✅ `activeConversationId` exists or null
- ✅ `inputText` max 10,000 chars
- ✅ `statusType` in ["ready", "processing", "error"]

### Business Rule Validation

- ✅ User cannot send empty message (whitespace-only)
- ✅ Send button disabled during processing
- ✅ Empty conversations not saved to storage
- ✅ Conversations ordered by `updatedAt` DESC in history
- ✅ Messages ordered by `timestamp` ASC in chat area

---

## Entity Lifecycle

### Conversation Lifecycle

```
1. User clicks "New Conversation"
   → Create Conversation with empty messages array
   → Set as activeConversationId
   → DO NOT persist yet (state: Created/Empty)

2. User sends first message
   → Add user message to conversation
   → Add system loopback message
   → Persist conversation to storage (state: Active)
   → Update conversation.updatedAt

3. User sends more messages
   → Append messages to conversation
   → Update conversation.updatedAt
   → Persist to storage

4. User switches to different conversation
   → Load conversation from storage
   → Update activeConversationId
   → Render messages in chat area

5. User deletes conversation (future enhancement)
   → Remove from storage
   → If active, switch to most recent or create new
```

### Message Lifecycle

```
1. User types in input area
   → Update AppState.inputText
   → No validation yet

2. User clicks Send or presses Enter
   → Validate inputText (not empty, max length)
   → If invalid: Show error in status bar, return
   → Set AppState.isProcessing = true
   → Create user Message (status: pending)
   → Add to current conversation
   → Clear input field

3. Process loopback
   → Create system Message with same text
   → Set both messages status to "sent"
   → Update conversation.updatedAt
   → Persist to storage
   → Set AppState.isProcessing = false

4. Handle error (if validation/storage fails)
   → Set message status to "error"
   → Show error in status bar
   → Set AppState.isProcessing = false
```

---

## Migration Strategy (Future)

### Version 1.0.0 → 2.0.0 (Example)

If breaking changes needed (e.g., add new required field):

```javascript
function migrateV1toV2(data) {
  if (data.version !== "1.0.0") return data;

  return {
    version: "2.0.0",
    conversations: data.conversations.map(conv => ({
      ...conv,
      // Add new field with default value
      newField: "defaultValue"
    })),
    activeConversationId: data.activeConversationId
  };
}
```

**Migration Principles**:
- Always preserve user data
- Provide defaults for new required fields
- Log migration steps for debugging
- Validate after migration

---

## Indexes & Queries (In-Memory)

Since we're using LocalStorage (not a database), all queries are in-memory JavaScript operations:

**Common Queries**:

1. **Get all conversations ordered by most recent**:
   ```javascript
   conversations.sort((a, b) =>
     new Date(b.updatedAt) - new Date(a.updatedAt)
   )
   ```

2. **Get conversation by ID**:
   ```javascript
   conversations.find(conv => conv.id === conversationId)
   ```

3. **Get messages for conversation**:
   ```javascript
   conversation.messages.sort((a, b) =>
     new Date(a.timestamp) - new Date(b.timestamp)
   )
   ```

4. **Get conversation title** (first message preview):
   ```javascript
   conversation.title ||
   conversation.messages[0]?.text.slice(0, 50) ||
   "New Conversation"
   ```

---

## Summary

This data model provides:
- ✅ Clear entity definitions with validation rules
- ✅ Versioned storage schema (Principle VII)
- ✅ State transition documentation
- ✅ Constraints aligned with success criteria
- ✅ Migration strategy for future changes

All entities are designed for simplicity (Principle VI) while supporting the required functionality from the spec.
