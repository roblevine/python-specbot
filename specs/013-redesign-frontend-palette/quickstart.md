# Quickstart: Frontend Palette and Layout Redesign

**Feature**: 013-redesign-frontend-palette
**Date**: 2026-01-16

## Prerequisites

- Node.js and npm installed
- Frontend development server running (`cd frontend && npm run dev`)
- Browser developer tools for visual inspection

## Implementation Order

Follow these thin slices in priority order. Each slice is independently testable and deliverable.

### Slice 1: Color Palette (P1) - Start Here

**Goal**: Replace grey/blue palette with warm colors in global.css

**File**: `frontend/public/styles/global.css`

**Steps**:
1. Add new warm color variables at top of `:root`
2. Update semantic variable mappings
3. Remove legacy grey/blue variables

**Test**: Load app and verify cream background, warm tones throughout

**Time**: ~15 minutes

---

### Slice 2: Message Layout (P1)

**Goal**: System messages centered without bubbles, user messages right-aligned with bubbles

**File**: `frontend/src/components/ChatArea/MessageBubble.vue`

**Steps**:
1. Remove bubble styling (background, border-radius) from system messages
2. Keep bubble styling for user messages with new tan color
3. Adjust alignment: system = full-width, user = right + max-width

**Test**: Send a message, verify system response has no bubble, user message is right-aligned with tan background

**Time**: ~30 minutes

---

### Slice 3: Chat Width Constraint (P2)

**Goal**: Constrain chat content to ~768px centered

**Files**:
- `frontend/public/styles/global.css` (add `--chat-max-width`)
- `frontend/src/components/ChatArea/ChatArea.vue`
- `frontend/src/components/InputArea/InputArea.vue`

**Steps**:
1. Add `--chat-max-width: 768px` variable
2. Apply max-width and auto margins to messages container
3. Apply same constraint to input area

**Test**: Resize browser to wide viewport, verify chat content stays centered at 768px

**Time**: ~20 minutes

---

### Slice 4: Metadata Typography (P2)

**Goal**: Smaller, subtle metadata text

**Files**:
- `frontend/public/styles/global.css` (add `--font-size-xs`)
- `frontend/src/components/StatusBar/StatusBar.vue`
- `frontend/src/components/ModelSelector/ModelSelector.vue`
- `frontend/src/components/ChatArea/MessageBubble.vue` (timestamps)

**Steps**:
1. Add `--font-size-xs: 0.75rem` variable
2. Apply to all metadata elements (timestamps, model indicators)
3. Use secondary color for reduced prominence

**Test**: Verify metadata is noticeably smaller than message text

**Time**: ~20 minutes

---

### Slice 5: Button Styling (P2)

**Goal**: Modest, ghost-style buttons

**Files**:
- `frontend/src/components/HistoryBar/HistoryBar.vue`
- `frontend/src/components/InputArea/InputArea.vue`

**Steps**:
1. Change button backgrounds to transparent
2. Add subtle border
3. Reduce hover effect intensity
4. Maintain focus indicators for accessibility

**Test**: Verify buttons appear subtle but still have clear hover/focus states

**Time**: ~20 minutes

---

### Slice 6: Sidebar Margin Fix (P3)

**Goal**: Fix collapsed sidebar expand button margin

**File**: `frontend/src/components/HistoryBar/HistoryBar.vue`

**Steps**:
1. Add `--collapsed-sidebar-margin: 12px` or apply directly
2. Add right padding/margin to expand button in collapsed state
3. Verify clickable area is reasonable

**Test**: Collapse sidebar, verify expand button has visible margin from right edge

**Time**: ~10 minutes

---

## Quick Reference

### New CSS Variables

```css
/* Add to :root in global.css */
--color-warm-cream: #FFDBBB;
--color-warm-tan: #CCBEB1;
--color-warm-brown: #997E67;
--color-warm-dark: #664930;
--chat-max-width: 768px;
--font-size-xs: 0.75rem;
```

### Testing Commands

```bash
# Run frontend tests
cd frontend && npm test

# Run E2E tests (visual)
cd frontend && npm run test:e2e

# Start dev server
cd frontend && npm run dev
```

### WCAG Contrast Reminders

- ✅ Dark text (#1d1d1f) on cream (#FFDBBB): 13:1
- ✅ Dark text (#1d1d1f) on tan (#CCBEB1): 9:1
- ✅ White text on dark brown (#664930): 8:1
- ❌ White text on warm brown (#997E67): 3.8:1 - DON'T USE

## Verification Checklist

After each slice, verify:

- [ ] App loads without console errors
- [ ] Colors match specification
- [ ] Text is readable (contrast check)
- [ ] Existing functionality still works
- [ ] Visual appearance matches intent
