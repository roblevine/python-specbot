# python-specbot Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-12

## Active Technologies
- JavaScript (ES6+), Vue 3.4.0 + Vue 3 (Composition API), Vite 5.0.0 (002-new-conversation-button)
- LocalStorage (via existing storage utilities in `frontend/src/storage/`) (002-new-conversation-button)
- Python 3.13 (confirmed in devcontainer) + FastAPI 0.115.0, uvicorn (ASGI server), Pydantic (validation) (003-backend-api-loopback)
- N/A (backend is stateless for loopback; frontend LocalStorage persists conversations) (003-backend-api-loopback)
- JavaScript ES6+ (Frontend), Python 3.13 (Backend) (005-chat-error-display)
- Browser LocalStorage (versioned schema v1.0.0 → v1.1.0) (005-chat-error-display, 008-openai-model-selector)
- Python 3.13 (backend), JavaScript ES6+ (frontend) + FastAPI 0.115.0, LangChain, langchain-openai, Vue 3.4.0, Vite 5.0.0 (006-openai-langchain-chat)
- LocalStorage (frontend, existing), N/A for backend (stateless) (006-openai-langchain-chat)
- Browser LocalStorage (schema v1.1.0) - no changes required for streaming (009-message-streaming)
- Python 3.11 (backend), JavaScript ES6+ (frontend) + FastAPI 0.115.0, Pydantic 2.10.0, Vue 3.4.0, Vite 5.0.0 (010-server-side-conversations)
- File-based JSON storage with abstraction layer for future database migration (010-server-side-conversations)
- Python 3.13 (backend), JavaScript ES6+ (frontend) + FastAPI 0.115.0, LangChain, langchain-openai, langchain-anthropic, Vue 3.4.0, Vite 5.0.0 (011-anthropic-support)
- File-based JSON storage (existing), Browser LocalStorage (frontend) (011-anthropic-support)
- Python 3.13 (backend), JavaScript ES6+ (frontend) + FastAPI 0.115.0, Pydantic 2.10.0, LangChain 0.3+, langchain-openai 0.2+, langchain-anthropic 0.2+, Vue 3.4.0, Vite 5.0.0 (012-modular-model-providers)
- File-based JSON storage (unchanged by this feature) (012-modular-model-providers)
- JavaScript (ES6+) + Vue 3.4.0, Vite 5.0.0 (013-redesign-frontend-palette)
- N/A (styling changes only) (013-redesign-frontend-palette)
- JavaScript (ES6+) for frontend, Python 3.13 for backend + Vue 3.4.0, Vite 5.0.0, FastAPI 0.115.0 (014-conversation-titles)
- Browser LocalStorage (frontend), File-based JSON (backend) - both already support title field (014-conversation-titles)
- 015-ux-refinements: Added JavaScript ES6+ (Frontend), Python 3.13 (Backend - no changes) + Vue 3.4.0, Vite 5.0.0
- 014-conversation-titles: Added JavaScript (ES6+) for frontend, Python 3.13 for backend + Vue 3.4.0, Vite 5.0.0, FastAPI 0.115.0
- 013-redesign-frontend-palette: Added JavaScript (ES6+) + Vue 3.4.0, Vite 5.0.0
- JavaScript ES6+ (Frontend) + Vue 3.4.0, Vite 5.0.0, marked (markdown parser - to be added), DOMPurify (XSS sanitization - to be added), highlight.js (syntax highlighting - to be added) (017-markdown-support)
- N/A (no storage changes - markdown rendered at display time) (017-markdown-support)
- JavaScript ES6+ + Vue 3.4.0, Vite 5.0.0 (018-audit-local-storage)
- Browser localStorage (settings only) (018-audit-local-storage)
- Python 3.13 (confirmed in devcontainer) + FastAPI 0.115.0, Pydantic 2.10.0, LangChain 0.3+ (018-separate-provider-configs)
- N/A (configuration only, file-based JSON storage unchanged) (018-separate-provider-configs)
- Python 3.13 (confirmed in devcontainer) + FastAPI 0.115.0, LangChain 0.3+, langchain-ollama (new dependency), Pydantic 2.10.0 (020-add-ollama-support)
- N/A (stateless provider, uses existing model configuration infrastructure) (020-add-ollama-support)
- JavaScript ES6+ (Frontend), Python 3.13 (Backend - minimal changes) + Vue 3.4.0, Vite 5.0.0, FastAPI 0.115.0, Pydantic 2.10.0 (021-disable-model-selector)
- File-based JSON (backend conversations), Browser localStorage (settings only) (021-disable-model-selector)
- JavaScript ES6+ (Frontend only) + Vue 3.4.0, Vite 5.0.0 (022-conversation-ux-fixes)
- N/A (no storage changes - uses existing `updatedAt` field from server) (022-conversation-ux-fixes)
- Python 3.13 (backend), JavaScript ES6+ (frontend) + FastAPI 0.115.0, LangChain 0.3+, langchain-openai 0.2+, langchain-anthropic 0.2+, langchain-ollama 0.2+, Vue 3.4.0, Vite 5.0.0 (024-add-langchain-tools)
- File-based JSON with schema versioning (v1.0.0 → v1.1.0 for tool calls) (024-add-langchain-tools)

