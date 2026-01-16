# Quickstart: Modular Model Providers

**Date**: 2026-01-16
**Feature**: 012-modular-model-providers

## Overview

This guide explains how to work with the new provider abstraction layer after implementation.

---

## Adding a New Provider

### Step 1: Create Provider Class

Create a new file in `backend/src/services/providers/`:

```python
# backend/src/services/providers/newprovider.py
from langchain_newprovider import ChatNewProvider
from newprovider import AuthenticationError, RateLimitError  # etc.

from .base import BaseProvider, ProviderConfig
from .errors import map_to_llm_error

class NewProvider(BaseProvider):
    @property
    def provider_id(self) -> str:
        return "newprovider"

    def create_llm(self, model_id: str) -> BaseChatModel:
        api_key = os.getenv(self.get_config().api_key_env)
        return ChatNewProvider(
            api_key=api_key,
            model=model_id,
            timeout=120,
        )

    def map_error(self, error: Exception) -> LLMServiceError:
        # Map provider-specific exceptions
        error_map = {
            AuthenticationError: "authentication",
            RateLimitError: "rate_limit",
            # ... add other mappings
        }
        return map_to_llm_error(error, error_map, self.provider_id)

    def get_config(self) -> ProviderConfig:
        return ProviderConfig(
            id="newprovider",
            name="New Provider",
            api_key_env="NEWPROVIDER_API_KEY",
            models_env="NEWPROVIDER_MODELS",
        )
```

### Step 2: Register Provider

Add to the registry in `backend/src/services/providers/__init__.py`:

```python
from .newprovider import NewProvider

# In the registration section:
register_provider("newprovider", NewProvider())
```

### Step 3: Configure Environment

Add environment variables:

```bash
# .env
NEWPROVIDER_API_KEY=your-api-key
NEWPROVIDER_MODELS=model-1,model-2,model-3
```

### Step 4: Add Tests

Create test file in `backend/tests/unit/providers/test_newprovider.py`:

```python
import pytest
from src.services.providers.newprovider import NewProvider

class TestNewProvider:
    def test_provider_id(self):
        provider = NewProvider()
        assert provider.provider_id == "newprovider"

    def test_create_llm_requires_api_key(self):
        # Test initialization

    def test_map_authentication_error(self):
        # Test error mapping
```

### Step 5: Verify

Run tests to ensure everything works:

```bash
cd backend && pytest tests/ -v
```

---

## Provider Interface Reference

### BaseProvider Protocol

All providers must implement:

| Method | Returns | Description |
|--------|---------|-------------|
| `provider_id` | `str` | Unique identifier for the provider |
| `create_llm(model_id)` | `BaseChatModel` | Create configured LangChain chat model |
| `map_error(error)` | `LLMServiceError` | Map provider error to unified error |
| `get_config()` | `ProviderConfig` | Return provider configuration metadata |

### ProviderConfig Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique identifier (matches `provider_id`) |
| `name` | `str` | Human-readable display name |
| `api_key_env` | `str` | Environment variable for API key |
| `models_env` | `str` | Environment variable for models list |

### LLMServiceError Categories

| Category | HTTP Status | Use Case |
|----------|-------------|----------|
| `authentication` | 401 | Invalid/missing API key |
| `rate_limit` | 429 | Too many requests |
| `connection` | 503 | Cannot reach provider |
| `timeout` | 504 | Request timed out |
| `invalid_request` | 400 | Bad request format |
| `internal` | 500 | Unexpected error |

---

## Testing

### Run All Tests

```bash
# Backend tests
cd backend && pytest tests/ -v

# Contract tests (verify backward compatibility)
cd backend && pytest tests/contract/ -v

# Frontend tests
cd frontend && npm test
```

### Test Coverage

```bash
cd backend && pytest tests/ --cov=src --cov-report=html
```

---

## Troubleshooting

### Provider Not Appearing in Models List

1. Check API key is set: `echo $PROVIDER_API_KEY`
2. Check models env is set: `echo $PROVIDER_MODELS`
3. Check provider is registered in `providers/__init__.py`
4. Check server logs for "Provider X disabled: missing API key" message

### Error Responses Not Consistent

1. Verify `map_error()` handles all provider-specific exceptions
2. Check error mapping returns correct category
3. Run error mapping tests: `pytest tests/unit/providers/test_errors.py -v`

### Existing Tests Failing

1. Ensure you haven't changed any public API contracts
2. Run contract tests: `pytest tests/contract/ -v`
3. Check for import path changes in test setup
