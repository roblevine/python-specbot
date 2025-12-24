# SpecBot - Spec-First Chatbot

SpecBot is a fully featured chat-bot, built spec-first using Spec-kit, in Python and Vue. It interfaces to multiple LLM providers, including local providers, and can be easily extended to support more. It features a web-based chat interface, with support for conversation history, message editing, and more.

## Current Implementation Status

### ✅ P1 MVP - Chat Interface with Message Loopback (Complete)

**Feature:** 001-chat-interface (Branch: `001-chat-interface`)

The initial MVP implementation provides a complete chat interface with message loopback functionality:

- **Message Sending & Display**: Users can type messages and see them displayed in the chat area
- **Loopback Functionality**: System echoes back user messages immediately (loopback response)
- **Conversation Persistence**: Messages are saved to browser LocalStorage and persist across page refreshes
- **Four-Panel Layout**:
  - Status bar (top) - Shows application state (Ready/Processing/Error)
  - History sidebar (left) - Displays conversation list
  - Chat area (center) - Shows messages with user/system distinction
  - Input area (bottom) - Text input with Send button

**Technologies:**
- **Frontend**: Vue.js 3 (Composition API)
- **Build Tool**: Vite 5
- **Testing**: Vitest (unit/integration), Playwright (E2E)
- **Storage**: Browser LocalStorage API
- **Code Quality**: ESLint, Prettier

**Test Coverage:**
- 72 unit & integration tests ✅
- 4 E2E tests (Playwright) ✅
- Total: 76 tests passing

**Production Bundle:** 75.78 KB JavaScript (29.30 KB gzipped)

## Getting Started

### Prerequisites

- Node.js v18 or higher
- npm v8 or higher

### Installation

```bash
cd frontend
npm install
```

### Development

Start the development server with hot module replacement:

```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:5173`

### Testing

#### Run All Unit & Integration Tests

```bash
cd frontend
npm test
```

#### Run Tests in Watch Mode

```bash
cd frontend
npm run test:watch
```

#### Run End-to-End Tests

```bash
cd frontend
npm run test:e2e
```

#### Run E2E Tests with UI

```bash
cd frontend
npm run test:e2e:ui
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
│   │   ├── storage/         # LocalStorage adapter & schema
│   │   └── utils/           # Utility functions (validation, logging, etc.)
│   ├── tests/
│   │   ├── unit/            # Unit tests (Vitest)
│   │   ├── integration/     # Integration tests
│   │   └── e2e/             # End-to-end tests (Playwright)
│   ├── public/              # Static assets
│   └── package.json
├── specs/                    # Feature specifications
│   └── 001-chat-interface/  # Chat interface spec & design docs
│       ├── spec.md          # Feature specification
│       ├── plan.md          # Implementation plan
│       ├── tasks.md         # Task breakdown (76 tasks completed)
│       ├── data-model.md    # Data schemas
│       ├── research.md      # Technical decisions
│       └── contracts/       # Component & storage interfaces
└── README.md                # This file
```

## Architecture

The frontend follows a modular architecture:

- **Components**: Vue Single File Components organized by feature
- **State Management**: Vue Composition API with composables (no Vuex/Pinia needed)
- **Storage Layer**: Abstracted LocalStorage with versioned schema (v1.0.0)
- **Utilities**: Shared validation, logging, and ID generation functions

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
