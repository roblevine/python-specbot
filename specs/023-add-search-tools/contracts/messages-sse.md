# Extended SSE Events for Tool-Enabled Streaming

**Feature**: 023-add-search-tools | **Version**: 1.0.0

## Overview

This document extends the existing SSE (Server-Sent Events) contract from Feature 009 to support tool invocations during message streaming.

## Endpoint

```
POST /api/v1/messages
Accept: text/event-stream
```

## Event Types

### Existing Events (Feature 009)

| Type | Description |
|------|-------------|
| `token` | Partial text content from LLM |
| `complete` | Response finished successfully |
| `error` | An error occurred |

### New Events (Feature 023)

| Type | Description |
|------|-------------|
| `tool_call` | LLM has decided to use a tool |
| `tool_result` | Tool execution has completed |

---

## Event Schemas

### TokenEvent (unchanged)

```json
{
  "type": "token",
  "content": "string"
}
```

### CompleteEvent (unchanged)

```json
{
  "type": "complete",
  "model": "string",
  "totalTokens": "number (optional)"
}
```

### ErrorEvent (unchanged)

```json
{
  "type": "error",
  "error": "string",
  "code": "string",
  "debug_info": "object (optional, only in DEBUG mode)"
}
```

### ToolCallEvent (NEW)

Emitted when the LLM decides to invoke a tool.

```json
{
  "type": "tool_call",
  "tool": "string",
  "invocation_id": "string",
  "args": "object"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Always `"tool_call"` |
| `tool` | string | Yes | Tool identifier (e.g., `"google_search"`) |
| `invocation_id` | string | Yes | Unique ID to correlate with result |
| `args` | object | Yes | Arguments passed to the tool |

**Example:**

```json
{
  "type": "tool_call",
  "tool": "google_search",
  "invocation_id": "call_abc123",
  "args": {
    "query": "current weather in London"
  }
}
```

### ToolResultEvent (NEW)

Emitted when a tool execution completes.

```json
{
  "type": "tool_result",
  "tool": "string",
  "invocation_id": "string",
  "success": "boolean",
  "sources": "array (optional)"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Always `"tool_result"` |
| `tool` | string | Yes | Tool identifier |
| `invocation_id` | string | Yes | Matches the `tool_call` event |
| `success` | boolean | Yes | Whether execution succeeded |
| `sources` | array | No | Attribution sources (for successful searches) |

**Example (success):**

```json
{
  "type": "tool_result",
  "tool": "google_search",
  "invocation_id": "call_abc123",
  "success": true,
  "sources": [
    {
      "title": "BBC Weather - London",
      "url": "https://www.bbc.com/weather/2643743"
    }
  ]
}
```

**Example (failure):**

```json
{
  "type": "tool_result",
  "tool": "google_search",
  "invocation_id": "call_abc123",
  "success": false
}
```

---

## Event Sequence

### Standard Response (no tools)

```
data: {"type":"token","content":"Hello"}

data: {"type":"token","content":" there!"}

data: {"type":"complete","model":"gpt-4"}
```

### Response with Tool Usage

```
data: {"type":"tool_call","tool":"google_search","invocation_id":"call_1","args":{"query":"weather London"}}

data: {"type":"tool_result","tool":"google_search","invocation_id":"call_1","success":true,"sources":[{"title":"BBC Weather","url":"..."}]}

data: {"type":"token","content":"Based on"}

data: {"type":"token","content":" my search,"}

data: {"type":"token","content":" the current"}

data: {"type":"token","content":" weather in London"}

data: {"type":"token","content":" is 12°C."}

data: {"type":"complete","model":"gpt-4"}
```

### Response with Multiple Tool Calls

```
data: {"type":"tool_call","tool":"google_search","invocation_id":"call_1","args":{"query":"Tesla stock price"}}

data: {"type":"tool_result","tool":"google_search","invocation_id":"call_1","success":true,"sources":[...]}

data: {"type":"tool_call","tool":"bbc_news","invocation_id":"call_2","args":{"query":"Tesla news"}}

data: {"type":"tool_result","tool":"bbc_news","invocation_id":"call_2","success":true,"sources":[...]}

data: {"type":"token","content":"Tesla's stock"}

...

data: {"type":"complete","model":"gpt-4"}
```

### Response with Tool Failure

```
data: {"type":"tool_call","tool":"google_search","invocation_id":"call_1","args":{"query":"weather"}}

data: {"type":"tool_result","tool":"google_search","invocation_id":"call_1","success":false}

data: {"type":"token","content":"I wasn't"}

data: {"type":"token","content":" able to search"}

data: {"type":"token","content":" the web, but"}

...

data: {"type":"complete","model":"gpt-4"}
```

---

## Frontend Handling Guidelines

### JavaScript Example

```javascript
import { streamMessage } from './services/apiClient.js';

streamMessage(
  messageText,
  // onToken
  (token) => {
    appendToMessage(token);
  },
  // onComplete
  (metadata) => {
    finalizeMessage(metadata);
  },
  // onError
  (error) => {
    showError(error);
  },
  conversationHistory,
  selectedModelId,
  // NEW: onToolCall
  (toolCall) => {
    showToolIndicator(toolCall.tool, toolCall.args);
  },
  // NEW: onToolResult
  (toolResult) => {
    hideToolIndicator();
    if (toolResult.sources) {
      storeSources(toolResult.sources);
    }
  }
);
```

### UI Feedback

| Event | UI Action |
|-------|-----------|
| `tool_call` | Show "Searching..." indicator with tool name |
| `tool_result` (success) | Hide indicator, store sources for attribution |
| `tool_result` (failure) | Hide indicator (LLM will explain in response) |
| `token` | Append text to message |
| `complete` | Finalize message, show attribution links |

---

## Error Codes (Extended)

| Code | Description |
|------|-------------|
| `AUTH_ERROR` | API key invalid or missing |
| `RATE_LIMIT` | Rate limit exceeded |
| `CONNECTION_ERROR` | Cannot connect to service |
| `TIMEOUT` | Request timed out |
| `LLM_ERROR` | LLM processing error |
| `TOOL_ERROR` | Tool execution failed (NEW) |

---

## Backward Compatibility

- Clients that don't handle `tool_call` and `tool_result` events will simply ignore them
- Text tokens and complete/error events work identically to Feature 009
- No changes to request format required
