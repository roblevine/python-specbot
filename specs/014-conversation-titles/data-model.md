# Data Model: Conversation Titles

**Feature**: 014-conversation-titles
**Date**: 2026-01-17

## Overview

The conversation title data model already exists in both frontend and backend. This document maps the existing fields and specifies the minimal changes needed.

## Existing Data Model

### Conversation Entity

**Backend Schema** (`backend/src/schemas.py`):

```python
class Conversation(BaseModel):
    id: str                           # Format: "conv-{uuid}"
    title: str                        # 1-100 characters (existing)
    createdAt: str                    # ISO-8601 timestamp
    updatedAt: str                    # ISO-8601 timestamp
    messages: List[ConversationMessage]
```

**Frontend Schema** (`frontend/src/storage/StorageSchema.js`):

```javascript
// Conversation object in localStorage
{
  id: string,                        // Format: "conv-{uuid}"
  title: string,                     // Full text (no server limit locally)
  createdAt: string,                 // ISO-8601 timestamp
  updatedAt: string,                 // ISO-8601 timestamp
  messages: Message[]
}
```

### Title Field Mapping

| Attribute | Backend | Frontend | Spec Requirement |
|-----------|---------|----------|------------------|
| Field name | `title` | `title` | FR-001 ✅ |
| Type | string | string | N/A |
| Min length | 1 | 1 non-whitespace | FR-018 |
| Max length | 100 | 500 (display) | FR-019 |
| Default | N/A | "New Conversation" | FR-003 |
| Persistence | JSON file | localStorage | FR-004 |

## State Transitions

### Title Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    Title State Machine                       │
└─────────────────────────────────────────────────────────────┘

[New Conversation Created]
         │
         ▼
┌─────────────────┐
│ "New Conversation" │◄──── Default title (FR-003)
└─────────────────┘
         │
         │ User sends first message
         ▼
┌─────────────────┐
│ First message   │◄──── Auto-generated title (FR-002)
│ text (full)     │      Stored without truncation (FR-005)
└─────────────────┘
         │
         │ User renames via menu
         ▼
┌─────────────────┐
│ Custom title    │◄──── User-defined title (FR-016)
│ (1-500 chars)   │      Validated before save (FR-018, FR-019)
└─────────────────┘
         │
         │ User renames again
         ▼
┌─────────────────┐
│ New custom      │◄──── Title can be changed unlimited times
│ title           │
└─────────────────┘
```

### Title Update Triggers

| Trigger | Action | Notes |
|---------|--------|-------|
| First message sent | Set title to message text | Only if title is "New Conversation" |
| User renames from StatusBar | Update title | Validated, saved immediately |
| User renames from HistoryBar | Update title | Validated, saved immediately |
| Conversation loaded from storage | No change | Title persisted as-is |

## Validation Rules

### Frontend Validation (New)

```javascript
// Proposed validation in utils/validators.js
function validateTitle(title) {
  const trimmed = title.trim();

  if (trimmed.length === 0) {
    return { valid: false, error: 'Title cannot be empty' };
  }

  if (trimmed.length > 500) {
    return { valid: false, error: 'Title cannot exceed 500 characters' };
  }

  return { valid: true, value: trimmed };
}
```

### Backend Validation (Existing)

- Pydantic enforces 1-100 character limit
- Frontend stores full title in localStorage
- Sync to backend may truncate (acceptable per research)

## Data Flow

### Title Display Flow

```
localStorage.conversations[i].title
         │
         ├──► StatusBar.vue (via activeConversationTitle prop)
         │         │
         │         └──► CSS truncates for display
         │
         └──► HistoryBar.vue (via conversations prop)
                   │
                   └──► CSS truncates for display
```

### Title Update Flow

```
User clicks Rename
         │
         ▼
RenameDialog.vue opens
         │
         ▼
User enters new title
         │
         ▼
validateTitle() checks input
         │
         ├──► Invalid: Show error, block save
         │
         └──► Valid: Emit 'save' event
                   │
                   ▼
         useConversations.renameConversation(id, newTitle)
                   │
                   ├──► Update conversation.title
                   ├──► Update conversation.updatedAt
                   └──► saveToStorage() → API call
                              │
                              ▼
                   All UI components update reactively
```

## No Schema Migration Required

The existing schema version (1.1.0) already supports titles. No migration is needed:

- New conversations: Created with "New Conversation" default
- Existing conversations: Already have title from auto-generation
- Storage format: Unchanged

## Relationships

```
┌─────────────────┐         ┌─────────────────┐
│   Conversation  │ 1    N  │     Message     │
│                 │─────────│                 │
│ - id            │         │ - id            │
│ - title ◄───────┼─────────│ - text (for    │
│ - createdAt     │         │   auto-title)  │
│ - updatedAt     │         │ - sender       │
│ - messages[]    │         │ - timestamp    │
└─────────────────┘         └─────────────────┘

Title derivation:
- Initial: Default "New Conversation"
- Auto-generated: First message.text (when message.sender === "user")
- Manual: User-provided via rename dialog
```
