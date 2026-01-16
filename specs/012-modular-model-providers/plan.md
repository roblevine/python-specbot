# Implementation Plan: Modular Model Providers

**Branch**: `012-modular-model-providers` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-modular-model-providers/spec.md`

## Summary

Consolidate and modularize the existing OpenAI and Anthropic provider implementations into a unified, extensible provider architecture. This refactoring eliminates ~150-200 lines of duplicated code (especially in exception handling), creates a provider registry pattern for easy addition of new providers, and maintains full backward compatibility with existing API contracts.

**Technical Approach**: Introduce a provider abstraction layer that encapsulates provider-specific initialization, error mapping, and configuration. Each provider becomes a self-contained module that implements a common interface, allowing the core LLM service to remain provider-agnostic.

## Configuration Consolidation

**Current State (to be replaced)**:
```bash
# Separate env vars per provider
OPENAI_MODELS='[{"id":"gpt-4",...}]'
ANTHROPIC_MODELS='[{"id":"claude-3-5-sonnet-20241022",...}]'
```

**Target State**:
```bash
# Single unified MODELS env var
MODELS='[
  {"id":"gpt-4","name":"GPT-4","description":"...","provider":"openai","default":false},
  {"id":"gpt-3.5-turbo","name":"GPT-3.5 Turbo","description":"...","provider":"openai","default":true},
  {"id":"claude-3-5-sonnet-20241022","name":"Claude 3.5 Sonnet","description":"...","provider":"anthropic","default":false}
]'

# API keys remain separate (as they should)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Filtering Logic**: When loading the configuration:
1. Parse all models from the unified `MODELS` variable
2. Check which provider API keys are configured (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`)
3. Filter out models whose provider API key is not set
4. Return only models that can actually be used

**Backward Compatibility**: If the new `MODELS` variable is not set, fall back to loading from the legacy `OPENAI_MODELS` and `ANTHROPIC_MODELS` variables.

## Technical Context

**Language/Version**: Python 3.13 (backend), JavaScript ES6+ (frontend)
**Primary Dependencies**: FastAPI 0.115.0, Pydantic 2.10.0, LangChain 0.3+, langchain-openai 0.2+, langchain-anthropic 0.2+, Vue 3.4.0, Vite 5.0.0
**Storage**: File-based JSON storage (unchanged by this feature)
**Testing**: pytest 8.3.0 (backend), vitest (frontend), openapi-core 0.18.2 (contract tests)
**Target Platform**: Linux server (backend), modern browsers (frontend)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: N/A - refactoring only, no performance regression expected
**Constraints**: Must preserve existing API contracts (`/api/v1/models`, `/api/v1/messages`)
**Scale/Scope**: 2 existing providers (OpenAI, Anthropic), designed for easy addition of more

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | ✅ PASS | No new API endpoints; existing contracts preserved (FR-006) |
| II. Modular Architecture | ✅ PASS | This feature explicitly improves modularity |
| III. Test-First Development | ✅ REQUIRED | Tests must be written first for provider interface |
| IV. Contract Testing | ✅ PASS | Existing contract tests verify backward compatibility |
| V. Observability | ✅ REQUIRED | FR-008 requires consistent logging format |
| VI. Simplicity & YAGNI | ⚠️ MONITOR | Provider abstraction adds indirection; justified by 40%+ code reduction (SC-002) |
| VII. Versioning | ✅ PASS | Internal refactoring, no public API version bump needed |
| VIII. Incremental Delivery | ✅ REQUIRED | Implement in thin slices: P1 config → P2 errors/factory → P3 tests |
| IX. Architecture Documentation | ✅ REQUIRED | Update architecture.md with new provider module structure |

**Architecture Documentation Update Required**: Yes - this feature changes the internal module structure. Update `architecture.md` with:
- New `services/providers/` module structure in Current Architecture
- Provider registry pattern and error mapping in Module Boundaries
- Decision record for provider abstraction pattern

## Project Structure

### Documentation (this feature)

```text
specs/012-modular-model-providers/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (existing contracts - no changes)
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── routes/
│   │       ├── models.py        # GET /api/v1/models (unchanged contract)
│   │       └── messages.py      # POST /api/v1/messages (unchanged contract)
│   ├── config/
│   │   └── models.py            # MODIFY: Consolidated provider registry
│   ├── services/
│   │   ├── llm_service.py       # MODIFY: Use provider abstraction
│   │   └── providers/           # NEW: Provider modules
│   │       ├── __init__.py      # Provider registry and base interface
│   │       ├── base.py          # Abstract provider interface
│   │       ├── openai.py        # OpenAI provider implementation
│   │       ├── anthropic.py     # Anthropic provider implementation
│   │       └── errors.py        # Unified error mapping
│   └── schemas.py               # UNCHANGED
└── tests/
    ├── contract/                # Existing contract tests (verify backward compat)
    ├── integration/
    │   └── test_model_selection.py  # MODIFY: Test new provider pattern
    └── unit/
        ├── test_llm_service.py      # MODIFY: Test provider abstraction
        ├── test_model_config.py     # MODIFY: Test consolidated config
        └── providers/               # NEW: Provider-specific tests
            ├── test_base.py         # Test provider interface
            ├── test_openai.py       # Test OpenAI provider
            ├── test_anthropic.py    # Test Anthropic provider
            └── test_errors.py       # Test error mapping

frontend/
├── src/
│   ├── services/
│   │   └── apiClient.js         # UNCHANGED (no frontend changes)
│   └── state/
│       └── useModels.js         # UNCHANGED (no frontend changes)
└── tests/                       # UNCHANGED (no frontend changes)
```

**Structure Decision**: Web application structure with backend changes only. Frontend remains unchanged as API contracts are preserved. New `providers/` module follows existing `services/` pattern for consistency.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Provider abstraction layer | Enables adding providers without modifying existing code (SC-001) | Direct provider handling requires if/elif chains that grow with each provider |
| Separate error mapping module | Consolidates ~90 lines of duplicate exception handling (SC-002) | Inline handling duplicates code between streaming/non-streaming methods |
