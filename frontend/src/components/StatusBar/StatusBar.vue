<template>
  <div
    class="status-bar"
    :class="statusClass"
  >
    <div class="status-bar-content">
      <div class="title-section">
        <span class="conversation-title">{{ title }}</span>
        <TitleMenu
          v-if="title !== 'New Conversation'"
          @rename="$emit('rename')"
        />
      </div>
      <div class="status-section">
        <div
          class="status-indicator"
          :class="`indicator-${statusType}`"
        />
        <span class="status-text">{{ status }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
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
    status: {
      type: String,
      default: 'Ready',
    },
    statusType: {
      type: String,
      default: 'ready',
      validator: value => ['ready', 'processing', 'error'].includes(value),
    },
  },
  emits: ['rename'],
  setup(props) {
    const statusClass = computed(() => ({
      'status-ready': props.statusType === 'ready',
      'status-processing': props.statusType === 'processing',
      'status-error': props.statusType === 'error',
    }))

    return {
      statusClass,
    }
  },
}
</script>

<style scoped>
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
  justify-content: space-between;
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

.status-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.indicator-ready {
  background-color: var(--color-success);
}

.indicator-processing {
  background-color: var(--color-warning);
  animation: pulse 1s ease-in-out infinite;
}

.indicator-error {
  background-color: var(--color-error);
}

.status-text {
  color: var(--color-text-secondary);
}

.status-error .status-text {
  color: var(--color-error);
  font-weight: 600;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}
</style>
