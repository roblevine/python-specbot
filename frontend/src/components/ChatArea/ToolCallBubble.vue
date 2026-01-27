<template>
  <div
    class="tool-call-bubble"
    :class="statusClass"
    :data-tool-id="toolCall.id"
    :data-status="toolCall.status"
  >
    <!-- Collapsed header - always visible -->
    <button
      class="tool-header"
      :aria-expanded="isExpanded"
      :aria-controls="`tool-details-${toolCall.id}`"
      @click="toggleExpanded"
      @keydown.enter.space.prevent="toggleExpanded"
    >
      <!-- Tool icon -->
      <span class="tool-icon">{{ toolIcon }}</span>

      <!-- Tool name -->
      <span class="tool-name">{{ toolCall.toolName }}</span>

      <!-- Status indicator -->
      <span
        class="status-indicator"
        :class="statusClass"
      >
        <span
          v-if="toolCall.status === 'pending'"
          class="status-pending"
        >
          <span class="spinner" />
          Running...
        </span>
        <span
          v-else-if="toolCall.status === 'success'"
          class="status-success"
        >
          ✓ Completed
        </span>
        <span
          v-else-if="toolCall.status === 'error'"
          class="status-error"
        >
          ✗ Failed
        </span>
      </span>

      <!-- Duration (if available) -->
      <span
        v-if="toolCall.durationMs"
        class="tool-duration"
      >
        {{ formatDuration(toolCall.durationMs) }}
      </span>

      <!-- Expand/collapse arrow -->
      <span
        class="expand-arrow"
        :class="{ expanded: isExpanded }"
      >
        ▼
      </span>
    </button>

    <!-- Expandable details section -->
    <transition name="expand">
      <div
        v-if="isExpanded"
        :id="`tool-details-${toolCall.id}`"
        class="tool-details"
      >
        <!-- Arguments section -->
        <div
          v-if="hasArgs"
          class="tool-section"
        >
          <div class="section-label">
            Arguments:
          </div>
          <pre class="tool-args">{{ formatArgs }}</pre>
        </div>

        <!-- Result section (success) -->
        <div
          v-if="toolCall.status === 'success' && toolCall.result"
          class="tool-section"
        >
          <div class="section-label">
            Result:
          </div>
          <div class="tool-result">
            {{ truncatedResult }}
          </div>
        </div>

        <!-- Links section (if available) -->
        <div
          v-if="hasLinks"
          class="tool-section"
        >
          <div class="section-label">
            Sources:
          </div>
          <ul class="tool-links">
            <li
              v-for="(link, idx) in toolCall.resultLinks"
              :key="idx"
              class="link-item"
            >
              <a
                :href="link.url"
                target="_blank"
                rel="noopener noreferrer"
                class="link-title"
              >
                {{ link.title }}
              </a>
              <span
                v-if="link.snippet"
                class="link-snippet"
              >{{ truncateText(link.snippet, 100) }}</span>
            </li>
          </ul>
        </div>

        <!-- Error section -->
        <div
          v-if="toolCall.status === 'error' && toolCall.error"
          class="tool-section error-section"
        >
          <div class="section-label">
            Error:
          </div>
          <div class="tool-error">
            {{ toolCall.error }}
          </div>
        </div>

        <!-- Debug info section (if available) -->
        <div
          v-if="toolCall.debugInfo"
          class="tool-section debug-section"
        >
          <div class="section-label">
            Debug Information:
          </div>
          <pre class="debug-info">{{ formatDebugInfo }}</pre>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'ToolCallBubble',
  props: {
    toolCall: {
      type: Object,
      required: true,
      validator: tc => {
        return tc.id && tc.toolId && tc.toolName && tc.status
      }
    }
  },
  setup(props) {
    const isExpanded = ref(false)

    const toggleExpanded = () => {
      isExpanded.value = !isExpanded.value
    }

    const statusClass = computed(() => {
      return `status-${props.toolCall.status}`
    })

    const toolIcon = computed(() => {
      // Map tool IDs to icons
      const icons = {
        'duckduckgo-search': '🔍',
        'web-browser': '🌐',
        'web_search': '🔍',
        'browse_url': '🌐'
      }
      return icons[props.toolCall.toolId] || '🔧'
    })

    const hasArgs = computed(() => {
      return props.toolCall.args && Object.keys(props.toolCall.args).length > 0
    })

    const formatArgs = computed(() => {
      if (!props.toolCall.args) return ''
      return JSON.stringify(props.toolCall.args, null, 2)
    })

    const hasLinks = computed(() => {
      return props.toolCall.resultLinks && props.toolCall.resultLinks.length > 0
    })

    const truncatedResult = computed(() => {
      if (!props.toolCall.result) return ''
      const maxLength = 500
      if (props.toolCall.result.length <= maxLength) {
        return props.toolCall.result
      }
      return props.toolCall.result.substring(0, maxLength) + '...'
    })

    const formatDebugInfo = computed(() => {
      if (!props.toolCall.debugInfo) return ''
      return JSON.stringify(props.toolCall.debugInfo, null, 2)
    })

    const formatDuration = (ms) => {
      if (ms < 1000) return `${ms}ms`
      return `${(ms / 1000).toFixed(1)}s`
    }

    const truncateText = (text, maxLength) => {
      if (!text || text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }

    return {
      isExpanded,
      toggleExpanded,
      statusClass,
      toolIcon,
      hasArgs,
      formatArgs,
      hasLinks,
      truncatedResult,
      formatDebugInfo,
      formatDuration,
      truncateText
    }
  }
}
</script>

