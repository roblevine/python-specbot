# Tasks: LangChain Tool Integration

**Input**: Design documents from `/specs/024-add-langchain-tools/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [X] T001 Add `duckduckgo-search>=6.0.0` to backend/requirements.txt
- [X] T002 [P] Add `beautifulsoup4>=4.12.0` to backend/requirements.txt
- [X] T003 [P] Add `lxml>=5.0.0` to backend/requirements.txt
- [X] T004 Run `pip install -r requirements.txt` to install new dependencies
- [X] T005 Create directory structure: `backend/src/services/tools/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Schemas

- [X] T006 Add ToolConfig schema to backend/src/schemas.py (id, name, description, enabled)
- [X] T007 [P] Add ToolCallRecord schema to backend/src/schemas.py (id, toolId, toolName, args, status, result, resultLinks, error, errorCode, debugInfo, startedAt, completedAt, durationMs)
- [X] T008 [P] Add ResultLink schema to backend/src/schemas.py (title, url, snippet)
- [X] T009 Add ToolCallEvent SSE schema to backend/src/schemas.py (type="tool_call", id, toolId, toolName, args)
- [X] T010 [P] Add ToolResultEvent SSE schema to backend/src/schemas.py (type="tool_result", id, status, result, resultLinks, durationMs)
- [X] T011 [P] Add ToolErrorEvent SSE schema to backend/src/schemas.py (type="tool_error", id, status, error, errorCode, debugInfo, durationMs)

### Tool Base Infrastructure

- [X] T012 Create base tool interface in backend/src/services/tools/base.py (BaseTool protocol with execute method)
- [X] T013 Create tool registry in backend/src/services/tools/__init__.py (TOOL_REGISTRY dict, load_enabled_tools function)
- [X] T014 Create tool configuration loader in backend/src/config/tools.py (load from TOOLS env var, following models.py pattern)

### Storage Schema Update

- [X] T015 Extend ConversationMessage schema with optional toolCalls field in backend/src/schemas.py
- [X] T016 Update storage schema version constant to v1.1.0 in backend/src/storage/file_storage.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 + 2 - Web Search & Tool Visibility (Priority: P1) 🎯 MVP

**Goal**: Users can trigger web searches and see tool usage in the conversation stream

**Independent Test**: Ask "What are the latest headlines about climate change?" and verify search executes with visible tool call UI

### Backend: Tool Implementations

- [X] T017 [US1] Implement DuckDuckGo search tool in backend/src/services/tools/duckduckgo.py
  - Use `DuckDuckGoSearchResults` from langchain_community
  - Return structured results with links
  - Handle timeout and network errors
- [X] T018 [P] [US1] Implement web browser tool in backend/src/services/tools/browser.py
  - Use `WebBaseLoader` + `BeautifulSoupTransformer`
  - Truncate output to 4000 chars
  - Handle timeout and connection errors

### Backend: Tool Binding & Streaming

- [X] T019 [US1] Add tool binding to LLM in backend/src/services/llm_service.py
  - Add `get_enabled_tools()` function
  - Add `bind_tools_to_llm()` helper
  - Modify `get_llm_for_model()` to optionally bind tools
- [X] T020 [US1] Extend `stream_ai_response()` in backend/src/services/llm_service.py
  - Detect `tool_call_chunks` in streaming response
  - Execute tool and collect result
  - Yield ToolCallEvent when tool invoked
  - Yield ToolResultEvent or ToolErrorEvent when complete
- [X] T021 [US1] Update message endpoint in backend/src/api/routes/messages.py
  - Load enabled tools at request start
  - Pass tools to LLM service

### Frontend: Tool Call Display

- [X] T022 [US2] Create ToolCallBubble.vue component in frontend/src/components/ChatArea/
  - Collapsible design (collapsed shows tool name + status indicator)
  - Expanded shows: args, result/links, error if any
  - Success (green) and error (red) styling
  - Expand/collapse animation
- [X] T023 [US2] Extend apiClient.js to handle tool events in frontend/src/services/
  - Add `onToolCall` callback parameter to `streamMessage()`
  - Add `onToolResult` callback parameter
  - Parse `tool_call`, `tool_result`, `tool_error` event types
- [X] T024 [US2] Extend useMessages.js state in frontend/src/state/
  - Add `toolCalls` array to message state
  - Add `addToolCall()` and `updateToolCall()` functions
  - Track pending/success/error status
- [X] T025 [US2] Integrate ToolCallBubble into ChatArea in frontend/src/components/ChatArea/ChatArea.vue
  - Render tool calls between user message and assistant response
  - Pass tool call data to ToolCallBubble component

**Checkpoint**: At this point, users can trigger searches and see tool usage in UI (MVP complete)

---

## Phase 4: User Story 3 - Tool History Persistence (Priority: P2)

**Goal**: Tool call information persists across conversation navigation

**Independent Test**: Trigger tool call, navigate away, return, verify tool call UI is restored

### Backend: Persistence

- [X] T026 [US3] Extend message serialization in backend/src/storage/file_storage.py
  - Include toolCalls field when saving messages (handled by Pydantic model_dump())
  - Preserve all ToolCallRecord fields
- [X] T027 [US3] Extend message deserialization in backend/src/storage/file_storage.py
  - Parse toolCalls from stored JSON (handled by Pydantic Conversation(**conv))
  - Handle missing field for backward compatibility (Optional field in schema)

### Backend: API Response

- [X] T028 [US3] Include toolCalls in conversation GET response in backend/src/api/routes/conversations.py
  - Ensure toolCalls array is returned with each message (automatic with Pydantic)

### Frontend: Restore Tool Calls

