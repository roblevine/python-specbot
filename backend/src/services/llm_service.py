"""
LLM Service - OpenAI ChatGPT Integration via LangChain

Manages LLM initialization, configuration, and message processing.

Feature: 006-openai-langchain-chat Phase 2 (Foundational)
Tasks: T006, T007
"""

import os
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Module-level cache for LLM instance (singleton pattern)
_llm_instance: Optional[ChatOpenAI] = None


def load_config() -> Dict[str, str]:
    """
    T007: Load LLM configuration from environment variables.

    Loads OPENAI_API_KEY (required) and OPENAI_MODEL (optional, defaults to gpt-3.5-turbo).

    Returns:
        Dictionary with 'api_key' and 'model' keys

    Raises:
        ValueError: If OPENAI_API_KEY is not set

    Examples:
        >>> # With environment: OPENAI_API_KEY=sk-abc123, OPENAI_MODEL=gpt-4
        >>> config = load_config()
        >>> config['api_key']
        'sk-abc123'
        >>> config['model']
        'gpt-4'
    """
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        logger.error("OPENAI_API_KEY environment variable is not set")
        raise ValueError(
            "OPENAI_API_KEY environment variable is required. "
            "Please set it in your .env file or environment."
        )

    # Default to gpt-3.5-turbo if OPENAI_MODEL not specified
    model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

    logger.info(f"Loaded LLM config: model={model}, api_key={'*' * 8}...{api_key[-4:]}")

    return {
        'api_key': api_key,
        'model': model
    }


def initialize_llm(api_key: str, model: str) -> ChatOpenAI:
    """
    T006: Initialize ChatOpenAI instance with provided configuration.

    Creates and configures a LangChain ChatOpenAI instance for message processing.

    Args:
        api_key: OpenAI API key
        model: Model name (e.g., 'gpt-3.5-turbo', 'gpt-4')

    Returns:
        Configured ChatOpenAI instance

    Examples:
        >>> llm = initialize_llm(api_key="sk-test-key", model="gpt-3.5-turbo")
        >>> type(llm).__name__
        'ChatOpenAI'
    """
    logger.info(f"Initializing ChatOpenAI with model: {model}")

    llm = ChatOpenAI(
        api_key=api_key,
        model=model
    )

    logger.info("ChatOpenAI initialized successfully")
    return llm


def get_llm_instance() -> ChatOpenAI:
    """
    T006: Get or create singleton LLM instance.

    Returns cached LLM instance if available, otherwise creates new instance
    from environment configuration. This ensures we reuse the same instance
    across requests for better performance.

    Returns:
        ChatOpenAI instance

    Raises:
        ValueError: If configuration is missing or invalid

    Examples:
        >>> llm1 = get_llm_instance()
        >>> llm2 = get_llm_instance()
        >>> llm1 is llm2  # Same instance
        True
    """
    global _llm_instance

    if _llm_instance is None:
        logger.info("Creating new LLM instance from environment config")
        config = load_config()
        _llm_instance = initialize_llm(
            api_key=config['api_key'],
            model=config['model']
        )
    else:
        logger.debug("Returning cached LLM instance")

    return _llm_instance


def convert_to_langchain_messages(message: str) -> list:
    """
    T006: Convert user message to LangChain message format.

    Converts a simple string message into the list format expected by
    LangChain's ChatOpenAI.ainvoke() method.

    Args:
        message: User message text

    Returns:
        List of message dictionaries in LangChain format

    Examples:
        >>> messages = convert_to_langchain_messages("Hello")
        >>> isinstance(messages, list)
        True
        >>> len(messages) > 0
        True
    """
    logger.debug(f"Converting message to LangChain format: {message[:50]}...")

    # LangChain expects a list of messages
    # For now, just convert the single message to proper format
    # Future: This will be extended to handle conversation history (User Story 2)
    messages = [
        {"role": "user", "content": message}
    ]

    logger.debug(f"Converted to {len(messages)} LangChain message(s)")
    return messages


async def get_ai_response(message: str) -> str:
    """
    T013: Get AI response for a user message.

    Sends the user message to OpenAI ChatGPT via LangChain and returns
    the AI-generated response.

    Args:
        message: User message text

    Returns:
        AI-generated response text

    Raises:
        ValueError: If message is empty or configuration is invalid
        Exception: If AI service call fails

    Examples:
        >>> import asyncio
        >>> response = asyncio.run(get_ai_response("Hello"))
        >>> len(response) > 0
        True
    """
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")

    logger.info(f"Processing AI request for message: {message[:50]}...")

    # Get LLM instance
    llm = get_llm_instance()

    # Convert message to LangChain format
    langchain_messages = convert_to_langchain_messages(message)

    # Call LLM service
    logger.debug(f"Invoking ChatOpenAI with {len(langchain_messages)} message(s)")
    response = await llm.ainvoke(langchain_messages)

    # Extract content from response
    ai_response = response.content
    logger.info(f"AI response received: {len(ai_response)} characters")
    logger.debug(f"AI response preview: {ai_response[:100]}...")

    return ai_response
