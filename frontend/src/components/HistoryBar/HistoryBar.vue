<template>
  <div class="history-bar">
    <div class="history-header">
      <h2>Conversations</h2>
    </div>
    <div class="conversations-list">
      <div
        v-for="conversation in conversations"
        :key="conversation.id"
        class="conversation-item"
        :class="{ active: conversation.id === activeConversationId }"
        @click="$emit('select-conversation', conversation.id)"
      >
        <div class="conversation-title">
          {{ conversation.title }}
        </div>
        <div class="conversation-preview">
          {{ getPreview(conversation) }}
        </div>
      </div>
      <div
        v-if="conversations.length === 0"
        class="empty-history"
      >
        No conversations yet
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HistoryBar',
  props: {
    conversations: {
      type: Array,
      default: () => [],
    },
    activeConversationId: {
      type: String,
      default: null,
    },
  },
  emits: ['select-conversation'],
  setup() {
    function getPreview(conversation) {
      if (conversation.messages.length === 0) {
        return 'No messages'
      }
      const lastMessage = conversation.messages[conversation.messages.length - 1]
      return lastMessage.text.slice(0, 50) + (lastMessage.text.length > 50 ? '...' : '')
    }

    return {
      getPreview,
    }
  },
}
</script>

<style scoped>
.history-bar {
  display: flex;
  flex-direction: column;
  width: var(--history-bar-width);
  background-color: var(--color-surface);
  border-right: 1px solid var(--color-border);
}

.history-header {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.history-header h2 {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text);
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: background-color 0.2s;
}

.conversation-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.conversation-item.active {
  background-color: var(--color-primary);
  color: white;
}

.conversation-title {
  font-weight: 600;
  font-size: var(--font-size-md);
  margin-bottom: var(--spacing-xs);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-preview {
  font-size: var(--font-size-sm);
  opacity: 0.8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.empty-history {
  padding: var(--spacing-lg);
  text-align: center;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}
</style>
