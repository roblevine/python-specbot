# Data Model: OpenAI LangChain Chat Integration

**Feature**: 006-openai-langchain-chat
**Date**: 2026-01-10
**Status**: Phase 1 Design

## Overview

This feature extends the existing message API to route messages through OpenAI's ChatGPT via LangChain. The data model remains largely unchanged from feature 003, with additions for conversation context handling.

## Entities

### Message (Existing - No Changes)

Frontend-side entity stored in LocalStorage.

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `id` | string | UUID for the message | Frontend generated |
| `text` | string | Message content (1-10,000 chars) | User input or AI response |
| `sender` | enum | `"user"` or `"system"` | Determined by message origin |
| `timestamp` | string | ISO-8601 datetime | Client timestamp |
| `status` | enum | `"pending"`, `"sent"`, `"error"` | Message lifecycle state |

**Notes**:
- `sender: "system"` is used for AI responses (maintaining existing pattern)
- No schema changes required for this feature

### Conversation (Existing - No Changes)

Frontend-side entity stored in LocalStorage.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | UUID with `conv-` prefix |
| `title` | string | First message preview (truncated) |
| `messages` | Message[] | Ordered array of messages |
| `createdAt` | string | ISO-8601 creation timestamp |
| `updatedAt` | string | ISO-8601 last update timestamp |

### LangChain Message Types (New - Backend Only)

Internal representation for LangChain API. Not persisted - converted on each request.

| LangChain Type | Maps From | Description |
|----------------|-----------|-------------|
| `HumanMessage` | `sender: "user"` | User's input message |
| `AIMessage` | `sender: "system"` | Previous AI responses |
| `SystemMessage` | (optional) | System prompt (not used in v1) |

**Conversion Logic**:
```python
def convert_to_langchain_messages(frontend_messages: list[dict]) -> list[BaseMessage]:
    """
    Convert frontend message format to LangChain message types.

    Args:
        frontend_messages: List of messages from frontend with 'sender' and 'text' fields

    Returns:
        List of LangChain HumanMessage/AIMessage objects
    """
    lc_messages = []
    for msg in frontend_messages:
        if msg["sender"] == "user":
            lc_messages.append(HumanMessage(content=msg["text"]))
        elif msg["sender"] == "system":
            lc_messages.append(AIMessage(content=msg["text"]))
    return lc_messages
```

## API Request/Response (Existing Schemas - Minor Update)

### MessageRequest (Unchanged)

```python
class MessageRequest(BaseModel):
    message: str              # Required, 1-10,000 chars
    conversationId: str?      # Optional, conv-{uuid} format
    timestamp: str?           # Optional, ISO-8601
```

### MessageResponse (Semantic Change Only)

The schema structure is unchanged, but the `message` field content changes:

| Version | `message` field content |
|---------|------------------------|
| 003 (loopback) | `"api says: {user_message}"` |
| 006 (OpenAI) | `"{ai_response}"` |

```python
class MessageResponse(BaseModel):
    status: Literal["success"]  # Always "success" for 200
    message: str                # AI-generated response (no prefix)
    timestamp: str              # Server-side ISO-8601 timestamp
```

**Breaking Change**: The `"api says: "` prefix is removed. This is acceptable because:
- The loopback was temporary (P1 MVP only)
- Frontend doesn't parse for this prefix
- Contract tests will be updated

### ErrorResponse (Extended)

New error types for AI service issues:

| Error Type | HTTP Status | `error` field | Trigger |
|------------|-------------|---------------|---------|
| AI Config Error | 503 | "AI service configuration error. Please contact support." | Invalid API key |
| AI Busy | 503 | "AI service is busy. Please try again in a moment." | Rate limit |
| AI Unavailable | 503 | "Unable to reach AI service. Please check your connection." | Network error |
| AI Timeout | 504 | "Request timed out. Please try again." | 30s timeout |
| Bad Request | 400 | "Message could not be processed. Please try rephrasing." | Content filter |

## State Transitions

### Message Lifecycle (Frontend - Unchanged)

```
[User Input] → pending → [API Call] → sent/error
                              ↓
                    [AI Response] → sent
```

### LLM Request Lifecycle (Backend - New)

```
[Request Received]
       ↓
[Validate Message] ──→ 400 Error (if invalid)
       ↓
[Convert to LangChain Messages]
       ↓
[Call OpenAI via LangChain] ──→ 503/504 Error (if fails)
       ↓
[Extract Response Content]
       ↓
[Return MessageResponse]
```

## Conversation Context

### Context Window Management

For this feature (v1), all messages in the conversation are sent to the LLM. Future versions may implement:
- Token counting and truncation
- Sliding window of recent messages
- Summary-based compression

### Request Payload with Context

When the frontend sends a message with conversation history:

```json
{
  "message": "What is my name?",
  "conversationId": "conv-abc123...",
  "timestamp": "2026-01-10T12:00:00.000Z",
  "history": [
    {"sender": "user", "text": "My name is Alice"},
    {"sender": "system", "text": "Nice to meet you, Alice!"},
    {"sender": "user", "text": "What is my name?"}
  ]
}
```

**Note**: The `history` field is a new optional field for this feature. If not provided, only the current message is sent to the LLM.

## Validation Rules

### Message Validation (Unchanged)
- Required, non-empty
- Maximum 10,000 characters
- Cannot be whitespace-only
- Preserves special characters, emoji, multi-byte

### Conversation ID Validation (Unchanged)
- Optional
- Must match pattern: `conv-{uuid}`

### History Validation (New)
- Optional array
- Each entry must have `sender` and `text` fields
- `sender` must be `"user"` or `"system"`
- `text` must be non-empty string

## Security Considerations

### Sensitive Data Handling

| Data | Storage | Exposure |
|------|---------|----------|
| OpenAI API Key | Backend `.env` only | Never logged, never in responses |
| User Messages | LocalStorage (frontend) | Sent to OpenAI API |
| AI Responses | LocalStorage (frontend) | Displayed in UI |
| Error Details | Logged (backend) | Sanitized for client |

### Error Message Sanitization

Raw OpenAI errors must be mapped to user-friendly messages:

```python
# NEVER expose this to client:
openai.AuthenticationError: Incorrect API key provided: sk-abc1...

# ALWAYS return this instead:
{"error": "AI service configuration error. Please contact support."}
```
