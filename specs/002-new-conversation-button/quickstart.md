# Quickstart Guide: New Conversation Button

**Feature**: 002-new-conversation-button
**Date**: 2025-12-25
**For**: Developers implementing this feature

## Overview

This quickstart guide provides step-by-step instructions for implementing the "New Conversation" button feature. Follow this guide after reading the implementation plan, research, and contracts.

---

## Prerequisites

Before starting implementation:

✅ **Required Knowledge**:
- Vue 3 Composition API basics
- Component props and events
- CSS styling with CSS variables
- Test-driven development workflow

✅ **Required Files Read**:
- [spec.md](./spec.md) - Feature requirements
- [plan.md](./plan.md) - Implementation strategy
- [research.md](./research.md) - Technical decisions
- [contracts/component-interface.md](./contracts/component-interface.md) - Component contract

✅ **Development Environment**:
- Node.js 18+ installed
- Dependencies installed (`npm install`)
- Development server running (`npm run dev`)
- Tests passing (`npm test`)

---

## Implementation Workflow (TDD)

### Phase 1: Write Tests First (RED) ⛔

**Duration**: ~30-45 minutes

Follow Test-Driven Development (Constitution Principle III):

#### Step 1.1: Create Unit Test File

```bash
# Create test file
touch frontend/src/components/HistoryBar/HistoryBar.test.js
```

#### Step 1.2: Write Unit Tests (MUST FAIL)

Add to `HistoryBar.test.js`:

```javascript
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import HistoryBar from './HistoryBar.vue'

describe('HistoryBar - New Conversation Button', () => {
  it('renders the new conversation button', () => {
    const wrapper = mount(HistoryBar, {
      props: {
        conversations: [],
        activeConversationId: null
      }
    })

    const button = wrapper.find('.new-conversation-btn')
    expect(button.exists()).toBe(true)
    expect(button.text()).toContain('New Conversation')
  })

  it('emits new-conversation event when button is clicked', async () => {
    const wrapper = mount(HistoryBar, {
      props: {
        conversations: [],
        activeConversationId: null
      }
    })

    const button = wrapper.find('.new-conversation-btn')
    await button.trigger('click')

    expect(wrapper.emitted('new-conversation')).toBeTruthy()
    expect(wrapper.emitted('new-conversation')).toHaveLength(1)
  })

  it('prevents rapid duplicate emissions (debounce)', async () => {
    vi.useFakeTimers()

    const wrapper = mount(HistoryBar, {
      props: {
        conversations: [],
        activeConversationId: null
      }
    })

    const button = wrapper.find('.new-conversation-btn')

    // Click 3 times rapidly
    await button.trigger('click')
    await button.trigger('click')
    await button.trigger('click')

    // Should only emit once
    expect(wrapper.emitted('new-conversation')).toHaveLength(1)

    // Wait for debounce to clear
    vi.advanceTimersByTime(300)

    // Click again
    await button.trigger('click')

    // Should emit second time
    expect(wrapper.emitted('new-conversation')).toHaveLength(2)

    vi.useRealTimers()
  })

  it('has correct accessibility attributes', () => {
    const wrapper = mount(HistoryBar, {
      props: {
        conversations: [],
        activeConversationId: null
      }
    })

    const button = wrapper.find('.new-conversation-btn')
    expect(button.attributes('aria-label')).toBe('Start new conversation')
  })
})
```

#### Step 1.3: Run Tests (VERIFY THEY FAIL)

```bash
npm test -- HistoryBar.test.js
```

**Expected**: All tests should fail with "element not found" or similar errors.

**🚨 CRITICAL**: If tests pass at this stage, you wrote the tests wrong. Tests MUST fail before implementation.

---

#### Step 1.4: Create E2E Test File

```bash
# Create E2E test file
touch frontend/tests/e2e/new-conversation.spec.js
```

#### Step 1.5: Write E2E Tests (MUST FAIL)

Add to `new-conversation.spec.js`:

