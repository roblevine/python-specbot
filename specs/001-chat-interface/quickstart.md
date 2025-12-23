# Quickstart Guide: Chat Interface Development

**Feature**: Chat Interface
**Date**: 2025-12-23
**Prerequisites**: Node.js 18+ installed

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Testing](#testing)
5. [Building for Production](#building-for-production)
6. [Troubleshooting](#troubleshooting)

---

## Initial Setup

### 1. Create Project Directory

```bash
# Navigate to repository root
cd /workspaces/python-specbot

# Create frontend directory
mkdir -p frontend
cd frontend
```

### 2. Initialize Node.js Project

```bash
# Initialize package.json
npm init -y

# Update package.json name
npm pkg set name="chat-interface"
npm pkg set version="0.1.0"
npm pkg set type="module"
```

### 3. Install Dependencies

```bash
# Core dependencies
npm install vue@^3.4.0

# Build tool
npm install -D vite@^5.0.0
npm install -D @vitejs/plugin-vue@^5.0.0

# Testing dependencies
npm install -D vitest@^1.0.0
npm install -D @vue/test-utils@^2.4.0
npm install -D @testing-library/vue@^9.0.0
npm install -D playwright@^1.40.0
npm install -D @playwright/test@^1.40.0

# Code quality
npm install -D eslint@^8.56.0
npm install -D eslint-plugin-vue@^9.19.0
npm install -D prettier@^3.1.0
```

### 4. Create Configuration Files

**vite.config.js**:
```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  },
  test: {
    environment: 'jsdom',
    globals: true
  }
})
```

**.eslintrc.json**:
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:vue/vue3-recommended"
  ],
  "env": {
    "browser": true,
    "es2022": true,
    "node": true
  },
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  }
}
```

**.prettierrc.json**:
```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

**playwright.config.js**:
```javascript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
})
```

### 5. Add Scripts to package.json

```bash
npm pkg set scripts.dev="vite"
npm pkg set scripts.build="vite build"
npm pkg set scripts.preview="vite preview"
npm pkg set scripts.test="vitest"
npm pkg set scripts.test:watch="vitest --watch"
npm pkg set scripts.test:e2e="playwright test"
npm pkg set scripts.test:e2e:ui="playwright test --ui"
npm pkg set scripts.lint="eslint src --ext .js,.vue"
npm pkg set scripts.lint:fix="eslint src --ext .js,.vue --fix"
npm pkg set scripts.format="prettier --write \"src/**/*.{js,vue,css}\""
```

### 6. Create Directory Structure

```bash
mkdir -p src/components/{App,ChatArea,HistoryBar,StatusBar,InputArea}
mkdir -p src/state
mkdir -p src/storage
mkdir -p src/utils
mkdir -p public/styles
mkdir -p tests/{unit,integration,e2e}
```

### 7. Create Entry Point Files

**public/index.html**:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chat Interface</title>
  <link rel="stylesheet" href="/styles/global.css">
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/index.js"></script>
</body>
</html>
```

**src/index.js**:
```javascript
import { createApp } from 'vue'
import App from './components/App/App.vue'

createApp(App).mount('#app')
```

**public/styles/global.css**:
```css
:root {
  --color-primary: #4a90e2;
  --color-background: #ffffff;
  --color-text: #333333;
  --color-border: #e0e0e0;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  color: var(--color-text);
  background-color: var(--color-background);
}

