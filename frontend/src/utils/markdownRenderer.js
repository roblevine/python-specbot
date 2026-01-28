/**
 * Markdown Renderer Utility - Feature 017
 *
 * Renders markdown text to sanitized HTML with syntax highlighting.
 * Used for AI assistant messages in the chat application.
 *
 * @module utils/markdownRenderer
 */

import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js/lib/core'

// Import only needed languages (FR-004) - tree-shaking for bundle size
import javascript from 'highlight.js/lib/languages/javascript'
import typescript from 'highlight.js/lib/languages/typescript'
import python from 'highlight.js/lib/languages/python'
import bash from 'highlight.js/lib/languages/bash'
import json from 'highlight.js/lib/languages/json'
import css from 'highlight.js/lib/languages/css'
import xml from 'highlight.js/lib/languages/xml' // includes HTML
import sql from 'highlight.js/lib/languages/sql'
import markdown from 'highlight.js/lib/languages/markdown'

// Register languages with primary names
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('json', json)
hljs.registerLanguage('css', css)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('sql', sql)
hljs.registerLanguage('markdown', markdown)

// Register language aliases (FR-004)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('ts', typescript)
hljs.registerLanguage('py', python)
hljs.registerLanguage('sh', bash)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('md', markdown)

// Configure marked with syntax highlighting
// Note: breaks: false lets standard markdown paragraph rules handle spacing
// See plan.md "Technical Decisions" for rationale (fixes double-spacing issue)
marked.setOptions({
  gfm: true, // GitHub Flavored Markdown (tables, strikethrough)
  breaks: false, // Let paragraph rules handle spacing (not \n → <br>)
})

// Custom renderer for code blocks with syntax highlighting
const renderer = new marked.Renderer()

renderer.code = function (code, language) {
  // Handle object input from newer marked versions
  let codeText = typeof code === 'object' ? code.text : code
  let lang = typeof code === 'object' ? code.lang : language

  // Normalize language
  if (lang) {
    lang = lang.toLowerCase().trim()
  }

  let highlightedCode
  try {
    if (lang && hljs.getLanguage(lang)) {
      // Use specified language
      highlightedCode = hljs.highlight(codeText, { language: lang }).value
    } else {
      // Auto-detect if no language specified or unknown language
      highlightedCode = hljs.highlightAuto(codeText).value
    }
  } catch (e) {
    // Fallback to escaped plain text on error
    highlightedCode = escapeHtml(codeText)
  }

  // Build the code block HTML with language class for potential future styling
  const langClass = lang ? ` language-${lang}` : ''
  return `<pre><code class="hljs${langClass}">${highlightedCode}</code></pre>`
}

marked.use({ renderer })

/**
 * Render markdown text to sanitized HTML
 *
 * @param {string} text - Raw markdown text
 * @returns {string} - Sanitized HTML safe for v-html
 */
export function renderMarkdown(text) {
  if (!text) return ''

  try {
    // Parse markdown to HTML
    const rawHtml = marked.parse(text)

    // Sanitize to prevent XSS (FR-002, SC-006)
    const cleanHtml = DOMPurify.sanitize(rawHtml, {
      // Allow highlight.js classes and link attributes
      ADD_ATTR: ['class', 'target', 'rel'],
    })

    return cleanHtml
  } catch (e) {
    // Graceful degradation on error - return escaped text
    console.warn('Markdown rendering failed:', e)
    return escapeHtml(text)
  }
}

/**
 * Escape HTML for plain text display (user messages)
 *
 * Uses the browser's built-in escaping via textContent/innerHTML
 * which handles all HTML entities correctly.
 *
 * @param {string} text - Raw text
 * @returns {string} - Escaped HTML safe for v-html or direct insertion
 */
export function escapeHtml(text) {
  if (!text) return ''

  // Use DOM to properly escape HTML entities
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// Export hljs for potential direct use (e.g., testing)
export { hljs }
