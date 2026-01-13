# SpecBot Architecture

**Last Updated**: 2026-01-13
**Current Version**: P1 + Backend API + OpenAI LangChain Chat + Model Selector + Message Streaming MVP (Features 006, 008, 009 Partial)

This document describes the current implemented architecture and planned future architecture for SpecBot.

---

## Current Architecture

### Overview

SpecBot is a **full-stack AI chat application** with a Vue.js frontend and Python FastAPI backend. The backend integrates with OpenAI ChatGPT via LangChain, providing AI-powered conversations with context retention and graceful error handling.

**Status**: ✅ **IMPLEMENTED** (Frontend P1 + Backend API 003 + OpenAI LangChain Chat 006 Complete)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (Client-Side)                    │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Vue.js Application (SPA)                   │ │
│  │                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │ │
│  │  │  StatusBar   │  │ HistorySidebar│  │  ChatArea    │  │ │
│  │  │ Component    │  │  Component    │  │  Component   │  │ │
│  │  └──────┬───────┘  └──────┬────────┘  └──────┬───────┘  │ │
│  │         │                 │                   │          │ │
│  │         └─────────────────┼───────────────────┘          │ │
│  │                           │                              │ │
│  │                  ┌────────▼────────┐                     │ │
│  │                  │ State Management│                     │ │
│  │                  │  (Composables)  │                     │ │
│  │                  └────────┬────────┘                     │ │
│  │                           │                              │ │
│  │         ┌─────────────────┼─────────────────┐            │ │
│  │         │                 │                 │            │ │
│  │    ┌────▼─────┐   ┌──────▼──────┐   ┌─────▼──────┐     │ │
│  │    │   API    │   │   Storage   │   │ InputArea  │     │ │
│  │    │  Client  │   │   Adapter   │   │ Component  │     │ │
│  │    └────┬─────┘   │(LocalStorage)│   └────────────┘     │ │
│  │         │         └─────────────┘                       │ │
│  └─────────┼───────────────────────────────────────────────┘ │
│            │                                                 │
│  ┌─────────▼──────────────────────────────────────────────┐ │
│  │           Browser LocalStorage (Persistence)            │ │
│  │    - Conversations (messages, metadata, timestamps)     │ │
│  │    - Model Selection (selectedModelId)                  │ │
│  │    - Schema Version: v1.1.0                             │ │
│  └─────────────────────────────────────────────────────────┘ │
└────────────┼────────────────────────────────────────────────┘
             │
     HTTP POST /api/v1/messages
             │
┌────────────▼────────────────────────────────────────────────┐
│              Backend API Server (Python/FastAPI)             │
│                     Port 8000                                │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  API Routes Layer                       │ │
│  │         POST /api/v1/messages (AI chat)                 │ │
│  │         GET /api/v1/models (model list)                 │ │
│  │         GET /health (health check)                      │ │
│  └──────────────────────┬─────────────────────────────────┘ │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │              Message Service Layer                    │   │
│  │   - validate_message(text)                            │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │                LLM Service Layer                      │   │
│  │   - get_ai_response(message, history)                 │   │
│  │   - Error mapping & sanitization                      │   │
│  │   - ChatOpenAI via LangChain                          │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │               Middleware Layer                        │   │
│  │   - CORS (allows localhost:5173)                      │   │
│  │   - Logging (request/response)                        │   │
│  │   - Error handling (sanitized 503/504)                │   │
│  └──────────────────────┬───────────────────────────────┘   │
└────────────────────────┼────────────────────────────────────┘
                         │
                 OpenAI API (ChatGPT)
                         │
                    ┌────▼────┐
                    │ OpenAI  │
                    │ ChatGPT │
                    │  API    │
                    └─────────┘
