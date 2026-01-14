# Phase 0: Research - Message Streaming Implementation

**Feature**: 009-message-streaming
**Date**: 2026-01-13
**Status**: Complete

## Overview

This document consolidates research findings for implementing real-time LLM response streaming using Server-Sent Events (SSE), LangChain async streaming, and Vue reactive components. All technical decisions are documented with rationale and alternatives considered.

---

## 1. FastAPI Server-Sent Events Implementation

### Decision: Use FastAPI StreamingResponse with SSE format

**Rationale**:
- FastAPI has native support for streaming via `StreamingResponse`
- SSE is simpler than WebSockets for unidirectional server→client communication
- Browser-native EventSource API handles reconnection automatically
- No additional dependencies required beyond FastAPI

**Implementation Pattern**:
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

async def event_generator():
    """Generate SSE events"""
    for i in range(10):
        # SSE format: "data: <payload>\n\n"
        data = json.dumps({"token": f"word{i}"})
        yield f"data: {data}\n\n"
        await asyncio.sleep(0.1)

@app.get("/stream")
async def stream_endpoint():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering if applicable
        }
    )
```

**Key Considerations**:
- **Content-Type**: Must be `text/event-stream`
- **Cache-Control**: Must be `no-cache` to prevent caching
- **Connection**: Should be `keep-alive` for persistent connection
- **Buffering**: Disable proxy buffering (nginx, cloudflare) with `X-Accel-Buffering: no`
- **Heartbeats**: Send periodic comments (`:ping\n\n`) to keep connection alive if no data for >30 seconds

**Error Handling**:
- Catch exceptions in generator and send error event before closing stream
- Use try/finally to ensure cleanup (close LLM resources)
- Log streaming errors with correlation ID for debugging

**Alternatives Considered**:
- **WebSockets**: Overkill for unidirectional streaming, more complex setup, requires ws:// protocol
- **HTTP Chunked Transfer Encoding**: More complex to implement, no browser-native API like EventSource
- **HTTP Long Polling**: Inefficient, high latency, not suitable for token-by-token streaming

---

## 2. LangChain Async Streaming (`astream`)

### Decision: Use LangChain's `astream()` method for token-by-token streaming

**Rationale**:
- LangChain provides native streaming support via `astream()`
- Returns async generator yielding AIMessageChunk objects
- Compatible with OpenAI's streaming API
- Minimal code changes from existing `ainvoke()` implementation

**Implementation Pattern**:
```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessageChunk

async def stream_ai_response(message: str, history: list = None):
    """Stream AI response token-by-token"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", streaming=True)

    # Build conversation
    messages = convert_to_langchain_messages(history or [])
    messages.append(HumanMessage(content=message))

    # Stream response
    async for chunk in llm.astream(messages):
        # chunk is AIMessageChunk with .content attribute
        if chunk.content:
            yield chunk.content  # Yield token string
```

**Key Considerations**:
- **Chunk Structure**: `AIMessageChunk` has `.content` (token string), `.response_metadata`, `.id`
- **Empty Chunks**: Some chunks may have empty `.content`, filter them out
- **Context Handling**: History/context handled same as `ainvoke()`, passed as messages list
- **Model Selection**: Works with all OpenAI models (gpt-3.5-turbo, gpt-4, gpt-4-turbo)
- **Error Handling**: Wrap in try/except, catch `APIError`, `RateLimitError`, `AuthenticationError`

**Error Patterns**:
```python
async def stream_ai_response(message: str):
    try:
        async for chunk in llm.astream(messages):
            yield {"type": "token", "content": chunk.content}
        yield {"type": "complete"}
    except AuthenticationError as e:
        yield {"type": "error", "error": "AI service configuration error"}
    except RateLimitError as e:
        yield {"type": "error", "error": "AI service is busy"}
    except Exception as e:
        yield {"type": "error", "error": "AI service error occurred"}
```

**Performance**:
- **Latency**: First token typically arrives within 0.5-1.5 seconds
- **Token Rate**: Varies by model, typically 10-50 tokens/second
- **Resource Usage**: Similar to `ainvoke()`, async generator is memory efficient

**Alternatives Considered**:
- **OpenAI Python SDK Direct**: More boilerplate, LangChain abstracts complexity
- **Streaming via Callbacks**: LangChain supports callbacks but astream is cleaner for SSE

---

## 3. Browser EventSource API

### Decision: Use native EventSource API for SSE consumption

**Rationale**:
- Browser-native API, no additional dependencies
- Automatic reconnection with exponential backoff
- Built-in event parsing for SSE format
- Simple event-driven interface

**Implementation Pattern**:
```javascript
function streamMessage(message, onToken, onComplete, onError) {
    const url = `/api/v1/messages/stream?message=${encodeURIComponent(message)}`;
    const eventSource = new EventSource(url);

    // Listen for token events
    eventSource.addEventListener('message', (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'token') {
            onToken(data.content);
        } else if (data.type === 'complete') {
            onComplete();
            eventSource.close();
        }
    });

    // Handle errors
    eventSource.addEventListener('error', (event) => {
        if (eventSource.readyState === EventSource.CLOSED) {
            onError('Connection closed');
        }
        eventSource.close();
    });

    // Return cleanup function
    return () => eventSource.close();
}
```

**Key Considerations**:
- **Concurrent Connections**: Browser limit is 6 connections per domain (HTTP/1.1)
- **Automatic Reconnection**: EventSource reconnects automatically with exponential backoff
- **Connection States**: CONNECTING (0), OPEN (1), CLOSED (2)
- **Custom Events**: SSE supports named events via `event: <name>` field
- **CORS**: Requires proper CORS headers from backend
- **Authentication**: Limited - cannot set custom headers, use query params or cookies

**Limitations**:
- Cannot set custom headers (e.g., Authorization bearer tokens) - use query params or cookies
- No bidirectional communication (use WebSockets if needed)
- Connection limit of 6 per domain (consider if app has multiple streaming features)

**Error Handling**:
```javascript
eventSource.addEventListener('error', (event) => {
    console.error('SSE error:', event);

    // Check connection state
    if (eventSource.readyState === EventSource.CONNECTING) {
        console.log('Reconnecting...');
    } else if (eventSource.readyState === EventSource.CLOSED) {
        console.log('Connection closed');
        onError('Connection lost');
    }
});
```

**Alternatives Considered**:
- **fetch() with ReadableStream**: More control but requires manual parsing, no auto-reconnect
- **WebSocket**: Overkill for unidirectional streaming, more complex
- **HTTP Long Polling**: Inefficient, not suitable for real-time token streaming

---

## 4. SSE Message Format Standards

### Decision: Use JSON in SSE data field with event types

**Format**:
```
# Token event
data: {"type": "token", "content": "Hello"}

# Complete event
data: {"type": "complete", "model": "gpt-4"}

# Error event
data: {"type": "error", "error": "AI service error occurred", "code": "LLM_ERROR"}

# Named events (alternative)
event: token
data: {"content": "Hello"}

event: complete
data: {"model": "gpt-4"}
```

**Rationale**:
- JSON payload is structured and easy to parse
- Event types enable different handling (token vs complete vs error)
- SSE supports both unnamed events (default) and named events (`event:` field)
- Compatible with EventSource API's addEventListener

**Chosen Format**: JSON with `type` field (unnamed events)
- Simpler: all events use default `message` listener
- Extensible: easy to add fields like `messageId`, `timestamp`, `metadata`
- Compatible: works with all SSE clients

**Event Types**:
1. **token**: Streaming token/chunk
   ```json
   {"type": "token", "content": "word"}
   ```
2. **complete**: Stream finished successfully
   ```json
   {"type": "complete", "model": "gpt-4", "totalTokens": 150}
   ```
3. **error**: Error occurred during streaming
   ```json
   {"type": "error", "error": "AI service error", "code": "LLM_ERROR"}
   ```

**SSE Format Rules**:
- Each event: `data: <payload>\n\n` (double newline required)
- Comments: `: <comment>\n` (used for heartbeats)
- Event ID: `id: <id>\n` (for resuming on reconnect)
- Event type: `event: <type>\n` (optional named events)
- Multi-line data: Multiple `data:` fields concatenated with newlines

**Heartbeat Pattern** (if no data for >30 seconds):
```
: ping
```

**Alternatives Considered**:
- **Plain Text**: Not structured, hard to distinguish token vs metadata
- **Named Events**: More complex client code, requires multiple listeners
- **XML/YAML**: Overkill, JSON is standard for web APIs

---

## 5. Vue Reactivity for Token Accumulation

### Decision: Use reactive `ref` with string accumulation

**Rationale**:
- Vue 3 reactivity system handles real-time updates efficiently
- `ref` with string accumulation is simplest approach
- Vue automatically batches DOM updates for performance
- Works seamlessly with v-html or v-text directives

**Implementation Pattern**:
```javascript
// In useMessages.js composable
import { ref } from 'vue';

export function useMessages() {
    const messages = ref([]);
    const streamingMessage = ref(null);
    const isStreaming = ref(false);

    function startStreaming(messageId) {
        isStreaming.value = true;
        streamingMessage.value = {
            id: messageId,
            sender: 'system',
            text: '',
            streaming: true,
            timestamp: new Date().toISOString()
        };
    }

    function appendToken(token) {
        if (streamingMessage.value) {
            // Accumulate token to existing text
            streamingMessage.value.text += token;
        }
    }

    function completeStreaming() {
        if (streamingMessage.value) {
            // Mark as complete and add to messages array
            streamingMessage.value.streaming = false;
            messages.value.push(streamingMessage.value);
            streamingMessage.value = null;
            isStreaming.value = false;
        }
    }

    return {
        messages,
        streamingMessage,
        isStreaming,
        startStreaming,
        appendToken,
        completeStreaming
    };
}
```

**Key Considerations**:
- **Reactivity**: Vue tracks changes to `streamingMessage.value.text`, triggers re-render
- **Performance**: String concatenation is efficient for typical response sizes (<10K chars)
- **Auto-scrolling**: Use `nextTick()` after token append to scroll to bottom
- **Debouncing**: Not needed - Vue batches updates automatically
- **Memory**: Temporary streaming message not persisted until complete

**Component Usage**:
```vue
<template>
  <!-- Regular messages -->
  <div v-for="msg in messages" :key="msg.id" class="message">
    {{ msg.text }}
  </div>

  <!-- Streaming message -->
  <div v-if="streamingMessage" class="message streaming">
    {{ streamingMessage.text }}
    <span class="cursor">▊</span>
  </div>
</template>

<script setup>
import { useMessages } from '@/state/useMessages';

const { messages, streamingMessage } = useMessages();
</script>
```

**Auto-Scroll Pattern**:
```javascript
import { nextTick } from 'vue';

function appendToken(token) {
    streamingMessage.value.text += token;

    // Scroll to bottom after DOM update
    nextTick(() => {
        const chatArea = document.querySelector('.chat-area');
        chatArea.scrollTop = chatArea.scrollHeight;
    });
}
```

**Alternatives Considered**:
- **Array of Tokens**: More memory, no performance benefit, complicates rendering
- **Incremental Updates**: Vue's reactivity already optimizes this
- **Web Workers**: Overkill for token accumulation, adds complexity

---

## 6. Concurrent Streaming Session Limits

### Decision: Limit to 1 active stream per conversation, warn users about browser limits

**Rationale**:
- Browser EventSource limit is 6 connections per domain (HTTP/1.1)
- UX: Users typically focus on one conversation at a time
- Backend: OpenAI API can handle 100+ concurrent streams without issue
- Frontend: Single active stream per conversation is sufficient

**Implementation Strategy**:
1. **Frontend State**: Track `isStreaming` flag in useMessages composable
2. **UI Blocking**: Disable send button while streaming in progress
3. **Connection Cleanup**: Always close EventSource when stream completes or errors
4. **User Feedback**: Show "Streaming..." status in StatusBar component

**Browser Connection Management**:
```javascript
// Track active EventSource connections
const activeStreams = new Map();

function streamMessage(conversationId, message) {
    // Close existing stream for this conversation if any
    if (activeStreams.has(conversationId)) {
        activeStreams.get(conversationId).close();
    }

    const eventSource = new EventSource(url);
    activeStreams.set(conversationId, eventSource);

    // Cleanup on complete/error
    const cleanup = () => {
        eventSource.close();
        activeStreams.delete(conversationId);
    };

    eventSource.addEventListener('message', (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'complete') cleanup();
    });

    eventSource.addEventListener('error', cleanup);

    return cleanup;
}
```

**Backend Considerations**:
- **Resource Limits**: FastAPI with Uvicorn handles 1000+ concurrent connections
- **Memory**: Each stream holds minimal memory (generator state + connection)
- **OpenAI Limits**: Rate limits apply per API key, not per stream
- **Monitoring**: Log active stream count for observability

**Connection Limit Warning**:
- If user opens multiple tabs/conversations, approaching 6 connection limit
- Browser will block new connections when limit reached
- Mitigation: Close streams when tab loses focus (optional optimization)

**Alternatives Considered**:
- **WebSocket Multiplexing**: More complex, not needed for single-stream-per-conversation use case
- **HTTP/2**: Reduces connection limit issue but still limited to browser capabilities
- **Connection Pooling**: Not applicable for SSE (connections are long-lived)

---

## 7. Streaming Error Recovery Patterns

### Decision: Graceful degradation with partial response preservation

**Error Categories**:
1. **Network Errors**: Connection lost during streaming
2. **LLM Errors**: OpenAI API errors (rate limit, timeout, auth)
3. **Client Errors**: Browser/EventSource errors

**Recovery Strategy**:

**1. Partial Response Preservation**:
```javascript
function handleStreamError(error, partialText) {
    // Save partial response to state
    if (partialText && partialText.trim()) {
        // Mark message as incomplete but visible
        const incompleteMessage = {
            id: generateId(),
            sender: 'system',
            text: partialText,
            incomplete: true,
            error: error.message,
            timestamp: new Date().toISOString()
        };
        messages.value.push(incompleteMessage);
    }

    // Show error to user
    appState.setError('Stream interrupted. Partial response saved.');
}
```

**2. Error Event Format**:
```python
# Backend sends error event before closing stream
async def stream_ai_response():
    try:
        async for chunk in llm.astream(messages):
            yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
    except Exception as e:
        # Send error event
        error_data = {
            'type': 'error',
            'error': 'AI service error occurred',
            'code': 'LLM_ERROR'
        }
        yield f"data: {json.dumps(error_data)}\n\n"
```

**3. Retry Logic**:
```javascript
function streamMessageWithRetry(message, maxRetries = 2) {
    let retryCount = 0;

    function attemptStream() {
        return streamMessage(
            message,
            onToken,
            onComplete,
            (error) => {
                if (retryCount < maxRetries && isRetryableError(error)) {
                    retryCount++;
                    console.log(`Retry attempt ${retryCount}/${maxRetries}`);
                    setTimeout(attemptStream, 1000 * retryCount); // Exponential backoff
                } else {
                    onError(error);
                }
            }
        );
    }

    return attemptStream();
}

function isRetryableError(error) {
    // Retry on network errors, not on client errors
    return error.type === 'network' || error.code === 'CONNECTION_LOST';
}
```

**4. User Actions on Error**:
- **Preserve Partial**: Automatically save partial response
- **Retry Option**: Show "Retry" button if error is retryable
- **Continue Conversation**: Allow user to send new message despite error
- **Clear Error**: Dismiss error state when user takes action

**Backend Error Handling**:
```python
async def event_generator():
    try:
        # Stream tokens
        async for chunk in stream_ai_response(message, history, model):
            yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

        # Success completion
        yield f"data: {json.dumps({'type': 'complete', 'model': model})}\n\n"

    except LLMTimeoutError as e:
        yield f"data: {json.dumps({'type': 'error', 'error': 'Request timed out', 'code': 'TIMEOUT'})}\n\n"
    except LLMRateLimitError as e:
        yield f"data: {json.dumps({'type': 'error', 'error': 'AI service is busy', 'code': 'RATE_LIMIT'})}\n\n"
    except Exception as e:
        logger.error(f"Stream error: {e}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'error': 'AI service error occurred', 'code': 'UNKNOWN'})}\n\n"
    finally:
        # Cleanup resources
        logger.info("Stream completed or errored, cleaning up")
```

**Observability**:
- Log all stream errors with correlation IDs
- Track metrics: success rate, partial responses, error types
- Include partial response length in error logs

**Alternatives Considered**:
- **No Partial Preservation**: Poor UX, users lose context
- **Automatic Retry**: May be annoying if errors are persistent
- **Buffer-and-Retry**: Adds latency, defeats purpose of streaming

---

## Summary of Technical Decisions

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| **Backend Streaming** | FastAPI StreamingResponse with SSE | Native support, simple, browser-compatible |
| **LLM Streaming** | LangChain `astream()` | Native async streaming, minimal code changes |
| **Frontend API** | Browser EventSource | Native API, auto-reconnect, event-driven |
| **Message Format** | JSON with type field | Structured, extensible, easy to parse |
| **Vue Reactivity** | Reactive ref with string accumulation | Simple, efficient, Vue-optimized |
| **Concurrency** | 1 stream per conversation | Matches UX, avoids browser limits |
| **Error Recovery** | Preserve partial + graceful degradation | Best UX, no data loss |

## Next Steps

With research complete, proceed to **Phase 1: Design & Contracts**:
1. Generate `data-model.md` - Streaming message entity and state transitions
2. Generate `contracts/streaming-api.yaml` - OpenAPI spec for streaming endpoint
3. Generate `quickstart.md` - Local testing guide for streaming
4. Update `CLAUDE.md` - Add streaming technologies to agent context

---

**Research Status**: ✅ COMPLETE
**Phase 1 Ready**: YES
**Blockers**: NONE
