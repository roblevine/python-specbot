# Research: Frontend Palette and Layout Redesign

**Feature**: 013-redesign-frontend-palette
**Date**: 2026-01-16
**Status**: Complete

## Research Questions

1. WCAG AA contrast compliance for the new color palette
2. CSS layout patterns for centered content with constrained width
3. Message layout patterns (centered system vs right-aligned user)
4. Metadata typography best practices

---

## 1. WCAG AA Contrast Compliance

### Color Palette

| Color Name | Hex | RGB | Relative Luminance |
|------------|-----|-----|-------------------|
| Light cream | #FFDBBB | (255, 219, 187) | 0.7551 |
| Tan | #CCBEB1 | (204, 190, 177) | 0.5312 |
| Warm brown | #997E67 | (153, 126, 103) | 0.2265 |
| Dark brown | #664930 | (102, 73, 48) | 0.0760 |

### Contrast Ratio Results

| Background | Text Color | Contrast Ratio | WCAG AA (4.5:1) |
|------------|------------|----------------|-----------------|
| #FFDBBB (light cream) | Black | 16.10:1 | **PASS** |
| #FFDBBB (light cream) | Near-black (#1d1d1f) | 13.01:1 | **PASS** |
| #CCBEB1 (tan) | Black | 11.62:1 | **PASS** |
| #CCBEB1 (tan) | Near-black (#1d1d1f) | 9.39:1 | **PASS** |
| #997E67 (warm brown) | White | 3.80:1 | **FAIL** |
| #997E67 (warm brown) | Black | ~4.8:1 | **PASS** |
| #664930 (dark brown) | White | 8.33:1 | **PASS** |

### Decision: Text Color Strategy

**Problem**: White text on #997E67 (warm brown) fails WCAG AA with only 3.80:1 contrast.

**Solution**:
- Use **near-black text** (#1d1d1f) on light backgrounds (#FFDBBB, #CCBEB1)
- Use **white text** (#FFFFFF) only on dark brown (#664930)
- If using #997E67 for sidebar, use **dark text** (black or near-black) instead of white

**Rationale**: Maintaining accessibility compliance is a hard requirement (FR-004). The warm brown (#997E67) works as an accent or background only with dark text.

**Alternatives Considered**:
- Darkening #997E67 to ~#7A6652 for white text compatibility - rejected as it changes the design palette
- Using #997E67 only for non-text elements (borders, dividers) - viable option

---

## 2. CSS Layout: Centered Content with Constrained Width

### Pattern: Max-Width Container with Auto Margins

```css
.chat-container {
  max-width: 768px;
  margin-left: auto;
  margin-right: auto;
  width: 100%;
  padding: 0 var(--spacing-md); /* Side padding on narrow screens */
}
```

### Decision: Container Approach

**Chosen Pattern**: CSS max-width with auto margins (flexbox centering alternative)

**Rationale**:
- Simple, widely supported pattern
- Works with existing component structure
- Graceful degradation on narrow viewports
- No JavaScript required

**Implementation Notes**:
- Apply to ChatArea component's inner content container
- Apply same constraint to InputArea component
- Use CSS custom property for reusability: `--chat-max-width: 768px`

---

## 3. Message Layout: System Center vs User Right

### Current Implementation Analysis

From `MessageBubble.vue`:
- Messages use flexbox with `justify-content: flex-end` for user, `flex-start` for system
- Both message types have bubble styling (background, border-radius, padding)

### Desired Layout

Based on Claude.ai reference:
- **System messages**: Full-width text content, no bubble, centered within container
- **User messages**: Right-aligned with subtle bubble/container

### Decision: Message Styling Approach

**System Messages**:
```css
.message.system {
  background: transparent;  /* No bubble */
  border-radius: 0;
  padding: 0;
  width: 100%;
  text-align: left;  /* Natural reading flow */
}
```

**User Messages**:
```css
.message.user {
  background: var(--color-user-message-bg);  /* #CCBEB1 tan */
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-md);
  margin-left: auto;  /* Push to right */
  max-width: 80%;  /* Don't span full width */
}
```

**Rationale**: Matches Claude.ai reference design where system responses are the "main content" and user messages are clearly distinguished inputs.

---

## 4. Metadata Typography

### Current Implementation

From components:
- Timestamps and model indicators use `--font-size-sm` (0.875rem)
- No specific "metadata" styling class

### Best Practices Research

- Metadata should be 2-3 sizes smaller than body text
- Use reduced opacity or lighter color for visual de-emphasis
- Consistent positioning (typically below or beside main content)

### Decision: Metadata Styling

**New CSS Variable**:
```css
--font-size-xs: 0.75rem;  /* 12px - for metadata */
--color-metadata: var(--color-text-secondary);
```

**Application**:
- Timestamps: `font-size: var(--font-size-xs)`
- Model indicators: `font-size: var(--font-size-xs)`
- Both use `color: var(--color-metadata)` for reduced prominence

**Rationale**: Creates clear visual hierarchy where message content is primary and metadata is secondary/informational.

---

## 5. Button Styling

### Current Implementation

From `HistoryBar.vue`:
- Buttons use box-shadow, background color, distinct borders
- Prominent hover effects

### Claude.ai Reference Analysis

- Minimal button styling
- Ghost/outline buttons
- Subtle hover state changes

### Decision: Modest Button Style

**Primary Button Pattern**:
```css
.button {
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text);
  cursor: pointer;
  transition: background-color 150ms ease;
}

.button:hover {
  background: rgba(0, 0, 0, 0.05);  /* Subtle darken on light backgrounds */
}

.button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

**Rationale**: Reduces visual noise while maintaining clear interactivity and accessibility.

---

## Summary of Decisions

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Text on light backgrounds | Near-black (#1d1d1f) | WCAG AA compliant (9-16:1 contrast) |
| Text on dark brown (#664930) | White | WCAG AA compliant (8.33:1) |
| Sidebar color | #997E67 with dark text OR #664930 with white text | #997E67 fails with white text |
| Chat container | max-width: 768px with auto margins | Simple, widely supported |
| System messages | No bubble, full-width, left-aligned text | Matches Claude.ai reference |
| User messages | Right-aligned bubble with max-width 80% | Clear visual distinction |
| Metadata font | 0.75rem (12px) with secondary color | Visual hierarchy |
| Button style | Ghost/outline with subtle hover | Reduced visual noise |
