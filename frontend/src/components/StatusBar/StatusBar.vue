<template>
  <!-- Feature 015: Simplified StatusBar - status indicator removed -->
  <div class="status-bar">
    <div class="status-bar-content">
      <div class="title-section">
        <span class="conversation-title">{{ title }}</span>
        <TitleMenu
          v-if="title !== 'New Conversation'"
          @rename="$emit('rename')"
        />
      </div>
    </div>
  </div>
</template>

<script>
// Feature 015: Simplified StatusBar - status/statusType props removed
import TitleMenu from '../TitleMenu/TitleMenu.vue'

export default {
  name: 'StatusBar',
  components: {
    TitleMenu,
  },
  props: {
    title: {
      type: String,
      default: 'New Conversation',
    },
  },
  emits: ['rename'],
}
</script>

<style scoped>
/* Feature 015: Simplified StatusBar - status indicator styles removed */
.status-bar {
  display: flex;
  align-items: center;
  height: var(--status-bar-height);
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  font-size: var(--font-size-xs);
}

.status-bar-content {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: var(--chat-max-width);
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

.title-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
