"""
Messages API Routes

Implements POST /api/v1/messages endpoint for AI chat.

Feature: 006-openai-langchain-chat User Story 1
Tasks: T014, T015
"""

import os
import time
import traceback
from datetime import datetime
from typing import Union

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import ValidationError

from src.schemas import MessageRequest, MessageResponse, ErrorResponse
from src.services.message_service import validate_message
from src.services.llm_service import (
    get_ai_response,
    stream_ai_response,
    LLMServiceError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMBadRequestError
)
from src.utils.logger import get_logger, llm_request_start, llm_request_complete, llm_request_error

logger = get_logger(__name__)

# Create router
router = APIRouter(tags=["messages"])


def is_debug_mode() -> bool:
    """Check if DEBUG mode is enabled (checked at runtime, not import time)."""
    return os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")


async def handle_streaming_request(request: MessageRequest) -> StreamingResponse:
    """
    T012: Handle streaming request with SSE (Server-Sent Events).

    Creates an async generator that streams AI response token-by-token
    using the SSE protocol.

    Feature: 009-message-streaming User Story 1 (P1)

    Args:
        request: MessageRequest with user message

    Returns:
        StreamingResponse with text/event-stream content type
    """
    logger.info(
        f"Received streaming request: "
        f"message_length={len(request.message)}, "
        f"conversation_id={request.conversationId}"
    )

    # Validate message (additional validation beyond Pydantic)
    validate_message(request.message)

    # Convert history from Pydantic models to dict format if provided
    history_dict = None
    if request.history:
        history_dict = [
            {"sender": msg.sender, "text": msg.text}
            for msg in request.history
        ]
        logger.debug(f"Including {len(history_dict)} message(s) from conversation history")

    # Log requested model (if specified)
    if request.model:
        logger.info(f"User requested model for streaming: {request.model}")

    async def event_generator():
        """
        Async generator that yields SSE-formatted events.

        Calls stream_ai_response() and converts each event to SSE format.
        """
        try:
            # Stream AI response
            async for event in stream_ai_response(
                message=request.message,
                history=history_dict,
                model=request.model
            ):
                # Convert event to SSE format using to_sse_format() method
                sse_data = event.to_sse_format()
                yield sse_data

        except Exception as e:
            # Log error (don't expose to client via SSE - already handled by stream_ai_response)
            logger.error(f"Error in streaming generator: {type(e).__name__}: {str(e)}")
            # stream_ai_response already yields ErrorEvent, so we don't need to yield here

    # Return StreamingResponse with SSE headers
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.post(
    "/messages",
    response_model=MessageResponse,
    responses={
        200: {
            "description": "Success - Returns JSON or SSE stream based on Accept header",
            "content": {
                "application/json": {"model": MessageResponse},
                "text/event-stream": {"description": "Server-Sent Events stream"}
            }
        },
        400: {"model": ErrorResponse, "description": "Bad Request - Invalid message"},
        422: {"model": ErrorResponse, "description": "Unprocessable Entity - Schema validation failure"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        503: {"model": ErrorResponse, "description": "Service Unavailable - AI service issues"},
        504: {"model": ErrorResponse, "description": "Gateway Timeout - AI request timed out"}
    },
    summary="Send message and receive AI response (streaming or non-streaming)",
    description="Accepts a user message and returns an AI-generated response. "
                "Use Accept: text/event-stream for streaming, Accept: application/json for non-streaming."
)
async def send_message(http_request: Request, request: MessageRequest) -> Union[MessageResponse, StreamingResponse]:
    """
    T014: POST /api/v1/messages endpoint with AI integration.
    T012: Extended to support streaming via Accept: text/event-stream header.

    Implements User Story 1:
    - Accepts message from frontend
    - Routes message to OpenAI ChatGPT via LLM service
    - Returns AI-generated response (streaming or non-streaming)
    - Validates message content
    - Handles errors appropriately

    Feature: 009-message-streaming - Check Accept header for streaming mode

    Args:
        http_request: FastAPI Request object (for accessing headers)
        request: MessageRequest with user message

    Returns:
        StreamingResponse with SSE events if Accept: text/event-stream
        MessageResponse with JSON if Accept: application/json (or default)

    Raises:
        HTTPException: 400 for validation errors, 500 for server errors, 503/504 for AI service errors
    """
    # T012: Check Accept header to determine streaming vs non-streaming
    accept_header = http_request.headers.get("accept", "application/json").lower()
    wants_streaming = "text/event-stream" in accept_header

    # T012: Route to streaming handler if requested
    if wants_streaming:
        return await handle_streaming_request(request)

    # Non-streaming (existing behavior)
    start_time = time.time()

    try:
        # Log incoming request
        logger.info(
            f"Received message request: "
            f"message_length={len(request.message)}, "
            f"conversation_id={request.conversationId}"
        )
        logger.debug(f"Message content: {request.message[:100]}...")

        # Validate message (additional validation beyond Pydantic)
        validate_message(request.message)

        # T024: Convert history from Pydantic models to dict format if provided
        history_dict = None
        if request.history:
            history_dict = [
                {"sender": msg.sender, "text": msg.text}
                for msg in request.history
            ]
            logger.debug(f"Including {len(history_dict)} message(s) from conversation history")

        # Log requested model (if specified)
        if request.model:
            logger.info(f"User requested model: {request.model}")

        # T015: Log LLM request start
        llm_request_start(request.message, request.model or "default")

        # T014, T024: Get AI response from LLM service (with optional history and model)
        # Returns tuple of (response, model_used)
        ai_response, model_used = await get_ai_response(
            request.message,
            history=history_dict,
            model=request.model  # T024: Pass model parameter from request
        )

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # T015: Log LLM request completion
        llm_request_complete(request.message, ai_response, model_used, duration_ms)

        # T025: Create response with model field
        response = MessageResponse(
            status="success",
            message=ai_response,
            timestamp=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            model=model_used  # T025: Include model in response
        )

        # Log response
        logger.info(
            f"Sending AI response: "
            f"response_length={len(response.message)}, "
            f"duration={duration_ms:.2f}ms, "
            f"timestamp={response.timestamp}"
        )

        return response

    except ValueError as e:
        # T036: Handle validation errors (400 Bad Request)
        error_message = str(e)
        logger.warning(f"Validation error: {error_message}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "error": error_message,
                "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            }
        )

    except ValidationError as e:
        # T036: Handle Pydantic validation errors (422 Unprocessable Entity)
        logger.warning(f"Schema validation error: {e}")

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "status": "error",
                "error": "Invalid request format",
                "detail": e.errors(),
                "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            }
        )

    except LLMTimeoutError as e:
        # T039: Handle LLM timeout errors (504 Gateway Timeout)
        logger.warning(f"LLM timeout: {e.message}")

        error_content = {
            "status": "error",
            "error": e.message,
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        }

        # In debug mode, include detailed error information
        if is_debug_mode():
            error_content["debug_info"] = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "original_error": getattr(e, 'original_error', None),
                "traceback": traceback.format_exc()
            }
            logger.warning("DEBUG mode enabled - exposing detailed error information in API response")

        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content=error_content
        )

    except LLMBadRequestError as e:
        # T039: Handle LLM bad request errors (400 Bad Request)
        logger.warning(f"LLM bad request: {e.message}")

        error_content = {
            "status": "error",
            "error": e.message,
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        }

        # In debug mode, include detailed error information
        if is_debug_mode():
            error_content["debug_info"] = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "original_error": getattr(e, 'original_error', None),
                "traceback": traceback.format_exc()
            }
            logger.warning("DEBUG mode enabled - exposing detailed error information in API response")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_content
        )

    except (LLMAuthenticationError, LLMRateLimitError, LLMConnectionError, LLMServiceError) as e:
        # T039: Handle LLM service errors (503 Service Unavailable)
        logger.warning(f"LLM service error: {e.message}")

        error_content = {
            "status": "error",
            "error": e.message,
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        }

        # In debug mode, include detailed error information
        if is_debug_mode():
            error_content["debug_info"] = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "original_error": str(getattr(e, 'original_error', None)),
                "traceback": traceback.format_exc()
            }
            logger.warning("DEBUG mode enabled - exposing detailed error information in API response")

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_content
        )

    except Exception as e:
        # T015: Log LLM error
        model_for_logging = request.model or "unknown"
        llm_request_error(request.message, model_for_logging, e)

        # T036: Handle unexpected errors (500 Internal Server Error)
        logger.error(f"Unexpected error processing message: {e}", exc_info=True)

        # Build error detail based on debug mode
        error_detail = {
            "status": "error",
            "error": "Internal server error occurred",
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        }

        # In debug mode, include detailed error information
        if is_debug_mode():
            error_detail["debug_info"] = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            logger.warning("DEBUG mode enabled - exposing detailed error information in API response")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )
