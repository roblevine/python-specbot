# Research: Modular Model Providers

**Date**: 2026-01-16
**Feature**: 012-modular-model-providers
**Status**: Complete

## Executive Summary

This research documents the current provider implementation, identifies consolidation opportunities, and recommends the provider pattern approach for this refactoring feature.

---

## Research Item 1: Current Provider Implementation Analysis

### Question
What is the current state of provider handling in the codebase, and what specific duplication exists?

### Findings

**Current Architecture:**

| Component | Location | Purpose |
|-----------|----------|---------|
| Configuration | `backend/src/config/models.py` | Provider registry, model schemas, configuration loading |
| LLM Service | `backend/src/services/llm_service.py` | Provider-agnostic interface for LLM calls |
| API Routes | `backend/src/api/routes/models.py`, `messages.py` | HTTP endpoints |

**Identified Duplication:**

1. **Exception Handling (~90 lines duplicated)**
   - `get_ai_response()` (lines 331-375): Catches provider-specific exceptions
   - `stream_ai_response()` (lines 465-554): Nearly identical exception handling
   - Both handle: AuthenticationError, RateLimitError, APIConnectionError, APITimeoutError, BadRequestError
   - Anthropic-specific extras: NotFoundError, PermissionDeniedError, InternalServerError

2. **LLM Initialization (lines 148-171)**
   - OpenAI: Creates ChatOpenAI with api_key, model, timeout, request_timeout
   - Anthropic: Creates ChatAnthropic with api_key, model, timeout (no request_timeout)
   - Nearly identical structure, only class name and params differ

3. **Configuration Loading (lines 181-198)**
   - `load_openai_models()` → `_load_models_from_env("OPENAI_MODELS", "openai")`
   - `load_anthropic_models()` → `_load_models_from_env("ANTHROPIC_MODELS", "anthropic")`
   - Both are 1-line wrappers calling the same helper

**Quantified Impact:**
- Total duplicated lines: ~150-200
- Exception handling alone: ~90 lines
- Reduction potential: 40-50% of provider-related code

### Decision
Proceed with provider abstraction to eliminate duplication and improve maintainability.

### Rationale
The duplication is significant enough (40%+ reduction potential) to justify the abstraction layer, especially given the stated intent to add more providers.

---

## Research Item 2: Provider Pattern Best Practices

### Question
What are the best practices for implementing a provider pattern in Python with LangChain?

### Findings

**Recommended Pattern: Registry + Abstract Base Class**

```python
# Abstract interface
class BaseProvider(ABC):
    @abstractmethod
    def create_llm(self, model_id: str) -> BaseChatModel:
        """Create LLM instance for given model."""
        pass

    @abstractmethod
    def map_error(self, error: Exception) -> LLMServiceError:
        """Map provider-specific error to unified error."""
        pass

    @abstractmethod
    def get_config(self) -> ProviderConfig:
        """Return provider configuration metadata."""
        pass

# Registry pattern
PROVIDER_REGISTRY: dict[str, BaseProvider] = {}

def register_provider(provider_id: str, provider: BaseProvider):
    PROVIDER_REGISTRY[provider_id] = provider

def get_provider(provider_id: str) -> BaseProvider:
    return PROVIDER_REGISTRY[provider_id]
```

**Why This Pattern:**
1. **Open/Closed Principle**: New providers added without modifying existing code
2. **Single Responsibility**: Each provider encapsulates its own logic
3. **Testability**: Providers can be mocked/tested independently
4. **Discoverability**: Registry shows all available providers

**Alternatives Considered:**

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Registry + ABC | Clean interface, extensible, testable | Slight indirection | ✅ CHOSEN |
| Factory function with dict | Simple, no ABC needed | Less type safety | Rejected |
| Plugin system | Maximum flexibility | Over-engineered for 2-3 providers | Rejected |
| Continue if/elif | No new abstractions | Grows with each provider | Rejected |

### Decision
Use Registry + Abstract Base Class pattern with Protocol (PEP 544) for type hints.

### Rationale
Provides the right balance of extensibility and simplicity. The abstract base ensures all providers implement required methods, while the registry enables dynamic lookup.

---

## Research Item 3: LangChain Provider Capabilities

### Question
Does LangChain provide capability detection or unified error handling that we can leverage?

### Findings