#app {
  height: 100vh;
  width: 100vw;
}
```

---

## Project Structure

After setup, your structure should look like:

```
frontend/
├── node_modules/
├── public/
│   ├── index.html
│   └── styles/
│       └── global.css
├── src/
│   ├── components/
│   │   ├── App/
│   │   │   ├── App.vue          # Create next
│   │   │   └── App.css
│   │   ├── ChatArea/
│   │   ├── HistoryBar/
│   │   ├── StatusBar/
│   │   └── InputArea/
│   ├── state/
│   │   ├── ConversationManager.js
│   │   ├── MessageManager.js
│   │   └── AppState.js
│   ├── storage/
│   │   ├── LocalStorageAdapter.js
│   │   └── StorageSchema.js
│   ├── utils/
│   │   ├── logger.js
│   │   ├── validators.js
│   │   └── idGenerator.js
│   └── index.js
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .eslintrc.json
├── .prettierrc.json
├── package.json
├── playwright.config.js
└── vite.config.js
```

---

## Development Workflow

### TDD Workflow (Test-First Development)

**This project follows strict TDD** per Principle III:

1. **Write Test First**:
   ```bash
   # Create test file
   touch tests/unit/ConversationManager.test.js

   # Start test watcher
   npm run test:watch
   ```

2. **Write Failing Test**:
   ```javascript
   // tests/unit/ConversationManager.test.js
   import { describe, it, expect } from 'vitest'
   import { useConversations } from '../../src/state/ConversationManager.js'

   describe('useConversations', () => {
     it('should initialize with empty conversations', () => {
       const { conversations } = useConversations()
       expect(conversations.value).toEqual([])
     })
   })
   ```

3. **Run Test - See It Fail** (RED):
   ```bash
   # Test should fail (module doesn't exist yet)
   ✗ should initialize with empty conversations
   ```

4. **Implement Minimum Code to Pass** (GREEN):
   ```javascript
   // src/state/ConversationManager.js
   import { ref } from 'vue'

   export function useConversations() {
     const conversations = ref([])
     return { conversations }
   }
   ```

5. **Run Test - See It Pass**:
   ```bash
   ✓ should initialize with empty conversations
   ```

6. **Refactor While Tests Stay Green**:
   - Improve code structure
   - Extract functions
   - Optimize performance
   - Tests continue passing

7. **Repeat for Next Feature**

### Start Development Server

```bash
# Start Vite dev server (http://localhost:5173)
npm run dev
```

**Features**:
- Hot Module Replacement (HMR) - changes reflect instantly
- Fast refresh for Vue components
- Detailed error overlay in browser

### Run Tests During Development

```bash
# Unit & Integration tests in watch mode
npm run test:watch

# Run all tests once
npm run test

# E2E tests (requires dev server running)
npm run test:e2e

# E2E tests with UI
npm run test:e2e:ui
```

### Code Quality Checks

```bash
# Check linting
npm run lint

# Fix linting issues automatically
npm run lint:fix

# Format code
npm run format
```

---

## Testing

### Unit Tests (Vitest)

Test individual functions and composables in isolation.

**Example**: `tests/unit/idGenerator.test.js`
```javascript
import { describe, it, expect } from 'vitest'
import { generateId } from '../../src/utils/idGenerator.js'

describe('generateId', () => {
  it('should generate UUIDs with correct prefix', () => {
    const id = generateId('conv')
    expect(id).toMatch(/^conv-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i)
  })

  it('should generate unique IDs', () => {
    const id1 = generateId('msg')
    const id2 = generateId('msg')
    expect(id1).not.toBe(id2)
  })
})
```

### Integration Tests (Vitest + Testing Library)

Test component interactions and data flow.

**Example**: `tests/integration/conversation-persistence.test.js`
```javascript
import { describe, it, expect, beforeEach } from 'vitest'
import { useConversations } from '../../src/state/ConversationManager.js'

describe('Conversation Persistence', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('should save and load conversations', async () => {
    const { createConversation, addMessage, saveToStorage, loadFromStorage, conversations } = useConversations()

    // Create conversation and add message
    createConversation()
    const convId = conversations.value[0].id
    addMessage(convId, { text: 'Hello', sender: 'user' })

    // Save to storage
    await saveToStorage()

    // Clear state and reload
    conversations.value = []
    await loadFromStorage()

    // Verify data persisted
    expect(conversations.value).toHaveLength(1)
    expect(conversations.value[0].messages).toHaveLength(1)
  })
})
```

### E2E Tests (Playwright)

Test complete user workflows across browsers.

**Example**: `tests/e2e/send-message.test.js`
```javascript
import { test, expect } from '@playwright/test'

