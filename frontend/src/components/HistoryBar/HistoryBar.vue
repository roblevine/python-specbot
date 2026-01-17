<template>
  <div
    class="history-bar"
    :class="{ collapsed: isCollapsed }"
  >
    <div class="history-header">
      <h2 v-if="!isCollapsed">
        Conversations
      </h2>
      <button
        class="collapse-button"
        :aria-label="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        :aria-expanded="!isCollapsed"
        @click="$emit('toggle-sidebar')"
      >
        <span class="icon">{{ isCollapsed ? '→' : '←' }}</span>
      </button>
    </div>
    <div
      v-if="!isCollapsed"
      class="button-container"
    >
      <button
        class="new-conversation-btn"
        aria-label="Start new conversation"
        @click="handleNewConversation"
      >
        New Conversation
      </button>
    </div>
    <div
      v-if="!isCollapsed"
      class="conversations-list"
    >
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
import { ref } from 'vue'

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
    isCollapsed: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['select-conversation', 'new-conversation', 'toggle-sidebar'],
  setup(props, { emit }) {
    const isCreating = ref(false)
    const DEBOUNCE_MS = 300

    function getPreview(conversation) {
      if (conversation.messages.length === 0) {
        return 'No messages'
      }
      const lastMessage = conversation.messages[conversation.messages.length - 1]
      return lastMessage.text.slice(0, 50) + (lastMessage.text.length > 50 ? '...' : '')
    }

    function handleNewConversation() {
      if (isCreating.value) {
        return
      }

      isCreating.value = true
      emit('new-conversation')

      setTimeout(() => {
        isCreating.value = false
      }, DEBOUNCE_MS)
    }

    return {
      getPreview,
      handleNewConversation,
    }
  },
}
</script>

<style scoped>
.history-bar {
  display: flex;
  flex-direction: column;
  width: var(--history-bar-width);
  background-color: var(--color-warm-cream);
  border-right: 1px solid var(--color-warm-dark);
  transition: width 300ms ease-in-out;
  overflow: hidden;
  color: #1d1d1f;
}

.history-bar.collapsed {
  width: 48px;
}

/* T037-T038: Add margin to collapsed sidebar expand button */
.history-bar.collapsed .history-header {
  justify-content: center;
  padding: var(--spacing-md) var(--collapsed-sidebar-margin);
}

/* Respect reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  .history-bar {
    transition: none;
  }
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--color-warm-dark);
  min-height: 56px;
}

.history-header h2 {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  white-space: nowrap;
}

.collapse-button {
  padding: var(--spacing-xs);
  background: transparent;
  border: 1px solid var(--color-warm-dark);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all 200ms ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  min-height: 32px;
  color: #1d1d1f;
}

.collapse-button:hover {
  background: rgba(0, 0, 0, 0.1);
  border-color: var(--color-warm-dark);
}

.collapse-button:focus-visible {
  outline: 2px solid var(--color-warm-dark);
  outline-offset: 2px;
}

.collapse-button .icon {
  font-size: 1.2rem;
  line-height: 1;
}

.button-container {
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 1px solid var(--color-warm-dark);
}

.new-conversation-btn {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: transparent;
  color: #1d1d1f;
  border: 1px solid var(--color-warm-dark);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: 500;
  transition: all 200ms ease;
}

.new-conversation-btn:hover {
  background-color: rgba(0, 0, 0, 0.1);
  border-color: var(--color-warm-dark);
}

.new-conversation-btn:active {
  background-color: rgba(0, 0, 0, 0.15);
  transform: translateY(1px);
}

.new-conversation-btn:focus-visible {
  outline: 2px solid var(--color-warm-dark);
  outline-offset: 2px;
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-warm-dark);
  cursor: pointer;
  transition: background-color 0.2s;
  color: #1d1d1f;
}

.conversation-item:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.conversation-item.active {
  background-color: var(--color-warm-dark);
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
  color: var(--color-warm-dark);
  font-size: var(--font-size-sm);
}
</style>
