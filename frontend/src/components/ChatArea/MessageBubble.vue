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
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'MessageBubble',
  props: {
    message: {
      type: Object,
      required: true,
      validator: msg => {
        return (
          msg.id &&
          msg.text !== undefined && // Allow empty text during streaming
          ['user', 'system', 'assistant'].includes(msg.sender) && // Support assistant messages
          msg.timestamp &&
          ['pending', 'sent', 'error', 'streaming'].includes(msg.status) // Support streaming status
        )
      },
    },
  },
  setup(props) {
    const messageClass = computed(() => ({
      'message-user': props.message.sender === 'user',
      'message-system': props.message.sender === 'system',
      'message-assistant': props.message.sender === 'assistant',
      'message-pending': props.message.status === 'pending',
      'message-error': props.message.status === 'error',
      'message-streaming': props.message.status === 'streaming',
    }))

    const formattedTime = computed(() => {
      const date = new Date(props.message.timestamp)
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
      })
    })

    return {
      messageClass,
      formattedTime,
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

.message-assistant {
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
</style>