### 009-message-streaming (2026-01-14) ✅ MVP COMPLETE
**Real-time LLM response streaming with Server-Sent Events (SSE)**

**Status**: User Story 1 (MVP) complete and production-ready

**Backend Implementation**:

**Frontend Implementation**:

**Error Handling & Robustness** (Bonus improvements beyond spec):

**Testing**:

**Key Files Modified**:

**Critical Bug Fixes**:

**Remaining Work** (Optional enhancements):

**How to Use**:
```javascript
// Frontend API call
import { streamMessage } from './services/apiClient.js'

streamMessage(
  messageText,
  (token) => console.log('Token:', token),           // onToken
  (metadata) => console.log('Complete:', metadata),  // onComplete
  (error) => console.error('Error:', error),         // onError
  conversationHistory,                                // history
  selectedModelId                                     // model
)
```

**Backend SSE format**:
```
data: {"type":"token","content":"Hello"}

data: {"type":"token","content":" world"}

data: {"type":"complete","model":"gpt-3.5-turbo","totalTokens":2}
```

### 008-openai-model-selector
Added model configuration system (Pydantic validation), GET /api/v1/models endpoint, ModelSelector component with descriptions, model indicators on messages, localStorage v1.1.0 schema with selectedModelId, per-request model selection

### 018-separate-provider-configs (2026-01-20) ✅ COMPLETE
**Separate provider model configurations with simplified format**

**What Changed**:
- Model configs now use provider-specific env vars: `OPENAI_MODELS`, `ANTHROPIC_MODELS`
- Each model only needs: `id`, `name`, `description` (no `provider` or `default` fields)
- Provider is inferred from which env var the model is defined in
- Default model specified via `DEFAULT_MODEL` env var (model ID string)
- Legacy `MODELS` env var is silently ignored

**Configuration Example**:
```bash
OPENAI_MODELS='[{"id": "gpt-4", "name": "GPT-4", "description": "Most capable"}]'
ANTHROPIC_MODELS='[{"id": "claude-sonnet", "name": "Claude Sonnet", "description": "Fast"}]'
DEFAULT_MODEL=gpt-4
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Key Files**:
- `backend/src/config/models.py` - Core model loading with `load_provider_models()`, `load_model_configuration()`
- `backend/.env.example` - Updated with new format and migration guide
- `backend/tests/unit/test_model_config.py` - Comprehensive tests for new format

**API Contract**: Unchanged - `/api/v1/models` response format preserved for frontend compatibility

### 020-add-ollama-support (2026-01-22) ✅ COMPLETE
**Local Ollama model support via LangChain**

**What Changed**:
- Added Ollama as a third provider alongside OpenAI and Anthropic
- Ollama doesn't require an API key (local server)
- Models configured via `OLLAMA_MODELS` env var (same format as other providers)
- Optional `OLLAMA_BASE_URL` for custom server locations (default: `http://localhost:11434`)
- Clear error messages when Ollama server is unavailable

**Configuration Example**:
```bash
# Ollama Models (no API key required)
OLLAMA_MODELS='[{"id": "llama2", "name": "Llama 2", "description": "Meta's Llama 2 7B model"}]'

# Optional: Custom Ollama server URL
OLLAMA_BASE_URL=http://192.168.1.100:11434

# Can coexist with cloud providers
DEFAULT_MODEL=llama2
```

**Key Files**:
- `backend/src/services/providers/ollama.py` - OllamaProvider class
- `backend/src/services/providers/errors.py` - `map_ollama_error()` for connection/timeout handling
- `backend/src/config/models.py` - Extended PROVIDERS, Literal type, check_provider_enabled()
- `backend/tests/unit/test_ollama_provider.py` - Comprehensive tests

**Prerequisites**:
1. Install Ollama: https://ollama.com
2. Pull a model: `ollama pull llama2`
3. Start server: `ollama serve` (usually auto-starts)

**API Contract**: Unchanged - Ollama models appear with `provider: "ollama"` in `/api/v1/models`

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

## Recent Changes
- 020-add-ollama-support: Added Ollama provider for local LLM support (langchain-ollama, OLLAMA_MODELS, OLLAMA_BASE_URL)
- 018-separate-provider-configs: Refactored model configuration to use provider-specific env vars (OPENAI_MODELS, ANTHROPIC_MODELS, DEFAULT_MODEL)
- 017-markdown-support: Added JavaScript ES6+ (Frontend) + Vue 3.4.0, Vite 5.0.0, marked (markdown parser - to be added), DOMPurify (XSS sanitization - to be added), highlight.js (syntax highlighting - to be added)
