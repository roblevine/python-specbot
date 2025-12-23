# Contract: Storage Interface

**Module**: `storage/LocalStorageAdapter`
**Purpose**: Provide abstraction layer for persisting and retrieving conversation data from browser LocalStorage
**Version**: 1.0.0

## Interface Definition

### `saveConversations(conversations, activeConversationId)`

Persist all conversations and active conversation ID to LocalStorage.

**Input**:
```typescript
saveConversations(
  conversations: Conversation[],
  activeConversationId: string | null
): Promise<void>
```

**Parameters**:
- `conversations` (Array<Conversation>): Array of conversation objects to save
- `activeConversationId` (string | null): ID of currently active conversation, or null if none

**Validation**:
- `conversations` MUST be a valid array
- Each conversation MUST conform to Conversation schema (see data-model.md)
- `activeConversationId` MUST be null or match an existing conversation ID
- Total data size MUST NOT exceed LocalStorage limits (~5MB)

**Success**:
- Resolves with `undefined`
- Data written to `localStorage` under key `chatInterface:v1:data`
- Previous data overwritten

**Failure** (throws Error):
- `ValidationError`: Invalid conversation structure
- `StorageError`: LocalStorage quota exceeded
- `SerializationError`: Unable to serialize data to JSON

**Side Effects**:
- Writes to `localStorage`
- Logs save operation to console (DEBUG level)

---

### `loadConversations()`

Load all conversations and active conversation ID from LocalStorage.

**Input**:
```typescript
loadConversations(): Promise<StorageData>
```

**Parameters**: None

**Success**:
```typescript
{
  conversations: Conversation[],
  activeConversationId: string | null
}
```

**Behavior**:
- If no data exists: Returns `{ conversations: [], activeConversationId: null }`
- If data exists: Validates and returns parsed data
- If validation fails: Logs error, returns empty state

**Failure** (throws Error):
- `DeserializationError`: Unable to parse JSON
- `MigrationError`: Data version incompatible and migration failed

**Side Effects**:
- Reads from `localStorage`
- Logs load operation to console (DEBUG level)
- May run migration if version mismatch detected

---

### `clearAllData()`

Remove all stored conversation data from LocalStorage.

**Input**:
```typescript
clearAllData(): Promise<void>
```

**Parameters**: None

**Success**:
- Resolves with `undefined`
- All data removed from `localStorage` (key: `chatInterface:v1:data`)

**Failure** (throws Error):
- `StorageError`: Unable to access LocalStorage

**Side Effects**:
- Removes data from `localStorage`
- Logs clear operation to console (DEBUG level)

---

### `getStorageInfo()`

Get information about current storage usage.

**Input**:
```typescript
getStorageInfo(): Promise<StorageInfo>
```

**Parameters**: None

**Success**:
```typescript
{
  used: number,        // Bytes used
  available: number,   // Estimated bytes available
  conversationCount: number,
  totalMessages: number
}
```

**Failure** (throws Error):
- `StorageError`: Unable to access LocalStorage

**Side Effects**:
- Reads from `localStorage` (read-only)

---

## Data Schema (v1.0.0)

Stored under key: `chatInterface:v1:data`

```json
{
  "version": "1.0.0",
  "conversations": [
    {
      "id": "conv-[uuid]",
      "createdAt": "ISO 8601 timestamp",
      "updatedAt": "ISO 8601 timestamp",
      "title": "string (max 50 chars)",
      "messages": [
        {
          "id": "msg-[uuid]",
          "text": "string (max 10,000 chars)",
          "sender": "user | system",
          "timestamp": "ISO 8601 timestamp",
          "status": "pending | sent | error"
        }
      ]
    }
  ],
  "activeConversationId": "conv-[uuid] | null"
}
```

---

## Error Handling

### Error Types

**ValidationError**:
- Thrown when: Input data doesn't conform to schema
- Example: Conversation missing required `id` field
- Recovery: Fix input data, retry operation

**StorageError**:
- Thrown when: LocalStorage operation fails (quota exceeded, access denied)
- Example: Trying to save when storage quota exceeded
- Recovery: Clear old conversations, reduce data size

**SerializationError**:
- Thrown when: Cannot convert data to JSON
- Example: Circular reference in data structure
- Recovery: Fix data structure, retry operation

**DeserializationError**:
- Thrown when: Cannot parse stored JSON
- Example: Corrupted data in LocalStorage
- Recovery: Clear storage, start fresh

**MigrationError**:
- Thrown when: Unable to migrate data from old version
- Example: v1.0.0 data incompatible with v2.0.0 schema
- Recovery: Manual data export, clear storage, reimport

---

## Contract Tests

### Test Scenarios

1. **Save and Load Round-Trip**:
   - GIVEN: Valid conversation array
   - WHEN: Save then load
   - THEN: Loaded data matches saved data

2. **Empty State**:
   - GIVEN: No existing data
   - WHEN: Load conversations
   - THEN: Returns empty array and null activeConversationId

3. **Validation Failure**:
   - GIVEN: Invalid conversation (missing required field)
   - WHEN: Save conversations
   - THEN: Throws ValidationError

4. **Storage Quota Exceeded**:
   - GIVEN: Data exceeding storage limit
   - WHEN: Save conversations
   - THEN: Throws StorageError

5. **Corrupted Data**:
   - GIVEN: Invalid JSON in LocalStorage
   - WHEN: Load conversations
   - THEN: Logs error, returns empty state

6. **Clear Data**:
   - GIVEN: Existing stored conversations
   - WHEN: clearAllData()
   - THEN: Subsequent load returns empty state

7. **Storage Info**:
   - GIVEN: 5 conversations with 10 messages each
   - WHEN: getStorageInfo()
   - THEN: Returns accurate usage and counts

---

## Implementation Notes

- Use `JSON.stringify()` and `JSON.parse()` for serialization
- Wrap all LocalStorage operations in try-catch blocks
- Log all operations for debugging (DEBUG level)
- Validate data before saving and after loading
- Handle missing LocalStorage gracefully (fallback to in-memory only)

---

## Versioning

**Current Version**: 1.0.0

**Future Migrations**:
- If schema changes, increment version number
- Implement migration function: `migrateV1toV2(data)`
- Test migration with real user data before release

**Breaking Changes** (require MAJOR version bump):
- Changing required fields
- Removing fields
- Changing field types

**Non-Breaking Changes** (allow MINOR version bump):
- Adding optional fields with defaults
- Expanding enum values
- Improving validation
