"""
Title Generation API Routes

Provides endpoint for generating conversation titles using LLM.

Feature: 019-llm-conversation-titles
Task: T011
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

from src.schemas import TitleGenerationRequest, TitleGenerationResponse, ErrorResponse
from src.services.title_service import generate_title
from src.services.providers.base import LLMServiceError
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(tags=["titles"])


@router.post(
    "/titles/generate",
    response_model=TitleGenerationResponse,
    responses={
        200: {"model": TitleGenerationResponse, "description": "Title generated successfully"},
        400: {"model": ErrorResponse, "description": "Bad request (validation error or invalid model)"},
        503: {"model": ErrorResponse, "description": "Service unavailable (LLM error)"},
    },
    summary="Generate a conversation title",
    description="""
Generates a succinct title for a conversation using an LLM.

Takes conversation messages and a model ID, returns a generated title.
The title is limited to 60 characters maximum.

The client is responsible for selecting the appropriate model:
- Use the configured title model for the current provider if available
- Fall back to the current conversation model if no title model is configured
"""
)
async def generate_conversation_title(request: TitleGenerationRequest):
    """
    Generate a conversation title from messages.

    Args:
        request: TitleGenerationRequest with messages and model ID

    Returns:
        TitleGenerationResponse with generated title
    """
    logger.info(f"Title generation request received for model: {request.model}")
    logger.debug(f"Messages count: {len(request.messages)}")

    try:
        # Convert request messages to dict format
        messages = [
            {"sender": msg.sender, "text": msg.text}
            for msg in request.messages
        ]

        # Generate title
        title = await generate_title(messages, request.model)

        logger.info(f"Title generated successfully: '{title}'")

        return TitleGenerationResponse(
            status="success",
            title=title
        )

    except ValueError as e:
        # Invalid model or validation error
        logger.warning(f"Title generation validation error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )

    except LLMServiceError as e:
        # LLM service error (rate limit, auth, connection, etc.)
        logger.error(f"LLM service error during title generation: {e.message}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "error": "AI service temporarily unavailable",
                "code": "LLM_ERROR",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )

    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error during title generation: {type(e).__name__}: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "error": "Title generation service unavailable",
                "code": "LLM_ERROR",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
