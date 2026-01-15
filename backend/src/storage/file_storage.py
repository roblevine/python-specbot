"""
File-Based Storage Implementation

Implements ConversationStorage using JSON file with file locking.
Designed for single-user applications with future database migration path.

Feature: 010-server-side-conversations
Task: T008
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from filelock import FileLock

from src.schemas import Conversation, ConversationSummary
from src.storage.base import ConversationStorage

logger = logging.getLogger(__name__)


class FileStorage(ConversationStorage):
    """
    File-based conversation storage using JSON.

    Features:
    - Thread-safe file locking via filelock
    - Atomic read-modify-write operations
    - Schema versioning for future migrations
    - Graceful handling of missing/corrupt files
    """

    SCHEMA_VERSION = "1.0.0"

    def __init__(self, storage_path: str):
        """
        Initialize file storage.

        Args:
            storage_path: Path to the JSON storage file.
        """
        self.storage_path = Path(storage_path)
        self.lock_path = Path(f"{storage_path}.lock")

        # Ensure parent directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"FileStorage initialized with path: {self.storage_path}")

    def _get_lock(self) -> FileLock:
        """Get a file lock for thread-safe operations."""
        return FileLock(str(self.lock_path))

    def _read_storage(self) -> Dict[str, Any]:
        """
        Read storage file with error handling.

        Returns:
            Storage data dict with conversations list.
        """
        if not self.storage_path.exists():
            logger.debug("Storage file does not exist, returning empty storage")
            return {
                "version": self.SCHEMA_VERSION,
                "conversations": []
            }

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Read {len(data.get('conversations', []))} conversations from storage")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Corrupt storage file, resetting: {e}")
            return {
                "version": self.SCHEMA_VERSION,
                "conversations": []
            }
        except Exception as e:
            logger.error(f"Error reading storage file: {e}")
            raise

    def _write_storage(self, data: Dict[str, Any]) -> None:
        """
        Write storage file atomically.

        Args:
            data: Storage data to write.
        """
        try:
            # Write to temp file first, then rename (atomic on most systems)
            temp_path = self.storage_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Atomic rename
            temp_path.replace(self.storage_path)
            logger.debug(f"Wrote {len(data.get('conversations', []))} conversations to storage")
        except Exception as e:
            logger.error(f"Error writing storage file: {e}")
            raise

    async def list_conversations(self) -> List[ConversationSummary]:
        """List all conversations as summaries."""
        with self._get_lock():
            data = self._read_storage()
            conversations = data.get("conversations", [])

            summaries = []
            for conv in conversations:
                summaries.append(ConversationSummary(
                    id=conv["id"],
                    title=conv["title"],
                    createdAt=conv["createdAt"],
                    updatedAt=conv["updatedAt"],
                    messageCount=len(conv.get("messages", []))
                ))

            # Sort by updatedAt descending (most recent first)
            summaries.sort(key=lambda x: x.updatedAt, reverse=True)

            logger.info(f"Listed {len(summaries)} conversations")
            return summaries

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a single conversation by ID."""
        with self._get_lock():
            data = self._read_storage()
            conversations = data.get("conversations", [])

            for conv in conversations:
                if conv["id"] == conversation_id:
                    logger.info(f"Found conversation: {conversation_id}")
                    return Conversation(**conv)

            logger.info(f"Conversation not found: {conversation_id}")
            return None

    async def save_conversation(self, conversation: Conversation) -> Conversation:
        """Save a conversation (create or update)."""
        with self._get_lock():
            data = self._read_storage()
            conversations = data.get("conversations", [])

            # Find existing conversation index
            existing_index = None
            for i, conv in enumerate(conversations):
                if conv["id"] == conversation.id:
                    existing_index = i
                    break

            # Convert to dict for storage
            conv_dict = conversation.model_dump()

            if existing_index is not None:
                # Update existing
                conversations[existing_index] = conv_dict
                logger.info(f"Updated conversation: {conversation.id}")
            else:
                # Create new
                conversations.append(conv_dict)
                logger.info(f"Created conversation: {conversation.id}")

            data["conversations"] = conversations
            self._write_storage(data)

            return conversation

    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation by ID."""
        with self._get_lock():
            data = self._read_storage()
            conversations = data.get("conversations", [])

            initial_count = len(conversations)
            conversations = [c for c in conversations if c["id"] != conversation_id]

            if len(conversations) < initial_count:
                data["conversations"] = conversations
                self._write_storage(data)
                logger.info(f"Deleted conversation: {conversation_id}")
                return True

            logger.info(f"Conversation not found for deletion: {conversation_id}")
            return False

    async def conversation_exists(self, conversation_id: str) -> bool:
        """Check if a conversation exists."""
        with self._get_lock():
            data = self._read_storage()
            conversations = data.get("conversations", [])

            exists = any(c["id"] == conversation_id for c in conversations)
            logger.debug(f"Conversation {conversation_id} exists: {exists}")
            return exists
