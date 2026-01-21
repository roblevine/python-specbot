# Research: Local Storage Audit and Cleanup

**Feature**: 018-audit-local-storage
**Date**: 2026-01-21

## Current State Analysis

### Existing Storage Architecture

The application currently uses a dual-storage approach:

1. **Server-side (primary)**: File-based JSON storage for conversations
2. **Browser localStorage (secondary)**: Mixed - conversations + settings + fallback

### Files Using localStorage

| File | Usage | To Change |
|------|-------|-----------|
| `frontend/src/storage/LocalStorageAdapter.js` | Conversation + settings persistence | Remove conversation code, simplify to settings-only |
| `frontend/src/storage/StorageSchema.js` | Schema v1.1.0 with conversations array | Rewrite for settings-only schema |
| `frontend/src/composables/useSidebarCollapse.js` | Direct localStorage (`sidebar.collapsed`) | Migrate to use unified adapter |
| `frontend/src/state/useModels.js` | Model selection via adapter | Update to use simplified adapter |
| `frontend/src/state/useConversations.js` | Migration + fallback code | Remove all localStorage dependencies |

### Current Schema (v1.1.0)

```javascript
{
  version: "1.1.0",
  conversations: [...],           // TO REMOVE
  activeConversationId: "...",    // TO REMOVE
  selectedModelId: "gpt-4",       // KEEP
  preferences: {
    sidebarCollapsed: false       // KEEP
  }
}
```

### Separate Key

- `sidebar.collapsed` - String boolean, used by `useSidebarCollapse.js`
- Should be consolidated into main schema

## Decision: New Settings Schema

**Decision**: Create a simplified settings-only schema (v2.0.0)

**Rationale**:
- Breaking change (removing conversations) warrants major version bump
- Clean slate avoids migration complexity from v1.1.0
- Simpler schema = simpler validation = fewer bugs

**Alternatives Considered**:
1. ~~Migrate v1.1.0 → v1.2.0 (removing fields)~~ - Rejected: Still requires migration code for a field we're removing
2. ~~Keep v1.1.0 with empty conversations~~ - Rejected: Leaves dead schema fields

### New Schema (v2.0.0)

```javascript
{
  version: "2.0.0",
  settings: {
    sidebarCollapsed: false,
    selectedModelId: null
  }
}
```

**Benefits**:
- Single `settings` object for all preferences
- Easy to extend: just add fields to `settings`
- No conversation-related fields
- Clear migration path: ignore old data, start fresh

## Decision: Storage Key Change

**Decision**: Use new storage key `specbot:settings:v2`

**Rationale**:
- Clean break from old `chatInterface:v1:data` key
- Old data remains intact (user can clear manually if desired)
- No accidental loading of old conversation data

**Alternatives Considered**:
1. ~~Keep same key~~ - Rejected: Risk of loading old conversation data
2. ~~Clear old key on first load~~ - Rejected: Unnecessary complexity

## Decision: Unified Storage Adapter

**Decision**: Single `SettingsStorage.js` module with simple API

**Rationale**:
- One place for all localStorage logic
- Consistent error handling
- Easy to test and maintain

**API Design**:
```javascript
// Save individual setting (immediate persistence)
saveSetting(key, value)

// Load all settings (on app init)
loadSettings() → { sidebarCollapsed, selectedModelId }

// Get single setting with default
getSetting(key, defaultValue)
```

## Decision: Remove Conversation Fallback

**Decision**: Remove all localStorage fallback code for conversations

**Rationale**:
- Spec assumption: "server is always available for conversation operations"
- Fallback code adds complexity and maintenance burden
- If server is unavailable, show error instead of degraded mode

**Code to Remove**:
- `useConversations.js`: Lines 164-171 (migration check), 203-237 (fallback), 247-295 (migrate function)
- `LocalStorageAdapter.js`: `saveConversations()`, `clearAllData()`
- `StorageSchema.js`: Conversation validation, conversation migration

## Testing Strategy

**Unit Tests Required**:
1. `SettingsStorage.test.js` - New adapter
   - Save/load settings
   - Default values
   - Corrupted data handling
   - localStorage unavailable

2. Update `useSidebarCollapse.test.js`
   - Uses new adapter
   - Persists on change

3. Update `useModels.test.js`
   - Uses new adapter
   - Validates model ID against available models

**Integration Tests**:
- Settings persist across page refresh
- Invalid stored model falls back to default

## Files to Create

| File | Purpose |
|------|---------|
| `frontend/src/storage/SettingsStorage.js` | New unified settings adapter |
| `frontend/src/storage/SettingsSchema.js` | New v2.0.0 schema definition |
| `frontend/tests/unit/SettingsStorage.test.js` | Unit tests |

## Files to Modify

| File | Changes |
|------|---------|
| `frontend/src/composables/useSidebarCollapse.js` | Use SettingsStorage instead of direct localStorage |
| `frontend/src/state/useModels.js` | Use SettingsStorage instead of LocalStorageAdapter |
| `frontend/src/state/useConversations.js` | Remove all localStorage imports and fallback code |

## Files to Delete

| File | Reason |
|------|--------|
| `frontend/src/storage/LocalStorageAdapter.js` | Replaced by SettingsStorage |
| `frontend/src/storage/StorageSchema.js` | Replaced by SettingsSchema |
| `frontend/tests/unit/LocalStorageAdapter.test.js` | Tests for deleted file |
| `frontend/tests/unit/StorageSchema.test.js` | Tests for deleted file |

## Implementation Order (Thin Slices)

### Slice 1: Settings Persistence (P1) - User Story 1 & 2
1. Create `SettingsSchema.js` with v2.0.0 schema
2. Create `SettingsStorage.js` with save/load API
3. Write tests for new storage
4. Update `useSidebarCollapse.js` to use new adapter
5. Update `useModels.js` to use new adapter
6. Verify settings persist across sessions

### Slice 2: Remove Legacy Code (P2) - User Story 3 & 4
1. Remove conversation code from `useConversations.js`
2. Delete `LocalStorageAdapter.js`
3. Delete `StorageSchema.js`
4. Update/delete associated tests
5. Verify app still works with server-only conversations
