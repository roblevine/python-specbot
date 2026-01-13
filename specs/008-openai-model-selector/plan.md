# Implementation Plan: OpenAI Model Selector

**Branch**: `008-openai-model-selector` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-openai-model-selector/spec.md`

## Summary

Add user-selectable OpenAI model support via a dropdown in the chat interface. Users can choose from configured models (e.g., GPT-4, GPT-3.5-turbo) before or during conversations. The backend will accept a model parameter per request, validate it against the configuration, and use the selected model for LLM invocations. Each response will indicate which model generated it.

## Technical Context

**Language/Version**: Python 3.13 (backend), JavaScript ES6+ (frontend)
**Primary Dependencies**: FastAPI 0.115.0, LangChain, langchain-openai, Vue 3.4.0, Vite 5.0.0, Pydantic 2.10.0
**Storage**: Browser LocalStorage (session persistence), Environment-based backend config
**Testing**: pytest 8.3.0 (backend), Vitest (frontend unit), Playwright (E2E), openapi-core 0.18.2 (contract testing)
**Target Platform**: Web application (Linux server backend, modern browsers frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Model selector interaction <100ms, no degradation to existing chat performance
**Constraints**: Session-based persistence only (not cross-browser-session), OpenAI models only (no other providers)
**Scale/Scope**: 2-10 configured models, single user sessions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance | Notes |
|-----------|------------|-------|
| I. API-First Design | PASS | Will define API contract changes before implementation |
| II. Modular Architecture | PASS | Model selector will be self-contained module (frontend component + backend service extension) |
| III. Test-First Development | PASS | Will write tests for model selection before implementation |
| IV. Integration & Contract Testing | PASS | Will update contract tests for new request/response fields, validate both directions |
| V. Observability & Debuggability | PASS | Will log model selection, include model in response for tracing |
| VI. Simplicity & YAGNI | PASS | Only implementing OpenAI models, session-based persistence, no cost tracking |
| VII. Versioning & Breaking Changes | PASS | API changes are backward-compatible (model field optional with default) |
| VIII. Incremental Delivery | PASS | Will implement in thin slices: P1 (basic selection) → P2 (model info) → P3 (mid-conversation) |
| IX. Living Architecture | PASS | Will update architecture.md with model selection flow |

**Architecture Update Required**: Yes - will add model configuration and selection flow to architecture.md

## Project Structure

### Documentation (this feature)

```text
specs/008-openai-model-selector/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI updates)
│   └── openapi-patch.yaml
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── main.py                           # FastAPI app (no changes expected)
├── src/
│   ├── api/routes/messages.py        # UPDATE: Accept model parameter
│   ├── services/
│   │   ├── llm_service.py            # UPDATE: Support model selection, load model config
│   │   └── message_service.py        # No changes expected
│   ├── schemas.py                    # UPDATE: Add model to request/response
│   └── config/
│       └── models.py                 # NEW: Model configuration schema
└── tests/
    ├── unit/
    │   └── test_llm_service.py       # UPDATE: Test model selection
    ├── integration/
    │   └── test_model_selection.py   # NEW: Test model selection flow
    └── contract/
        └── test_message_api_contract.py  # UPDATE: Contract with model field

frontend/
├── src/
│   ├── components/
│   │   ├── App/App.vue               # UPDATE: Include ModelSelector
│   │   ├── ModelSelector/            # NEW: Model dropdown component
│   │   │   ├── ModelSelector.vue
│   │   │   └── ModelSelector.test.js
│   │   └── MessageBubble/MessageBubble.vue  # UPDATE: Show model indicator
│   ├── state/
│   │   ├── useAppState.js            # UPDATE: Add selectedModel state
│   │   └── useModels.js              # NEW: Model selection composable
│   ├── services/
│   │   └── apiClient.js              # UPDATE: Pass model in requests
│   └── storage/
│       └── StorageSchema.js          # UPDATE: Add selectedModel to schema
└── tests/
    ├── unit/
    │   └── components/
    │       └── ModelSelector.test.js # NEW: Component tests
    ├── integration/
    │   └── model-selection.test.js   # NEW: Integration tests
    └── contract/
        └── sendMessage.contract.test.js  # UPDATE: Contract with model
```

**Structure Decision**: Web application structure (frontend + backend) - extending existing architecture from feature 006.

## Complexity Tracking

No violations identified. Feature uses existing patterns and technologies with minimal additions:
- One new component (ModelSelector)
- One new composable (useModels)
- Extensions to existing services and schemas
- No new external dependencies required
