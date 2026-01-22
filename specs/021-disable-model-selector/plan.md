# Implementation Plan: Disable Model Selector After Conversation Starts

**Branch**: `021-disable-model-selector` | **Date**: 2026-01-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/021-disable-model-selector/spec.md`

## Summary

Lock the model selector UI component once a conversation has started (first message sent) to prevent model changes mid-conversation. When loading previous conversations, display the conversation's model in a disabled selector. This is a frontend-focused feature since the backend already stores model information with messages.

## Technical Context

**Language/Version**: JavaScript ES6+ (Frontend), Python 3.13 (Backend - minimal changes)
**Primary Dependencies**: Vue 3.4.0, Vite 5.0.0, FastAPI 0.115.0, Pydantic 2.10.0
**Storage**: File-based JSON (backend conversations), Browser localStorage (settings only)
**Testing**: Vitest (frontend unit/component tests), pytest (backend unit tests)
**Target Platform**: Web browser (modern browsers supporting ES6+)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Model selector state transition within 200ms of user actions
**Constraints**: No changes to API contracts, backward compatible with existing conversations
**Scale/Scope**: Single-user chat application, ~3 frontend files to modify

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | ✅ PASS | No new API endpoints needed; existing `/api/v1/models` and conversation storage sufficient |
| II. Modular Architecture | ✅ PASS | Changes isolated to ModelSelector component and useConversations composable |
| III. Test-First Development | ✅ REQUIRED | Tests must be written before implementation |
| IV. Integration & Contract Testing | ✅ PASS | No API contract changes; frontend component tests required |
| V. Observability & Debuggability | ✅ PASS | No new logging required for UI state change |
| VI. Simplicity & YAGNI | ✅ PASS | Minimal changes: add disabled prop logic, no new abstractions |
| VII. Versioning & Breaking Changes | ✅ PASS | No breaking changes; backward compatible with legacy conversations |
| VIII. Incremental Delivery | ✅ REQUIRED | Implement as thin vertical slices (P1 stories first) |
| IX. Living Architecture Documentation | ✅ PASS | No architectural changes; UI behavior change only |

**Architecture Update Required**: No - this is a UI behavior change within existing component boundaries.

## Project Structure

### Documentation (this feature)

```text
specs/021-disable-model-selector/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output - research findings
├── data-model.md        # Phase 1 output - data structure documentation
├── quickstart.md        # Phase 1 output - implementation guide
├── contracts/           # Phase 1 output - no new contracts (existing sufficient)
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── schemas.py              # ConversationMessage already has model field
│   └── api/routes/
│       └── conversations.py    # No changes needed
└── tests/
    └── unit/                   # Existing tests sufficient

frontend/
├── src/
│   ├── components/
│   │   ├── ModelSelector/
│   │   │   └── ModelSelector.vue    # Add disabled logic based on conversation state
│   │   ├── InputArea/
│   │   │   └── InputArea.vue        # Pass disabled state to ModelSelector
│   │   └── App/
│   │       └── App.vue              # Orchestrate conversation-based model state
│   └── state/
│       ├── useModels.js             # May need method to set model without persisting globally
│       └── useConversations.js      # Track conversation model, provide hasMessages computed
└── tests/
    └── unit/
        └── components/
            └── ModelSelector.spec.js  # Tests for disabled state logic
```

**Structure Decision**: Web application structure (Option 2). Primary changes in frontend components and state management. Backend requires no changes as model field already exists in message schema.

## Complexity Tracking

> No constitution violations identified. Feature is straightforward UI state management.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| State Management | Use existing composables | No new state management patterns needed |
| Disabled State | Prop-based | ModelSelector already accepts disabled prop |
| Model Restoration | Derive from conversation messages | Model field exists in messages; no new data needed |

## Key Implementation Decisions

1. **Derive conversation model from first system message**: Rather than adding a new `modelId` field to Conversation, derive the model from the first system message's `model` field. This avoids schema changes and uses existing data.

2. **Disable logic location**: Compute `isModelSelectorDisabled` in App.vue based on `activeConversation.messages.length > 0` and pass to InputArea.

3. **Model restoration on conversation load**: When switching conversations, if conversation has messages, read model from first system message and set selectedModelId (without persisting to global storage).

4. **Legacy conversation handling**: If conversation has messages but no model field on any message, use the current default model and display it in disabled state.

5. **Unavailable model handling**: If stored model ID is not in availableModels list, display the model name with "(unavailable)" suffix in disabled state.