**What LangChain Provides:**
- Unified interface: `BaseChatModel` with `invoke()`, `ainvoke()`, `stream()`, `astream()`
- Message normalization: `HumanMessage`, `AIMessage`, `SystemMessage`
- Consistent async patterns across providers

**What LangChain Does NOT Provide:**
- Capability detection (no "does this model support vision?" query)
- Unified error handling (each provider throws its own exceptions)
- Provider-agnostic initialization (each has different parameters)

**Exception Types by Provider:**

| Error Type | OpenAI | Anthropic |
|------------|--------|-----------|
| AuthenticationError | ✅ | ✅ |
| RateLimitError | ✅ | ✅ |
| APIConnectionError | ✅ | ✅ |
| APITimeoutError | ✅ | ✅ |
| BadRequestError | ✅ | ✅ |
| NotFoundError | ❌ | ✅ |
| PermissionDeniedError | ❌ | ✅ |
| InternalServerError | ❌ | ✅ |

**Initialization Parameter Differences:**

| Parameter | OpenAI | Anthropic |
|-----------|--------|-----------|
| api_key | Required | Required |
| model | Required | Required |
| timeout | Optional | Optional |
| request_timeout | Optional | Not supported |
| temperature | 0-2 range | 0-1 range |

### Decision
Build our own error mapping layer on top of LangChain's abstractions.

### Rationale
LangChain's interface is stable and well-designed, but error handling must be implemented at our layer since LangChain doesn't normalize exceptions.

---

## Research Item 4: Backward Compatibility Strategy

### Question
How do we ensure existing tests and API contracts continue to work?

### Findings

**API Contracts (MUST be preserved):**
- `GET /api/v1/models` - Returns list of available models with provider info
- `POST /api/v1/messages` - Sends message, returns AI response (streaming/non-streaming)

**Existing Tests:**
- `test_models_api_contract.py` - Contract tests for models endpoint
- `test_llm_service.py` - Unit tests for LLM service
- `test_model_config.py` - Configuration tests
- `test_model_selection.py` - Integration tests

**Strategy:**
1. Run all existing tests before refactoring to establish baseline
2. Implement provider abstraction without changing public interfaces
3. Run all existing tests after refactoring - they MUST pass without modification
4. Add new tests for provider interface and registry

### Decision
Refactoring is strictly internal; all public interfaces remain unchanged.

### Rationale
FR-006 explicitly requires preserving existing API contracts. The refactoring improves internal structure without affecting external behavior.

---

## Research Item 5: Error Mapping Design

### Question
How should provider-specific errors be mapped to unified service errors?

### Findings

**Current Error Categories in LLMServiceError:**

| Category | HTTP Status | Description |
|----------|-------------|-------------|
| authentication | 401 | API key invalid or missing |
| rate_limit | 429 | Too many requests |
| connection | 503 | Cannot reach provider |
| timeout | 504 | Request timed out |
| invalid_request | 400 | Malformed request |
| internal | 500 | Unexpected error |

**Proposed Mapping:**

```python
ERROR_CATEGORY_MAP = {
    # Common to all providers
    "AuthenticationError": "authentication",
    "RateLimitError": "rate_limit",
    "APIConnectionError": "connection",
    "APITimeoutError": "timeout",
    "BadRequestError": "invalid_request",

    # Anthropic-specific (map to closest generic)
    "NotFoundError": "invalid_request",
    "PermissionDeniedError": "authentication",
    "InternalServerError": "internal",
}
```

### Decision
Create unified error mapping with explicit category assignments.

### Rationale
Consistent error responses (SC-005) require deterministic mapping from provider errors to our error categories.

---

## Summary of Decisions

| Research Item | Decision | Impact |
|---------------|----------|--------|
| Current Implementation | Confirmed ~150-200 lines of duplication | Validates need for refactoring |
| Provider Pattern | Registry + Abstract Base Class | Architecture foundation |
| LangChain Capabilities | Build error mapping layer | Custom implementation required |
| Backward Compatibility | Preserve all public interfaces | No breaking changes |
| Error Mapping | Unified category mapping | Consistent error responses |

## Next Steps

1. **Phase 1**: Design data model and contracts
2. **Implementation**: Follow thin slice approach per constitution
3. **Validation**: Run all existing tests after each slice
