# Quickstart Guide: Backend API Loopback

**Feature**: 003-backend-api-loopback
**Date**: 2025-12-28
**Audience**: Developers implementing or testing this feature

This guide helps you quickly set up and test the backend API loopback feature.

---

## Prerequisites

- **Python 3.13** (confirmed in devcontainer)
- **Node.js** (for frontend - already installed in devcontainer)
- **Git** (for version control)
- **Terminal** (bash/zsh)

---

## Quick Setup (5 minutes)

### Step 1: Create Backend Directory Structure

```bash
cd /workspaces/python-specbot

# Create backend directory structure
mkdir -p backend/src/api/routes
mkdir -p backend/src/services
mkdir -p backend/src/middleware
mkdir -p backend/src/utils
mkdir -p backend/tests/contract
mkdir -p backend/tests/integration
mkdir -p backend/tests/unit
```

### Step 2: Create requirements.txt

```bash
cd backend
cat > requirements.txt <<'EOF'
# Core framework
fastapi[standard]==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.10.0

# HTTP client for testing
httpx==0.28.0

# Testing
pytest==8.3.0
pytest-asyncio==0.24.0
pytest-cov==4.1.0

# Contract testing
openapi-core==0.18.2
pyyaml==6.0.1

# Environment configuration
python-dotenv==1.0.0
EOF
```

### Step 3: Create Virtual Environment and Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Create .env File

```bash
cat > .env <<'EOF'
# Backend API Configuration
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:5173
LOG_LEVEL=DEBUG
EOF
```

### Step 5: Verify Installation

```bash
# Check Python version
python --version
# Expected: Python 3.13.x

# Check pip packages
pip list | grep fastapi
# Expected: fastapi 0.115.0

pip list | grep pytest
# Expected: pytest 8.3.0
```

---

## Development Workflow

### Terminal 1: Run Backend Server

```bash
cd /workspaces/python-specbot/backend
source venv/bin/activate
python main.py
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Access**:
- API Endpoint: http://localhost:8000/api/v1/messages
- Auto-generated Docs: http://localhost:8000/docs (Swagger UI)
- Alternative Docs: http://localhost:8000/redoc (ReDoc)

### Terminal 2: Run Frontend Server

```bash
cd /workspaces/python-specbot/frontend
npm run dev
```

**Expected Output**:
```
  VITE v5.0.0  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Access**:
- Frontend: http://localhost:5173

---

## Testing the API

### Option 1: Interactive API Docs (Recommended for Quick Testing)

1. Open http://localhost:8000/docs in browser
2. Click **POST /api/v1/messages**
3. Click **Try it out**
4. Enter test payload:
   ```json
   {
     "message": "Hello world"
   }
   ```
5. Click **Execute**
6. See response:
   ```json
   {
     "status": "success",
     "message": "api says: Hello world",
     "timestamp": "2025-12-28T10:00:01.234Z"
   }
   ```

### Option 2: cURL Command Line

```bash
# Basic message
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello world"}'

# Expected response:
# {"status":"success","message":"api says: Hello world","timestamp":"2025-12-28T..."}

# Message with special characters
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Test 🚀"}'

# Test error handling (empty message)
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"message": ""}'

# Expected response:
# {"status":"error","error":"Message cannot be empty","timestamp":"2025-12-28T..."}
```

### Option 3: Python Script

```bash
# Create test script
cat > test_api.py <<'EOF'
import httpx

BASE_URL = "http://localhost:8000"

def test_loopback():
    response = httpx.post(
        f"{BASE_URL}/api/v1/messages",
        json={"message": "Hello world"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_loopback()
EOF

# Run test script
python test_api.py
```

### Option 4: Frontend Integration Test

1. Open http://localhost:5173 in browser
2. Type "Hello world" in message input
3. Click Send
4. Verify chat area shows:
   - **User**: "Hello world"
   - **System**: "api says: Hello world"

---

## Running Tests (TDD Workflow)

### Run All Tests

```bash
cd /workspaces/python-specbot/backend
source venv/bin/activate

# Run all tests with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html

# Open coverage report in browser
# HTML report saved to htmlcov/index.html
```

### Run Specific Test Categories

