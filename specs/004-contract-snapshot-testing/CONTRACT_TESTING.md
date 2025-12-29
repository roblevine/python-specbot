# Contract Testing Quick Reference

**Feature**: 004-contract-snapshot-testing
**Status**: MVP Implemented (User Stories 1 & 2)

## Overview

The contract testing system automatically captures frontend HTTP requests as snapshots and replays them to the backend to verify compatibility. This prevents contract mismatches like the `conversationId` format bug.

## Quick Start

### Run All Contract Tests (Recommended)

```bash
# From repository root
./scripts/run-contract-tests.sh
```

This single command:
1. ✅ Checks all prerequisites
2. ✅ Runs frontend tests to capture snapshots
3. ✅ Verifies snapshots were generated
4. ✅ Runs backend tests to replay snapshots
5. ✅ Reports results

**Expected output:**
```
✓ Contract testing workflow complete!
✓ Frontend captured actual request formats as snapshots
✓ Backend successfully replayed and processed all snapshots
✓ No contract mismatches detected
```

### Script Options

```bash
# Show detailed test output
./scripts/run-contract-tests.sh --verbose

# Only run frontend snapshot capture
./scripts/run-contract-tests.sh --frontend-only

# Only run backend snapshot replay (requires snapshots to exist)
./scripts/run-contract-tests.sh --backend-only

# Skip prerequisite checks (faster, use when deps already installed)
./scripts/run-contract-tests.sh --skip-prereqs
```

## Manual Testing

### Frontend: Capture Snapshots

```bash
cd frontend
npm test tests/contract/
```

**Output:**
- Snapshots written to: `specs/contract-snapshots/`
- Tests validate requests against OpenAPI spec
- Dynamic data (UUIDs, timestamps) normalized for stable diffs

### Backend: Replay Snapshots

```bash
cd backend
PYTHONPATH=/workspaces/python-specbot/backend venv/bin/pytest tests/contract/test_replay.py -v
```

**Output:**
- Loads all snapshots from `specs/contract-snapshots/`
- Replays each request to backend
- Verifies backend returns 2xx status and valid response structure

## How It Works

### 1. Frontend Snapshot Capture

```javascript
// frontend/tests/contract/sendMessage.test.js
import { captureSnapshot } from '../helpers/contract.js';

it('captures POST /api/v1/messages snapshot', async () => {
  const request = {
    method: 'POST',
    path: '/api/v1/messages',
    headers: { 'Content-Type': 'application/json' },
    body: { message: 'Hello world', conversationId: 'conv-123' }
  };

  await captureSnapshot('sendMessage', request);
  // ✓ Validates against OpenAPI spec
  // ✓ Normalizes dynamic data
  // ✓ Writes to specs/contract-snapshots/sendMessage.json
});
```

### 2. Generated Snapshot

```json
{
  "metadata": {
    "operationId": "sendMessage",
    "capturedAt": "2025-12-29T21:12:48.094Z",
    "frontendVersion": "1.0.0"
  },
  "request": {
    "method": "POST",
    "path": "/api/v1/messages",
    "headers": { "Content-Type": "application/json" },
    "body": {
      "message": "Hello world",
      "conversationId": "conv-00000000-0000-0000-0000-000000000000"
    }
  }
}
```

### 3. Backend Snapshot Replay

```python
# backend/tests/contract/test_replay.py
from tests.helpers.contract import load_snapshots, replay_snapshot

@pytest.mark.parametrize("snapshot", load_snapshots())
def test_backend_handles_frontend_snapshots(client, snapshot):
    response = replay_snapshot(client, snapshot)

    # ✓ Backend must accept frontend's actual request format
    assert response.status_code < 300
```

## Adding New Contract Tests

### 1. Add Frontend Test

Create new test in `frontend/tests/contract/`:

```javascript
import { captureSnapshot } from '../helpers/contract.js';

it('captures newOperation snapshot', async () => {
  const request = {
    method: 'POST',
    path: '/api/v1/new-endpoint',
    headers: { 'Content-Type': 'application/json' },
    body: { /* request body */ }
  };

  await captureSnapshot('newOperation', request);
});
```

### 2. Run Frontend Tests

```bash
cd frontend && npm test tests/contract/
```

A new snapshot file `specs/contract-snapshots/newOperation.json` will be created.

### 3. Run Backend Tests

```bash
cd backend
PYTHONPATH=/workspaces/python-specbot/backend venv/bin/pytest tests/contract/test_replay.py -v
```

The backend test automatically picks up the new snapshot and replays it. **No backend test code changes needed!**

## Troubleshooting

### ❌ Frontend test fails: "Request validation failed"

**Problem:** Request doesn't match OpenAPI schema

**Solution:** Check error message for field-level details. Update request to match OpenAPI spec in:
```
specs/003-backend-api-loopback/contracts/message-api.yaml
```

### ❌ Backend test fails: "Backend rejected snapshot"

**Problem:** Backend cannot process frontend's request format (CONTRACT MISMATCH!)

**Solution:** This is the bug we're trying to catch! Either:
1. Fix backend to accept frontend's format (if frontend is correct)
2. Fix frontend to send correct format (if backend is correct)
3. Update OpenAPI spec if contract intentionally changed

### ❌ "No snapshots found"

**Problem:** Frontend tests haven't run yet

**Solution:**
```bash
# Run frontend tests first to generate snapshots
cd frontend && npm test tests/contract/
```

## Integration with Development Workflow

### Before Committing API Changes

```bash
# Run contract tests to verify compatibility
./scripts/run-contract-tests.sh

# If tests pass, commit both code AND snapshot changes
git add specs/contract-snapshots/
git commit -m "Update API contract for feature XYZ"
```

### Reviewing Pull Requests

If snapshot files changed in PR:
1. Review the diff in `specs/contract-snapshots/`
2. Verify changes are intentional
3. Ensure both frontend and backend tests pass

Contract snapshots are **source of truth** for actual API behavior!

## File Structure

```
specs/
├── contract-snapshots/           # Shared snapshot directory (committed to git)
│   ├── sendMessage.json          # POST /api/v1/messages contract
│   ├── healthCheck.json          # GET /health contract
│   └── .gitkeep

frontend/
└── tests/
    ├── contract/                 # Frontend contract tests
    │   ├── sendMessage.test.js
    │   └── healthCheck.test.js
    └── helpers/
        └── contract.js           # Snapshot capture utilities

backend/
└── tests/
    ├── contract/                 # Backend contract tests
    │   └── test_replay.py
    └── helpers/
        └── contract.py           # Snapshot replay utilities

scripts/
└── run-contract-tests.sh         # Automated workflow script
```

## Performance

- **Frontend snapshot capture**: < 1 second for all operations
- **Backend snapshot replay**: < 1 second for all operations
- **Total workflow**: < 5 seconds end-to-end

## Next Features (Not Yet Implemented)

- **CI Integration** (User Story 3 - P2): Automatic contract validation in GitHub Actions
- **Git Hooks** (User Story 4 - P3): Pre-commit snapshot regeneration
- **Enhanced error messages**: Field-level diffs for validation failures

## Resources

- **Specification**: `specs/004-contract-snapshot-testing/spec.md`
- **Implementation Plan**: `specs/004-contract-snapshot-testing/plan.md`
- **Task List**: `specs/004-contract-snapshot-testing/tasks.md`
- **OpenAPI Contract**: `specs/003-backend-api-loopback/contracts/message-api.yaml`
