<template>
  <div
    ref="chatArea"
    class="chat-area"
  >
    <div
      v-if="messages.length === 0 && !streamingMessage"
      class="empty-state"
    >
      <p>No messages yet. Start typing below!</p>
    </div>
    <div
      v-if="messages.length > 0 || streamingMessage"
      class="messages-container"
    >
      <MessageBubble
        v-for="message in messages"
        :key="message.id"
        :message="message"
      />
      <!-- T021: Display streaming message below regular messages -->
      <MessageBubble
        v-if="streamingMessage"
        :key="'streaming-' + streamingMessage.id"
        :message="streamingMessage"
      />
    </div>
    <div
      v-if="isProcessing"
      class="loading-indicator"
    >
      <span class="loading-dots">Processing...</span>
    </div>
  </div>
</template>

<script>
import { ref, watch, nextTick } from 'vue'
import MessageBubble from './MessageBubble.vue'
import { useMessages } from '../../state/useMessages.js'

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
    const { streamingMessage, isStreaming } = useMessages()

    // Auto-scroll to bottom helper
    const scrollToBottom = async () => {
      await nextTick()
      if (chatArea.value) {
        chatArea.value.scrollTop = chatArea.value.scrollHeight
      }
    }

    // Auto-scroll to bottom when messages change
    watch(
      () => props.messages.length,
      scrollToBottom
    )

    // T021: Auto-scroll when streaming message text changes
    watch(
      () => streamingMessage.value?.text,
      scrollToBottom
    )

    return {
      chatArea,
      streamingMessage,
      isStreaming,
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
  max-width: var(--chat-max-width);
  margin-left: auto;
  margin-right: auto;
  padding: 0 var(--spacing-md);
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
