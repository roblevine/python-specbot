# Contracts: Add Ollama Model Support

**Feature**: 020-add-ollama-support
**Date**: 2026-01-22

## No New Contracts Required

This feature does not introduce new API endpoints. It extends the existing provider infrastructure and uses the existing `/api/v1/models` endpoint.

### Existing Contracts (Unchanged)

#### GET /api/v1/models

**Response Schema** (unchanged):

```json
{
  "models": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "provider": "openai" | "anthropic" | "ollama",
      "default": boolean
    }
  ]
}
```

**Change**: The `provider` field now accepts `"ollama"` as a valid value.

This is a backward-compatible additive change - existing clients that don't know about Ollama will simply see models with `provider: "ollama"` and can display them normally.

### Why No New Contracts

1. **Provider pattern**: Ollama follows the same provider interface as OpenAI/Anthropic
2. **Existing endpoints**: Models listed via `/api/v1/models`, messages sent via existing chat endpoints
3. **No schema changes**: Model config format is identical (id, name, description)
4. **Transparent to frontend**: Frontend model selector automatically displays Ollama models

### Contract Tests

Existing contract tests for `/api/v1/models` will automatically cover Ollama models when configured. No new contract tests needed - just ensure existing tests pass with Ollama models present.
