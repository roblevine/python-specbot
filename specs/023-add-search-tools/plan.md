# Implementation Plan: Add Search Tools to Chatbot

**Branch**: `023-add-search-tools` | **Date**: 2026-01-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/023-add-search-tools/spec.md`

## Summary

This feature introduces a modular tool architecture to the chatbot, enabling LLM-driven tool usage during conversations. The initial implementation includes a web search tool (using DuckDuckGo via LangChain - free, no API key) and a BBC News search tool (using RSS feeds). Tools are standalone modules configured via environment variables, following the existing provider pattern in the codebase. LangChain's native tool support will be leveraged to integrate tools with the existing chat flow while maintaining streaming capabilities.

## Technical Context

**Language/Version**: Python 3.13 (backend), JavaScript ES6+ (frontend)
**Primary Dependencies**: FastAPI 0.115.0, LangChain 0.3+, langchain-community (DuckDuckGo), langchain-openai, langchain-anthropic, langchain-ollama, feedparser, Vue 3.4.0, Vite 5.0.0
**Storage**: File-based JSON (backend conversations), Browser localStorage (frontend settings) - No changes required
**Testing**: pytest (backend), Vitest (frontend)
**Target Platform**: Linux server (backend), Modern browsers (frontend)
**Project Type**: Web application (separate frontend/backend)
**Performance Goals**: Tool responses within 10 seconds, streaming maintained during tool execution
**Constraints**: Graceful degradation when tools unavailable, no breaking changes to existing chat API
**Scale/Scope**: 2 initial tools (Web Search via DuckDuckGo, BBC News via RSS), extensible architecture for future tools, no API keys required

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence/Notes |
|-----------|--------|----------------|
| I. API-First Design | PASS | New `/api/v1/tools` endpoint will have OpenAPI contract defined before implementation |
| II. Modular Architecture | PASS | Tools designed as standalone modules in `backend/src/services/tools/`, following existing provider pattern |
| III. Test-First Development | PASS | Tests will be written first for tool protocol, registry, and individual tools |
| IV. Integration & Contract Testing | PASS | Contract tests for tools endpoint, integration tests for tool execution flow |
| V. Observability & Debuggability | PASS | Structured logging for tool invocations, timing metrics, error contexts |
| VI. Simplicity & YAGNI | PASS | Starting with 2 tools, no speculative multi-tool orchestration |
| VII. Versioning & Breaking Changes | PASS | Additive API changes only, existing `/messages` endpoint extended but not broken |
| VIII. Incremental Delivery | PASS | P1: Web Search tool (DuckDuckGo) + framework, P2: BBC News tool, P3: Admin tools endpoint |
| IX. Living Architecture Documentation | PASS | Will update architecture.md with tool subsystem documentation |

**Architecture Update Required**: Yes - New tool subsystem adds:
- New module: `backend/src/services/tools/` with base protocol, registry, and tool implementations
- New API endpoint: `GET /api/v1/tools` for listing enabled tools
- Extended SSE format: New event types for tool invocation status
- Configuration: Tool-specific environment variables following provider pattern

## Project Structure

### Documentation (this feature)

```text
specs/023-add-search-tools/
├── plan.md              # This file
├── research.md          # Phase 0 output - technology decisions
├── data-model.md        # Phase 1 output - entity definitions
├── quickstart.md        # Phase 1 output - developer guide
├── contracts/           # Phase 1 output - OpenAPI specs
│   ├── tools-api.yaml   # Tools endpoint contract
│   └── messages-sse.md  # Extended SSE event types
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── routes/
│   │       ├── messages.py      # Extended for tool-aware streaming
│   │       └── tools.py         # NEW: Tools list endpoint
│   ├── config/
│   │   └── tools.py             # NEW: Tool configuration loading
│   ├── services/
│   │   ├── tools/               # NEW: Tool subsystem
│   │   │   ├── __init__.py      # Tool registry export
│   │   │   ├── base.py          # BaseTool protocol + ToolResult
│   │   │   ├── registry.py      # ToolRegistry class
│   │   │   ├── errors.py        # Tool-specific errors
│   │   │   ├── web_search.py    # Web Search tool (DuckDuckGo)
│   │   │   └── bbc_news.py      # BBC News tool (RSS)
│   │   └── llm_service.py       # Extended for tool binding
│   └── schemas.py               # Extended with tool-related schemas
└── tests/
    ├── contract/
    │   └── test_tools_api.py    # NEW: Contract tests
    ├── integration/
    │   └── test_tool_execution.py # NEW: Tool integration tests
    └── unit/
        └── tools/               # NEW: Tool unit tests
            ├── test_base.py
            ├── test_registry.py
            ├── test_web_search.py
            └── test_bbc_news.py

frontend/
├── src/
│   ├── components/
│   │   └── ChatMessage.vue      # Extended for tool status display
│   └── services/
│       └── apiClient.js         # Extended for tool SSE events
└── tests/
    └── [component tests as needed]
```

**Structure Decision**: Web application structure (Option 2) - matches existing codebase with separate frontend/backend directories. Tools follow the established provider pattern with Protocol-based interfaces and a registry for runtime discovery.

## Complexity Tracking

> No violations to justify - design follows existing patterns.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Tool architecture | Matches provider pattern | Reuses proven Protocol + Registry approach from providers |
| LangChain tools | Native integration | LangChain already supports tools natively, no custom framework needed |
| Configuration | Environment variables | Consistent with OPENAI_MODELS, ANTHROPIC_MODELS pattern |
