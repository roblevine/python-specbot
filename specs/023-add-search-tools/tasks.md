# Tasks: Add Search Tools to Chatbot

**Input**: Design documents from `/specs/023-add-search-tools/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per Constitution Principle III (Test-First Development)

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story this task belongs to (US1, US2, US3)
- Paths use web app convention: `backend/`, `frontend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and create base tool subsystem structure

- [x] T001 Install new dependencies: `langchain-community`, `duckduckgo-search`, `feedparser` in backend/requirements.txt
- [x] T002 [P] Create tool subsystem directory structure at backend/src/services/tools/
- [x] T003 [P] Add tool-related Pydantic schemas to backend/src/schemas.py (ToolInfo, ToolsResponse, ToolCallEvent, ToolResultEvent)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core tool infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundation

- [x] T004 [P] Write unit tests for BaseTool protocol in backend/tests/unit/tools/test_base.py
- [x] T005 [P] Write unit tests for ToolRegistry in backend/tests/unit/tools/test_registry.py

### Implementation for Foundation

- [x] T006 [P] Implement ToolResult dataclass in backend/src/services/tools/base.py
- [x] T007 [P] Implement BaseTool Protocol in backend/src/services/tools/base.py
- [x] T008 Implement ToolRegistry class in backend/src/services/tools/registry.py
- [x] T009 [P] Implement tool-specific errors (ToolError, ToolDisabledError, ToolExecutionError) in backend/src/services/tools/errors.py
- [x] T010 Create tool subsystem __init__.py with registry export in backend/src/services/tools/__init__.py
- [x] T011 Run foundation tests and verify they pass

**Checkpoint**: Tool framework ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Web Search During Conversation (Priority: P1) 🎯 MVP

**Goal**: User asks a question requiring current information; chatbot uses DuckDuckGo search and provides attributed response

**Independent Test**: Ask chatbot "What is the current weather in London?" and verify it searches the web and includes source attribution

### Tests for User Story 1

- [x] T012 [P] [US1] Write unit tests for WebSearchTool in backend/tests/unit/tools/test_web_search.py
- [ ] T013 [P] [US1] Write integration test for tool execution in streaming flow in backend/tests/integration/test_tool_execution.py

### Implementation for User Story 1

- [x] T014 [US1] Implement WebSearchTool class using DuckDuckGo in backend/src/services/tools/web_search.py
- [x] T015 [US1] Register WebSearchTool in backend/src/services/tools/__init__.py
- [x] T016 [US1] Extend llm_service.py to bind tools and implement agentic loop in backend/src/services/llm_service.py
- [x] T017 [US1] Add ToolCallEvent and ToolResultEvent SSE emission in backend/src/api/routes/messages.py
- [x] T018 [US1] Add logging for tool invocations in backend/src/services/tools/web_search.py
- [x] T019 [P] [US1] Extend frontend apiClient.js to handle tool_call and tool_result SSE events in frontend/src/services/apiClient.js
- [x] T020 [P] [US1] Add tool status indicator UI in ChatMessage.vue (show "Searching..." during tool execution) in frontend/src/components/ChatMessage.vue
- [x] T021 [US1] Run User Story 1 tests and verify they pass

**Checkpoint**: Web search tool fully functional - chatbot can search the web and stream responses with tool usage

---

## Phase 4: User Story 2 - BBC News Search (Priority: P2)

**Goal**: User asks about current news; chatbot uses BBC News RSS feeds and returns summarized articles with links

**Independent Test**: Ask chatbot "What's the latest news about climate change?" and verify it returns BBC News articles with headlines and links

### Tests for User Story 2

- [x] T022 [P] [US2] Write unit tests for BBCNewsTool in backend/tests/unit/tools/test_bbc_news.py

### Implementation for User Story 2

- [x] T023 [US2] Implement BBCNewsTool class using feedparser in backend/src/services/tools/bbc_news.py
- [x] T024 [US2] Register BBCNewsTool in backend/src/services/tools/__init__.py
- [x] T025 [US2] Add logging for BBC news tool invocations in backend/src/services/tools/bbc_news.py
- [x] T026 [US2] Run User Story 2 tests and verify they pass

