# Data Model: Backend API Loopback

**Feature**: 003-backend-api-loopback
**Date**: 2025-12-28
**Status**: Phase 1 Design

This document defines the data entities, validation rules, and schemas for the backend API loopback feature.

---

## Overview

The backend API loopback feature is **stateless** - it does not persist any data. All entities represent request/response payloads exchanged between the frontend and backend over HTTP.

**Storage Strategy**: Frontend continues to persist conversations in LocalStorage. Backend does not have a database in this phase.

---

## Entities

### 1. Message Request

**Description**: Payload sent from frontend to backend when user sends a message.

**Fields**:

| Field Name | Type | Required | Validation Rules | Description |
|------------|------|----------|------------------|-------------|
| `message` | string | Yes | - minLength: 1<br>- maxLength: 10,000<br>- Cannot be only whitespace | The user's message text |
| `conversationId` | string (UUID) | No | - Valid UUID v4 format | Optional conversation ID for future use |
| `timestamp` | string (ISO-8601) | No | - Valid ISO-8601 datetime | Client-side timestamp of message creation |

**Validation Rules** (per spec.md FR-007, FR-010, FR-012):
- Message text MUST NOT be empty or contain only whitespace
- Message text MUST NOT exceed 10,000 characters
- Message text MUST preserve special characters, emoji, and multi-byte characters
- Message text MUST support line breaks and formatting

**Example (Valid)**:
```json
{
  "message": "Hello world",
  "conversationId": "a1b2c3d4-5678-90ab-cdef-123456789abc",
  "timestamp": "2025-12-28T10:00:00.000Z"
}
```

**Example (Minimal)**:
```json
{
  "message": "Test"
}
```

**Example (Special Characters)**:
```json
{
  "message": "Hello 🚀 World!\nNew line here."
}
```

---

### 2. Message Response

**Description**: Payload sent from backend to frontend after processing a message request.

**Fields**:

| Field Name | Type | Required | Validation Rules | Description |
|------------|------|----------|------------------|-------------|
| `status` | string (enum) | Yes | - Values: `"success"`, `"error"` | Response status indicator |
| `message` | string | Yes (if success) | - Must start with `"api says: "`<br>- Preserves all characters from request | The loopback message with API prefix |
| `error` | string | Yes (if error) | - Descriptive error message | Error description (only present if status = "error") |
| `timestamp` | string (ISO-8601) | Yes | - Valid ISO-8601 datetime | Server-side timestamp of response creation |

**Validation Rules** (per spec.md FR-002, FR-011):
- If `status = "success"`: `message` field MUST be present and start with `"api says: "`
- If `status = "error"`: `error` field MUST be present with actionable error description
- Server MUST preserve message content exactly (no truncation, no modification except prefix)
- Response MUST include server-generated timestamp

**Example (Success)**:
```json
{
  "status": "success",
  "message": "api says: Hello world",
  "timestamp": "2025-12-28T10:00:01.234Z"
}
```

**Example (Success with Special Characters)**:
```json
{
  "status": "success",
  "message": "api says: Hello 🚀 World!\nNew line here.",
  "timestamp": "2025-12-28T10:00:01.234Z"
}
```

**Example (Error - Validation)**:
```json
{
  "status": "error",
  "error": "Message cannot be empty",
  "timestamp": "2025-12-28T10:00:01.234Z"
}
```

**Example (Error - Message Too Long)**:
```json
{
  "status": "error",
  "error": "Message exceeds maximum length of 10,000 characters",
  "timestamp": "2025-12-28T10:00:01.234Z"
}
```

---

### 3. Error Response

**Description**: Standardized error response for HTTP-level errors (validation, server errors, timeouts).

**Fields**:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `status` | string | Yes | Always `"error"` |
| `error` | string | Yes | Human-readable error message |
| `detail` | object | No | Additional error context (validation errors, field-level details) |
| `timestamp` | string (ISO-8601) | Yes | Server-side timestamp of error |

