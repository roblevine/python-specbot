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

# Add commands for 

## Code Style

: Follow standard conventions

## Recent Changes
- 009-message-streaming: Added Python 3.13 (backend), JavaScript ES6+ (frontend)
<<<<<<< HEAD
- 008-openai-model-selector: Added Python 3.13 (backend), JavaScript ES6+ (frontend) + FastAPI 0.115.0, LangChain, langchain-openai, Vue 3.4.0, Vite 5.0.0, Pydantic 2.10.0
=======
- 008-openai-model-selector: Added model configuration system (Pydantic validation), GET /api/v1/models endpoint, ModelSelector component with descriptions, model indicators on messages, localStorage v1.1.0 schema with selectedModelId, per-request model selection
>>>>>>> claude/openai-model-selector-xLAbS


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
