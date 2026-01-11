# API Contracts: UI Redesign

**Feature**: 007-ui-redesign
**Date**: 2026-01-11

## Overview

This feature does **not introduce any API changes**. All modifications are frontend-only (CSS and client-side JavaScript).

## Rationale

The UI redesign affects only the presentation layer:
- CSS variable updates in `global.css`
- Component style modifications
- New composable for sidebar state management
- LocalStorage schema extension (client-side only)

**No server communication is added, modified, or removed.**

## Existing API Contracts (Unchanged)

The following existing API contracts remain valid and are **not affected** by this feature:

### 1. POST `/api/chat/send`
**Status**: ✅ Unchanged
**Reason**: UI changes don't affect message sending logic

### 2. GET `/api/health`
**Status**: ✅ Unchanged
**Reason**: Health check endpoint unaffected by visual changes

## Contract Test Status

**Impact**: None

Since no API contracts are modified, existing contract tests remain valid:
- `frontend/tests/contract/sendMessage.test.js` - ✅ No changes needed
- `frontend/tests/contract/healthCheck.test.js` - ✅ No changes needed
- `backend/tests/contract/*` - ✅ No changes needed

## LocalStorage "Contract" (Client-Side Only)

While not an API contract, the LocalStorage schema acts as an implicit contract between app versions:

### Schema Version Update

**Current**: v1.0.0
**New**: v1.1.0

**Change**:
```diff
{
  version: "1.1.0",
  conversations: [...],
  activeConversationId: string | null,
+ preferences: {
+   sidebarCollapsed: boolean
+ }
}
```

**Backward Compatibility**: ✅ Yes
- v1.1.0 code can read v1.0.0 data (adds defaults)
- v1.0.0 code can read v1.1.0 data (ignores unknown fields)

**Migration**: Automatic on first load

**Testing**:
- Unit tests for schema validation in `StorageSchema.test.js`
- Integration tests for migration logic

## Validation

Since this feature has no API changes, the standard contract testing workflow does not apply:

- ❌ No OpenAPI spec updates required
- ❌ No contract snapshot generation needed
- ❌ No backend contract replay required
- ✅ Existing contract tests continue to pass
- ✅ LocalStorage schema tested via unit tests

## Summary

**API Impact**: None
**Contract Changes**: None
**Contract Tests**: No updates required
**Backward Compatibility**: Full (LocalStorage schema migration only)
