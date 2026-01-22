# Implementation Plan: Add Ollama Model Support

**Branch**: `020-add-ollama-support` | **Date**: 2026-01-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/020-add-ollama-support/spec.md`

## Summary

Add local Ollama model support through the existing LangChain provider infrastructure. This enables users to select and use models running on their local Ollama server alongside cloud providers (OpenAI, Anthropic). Implementation follows the established provider pattern with a new `OllamaProvider` class, configuration via `OLLAMA_MODELS` environment variable, and proper error handling for connection failures.

## Technical Context

**Language/Version**: Python 3.13 (confirmed in devcontainer)
**Primary Dependencies**: FastAPI 0.115.0, LangChain 0.3+, langchain-ollama (new dependency), Pydantic 2.10.0
**Storage**: N/A (stateless provider, uses existing model configuration infrastructure)
**Testing**: pytest with existing test patterns
**Target Platform**: Linux server (devcontainer), cross-platform Ollama support
**Project Type**: Web application (backend API + Vue frontend)
**Performance Goals**: Match existing provider timeout (120 seconds), streaming support
**Constraints**: Follow existing provider architecture patterns for consistency
**Scale/Scope**: Single Ollama server instance per deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | ✅ PASS | No new API endpoints; uses existing `/api/v1/models` |
| II. Modular Architecture | ✅ PASS | Self-contained `OllamaProvider` module following existing pattern |
| III. Test-First Development | ✅ PASS | Unit tests for provider, error mapping, config loading |
| IV. Contract Testing | ✅ PASS | No contract changes; existing API response format preserved |
| V. Observability | ✅ PASS | Structured logging for provider initialization, errors |
| VI. Simplicity/YAGNI | ✅ PASS | Follows existing patterns exactly; minimal new code |
| VII. Versioning | ✅ PASS | No breaking changes; additive feature |
| VIII. Incremental Delivery | ✅ PASS | Three thin slices: P1 (core), P2 (errors), P3 (custom URL) |
| IX. Living Documentation | ✅ PASS | Will update architecture.md with new provider |

**Architecture Documentation**: This feature adds a new provider module. Update `architecture.md` to include:
- Ollama provider in the provider registry diagram
- langchain-ollama dependency in technology stack
- Configuration pattern (OLLAMA_MODELS, OLLAMA_BASE_URL)

## Project Structure

### Documentation (this feature)

```text
specs/020-add-ollama-support/
├── plan.md              # This file
├── research.md          # Phase 0: LangChain-Ollama research
├── data-model.md        # Phase 1: Provider config changes
├── quickstart.md        # Phase 1: Setup instructions
├── contracts/           # Phase 1: No new contracts (existing API)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── config/
│   │   └── models.py           # Add OLLAMA_MODELS, OLLAMA_BASE_URL support
│   └── services/
│       └── providers/
│           ├── __init__.py     # Register OllamaProvider
│           ├── ollama.py       # NEW: OllamaProvider implementation
│           ├── errors.py       # Add map_ollama_error function
│           └── base.py         # Modify ProviderConfig (optional api_key_env)
└── tests/
    └── unit/
        ├── test_ollama_provider.py  # NEW: Provider unit tests
        └── test_model_config.py     # Add Ollama config tests

backend/.env.example                 # Add Ollama configuration examples
```

**Structure Decision**: Web application structure (Option 2). Backend-only changes - frontend automatically displays Ollama models via existing model selector infrastructure.

## Complexity Tracking

No constitution violations. All principles pass.
