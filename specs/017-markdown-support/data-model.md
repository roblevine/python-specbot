# Data Model: Markdown Support

**Feature**: 017-markdown-support
**Date**: 2026-01-18

## Overview

This feature is **frontend-only** and does not modify the existing data model. Markdown rendering occurs at display time - the raw message text is stored unchanged, and rendering transforms it to HTML for display.

## Existing Entities (Unchanged)

### Message

The existing message entity remains unchanged. Markdown is rendered from the `text` field.

```typescript
interface Message {
  id: string              // Unique identifier (e.g., "msg-xxxxx")
  text: string            // Raw content - may contain markdown
  sender: 'user' | 'system'  // Message source
  timestamp: string       // ISO8601 timestamp
  status: 'pending' | 'sent' | 'error' | 'streaming'
  model?: string          // Optional: model that generated response
  errorMessage?: string   // Error details (error status only)
  errorType?: string      // Error classification
  errorDetails?: string   // Additional error context
}
```

**Markdown Rendering Rule**: Only messages with `sender === 'system'` are rendered as markdown. User messages (`sender === 'user'`) display as plain text to preserve exact input.

## New Rendering Concepts (Frontend Only)

These are not persisted - they exist only during rendering.

### RenderedMarkdown

Computed result of markdown parsing and sanitization.

```typescript
interface RenderedMarkdown {
  html: string            // Sanitized HTML output
  codeBlocks: CodeBlock[] // Extracted code blocks for enhanced rendering
}
```

### CodeBlock

Represents a fenced code block within a message for enhanced rendering (syntax highlighting, copy button).

```typescript
interface CodeBlock {
  id: string              // Unique ID within message (for copy button state)
  language: string | null // Language hint (e.g., "python", "javascript", null)
  content: string         // Raw code content (for clipboard copy)
  highlightedHtml: string // Syntax-highlighted HTML
}
```

## Data Flow

```
┌─────────────────┐
│  Message.text   │  Raw markdown text (stored)
│  (raw string)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  marked.parse() │  Convert markdown to HTML
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DOMPurify.      │  Remove XSS vectors
│ sanitize()      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ highlight.js    │  Apply syntax highlighting to code blocks
│ (via renderer)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Rendered HTML  │  Safe HTML for v-html display
│  (not stored)   │
└─────────────────┘
```

## Validation Rules

| Field | Rule | Rationale |
|-------|------|-----------|
| Message.text | Any string | Markdown parsing handles any input gracefully |
| CodeBlock.language | Lowercase, alphanumeric | Normalized for highlight.js lookup |
| RenderedMarkdown.html | Must pass DOMPurify | XSS prevention (FR-002) |

## State Transitions

No state transitions - markdown rendering is stateless and idempotent. The same input always produces the same output.

## Storage Impact

**None** - This feature adds no new storage requirements. Messages continue to store raw text. Markdown rendering is purely a display-time transformation.

## API Contracts

**None required** - This is a frontend-only feature. No new endpoints are added or modified. The existing message endpoints continue to return raw text which the frontend renders as markdown.

See `/specs/017-markdown-support/contracts/` - empty for this feature.
