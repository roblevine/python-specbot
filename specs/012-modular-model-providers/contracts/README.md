# API Contracts: Modular Model Providers

**Date**: 2026-01-16
**Feature**: 012-modular-model-providers

## Contract Status: UNCHANGED

This feature is an internal refactoring that does not modify any external API contracts.

### Preserved Contracts

The following API contracts remain unchanged and are verified by existing contract tests:

| Endpoint | Method | Contract Location |
|----------|--------|-------------------|
| `/api/v1/models` | GET | `backend/tests/contract/test_models_api_contract.py` |
| `/api/v1/messages` | POST | `backend/tests/contract/test_messages_api_contract.py` |

### Existing Contract Tests

All existing contract tests will be run during implementation to verify backward compatibility:

```bash
# Run contract tests
cd backend && pytest tests/contract/ -v
```

### What Changes

Only internal implementation changes:
- Provider initialization logic moved to provider classes
- Error handling consolidated in provider error mappers
- Configuration loading unified through provider registry

### What Does NOT Change

- Request/response schemas
- HTTP status codes
- Error response formats
- Environment variable names
- Model list structure in GET /api/v1/models
- Message format in POST /api/v1/messages

### Verification

Per FR-006 (Backward Compatibility), all existing contract tests must pass without modification to test assertions. Test setup may change if needed to accommodate the new provider structure.

## New Internal Contracts

While external APIs are unchanged, new internal contracts are introduced:

### BaseProvider Protocol

```python
from typing import Protocol
from langchain_core.language_models import BaseChatModel

class BaseProvider(Protocol):
    @property
    def provider_id(self) -> str: ...

    def create_llm(self, model_id: str) -> BaseChatModel: ...

    def map_error(self, error: Exception) -> LLMServiceError: ...

    def get_config(self) -> ProviderConfig: ...
```

This internal contract is enforced through Python's Protocol (PEP 544) and unit tests, not through API contract tests.
