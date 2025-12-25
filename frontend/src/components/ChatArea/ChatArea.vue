<template>
  <div ref="chatArea" class="chat-area">
    <div v-if="messages.length === 0" class="empty-state">
      <p>No messages yet. Start typing below!</p>
    </div>
    <div v-else class="messages-container">
      <MessageBubble v-for="message in messages" :key="message.id" :message="message" />
    </div>
    <div v-if="isProcessing" class="loading-indicator">
      <span class="loading-dots">Processing...</span>
    </div>
  </div>
</template>

<script>
import { ref, watch, nextTick } from 'vue'
import MessageBubble from './MessageBubble.vue'

export default {
  name: 'ChatArea',
  components: {
    MessageBubble,
  },
  props: {
    messages: {
      type: Array,
      default: () => [],
    },
    isProcessing: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const chatArea = ref(null)

    // Auto-scroll to bottom when messages change
    watch(
      () => props.messages.length,
      async () => {
        await nextTick()
        if (chatArea.value) {
          chatArea.value.scrollTop = chatArea.value.scrollHeight
        }
      }
    )

    return {
      chatArea,
    }
  },
}
</script>

<style scoped>
.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
  background-color: var(--color-background);
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary);
  font-size: var(--font-size-lg);
}

.loading-indicator {
  padding: var(--spacing-md);
  text-align: center;
  color: var(--color-text-secondary);
}

.loading-dots {
  display: inline-block;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