```bash
# Contract tests only (OpenAPI schema validation)
pytest tests/contract/ -v

# Integration tests only (full HTTP flow)
pytest tests/integration/ -v

# Unit tests only (business logic)
pytest tests/unit/ -v
```

### Run Tests with Markers

```bash
# Run only contract tests
pytest -m contract -v

# Run only integration tests
pytest -m integration -v

# Run only unit tests
pytest -m unit -v
```

---

## Common Tasks

### Check Backend Server Status

```bash
# Health check endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"ok"}
```

### Stop Services

```bash
# Stop backend (in Terminal 1)
# Press CTRL+C

# Stop frontend (in Terminal 2)
# Press CTRL+C
```

### Restart Backend with Code Changes

The backend uses `--reload` mode, so code changes automatically restart the server.

**No manual restart needed** - just save your files!

### View Backend Logs

Backend logs are printed to Terminal 1 where you ran `python main.py`.

**Log Levels**:
- `DEBUG`: Request/response details
- `INFO`: Normal operations
- `WARNING`: Potential issues
- `ERROR`: Failures

**Example Log Output**:
```
INFO:     127.0.0.1:54321 - "POST /api/v1/messages HTTP/1.1" 200 OK
DEBUG:    Request: {"message": "Hello world"}
DEBUG:    Response: {"status": "success", "message": "api says: Hello world"}
```

### Deactivate Virtual Environment

```bash
deactivate
```

---

## Troubleshooting

### Issue: "Port 8000 already in use"

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use alternative port in .env
echo "API_PORT=8001" >> backend/.env
```

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution**:
```bash
# Ensure virtual environment is activated
source backend/venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Issue: "Cannot connect to backend" (Frontend error)

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS configuration in backend (should allow `http://localhost:5173`)
3. Verify frontend is calling correct URL (`http://localhost:8000/api/v1/messages`)

### Issue: Tests Failing

**Solution**:
```bash
# Run tests with verbose output to see errors
pytest -v --tb=short

# Run specific failing test
pytest tests/contract/test_message_api_contract.py::test_name -v

# Check if backend server is not running (it shouldn't be for tests)
# Tests use TestClient which runs in-process
```

---

## API Contract Reference

### POST /api/v1/messages

**Request**:
```json
{
  "message": "string (required, 1-10,000 chars)",
  "conversationId": "string (optional, UUID v4)",
  "timestamp": "string (optional, ISO-8601)"
}
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "message": "api says: <original message>",
  "timestamp": "string (ISO-8601)"
}
```

**Response (400 Bad Request)**:
```json
{
  "status": "error",
  "error": "Error message",
  "timestamp": "string (ISO-8601)"
}
```

**Full Contract**: See `specs/003-backend-api-loopback/contracts/message-api.yaml`

---

## Next Steps

1. **Implement P1 Tests** (TDD):
   - Write failing contract tests
   - Write failing integration tests
   - Write failing unit tests

2. **Implement P1 Code**:
   - Create `backend/main.py` (app entry point)
   - Create `backend/src/api/routes/messages.py` (endpoint)
   - Create `backend/src/services/message_service.py` (loopback logic)

3. **Verify Tests Pass**:
   - Run `pytest -v` and confirm all green

4. **Update Frontend**:
   - Create `frontend/src/services/apiClient.js`
   - Update `useMessages.js` to call backend API instead of local loopback

5. **Run E2E Tests**:
   - Update `frontend/tests/e2e/send-message.test.js` for backend integration
   - Run `npm run test:e2e`

6. **Update Documentation**:
   - Update `architecture.md` with backend details (ADR for FastAPI choice)
   - Update `README.md` with backend setup instructions

---

## Resources

- **Feature Spec**: `specs/003-backend-api-loopback/spec.md`
- **Implementation Plan**: `specs/003-backend-api-loopback/plan.md`
- **Data Model**: `specs/003-backend-api-loopback/data-model.md`
- **API Contract**: `specs/003-backend-api-loopback/contracts/message-api.yaml`
- **Research**: `specs/003-backend-api-loopback/research.md`
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Pytest Documentation**: https://docs.pytest.org
- **OpenAPI Specification**: https://swagger.io/specification/

---

**Questions?** See `specs/003-backend-api-loopback/plan.md` or consult the team.
