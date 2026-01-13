# Quickstart: OpenAI Model Selector

**Feature**: 008-openai-model-selector
**Date**: 2026-01-11

## Prerequisites

- Existing SpecBot installation (feature 006-openai-langchain-chat completed)
- Valid OpenAI API key with access to desired models
- Node.js 18+ and Python 3.13+

## Configuration

### 1. Configure Available Models

Set the `OPENAI_MODELS` environment variable in `backend/.env`:

```bash
# Multi-model configuration (JSON array)
OPENAI_MODELS='[
  {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model for complex reasoning", "default": false},
  {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "Faster GPT-4 with latest knowledge", "default": false},
  {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient for most tasks", "default": true}
]'

# Keep existing key
OPENAI_API_KEY=sk-your-api-key-here
```

**Single Model Fallback**: If `OPENAI_MODELS` is not set, the system falls back to `OPENAI_MODEL` environment variable (existing behavior).

### 2. Start Backend

```bash
cd backend
source venv/bin/activate  # or equivalent for your OS
uvicorn main:app --reload --port 8000
```

### 3. Start Frontend

```bash
cd frontend
npm run dev
```

## Verification

### Test Models Endpoint

```bash
curl http://localhost:8000/api/v1/models
```

Expected response:
```json
{
  "models": [
    {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model for complex reasoning", "default": false},
    {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "Faster GPT-4 with latest knowledge", "default": false},
    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient for most tasks", "default": true}
  ]
}
```

### Test Model Selection

```bash
# With explicit model selection
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "model": "gpt-4"}'

# Response includes model field
# {"status": "success", "message": "...", "timestamp": "...", "model": "gpt-4"}
```

### Test Invalid Model

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "model": "invalid-model"}'

# Expected 400 error
# {"status": "error", "error": "Invalid model: invalid-model. Available models: gpt-4, gpt-4-turbo, gpt-3.5-turbo"}
```

### Test Frontend

1. Open http://localhost:5173
2. Verify model selector dropdown appears above input area
3. Select a model from the dropdown
4. Send a message
5. Verify response shows model indicator in message bubble
6. Refresh page - verify selected model persists

## Running Tests

### Backend Tests

```bash
cd backend
pytest tests/ -v

# Specific test files for this feature
pytest tests/unit/test_llm_service.py -v
pytest tests/integration/test_model_selection.py -v
pytest tests/contract/test_message_api_contract.py -v
```

### Frontend Tests

```bash
cd frontend
npm run test

# Specific test files for this feature
npm run test -- --grep "ModelSelector"
npm run test -- --grep "model selection"
```

### Contract Tests

```bash
# Backend contract validation
cd backend
pytest tests/contract/ -v

# Frontend contract capture
cd frontend
npm run test:contract
```

### E2E Tests

```bash
cd frontend
npm run test:e2e
```

## Troubleshooting

### "Invalid model" error

- Verify model ID matches exactly (case-sensitive)
- Check `OPENAI_MODELS` environment variable is valid JSON
- Ensure model is available in your OpenAI account

### Model selector not appearing

- Check browser console for JavaScript errors
- Verify `/api/v1/models` endpoint returns data
- Clear browser localStorage and refresh

### Model selection not persisting

- Check browser localStorage for `chatInterface:v1:data`
- Verify `selectedModelId` field is present
- Clear cache and try again

### "Service unavailable" on /api/v1/models

- Check `OPENAI_MODELS` is set and valid JSON
- Verify at least one model has `"default": true`
- Check backend logs for configuration errors

## Next Steps

After verification:

1. Run `/speckit.tasks` to generate implementation tasks
2. Implement according to thin-slice approach (P1 → P2 → P3)
3. Update architecture.md with model selection flow
4. Commit contract tests before implementation (TDD)
