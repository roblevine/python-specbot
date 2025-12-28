# Research Summary: Backend API Loopback Feature

**Feature**: 003-backend-api-loopback
**Date**: 2025-12-28
**Research Phase**: Phase 0 - Technical Decisions

This document consolidates research findings to resolve all "NEEDS CLARIFICATION" items from the Technical Context in plan.md.

---

## Research Question 1: Python Web Framework Selection

**Question**: Which Python web framework should we use? (FastAPI vs Flask vs other lightweight options)

### Decision: **FastAPI**

### Rationale:

**Perfect Alignment with Requirements:**
- **Lightweight & Stateless**: FastAPI requires minimal dependencies (fastapi + uvicorn). No ORM or database needed for loopback.
- **API-First Design**: Built specifically for REST APIs with automatic OpenAPI documentation generation (aligns with Constitution Principle I)
- **Performance**: ASGI-based, easily meets <2s response time requirement and handles 10+ concurrent requests
- **Native Async Support**: async/await built-in for efficient request handling

**Developer Experience Benefits:**
- **Automatic API Documentation**: Auto-generates interactive Swagger docs at `/docs` endpoint
- **Type Safety**: Pydantic models provide automatic request/response validation
- **Modern Python**: Leverages Python 3.13 type hints for IDE autocomplete
- **Built-in CORS**: `CORSMiddleware` included (no extra dependencies)

**Testing Excellence:**
- **TestClient**: Built-in test client for synchronous testing
- **pytest Integration**: Seamless integration with pytest (project standard)
- **Contract Testing**: Auto-generated OpenAPI schemas enable contract validation
- **No Server Required**: Tests run in-process

**Future-Proofing:**
- **Streaming Support**: Native SSE and WebSocket support for future LLM streaming responses
- **Background Tasks**: For async operations
- **Active Ecosystem**: Large community, excellent documentation, active development

### Alternatives Considered:

**Flask** - Rejected
- **Pros**: Extremely lightweight, simpler learning curve, battle-tested since 2010
- **Cons**:
  - No built-in validation (would need marshmallow/pydantic extension)
  - No automatic API documentation (would need flask-swagger/flasgger)
  - Requires flask-cors extension for CORS support
  - WSGI-based (slower than ASGI under concurrent load)
  - Async support requires Flask 2.0+ with additional complexity
- **Verdict**: Would end up adding extensions that FastAPI provides out-of-the-box, losing simplicity advantage

**Other Lightweight Frameworks** - Rejected
- **Bottle**: Too minimal, no async, dying ecosystem
- **Sanic**: Less mature than FastAPI, smaller ecosystem
- **Starlette**: Lower-level (FastAPI is built on it), no validation/docs
- **Tornado**: Older design patterns, more verbose

### Dependencies Required:

```txt
fastapi[standard]==0.115.0   # Core framework + uvicorn + pydantic
pytest==8.3.0                 # Testing framework
httpx==0.28.0                 # HTTP client for testing
pytest-asyncio==0.24.0        # Async test support
python-dotenv==1.0.0          # Environment variable management
```

**Total Size**: ~30MB including dependencies (lightweight)

---

## Research Question 2: Deployment Environment & Configuration

**Question**: What Python version, deployment approach, and configuration should we use?

### Python Version Decision: **Python 3.13**

**Rationale:**
- Devcontainer already uses Python 3.13.11 (confirmed in `.devcontainer/devcontainer.json`)
- Latest stable release (2025 current standard)
- FastAPI fully supports Python 3.8+ including 3.13
- Modern async features and performance improvements
- Consistency with existing development environment

**Action**: Use Python 3.13 as specified in devcontainer (no changes needed)

---

### Local Development Approach

**Decision**: FastAPI + uvicorn with simple `python main.py` wrapper

**How Developers Will Run It:**

```bash
# Option 1: Direct uvicorn (development)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Simplified wrapper script (recommended)
cd backend
python main.py
```

**Main.py wrapper example:**
```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
```

**Why uvicorn:**
- FastAPI's recommended ASGI server
- Hot-reload for development (`--reload` flag)
- Production-ready with minimal configuration
- Standard Python API server in 2025

---

### Tooling: Virtual Environments & Dependencies

**Decision**: Standard Python venv + requirements.txt

