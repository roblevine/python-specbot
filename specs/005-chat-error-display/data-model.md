# Data Model: Chat Error Display

**Feature**: 005-chat-error-display
**Date**: 2026-01-10
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the data structures for displaying errors in the chat interface. The model extends the existing message schema with optional error fields while maintaining backward compatibility.

## Entity Definitions

### 1. Message (Extended)

**Purpose**: Represents a chat message with optional error information

**Location**: Frontend state management (`useMessages.js`, `useConversations.js`)

**Schema**:

```typescript
interface Message {
  // Existing fields (no changes)
  id: string                    // Format: "msg-{uuid}"
  text: string                  // Message content
  sender: 'user' | 'system'     // Message sender type
  timestamp: string             // ISO 8601 format (e.g., "2026-01-10T20:24:44.123Z")
  status: 'pending' | 'sent' | 'error'  // Message status

  // NEW: Optional error fields (backward compatible)
  errorMessage?: string         // User-friendly error summary (max 100 chars)
  errorType?: ErrorType         // Categorized error type
  errorCode?: number            // HTTP status code (if server error)
  errorDetails?: string         // Full error details for expansion (max 10,000 chars)
  errorTimestamp?: string       // ISO 8601 timestamp when error occurred
}
```

**Field Descriptions**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `id` | string | Yes | Unique message identifier | Must start with "msg-" |
| `text` | string | Yes | Message content | 1-10,000 characters |
| `sender` | enum | Yes | Who sent the message | "user" or "system" |
| `timestamp` | string | Yes | When message was created | Valid ISO 8601 date |
| `status` | enum | Yes | Message delivery status | "pending", "sent", or "error" |
| `errorMessage` | string | No | Short error description | Max 100 chars, plain text |
| `errorType` | enum | No | Error category | See ErrorType enum below |
| `errorCode` | number | No | HTTP status code | 100-599 |
| `errorDetails` | string | No | Full error information | Max 10,000 chars, may contain JSON/stack traces |
| `errorTimestamp` | string | No | Error occurrence time | Valid ISO 8601 date |

**State Transitions**:

```
┌─────────┐
│ pending │ ──(API success)──> │ sent │
└─────────┘                     └──────┘
     │
     │
     └──(API error)──> │ error │
                        └───────┘
                             │
                             │ (error fields populated)
                             ▼
                        {errorMessage, errorType, errorCode, errorDetails, errorTimestamp}
```

**Backward Compatibility**:
- All error fields are optional
- Existing messages without error fields remain valid
- Components gracefully handle missing error fields with `v-if` checks

### 2. ErrorType (Enum)

**Purpose**: Categorizes errors for consistent display and handling

**Values**:

```typescript
enum ErrorType {
  NETWORK_ERROR = 'Network Error',           // Connection failures, timeouts, CORS
  SERVER_ERROR = 'Server Error',             // 500-series HTTP errors
  VALIDATION_ERROR = 'Validation Error',     // 400, 422 HTTP errors
  CLIENT_ERROR = 'Client Error',             // 4xx errors (except validation)
  UNKNOWN_ERROR = 'Unknown Error'            // Catch-all for unexpected errors
}
```

**Mapping Rules** (from `apiClient.js`):

| HTTP Status | Error Response | ErrorType |
|-------------|----------------|-----------|
| Network failure | `fetch()` throws | `NETWORK_ERROR` |
| Timeout | Request > 10s | `NETWORK_ERROR` |
| CORS error | CORS rejection | `NETWORK_ERROR` |
| 400 | Bad Request | `VALIDATION_ERROR` |
| 422 | Unprocessable Entity | `VALIDATION_ERROR` |
| 401, 403 | Unauthorized/Forbidden | `CLIENT_ERROR` |
| 404 | Not Found | `CLIENT_ERROR` |
| 500 | Internal Server Error | `SERVER_ERROR` |
| 503 | Service Unavailable | `SERVER_ERROR` |
| Other 5xx | Server errors | `SERVER_ERROR` |
| Other | Unexpected | `UNKNOWN_ERROR` |

