# Quickstart: Server-Side Conversation Storage

**Feature**: 010-server-side-conversations
**Date**: 2026-01-15

## Overview

This feature migrates conversation storage from browser localStorage to server-side file-based persistence. After implementation, conversations are stored on the server and accessible from any browser.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Backend and frontend development environment set up
- OpenAI API key configured

## Quick Verification

After implementation, verify the feature works:

### 1. Start the backend server

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 2. Start the frontend

```bash
cd frontend
npm run dev
```

### 3. Test the API directly

```bash
# List conversations (should be empty initially)
curl http://localhost:8000/api/v1/conversations

# Create a conversation
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "Test conversation"}'

# List conversations again (should show the new one)
curl http://localhost:8000/api/v1/conversations
```

### 4. Test via UI

1. Open http://localhost:5173
2. Create a new conversation
3. Send a message
4. Refresh the browser - conversation should persist
5. Open in a different browser - conversation should appear

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/conversations` | List all conversations |
| GET | `/api/v1/conversations/{id}` | Get single conversation |
| POST | `/api/v1/conversations` | Create new conversation |
| PUT | `/api/v1/conversations/{id}` | Update conversation |
| DELETE | `/api/v1/conversations/{id}` | Delete conversation |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STORAGE_PATH` | `data/conversations.json` | Path to storage file |
| `STORAGE_TYPE` | `file` | Storage backend type (future: `database`) |

### Storage Location

By default, conversations are stored in `backend/data/conversations.json`. The directory is created automatically on first write.

## Troubleshooting

### Conversations not loading

1. Check backend is running: `curl http://localhost:8000/health`
2. Check storage file exists: `ls backend/data/conversations.json`
3. Check file permissions: Server needs read/write access

### Data not persisting

1. Check for write errors in backend logs
2. Verify storage directory is writable
3. Check for file locking issues (multiple servers)

### Migration from localStorage

On first load with existing localStorage data:
1. Frontend detects empty server + non-empty localStorage
2. Conversations are migrated to server automatically
3. localStorage is cleared after successful migration

## Development Tips

### Testing storage layer

```bash
cd backend
pytest tests/unit/test_file_storage.py -v
```

### Testing API endpoints

```bash
cd backend
pytest tests/integration/test_conversations.py -v
```

### Contract tests

```bash
# Backend
cd backend
pytest tests/contract/ -v

# Frontend
cd frontend
npm run test:contract
```

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────>│    Backend      │────>│    Storage      │
│                 │     │                 │     │                 │
│ useConversations│     │ conversations   │     │ FileStorage     │
│ apiClient.js    │     │ route           │     │ (conversations  │
│                 │<────│ storage_service │<────│  .json)         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Next Steps

After verifying basic functionality:

1. Run full test suite: `./scripts/test-all.sh`
2. Check contract tests pass
3. Verify error handling for network failures
4. Test concurrent access scenarios
