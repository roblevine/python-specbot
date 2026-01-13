# Quickstart: Testing Message Streaming Locally

**Feature**: 009-message-streaming
**Date**: 2026-01-13

## Overview

This guide walks you through testing the message streaming feature in your local development environment. You'll learn how to start the backend/frontend, test with curl, and verify streaming behavior.

---

## Prerequisites

1. **Environment Setup**: Ensure you have the development environment running
   ```bash
   # Backend requirements
   python --version  # Should be 3.13+
   pip list | grep fastapi  # Should have FastAPI 0.115.0+

   # Frontend requirements
   node --version  # Should be 18+
   npm list | grep vue  # Should have Vue 3.4.0+
   ```

2. **OpenAI API Key**: Set your API key in `.env`
   ```bash
   echo "OPENAI_API_KEY=sk-your-key-here" > .env
   ```

3. **Install Dependencies** (if not already installed)
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd ../frontend
   npm install
   ```

---

## Step 1: Start the Backend Server

Start the FastAPI backend with streaming support:

```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend is Running**:
```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{"status": "healthy", "timestamp": "2026-01-13T10:30:45.123Z"}
```

---

## Step 2: Test Streaming with curl

Test the streaming endpoint using curl as an SSE client:

### Simple Streaming Test

```bash
curl -N -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8000/api/v1/messages \
  -d '{"message": "What is the capital of France?"}'
```

**Expected Output** (streaming in real-time):
```
data: {"type": "token", "content": "The"}

data: {"type": "token", "content": " capital"}

data: {"type": "token", "content": " of"}

data: {"type": "token", "content": " France"}

data: {"type": "token", "content": " is"}

data: {"type": "token", "content": " Paris"}

data: {"type": "token", "content": "."}

data: {"type": "complete", "model": "gpt-3.5-turbo"}

```

**curl Flags Explained**:
- `-N`: Disable buffering (required for streaming)
- `-H "Accept: text/event-stream"`: Request SSE streaming
- `-X POST`: HTTP POST method
- `-d`: JSON request body

### Test with Conversation History

```bash
curl -N -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8000/api/v1/messages \
  -d '{
    "message": "What about Germany?",
    "history": [
      {"sender": "user", "text": "What is the capital of France?"},
      {"sender": "system", "text": "The capital of France is Paris."}
    ]
  }'
```

**Expected Output**:
```
data: {"type": "token", "content": "The"}

data: {"type": "token", "content": " capital"}

data: {"type": "token", "content": " of"}

data: {"type": "token", "content": " Germany"}

data: {"type": "token", "content": " is"}

data: {"type": "token", "content": " Berlin"}

data: {"type": "token", "content": "."}

data: {"type": "complete", "model": "gpt-3.5-turbo"}

```

### Test with Specific Model

```bash
curl -N -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8000/api/v1/messages \
  -d '{
    "message": "Explain quantum computing in one sentence",
    "model": "gpt-4"
  }'
```

---

## Step 3: Test Error Scenarios

### Invalid Model

```bash
curl -N -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8000/api/v1/messages \
  -d '{"message": "Hello", "model": "invalid-model"}'
```

**Expected Output**:
```
HTTP/1.1 400 Bad Request
{"status": "error", "error": "Invalid model: invalid-model. Available models: gpt-3.5-turbo, gpt-4, gpt-4-turbo", "timestamp": "..."}
```

### Empty Message

```bash
curl -N -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8000/api/v1/messages \
  -d '{"message": ""}'
```

**Expected Output**:
```
HTTP/1.1 400 Bad Request
{"status": "error", "error": "Message cannot be empty", "timestamp": "..."}
```

### Simulate Timeout (if implemented)

```bash
# Set a very short timeout in backend (for testing)
# Then send a complex query that will timeout
curl -N -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8000/api/v1/messages \
  -d '{"message": "Write a 5000-word essay on quantum physics"}'
```

**Expected Output**:
```
data: {"type": "token", "content": "Quantum"}

data: {"type": "token", "content": " physics"}

...

data: {"type": "error", "error": "Request timed out", "code": "TIMEOUT"}

```

---

## Step 4: Start the Frontend and Test Visually

Start the Vue frontend to test streaming in the browser:

```bash
cd frontend
npm run dev
```

**Expected Output**:
```
  VITE v5.0.0  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

**Open Browser**:
1. Navigate to `http://localhost:5173`
2. Enter a message in the input area: "What is the capital of France?"
3. Click "Send"
4. **Observe**:
   - Message appears in chat area
   - Status bar shows "Streaming..."
   - Response tokens appear progressively in real-time
   - Animated cursor (▊) appears at end of streaming message
   - Status bar shows "Ready" when streaming completes
   - Input is disabled during streaming

**Expected Behavior**:
- First token appears within 1-2 seconds
- Each token appears immediately as received
- Smooth typing animation effect
- Auto-scrolls to keep latest content visible
- Message saved to LocalStorage when complete

---

## Step 5: Debug Streaming Issues

### Check Backend Logs

Backend logs show streaming activity:

