"""
Messages API Routes

Implements POST /api/v1/messages endpoint for message loopback.

Feature: 003-backend-api-loopback User Story 1
Tasks: T035, T036, T037
"""

from datetime import datetime
from typing import Union

from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from src.schemas import MessageRequest, MessageResponse, ErrorResponse
from src.services.message_service import create_loopback_message, validate_message
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(tags=["messages"])


@router.post(
    "/messages",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request - Invalid message"},
        422: {"model": ErrorResponse, "description": "Unprocessable Entity - Schema validation failure"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Send message and receive loopback response",
    description="Accepts a user message and returns a loopback response with 'api says: ' prefix"
)
async def send_message(request: MessageRequest) -> MessageResponse:
    """
    T035: POST /api/v1/messages endpoint.

    Implements User Story 1:
    - Accepts message from frontend
    - Returns loopback response with "api says: " prefix
    - Validates message content
    - Handles errors appropriately

    Args:
        request: MessageRequest with user message

    Returns:
        MessageResponse with loopback message

    Raises:
        HTTPException: 400 for validation errors, 500 for server errors
    """
    try:
        # Log incoming request (T037 - per FR-014)
        logger.info(
            f"Received message request: "
            f"message_length={len(request.message)}, "
            f"conversation_id={request.conversationId}"
        )
        logger.debug(f"Message content: {request.message[:100]}...")

        # T034: Validate message (additional validation beyond Pydantic)
        validate_message(request.message)

        # T033: Create loopback message
        loopback_message = create_loopback_message(request.message)

        # Create response
        response = MessageResponse(
            status="success",
            message=loopback_message,
            timestamp=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        )

        # Log response (T037 - per FR-014)
        logger.info(
            f"Sending loopback response: "
            f"response_length={len(response.message)}, "
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
