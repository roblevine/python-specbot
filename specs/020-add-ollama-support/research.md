# Research: Add Ollama Model Support

**Feature**: 020-add-ollama-support
**Date**: 2026-01-22

## Research Tasks

### 1. LangChain Ollama Integration

**Question**: How to integrate Ollama with LangChain?

**Decision**: Use `langchain-ollama` package with `ChatOllama` class

**Rationale**:
- Official LangChain integration for Ollama
- `ChatOllama` class follows same interface as `ChatOpenAI` and `ChatAnthropic`
- Supports streaming out of the box
- Handles connection errors gracefully

**Alternatives Considered**:
- Direct Ollama HTTP API: Rejected - would bypass LangChain abstraction and require custom streaming implementation
- langchain-community Ollama: Deprecated in favor of dedicated langchain-ollama package

**Implementation**:
```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama2",
    base_url="http://localhost:11434",
    timeout=120
)
```

### 2. Ollama Error Types

**Question**: What errors can Ollama throw and how to map them?

**Decision**: Map Ollama/httpx connection errors to existing LLMServiceError hierarchy

**Rationale**:
- Ollama uses httpx under the hood, so errors come from httpx
- Need to handle: connection refused, timeout, model not found
- Map to existing error classes for consistent frontend handling

**Error Mapping**:
| Ollama/httpx Error | LLMServiceError |
|-------------------|-----------------|
| `httpx.ConnectError` | `LLMConnectionError` ("Unable to reach local Ollama server") |
| `httpx.TimeoutException` | `LLMTimeoutError` ("Request to Ollama timed out") |
| `httpx.HTTPStatusError` (404) | `LLMBadRequestError` ("Model not found in Ollama") |
| `httpx.HTTPStatusError` (other) | `LLMServiceError` (generic) |

**Note**: Ollama does not have authentication errors (no API key required).

### 3. Configuration Pattern

**Question**: How to configure Ollama models following existing patterns?

**Decision**: Use `OLLAMA_MODELS` env var (same JSON format) + `OLLAMA_BASE_URL` env var

**Rationale**:
- Consistent with `OPENAI_MODELS`, `ANTHROPIC_MODELS` pattern
- Base URL needed because Ollama can run on non-default host/port
- No API key env var needed (Ollama is local, unauthenticated by default)

**Configuration Format**:
```bash
# Models (same format as other providers)
OLLAMA_MODELS='[
  {"id": "llama2", "name": "Llama 2", "description": "Meta's Llama 2 model"},
  {"id": "codellama", "name": "Code Llama", "description": "Specialized for code generation"}
]'

# Base URL (optional, defaults to http://localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434
```

### 4. ProviderConfig Modification

**Question**: How to handle Ollama's lack of API key requirement?

**Decision**: Make `api_key_env` optional in `ProviderConfig` with special handling for Ollama

**Rationale**:
- Current `ProviderConfig` requires `api_key_env` field
- Ollama doesn't need an API key
- Options: (a) make field optional, (b) use dummy env var, (c) special case in `is_enabled()`

**Implementation**:
- Add `api_key_env: Optional[str]` to `ProviderConfig` (change from required to optional)
- Modify `is_enabled()` to return `True` if `api_key_env` is None (provider always enabled)
- Ollama provider sets `api_key_env=None` in its config

**Alternative Rejected**: Using a dummy `OLLAMA_API_KEY` env var that must be set to any value - this is confusing UX and violates principle VI (simplicity).

### 5. Provider Enablement Logic

**Question**: When is Ollama provider considered "enabled"?

**Decision**: Ollama is enabled if `OLLAMA_MODELS` is configured (non-empty)

**Rationale**:
- Unlike cloud providers, Ollama has no API key to check
- If user configures models, they intend to use Ollama
- Connection availability is checked at runtime, not startup

**Implementation**:
```python
def is_enabled(self) -> bool:
    # For Ollama: enabled if models are configured
    # (api_key_env is None, so skip API key check)
    if self._config.api_key_env is None:
        import os
        models = os.getenv(self._config.models_env)
        return bool(models and models.strip())
    # For other providers: check API key
    return super().is_enabled()
```

### 6. Streaming Support

**Question**: Does ChatOllama support streaming?

**Decision**: Yes, streaming works identically to other LangChain providers

**Rationale**:
- `ChatOllama` inherits from `BaseChatModel`
- Supports `stream()` method and async `astream()`
- Existing streaming infrastructure in `llm_service.py` works without modification

**Verification**: No changes needed to streaming code; `stream_ai_response()` already handles any `BaseChatModel`.

## Summary

| Research Item | Decision | Impact |
|---------------|----------|--------|
| LangChain Integration | `langchain-ollama` package, `ChatOllama` class | New dependency |
| Error Mapping | Map httpx errors to LLMServiceError hierarchy | New `map_ollama_error()` function |
| Configuration | `OLLAMA_MODELS` + `OLLAMA_BASE_URL` env vars | Update `models.py` |
| ProviderConfig | Make `api_key_env` optional | Minor schema change |
| Enablement | Enabled if models configured | Custom `is_enabled()` logic |
| Streaming | Works out of the box | No changes needed |

## Dependencies

**New Package**: `langchain-ollama>=0.2.0`

Add to `backend/requirements.txt`:
```
langchain-ollama>=0.2.0
```
