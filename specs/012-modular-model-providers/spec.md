# Feature Specification: Modular Model Providers

**Feature Branch**: `012-modular-model-providers`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "we now support two model providers - OpenAI and Anthropic. We will shortly introduce more. Firstly, we have some work to clean up and consolidate to make this properly modular and extensible against multiple model providers. For instance, in config, the available models for OpenAI and Anthropic are listed separately, but this should be a consolidated list that includes provider information. There may well be further consolidations in code, config, tests and documentation. Please tidy up the implementations and move us to a proper provider type pattern approach"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Unified Provider Configuration (Priority: P1)

As a developer configuring the application, I want to define all model providers and their models in a single consolidated configuration structure, so that I can easily see all available models across providers and add new providers without modifying multiple configuration locations.

**Why this priority**: This is the foundation for all other consolidation work. Without a unified configuration structure, the system cannot properly support modular providers. This directly addresses the user's primary concern about "models for OpenAI and Anthropic listed separately."

**Independent Test**: Can be fully tested by configuring a new provider entry and verifying it appears in the models list without code changes to provider-specific loading functions.

**Acceptance Scenarios**:

1. **Given** a configuration with multiple providers defined, **When** the application starts, **Then** all models from all enabled providers are available in a single consolidated list with provider information included.

2. **Given** a provider configuration entry, **When** the required API key environment variable is not set, **Then** models for that provider are excluded from the available models list and the system logs a clear message.

3. **Given** a new provider needs to be added, **When** a developer adds the provider configuration, **Then** no changes are required to existing provider code or loading logic.

---

### User Story 2 - Consolidated Error Handling (Priority: P2)

As a developer maintaining the chat service, I want provider-specific errors to be handled through a unified error mapping system, so that I don't have to duplicate exception handling code for each provider and each method that calls the LLM.

**Why this priority**: Current implementation has ~90 lines of duplicated exception handling between `get_ai_response()` and `stream_ai_response()`. This consolidation significantly reduces maintenance burden and ensures consistent error responses.

**Independent Test**: Can be fully tested by triggering various provider errors (authentication, rate limit, timeout) and verifying consistent error responses regardless of which method was called.

**Acceptance Scenarios**:

1. **Given** an authentication error from any provider, **When** the error is processed, **Then** a consistent authentication error response is returned using the same code path.

2. **Given** a rate limit error from any provider, **When** the error is processed, **Then** the error is mapped to a unified rate limit error with appropriate retry information.

3. **Given** a provider-specific error type that doesn't exist in other providers, **When** the error is processed, **Then** it is gracefully mapped to the most appropriate generic error category.

---

### User Story 3 - Provider Factory Pattern (Priority: P2)

As a developer adding a new LLM provider, I want to implement a provider interface with standardized methods, so that I can add new providers by implementing a well-defined contract rather than modifying existing switch statements.

**Why this priority**: Equal priority with error handling as both are needed for proper extensibility. The current factory function uses if/elif chains that must be modified for each new provider.

**Independent Test**: Can be fully tested by creating a mock provider implementation and verifying it integrates correctly without modifying existing provider code.

**Acceptance Scenarios**:

1. **Given** a new provider implementation, **When** it is registered with the system, **Then** it becomes available for use without modifying the core factory code.

2. **Given** multiple registered providers, **When** a model is requested, **Then** the correct provider instance is created based on the model's provider field.

3. **Given** a provider with custom initialization requirements, **When** the provider is instantiated, **Then** provider-specific parameters (like timeout settings) are correctly applied.

---

### User Story 4 - Test Consolidation (Priority: P3)

As a developer writing tests, I want provider tests to follow a consistent pattern, so that I can easily add tests for new providers by following an established template.

**Why this priority**: Tests should reflect the consolidated architecture. This is lower priority because existing tests will continue to pass during refactoring.

**Independent Test**: Can be fully tested by examining test coverage reports and verifying provider-agnostic test patterns exist alongside provider-specific tests.

