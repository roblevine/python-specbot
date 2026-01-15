# Data Model: Server-Side Conversation Storage

**Feature**: 010-server-side-conversations
**Date**: 2026-01-15

## Entity Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Conversation                         │
│  ─────────────────────────────────────────────────────  │
│  id: string (UUID format: conv-xxxxxxxx-xxxx-...)      │
│  title: string (auto-generated from first message)     │
│  createdAt: datetime (ISO 8601)                        │
│  updatedAt: datetime (ISO 8601)                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              messages: Message[]                │   │
│  │  ─────────────────────────────────────────────  │   │
│  │  id: string (UUID format: msg-xxxxxxxx-...)    │   │
│  │  text: string (1-10,000 characters)            │   │
│  │  sender: "user" | "system"                     │   │
│  │  timestamp: datetime (ISO 8601)                │   │
│  │  status: "pending" | "sent" | "error"          │   │
│  │  model?: string (e.g., "gpt-4")                │   │
│  │  errorMessage?: string (if status="error")     │   │
│  │  errorType?: string (if status="error")        │   │
│  │  errorCode?: number (if status="error")        │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Entities

### Conversation

A container for a series of messages between user and AI.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique identifier, format: `conv-{uuid}` |
| title | string | Yes | Conversation title (auto-generated from first message, max 100 chars) |
| createdAt | datetime | Yes | ISO 8601 timestamp when conversation was created |
| updatedAt | datetime | Yes | ISO 8601 timestamp of last modification |
| messages | Message[] | Yes | Ordered list of messages (chronological) |

**Validation Rules**:
- `id` must match pattern `conv-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}`
- `title` is non-empty, max 100 characters
- `createdAt` <= `updatedAt`
- `messages` array can be empty (new conversation)

### Message

An individual exchange within a conversation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique identifier, format: `msg-{uuid}` |
| text | string | Yes | Message content (1-10,000 characters) |
| sender | enum | Yes | Either "user" or "system" |
| timestamp | datetime | Yes | ISO 8601 timestamp when message was created |
| status | enum | Yes | "pending", "sent", or "error" |
| model | string | No | Model ID used for system responses (e.g., "gpt-4") |
| errorMessage | string | No | Error description (only if status="error") |
| errorType | string | No | Error category (only if status="error") |
| errorCode | number | No | HTTP-like error code (only if status="error") |

**Validation Rules**:
- `id` must match pattern `msg-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}`
- `text` length: 1-10,000 characters
- `sender` must be exactly "user" or "system"
- `status` must be exactly "pending", "sent", or "error"
- Error fields only present when `status` is "error"

### ConversationSummary

Lightweight representation for listing conversations (without full messages).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Conversation ID |
| title | string | Yes | Conversation title |
| createdAt | datetime | Yes | Creation timestamp |
| updatedAt | datetime | Yes | Last modification timestamp |
| messageCount | number | Yes | Number of messages in conversation |

## Storage Schema

### File Storage Format

The `conversations.json` file contains:

```json
{
  "version": "1.0.0",
  "conversations": [
    {
      "id": "conv-12345678-1234-1234-1234-123456789abc",
      "title": "Discussion about Python",
      "createdAt": "2026-01-15T10:00:00.000Z",
      "updatedAt": "2026-01-15T10:05:30.000Z",
      "messages": [
        {
          "id": "msg-87654321-4321-4321-4321-cba987654321",
          "text": "How do I read a file in Python?",
          "sender": "user",
          "timestamp": "2026-01-15T10:00:00.000Z",
          "status": "sent"
        },
        {
          "id": "msg-11111111-2222-3333-4444-555555555555",
          "text": "You can use the open() function...",
          "sender": "system",
          "timestamp": "2026-01-15T10:00:05.000Z",
          "status": "sent",
          "model": "gpt-4"
        }
      ]
    }
  ]
}
```

### Schema Versioning

| Version | Changes |
|---------|---------|
| 1.0.0 | Initial schema (matches frontend localStorage v1.1.0 structure) |

**Migration Strategy**: When schema version changes, storage service handles migration on load.

## State Transitions

### Message Status

```
┌─────────┐    send     ┌─────────┐
│ pending │ ──────────> │  sent   │
└─────────┘             └─────────┘
     │
     │ error
     v
┌─────────┐
│  error  │
└─────────┘
```

- **pending**: Message created, awaiting processing
- **sent**: Message successfully delivered/received
- **error**: Message processing failed (error fields populated)

## Relationships

```
Conversation 1 ────── * Message
     │
     └── Contains ordered list of messages
         - Messages belong to exactly one conversation
         - Messages ordered by timestamp (ascending)
         - Deleting conversation deletes all messages
```

## Indexes (Future Database)

When migrating to database storage:

| Entity | Index | Purpose |
|--------|-------|---------|
| Conversation | id (primary) | Fast lookup by ID |
| Conversation | updatedAt (desc) | List sorted by recent |
| Message | conversation_id | Filter messages by conversation |
| Message | timestamp | Order messages chronologically |