**HTTP Status Codes**:

| Status Code | Scenario | Error Message Example |
|-------------|----------|----------------------|
| `200 OK` | Success | N/A (uses Message Response) |
| `400 Bad Request` | Invalid message (empty, too long, malformed JSON) | `"Message cannot be empty"` |
| `422 Unprocessable Entity` | Schema validation failure | `"Invalid request format"` |
| `500 Internal Server Error` | Server error | `"Internal server error occurred"` |
| `503 Service Unavailable` | Server overloaded or unavailable | `"Service temporarily unavailable"` |

**Example (400 - Empty Message)**:
```json
{
  "status": "error",
  "error": "Message cannot be empty",
  "timestamp": "2025-12-28T10:00:01.234Z"
}
```

**Example (422 - Schema Validation)**:
```json
{
  "status": "error",
  "error": "Invalid request format",
  "detail": {
    "field": "message",
    "issue": "Field required"
  },
  "timestamp": "2025-12-28T10:00:01.234Z"
}
```

**Example (500 - Server Error)**:
```json
{
  "status": "error",
  "error": "Internal server error occurred",
  "timestamp": "2025-12-28T10:00:01.234Z"
}
```

---

## Pydantic Models (FastAPI Implementation)

### Message Request Model

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class MessageRequest(BaseModel):
    """Request payload for sending a message"""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User message text",
        examples=["Hello world", "Test message 🚀"]
    )
    conversationId: Optional[str] = Field(
        None,
        description="Optional conversation ID",
        pattern=r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$',
        examples=["a1b2c3d4-5678-90ab-cdef-123456789abc"]
    )
    timestamp: Optional[str] = Field(
        None,
        description="Client-side timestamp (ISO-8601)",
        examples=["2025-12-28T10:00:00.000Z"]
    )

    @field_validator('message')
    @classmethod
    def message_not_whitespace(cls, v: str) -> str:
        """Validate message is not only whitespace"""
        if not v.strip():
            raise ValueError('Message cannot be only whitespace')
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Hello world",
                    "conversationId": "a1b2c3d4-5678-90ab-cdef-123456789abc",
                    "timestamp": "2025-12-28T10:00:00.000Z"
                }
            ]
        }
    }
```

### Message Response Model

```python
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class MessageResponse(BaseModel):
    """Response payload for successful message processing"""

    status: Literal["success"] = Field(
        default="success",
        description="Response status"
    )
    message: str = Field(
        ...,
        description="Loopback message with 'api says: ' prefix",
        examples=["api says: Hello world"]
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="Server-side timestamp (ISO-8601)",
        examples=["2025-12-28T10:00:01.234Z"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "message": "api says: Hello world",
                    "timestamp": "2025-12-28T10:00:01.234Z"
                }
            ]
        }
    }
```

### Error Response Model

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any
from datetime import datetime

class ErrorResponse(BaseModel):
    """Response payload for errors"""

    status: Literal["error"] = Field(
        default="error",
        description="Response status"
    )
    error: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Message cannot be empty", "Invalid request format"]
    )
    detail: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error context",
        examples=[{"field": "message", "issue": "Field required"}]
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="Server-side timestamp (ISO-8601)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "error",
                    "error": "Message cannot be empty",
                    "timestamp": "2025-12-28T10:00:01.234Z"
                }
            ]
        }
    }
```

---

## State Transitions

