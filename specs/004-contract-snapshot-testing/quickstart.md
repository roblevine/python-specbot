# Quickstart Guide: Contract Snapshot Testing

**Feature**: 004-contract-snapshot-testing
**Date**: 2025-12-29
**Audience**: Developers implementing contract tests

This guide shows you how to capture frontend request snapshots and replay them to the backend.

---

## Prerequisites

- **Node.js 18+** (for frontend tests)
- **Python 3.13** (for backend tests)
- **OpenAPI spec** (from feature 003: `specs/003-backend-api-loopback/openapi.json`)
- **Vitest** (already installed in frontend)
- **pytest** (already installed in backend)

---

## Quick Setup (10 minutes)

### Step 1: Install Frontend Dependencies

```bash
cd /workspaces/python-specbot/frontend

npm install --save-dev core-ajv-schema-validator
```

### Step 2: Create Snapshot Directory

```bash
cd /workspaces/python-specbot

mkdir -p specs/contract-snapshots
touch specs/contract-snapshots/.gitkeep
```

### Step 3: Create Frontend Contract Helper

**File**: `frontend/tests/helpers/contract.js`

```javascript
import { validateSchema } from 'core-ajv-schema-validator';
import { writeFileSync } from 'fs';
import openapiSpec from '../../../specs/003-backend-api-loopback/openapi.json';

export function captureSnapshot(operationId, request) {
  // Normalize dynamic data
  const normalized = {
    ...request,
    body: request.body ? normalizeDynamicData(request.body) : null
  };

  const snapshot = {
    metadata: {
      operationId,
      capturedAt: new Date().toISOString()
    },
    request: normalized
  };

  writeFileSync(
    `specs/contract-snapshots/${operationId}.json`,
    JSON.stringify(snapshot, null, 2)
  );
}

function normalizeDynamicData(data) {
  // Replace UUIDs with stable values for git diffs
  const str = JSON.stringify(data);
  const normalized = str.replace(
    /conv-[a-f0-9-]+/g,
    'conv-00000000-0000-0000-0000-000000000000'
  );
  return JSON.parse(normalized);
}
```

### Step 4: Create Backend Contract Helper

**File**: `backend/tests/helpers/contract.py`

```python
import json
from pathlib import Path

def load_snapshots():
    """Load all contract snapshots"""
    snapshot_dir = Path("specs/contract-snapshots")
    return [
        json.load(open(f))
        for f in snapshot_dir.glob("*.json")
        if f.name != ".gitkeep"
    ]

def replay_snapshot(client, snapshot):
    """Replay snapshot request to backend"""
    req = snapshot["request"]
    response = client.request(
        method=req["method"],
        path=req["path"],
        headers=req.get("headers", {}),
        json=req.get("body")
    )
    return response
```

---

## Usage

### Capture Snapshots (Frontend)

**Example Test**: `frontend/tests/contract/messages.test.js`

```javascript
import { describe, it, expect } from 'vitest';
import { captureSnapshot } from '../helpers/contract';

describe('Message API Contract', () => {
  it('captures POST /api/v1/messages snapshot', () => {
    const request = {
      method: 'POST',
      path: '/api/v1/messages',
      headers: { 'Content-Type': 'application/json' },
      body: {
        message: 'hello',
        conversationId: 'conv-123-456'
      }
    };

    captureSnapshot('sendMessage', request);
  });
});
```

**Run**:
```bash
cd frontend
npm test tests/contract/
```

**Result**: `specs/contract-snapshots/sendMessage.json` created

### Replay Snapshots (Backend)

**Example Test**: `backend/tests/contract/test_replay.py`

```python
import pytest
from tests.helpers.contract import load_snapshots, replay_snapshot

@pytest.mark.parametrize("snapshot", load_snapshots())
def test_backend_handles_frontend_snapshots(client, snapshot):
    """Verify backend can handle actual frontend requests"""
    response = replay_snapshot(client, snapshot)

    assert response.status_code < 300, (
        f"Backend rejected snapshot {snapshot['metadata']['operationId']}: "
        f"{response.text}"
    )
```

**Run**:
```bash
cd backend
source venv/bin/activate
PYTHONPATH=/workspaces/python-specbot/backend pytest tests/contract/ -v
```

---

## Workflow

### Development Flow

1. **Modify frontend API client** → Update request format
2. **Run frontend tests** → Snapshots auto-regenerate
3. **Review snapshot diff** → Verify changes are intentional
4. **Run backend tests** → Verify backend can handle new format
5. **Commit snapshot changes** → Snapshots are version-controlled artifacts

### CI Pipeline Flow

```bash
# Run frontend tests (generates snapshots)
cd frontend && npm test

# Run backend contract tests (replays snapshots)
cd backend && pytest tests/contract/

# Check snapshots are committed
git diff --exit-code specs/contract-snapshots/ || (
  echo "ERROR: Contract snapshots changed but not committed"
  exit 1
)
```

---

## Troubleshooting

### Snapshot validation fails

**Error**: `Request validation failed: message is required`

**Fix**: Ensure request matches OpenAPI schema in `specs/003-backend-api-loopback/openapi.json`

### Backend replay fails

**Error**: `Backend rejected snapshot sendMessage: 422 Unprocessable Entity`

**Fix**: Backend doesn't support frontend's request format - this is a contract break! Fix backend to match contract.

### Snapshots not found

**Error**: `FileNotFoundError: specs/contract-snapshots`

**Fix**: Run frontend tests first to generate snapshots before backend tests

---

## Next Steps

- Add contract tests to CI pipeline (User Story 3 - P2)
- Set up git hooks for automatic snapshot regeneration (User Story 4 - P3)
- Add contract tests for all API operations beyond POST /api/v1/messages
