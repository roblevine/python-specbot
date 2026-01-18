# Quickstart: Delete Conversation Feature

**Branch**: `016-delete-conversation`
**Date**: 2026-01-18

## Overview

Add a "Delete" option to the conversation context menu in the history sidebar, with a confirmation dialog to prevent accidental deletion. The delete option is hidden for the currently active conversation.

## Prerequisites

- Backend server running (`cd backend && uvicorn src.main:app --reload`)
- Frontend dev server running (`cd frontend && npm run dev`)
- Existing test suites passing

## Implementation Order (Thin Slices)

### Slice 1: P1 - Basic Delete Flow (MVP)
1. Extend TitleMenu with `showDelete` prop and `delete` emit
2. Create DeleteConfirmationDialog component
3. Wire up HistoryBar to emit delete events
4. Add delete handler in App.vue
5. Connect to existing `deleteConversation()` in useConversations

### Slice 2: P2 - Confirmation Dialog Polish
1. Add conversation title to confirmation message
2. Style delete button as danger/destructive (red)
3. Add keyboard support (Enter to confirm, Escape to cancel)

### Slice 3: P3 - Active Conversation Protection
1. Pass `showDelete={conversation.id !== activeConversationId}` in HistoryBar
2. Verify delete option hidden for active conversation

## Key Files to Modify

| File | Changes |
|------|---------|
| `frontend/src/components/TitleMenu/TitleMenu.vue` | Add `showDelete` prop, `delete` emit, menu item |
| `frontend/src/components/HistoryBar/HistoryBar.vue` | Pass prop, handle emit, bubble event |
| `frontend/src/components/App/App.vue` | Handle event, show dialog, call composable |
| `frontend/src/components/DeleteConfirmationDialog/DeleteConfirmationDialog.vue` | **NEW**: Confirmation modal |

## New Component: DeleteConfirmationDialog

```vue
<template>
  <div class="dialog-overlay" @click.self="$emit('cancel')">
    <div class="dialog-box">
      <h2>Delete Conversation</h2>
      <p>Are you sure you want to delete "{{ conversationTitle }}"?</p>
      <p class="warning">This action cannot be undone.</p>
      <div class="dialog-actions">
        <button class="cancel-btn" @click="$emit('cancel')">Cancel</button>
        <button class="delete-btn" @click="$emit('confirm')">Delete</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  conversationTitle: { type: String, required: true }
})
defineEmits(['confirm', 'cancel'])
</script>
```

## Testing Strategy

### Unit Tests
- TitleMenu: Verify `delete` emit fires, verify option hidden when `showDelete=false`
- DeleteConfirmationDialog: Verify emits, keyboard handling, title display

### Integration Tests
- Full flow: Click delete → dialog appears → confirm → conversation removed
- Cancel flow: Click delete → dialog appears → cancel → conversation remains
- Error handling: Mock API failure → error displayed → conversation remains

## Running Tests

```bash
# Frontend unit tests
cd frontend && npm test

# Frontend with coverage
cd frontend && npm run test:coverage

# All tests
./scripts/test-all.sh
```

## Verification Checklist

- [ ] Delete option appears in context menu for non-active conversations
- [ ] Delete option NOT visible for active conversation
- [ ] Confirmation dialog shows conversation title
- [ ] Cancel/Escape closes dialog without deleting
- [ ] Confirm removes conversation from list immediately
- [ ] Deleted conversation does not return after page refresh
- [ ] Error message displayed if deletion fails
- [ ] All existing tests still pass
