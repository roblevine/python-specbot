# Data Model: LLM-Generated Conversation Titles

**Feature**: 019-llm-conversation-titles
**Date**: 2026-01-21

## Entities

### Title Generation Request

A request to generate a conversation title from conversation messages.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| messages | array | Yes | Array of message objects (min 2: user + assistant) |
| model | string | Yes | Model ID to use for title generation |

**Message Object**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| sender | string | Yes | Message sender: "user" or "system" |
| text | string | Yes | Message content |

**Validation Rules**:
- `messages` must contain at least 2 messages (first user message + first assistant response)
- `model` must be a valid, available model ID
- Message `text` cannot be empty
- Message `sender` must be "user" or "system"

### Title Generation Response

Response containing the generated title.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| status | string | Yes | "success" or "error" |
| title | string | Conditional | Generated title (max 60 chars), present on success |
| error | string | Conditional | Error message, present on error |

### Title Model Configuration (Extension to ModelConfig)

Extends the existing model configuration with title model support.

**New Environment Variables**:
| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| OPENAI_TITLE_MODEL | string | No | Model ID to use for titles with OpenAI provider |
| ANTHROPIC_TITLE_MODEL | string | No | Model ID to use for titles with Anthropic provider |

**Extended Model Response**:
The `/api/v1/models` endpoint response will include a `titleModel` boolean field:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Model identifier |
| name | string | Yes | Human-readable name |
| description | string | Yes | Model description |
| provider | string | Yes | Provider identifier |
| default | boolean | Yes | Whether this is the default model |
| titleModel | boolean | Yes | **NEW**: Whether this is the title model for its provider |

## State Transitions

### Conversation Title State

```
[No Title] --create--> "New Conversation"
                           |
                           v
                   [First Exchange Complete]
                           |
            +--------------+---------------+
            |                              |
            v                              v
    [Title Generation]             [Generation Failed]
            |                              |
            v                              v
    "LLM-Generated Title"        "First Message Text"
            |                              |
            +--------> [User Rename] <-----+
                           |
                           v
                    "User-Set Title"
```

**State Rules**:
1. Title starts as "New Conversation" on conversation creation
2. After first message exchange completes, title generation is triggered
3. If generation succeeds, title becomes LLM-generated text (max 60 chars)
4. If generation fails, title falls back to first message text
5. User can manually rename at any time, which is preserved
6. Generated titles are NOT regenerated on subsequent messages
7. User-set titles are NEVER overwritten by generation

### Title Generation Flag

To track whether title generation has been attempted:

**Frontend State** (in conversation object):
| Field | Type | Description |
|-------|------|-------------|
| titleGenerated | boolean | Whether title generation has been attempted |

This field is used client-side only to prevent re-triggering generation:
- Set to `false` on conversation creation
- Set to `true` after title generation attempt (success or failure)
- Not persisted to server (derived from title !== "New Conversation")

## Relationships

```
┌─────────────────────┐
│   Model Config      │
├─────────────────────┤      configures
│ models[]            │─────────────────┐
│ titleModels{}       │                 │
└─────────────────────┘                 │
                                        v
┌─────────────────────┐         ┌───────────────────┐
│   Conversation      │         │  Title Service    │
├─────────────────────┤  uses   ├───────────────────┤
│ id                  │◄────────│ generate_title()  │
│ title               │         │                   │
│ messages[]          │─────────►                   │
└─────────────────────┘ input   └───────────────────┘
                                        │
                                        │ calls
                                        v
                                ┌───────────────────┐
                                │   LLM Service     │
                                ├───────────────────┤
                                │ get_llm_for_model │
                                └───────────────────┘
```

## Validation Constraints

### Title Length
- Maximum: 60 characters
- Minimum: 1 character (cannot be empty)
- Truncation: At word boundary when LLM exceeds limit

### Message Requirements for Title Generation
- Minimum 2 messages required
- First message must be from "user"
- Second message must be from "system" (assistant response)

### Model ID Validation
- Must exist in configured models
- Must belong to an enabled provider (API key configured)
- For title generation, should ideally be a cost-effective model