### Message Processing State Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vue.js)                         │
│                                                              │
│  User types message → Validation → POST /api/v1/messages    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Receive Request                                    │  │
│  │    - Parse JSON payload                               │  │
│  │    - Validate against MessageRequest schema           │  │
│  └────────┬─────────────────────────────────────────────┘  │
│           │                                                  │
│           ├──[Invalid]─> Return 400/422 Error Response      │
│           │                                                  │
│           └──[Valid]──┐                                      │
│                       ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 2. Process Message                                    │  │
│  │    - Extract message text                             │  │
│  │    - Prepend "api says: " prefix                      │  │
│  │    - Preserve all characters (emoji, newlines, etc.)  │  │
│  └────────┬─────────────────────────────────────────────┘  │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 3. Create Response                                    │  │
│  │    - Build MessageResponse with loopback message      │  │
│  │    - Add server timestamp                             │  │
│  │    - Return 200 OK                                    │  │
│  └────────┬─────────────────────────────────────────────┘  │
└───────────┼─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vue.js)                         │
│                                                              │
│  Receive response → Update chat area → Display message      │
└─────────────────────────────────────────────────────────────┘
```

### Error Handling States

```
Request Received
    │
    ├─> [Empty message] ──> 400 Bad Request
    │                       "Message cannot be empty"
    │
    ├─> [Too long (>10k)] ─> 400 Bad Request
    │                        "Message exceeds maximum length"
    │
    ├─> [Malformed JSON] ──> 422 Unprocessable Entity
    │                        "Invalid request format"
    │
    ├─> [Server error] ────> 500 Internal Server Error
    │                        "Internal server error occurred"
    │
    └─> [Valid message] ───> 200 OK
                             MessageResponse with loopback
```

---

## Validation Rules Summary

### Request Validation (per spec.md Functional Requirements)

| Rule ID | Field | Validation | Error Response |
|---------|-------|------------|----------------|
| VR-001 | `message` | REQUIRED | HTTP 422 "Field required" |
| VR-002 | `message` | minLength: 1 | HTTP 400 "Message cannot be empty" |
| VR-003 | `message` | maxLength: 10,000 | HTTP 400 "Message exceeds maximum length" |
| VR-004 | `message` | Not only whitespace | HTTP 400 "Message cannot be empty" |
| VR-005 | `conversationId` | Optional UUID v4 format | HTTP 400 "Invalid conversation ID format" |
| VR-006 | Request JSON | Valid JSON structure | HTTP 422 "Invalid request format" |

### Response Validation (per spec.md Functional Requirements)

| Rule ID | Field | Validation | Notes |
|---------|-------|------------|-------|
| VR-007 | `status` | REQUIRED, enum: success/error | Always present |
| VR-008 | `message` | REQUIRED if status=success | Must start with "api says: " |
| VR-009 | `message` | Preserves all characters | No truncation, no modification (except prefix) |
| VR-010 | `error` | REQUIRED if status=error | Descriptive, actionable error message |
| VR-011 | `timestamp` | REQUIRED, ISO-8601 format | Server-generated |

---

## Future Considerations (NOT P1)

### Planned Enhancements (P2+)

**Conversation Persistence**:
- When backend adds database, MessageRequest will include mandatory `conversationId`
- Backend will persist message history in PostgreSQL
- Response will include `messageId` for client reference

**Authentication**:
- Add `userId` field to MessageRequest (from JWT token)
- Add authorization checks before processing messages

**LLM Integration**:
- Replace loopback with actual LLM API calls
- Add streaming response support (Server-Sent Events)
- Add `model` and `parameters` fields to MessageRequest

**Rate Limiting**:
- Add `X-RateLimit-Remaining` headers to MessageResponse
- Implement per-user rate limits

---

## Schema Version

**Current Version**: 1.0.0
**Date**: 2025-12-28
**Status**: Initial implementation

**Versioning Strategy**:
- **MAJOR**: Breaking changes to request/response structure
- **MINOR**: New optional fields, backward-compatible additions
- **PATCH**: Clarifications, documentation updates

---

## References

- **Feature Spec**: `specs/003-backend-api-loopback/spec.md`
- **API Contract**: `specs/003-backend-api-loopback/contracts/message-api.yaml` (OpenAPI 3.1)
- **Implementation Plan**: `specs/003-backend-api-loopback/plan.md`
- **Research**: `specs/003-backend-api-loopback/research.md`
