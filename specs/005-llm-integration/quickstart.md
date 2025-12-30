# Developer Quickstart: LLM Backend Integration

**Feature**: 005-llm-integration
**Created**: 2025-12-30
**For**: Developers implementing streaming LLM chat with LangChain

## Overview

This feature integrates LangChain to enable streaming AI conversations with support for multiple LLM providers. The initial implementation uses OpenAI (GPT-5, GPT-5 Codex), with imminent support for Anthropic Claude, Ollama, and local models.

**Architecture**: Frontend (Vue.js) → FastAPI Backend → LangChain → LLM Provider(s)

**Key Technologies**:
- **Backend**: Python 3.13, FastAPI 0.115.0, LangChain 0.3.x, Pydantic 2.10.0
- **Frontend**: Vue 3.4.0, Vite 5.0.0, EventSource (SSE)
- **LLM Providers**: OpenAI (initial), Anthropic/Ollama/local (imminent)

## Quick Start

### 1. Install Dependencies

```bash
# Backend dependencies
cd backend
pip install langchain langchain-openai langchain-core
pip install openai  # LangChain peer dependency

# Already have: fastapi, uvicorn, pydantic, pytest
```

**requirements.txt additions**:
```txt
langchain==0.3.0
langchain-openai==0.3.0
langchain-core==0.3.0
langchain-anthropic==0.3.0  # For imminent multi-provider support
langchain-community==0.3.0  # For Ollama/local models
openai>=1.0.0
```

### 2. Configure Environment Variables

Create/update `backend/.env`:
```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_ORG_ID=org-your-org-id  # Optional

# Model Configuration
DEFAULT_LLM_MODEL=gpt-5
AVAILABLE_MODELS=gpt-5,gpt-5-codex

# Streaming Configuration
STREAM_TIMEOUT=30  # seconds
MAX_TOKENS=4096
TEMPERATURE=0.7
```

### 3. Run Development Servers

**Backend**:
```bash
cd backend
python main.py
# Server runs on http://localhost:8000
# API docs: http://localhost:8000/docs
```

**Frontend**:
```bash
cd frontend
npm run dev
# App runs on http://localhost:5173
```

## Key Implementation Patterns

### Backend: LangChain Streaming with FastAPI

**File**: `backend/src/services/llm_service.py`

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from fastapi.responses import StreamingResponse
import json
import uuid

class LLMService:
    def __init__(self):
        self.models = {
            "gpt-5": ChatOpenAI(model="gpt-5", streaming=True),
            "gpt-5-codex": ChatOpenAI(model="gpt-5-codex", streaming=True),
        }

    async def stream_chat_response(
        self,
        message: str,
        conversation_history: list[dict],
        model: str = "gpt-5"
    ):
        """
        Stream AI response using LangChain.

        Yields Server-Sent Events (SSE) with format:
        - event: message\ndata: {"type": "start", "messageId": "msg-xxx"}
        - event: message\ndata: {"type": "chunk", "content": "text"}
        - event: message\ndata: {"type": "done", "messageId": "msg-xxx", "model": "gpt-5"}
        - event: error\ndata: {"type": "error", "code": "...", "message": "..."}
        """
        message_id = f"msg-{uuid.uuid4()}"
        llm = self.models.get(model, self.models["gpt-5"])

        # Convert conversation history to LangChain message format
        messages = []
        for msg in conversation_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                messages.append(SystemMessage(content=msg["content"]))

        # Add current user message
        messages.append(HumanMessage(content=message))

        async def generate():
            try:
                # Send start event
                yield f"event: message\n"
                yield f"data: {json.dumps({'type': 'start', 'messageId': message_id})}\n\n"

                # Stream response chunks
                async for chunk in llm.astream(messages):
                    if chunk.content:
                        yield f"event: message\n"
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk.content})}\n\n"

                # Send done event
                yield f"event: message\n"
                yield f"data: {json.dumps({'type': 'done', 'messageId': message_id, 'model': model})}\n\n"

            except Exception as e:
                # Send error event
                error_code = self._classify_error(e)
                error_message = self._get_user_friendly_message(error_code, e)

                yield f"event: error\n"
                yield f"data: {json.dumps({'type': 'error', 'code': error_code, 'message': error_message})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    def _classify_error(self, error: Exception) -> str:
        """Map exception to error code"""
        error_str = str(error).lower()
        if "authentication" in error_str or "api key" in error_str:
            return "authentication_error"
        elif "rate limit" in error_str or "429" in error_str:
            return "rate_limit_exceeded"
        elif "timeout" in error_str:
            return "network_timeout"
        elif "503" in error_str or "unavailable" in error_str:
            return "model_unavailable"
        else:
            return "llm_provider_error"

    def _get_user_friendly_message(self, code: str, error: Exception) -> str:
        """Get non-technical error message for users"""
        messages = {
            "authentication_error": "Unable to connect to AI service. Please check your configuration.",
            "rate_limit_exceeded": "The AI service is temporarily busy. Please try again in a moment.",
            "network_timeout": "Connection lost. Please check your network and try again.",
            "model_unavailable": "The selected AI model is temporarily unavailable. Please try again later.",
            "llm_provider_error": "An unexpected error occurred. Please try again.",
        }
        return messages.get(code, str(error))
