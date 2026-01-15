"""
Storage Service

Initializes and provides access to the conversation storage layer.
Reads configuration from environment variables.

Feature: 010-server-side-conversations
Task: T009
"""

import logging
import os
from functools import lru_cache
from pathlib import Path

from src.storage.base import ConversationStorage
from src.storage.file_storage import FileStorage

logger = logging.getLogger(__name__)

# Default storage path relative to backend directory
DEFAULT_STORAGE_PATH = "data/conversations.json"


@lru_cache(maxsize=1)
def get_storage() -> ConversationStorage:
    """
    Get the conversation storage instance (singleton).

    Reads STORAGE_PATH from environment, falls back to default.
    Uses lru_cache to ensure single instance.

    Returns:
        ConversationStorage implementation.
    """
    storage_path = os.getenv("STORAGE_PATH", DEFAULT_STORAGE_PATH)

    # If relative path, make it relative to backend directory
    if not os.path.isabs(storage_path):
        # Find backend directory (parent of src)
        backend_dir = Path(__file__).parent.parent.parent
        storage_path = str(backend_dir / storage_path)

    logger.info(f"Initializing storage with path: {storage_path}")

    # Currently only file storage is implemented
    # Future: Add database storage option based on STORAGE_TYPE env var
    return FileStorage(storage_path)


def reset_storage_cache() -> None:
    """
    Clear the storage cache (for testing).

    Forces get_storage() to create a new instance on next call.
    """
    get_storage.cache_clear()
    logger.debug("Storage cache cleared")
