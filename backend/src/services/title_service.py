"""
Title Generation Service

Generates conversation titles using LLM based on conversation content.

Feature: 019-llm-conversation-titles
Tasks: T009, T013
"""

from typing import Dict, List
from langchain_core.messages import HumanMessage

from src.utils.logger import get_logger
from src.services.llm_service import get_llm_for_model

logger = get_logger(__name__)

# Maximum title length
MAX_TITLE_LENGTH = 60


def build_title_prompt(messages: List[Dict[str, str]]) -> str:
    """
    Build a prompt for title generation from conversation messages.

    Args:
        messages: List of message dictionaries with "sender" and "text" fields

    Returns:
        str: Prompt string for LLM to generate title
    """
    # Extract first user message and first assistant response
    user_message = ""
    assistant_message = ""

    for msg in messages:
        if msg.get("sender") == "user" and not user_message:
            user_message = msg.get("text", "")
        elif msg.get("sender") == "system" and not assistant_message:
            assistant_message = msg.get("text", "")

        if user_message and assistant_message:
            break

    prompt = f"""Generate a concise title (maximum {MAX_TITLE_LENGTH} characters) that summarizes this conversation.
Return ONLY the title text, no quotes, no explanation, no prefix like "Title:".

User: {user_message}
Assistant: {assistant_message}"""

    logger.debug(f"Built title prompt with {len(prompt)} characters")
    return prompt


def truncate_title(title: str, max_length: int = MAX_TITLE_LENGTH) -> str:
    """
    Truncate title to maximum length at word boundary.

    Args:
        title: The title string to truncate
        max_length: Maximum allowed length (default: 60)

    Returns:
        str: Truncated title
    """
    if len(title) <= max_length:
        return title

    # Find the last space before max_length
    truncated = title[:max_length]
    last_space = truncated.rfind(' ')

    if last_space > max_length // 2:
        # Truncate at word boundary if we're not cutting too much
        truncated = truncated[:last_space]
    else:
        # Just hard truncate if no good word boundary
        truncated = title[:max_length]

    logger.debug(f"Truncated title from {len(title)} to {len(truncated)} characters")
    return truncated.strip()


def clean_title_response(response: str) -> str:
    """
    Clean LLM response to extract just the title.

    Removes quotes, common prefixes, and extra whitespace.

    Args:
        response: Raw LLM response string

    Returns:
        str: Cleaned title string
    """
    if not response:
        return ""

    title = response.strip()

    # Remove surrounding quotes
    if (title.startswith('"') and title.endswith('"')) or \
       (title.startswith("'") and title.endswith("'")):
        title = title[1:-1]

    # Remove common LLM prefixes
    prefixes_to_remove = [
        "Title:",
        "title:",
        "TITLE:",
        "Conversation title:",
        "conversation title:",
        "Here is a title:",
        "here is a title:",
        "The title is:",
        "the title is:",
    ]

    for prefix in prefixes_to_remove:
        if title.lower().startswith(prefix.lower()):
            title = title[len(prefix):].strip()
            break

    # Final cleanup
    title = title.strip()

    # Remove quotes again in case they were inside prefix
    if (title.startswith('"') and title.endswith('"')) or \
       (title.startswith("'") and title.endswith("'")):
        title = title[1:-1]

    return title.strip()


async def generate_title(messages: List[Dict[str, str]], model_id: str) -> str:
    """
    Generate a conversation title using LLM.

    Args:
        messages: List of message dictionaries with "sender" and "text" fields
                 Must contain at least 2 messages (user + assistant)
        model_id: Model ID to use for title generation

    Returns:
        str: Generated title (max 60 characters)

    Raises:
        ValueError: If messages array is invalid or model not found
        LLMServiceError: If LLM call fails
    """
    logger.info(f"Generating title using model: {model_id}")
    logger.debug(f"Input messages count: {len(messages)}")

    if not messages or len(messages) < 2:
        logger.error("Title generation requires at least 2 messages")
        raise ValueError("Messages array must contain at least 2 messages")

    try:
        # Build prompt
        prompt = build_title_prompt(messages)

        # Get LLM instance
        logger.debug(f"Getting LLM instance for model: {model_id}")
        llm = get_llm_for_model(model_id)

        # Create message for LLM
        llm_message = HumanMessage(content=prompt)

        # Call LLM
        logger.debug("Invoking LLM for title generation")
        response = await llm.ainvoke([llm_message])

        # Extract and clean response
        raw_title = response.content
        logger.debug(f"Raw LLM response: {raw_title[:100]}...")

        cleaned_title = clean_title_response(raw_title)
        logger.debug(f"Cleaned title: {cleaned_title}")

        # Truncate if needed
        final_title = truncate_title(cleaned_title)

        logger.info(f"Generated title: '{final_title}' ({len(final_title)} chars)")
        return final_title

    except ValueError as e:
        # Re-raise validation errors
        logger.error(f"Validation error in title generation: {str(e)}")
        raise

    except Exception as e:
        # Log and re-raise other errors
        logger.error(f"Error generating title: {type(e).__name__}: {str(e)}")
        raise
