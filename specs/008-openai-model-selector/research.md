# Research: OpenAI Model Selector

**Feature**: 008-openai-model-selector
**Date**: 2026-01-11
**Status**: Complete

## Research Questions

### Q1: How should model configuration be structured?

**Decision**: Use environment variable `OPENAI_MODELS` as JSON array with model metadata

**Rationale**:
- Follows existing pattern of environment-based configuration (`OPENAI_API_KEY`, `OPENAI_MODEL`)
- JSON format allows rich metadata (id, name, description, default flag)
- Single environment variable simplifies deployment
- Easy to override in different environments (dev/staging/prod)

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| Separate env vars per model | Doesn't scale, hard to add metadata |
| Config file (YAML/JSON) | Requires file management, more complex deployment |
| Database configuration | Over-engineering for simple model list |
| Hardcoded in application | Not configurable per environment |

**Implementation Details**:
```python
# Environment variable format
OPENAI_MODELS='[
  {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model", "default": false},
  {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}
]'

# Fallback when not set: use OPENAI_MODEL as single model with default=true
```

---

### Q2: How should model selection be passed to the backend?

**Decision**: Add optional `model` field to existing MessageRequest schema

**Rationale**:
- Backward compatible (optional field with default fallback)
- Per-request model selection enables mid-conversation changes
- Follows REST principles (request contains all needed context)
- No session state on server (stateless backend)

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| Separate endpoint per model | Not RESTful, URL explosion |
| Query parameter | Less structured than request body |
| Header-based | Harder to test/debug, not visible in body |
| Server-side session state | Violates stateless principle, complicates scaling |

**Implementation Details**:
```python
# MessageRequest schema extension
class MessageRequest(BaseModel):
    message: str
    conversationId: Optional[str] = None
    timestamp: Optional[str] = None
    history: Optional[List[HistoryMessage]] = None
    model: Optional[str] = None  # NEW: Model ID to use
```

---

### Q3: How should the backend validate model selection?

**Decision**: Validate against configured model list; reject unknown models with 400 Bad Request

**Rationale**:
- Prevents typos or invalid model IDs from causing OpenAI API errors
- Provides clear error message to frontend
- Consistent with existing validation patterns (Pydantic)
- Fail-fast approach (validate early, not at OpenAI call)

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| Pass-through to OpenAI | Obscure error messages, unnecessary API call |
| Silent fallback to default | Hides configuration errors, confusing behavior |
| Regex-based validation | Too permissive, doesn't verify model exists |

**Implementation Details**:
```python
# In llm_service.py
def validate_model(model_id: str, available_models: List[dict]) -> bool:
    return any(m['id'] == model_id for m in available_models)

# 400 response on invalid model
{"status": "error", "error": "Invalid model: gpt-5. Available models: gpt-4, gpt-3.5-turbo"}
```

---

### Q4: How should the response indicate which model was used?

**Decision**: Add `model` field to MessageResponse schema

**Rationale**:
- Enables FR-009 (display which model generated response)
- Useful for debugging and transparency
- Backward compatible (new field, no breaking change)
- Matches request/response symmetry pattern

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| Response header | Harder to access in frontend, not part of body |
| Separate metadata endpoint | Extra round-trip, not contextual |
| Only show in UI, not API | Loses API contract clarity |

**Implementation Details**:
```python
class MessageResponse(BaseModel):
    status: Literal["success"]
    message: str
    timestamp: str
    model: str  # NEW: Model ID that generated response
```

---

### Q5: How should the frontend expose the model selector?

**Decision**: Dropdown component above the input area, persistent during session

**Rationale**:
- Visible but not intrusive placement
- Dropdown is familiar UI pattern for selection
- Session persistence avoids repeated selection
- Position near input associates it with message sending

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| Settings modal | Hidden, extra clicks to access |
| Inline in message input | Clutters input area |
| Sidebar toggle | Takes screen space, overkill for simple selection |
| Per-message selection | Too granular, confusing UX |