test('user can send message and see loopback', async ({ page }) => {
  await page.goto('/')

  // Type message
  await page.fill('[data-testid="message-input"]', 'Hello world')

  // Click send
  await page.click('[data-testid="send-button"]')

  // Verify user message appears
  await expect(page.locator('[data-testid="message-user"]').last()).toContainText('Hello world')

  // Verify loopback response appears
  await expect(page.locator('[data-testid="message-system"]').last()).toContainText('Hello world')

  // Verify input cleared
  await expect(page.locator('[data-testid="message-input"]')).toHaveValue('')
})
```

### Test Coverage

```bash
# Run tests with coverage report
npm run test -- --coverage

# Coverage targets (per constitution):
# - State management: 80%+
# - Storage modules: 80%+
# - Utils: 80%+
# - Components: 70%+
```

---

## Building for Production

### Create Production Build

```bash
# Build optimized bundle
npm run build

# Output: frontend/dist/
```

### Preview Production Build

```bash
# Serve production build locally
npm run preview

# Opens http://localhost:4173
```

### Production Build Checklist

- [ ] All tests passing
- [ ] Linting passes
- [ ] Bundle size < 5MB (check `dist/` folder size)
- [ ] Tested in Chrome, Firefox, Safari, Edge (latest 2 versions)
- [ ] Verified LocalStorage persistence works
- [ ] Performance meets criteria (SC-001 through SC-008)

---

## Troubleshooting

### Issue: "Failed to resolve module"

**Cause**: Missing dependency or incorrect import path

**Solution**:
```bash
# Install missing dependency
npm install <package-name>

# Or check import path is correct
# Use relative paths: './Component.vue' not 'Component.vue'
```

### Issue: Tests failing with "ReferenceError: localStorage is not defined"

**Cause**: Vitest doesn't have DOM environment by default

**Solution**: Ensure `vite.config.js` has:
```javascript
test: {
  environment: 'jsdom',
  globals: true
}
```

### Issue: HMR not working

**Cause**: Vite dev server not detecting file changes

**Solution**:
```bash
# Restart dev server
# Ctrl+C, then npm run dev
```

### Issue: E2E tests timing out

**Cause**: Dev server not started or wrong port

**Solution**:
```bash
# Ensure dev server running on port 5173
npm run dev

# In another terminal:
npm run test:e2e
```

### Issue: LocalStorage quota exceeded

**Cause**: Too much test data or real usage data

**Solution**:
```javascript
// Clear storage in browser DevTools:
localStorage.clear()

// Or programmatically:
import { clearAllData } from './storage/LocalStorageAdapter.js'
await clearAllData()
```

---

## Next Steps

1. **Follow TDD Workflow**: Write tests first, then implement
2. **Start with P1 User Story**: Send and View Message Loopback
3. **Implement Components**: Follow contracts in `contracts/ComponentInterfaces.md`
4. **Implement Storage**: Follow contracts in `contracts/StorageInterface.md`
5. **Verify Against Success Criteria**: Test all SC-001 through SC-008
6. **Run Full Test Suite**: Unit + Integration + E2E
7. **Build Production Bundle**: `npm run build`

---

## Quick Reference Commands

```bash
# Development
npm run dev              # Start dev server
npm run test:watch       # Run tests in watch mode

# Testing
npm run test             # Run unit/integration tests
npm run test:e2e         # Run E2E tests
npm run test -- --coverage  # Test with coverage

# Code Quality
npm run lint             # Check linting
npm run format           # Format code

# Production
npm run build            # Build for production
npm run preview          # Preview production build
```

---

## Resources

- [Vue.js 3 Documentation](https://vuejs.org/guide/)
- [Vite Documentation](https://vitejs.dev/guide/)
- [Vitest Documentation](https://vitest.dev/guide/)
- [Playwright Documentation](https://playwright.dev/docs/intro)
- [Project Spec](./spec.md)
- [Data Model](./data-model.md)
- [Component Contracts](./contracts/ComponentInterfaces.md)
- [Storage Contracts](./contracts/StorageInterface.md)
