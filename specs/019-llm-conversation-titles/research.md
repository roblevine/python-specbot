# Research: LLM-Generated Conversation Titles

**Feature**: 019-llm-conversation-titles
**Date**: 2026-01-21

## Research Tasks

### 1. API Endpoint Design

**Decision**: Use `POST /api/v1/titles/generate` as a standalone endpoint

**Rationale**:
- Title generation is a distinct operation from conversation CRUD
- Keeps conversations endpoint focused on data persistence
- Allows for easy rate limiting and monitoring of title generation requests
- RESTful: POST because it creates/generates content (idempotent but has side effects via LLM)

**Alternatives Considered**:
- `POST /api/v1/conversations/{id}/title` - Rejected: Too tightly coupled to conversations, complicates routing
- Adding action to conversations endpoint - Rejected: Violates single responsibility principle
- WebSocket for title generation - Rejected: Over-engineering for a simple request/response

### 2. Title Model Configuration Pattern

**Decision**: Add per-provider `TITLE_MODEL` environment variables

**Rationale**:
- Follows established pattern of provider-specific env vars (OPENAI_MODELS, ANTHROPIC_MODELS)
- Simple and explicit configuration
- No changes needed to existing model config structure
- Defaults gracefully to conversation model when not set

**Configuration Design**:
```bash
# Per-provider title model (optional)
OPENAI_TITLE_MODEL=gpt-3.5-turbo
ANTHROPIC_TITLE_MODEL=claude-haiku-4-5-20251001
```

**Alternatives Considered**:
- Adding `title_model: true` field to model configs - Rejected: Requires schema changes, harder to override
- Global `TITLE_MODEL` env var - Rejected: Doesn't support provider-specific selection
- Query parameter to specify title model - Rejected: Client shouldn't need to know available models

### 3. Title Generation Prompt Engineering

**Decision**: Use a focused, constrained prompt with explicit length limits

**Prompt Design**:
```
Generate a concise title (maximum 60 characters) that summarizes this conversation.
Return ONLY the title text, no quotes, no explanation.

User: {first_user_message}
Assistant: {first_assistant_response}
```

**Rationale**:
- Clear instruction on length constraint
- Explicit about output format (no extra text)
- Provides minimal context (first exchange only) for consistency
- Works across different LLM providers

**Post-processing**:
- Strip whitespace and quotes
- Truncate to 60 characters at word boundary if LLM exceeds limit
- Fallback to first message text if response is empty or invalid

### 4. Frontend Integration Pattern

**Decision**: Call title generation after streaming completion, non-blocking

**Flow**:
1. User sends first message
2. Streaming response begins, title stays "New Conversation"
3. Streaming completes (onComplete callback)
4. Frontend calls title generation endpoint asynchronously
5. On success, update conversation title
6. On failure, fall back to first message text (current behavior)

**Rationale**:
- Non-blocking: User can continue chatting immediately
- Graceful degradation: Failure doesn't break the app
- Clear timing: Title generated only after full response available

**Alternatives Considered**:
- Generate title before response - Rejected: Adds latency to user-perceived response time
- Generate title in parallel with response - Rejected: No assistant response available yet
- Server generates title automatically - Rejected: Requires server to track "first message" state

### 5. Model Selection Logic (Client-Side)

**Decision**: Client determines title model based on provider of current conversation model

**Logic**:
```javascript
function getTitleModel(currentModelId, models) {
  const currentModel = models.find(m => m.id === currentModelId)
  if (!currentModel) return currentModelId

  // Find title model for this provider
  const titleModel = models.find(m =>
    m.provider === currentModel.provider && m.titleModel === true
  )

  // Fall back to current model if no title model configured
  return titleModel ? titleModel.id : currentModelId
}
```

**API Contract Update**:
The `/api/v1/models` endpoint will include a `titleModel` boolean field for models that are configured as title models.

**Rationale**:
- Client has model info from existing /models endpoint
- Simple logic that's easy to test
- Graceful fallback when no title model configured

### 6. Error Handling & Fallback Strategy

**Decision**: Multi-layer fallback with silent degradation

**Fallback Chain**:
1. LLM generates title → Success
2. LLM returns empty/invalid → Use first message text (truncated to 60 chars)
3. API call fails → Use first message text (current behavior)
4. Network timeout → Use first message text

**Error Logging**:
- Log all title generation failures at WARNING level
- Include model ID, error type, and conversation ID in log
- Do not expose errors to user (title is secondary feature)

**Rationale**:
- Title generation is non-critical feature
- User experience shouldn't suffer from title generation failures
- Logs allow monitoring without user disruption

### 7. Existing Code Integration Points

**Backend Changes**:
1. `backend/src/api/routes/titles.py` - New endpoint (POST /api/v1/titles/generate)
2. `backend/src/services/title_service.py` - Title generation logic
3. `backend/src/config/models.py` - Load OPENAI_TITLE_MODEL, ANTHROPIC_TITLE_MODEL
4. `backend/src/api/routes/models.py` - Include titleModel field in response

**Frontend Changes**:
1. `frontend/src/services/apiClient.js` - Add generateTitle() function
2. `frontend/src/state/useConversations.js` - Replace first-message title logic
3. `frontend/src/components/App/App.vue` - Trigger title generation after streaming

**Reusable Components**:
- `llm_service.get_llm_for_model()` - Reuse for title generation
- `convert_to_langchain_messages()` - Reuse for building prompt
- Error handling patterns from existing LLM service

### 8. Testing Strategy

**Unit Tests**:
- Title service: prompt construction, post-processing, truncation
- Model config: title model loading and validation
- Frontend: model selection logic, API call handling

**Integration Tests**:
- Title generation endpoint: valid request, invalid model, empty messages
- Contract tests: request/response format validation

**E2E Tests**:
- Full flow: send message → receive response → title updates
- Fallback: API failure → title set to first message

## Summary of Decisions

| Area | Decision |
|------|----------|
| Endpoint | `POST /api/v1/titles/generate` |
| Configuration | `OPENAI_TITLE_MODEL`, `ANTHROPIC_TITLE_MODEL` env vars |
| Prompt | Constrained prompt with 60-char limit instruction |
| Frontend Timing | After streaming completion, non-blocking |
| Model Selection | Client-side based on provider of current model |
| Error Handling | Silent fallback to first message text |
