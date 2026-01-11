# Data Model: OpenAI Model Selector

**Feature**: 008-openai-model-selector
**Date**: 2026-01-11
**Status**: Complete

## Entities

### Model (Backend Configuration)

Represents an available OpenAI model in the system configuration.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | OpenAI model identifier (e.g., "gpt-4", "gpt-3.5-turbo") |
| name | string | Yes | Human-readable display name (e.g., "GPT-4") |
| description | string | Yes | Brief description of model characteristics |
| default | boolean | No | Whether this is the default model (default: false) |

**Validation Rules**:
- `id`: Non-empty string, valid OpenAI model identifier
- `name`: Non-empty string, max 50 characters
- `description`: Non-empty string, max 200 characters
- `default`: Exactly one model must have `default: true` in configuration

**Example**:
```json
{
  "id": "gpt-4",
  "name": "GPT-4",
  "description": "Most capable model for complex tasks",
  "default": false
}
```

---

### ModelConfiguration (Backend)

Root configuration structure for available models.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| models | Model[] | Yes | Array of available model configurations |

**Validation Rules**:
- `models`: Must contain at least one model
- Exactly one model must have `default: true`
- All `id` values must be unique

**Source**: Environment variable `OPENAI_MODELS` as JSON string

**Fallback**: If `OPENAI_MODELS` not set, use single model from `OPENAI_MODEL` env var (or "gpt-3.5-turbo" default) with generated metadata.

---

### MessageRequest (Extended)

Extended request payload for chat messages.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | User message text (1-10,000 chars) |
| conversationId | string | No | Conversation UUID with "conv-" prefix |
| timestamp | string | No | Client timestamp (ISO-8601) |
| history | HistoryMessage[] | No | Previous messages for context |
| **model** | string | **No** | **NEW: Model ID to use for this request** |

**Validation Rules (model field)**:
- If provided, must match an `id` in the configured models
- If not provided or null, use the default model
- Invalid model ID returns 400 Bad Request

---

### MessageResponse (Extended)

Extended response payload for chat responses.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| status | "success" | Yes | Response status |
| message | string | Yes | AI-generated response text |
| timestamp | string | Yes | Server timestamp (ISO-8601) |
| **model** | string | **Yes** | **NEW: Model ID that generated this response** |

---

### ModelsResponse (New)

Response payload for the models listing endpoint.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| models | ModelInfo[] | Yes | Array of available models |

---

### ModelInfo (New)

Model information returned by the models endpoint.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Model identifier for API requests |
| name | string | Yes | Display name for UI |
| description | string | Yes | Description for user information |
| default | boolean | Yes | Whether this is the default model |

---

### StorageSchema (Extended - Frontend)

Extended LocalStorage schema structure.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| version | string | Yes | Schema version ("1.0.0") |
| conversations | Conversation[] | Yes | Array of conversations |
| activeConversationId | string | null | No | Currently active conversation |
| **selectedModelId** | string | null | **No** | **NEW: Currently selected model ID** |

**Validation Rules (selectedModelId)**:
- Optional field (null if never selected)
- If present, should match a model ID from API
- Invalid/stale values cleared on app load

---

### Message (Extended - Frontend)

Extended message entity for display.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Message UUID |
| sender | "user" \| "system" | Yes | Message sender type |
| text | string | Yes | Message content |
| timestamp | string | Yes | Message timestamp |
| error | object | No | Error details if applicable |
| **model** | string | **No** | **NEW: Model that generated response (system messages only)** |

---

## State Transitions

### Model Selection Flow

```
┌─────────────────┐
│   App Load      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     Yes    ┌─────────────────┐
│ selectedModelId ├───────────►│ Validate model  │
│  in storage?    │            │  exists in API  │
└────────┬────────┘            └────────┬────────┘
         │ No                           │
         ▼                              ▼ Valid
┌─────────────────┐            ┌─────────────────┐
│ Fetch models    │            │ Use stored      │
│ from API        │            │ selection       │
└────────┬────────┘            └─────────────────┘
         │                              │ Invalid
         ▼                              ▼
┌─────────────────┐            ┌─────────────────┐
│ Set default     │◄───────────┤ Clear storage,  │
│ model           │            │ use default     │
└────────┬────────┘            └─────────────────┘
         │
         ▼
┌─────────────────┐
│ User selects    │
│ different model │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Save to storage │
│ Use for requests│
└─────────────────┘
```

### Message Flow with Model

```
User Action                 Frontend State                 Backend
───────────────────────────────────────────────────────────────────
Select "GPT-4"        →     selectedModelId = "gpt-4"
                            Save to localStorage

Type message          →
Click Send            →
                            Build request:
                            {
                              message: "...",
                              model: "gpt-4",      ← from state
                              history: [...]
                            }

                      →     POST /api/v1/messages  →     Validate model
                                                          Initialize ChatOpenAI(model="gpt-4")
                                                          Call OpenAI

                      ←     Response               ←     {
                            {                             status: "success",
                              status,                     message: "...",
                              message,                    model: "gpt-4"  ← echo back
                              model: "gpt-4"            }
                            }

                            Create system message
                            with model="gpt-4"
                            Display in MessageBubble
                            with model indicator
```

---

## Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                         Backend                                  │
│  ┌─────────────────┐      ┌─────────────────────────────────┐  │
│  │ ModelConfig     │      │ MessageRequest                   │  │
│  │ (env variable)  │      │ - model?: string                 │  │
│  │ - models[]      │◄─────│                                  │  │
│  └────────┬────────┘      └─────────────────────────────────┘  │
│           │ validates                                           │
│           ▼                                                     │
│  ┌─────────────────┐      ┌─────────────────────────────────┐  │
│  │ LLM Service     │─────►│ MessageResponse                  │  │
│  │ - model param   │      │ - model: string                  │  │
│  └─────────────────┘      └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│  ┌─────────────────┐      ┌─────────────────────────────────┐  │
│  │ ModelsResponse  │─────►│ useModels composable             │  │
│  │ from GET /models│      │ - availableModels[]              │  │
│  └─────────────────┘      │ - selectedModelId                │  │
│                           └────────────┬────────────────────┘  │
│                                        │                        │
│                                        ▼                        │
│  ┌─────────────────┐      ┌─────────────────────────────────┐  │
│  │ StorageSchema   │◄─────│ ModelSelector component          │  │
│  │ selectedModelId │      │ - dropdown UI                    │  │
│  └─────────────────┘      └─────────────────────────────────┘  │
│                                        │                        │
│                                        ▼                        │
│                           ┌─────────────────────────────────┐  │
│                           │ Message entity                   │  │
│                           │ - model (for display)            │  │
│                           └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```
