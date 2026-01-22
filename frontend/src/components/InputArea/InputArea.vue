<template>
  <div class="input-area">
    <!-- Feature 015: ModelSelector positioned above chat input within input pane -->
    <!-- Feature 021: Pass disabled state to lock model selector after conversation starts -->
    <ModelSelector class="model-selector-container" :disabled="modelSelectorDisabled" />
    <div class="input-container">
      <textarea
        ref="inputRef"
        v-model="inputText"
        class="input-textarea"
        placeholder="Type your message..."
        :disabled="disabled"
        @keydown.enter.exact="handleEnter"
        @keydown.enter.shift.exact="handleShiftEnter"
        @blur="handleBlur"
      />
      <button
        class="send-button"
        :disabled="disabled || !canSend"
        @click="handleSend"
      >
        Send
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, nextTick } from 'vue'
// Feature 015: Import ModelSelector for positioning within input area
import ModelSelector from '../ModelSelector/ModelSelector.vue'

export default {
  name: 'InputArea',
  components: {
    ModelSelector,
  },
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
    /**
     * Feature: 021-disable-model-selector
     * Controls whether the model selector is disabled (locked)
     * Set to true when conversation has messages to prevent model changes
     */
    modelSelectorDisabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['send-message'],
  setup(props, { emit }) {
    const inputText = ref('')
    // Feature 022: Template ref for textarea element
    const inputRef = ref(null)
    // Feature 022: Track if user had focus before sending
    const hadFocusBeforeSend = ref(false)

    const canSend = computed(() => {
      return inputText.value.trim().length > 0
    })

    function handleSend() {
      if (!canSend.value || props.disabled) return

      // Feature 022: Capture focus state before sending
      hadFocusBeforeSend.value = document.activeElement === inputRef.value

      const text = inputText.value.trim()
      if (text) {
        emit('send-message', text)
        inputText.value = ''
      }
    }

    function handleEnter(event) {
      // Enter without Shift = Send
      event.preventDefault()
      handleSend()
    }

    function handleShiftEnter() {
      // Shift+Enter = new line (default behavior, don't prevent)
      // Textarea default behavior will insert newline
    }

    /**
     * Feature 022: Handle blur to detect when user intentionally clicks elsewhere
     * This resets the focus tracking so we don't forcibly restore focus
     */
    function handleBlur() {
      // Small delay to allow click events to register first
      // This handles the case where clicking the send button triggers blur
      setTimeout(() => {
        // If the textarea is no longer focused and we're not in a send operation,
        // the user intentionally moved focus elsewhere
        if (document.activeElement !== inputRef.value && !props.disabled) {
          hadFocusBeforeSend.value = false
        }
      }, 100)
    }

    /**
     * Feature 022: Restore focus to input after response completes
     * Called by parent component when AI response is finished
     */
    function restoreFocus() {
      if (hadFocusBeforeSend.value) {
        nextTick(() => {
          inputRef.value?.focus()
        })
      }
    }

    function clearInput() {
      inputText.value = ''
    }

    return {
      inputText,
      inputRef,
      canSend,
      handleSend,
      handleEnter,
      handleShiftEnter,
      handleBlur,
      restoreFocus,
      clearInput,
    }
  },
}
</script>

<style scoped>
.input-area {
  padding: var(--spacing-md);
  background-color: var(--color-surface);
  border-top: 1px solid var(--color-border);
  /* Feature 015: Increased height to accommodate model selector above input */
  min-height: var(--input-area-height);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

/* Feature 015: Model selector container - aligned with chat message area width */
.model-selector-container {
  max-width: var(--chat-max-width);
  margin-left: auto;
  margin-right: auto;
  width: 100%;
}

.input-container {
  display: flex;
  gap: var(--spacing-md);
  max-width: var(--chat-max-width);
  margin-left: auto;
  margin-right: auto;
  width: 100%;
  flex: 1;
  min-height: 0;
}

.input-textarea {
  flex: 1;
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  font-family: var(--font-family);
  font-size: var(--font-size-md);
  resize: none;
  outline: none;
  transition: border-color 0.2s;
}

.input-textarea:focus {
  border-color: var(--color-primary);
}

.input-textarea:disabled {
  background-color: var(--color-surface);
  opacity: 0.6;
  cursor: not-allowed;
}

/* Feature 015: Clear enabled/disabled button states */
.send-button {
  padding: 0 var(--spacing-xl);
  background-color: var(--color-primary);
  color: white;
  border: 1px solid var(--color-primary);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-md);
  font-weight: 500;
  cursor: pointer;
  transition: all 200ms ease;
}

.send-button:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.send-button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.send-button:disabled {
  background-color: transparent;
  color: var(--color-text-secondary);
  border-color: var(--color-border);
  opacity: 0.5;
  cursor: not-allowed;
}

.send-button:active:not(:disabled) {
  background-color: var(--color-warm-dark);
  border-color: var(--color-warm-dark);
  transform: scale(0.98);
}
</style>