```

### Component Structure

**Frontend Application** (`frontend/src/`)

```
frontend/
├── src/
│   ├── components/           # Vue Single File Components
│   │   ├── App.vue          # Root component (4-panel layout)
│   │   ├── StatusBar.vue    # Application status (Ready/Processing/Error)
│   │   ├── HistorySidebar.vue # Conversation list (currently single conversation)
│   │   ├── ChatArea.vue     # Message display with user/system distinction
│   │   └── InputArea.vue    # Text input + Send button
│   │
│   ├── state/               # State management (Vue Composition API)
│   │   ├── useMessages.js   # Message state composable (with API integration)
│   │   ├── useAppState.js   # Application state (processing, status, errors)
│   │   └── useConversations.js  # Conversation state composable
│   │
│   ├── services/            # External service integrations
│   │   └── apiClient.js     # Backend API client (fetch wrapper)
│   │
│   ├── storage/             # Persistence layer
│   │   ├── LocalStorageAdapter.js  # LocalStorage adapter
│   │   └── StorageSchema.js        # Data schema v1.0.0
│   │
│   └── utils/               # Shared utilities
│       ├── validators.js    # Input validation
│       ├── logger.js        # Logging utilities
│       └── idGenerator.js   # UUID generation
│
├── tests/
│   ├── unit/                # Unit tests (Vitest) - 68 tests
│   ├── integration/         # Integration tests (Vitest) - 4 tests
│   └── e2e/                 # End-to-end tests (Playwright) - 4 tests
│
└── public/                  # Static assets
```

**Backend API Server** (`backend/`)

```
backend/
├── src/
│   ├── api/
│   │   └── routes/
│   │       └── messages.py  # POST /api/v1/messages endpoint (AI chat)
│   │
│   ├── services/
│   │   ├── message_service.py  # Message validation
│   │   └── llm_service.py      # LLM integration (ChatOpenAI via LangChain)
│   │
│   ├── middleware/
│   │   └── logging_middleware.py  # Request/response logging
│   │
│   ├── utils/
│   │   └── logger.py        # Structured logging setup (with LLM logging)
│   │
│   └── schemas.py           # Pydantic models (MessageRequest, MessageResponse)
│
├── tests/
│   ├── contract/            # OpenAPI schema validation tests (51 tests)
│   ├── integration/         # Full request-response cycle tests
│   └── unit/                # Service and utility tests
│
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies (includes langchain, langchain-openai)
└── pytest.ini              # Test configuration
```

### Technology Stack (Current)

| Layer | Technology | Version | Status |
|-------|-----------|---------|--------|
| **Frontend Framework** | Vue.js (Composition API) | 3.4.0 | ✅ In Use |
| **Build Tool** | Vite | 5.0.0 | ✅ In Use |
| **Frontend Testing** | Vitest + Playwright | Latest | ✅ In Use |
| **State Management** | Vue Composables | Native | ✅ In Use |
| **Frontend Storage** | Browser LocalStorage | Native API | ✅ In Use |
| **Backend Language** | Python | 3.13 | ✅ In Use |
| **Backend Framework** | FastAPI | 0.115.0 | ✅ In Use |
| **ASGI Server** | uvicorn | 0.32.0 | ✅ In Use |
| **Data Validation** | Pydantic | 2.10.0 | ✅ In Use |
| **LLM Framework** | LangChain | 0.3.0+ | ✅ In Use |
| **LLM Provider** | langchain-openai (OpenAI ChatGPT) | 0.2.0+ | ✅ In Use |
| **Backend Testing** | pytest + httpx + openapi-core | 8.3.0 | ✅ In Use |
| **API Documentation** | OpenAPI 3.1 (auto-generated) | 3.1.0 | ✅ In Use |
| **Code Quality** | ESLint + Prettier (frontend) | Latest | ✅ In Use |
| **Package Manager** | npm (frontend), pip (backend) | 8+ / Latest | ✅ In Use |

### Data Flow (Current Implementation)

**Frontend → Backend → OpenAI ChatGPT → Backend → Frontend** (Feature 006)

```
User Action (Type Message)
    │
    ▼
InputArea Component
    │
    ├─► Validation (utils/validators.js)
    │
    ▼
State Management (useMessages.js)
    │
    ├─► Generate Message ID (utils/idGenerator.js)
    ├─► Add User Message (optimistic update)
    │
    ▼
API Client (services/apiClient.js)
    │
    ├─► POST /api/v1/messages
    ├─► Timeout: 10 seconds
    ├─► Headers: Content-Type: application/json
    │
    ▼
Backend API Server (main.py)
    │
    ├─► CORS Middleware (validate origin)
    ├─► Logging Middleware (log request)
    │
    ▼
Messages Route (/api/v1/messages)
    │
    ├─► Pydantic Validation (MessageRequest schema)
    │
    ▼
Message Service (message_service.py)
    │
    ├─► validate_message() - Check empty, whitespace, length
    │
    ▼
LLM Service (llm_service.py)
    │
    ├─► get_ai_response(message, history) - Get AI response with context
    ├─► convert_to_langchain_messages() - Format history for ChatGPT
    ├─► ChatOpenAI.ainvoke() - Call OpenAI API via LangChain
    ├─► Error mapping & sanitization (503/504/400)
    │
    ▼
OpenAI ChatGPT API
    │
    ├─► Process message with conversation context
    ├─► Generate intelligent response
    │
    ▼
LLM Service receives AI response
    │
    ├─► Return AI-generated message
    │
    ▼
MessageResponse (Pydantic schema)
    │
    ├─► status: "success"
    ├─► message: "{ai_response}"
    ├─► timestamp: server timestamp
    │
    ▼
HTTP Response (200 OK, JSON)
    │
    ▼
API Client (receives response)
    │
    ├─► Error handling (timeout, network, HTTP errors)
    │
    ▼
State Management (useMessages.js)
    │
    ├─► Add System Message (from API response)
    ├─► Mark User Message as sent
    │
    ▼
Storage Adapter (LocalStorageAdapter.js)
    │
    ├─► Serialize to Schema v1.0.0
    ├─► Write to Browser LocalStorage
    │
    ▼
State Update Triggers Re-render
    │
    ▼