```javascript
import { test, expect } from '@playwright/test'

test.describe('New Conversation Button', () => {
  test('user can start a new conversation', async ({ page }) => {
    await page.goto('http://localhost:5173')

    // Send a message in first conversation
    await page.fill('textarea', 'First message')
    await page.click('button:has-text("Send")')

    // Wait for message to appear
    await expect(page.locator('.message-bubble')).toHaveCount(2) // user + loopback

    // Click new conversation button
    await page.click('button:has-text("New Conversation")')

    // Verify chat area is empty
    await expect(page.locator('.message-bubble')).toHaveCount(0)

    // Verify previous conversation is in history
    await expect(page.locator('.conversation-item')).toHaveCount(2)
  })

  test('unsaved message is discarded when starting new conversation', async ({ page }) => {
    await page.goto('http://localhost:5173')

    // Type message but don't send
    await page.fill('textarea', 'Unsaved message')

    // Click new conversation button
    await page.click('button:has-text("New Conversation")')

    // Verify input is cleared
    await expect(page.locator('textarea')).toHaveValue('')

    // Verify no messages in chat area
    await expect(page.locator('.message-bubble')).toHaveCount(0)
  })

  test('rapid clicks only create one new conversation', async ({ page }) => {
    await page.goto('http://localhost:5173')

    const initialCount = await page.locator('.conversation-item').count()

    // Click button 5 times rapidly
    for (let i = 0; i < 5; i++) {
      await page.click('button:has-text("New Conversation")', { delay: 50 })
    }

    // Wait a bit for any async operations
    await page.waitForTimeout(500)

    // Should only have created 1 new conversation
    const finalCount = await page.locator('.conversation-item').count()
    expect(finalCount).toBe(initialCount + 1)
  })

  test('button is keyboard accessible', async ({ page }) => {
    await page.goto('http://localhost:5173')

    // Tab to the button
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab') // May need multiple tabs depending on layout

    // Verify button is focused
    const button = page.locator('button:has-text("New Conversation")')
    await expect(button).toBeFocused()

    // Press Enter to activate
    await page.keyboard.press('Enter')

    // Verify new conversation was created
    await expect(page.locator('.conversation-item')).toHaveCount(2)
  })
})
```

#### Step 1.6: Run E2E Tests (VERIFY THEY FAIL)

```bash
npm run test:e2e
```

**Expected**: All E2E tests should fail (button not found, etc.)

---

### Phase 2: Implement Code (GREEN) ✅

**Duration**: ~20-30 minutes

Now that tests are failing, implement the minimum code to pass them.

#### Step 2.1: Modify HistoryBar Component

Open `frontend/src/components/HistoryBar/HistoryBar.vue`

**Add to template** (after the `<h2>` heading, inside `.history-header`):

```vue
<template>
  <div class="history-bar">
    <div class="history-header">
      <h2>Conversations</h2>
      <button
        class="new-conversation-btn"
        aria-label="Start new conversation"
        @click="handleNewConversation"
      >
        New Conversation
      </button>
    </div>
    <div class="conversations-list">
      <!-- Existing conversation list code remains unchanged -->
    </div>
  </div>
</template>
```

**Add to script** (update emits and add handler):

```javascript
export default {
  name: 'HistoryBar',
  props: {
    conversations: {
      type: Array,
      default: () => [],
    },
    activeConversationId: {
      type: String,
      default: null,
    },
  },
  emits: ['select-conversation', 'new-conversation'], // Add new-conversation
  setup(props, { emit }) {
    let isCreating = false // Debounce guard

    function getPreview(conversation) {
      // Existing code unchanged
    }

    function handleNewConversation() {
      if (isCreating) return
      isCreating = true

      emit('new-conversation')

      setTimeout(() => {
        isCreating = false
      }, 300)
    }

    return {
      getPreview,
      handleNewConversation, // Add to return
    }
  },
}
```

**Add to styles** (add button styles):

```css
.history-header {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.new-conversation-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: 500;
  transition: background-color 0.2s;
}

.new-conversation-btn:hover {
  background-color: var(--color-primary-dark);
}

.new-conversation-btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

#### Step 2.2: Add Event Handler to App Component

Open `frontend/src/components/App/App.vue`

**Update template** (add new event handler):

```vue
<HistoryBar
  :conversations="conversations"
  :active-conversation-id="activeConversationId"
  @select-conversation="handleSelectConversation"
  @new-conversation="handleNewConversation"
/>
```

**Add to script** (add new handler function):

```javascript
// Add after handleSelectConversation
function handleNewConversation() {
  try {
    logger.info('Creating new conversation from button click')
    const { createConversation } = useConversations()
    createConversation()
    saveToStorage()
    logger.info('New conversation created successfully')
  } catch (error) {
    logger.error('Failed to create new conversation', error)
    setError('Failed to create new conversation')
  }
}

// Add to return statement
return {
  conversations,
  activeConversationId,
  currentMessages,
  isProcessing,
  status,
  statusType,
  handleSendMessage,
  handleSelectConversation,
  handleNewConversation, // Add this line
}
```

#### Step 2.3: Run Tests (VERIFY THEY PASS)

```bash
# Run unit tests
npm test -- HistoryBar.test.js

