# Research: Server-Side Conversation Storage

**Feature**: 010-server-side-conversations
**Date**: 2026-01-15

## Research Topics

### 1. File-Based Storage with Concurrency Control

**Question**: How to implement file-based JSON storage with safe concurrent access?

**Decision**: Use Python's `filelock` library with JSON file storage

**Rationale**:
- `filelock` is cross-platform and well-maintained
- Simple file locking prevents data corruption from concurrent writes
- JSON format is human-readable and matches existing frontend data structure
- No additional dependencies beyond `filelock`

**Alternatives Considered**:
- SQLite with WAL mode: More complex than needed for single-user app
- In-memory with periodic flush: Risk of data loss on crash
- LMDB: Overkill for simple key-value storage of conversations

**Implementation Pattern**:
```python
from filelock import FileLock

lock = FileLock("data/conversations.json.lock")
with lock:
    # Read, modify, write operations here
```

### 2. Storage Abstraction Pattern

**Question**: How to design storage layer for easy database migration?

**Decision**: Repository pattern with abstract base class

**Rationale**:
- Abstract base class defines interface contract
- Concrete implementations (file, database) are interchangeable
- Dependency injection allows runtime selection
- Clean separation of concerns

**Alternatives Considered**:
- Duck typing only: Less explicit contract, harder to test
- Full ORM from start: Over-engineering for file storage phase
- Event sourcing: Too complex for conversation storage

**Implementation Pattern**:
```python
from abc import ABC, abstractmethod

class ConversationStorage(ABC):
    @abstractmethod
    async def list_conversations(self) -> List[ConversationSummary]: ...

    @abstractmethod
    async def get_conversation(self, id: str) -> Conversation: ...

    @abstractmethod
    async def save_conversation(self, conversation: Conversation) -> None: ...

    @abstractmethod
    async def delete_conversation(self, id: str) -> bool: ...
```

### 3. API Design for Conversation CRUD

**Question**: RESTful endpoint design for conversation operations?

**Decision**: Standard REST with `/api/v1/conversations` resource

**Rationale**:
- Consistent with existing `/api/v1/messages` and `/api/v1/models` patterns
- Standard HTTP methods (GET, POST, PUT, DELETE)
- JSON request/response bodies with Pydantic validation
- Follows existing project conventions

**Endpoints**:
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/conversations` | List all conversations (summaries) |
| GET | `/api/v1/conversations/{id}` | Get single conversation with messages |
| POST | `/api/v1/conversations` | Create new conversation |
| PUT | `/api/v1/conversations/{id}` | Update conversation (add messages, update title) |
| DELETE | `/api/v1/conversations/{id}` | Delete conversation |

### 4. Frontend API Integration Pattern

**Question**: How to integrate server API with existing Vue composables?

**Decision**: Extend apiClient.js with conversation methods, update useConversations.js

**Rationale**:
- Maintains existing separation of concerns (apiClient for HTTP, composables for state)
- Minimal changes to component code
- Error handling follows existing patterns
- Async/await with error state management

**Implementation Pattern**:
```javascript
// apiClient.js
export async function getConversations() { ... }
export async function getConversation(id) { ... }
export async function saveConversation(conversation) { ... }
export async function deleteConversation(id) { ... }

// useConversations.js
async function loadFromServer() {
  try {
    const data = await getConversations()
    conversations.value = data
  } catch (error) {
    // Handle error, show user feedback
  }
}
```

### 5. Data Migration Strategy

**Question**: How to handle existing localStorage data?

**Decision**: One-time migration on first server interaction

**Rationale**:
- Users shouldn't lose existing conversations
- Migration runs once when localStorage has data but server is empty
- After migration, localStorage is cleared
- Simple flag prevents repeated migration attempts

**Migration Flow**:
1. App loads → Check if server has conversations
2. If server empty AND localStorage has data → Migrate
3. POST each conversation to server
4. Clear localStorage after successful migration
5. Continue with server-only storage

### 6. Error Handling Strategy

**Question**: How to handle storage failures gracefully?

**Decision**: Structured error responses with specific error codes

**Rationale**:
- Consistent with existing error handling patterns
- Frontend can display appropriate user messages
- Supports retry logic for transient failures
- Logging enables debugging

**Error Codes**:
| Code | Meaning | User Action |
|------|---------|-------------|
| STORAGE_READ_ERROR | Cannot read from storage | Retry or contact support |
| STORAGE_WRITE_ERROR | Cannot write to storage | Retry or free space |
| CONVERSATION_NOT_FOUND | Requested conversation doesn't exist | Refresh list |
| VALIDATION_ERROR | Invalid data format | Fix input |

## Dependencies

### Backend
- `filelock>=3.0.0` - Cross-platform file locking

### Frontend
- No new dependencies required

## Open Questions (Resolved)

1. ✅ **File location**: Store in `backend/data/conversations.json` (configurable via env var)
2. ✅ **Concurrent requests**: Use file locking with `filelock` library
3. ✅ **Large conversations**: Return full messages for now; pagination can be added later if needed
4. ✅ **Migration**: One-time migration from localStorage on first server contact
