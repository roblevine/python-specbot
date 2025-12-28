# Feature Specification: Backend API Loopback

**Feature Branch**: `003-backend-api-loopback`
**Created**: 2025-12-28
**Status**: Draft
**Input**: User description: "we are now going to build out the back-end in a very simple form. We will stand up the backend, initially only implementing the loopback message, and replacing the client-side loopback with this. Responses from the server will be prefixed with 'api says: '."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Send Message to Backend and Receive Loopback Response (Priority: P1)

Users can send messages through the chat interface and receive responses from the backend server instead of the client-side loopback. The server echoes back the user's message prefixed with "api says: ".

**Why this priority**: This is the foundational capability that establishes backend communication. It proves the full-stack integration works (frontend → backend → frontend) and provides a simple, testable endpoint for validating the architecture before adding complex LLM integrations.

**Independent Test**: Can be fully tested by sending a message through the chat interface and verifying that the response comes from the backend server with the "api says: " prefix. This delivers immediate value by demonstrating working client-server communication.

**Acceptance Scenarios**:

1. **Given** the user is on the chat interface, **When** the user types "Hello world" and clicks Send, **Then** the chat area displays the user message followed by a system message containing "api says: Hello world"

2. **Given** the user has sent a message, **When** the backend server processes the request, **Then** the response is received within 2 seconds and displayed in the chat area

3. **Given** the user sends multiple messages in sequence, **When** each message is processed, **Then** each response contains "api says: " followed by the exact text of the corresponding user message

4. **Given** the user sends a message with special characters (emoji, punctuation, line breaks), **When** the backend processes it, **Then** the response preserves all special characters in the loopback message

---

### User Story 2 - Handle Backend Connection Errors Gracefully (Priority: P2)

When the backend server is unavailable or experiences errors, users receive clear feedback about the connection status and can understand what went wrong.

**Why this priority**: Error handling is essential for production readiness but can be implemented after basic functionality works. Users need to know when the backend is down versus when their message was processed.

**Independent Test**: Can be tested by stopping the backend server and attempting to send a message, then verifying appropriate error messages appear. Also test by simulating network timeouts.

**Acceptance Scenarios**:

1. **Given** the backend server is not running, **When** the user sends a message, **Then** the status bar shows "Error: Cannot connect to server" and the message is not sent

2. **Given** the user is sending a message, **When** the backend takes longer than 10 seconds to respond, **Then** the request times out and displays "Error: Request timed out. Please try again."

3. **Given** the backend returns a server error (500), **When** the user sends a message, **Then** the status bar shows "Error: Server error occurred" and the user can retry sending

4. **Given** the backend connection fails mid-request, **When** the error occurs, **Then** the user's message remains in the input area so they can retry without retyping

---

### Edge Cases

- What happens when the user sends an empty message? (Frontend validation should prevent this, but backend should reject empty messages gracefully)
- What happens when the user sends extremely long messages (>10,000 characters)? (Backend should have message length limits)
- What happens if the backend is under heavy load and responses are delayed? (Frontend should show loading indicator and handle timeouts)
- What happens when multiple messages are sent rapidly in succession? (Backend should handle concurrent requests and maintain message order)
- What happens if the network connection drops during message transmission? (Frontend should detect network errors and show appropriate message)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a backend API server that accepts message requests from the frontend
- **FR-002**: Backend server MUST echo back received messages prefixed with "api says: " in the response
- **FR-003**: Frontend MUST send user messages to the backend API instead of processing them locally
- **FR-004**: Frontend MUST display backend responses in the chat area as system messages
- **FR-005**: System MUST maintain message order - responses appear in the same order as requests
- **FR-006**: Backend MUST respond to valid message requests within 2 seconds under normal load
- **FR-007**: Backend MUST reject messages exceeding 10,000 characters with appropriate error response
- **FR-008**: Frontend MUST handle backend connection failures and display error messages to users
- **FR-009**: Frontend MUST implement request timeout of 10 seconds for backend API calls
- **FR-010**: Backend MUST accept messages containing special characters, emoji, and multi-byte characters
- **FR-011**: System MUST preserve message content exactly as sent (no truncation or modification except the "api says: " prefix)
- **FR-012**: Backend MUST validate incoming requests and reject malformed or missing message data
- **FR-013**: Frontend MUST show loading indicator while waiting for backend response
- **FR-014**: Backend MUST log all incoming requests and responses for debugging purposes

### Key Entities

- **Message Request**: User-submitted message from frontend to backend, containing message text and metadata (timestamp, conversation ID if applicable)
- **Message Response**: Backend response containing the loopback message with "api says: " prefix, status code, and any error information
- **Conversation Context**: Reference to the active conversation (may use existing conversation ID from frontend LocalStorage)

### Assumptions

- **Backend Framework**: Assuming a REST API approach with JSON request/response format (implementation details to be determined in planning phase)
- **Communication Protocol**: HTTP/HTTPS for request-response pattern (WebSocket not needed for simple loopback)
- **Message Format**: Messages sent as plain text strings in JSON payload
- **Conversation Persistence**: Backend does not yet persist conversations - it only echoes messages. Conversation storage remains in frontend LocalStorage for now.
- **Authentication**: No authentication required for this initial backend implementation (will be added in future iterations)
- **CORS**: Backend will need to allow requests from the frontend origin (localhost during development)
- **Port Configuration**: Backend and frontend run on different ports (frontend likely 5173, backend port TBD in planning)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can send messages through the chat interface and receive backend responses with "api says: " prefix within 2 seconds
- **SC-002**: System successfully handles 100 messages in sequence without errors or message loss
- **SC-003**: When backend is unavailable, users see clear error messages within 1 second of sending a message
- **SC-004**: 100% of sent messages receive responses in the correct order (no message reordering)
- **SC-005**: Special characters and emoji in messages are preserved exactly in responses (character-for-character match)
- **SC-006**: System functionality is verified at all levels - individual components work correctly, components integrate properly, and complete user workflows succeed
- **SC-007**: Users experience no noticeable difference in chat interface behavior compared to client-side loopback (except for "api says: " prefix and network latency)
