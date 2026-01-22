# Data Model: Add Ollama Model Support

**Feature**: 020-add-ollama-support
**Date**: 2026-01-22

## Overview

This feature adds Ollama as a third provider alongside OpenAI and Anthropic. The data model changes are minimal since Ollama follows the existing provider pattern.

## Entity Changes

### 1. ProviderConfig (Modified)

**Location**: `backend/src/services/providers/base.py`

**Change**: Make `api_key_env` optional to support Ollama (which has no API key)

```python
class ProviderConfig(BaseModel):
    id: str                           # "openai", "anthropic", "ollama"
    name: str                         # "OpenAI", "Anthropic", "Ollama"
    api_key_env: Optional[str] = None # "OPENAI_API_KEY", "ANTHROPIC_API_KEY", None for Ollama
    models_env: str                   # "OPENAI_MODELS", "ANTHROPIC_MODELS", "OLLAMA_MODELS"
```

**Validation Changes**:
- `api_key_env` validator: Allow None, only validate if provided
- `is_enabled()` method: Return True if `api_key_env` is None (always enabled)

### 2. ModelConfig (Unchanged)

**Location**: `backend/src/config/models.py`

The existing `ModelConfig` schema supports Ollama without changes:

```python
class ModelConfig(BaseModel):
    id: str                                    # "llama2", "codellama", etc.
    name: str                                  # "Llama 2", "Code Llama"
    description: str                           # Model description
    provider: Literal["openai", "anthropic", "ollama"]  # Add "ollama" to literal
    default: bool = False                      # Can be default model
```

**Change**: Extend `provider` Literal type to include `"ollama"`

### 3. PROVIDERS Registry (Extended)

**Location**: `backend/src/config/models.py`

```python
PROVIDERS: Dict[str, Dict[str, str]] = {
    "openai": {
        "name": "OpenAI",
        "api_key_env": "OPENAI_API_KEY",
    },
    "anthropic": {
        "name": "Anthropic",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    "ollama": {                    # NEW
        "name": "Ollama",
        "api_key_env": None,       # No API key required
    }
}

PROVIDER_ENV_VARS: Dict[str, str] = {
    "openai": "OPENAI_MODELS",
    "anthropic": "ANTHROPIC_MODELS",
    "ollama": "OLLAMA_MODELS",     # NEW
}
```

## New Entities

### 4. OllamaProvider

**Location**: `backend/src/services/providers/ollama.py`

```python
class OllamaProvider(AbstractProvider):
    """Ollama provider for local LLM server."""

    _config: ProviderConfig
    _base_url: str  # From OLLAMA_BASE_URL or default

    # Properties
    provider_id: str  # "ollama"

    # Methods
    create_llm(model_id: str) -> BaseChatModel  # Returns ChatOllama
    map_error(error: Exception) -> LLMServiceError
    get_config() -> ProviderConfig
```

**Configuration**:
```python
ProviderConfig(
    id="ollama",
    name="Ollama",
    api_key_env=None,  # No API key
    models_env="OLLAMA_MODELS"
)
```

## Environment Variables

### New Variables

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `OLLAMA_MODELS` | JSON array | Yes (if using Ollama) | - | Model configurations |
| `OLLAMA_BASE_URL` | URL string | No | `http://localhost:11434` | Ollama server URL |

### Example Configuration

```bash
# Ollama Models
OLLAMA_MODELS='[
  {"id": "llama2", "name": "Llama 2", "description": "Meta's Llama 2 7B model"},
  {"id": "llama2:13b", "name": "Llama 2 13B", "description": "Larger Llama 2 model"},
  {"id": "codellama", "name": "Code Llama", "description": "Specialized for code"}
]'

# Custom Ollama server (optional)
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

## Relationships

```
┌─────────────────────┐
│  ModelsConfiguration │
│  (unchanged)         │
└──────────┬──────────┘
           │ contains 0..n
           ▼
┌─────────────────────┐
│     ModelConfig     │
│  provider: "ollama" │◄─── provider field extended
└──────────┬──────────┘
           │ references
           ▼
┌─────────────────────┐
│   OllamaProvider    │──── NEW
│   (AbstractProvider)│
└──────────┬──────────┘
           │ creates
           ▼
┌─────────────────────┐
│     ChatOllama      │──── From langchain-ollama
│   (BaseChatModel)   │
└─────────────────────┘
```

## State Transitions

Ollama models follow the same lifecycle as other provider models:

1. **Configured**: Model defined in `OLLAMA_MODELS`
2. **Available**: Listed in `/api/v1/models` response (no API key check for Ollama)
3. **Selected**: User selects model in frontend
4. **Active**: Model used for message generation

## Validation Rules

1. **Model ID**: Must be valid Ollama model identifier (alphanumeric, colons, hyphens)
2. **Base URL**: Must be valid HTTP/HTTPS URL
3. **Uniqueness**: Model IDs must be unique across ALL providers
4. **Default Model**: Can be an Ollama model if set via `DEFAULT_MODEL` env var
