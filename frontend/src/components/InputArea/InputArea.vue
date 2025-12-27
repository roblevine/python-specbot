<template>
  <div class="input-area">
    <textarea
      v-model="inputText"
      class="input-textarea"
      placeholder="Type your message..."
      :disabled="disabled"
      @keydown.enter.exact="handleEnter"
      @keydown.enter.shift.exact="handleShiftEnter"
    />
    <button class="send-button" :disabled="disabled || !canSend" @click="handleSend">Send</button>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'InputArea',
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
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background-color: var(--color-surface);
  border-top: 1px solid var(--color-border);
  height: var(--input-area-height);
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

.send-button {
  padding: 0 var(--spacing-xl);
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-md);
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.send-button:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.send-button:disabled {
  background-color: var(--color-secondary);
  opacity: 0.5;
  cursor: not-allowed;
}

.send-button:active:not(:disabled) {
  transform: scale(0.98);
}
</style>
