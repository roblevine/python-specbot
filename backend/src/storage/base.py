"""
Abstract Storage Interface

Defines the contract for conversation storage implementations.
Enables swapping between file storage, database, or other backends.

Feature: 010-server-side-conversations
Task: T007
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.schemas import Conversation, ConversationSummary


class ConversationStorage(ABC):
    """
    Abstract base class for conversation storage.

    Implementations must provide CRUD operations for conversations.
    This abstraction allows future migration from file storage to database.
    """

    @abstractmethod
    async def list_conversations(self) -> List[ConversationSummary]:
        """
        List all conversations (summaries only).

        Returns:
            List of conversation summaries ordered by updatedAt (descending).
        """
        pass

    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a single conversation with all messages.

        Args:
            conversation_id: The conversation ID to retrieve.

        Returns:
            The conversation if found, None otherwise.
        """
        pass

    @abstractmethod
    async def save_conversation(self, conversation: Conversation) -> Conversation:
        """
        Save a conversation (create or update).

        Args:
            conversation: The conversation to save.

        Returns:
            The saved conversation.
        """
        pass

    @abstractmethod
    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: The conversation ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        pass

    @abstractmethod
    async def conversation_exists(self, conversation_id: str) -> bool:
        """
        Check if a conversation exists.

        Args:
            conversation_id: The conversation ID to check.

        Returns:
            True if exists, False otherwise.
        """
        pass