# Run E2E tests
npm run test:e2e -- new-conversation.spec.js
```

**Expected**: All tests should now pass ✅

**🚨 CRITICAL**: If tests still fail, debug until they pass. DO NOT proceed to Phase 3 with failing tests.

---

### Phase 3: Refactor (REFINE) 🔄

**Duration**: ~10-15 minutes

Now that tests pass, refactor for code quality while keeping tests green.

#### Potential Refactorings

1. **Extract debounce constant**:
   ```javascript
   const DEBOUNCE_MS = 300

   setTimeout(() => {
     isCreating = false
   }, DEBOUNCE_MS)
   ```

2. **Add CSS variable for button hover color** (if not exists):
   ```css
   :root {
     --color-primary-dark: #0056b3; /* Add if missing */
   }
   ```

3. **Improve button text responsiveness** (optional):
   ```vue
   <button class="new-conversation-btn">
     <span class="btn-text-full">New Conversation</span>
     <span class="btn-text-short">+ New</span>
   </button>
   ```

**After each refactoring**: Run tests to ensure they still pass!

---

## Verification Checklist

Before considering the feature complete:

### Functional Testing

- [ ] Button appears in HistoryBar header
- [ ] Button has correct label ("New Conversation")
- [ ] Clicking button creates a new conversation
- [ ] New conversation appears in history list
- [ ] Chat area clears when new conversation created
- [ ] Previous conversation is preserved in history
- [ ] Unsaved message is discarded (no confirmation)
- [ ] Rapid clicks only create one conversation
- [ ] Empty conversation doesn't prevent button click

### Visual Testing

- [ ] Button styling matches design (primary color, padding, border-radius)
- [ ] Button hover state works (darker background)
- [ ] Button is visible and not overlapping with heading
- [ ] Layout doesn't break on mobile/narrow screens
- [ ] Focus indicator is visible when tabbing to button

### Accessibility Testing

- [ ] Button has `aria-label="Start new conversation"`
- [ ] Button is keyboard accessible (Tab to focus, Enter to activate)
- [ ] Focus indicator meets WCAG contrast requirements (3:1 minimum)
- [ ] Screen reader announces button correctly

### Performance Testing

- [ ] Button click feels instant (< 100ms perceived delay)
- [ ] No UI freezing during conversation creation
- [ ] Page remains responsive during operation

### Test Coverage

- [ ] All unit tests pass (`npm test`)
- [ ] All E2E tests pass (`npm run test:e2e`)
- [ ] Test coverage includes happy path and edge cases
- [ ] Tests were written BEFORE implementation (verified RED → GREEN)

### Code Quality

- [ ] No console errors in browser DevTools
- [ ] No ESLint warnings (`npm run lint`)
- [ ] Code follows existing component patterns
- [ ] Comments explain non-obvious logic (debouncing)

---

## Troubleshooting

### Tests Fail: "Button not found"

**Cause**: Template not updated correctly

**Fix**: Verify button is inside `.history-header` div

---

### Tests Fail: "Event not emitted"

**Cause**: Event handler not added or emits array not updated

**Fix**:
1. Check `emits: ['select-conversation', 'new-conversation']`
2. Verify `emit('new-conversation')` is called in handler

---

### E2E Test Fails: "Button not clickable"

**Cause**: Button might be covered by another element

**Fix**: Check z-index and layout in `.history-header`

---

### Rapid Clicks Create Multiple Conversations

**Cause**: Debounce guard not working

**Fix**: Verify `isCreating` flag is checked at start of handler

---

### Button Styling Looks Wrong

**Cause**: CSS variables not defined or overridden

**Fix**:
1. Check `index.css` for CSS variable definitions
2. Verify no conflicting styles in parent components

---

## Next Steps

After completing this feature:

1. **Run full test suite**: `npm test && npm run test:e2e`
2. **Manual testing**: Open browser and test all scenarios
3. **Create pull request**: Follow PR template
4. **Request code review**: Tag reviewer familiar with Vue components

---

## Files Modified Summary

### Modified Files

```
frontend/src/components/HistoryBar/HistoryBar.vue
frontend/src/components/App/App.vue
```

### New Files

```
frontend/src/components/HistoryBar/HistoryBar.test.js
frontend/tests/e2e/new-conversation.spec.js
```

### Total Changes

- **Lines added**: ~100-150
- **Lines modified**: ~10-20
- **Components modified**: 2
- **Tests added**: 8 unit + 4 E2E = 12 total

---

## Estimated Timeline

| Phase | Duration | Description |
|-------|----------|-------------|
| Phase 1: Write Tests | 30-45 min | Create unit and E2E tests (RED) |
| Phase 2: Implementation | 20-30 min | Add button, event handler (GREEN) |
| Phase 3: Refactoring | 10-15 min | Clean up code (REFINE) |
| Verification | 10-15 min | Run all checks and manual testing |
| **Total** | **70-105 min** | ~1-2 hours for complete implementation |

**For experienced Vue developers**: Can be completed in ~1 hour

**For developers new to Vue**: May take 1.5-2 hours

---

## Resources

### Documentation

- [Vue 3 Composition API](https://vuejs.org/guide/introduction.html)
- [Vitest Testing Guide](https://vitest.dev/guide/)
- [Playwright E2E Testing](https://playwright.dev/docs/intro)

### Project Files

- [Feature Spec](./spec.md)
- [Implementation Plan](./plan.md)
- [Research Document](./research.md)
- [Component Contract](./contracts/component-interface.md)
- [Constitution](../../.specify/memory/constitution.md)

---

## Support

If you get stuck:

1. Review the research.md document for technical decisions
2. Check existing HistoryBar code for patterns
3. Run tests in watch mode (`npm run test:watch`) for rapid feedback
4. Use browser DevTools to inspect component state

**Remember**: Follow TDD! Tests must fail first, then pass after implementation.
