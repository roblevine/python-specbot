# Research: Disable Model Selector After Conversation Starts

**Feature**: 021-disable-model-selector
**Date**: 2026-01-22

## Research Questions

### Q1: How does the ModelSelector component currently handle disabled state?

**Decision**: Use existing disabled prop mechanism

**Findings**:
- ModelSelector.vue already accepts a `disabled` prop (line 11)
- Current disabled conditions: `isLoading || availableModels.length === 0`
- CSS styling for disabled state already exists (opacity: 0.6, cursor: not-allowed)
- ARIA accessibility attributes handle disabled state properly

**Rationale**: The component is already well-designed for disabled states. We simply need to extend the disabled condition to include "conversation has messages".

**Alternatives Considered**:
- Creating a new "locked" state separate from disabled → Rejected: unnecessary complexity, disabled conveys the intent
- Adding a visual lock icon → Could be future enhancement, but disabled state is sufficient for MVP

### Q2: Where is the conversation's model stored?

**Decision**: Derive from first system message's `model` field

**Findings**:
- `ConversationMessage` schema has `model: Optional[str]` field (backend/src/schemas.py)
- System messages (LLM responses) store the model that generated them
- User messages don't typically have model field populated
- Message streaming code sets model field when creating system message (useMessages.js:233)

**Rationale**: The model information is already stored with messages. Extracting it from the first system message is reliable and avoids schema changes.

**Alternatives Considered**:
- Add `modelId` field to Conversation schema → Rejected: requires backend schema change, data migration, more complexity
- Store model on user message when sent → Rejected: model field semantically belongs with system response

### Q3: How to handle model restoration when loading a previous conversation?

**Decision**: Set selectedModelId via setSelectedModel() but skip persisting to global settings

**Findings**:
- `setSelectedModel(modelId)` in useModels.js updates state AND persists to SettingsStorage
- We need to update the display without affecting the user's global model preference
- Options: (a) modify setSelectedModel to accept a "persist" flag, or (b) separate display model from global preference

**Rationale**: Adding a `persist` parameter to `setSelectedModel()` is minimal change and keeps logic centralized.

**Implementation**:
```javascript
// useModels.js
const setSelectedModel = (modelId, persist = true) => {
  selectedModelId.value = modelId
  if (persist) {
    SettingsStorage.saveSetting('selectedModelId', modelId)
  }
}
```

**Alternatives Considered**:
- Create separate `displayModelId` state → Rejected: duplicates state, more complex
- Always persist even when loading conversation → Rejected: would change user's global preference unexpectedly

### Q4: How to detect if conversation has messages?

**Decision**: Check `activeConversation.value?.messages?.length > 0` in App.vue

**Findings**:
- `useConversations()` exposes `activeConversation` reactive ref
- Messages array is always present (may be empty array for new conversations)
- Check should happen in App.vue and result passed down as prop

**Rationale**: Simple, direct check. No need for computed property in composable since it's trivial.

**Implementation**:
```javascript
// App.vue
const hasMessages = computed(() =>
  activeConversation.value?.messages?.length > 0
)
```

**Alternatives Considered**:
- Add `hasMessages` computed to useConversations → Could do this, but adds overhead for simple check
- Check in ModelSelector directly → Rejected: component shouldn't know about conversations

### Q5: How to handle legacy conversations without model field?

**Decision**: Use current default model and display in disabled state

**Findings**:
- Older conversations may have messages with `model: null` or `model: undefined`
- The `getDefaultModel()` function returns the configured default model
- User can see what model is selected but cannot change it

**Rationale**: Graceful degradation. User sees a model selected (the default) rather than empty or error state.

**Implementation**:
```javascript
const getConversationModel = (conversation) => {
  const firstSystemMsg = conversation.messages.find(m => m.sender === 'system' && m.model)
  return firstSystemMsg?.model || getDefaultModel()?.id || null
}
```

### Q6: How to handle unavailable models?

**Decision**: Display model ID with "(unavailable)" suffix, keep selector disabled

**Findings**:
- Models can be removed from configuration after conversations are created
- ModelSelector currently only shows available models in dropdown
- Need to handle case where stored model ID doesn't match any available model

**Rationale**: User should see what model was used (even if unavailable) rather than a confusing default or error.

**Implementation**:
- Check if model ID exists in availableModels list
- If not found, add a synthetic entry with name like "gpt-4 (unavailable)"
- Keep selector disabled regardless

### Q7: When should selector re-enable for new conversation?

**Decision**: Enable when `createConversation()` is called and messages.length === 0

**Findings**:
- "New Conversation" button calls `createConversation()`
- This creates conversation with empty messages array
- Selector should immediately become enabled

**Rationale**: The condition `messages.length > 0` naturally handles this - new conversation has no messages so selector is enabled.

## Summary of Key Decisions

| Question | Decision | Complexity |
|----------|----------|------------|
| Disabled state mechanism | Use existing disabled prop | Low |
| Model storage | Derive from first system message | Low |
| Model restoration | setSelectedModel with persist=false | Low |
| Has messages check | Simple length check in App.vue | Low |
| Legacy conversations | Use default model | Low |
| Unavailable models | Show "(unavailable)" suffix | Medium |
| New conversation | Messages.length === 0 enables selector | Low |

## No Outstanding Clarifications

All technical questions have been resolved through codebase exploration. No NEEDS CLARIFICATION items remain.
