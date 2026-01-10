"""
Chat Streaming API Routes

Handles streaming chat responses from LLM models.
Implements Server-Sent Events (SSE) for real-time response streaming.

Feature: 005-llm-integration
Tasks: T008 (skeleton), T022-T023 (implementation)
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.schemas import ChatStreamRequest
from src.services.llm_service import LLMService
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["Chat", "Streaming"])


@router.post("/stream")
async def stream_chat_response(request: ChatStreamRequest):
    """
    Stream AI chat response using Server-Sent Events (SSE).

    T022-T024: Full implementation with validation, streaming, and logging.

    Args:
        request: ChatStreamRequest with message, conversationId, conversationHistory, model

    Returns:
        StreamingResponse with text/event-stream content type

    Raises:
        HTTPException: On validation errors or LLM failures
    """
    logger.info(
        f"POST /api/v1/chat/stream - model={request.model}, "
        f"conversationId={request.conversationId}, "
        f"history_length={len(request.conversationHistory)}, "
        f"message_length={len(request.message)}"
    )

    # T023: Request validation is handled by Pydantic (ChatStreamRequest)
    # Additional validation could go here if needed

    # Initialize LLM service
    llm_service = LLMService()

    # T024: Structured logging for LLM request
    logger.debug(
        f"Stream request details: conversationId={request.conversationId}, "
        f"model={request.model}, historyMessages={len(request.conversationHistory)}"
    )

    # Convert conversationHistory to list of dicts for service
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in request.conversationHistory
    ]

    # T022: Call LLMService and return StreamingResponse
    return StreamingResponse(
        llm_service.stream_chat_response(
            message=request.message,
            conversation_history=history,
            model=request.model
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
