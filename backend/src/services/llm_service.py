"""
LLM Service Module

Manages LLM interactions using LangChain for streaming chat responses.
Supports multiple LLM providers (OpenAI, Anthropic, Ollama, local models).

Feature: 005-llm-integration
Tasks: T007 (skeleton), T019-T021, T024 (implementation)
"""

import json
import uuid
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

        T019: Full implementation with SSE streaming.

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
        # Generate unique message ID
        message_id = f"msg-{uuid.uuid4()}"

        logger.info(
            f"Starting stream: model={model}, messageId={message_id}, "
            f"historyLength={len(conversation_history)}"
        )

        try:
            # Validate model exists
            if model not in self.models:
                raise ValueError(
                    f"Unsupported model: {model}. "
                    f"Available models: {', '.join(self.models.keys())}"
                )

            # Get LangChain model instance
            llm = self.models[model]

            # Convert conversation history to LangChain messages
            # For User Story 1, history is empty (US3 will implement full history)
            history_messages = self._convert_history_to_messages(conversation_history)

            # Create message list: history + current user message
            messages = history_messages + [HumanMessage(content=message)]

            # Yield start event
            start_event = {
                "type": "start",
                "messageId": message_id
            }
            yield f"event: message\ndata: {json.dumps(start_event)}\n\n"

            logger.debug(f"Stream started: {message_id}")

            # Stream response from LLM
            chunk_count = 0
            async for chunk in llm.astream(messages):
                # Extract content from chunk
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)

                if content:
                    chunk_count += 1
                    chunk_event = {
                        "type": "chunk",
                        "content": content
                    }
                    yield f"event: message\ndata: {json.dumps(chunk_event)}\n\n"

            logger.info(f"Stream completed: {message_id}, chunks={chunk_count}")

            # Yield done event
            done_event = {
                "type": "done",
                "messageId": message_id,
                "model": model
            }
            yield f"event: message\ndata: {json.dumps(done_event)}\n\n"

        except Exception as e:
            logger.error(f"Stream error: {message_id}, error={str(e)}", exc_info=True)

            # Classify error and get user-friendly message
            error_code = self._classify_error(e)
            error_message = self._get_user_friendly_message(error_code, e)

            # Yield error event
            error_event = {
                "type": "error",
                "code": error_code,
                "message": error_message
            }
            yield f"event: error\ndata: {json.dumps(error_event)}\n\n"

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

        T020: Full implementation with error type detection.

        Args:
            error: Exception raised during LLM interaction

        Returns:
            Error code string (e.g., "authentication_error", "rate_limit_exceeded")
        """
        error_str = str(error).lower()
        error_type = type(error).__name__

        # Authentication errors
        if "api_key" in error_str or "authentication" in error_str or "unauthorized" in error_str:
            return "authentication_error"

        # Rate limit errors
        if "rate limit" in error_str or "rate_limit" in error_str or "429" in error_str:
            return "rate_limit_exceeded"

        # Timeout errors
        if "timeout" in error_str or error_type in ["TimeoutError", "asyncio.TimeoutError"]:
            return "network_timeout"

        # Model unavailable
        if "model" in error_str and ("unavailable" in error_str or "not found" in error_str):
            return "model_unavailable"

        # Validation errors
        if error_type in ["ValueError", "ValidationError"] or "validation" in error_str:
            return "validation_error"

        # Default: generic LLM provider error
        return "llm_provider_error"

    def _get_user_friendly_message(self, code: str, error: Exception) -> str:
        """
        Get non-technical error message for users.

        T021: Full implementation with user-friendly messages.

        Args:
            code: Error code from _classify_error
            error: Original exception

        Returns:
            User-friendly error message
        """
        # Map error codes to user-friendly messages
        error_messages = {
            "authentication_error": (
                "Unable to connect to the AI service. "
                "Please check your API configuration."
            ),
            "rate_limit_exceeded": (
                "The AI service is temporarily busy. "
                "Please try again in a moment."
            ),
            "model_unavailable": (
                "The selected AI model is temporarily unavailable. "
                "Please try again later or select a different model."
            ),
            "network_timeout": (
                "The request took too long to complete. "
                "Please try again or try a shorter message."
            ),
            "validation_error": (
                "There was a problem with your request. "
                "Please check your message and try again."
            ),
            "llm_provider_error": (
                "An unexpected error occurred. "
                "Please try again."
            ),
        }

        return error_messages.get(code, error_messages["llm_provider_error"])
