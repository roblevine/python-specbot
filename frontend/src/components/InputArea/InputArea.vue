<template>
  <div class="input-area">
    <!-- Feature 015: ModelSelector positioned above chat input within input pane -->
    <ModelSelector class="model-selector-container" />
    <div class="input-container">
      <textarea
        v-model="inputText"
        class="input-textarea"
        placeholder="Type your message..."
        :disabled="disabled"
        @keydown.enter.exact="handleEnter"
        @keydown.enter.shift.exact="handleShiftEnter"
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
import { ref, computed } from 'vue'
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
  },
  emits: ['send-message'],
  setup(props, { emit }) {
    const inputText = ref('')

    const canSend = computed(() => {
      return inputText.value.trim().length > 0
    })

    function handleSend() {
      if (!canSend.value || props.disabled) return

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

    function clearInput() {
      inputText.value = ''
    }

    return {
      inputText,
      canSend,
      handleSend,
      handleEnter,
      handleShiftEnter,
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

/* Feature 015: Model selector container - no width constraints for full-width layout */
.model-selector-container {
  width: 100%;
}

.input-container {
  display: flex;
  gap: var(--spacing-md);
  flex: 1;
  min-height: 0;
  /* Feature 015: Removed max-width constraint to restore full-width textarea */
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
