# Feature Specification: Conversation Titles

**Feature Branch**: `014-conversation-titles`
**Created**: 2026-01-17
**Status**: Draft
**Input**: User description: "Introduce conversation titles feature. Each conversation has a title that is initially the first message sent by the user. The top status line should show the title, aligned with the chat window. The conversation history shows only the title for each conversation (not the preview of the last message currently shown). Users can rename conversations via an ellipsis menu option in both the message history and the title bar."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Display Title in Status Bar (Priority: P1)

A user is viewing an active conversation. The status bar at the top of the application displays the conversation's title, aligned with the chat window content area, helping the user understand which conversation they're currently viewing.

**Why this priority**: This is the most visible part of the feature and provides immediate context to users about what conversation they're in. Without this, the title feature has no primary display location.

**Independent Test**: Can be fully tested by creating a conversation, sending a message, and verifying the status bar displays the conversation title aligned with the chat content.

**Acceptance Scenarios**:

1. **Given** a user starts a new conversation and sends "Help me debug my code", **When** the conversation is active, **Then** the status bar displays "Help me debug my code" as the title
2. **Given** a user switches between conversations, **When** each conversation becomes active, **Then** the status bar updates to show that conversation's title
3. **Given** the chat window has a maximum width constraint, **When** the status bar displays the title, **Then** the title is aligned with the chat content area (not full viewport width)
4. **Given** a conversation has a very long title, **When** displayed in the status bar, **Then** the title is truncated with ellipsis to fit available space

---

### User Story 2 - Auto-generate Title from First User Message (Priority: P1)

A user starts a new conversation and sends their first message. The system automatically uses this first message as the conversation title, providing meaningful identification without requiring manual title creation.

**Why this priority**: This is the core mechanism for title generation. Without automatic title creation, users would need to manually title every conversation, creating friction. This must exist for the feature to be usable.

**Independent Test**: Can be fully tested by creating new conversations with various first messages and verifying each conversation's title matches the first user message.

**Acceptance Scenarios**:

1. **Given** a user starts a new conversation, **When** they send their first message "What is the capital of France?", **Then** the conversation title becomes "What is the capital of France?"
2. **Given** a new conversation has no messages yet, **When** viewing the conversation, **Then** the title displays a default placeholder (e.g., "New Conversation")
3. **Given** a user sends a very long first message (>200 characters), **When** the title is generated, **Then** the full message is stored as the title (truncation happens only at display time)
4. **Given** a conversation already has a title, **When** messages are added or deleted, **Then** the title remains unchanged (only first message sets initial title)

---

### User Story 3 - Display Titles in Conversation History (Priority: P1)

A user views the conversation history sidebar. Each conversation item displays only its title (not a preview of the last message), making it easier to identify and navigate between conversations.

**Why this priority**: This is a critical usability improvement that directly addresses the current limitation. Users can find conversations by their meaningful titles rather than scanning message previews.

**Independent Test**: Can be fully tested by creating multiple conversations with different titles and verifying the history sidebar shows only titles with no message previews.

**Acceptance Scenarios**:

1. **Given** the user has multiple conversations, **When** viewing the history sidebar, **Then** each conversation displays only its title (no message preview below)
2. **Given** a conversation has a long title, **When** displayed in the history sidebar, **Then** the title is truncated with ellipsis to fit the sidebar width
3. **Given** a conversation has the default title "New Conversation", **When** displayed in the history sidebar, **Then** it shows "New Conversation" (not an empty state)
4. **Given** multiple conversations have similar titles, **When** viewing the history, **Then** each title is displayed fully (or consistently truncated) to aid differentiation

---

### User Story 4 - Rename Conversation from Title Bar (Priority: P2)

A user viewing a conversation clicks an ellipsis menu in the title bar and selects "Rename". They can update the conversation title to something more meaningful than the auto-generated default.

**Why this priority**: This provides users control over their conversation organization. While not critical for basic functionality (auto-titles work fine), it enhances usability for power users and long-term organization.

**Independent Test**: Can be fully tested by clicking the ellipsis menu in the title bar, selecting rename, entering a new title, and verifying the title updates throughout the UI.

**Acceptance Scenarios**:

1. **Given** a user is viewing a conversation, **When** they click the ellipsis menu icon in the title bar, **Then** a menu appears with a "Rename" option
2. **Given** the user selects "Rename" from the title bar menu, **When** the rename interface appears, **Then** the current title is pre-populated for editing
3. **Given** the user enters a new title "Project Planning Discussion" and confirms, **When** the rename is saved, **Then** the title bar, status bar, and history sidebar all update to show the new title
4. **Given** the user cancels the rename operation, **When** they dismiss the rename interface, **Then** the original title remains unchanged
5. **Given** the user enters an empty title, **When** they attempt to save, **Then** the system prevents saving and prompts for a valid title

---

### User Story 5 - Rename Conversation from History Sidebar (Priority: P2)

A user viewing the conversation history sidebar clicks an ellipsis menu on a conversation item and selects "Rename". They can update the conversation title without having to switch to that conversation first.

**Why this priority**: This provides an alternative location for renaming, useful during conversation organization sessions. However, renaming from the title bar (US4) is the primary method, making this a secondary enhancement.

**Independent Test**: Can be fully tested by clicking the ellipsis menu on a conversation in the history sidebar, selecting rename, and verifying the title updates.

**Acceptance Scenarios**:

1. **Given** a user is viewing the conversation history sidebar, **When** they hover over or interact with a conversation item, **Then** an ellipsis menu icon appears
2. **Given** the user clicks the ellipsis menu on a conversation item, **When** the menu opens, **Then** it displays a "Rename" option
3. **Given** the user selects "Rename" from the history sidebar menu, **When** the rename interface appears, **Then** the current title is pre-populated for editing
4. **Given** the user saves a new title from the history sidebar, **When** the rename completes, **Then** the history sidebar updates immediately and the title bar updates if that conversation is currently active
5. **Given** the user renames a conversation that is not currently active, **When** they later switch to that conversation, **Then** the title bar displays the updated title

---

### Edge Cases

- What happens when the first user message contains special characters (newlines, emojis, HTML/markdown)? The title should store them but display appropriately (e.g., strip/normalize newlines).
- What happens when a user renames a conversation to a very long title (>500 characters)? System should enforce a reasonable maximum length.
- What happens when a user tries to rename a conversation while it's processing a message? Rename should be disabled during processing or queued.
- What happens to existing conversations that don't have titles (created before this feature)? They should be migrated to use their first user message as the title, or "Untitled Conversation" if no messages exist.
- What happens when multiple users access the same conversation simultaneously and rename it? This depends on whether the system supports multi-user access (assumed single-user for now).
- What happens to the title if the first message is deleted? The title should remain unchanged (titles persist independently of messages after initial creation).

## Requirements *(mandatory)*

### Functional Requirements

**Title Storage and Generation**
- **FR-001**: System MUST add a title property to each conversation entity
- **FR-002**: System MUST automatically set a new conversation's title to the text of the first user message when that message is sent
- **FR-003**: System MUST use a default title "New Conversation" for conversations that have no messages yet
- **FR-004**: System MUST persist conversation titles across sessions (saved to storage)
- **FR-005**: System MUST preserve the full text of the title without automatic truncation (truncation only for display)

**Title Display**
- **FR-006**: System MUST display the current conversation's title in the status bar at the top of the application
- **FR-007**: System MUST align the title display in the status bar with the chat window content area (respecting max-width constraints)
- **FR-008**: System MUST display conversation titles in the history sidebar for each conversation item
- **FR-009**: System MUST replace the current message preview display in the history sidebar with title-only display
- **FR-010**: System MUST truncate long titles with ellipsis when displayed in constrained spaces (status bar, history sidebar)
- **FR-011**: System MUST update the displayed title immediately when a conversation is renamed

**Title Editing**
- **FR-012**: System MUST provide an ellipsis menu in the title bar with a "Rename" option
- **FR-013**: System MUST provide an ellipsis menu on each conversation item in the history sidebar with a "Rename" option
- **FR-014**: System MUST display a rename interface (input field or inline editor) when the user selects "Rename"
- **FR-015**: System MUST pre-populate the rename interface with the current title
- **FR-016**: System MUST save the new title when the user confirms the rename operation
- **FR-017**: System MUST cancel the rename operation without changes when the user dismisses or cancels
- **FR-018**: System MUST validate that renamed titles are not empty (minimum 1 non-whitespace character)
- **FR-019**: System MUST enforce a maximum title length of 500 characters

**Data Migration**
- **FR-020**: System MUST migrate existing conversations to include a title field on first load after feature deployment
- **FR-021**: System MUST set migrated conversation titles to their first user message text, or "Untitled Conversation" if no messages exist

### Key Entities

- **Conversation**: Represents a conversation between user and assistant. Key attributes: id, title (new), messages array, creation timestamp. The title is a text string that defaults to the first user message content.
- **Title Display Component**: UI element in the status bar showing the current conversation's title. Attributes: displayed text (truncated if needed), alignment with chat content area.
- **Conversation History Item**: UI element in the sidebar representing a conversation. Attributes: conversation id, displayed title (replaces previous preview text), active state.
- **Rename Menu**: UI component providing rename functionality. Attributes: menu trigger (ellipsis icon), menu items (Rename option), location (title bar or history sidebar).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of conversations display their title in the status bar when active
- **SC-002**: 100% of new conversations automatically receive a title matching their first user message
- **SC-003**: Conversation history sidebar displays only titles for all conversations (0% showing message previews)
- **SC-004**: Users can successfully rename any conversation from both the title bar and history sidebar with 100% success rate
- **SC-005**: Title updates reflect immediately (within 100ms) across all display locations (status bar, history sidebar)
- **SC-006**: All existing conversations are successfully migrated with appropriate titles on first load
- **SC-007**: Long titles are consistently truncated with ellipsis in all display contexts, maintaining readability
- **SC-008**: Users can identify and navigate between conversations 40% faster using titles compared to message previews (measured by time to find a specific conversation)
- **SC-009**: Title validation prevents empty titles in 100% of rename attempts with empty input

## Assumptions

- The application is single-user (no concurrent multi-user editing of conversation titles)
- Conversations are stored in a format that supports adding new properties (title field)
- The status bar has sufficient space to display conversation titles (with truncation for very long titles)
- Users prefer meaningful titles over message previews for conversation navigation
- The ellipsis menu pattern is familiar and discoverable for users
- Conversation titles do not require rich text formatting (plain text only)
- Title character limit of 500 characters is sufficient for all use cases
- Existing conversations can be migrated without data loss or breaking changes
- The rename operation is synchronous or appears synchronous to users (no long loading states)
- Title bar refers to the status bar area at the top of the application (not the browser window title)