ChatArea Component (Displays AI-generated responses)
```

### Module Boundaries (Current)

**Components** ↔ **State Management**
- Interface: Vue reactive refs and composables
- Components consume state via `useConversation()` composable
- Components never directly access storage

**State Management** ↔ **Storage**
- Interface: `loadConversation()`, `saveConversation()` functions
- State layer handles business logic (loopback generation, validation)
- Storage layer handles serialization and persistence

**Utilities** → Used by all layers
- Pure functions with no side effects
- No dependencies on other modules

### Data Schema (Current)

**LocalStorage Schema v1.1.0** (`frontend/src/storage/schema.js`)

```javascript
{
  version: "1.1.0",
  conversations: [
    {
      id: "uuid-v4",
      title: "Conversation Title",
      createdAt: "ISO-8601 timestamp",
      updatedAt: "ISO-8601 timestamp",
      messages: [
        {
          id: "uuid-v4",
          role: "user" | "system",
          content: "Message text",
          timestamp: "ISO-8601 timestamp",
          model: "gpt-4" | "gpt-3.5-turbo" | null  // Feature 008: Model used for response
        }
      ]
    }
  ],
  activeConversationId: "uuid-v4" | null,
  selectedModelId: "gpt-4" | "gpt-3.5-turbo" | null,  // Feature 008: Currently selected model
  preferences: {
    sidebarCollapsed: boolean  // Feature 007: UI preference
  }
}
```

**Schema Migration**: v1.0.0 → v1.1.0
- Added `selectedModelId` field for model selection persistence
- Added `model` field to messages to track which model generated each response
- Added `preferences` object for UI state persistence

---

## Planned Architecture

### Overview

The planned architecture evolves SpecBot into a **full-stack chat application** with backend API and multiple LLM provider integrations.

**Status**: ⚠️ **NOT IMPLEMENTED**

### Future Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  Browser (Client-Side)                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Vue.js Frontend (Same as Current)               │ │
│  │  + Multiple Conversation Navigation (P2)                │ │
│  │  + New Conversation Button (P3)                         │ │
│  │  + Enhanced Status/Error Handling (P4)                  │ │
│  └──────────────────────┬─────────────────────────────────┘ │
└─────────────────────────┼───────────────────────────────────┘
                          │
                   HTTP/WebSocket
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Backend API Server                          │
│                ⚠️ NOT IMPLEMENTED                            │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           API Layer (FastAPI/Python)                    │ │
│  │  - /api/conversations (CRUD)                            │ │
│  │  - /api/messages (send, stream)                         │ │
│  │  - /api/providers (list, configure)                     │ │
│  └──────────────────────┬─────────────────────────────────┘ │
│                         │                                    │
│  ┌────────────────────┬─▼──────────────┬─────────────────┐  │
│  │  Conversation      │  LLM Service   │  Provider       │  │
│  │  Service           │  Orchestrator  │  Adapters       │  │
│  └────────┬───────────┴────────┬───────┴────────┬────────┘  │
│           │                    │                │            │
│  ┌────────▼────────┐  ┌────────▼────────┐  ┌───▼─────────┐ │
│  │   PostgreSQL    │  │  Redis Cache    │  │  Provider   │ │
│  │   Database      │  │  (Sessions)     │  │  Configs    │ │
│  │ ⚠️ NOT IMPL     │  │ ⚠️ NOT IMPL     │  │ ⚠️ NOT IMPL │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
              Multiple LLM Provider APIs
                          │
         ┌────────────────┼────────────────┐
         │                │                │
    ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
    │ OpenAI  │     │ Anthropic│    │ Local   │
    │   API   │     │   API    │    │ LLMs    │
    │⚠️ NOT   │     │⚠️ NOT    │    │⚠️ NOT   │
    │  IMPL   │     │  IMPL    │    │  IMPL   │
    └─────────┘     └─────────┘     └─────────┘
```

### Planned Features (Priority Order)

#### P2: Multiple Conversation Navigation ⚠️ NOT IMPLEMENTED
- Switch between multiple conversations
- Conversation list with previews and timestamps
- Most recent conversation auto-selection
- **Technology**: Extend current Vue.js components
- **Storage**: Extend LocalStorage schema to support multiple conversations

#### P3: New Conversation Creation ⚠️ NOT IMPLEMENTED
- "New Conversation" button in UI
- Empty conversation handling
- Conversation organization/sorting
- **Technology**: Vue.js component additions
- **Storage**: LocalStorage (before backend migration)

#### P4: Enhanced Status & Error Handling ⚠️ NOT IMPLEMENTED
- Enhanced status bar (Ready/Processing/Error/Connecting)
- Error recovery mechanisms
- Connection status indicators
- Retry logic
- **Technology**: Vue.js composables for error state

#### Future: Backend API ⚠️ NOT IMPLEMENTED
- **Technology Stack** (Planned):
  - Language: Python 3.11+
  - Framework: FastAPI
  - Database: PostgreSQL
  - Cache: Redis
  - Authentication: JWT tokens
- **Endpoints** (Planned):
  - `POST /api/conversations` - Create conversation
  - `GET /api/conversations` - List conversations
  - `GET /api/conversations/{id}` - Get conversation
  - `POST /api/conversations/{id}/messages` - Send message
  - `GET /api/conversations/{id}/messages/stream` - Stream LLM response

#### Future: LLM Provider Integration ⚠️ NOT IMPLEMENTED
- Multiple provider support (OpenAI, Anthropic, local models)
- Provider switching per conversation
- Streaming response support (Server-Sent Events or WebSocket)
- Provider-specific configuration (API keys, model selection, parameters)
- **Architecture Pattern**: Adapter pattern for provider abstraction

### Technology Stack (Planned)

| Layer | Technology | Version | Status |
|-------|-----------|---------|--------|
| **Backend Framework** | FastAPI | 0.100+ | ⚠️ NOT IMPLEMENTED |
| **Backend Language** | Python | 3.11+ | ⚠️ NOT IMPLEMENTED |
| **Database** | PostgreSQL | 15+ | ⚠️ NOT IMPLEMENTED |
| **Cache** | Redis | 7+ | ⚠️ NOT IMPLEMENTED |
| **ORM** | SQLAlchemy | 2.0+ | ⚠️ NOT IMPLEMENTED |
| **API Testing** | pytest + httpx | Latest | ⚠️ NOT IMPLEMENTED |
| **LLM SDK - OpenAI** | openai | Latest | ⚠️ NOT IMPLEMENTED |
| **LLM SDK - Anthropic** | anthropic | Latest | ⚠️ NOT IMPLEMENTED |
| **Streaming** | SSE or WebSocket | Native | ⚠️ NOT IMPLEMENTED |

### Data Flow (Planned - Full Stack)

```
User Action (Send Message)
    │
    ▼
Frontend (Vue.js)
    │
    ├─► POST /api/conversations/{id}/messages
    │
    ▼
Backend API (FastAPI)
    │
    ├─► Conversation Service (validate, save to DB)
    │
    ▼
LLM Service Orchestrator
    │
    ├─► Select Provider (based on conversation config)
    ├─► Provider Adapter (OpenAI/Anthropic/Local)
    │
    ▼
LLM Provider API
    │
    ├─► Stream Response Chunks
    │
    ▼
Backend → Frontend (SSE/WebSocket)
    │
    ▼
ChatArea Component (Live Update)
```

---

## Architectural Decision Records (ADRs)

### ADR-001: Vue.js Composition API for State Management

**Date**: 2025-12-23
**Status**: ✅ Implemented

**Context**: Need state management for conversation and message handling in P1 MVP.

**Decision**: Use Vue 3 Composition API with composables instead of Vuex/Pinia.

**Rationale**:
- P1 MVP has simple state needs (single conversation, message list)
- Composition API provides sufficient reactivity and sharing
- Avoids heavyweight state management library for MVP
- Can migrate to Vuex/Pinia later if complexity increases
- Follows Vue 3 best practices and modern patterns

**Consequences**:
- ✅ Simpler codebase for MVP
- ✅ Easier testing (pure functions)
- ⚠️ May need refactoring if state complexity grows significantly in P3+

---

### ADR-002: LocalStorage for MVP Persistence

**Date**: 2025-12-23
**Status**: ✅ Implemented

**Context**: P1 MVP needs to persist conversations across browser sessions.

**Decision**: Use browser LocalStorage with versioned schema (v1.0.0).

**Rationale**:
- MVP is browser-based with no backend
- LocalStorage provides simple, synchronous persistence
- Schema versioning enables future migrations
- No server costs for MVP
- Fast prototyping and testing

**Consequences**:
- ✅ Zero backend infrastructure for MVP
- ✅ Instant persistence with no network latency
- ⚠️ Data limited to ~5-10MB per domain
- ⚠️ Data not shared across devices/browsers
- ⚠️ Must migrate to backend storage in future (P4+ or LLM integration)

**Migration Path**: When backend is added, LocalStorage adapter will be replaced with API calls. Schema versioning ensures smooth data migration.

---

### ADR-003: Modular Component Architecture

**Date**: 2025-12-23
**Status**: ✅ Implemented

**Context**: Frontend needs clear separation of concerns and independent testability.

**Decision**: Organize code into layers: Components → State → Storage → Utils.

**Rationale**:
- Aligns with Constitution Principle II (Modular Architecture)
- Each layer has single responsibility
- Independent testing of each layer
- Clear boundaries prevent coupling
- Easy to replace layers (e.g., swap LocalStorage for API client)

**Consequences**:
- ✅ Highly testable (76 tests passing)
- ✅ Easy to understand component responsibilities
- ✅ Storage abstraction enables future backend migration
- ✅ Utils are reusable across project

---

### ADR-004: Test-First Development with Vitest + Playwright

**Date**: 2025-12-23
**Status**: ✅ Implemented

**Context**: Constitution Principle III mandates Test-Driven Development (TDD).

**Decision**: Use Vitest for unit/integration tests and Playwright for E2E tests.

**Rationale**:
- Vitest is Vite-native (same config, fast, ESM support)
- Playwright provides reliable cross-browser E2E testing
- TDD workflow: write failing tests → implement → verify green
- Comprehensive coverage (unit, integration, E2E)

**Consequences**:
- ✅ 76 tests written and passing (72 unit/integration, 4 E2E)
- ✅ Tests written before implementation (TDD followed)
- ✅ Fast feedback loop with Vitest watch mode
- ✅ E2E tests catch integration issues

**Test Coverage**:
- Unit tests: Components, state management, storage, utils
- Integration tests: Component + state + storage workflows
- E2E tests: Full user journeys (send message, persistence, loopback)

---

### ADR-005: Four-Panel Layout for Chat Interface

**Date**: 2025-12-23
**Status**: ✅ Implemented

**Context**: Chat interface needs clear visual organization.

**Decision**: Implement four-panel layout: StatusBar (top), HistorySidebar (left), ChatArea (center), InputArea (bottom).

**Rationale**:
- Standard chat application pattern (familiar UX)
- Clear visual hierarchy and information architecture
- Supports future features (P2: multiple conversations in sidebar)
- Responsive design patterns

**Consequences**:
- ✅ Familiar user experience
- ✅ Room for future features without redesign
- ✅ Clear component boundaries

---

### ADR-006: FastAPI for Backend API Framework

**Date**: 2025-12-28
**Status**: ✅ Implemented (Feature 003)

**Context**: Need a Python backend API framework for message loopback and future LLM integrations.

**Decision**: Use FastAPI 0.115.0 with Pydantic for data validation and uvicorn as the ASGI server.

**Alternatives Considered**:
1. **Flask** - Simpler, more mature, but lacks native async support and automatic API documentation
2. **Django REST Framework** - Full-featured but heavyweight for our API-only needs
3. **FastAPI** - Modern, async-native, automatic OpenAPI docs, excellent type hints

**Rationale**:
- **API-First Design** (Principle I): FastAPI auto-generates OpenAPI 3.1 docs from code
- **Performance**: Native async/await support for future streaming LLM responses
- **Type Safety**: Pydantic provides runtime validation matching our TypeScript frontend patterns
- **Developer Experience**: Automatic `/docs` endpoint, clear error messages, fast iteration
- **Testing**: Built-in TestClient integrates with pytest, openapi-core validates contracts
- **Simplicity** (Principle VI): Minimal boilerplate, clear request/response patterns

**Implementation Details**:
- **Port**: 8000 (standard Python API convention, avoids collision with frontend on 5173)
- **CORS**: Configured to allow localhost:5173 for local development
- **Middleware**: Logging middleware for request/response tracking (FR-014)
- **Validation**: Pydantic schemas match OpenAPI contract exactly
- **Error Handling**: Structured error responses (400, 422, 500) with timestamps

**Consequences**:
- ✅ Automatic interactive API documentation at `/docs`
- ✅ OpenAPI 3.1 contract generated from code (single source of truth)
- ✅ Fast development iteration with auto-reload
- ✅ Ready for async streaming when adding LLM providers
- ✅ Excellent type hints improve IDE support and reduce bugs
- ⚠️ Newer framework than Flask (less Stack Overflow answers, but excellent official docs)

**Architecture Impact**:
- Frontend communicates via HTTP POST to `/api/v1/messages`
- Backend validates requests with Pydantic, processes via service layer
- Responses follow OpenAPI contract (status, message, timestamp)
- Foundation for future endpoints: `/api/conversations`, `/api/messages/stream`

---

### ADR-007: LangChain with OpenAI ChatGPT for LLM Integration

**Date**: 2026-01-11
**Status**: ✅ Implemented (Feature 006)

**Context**: Need to integrate AI chat capabilities into SpecBot backend, replacing the loopback message pattern with actual LLM responses.

**Decision**: Use LangChain framework with langchain-openai provider for OpenAI ChatGPT integration, supporting conversation context and graceful error handling.

**Alternatives Considered**:
1. **Direct OpenAI SDK** - Lower-level, more control, but requires manual context management and message formatting
2. **Anthropic Claude** - Alternative LLM provider, but OpenAI has broader ecosystem and better documentation
3. **LangChain** - Abstraction layer that simplifies LLM integration, supports multiple providers, handles message formatting

**Rationale**:
- **Provider Abstraction**: LangChain provides consistent interface across different LLM providers (future-proofs for Anthropic, local models)
- **Conversation Context**: Built-in support for conversation history via message formatting
- **Error Handling**: Structured exception hierarchy (AuthenticationError, RateLimitError, APIConnectionError, etc.)
- **Async Support**: Native async/await with `ainvoke()` method integrates seamlessly with FastAPI
- **Test-Driven Development** (Principle III): Comprehensive test suite (51 tests) covering error scenarios and context retention
- **Simplicity** (Principle VI): Clean abstraction over raw API calls, minimal boilerplate

**Implementation Details**:
- **LLM Service Layer**: `llm_service.py` encapsulates all LLM interactions
- **Singleton Pattern**: Single ChatOpenAI instance reused across requests for performance
- **Error Mapping**: Custom exception classes map OpenAI errors to sanitized HTTP responses
  - AuthenticationError → 503 "AI service configuration error"
  - RateLimitError → 503 "AI service is busy"
  - APIConnectionError → 503 "Unable to reach AI service"
  - TimeoutError → 504 "Request timed out"
  - BadRequestError → 400 "Message could not be processed"
- **Context Retention**: Conversation history passed via `history` array in MessageRequest
- **Security**: Sanitized error messages prevent API key exposure (verified by integration tests)

**Consequences**:
- ✅ Production-ready AI chat with intelligent responses
- ✅ Conversation context maintained across multi-turn dialogues (tested to 10+ messages)
- ✅ Graceful error handling with user-friendly messages (no sensitive data exposed)
- ✅ Ready for future LLM provider additions (Anthropic Claude, local models)
- ✅ All 51 backend tests passing (100% pass rate)
- ⚠️ OpenAI API costs scale with usage (requires API key management and usage monitoring)
- ⚠️ Requires OPENAI_API_KEY environment variable for operation

**Architecture Impact**:
- New LLM service layer sits between message routes and OpenAI API
- Message flow: Frontend → API Route → LLM Service → OpenAI ChatGPT → LLM Service → API Route → Frontend
- Error responses use JSONResponse (not HTTPException) to match OpenAPI contract structure
- Conversation history stored in frontend LocalStorage, passed to backend on each request

---

### ADR-008: Model Selector with Per-Request Model Selection

**Date**: 2026-01-12
**Status**: ✅ Implemented (Feature 008)

**Context**: Users need the ability to select different OpenAI models (GPT-4, GPT-3.5-turbo) for different conversations and see which model generated each response.

**Decision**: Implement a model selection system with:
- Backend: Pydantic-based model configuration, GET /api/v1/models endpoint, per-request model parameter
- Frontend: ModelSelector dropdown component, useModels composable, model indicators on messages
- Persistence: localStorage v1.1.0 schema with selectedModelId and per-message model tracking

**Alternatives Considered**:
1. **Server-side model switching** - User account on backend with model preference. Rejected: requires authentication, not needed for MVP
2. **Hardcoded single model** - Simplest approach. Rejected: inflexible, can't test different models
3. **Per-request model selection** - Selected option: stateless backend, flexible, supports future multi-model conversations

**Rationale**:
- **Stateless Backend** (Principle II): Model passed per-request, no server-side session state
- **Configuration-Driven**: OPENAI_MODELS env var defines available models with descriptions
- **User Experience**: Clear model information (descriptions), visual indicators showing which model generated each response
- **Accessibility**: Full ARIA labels and keyboard navigation support
- **Error Handling**: Comprehensive validation, user-friendly error messages with "How to fix" guidance
- **Test Coverage**: 285 total tests (93 backend + 192 frontend), 100% pass rate

**Implementation Details**:
- **Backend Configuration** (`backend/src/config/models.py`):
  - Pydantic-based model validation (ModelConfig, ModelsConfiguration)
  - Custom ModelConfigurationError with contextual help messages
  - Support for both OPENAI_MODELS (multi-model JSON array) and OPENAI_MODEL (single model fallback)
  - Validates: non-empty models, exactly one default, unique IDs, required fields

- **Backend API** (`backend/src/api/routes/models.py`):
  - GET /api/v1/models returns list of available models with id, name, description, default
  - Caches configuration per-request (stateless, re-reads on each request)
  - Error handling: 503 Service Unavailable if configuration invalid

- **Backend LLM Integration** (`backend/src/services/llm_service.py`):
  - Optional `model` parameter in get_ai_response()
  - Validates model against configuration
  - Logs model selection events (user-selected vs default)
  - Returns tuple: (response, model_used) to track which model was actually used

- **Frontend State Management** (`frontend/src/state/useModels.js`):
  - useModels() composable manages model selection state
  - Fetches available models from backend on initialization
  - Persists selected model to localStorage
  - Validates stored model still available on load (graceful fallback to default)

- **Frontend UI** (`frontend/src/components/ModelSelector/ModelSelector.vue`):
  - Dropdown shows model name and description (e.g., "GPT-4 — Most capable model")
  - Loading state while fetching models
  - Error state with user-friendly messages
  - Accessibility: ARIA labels, keyboard navigation, screen reader support

- **Frontend Message Display** (`frontend/src/components/ChatArea/MessageBubble.vue`):
  - Model indicator on system messages showing which model generated the response
  - Subtle styling (italic, low opacity) to be non-intrusive
  - Enables users to compare model responses in same conversation

**Model Selection Flow**:
```
App Load
  │
  ├─► useModels.initializeModels()
  │   ├─► GET /api/v1/models (fetch available models)
  │   ├─► Load selectedModelId from localStorage
  │   ├─► Validate stored model still available
  │   └─► Fallback to default if invalid
  │
User Selects Model
  │
  ├─► ModelSelector.handleModelChange()
  │   ├─► useModels.setSelectedModel(modelId)
  │   └─► Save to localStorage
  │
User Sends Message
  │
  ├─► useMessages.sendMessage()
  │   ├─► Include selectedModelId in request
  │   └─► POST /api/v1/messages { message, model: "gpt-4", history }
  │
Backend Processes
  │
  ├─► messages.send_message()
  │   ├─► Load model configuration
  │   ├─► Validate requested model
  │   └─► get_ai_response(message, history, model="gpt-4")
  │
Backend Returns
  │
  ├─► MessageResponse { message, model: "gpt-4", ... }
  │
Frontend Displays
  │
  └─► MessageBubble shows response with model indicator: "gpt-4"
```

**Consequences**:
- ✅ Users can select GPT-4, GPT-3.5-turbo, or other configured models
- ✅ Each message shows which model generated it (transparent AI interaction)
- ✅ Model selection persists across page reloads
- ✅ Backend validates model requests, fallbacks to default for invalid models
- ✅ Configuration-driven: add new models via OPENAI_MODELS env var (no code changes)
- ✅ Comprehensive error handling with helpful "How to fix" messages
- ✅ Full accessibility support (ARIA labels, keyboard navigation)
- ✅ 285 tests passing (100% coverage)
- ⚠️ Model switching mid-conversation possible (can be confusing, but also powerful for A/B testing responses)

