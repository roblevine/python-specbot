# Quickstart: Local Storage Audit Implementation

**Feature**: 018-audit-local-storage
**Date**: 2026-01-21

## Overview

This guide covers implementing the simplified localStorage settings system. The goal is to:
1. Create a new settings-only storage mechanism
2. Remove all conversation-related localStorage code
3. Consolidate scattered localStorage usage

## Prerequisites

- Node.js and npm installed
- Frontend dev server runnable (`npm run dev` in `/frontend`)
- Vitest for testing (`npm test`)

## Implementation Steps

### Step 1: Create New Settings Schema

Create `frontend/src/storage/SettingsSchema.js`:

```javascript
/**
 * Settings Schema v2.0.0
 * Simple user preferences storage - no conversation data
 */

export const SETTINGS_VERSION = '2.0.0'
export const SETTINGS_KEY = 'specbot:settings:v2'

export const DEFAULT_SETTINGS = {
  sidebarCollapsed: false,
  selectedModelId: null,
}

export function createDefaultSettings() {
  return {
    version: SETTINGS_VERSION,
    settings: { ...DEFAULT_SETTINGS },
  }
}

export function validateSettings(data) {
  // Validation logic - return { isValid, data, error }
}
```

### Step 2: Create Settings Storage Adapter

Create `frontend/src/storage/SettingsStorage.js`:

```javascript
/**
 * Settings Storage Adapter
 * Unified interface for all localStorage settings operations
 */

import { SETTINGS_KEY, createDefaultSettings, validateSettings } from './SettingsSchema.js'

export function loadSettings() {
  // Load and validate from localStorage
}

export function saveSetting(key, value) {
  // Update single setting and persist
}

export function getSetting(key, defaultValue = null) {
  // Get single setting with fallback
}
```

### Step 3: Write Tests First (TDD)

Create `frontend/tests/unit/SettingsStorage.test.js`:

```javascript
import { describe, it, expect, beforeEach } from 'vitest'
import { loadSettings, saveSetting, getSetting } from '../../src/storage/SettingsStorage.js'

describe('SettingsStorage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  describe('loadSettings', () => {
    it('returns defaults when no data exists', () => {
      const settings = loadSettings()
      expect(settings.sidebarCollapsed).toBe(false)
      expect(settings.selectedModelId).toBe(null)
    })

    it('loads persisted settings', () => {
      // Setup and test
    })

    it('returns defaults for corrupted data', () => {
      localStorage.setItem('specbot:settings:v2', 'invalid json')
      const settings = loadSettings()
      expect(settings.sidebarCollapsed).toBe(false)
    })
  })

  describe('saveSetting', () => {
    it('persists setting immediately', () => {
      saveSetting('sidebarCollapsed', true)
      const settings = loadSettings()
      expect(settings.sidebarCollapsed).toBe(true)
    })
  })
})
```

### Step 4: Update useSidebarCollapse

Modify `frontend/src/composables/useSidebarCollapse.js`:

```javascript
// BEFORE: Direct localStorage
localStorage.getItem('sidebar.collapsed')
localStorage.setItem('sidebar.collapsed', value)

// AFTER: Use SettingsStorage
import { getSetting, saveSetting } from '../storage/SettingsStorage.js'

const loadFromStorage = () => {
  isCollapsed.value = getSetting('sidebarCollapsed', false)
}

watch(isCollapsed, (newValue) => {
  saveSetting('sidebarCollapsed', newValue)
})
```

### Step 5: Update useModels

Modify `frontend/src/state/useModels.js`:

```javascript
// BEFORE: Uses old LocalStorageAdapter
import { loadConversations, saveSelectedModel } from '../storage/LocalStorageAdapter.js'

// AFTER: Uses SettingsStorage
import { getSetting, saveSetting } from '../storage/SettingsStorage.js'

function loadSelectedModelFromStorage() {
  return getSetting('selectedModelId', null)
}

function setSelectedModel(modelId) {
  selectedModelId.value = modelId
  saveSetting('selectedModelId', modelId)
}
```

### Step 6: Remove localStorage from useConversations

Modify `frontend/src/state/useConversations.js`:

```javascript
// REMOVE these imports:
import { saveConversations, loadConversations, clearAllData } from '../storage/LocalStorageAdapter.js'

// REMOVE these code blocks:
// - migrateFromLocalStorage function (lines 247-295)
// - Migration check in loadFromStorage (lines 164-171)
// - Fallback to localStorage in catch block (lines 203-237)
// - hasMigrated ref and usage

// SIMPLIFY loadFromStorage to only use server API
async function loadFromStorage() {
  isLoading.value = true
  loadError.value = null

  try {
    const response = await apiGetConversations()
    // ... server-only logic
  } catch (error) {
    loadError.value = error.message || 'Failed to load conversations'
    // NO localStorage fallback - just show error
  } finally {
    isLoading.value = false
  }
}
```

### Step 7: Delete Old Storage Files

```bash
# Delete old storage files
rm frontend/src/storage/LocalStorageAdapter.js
rm frontend/src/storage/StorageSchema.js

# Delete old tests
rm frontend/tests/unit/LocalStorageAdapter.test.js
rm frontend/tests/unit/StorageSchema.test.js
```

### Step 8: Run Tests

```bash
cd frontend
npm test
```

Verify:
- New SettingsStorage tests pass
- Updated composable tests pass
- No import errors from deleted files

## Verification Checklist

- [ ] New `SettingsSchema.js` created with v2.0.0 schema
- [ ] New `SettingsStorage.js` created with save/load API
- [ ] `useSidebarCollapse.js` uses new adapter
- [ ] `useModels.js` uses new adapter
- [ ] `useConversations.js` has no localStorage code
- [ ] Old `LocalStorageAdapter.js` deleted
- [ ] Old `StorageSchema.js` deleted
- [ ] All tests pass
- [ ] Settings persist across browser refresh
- [ ] App works with server-only conversations

## Common Issues

### "Module not found" errors
After deleting old files, search for any remaining imports:
```bash
grep -r "LocalStorageAdapter" frontend/src/
grep -r "StorageSchema" frontend/src/
```

### Settings not persisting
Check browser console for localStorage errors. In private browsing mode, settings won't persist - this is expected behavior.

### Model selection resets
Expected on first load after migration. User needs to re-select their preferred model once.
