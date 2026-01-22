# Quickstart: Add Ollama Model Support

**Feature**: 020-add-ollama-support
**Date**: 2026-01-22

## Prerequisites

1. **Ollama installed**: Download from https://ollama.com
2. **At least one model pulled**: `ollama pull llama2`
3. **Ollama server running**: `ollama serve` (usually starts automatically)

## Setup Steps

### 1. Install New Dependency

```bash
cd backend
pip install langchain-ollama>=0.2.0
```

Or add to `requirements.txt`:
```
langchain-ollama>=0.2.0
```

### 2. Configure Environment

Add to `backend/.env`:

```bash
# Ollama Models
OLLAMA_MODELS='[
  {"id": "llama2", "name": "Llama 2", "description": "Meta's Llama 2 7B model"}
]'

# Optional: Custom Ollama server URL (default: http://localhost:11434)
# OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Verify Ollama Server

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Expected response: {"models":[{"name":"llama2",...}]}
```

### 4. Start Backend

```bash
cd backend
python -m uvicorn src.main:app --reload
```

### 5. Verify Integration

```bash
# Check models endpoint includes Ollama
curl http://localhost:8000/api/v1/models | jq

# Expected: Ollama models listed with provider: "ollama"
```

## Configuration Examples

### Minimal (Ollama only)

```bash
OLLAMA_MODELS='[{"id": "llama2", "name": "Llama 2", "description": "Local Llama 2"}]'
DEFAULT_MODEL=llama2
```

### Mixed Providers

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODELS='[{"id": "gpt-4", "name": "GPT-4", "description": "OpenAI GPT-4"}]'

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODELS='[{"id": "claude-3-sonnet", "name": "Claude 3", "description": "Anthropic Claude"}]'

# Ollama (local)
OLLAMA_MODELS='[{"id": "llama2", "name": "Llama 2", "description": "Local Llama 2"}]'

# Default to local model
DEFAULT_MODEL=llama2
```

### Remote Ollama Server

```bash
OLLAMA_MODELS='[{"id": "llama2", "name": "Llama 2", "description": "Remote Llama 2"}]'
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

## Testing

### Unit Tests

```bash
cd backend
pytest tests/unit/test_ollama_provider.py -v
pytest tests/unit/test_model_config.py -v -k ollama
```

### Manual Testing

1. Start Ollama: `ollama serve`
2. Start backend: `uvicorn src.main:app --reload`
3. Start frontend: `npm run dev`
4. Select Ollama model in model selector
5. Send a message and verify response

### Testing Without Ollama Server

To test error handling:

1. Configure Ollama models in `.env`
2. Stop Ollama server: `pkill ollama`
3. Send a message → expect connection error

## Troubleshooting

### "Unable to reach local Ollama server"

- Check Ollama is running: `ollama serve`
- Verify URL: `curl http://localhost:11434/api/tags`
- Check `OLLAMA_BASE_URL` if using custom port

### "Model not found in Ollama"

- List available models: `ollama list`
- Pull missing model: `ollama pull <model-name>`
- Ensure model ID in config matches Ollama exactly

### Models not appearing in selector

- Verify `OLLAMA_MODELS` env var is set
- Check JSON syntax is valid
- Restart backend after config changes

## Files Modified

| File | Change |
|------|--------|
| `backend/requirements.txt` | Add `langchain-ollama>=0.2.0` |
| `backend/src/services/providers/base.py` | Optional `api_key_env` in ProviderConfig |
| `backend/src/services/providers/ollama.py` | NEW: OllamaProvider class |
| `backend/src/services/providers/errors.py` | Add `map_ollama_error()` |
| `backend/src/services/providers/__init__.py` | Register OllamaProvider |
| `backend/src/config/models.py` | Add Ollama to PROVIDERS, extend Literal type |
| `backend/.env.example` | Add Ollama configuration examples |
