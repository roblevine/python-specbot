# Feature Specification: Add Ollama Model Support

**Feature Branch**: `020-add-ollama-support`
**Created**: 2026-01-22
**Status**: Draft
**Input**: User description: "Add local Ollama model support through the same LangChain infrastructure"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Use Local Ollama Models (Priority: P1)

As a user, I want to select and use models running on my local Ollama server so that I can chat with locally-hosted LLMs without relying on external API services.

**Why this priority**: This is the core functionality - without the ability to select and use Ollama models, the feature has no value. Users need this for privacy-focused workflows, offline capabilities, and cost savings.

**Independent Test**: Can be fully tested by configuring Ollama models in environment variables, starting a local Ollama server with a model like `llama2`, selecting that model in the UI, and sending a chat message to verify response generation.

**Acceptance Scenarios**:

1. **Given** I have Ollama running locally with models installed, **When** I view the model selector, **Then** I see my configured Ollama models listed alongside cloud provider models.
2. **Given** I have selected an Ollama model, **When** I send a chat message, **Then** I receive a streamed response from the local Ollama server.
3. **Given** Ollama models are configured, **When** I select an Ollama model and chat, **Then** the message indicator shows the Ollama model was used for that response.

---

### User Story 2 - Handle Ollama Server Unavailable (Priority: P2)

As a user, I want clear feedback when my local Ollama server is not running or unreachable so that I understand why my messages are failing and can take corrective action.

**Why this priority**: Error handling is critical for usability - users need to understand when their local server is down versus other issues. However, this depends on P1 being functional first.

**Independent Test**: Can be tested by configuring Ollama models, stopping the Ollama server, attempting to send a message, and verifying that an appropriate error message appears.

**Acceptance Scenarios**:

1. **Given** Ollama server is not running, **When** I attempt to send a message to an Ollama model, **Then** I receive a clear error message indicating the local server is unreachable.
2. **Given** I was chatting with an Ollama model and the server goes down mid-conversation, **When** I send a new message, **Then** I receive an error explaining the connection was lost.
3. **Given** I see an Ollama connection error, **When** I start the Ollama server and retry my message, **Then** the message is processed successfully.

---

### User Story 3 - Configure Custom Ollama Server URL (Priority: P3)

As a user running Ollama on a different machine or port, I want to configure the Ollama server URL so that I can connect to remote or non-default Ollama instances.

**Why this priority**: While most users run Ollama locally on the default port, some advanced users run it on remote machines or custom ports. This extends flexibility without being essential for basic functionality.

**Independent Test**: Can be tested by running Ollama on a non-default port (e.g., 11435), configuring the custom URL in environment variables, and verifying that the system connects to the correct server.

**Acceptance Scenarios**:

1. **Given** I have configured a custom Ollama base URL, **When** I send a message to an Ollama model, **Then** the system connects to my custom URL instead of the default localhost:11434.
2. **Given** no custom URL is configured, **When** I use Ollama models, **Then** the system defaults to http://localhost:11434.

---

### Edge Cases

- What happens when a user configures Ollama models but has no Ollama server installed?
  - System displays a connection error when attempting to use Ollama models
- How does the system handle Ollama models that are configured but not installed in Ollama?
  - Ollama returns an error; system displays a clear message about the model not being found
- What happens if Ollama server is very slow to respond (e.g., downloading a model)?
  - System respects configured timeout; displays timeout error if exceeded
- How does the system handle mixed conversations (switching between cloud and local models)?
  - System handles seamlessly; each message is processed by its selected model

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support Ollama as a model provider using the existing provider architecture pattern
- **FR-002**: System MUST allow configuration of Ollama models via the `OLLAMA_MODELS` environment variable in the same JSON format as other providers
- **FR-003**: System MUST support optional configuration of Ollama server URL via `OLLAMA_BASE_URL` environment variable
- **FR-004**: System MUST default to `http://localhost:11434` when no custom base URL is configured
- **FR-005**: System MUST display Ollama models in the model selector with "ollama" provider identification
- **FR-006**: System MUST support streaming responses from Ollama models using the existing streaming infrastructure
- **FR-007**: System MUST map Ollama-specific errors to user-friendly error messages
- **FR-008**: System MUST indicate when an Ollama model was used for a response (via model indicator on messages)
- **FR-009**: System MUST NOT require an API key for Ollama provider (local server authentication is optional)
- **FR-010**: System MUST gracefully handle Ollama server connection failures with clear error messaging

### Key Entities

- **Ollama Provider**: A model provider representing the local Ollama server, following the same pattern as OpenAI and Anthropic providers
- **Ollama Model Configuration**: Model definitions including id, name, and description (provider inferred from OLLAMA_MODELS env var)
- **Ollama Base URL**: Optional configuration for custom server location (host and port)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully send messages to locally-hosted Ollama models and receive streamed responses
- **SC-002**: Ollama models appear in the model selector and are visually distinguishable as local/Ollama models
- **SC-003**: Connection errors to Ollama server are clearly communicated to users within 5 seconds of failure
- **SC-004**: System functions correctly with Ollama as the only configured provider (no cloud providers required)
- **SC-005**: Switching between Ollama and cloud provider models mid-conversation works seamlessly with no data loss

## Assumptions

- Users have Ollama installed and running on their local machine (or network) with at least one model pulled
- Ollama server exposes the standard API at the configured base URL
- The LangChain Ollama integration (langchain-ollama) provides equivalent capabilities to OpenAI/Anthropic integrations
- Users understand that Ollama response quality and speed depends on their local hardware capabilities
- No authentication is required for Ollama server access (standard Ollama default configuration)

## Out of Scope

- Automatic detection or listing of available models from the Ollama server (models must be explicitly configured)
- Installing or managing Ollama models from within the application
- GPU/hardware configuration or optimization guidance
- Ollama server health monitoring or status dashboard
- Multiple Ollama server configurations (only one base URL supported)
