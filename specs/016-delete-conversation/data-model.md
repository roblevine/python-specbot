# Data Model: Delete Conversation Feature

**Date**: 2026-01-18
**Branch**: `016-delete-conversation`

## Overview

This feature does not introduce new data entities. It uses the existing `Conversation` entity and removes it from storage upon deletion.

---

## Existing Entities (No Changes)

### Conversation

The conversation entity being deleted. Structure defined in existing codebase.

| Field | Type | Description |
|-------|------|-------------|
| id | string (UUID) | Unique identifier |
| title | string | Display title (shown in confirmation dialog) |
| messages | array | Chat messages (deleted with conversation) |
| createdAt | string (ISO 8601) | Creation timestamp |
| updatedAt | string (ISO 8601) | Last modification timestamp |

**Delete Behavior**: Complete removal of conversation record including all messages.

**Storage Location**:
- Backend: File-based JSON storage (`backend/src/storage/`)
- Frontend: Synced via API; local state in `useConversations`

---

## New UI State (Frontend Only)

### Delete Dialog State

Managed in `App.vue` component (following RenameDialog pattern).

| State | Type | Initial | Description |
|-------|------|---------|-------------|
| showDeleteDialog | boolean | false | Controls dialog visibility |
| deletingConversationId | string | null | ID of conversation to delete |
| deletingConversationTitle | string | '' | Title shown in confirmation |

**State Transitions**:

```
[Hidden] --user clicks Delete--> [Showing Dialog]
[Showing Dialog] --user confirms--> [Processing] --success--> [Hidden]
[Showing Dialog] --user confirms--> [Processing] --error--> [Hidden] + error in status
[Showing Dialog] --user cancels--> [Hidden]
[Showing Dialog] --escape key--> [Hidden]
```

---

## Component Props & Emits

### TitleMenu Component

**New Props**:
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| showDelete | boolean | true | Whether to show Delete option |

**New Emits**:
| Emit | Payload | Description |
|------|---------|-------------|
| delete | none | Fired when Delete menu item clicked |

### DeleteConfirmationDialog Component (New)

**Props**:
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| conversationTitle | string | Yes | Title displayed in confirmation message |

**Emits**:
| Emit | Payload | Description |
|------|---------|-------------|
| confirm | none | User confirmed deletion |
| cancel | none | User cancelled (button or Escape) |

### HistoryBar Component

**New Emits**:
| Emit | Payload | Description |
|------|---------|-------------|
| delete-conversation | conversationId (string) | Bubbles up delete request |

---

## Validation Rules

### Delete Confirmation Dialog

| Rule | Condition | Error |
|------|-----------|-------|
| Valid title | `conversationTitle.length > 0` | N/A (required prop) |

### Delete Operation

| Rule | Condition | Error Response |
|------|-----------|----------------|
| Conversation exists | ID found in storage | 404 Not Found |
| Not active conversation | `id !== activeConversationId` | N/A (button hidden) |

---

## Data Flow

```
User Action                  Component Chain                    State Change
-----------                  ---------------                    ------------
Click menu ellipsis    -->   TitleMenu opens                   isOpen = true
Click "Delete"         -->   TitleMenu emits 'delete'          -
                       -->   HistoryBar emits 'delete-conversation'
                       -->   App.vue handler                   showDeleteDialog = true
                                                               deletingConversationId = id
                                                               deletingConversationTitle = title
Click "Cancel"         -->   Dialog emits 'cancel'             showDeleteDialog = false
                       -->   App.vue handler                   deletingConversationId = null

Click "Delete" confirm -->   Dialog emits 'confirm'            -
                       -->   App.vue calls deleteConversation()
                       -->   useConversations.deleteConversation()
                       -->   apiClient.deleteConversation()
                       -->   DELETE /api/v1/conversations/{id}
                       <--   204 No Content                    conversations array updated
                       -->   App.vue handler                   showDeleteDialog = false
```
