# Research: Separate Provider Configurations

**Feature**: 018-separate-provider-configs
**Date**: 2026-01-20

## Overview

This document captures research decisions for refactoring the model configuration system from a unified `MODELS` env var to separate provider-specific variables.

## Research Topics

### 1. Provider-Specific Environment Variable Naming

**Decision**: Use `{PROVIDER}_MODELS` pattern (`OPENAI_MODELS`, `ANTHROPIC_MODELS`)

**Rationale**:
- Consistent with existing API key naming (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`)
- Clear association between provider and its models
- Easy to extend for future providers (e.g., `GOOGLE_MODELS`)
- Supports shell tab-completion (all OpenAI vars start with `OPENAI_`)

**Alternatives Considered**:
- `MODELS_OPENAI` / `MODELS_ANTHROPIC` - Rejected: inconsistent with API key pattern
- `LLM_OPENAI_MODELS` - Rejected: unnecessarily verbose

### 2. Default Model Reference Strategy

**Decision**: Use single `DEFAULT_MODEL` env var containing model ID string

**Rationale**:
- Simple scalar value (not JSON)
- Decouples default selection from model definitions
- Can be changed independently without editing model configs
- Model ID is unique across all providers (validated)

**Alternatives Considered**:
- `DEFAULT_PROVIDER` + `DEFAULT_MODEL_ID` - Rejected: over-complicated, provider can be inferred from model ID
- Automatic first-model default - Kept as fallback, but explicit `DEFAULT_MODEL` preferred

**Fallback Behavior**:
1. If `DEFAULT_MODEL` set to valid, available model → use it
2. If `DEFAULT_MODEL` set but model's provider disabled → warn, use first available
3. If `DEFAULT_MODEL` set to invalid ID → error at startup
4. If `DEFAULT_MODEL` not set → use first model from first available provider

### 3. Provider Ordering for Fallback

**Decision**: Alphabetical order (anthropic, openai)

**Rationale**:
- Deterministic and predictable
- No implicit preference for any provider
- Easy to understand and document

**Implementation**: Sort provider IDs alphabetically when iterating

### 4. Duplicate Model ID Validation

**Decision**: Reject configuration if any model ID appears in multiple provider configs

**Rationale**:
- Model IDs must be globally unique for `DEFAULT_MODEL` reference to work
- Prevents ambiguity in `get_model_by_id()` and `get_provider_for_model()`
- Clear error message helps users fix configuration

**Error Message Format**:
```
Duplicate model ID 'gpt-4' found in both OPENAI_MODELS and ANTHROPIC_MODELS.
Model IDs must be unique across all providers.
```

### 5. Legacy MODELS Variable Handling

**Decision**: Silently ignore if present

**Rationale**:
- Per clarification: no backward compatibility required
- Logging a warning would add noise for users who haven't cleaned up
- No error because it's not a configuration mistake (just unused)

**Alternatives Considered**:
- Log deprecation warning - Rejected: adds noise, no transition period anyway
- Error if present - Rejected: too aggressive for unused variable
- Use as fallback - Rejected: explicitly ruled out in clarification

### 6. Empty Provider Configuration Handling

**Decision**: Empty array `[]` is valid, provider just has no models

**Rationale**:
- Allows explicit "I have no models for this provider" configuration
- Consistent with "provider disabled if no API key" behavior
- Other providers can still provide models

**Example**:
```bash
OPENAI_MODELS='[]'  # Valid: OpenAI has no models configured
ANTHROPIC_MODELS='[{"id": "claude-3", "name": "Claude 3", "description": "..."}]'
DEFAULT_MODEL=claude-3
```

### 7. Pydantic Model Simplification

**Decision**: Remove `provider` and `default` fields from `ModelConfig`

**Rationale**:
- `provider` is implicit from the env var source
- `default` is specified separately in `DEFAULT_MODEL`
- Simpler model with fewer fields to maintain
- Less opportunity for configuration errors

**New ModelConfig Fields**:
- `id`: str (required)
- `name`: str (required, max 50 chars)
- `description`: str (required, max 200 chars)

### 8. API Response Preservation

**Decision**: `/api/v1/models` response format unchanged

**Rationale**:
- Frontend depends on `provider` and `default` fields
- Breaking API would require frontend changes (out of scope)
- Provider info is added at response time from internal data

**Implementation**: Aggregate models from all providers, add `provider` field from source, calculate `default` from `DEFAULT_MODEL` match.

## Summary

| Topic | Decision |
|-------|----------|
| Env var naming | `{PROVIDER}_MODELS` pattern |
| Default reference | `DEFAULT_MODEL` env var with model ID |
| Provider order | Alphabetical for deterministic fallback |
| Duplicate IDs | Reject with clear error |
| Legacy MODELS | Silently ignore |
| Empty provider | Valid (no models for that provider) |
| ModelConfig fields | Simplified: id, name, description only |
| API response | Format unchanged (add provider/default at response time) |
