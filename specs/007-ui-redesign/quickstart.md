# Quickstart: UI Redesign Implementation

**Feature**: 007-ui-redesign
**Branch**: `007-ui-redesign`
**Date**: 2026-01-11

## Prerequisites

- Node.js and npm installed (for frontend)
- Existing project setup complete (see root README.md)
- Familiarity with Vue 3 Composition API
- Basic CSS knowledge (CSS Variables, Flexbox, Transitions)

## Implementation Overview

This feature implements a visual redesign with three thin vertical slices:
1. **Slice 1 (P1)**: Color scheme CSS changes
2. **Slice 2 (P2)**: Collapsible sidebar with persistent state
3. **Slice 3 (P3)**: Button styling refinements

Each slice is independently testable and deployable following TDD principles.

## Setup

### 1. Verify Branch
```bash
git checkout 007-ui-redesign
git status  # Should show you're on 007-ui-redesign
```

### 2. Install Dependencies (if needed)
```bash
cd frontend
npm install
```

### 3. Start Development Server
```bash
npm run dev
```
Application should be running at http://localhost:5173

### 4. Run Tests
```bash
# Unit tests
npm run test

# E2E tests (separate terminal)
npm run test:e2e
```

## Implementation Path (TDD Workflow)

### Slice 1: Color Scheme (P1) - Estimated 2-3 hours

#### Step 1.1: Write CSS Variable Tests
**File**: `frontend/tests/unit/colorPalette.test.js` (NEW)

Write tests to verify:
- CSS variables defined in `:root`
- Color values match specification
- Contrast ratios meet WCAG 2.1 AA

**Expected Result**: Tests FAIL (variables don't exist yet)

#### Step 1.2: Update CSS Variables
**File**: `frontend/public/styles/global.css`

Update `:root` section:
```css
:root {
  /* Replace existing color variables with new grey/pastel blue palette */
  --color-grey-bg: #f5f5f7;
  --color-grey-surface: #ffffff;
  --color-grey-border: #d1d1d6;
  --color-grey-text-primary: #1d1d1f;
  --color-grey-text-secondary: #86868b;
  --color-blue-primary: #a8c9e8;
  --color-blue-hover: #8fb3d9;
  --color-blue-light: #d4e4f5;

  /* Update semantic aliases */
  --color-user-message-bg: var(--color-blue-primary);
  --color-user-message-text: var(--color-grey-text-primary);
  --color-assistant-message-bg: var(--color-grey-surface);
  --color-assistant-message-text: var(--color-grey-text-primary);
  --color-background: var(--color-grey-bg);
  --color-text: var(--color-grey-text-primary);
  --color-text-secondary: var(--color-grey-text-secondary);
  --color-border: var(--color-grey-border);
}
```

**Expected Result**: Tests PASS

#### Step 1.3: Update Component Styles
**Files**: All Vue components using old color variables

Review and update:
- `StatusBar.vue`: Update background and text colors
- `ChatArea.vue`: Update message bubble colors
- `InputArea.vue`: Update input styling
- `HistoryBar.vue`: Update sidebar background

**Validation**:
- Run `npm run dev` and visually inspect
- Verify all UI elements use new color scheme
- No visual inconsistencies

#### Step 1.4: Manual Accessibility Check
Use browser dev tools to verify contrast ratios:
- Text on background: Check with color contrast analyzer
- All combinations must meet WCAG 2.1 AA (4.5:1 for normal text)

**Expected Result**: All contrast ratios pass

#### Step 1.5: Commit Slice 1
```bash
git add frontend/public/styles/global.css
git add frontend/src/components/
git add frontend/tests/unit/colorPalette.test.js
git commit -m "feat: implement grey/pastel blue color scheme (P1)

- Update CSS variables in global.css
- Apply new color scheme to all components
- Verify WCAG 2.1 AA contrast ratios
- Add tests for color palette validation

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Slice 2: Collapsible Sidebar (P2) - Estimated 3-4 hours

#### Step 2.1: Write Composable Tests
**File**: `frontend/tests/unit/useSidebarCollapse.test.js` (NEW)

Write tests for:
- `isCollapsed` reactive state
- `toggle()` method
- `loadFromStorage()` loads from LocalStorage
- `watch` saves to LocalStorage on state change

**Expected Result**: Tests FAIL (composable doesn't exist)

#### Step 2.2: Create Sidebar Collapse Composable
**File**: `frontend/src/composables/useSidebarCollapse.js` (NEW)

```javascript
import { ref, watch } from 'vue'
import * as logger from '../utils/logger.js'

export function useSidebarCollapse() {
  const isCollapsed = ref(false)

  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem('sidebar.collapsed')
      if (stored !== 'true' && stored !== 'false') {
        logger.warn('Invalid sidebar.collapsed value, defaulting to false', { stored })
        isCollapsed.value = false
        return
      }
      isCollapsed.value = stored === 'true'
      logger.debug('Loaded sidebar state from storage', { isCollapsed: isCollapsed.value })
    } catch (error) {
      logger.error('Failed to load sidebar state', error)
      isCollapsed.value = false
    }
  }

  watch(isCollapsed, (newValue) => {
    try {
      localStorage.setItem('sidebar.collapsed', String(newValue))
      logger.debug('Saved sidebar state to storage', { isCollapsed: newValue })
    } catch (error) {
      logger.error('Failed to persist sidebar preference', error)
    }
  })

  const toggle = () => {
    isCollapsed.value = !isCollapsed.value
    logger.info('Sidebar toggled', { isCollapsed: isCollapsed.value })
  }

  const collapse = () => {
    isCollapsed.value = true
  }

  const expand = () => {
    isCollapsed.value = false
  }

  return {
    isCollapsed,
    toggle,
    collapse,
    expand,
    loadFromStorage
  }
}
```

**Expected Result**: Tests PASS

#### Step 2.3: Update LocalStorage Schema
**File**: `frontend/src/storage/StorageSchema.js`

Add schema migration logic for v1.1.0:
```javascript
// Update version
const CURRENT_VERSION = '1.1.0'

