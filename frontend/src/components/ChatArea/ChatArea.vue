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
      <template
        v-for="message in messages"
        :key="message.id"
      >
        <MessageBubble :message="message" />
        <!-- T025: Display tool calls attached to historical messages -->
        <template v-if="message.toolCalls && message.toolCalls.length > 0">
          <ToolCallBubble
            v-for="toolCall in message.toolCalls"
            :key="toolCall.id"
            :tool-call="toolCall"
          />
        </template>
      </template>
      <!-- T025: Display current tool calls during streaming -->
      <template v-if="currentToolCalls && currentToolCalls.length > 0">
        <ToolCallBubble
          v-for="toolCall in currentToolCalls"
          :key="toolCall.id"
          :tool-call="toolCall"
        />
      </template>
      <!-- T021: Display streaming message below tool calls -->
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
import ToolCallBubble from './ToolCallBubble.vue'  // T025: Tool call display
import { useMessages } from '../../state/useMessages.js'

export default {
  name: 'ChatArea',
  components: {
    MessageBubble,
    ToolCallBubble,  // T025: Register tool call component
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
    // T024: Get currentToolCalls for live tool call display
    const { streamingMessage, isStreaming, currentToolCalls } = useMessages()

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

    // T025: Auto-scroll when tool calls change
    watch(
      () => currentToolCalls.value?.length,
      scrollToBottom
    )

    return {
      chatArea,
      streamingMessage,
      isStreaming,
      currentToolCalls,  // T025: Expose for template
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
