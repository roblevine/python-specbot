# python-specbot Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-23

## Active Technologies
- JavaScript (ES6+), Vue 3.4.0 + Vue 3 (Composition API), Vite 5.0.0 (002-new-conversation-button)
- LocalStorage (via existing storage utilities in `frontend/src/storage/`) (002-new-conversation-button)
- Python 3.13 (confirmed in devcontainer) + FastAPI 0.115.0, uvicorn (ASGI server), Pydantic (validation) (003-backend-api-loopback)
- N/A (backend is stateless for loopback; frontend LocalStorage persists conversations) (003-backend-api-loopback)
- JavaScript ES6+ (Frontend), Python 3.13 (Backend) (005-chat-error-display)
- Browser LocalStorage (versioned schema v1.0.0) (005-chat-error-display)

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
- 005-chat-error-display: Added JavaScript ES6+ (Frontend), Python 3.13 (Backend)
- 003-backend-api-loopback: Added Python 3.13 (confirmed in devcontainer) + FastAPI 0.115.0, uvicorn (ASGI server), Pydantic (validation)
- 002-new-conversation-button: Added JavaScript (ES6+), Vue 3.4.0 + Vue 3 (Composition API), Vite 5.0.0


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