**Checkpoint**: BBC News tool functional - chatbot can search BBC News alongside web search

---

## Phase 5: User Story 3 - Tool Configuration by Administrator (Priority: P3)

**Goal**: Administrator can configure which tools are enabled via environment variables; system provides endpoint to list enabled tools

**Independent Test**: Set `TOOLS_WEB_SEARCH_ENABLED=false`, restart, verify web search tool doesn't appear in `/api/v1/tools` response

### Tests for User Story 3

- [x] T027 [P] [US3] Write contract tests for GET /api/v1/tools endpoint in backend/tests/contract/test_tools_api.py
- [ ] T028 [P] [US3] Write unit tests for tool configuration loading in backend/tests/unit/tools/test_config.py

### Implementation for User Story 3

- [ ] T029 [US3] Implement tool configuration loading from env vars in backend/src/config/tools.py
- [x] T030 [US3] Implement GET /api/v1/tools endpoint in backend/src/api/routes/tools.py
- [x] T031 [US3] Register tools router in backend/src/api/routes/main.py
- [x] T032 [US3] Update backend/.env.example with tool configuration variables
- [x] T033 [US3] Run User Story 3 tests and verify they pass

**Checkpoint**: Tool configuration complete - administrators can enable/disable tools and query enabled tools

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and improvements across all stories

- [ ] T034 [P] Update architecture.md with tool subsystem documentation
- [ ] T035 [P] Add tool usage examples to README or quickstart documentation
- [ ] T036 Code review and cleanup across all tool files
- [ ] T037 Run full test suite and verify all tests pass
- [ ] T038 Manual end-to-end testing: test all three user stories in sequence

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational completion
  - US1 can start immediately after Foundational
  - US2 can start after Foundational (independent of US1)
  - US3 can start after Foundational (independent of US1/US2)
- **Polish (Phase 6)**: Depends on desired user stories being complete

### User Story Dependencies

| Story | Depends On | Can Run In Parallel With |
|-------|------------|--------------------------|
| US1 (P1) | Foundational only | US2, US3 (if staffed) |
| US2 (P2) | Foundational only | US1, US3 (if staffed) |
| US3 (P3) | Foundational only | US1, US2 (if staffed) |

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Backend implementation before frontend
3. Core tool logic before SSE/API integration
4. Run story tests before moving to next story

### Parallel Opportunities per Phase

**Phase 1 (Setup):**
```
T002, T003 can run in parallel
```

**Phase 2 (Foundational):**
```
T004, T005 can run in parallel (tests)
T006, T007, T009 can run in parallel (implementation)
```

**Phase 3 (US1):**
```
T012, T013 can run in parallel (tests)
T019, T020 can run in parallel (frontend)
```

**Phase 4 (US2):**
```
T022 standalone test
```

**Phase 5 (US3):**
```
T027, T028 can run in parallel (tests)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T011)
3. Complete Phase 3: User Story 1 (T012-T021)
4. **STOP and VALIDATE**: Test web search independently
5. Deploy/demo MVP with web search capability

### Incremental Delivery

1. Setup + Foundational → Tool framework ready
2. Add US1 (Web Search) → Test → Deploy (MVP!)
3. Add US2 (BBC News) → Test → Deploy
4. Add US3 (Admin Config) → Test → Deploy
5. Polish → Final release

### Estimated Task Counts

| Phase | Tasks | Parallel Opportunities |
|-------|-------|----------------------|
| Setup | 3 | 2 |
| Foundational | 8 | 5 |
| US1 (MVP) | 10 | 4 |
| US2 | 5 | 1 |
| US3 | 7 | 2 |
| Polish | 5 | 2 |
| **Total** | **38** | **16** |

---

## Notes

- All tools use free services (DuckDuckGo, BBC RSS) - no API keys required
- Constitution requires TDD - all test tasks included
- [P] tasks can run in parallel within their phase
- [Story] labels enable tracking which tasks belong to which user story
- Each user story is independently testable and deployable
- Stop at any checkpoint to validate current functionality
