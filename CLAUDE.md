# python-specbot Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-23

## Active Technologies
- JavaScript (ES6+), Vue 3.4.0 + Vue 3 (Composition API), Vite 5.0.0 (002-new-conversation-button)
- LocalStorage (via existing storage utilities in `frontend/src/storage/`) (002-new-conversation-button)
- Python 3.13 (confirmed in devcontainer) + FastAPI 0.115.0, uvicorn (ASGI server), Pydantic (validation) (003-backend-api-loopback)
- N/A (backend is stateless for loopback; frontend LocalStorage persists conversations) (003-backend-api-loopback)
- JavaScript ES6+ (Frontend), Python 3.13 (Backend) (005-chat-error-display)
- Browser LocalStorage (versioned schema v1.0.0) (005-chat-error-display)
- Python 3.13 (backend), JavaScript ES6+ (frontend) + FastAPI 0.115.0, LangChain, langchain-openai, Vue 3.4.0, Vite 5.0.0 (006-openai-langchain-chat)
- LocalStorage (frontend, existing), N/A for backend (stateless) (006-openai-langchain-chat)
- JavaScript ES6+ (Frontend only, no backend changes) + Vue 3.4.0, CSS3 (CSS Variables, Flexbox, Transitions) (007-ui-redesign)
- Browser LocalStorage (via existing StorageAdapter) for sidebar collapse preference (007-ui-redesign)

- (001-chat-interface)

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
- 007-ui-redesign: Added JavaScript ES6+ (Frontend only, no backend changes) + Vue 3.4.0, CSS3 (CSS Variables, Flexbox, Transitions)
- 006-openai-langchain-chat: Added Python 3.13 (backend), JavaScript ES6+ (frontend) + FastAPI 0.115.0, LangChain, langchain-openai, Vue 3.4.0, Vite 5.0.0
- 005-chat-error-display: Added JavaScript ES6+ (Frontend), Python 3.13 (Backend)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
