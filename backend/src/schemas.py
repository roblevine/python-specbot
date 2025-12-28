"""
Pydantic Schemas for API Request/Response Models

Defines data validation and serialization for the Message API.
Based on contracts/message-api.yaml and data-model.md.

Feature: 003-backend-api-loopback
Tasks: T030, T031, T032
"""

from datetime import datetime
from typing import Any, Dict, Literal, Optional

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
        description="Optional conversation ID (UUID format)",
        pattern=r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
        examples=["a1b2c3d4-5678-90ab-cdef-123456789abc"]
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
                    "conversationId": "a1b2c3d4-5678-90ab-cdef-123456789abc",
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
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="Server-side timestamp (ISO-8601)",
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
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="Server-side timestamp (ISO-8601)"
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