**Acceptance Scenarios**:

1. **Given** a new provider implementation, **When** I write tests for it, **Then** I can use a consistent test pattern/template that covers initialization, error mapping, and response handling.

2. **Given** the consolidated provider architecture, **When** tests are run, **Then** all existing tests continue to pass with the new structure.

---

### Edge Cases

- **Invalid API key**: When a provider's API key is present but invalid, the system returns an authentication error through the unified error mapping. The provider remains in the available list (configuration is valid) but requests fail with a clear authentication error message.

- **Provider unavailable mid-conversation**: When a provider becomes unavailable during a conversation, the system returns a connection or timeout error through the unified error mapping. Users can retry or switch to a different model/provider. Conversation history is preserved.

- **Unknown model ID**: When a model ID is requested that doesn't match any configured provider, the system returns a validation error at request time. The error message indicates the model is not available in the current configuration.

- **Provider capability differences**: For core functionality (chat and streaming), all providers support the same capabilities through LangChain's unified interface. LangChain normalizes the underlying API differences. Advanced provider-specific features (vision, function calling) are out of scope for this consolidation and will be addressed in future features if/when needed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST maintain a single unified provider registry that contains all provider metadata including name, API key environment variable name, and models environment variable name.

- **FR-002**: System MUST load models from all enabled providers into a single consolidated list that includes provider identification for each model.

- **FR-003**: System MUST support adding new providers through configuration and a standardized provider interface without modifying existing provider implementations.

- **FR-004**: System MUST map provider-specific exceptions to a unified set of service-level errors that are consistent across all providers.

- **FR-005**: System MUST eliminate duplicate exception handling between streaming and non-streaming response methods.

- **FR-006**: System MUST preserve all existing API contracts and response formats to maintain backward compatibility.

- **FR-007**: System MUST handle provider-specific initialization parameters (such as timeout settings) through the provider abstraction without special-casing in core code.

- **FR-008**: System MUST log provider-related events (initialization, errors, missing configuration) in a consistent format across all providers.

- **FR-009**: System MUST continue to support provider-specific error types that don't have equivalents in other providers by mapping them to appropriate generic error categories.

### Key Entities

- **Provider**: Represents an LLM service provider (e.g., OpenAI, Anthropic). Contains: identifier, display name, configuration requirements, supported features.

- **Model**: Represents a specific model offered by a provider. Contains: model identifier, provider reference, display name, description, capabilities.

- **ProviderError**: Unified error representation that abstracts provider-specific exceptions. Contains: error category, message, provider source, retry information.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Adding a new provider requires implementing only the provider interface plus configuration - no modifications to existing provider code or core service logic.

- **SC-002**: Exception handling code is reduced by at least 40% through consolidation of duplicate handlers.

- **SC-003**: All existing frontend and backend tests pass without modification to test assertions (only test setup may change if needed).

- **SC-004**: Configuration for all providers is visible in a single location, eliminating the need to check multiple files or functions to understand available providers.

- **SC-005**: Error responses from any provider follow an identical structure and status code mapping.

- **SC-006**: Documentation clearly describes how to add a new provider, with estimated effort of under 1 hour for a developer familiar with the codebase.

## Assumptions

- The LangChain library will continue to be used as the LLM abstraction layer, and new providers will have LangChain support available.
- Provider-specific features beyond basic chat completion (e.g., function calling, vision) are out of scope for this consolidation.
- The existing file-based JSON storage and frontend localStorage mechanisms remain unchanged.
- Environment variables will continue to be the mechanism for API key configuration.
- The current API endpoints (`/api/v1/models`, `/api/v1/messages`) maintain their contracts.

## Out of Scope

- Adding new LLM providers (this feature is about making it easier to add them).
- Changes to the frontend model selector UI.
- Provider-specific advanced features (function calling, vision, embeddings).
- Migration to a different LLM abstraction library.
- Changes to conversation storage or persistence mechanisms.
