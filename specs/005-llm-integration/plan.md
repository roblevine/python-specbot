# Implementation Plan: LLM Backend Integration

**Branch**: `005-llm-integration` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-llm-integration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate LLM backend to enable real-time AI conversations with streaming responses. Users can send messages and receive progressive AI-generated responses from either GPT-5 or GPT-5 Codex models, selected via a status bar picker. The system maintains conversation context across multiple message exchanges and handles errors gracefully with dual feedback (status bar indicator + chat area details). The Send button transforms to a Stop button during streaming, allowing users to interrupt responses.

## Technical Context

**Language/Version**: Python 3.13 (backend), JavaScript ES6+ (frontend)
**Primary Dependencies**: FastAPI 0.115.0, Pydantic 2.10.0, **LangChain 0.3.x** (langchain-core, langchain-openai for initial phase, langchain-anthropic and langchain-community for imminent multi-provider support), Vue.js 3.4.0, Vite 5.0.0
**Storage**: Browser LocalStorage (conversation history and model selection persistence), Backend stateless (conversation context managed by LangChain memory)
**Testing**: pytest 8.3.0 (backend unit/integration/contract), Vitest 1.0.0 (frontend unit/integration), Playwright 1.40.0 (E2E), openapi-core 0.18.2 (contract validation)
**Target Platform**: Web application (Linux server backend via uvicorn, browser-based frontend)
**Project Type**: Web (frontend/backend separation)
**Performance Goals**: First token < 3 seconds (SC-001), Stop button response < 500ms (SC-009), streaming with progressive rendering (SC-002)
**Constraints**: 10-second API timeout (frontend), stateless backend (no server-side conversation storage), LLM provider rate limits (varies by provider)
**Scale/Scope**: Single-user chatbot, conversation context managed by LangChain memory (4k-128k tokens depending on model), Initial: 2 OpenAI models (GPT-5, GPT-5 Codex), Imminent (days/weeks): Multi-provider (Anthropic Claude, Ollama, local models), RAG integration, MCP support

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: API-First Design ✅ PASS
- **Status**: Contract must be defined before implementation
- **Action**: Will create OpenAPI contract for streaming LLM endpoint in Phase 1 (contracts/)
- **Compliance**: Following existing pattern from feature 003 (message-api.yaml)

### Principle II: Modular Architecture ✅ PASS
- **Status**: Feature follows existing modular structure
- **Backend Modules**: New LLM service module (llm_service.py), existing routes/messages.py extended
- **Frontend Modules**: New streaming handler, model picker component, existing state management extended
- **Boundaries**: Clear separation between LLM client, message routing, and UI streaming

### Principle III: Test-First Development (NON-NEGOTIABLE) ✅ PASS
- **Status**: TDD workflow will be followed per constitution
- **Workflow**: Write failing tests → implement → refactor
- **Test Coverage**: Unit tests (LLM service, streaming), integration tests (API endpoints), contract tests (request/response validation), E2E tests (user flows)

### Principle IV: Integration & Contract Testing (NON-NEGOTIABLE) ✅ PASS
- **Status**: Contract tests required for new streaming endpoint
- **Action**: Will create consumer-driven contract tests with request AND response validation
- **Snapshots**: Contract snapshots will be committed to tests/contract/snapshots/
- **Workflow**: Frontend captures requests → validate against OpenAPI → backend replays snapshots

### Principle V: Observability & Debuggability ✅ PASS
- **Status**: Structured logging required for LLM interactions
- **Logging Points**: LLM request/response, streaming events, errors, model selection
- **Error Context**: LLM API errors include actionable details (rate limit, auth, network)
- **Compliance**: Following existing logging pattern (backend/src/utils/logger.py)

### Principle VI: Simplicity & YAGNI ✅ PASS (with justification)
- **Status**: LangChain chosen despite higher complexity due to imminent feature requirements
- **Approach**: Start with OpenAI via LangChain, architecture ready for imminent multi-provider/RAG/MCP additions
- **Technology Choice**: **LangChain 0.3.x** (justified by confirmed roadmap - see rationale below)
- **YAGNI Justification**: Multi-provider support, RAG, and MCP are NOT speculative - all confirmed for implementation within days/weeks. Starting with simpler library (OpenAI SDK) would require complete rework in days. LangChain's complexity is necessary infrastructure for the actual roadmap, not speculative features.

### Principle VII: Versioning & Breaking Changes ✅ PASS
- **Status**: API changes follow semantic versioning
- **New Endpoint**: `/api/v1/chat/stream` (new, not breaking existing endpoints)
- **Model Field**: Add `selectedModel` to frontend storage schema (requires migration plan)

### Principle VIII: Incremental Delivery & Thin Slices (NON-NEGOTIABLE) ✅ PASS
- **Status**: Feature will be implemented in prioritized slices
- **Slice 1 (P1)**: Send message → receive streamed AI response (end-to-end value)
- **Slice 2 (P2)**: Model picker in status bar → route to selected model
- **Slice 3 (P3)**: Conversation context management
- **Prohibited**: Will NOT implement all UI/backend/streaming in one commit