### 3. ErrorDetails (Structured)

**Purpose**: Structured format for `errorDetails` field when available

**Format**: JSON string (when backend provides structured error)

```typescript
interface ErrorDetailsStructure {
  error: string                  // Main error message
  detail?: object                // Additional error context
  timestamp: string              // When error occurred (ISO 8601)
  statusCode?: number            // HTTP status code
  requestId?: string             // Request tracking ID (if available)
  stack?: string                 // Stack trace (development only)
}
```

**Example**:
```json
{
  "error": "Message validation failed",
  "detail": {
    "field": "text",
    "issue": "String should have at least 1 character",
    "type": "string_too_short"
  },
  "timestamp": "2026-01-10T20:30:15.123Z",
  "statusCode": 422
}
```

**Fallback**: If backend error is plain string, use string directly in `errorDetails`

### 4. SensitiveDataPattern

**Purpose**: Defines patterns for detecting and redacting sensitive information

**Location**: `utils/sensitiveDataRedactor.js`

**Schema**:

```typescript
interface SensitiveDataPattern {
  name: string                   // Pattern name (e.g., "AWS API Key")
  pattern: RegExp                // Regular expression to match sensitive data
  replacement: string            // Text to replace matches with
}
```

**Example Patterns**:

```javascript
const SENSITIVE_PATTERNS = [
  {
    name: 'AWS API Key',
    pattern: /AKIA[0-9A-Z]{16}/g,
    replacement: '***REDACTED_AWS_KEY***'
  },
  {
    name: 'Bearer Token',
    pattern: /Bearer\s+[a-zA-Z0-9\-._~+/]+=*/g,
    replacement: 'Bearer ***REDACTED_TOKEN***'
  },
  {
    name: 'JWT Token',
    pattern: /eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}/g,
    replacement: '***REDACTED_JWT***'
  }
]
```

### 5. CollapsibleState

**Purpose**: Manages expand/collapse state for error details

**Location**: `composables/useCollapsible.js`

**Schema**:

```typescript
interface CollapsibleState {
  isExpanded: Ref<boolean>       // Current expanded state
  toggle: () => void             // Toggle expanded/collapsed
  expand: () => void             // Set to expanded
  collapse: () => void           // Set to collapsed
  triggerAttrs: ComputedRef<{    // ARIA attributes for trigger button
    'aria-expanded': boolean
    'aria-controls': string
    'type': 'button'
  }>
  contentAttrs: ComputedRef<{    // ARIA attributes for content region
    'id': string
    'role': 'region'
    'aria-hidden': boolean
  }>
}
```

## Relationships

```
┌─────────────────┐
│    Message      │
├─────────────────┤
│ id              │
│ text            │
│ sender          │
│ timestamp       │
│ status          │◄────────┐
│ errorMessage?   │         │
│ errorType?      │────┐    │
│ errorCode?      │    │    │
│ errorDetails?   │    │    │
│ errorTimestamp? │    │    │
└─────────────────┘    │    │
                       │    │
                       ▼    │
                ┌────────────────┐
                │   ErrorType    │
                ├────────────────┤
                │ NETWORK_ERROR  │
                │ SERVER_ERROR   │
                │ VALIDATION_... │
                │ CLIENT_ERROR   │
                │ UNKNOWN_ERROR  │
                └────────────────┘

┌──────────────────────┐
│  ErrorDetails        │
│  (JSON structure)    │
├──────────────────────┤
│ error                │
│ detail?              │
│ timestamp            │
│ statusCode?          │
│ requestId?           │
│ stack?               │
└──────────────────────┘

┌────────────────────────┐        ┌──────────────────────┐
│ SensitiveDataPattern   │───*────│  errorDetails field  │
├────────────────────────┤        └──────────────────────┘
│ name                   │
│ pattern (RegExp)       │
│ replacement            │
└────────────────────────┘
```