```bash
# In backend terminal
tail -f logs/app.log  # If logging to file
# OR watch console output
```

**Look for**:
```
INFO:     Stream started: message_id=msg-abc123, model=gpt-4
INFO:     Token streamed: length=5, total=5
INFO:     Token streamed: length=8, total=13
INFO:     Stream completed: message_id=msg-abc123, total_tokens=150, duration=2.5s
```

### Check Frontend Console

Open browser DevTools (F12) and check Console:

```javascript
// Should see logs like:
[StreamAPI] Starting stream for message: "What is..."
[StreamAPI] EventSource opened
[StreamAPI] Token received: "The"
[StreamAPI] Token received: " capital"
[StreamAPI] Stream completed, model: gpt-4
[StreamAPI] EventSource closed
```

### Check Network Activity

In DevTools Network tab:
1. Filter by "XHR" or "EventSource"
2. Look for POST /api/v1/messages request
3. Should show `Type: eventsource`
4. Click to view Headers:
   - Accept: text/event-stream
   - Content-Type: application/json
5. Click "EventStream" tab to see events in real-time

### Common Issues

**Issue**: No streaming, only JSON response
**Cause**: Missing `Accept: text/event-stream` header
**Fix**: Ensure apiClient.js sets correct Accept header

**Issue**: Connection closes immediately
**Cause**: Proxy/nginx buffering enabled
**Fix**: Add `X-Accel-Buffering: no` header in backend response

**Issue**: Tokens arrive in batches, not smoothly
**Cause**: Buffering somewhere in the stack
**Fix**: Check nginx/proxy config, ensure `Cache-Control: no-cache`

**Issue**: Error "Too many connections"
**Cause**: Browser EventSource limit (6 per domain)
**Fix**: Close inactive streams, limit concurrent streaming sessions

---

## Step 6: Test with Browser EventSource API

Create a simple HTML page to test streaming manually:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Streaming Test</title>
</head>
<body>
  <h1>SSE Streaming Test</h1>
  <button onclick="startStream()">Start Stream</button>
  <button onclick="stopStream()">Stop Stream</button>
  <div id="output"></div>

  <script>
    let eventSource = null;

    async function startStream() {
      // Send POST request to get stream URL
      const response = await fetch('http://localhost:8000/api/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify({
          message: 'What is the capital of France?'
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            handleEvent(data);
          }
        }
      }
    }

    function handleEvent(data) {
      const output = document.getElementById('output');
      if (data.type === 'token') {
        output.textContent += data.content;
      } else if (data.type === 'complete') {
        output.textContent += '\n\n[Complete - Model: ' + data.model + ']';
      } else if (data.type === 'error') {
        output.textContent += '\n\n[Error: ' + data.error + ']';
      }
    }

    function stopStream() {
      if (eventSource) {
        eventSource.close();
        eventSource = null;
      }
    }
  </script>
</body>
</html>
```

Save as `test-streaming.html` and open in browser.

---

## Step 7: Verify Contract Tests (After Implementation)

After implementing streaming, verify contract tests pass:

```bash
# Backend contract tests
cd backend
pytest tests/contract/test_message_api_contract.py -v

# Should include new tests:
# - test_streaming_endpoint_contract()
# - test_sse_event_format()
# - test_streaming_error_events()
```

**Expected Output**:
```
tests/contract/test_message_api_contract.py::test_streaming_endpoint_contract PASSED
tests/contract/test_message_api_contract.py::test_sse_event_format PASSED
tests/contract/test_message_api_contract.py::test_streaming_error_events PASSED
```

---

## Performance Benchmarks

Expected performance metrics for local testing:

| Metric | Target | Typical |
|--------|--------|---------|
| First token latency | < 1s | 0.5-1.5s |
| Token throughput | 10-50 tokens/sec | ~20 tokens/sec |
| Stream duration (100 tokens) | < 10s | 3-7s |
| Memory per stream | < 10MB | ~5MB |
| Concurrent streams supported | 100+ | Limited by OpenAI rate limits |

---

## Troubleshooting

### Backend Not Starting

**Check**:
- Python version (must be 3.13+)
- Dependencies installed: `pip list | grep fastapi`
- Port 8000 not already in use: `lsof -i :8000`

### Frontend Not Connecting

**Check**:
- Backend is running on port 8000
- CORS enabled in backend (should allow localhost:5173)
- Browser console for CORS errors

### Streaming Not Working

**Check**:
- Accept header set to `text/event-stream`
- Backend logs show "Stream started"
- Network tab shows EventSource type connection
- No proxy/nginx buffering issues

### Slow Streaming

**Check**:
- OpenAI API latency (check OpenAI status)
- Network latency to OpenAI
- Backend/frontend on same machine (minimize network hops)

---

## Next Steps

After verifying streaming works locally:
1. Review contract tests in `backend/tests/contract/`
2. Run full test suite: `npm test` (frontend), `pytest` (backend)
3. Deploy to staging environment for end-to-end testing
4. Monitor streaming metrics (token rate, success rate, errors)

---

**Quickstart Status**: ✅ COMPLETE
**Ready for Implementation**: YES
