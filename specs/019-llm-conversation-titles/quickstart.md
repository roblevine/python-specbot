# Quickstart: LLM-Generated Conversation Titles

**Feature**: 019-llm-conversation-titles
**Date**: 2026-01-21

## Overview

This feature replaces the current title generation behavior (using first message text) with LLM-generated titles. After the first message exchange in a conversation, the system automatically generates a succinct title using an LLM.

## Configuration

### 1. Configure Title Models (Optional)

Add title model configuration to your `.env` file. If not configured, the system uses the current conversation model.

```bash
# .env additions for title models
# These specify which model to use for generating titles per provider

# OpenAI title model (optional - defaults to conversation model)
OPENAI_TITLE_MODEL=gpt-3.5-turbo

# Anthropic title model (optional - defaults to conversation model)
ANTHROPIC_TITLE_MODEL=claude-haiku-4-5-20251001
```

### 2. Verify Configuration

Start the backend and check the `/api/v1/models` endpoint:

```bash
curl http://localhost:8000/api/v1/models | jq
```

You should see `titleModel: true` on the configured title models:

```json
{
  "models": [
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "provider": "openai",
      "default": false,
      "titleModel": false
    },
    {
      "id": "gpt-3.5-turbo",
      "name": "GPT-3.5 Turbo",
      "provider": "openai",
      "default": true,
      "titleModel": true
    }
  ]
}
```

## API Usage

### Generate a Title

```bash
curl -X POST http://localhost:8000/api/v1/titles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"sender": "user", "text": "How do I implement a binary search tree in Python?"},
      {"sender": "system", "text": "To implement a binary search tree in Python, you will need to create a Node class..."}
    ],
    "model": "gpt-3.5-turbo"
  }'
```

**Response:**
```json
{
  "status": "success",
  "title": "Python Binary Search Tree Implementation"
}
```

## Frontend Integration

### Automatic Title Generation

The frontend automatically generates titles after the first message exchange:

1. User sends first message to a new conversation
2. Assistant response streams back
3. After streaming completes, frontend calls title generation API
4. Conversation title updates in the sidebar

### Manual Testing Flow

1. Start a new conversation (title shows "New Conversation")
2. Send any message
3. Wait for assistant response to complete
4. Title automatically updates to LLM-generated summary
5. Subsequent messages do not re-trigger title generation

### Error Handling

If title generation fails:
- Title falls back to the first message text (truncated)
- Error is logged (not shown to user)
- User can manually rename via the title menu

## Development

### Running Tests

```bash
# Backend unit tests
cd backend
pytest tests/unit/test_title_service.py -v

# Backend integration tests
pytest tests/integration/test_titles_api.py -v

# Frontend tests
cd frontend
npm test -- tests/unit/useConversations.test.js
```

### Key Files

**Backend:**
- `backend/src/api/routes/titles.py` - Title generation endpoint
- `backend/src/services/title_service.py` - Title generation service
- `backend/src/config/models.py` - Title model configuration

**Frontend:**
- `frontend/src/services/apiClient.js` - API client with `generateTitle()`
- `frontend/src/state/useConversations.js` - Title generation trigger logic

## Troubleshooting

### Title not generating?

1. Check backend logs for errors
2. Verify model ID is valid: `curl http://localhost:8000/api/v1/models`
3. Ensure at least 2 messages in conversation (user + assistant)

### Wrong model being used?

1. Check `OPENAI_TITLE_MODEL` / `ANTHROPIC_TITLE_MODEL` env vars
2. Verify provider matches current conversation model
3. Check `/api/v1/models` response for `titleModel: true`

### Title too long?

Titles are automatically truncated to 60 characters at word boundary. If LLM returns longer text, it's handled automatically.

## Architecture

```
┌─────────────────┐     1. Complete         ┌──────────────────┐
│   Frontend      │ ────────────────────►   │   Chat Window    │
│   (Vue.js)      │                         │                  │
└────────┬────────┘                         └──────────────────┘
         │
         │ 2. Generate title
         │
         ▼
┌─────────────────┐     3. POST /titles/    ┌──────────────────┐
│   API Client    │ ────────────────────►   │   FastAPI        │
│                 │        generate         │   Backend        │
└────────┬────────┘                         └────────┬─────────┘
         │                                           │
         │                                           │ 4. LLM call
         │                                           ▼
         │                                  ┌──────────────────┐
         │                                  │   Title Service  │
         │                                  │   (LangChain)    │
         │                                  └────────┬─────────┘
         │                                           │
         │                                           │ 5. Generate
         │                                           ▼
         │                                  ┌──────────────────┐
         │ 6. Update title                  │   OpenAI /       │
         ◄──────────────────────────────────│   Anthropic      │
                                            └──────────────────┘
```
