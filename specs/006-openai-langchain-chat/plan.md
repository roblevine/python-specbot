# Implementation Plan: OpenAI LangChain Chat Integration

**Branch**: `006-openai-langchain-chat` | **Date**: 2026-01-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-openai-langchain-chat/spec.md`

## Summary

Route chat messages to OpenAI's ChatGPT model via LangChain, replacing the current loopback API with real AI responses. This is the first production LLM integration, designed for future multi-model support. The backend will be extended with an LLM service layer using LangChain, while the frontend requires no changes as the API contract remains compatible.

## Technical Context

**Language/Version**: Python 3.13 (backend), JavaScript ES6+ (frontend)
**Primary Dependencies**: FastAPI 0.115.0, LangChain, langchain-openai, Vue 3.4.0, Vite 5.0.0
**Storage**: LocalStorage (frontend, existing), N/A for backend (stateless)
**Testing**: pytest 8.3.0 + pytest-asyncio (backend), Vitest 1.0.0 + Playwright 1.40.0 (frontend)
**Target Platform**: Linux server (backend), Modern browsers (frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: AI response within 10 seconds (per SC-001)
**Constraints**: Conversation context for 10+ messages (per SC-002), no sensitive data exposure (per SC-003)
**Scale/Scope**: Single-user chat application, initial OpenAI integration

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | PASS | Extending existing `/api/v1/messages` contract; response format preserved |
| II. Modular Architecture | PASS | New `llm_service.py` module with clear boundary; LangChain abstraction |
| III. Test-First Development | REQUIRED | Tests must be written before LLM service implementation |
| IV. Integration & Contract Testing | REQUIRED | Contract tests must validate AI responses; update OpenAPI spec |
| V. Observability & Debuggability | REQUIRED | LLM calls must be logged; error contexts preserved |
| VI. Simplicity & YAGNI | PASS | Single OpenAI model only; no premature multi-model abstraction |
| VII. Versioning & Breaking Changes | PASS | Non-breaking change; response format compatible |
| VIII. Incremental Delivery | REQUIRED | Implement as thin slices: P1 (send/receive) → P2 (context) → P3 (errors) |
| IX. Living Architecture Documentation | REQUIRED | Update architecture.md with LLM service layer |

**Architecture Update Required**: Yes - new LLM service layer, LangChain integration, OpenAI dependency

## Project Structure

### Documentation (this feature)

```text
specs/006-openai-langchain-chat/
├── plan.md              # This file
├── research.md          # Phase 0 output - LangChain best practices
├── data-model.md        # Phase 1 output - Message/conversation models
├── quickstart.md        # Phase 1 output - Developer setup guide
├── contracts/           # Phase 1 output - Updated OpenAPI spec
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── routes/
│   │       └── messages.py          # Extend to call LLM service
│   ├── schemas.py                   # Existing MessageRequest/Response (unchanged)
│   ├── services/
│   │   ├── message_service.py       # Existing validation (keep)
│   │   └── llm_service.py           # NEW: LangChain OpenAI integration
│   ├── middleware/
│   │   └── logging_middleware.py    # Existing (unchanged)
│   └── utils/
│       └── logger.py                # Existing (unchanged)
├── tests/
│   ├── unit/
│   │   ├── test_message_service.py  # Existing
│   │   └── test_llm_service.py      # NEW: LLM service unit tests
│   ├── integration/
│   │   ├── test_message_loopback_flow.py  # Update for AI responses
│   │   └── test_openai_integration.py     # NEW: OpenAI integration tests
│   └── contract/
│       └── test_message_api_contract.py   # Update contract assertions
├── requirements.txt                 # Add langchain, langchain-openai
└── .env.example                     # Add OPENAI_API_KEY, OPENAI_MODEL

frontend/
├── src/
│   ├── components/                  # No changes required
│   ├── services/
│   │   └── apiClient.js             # No changes required
│   └── state/
│       └── useMessages.js           # No changes required
└── tests/                           # No changes required (API contract unchanged)
```

**Structure Decision**: Web application with existing frontend/backend split. Backend extended with new LLM service module. Frontend unchanged - API contract remains compatible.

## Complexity Tracking

No violations to justify. Design follows constitution principles:
- Single new module (llm_service.py) with clear purpose
- LangChain is user-required (not premature abstraction)
- No speculative features for future models
