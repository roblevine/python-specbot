# Research: Markdown Support

**Feature**: 017-markdown-support
**Date**: 2026-01-18
**Purpose**: Resolve technology choices for markdown rendering implementation

## Research Areas

1. Markdown parsing library selection
2. Syntax highlighting library selection
3. XSS sanitization approach
4. Vue 3 integration patterns
5. Streaming markdown rendering

---

## 1. Markdown Parsing Library

### Candidates Evaluated

| Library | Stars | Weekly Downloads | Size | GFM Support |
|---------|-------|------------------|------|-------------|
| marked | 32.1k | ~7M | 40KB | ✅ Yes |
| markdown-it | 17.4k | ~6M | 90KB | ✅ Via plugins |
| remark | 7k | ~3M | 200KB+ | ✅ Via plugins |

### Decision: **marked**

### Rationale

1. **Speed**: marked is optimized for browser performance with minimal overhead
2. **Simplicity**: Simple API (`marked.parse(text)`) requires no configuration for basic use
3. **GFM Support**: Native GitHub-Flavored Markdown support including tables, strikethrough, and task lists
4. **Size**: Smaller bundle size (40KB vs 90KB+) important for frontend
5. **Adoption**: Most downloaded markdown parser, well-maintained

### Alternatives Rejected

- **markdown-it**: More extensible but overkill for our needs. Steeper learning curve, plugin system adds complexity we don't need.
- **remark**: Full AST manipulation is unnecessary. Much larger bundle size with ecosystem dependencies.

### Sources

