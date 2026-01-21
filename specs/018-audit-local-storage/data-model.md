# Data Model: Local Storage Settings

**Feature**: 018-audit-local-storage
**Date**: 2026-01-21

## Overview

This feature defines a simplified localStorage schema for user settings only. All conversation data is stored server-side; localStorage is used exclusively for client-side preferences.

## Entities

### UserSettings

Represents all user preferences stored in browser localStorage.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| version | string | Yes | "2.0.0" | Schema version for migration support |
| settings.sidebarCollapsed | boolean | Yes | false | Whether the sidebar is collapsed |
| settings.selectedModelId | string \| null | Yes | null | ID of the currently selected LLM model |

### Storage Location

- **Key**: `specbot:settings:v2`
- **Storage**: Browser localStorage
- **Format**: JSON string

## Schema Definition

```javascript
// SettingsSchema.js

export const SETTINGS_VERSION = '2.0.0'
export const SETTINGS_KEY = 'specbot:settings:v2'

/**
 * Default settings structure
 */
export const DEFAULT_SETTINGS = {
  sidebarCollapsed: false,
  selectedModelId: null,
}

/**
 * Full schema structure (stored in localStorage)
 */
const schema = {
  version: SETTINGS_VERSION,
  settings: DEFAULT_SETTINGS,
}
```

## Validation Rules

### Version Field
- Must be exactly `"2.0.0"`
- If version mismatch or missing, reset to defaults

### sidebarCollapsed
- Must be boolean
- If invalid type, default to `false`

### selectedModelId
- Must be `null` or non-empty string
- Validation against available models happens at runtime (in useModels)
- Invalid/unavailable model ID falls back to default model

## State Transitions

### On Application Load
```
localStorage.getItem(SETTINGS_KEY)
    ├─ null/undefined → Return DEFAULT_SETTINGS
    ├─ Invalid JSON → Log warning, Return DEFAULT_SETTINGS
    ├─ Version mismatch → Log warning, Return DEFAULT_SETTINGS
    └─ Valid → Return settings object
```

### On Setting Change
```
User changes setting
    → Update in-memory state
    → Immediately persist to localStorage
    → Log debug message
```

### On localStorage Unavailable
```
Try localStorage operation
    └─ Catch error → Log warning, Continue with in-memory only
```

## Relationships

```
┌─────────────────────────────────────────────────────────┐
│                    Browser Storage                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │  specbot:settings:v2                            │    │
│  │  {                                              │    │
│  │    version: "2.0.0",                            │    │
│  │    settings: {                                  │    │
│  │      sidebarCollapsed: boolean,                 │    │
│  │      selectedModelId: string | null             │    │
│  │    }                                            │    │
│  │  }                                              │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
          │                           │
          ▼                           ▼
┌─────────────────────┐    ┌─────────────────────┐
│  useSidebarCollapse │    │     useModels       │
│  ─────────────────  │    │  ───────────────    │
│  - isCollapsed      │    │  - selectedModelId  │
│  - toggle()         │    │  - setSelectedModel │
│  - loadFromStorage  │    │  - initializeModels │
└─────────────────────┘    └─────────────────────┘
```

## Extensibility

To add a new setting:

1. Add field to `DEFAULT_SETTINGS` in `SettingsSchema.js`
2. Add validation in `validateSettings()` if needed
3. Use `saveSetting(key, value)` and `getSetting(key)` in consuming component
4. No schema version change needed for additive changes

Example adding a new setting:
```javascript
// SettingsSchema.js
export const DEFAULT_SETTINGS = {
  sidebarCollapsed: false,
  selectedModelId: null,
  theme: 'light',  // NEW: Add with default value
}

// Component using the new setting
import { getSetting, saveSetting } from '../storage/SettingsStorage.js'

const theme = getSetting('theme', 'light')
saveSetting('theme', 'dark')
```

## Migration from v1.x

**Decision**: No migration - clean break

- Old `chatInterface:v1:data` key is ignored
- Old data remains in localStorage (user can clear manually)
- New settings start with defaults
- Model selection may need to be re-selected once

**Rationale**:
- Migration code adds complexity for a one-time operation
- Old schema contains conversation data we explicitly want to stop using
- Starting fresh is simpler and aligns with the feature goal
