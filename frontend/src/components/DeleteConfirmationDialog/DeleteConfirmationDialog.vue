<template>
  <div
    class="delete-dialog-overlay"
    @click.self="handleCancel"
    @keyup.escape="handleCancel"
  >
    <div
      class="delete-dialog"
      role="dialog"
      aria-labelledby="delete-dialog-title"
      aria-modal="true"
    >
      <h3
        id="delete-dialog-title"
        class="dialog-title"
      >
        Delete Conversation
      </h3>
      <p class="dialog-message">
        Are you sure you want to delete "<strong>{{ conversationTitle }}</strong>"?
      </p>
      <p class="dialog-warning">
        This action cannot be undone.
      </p>
      <div class="dialog-actions">
        <button
          ref="cancelButtonRef"
          class="btn btn-secondary"
          @click="handleCancel"
        >
          Cancel
        </button>
        <button
          class="btn btn-danger"
          @click="handleConfirm"
        >
          Delete
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'DeleteConfirmationDialog',
  props: {
    conversationTitle: {
      type: String,
      required: true,
    },
  },
  emits: ['confirm', 'cancel'],
  setup(props, { emit }) {
    const cancelButtonRef = ref(null)

    function handleConfirm() {
      emit('confirm')
    }

    function handleCancel() {
      emit('cancel')
    }

    function handleEscape(event) {
      if (event.key === 'Escape') {
        handleCancel()
      }
    }

    onMounted(() => {
      // Focus the cancel button for safety (less destructive action)
      if (cancelButtonRef.value) {
        cancelButtonRef.value.focus()
      }
      document.addEventListener('keydown', handleEscape)
    })

    onUnmounted(() => {
      document.removeEventListener('keydown', handleEscape)
    })

    return {
      cancelButtonRef,
      handleConfirm,
      handleCancel,
    }
  },
}
</script>

<style scoped>
.delete-dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.5);
}

.delete-dialog {
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

.dialog-message {
  margin: 0 0 var(--spacing-sm);
  font-size: var(--font-size-md);
  color: var(--color-text);
  line-height: 1.5;
}

.dialog-message strong {
  word-break: break-word;
}

.dialog-warning {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-error, #dc2626);
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

.btn-danger {
  background-color: var(--color-error, #dc2626);
  border: none;
  color: white;
}

.btn-danger:hover {
  background-color: #b91c1c;
}

.btn-danger:focus-visible {
  outline-color: var(--color-error, #dc2626);
}
</style>
