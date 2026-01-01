"""
LLM Service Module

Manages LLM interactions using LangChain for streaming chat responses.
Supports multiple LLM providers (OpenAI, Anthropic, Ollama, local models).

Feature: 005-llm-integration
Tasks: T007 (skeleton), T019-T021, T024 (implementation)
"""

from typing import AsyncIterator, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

from src.config import settings, MODEL_MAPPINGS, validate_api_key
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """
    LLM service for streaming chat responses via LangChain.

    Supports:
    - Multiple LLM models (GPT-5, GPT-5 Codex, future: Claude, Ollama, local)
    - Streaming responses with Server-Sent Events (SSE)
    - Conversation history management
    - Error handling with user-friendly messages
    """

    def __init__(self):
        """Initialize LLM service with configured models."""
        # Validate API key on initialization
        if not validate_api_key():
            logger.warning("OpenAI API key not configured - LLM service may fail")

        # Initialize LangChain models for each supported LLM
        self.models: Dict[str, ChatOpenAI] = {
            "gpt-5": ChatOpenAI(
                model=MODEL_MAPPINGS["gpt-5"],
                streaming=True,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                timeout=settings.stream_timeout,
            ),
            "gpt-5-codex": ChatOpenAI(
                model=MODEL_MAPPINGS["gpt-5-codex"],
                streaming=True,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                timeout=settings.stream_timeout,
            ),
        }

        logger.info(
            f"LLM Service initialized with models: {list(self.models.keys())}"
        )

    async def stream_chat_response(
        self,
        message: str,
        conversation_history: list[dict],
        model: str = "gpt-5"
    ) -> AsyncIterator[str]:
        """
        Stream AI chat response using LangChain.

        This is a skeleton implementation. Full implementation in T019.

        Args:
            message: User's message text
            conversation_history: Previous messages for context [{role, content}, ...]
            model: LLM model to use (default: gpt-5)

        Yields:
            Server-Sent Event formatted strings:
            - event: message\ndata: {"type": "start", "messageId": "msg-xxx"}\n\n
            - event: message\ndata: {"type": "chunk", "content": "text"}\n\n
            - event: message\ndata: {"type": "done", "messageId": "msg-xxx", "model": "gpt-5"}\n\n
            - event: error\ndata: {"type": "error", "code": "...", "message": "..."}\n\n
        """
        # Skeleton - full implementation in T019
        logger.info(f"stream_chat_response called with model={model}")
        raise NotImplementedError("Implementation in T019")

    def _convert_history_to_messages(
        self, conversation_history: list[dict]
    ) -> list[BaseMessage]:
        """
        Convert conversation history dicts to LangChain message objects.

        Full implementation in T047 (User Story 3).

        Args:
            conversation_history: List of {role, content} dicts

        Returns:
            List of LangChain message objects (HumanMessage, AIMessage, SystemMessage)
        """
        # Skeleton - full implementation in T047
        return []

    def _classify_error(self, error: Exception) -> str:
        """
        Classify exception into user-facing error code.

        Full implementation in T020.

        Args:
            error: Exception raised during LLM interaction

        Returns:
            Error code string (e.g., "authentication_error", "rate_limit_exceeded")
        """
        # Skeleton - full implementation in T020
        return "llm_provider_error"

    def _get_user_friendly_message(self, code: str, error: Exception) -> str:
        """
        Get non-technical error message for users.

        Full implementation in T021.

        Args:
            code: Error code from _classify_error
            error: Original exception

        Returns:
            User-friendly error message
        """
        # Skeleton - full implementation in T021
        return "An unexpected error occurred. Please try again."
