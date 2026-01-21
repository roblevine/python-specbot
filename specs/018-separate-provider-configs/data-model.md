# Data Model: Separate Provider Configurations

**Feature**: 018-separate-provider-configs
**Date**: 2026-01-20

## Overview

This document defines the data models for the refactored model configuration system.

## Environment Variables (Input)

### Provider-Specific Model Lists

```bash
# OpenAI models (JSON array, optional if provider not used)
OPENAI_MODELS='[
  {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model"},
  {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient"}
]'

# Anthropic models (JSON array, optional if provider not used)
ANTHROPIC_MODELS='[
  {"id": "claude-sonnet-4-5-20250929", "name": "Claude 4.5 Sonnet", "description": "Most capable"},
  {"id": "claude-haiku-4-5-20251001", "name": "Claude 4.5 Haiku", "description": "Fast and efficient"}
]'

# Default model (plain string, optional - falls back to first available)
DEFAULT_MODEL=gpt-3.5-turbo
```

## Pydantic Models

### ProviderModelConfig (NEW - Simplified)

Represents a single model within a provider's configuration. No `provider` or `default` fields.

```python
class ProviderModelConfig(BaseModel):
    """Configuration for a single model within a provider."""

    id: str = Field(
        ...,
        description="Model identifier (e.g., 'gpt-4')",
        min_length=1
    )
    name: str = Field(
        ...,
        description="Human-readable display name",
        max_length=50,
        min_length=1
    )
    description: str = Field(
        ...,
        description="Brief model description",
        max_length=200,
        min_length=1
    )
```

**Validation Rules**:
- `id`: Non-empty string, whitespace trimmed
- `name`: 1-50 characters, whitespace trimmed
- `description`: 1-200 characters, whitespace trimmed

### ModelConfig (RETAINED - Internal/API)

Full model configuration used internally and in API responses. Includes computed `provider` and `default` fields.

```python
class ModelConfig(BaseModel):
    """Full model configuration with provider and default info."""

    id: str
    name: str
    description: str
    provider: Literal["openai", "anthropic"]
    default: bool = False
```

**Usage**: Created internally by merging `ProviderModelConfig` with provider ID and default status.

### ModelsConfiguration (RETAINED)

Root configuration containing all enabled models. Unchanged structure.

```python
class ModelsConfiguration(BaseModel):
    """Aggregated configuration for all available models."""

    models: List[ModelConfig] = Field(
        ...,
        min_length=1,
        description="List of available models from all providers"
    )
```

**Validation Rules**:
- At least one model must be present
- No duplicate model IDs across all models
- Exactly one model must have `default=True`

## Entity Relationships

```
┌─────────────────────────┐
│   Environment Variables │
├─────────────────────────┤
│ OPENAI_MODELS (JSON)    │──┐
│ ANTHROPIC_MODELS (JSON) │──┼──► Parse & Validate
│ DEFAULT_MODEL (string)  │──┘
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│  ProviderModelConfig[]  │  (per provider, simplified)
│  - id                   │
│  - name                 │
│  - description          │
└─────────────────────────┘
            │
            │ Merge with provider ID + default status
            ▼
┌─────────────────────────┐
│     ModelConfig[]       │  (aggregated, full info)
│  - id                   │
│  - name                 │
│  - description          │
│  - provider             │  ◄── Added from source env var
│  - default              │  ◄── Computed from DEFAULT_MODEL match
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│  ModelsConfiguration    │  (validated collection)
│  - models[]             │
└─────────────────────────┘
```

## State Transitions

### Configuration Loading Flow

```
1. INITIAL
   ↓
2. CHECK_PROVIDERS
   - Check OPENAI_API_KEY → openai_enabled
   - Check ANTHROPIC_API_KEY → anthropic_enabled
   - If neither enabled → ERROR: No providers configured
   ↓
3. LOAD_PROVIDER_CONFIGS
   - Parse OPENAI_MODELS (if openai_enabled)
   - Parse ANTHROPIC_MODELS (if anthropic_enabled)
   - If parse error → ERROR: Invalid JSON in {PROVIDER}_MODELS
   ↓
4. VALIDATE_MODELS
   - Validate each ProviderModelConfig
   - Collect all models with provider tag
   - Check for duplicate IDs → ERROR if found
   - If no models → ERROR: No models available
   ↓
5. RESOLVE_DEFAULT
   - Read DEFAULT_MODEL env var
   - If set and valid → mark that model as default
   - If set but invalid ID → ERROR: Invalid DEFAULT_MODEL
   - If set but provider disabled → WARN, use first available
   - If not set → use first model (alphabetical provider order)
   ↓
6. READY
   - Return ModelsConfiguration
```

## Validation Rules Summary

| Field | Rule | Error Message |
|-------|------|---------------|
| Model ID | Non-empty, unique across all providers | "Duplicate model ID '{id}' found" |
| Model name | 1-50 chars | "Model name must be 1-50 characters" |
| Model description | 1-200 chars | "Description must be 1-200 characters" |
| DEFAULT_MODEL | Must match existing model ID (if set) | "Invalid DEFAULT_MODEL: '{id}' not found" |
| Provider config | Valid JSON array | "Invalid JSON in {PROVIDER}_MODELS" |
| Overall | At least one model from enabled providers | "No models available for enabled providers" |

## Migration from Old Format

**Old Format** (MODELS env var):
```json
[
  {"id": "gpt-4", "name": "GPT-4", "description": "...", "provider": "openai", "default": false},
  {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "...", "provider": "openai", "default": true}
]
```

**New Format** (separate env vars):
```bash
OPENAI_MODELS='[
  {"id": "gpt-4", "name": "GPT-4", "description": "..."},
  {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "..."}
]'
DEFAULT_MODEL=gpt-3.5-turbo
```

**Migration Steps**:
1. Group models by `provider` field
2. Create `{PROVIDER}_MODELS` for each group
3. Remove `provider` and `default` fields from each model
4. Set `DEFAULT_MODEL` to the ID of the model that had `"default": true`
5. Remove old `MODELS` env var
