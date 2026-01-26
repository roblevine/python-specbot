# Implementation Plan: LangChain Tool Integration

**Branch**: `024-add-langchain-tools` | **Date**: 2026-01-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/024-add-langchain-tools/spec.md`

## Summary

Integrate LangChain tools (DuckDuckGo search and web browser) into the chatbot with:
- Server-side tool configuration via environment variables (following existing model config pattern)
- Provider-agnostic tool binding for OpenAI, Anthropic, and Ollama
- SSE streaming of tool call events to frontend
- Collapsible tool call UI in conversation stream showing status and details
- Persistent storage of tool call records in conversation history

## Technical Context

**Language/Version**: Python 3.13 (backend), JavaScript ES6+ (frontend)
**Primary Dependencies**: FastAPI 0.115.0, LangChain 0.3+, langchain-openai 0.2+, langchain-anthropic 0.2+, langchain-ollama 0.2+, Vue 3.4.0, Vite 5.0.0
**Storage**: File-based JSON with schema versioning (v1.0.0 → v1.1.0 for tool calls)
**Testing**: pytest 8.3.0, pytest-asyncio 0.24.0, Vitest 1.0.0, Playwright 1.40.0
**Target Platform**: Linux server (backend), Modern browsers (frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Tool calls should complete within reasonable timeouts (30s for search, 60s for browser); streaming latency <100ms for tool call events
**Constraints**: Tool results may be large (web pages); need truncation/summarization. Cross-provider compatibility required.
**Scale/Scope**: 2 tools initially (DuckDuckGo search, web browser); extensible configuration for future tools

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | ✅ PASS | Will define tool call SSE event contracts before implementation |
| II. Modular Architecture | ✅ PASS | Tools as self-contained modules with registry pattern (follows provider pattern) |
| III. Test-First Development | ✅ PASS | Will write tests for tool loading, execution, and streaming before implementation |
| IV. Integration & Contract Testing | ✅ PASS | Contract tests for new SSE event types; integration tests for tool execution |
| V. Observability & Debuggability | ✅ PASS | Tool loading logged at startup; debug info in error events when DEBUG enabled |
| VI. Simplicity & YAGNI | ✅ PASS | Start with 2 tools; no speculative abstractions; follow existing patterns |
| VII. Versioning & Breaking Changes | ✅ PASS | Storage schema bump v1.0.0 → v1.1.0 for tool calls; backward compatible |
| VIII. Incremental Delivery | ✅ PASS | User stories prioritized P1-P3; thin slices per story |
| IX. Living Architecture Documentation | ✅ PASS | Will update architecture.md with tool subsystem |

**Architecture Documentation Update Required**: Yes - this feature adds:
- New tool subsystem (tool registry, tool configuration, tool execution)
- New SSE event types (tool_call, tool_result)
- Extended message schema for tool call records
- New frontend component (ToolCallBubble)

## Project Structure

### Documentation (this feature)

```text
specs/024-add-langchain-tools/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── tool-events.yaml # SSE event schemas
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── config/
│   │   ├── models.py         # Existing model configuration
│   │   └── tools.py          # NEW: Tool configuration
│   ├── services/
│   │   ├── providers/        # Existing provider implementations
│   │   ├── tools/            # NEW: Tool implementations
│   │   │   ├── __init__.py   # Tool registry
│   │   │   ├── base.py       # Base tool interface
│   │   │   ├── duckduckgo.py # DuckDuckGo search tool
│   │   │   └── browser.py    # Web browser tool
│   │   └── llm_service.py    # Extend for tool binding
│   ├── schemas.py            # Extend with tool call schemas
│   └── storage/
│       └── file_storage.py   # Extend for tool call persistence
└── tests/
    ├── unit/
    │   └── test_tools.py     # NEW: Tool unit tests
    ├── integration/
    │   └── test_tool_execution.py  # NEW: Tool integration tests
    └── contract/
        └── test_tool_events.py     # NEW: SSE event contract tests

frontend/
├── src/
│   ├── components/
│   │   └── ChatArea/
│   │       ├── MessageBubble.vue   # Existing
│   │       └── ToolCallBubble.vue  # NEW: Collapsible tool call UI
│   ├── services/
│   │   └── apiClient.js            # Extend for tool call events
│   └── state/
│       └── useMessages.js          # Extend for tool call state
└── tests/
    └── unit/
        └── ToolCallBubble.spec.js  # NEW: Component tests
```

**Structure Decision**: Follows existing web application structure with backend/frontend separation. Tool implementations follow the provider pattern with registry and configuration loading at startup.

## Complexity Tracking

> No violations - design follows existing patterns and constitution principles.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
