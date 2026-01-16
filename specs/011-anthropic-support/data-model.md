# Data Model: Anthropic Claude Model Support

**Feature**: 011-anthropic-support
**Date**: 2026-01-15
**Phase**: 1 - Design

## Entity Changes

### ModelConfig (Extended)

Extends the existing `ModelConfig` Pydantic model to include provider information.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string | Yes | - | Model identifier (e.g., "claude-3-5-sonnet-20241022") |
| `name` | string | Yes | - | Human-readable display name (max 50 chars) |
| `description` | string | Yes | - | Brief model description (max 200 chars) |
| `provider` | string | Yes | - | Provider identifier: "openai" or "anthropic" |
| `default` | boolean | No | false | Whether this is the default model |

**Validation Rules**:
- `id`: Non-empty string, trimmed
- `name`: Non-empty string, max 50 characters
- `description`: Non-empty string, max 200 characters
- `provider`: Must be one of: "openai", "anthropic" (extensible for future providers)
- `default`: Exactly one model across all providers must be marked as default

**Backward Compatibility**:
- Existing `OPENAI_MODELS` without provider field defaults to `provider: "openai"`
- New configurations must include provider field

### Provider (New Concept)

Represents an AI service provider. Not a separate entity in storage, but a logical grouping.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | string | Provider identifier: "openai", "anthropic" |
| `name` | string | Display name: "OpenAI", "Anthropic" |
| `api_key_env` | string | Environment variable name for API key |
| `models_env` | string | Environment variable name for models config |
| `enabled` | boolean | True if API key is configured |

**Provider Registry** (compile-time, not stored):
```python
PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "api_key_env": "OPENAI_API_KEY",
        "models_env": "OPENAI_MODELS"
    },
    "anthropic": {
        "name": "Anthropic",
        "api_key_env": "ANTHROPIC_API_KEY",
        "models_env": "ANTHROPIC_MODELS"
    }
}
```

### ModelsConfiguration (Extended)

Aggregates models from all configured providers.

| Field | Type | Description |
|-------|------|-------------|
| `models` | List[ModelConfig] | Combined list from all enabled providers |

**Validation Rules**:
- At least one model must be configured (from any provider)
- Model IDs must be unique across all providers
- Exactly one model must be marked as default
- Models from unconfigured providers are excluded

## State Transitions

### Model Selection State

```
┌─────────────────┐
│  No Conversation │
│   (selector ON)  │
└────────┬────────┘
         │ User sends first message
         ▼
┌─────────────────┐
│ Active Conversation │
│  (selector LOCKED)  │
└────────┬────────────┘
         │ User starts new conversation
         ▼
┌─────────────────┐
│  No Conversation │
│   (selector ON)  │
└─────────────────┘
```

## API Response Schema Changes

### GET /api/v1/models Response

**Before** (008-openai-model-selector):
```json
{
  "models": [
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "description": "Most capable model",
      "default": true
    }
  ]
}
```

**After** (011-anthropic-support):
```json
{
  "models": [
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "description": "Most capable model",
      "provider": "openai",
      "default": false
    },
    {
      "id": "claude-3-5-sonnet-20241022",
      "name": "Claude 3.5 Sonnet",
      "description": "Most capable Claude model",
      "provider": "anthropic",
      "default": true
    }
  ]
}
```

## Frontend State Changes

### useModels Composable

| State | Type | Description |
|-------|------|-------------|
| `availableModels` | Ref<ModelConfig[]> | Models from all enabled providers |
| `selectedModelId` | Ref<string> | Currently selected model ID |
| `isLoading` | Ref<boolean> | Loading state |
| `error` | Ref<string\|null> | Error message if any |

### Conversation State Integration

| State | Type | Description |
|-------|------|-------------|
| `hasActiveMessages` | Computed<boolean> | True if current conversation has messages |

Used to disable model selector when conversation is active.

## Migration Notes

1. **Existing OpenAI configurations**: Add `"provider": "openai"` to each model in `OPENAI_MODELS`
2. **Default model**: If both providers configured, update default flag to be on exactly one model
3. **No data migration needed**: Configuration is environment-based, not persisted
