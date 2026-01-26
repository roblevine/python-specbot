# Data Model: LangChain Tool Integration

**Feature**: 024-add-langchain-tools
**Date**: 2026-01-26

## Overview

This document defines the data entities, schemas, and relationships for the LangChain tool integration feature.

---

## Entities

### 1. ToolConfig

Defines an available tool in the system configuration.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique tool identifier (e.g., "duckduckgo-search") |
| name | string | Yes | Human-readable display name |
| description | string | Yes | Tool description shown to users |
| enabled | boolean | Yes | Whether the tool is active |

**Validation Rules**:
- `id`: alphanumeric with hyphens, 1-50 characters
- `name`: 1-100 characters
- `description`: 1-500 characters

**Example**:
```json
{
  "id": "duckduckgo-search",
  "name": "Web Search",
  "description": "Search the web using DuckDuckGo",
  "enabled": true
}
```

---

### 2. ToolCallRecord

Represents a single tool invocation within a conversation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique call identifier (format: `tool-{uuid}`) |
| toolId | string | Yes | Reference to ToolConfig.id |
| toolName | string | Yes | Tool display name at time of call |
| args | object | Yes | Input arguments passed to the tool |
| status | enum | Yes | `"pending"`, `"success"`, `"error"` |
| result | string | No | Tool output (if successful) |
| resultLinks | array | No | Extracted links from result (for search tools) |
| error | string | No | Human-readable error message (if failed) |
| errorCode | string | No | Error code for categorization |
| debugInfo | object | No | Debug details (only when DEBUG=true) |
| startedAt | string | Yes | ISO-8601 timestamp when execution started |
| completedAt | string | No | ISO-8601 timestamp when execution completed |
| durationMs | integer | No | Execution duration in milliseconds |

**Validation Rules**:
- `id`: must match pattern `tool-[a-f0-9-]{36}`
- `status`: one of `["pending", "success", "error"]`
- `args`: valid JSON object
- `startedAt`, `completedAt`: valid ISO-8601 datetime

**State Transitions**:
```
pending → success (tool completed successfully)
pending → error (tool failed)
```

**Example (Success)**:
```json
{
  "id": "tool-550e8400-e29b-41d4-a716-446655440000",
  "toolId": "duckduckgo-search",
  "toolName": "Web Search",
  "args": {
    "query": "latest climate change news"
  },
  "status": "success",
  "result": "Found 5 results for 'latest climate change news'...",
  "resultLinks": [
    {"title": "Climate Report 2026", "url": "https://example.com/climate"},
    {"title": "Global Warming Update", "url": "https://example.com/warming"}
  ],
  "startedAt": "2026-01-26T10:30:00.000Z",
  "completedAt": "2026-01-26T10:30:02.500Z",
  "durationMs": 2500
}
```

**Example (Error)**:
```json
{
  "id": "tool-550e8400-e29b-41d4-a716-446655440001",
  "toolId": "web-browser",
  "toolName": "Browse URL",
  "args": {
    "url": "https://unreachable-site.example"
  },
  "status": "error",
  "error": "Unable to connect to the website. The server may be down.",
  "errorCode": "CONNECTION_ERROR",
  "debugInfo": {
    "exception": "ConnectionError",
    "message": "Failed to establish connection",
    "timeout_seconds": 30
  },
  "startedAt": "2026-01-26T10:31:00.000Z",
  "completedAt": "2026-01-26T10:31:30.000Z",
  "durationMs": 30000
}
```

---

### 3. ResultLink

Extracted link from tool result (used for search results).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Link title/description |
| url | string | Yes | Full URL |
| snippet | string | No | Text snippet from page |

**Validation Rules**:
- `url`: valid URL format
- `title`: 1-200 characters

---

### 4. Extended ConversationMessage

The existing `ConversationMessage` entity is extended with an optional `toolCalls` field.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| ... | ... | ... | (all existing fields preserved) |
| toolCalls | ToolCallRecord[] | No | Tool calls made while generating this message |

**Schema Version**: v1.0.0 → v1.1.0

**Backward Compatibility**:
- Existing messages without `toolCalls` remain valid
- `toolCalls` defaults to `null` or empty array when not present

---

## Relationships

```
ToolConfig (1) ←─── (*) ToolCallRecord
    │                      │
    │                      ├── resultLinks: ResultLink[]
    │                      │
ConversationMessage (1) ←─── (*) ToolCallRecord
```

- A `ToolConfig` can be referenced by many `ToolCallRecord` instances
- A `ConversationMessage` can contain zero or more `ToolCallRecord` instances
- `ToolCallRecord` embeds `ResultLink` objects (no separate storage)

---

## Storage Schema

### Tool Configuration (Environment)

```bash
TOOLS='[
  {"id": "duckduckgo-search", "name": "Web Search", "description": "Search the web", "enabled": true},
  {"id": "web-browser", "name": "Browse URL", "description": "Read web pages", "enabled": true}
]'
```

### Conversation Storage (JSON)

```json
{
  "schemaVersion": "1.1.0",
  "conversations": [
    {
      "id": "conv-xxx",
      "messages": [
        {
          "id": "msg-xxx",
          "text": "Here's what I found...",
          "sender": "system",
          "timestamp": "2026-01-26T10:30:05.000Z",
          "model": "gpt-4",
          "toolCalls": [
            {
              "id": "tool-xxx",
              "toolId": "duckduckgo-search",
              "toolName": "Web Search",
              "args": {"query": "..."},
              "status": "success",
              "result": "...",
              "resultLinks": [...],
              "startedAt": "...",
              "completedAt": "...",
              "durationMs": 2500
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Migration

### v1.0.0 → v1.1.0

**Changes**:
- Add optional `toolCalls` field to `ConversationMessage`

**Migration Strategy**:
- No data migration required (new field is optional)
- Bump `schemaVersion` on next write
- Read path handles missing `toolCalls` gracefully

**Rollback**:
- v1.0.0 readers ignore unknown `toolCalls` field
- No data loss on downgrade
