<template>
  <div class="code-block">
    <!-- Language label -->
    <div
      v-if="language"
      class="code-block-header"
    >
      <span class="language-label">{{ language }}</span>
      <button
        type="button"
        class="copy-button"
        @click="copyToClipboard"
      >
        <span
          v-if="copied"
          class="copy-feedback"
        >
          <span class="copy-icon">&#10003;</span> Copied!
        </span>
        <span
          v-else
          class="copy-text"
        >
          <span class="copy-icon">&#128203;</span> Copy
        </span>
      </button>
    </div>
    <!-- Copy button only (no language) -->
    <div
      v-else
      class="code-block-header code-block-header-minimal"
    >
      <button
        type="button"
        class="copy-button"
        @click="copyToClipboard"
      >
        <span
          v-if="copied"
          class="copy-feedback"
        >
          <span class="copy-icon">&#10003;</span> Copied!
        </span>
        <span
          v-else
          class="copy-text"
        >
          <span class="copy-icon">&#128203;</span> Copy
        </span>
      </button>
    </div>
    <!-- Code content -->
    <pre class="code-content"><code v-html="highlightedCode" /></pre>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { hljs } from '../../utils/markdownRenderer.js'

export default {
  name: 'CodeBlock',
  props: {
    code: {
      type: String,
      required: true
    },
    language: {
      type: String,
      default: null
    }
  },
  setup(props) {
    const copied = ref(false)
    let copyTimeout = null

    // Compute highlighted code
    const highlightedCode = computed(() => {
      if (!props.code) return ''

      try {
        if (props.language && hljs.getLanguage(props.language)) {
          return hljs.highlight(props.code, { language: props.language }).value
        }
        // Auto-detect if no language
        return hljs.highlightAuto(props.code).value
      } catch (e) {
        // Fallback to plain escaped text
        return escapeHtml(props.code)
      }
    })

    // Escape HTML helper
    function escapeHtml(text) {
      const div = document.createElement('div')
      div.textContent = text
      return div.innerHTML
    }

    // Copy to clipboard with feedback
    async function copyToClipboard() {
      try {
        await navigator.clipboard.writeText(props.code)
        copied.value = true

        // Clear existing timeout
        if (copyTimeout) {
          clearTimeout(copyTimeout)
        }

        // Reset after 2 seconds
        copyTimeout = setTimeout(() => {
          copied.value = false
        }, 2000)
      } catch (err) {
        console.warn('Failed to copy to clipboard:', err)
        // Fallback: try execCommand (for older browsers)
        try {
          const textarea = document.createElement('textarea')
          textarea.value = props.code
          textarea.style.position = 'fixed'
          textarea.style.opacity = '0'
          document.body.appendChild(textarea)
          textarea.select()
          document.execCommand('copy')
          document.body.removeChild(textarea)
          copied.value = true
          copyTimeout = setTimeout(() => {
            copied.value = false
          }, 2000)
        } catch (fallbackErr) {
          console.error('Fallback copy failed:', fallbackErr)
        }
      }
    }

    return {
      copied,
      highlightedCode,
      copyToClipboard
    }
  }
}
</script>

<style scoped>
.code-block {
  position: relative;
  margin-bottom: 0.75em;
  border-radius: 6px;
  overflow: hidden;
  background: #1e1e1e;
}

.code-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5em 1em;
  background: #2d2d2d;
  border-bottom: 1px solid #3d3d3d;
}

.code-block-header-minimal {
  justify-content: flex-end;
}

.language-label {
  font-size: 0.75em;
  color: #858585;
  text-transform: lowercase;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

.copy-button {
  display: flex;
  align-items: center;
  gap: 0.25em;
  padding: 0.25em 0.5em;
  font-size: 0.75em;
  color: #858585;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

.copy-button:hover {
  color: #d4d4d4;
  background: #3d3d3d;
  border-color: #4d4d4d;
}

.copy-button:active {
  background: #4d4d4d;
}

.copy-icon {
  font-size: 1em;
}

.copy-feedback {
  color: #4ade80;
}

.copy-text {
  display: flex;
  align-items: center;
  gap: 0.25em;
}

.code-content {
  margin: 0;
  padding: 1em;
  overflow-x: auto;
  color: #d4d4d4;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 0.875em;
  line-height: 1.5;
}

.code-content code {
  background: transparent;
  padding: 0;
  font-family: inherit;
  font-size: inherit;
}
</style>