- [X] T029 [US3] Update conversation loading in frontend/src/state/useConversations.js
  - Parse toolCalls from API response (messages already include toolCalls)
  - Populate message state with persisted tool calls
- [X] T030 [US3] Ensure ToolCallBubble renders persisted tool calls correctly
  - Handle all states (success, error)
  - Render resultLinks if present
  - Render error details if present

**Checkpoint**: Tool history persists across navigation

---

## Phase 5: User Story 4 - Administrator Tool Configuration (Priority: P2)

**Goal**: Administrators can enable/disable tools via environment configuration

**Independent Test**: Set `TOOLS` env var with one tool disabled, restart server, verify only enabled tools load

### Backend: Configuration

- [X] T031 [US4] Implement tool config validation in backend/src/config/tools.py
  - Validate required fields (id, name, description, enabled)
  - Log validation errors clearly
- [X] T032 [US4] Add startup tool loading in backend/main.py
  - Call `load_enabled_tools()` on startup
  - Log: loaded tools, disabled tools, failed tools
- [X] T033 [US4] Handle missing/invalid tool IDs gracefully
  - Log warning for unknown tool IDs in config
  - Continue loading other valid tools

### Documentation

- [X] T034 [US4] Update backend/.env.example with TOOLS configuration
  - Add example TOOLS JSON with both tools
  - Document enable/disable pattern

**Checkpoint**: Administrators can configure tools via environment

---

## Phase 6: User Story 5 - Debug Information (Priority: P3)

**Goal**: Debug mode shows detailed error information for troubleshooting

**Independent Test**: Enable DEBUG=true, trigger tool failure, verify expanded details show technical info

### Backend: Debug Info

- [X] T035 [US5] Add debug info to ToolErrorEvent in backend/src/services/llm_service.py
  - Check DEBUG environment variable (using _is_debug_mode())
  - Include exception type, message, stack trace when DEBUG=true
  - Include request details (URL, timeout) when relevant
- [X] T036 [US5] Ensure debug info is NOT included when DEBUG=false
  - Verify error events only contain user-friendly message

### Frontend: Debug Display

- [X] T037 [US5] Add debug section to ToolCallBubble expanded view
  - Only render if debugInfo is present
  - Show in monospace/code format
  - Clearly label as "Debug Information"

**Checkpoint**: Debug mode provides detailed troubleshooting information

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Error Handling

- [X] T038 [P] Add timeout handling for tool execution (30s search, 60s browser)
- [X] T039 [P] Add network error handling with user-friendly messages
- [X] T040 [P] Handle provider-specific tool support gracefully (warn if Ollama model doesn't support tools)

### Testing

- [X] T041 [P] Unit tests for tool configuration loading in backend/tests/unit/test_tool_config.py
- [X] T042 [P] Unit tests for DuckDuckGo tool in backend/tests/unit/test_duckduckgo_tool.py
- [X] T043 [P] Unit tests for web browser tool in backend/tests/unit/test_browser_tool.py
- [ ] T044 [P] Contract tests for SSE tool events (optional - deferred)
- [ ] T045 [P] Component tests for ToolCallBubble (optional - deferred)
- [ ] T046 Integration test for tool execution flow (optional - deferred)

### Documentation

- [ ] T047 [P] Update architecture.md with tool subsystem (optional - deferred)
- [ ] T048 [P] Validate quickstart.md instructions work end-to-end (optional - deferred)
- [ ] T049 Update CLAUDE.md with new 024 feature information (optional - deferred)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS all user stories
    ↓
┌───────────────────────────────────────────────┐
│  Phase 3 (US1+US2) ← MVP, do this first!      │
│      ↓                                         │
│  Phase 4 (US3) ← Persistence                  │
│      ↓                                         │
│  Phase 5 (US4) ← Configuration                │
│      ↓                                         │
│  Phase 6 (US5) ← Debug info                   │
└───────────────────────────────────────────────┘
    ↓
Phase 7 (Polish)
```

### User Story Dependencies

- **US1 + US2 (P1)**: Combined because tool execution and visibility are inseparable for MVP
- **US3 (P2)**: Depends on US1+US2 (needs tool calls to persist)
- **US4 (P2)**: Can be done in parallel with US3 after US1+US2
- **US5 (P3)**: Depends on US1+US2 (needs error events to enhance)

### Parallel Opportunities

Within Phase 2 (Foundational):
- T007, T008, T010, T011 can run in parallel (independent schemas)

Within Phase 3 (MVP):
- T017, T018 can run in parallel (independent tool implementations)
- T022, T023, T024 can run in parallel (independent frontend files)

Within Phase 7 (Polish):
- All test tasks (T041-T046) can run in parallel
- All documentation tasks (T047-T049) can run in parallel

---

## Implementation Strategy

### MVP First (Recommended)

1. Complete Phase 1: Setup (5 minutes)
2. Complete Phase 2: Foundational (1-2 hours)
3. Complete Phase 3: US1+US2 MVP (3-4 hours)
4. **STOP and VALIDATE**: Test search + visibility works
5. Demo to stakeholders if ready

### Full Feature

After MVP validation:
1. Add Phase 4: Persistence (1-2 hours)
2. Add Phase 5: Configuration (1 hour)
3. Add Phase 6: Debug info (30 minutes)
4. Complete Phase 7: Polish (2-3 hours)

---

## Notes

- All file paths are relative to repository root
- [P] tasks can run in parallel within their phase
- Commit after each task or logical group
- Run `pytest` after backend changes
- Run `npm test` after frontend changes
- Test with all three providers (OpenAI, Anthropic, Ollama) before marking complete
