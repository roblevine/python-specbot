# Quickstart: Markdown Support

**Feature**: 017-markdown-support
**Date**: 2026-01-18

## Prerequisites

- Node.js 18+ installed
- Frontend development server running (`npm run dev` in `/frontend`)
- Familiarity with Vue 3 Composition API

## Quick Setup

### 1. Install Dependencies

```bash
cd frontend
npm install marked dompurify highlight.js
```

### 2. Create Markdown Renderer Utility

Create `frontend/src/utils/markdownRenderer.js`:

```javascript
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js/lib/core'

// Import only needed languages (FR-004)
import javascript from 'highlight.js/lib/languages/javascript'
import typescript from 'highlight.js/lib/languages/typescript'
import python from 'highlight.js/lib/languages/python'
import bash from 'highlight.js/lib/languages/bash'
import json from 'highlight.js/lib/languages/json'
import css from 'highlight.js/lib/languages/css'
import xml from 'highlight.js/lib/languages/xml' // includes HTML
import sql from 'highlight.js/lib/languages/sql'
import markdown from 'highlight.js/lib/languages/markdown'

// Register languages
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('ts', typescript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('py', python)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('sh', bash)
hljs.registerLanguage('json', json)
hljs.registerLanguage('css', css)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('sql', sql)
hljs.registerLanguage('markdown', markdown)
hljs.registerLanguage('md', markdown)

// Configure marked with syntax highlighting
marked.setOptions({
  gfm: true, // GitHub Flavored Markdown (tables, strikethrough)
  breaks: true, // Convert \n to <br>
  highlight: (code, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    // Auto-detect if no language specified
    return hljs.highlightAuto(code).value
  }
})

/**
 * Render markdown text to sanitized HTML
 * @param {string} text - Raw markdown text
 * @returns {string} - Sanitized HTML
 */
export function renderMarkdown(text) {
  if (!text) return ''

  const rawHtml = marked.parse(text)
  const cleanHtml = DOMPurify.sanitize(rawHtml)

  return cleanHtml
}

/**
 * Escape HTML for plain text display (user messages)
 * @param {string} text - Raw text
 * @returns {string} - Escaped HTML
 */
export function escapeHtml(text) {
  if (!text) return ''

  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}
```

### 3. Update MessageBubble Component

Modify `frontend/src/components/ChatArea/MessageBubble.vue`:

```vue
<template>
  <div :class="messageClasses">
    <!-- For system (assistant) messages: render markdown -->
    <div
      v-if="message.sender === 'system'"
      class="message-text markdown-content"
      v-html="renderedContent"
    />
    <!-- For user messages: plain text -->
    <div
      v-else
      class="message-text"
    >
      {{ message.text }}
    </div>
    <!-- ... rest of template ... -->
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { renderMarkdown } from '@/utils/markdownRenderer'

const props = defineProps({
  message: { type: Object, required: true }
})

const renderedContent = computed(() => {
  return renderMarkdown(props.message.text)
})

// ... rest of script ...
</script>
```

### 4. Add Markdown Styles

Add to `frontend/public/styles/global.css`:

```css
/* Markdown Content Styles */
.markdown-content {
  line-height: 1.6;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  margin-top: 1em;
  margin-bottom: 0.5em;
  font-weight: 600;
}

.markdown-content p {
  margin-bottom: 0.75em;
}

.markdown-content ul,
.markdown-content ol {
  margin-left: 1.5em;
  margin-bottom: 0.75em;
}

.markdown-content code {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 0.9em;
  background: rgba(0, 0, 0, 0.05);
  padding: 0.2em 0.4em;
  border-radius: 3px;
}

.markdown-content pre {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 1em;
  border-radius: 6px;
  overflow-x: auto;
  margin-bottom: 0.75em;
}

.markdown-content pre code {
  background: transparent;
  padding: 0;
  font-size: 0.875em;
}

.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 0.75em;
}

.markdown-content th,
.markdown-content td {
  border: 1px solid var(--color-warm-tan);
  padding: 0.5em 0.75em;
  text-align: left;
}

.markdown-content th {
  background: var(--color-warm-cream);
  font-weight: 600;
}

.markdown-content a {
  color: var(--color-warm-brown);
  text-decoration: underline;
}

.markdown-content blockquote {
  border-left: 3px solid var(--color-warm-tan);
  margin-left: 0;
  padding-left: 1em;
  color: #666;
}
```

### 5. Import highlight.js Theme

Add to `frontend/src/index.js` or component:

```javascript
import 'highlight.js/styles/vs2015.css' // Dark theme for code blocks
```

## Verification

### Manual Testing

1. Start the dev server: `npm run dev`
2. Send a message that triggers AI response with markdown
3. Verify:
   - Code blocks have dark background and syntax highlighting
   - Bold/italic text renders correctly
   - Lists have proper indentation
   - Tables render with borders
   - Links are clickable

### Test Prompts

Use these prompts to test markdown rendering:

```
Show me a Python hello world example with explanation
```

```
Create a comparison table of JavaScript vs Python
```

```
Explain the difference between let, const, and var with code examples
```

## Implementation Order (Thin Slices)

Follow the constitution's incremental delivery principle:

### Slice 1: Basic Markdown (P1 - MVP)
1. Install dependencies
2. Create `markdownRenderer.js` utility
3. Update `MessageBubble.vue` to use `v-html`
4. Add basic CSS for markdown elements
5. **Test & Commit**

### Slice 2: Syntax Highlighting (P2)
1. Configure highlight.js with language imports
2. Add highlight.js CSS theme
3. Style code blocks (dark theme, scrolling)
4. **Test & Commit**

### Slice 3: Copy Button (P3)
1. Create `CodeBlock.vue` component
2. Add copy button with clipboard API
3. Add visual feedback (copied state)
4. **Test & Commit**

## Troubleshooting

### Code blocks not highlighting
- Check language is registered in `markdownRenderer.js`
- Verify highlight.js CSS is imported
- Check browser console for errors

### XSS warning in console
- Ensure DOMPurify is correctly sanitizing output
- Check that `v-html` is only used with sanitized content

### Streaming causes flicker
- Vue's reactivity should handle this automatically
- If issues persist, consider debouncing the computed property

## Related Files

| File | Purpose |
|------|---------|
| `src/utils/markdownRenderer.js` | Markdown parsing + sanitization |
| `src/components/ChatArea/MessageBubble.vue` | Message display |
| `src/components/ChatArea/CodeBlock.vue` | Code block with copy (P3) |
| `public/styles/global.css` | Markdown element styles |
| `tests/unit/markdownRenderer.test.js` | Unit tests |
