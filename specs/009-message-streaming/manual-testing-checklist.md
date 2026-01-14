# Manual Testing Checklist: Message Streaming (T024)

**Feature**: 009-message-streaming
**Date**: 2026-01-13
**User Story**: US1 - Real-Time Response Streaming

## Prerequisites

- Backend server running: `cd backend && python -m uvicorn main:app --reload`
- Frontend running: `cd frontend && npm run dev`
- Browser DevTools open (Network tab, Console)

---

## Test Cases

### 1. Basic Streaming Functionality

- [ ] **TC001**: Send a simple message ("Hello")
  - ✅ First token appears within 1 second
  - ✅ Tokens appear progressively (word-by-word or token-by-token)
  - ✅ Streaming indicator (blinking cursor) visible during streaming
  - ✅ Message completes and indicator disappears
  - ✅ Completed message saved in conversation history

- [ ] **TC002**: Send a longer message requesting detailed response
  - ✅ Streaming continues smoothly for longer responses
  - ✅ No lag or stuttering between tokens
  - ✅ Auto-scroll keeps latest tokens visible

### 2. Network & Protocol

- [ ] **TC003**: Verify SSE in DevTools Network tab
  - ✅ Request shows "EventStream" type
  - ✅ Accept header: `text/event-stream`
  - ✅ Response Content-Type: `text/event-stream`
  - ✅ Events visible in Network panel

- [ ] **TC004**: Check console logs for streaming events
  - ✅ "Stream started" log appears
  - ✅ Token received logs (every 10 tokens if debug enabled)
  - ✅ "Stream completed" log with duration and token count

### 3. Conversation History

- [ ] **TC005**: Send follow-up message with context
  - ✅ Second message includes history from first message
  - ✅ LLM responds with contextual awareness
  - ✅ Both messages saved in localStorage

- [ ] **TC006**: Reload page and verify history
  - ✅ Previous messages load from localStorage
  - ✅ Can send new streaming message with history

### 4. Model Selection

- [ ] **TC007**: Select different model (e.g., gpt-4)
  - ✅ Streaming works with selected model
  - ✅ Model indicator displays correct model name
  - ✅ Response quality matches selected model

- [ ] **TC008**: Switch models between messages
  - ✅ Each message uses its selected model
  - ✅ Model indicators show correct model per message

### 5. Error Handling

- [ ] **TC009**: Stop backend during streaming
  - ✅ Error message displays after connection loss
  - ✅ Partial response preserved if any tokens received
  - ✅ Error indicator visible

- [ ] **TC010**: Send empty message
  - ✅ Validation error prevents streaming start
  - ✅ Error message shown to user

- [ ] **TC011**: Test with rate limit (if applicable)
  - ✅ ErrorEvent received and displayed
  - ✅ Partial tokens preserved
  - ✅ User can retry after error

### 6. Special Characters & Unicode

- [ ] **TC012**: Request response with emojis
  - ✅ Emojis stream correctly (🚀 🎉 ✨)
  - ✅ No encoding issues or broken characters

- [ ] **TC013**: Request response with non-Latin scripts
  - ✅ Unicode characters stream correctly (中文, العربية, עברית)
  - ✅ Characters display properly in UI

### 7. UI/UX

- [ ] **TC014**: Visual streaming indicators
  - ✅ Blinking cursor appears during streaming
  - ✅ Subtle pulse animation on streaming message
  - ✅ Indicators disappear when streaming completes

- [ ] **TC015**: Message bubble styling
  - ✅ Streaming messages have distinct styling
  - ✅ Completed messages return to normal styling
  - ✅ Timestamp displays correctly

- [ ] **TC016**: Auto-scroll behavior
  - ✅ Chat scrolls automatically as tokens arrive
  - ✅ User can scroll up during streaming without interference
  - ✅ Scroll position maintained for older messages

### 8. Concurrent & Edge Cases

- [ ] **TC017**: Send message while streaming
  - ✅ Cannot send new message while streaming (button disabled or warning shown)
  - ✅ OR: New message queued and sent after current stream completes

- [ ] **TC018**: Multiple rapid messages
  - ✅ Messages stream in sequence
  - ✅ No race conditions or overlapping streams

- [ ] **TC019**: Browser tab switch during streaming
  - ✅ Streaming continues in background
  - ✅ Tokens visible when returning to tab

### 9. Performance

- [ ] **TC020**: First token latency
  - ✅ Measure time from send to first token
  - ✅ Target: < 1 second (check console logs for timing)

- [ ] **TC021**: Stream throughput
  - ✅ Tokens arrive smoothly without noticeable delays
  - ✅ Check console: tokens per second metric in "Stream completed" log

### 10. Backward Compatibility

- [ ] **TC022**: Verify non-streaming still works
  - ✅ Old clients (if any) receive complete JSON response
  - ✅ API handles both `Accept: application/json` and `Accept: text/event-stream`

---

## Acceptance Criteria Validation

From spec.md User Story 1:

1. ✅ **First token within 1-2 seconds**: Verify with TC001, TC020
2. ✅ **Each token appears immediately**: Verify with TC001, TC002
3. ✅ **Completed messages saved**: Verify with TC001, TC005, TC006
4. ✅ **Message ordering maintained**: Verify with TC018

---

## Test Results

**Date Tested**: _____________
**Tester**: _____________
**Environment**: _____________

**Pass Rate**: _____ / 22 test cases

**Issues Found**:
1.
2.
3.

**Notes**:


---

## Curl Commands for Direct API Testing

```bash
# Test SSE endpoint directly
curl -N -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -d '{"message":"Tell me a short story","timestamp":"2026-01-13T22:00:00Z"}' \
  http://localhost:8000/api/v1/messages

# Test JSON endpoint (backward compatibility)
curl -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","timestamp":"2026-01-13T22:00:00Z"}' \
  http://localhost:8000/api/v1/messages
```

---

## Known Limitations

- T021-T023 (ChatArea update, integration tests, E2E tests) are not yet implemented
- Full integration of streaming into ChatArea component pending
- E2E tests with Playwright not yet created

**Status**: Backend streaming MVP complete (T001-T020), frontend UI components partially complete
