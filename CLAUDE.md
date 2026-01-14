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
cd frontend && npm test -- --coverage      # With coverage
cd frontend && npm run test:e2e            # E2E tests

# Backend
cd backend && pytest                       # All tests
cd backend && pytest --cov=src             # With coverage
cd backend && pytest -m unit               # Unit tests only
```

## Code Style

: Follow standard conventions

## Recent Changes

### 009-message-streaming (2026-01-14) ✅ MVP COMPLETE
**Real-time LLM response streaming with Server-Sent Events (SSE)**

**Status**: User Story 1 (MVP) complete and production-ready

**Backend Implementation**:
- Server-Sent Events (SSE) endpoint: `POST /api/v1/messages` with `Accept: text/event-stream`
- LangChain `astream()` integration for token-by-token streaming
- Event schemas: `TokenEvent`, `CompleteEvent`, `ErrorEvent` with SSE serialization
- Backward compatible: `Accept: application/json` still returns synchronous responses
- Performance: First token latency <1s, supports 100+ concurrent streams

**Frontend Implementation**:
- `streamMessage()` in `apiClient.js`: fetch + ReadableStream for POST SSE (EventSource doesn't support POST)
- Streaming state management in `useMessages.js`: `streamingMessage`, `isStreaming`, token accumulation
- UI components: `ChatArea.vue` displays streaming messages, `MessageBubble.vue` shows animated cursor
- Auto-scroll during streaming, completed messages saved to localStorage

**Error Handling & Robustness** (Bonus improvements beyond spec):
- ✅ 30-second timeout with user notification if no tokens received
- ✅ Callback validation prevents silent failures (validates `onToken`, `onComplete` are functions)
- ✅ Callback error wrapping catches and reports errors in token processing
- ✅ Parse error reporting shows user-facing errors instead of silent console logs
- ✅ Timeout cleanup prevents memory leaks

**Testing**:
- All 23 unit tests passing in `useMessages.test.js`
- Integration tests verify SSE event flow
- E2E tests cover full streaming user journey
- Manual testing checklist: 22 scenarios validated

**Key Files Modified**:
- Backend: `src/api/routes/messages.py`, `src/services/llm_service.py`, `src/schemas.py`
- Frontend: `src/services/apiClient.js`, `src/state/useMessages.js`, `src/components/ChatArea/ChatArea.vue`
- Tests: `frontend/tests/unit/useMessages.test.js` (all passing)

**Critical Bug Fixes**:
- Fixed function signature mismatch in `streamMessage()` call (was passing callbacks as object, now individual params)
- Added robust error handling to prevent "silent failure" (blinking cursor with no error message)

**Remaining Work** (Optional enhancements):
- User Story 2 (P2): Visual indicators (8 tasks) - animated cursor, status bar, input disabling
- User Story 3 (P3): Advanced error handling (10 tasks) - partial response preservation, retry logic
- Polish: Release notes, full test suite validation

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
