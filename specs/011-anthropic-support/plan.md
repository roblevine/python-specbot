# Implementation Plan: Anthropic Claude Model Support

**Branch**: `011-anthropic-support` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-anthropic-support/spec.md`

## Summary

Add Anthropic Claude model support as the first step in a multi-provider architecture. This extends the existing LangChain-based LLM service to support both OpenAI and Anthropic providers, allowing users to select Claude models alongside existing GPT models. The design uses LangChain's provider abstraction (`ChatAnthropic`) to enable future expansion to Ollama and OpenRouter.

## Technical Context

**Language/Version**: Python 3.13 (backend), JavaScript ES6+ (frontend)
**Primary Dependencies**: FastAPI 0.115.0, LangChain, langchain-openai, langchain-anthropic, Vue 3.4.0, Vite 5.0.0
**Storage**: File-based JSON storage (existing), Browser LocalStorage (frontend)
**Testing**: pytest (backend), Vitest (frontend), contract tests
**Target Platform**: Linux server (backend), Modern browsers (frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Response streaming at parity with OpenAI, model selection < 5 seconds
**Constraints**: Model locked after conversation starts (no mid-conversation switching)
**Scale/Scope**: 2+ Anthropic models, flexible multi-provider architecture

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | ✅ PASS | Extending existing `/api/v1/models` and `/api/v1/messages` contracts |
| II. Modular Architecture | ✅ PASS | Provider abstraction as separate module, clean boundaries |
| III. Test-First Development | ✅ PASS | Tests written before implementation per existing patterns |
| IV. Integration & Contract Testing | ✅ PASS | Contract tests required for model endpoint changes |
| V. Observability & Debuggability | ✅ PASS | Logging patterns already established in llm_service.py |
| VI. Simplicity & YAGNI | ✅ PASS | Minimal changes - extend existing patterns, no over-engineering |
| VII. Versioning & Breaking Changes | ✅ PASS | Backward compatible - adds provider field to model config |
| VIII. Incremental Delivery | ✅ PASS | P1 (basic Claude support) → P2 (provider organization) → P3 (config flexibility) |
| IX. Living Architecture Documentation | ⚠️ UPDATE | architecture.md needs provider abstraction documentation |

**Architecture Documentation Update Required**:
- Add provider abstraction layer to Current Architecture section
- Document multi-provider routing flow
- Update Technology Stack with langchain-anthropic dependency

## Project Structure

### Documentation (this feature)

```text
specs/011-anthropic-support/
├── plan.md              # This file
├── research.md          # Phase 0: LangChain multi-provider patterns
├── data-model.md        # Phase 1: Extended model/provider entities
├── quickstart.md        # Phase 1: Setup guide for Anthropic
├── contracts/           # Phase 1: Updated API contracts
│   ├── models-response.json
│   └── messages-request.json
└── tasks.md             # Phase 2: Implementation tasks
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── config/
│   │   └── models.py        # MODIFY: Add provider field, load ANTHROPIC_MODELS
│   ├── services/
│   │   └── llm_service.py   # MODIFY: Add ChatAnthropic support, provider routing
│   └── api/
│       └── routes/
│           └── models.py    # MODIFY: Return provider info with models
└── tests/
    ├── contract/            # ADD: Contract tests for provider responses
    ├── integration/         # ADD: Multi-provider integration tests
    └── unit/                # ADD: Provider routing unit tests

frontend/
├── src/
│   ├── components/
│   │   └── ModelSelector/
│   │       └── ModelSelector.vue  # MODIFY: Display provider labels
│   ├── services/
│   │   └── apiClient.js           # No changes needed (generic)
│   └── state/
│       └── useModels.js           # MODIFY: Handle provider field
└── tests/
    └── unit/                      # ADD: Provider display tests
```

**Structure Decision**: Web application structure (frontend + backend) - extending existing layout with provider abstraction in backend services.

## Complexity Tracking

> No violations requiring justification. Implementation follows existing patterns.
