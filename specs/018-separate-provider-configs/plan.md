# Implementation Plan: Separate Provider Configurations

**Branch**: `018-separate-provider-configs` | **Date**: 2026-01-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/018-separate-provider-configs/spec.md`

## Summary

Refactor the model configuration system to use separate provider-specific environment variables (`OPENAI_MODELS`, `ANTHROPIC_MODELS`) instead of the unified `MODELS` variable. Add a `DEFAULT_MODEL` env var for specifying the default model by ID. This is a clean-break change with no backward compatibility - users must migrate their configuration.

**Key Changes**:
1. Replace `MODELS` env var with `OPENAI_MODELS` and `ANTHROPIC_MODELS`
2. Add `DEFAULT_MODEL` env var (references model ID from any provider)
3. Remove `provider` and `default` fields from individual model configs (now implicit)
4. Preserve API response format (`/api/v1/models` still returns models with provider info)

## Technical Context

**Language/Version**: Python 3.13 (confirmed in devcontainer)
**Primary Dependencies**: FastAPI 0.115.0, Pydantic 2.10.0, LangChain 0.3+
**Storage**: N/A (configuration only, file-based JSON storage unchanged)
**Testing**: pytest with unit, integration, and contract tests
**Target Platform**: Linux server (Docker/devcontainer)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: N/A (configuration change, no performance impact)
**Constraints**: Clean break migration - no backward compatibility
**Scale/Scope**: 2 providers (OpenAI, Anthropic), extensible pattern

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | ✅ Pass | API contract unchanged (`/api/v1/models` returns same structure) |
| II. Modular Architecture | ✅ Pass | Changes localized to `config/models.py` |
| III. Test-First Development | ✅ Required | Tests must be written first, verify they fail |
| IV. Contract Testing | ✅ Required | Contract tests exist, must verify they pass |
| V. Observability | ✅ Pass | Existing logging preserved, error messages improved |
| VI. Simplicity & YAGNI | ✅ Pass | Simpler config format (no redundant provider/default fields) |
| VII. Versioning | ⚠️ Note | Breaking change - no deprecation period per clarification |
| VIII. Incremental Delivery | ✅ Pass | Single thin slice - one user story at a time |
| IX. Living Architecture | ✅ Pass | No architectural changes (config format only) |

**Gate Result**: PASS - All principles satisfied or explicitly addressed.

**Note**: No architectural changes required for `architecture.md` - this is a configuration format change only, not a structural change to the system.

## Project Structure

### Documentation (this feature)

```text
specs/018-separate-provider-configs/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contract unchanged)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── config/
│   │   └── models.py        # PRIMARY: Model configuration (refactor)
│   ├── api/routes/
│   │   └── models.py        # API endpoint (unchanged - response format preserved)
│   └── services/
│       └── llm_service.py   # Uses config (minimal changes)
├── tests/
│   ├── unit/
│   │   └── test_model_config.py  # PRIMARY: Config tests (rewrite)
│   ├── contract/
│   │   └── test_models_api_contract.py  # Verify unchanged
│   └── integration/
│       └── test_model_selection.py  # Update env var setup
├── .env.example             # Update documentation
└── .env.test               # Update test configuration

frontend/
└── (no changes - API response format preserved)
```

**Structure Decision**: Web application structure preserved. Changes localized to backend configuration module.

## Complexity Tracking

> No Constitution Check violations requiring justification.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Backward Compatibility | None | Per clarification - clean break migration |
| Provider Order | Alphabetical (anthropic, openai) | Deterministic fallback behavior |
| Legacy MODELS handling | Ignore silently | No error, no warning - just not used |
