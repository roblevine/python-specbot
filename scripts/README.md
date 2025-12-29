# Scripts Directory

This directory contains utility scripts for running and testing the SpecBot application.

## Available Scripts

### 🚀 Start Development Servers

**`./scripts/start-servers.sh`**

Starts both backend and frontend servers for local development.

**Usage:**
```bash
./scripts/start-servers.sh
```

**What it does:**
- ✅ Checks prerequisites (virtual environment, node_modules)
- 🔧 Creates frontend `.env` file if missing
- 📡 Starts backend server on http://localhost:8000
- 🎨 Starts frontend server on http://localhost:5173
- Runs frontend in foreground (Ctrl+C to stop both)

**Ports:**
- Backend: http://localhost:8000
- Backend API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

**Stop servers:** Press `Ctrl+C` in the terminal

---

### ✅ Run Contract Tests

**`./scripts/run-contract-tests.sh`**

Runs the complete contract testing workflow to verify frontend-backend API compatibility.

**Usage:**
```bash
# Run complete workflow (recommended)
./scripts/run-contract-tests.sh

# With detailed output
./scripts/run-contract-tests.sh --verbose

# Only run frontend snapshot capture
./scripts/run-contract-tests.sh --frontend-only

# Only run backend snapshot replay
./scripts/run-contract-tests.sh --backend-only

# Skip prerequisite checks (faster)
./scripts/run-contract-tests.sh --skip-prereqs
```

**What it does:**
1. **Prerequisites Check** - Verifies dependencies and OpenAPI spec
2. **Frontend Tests** - Captures actual HTTP request formats as snapshots
3. **Snapshot Verification** - Confirms snapshots were generated
4. **Backend Tests** - Replays snapshots to verify backend compatibility

**Exit codes:**
- `0` - All tests passed, no contract mismatches
- `1` - Tests failed or contract mismatch detected

**Documentation:** See `specs/004-contract-snapshot-testing/CONTRACT_TESTING.md`

---

## Common Workflows

### Start Development

```bash
# 1. Start servers
./scripts/start-servers.sh

# 2. Open browser to http://localhost:5173
# 3. Start coding - changes auto-reload!
```

### Before Committing API Changes

```bash
# Run contract tests to verify compatibility
./scripts/run-contract-tests.sh

# If tests pass, commit both code and snapshots
git add specs/contract-snapshots/
git commit -m "Update API contract"
```

### Continuous Integration

```bash
# Run in CI pipeline
./scripts/run-contract-tests.sh --skip-prereqs
```

---

## Script Permissions

All scripts should be executable. If you get "Permission denied":

```bash
chmod +x scripts/*.sh
```

---

## Troubleshooting

### Start Servers Script

**Error: "Backend virtual environment not found"**
```bash
cd backend
python -m venv venv
venv/bin/pip install -r requirements.txt
```

**Error: "Frontend dependencies not installed"**
```bash
cd frontend
npm install
```

**Error: "Port already in use"**
```bash
# Find and kill process using the port
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
kill -9 <PID>
```

### Contract Tests Script

**Error: "No snapshots found"**

Solution: Run frontend tests first to generate snapshots:
```bash
cd frontend && npm test tests/contract/
```

**Error: "Backend rejected snapshot"**

This indicates a **contract mismatch** between frontend and backend!

Solution:
1. Check the error details in the output
2. Fix either frontend or backend to match the contract
3. Update OpenAPI spec if contract intentionally changed

---

## Adding New Scripts

When adding new scripts to this directory:

1. **Make it executable:**
   ```bash
   chmod +x scripts/your-script.sh
   ```

2. **Use repository root:**
   ```bash
   REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
   cd "$REPO_ROOT"
   ```

3. **Add usage comment:**
   ```bash
   # Usage: ./scripts/your-script.sh [options]
   ```

4. **Update this README** with documentation

---

## Related Documentation

- **Quick Start Guide**: `/QUICKSTART.md`
- **Contract Testing**: `/specs/004-contract-snapshot-testing/CONTRACT_TESTING.md`
- **Architecture**: `/architecture.md`
- **Backend Setup**: `/backend/README.md`
