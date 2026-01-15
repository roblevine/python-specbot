"""
Pydantic Schemas for API Request/Response Models

Defines data validation and serialization for the Message API.
Based on contracts/message-api.yaml and data-model.md.

Feature: 003-backend-api-loopback (extended by 006-openai-langchain-chat, 009-message-streaming)
Tasks: T030, T031, T032, T020, T021, T007 (streaming events)

Feature: 010-server-side-conversations
Tasks: T004, T005, T006 (conversation storage schemas)
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class HistoryMessage(BaseModel):
    """
    T020: Individual message in conversation history.

    Represents a single message from conversation history
    for context-aware AI responses.

    Feature: 006-openai-langchain-chat User Story 2
    """

    sender: Literal["user", "system"] = Field(
        ...,
        description="Message sender (user or system/AI)"
    )
    text: str = Field(
        ...,
        min_length=1,
        description="Message content"
    )

    @field_validator('text')
    @classmethod
    def text_not_whitespace(cls, v: str) -> str:
        """Validate text is not only whitespace (T021)"""
        if not v.strip():
            raise ValueError('Message text cannot be only whitespace')
        return v


class MessageRequest(BaseModel):
    """
    T030: Request payload for sending a message.

    Validates FR-007, FR-010, FR-012:
    - Message required, 1-10,000 chars
    - Accepts special characters, emoji, multi-byte
    - Validates format and rejects malformed data

    T020: Extended to support conversation history for context-aware responses.
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
    history: Optional[List[HistoryMessage]] = Field(
        None,
        description="Optional conversation history for context-aware responses",
        examples=[[
            {"sender": "user", "text": "My name is Alice"},
            {"sender": "system", "text": "Nice to meet you, Alice!"}
        ]]
    )
    model: Optional[str] = Field(
        None,
        description="Model ID to use for this request. If not provided, uses the configured default model.",
        examples=["gpt-4", "gpt-3.5-turbo"]
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
    model: str = Field(
        ...,
        description="Model ID that generated this response",
        examples=["gpt-4", "gpt-3.5-turbo"]
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
# Streaming Event Schemas (Feature: 009-message-streaming)
# ============================================================================

class TokenEvent(BaseModel):
    """
    T007: Streaming token event.

    Represents a single token/chunk from LLM streaming response.

    Feature: 009-message-streaming Task T007
    """

    type: Literal["token"] = Field(
        default="token",
        description="Event type identifier"
    )
    content: str = Field(
        ...,
        description="Token/chunk content from LLM"
    )

    def to_sse_format(self) -> str:
        """
        Convert to SSE (Server-Sent Events) format.

        Returns:
            str: SSE formatted string "data: <JSON>\n\n"
        """
        json_str = self.model_dump_json()
        return f"data: {json_str}\n\n"


class CompleteEvent(BaseModel):
    """
    T007: Streaming completion event.

    Signals successful completion of streaming response.

    Feature: 009-message-streaming Task T007
    """

    type: Literal["complete"] = Field(
        default="complete",
        description="Event type identifier"
    )
    model: str = Field(
        ...,
        description="Model ID that generated the response"
    )
    totalTokens: Optional[int] = Field(
        None,
        description="Total number of tokens in the response (optional)"
    )

    def to_sse_format(self) -> str:
        """
        Convert to SSE (Server-Sent Events) format.

        Returns:
            str: SSE formatted string "data: <JSON>\n\n"
        """
        json_str = self.model_dump_json()
        return f"data: {json_str}\n\n"


class ErrorEvent(BaseModel):
    """
    T007: Streaming error event.

    Signals error during streaming response.

    Feature: 009-message-streaming Task T007
    """

    type: Literal["error"] = Field(
        default="error",
        description="Event type identifier"
    )
    error: str = Field(
        ...,
        description="Human-readable error message"
    )
    code: Literal[
        "TIMEOUT",
        "RATE_LIMIT",
        "LLM_ERROR",
        "AUTH_ERROR",
        "CONNECTION_ERROR",
        "UNKNOWN"
    ] = Field(
        ...,
        description="Machine-readable error code"
    )

    def to_sse_format(self) -> str:
        """
        Convert to SSE (Server-Sent Events) format.

        Returns:
            str: SSE formatted string "data: <JSON>\n\n"
        """
        json_str = self.model_dump_json()
        return f"data: {json_str}\n\n"


# ============================================================================
# Conversation Storage Schemas (Feature: 010-server-side-conversations)
# ============================================================================

class ConversationMessage(BaseModel):
    """
    T004: Full message schema for conversation storage.

    Extends HistoryMessage with additional metadata for persistence.

    Feature: 010-server-side-conversations Task T004
    """

    id: str = Field(
        ...,
        description="Unique message identifier",
        pattern=r'^msg-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
        examples=["msg-12345678-1234-1234-1234-123456789abc"]
    )
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Message content"
    )
    sender: Literal["user", "system"] = Field(
        ...,
        description="Message sender (user or system/AI)"
    )
    timestamp: str = Field(
        ...,
        description="When the message was created (ISO-8601)",
        examples=["2026-01-15T10:00:00.000Z"]
    )
    status: Literal["pending", "sent", "error"] = Field(
        ...,
        description="Message delivery status"
    )
    model: Optional[str] = Field(
        None,
        description="Model ID used for system responses",
        examples=["gpt-4", "gpt-3.5-turbo"]
    )
    errorMessage: Optional[str] = Field(
        None,
        description="Error description (only if status is error)"
    )
    errorType: Optional[str] = Field(
        None,
        description="Error category (only if status is error)"
    )
    errorCode: Optional[int] = Field(
        None,
        description="Error code (only if status is error)"
    )


class Conversation(BaseModel):
    """
    T005: Full conversation schema for storage.

    Contains all conversation metadata and messages.

    Feature: 010-server-side-conversations Task T005
    """

    id: str = Field(
        ...,
        description="Unique conversation identifier",
        pattern=r'^conv-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
        examples=["conv-12345678-1234-1234-1234-123456789abc"]
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Conversation title"
    )
    createdAt: str = Field(
        ...,
        description="When the conversation was created (ISO-8601)",
        examples=["2026-01-15T10:00:00.000Z"]
    )
    updatedAt: str = Field(
        ...,
        description="When the conversation was last modified (ISO-8601)",
        examples=["2026-01-15T10:05:30.000Z"]
    )
    messages: List[ConversationMessage] = Field(
        default_factory=list,
        description="Ordered list of messages (chronological)"
    )


class ConversationSummary(BaseModel):
    """
    T005: Lightweight conversation representation for listing.

    Excludes full message content for performance.

    Feature: 010-server-side-conversations Task T005
    """

    id: str = Field(
        ...,
        description="Unique conversation identifier",
        pattern=r'^conv-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
    )
    title: str = Field(
        ...,
        description="Conversation title"
    )
    createdAt: str = Field(
        ...,
        description="When the conversation was created"
    )
    updatedAt: str = Field(
        ...,
        description="When the conversation was last modified"
    )
    messageCount: int = Field(
        ...,
        ge=0,
        description="Number of messages in conversation"
    )


class CreateConversationRequest(BaseModel):
    """
    T006: Request payload for creating a new conversation.

    Feature: 010-server-side-conversations Task T006
    """

    id: Optional[str] = Field(
        None,
        description="Optional client-generated conversation ID",
        pattern=r'^conv-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
    )
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Optional title (defaults to 'New Conversation')"
    )
    messages: Optional[List[ConversationMessage]] = Field(
        None,
        description="Optional initial messages"
    )


class UpdateConversationRequest(BaseModel):
    """
    T006: Request payload for updating a conversation.

    Feature: 010-server-side-conversations Task T006
    """

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated conversation title"
    )
    messages: Optional[List[ConversationMessage]] = Field(
        None,
        description="Complete messages array (replaces existing)"
    )


class ConversationResponse(BaseModel):
    """
    T006: Response payload for single conversation operations.

    Feature: 010-server-side-conversations Task T006
    """

    status: Literal["success"] = Field(
        default="success",
        description="Response status"
    )
    conversation: Conversation = Field(
        ...,
        description="The conversation data"
    )


class ConversationListResponse(BaseModel):
    """
    T006: Response payload for listing conversations.

    Feature: 010-server-side-conversations Task T006
    """

    status: Literal["success"] = Field(
        default="success",
        description="Response status"
    )
    conversations: List[ConversationSummary] = Field(
        default_factory=list,
        description="List of conversation summaries"
    )
