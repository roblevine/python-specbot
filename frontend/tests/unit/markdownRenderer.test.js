/**
 * Unit tests for markdownRenderer utility - Feature 017
 *
 * Tests cover:
 * - Basic markdown rendering (T004)
 * - XSS sanitization (FR-002, SC-006)
 * - Malformed markdown handling
 * - Syntax highlighting (T013)
 * - HTML escaping for user messages
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { renderMarkdown, escapeHtml, hljs } from '../../src/utils/markdownRenderer.js'

describe('markdownRenderer', () => {
  describe('renderMarkdown - Basic Markdown', () => {
    it('should return empty string for null input', () => {
      expect(renderMarkdown(null)).toBe('')
    })

    it('should return empty string for undefined input', () => {
      expect(renderMarkdown(undefined)).toBe('')
    })

    it('should return empty string for empty string input', () => {
      expect(renderMarkdown('')).toBe('')
    })

    it('should render plain text as paragraph', () => {
      const result = renderMarkdown('Hello world')
      expect(result).toContain('Hello world')
    })

    it('should render headers correctly', () => {
      expect(renderMarkdown('# Heading 1')).toContain('<h1')
      expect(renderMarkdown('## Heading 2')).toContain('<h2')
      expect(renderMarkdown('### Heading 3')).toContain('<h3')
    })

    it('should render bold text', () => {
      const result = renderMarkdown('**bold text**')
      expect(result).toContain('<strong>bold text</strong>')
    })

    it('should render italic text', () => {
      const result = renderMarkdown('*italic text*')
      expect(result).toContain('<em>italic text</em>')
    })

    it('should render inline code', () => {
      const result = renderMarkdown('Use `const` keyword')
      expect(result).toContain('<code>const</code>')
    })

    it('should render unordered lists', () => {
      const result = renderMarkdown('- Item 1\n- Item 2\n- Item 3')
      expect(result).toContain('<ul>')
      expect(result).toContain('<li>')
      expect(result).toContain('Item 1')
    })

    it('should render ordered lists', () => {
      const result = renderMarkdown('1. First\n2. Second\n3. Third')
      expect(result).toContain('<ol>')
      expect(result).toContain('<li>')
    })

    it('should render links', () => {
      const result = renderMarkdown('[Google](https://google.com)')
      expect(result).toContain('<a href="https://google.com"')
      expect(result).toContain('Google</a>')
    })

    it('should render blockquotes', () => {
      const result = renderMarkdown('> This is a quote')
      expect(result).toContain('<blockquote>')
    })

    it('should render tables (GFM)', () => {
      const table = `
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
`
      const result = renderMarkdown(table)
      expect(result).toContain('<table>')
      expect(result).toContain('<th>')
      expect(result).toContain('<td>')
    })

    it('should render code blocks', () => {
      const result = renderMarkdown('```\ncode here\n```')
      expect(result).toContain('<pre>')
      expect(result).toContain('<code')
    })

    it('should NOT convert single line breaks to <br> (breaks: false)', () => {
      // With breaks: false, single newlines within a paragraph are treated as
      // soft line breaks (space), not <br> tags. This prevents double-spacing
      // when AI responses have standard markdown formatting.
      // See plan.md "Technical Decisions" for rationale.
      const result = renderMarkdown('Line 1\nLine 2')
      expect(result).not.toContain('<br')
      expect(result).toContain('Line 1')
      expect(result).toContain('Line 2')
    })

    it('should create separate paragraphs with blank lines', () => {
      // Blank lines (double newline) should create separate paragraphs
      const result = renderMarkdown('Paragraph 1\n\nParagraph 2')
      // Should have two <p> tags (or the content in separate blocks)
      expect(result).toContain('Paragraph 1')
      expect(result).toContain('Paragraph 2')
    })
  })

  describe('renderMarkdown - XSS Sanitization (FR-002, SC-006)', () => {
    it('should sanitize script tags', () => {
      const result = renderMarkdown('<script>alert("XSS")</script>')
      expect(result).not.toContain('<script>')
      expect(result).not.toContain('alert')
    })

    it('should sanitize onclick handlers', () => {
      const result = renderMarkdown('<div onclick="alert(1)">Click me</div>')
      expect(result).not.toContain('onclick')
    })

    it('should sanitize javascript: URLs', () => {
      const result = renderMarkdown('[Click](javascript:alert(1))')
      expect(result).not.toContain('javascript:')
    })

    it('should sanitize onerror handlers', () => {
      const result = renderMarkdown('<img src="x" onerror="alert(1)">')
      expect(result).not.toContain('onerror')
    })

    it('should sanitize data: URLs with scripts', () => {
      const result = renderMarkdown('<a href="data:text/html,<script>alert(1)</script>">Link</a>')
      expect(result).not.toContain('data:text/html')
    })

    it('should not render onclick in valid anchor tags', () => {
      // Test actual HTML injection, not malformed markdown
      const malicious = '<a href="https://example.com" onclick="alert(1)">Click</a>'
      const result = renderMarkdown(malicious)
      expect(result).not.toContain('onclick')
    })

    it('should handle nested script attempts', () => {
      const result = renderMarkdown('<scr<script>ipt>alert(1)</scr</script>ipt>')
      expect(result).not.toContain('<script>')
    })

    it('should sanitize SVG with embedded scripts', () => {
      const result = renderMarkdown('<svg onload="alert(1)"><circle r="10"/></svg>')
      expect(result).not.toContain('onload')
    })

    it('should preserve safe HTML attributes', () => {
      const result = renderMarkdown('```javascript\nconst x = 1;\n```')
      // Should contain class attribute for highlight.js
      expect(result).toContain('class=')
    })
  })

  describe('renderMarkdown - Malformed Markdown', () => {
    it('should handle unclosed bold markers', () => {
      const result = renderMarkdown('This is **bold text without closing')
      expect(result).toContain('bold text without closing')
      // Should not crash
    })

    it('should handle unclosed code blocks', () => {
      const result = renderMarkdown('```javascript\nconst x = 1;')
      // With syntax highlighting, the code is wrapped in spans
      // Just verify the code block is rendered and contains the code
      expect(result).toContain('<pre>')
      expect(result).toContain('<code')
      expect(result).toContain('const')
      expect(result).toContain('x')
      // Should not crash
    })

    it('should handle unclosed inline code', () => {
      const result = renderMarkdown('Use `const without closing')
      expect(result).toContain('const')
    })

    it('should handle nested unclosed markers', () => {
      const result = renderMarkdown('**bold *and italic')
      expect(result).toBeDefined()
    })

    it('should handle incomplete tables', () => {
      const result = renderMarkdown('| Header |\n|---')
      expect(result).toBeDefined()
    })

    it('should handle extremely long input', () => {
      const longText = 'a'.repeat(100000)
      const result = renderMarkdown(longText)
      expect(result).toContain('a')
    })

    it('should handle mixed valid and invalid markdown', () => {
      const mixed = '# Valid Header\n<script>bad</script>\n**bold**'
      const result = renderMarkdown(mixed)
      expect(result).toContain('<h1')
      expect(result).toContain('<strong>bold</strong>')
      expect(result).not.toContain('<script>')
    })
  })

  describe('renderMarkdown - Syntax Highlighting (T013)', () => {
    it('should highlight JavaScript code with specified language', () => {
      const code = '```javascript\nconst x = 1;\n```'
      const result = renderMarkdown(code)
      // highlight.js adds hljs class and span elements for tokens
      expect(result).toContain('hljs')
      expect(result).toContain('<span')
    })

    it('should highlight Python code', () => {
      const code = '```python\ndef hello():\n    print("Hello")\n```'
      const result = renderMarkdown(code)
      expect(result).toContain('hljs')
    })

    it('should highlight TypeScript code', () => {
      const code = '```typescript\nconst x: number = 1;\n```'
      const result = renderMarkdown(code)
      expect(result).toContain('hljs')
    })

    it('should handle language alias js for javascript', () => {
      const code = '```js\nconst x = 1;\n```'
      const result = renderMarkdown(code)
      expect(result).toContain('hljs')
    })

    it('should handle language alias py for python', () => {
      const code = '```py\ndef test(): pass\n```'
      const result = renderMarkdown(code)
      expect(result).toContain('hljs')
    })

    it('should handle language alias ts for typescript', () => {
      const code = '```ts\nconst x: string = "hello";\n```'
      const result = renderMarkdown(code)
      expect(result).toContain('hljs')
    })

    it('should handle language alias sh for bash', () => {
      const code = '```sh\necho "hello"\n```'
      const result = renderMarkdown(code)
      expect(result).toContain('hljs')
    })

    it('should auto-detect language when not specified', () => {
      // Code block without language
      const code = '```\nfunction hello() { return 1; }\n```'
      const result = renderMarkdown(code)
      // Should still add hljs class even with auto-detection
      expect(result).toContain('hljs')
    })

    it('should handle unknown language gracefully', () => {
      const code = '```unknownlang\nsome code\n```'
      const result = renderMarkdown(code)
      // Should not crash, should still render code block
      expect(result).toContain('<pre>')
      expect(result).toContain('<code')
    })

    it('should add language class to code block', () => {
      const code = '```javascript\nconst x = 1;\n```'
      const result = renderMarkdown(code)
      expect(result).toContain('language-javascript')
    })

    it('should highlight JSON', () => {
      const code = '```json\n{"key": "value"}\n```'
      const result = renderMarkdown(code)
      expect(result).toContain('hljs')
    })

    it('should highlight CSS', () => {
      const code = '```css\n.class { color: red; }\n```'
      const result = renderMarkdown(code)
      expect(result).toContain('hljs')
    })

    it('should highlight HTML via xml alias', () => {
      const code = '```html\n<div>Hello</div>\n```'
      const result = renderMarkdown(code)
      expect(result).toContain('hljs')
    })

    it('should highlight SQL', () => {
      const code = '```sql\nSELECT * FROM users;\n```'
      const result = renderMarkdown(code)
      expect(result).toContain('hljs')
    })

    it('should highlight Bash', () => {
      const code = '```bash\necho "Hello World"\n```'
      const result = renderMarkdown(code)
      expect(result).toContain('hljs')
    })

    it('should highlight Markdown', () => {
      const code = '```markdown\n# Title\n**bold**\n```'
      const result = renderMarkdown(code)
      expect(result).toContain('hljs')
    })
  })

  describe('escapeHtml', () => {
    it('should return empty string for null input', () => {
      expect(escapeHtml(null)).toBe('')
    })

    it('should return empty string for undefined input', () => {
      expect(escapeHtml(undefined)).toBe('')
    })

    it('should return empty string for empty string input', () => {
      expect(escapeHtml('')).toBe('')
    })

    it('should escape < and > characters', () => {
      const result = escapeHtml('<script>alert(1)</script>')
      expect(result).not.toContain('<script>')
      expect(result).toContain('&lt;script&gt;')
    })

    it('should escape & character', () => {
      const result = escapeHtml('Tom & Jerry')
      expect(result).toBe('Tom &amp; Jerry')
    })

    it('should preserve " character in text content', () => {
      // Note: textContent/innerHTML doesn't escape quotes since they're
      // only dangerous in attribute contexts, not text content
      const result = escapeHtml('Say "Hello"')
      expect(result).toBe('Say "Hello"')
    })

    it('should preserve plain text', () => {
      const result = escapeHtml('Hello world')
      expect(result).toBe('Hello world')
    })

    it('should handle multiple special characters', () => {
      const result = escapeHtml('<a href="test?x=1&y=2">Link</a>')
      expect(result).toContain('&lt;a')
      expect(result).toContain('&amp;')
    })

    it('should preserve unicode characters', () => {
      const result = escapeHtml('Hello 世界 🚀')
      expect(result).toBe('Hello 世界 🚀')
    })

    it('should handle newlines', () => {
      const result = escapeHtml('Line 1\nLine 2')
      expect(result).toBe('Line 1\nLine 2')
    })
  })

  describe('hljs export', () => {
    it('should export hljs for external use', () => {
      expect(hljs).toBeDefined()
    })

    it('should have registered languages', () => {
      expect(hljs.getLanguage('javascript')).toBeDefined()
      expect(hljs.getLanguage('python')).toBeDefined()
      expect(hljs.getLanguage('typescript')).toBeDefined()
      expect(hljs.getLanguage('bash')).toBeDefined()
      expect(hljs.getLanguage('json')).toBeDefined()
      expect(hljs.getLanguage('css')).toBeDefined()
      expect(hljs.getLanguage('xml')).toBeDefined()
      expect(hljs.getLanguage('sql')).toBeDefined()
      expect(hljs.getLanguage('markdown')).toBeDefined()
    })

    it('should have registered language aliases', () => {
      expect(hljs.getLanguage('js')).toBeDefined()
      expect(hljs.getLanguage('ts')).toBeDefined()
      expect(hljs.getLanguage('py')).toBeDefined()
      expect(hljs.getLanguage('sh')).toBeDefined()
      expect(hljs.getLanguage('html')).toBeDefined()
      expect(hljs.getLanguage('md')).toBeDefined()
    })
  })
})