### Principle IX: Living Architecture Documentation ⚠️ ACTION REQUIRED
- **Status**: Feature introduces new architectural components
- **Required Updates to architecture.md**:
  - Add LLM integration layer to Current Architecture
  - Document streaming SSE/EventSource pattern
  - Add LLM provider abstraction to Technology Stack
  - Create ADR for LLM library choice (after Phase 0 research)
  - Update data flow diagram (frontend → backend → LLM provider)

**Gate Status**: ✅ PASS (with action required to update architecture.md during implementation)

**Note**: This feature introduces significant architectural changes:
- New external integration (LLM APIs - initially OpenAI, imminent: Anthropic, Ollama, local models)
- New communication pattern (Server-Sent Events for streaming)
- New backend service layer (LangChain-based LLM abstraction)
- Frontend state management for streaming and model selection
- Architecture designed for imminent RAG and MCP integration

**Product Roadmap Context** (justifies LangChain choice):
- **Days 1-7 (Feature 005)**: Basic OpenAI streaming with GPT-5/GPT-5 Codex
- **Week 2 (Feature 006+)**: Multi-provider support (Anthropic Claude, Ollama, local models)
- **Weeks 3-4 (Feature 007+)**: RAG integration (vector stores, document retrieval)
- **Weeks 4-5 (Feature 008+)**: MCP (Model Context Protocol) integration

All features above are **confirmed and imminent**, not speculative. LangChain provides the foundation for this roadmap without requiring architectural rewrites.

architecture.md MUST be updated with these changes when implementing each slice.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── routes/
│   │       ├── messages.py         # Extend for streaming endpoint
│   │       └── chat.py             # NEW: Streaming chat endpoint
│   ├── services/
│   │   ├── message_service.py      # Existing loopback service
│   │   └── llm_service.py          # NEW: LLM client abstraction
│   ├── middleware/
│   │   └── logging_middleware.py   # Existing (may extend for streaming logs)
│   ├── utils/
│   │   └── logger.py               # Existing structured logging
│   ├── schemas.py                  # Extend with streaming models
│   └── config.py                   # NEW: LLM configuration (API keys, models)
├── tests/
│   ├── unit/
│   │   ├── test_message_service.py # Existing
│   │   └── test_llm_service.py     # NEW: LLM service unit tests
│   ├── integration/
│   │   ├── test_message_loopback_flow.py # Existing
│   │   └── test_streaming_chat.py  # NEW: Streaming endpoint tests
│   ├── contract/
│   │   ├── test_message_api_contract.py # Existing
│   │   └── test_chat_streaming_contract.py # NEW: Streaming contract tests
│   └── conftest.py                 # Extend with LLM mocks
├── main.py                          # Register new chat router
└── requirements.txt                 # Add LLM library dependency

frontend/
├── src/
│   ├── components/
│   │   ├── App.vue                 # Existing
│   │   ├── StatusBar.vue           # EXTEND: Add model picker
│   │   ├── ChatArea.vue            # EXTEND: Stream rendering
│   │   ├── InputArea.vue           # EXTEND: Send → Stop button
│   │   ├── MessageBubble.vue       # Existing
│   │   ├── HistorySidebar.vue      # Existing
│   │   └── ModelPicker.vue         # NEW: Model selection dropdown
│   ├── state/
│   │   ├── useMessages.js          # EXTEND: Streaming state
│   │   ├── useAppState.js          # EXTEND: Error state for status bar
│   │   ├── useConversations.js     # Existing
│   │   └── useModelSelection.js    # NEW: Model picker state
│   ├── services/
│   │   ├── apiClient.js            # EXTEND: Streaming endpoint
│   │   └── streamingClient.js      # NEW: EventSource/SSE handler
│   ├── storage/
│   │   ├── LocalStorageAdapter.js  # EXTEND: Model selection persistence
│   │   └── StorageSchema.js        # EXTEND: Add selectedModel field (v2.0.0)
│   └── utils/
│       ├── idGenerator.js          # Existing
│       ├── validators.js           # Existing
│       └── logger.js               # Existing
├── tests/
│   ├── unit/
│   │   ├── ModelPicker.test.js     # NEW: Model picker tests
│   │   └── streamingClient.test.js # NEW: Streaming client tests
│   ├── integration/
│   │   └── streaming-flow.test.js  # NEW: Full streaming integration
│   ├── contract/
│   │   └── chat-streaming-contract.test.js # NEW: Contract validation
│   └── e2e/
│       └── llm-integration.spec.js # NEW: E2E streaming tests
└── package.json                     # Add dependencies (if needed)

tests/ (repo root)
└── contract/
    └── snapshots/
        └── chat-streaming/          # NEW: Contract snapshots for streaming
```

**Structure Decision**: Web application with frontend/backend separation. This feature extends existing modules (StatusBar, InputArea, apiClient) and adds new modules for LLM integration (llm_service.py, streamingClient.js, ModelPicker.vue). Contract tests follow established pattern with snapshots in tests/contract/snapshots/.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
