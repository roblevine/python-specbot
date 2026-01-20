# Quickstart: Separate Provider Configurations

**Feature**: 018-separate-provider-configs
**Date**: 2026-01-20

## Overview

This guide explains how to configure models using the new provider-specific environment variables.

## Configuration Format

### Basic Setup

```bash
# API Keys (unchanged)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Provider-specific model lists (NEW)
OPENAI_MODELS='[
  {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model for complex reasoning"},
  {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient for most tasks"}
]'

ANTHROPIC_MODELS='[
  {"id": "claude-sonnet-4-5-20250929", "name": "Claude 4.5 Sonnet", "description": "Most capable Claude model"},
  {"id": "claude-haiku-4-5-20251001", "name": "Claude 4.5 Haiku", "description": "Fast and efficient"}
]'

# Default model (NEW - references model ID)
DEFAULT_MODEL=gpt-3.5-turbo
```

## Configuration Examples

### OpenAI Only

```bash
OPENAI_API_KEY=sk-...

OPENAI_MODELS='[
  {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model"},
  {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient"}
]'

DEFAULT_MODEL=gpt-4
```

### Anthropic Only

```bash
ANTHROPIC_API_KEY=sk-ant-...

ANTHROPIC_MODELS='[
  {"id": "claude-sonnet-4-5-20250929", "name": "Claude 4.5 Sonnet", "description": "Most capable"},
  {"id": "claude-haiku-4-5-20251001", "name": "Claude 4.5 Haiku", "description": "Fast and efficient"}
]'

DEFAULT_MODEL=claude-sonnet-4-5-20250929
```

### Multi-Provider

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

OPENAI_MODELS='[
  {"id": "gpt-4", "name": "GPT-4", "description": "OpenAI flagship model"}
]'

ANTHROPIC_MODELS='[
  {"id": "claude-sonnet-4-5-20250929", "name": "Claude 4.5 Sonnet", "description": "Anthropic flagship model"}
]'

# Default can be from any provider
DEFAULT_MODEL=claude-sonnet-4-5-20250929
```

### No Default Specified (Auto-Fallback)

```bash
OPENAI_API_KEY=sk-...

OPENAI_MODELS='[
  {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model"}
]'

# DEFAULT_MODEL not set - uses first available model (gpt-4)
```

## Migration from Old Format

### Before (Old Format)

```bash
MODELS='[
  {"id": "gpt-4", "name": "GPT-4", "description": "...", "provider": "openai", "default": false},
  {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "...", "provider": "openai", "default": true},
  {"id": "claude-sonnet", "name": "Claude Sonnet", "description": "...", "provider": "anthropic", "default": false}
]'
```

### After (New Format)

```bash
OPENAI_MODELS='[
  {"id": "gpt-4", "name": "GPT-4", "description": "..."},
  {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "..."}
]'

ANTHROPIC_MODELS='[
  {"id": "claude-sonnet", "name": "Claude Sonnet", "description": "..."}
]'

DEFAULT_MODEL=gpt-3.5-turbo
```

### Migration Checklist

1. [ ] Group models by `provider` field
2. [ ] Create `OPENAI_MODELS` with OpenAI models (remove `provider` and `default` fields)
3. [ ] Create `ANTHROPIC_MODELS` with Anthropic models (remove `provider` and `default` fields)
4. [ ] Set `DEFAULT_MODEL` to the ID of the model that had `"default": true`
5. [ ] Remove old `MODELS` environment variable
6. [ ] Test application startup

## Model Config Schema

Each model in a provider's list must have:

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `id` | string | Yes | Non-empty, unique across ALL providers |
| `name` | string | Yes | 1-50 characters |
| `description` | string | Yes | 1-200 characters |

**Note**: The `provider` and `default` fields are **not allowed** in the new format. Provider is inferred from the env var, default is specified separately.

## Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| "No AI providers configured" | No API keys set | Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` |
| "Invalid JSON in OPENAI_MODELS" | Malformed JSON | Check JSON syntax |
| "Duplicate model ID 'xxx' found" | Same ID in multiple providers | Use unique IDs across all providers |
| "Invalid DEFAULT_MODEL: 'xxx' not found" | DEFAULT_MODEL doesn't match any model ID | Set to a valid model ID |
| "No models available" | Provider configs empty or all providers disabled | Configure models for an enabled provider |

## Testing Configuration

For testing, use `.env.test`:

```bash
OPENAI_API_KEY=test-key

OPENAI_MODELS='[{"id": "test-model", "name": "Test", "description": "For testing"}]'

DEFAULT_MODEL=test-model
```
