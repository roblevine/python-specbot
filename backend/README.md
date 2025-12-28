# SpecBot Backend API

Backend API server for SpecBot chat interface with message loopback functionality.

**Feature**: 003-backend-api-loopback
**Framework**: FastAPI 0.115.0
**Python**: 3.13+

## Quick Start

### 1. Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and adjust if needed:

```bash
cp .env.example .env
```

Default configuration:
- API Host: `0.0.0.0`
- API Port: `8000`
- Frontend URL: `http://localhost:5173` (for CORS)
- Log Level: `DEBUG`

### 3. Run Server

```bash
python main.py
```

Server starts at: http://localhost:8000

API Documentation: http://localhost:8000/docs

### 4. Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m contract      # Contract tests only
```

## API Endpoints

### POST /api/v1/messages

Send a message and receive loopback response with "api says: " prefix.

**Request:**
```json
{
  "message": "Hello world"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "api says: Hello world",
  "timestamp": "2025-12-28T10:00:01.234Z"
}
```

### GET /health

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "ok"
}
```

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   └── routes/       # API endpoint handlers
│   ├── services/         # Business logic
│   ├── middleware/       # Request/response middleware
│   └── utils/            # Shared utilities
├── tests/
│   ├── contract/         # OpenAPI schema validation
│   ├── integration/      # Full request-response tests
│   └── unit/             # Service and utility tests
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── pytest.ini          # Test configuration
```

## Development

### Running with Auto-Reload

The server automatically reloads on code changes in development mode:

```bash
python main.py
```

### Testing Strategy

1. **Contract Tests**: Validate API requests/responses against OpenAPI schema
2. **Integration Tests**: Test full request-response cycle via TestClient
3. **Unit Tests**: Test business logic in isolation

All tests follow TDD workflow (write failing tests first, then implement).

## Feature Documentation

Full specification and design docs:
- Spec: `/specs/003-backend-api-loopback/spec.md`
- Implementation Plan: `/specs/003-backend-api-loopback/plan.md`
- API Contract: `/specs/003-backend-api-loopback/contracts/message-api.yaml`
- Data Model: `/specs/003-backend-api-loopback/data-model.md`

## License

MIT
