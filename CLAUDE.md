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

## Project Structure

```text
src/
tests/
```

## Commands

### Testing

**Quick Test Scripts** (from project root):
```bash
./scripts/test-all.sh              # Run all tests (backend + frontend + contract)
./scripts/test-all.sh --coverage   # Run all tests with coverage reports
./scripts/test-backend.sh          # Run backend tests only
./scripts/test-frontend.sh         # Run frontend tests only
```

**Manual Testing**:
```bash
# Frontend
cd frontend && npm test                    # All tests
cd frontend && npm run test:coverage       # With coverage
cd frontend && npm run test:e2e            # E2E tests

# Backend
cd backend && pytest                       # All tests
cd backend && pytest --cov=src             # With coverage
cd backend && pytest -m unit               # Unit tests only
```

## Code Style

: Follow standard conventions

## Recent Changes
- 014-conversation-titles: Added JavaScript (ES6+) for frontend, Python 3.13 for backend + Vue 3.4.0, Vite 5.0.0, FastAPI 0.115.0
- 013-redesign-frontend-palette: Added JavaScript (ES6+) + Vue 3.4.0, Vite 5.0.0
- 012-modular-model-providers: Added Python 3.13 (backend), JavaScript ES6+ (frontend) + FastAPI 0.115.0, Pydantic 2.10.0, LangChain 0.3+, langchain-openai 0.2+, langchain-anthropic 0.2+, Vue 3.4.0, Vite 5.0.0

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

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
