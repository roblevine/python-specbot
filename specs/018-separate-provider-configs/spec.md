# Feature Specification: Separate Provider Configurations

**Feature Branch**: `018-separate-provider-configs`
**Created**: 2026-01-20
**Status**: Draft
**Input**: User description: "Separate model provider configurations - break out OpenAI and Anthropic into separate collections with a single default model key"

## Background

This feature reverses part of the 012-modular-model-providers implementation, which consolidated all models into a single `MODELS` environment variable. User feedback indicates that separate provider configurations are preferable for managing models on a per-provider basis.

**Current State (012)**: Single `MODELS` env var containing a JSON array where each model has `id`, `name`, `description`, `provider`, and `default` fields.

**Desired State (018)**: Separate environment variables per provider (`OPENAI_MODELS`, `ANTHROPIC_MODELS`) plus a single `DEFAULT_MODEL` key that references a model ID from any provider collection.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Separate Provider Model Collections (Priority: P1)

As a developer configuring the application, I want to define models for each provider in separate environment variables, so that I can manage provider-specific model lists independently and see at a glance which models belong to which provider.

**Why this priority**: This is the core change requested. Separate provider configurations make it easier to add/remove models for a specific provider without parsing through a combined list, and prepares the architecture for future provider-specific configuration options.

**Configuration Format**: Each provider has its own environment variable (`OPENAI_MODELS`, `ANTHROPIC_MODELS`) containing a JSON array of model objects. Model objects no longer include a `provider` field (it's implicit from the variable name) or a `default` field.

**Example**:
```
OPENAI_MODELS='[
  {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model for complex reasoning"},
  {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient for most tasks"}
]'

ANTHROPIC_MODELS='[
  {"id": "claude-sonnet-4-5-20250929", "name": "Claude 4.5 Sonnet", "description": "Most capable Claude model for complex tasks"},
  {"id": "claude-haiku-4-5-20251001", "name": "Claude 4.5 Haiku", "description": "Fast and efficient for simple tasks"}
]'

DEFAULT_MODEL=gpt-3.5-turbo
```

**Independent Test**: Can be fully tested by configuring separate `OPENAI_MODELS` and `ANTHROPIC_MODELS` variables and verifying all models load correctly with their implicit provider association.

**Acceptance Scenarios**:

1. **Given** `OPENAI_MODELS` and `ANTHROPIC_MODELS` are configured with valid model lists, **When** the application starts, **Then** all models from both providers are loaded and available, with provider association inferred from the source variable.

2. **Given** only `OPENAI_MODELS` is configured (and OPENAI_API_KEY is set), **When** the application starts, **Then** only OpenAI models are available and the system operates normally.

3. **Given** only `ANTHROPIC_MODELS` is configured (and ANTHROPIC_API_KEY is set), **When** the application starts, **Then** only Anthropic models are available and the system operates normally.

4. **Given** a provider's models are configured but its API key is not set, **When** the application loads, **Then** that provider's models are excluded from the available models list while the other provider's models remain available.

5. **Given** the legacy unified `MODELS` variable is set alongside new provider-specific variables, **When** the application starts, **Then** the provider-specific variables take precedence and the legacy `MODELS` variable is ignored.

---

### User Story 2 - Single Default Model Reference (Priority: P1)

As a developer, I want to specify the default model using a single `DEFAULT_MODEL` environment variable that references a model ID, so that the default selection is clearly separated from model definitions and can be changed without editing model configurations.

**Why this priority**: This is the other core change requested. Separating the default selection from model definitions means the default can be changed independently and eliminates the need for a `default` boolean field in each model configuration.

**Independent Test**: Can be fully tested by setting `DEFAULT_MODEL` to various model IDs and verifying the correct model is used as the default.

**Acceptance Scenarios**:

1. **Given** `DEFAULT_MODEL` is set to a valid model ID that exists in one of the provider configurations, **When** the application loads, **Then** that model is used as the default for new conversations.

2. **Given** `DEFAULT_MODEL` is set to an OpenAI model ID, **When** the user opens the application without selecting a model, **Then** the OpenAI model is pre-selected.

3. **Given** `DEFAULT_MODEL` is set to an Anthropic model ID, **When** the user opens the application without selecting a model, **Then** the Anthropic model is pre-selected.

4. **Given** `DEFAULT_MODEL` is not set, **When** the application loads, **Then** the first model from the first available provider is used as the default.

5. **Given** `DEFAULT_MODEL` references a model whose provider API key is not configured, **When** the application loads, **Then** the system falls back to the first available model from an enabled provider and logs a warning.

6. **Given** `DEFAULT_MODEL` references a model ID that does not exist in any provider configuration, **When** the application loads, **Then** a clear error message indicates the invalid default model reference.

---

### User Story 3 - Backward Compatibility Migration (Priority: P2)

As a developer with an existing deployment, I want the system to support the legacy `MODELS` configuration during a transition period, so that I can migrate to the new format without immediate downtime.

**Why this priority**: Existing deployments should not break immediately. This provides a graceful migration path.

**Independent Test**: Can be fully tested by configuring only the legacy `MODELS` variable and verifying the system still works, with deprecation warnings logged.

**Acceptance Scenarios**:

1. **Given** only the legacy `MODELS` variable is configured (no provider-specific variables), **When** the application starts, **Then** the system loads models from `MODELS` with a deprecation warning logged.

2. **Given** the legacy `MODELS` variable is configured, **When** loading models, **Then** a warning message indicates the recommended migration to provider-specific variables.

3. **Given** both legacy `MODELS` and provider-specific variables are configured, **When** the application starts, **Then** provider-specific variables take precedence and a warning is logged about the ignored legacy variable.

---

### Edge Cases

- **Duplicate model IDs across providers**: When the same model ID appears in both `OPENAI_MODELS` and `ANTHROPIC_MODELS`, the system rejects the configuration with a clear error message indicating which IDs are duplicated.

- **Empty provider configuration**: When a provider's models variable is set to an empty array `[]`, that provider has no models available but the configuration is still valid (other providers may have models).

- **DEFAULT_MODEL provider disabled**: When the default model belongs to a provider whose API key is not set, the system selects the first available model from an enabled provider as the fallback default.

- **All providers disabled**: When no provider API keys are configured, the system fails with a clear error indicating that at least one provider must be enabled.

- **Invalid JSON in provider config**: When a provider's models variable contains invalid JSON, a clear error message identifies which provider configuration has the issue.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support separate environment variables for each provider's model list (`OPENAI_MODELS`, `ANTHROPIC_MODELS`).

- **FR-002**: System MUST infer the provider from the configuration source (e.g., models in `OPENAI_MODELS` are OpenAI models).

- **FR-003**: System MUST support a `DEFAULT_MODEL` environment variable that specifies the default model by ID.

- **FR-004**: System MUST NOT require a `default` field in individual model configurations.

- **FR-005**: System MUST NOT require a `provider` field in individual model configurations (provider is implicit).

- **FR-006**: System MUST validate that no duplicate model IDs exist across all provider configurations.

- **FR-007**: System MUST fall back to the first available model when `DEFAULT_MODEL` is not set or references an unavailable model.

- **FR-008**: System MUST support the legacy `MODELS` variable for backward compatibility with deprecation warnings.

- **FR-009**: System MUST prioritize provider-specific variables over the legacy `MODELS` variable when both are present.

- **FR-010**: System MUST preserve all existing API contracts and response formats (the `/api/v1/models` endpoint continues to return models with provider information).

- **FR-011**: System MUST log clear error messages identifying which provider configuration has issues when validation fails.

### Key Entities

- **ProviderModelsConfig**: Represents the model list for a single provider. Contains: list of models (each with id, name, description). Provider identity is implicit from the configuration source.

- **ModelConfig**: Simplified model configuration without provider or default fields. Contains: id, name, description.

- **SystemModelsConfig**: Aggregated view of all provider configurations plus the default model reference. Used internally after loading and merging all provider configurations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can add or modify models for a specific provider by editing only that provider's configuration variable.

- **SC-002**: Changing the default model requires modifying only the `DEFAULT_MODEL` variable, not any model definitions.

- **SC-003**: Existing deployments using the legacy `MODELS` format continue to work without immediate changes.

- **SC-004**: All existing frontend and backend tests pass without modification to test assertions.

- **SC-005**: The `/api/v1/models` endpoint returns identical response structure as before (models include provider information for frontend display).

- **SC-006**: Configuration errors clearly identify which provider's configuration has the issue.

## Assumptions

- The provider registry (mapping provider IDs to API key environment variables) remains unchanged.
- Only two providers (OpenAI, Anthropic) are currently supported; the pattern should easily extend to future providers.
- Environment variables remain the configuration mechanism.
- The frontend model selector and storage schemas do not require changes (provider information is still included in API responses).

## Out of Scope

- Adding new LLM providers.
- Changes to the frontend model selector UI.
- Changes to the provider factory pattern or error handling from 012.
- Provider-specific configuration options beyond model lists (this feature prepares the ground but does not implement provider-specific settings).
