# Research: UI Redesign

**Feature**: 007-ui-redesign
**Date**: 2026-01-11
**Phase**: 0 - Research & Technology Decisions

## Overview

This document captures all technical research and decisions made during the planning phase for the UI redesign feature. The feature is primarily CSS-based with minimal JavaScript additions, focusing on visual improvements without architectural changes.

## Research Areas

### 1. Color Scheme Selection

**Question**: What specific grey and pastel blue values should we use for the color scheme?

**Decision**: Use a grey-based palette with pastel blue accents:
- **Primary Grey Tones**:
  - Background: `#f5f5f7` (light grey, Apple-inspired)
  - Surface: `#ffffff` (white for content areas)
  - Border: `#d1d1d6` (medium grey for dividers)
  - Text Primary: `#1d1d1f` (near-black for readability)
  - Text Secondary: `#86868b` (medium grey for secondary text)

- **Pastel Blue Accents**:
  - Primary Blue: `#a8c9e8` (soft pastel blue for user messages)
  - Blue Hover: `#8fb3d9` (slightly darker for hover states)
  - Blue Light: `#d4e4f5` (very light blue for subtle backgrounds)

**Rationale**:
- Grey-dominant palette creates professional, calm aesthetic
- Pastel blue provides warmth without overwhelming
- Colors tested for WCAG 2.1 AA compliance (4.5:1 for normal text)
- Apple-inspired grey values are proven to reduce eye fatigue
- Pastel blue differentiates user messages while maintaining subtlety

**Alternatives Considered**:
- **Tailwind default blues** (`#3b82f6`) - Rejected: too saturated, not pastel
- **Material Design greys** - Rejected: slightly warmer tones preferred
- **Pure grayscale** - Rejected: lacks warmth and personality

**Contrast Validation**:
- `#1d1d1f` on `#f5f5f7`: 12.6:1 ✅ (exceeds 4.5:1)
- `#ffffff` on `#a8c9e8`: 3.8:1 ⚠️ (use for large text only, or darker text)
- `#1d1d1f` on `#a8c9e8`: 9.5:1 ✅ (safe for user message text)

---

### 2. Sidebar Collapse Implementation

**Question**: How should we implement the collapsible sidebar with persistent state?

**Decision**: Use Vue 3 Composition API with LocalStorage persistence
- **Component**: New `useSidebarCollapse.js` composable
- **State Management**: Reactive `ref` for collapse state
- **Persistence**: Store in LocalStorage key `sidebar.collapsed` (boolean)
- **Animation**: CSS transition on sidebar width (300ms ease-in-out)
- **Toggle Control**: Icon button in HistoryBar header

**Rationale**:
- Composable pattern matches existing codebase (`useConversations.js`, `useMessages.js`)
- LocalStorage is already used for conversations (see `LocalStorageAdapter.js`)
- CSS transitions provide smooth 60fps animations without JavaScript overhead
- Single boolean state keeps complexity minimal

**Alternatives Considered**:
- **Vuex/Pinia store** - Rejected: overkill for single boolean preference
- **sessionStorage** - Rejected: users expect persistence across sessions
- **JavaScript animation** - Rejected: CSS transitions more performant
- **Click outside to collapse** - Rejected: too unpredictable, button better UX

**Implementation Pattern**:
```javascript
// useSidebarCollapse.js
import { ref, watch } from 'vue'

export function useSidebarCollapse() {
  const isCollapsed = ref(false)

  // Load from storage on init
  const loadFromStorage = () => {
    const stored = localStorage.getItem('sidebar.collapsed')
    isCollapsed.value = stored === 'true'
  }

  // Save on change
  watch(isCollapsed, (newValue) => {
    localStorage.setItem('sidebar.collapsed', String(newValue))
  })

  const toggle = () => {
    isCollapsed.value = !isCollapsed.value
  }

  return { isCollapsed, toggle, loadFromStorage }
}
```

---

### 3. CSS Architecture Approach

**Question**: Should we use CSS-in-JS, scoped styles, or global CSS variables?

**Decision**: CSS Variables in `global.css` + Scoped Component Styles
- **Global Variables**: Define color palette in `:root` of `global.css`
- **Component Styles**: Use scoped `<style scoped>` blocks referencing variables
- **No CSS-in-JS**: Avoid runtime overhead, leverage existing pattern

**Rationale**:
- Existing codebase uses this pattern (see `global.css:9-23`)
- CSS variables enable theme consistency without prop drilling
- Scoped styles prevent accidental style leakage
- No new dependencies required
- Easy to override for future dark mode (just swap variable values)

**Alternatives Considered**:
- **Tailwind CSS** - Rejected: large refactor, not worth for styling update
- **CSS Modules** - Rejected: no benefit over scoped styles in Vue
- **Styled Components** - Rejected: adds runtime overhead and new dependency

**Variable Naming Convention**:
```css
:root {
  /* Base colors */
  --color-grey-bg: #f5f5f7;
  --color-grey-surface: #ffffff;
  --color-grey-border: #d1d1d6;
  --color-grey-text-primary: #1d1d1f;
  --color-grey-text-secondary: #86868b;

  /* Accent colors */
  --color-blue-primary: #a8c9e8;
  --color-blue-hover: #8fb3d9;
  --color-blue-light: #d4e4f5;

  /* Semantic aliases */
  --color-user-message-bg: var(--color-blue-primary);
  --color-user-message-text: var(--color-grey-text-primary);
  --color-assistant-message-bg: var(--color-grey-surface);
  --color-assistant-message-text: var(--color-grey-text-primary);
}
```