**Rationale:**
- Built into Python standard library (no external tools needed)
- Official Python recommendation
- Already configured in `.gitignore` (lines 27-31)
- Simple for contributors (no Poetry/Pipenv learning curve)
- Aligns with Constitution Principle VI (Simplicity & YAGNI)

**Setup Workflow:**
```bash
# Create virtual environment (one-time)
cd backend
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python main.py
```

**Why NOT Poetry/Pipenv for P1:**
- Adds complexity for minimal benefit at MVP stage
- venv + requirements.txt sufficient for this project scope
- Can migrate to Poetry later if dependency management becomes complex

---

### Configuration: Ports, CORS, Environment Variables

#### Port Configuration

**Decision**: Port 8000 for backend

**Standard Ports:**
- **Frontend (Vite)**: Port 5173 (already configured in `frontend/vite.config.js`)
- **Backend (FastAPI)**: Port 8000 (Python API convention)

**Why Port 8000:**
- Standard FastAPI/Django convention
- Clear separation from frontend (5173)
- No conflict with common services
- Easy to remember (8000 = backend, 5173 = frontend)

---

#### CORS Setup

**Decision**: FastAPI CORSMiddleware with explicit localhost origins

**Implementation:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration for local development
origins = [
    "http://localhost:5173",      # Vite dev server
    "http://127.0.0.1:5173",      # Alternative localhost
    "http://0.0.0.0:5173",        # Docker/container access
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Rationale:**
- Explicit origins (more secure than wildcard)
- Supports both `localhost` and `127.0.0.1` (browser differences)
- Includes `0.0.0.0` for devcontainer/Docker scenarios
- `allow_credentials=True` supports future auth features
- Simple one-time configuration

---

#### Environment Variables

**Decision**: python-dotenv for local development

**.env file (git-ignored):**
```bash
# Backend API Configuration
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:5173
LOG_LEVEL=DEBUG
```

**Loading in main.py:**
```python
from dotenv import load_dotenv
import os

load_dotenv()

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

**Rationale:**
- Different configs for dev/test/prod
- Secret management ready for future LLM API keys
- Already configured in `.gitignore` (lines 105-108)
- Standard practice for 12-factor apps

---

### Development Workflow Summary

**Complete Developer Onboarding:**

```bash
# 1. Setup backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Create .env file (optional for P1)
cp .env.example .env

# 3. Run backend (port 8000)
python main.py

# 4. In another terminal: Run frontend (port 5173)
cd frontend
npm install
npm run dev

# 5. Access application
# Frontend: http://localhost:5173
# Backend API docs: http://localhost:8000/docs
```

---

## Research Question 3: API Testing Best Practices

**Question**: How should we implement contract testing, integration testing, and TDD workflow with pytest?

### Contract Testing Tool Decision

**Decision**: `openapi-core` + `pytest-openapi-schema-validator`

**Rationale:**
- **openapi-core**: Industry-standard library for validating requests/responses against OpenAPI 3.x specifications
- **Native pytest integration**: Seamless test integration
- **Two-way validation**: Validates both incoming requests AND outgoing responses
- **Clear error reporting**: Shows exactly which part of schema failed

**Alternative Considered: schemathesis**
- Excellent for property-based/fuzzing testing
- Better for P2/P3 when automated test case generation needed
- For P1 basic loopback, explicit contract tests with `openapi-core` provide clearer TDD workflow

**Implementation:**
```python
# tests/contract/test_message_api_contract.py
import pytest
from openapi_core import Spec

@pytest.fixture
def openapi_spec():
    """Load OpenAPI specification from contracts/ directory"""
    with open('specs/003-backend-api-loopback/contracts/message-api.yaml') as f:
        spec_dict = yaml.safe_load(f)
    return Spec.from_dict(spec_dict)

def test_loopback_response_matches_contract(client, openapi_spec):
    """Contract test: Response matches OpenAPI schema"""
    response = client.post("/api/v1/messages", json={"message": "Hello world"})
    validate_response(response, spec=openapi_spec)
    assert response.status_code == 200
```

---

### HTTP Testing Approach Decision

**Decision**: FastAPI's `TestClient` (primary) + `httpx` (optional for framework-agnostic tests)

**FastAPI TestClient Implementation:**
```python
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    """Create test client for API"""
    return TestClient(app)

def test_send_message_loopback(client):
    """Integration test: Full HTTP request-response cycle"""
    payload = {"message": "Hello world"}
    response = client.post("/api/v1/messages", json=payload)

    assert response.status_code == 200
    assert response.json()["message"] == "api says: Hello world"
```

**Why httpx over requests:**
- Modern, actively maintained (requests in maintenance mode)
- Async/await support for concurrent tests
- Better timeout handling
- HTTP/2 support
- Same API as requests (easy migration)

---

### Test Organization

**Directory Structure:**

```
backend/
├── tests/
│   ├── conftest.py              # Shared pytest fixtures
│   ├── contract/                # Contract tests (OpenAPI validation)
│   │   └── test_message_api_contract.py
│   ├── integration/             # Full HTTP request-response tests
│   │   ├── test_message_loopback_flow.py
│   │   └── test_error_handling.py
│   └── unit/                    # Business logic tests
│       ├── test_message_service.py
│       └── test_validation.py
```

**Test Naming Convention:**
```python
# Pattern: test_<feature>_<scenario>_<expected_outcome>

def test_message_request_schema_valid_input():
    """Contract: Valid message request matches OpenAPI schema"""

def test_send_message_returns_loopback_response():
    """Integration: POST /api/v1/messages returns echoed message"""

def test_loopback_service_adds_prefix_to_message():
    """Unit: Message service prepends 'api says: ' to input"""
```

**Rationale:**
- Mirrors frontend test structure (unit/integration/e2e → unit/integration/contract)
- Clear separation by test type
- Easy to run specific test categories with `pytest -m <marker>`

---

### TDD Workflow Examples

#### Phase 1: Write Failing Contract Test (RED)

```python
# tests/contract/test_message_api_contract.py
def test_loopback_response_matches_contract(client, openapi_spec):
    """Contract test: Response matches OpenAPI schema

    EXPECTED TO FAIL: Endpoint doesn't exist yet
    """
    response = client.post("/api/v1/messages", json={"message": "Hello world"})

    # This will FAIL because:
    # 1. Endpoint returns 404 (not implemented)
    # 2. Response schema doesn't match spec
    validate_response(response, spec=openapi_spec)
    assert response.status_code == 200
```

**Run test:**
```bash
pytest tests/contract/ -v
# OUTPUT (RED): FAILED - AssertionError: 404 != 200
```

---

#### Phase 2: Write Failing Integration Test (RED)

```python
# tests/integration/test_message_loopback_flow.py
def test_send_message_receives_loopback_response(client):
    """Integration test: Full HTTP loopback flow

    EXPECTED TO FAIL: Implementation doesn't exist yet
    Acceptance Criteria: spec.md User Story 1, Scenario 1
    """
    payload = {"message": "Hello world"}
    response = client.post("/api/v1/messages", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "api says: Hello world"
```

**Run test:**
```bash
pytest tests/integration/ -v
# OUTPUT (RED): FAILED - AssertionError: 404 != 200
```

---

#### Phase 3: Write Failing Unit Test (RED)

```python
# tests/unit/test_message_service.py
from backend.services.message_service import create_loopback_message

def test_loopback_message_adds_api_prefix():
    """Unit test: Message service adds 'api says: ' prefix

    EXPECTED TO FAIL: Function doesn't exist yet
    """
    user_message = "Hello world"
    loopback = create_loopback_message(user_message)
    assert loopback == "api says: Hello world"
```

**Run test:**
```bash
pytest tests/unit/ -v
# OUTPUT (RED): FAILED - ImportError: cannot import 'create_loopback_message'
```

---

#### Phase 4: Implement Minimum Code to Pass (GREEN)

```python
# backend/services/message_service.py
def create_loopback_message(user_message: str) -> str:
    """Create loopback message with API prefix"""
    return f"api says: {user_message}"

# backend/api/routes/messages.py
from fastapi import APIRouter
from backend.services.message_service import create_loopback_message

@router.post("/api/v1/messages")
async def send_message(request: MessageRequest):
    """Accept message and return loopback response"""
    loopback = create_loopback_message(request.message)
    return MessageResponse(status="success", message=loopback)
```

**Run tests:**
```bash
pytest tests/ -v
# OUTPUT (GREEN): All tests PASSED
```

---

#### Phase 5: Refactor (keep tests GREEN)

```python
# backend/services/message_service.py (refactored)
class MessageService:
    API_PREFIX = "api says: "

    @classmethod
    def create_loopback(cls, message: str) -> str:
        """Create loopback message with API prefix"""
        return f"{cls.API_PREFIX}{message}"
```

**Run tests after refactor:**
```bash
pytest tests/ -v
# OUTPUT (STILL GREEN): All tests PASSED
```

---

### Test Data & Fixtures Best Practices

**Shared Fixtures (conftest.py):**
```python
@pytest.fixture
def client():
    """FastAPI test client for integration tests"""
    return TestClient(app)

@pytest.fixture
def sample_message_payload():
    """Valid message payload for testing"""
    return {
        "message": "Hello world",
        "timestamp": "2025-12-28T10:00:00Z"
    }

@pytest.fixture
def invalid_message_payloads():
    """Collection of invalid payloads for error testing"""
    return {
        "empty_message": {"message": ""},
        "missing_message": {},
        "too_long": {"message": "x" * 10001},
    }
```

**Parametrized Tests:**
```python
@pytest.mark.parametrize("message,expected", [
    ("Hello", "api says: Hello"),
    ("Test 123", "api says: Test 123"),
    ("Emoji 😀", "api says: Emoji 😀"),
])
def test_loopback_preserves_content(client, message, expected):
    """Integration: Loopback preserves exact message content"""
    response = client.post("/api/v1/messages", json={"message": message})
    assert response.json()["message"] == expected
```

---

### pytest Configuration

**pytest.ini:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=backend/src
    --cov-report=html

markers =
    unit: Unit tests (business logic only)
    integration: Integration tests (HTTP request-response)
    contract: Contract tests (OpenAPI schema validation)
```

**Running Tests by Category:**
```bash
pytest -m contract      # Contract tests only
pytest -m integration   # Integration tests only
pytest -m unit          # Unit tests only
pytest --cov            # With coverage report
```

---

### Testing Dependencies

```txt
# Testing
pytest==8.3.0
pytest-asyncio==0.24.0
pytest-cov==4.1.0

# Contract testing
openapi-core==0.18.2
pyyaml==6.0.1

# Optional: Property-based testing (P2/P3)
# schemathesis==3.22.0
```

---

## Summary of All Technical Decisions

| Decision Area | Choice | Rationale |
|--------------|--------|-----------|
| **Python Version** | 3.13 | Already in devcontainer, latest stable, FastAPI compatible |
| **Framework** | FastAPI | API-First design, auto-docs, async, CORS built-in, testing excellence |
| **ASGI Server** | uvicorn | FastAPI standard, hot-reload for dev, production-ready |
| **Virtual Env** | venv | Python stdlib, simple, already git-ignored, YAGNI |
| **Dependencies** | requirements.txt | Simple, no extra tools for MVP, can upgrade later |
| **Backend Port** | 8000 | Standard Python API convention, clear separation |
| **Frontend Port** | 5173 | Already configured (Vite default) |
| **CORS** | CORSMiddleware | Built-in FastAPI, explicit origins, secure |
| **Environment Config** | python-dotenv | Standard, .env already git-ignored, 12-factor apps |
| **Contract Testing** | openapi-core | Industry standard, validates OpenAPI schemas |
| **HTTP Testing** | TestClient + httpx | FastAPI native, modern async support |
| **Test Organization** | contract/integration/unit | Clear separation, mirrors frontend structure |
| **TDD Workflow** | Red → Green → Refactor | Constitution Principle III (mandatory) |

---

## References

- **Devcontainer Config**: `/workspaces/python-specbot/.devcontainer/devcontainer.json`
- **Architecture Doc**: `/workspaces/python-specbot/architecture.md`
- **Feature Spec**: `/workspaces/python-specbot/specs/003-backend-api-loopback/spec.md`
- **Constitution**: `/workspaces/python-specbot/.specify/memory/constitution.md`
- **Frontend Tests** (reference patterns):
  - `/workspaces/python-specbot/frontend/tests/unit/LocalStorageAdapter.test.js`
  - `/workspaces/python-specbot/frontend/tests/integration/message-flow.test.js`
  - `/workspaces/python-specbot/frontend/tests/e2e/send-message.test.js`

---

## Next Steps (Phase 1)

1. Update plan.md Technical Context with resolved decisions
2. Create data-model.md with entity definitions
3. Create contracts/message-api.yaml with OpenAPI specification
4. Create quickstart.md with setup instructions
5. Update CLAUDE.md with new backend technologies
6. Re-evaluate Constitution Check with complete technical context
