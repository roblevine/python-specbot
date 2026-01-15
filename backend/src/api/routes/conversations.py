"""
Conversations API Routes

CRUD endpoints for conversation management.
Based on contracts/conversations-api.yaml.

Feature: 010-server-side-conversations
Tasks: T011, T012, T018 (GET endpoints), T019, T020, T027 (POST/PUT), T028, T032 (DELETE)
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from src.schemas import (
    Conversation,
    ConversationListResponse,
    ConversationResponse,
    ConversationSummary,
    CreateConversationRequest,
    ErrorResponse,
    UpdateConversationRequest,
)
from src.services.storage_service import get_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


def generate_conversation_id() -> str:
    """Generate a new conversation ID with conv- prefix."""
    return f"conv-{uuid.uuid4()}"


def get_current_timestamp() -> str:
    """Get current timestamp in ISO-8601 format."""
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


@router.get(
    "",
    response_model=ConversationListResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    summary="List all conversations",
    description="Returns a list of conversation summaries (without full message content)"
)
async def list_conversations() -> ConversationListResponse:
    """
    T011: List all conversations.

    Returns conversation summaries ordered by most recently updated.
    """
    logger.info("Listing all conversations")

    try:
        storage = get_storage()
        summaries = await storage.list_conversations()

        logger.info(f"Successfully listed {len(summaries)} conversations")
        return ConversationListResponse(
            status="success",
            conversations=summaries
        )
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to list conversations", "code": "STORAGE_READ_ERROR"}
        )


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Conversation not found"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    summary="Get a single conversation",
    description="Returns a conversation with all its messages"
)
async def get_conversation(conversation_id: str) -> ConversationResponse:
    """
    T012: Get a single conversation by ID.

    Returns the full conversation including all messages.
    """
    logger.info(f"Getting conversation: {conversation_id}")

    try:
        storage = get_storage()
        conversation = await storage.get_conversation(conversation_id)

        if conversation is None:
            logger.warning(f"Conversation not found: {conversation_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Conversation not found",
                    "code": "CONVERSATION_NOT_FOUND",
                    "detail": f"No conversation found with ID {conversation_id}"
                }
            )

        logger.info(f"Successfully retrieved conversation: {conversation_id}")
        return ConversationResponse(
            status="success",
            conversation=conversation
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get conversation", "code": "STORAGE_READ_ERROR"}
        )


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    summary="Create a new conversation",
    description="Creates a new conversation with optional initial data"
)
async def create_conversation(
    request: CreateConversationRequest
) -> ConversationResponse:
    """
    T019: Create a new conversation.

    Accepts optional ID, title, and initial messages.
    Generates ID and timestamp if not provided.
    """
    logger.info("Creating new conversation")

    try:
        storage = get_storage()

        # Generate ID if not provided
        conversation_id = request.id or generate_conversation_id()

        # Check if ID already exists
        if request.id and await storage.conversation_exists(request.id):
            logger.warning(f"Conversation ID already exists: {request.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Conversation ID already exists",
                    "code": "VALIDATION_ERROR"
                }
            )

        timestamp = get_current_timestamp()

        conversation = Conversation(
            id=conversation_id,
            title=request.title or "New Conversation",
            createdAt=timestamp,
            updatedAt=timestamp,
            messages=request.messages or []
        )

        saved = await storage.save_conversation(conversation)

        logger.info(f"Successfully created conversation: {conversation_id}")
        return ConversationResponse(
            status="success",
            conversation=saved
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to create conversation", "code": "STORAGE_WRITE_ERROR"}
        )


@router.put(
    "/{conversation_id}",
    response_model=ConversationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    summary="Update a conversation",
    description="Updates conversation data (title, messages)"
)
async def update_conversation(
    conversation_id: str,
    request: UpdateConversationRequest
) -> ConversationResponse:
    """
    T020: Update an existing conversation.

    Updates title and/or messages. Messages array replaces existing.
    """
    logger.info(f"Updating conversation: {conversation_id}")

    try:
        storage = get_storage()

        # Get existing conversation
        existing = await storage.get_conversation(conversation_id)
        if existing is None:
            logger.warning(f"Conversation not found for update: {conversation_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Conversation not found",
                    "code": "CONVERSATION_NOT_FOUND",
                    "detail": f"No conversation found with ID {conversation_id}"
                }
            )

        # Update fields
        updated_title = request.title if request.title is not None else existing.title
        updated_messages = request.messages if request.messages is not None else existing.messages

        conversation = Conversation(
            id=conversation_id,
            title=updated_title,
            createdAt=existing.createdAt,
            updatedAt=get_current_timestamp(),
            messages=updated_messages
        )

        saved = await storage.save_conversation(conversation)

        logger.info(f"Successfully updated conversation: {conversation_id}")
        return ConversationResponse(
            status="success",
            conversation=saved
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to update conversation", "code": "STORAGE_WRITE_ERROR"}
        )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Conversation not found"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    summary="Delete a conversation",
    description="Permanently deletes a conversation and all its messages"
)
async def delete_conversation(conversation_id: str) -> None:
    """
    T028: Delete a conversation.

    Permanently removes the conversation and all messages.
    """
    logger.info(f"Deleting conversation: {conversation_id}")

    try:
        storage = get_storage()
        deleted = await storage.delete_conversation(conversation_id)

        if not deleted:
            logger.warning(f"Conversation not found for deletion: {conversation_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Conversation not found",
                    "code": "CONVERSATION_NOT_FOUND",
                    "detail": f"No conversation found with ID {conversation_id}"
                }
            )

        logger.info(f"Successfully deleted conversation: {conversation_id}")
        # Return None for 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to delete conversation", "code": "STORAGE_WRITE_ERROR"}
        )
