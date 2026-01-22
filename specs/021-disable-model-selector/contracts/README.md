# API Contracts: Disable Model Selector

**Feature**: 021-disable-model-selector
**Date**: 2026-01-22

## No New Contracts Required

This feature is a **frontend-only UI behavior change** that does not require any API modifications.

### Existing Contracts Used

| Endpoint | Purpose | Contract Location |
|----------|---------|-------------------|
| `GET /api/v1/models` | Fetch available models | `specs/008-openai-model-selector/contracts/` |
| `GET /api/v1/conversations/:id` | Load conversation with messages | `specs/010-server-side-conversations/contracts/` |
| `POST /api/v1/messages` | Send message (includes model field) | `specs/009-message-streaming/contracts/` |

### Why No New Contracts

1. **Model information already exists**: Messages already store the `model` field (added in feature 009)
2. **No new endpoints needed**: Disabling the selector is purely a UI state change
3. **No request/response changes**: Existing API payloads contain all required data
4. **Backward compatible**: Works with existing conversations and API responses

### Relevant Existing Schemas

**Message with model field** (from `/api/v1/messages` response):
```json
{
  "id": "msg-abc123",
  "text": "Hello, how can I help?",
  "sender": "system",
  "timestamp": "2026-01-22T10:30:00Z",
  "status": "sent",
  "model": "gpt-4"
}
```

**Conversation with messages** (from `/api/v1/conversations/:id`):
```json
{
  "id": "conv-xyz789",
  "title": "Chat about coding",
  "createdAt": "2026-01-22T10:00:00Z",
  "updatedAt": "2026-01-22T10:30:00Z",
  "messages": [
    { "id": "msg-1", "text": "Hi", "sender": "user", "model": null },
    { "id": "msg-2", "text": "Hello!", "sender": "system", "model": "gpt-4" }
  ]
}
```

The frontend will use the existing `model` field from system messages to determine:
1. Which model the conversation uses
2. What to display in the disabled model selector
