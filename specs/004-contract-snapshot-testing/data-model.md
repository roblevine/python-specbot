# Data Model: Consumer-Driven Contract Testing with Snapshot Validation

**Feature**: 004-contract-snapshot-testing
**Date**: 2025-12-29
**Status**: Phase 1 Design

This document defines the data entities, snapshot structure, and validation rules for the contract testing system.

---

## Overview

The contract testing system captures frontend HTTP requests as JSON snapshots, validates them against OpenAPI specs, and replays them to the backend. All entities are file-based artifacts stored in git.

**Storage Strategy**: Snapshots stored as JSON files in `specs/contract-snapshots/` directory, committed to version control.

---

## Entities

### 1. Contract Snapshot

**Description**: JSON file capturing an actual HTTP request from frontend tests.

**File Location**: `specs/contract-snapshots/{operation-name}.json`

**Fields**:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `metadata.operationId` | string | Yes | OpenAPI operation ID (e.g., "sendMessage") |
| `metadata.capturedAt` | string (ISO-8601) | Yes | Timestamp when snapshot was captured |
| `metadata.frontendVersion` | string | No | Frontend version that generated snapshot |
| `request.method` | string | Yes | HTTP method (GET, POST, PUT, DELETE, etc.) |
| `request.path` | string | Yes | API endpoint path (e.g., "/api/v1/messages") |
| `request.headers` | object | Yes | HTTP headers (Content-Type, Authorization, etc.) |
| `request.body` | object/null | Yes | Request payload (null for GET requests) |

**Example (send-message.json)**:
```json
{
  "metadata": {
    "operationId": "sendMessage",
    "capturedAt": "2025-12-29T10:00:00.000Z",
    "frontendVersion": "1.0.0"
  },
  "request": {
    "method": "POST",
    "path": "/api/v1/messages",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": {
      "message": "Hello world",
      "conversationId": "conv-a1b2c3d4-5678-90ab-cdef-123456789abc"
    }
  }
}
```

**Normalization Rules** (FR-027):
- Dynamic timestamps → Stable placeholder: `"2025-01-01T00:00:00.000Z"`
- UUIDs in body → Stable format: `"00000000-0000-0000-0000-000000000000"`
- Captured metadata timestamp → Real timestamp preserved

---

### 2. API Request Format

**Description**: Structure of HTTP requests sent by frontend API clients.

**Source**: Frontend `src/services/api.js` (or similar)

**Validation**:
- MUST match OpenAPI operation schema
- MUST include required headers (Content-Type for POST/PUT)
- MUST use correct HTTP method for operation

**Example Request**:
```javascript
// Frontend API client code
const response = await fetch('/api/v1/messages', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: userInput,
    conversationId: currentConversationId
  })
});
```

**Captured As Snapshot**:
```json
{
  "request": {
    "method": "POST",
    "path": "/api/v1/messages",
    "headers": { "Content-Type": "application/json" },
    "body": {
      "message": "hello",
      "conversationId": "conv-123"
    }
  }
}
```

---

### 3. OpenAPI Specification

**Description**: Single source of truth for API contracts (from feature 003).

**File Location**: `specs/003-backend-api-loopback/openapi.json`

**Used For**:
- Validating frontend snapshots before writing to disk
- Validating backend responses during replay tests
- Identifying operation IDs for snapshot naming

**Example Operation**:
```yaml
paths:
  /api/v1/messages:
    post:
      operationId: sendMessage
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [message]
              properties:
                message:
                  type: string
                  minLength: 1
                conversationId:
                  type: string
                  pattern: "^conv-[a-f0-9-]+$"
```

---

## Validation Rules

### Frontend Snapshot Generation (FR-001 to FR-009)

| Rule | Description | Error Handling |
|------|-------------|----------------|
| VR-001 | Captured request MUST validate against OpenAPI schema | Fail test with field-level error |
| VR-002 | Snapshot file MUST be valid JSON | Fail snapshot write |
| VR-003 | Dynamic data MUST be normalized | Auto-normalize before write |
| VR-004 | File size MUST be < 1MB | Fail test with size warning |

### Backend Snapshot Replay (FR-010 to FR-014)

| Rule | Description | Error Handling |
|------|-------------|----------------|
| VR-005 | All snapshots in directory MUST be loaded | Fail if directory missing |
| VR-006 | Replayed request MUST match snapshot exactly | Fail test with diff |
| VR-007 | Backend response MUST be 2xx status | Fail test with backend error |
| VR-008 | Response MUST validate against OpenAPI schema | Fail test with schema error |

---

## Directory Structure

```
specs/
├── contract-snapshots/           # Shared snapshot directory
│   ├── send-message.json         # POST /api/v1/messages
│   ├── get-health.json           # GET /health
│   └── .gitkeep
├── 003-backend-api-loopback/
│   └── openapi.json              # API contract source of truth
└── 004-contract-snapshot-testing/
    ├── spec.md
    ├── plan.md
    ├── research.md
    └── data-model.md             # This file
```

---

## Frontend Test Helper (Vitest)

**File**: `frontend/tests/helpers/contract.js`

```javascript
import { validateSchema } from 'core-ajv-schema-validator';
import openapiSpec from '../../../specs/003-backend-api-loopback/openapi.json';
import { writeFileSync } from 'fs';

export async function captureSnapshot(operationId, request) {
  // Validate request against OpenAPI
  const validation = validateRequest(operationId, request);
  if (!validation.valid) {
    throw new Error(`Request validation failed: ${validation.errors.join(', ')}`);
  }

  // Normalize dynamic data
  const normalized = normalizeRequest(request);

  // Build snapshot
  const snapshot = {
    metadata: {
      operationId,
      capturedAt: new Date().toISOString(),
      frontendVersion: '1.0.0'
    },
    request: normalized
  };

  // Write to file
  const filename = `specs/contract-snapshots/${operationId}.json`;
  writeFileSync(filename, JSON.stringify(snapshot, null, 2));
}
```

---

## Backend Test Helper (pytest)

**File**: `backend/tests/helpers/contract.py`

```python
import json
from pathlib import Path
from openapi_core import Spec
from openapi_core.validation.request import validate_request

def load_snapshots():
    """Load all contract snapshots"""
    snapshot_dir = Path("specs/contract-snapshots")
    snapshots = []
    for file in snapshot_dir.glob("*.json"):
        with open(file) as f:
            snapshots.append(json.load(f))
    return snapshots

def replay_snapshot(client, snapshot):
    """Replay snapshot to backend and validate response"""
    req = snapshot["request"]
    response = client.request(
        method=req["method"],
        path=req["path"],
        headers=req["headers"],
        json=req.get("body")
    )

    assert response.status_code < 300, f"Backend rejected request: {response.text}"
    return response
```

---

## References

- **Feature Spec**: `specs/004-contract-snapshot-testing/spec.md`
- **Research**: `specs/004-contract-snapshot-testing/research.md`
- **OpenAPI Spec**: `specs/003-backend-api-loopback/openapi.json`