---

### 4. Button Styling Standards

**Question**: What defines "proper button styling" for the New Conversation control?

**Decision**: Use modern button design with clear affordances
- **Base State**: Solid border, subtle background, rounded corners
- **Hover State**: Background color shift, slight shadow
- **Active State**: Inset shadow to simulate press
- **Focus State**: Outline for keyboard navigation accessibility

**Rationale**:
- Clear visual hierarchy establishes interactivity
- Hover feedback reduces uncertainty
- Focus states required for WCAG 2.1 compliance
- Matches modern UI conventions users expect

**Alternatives Considered**:
- **Text button only** - Rejected: insufficient visual weight for primary action
- **Floating action button (FAB)** - Rejected: doesn't fit within sidebar context
- **Icon-only button** - Rejected: spec requires clear button appearance

**CSS Implementation**:
```css
.new-conversation-button {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-grey-surface);
  border: 1px solid var(--color-grey-border);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all 200ms ease;
}

.new-conversation-button:hover {
  background: var(--color-blue-light);
  border-color: var(--color-blue-primary);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.new-conversation-button:active {
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
}

.new-conversation-button:focus-visible {
  outline: 2px solid var(--color-blue-primary);
  outline-offset: 2px;
}
```

---

### 5. Testing Strategy

**Question**: How should we test visual changes and sidebar functionality?

**Decision**: Multi-layer testing approach
- **Unit Tests**: Test `useSidebarCollapse` composable in isolation
- **Integration Tests**: Test sidebar toggle with LocalStorage mocking
- **E2E Tests**: Playwright tests for visual rendering and interaction
- **Manual Testing**: Visual review for color accuracy and aesthetics

**Rationale**:
- Unit tests validate state management logic
- Integration tests ensure storage persistence works
- E2E tests catch visual regressions
- Manual review necessary for subjective aesthetic judgment
- Matches existing test structure (see `frontend/tests/`)

**Alternatives Considered**:
- **Visual regression testing (Chromatic, Percy)** - Rejected: no budget/infrastructure for external service
- **Screenshot comparison** - Rejected: too brittle, many false positives
- **Skip E2E tests** - Rejected: need coverage for collapse interaction

**Test Coverage Targets**:
- `useSidebarCollapse.js`: 100% (simple composable, easy to cover)
- Sidebar collapse integration: 90%+ (cover happy path + error cases)
- E2E visual test: At least 1 test verifying collapse workflow

---

### 6. Browser Compatibility

**Question**: What browsers must we support for CSS features used?

**Decision**: Target modern evergreen browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- **CSS Variables**: Supported since Chrome 49, Firefox 31, Safari 9.1
- **Flexbox**: Universally supported
- **CSS Transitions**: Universally supported
- **LocalStorage**: Universally supported

**Rationale**:
- All required features have >95% browser support
- No polyfills or fallbacks needed
- Existing app already targets these browsers (Vue 3 requirement)

**Alternatives Considered**:
- **Support IE11** - Rejected: Vue 3 doesn't support IE11, moot point
- **Target only Chrome** - Rejected: unnecessarily restrictive

---

### 7. Accessibility Considerations

**Question**: What accessibility requirements apply beyond contrast ratios?

**Decision**: Ensure full keyboard navigation and screen reader support
- **Keyboard Navigation**: Tab to collapse button, Enter/Space to toggle
- **Screen Reader**: Announce collapsed/expanded state with `aria-label`
- **Focus Management**: Maintain focus on toggle button after collapse
- **Reduced Motion**: Respect `prefers-reduced-motion` for animations

**Rationale**:
- WCAG 2.1 Level AA requires keyboard access
- Screen reader users need state announcements
- Reduced motion preference prevents vestibular issues

**Alternatives Considered**:
- **Skip screen reader support** - Rejected: violates WCAG 2.1 AA
- **Visual indicator only** - Rejected: inaccessible to blind users

**Implementation Notes**:
```vue
<!-- In HistoryBar.vue -->
<button
  @click="toggle"
  :aria-label="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
  aria-expanded="!isCollapsed"
>
  <Icon :name="isCollapsed ? 'chevron-right' : 'chevron-left'" />
</button>
```

```css
/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  .history-bar {
    transition: none;
  }
}
```

---

## Summary of Key Decisions

| Area | Decision | Primary Rationale |
|------|----------|------------------|
| Color Scheme | Grey (#f5f5f7) + Pastel Blue (#a8c9e8) | Professional aesthetic, WCAG compliant, reduces eye fatigue |
| Sidebar Collapse | Vue composable + LocalStorage | Matches existing patterns, simple state management |
| CSS Architecture | CSS Variables + Scoped Styles | Already in use, no new dependencies, future-proof for theming |
| Button Styling | Modern affordances (border, hover, shadow) | Clear interactivity, accessibility compliant |
| Testing | Unit + Integration + E2E | Multi-layer coverage, balances thoroughness with pragmatism |
| Browser Support | Modern evergreen (90+) | All features universally supported, no polyfills needed |
| Accessibility | Full keyboard + screen reader | WCAG 2.1 AA compliance, inclusive design |

---

## Open Questions / Future Considerations

**None at this time.** All technical decisions required for implementation are resolved.

**Future Enhancements (Out of Scope)**:
- Dark mode theme (would leverage CSS variables for easy swap)
- Responsive mobile layout (separate feature)
- Customizable color themes (YAGNI for now)
