<template>
  <div
    class="message-bubble"
    :class="messageClass"
    :data-sender="message.sender"
    :data-message-id="message.id"
  >
    <div class="message-text">
      {{ message.text }}
    </div>
    <div class="message-timestamp">
      {{ formattedTime }}
    </div>
    <!-- T025-T027: Error section for status='error' -->
    <div v-if="message.status === 'error'" class="error-section">
      <div class="error-icon">⚠</div>
      <div class="error-message">{{ message.errorMessage }}</div>

      <!-- T053: Details toggle button -->
      <button
        v-if="hasErrorDetails"
        class="error-toggle"
        @click="errorCollapsible.toggle"
        @keydown="handleKeyDown"
        v-bind="errorCollapsible.triggerAttrs"
      >
        {{ errorCollapsible.isExpanded.value ? 'Hide Details' : 'Details' }}
      </button>
    </div>

    <!-- T054-T055: Expandable error details section with transition -->
    <transition name="expand">
      <div
        v-if="hasErrorDetails && errorCollapsible.isExpanded.value"
        class="error-details"
        v-bind="errorCollapsible.contentAttrs"
      >
        <div class="error-details-header">
          <strong>Type:</strong> {{ message.errorType }}
          <span v-if="message.errorCode"> | <strong>Code:</strong> {{ message.errorCode }}</span>
        </div>
        <pre class="error-stack">{{ redactedErrorDetails }}</pre>
      </div>
    </transition>
  </div>
</template>

<script>
import { computed } from 'vue'
// T048-T049: Import useCollapsible composable and redactSensitiveData
import { useCollapsible } from '../../composables/useCollapsible.js'
import { redactSensitiveData } from '../../utils/sensitiveDataRedactor.js'

export default {
  name: 'MessageBubble',
  props: {
    message: {
      type: Object,
      required: true,
      validator: msg => {
        return (
          msg.id &&
          msg.text &&
          ['user', 'system'].includes(msg.sender) &&
          msg.timestamp &&
          ['pending', 'sent', 'error'].includes(msg.status)
        )
      },
    },
  },
  setup(props) {
    const messageClass = computed(() => ({
      'message-user': props.message.sender === 'user',
      'message-system': props.message.sender === 'system',
      'message-pending': props.message.status === 'pending',
      'message-error': props.message.status === 'error',
    }))

    const formattedTime = computed(() => {
      const date = new Date(props.message.timestamp)
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
      })
    })

    // T050: Add errorCollapsible instance
    const errorCollapsible = useCollapsible(false)

    // T051: Add hasErrorDetails computed property
    const hasErrorDetails = computed(() => {
      return props.message.status === 'error' && props.message.errorDetails
    })

    // T052: Add redactedErrorDetails computed property
    const redactedErrorDetails = computed(() => {
      if (!props.message.errorDetails) return ''

      // Parse JSON if it's a string, otherwise use as is
      let detailsText = props.message.errorDetails
      if (typeof detailsText === 'string') {
        try {
          // Pretty print JSON for readability
          const parsed = JSON.parse(detailsText)
          detailsText = JSON.stringify(parsed, null, 2)
        } catch (e) {
          // If not valid JSON, use as is
        }
      }

      // Redact sensitive data
      return redactSensitiveData(detailsText, false)
    })

    // T046: Handle keyboard navigation
    const handleKeyDown = (event) => {
      if (event.key === 'Enter' || event.key === ' ' || event.key === 'Spacebar') {
        event.preventDefault()
        errorCollapsible.toggle()
      }
    }

    return {
      messageClass,
      formattedTime,
      errorCollapsible,
      hasErrorDetails,
      redactedErrorDetails,
      handleKeyDown,
    }
  },
}
</script>

<style scoped>
.message-bubble {
  max-width: 70%;
  margin: var(--spacing-sm) 0;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-lg);
  word-wrap: break-word;
  animation: slideIn 0.2s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-user {
  align-self: flex-end;
  background-color: var(--color-user-message-bg);
  color: var(--color-user-message-text);
  margin-left: auto;
}

.message-system {
  align-self: flex-start;
  background-color: var(--color-system-message-bg);
  color: var(--color-system-message-text);
  margin-right: auto;
}

.message-text {
  font-size: var(--font-size-md);
  line-height: 1.5;
  white-space: pre-wrap;
}

.message-timestamp {
  font-size: var(--font-size-sm);
  opacity: 0.7;
  margin-top: var(--spacing-xs);
  text-align: right;
}

.message-pending {
  opacity: 0.6;
}

.message-error {
  border: 2px solid var(--color-error);
  opacity: 0.8;
}

/* T028: Error section styling */
.error-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  margin-top: var(--spacing-sm);
  padding: var(--spacing-sm);
  background-color: var(--color-error-background);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
}

.error-icon {
  color: var(--color-error);
  font-size: var(--font-size-lg);
  flex-shrink: 0;
}

.error-message {
  color: var(--color-error);
  word-wrap: break-word;
  flex: 1;
}

/* T056: Error toggle button styling */
.error-toggle {
  margin-left: auto;
  padding: var(--spacing-xs) var(--spacing-sm);
  background-color: transparent;
  border: 1px solid var(--color-error);
  border-radius: var(--border-radius-sm);
  color: var(--color-error);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
}

.error-toggle:hover {
  background-color: var(--color-error);
  color: white;
}

.error-toggle:focus {
  outline: 2px solid var(--color-error);
  outline-offset: 2px;
}

/* T057: Error details section styling */
.error-details {
  margin-top: var(--spacing-sm);
  padding: var(--spacing-sm);
  background-color: rgba(239, 68, 68, 0.05);
  border-left: 3px solid var(--color-error);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
}

.error-details-header {
  margin-bottom: var(--spacing-xs);
  color: var(--color-error);
}

/* T058: Error stack pre tag styling */
.error-stack {
  font-family: 'Courier New', Courier, monospace;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  background-color: rgba(0, 0, 0, 0.05);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}

/* T059: Expand/collapse transition styles */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
}

.expand-enter-to,
.expand-leave-from {
  max-height: 500px;
  opacity: 1;
  transform: translateY(0);
}
</style>
