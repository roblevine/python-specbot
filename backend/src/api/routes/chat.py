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

    This is a skeleton implementation. Full implementation in T022.

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
        f"history_length={len(request.conversationHistory)}"
    )

    # Skeleton - full implementation in T022
    raise HTTPException(
        status_code=501,
        detail="Chat streaming endpoint not yet implemented (T022)"
    )