```

**File**: `backend/src/api/routes/chat.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Literal
from src.services.llm_service import LLMService

router = APIRouter(prefix="/api/v1/chat", tags=["Chat", "Streaming"])

class ChatStreamRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    conversationId: str = Field(..., pattern=r"^conv-[0-9a-f-]{36}$")
    conversationHistory: List[Dict[str, str]] = Field(default_factory=list)
    model: Literal["gpt-5", "gpt-5-codex"] = "gpt-5"

    @validator('message')
    def message_not_empty(cls, v):
        if not v or v.strip() == '':
            raise ValueError('Message cannot be empty or whitespace-only')
        return v

@router.post("/stream")
async def stream_chat_response(request: ChatStreamRequest):
    """
    Stream AI chat response using Server-Sent Events (SSE).

    Returns progressive response chunks as the LLM generates them.
    Client should accumulate chunks to build complete message.
    """
    llm_service = LLMService()

    return await llm_service.stream_chat_response(
        message=request.message,
        conversation_history=request.conversationHistory,
        model=request.model
    )
```

**File**: `backend/main.py` (register router)

```python
from src.api.routes import chat

app.include_router(chat.router)
```

### Frontend: EventSource Streaming Client

**File**: `frontend/src/services/streamingClient.js`

```javascript
export class StreamingClient {
  constructor(baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') {
    this.baseURL = baseURL
    this.activeStream = null
  }

