# Quickstart: OpenAI LangChain Chat Integration

**Feature**: 006-openai-langchain-chat
**Date**: 2026-01-10

## Prerequisites

- Python 3.13+
- Node.js 18+
- OpenAI API key (get one at https://platform.openai.com/api-keys)

## Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install new dependencies
pip install langchain langchain-openai

# Or update from requirements.txt (after implementation)
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

Create or update `.env` file in the `backend/` directory:

```bash
# backend/.env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Existing settings
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:5173
LOG_LEVEL=INFO
```

**Security Notes**:
- Never commit `.env` to version control
- `.env` is already in `.gitignore`
- Use `.env.example` as a template

### 3. Start the Application

```bash
# Terminal 1: Start backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### 4. Verify Setup

1. Open browser to http://localhost:5173
2. Type a message and click Send
3. You should receive an AI response (not "api says: " loopback)

## Testing

### Run Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run only unit tests (fast, no API calls)
pytest -m unit

# Run integration tests (uses mocked OpenAI)
pytest -m integration

# Run with coverage
pytest --cov=src
```

### Run Frontend Tests

```bash
cd frontend

# Run unit tests
npm run test

# Run E2E tests (requires both servers running)
npm run test:e2e
```

## Troubleshooting

### "AI service configuration error"

**Cause**: Invalid or missing OpenAI API key

**Fix**:
1. Check `backend/.env` has `OPENAI_API_KEY` set
2. Verify API key is valid at https://platform.openai.com/api-keys
3. Restart the backend server

### "AI service is busy"

**Cause**: OpenAI rate limit exceeded

**Fix**:
1. Wait a moment and retry
2. Check your OpenAI usage at https://platform.openai.com/usage
3. Consider upgrading your OpenAI plan

### "Unable to reach AI service"

**Cause**: Network connectivity issue

**Fix**:
1. Check internet connection
2. Verify OpenAI API status at https://status.openai.com
3. Check firewall/proxy settings

### "Request timed out"

**Cause**: OpenAI response took too long (>30 seconds)

**Fix**:
1. Retry with a simpler/shorter message
2. Check OpenAI status for degraded performance
3. Consider using a faster model (gpt-3.5-turbo vs gpt-4)

## Development Tips

### Viewing Logs

Backend logs show LLM request details:

```bash
# Tail backend logs
cd backend
uvicorn main:app --reload 2>&1 | grep -E "(llm_|INFO|ERROR)"
```

### Testing Without OpenAI

For development without API costs, you can mock the LLM service:

```python
# In tests, use mocked responses
@pytest.fixture
def mock_llm():
    with patch('src.services.llm_service.get_ai_response') as mock:
        mock.return_value = "This is a mocked AI response"
        yield mock
```

### Switching Models

Change the model in `.env`:

```bash
# Fast and cheap
OPENAI_MODEL=gpt-3.5-turbo

# More capable
OPENAI_MODEL=gpt-4

# Latest GPT-4
OPENAI_MODEL=gpt-4-turbo
```

## API Usage Example

### Simple Message

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

### Message with Conversation History

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my name?",
    "history": [
      {"sender": "user", "text": "My name is Alice"},
      {"sender": "system", "text": "Nice to meet you, Alice!"}
    ]
  }'
```

## Next Steps

After setup:
1. Run `/speckit.tasks` to generate implementation tasks
2. Follow TDD workflow: write tests → verify fail → implement → verify pass
3. Update contract tests when API behavior changes
4. Update `architecture.md` with LLM service layer details