- [npm-compare: marked vs markdown-it](https://npm-compare.com/marked,markdown-it)
- [Marked Documentation](https://marked.js.org/)

---

## 2. Syntax Highlighting Library

### Candidates Evaluated

| Library | Stars | Bundle Size | Languages | Auto-detect |
|---------|-------|-------------|-----------|-------------|
| highlight.js | 24.7k | ~30KB core | 190+ | ✅ Yes |
| Prism | 12.8k | ~2KB core | 290+ | ❌ No |
| Shiki | 10k | ~50KB | VSCode themes | ❌ No |

### Decision: **highlight.js**

### Rationale

1. **Auto-detection**: Automatically detects language when not specified - critical for AI responses that may omit language hints
2. **Integration**: Works seamlessly with marked via custom renderer
3. **Tree-shaking**: Can import only needed languages to reduce bundle size
4. **Browser Support**: Works in browser without build-time processing
5. **Performance**: 9KB/ms parsing speed sufficient for real-time rendering

### Alternatives Rejected

- **Prism**: No automatic language detection. Would require all code blocks to specify language.
- **Shiki**: Build-time only, uses TextMate grammars requiring WASM. Overkill for runtime highlighting.

### Configuration

Import only required languages to minimize bundle:
```javascript
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import typescript from 'highlight.js/lib/languages/typescript'
// ... other languages from FR-004
hljs.registerLanguage('javascript', javascript)
```

### Sources

- [highlight.js vs Prism comparison](https://github.com/highlightjs/highlight.js/issues/3625)
- [Benchmark: highlight.js vs Prism](https://www.peterbe.com/plog/benchmark-compare-highlight.js-vs-prism)

---

## 3. XSS Sanitization

### Decision: **DOMPurify**

### Rationale

1. **Industry Standard**: Recommended by Marked documentation, developed by Cure53 security researchers
2. **DOM-based**: Uses browser's DOM parser for accurate sanitization (not regex-based)
3. **Default Security**: Blocks all event handlers, javascript: URLs, and dangerous tags by default
4. **Performance**: Super-fast, uber-tolerant sanitization
5. **Configurability**: Allows customization if needed (e.g., allowing specific tags)

### Integration Pattern

```javascript
import DOMPurify from 'dompurify'
import { marked } from 'marked'

function renderMarkdown(text) {
  const rawHtml = marked.parse(text)
  const cleanHtml = DOMPurify.sanitize(rawHtml)
  return cleanHtml
}
```

### Best Practices Applied

1. Sanitize at render time, not storage time
2. Use default configuration (maximally restrictive)
3. Combine with Content Security Policy as defense-in-depth
4. Keep DOMPurify updated for latest vulnerability patches

### Alternatives Rejected

- **sanitize-html**: Node.js focused, less browser-optimized
- **xss**: Older library, less actively maintained
- **Server-side only**: Client-side sanitization still needed for real-time rendering

### Sources

- [DOMPurify GitHub](https://github.com/cure53/DOMPurify)
- [Using Markdown Securely](https://neworbit.co.uk/using-markdown-securely/)

---

## 4. Vue 3 Integration Pattern

### Decision: Use `v-html` with sanitized content

### Rationale

Vue 3's `v-html` directive renders raw HTML. Combined with DOMPurify sanitization, this is safe and performant.

### Implementation Pattern

```vue
<template>
  <div
    class="message-text markdown-content"
    v-html="renderedContent"
  />
</template>

<script setup>
import { computed } from 'vue'
import { renderMarkdown } from '@/utils/markdownRenderer'

const props = defineProps({
  message: { type: Object, required: true }
})

const renderedContent = computed(() => {
  if (props.message.sender === 'user') {
    return escapeHtml(props.message.text) // Plain text for user messages
  }
  return renderMarkdown(props.message.text)
})
</script>
```

### Alternatives Rejected

- **vue-markdown**: Adds unnecessary Vue-specific wrapper, we control rendering ourselves
- **Teleport/Portal**: Not needed, rendering in place is sufficient
- **Custom directive**: Overkill, computed property is cleaner

---

## 5. Streaming Markdown Rendering

### Challenge

During SSE streaming, markdown arrives token-by-token. Incomplete markdown (e.g., unclosed code blocks) must render gracefully.

### Decision: Re-render on each token with graceful degradation

### Rationale

1. **marked handles incomplete markdown**: Unclosed blocks render as-is without breaking
2. **Performance acceptable**: Re-parsing ~5KB message takes <1ms
3. **No flicker**: Vue's DOM diffing prevents visual jumps
4. **Simplicity**: No complex partial parsing or buffering needed

### Implementation Strategy

```javascript
// In MessageBubble component
const renderedContent = computed(() => {
  // Re-computes on every message.text change (including streaming tokens)
  return renderMarkdown(props.message.text)
})
```

### Edge Case Handling

| Scenario | Behavior |
|----------|----------|
| Unclosed code block | Renders as code until closed |
| Unclosed bold `**text` | Renders asterisks as text |
| Partial table | Renders available rows |
| Split token mid-word | Renders partial word, completes on next token |

### Performance Optimization (if needed)

If streaming causes performance issues:
1. Debounce re-renders during rapid token receipt (100ms)
2. Only re-render code blocks when language tag completes

### Alternatives Rejected

- **Buffer until complete block**: Delays rendering, poor UX
- **Custom incremental parser**: Complex, unnecessary given marked's tolerance
- **Web Worker parsing**: Adds latency, DOM operations must be main thread anyway

---

## Summary of Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| Markdown Parser | marked | Speed, simplicity, GFM support |
| Syntax Highlighting | highlight.js | Auto-detection, browser-native |
| XSS Sanitization | DOMPurify | Industry standard, DOM-based |
| Vue Integration | v-html + computed | Simple, reactive, safe with sanitization |
| Streaming | Re-render each token | marked tolerates incomplete markdown |

## Dependencies to Add

```json
{
  "dependencies": {
    "marked": "^12.0.0",
    "dompurify": "^3.0.0",
    "highlight.js": "^11.9.0"
  }
}
```

## Open Questions Resolved

All technical unknowns from the plan have been resolved through this research. No NEEDS CLARIFICATION items remain.