<style scoped>
.tool-call-bubble {
  margin: 8px 0;
  border-radius: 8px;
  background-color: var(--color-bg-tertiary, #f5f5f5);
  border: 1px solid var(--color-border, #e0e0e0);
  overflow: hidden;
  font-size: 0.875rem;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  color: var(--color-text-primary, #333);
  font-family: inherit;
  font-size: 0.875rem;
}

.tool-header:hover {
  background-color: var(--color-bg-hover, rgba(0, 0, 0, 0.05));
}

.tool-header:focus {
  outline: 2px solid var(--color-primary, #007bff);
  outline-offset: -2px;
}

.tool-icon {
  font-size: 1.1rem;
}

.tool-name {
  font-weight: 500;
  flex-grow: 1;
}

.status-indicator {
  font-size: 0.75rem;
}

.status-pending {
  color: var(--color-warning, #f0ad4e);
  display: flex;
  align-items: center;
  gap: 4px;
}

.spinner {
  display: inline-block;
  width: 10px;
  height: 10px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.status-success {
  color: var(--color-success, #28a745);
}

.status-error {
  color: var(--color-error, #dc3545);
}

.tool-duration {
  font-size: 0.7rem;
  color: var(--color-text-muted, #888);
}

.expand-arrow {
  font-size: 0.7rem;
  color: var(--color-text-muted, #888);
  transition: transform 0.2s ease;
}

.expand-arrow.expanded {
  transform: rotate(180deg);
}

/* Status-specific bubble styling */
.tool-call-bubble.status-pending {
  border-color: var(--color-warning, #f0ad4e);
}

.tool-call-bubble.status-success {
  border-color: var(--color-success, #28a745);
}

.tool-call-bubble.status-error {
  border-color: var(--color-error, #dc3545);
}

/* Details section */
.tool-details {
  padding: 12px;
  border-top: 1px solid var(--color-border, #e0e0e0);
  background-color: var(--color-bg-secondary, #fafafa);
}

.tool-section {
  margin-bottom: 12px;
}

.tool-section:last-child {
  margin-bottom: 0;
}

.section-label {
  font-weight: 500;
  font-size: 0.75rem;
  color: var(--color-text-muted, #888);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tool-args {
  background-color: var(--color-bg-tertiary, #f0f0f0);
  padding: 8px;
  border-radius: 4px;
  font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
  font-size: 0.75rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}

.tool-result {
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--color-text-primary, #333);
  line-height: 1.5;
}

.tool-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.link-item {
  margin-bottom: 8px;
  padding: 6px 8px;
  background-color: var(--color-bg-tertiary, #f0f0f0);
  border-radius: 4px;
}

.link-title {
  color: var(--color-primary, #007bff);
  text-decoration: none;
  font-weight: 500;
  display: block;
}

.link-title:hover {
  text-decoration: underline;
}

.link-snippet {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-muted, #888);
  margin-top: 2px;
}

.tool-error {
  color: var(--color-error, #dc3545);
  font-weight: 500;
}

.error-section {
  background-color: rgba(220, 53, 69, 0.1);
  padding: 8px;
  border-radius: 4px;
}

.debug-section {
  background-color: rgba(108, 117, 125, 0.1);
  padding: 8px;
  border-radius: 4px;
}

.debug-info {
  background-color: var(--color-bg-tertiary, #f0f0f0);
  padding: 8px;
  border-radius: 4px;
  font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
  font-size: 0.7rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  color: var(--color-text-muted, #666);
}

/* Expand transition */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}
</style>
