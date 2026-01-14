# SpecBot - Spec-First Chatbot

SpecBot is a fully featured chat-bot, built spec-first using Spec-kit, in Python and Vue. It interfaces to multiple LLM providers, including local providers, and can be easily extended to support more. It features a web-based chat interface, with support for conversation history, message editing, and more.

## Getting Started

### Prerequisites

- **Frontend**: Node.js v18+, npm v8+
- **Backend**: Python 3.13+, pip

### Installation

**Frontend:**
```bash
cd frontend
npm install
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

### Development

**Option 1: Run Both Servers** (Recommended)

Terminal 1 - Backend API:
```bash
cd backend
python main.py
```
Backend starts at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```
Frontend starts at `http://localhost:5173`

**Option 2: Frontend Only** (Limited - no backend integration)

```bash
cd frontend
npm run dev
```
The application will be available at `http://localhost:5173` but API calls will fail.

### Testing

**Quick Test Scripts** (Recommended)

Run tests from the project root using convenience scripts:

```bash
# Run all tests (backend + frontend, including contract tests)
./scripts/test-all.sh

# Run with coverage reports
./scripts/test-all.sh --coverage

# Run only backend tests
./scripts/test-all.sh --backend-only

# Run only frontend tests
./scripts/test-all.sh --frontend-only

# Or run individually
./scripts/test-backend.sh     # Backend tests only
./scripts/test-frontend.sh    # Frontend tests only
```

**Frontend Tests (Manual):**

```bash
cd frontend

# Run all unit & integration tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm test -- --coverage

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui
```

**Backend Tests (Manual):**

```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m contract      # Contract tests only

# Run with verbose output
pytest tests/ -v
```

### Code Quality

#### Lint Code

```bash
cd frontend
npm run lint
```

#### Format Code

```bash
cd frontend
npm run format
```

### Production Build

Build optimized production bundle:

```bash
cd frontend
npm run build
```

Build output will be in `frontend/dist/`

Preview production build:

```bash
cd frontend
npm run preview
```

## Project Structure

```
python-specbot/
├── frontend/                  # Vue.js frontend application
│   ├── src/
│   │   ├── components/       # Vue components (App, ChatArea, InputArea, etc.)
│   │   ├── state/           # State management composables
│   │   ├── services/        # API client for backend communication
│   │   ├── storage/         # LocalStorage adapter & schema
│   │   └── utils/           # Utility functions (validation, logging, etc.)
│   ├── tests/
│   │   ├── unit/            # Unit tests (Vitest)
│   │   ├── integration/     # Integration tests
│   │   ├── contract/        # Contract snapshot tests
│   │   └── e2e/             # End-to-end tests (Playwright)
│   ├── public/              # Static assets
│   └── package.json
├── backend/                   # Python FastAPI backend server
│   ├── src/
│   │   ├── api/routes/      # API endpoint handlers
│   │   ├── services/        # Business logic (message processing, LLM streaming)
│   │   ├── middleware/      # CORS, logging middleware
│   │   ├── utils/           # Logging, validation utilities
│   │   └── schemas.py       # Pydantic data models
│   ├── tests/
│   │   ├── contract/        # OpenAPI schema validation tests
│   │   ├── integration/     # Full request-response tests
│   │   └── unit/            # Service and utility tests
│   ├── main.py              # FastAPI application entry point
│   ├── requirements.txt     # Python dependencies
│   └── pytest.ini           # Test configuration
├── scripts/                   # Test and utility scripts
│   ├── test-all.sh          # Run all tests (backend + frontend + contract)
│   ├── test-backend.sh      # Run backend tests only
│   └── test-frontend.sh     # Run frontend tests only
├── specs/                    # Feature specifications
│   ├── 001-chat-interface/  # Chat interface spec & design docs
│   │   ├── spec.md          # Feature specification
│   │   ├── plan.md          # Implementation plan
│   │   ├── tasks.md         # Task breakdown
│   │   └── ...
│   └── 009-message-streaming/  # Streaming feature spec & design docs
│       ├── spec.md          # Feature specification
│       ├── plan.md          # Implementation plan
│       ├── tasks.md         # Task breakdown (46 tasks)
│       ├── data-model.md    # Data schemas (StreamEvent, StreamingMessage)
│       ├── contracts/       # OpenAPI 3.1 specification for SSE
│       └── ...
├── architecture.md           # Living architecture documentation
└── README.md                # This file
```

## Architecture

SpecBot uses a **full-stack modular architecture**:

**Frontend (Vue.js):**
- **Components**: Vue Single File Components organized by feature
- **State Management**: Vue Composition API with composables (no Vuex/Pinia needed)
- **API Client**: Fetch-based client with error handling and timeout support
- **Storage Layer**: Abstracted LocalStorage with versioned schema (v1.0.0)
- **Utilities**: Shared validation, logging, and ID generation functions

**Backend (FastAPI):**
- **API Routes**: RESTful endpoints with automatic OpenAPI documentation
- **Service Layer**: Business logic (message processing, validation)
- **Middleware**: CORS, request/response logging, error handling
- **Data Validation**: Pydantic schemas for type-safe request/response

**Communication:**
- Frontend → Backend: HTTP POST to `/api/v1/messages`
- Backend → Frontend: JSON responses with structured error handling
- Timeout: 10 seconds on frontend requests
- CORS: Configured for localhost development

See `architecture.md` for detailed diagrams, data flow, and ADRs.

## Development Workflow

1. **Specification First**: All features start with a detailed specification in `specs/`
2. **Test-Driven Development**: Tests written before implementation (TDD)
3. **Incremental Delivery**: Features delivered as thin vertical slices (P1, P2, P3...)
4. **Code Quality**: ESLint and Prettier enforce consistent code style

## Roadmap

### ✅ P1 - Send and View Message Loopback (Complete)
- Basic chat interface with loopback functionality
- Message persistence in LocalStorage
- Single conversation support

### 🔜 P2 - Navigate Conversation History (Planned)
- Switch between multiple conversations
- Conversation list with previews
- Most recent conversation selection

### 🔜 P3 - Start New Conversation (Planned)
- Create new conversations
- Empty conversation handling
- Conversation organization

### 🔜 P4 - System Status & Error Handling (Planned)
- Enhanced status bar
- Error recovery mechanisms
- Connection status indicators

### 🔜 Future - LLM Integration
- Multiple LLM provider support
- Real chat functionality (replacing loopback)
- Streaming responses

## Contributing

This project follows the Spec-kit methodology with strict adherence to:
- API-First Design
- Modular Architecture
- Test-First Development
- Incremental Delivery & Thin Slices

See `/specs/001-chat-interface/` for detailed design documentation.

## License

[License TBD]
