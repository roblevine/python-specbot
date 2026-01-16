# Research: Anthropic Claude Model Support

**Feature**: 011-anthropic-support
**Date**: 2026-01-15
**Phase**: 0 - Research

## Research Questions

### 1. LangChain ChatAnthropic Integration

**Question**: How does langchain-anthropic integrate with the existing LangChain architecture?

**Decision**: Use `langchain-anthropic` package with `ChatAnthropic` class

**Rationale**:
- `ChatAnthropic` follows the same `BaseChatModel` interface as `ChatOpenAI`
- Compatible `ainvoke()` and `astream()` methods for both sync and async operations
- Same message format (`HumanMessage`, `AIMessage`) works across providers
- LangChain handles provider-specific API differences internally

**Alternatives Considered**:
- Direct Anthropic SDK: Rejected - would require separate message handling, no streaming parity
- Custom abstraction layer: Rejected - LangChain already provides this, YAGNI principle

**Implementation Pattern**:
```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    api_key=api_key,
    model="claude-3-5-sonnet-20241022",
    timeout=120
)

# Same interface as ChatOpenAI
response = await llm.ainvoke(messages)
async for chunk in llm.astream(messages):
    yield chunk.content
```

### 2. Provider Configuration Strategy

**Question**: How should we configure multiple providers with separate API keys and model lists?

**Decision**: Separate environment variables per provider with unified model configuration

**Rationale**:
- `OPENAI_API_KEY` + `OPENAI_MODELS` (existing)
- `ANTHROPIC_API_KEY` + `ANTHROPIC_MODELS` (new)
- Providers are enabled based on API key presence
- Model configuration includes provider field for routing

**Alternatives Considered**:
- Single MODELS env var with provider in each model: Rejected - harder to manage credentials
- Config file instead of env vars: Rejected - would break existing deployment patterns

**Configuration Schema**:
```json
// ANTHROPIC_MODELS environment variable
[
  {
    "id": "claude-3-5-sonnet-20241022",
    "name": "Claude 3.5 Sonnet",
    "description": "Most capable Claude model for complex tasks",
    "provider": "anthropic",
    "default": true
  },
  {
    "id": "claude-3-haiku-20240307",
    "name": "Claude 3 Haiku",
    "description": "Fast and efficient for simple tasks",
    "provider": "anthropic",
    "default": false
  }
]
```

### 3. Provider Routing Architecture

**Question**: How should the LLM service route requests to the correct provider?

**Decision**: Factory pattern based on model's provider field

**Rationale**:
- Model configuration includes `provider` field
- LLM service looks up provider from model ID
- Creates appropriate LangChain instance (ChatOpenAI or ChatAnthropic)
- Error handling maps provider-specific exceptions to common types

**Implementation Pattern**:
```python
def get_llm_for_model(model_id: str, config: ModelsConfiguration):
    model = get_model_by_id(model_id, config)

    if model.provider == "openai":
        return ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'), model=model_id)
    elif model.provider == "anthropic":
        return ChatAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'), model=model_id)
    else:
        raise ValueError(f"Unsupported provider: {model.provider}")
```

### 4. Anthropic Error Mapping

**Question**: How do Anthropic API errors map to our existing error types?

**Decision**: Map anthropic exceptions to existing LLMServiceError hierarchy

**Rationale**:
- Anthropic uses similar error patterns: AuthenticationError, RateLimitError, etc.
- Import from `anthropic` package (installed as dependency of langchain-anthropic)
- Map to same user-friendly messages as OpenAI errors

**Error Mapping**:
| Anthropic Exception | LLM Service Error | HTTP Code |
|---------------------|-------------------|-----------|
| `AuthenticationError` | `LLMAuthenticationError` | 503 |
| `RateLimitError` | `LLMRateLimitError` | 503 |
| `APIConnectionError` | `LLMConnectionError` | 503 |
| `APITimeoutError` | `LLMTimeoutError` | 504 |
| `BadRequestError` | `LLMBadRequestError` | 400 |

### 5. Frontend Provider Display

**Question**: How should the UI display provider information in the model selector?

**Decision**: Show provider as prefix label in dropdown options

**Rationale**:
- Clear visual distinction between providers
- Consistent with common multi-provider UI patterns
- Minimal UI changes required

**Display Format**:
```
OpenAI: GPT-4 — Most capable model for complex tasks
OpenAI: GPT-3.5 Turbo — Fast and efficient
Anthropic: Claude 3.5 Sonnet — Most capable Claude model
Anthropic: Claude 3 Haiku — Fast and efficient
```

### 6. Model Locking Mechanism

**Question**: How should the frontend enforce model locking after conversation starts?

**Decision**: Disable model selector when conversation has messages

**Rationale**:
- Simple boolean check: `hasMessages` from conversation state
- Model selector `disabled` attribute already supported
- No backend changes needed for enforcement (frontend-only)

**Implementation**:
```vue
<select
  :disabled="isLoading || availableModels.length === 0 || hasActiveMessages"
  ...
>
```

## Dependencies

### Required Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `langchain-anthropic` | ^0.2.0 | Anthropic Claude integration |
| `anthropic` | ^0.34.0 | Installed as dependency (error types) |

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | No* | Anthropic API key. If not set, Anthropic models hidden |
| `ANTHROPIC_MODELS` | No* | JSON array of Anthropic model configurations |

*At least one provider (OpenAI or Anthropic) must be configured.

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Streaming behavior differs between providers | Low | Medium | LangChain abstracts this; test both providers |
| API key validation timing | Low | Low | Validate on startup, cache validation result |
| Model ID collision between providers | Very Low | High | Provider field ensures uniqueness |

## Next Steps

1. **Phase 1**: Generate data-model.md with extended ModelConfig schema
2. **Phase 1**: Generate API contracts for models endpoint with provider field
3. **Phase 1**: Create quickstart.md for Anthropic setup
