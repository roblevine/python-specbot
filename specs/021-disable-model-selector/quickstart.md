# Quickstart: Disable Model Selector After Conversation Starts

**Feature**: 021-disable-model-selector
**Date**: 2026-01-22

## Overview

This guide provides step-by-step instructions for implementing the model selector locking behavior. The feature disables the model selector once a conversation has messages, preventing mid-conversation model changes.

## Prerequisites

- Node.js 18+ and npm
- Python 3.13 and pip
- Running backend server (`npm run dev` in backend/)
- Running frontend dev server (`npm run dev` in frontend/)

## Implementation Steps

### Step 1: Modify useModels Composable

**File**: `frontend/src/state/useModels.js`

Add optional `persist` parameter to `setSelectedModel`:

```javascript
// Before
const setSelectedModel = (modelId) => {
  selectedModelId.value = modelId
  SettingsStorage.saveSetting('selectedModelId', modelId)
}

// After
const setSelectedModel = (modelId, persist = true) => {
  selectedModelId.value = modelId
  if (persist) {
    SettingsStorage.saveSetting('selectedModelId', modelId)
  }
}
```

### Step 2: Add Helper Function for Conversation Model

**File**: `frontend/src/state/useConversations.js` or `frontend/src/components/App/App.vue`

```javascript
/**
 * Get the model ID used in a conversation from its first system message
 * @param {Object} conversation - Conversation object with messages array
 * @returns {string|null} - Model ID or null if not found
 */
const getConversationModelId = (conversation) => {
  if (!conversation?.messages?.length) return null

  const firstSystemMessage = conversation.messages.find(
    msg => msg.sender === 'system' && msg.model
  )

  return firstSystemMessage?.model || null
}
```

### Step 3: Add Computed Properties in App.vue

**File**: `frontend/src/components/App/App.vue`

```javascript
// Import at top
import { computed, watch } from 'vue'

// In setup or script setup
const { activeConversation, setActiveConversation } = useConversations()
const { selectedModelId, setSelectedModel, availableModels, getDefaultModel } = useModels()

// Computed: Should model selector be disabled?
const isModelSelectorDisabled = computed(() => {
  return activeConversation.value?.messages?.length > 0
})

// Computed: Get conversation's model ID
const conversationModelId = computed(() => {
  return getConversationModelId(activeConversation.value)
})

// Watch: Restore model when switching conversations
watch(activeConversation, (newConversation) => {
  if (newConversation?.messages?.length > 0) {
    const modelId = getConversationModelId(newConversation)
    if (modelId) {
      setSelectedModel(modelId, false) // Don't persist
    } else {
      // Legacy conversation without model - use default
      const defaultModel = getDefaultModel()
      if (defaultModel) {
        setSelectedModel(defaultModel.id, false)
      }
    }
  }
}, { immediate: true })
```

### Step 4: Pass Disabled State to InputArea

**File**: `frontend/src/components/App/App.vue`

Update template to pass disabled state:

```vue
<template>
  <!-- ... -->
  <InputArea
    :disabled="isProcessing"
    :model-selector-disabled="isModelSelectorDisabled"
    @send="handleSend"
  />
  <!-- ... -->
</template>
```

### Step 5: Update InputArea Component

**File**: `frontend/src/components/InputArea/InputArea.vue`

Add new prop and pass to ModelSelector:

```vue
<script setup>
const props = defineProps({
  disabled: Boolean,
  modelSelectorDisabled: Boolean  // NEW
})
</script>

<template>
  <div class="input-area">
    <ModelSelector
      :disabled="props.modelSelectorDisabled"
      <!-- other props -->
    />
    <!-- rest of template -->
  </div>
</template>
```

### Step 6: Handle Unavailable Models (Edge Case)

**File**: `frontend/src/components/App/App.vue`

```javascript
// Computed: Check if conversation's model is available
const isConversationModelAvailable = computed(() => {
  const modelId = conversationModelId.value
  if (!modelId) return true
  return availableModels.value.some(m => m.id === modelId)
})

// If model unavailable, we still show the model ID but add indicator
// This can be handled in ModelSelector or by creating a display name
```

## Testing the Implementation

### Manual Test Cases

1. **New conversation - selector enabled**
   - Click "New Conversation"
   - Verify model selector dropdown works
   - Change model selection
   - Verify change is reflected

2. **After first message - selector disabled**
   - In new conversation, send a message
   - After response received, try clicking model selector
   - Verify selector is grayed out and non-interactive

3. **Load previous conversation - shows correct model**
   - Create conversation using GPT-4
   - Navigate to conversation list
   - Click to load the conversation
   - Verify model selector shows "GPT-4" and is disabled

4. **New conversation after viewing existing**
   - While viewing conversation with messages
   - Click "New Conversation"
   - Verify model selector becomes enabled

### Automated Tests

Create test file: `frontend/tests/unit/components/ModelSelector.spec.js`

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ModelSelector from '@/components/ModelSelector/ModelSelector.vue'

describe('ModelSelector disabled state', () => {
  it('is enabled when disabled prop is false', () => {
    const wrapper = mount(ModelSelector, {
      props: { disabled: false, models: mockModels }
    })
    expect(wrapper.find('select').attributes('disabled')).toBeUndefined()
  })

  it('is disabled when disabled prop is true', () => {
    const wrapper = mount(ModelSelector, {
      props: { disabled: true, models: mockModels }
    })
    expect(wrapper.find('select').attributes('disabled')).toBeDefined()
  })
})
```

## Verification Checklist

- [ ] Model selector enabled for new conversation (0 messages)
- [ ] Model selector disabled after first message sent
- [ ] Loading previous conversation shows correct model
- [ ] Loading previous conversation disables selector
- [ ] New Conversation button re-enables selector
- [ ] Legacy conversations without model show default model
- [ ] Unavailable models display with indicator
- [ ] No console errors during state transitions

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Selector not disabling | Watch not triggering | Check activeConversation reactivity |
| Wrong model displayed | Model field missing | Check message has model field set |
| Selector stays disabled | Stale state | Verify setActiveConversation resets properly |
| Global preference changed | persist=true used | Ensure persist=false when loading conversation |
