"""
Messages API Routes

Implements POST /api/v1/messages endpoint for AI chat.

Feature: 006-openai-langchain-chat User Story 1
Tasks: T014, T015
"""

import time
from datetime import datetime
from typing import Union

from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from src.schemas import MessageRequest, MessageResponse, ErrorResponse
from src.services.message_service import validate_message
from src.services.llm_service import get_ai_response, load_config
from src.utils.logger import get_logger, llm_request_start, llm_request_complete, llm_request_error

logger = get_logger(__name__)

# Create router
router = APIRouter(tags=["messages"])


@router.post(
    "/messages",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request - Invalid message"},
        422: {"model": ErrorResponse, "description": "Unprocessable Entity - Schema validation failure"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        503: {"model": ErrorResponse, "description": "Service Unavailable - AI service issues"},
        504: {"model": ErrorResponse, "description": "Gateway Timeout - AI request timed out"}
    },
    summary="Send message and receive AI response",
    description="Accepts a user message and returns an AI-generated response from OpenAI ChatGPT via LangChain"
)
async def send_message(request: MessageRequest) -> MessageResponse:
    """
    T014: POST /api/v1/messages endpoint with AI integration.

    Implements User Story 1:
    - Accepts message from frontend
    - Routes message to OpenAI ChatGPT via LLM service
    - Returns AI-generated response
    - Validates message content
    - Handles errors appropriately

    Args:
        request: MessageRequest with user message

    Returns:
        MessageResponse with AI-generated message

    Raises:
        HTTPException: 400 for validation errors, 500 for server errors, 503/504 for AI service errors
    """
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

        # Get model configuration for logging
        config = load_config()
        model = config['model']

        # T015: Log LLM request start
        llm_request_start(request.message, model)

        # T014: Get AI response from LLM service
        ai_response = await get_ai_response(request.message)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # T015: Log LLM request completion
        llm_request_complete(request.message, ai_response, model, duration_ms)

        # Create response
        response = MessageResponse(
            status="success",
            message=ai_response,
            timestamp=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
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

    except Exception as e:
        # T015: Log LLM error
        try:
            config = load_config()
            model = config['model']
            llm_request_error(request.message, model, e)
        except:
            # If we can't load config, just log the error normally
            logger.error(f"LLM error (config unavailable): {e}", exc_info=True)

        # T036: Handle unexpected errors (500 Internal Server Error)
        logger.error(f"Unexpected error processing message: {e}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "error": "Internal server error occurred",
                "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            }
        )