**Architecture Impact**:
- New model configuration layer in backend (`src/config/models.py`)
- New models API endpoint (`GET /api/v1/models`)
- Extended message API to accept optional `model` parameter
- LocalStorage schema upgraded to v1.1.0 with `selectedModelId` and per-message `model` fields
- LLM service now returns tuple: (response, model_used) instead of just response

**Configuration Example** (`.env`):
```bash
# Single model (simple setup)
OPENAI_MODEL=gpt-3.5-turbo

# Multi-model (enables model selector)
OPENAI_MODELS='[
  {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model", "default": true},
  {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": false}
]'
```

---

## Migration Paths

### LocalStorage → Backend Migration (Planned)

**Trigger**: When backend API is implemented (Future phase)

**Strategy**:
1. Implement backend API with same schema structure
2. Create API client to replace LocalStorage adapter
3. Add migration endpoint: `POST /api/migrate` accepts LocalStorage export
4. Frontend detects old LocalStorage data and prompts migration
5. After successful migration, archive LocalStorage data (don't delete immediately)

**Risk Mitigation**:
- Schema versioning ensures compatibility
- Migration is opt-in (user triggered)
- LocalStorage remains as fallback during transition

---

### Frontend-Only → Full-Stack Migration (Planned)

**Trigger**: When LLM integration is needed (Future phase)

**Strategy**:
1. Build backend API incrementally (conversations first, then LLM)
2. Add feature flags to enable/disable backend features
3. Support hybrid mode: LocalStorage for offline, API for online
4. Progressive enhancement approach

---

## Current Limitations & Known Issues

### Current Limitations (P1 MVP)
1. **Single Conversation**: Only one conversation supported (P2 will add multiple)
2. **Loopback Only**: No real LLM integration (Future phase)
3. **Browser-Only Data**: No cross-device sync (requires backend)
4. **No Authentication**: Public access (backend will add auth)
5. **Limited Error Handling**: Basic error states (P4 will enhance)

### Technical Debt
1. **LocalStorage Size Limit**: ~5-10MB per domain (migrate to backend when exceeded)
2. **No Offline Support**: Requires browser (PWA could be added later)
3. **No Message Search**: Linear scan of messages (backend will add search)

---

## Performance Characteristics

### Current Performance (P1 MVP)

**Bundle Size**: 75.78 KB JavaScript (29.30 KB gzipped)

**Load Time**: < 1s on modern browsers

**LocalStorage Operations**:
- Read: < 10ms (synchronous)
- Write: < 50ms (synchronous)

**Test Execution**:
- Unit/Integration: ~2-3 seconds (72 tests)
- E2E: ~10-15 seconds (4 tests)

### Performance Goals (Future)

**Backend API** (⚠️ NOT IMPLEMENTED):
- P95 latency: < 200ms for message send
- Streaming: First token < 500ms
- Throughput: 1000 concurrent users

---

## Security Considerations

### Current Security (P1 MVP)

**Client-Side Only**:
- No server = no server-side attacks
- LocalStorage is same-origin (browser sandboxed)
- No authentication required (local data)

### Planned Security (Backend) ⚠️ NOT IMPLEMENTED

**Authentication**:
- JWT tokens for API access
- OAuth2 for third-party integrations
- Secure session management (Redis)

**Data Protection**:
- HTTPS only
- Input validation at API boundaries
- SQL injection prevention (parameterized queries)
- XSS prevention (content sanitization)

**LLM API Keys**:
- Stored server-side only (never in frontend)
- Encrypted at rest
- Rotated regularly

---

## Development Workflow

### Current Workflow (P1 MVP)

1. **Local Development**: `npm run dev` (Vite dev server at localhost:5173)
2. **Testing**: `npm test` (Vitest) + `npm run test:e2e` (Playwright)
3. **Linting**: `npm run lint` (ESLint)
4. **Formatting**: `npm run format` (Prettier)
5. **Build**: `npm run build` → `frontend/dist/`

### Future Workflow (Backend) ⚠️ NOT IMPLEMENTED

1. **Backend Development**: Python FastAPI server
2. **API Testing**: pytest with contract tests
3. **Database Migrations**: Alembic (SQLAlchemy)
4. **Docker Compose**: Frontend + Backend + PostgreSQL + Redis
5. **CI/CD**: GitHub Actions (tests, linting, deployment)

---

## Questions & Decisions Needed

---

## Message Streaming Architecture (Feature 009)

**Status**: ✅ **PARTIALLY IMPLEMENTED** (Backend MVP complete, Frontend components in progress)
**Last Updated**: 2026-01-13

### Overview

Real-time message streaming allows users to see LLM responses token-by-token as they're generated, providing immediate feedback and improved perceived performance.

### Streaming Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vue.js)                        │
│                                                              │
│  User sends message                                          │
│         │                                                   │
│         ▼                                                   │
│  streamMessage(text, onToken, onComplete, onError)          │
│         │                                                   │
│         │ fetch() with Accept: text/event-stream           │
│         │                                                   │
└─────────┼──────────────────────────────────────────────────┘
          │
          │ HTTP POST /api/v1/messages
          │ Accept: text/event-stream
          │
┌─────────▼──────────────────────────────────────────────────┐
│              Backend API (FastAPI)                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Check Accept header                                 │ │
│  │     - text/event-stream → Streaming                     │ │
│  │     - application/json → Traditional                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  2. stream_ai_response() generator                    │   │
│  │     - LangChain astream() for token-by-token          │   │
│  │     - Yields TokenEvent, CompleteEvent, ErrorEvent    │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  3. StreamingResponse                                 │   │
│  │     - Format: "data: {...}\n\n" (SSE)                 │   │
│  │     - Headers: text/event-stream, no-cache            │   │
│  └──────────────────────┬───────────────────────────────┘   │
└────────────────────────┼────────────────────────────────────┘
                         │
                    SSE Stream
                         │
┌─────────────────────────▼──────────────────────────────────┐
│                Frontend ReadableStream                      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Parse SSE events (buffer for partial events)          │ │
│  │     data: {"type":"token","content":"Hello"}           │ │
│  │     data: {"type":"complete","model":"gpt-3.5-turbo"}  │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  Streaming State Management (useMessages)             │   │
│  │     - startStreaming(messageId, model)                │   │
│  │     - appendToken(content)                            │   │
│  │     - completeStreaming() → save to localStorage      │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  UI Update (MessageBubble)                            │   │
│  │     - Reactive text display                           │   │
│  │     - Streaming indicator (blinking cursor)           │   │
│  │     - Auto-scroll to latest token                     │   │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Event Types

**TokenEvent**: Streaming token content
```json
{
  "type": "token",
  "content": "Hello"
}
```

**CompleteEvent**: Stream completion with metadata
```json
{
  "type": "complete",
  "model": "gpt-3.5-turbo",
  "totalTokens": 150
}
```

**ErrorEvent**: Streaming errors
```json
{
  "type": "error",
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT"
}
```

### Implementation Status

**Backend (Completed)** ✅
- `stream_ai_response()` generator in `llm_service.py`
- SSE endpoint in `messages.py` with Accept header routing
- StreamEvent schemas (TokenEvent, CompleteEvent, ErrorEvent)
- Full test coverage (unit, contract, integration)

**Frontend API Client (Completed)** ✅
- `streamMessage()` in `apiClient.js`
- SSE parsing with buffering for partial events
- Callback-based API: onToken, onComplete, onError
- AbortController for stream cancellation

**Frontend State Management (Completed)** ✅
- Streaming state in `useMessages.js`
- `streamingMessage` ref, `isStreaming` flag
- Functions: startStreaming, appendToken, completeStreaming, abortStreaming, errorStreaming

**Frontend UI Components (Partially Complete)** 🚧
- MessageBubble: ✅ Streaming status, animated cursor indicator
- ChatArea: ⏳ Pending integration (T021)
- Auto-scroll: ⏳ Pending (T021)

**Testing**
- ✅ Backend: 9 unit tests, 10 contract tests, 9 integration tests
- ✅ Frontend API: 13 tests
- ✅ Frontend State: 11 tests
- ✅ Frontend UI: 9 tests (MessageBubble)
- ⏳ Frontend Integration: Pending (T022)
- ⏳ E2E Tests: Pending (T023)

### Architecture Decision Record: SSE vs WebSocket

**Decision**: Use Server-Sent Events (SSE) over WebSocket for LLM streaming

**Rationale**:
1. **Simplicity**: SSE is simpler - unidirectional, HTTP-based, no special handshake
2. **Browser Support**: Native EventSource API, automatic reconnection
3. **Infrastructure**: Works with standard HTTP/HTTPS, no special proxy configuration
4. **Use Case Fit**: LLM streaming is unidirectional (server → client only)
5. **Fallback**: Can gracefully degrade to traditional JSON for old clients

**Trade-offs**:
- ❌ No bidirectional communication (but not needed for streaming responses)
- ❌ EventSource doesn't support POST (workaround: use fetch + ReadableStream)
- ✅ Simpler than WebSocket for this use case
- ✅ Automatic reconnection on network issues
- ✅ Standard HTTP caching/proxying works

**Implementation Note**: Used `fetch()` with `ReadableStream` instead of `EventSource` API to support POST requests with request body.

---

### Open Questions

1. **Backend Hosting**: Where will backend be deployed? (Cloud provider TBD)
2. **Database Schema**: Should we use PostgreSQL JSONB for messages or relational tables?
3. ~~**Streaming Protocol**: Server-Sent Events (SSE) or WebSocket for LLM streaming?~~ ✅ **DECIDED: SSE** (see ADR above)
4. **Authentication**: Should we support social login (Google, GitHub) or email/password?
5. **Multi-tenancy**: Single-tenant (self-hosted) or multi-tenant (SaaS)?

### Decisions for P2 Planning

- How many conversations should be shown in sidebar? (All, recent N, paginated?)
- Should conversation list be searchable?
- What metadata should be shown in conversation previews? (title, date, message count?)

---

**Document Maintenance**: This architecture.md is updated per Constitution Principle IX whenever:
- New features are added (update Current Architecture)
- Architectural decisions are made (add ADR)
- Technology stack changes (update tables)
- Future plans change (update Planned Architecture with NOT IMPLEMENTED markers)
