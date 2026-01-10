"""
Pydantic Schemas for API Request/Response Models

Defines data validation and serialization for the Message API and Chat Streaming API.
Based on contracts/message-api.yaml, contracts/chat-streaming-api.yaml, and data-model.md.

Feature: 003-backend-api-loopback, 005-llm-integration
Tasks: T030, T031, T032 (003), T006 (005)
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class MessageRequest(BaseModel):
    """
    T030: Request payload for sending a message.

    Validates FR-007, FR-010, FR-012:
    - Message required, 1-10,000 chars
    - Accepts special characters, emoji, multi-byte
    - Validates format and rejects malformed data
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User message text",
        examples=["Hello world", "Test message 🚀"]
    )
    conversationId: Optional[str] = Field(
        None,
        description="Optional conversation ID (with conv- prefix)",
        pattern=r'^conv-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
        examples=["conv-a1b2c3d4-5678-90ab-cdef-123456789abc"]
    )
    timestamp: Optional[str] = Field(
        None,
        description="Client-side timestamp (ISO-8601)",
        examples=["2025-12-28T10:00:00.000Z"]
    )

    @field_validator('message')
    @classmethod
    def message_not_whitespace(cls, v: str) -> str:
        """Validate message is not only whitespace (per FR-012)"""
        if not v.strip():
            raise ValueError('Message cannot be only whitespace')
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Hello world",
                    "conversationId": "conv-a1b2c3d4-5678-90ab-cdef-123456789abc",
                    "timestamp": "2025-12-28T10:00:00.000Z"
                }
            ]
        }
    }


class MessageResponse(BaseModel):
    """
    T031: Response payload for successful message processing.

    Validates FR-002, FR-011:
    - Includes "api says: " prefix
    - Preserves message content exactly
    """

    status: Literal["success"] = Field(
        default="success",
        description="Response status"
    )
    message: str = Field(
        ...,
        description="Loopback message with 'api says: ' prefix",
        examples=["api says: Hello world"]
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        description="Server-side timestamp (ISO-8601 with milliseconds)",
        examples=["2025-12-28T10:00:01.234Z"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "message": "api says: Hello world",
                    "timestamp": "2025-12-28T10:00:01.234Z"
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """
    T032: Response payload for errors.

    Validates FR-008, FR-012:
    - Provides descriptive error messages
    - Includes actionable context
    """

    status: Literal["error"] = Field(
        default="error",
        description="Response status"
    )
    error: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Message cannot be empty", "Invalid request format"]
    )
    detail: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error context",
        examples=[{"field": "message", "issue": "Field required"}]
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        description="Server-side timestamp (ISO-8601 with milliseconds)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "error",
                    "error": "Message cannot be empty",
                    "timestamp": "2025-12-28T10:00:01.234Z"
                }
            ]
        }
    }


# ============================================================================
# LLM Chat Streaming Schemas (Feature 005)
# ============================================================================


class HistoryMessage(BaseModel):
    """
    T006: Single message in conversation history.

    Used to provide context for LLM streaming requests.
    Based on contracts/chat-streaming-api.yaml HistoryMessage schema.
    """

    role: Literal["user", "assistant", "system"] = Field(
        ...,
        description="Message sender role"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Message content"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "role": "user",
                    "content": "What is Python?"
                }
            ]
        }
    }


class ChatStreamRequest(BaseModel):
    """
    T006: Request payload for streaming chat responses.

    Validates:
    - Message: 1-10,000 chars, not whitespace-only
    - conversationId: UUID with 'conv-' prefix
    - conversationHistory: Array of role/content pairs
    - model: One of the supported LLM models

    Based on contracts/chat-streaming-api.yaml ChatStreamRequest schema.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's message text"
    )
    conversationId: str = Field(
        ...,
        pattern=r'^conv-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        description="Unique conversation identifier (UUID with 'conv-' prefix)"
    )
    conversationHistory: List[HistoryMessage] = Field(
        default_factory=list,
        description="Previous messages for context (optional, default: empty array)"
    )
    model: Literal["gpt-5", "gpt-5-codex"] = Field(
        default="gpt-5",
        description="LLM model to use for this request"
    )

    @field_validator('message')
    @classmethod
    def message_not_whitespace(cls, v: str) -> str:
        """Validate message is not only whitespace"""
        if not v.strip():
            raise ValueError('Message cannot be empty or whitespace-only')
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Hello, how are you?",
                    "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000",
                    "conversationHistory": [],
                    "model": "gpt-5"
                },
                {
                    "message": "What was my previous question?",
                    "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000",
                    "conversationHistory": [
                        {
                            "role": "user",
                            "content": "Tell me about Python"
                        },
                        {
                            "role": "assistant",
                            "content": "Python is a high-level programming language..."
                        }
                    ],
                    "model": "gpt-5"
                }
            ]
        }
    }


class StreamStartEvent(BaseModel):
    """Stream start event indicating message ID"""
    type: Literal["start"] = "start"
    messageId: str = Field(
        ...,
        pattern=r'^msg-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        description="Unique ID for this AI response message"
    )


class StreamChunkEvent(BaseModel):
    """Stream chunk event with partial content"""
    type: Literal["chunk"] = "chunk"
    content: str = Field(
        ...,
        description="Partial text content to append"
    )


class StreamDoneEvent(BaseModel):
    """Stream completion event"""
    type: Literal["done"] = "done"
    messageId: str = Field(
        ...,
        pattern=r'^msg-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        description="ID of the completed message"
    )
    model: Literal["gpt-5", "gpt-5-codex"] = Field(
        ...,
        description="Model that generated this response"
    )


class StreamErrorEvent(BaseModel):
    """Stream error event"""
    type: Literal["error"] = "error"
    code: Literal[
        "authentication_error",
        "rate_limit_exceeded",
        "model_unavailable",
        "network_timeout",
        "llm_provider_error",
        "validation_error"
    ] = Field(
        ...,
        description="Machine-readable error code"
    )
    message: str = Field(
        ...,
        description="Human-readable error message (non-technical)"
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error context (optional)"
    )
