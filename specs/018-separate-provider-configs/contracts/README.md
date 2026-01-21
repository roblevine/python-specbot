# API Contracts: Separate Provider Configurations

**Feature**: 018-separate-provider-configs
**Date**: 2026-01-20

## Overview

This feature does **NOT** change the API contract. The `/api/v1/models` endpoint response format remains identical.

## Unchanged Endpoint

### GET /api/v1/models

**Response Format** (unchanged):

```json
{
  "models": [
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "description": "Most capable model for complex reasoning",
      "provider": "openai",
      "default": false
    },
    {
      "id": "gpt-3.5-turbo",
      "name": "GPT-3.5 Turbo",
      "description": "Fast and efficient for most tasks",
      "provider": "openai",
      "default": true
    },
    {
      "id": "claude-sonnet-4-5-20250929",
      "name": "Claude 4.5 Sonnet",
      "description": "Most capable Claude model for complex tasks",
      "provider": "anthropic",
      "default": false
    }
  ]
}
```

**Notes**:
- The `provider` field is still included in the response (computed from source env var)
- The `default` field is still included (computed from `DEFAULT_MODEL` match)
- Frontend code requires no changes
- Existing contract tests should pass without modification

## Contract Test Verification

The existing contract tests in `backend/tests/contract/test_models_api_contract.py` should continue to pass. The test configuration may need to be updated to use the new environment variable format, but the assertions remain the same.

## Why No Contract Changes

This feature changes the **internal configuration format** (how models are specified in environment variables), not the **external API contract** (how models are returned to clients).

The transformation happens at load time:
1. Read provider-specific env vars (`OPENAI_MODELS`, `ANTHROPIC_MODELS`)
2. Parse simplified model configs (no provider/default fields)
3. Add `provider` field from source env var name
4. Add `default` field based on `DEFAULT_MODEL` match
5. Return full model configs via API (same format as before)