// Add migration
function migrateSchema(data) {
  if (data.version === '1.0.0') {
    data.preferences = { sidebarCollapsed: false }
    data.version = '1.1.0'
  }
  return data
}
```

**File**: `frontend/tests/unit/StorageSchema.test.js`

Add tests for schema migration.

**Expected Result**: Tests PASS

#### Step 2.4: Integrate Composable in App
**File**: `frontend/src/components/App/App.vue`

```javascript
import { useSidebarCollapse } from '../../composables/useSidebarCollapse.js'

export default {
  setup() {
    const { isCollapsed, toggle, loadFromStorage } = useSidebarCollapse()

    onMounted(() => {
      loadFromStorage()
      // ... existing initialization
    })

    return {
      isCollapsed,
      toggleSidebar: toggle,
      // ... existing returns
    }
  }
}
```

#### Step 2.5: Update HistoryBar Component
**File**: `frontend/src/components/HistoryBar/HistoryBar.vue`

Add collapse button and CSS transitions:
```vue
<template>
  <aside
    class="history-bar"
    :class="{ 'collapsed': isCollapsed }"
  >
    <header class="history-bar-header">
      <h2 v-if="!isCollapsed">Conversations</h2>
      <button
        class="collapse-button"
        @click="$emit('toggle-sidebar')"
        :aria-label="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        :aria-expanded="!isCollapsed"
      >
        <span class="icon">{{ isCollapsed ? '→' : '←' }}</span>
      </button>
    </header>
    <!-- ... rest of sidebar content ... -->
  </aside>
</template>

<script>
export default {
  props: {
    isCollapsed: {
      type: Boolean,
      default: false
    }
  },
  emits: ['toggle-sidebar']
}
</script>

<style scoped>
.history-bar {
  width: var(--history-bar-width, 250px);
  transition: width 300ms ease-in-out;
  overflow: hidden;
}

.history-bar.collapsed {
  width: 48px;
}

@media (prefers-reduced-motion: reduce) {
  .history-bar {
    transition: none;
  }
}

.collapse-button {
  padding: 0.5rem;
  background: var(--color-grey-surface);
  border: 1px solid var(--color-grey-border);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all 200ms ease;
}

.collapse-button:hover {
  background: var(--color-blue-light);
  border-color: var(--color-blue-primary);
}

.collapse-button:focus-visible {
  outline: 2px solid var(--color-blue-primary);
  outline-offset: 2px;
}
</style>
```

#### Step 2.6: Write Integration Tests
**File**: `frontend/tests/integration/sidebar-collapse.test.js` (NEW)

Test:
- Sidebar toggles on button click
- State persists to LocalStorage
- State loads from LocalStorage on mount
- Collapsed class applied correctly

#### Step 2.7: Write E2E Test
**File**: `frontend/tests/e2e/ui-redesign.spec.js` (NEW)

Test full workflow:
- User clicks collapse button
- Sidebar animates and collapses
- Refresh page
- Sidebar remains collapsed

#### Step 2.8: Run All Tests
```bash
npm run test         # Unit + integration
npm run test:e2e     # E2E
```

**Expected Result**: All tests PASS

#### Step 2.9: Commit Slice 2
```bash
git add frontend/src/composables/useSidebarCollapse.js
git add frontend/src/components/App/App.vue
git add frontend/src/components/HistoryBar/HistoryBar.vue
git add frontend/src/storage/StorageSchema.js
git add frontend/tests/
git commit -m "feat: implement collapsible sidebar with persistent state (P2)

- Create useSidebarCollapse composable
- Add collapse/expand toggle button to HistoryBar
- Persist sidebar state to LocalStorage
- Update schema to v1.1.0 with preferences field
- Add CSS transitions with reduced-motion support
- Add full test coverage (unit, integration, E2E)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Slice 3: Button Styling (P3) - Estimated 1-2 hours

#### Step 3.1: Write Button Style Tests
**File**: `frontend/tests/unit/HistoryBar.test.js` (MODIFY)

Add tests for:
- New conversation button has proper button styling
- Hover states apply correctly
- Focus states meet accessibility requirements

