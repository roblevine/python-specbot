# Implementation Plan: Markdown Support

**Branch**: `017-markdown-support` | **Date**: 2026-01-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/017-markdown-support/spec.md`

## Summary

Implement markdown rendering for AI assistant messages in the chat application. This includes rendering standard markdown elements (headers, bold, italic, code blocks, lists, links, tables), syntax highlighting for code blocks, copy-to-clipboard functionality, and XSS sanitization. The implementation is frontend-only, modifying the MessageBubble component to render markdown instead of plain text.

## Technical Context

**Language/Version**: JavaScript ES6+ (Frontend)
**Primary Dependencies**: Vue 3.4.0, Vite 5.0.0, marked (markdown parser - to be added), DOMPurify (XSS sanitization - to be added), highlight.js (syntax highlighting - to be added)
**Storage**: N/A (no storage changes - markdown rendered at display time)
**Testing**: Vitest 1.0.0, @vue/test-utils 2.4.0, @testing-library/vue 8.0.0, Playwright 1.40.0
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend-only changes)
**Performance Goals**: Code blocks visually distinct within 0.5s of message receipt (SC-002)
**Constraints**: No visual glitches during streaming (SC-005), 100% XSS prevention (SC-006)
**Scale/Scope**: Single component modification (MessageBubble.vue) with supporting utilities

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | ✅ N/A | No API changes - frontend-only feature |
| II. Modular Architecture | ✅ Pass | Markdown rendering encapsulated in reusable utility/component |
| III. Test-First Development | ✅ Required | Tests must be written before implementation |
| IV. Integration & Contract Testing | ✅ N/A | No API changes - no contract tests needed |
| V. Observability & Debuggability | ✅ Pass | Error handling for malformed markdown with graceful degradation |
| VI. Simplicity & YAGNI | ✅ Pass | Using established libraries (marked, highlight.js) vs custom parser |
| VII. Versioning & Breaking Changes | ✅ N/A | No breaking changes - additive feature |
| VIII. Incremental Delivery | ✅ Required | P1 (basic rendering) → P2 (syntax highlighting) → P3 (copy button) |
| IX. Living Architecture Documentation | ✅ Required | Update architecture.md with new frontend dependencies |

**Architecture Documentation Update Required**: Yes - add markdown rendering dependencies to frontend technology stack section.

## Project Structure

### Documentation (this feature)

```text
specs/017-markdown-support/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # N/A - no API changes
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   └── ChatArea/
│   │       ├── MessageBubble.vue     # PRIMARY: Add markdown rendering
│   │       └── CodeBlock.vue         # NEW: Code block with copy button
│   ├── utils/
│   │   └── markdownRenderer.js       # NEW: Markdown parsing + sanitization
│   └── ...
├── public/
│   └── styles/
│       └── global.css                # ADD: Markdown element styles
└── tests/
    ├── unit/
    │   ├── MessageBubble.test.js     # MODIFY: Add markdown tests
    │   ├── CodeBlock.test.js         # NEW: Code block tests
    │   └── markdownRenderer.test.js  # NEW: Parser/sanitizer tests
    └── integration/
        └── markdown-streaming.test.js # NEW: Streaming markdown tests
```

**Structure Decision**: Web application - frontend-only changes. No backend modifications required. The markdown rendering will be implemented as a utility function with a supporting CodeBlock component for enhanced code display.

## Complexity Tracking

> No violations - using standard libraries and thin vertical slices.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Markdown Parser | marked library | Lightweight, fast, widely used, GFM support |
| Syntax Highlighting | highlight.js | Comprehensive language support, tree-shakeable |
| XSS Prevention | DOMPurify | Industry standard, well-maintained |
| Code Block Component | Separate component | Encapsulates copy button, language label, highlighting |

## Technical Decisions

### Markdown Line Break Handling

**Decision**: Use `breaks: false` in marked configuration

**Context**: The marked library has a `breaks` option that controls how single newlines are handled:
- `breaks: true` - Convert every `\n` to a `<br>` tag (GFM-style line breaks)
- `breaks: false` - Let standard markdown paragraph rules handle spacing (blank line = paragraph break)

**Problem with `breaks: true`**: When AI responses contain standard markdown with blank lines between sections, using `breaks: true` causes double-spacing because:
1. Single `\n` characters become `<br>` tags
2. Blank lines still create paragraph breaks (`<p>` tags)
3. CSS margins on `<p>`, `<ul>`, `<li>` elements add additional spacing
4. Result: excessive whitespace between all elements

**Rationale for `breaks: false`**:
- AI models output properly formatted markdown with blank lines for paragraph separation
- Standard markdown rules handle this correctly without manual intervention
- CSS margins provide consistent, predictable spacing
- Matches rendering behavior of other markdown viewers (GitHub, VS Code, etc.)

**Implementation**: In `frontend/src/utils/markdownRenderer.js`:
```javascript
marked.setOptions({
  gfm: true,
  breaks: false, // Let standard markdown paragraph rules handle spacing
})
```

### List Item Paragraph Margins

**Decision**: Remove paragraph margins inside list items

**Context**: When AI responses contain blank lines between list item content, the marked parser wraps list item content in `<p>` tags:

```html
<!-- AI writes markdown like: -->
- Item 1

- Item 2

<!-- Marked renders as: -->
<ul>
  <li><p>Item 1</p></li>
  <li><p>Item 2</p></li>
</ul>
```

**Problem**: The default `<p>` margin (`margin-bottom: 0.75em`) creates excessive spacing between list items because:
1. Each `<li>` already has `margin-bottom: 0.25em`
2. The `<p>` inside adds another `0.75em`
3. Result: ~1em spacing between items instead of expected ~0.25em

**Rationale for removing inner paragraph margins**:
- List items should have consistent, compact spacing regardless of whether they contain `<p>` tags
- Matches rendering behavior of GitHub markdown, VS Code, and other viewers
- The `<li>` element's margin provides sufficient visual separation

**Implementation**: In `frontend/public/styles/global.css`:
```css
/* Remove paragraph margins inside list items */
.markdown-content li > p {
  margin-bottom: 0.25em;
}

.markdown-content li > p:last-child {
  margin-bottom: 0;
}
```
