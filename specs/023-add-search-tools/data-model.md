# Data Model: Add Search Tools to Chatbot

**Feature**: 023-add-search-tools | **Date**: 2026-01-22

## Overview

This document defines the data entities for the search tools feature. The design follows the existing provider pattern and integrates with LangChain's tool system.

---

## 1. Tool Entity

Represents a standalone capability that extends the chatbot's abilities.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `google_search`, `bbc_news`) |
| `name` | string | Yes | Human-readable name (e.g., "Google Search") |
| `description` | string | Yes | Description for LLM to understand when to use |
| `enabled` | boolean | Yes | Whether tool is currently available |
| `requires_api_key` | boolean | Yes | Whether tool needs external API key |
| `api_key_env_var` | string | No | Environment variable name for API key |

### Example

```json
{
  "id": "google_search",
  "name": "Google Search",
  "description": "Search the web for current information about any topic",
  "enabled": true,
  "requires_api_key": true,
  "api_key_env_var": "TAVILY_API_KEY"
}
```

---

## 2. ToolResult Entity

Represents the outcome of a tool execution.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `success` | boolean | Yes | Whether execution succeeded |
| `content` | string | Yes | Result content or error message |
| `sources` | array[Source] | No | Attribution sources |
| `error_code` | string | No | Error code if failed |
| `execution_time_ms` | integer | No | Execution duration |

### Source Sub-Entity

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | Yes | Source title |
| `url` | string | Yes | Source URL |
| `snippet` | string | No | Brief excerpt |

### Example (Success)

```json
{
  "success": true,
  "content": "The current weather in London is 12°C with cloudy skies...",
  "sources": [
    {
      "title": "BBC Weather - London",
      "url": "https://www.bbc.com/weather/2643743",
      "snippet": "London weather forecast including..."
    }
  ],
  "execution_time_ms": 1250
}
```

### Example (Failure)

```json
{
  "success": false,
  "content": "Web search is temporarily unavailable",
  "sources": [],
  "error_code": "RATE_LIMIT",
  "execution_time_ms": 150
}
```

---

## 3. ToolInvocation Entity

Represents a record of when a tool was called during a conversation.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique invocation ID |
| `tool_id` | string | Yes | Tool that was invoked |
| `arguments` | object | Yes | Arguments passed to tool |
| `result` | ToolResult | Yes | Execution result |
| `timestamp` | datetime | Yes | When invocation occurred |
| `model_id` | string | Yes | Model that requested tool |

### Example

```json
{
  "id": "inv_abc123",
  "tool_id": "google_search",
  "arguments": {
    "query": "current weather in London"
  },
  "result": {
    "success": true,
    "content": "...",
    "sources": [...]
  },
  "timestamp": "2026-01-22T14:30:00Z",
  "model_id": "gpt-4"
}
```

---

## 4. SearchResult Entity

Structured result from a search tool.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | Yes | Result title |
| `url` | string | Yes | Source URL |
| `snippet` | string | Yes | Brief excerpt/description |
| `published_date` | datetime | No | Publication date (for news) |
| `source_name` | string | No | Source attribution |

### Example

```json
{
  "title": "Climate change: Global temperatures hit record high",
  "url": "https://www.bbc.com/news/science-12345",
  "snippet": "Global temperatures reached a new record in 2025...",
  "published_date": "2026-01-22T10:00:00Z",
  "source_name": "BBC News"
}
```

---

## 5. ToolConfiguration Entity

Settings for tool enablement and operation.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `tool_id` | string | Yes | Tool identifier |
| `enabled` | boolean | Yes | Explicit enable/disable |
| `api_key` | string | No | API key (if required) |
| `custom_settings` | object | No | Tool-specific settings |

### Environment Variable Mapping

| Tool | API Key Env Var | Enable Env Var |
|------|-----------------|----------------|
| google_search | `TAVILY_API_KEY` | `TOOLS_GOOGLE_SEARCH_ENABLED` |
| bbc_news | N/A (no key needed) | `TOOLS_BBC_NEWS_ENABLED` |

---

## 6. SSE Event Types

Extended Server-Sent Events for tool communication.

### ToolCallEvent

Emitted when the LLM decides to use a tool.

```typescript
interface ToolCallEvent {
  type: "tool_call";
  tool: string;      // Tool ID
  args: object;      // Arguments
  invocation_id: string;  // For tracking
}
```

### ToolResultEvent

Emitted when a tool execution completes.

```typescript
interface ToolResultEvent {
  type: "tool_result";
  tool: string;           // Tool ID
  invocation_id: string;  // Matches call
  success: boolean;
  sources?: Source[];     // Attribution
}
```

### Event Flow Example

```
1. User: "What's the weather in London?"
2. SSE: {"type": "tool_call", "tool": "google_search", "args": {"query": "weather London"}}
3. [Backend executes tool]
4. SSE: {"type": "tool_result", "tool": "google_search", "success": true, "sources": [...]}
5. SSE: {"type": "token", "content": "The current weather"}
6. SSE: {"type": "token", "content": " in London is"}
7. ...
8. SSE: {"type": "complete", "model": "gpt-4"}
```

---

## 7. Entity Relationships

```
┌─────────────────┐
│      Tool       │
│  (id, name,     │
│  description)   │
└────────┬────────┘
         │
         │ configured by
         ▼
┌─────────────────┐
│ToolConfiguration│
│ (enabled,       │
│  api_key)       │
└────────┬────────┘
         │
         │ produces
         ▼
┌─────────────────┐        ┌─────────────────┐
│ ToolInvocation  │───────▶│   ToolResult    │
│ (id, arguments, │contains│ (success,       │
│  timestamp)     │        │  content)       │
└─────────────────┘        └────────┬────────┘
                                    │
                                    │ contains
                                    ▼
                           ┌─────────────────┐
                           │  SearchResult   │
                           │ (title, url,    │
                           │  snippet)       │
                           └─────────────────┘
```

---

## 8. Validation Rules

### Tool ID
- Pattern: `^[a-z][a-z0-9_]*$` (lowercase, alphanumeric with underscores)
- Min length: 2
- Max length: 50

### Tool Name
- Non-empty string
- Max length: 100

### Tool Description
- Non-empty string
- Max length: 500
- Should describe when LLM should use the tool

### Search Query (Arguments)
- Min length: 1
- Max length: 500
- Trimmed of whitespace

### URL in SearchResult
- Must be valid URL format
- Must start with `http://` or `https://`

---

## 9. State Transitions

### Tool Enablement States

```
         ┌──────────────────┐
         │   Not Configured │
         │  (no env vars)   │
         └────────┬─────────┘
                  │
                  │ TAVILY_API_KEY set
                  ▼
         ┌──────────────────┐
         │     Enabled      │◀────────┐
         │  (key valid)     │         │
         └────────┬─────────┘         │
                  │                   │
                  │ TOOLS_*_ENABLED   │ TOOLS_*_ENABLED
                  │ = false           │ = true
                  ▼                   │
         ┌──────────────────┐         │
         │    Disabled      │─────────┘
         │   (explicit)     │
         └──────────────────┘
```

### Tool Invocation States

```
Idle ──▶ Executing ──▶ Success
              │
              └──────▶ Failed
```
