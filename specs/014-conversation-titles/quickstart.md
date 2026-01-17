# Quickstart: Conversation Titles Implementation

**Feature**: 014-conversation-titles
**Date**: 2026-01-17

## Prerequisites

- Node.js 18+ installed
- Frontend dev server runs: `cd frontend && npm run dev`
- Existing tests pass: `cd frontend && npm test`

## Implementation Summary

This is a **frontend-only** feature. Backend is already complete.

### Files to Create (2 new components)

1. `frontend/src/components/TitleMenu/TitleMenu.vue` - Ellipsis dropdown menu
2. `frontend/src/components/RenameDialog/RenameDialog.vue` - Modal for renaming

### Files to Modify (4 existing files)

1. `frontend/src/components/StatusBar/StatusBar.vue` - Add title display
2. `frontend/src/components/HistoryBar/HistoryBar.vue` - Remove preview, add menu
3. `frontend/src/components/App/App.vue` - Wire up title and rename handling
4. `frontend/src/state/useConversations.js` - Add renameConversation function

## Quick Implementation Guide

### Step 1: Enhance Auto-Title (useConversations.js)

**Current code** (lines 107-110):
```javascript
if (conversation.title === 'New Conversation' && conversation.messages.length === 1) {
  conversation.title = message.text.slice(0, 50)
}
```

**Change to**:
```javascript
if (conversation.title === 'New Conversation' && conversation.messages.length === 1) {
  conversation.title = message.text  // Store full text, no truncation
}
```

**Add rename function**:
```javascript
function renameConversation(conversationId, newTitle) {
  const conversation = conversations.value.find(c => c.id === conversationId)
  if (conversation) {
    conversation.title = newTitle.trim()
    conversation.updatedAt = new Date().toISOString()
    saveToStorage()
  }
}
```

### Step 2: Create TitleMenu Component

```vue
<!-- frontend/src/components/TitleMenu/TitleMenu.vue -->
<template>
  <div class="title-menu">
    <button
      class="menu-trigger"
      @click="toggleMenu"
      aria-label="Conversation options"
    >
      ⋯
    </button>
    <div v-if="isOpen" class="menu-dropdown">
      <button @click="handleRename">Rename</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'TitleMenu',
  emits: ['rename'],
  setup(props, { emit }) {
    const isOpen = ref(false)

    function toggleMenu() {
      isOpen.value = !isOpen.value
    }

    function handleRename() {
      isOpen.value = false
      emit('rename')
    }

    function handleClickOutside(event) {
      if (!event.target.closest('.title-menu')) {
        isOpen.value = false
      }
    }

    onMounted(() => document.addEventListener('click', handleClickOutside))
    onUnmounted(() => document.removeEventListener('click', handleClickOutside))

    return { isOpen, toggleMenu, handleRename }
  }
}
</script>
```

### Step 3: Create RenameDialog Component

```vue
<!-- frontend/src/components/RenameDialog/RenameDialog.vue -->
<template>
  <div class="rename-dialog-overlay" @click.self="$emit('cancel')">
    <div class="rename-dialog">
      <h3>Rename Conversation</h3>
      <input
        v-model="titleInput"
        ref="inputRef"
        @keyup.enter="handleSave"
        @keyup.escape="$emit('cancel')"
        maxlength="500"
      />
      <p v-if="error" class="error">{{ error }}</p>
      <div class="actions">
        <button @click="$emit('cancel')">Cancel</button>
        <button @click="handleSave" :disabled="!isValid">Save</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'RenameDialog',
  props: {
    currentTitle: { type: String, required: true }
  },
  emits: ['save', 'cancel'],
  setup(props, { emit }) {
    const titleInput = ref(props.currentTitle)
    const inputRef = ref(null)

    const error = computed(() => {
      const trimmed = titleInput.value.trim()
      if (trimmed.length === 0) return 'Title cannot be empty'
      if (trimmed.length > 500) return 'Title cannot exceed 500 characters'
      return null
    })

    const isValid = computed(() => !error.value)

    function handleSave() {
      if (isValid.value) {
        emit('save', titleInput.value.trim())
      }
    }

    onMounted(() => {
      inputRef.value?.focus()
      inputRef.value?.select()
    })

    return { titleInput, inputRef, error, isValid, handleSave }
  }
}
</script>
```

### Step 4: Update StatusBar (Add Title Display)

Add to template:
```vue
<div class="status-bar">
  <div class="title-section">
    <span class="conversation-title">{{ title }}</span>
    <TitleMenu v-if="title !== 'New Conversation'" @rename="$emit('rename')" />
  </div>
  <div class="status-indicator" :class="statusType">
    <!-- existing status content -->
  </div>
</div>
```

Add prop:
```javascript
props: {
  title: { type: String, default: 'New Conversation' },
  // ... existing props
}
```

### Step 5: Update HistoryBar (Title Only, Add Menu)

**Remove** from template:
```vue
<div class="conversation-preview">
  {{ getPreview(conversation) }}
</div>
```

**Remove** from script:
```javascript
function getPreview(conversation) { ... }
```

**Add** to each conversation item:
```vue
<TitleMenu @rename="$emit('rename-conversation', conversation.id)" />
```

### Step 6: Update App.vue (Wire Everything)

Add computed:
```javascript
const activeConversationTitle = computed(() => {
  const active = conversations.value.find(c => c.id === activeConversationId.value)
  return active?.title || 'New Conversation'
})
```

Add state:
```javascript
const showRenameDialog = ref(false)
const renamingConversationId = ref(null)
```

Add handlers:
```javascript
function handleRenameRequest(conversationId) {
  renamingConversationId.value = conversationId || activeConversationId.value
  showRenameDialog.value = true
}

function handleRenameSave(newTitle) {
  renameConversation(renamingConversationId.value, newTitle)
  showRenameDialog.value = false
}
```

## Testing Checklist

### Unit Tests to Add

- [ ] `TitleMenu.vue` - Opens/closes on click, emits 'rename' event
- [ ] `RenameDialog.vue` - Validates input, emits 'save' with trimmed title
- [ ] `useConversations.renameConversation()` - Updates title and timestamp

### Manual Testing

1. Create new conversation → Title shows "New Conversation"
2. Send first message → Title updates to message text
3. Check StatusBar → Title displayed, aligned with chat
4. Check HistoryBar → Only title shown, no preview
5. Click ellipsis in StatusBar → Menu opens with "Rename"
6. Rename conversation → Title updates everywhere
7. Hover conversation in HistoryBar → Ellipsis appears
8. Rename from HistoryBar → Title updates correctly

## CSS Guidelines

Use existing CSS variables:
- `--chat-max-width: 768px` for title container alignment
- `--font-size-sm` for title text
- `--color-text` for title color
- `--color-border` for menu borders

Truncation with CSS:
```css
.conversation-title {
  max-width: var(--chat-max-width);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

## Common Pitfalls

1. **Don't truncate on storage** - Store full title, truncate only for display
2. **Validate before save** - Check non-empty and max length
3. **Update `updatedAt`** - Always set when title changes
4. **Handle default title** - Don't show rename menu for "New Conversation"
5. **Click outside to close** - Menu should close when clicking elsewhere