**Implementation Details**:
```
┌─────────────────────────────────┐
│ StatusBar                       │
├─────────────────────────────────┤
│ ChatArea (messages)             │
│                                 │
│                                 │
├─────────────────────────────────┤
│ [Model: GPT-4 ▼] ← NEW          │
│ ┌─────────────────────────────┐ │
│ │ InputArea                   │ │
│ │ Type a message... [Send]    │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

---

### Q6: How should frontend persist model selection?

**Decision**: Extend StorageSchema to include `selectedModelId` field at root level

**Rationale**:
- Follows existing session persistence pattern
- Simple addition to existing schema structure
- Root-level field (not per-conversation) matches session scope
- Schema version bump not required (optional field)

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| Per-conversation model | Complicates UX, spec says session-level |
| In-memory only | Loses selection on page refresh within session |
| Separate localStorage key | Fragments storage, harder to maintain |

**Implementation Details**:
```javascript
// Updated schema structure (v1.0.0 compatible)
{
  version: '1.0.0',
  conversations: [...],
  activeConversationId: 'conv-...',
  selectedModelId: 'gpt-4'  // NEW: Optional, defaults to null
}
```

---

### Q7: How should the frontend fetch available models?

**Decision**: New GET /api/v1/models endpoint returns model list with metadata

**Rationale**:
- Decouples frontend from backend configuration
- Allows backend to control available models
- Metadata (name, description, default) enables rich UI
- RESTful pattern for resource listing

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| Hardcode in frontend | Not configurable, duplicates backend |
| Environment variable in frontend | Build-time only, not dynamic |
| Include in health check | Pollutes health endpoint semantics |
| Query parameter discovery | Non-standard, harder to implement |

**Implementation Details**:
```yaml
# GET /api/v1/models
Response 200:
{
  "models": [
    {"id": "gpt-4", "name": "GPT-4", "description": "Most capable", "default": false},
    {"id": "gpt-3.5-turbo", "name": "GPT-3.5", "description": "Fast", "default": true}
  ]
}
```

---

### Q8: How should the LLM service handle per-request model selection?

**Decision**: Remove singleton pattern; create ChatOpenAI instance per request with specified model

**Rationale**:
- Different models require different ChatOpenAI instances
- Per-request instantiation is simple and correct
- ChatOpenAI instantiation is lightweight (no connection pooling)
- Follows LangChain documentation patterns

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| Cache instance per model | Premature optimization, adds complexity |
| Single instance with model override | Not supported by LangChain ChatOpenAI |
| Global model switch | Race conditions in concurrent requests |

**Implementation Details**:
```python
# Modified get_ai_response signature
async def get_ai_response(
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    model: Optional[str] = None  # NEW: Override model for this request
) -> str:
    config = load_config()
    model_to_use = model or get_default_model(config)
    llm = initialize_llm(config['api_key'], model_to_use)
    # ... rest of implementation
```

---

## Dependencies & Integration Points

### Backend Dependencies (No Changes)
- LangChain, langchain-openai: Already support model parameter
- FastAPI, Pydantic: Already in use for schemas
- No new Python packages required

### Frontend Dependencies (No Changes)
- Vue 3 Composition API: Supports new component
- Existing apiClient.js: Will be extended
- No new npm packages required

### Integration Points

1. **Backend Config → LLM Service**: Model list loaded at startup
2. **Frontend → GET /api/v1/models**: Fetch available models on app load
3. **Frontend → POST /api/v1/messages**: Include selected model in request
4. **MessageResponse → MessageBubble**: Display model indicator per message

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| OpenAI model deprecation | Medium | Low | Validate against OpenAI's supported models |
| Invalid model config syntax | Low | Medium | Validate JSON on startup, fallback to default |
| Frontend/backend model mismatch | Low | Medium | Backend validates, returns error |
| Model selector slows UI | Low | Low | Async fetch, cache model list |

---

## Open Questions (Resolved)

All clarifications from spec have been resolved through research:

1. **Configuration format**: JSON array in environment variable
2. **API changes**: Optional `model` field in request, required in response
3. **Frontend placement**: Dropdown above input area
4. **Persistence scope**: Session-level (localStorage), not per-conversation
5. **Model validation**: Backend validates against configuration list