## Validation Rules

### Message Validation

1. **Required Fields**:
   - `id`, `text`, `sender`, `timestamp`, `status` must always be present
   - Validation enforced in `MessageBubble.vue` props validator

2. **Error Field Constraints**:
   - If `status === 'error'`, at minimum `errorMessage` should be present
   - `errorType` should be one of the ErrorType enum values
   - `errorCode` must be in range 100-599 if present
   - `errorDetails` max length: 10,000 characters (prevents memory issues)

3. **Timestamp Format**:
   - Must be valid ISO 8601 format
   - Validated via `new Date(timestamp).toString() !== 'Invalid Date'`

### Error Details Validation

1. **Sensitive Data Check**:
   - Run `containsSensitiveData(errorDetails)` before display
   - Redact automatically if sensitive patterns detected

2. **Size Limits**:
   - Error message summary: max 100 characters (truncate with "...")
   - Error details: max 10,000 characters (prevent DOM bloat)

3. **XSS Prevention**:
   - All error text displayed in `<pre>` or text nodes (no `v-html`)
   - No user-generated HTML allowed in error fields

## Storage Schema (LocalStorage)

**Location**: Browser LocalStorage via `frontend/src/storage/`

**Schema Version**: v1.0.0 (unchanged - backward compatible)

**Storage Key**: `chatInterface:v1:data`

**Structure**:
```json
{
  "version": "1.0.0",
  "conversations": [
    {
      "id": "conv-uuid",
      "createdAt": "2026-01-10T20:00:00.000Z",
      "messages": [
        {
          "id": "msg-uuid",
          "text": "Hello",
          "sender": "user",
          "timestamp": "2026-01-10T20:00:01.000Z",
          "status": "sent"
        },
        {
          "id": "msg-uuid-2",
          "text": "Failed message",
          "sender": "user",
          "timestamp": "2026-01-10T20:00:05.000Z",
          "status": "error",
          "errorMessage": "Message failed to send",
          "errorType": "Network Error",
          "errorDetails": "Cannot connect to server",
          "errorTimestamp": "2026-01-10T20:00:06.000Z"
        }
      ]
    }
  ],
  "activeConversationId": "conv-uuid"
}
```

**Migration Strategy**:
- No migration needed - error fields are additive
- Existing messages without error fields remain valid
- New error messages include error fields automatically

## Component Data Flow

```
┌──────────────┐
│ User Action  │ (sends message)
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│ useMessages.js  │ creates message with status: 'pending'
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ apiClient.js    │ sends POST /api/v1/messages
└────────┬────────┘
         │
         ├─(success)────> status: 'sent'
         │
         └─(error)──────> status: 'error'
                          errorMessage: "Message failed to send"
                          errorType: "Network Error"
                          errorCode: null
                          errorDetails: "Cannot connect to server"
                          errorTimestamp: ISO timestamp
                          │
                          ▼
                    ┌──────────────────┐
                    │ useMessages.js   │ updates message in state
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ ChatArea.vue     │ renders messages
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ MessageBubble    │ displays error section
                    │                  │ (if status === 'error')
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────────────┐
                    │ useCollapsible           │ manages expand state
                    │ sensitiveDataRedactor    │ redacts sensitive data
                    └──────────────────────────┘
```

## Summary

**Key Entities**:
1. **Message** (extended): Adds 5 optional error fields
2. **ErrorType**: Enum with 5 error categories
3. **ErrorDetails**: Structured format for detailed errors
4. **SensitiveDataPattern**: Regex patterns for redaction
5. **CollapsibleState**: State management for expand/collapse

**No Breaking Changes**: All modifications are additive and backward compatible

**Next Step**: Generate contracts (none required - frontend-only feature)
