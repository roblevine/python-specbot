# Research: OpenAI LangChain Chat Integration

**Feature**: 006-openai-langchain-chat
**Date**: 2026-01-10
**Purpose**: Resolve technical unknowns and document design decisions

## Research Topics

### 1. LangChain OpenAI Integration Pattern

**Decision**: Use `langchain-openai` with `ChatOpenAI` class for chat completions

**Rationale**:
- `ChatOpenAI` is the standard LangChain wrapper for OpenAI's chat models
- Provides consistent interface that will work with future model providers
- Handles message formatting (system, human, AI) automatically
- Built-in retry logic and error handling
- Async support via `ainvoke()` for FastAPI compatibility

**Alternatives Considered**:
- **Direct OpenAI SDK**: Simpler but lacks abstraction for future multi-model support
- **LangChain legacy `OpenAI` class**: Deprecated in favor of `ChatOpenAI`
- **LangGraph**: Overkill for simple chat; better for complex agent workflows

**Implementation Pattern**:
```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Async invocation for FastAPI
response = await llm.ainvoke(messages)
```

---

### 2. Conversation History Management

**Decision**: Convert frontend message format to LangChain message types on each request

**Rationale**:
- Frontend already stores conversation history in LocalStorage
- Backend remains stateless (no session storage needed)
- Each request includes full conversation context
- Simpler architecture; no server-side session management

**Alternatives Considered**:
- **Server-side session storage (Redis)**: Adds complexity; not needed for single-user app
- **LangChain ConversationBufferMemory**: Requires persistent backend state
- **Token-limited history**: Premature optimization; implement if/when needed

**Implementation Pattern**:
```python
def convert_to_langchain_messages(messages: list[dict]) -> list:
    """Convert frontend message format to LangChain messages."""
    lc_messages = []
    for msg in messages:
        if msg["sender"] == "user":
            lc_messages.append(HumanMessage(content=msg["text"]))
        elif msg["sender"] == "system":
            lc_messages.append(AIMessage(content=msg["text"]))
    return lc_messages
```

---

### 3. API Key Configuration

**Decision**: Environment variable `OPENAI_API_KEY` loaded via `python-dotenv`

**Rationale**:
- Industry standard for secrets management
- Already using `python-dotenv` in backend
- Works with Docker, CI/CD, and local development
- No code changes needed to update key

**Alternatives Considered**:
- **Config file**: Secrets shouldn't be in files checked into VCS
- **AWS Secrets Manager / Vault**: Overkill for current scope
- **Request header**: Security risk; exposes key to frontend

**Implementation**:
- Add to `.env.example`: `OPENAI_API_KEY=your-api-key-here`
- Add to `.env.example`: `OPENAI_MODEL=gpt-3.5-turbo`
- Load in `llm_service.py` on initialization

---

### 4. Error Handling Strategy

**Decision**: Catch LangChain/OpenAI exceptions and convert to user-friendly messages

**Rationale**:
- OpenAI SDK raises specific exceptions (AuthenticationError, RateLimitError, etc.)
- Must not expose API keys or internal errors to users (FR-006)
- Existing error handling pattern in `messages.py` can be extended

**Error Mapping**:
| OpenAI Exception | User Message | HTTP Status |
|------------------|--------------|-------------|
| `AuthenticationError` | "AI service configuration error. Please contact support." | 503 |
| `RateLimitError` | "AI service is busy. Please try again in a moment." | 503 |
| `APIConnectionError` | "Unable to reach AI service. Please check your connection." | 503 |
| `APIStatusError` (500) | "AI service is temporarily unavailable." | 503 |
| `BadRequestError` | "Message could not be processed. Please try rephrasing." | 400 |
| Timeout | "Request timed out. Please try again." | 504 |

**Implementation Pattern**:
```python
from openai import AuthenticationError, RateLimitError, APIConnectionError

try:
    response = await llm.ainvoke(messages)
except AuthenticationError:
    raise HTTPException(503, "AI service configuration error")
except RateLimitError:
    raise HTTPException(503, "AI service is busy. Please try again.")
```

---

### 5. Async/Sync Considerations

**Decision**: Use async `ainvoke()` throughout for non-blocking I/O

**Rationale**:
- FastAPI is async-first; blocking calls hurt concurrency
- LangChain's `ChatOpenAI` supports `ainvoke()` natively
- OpenAI API calls are I/O-bound (network latency)
- Matches existing async patterns in `messages.py`

**Implementation**:
```python
async def get_ai_response(messages: list) -> str:
    response = await llm.ainvoke(messages)
    return response.content
```

---

### 6. Model Configuration

**Decision**: Default to `gpt-3.5-turbo`, configurable via environment variable

**Rationale**:
- `gpt-3.5-turbo` is cost-effective and fast for general chat
- Environment variable allows switching models without code change
- No user-facing model selection in this iteration (per spec assumptions)

**Configuration**:
```
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4, gpt-4-turbo, etc.
```

---

### 7. Request Timeout

**Decision**: 30-second timeout for OpenAI API calls

**Rationale**:
- Success criteria SC-001 requires response within 10 seconds "under normal conditions"
- 30 seconds provides buffer for slow responses without hanging indefinitely
- LangChain/OpenAI SDK supports timeout configuration

**Implementation**:
```python
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
    timeout=30,
    max_retries=2
)
```

---

### 8. Logging Strategy

**Decision**: Log LLM requests/responses at INFO level, errors at ERROR level

**Rationale**:
- Constitution Principle V requires observability
- Existing `LoggingMiddleware` handles HTTP layer
- Need additional logging for LLM-specific operations
- Must NOT log full message content (privacy) - log metadata only

**Log Events**:
- `llm_request_start`: conversation_id, message_count, model
- `llm_request_complete`: conversation_id, response_length, latency_ms
- `llm_request_error`: conversation_id, error_type, error_message (sanitized)

---

## Dependencies to Add

```text
# backend/requirements.txt additions
langchain>=0.3.0
langchain-openai>=0.2.0
```

---

## Testing Strategy

### Unit Tests (test_llm_service.py)
- Mock `ChatOpenAI` to test message conversion
- Test error handling for each exception type
- Test configuration loading

### Integration Tests (test_openai_integration.py)
- Use VCR.py or responses library to record/replay OpenAI responses
- Test full message flow with mocked external API
- Test conversation context preservation

### Contract Tests
- Update OpenAPI spec to document AI response format
- Response structure unchanged: `{ status, message, timestamp }`
- Contract tests verify compatibility

---

## Summary of Decisions

| Topic | Decision | Complexity |
|-------|----------|------------|
| LangChain pattern | `ChatOpenAI` with `ainvoke()` | Low |
| Conversation history | Stateless; convert on each request | Low |
| API key config | Environment variable | Low |
| Error handling | Map exceptions to user-friendly messages | Medium |
| Async | Use `ainvoke()` throughout | Low |
| Model config | Env var, default `gpt-3.5-turbo` | Low |
| Timeout | 30 seconds | Low |
| Logging | Metadata only, no content | Low |

All NEEDS CLARIFICATION items have been resolved. Ready for Phase 1.
