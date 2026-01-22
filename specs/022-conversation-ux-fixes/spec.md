# Feature Specification: Conversation UX Fixes

**Feature Branch**: `022-conversation-ux-fixes`
**Created**: 2026-01-22
**Status**: Draft
**Input**: User description: "Minor bug fixes/improvements for conversation history sidebar and chat input focus retention"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conversation History Ordering (Priority: P1)

As a user viewing the conversation sidebar, I want the most recently updated conversations to appear at the top of the list so that I can quickly access my latest chats without scrolling.

**Why this priority**: This is a bug fix - the current behavior (new conversations appearing at bottom) is counterintuitive and impacts core usability. Users expect most recent items first in any list-based interface.

**Independent Test**: Can be fully tested by creating a new conversation and verifying it appears at the top of the conversation list. Delivers immediate value by reducing time to find recent conversations.

**Acceptance Scenarios**:

1. **Given** I have multiple existing conversations, **When** I create a new conversation, **Then** the new conversation appears at the top of the conversation list.
2. **Given** I have multiple conversations, **When** a conversation receives a new message (becomes most recently active), **Then** that conversation moves to the top of the list.
3. **Given** I have conversations sorted by recency, **When** I reload the application, **Then** the conversations remain sorted with most recent first.

---

### User Story 2 - Maintain Chat Input Focus (Priority: P1)

As a user engaged in a conversation, I want the message input field to retain focus after the AI response completes so that I can continue typing without clicking the input box again.

**Why this priority**: This significantly impacts keyboard-only workflow. Users typing multiple messages in succession should not need to re-select the input field between each exchange.

**Independent Test**: Can be tested by typing a message, pressing Enter to send, waiting for the complete AI response, and verifying the cursor remains in the input field ready for the next message.

**Acceptance Scenarios**:

1. **Given** I have focus in the message input box and type a message, **When** I press Enter and the message is sent and the AI response completes, **Then** the focus remains in the message input box.
2. **Given** I have focus in the input box and send a message, **When** the response is streaming, **Then** focus remains in the input box throughout the streaming process.
3. **Given** I have focus in the input box and the Send button becomes disabled during response, **When** the Send button re-enables after response completion, **Then** my cursor/focus is still in the message input box.
4. **Given** I click elsewhere in the UI while waiting for a response, **When** the AI response completes, **Then** focus is NOT forcibly returned to the input (respects user's focus change).

---

### User Story 3 - Add Timestamps to Conversation List (Priority: P2)

As a user browsing my conversation history, I want to see the date and time of each conversation's last activity so that I can identify conversations by when they occurred.

**Why this priority**: Improves discoverability and context for users with many conversations. Helps users find "that conversation from yesterday" or "the one from last week."

**Independent Test**: Can be tested by viewing the conversation list and verifying each entry displays a human-readable timestamp beneath the conversation title.

**Acceptance Scenarios**:

1. **Given** I view the conversation sidebar, **When** I look at a conversation entry, **Then** I see the date/time of last activity as small subtext below the conversation title.
2. **Given** a conversation was last active today, **When** viewing the timestamp, **Then** it shows time only (e.g., "3:45 PM") or relative time (e.g., "2 hours ago").
3. **Given** a conversation was last active on a previous day, **When** viewing the timestamp, **Then** it shows the day/date (e.g., "Yesterday" or "Jan 20, 2026").

---

### User Story 4 - Compact Conversation List Styling (Priority: P2)

As a user with many conversations, I want the conversation list entries to be more compact so that I can see more conversations without scrolling and reduce visual clutter.

**Why this priority**: Improves information density and usability. The current styling has oversized text and excessive spacing, which limits the number of visible conversations.

**Independent Test**: Can be tested by viewing the conversation sidebar and confirming entries use smaller text and reduced vertical spacing compared to current implementation.

**Acceptance Scenarios**:

1. **Given** I view the conversation sidebar, **When** I look at conversation entry text, **Then** the font size is smaller than the current oversized text while remaining readable.
2. **Given** I view multiple conversation entries, **When** I observe the vertical spacing between entries, **Then** the spacing is reduced to show more entries in the same viewport height.
3. **Given** a conversation title is too long, **When** displayed in the sidebar, **Then** it truncates gracefully with ellipsis without excessive wasted space.
4. **Given** I view the conversation list, **When** comparing before/after, **Then** I can see approximately 30-50% more conversation entries in the same viewport height.

---

### Edge Cases

- What happens when conversation list is empty? (Show empty state, no timestamp issues)
- How does system handle very old timestamps? (Display full date for conversations older than 7 days)
- What happens when user rapidly sends multiple messages? (Focus should remain stable)
- How does focus behave if an error occurs during message send? (Focus remains in input for retry)
- What happens when timestamps cross midnight during a session? (Timestamps update to "Yesterday" appropriately)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST sort conversation list with most recently active conversation at the top.
- **FR-002**: System MUST update conversation order when a new message is added to any conversation.
- **FR-003**: System MUST persist conversation ordering across page reloads.
- **FR-004**: System MUST maintain focus in the message input field after a message is sent and response is received, provided user has not clicked elsewhere.
- **FR-005**: System MUST NOT forcibly return focus to input if user intentionally clicked elsewhere during response.
- **FR-006**: System MUST display last activity timestamp as subtext below each conversation title in the sidebar.
- **FR-007**: System MUST format timestamps appropriately: relative/time-only for recent conversations, date for older ones.
- **FR-008**: System MUST use smaller font size for conversation titles in the sidebar compared to current implementation.
- **FR-009**: System MUST reduce vertical spacing between conversation list entries.
- **FR-010**: System MUST continue to truncate long conversation titles with ellipsis.

### Key Entities

- **Conversation**: Existing entity that tracks chat sessions. Relevant attribute: `updatedAt` timestamp used for sorting and display.
- **Message Input State**: Tracks whether user has focus in the chat input field and whether they intentionally moved focus away.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New conversations appear at the top of the conversation list immediately after creation (verified visually).
- **SC-002**: Users can send 5 consecutive messages using keyboard only (Enter to send) without needing to click the input field between messages.
- **SC-003**: Each conversation entry displays a readable timestamp showing last activity date/time.
- **SC-004**: The conversation list displays at least 30% more entries in the same viewport height compared to current implementation.
- **SC-005**: Conversation title text is visibly smaller while remaining readable at standard viewing distances.
- **SC-006**: Focus retention works correctly across all message send/receive scenarios (standard send, streaming response, error conditions).

## Assumptions

- The conversation data model already includes an `updatedAt` or equivalent timestamp field for sorting and display.
- Timestamp formatting follows standard locale conventions (12/24 hour based on user's system settings).
- "Recently active" for timestamp display purposes means within the last 24 hours.
- The font size reduction targets approximately 80-90% of current size (specific value to be determined during implementation based on visual testing).
- Vertical spacing reduction targets approximately 60-70% of current spacing (specific value to be determined during implementation).
