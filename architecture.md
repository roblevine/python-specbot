# SpecBot Architecture

**Last Updated**: 2025-12-28
**Current Version**: P1 + Backend API (Feature 003 Complete)

This document describes the current implemented architecture and planned future architecture for SpecBot.

---

## Current Architecture

### Overview

SpecBot is a **full-stack chat application** with a Vue.js frontend and Python FastAPI backend. The backend provides a message loopback API that echoes messages with "api says: " prefix, establishing the foundation for future LLM integrations.

**Status**: ✅ **IMPLEMENTED** (Frontend P1 + Backend API 003 Complete)

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
│  │    - Schema Version: v1.0.0                             │ │
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
│  │         POST /api/v1/messages (loopback)                │ │
│  │         GET /health (health check)                      │ │
│  └──────────────────────┬─────────────────────────────────┘ │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │              Message Service Layer                    │   │
│  │   - create_loopback_message(text)                     │   │
│  │   - validate_message(text)                            │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │               Middleware Layer                        │   │
│  │   - CORS (allows localhost:5173)                      │   │
│  │   - Logging (request/response)                        │   │
│  │   - Error handling                                    │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
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
│   │       └── messages.py  # POST /api/v1/messages endpoint
│   │
│   ├── services/
│   │   └── message_service.py  # Business logic (loopback, validation)
│   │
│   ├── middleware/
│   │   └── logging_middleware.py  # Request/response logging
│   │
│   ├── utils/
│   │   └── logger.py        # Structured logging setup
│   │
│   └── schemas.py           # Pydantic models (MessageRequest, MessageResponse)
│
├── tests/
│   ├── contract/            # OpenAPI schema validation tests
│   ├── integration/         # Full request-response cycle tests
│   └── unit/                # Service and utility tests
│
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
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
| **Backend Testing** | pytest + httpx + openapi-core | 8.3.0 | ✅ In Use |
| **API Documentation** | OpenAPI 3.1 (auto-generated) | 3.1.0 | ✅ In Use |
| **Code Quality** | ESLint + Prettier (frontend) | Latest | ✅ In Use |
| **Package Manager** | npm (frontend), pip (backend) | 8+ / Latest | ✅ In Use |

### Data Flow (Current Implementation)

**Frontend → Backend → Frontend** (Feature 003)

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
    ├─► create_loopback_message() - Add "api says: " prefix
    │
    ▼
MessageResponse (Pydantic schema)
    │
    ├─► status: "success"
    ├─► message: "api says: {user_message}"
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
ChatArea Component (Displays Messages with "api says: " prefix)
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

**LocalStorage Schema v1.0.0** (`frontend/src/storage/schema.js`)

```javascript
{
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
          timestamp: "ISO-8601 timestamp"
        }
      ]
    }
  ],
  schemaVersion: "1.0.0"
}
```

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

### Open Questions

1. **Backend Hosting**: Where will backend be deployed? (Cloud provider TBD)
2. **Database Schema**: Should we use PostgreSQL JSONB for messages or relational tables?
3. **Streaming Protocol**: Server-Sent Events (SSE) or WebSocket for LLM streaming?
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
