# Data Model: Modular Model Providers

**Date**: 2026-01-16
**Feature**: 012-modular-model-providers

## Overview

This document defines the internal data models for the provider abstraction layer. Note: This is a refactoring feature - no changes to external API contracts or database schemas.

---

## Entity Definitions

### ProviderConfig

Represents configuration metadata for an LLM provider.

```
ProviderConfig
├── id: string (unique identifier, e.g., "openai", "anthropic")
├── name: string (display name, e.g., "OpenAI", "Anthropic")
├── api_key_env: string (environment variable name for API key)
├── models_env: string (environment variable name for models list)
└── enabled: boolean (computed from api_key availability)
```

**Validation Rules:**
- `id` must be lowercase alphanumeric with optional hyphens
- `api_key_env` must be a valid environment variable name
- `enabled` is true only if the API key environment variable is set and non-empty

**Relationships:**
- One ProviderConfig → Many ModelConfig

---

### ModelConfig (existing, unchanged)

Represents a specific model offered by a provider.

```
ModelConfig
├── id: string (model identifier, e.g., "gpt-4", "claude-3-5-sonnet-latest")
├── name: string (display name)
├── description: string (model description)
├── provider: string (reference to ProviderConfig.id)
└── default: boolean (is this the default model?)
```

**Validation Rules:**
- `id` must be non-empty string
- `provider` must reference a valid ProviderConfig.id
- Only one model per provider may have `default=true`

**Relationships:**
- Many ModelConfig → One ProviderConfig

---

### LLMServiceError (existing, extended)

Unified error representation for provider-specific exceptions.

```
LLMServiceError
├── category: enum (authentication | rate_limit | connection | timeout | invalid_request | internal)
├── message: string (user-friendly error message)
├── provider: string (source provider id, optional)
├── retry_after: integer (seconds until retry, optional for rate_limit)
└── details: object (additional context, optional)
```

**Category Definitions:**

| Category | HTTP Status | Description |
|----------|-------------|-------------|
| authentication | 401 | API key invalid, expired, or missing |
| rate_limit | 429 | Request rate exceeded, retry after delay |
| connection | 503 | Cannot reach provider service |
| timeout | 504 | Request exceeded time limit |
| invalid_request | 400 | Malformed or invalid request |
| internal | 500 | Unexpected internal error |

---

### BaseProvider (new, abstract)

Abstract interface that all provider implementations must satisfy.

```
BaseProvider (Protocol/ABC)
├── provider_id: string (property)
├── create_llm(model_id: string) -> BaseChatModel
├── map_error(error: Exception) -> LLMServiceError
└── get_config() -> ProviderConfig
```

**Contract:**
- `create_llm()` must return a configured LangChain chat model instance
- `map_error()` must map any provider-specific exception to LLMServiceError
- `get_config()` must return the provider's configuration metadata

---

## State Transitions

### Provider Lifecycle

```
            ┌──────────────────┐
            │   REGISTERED     │
            │ (in registry)    │
            └────────┬─────────┘
                     │ check api_key
                     ▼
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐         ┌───────────────┐
│   ENABLED     │         │   DISABLED    │
│ (key present) │         │ (key missing) │
└───────┬───────┘         └───────────────┘
        │ create_llm()
        ▼
┌───────────────┐
│    ACTIVE     │
│ (LLM created) │
└───────┬───────┘
        │ error
        ▼
┌───────────────┐
│   ERRORED     │
│ (LLMServiceError)
└───────────────┘
```

---

## Registry Structure

### ProviderRegistry

Central registry for all available providers.

```
ProviderRegistry
├── providers: dict[string, BaseProvider]
├── register(provider_id: string, provider: BaseProvider) -> void
├── get(provider_id: string) -> BaseProvider | None
├── get_all() -> list[BaseProvider]
└── get_enabled() -> list[BaseProvider]
```

**Initialization:**
1. All providers are registered at module import time
2. Registry iterates providers to determine enabled status
3. Only enabled providers contribute to available models list

---

## Mapping Tables

### Error Category Mapping

Maps provider-specific exceptions to unified error categories.

| Provider Exception | Error Category | Notes |
|-------------------|----------------|-------|
| `openai.AuthenticationError` | authentication | API key invalid |
| `openai.RateLimitError` | rate_limit | Rate exceeded |
| `openai.APIConnectionError` | connection | Network issue |
| `openai.APITimeoutError` | timeout | Request timeout |
| `openai.BadRequestError` | invalid_request | Bad input |
| `anthropic.AuthenticationError` | authentication | API key invalid |
| `anthropic.RateLimitError` | rate_limit | Rate exceeded |
| `anthropic.APIConnectionError` | connection | Network issue |
| `anthropic.APITimeoutError` | timeout | Request timeout |
| `anthropic.BadRequestError` | invalid_request | Bad input |
| `anthropic.NotFoundError` | invalid_request | Model not found |
| `anthropic.PermissionDeniedError` | authentication | Permissions |
| `anthropic.InternalServerError` | internal | Server error |

---

## Migration Notes

### From Current Implementation

| Current | New | Change |
|---------|-----|--------|
| `PROVIDERS` dict in models.py | `ProviderRegistry` class | Encapsulated in registry |
| `load_openai_models()` | `OpenAIProvider.get_config()` | Moved to provider |
| `load_anthropic_models()` | `AnthropicProvider.get_config()` | Moved to provider |
| Exception handling in llm_service.py | `provider.map_error()` | Moved to provider |
| `get_llm_for_model()` if/elif | `registry.get(provider).create_llm()` | Registry lookup |

### Backward Compatibility

All existing public interfaces remain unchanged:
- `ModelConfig` schema unchanged
- API response formats unchanged
- Environment variable names unchanged
