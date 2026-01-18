# Feature Specification: Delete Conversation

**Feature Branch**: `016-delete-conversation`
**Created**: 2026-01-18
**Status**: Draft
**Input**: User description: "I'd like to add a delete option for conversations in the history. It will manifest as an additional option in the ellipses context menu for messages in the history. It should not appear in the context menu for the current conversation at the top. This delete will completely expunge all traces of the conversation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delete Historical Conversation (Priority: P1)

A user wants to remove an old conversation they no longer need from their history. They locate the conversation in the sidebar, click the ellipsis menu, and select "Delete" to permanently remove it. The conversation disappears from the history list immediately.

**Why this priority**: This is the core functionality of the feature. Without the ability to delete conversations, users cannot manage their conversation history, leading to clutter and potential privacy concerns.

**Independent Test**: Can be fully tested by creating multiple conversations, then deleting one via the context menu and verifying it no longer appears in the history list.

**Acceptance Scenarios**:

1. **Given** a user has multiple conversations in their history, **When** they click the ellipsis menu on a non-active conversation, **Then** they see both "Rename" and "Delete" options in the menu.
2. **Given** a user clicks "Delete" on a conversation, **When** the deletion completes, **Then** the conversation is removed from the sidebar history list.
3. **Given** a user deletes a conversation, **When** they refresh the page, **Then** the deleted conversation does not reappear.

---

### User Story 2 - Deletion Confirmation (Priority: P2)

A user accidentally clicks "Delete" on a conversation they didn't mean to remove. A confirmation dialog appears asking them to confirm the action, preventing accidental data loss.

**Why this priority**: Confirmation prevents irreversible data loss from accidental clicks. While secondary to the core delete functionality, it's essential for a safe user experience.

**Independent Test**: Can be tested by clicking Delete on any conversation and verifying a confirmation dialog appears before any deletion occurs.

**Acceptance Scenarios**:

1. **Given** a user clicks "Delete" on a conversation, **When** the action is triggered, **Then** a confirmation dialog appears before deletion proceeds.
2. **Given** a confirmation dialog is displayed, **When** the user clicks "Cancel" or presses Escape, **Then** the dialog closes and the conversation remains intact.
3. **Given** a confirmation dialog is displayed, **When** the user confirms deletion, **Then** the conversation is permanently removed.

---

### User Story 3 - Protected Active Conversation (Priority: P3)

A user is actively working in a conversation. The ellipsis menu for this active conversation does not show the Delete option, preventing users from accidentally deleting the conversation they are currently using.

**Why this priority**: This is a safeguard feature that prevents edge-case user errors. The core delete and confirmation features must work first before adding this protection layer.

**Independent Test**: Can be tested by selecting a conversation and verifying its context menu does not contain the Delete option while it remains active.

**Acceptance Scenarios**:

1. **Given** a conversation is currently active (selected/displayed in the main area), **When** a user opens its ellipsis context menu, **Then** the "Delete" option is not visible.
2. **Given** a conversation was previously active but user switched to another, **When** the user opens the ellipsis menu on the now-inactive conversation, **Then** the "Delete" option is visible.

---

### Edge Cases

- What happens when the user deletes the last non-active conversation? The history shows only the active conversation.
- What happens if deletion fails due to a server error? An error message is displayed and the conversation remains in the list.
- What happens if user tries to delete while offline? The operation fails gracefully with an appropriate error message.
- What happens if user rapidly clicks delete on multiple conversations? Each deletion request is processed independently with individual confirmations.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a "Delete" option in the ellipsis context menu for all conversations except the currently active conversation.
- **FR-002**: System MUST display a confirmation dialog when a user selects "Delete" from the context menu.
- **FR-003**: The confirmation dialog MUST clearly identify which conversation will be deleted (showing the conversation title).
- **FR-004**: The confirmation dialog MUST provide "Cancel" and "Delete" action buttons with "Delete" styled as a destructive action.
- **FR-005**: Upon confirmation, the system MUST permanently remove all conversation data from storage (both frontend and backend).
- **FR-006**: System MUST update the conversation history list immediately after successful deletion without requiring a page refresh.
- **FR-007**: System MUST NOT display the "Delete" option for the currently active conversation in the sidebar.
- **FR-008**: System MUST display an error message if deletion fails, keeping the conversation intact.
- **FR-009**: The confirmation dialog MUST be dismissible via Escape key or clicking outside the dialog (same as existing Rename dialog).
- **FR-010**: System MUST prevent multiple simultaneous delete operations on the same conversation.

### Key Entities

- **Conversation**: The entity being deleted; contains id, title, messages array, createdAt, and updatedAt timestamps. Deletion removes the entire conversation record including all associated messages.
- **Confirmation Dialog**: Modal component that blocks interaction until user confirms or cancels the delete action.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can delete any non-active conversation in 3 or fewer clicks (open menu, click Delete, confirm).
- **SC-002**: Deleted conversations are completely removed from history with no residual data remaining after deletion.
- **SC-003**: The confirmation dialog prevents 100% of accidental single-click deletions by requiring explicit confirmation.
- **SC-004**: Users receive immediate visual feedback upon successful deletion (conversation disappears from list).
- **SC-005**: Users receive clear error feedback within 2 seconds if deletion fails.
- **SC-006**: 100% of active conversations are protected from accidental deletion (Delete option hidden).

## Assumptions

- The existing backend DELETE /api/v1/conversations/{id} endpoint provides complete conversation removal (this endpoint already exists per codebase exploration).
- The existing TitleMenu component can be extended to support additional menu options.
- The delete confirmation dialog will follow the same modal pattern as the existing RenameDialog component.
- Users understand that deletion is permanent and irreversible (communicated via confirmation dialog text).
- The active conversation is determined by the `activeConversationId` state variable already in use.