**Expected Result**: Tests FAIL (button doesn't have new styles yet)

#### Step 3.2: Update New Conversation Button
**File**: `frontend/src/components/HistoryBar/HistoryBar.vue`

Update button styles:
```vue
<style scoped>
.new-conversation-button {
  padding: var(--spacing-sm) var(--spacing-md);
  margin: var(--spacing-md);
  background: var(--color-grey-surface);
  border: 1px solid var(--color-grey-border);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  font-size: var(--font-size-md);
  font-weight: 500;
  color: var(--color-grey-text-primary);
  transition: all 200ms ease;
  width: calc(100% - 2 * var(--spacing-md));
}

.new-conversation-button:hover {
  background: var(--color-blue-light);
  border-color: var(--color-blue-primary);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.new-conversation-button:active {
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.new-conversation-button:focus-visible {
  outline: 2px solid var(--color-blue-primary);
  outline-offset: 2px;
}
</style>
```

**Expected Result**: Tests PASS

#### Step 3.3: Manual Visual Review
- Verify button looks like a button (clear affordances)
- Test hover states
- Test keyboard focus (Tab key)
- Verify it fits color scheme

#### Step 3.4: Run All Tests
```bash
npm run test
npm run test:e2e
```

**Expected Result**: All tests PASS

#### Step 3.5: Commit Slice 3
```bash
git add frontend/src/components/HistoryBar/HistoryBar.vue
git add frontend/tests/unit/HistoryBar.test.js
git commit -m "feat: improve new conversation button styling (P3)

- Add proper button affordances (border, background, shadow)
- Implement hover and active states
- Add focus-visible outline for accessibility
- Integrate with grey/pastel blue color scheme

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Verification

### Final Checklist

After completing all three slices, verify:

- [ ] All unit tests pass: `npm run test`
- [ ] All E2E tests pass: `npm run test:e2e`
- [ ] Linting passes: `npm run lint`
- [ ] Visual inspection: All UI elements follow grey/pastel blue scheme
- [ ] Accessibility: Sidebar toggle works with keyboard (Tab + Enter)
- [ ] Persistence: Sidebar state persists across page reloads
- [ ] Color contrast: All text meets WCAG 2.1 AA (4.5:1 minimum)
- [ ] Reduced motion: Sidebar respects `prefers-reduced-motion`
- [ ] No console errors in browser dev tools
- [ ] Existing functionality unaffected (send messages, create conversations)

### Manual Testing Script

1. **Color Scheme**:
   - Open app in browser
   - Verify background is light grey (#f5f5f7)
   - Send a message, verify user message has pastel blue background (#a8c9e8)
   - Verify assistant message has grey/white background
   - Check all text is readable (high contrast)

2. **Collapsible Sidebar**:
   - Click collapse button in sidebar
   - Verify sidebar animates smoothly to collapsed state (48px width)
   - Click expand button (now visible as →)
   - Verify sidebar expands back to full width (250px)
   - Refresh page
   - Verify sidebar remains in last state (collapsed or expanded)
   - Test keyboard navigation: Tab to button, press Enter
   - Clear LocalStorage, verify sidebar defaults to expanded

3. **Button Styling**:
   - Observe "New Conversation" button
   - Verify it has clear button appearance (border, background)
   - Hover over button, verify hover state (blue tint, shadow)
   - Click button, verify active state (inset shadow)
   - Tab to button, verify focus outline appears

### Performance Validation

Open Chrome DevTools:
1. **Performance Tab**: Record interaction
   - Click collapse button
   - Verify animation runs at 60fps (no frame drops)
   - Should complete in ~300ms

2. **Lighthouse**: Run audit
   - Accessibility score: 100 (or close)
   - Performance: Should not degrade from baseline
   - Verify contrast ratios reported as passing

## Troubleshooting

### Issue: Colors not updating
- **Solution**: Hard refresh browser (Ctrl+Shift+R / Cmd+Shift+R)
- **Cause**: CSS cached by browser

### Issue: Sidebar doesn't persist
- **Solution**: Check browser console for LocalStorage errors
- **Possible Causes**:
  - Private browsing mode (LocalStorage disabled)
  - Quota exceeded (unlikely with single boolean)
  - Check `useSidebarCollapse.js` logs

### Issue: Tests failing
- **Solution**: Run `npm install` to ensure dependencies updated
- **Check**: Test setup in `frontend/tests/setup.js` mocks LocalStorage

### Issue: Transitions not smooth
- **Solution**: Check GPU acceleration in browser settings
- **Workaround**: Increase transition duration in CSS (300ms → 500ms)

## Next Steps

After completing implementation and verification:

1. **Generate tasks.md**: Run `/speckit.tasks` command
2. **Create Pull Request**: Push branch and create PR to main
3. **Request Review**: Tag reviewer, reference spec and plan docs
4. **Demo**: Record short video showing three slices working

## References

- **Spec**: [spec.md](./spec.md)
- **Plan**: [plan.md](./plan.md)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Contracts**: [contracts/README.md](./contracts/README.md)

## Support

If you encounter issues not covered here:
1. Check feature spec for requirements
2. Review research.md for technical decisions
3. Examine data-model.md for schema details
4. Ask for clarification from feature author
