# Research: Chat Error Display

**Feature**: 005-chat-error-display
**Date**: 2026-01-10
**Phase**: Phase 0 - Research

## Overview

This document consolidates research findings for implementing error display in the Vue.js chat interface. Research focused on three key areas: error display UI patterns, sensitive data redaction, and Vue.js expandable component implementation.

## 1. Error Display UI Patterns

### Decision: Inline Error Display with Expandable Details

**Chosen Approach**: Display errors inline within the message bubble area with a collapsible details section.

**Rationale**:
- **Proximity to source**: Errors appear next to the failed message, reducing cognitive load
- **Industry standard**: Slack, Discord, and Teams all use inline error display
- **Accessibility**: Easier for screen readers and keyboard navigation when errors are in the message flow
- **Mobile-friendly**: Avoids issues with virtual keyboards covering bottom-positioned errors

**Visual Design Elements**:
- High-contrast red (#DC2626) for error indicators
- Warning triangle/exclamation icon (never rely on color alone for accessibility)
- Bold text for error message summary
- Distinct border/background for error section
- "Details" button for expanding full error information

**Alternatives Considered**:
- **Toast notifications**: Dismissed - errors disappear and provide no history
- **Bottom status bar only**: Dismissed - current implementation, users requested better visibility
- **Modal dialogs**: Dismissed - too disruptive for non-critical errors
- **Right-side panel**: Dismissed - accessibility issues with magnification software

### Accessibility Requirements (WCAG 3.3.1)

**ARIA Attributes**:
- `aria-expanded` on toggle button to indicate expanded/collapsed state
- `aria-controls` linking button to content region
- `role="region"` on error details section
- `aria-label` providing context for screen readers

**Keyboard Navigation**:
- Enter and Space keys activate toggle button
- Focus remains on toggle after collapse
- Clear visual focus indicators (2px outline, 2px offset)

**Message Clarity**:
- 14 words or less = 90% comprehension rate
- Avoid technical jargon (use "Message failed to send" not "500 Internal Server Error")
- Provide actionable information when possible

## 2. Sensitive Data Redaction

### Decision: Custom Regex-Based Redaction with Pattern Library

**Chosen Approach**: Implement custom JavaScript utility using proven regex patterns from the Secrets-Patterns-DB (1,600+ patterns) and security best practices.

**Rationale**:
- **No additional dependencies**: Pure JavaScript solution, no npm packages required
- **Customizable**: Easy to add project-specific patterns
- **Lightweight**: ~2KB for patterns vs 15KB+ for libraries
- **Proven patterns**: Based on open-source Secrets-Patterns-DB maintained by security researchers

**Patterns to Implement** (ordered specific to generic):

1. **Specific API Keys**:
   - AWS: `AKIA[0-9A-Z]{16}`
   - Google: `AIza[0-9A-Za-z\-_]{35}`
   - Stripe: `sk_live_[0-9a-zA-Z]{24}`
   - GitHub: `gh[pousr]_[A-Za-z0-9_]{36,255}`

2. **Generic Tokens**:
   - Bearer tokens: `Bearer\s+[a-zA-Z0-9\-._~+/]+=*`
   - JWT: `eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}`

3. **Private Keys**:
   - RSA/generic: `-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----`

4. **Passwords and Secrets**:
   - Password assignments: `(?:password|pwd|pass)['"\s:=]+[^\s'"]{4,100}`
   - Generic secrets: `(?:secret|token)['"\s:=]+[a-zA-Z0-9\-_.]{8,100}`

5. **Session Tokens**:
   - URL parameters: `[?&](session|token|auth)=[a-zA-Z0-9\-_]{10,}`

**Redaction Format**:
- Clear markers: `***REDACTED_[TYPE]***` (e.g., `***REDACTED_AWS_KEY***`)
- Preserves context while hiding sensitive data
- Visually distinct from normal text

**Alternatives Considered**:
- **redact-pii npm package**: Dismissed - 15KB overhead for functionality we can implement in 2KB
- **Google Cloud DLP API**: Dismissed - requires external service, adds latency and costs
- **Simple string replacement**: Dismissed - too simplistic, misses many patterns

### Security Implementation

**Default Behavior**: Always redact sensitive data

**Toggle Show/Hide**:
- **Warning dialog** before revealing sensitive data
- **Session-only state**: Don't persist "show sensitive" preference
- **Client-side only**: Never log or send unredacted data to server
- **Clear warning text**: "This error message may contain sensitive information such as API keys or tokens. Only reveal this in a secure environment."

**Detection Function**:
- `containsSensitiveData(text)`: Returns boolean if any pattern matches
- `detectSensitivePatterns(text)`: Returns array of matched pattern names
- `redactSensitiveData(text)`: Returns redacted text

## 3. Vue.js Expandable Component Implementation

### Decision: Vue Transitions with Composition API Composable

**Chosen Approach**: Create reusable `useCollapsible` composable that manages state and provides ARIA attributes, combined with Vue's `<transition>` component for animations.

**Rationale**:
- **Reusable**: Composable can be used for any expandable content, not just errors
- **Vue-native**: Uses built-in Vue transitions, no additional libraries
- **Accessible by default**: Composable returns proper ARIA attributes
- **Simple API**: `toggle()`, `expand()`, `collapse()` methods with `isExpanded` reactive state

**Implementation Pattern**:

```javascript
// useCollapsible.js composable
export function useCollapsible(initialExpanded = false) {
  const isExpanded = ref(initialExpanded)

  const toggle = () => { isExpanded.value = !isExpanded.value }
  const expand = () => { isExpanded.value = true }
  const collapse = () => { isExpanded.value = false }

  const triggerAttrs = computed(() => ({
    'aria-expanded': isExpanded.value,
    'aria-controls': 'collapsible-content',
    'type': 'button'
  }))

  const contentAttrs = computed(() => ({
    'id': 'collapsible-content',
    'role': 'region',
    'aria-hidden': !isExpanded.value
  }))

  return { isExpanded, toggle, expand, collapse, triggerAttrs, contentAttrs }
}
```

**Animation Strategy**:
- **Vue Transition**: Use `<transition name="expand">` with CSS keyframes
- **Easing**: Cubic-bezier for natural motion (`cubic-bezier(0.4, 0, 0.2, 1)`)
- **Duration**: 300ms expand, 200ms collapse (asymmetric for better UX)
- **Properties**: Animate `max-height` and `opacity` simultaneously

**Alternatives Considered**:
- **Pure CSS transitions**: Dismissed - less control, no lifecycle hooks
- **Animation libraries (GSAP, Anime.js)**: Dismissed - overkill for simple expand/collapse
- **Headless UI libraries (Radix Vue)**: Dismissed - adds 50KB+ for one component

### Performance Optimizations

1. **Use `v-if` instead of `v-show`**: Don't render error details when collapsed (saves DOM nodes)
2. **Set reasonable max-height**: Limit to 300px to prevent layout thrashing
3. **Debounce rapid toggles**: 300ms timeout prevents animation jank
4. **Overflow hidden during transition**: Prevents content flicker

**Layout Stability**:
- Max-height prevents infinite expansion for very large error messages
- Scrollable region (overflow-y: auto) for error details exceeding 150px
- Word-break and white-space handling for long tokens/URLs

## 4. Integration with Existing Codebase

### Current Architecture Context

**Existing Error Handling**:
- Frontend: `ApiError` class with statusCode and details properties
- Status display: StatusBar component shows errors for 5 seconds
- Message status: Messages have `status: 'error'` but no error details attached
- Backend: ErrorResponse schema with status, error, detail, timestamp

**Required Changes**:

1. **Message Schema Extension** (backward compatible):
   ```javascript
   {
     id: string,
     text: string,
     sender: "user" | "system",
     timestamp: string,
     status: "pending" | "sent" | "error",
     // NEW: Optional error fields
     errorMessage?: string,      // User-friendly summary
     errorType?: string,          // "Network Error", "Server Error", etc.
     errorCode?: number,          // HTTP status code
     errorDetails?: string        // Full error details for expansion
   }
   ```

2. **Component Modifications**:
   - `MessageBubble.vue`: Add error section with expand/collapse
   - `ChatArea.vue`: No changes required (already renders MessageBubble array)
   - `useMessages.js`: Attach error details to message on API error

3. **New Files**:
   - `/frontend/src/utils/sensitiveDataRedactor.js`
   - `/frontend/src/composables/useCollapsible.js`
   - `/frontend/src/utils/errorFormatter.js` (optional - format errors for display)

### CSS Variables to Use

From existing `/frontend/public/styles/global.css`:
- Colors: `var(--color-error)`, `var(--color-text-secondary)`
- Spacing: `var(--spacing-xs)`, `var(--spacing-sm)`
- Font sizes: `var(--font-size-xs)`, `var(--font-size-sm)`

**New CSS Variables to Add**:
```css
:root {
  --color-error-light: #FCA5A5;        /* Lighter red for borders */
  --color-error-background: #FEF2F2;    /* Very light red for backgrounds */
}
```

## 5. Testing Strategy

### Unit Tests (Vitest)

1. **sensitiveDataRedactor.test.js**:
   - Test each regex pattern individually
   - Test combined patterns
   - Test edge cases (malformed tokens, partial matches)
   - Test performance with large text blocks

2. **useCollapsible.test.js**:
   - Test initial state (expanded/collapsed)
   - Test toggle, expand, collapse methods
   - Verify ARIA attribute values
   - Test debounce behavior

3. **ErrorMessage.test.js** (component tests):
   - Test rendering with different error types
   - Test expand/collapse behavior
   - Test sensitive data redaction display
   - Test keyboard navigation

### Integration Tests (Vitest)

1. **errorDisplay.test.js**:
   - Test full flow: API error → error message display → expand details
   - Mock API client with different error responses (400, 422, 500, network)
   - Verify error appears in chat with correct styling
   - Verify error details expand/collapse

### E2E Tests (Playwright)

1. **error-scenarios.spec.js**:
   - Simulate network failure and verify error display
   - Simulate server error and verify error display
   - Test expand/collapse interaction
   - Test sensitive data toggle with warning
   - Verify accessibility (keyboard navigation, screen reader)

## 6. Implementation Phases (Thin Slices)

### Slice 1 (P1): Basic Error Display
- Extend message schema with error fields
- Add error section to MessageBubble component
- Display error summary with visual distinction
- Tests: error rendering, visual styling

**Deliverable**: Client-side errors (network, timeout) display in chat with red styling

### Slice 2 (P2): Server Error Integration
- Extend apiClient.js to attach error details to messages
- Map HTTP status codes to error types
- Display server error messages in chat
- Tests: 400/422/500 error display

**Deliverable**: Server errors display in chat with detailed error messages

### Slice 3 (P3): Expandable Details + Redaction
- Implement useCollapsible composable
- Create sensitiveDataRedactor utility
- Add expand/collapse UI to error section
- Add sensitive data toggle with warning
- Tests: expand/collapse, redaction, toggle behavior

**Deliverable**: Users can expand errors to see full details with sensitive data redacted

## Summary

All research is complete with clear technical decisions:

1. **Error Display**: Inline with expandable details, high-contrast red styling, full accessibility support
2. **Sensitive Data**: Custom regex-based redaction with 15+ proven patterns, warning dialog before reveal
3. **Expandable UI**: Vue Composition API composable with Vue transitions, 300ms animation

No additional dependencies required. All solutions use existing Vue 3, CSS, and vanilla JavaScript. Implementation can proceed to Phase 1 (Design & Contracts).

## References

- [Error Message Guidelines - Nielsen Norman Group](https://www.nngroup.com/articles/error-message-guidelines/)
- [Accessible Form Error Messaging Best Practices](https://www.reform.app/blog/accessible-form-error-messaging-best-practices)
- [Secrets Patterns DB - Open Source Regex Database](https://github.com/mazen160/secrets-patterns-db)
- [Radix Vue Collapsible Component](https://www.radix-vue.com/components/collapsible)
- [Vue 3 Composables Guide](https://vuejs.org/guide/reusability/composables.html)
- [WCAG 3.3.1 Error Identification](https://www.w3.org/WAI/WCAG21/Understanding/error-identification.html)