  /**
   * Start streaming chat response
   * @param {string} message - User message
   * @param {string} conversationId - Conversation ID
   * @param {Array} conversationHistory - Previous messages [{role, content}]
   * @param {string} model - LLM model ("gpt-5" or "gpt-5-codex")
   * @param {Object} callbacks - Event handlers
   * @returns {AbortController} Controller to cancel stream
   */
  async streamChat(message, conversationId, conversationHistory, model, callbacks) {
    const { onStart, onChunk, onDone, onError } = callbacks

    // Create request body
    const requestBody = {
      message,
      conversationId,
      conversationHistory: conversationHistory || [],
      model: model || 'gpt-5'
    }

    // Use fetch with ReadableStream for SSE
    const controller = new AbortController()
    this.activeStream = controller

    try {
      const response = await fetch(`${this.baseURL}/api/v1/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
        signal: controller.signal
      })

      if (!response.ok) {
        const errorData = await response.json()
        onError?.(errorData)
        return controller
      }

      // Parse Server-Sent Events
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            // Event type (message or error)
            continue
          } else if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6))

            if (data.type === 'start') {
              onStart?.(data.messageId)
            } else if (data.type === 'chunk') {
              onChunk?.(data.content)
            } else if (data.type === 'done') {
              onDone?.(data.messageId, data.model)
            } else if (data.type === 'error') {
              onError?.(data)
            }
          }
        }
      }
    } catch (error) {
      if (error.name !== 'AbortError') {
        onError?.({
          code: 'network_error',
          message: 'Connection lost. Please check your network and try again.'
        })
      }
    } finally {
      this.activeStream = null
    }

    return controller
  }

  /**
   * Stop active stream
   */
  stopStream() {
    if (this.activeStream) {
      this.activeStream.abort()
      this.activeStream = null
    }
  }
}
```

**File**: `frontend/src/state/useModelSelection.js`

```javascript
import { ref, watch } from 'vue'

const STORAGE_KEY = 'llm:modelSelection'
const DEFAULT_MODEL = 'gpt-5'

export function useModelSelection() {
  const selectedModel = ref(loadModelSelection())

  function loadModelSelection() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const data = JSON.parse(stored)
        return data.selectedModel || DEFAULT_MODEL
      }
    } catch (error) {
      console.error('Failed to load model selection:', error)
    }
    return DEFAULT_MODEL
  }

  function saveModelSelection(model) {
    selectedModel.value = model
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        selectedModel: model,
        lastUpdated: new Date().toISOString()
      }))
    } catch (error) {
      console.error('Failed to save model selection:', error)
    }
  }

  // Persist changes
  watch(selectedModel, (newModel) => {
    saveModelSelection(newModel)
  })

  return {
    selectedModel,
    setModel: saveModelSelection,
    availableModels: ['gpt-5', 'gpt-5-codex']
  }
}
```

## Testing Patterns

### Backend: Unit Test for LLM Service

**File**: `backend/tests/unit/test_llm_service.py`

```python
import pytest
from unittest.mock import AsyncMock, patch
from src.services.llm_service import LLMService

@pytest.mark.asyncio
async def test_stream_chat_response():
    """Test that LLM service streams response chunks correctly"""
    service = LLMService()

    # Mock LangChain ChatOpenAI
    with patch.object(service.models['gpt-5'], 'astream') as mock_stream:
        # Simulate streaming chunks
        mock_stream.return_value = [
            type('Chunk', (), {'content': 'Hello'})(),
            type('Chunk', (), {'content': ' world'})(),
            type('Chunk', (), {'content': '!'})(),
        ].__aiter__()

        response = await service.stream_chat_response(
            message="Hi there",
            conversation_history=[],
            model="gpt-5"
        )

        # Collect all events
        events = []
        async for chunk in response.body_iterator:
            events.append(chunk.decode())

        # Verify event sequence
        assert 'event: message' in events[0]
        assert '"type": "start"' in events[1]
        assert '"type": "chunk"' in events[3]
        assert '"content": "Hello"' in events[3]
        assert '"type": "done"' in events[-1]
```

### Frontend: Unit Test for Streaming Client

**File**: `frontend/tests/unit/streamingClient.test.js`

```javascript
import { describe, it, expect, vi } from 'vitest'
import { StreamingClient } from '@/services/streamingClient'

describe('StreamingClient', () => {
  it('should parse SSE events correctly', async () => {
    const client = new StreamingClient()
    const onStart = vi.fn()
    const onChunk = vi.fn()
    const onDone = vi.fn()

    // Mock fetch with SSE response
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        body: {
          getReader: () => ({
            read: vi.fn()
              .mockResolvedValueOnce({
                done: false,
                value: new TextEncoder().encode(
                  'event: message\ndata: {"type":"start","messageId":"msg-123"}\n\n'
                )
              })
              .mockResolvedValueOnce({
                done: false,
                value: new TextEncoder().encode(
                  'event: message\ndata: {"type":"chunk","content":"Hello"}\n\n'
                )
              })
              .mockResolvedValueOnce({
                done: false,
                value: new TextEncoder().encode(
                  'event: message\ndata: {"type":"done","messageId":"msg-123","model":"gpt-5"}\n\n'
                )
              })
              .mockResolvedValueOnce({ done: true })
          })
        }
      })
    )

    await client.streamChat('Test', 'conv-123', [], 'gpt-5', {
      onStart,
      onChunk,
      onDone
    })

    expect(onStart).toHaveBeenCalledWith('msg-123')
    expect(onChunk).toHaveBeenCalledWith('Hello')
    expect(onDone).toHaveBeenCalledWith('msg-123', 'gpt-5')
  })
})
```

## Development Workflow

### 1. Write Failing Tests (TDD)
```bash
# Backend
cd backend
pytest tests/unit/test_llm_service.py -v  # Should FAIL initially

# Frontend
cd frontend
npm test -- streamingClient.test.js  # Should FAIL initially
```

### 2. Implement Feature
- Backend: Create `llm_service.py` and `chat.py` router
- Frontend: Create `streamingClient.js` and update components

### 3. Verify Tests Pass
```bash
# Backend
pytest tests/unit/test_llm_service.py -v  # Should PASS

# Frontend
npm test -- streamingClient.test.js  # Should PASS
```

### 4. Integration Tests
```bash
# Backend integration test
pytest tests/integration/test_streaming_chat.py -v

# Frontend E2E test
npm run test:e2e -- llm-integration.spec.js
```

### 5. Contract Tests
```bash
# Capture contract snapshots (frontend)
cd frontend
npm run test:contract:capture

# Validate contracts (backend)
cd backend
pytest tests/contract/test_chat_streaming_contract.py -v
```

## Common Gotchas

### 1. EventSource vs Fetch for SSE
- **Don't use `EventSource`** - it only supports GET requests
- **Use `fetch` with `ReadableStream`** - supports POST with request body

### 2. LangChain Message Format
```python
# Correct: Use LangChain message classes
from langchain_core.messages import HumanMessage, AIMessage
messages = [HumanMessage(content="Hello")]

# Incorrect: Plain dicts won't work
messages = [{"role": "user", "content": "Hello"}]  # ❌
```

### 3. Streaming Response Headers
```python
# Required headers for SSE
return StreamingResponse(
    generate(),
    media_type="text/event-stream",  # Critical!
    headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }
)
```

### 4. Frontend SSE Parsing
```javascript
// SSE format: "event: message\ndata: {...}\n\n"
// Must parse both event type and data
if (line.startsWith('data: ')) {
  const data = JSON.parse(line.slice(6))  // Skip "data: "
}
```

## Next Steps: Multi-Provider Support (Week 2)

```python
# backend/src/services/llm_service.py
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama

class LLMService:
    def __init__(self):
        self.models = {
            # OpenAI models
            "gpt-5": ChatOpenAI(model="gpt-5", streaming=True),
            "gpt-5-codex": ChatOpenAI(model="gpt-5-codex", streaming=True),

            # Anthropic models (Week 2)
            "claude-3-opus": ChatAnthropic(model="claude-3-opus-20240229", streaming=True),
            "claude-3-sonnet": ChatAnthropic(model="claude-3-sonnet-20240229", streaming=True),

            # Local models via Ollama (Week 2)
            "llama-3-70b": ChatOllama(model="llama3:70b", streaming=True),
            "codellama-34b": ChatOllama(model="codellama:34b", streaming=True),
        }
```

**No code changes needed in streaming logic** - LangChain provides unified interface!

## Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [LangChain Streaming Guide](https://python.langchain.com/docs/expression_language/streaming)
- [FastAPI SSE Guide](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [MDN Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [OpenAPI Contract](./contracts/chat-streaming-api.yaml)
- [Data Model](./data-model.md)
- [Research Document](./research.md)
