<template>
  <div
    class="rename-dialog-overlay"
    @click.self="handleCancel"
  >
    <div
      class="rename-dialog"
      role="dialog"
      aria-labelledby="rename-dialog-title"
      aria-modal="true"
    >
      <h3
        id="rename-dialog-title"
        class="dialog-title"
      >
        Rename Conversation
      </h3>
      <input
        ref="inputRef"
        v-model="titleInput"
        type="text"
        class="title-input"
        :class="{ 'has-error': error }"
        placeholder="Enter conversation title"
        maxlength="500"
        @keyup.enter="handleSave"
        @keyup.escape="handleCancel"
      >
      <p
        v-if="error"
        class="error-message"
      >
        {{ error }}
      </p>
      <p class="character-count">
        {{ titleInput.length }} / 500
      </p>
      <div class="dialog-actions">
        <button
          class="btn btn-secondary"
          @click="handleCancel"
        >
          Cancel
        </button>
        <button
          class="btn btn-primary"
          :disabled="!isValid"
          @click="handleSave"
        >
          Save
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'RenameDialog',
  props: {
    currentTitle: {
      type: String,
      required: true,
    },
  },
  emits: ['save', 'cancel'],
  setup(props, { emit }) {
    const titleInput = ref(props.currentTitle)
    const inputRef = ref(null)

    const error = computed(() => {
      const trimmed = titleInput.value.trim()
      if (trimmed.length === 0) {
        return 'Title cannot be empty'
      }
      if (trimmed.length > 500) {
        return 'Title cannot exceed 500 characters'
      }
      return null
    })

    const isValid = computed(() => !error.value)

    function handleSave() {
      if (isValid.value) {
        emit('save', titleInput.value.trim())
      }
    }

    function handleCancel() {
      emit('cancel')
    }

    onMounted(() => {
      // Focus and select the input on mount
      if (inputRef.value) {
        inputRef.value.focus()
        inputRef.value.select()
      }
    })

    return {
      titleInput,
      inputRef,
      error,
      isValid,
      handleSave,
      handleCancel,
    }
  },
}
</script>

<style scoped>
.rename-dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.5);
}

.rename-dialog {
  width: 100%;
  max-width: 400px;
  padding: var(--spacing-lg);
  background-color: var(--color-surface);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.dialog-title {
  margin: 0 0 var(--spacing-md);
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text);
}

.title-input {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-md);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  background-color: var(--color-background);
  color: var(--color-text);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.title-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb, 0, 112, 243), 0.2);
}

.title-input.has-error {
  border-color: var(--color-error);
}

.title-input.has-error:focus {
  box-shadow: 0 0 0 3px rgba(var(--color-error-rgb, 239, 68, 68), 0.2);
}

.error-message {
  margin: var(--spacing-xs) 0 0;
  font-size: var(--font-size-sm);
  color: var(--color-error);
}

.character-count {
  margin: var(--spacing-xs) 0 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  text-align: right;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

.btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  font-size: var(--font-size-sm);
  font-weight: 500;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: background-color 0.2s, opacity 0.2s;
}

.btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.btn-secondary {
  background-color: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.btn-secondary:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.btn-primary {
  background-color: var(--color-primary, #0070f3);
  border: none;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark, #0060df);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
