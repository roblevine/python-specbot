"""
LLM Service - Multi-Provider Chat Integration via LangChain

Manages LLM initialization, configuration, and message processing for
all registered LLM providers via the provider registry.

Features: 006-openai-langchain-chat, 011-anthropic-support, 012-modular-model-providers
Extended: 024-add-langchain-tools - Added tool calling support
"""

import json
import os
import asyncio
import traceback
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, List, Union
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.language_models.chat_models import BaseChatModel

from src.utils.logger import get_logger

# Import error classes from providers.base (centralized to avoid circular imports)
from src.services.providers.base import (
    LLMServiceError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMBadRequestError
)

# Import registry after error classes to avoid circular imports
from src.services.providers import registry

from src.config.models import (
    load_model_configuration,
    get_default_model,
    validate_model_id,
    get_model_by_id,
    get_provider_for_model,
    ModelConfigurationError,
    PROVIDERS
)
from src.schemas import (
    TokenEvent, CompleteEvent, ErrorEvent,
    ToolCallEvent, ToolResultEvent, ToolErrorEvent, ResultLink
)

logger = get_logger(__name__)

# Default system prompt to guide model behavior
# Instructs the model to match the user's language for natural multilingual support
DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant. Always respond in the same language as the user's message. Be concise, accurate, and helpful."""


def _is_debug_mode() -> bool:
    """Check if DEBUG mode is enabled."""
    return os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')


def _build_debug_info(error: Exception, error_type: str) -> Optional[Dict[str, Any]]:
    """
    Build debug_info dict for streaming errors when DEBUG mode is enabled.

    Args:
        error: The exception that occurred
        error_type: The type/class name of the error

    Returns:
        Dict with debug info if DEBUG mode is enabled, None otherwise
    """
    if not _is_debug_mode():
        return None

    return {
        "error_type": error_type,
        "error_message": str(error),
        "original_error": str(getattr(error, 'original_error', error)),
        "traceback": traceback.format_exc()
    }


def _llm_error_to_event(error: LLMServiceError) -> tuple[str, str]:
    """
    T031: Map an LLMServiceError to error message and code for streaming.

    Args:
        error: The LLMServiceError to map

    Returns:
        Tuple of (error_message, error_code)
    """
    if isinstance(error, LLMAuthenticationError):
        return error.message, "AUTH_ERROR"
    if isinstance(error, LLMRateLimitError):
        return error.message, "RATE_LIMIT"
    if isinstance(error, LLMConnectionError):
        return error.message, "CONNECTION_ERROR"
    if isinstance(error, LLMTimeoutError):
        return error.message, "TIMEOUT"
    if isinstance(error, LLMBadRequestError):
        return error.message, "LLM_ERROR"
    # Generic LLMServiceError
    return error.message, "LLM_ERROR"


# ============================================================================
# Tool Support Functions (Feature: 024-add-langchain-tools)
# ============================================================================

def get_enabled_tools() -> List:
    """
    T019: Get list of enabled tool instances.

    Loads tool configuration and returns instantiated tools.

    Returns:
        List of BaseTool instances for enabled tools
    """
    from src.config.tools import load_tool_configuration
    from src.services.tools import load_enabled_tools

    try:
        tool_configs = load_tool_configuration()
        # Convert Pydantic models to dicts
        config_dicts = [
            {"id": tc.id, "name": tc.name, "description": tc.description, "enabled": tc.enabled}
            for tc in tool_configs
        ]
        tools = load_enabled_tools(config_dicts)
        logger.info(f"Loaded {len(tools)} enabled tool(s)")
        return tools
    except Exception as e:
        logger.warning(f"Failed to load tools: {e}")
        return []


def get_langchain_tools(tools: List) -> List:
    """
    T019: Convert BaseTool instances to LangChain-compatible tools.

    Args:
        tools: List of BaseTool instances

    Returns:
        List of LangChain tool objects
    """
    from src.services.tools import get_langchain_tools as _get_lc_tools
    return _get_lc_tools(tools)


def bind_tools_to_llm(llm: BaseChatModel, langchain_tools: List, provider: str) -> BaseChatModel:
    """
    T019: Bind tools to an LLM instance.

    Handles provider-specific configuration for tool binding.

    Args:
        llm: LLM instance to bind tools to
        langchain_tools: List of LangChain tools
        provider: Provider ID ('openai', 'anthropic', 'ollama')

    Returns:
        LLM with tools bound
    """
    if not langchain_tools:
        return llm

    try:
        if provider == "anthropic":
            # Anthropic requires strict mode for tool calling
            return llm.bind_tools(langchain_tools)
        elif provider == "ollama":
            # Ollama tool support is experimental
            logger.warning("Tool calling with Ollama is experimental and may not work with all models")
            return llm.bind_tools(langchain_tools)
        else:
            # OpenAI and others use default binding
            return llm.bind_tools(langchain_tools)
    except Exception as e:
        logger.error(f"Failed to bind tools to LLM: {e}")
        raise


def _generate_tool_call_id() -> str:
    """Generate a unique tool call ID."""
    return f"tool-{uuid.uuid4()}"


def get_llm_for_model(model_id: str, config=None) -> BaseChatModel:
    """
    T029: Factory function to get the appropriate LLM instance for a model.

    Uses the provider registry to create LLM instances, eliminating
    provider-specific code paths.

    Args:
        model_id: The model ID to create an LLM instance for
        config: Optional ModelsConfiguration (loads from env if not provided)

    Returns:
        BaseChatModel: Configured chat model instance from the appropriate provider

    Raises:
        ValueError: If model not found or provider not supported
        LLMAuthenticationError: If provider API key not configured
    """
    if config is None:
        config = load_model_configuration()

    model = get_model_by_id(model_id, config)
    if not model:
        raise ValueError(f"Model not found: {model_id}")

    provider_id = model.provider

    # T029: Use registry to get provider instance
    provider = registry.get(provider_id)
    if not provider:
        raise ValueError(f"Unsupported provider: {provider_id}")

    logger.debug(f"Creating LLM instance for model: {model_id} via {provider_id} provider")
    return provider.create_llm(model_id)


def convert_to_langchain_messages(
    history: List[Dict[str, str]],
    include_system_prompt: bool = True
) -> List[BaseMessage]:
    """
    Convert conversation history to LangChain message format.

    Converts an array of message objects with sender/text fields into
    LangChain message types (HumanMessage for user, AIMessage for system).
    Optionally prepends a system prompt to ensure consistent behavior.

    Args:
        history: List of message dictionaries with "sender" and "text" fields
                 sender can be "user" or "system"
        include_system_prompt: Whether to include the default system prompt
                               (helps multilingual models respond in English)

    Returns:
        List of LangChain message objects (SystemMessage, HumanMessage, or AIMessage)
    """
    logger.debug(f"Converting {len(history)} message(s) to LangChain format")

    langchain_messages: List[BaseMessage] = []

    # Add system prompt first to guide model behavior (especially for multilingual models)
    if include_system_prompt:
        langchain_messages.append(SystemMessage(content=DEFAULT_SYSTEM_PROMPT))

    for msg in history:
        sender = msg.get("sender")
        text = msg.get("text", "")

        if sender == "user":
            langchain_messages.append(HumanMessage(content=text))
        elif sender == "system":
            langchain_messages.append(AIMessage(content=text))
        else:
            logger.warning(f"Unknown sender type: {sender}, skipping message")

    logger.debug(f"Converted to {len(langchain_messages)} LangChain message(s)")
    return langchain_messages


def _map_exception_to_llm_error(e: Exception) -> LLMServiceError:
    """
    T018: Map provider-specific exceptions to LLM service errors.

    Handles both OpenAI and Anthropic exception types.

    Args:
        e: The exception to map

    Returns:
        Appropriate LLMServiceError subclass
    """
    # OpenAI exceptions
    if isinstance(e, OpenAIAuthenticationError):
        return LLMAuthenticationError(original_error=e)
    if isinstance(e, OpenAIRateLimitError):
        return LLMRateLimitError(original_error=e)
    if isinstance(e, OpenAIAPIConnectionError):
        return LLMConnectionError(original_error=e)
    if isinstance(e, (OpenAIAPITimeoutError, asyncio.TimeoutError)):
        return LLMTimeoutError(original_error=e)
    if isinstance(e, OpenAIBadRequestError):
        return LLMBadRequestError(original_error=e)

    # Anthropic exceptions
    if isinstance(e, AnthropicAuthenticationError):
        return LLMAuthenticationError(original_error=e)
    if isinstance(e, AnthropicRateLimitError):
        return LLMRateLimitError(original_error=e)
    if isinstance(e, AnthropicAPIConnectionError):
        return LLMConnectionError(original_error=e)
    if isinstance(e, AnthropicAPITimeoutError):
        return LLMTimeoutError(original_error=e)
    if isinstance(e, AnthropicBadRequestError):
        return LLMBadRequestError(original_error=e)

    # Default: generic LLM error
    return LLMServiceError("AI service error occurred", original_error=e)


async def get_ai_response(
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    model: Optional[str] = None
) -> tuple[str, str]:
    """
    T015: Get AI response for a user message with multi-provider support.

    Sends the user message to the appropriate LLM provider via LangChain and returns
    the AI-generated response.

    Args:
        message: User message text
        history: Optional list of previous messages with sender/text fields
        model: Optional model ID to use for this request.
               If not provided, uses the configured default model.

    Returns:
        Tuple of (AI-generated response text, model ID used)

    Raises:
        LLMAuthenticationError: If API key is invalid → 503
        LLMRateLimitError: If rate limit exceeded → 503
        LLMConnectionError: If cannot reach API → 503
        LLMTimeoutError: If request times out → 504
        LLMBadRequestError: If request is malformed → 400
        ValueError: If message is empty or model is invalid
    """
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")

    logger.info(f"Processing AI request for message: {message[:50]}...")
    if history:
        logger.info(f"Including {len(history)} message(s) from conversation history")

    provider = None  # Initialize for exception handler scope

    try:
        # Load model configuration
        config = load_model_configuration()

        # Determine which model to use
        if model:
            model_to_use = model
            logger.info(f"User-selected model: {model_to_use}")
        else:
            model_to_use = get_default_model(config)
            logger.info(f"Using default model: {model_to_use}")

        # Validate model against configuration
        if not validate_model_id(model_to_use, config):
            available_models = [m.id for m in config.models]
            logger.error(f"Invalid model requested: {model_to_use}. Available: {', '.join(available_models)}")
            raise ValueError(
                f"Invalid model: {model_to_use}. "
                f"Available models: {', '.join(available_models)}"
            )

        # Get provider for logging
        provider = get_provider_for_model(model_to_use, config)
        logger.info(f"Using provider: {provider}")

        # T015: Get LLM instance using factory function
        llm = get_llm_for_model(model_to_use, config)

        # Build conversation history
        conversation = history.copy() if history else []
        conversation.append({"sender": "user", "text": message})

        # Convert to LangChain format
        langchain_messages = convert_to_langchain_messages(conversation)

        # Call LLM service
        logger.debug(f"Invoking LLM with {len(langchain_messages)} message(s)")
        response = await llm.ainvoke(langchain_messages)

        # Extract content from response
        ai_response = response.content
        logger.info(f"AI response received: {len(ai_response)} characters")
        logger.debug(f"AI response preview: {ai_response[:100]}...")

        return ai_response, model_to_use

    except LLMServiceError:
        # Re-raise LLM service errors as-is
        raise

    except asyncio.TimeoutError as e:
        # Handle asyncio timeout separately as it's not provider-specific
        logger.error(f"LLM request timed out: {type(e).__name__}")
        raise LLMTimeoutError(original_error=e)

    except ValueError:
        # Re-raise validation errors (invalid model, etc.) as-is
        raise

    except Exception as e:
        # T030: Use provider's error mapping for all other exceptions
        logger.error(f"LLM error: {type(e).__name__}: {str(e)}")
        from src.services.providers.errors import map_provider_error
        raise map_provider_error(e, provider or "unknown")


async def stream_ai_response(
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    model: Optional[str] = None
):
    """
    T016: Stream AI response as token-by-token events with multi-provider support.

    Streams the AI response as a sequence of events using Server-Sent Events protocol.
    Uses LangChain's astream() for token-by-token streaming from the LLM.

    Args:
        message: User message text
        history: Optional list of previous messages with sender/text fields
        model: Optional model ID to use for this request.

    Yields:
        TokenEvent: For each token/chunk from the LLM
        CompleteEvent: Final event indicating stream completion with model info
        ErrorEvent: If an error occurs during streaming
    """
    if not message or not message.strip():
        yield ErrorEvent(
            error="Message cannot be empty",
            code="UNKNOWN"
        )
        return

    logger.info(f"Starting streaming for message: {message[:50]}...")
    if history:
        logger.info(f"Including {len(history)} message(s) from conversation history")

    provider = None  # Initialize for exception handler scope

    try:
        # Load model configuration
        config = load_model_configuration()

        # Determine which model to use
        if model:
            model_to_use = model
            logger.info(f"User-selected model: {model_to_use}")
        else:
            model_to_use = get_default_model(config)
            logger.info(f"Using default model: {model_to_use}")

        # Validate model against configuration
        if not validate_model_id(model_to_use, config):
            available_models = [m.id for m in config.models]
            logger.error(f"Invalid model requested: {model_to_use}. Available: {', '.join(available_models)}")
            yield ErrorEvent(
                error=f"Invalid model: {model_to_use}",
                code="UNKNOWN"
            )
            return

        # Get provider for logging
        provider = get_provider_for_model(model_to_use, config)
        logger.info(f"Using provider: {provider}")

        # T016: Get LLM instance using factory function
        llm = get_llm_for_model(model_to_use, config)

        # Build conversation history
        conversation = history.copy() if history else []
        conversation.append({"sender": "user", "text": message})

        # Convert to LangChain format
        langchain_messages = convert_to_langchain_messages(conversation)

        # Stream LLM response
        logger.debug(f"Streaming from LLM with {len(langchain_messages)} message(s)")

        async for chunk in llm.astream(langchain_messages):
            # Extract content from chunk
            # Handle different content formats from providers:
            # - OpenAI: chunk.content is a string
            # - Anthropic: chunk.content may be a list of content blocks
            content = chunk.content
            if isinstance(content, list):
                # Extract text from content blocks (Anthropic format)
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        text_parts.append(block.get('text', ''))
                    elif isinstance(block, str):
                        text_parts.append(block)
                    elif hasattr(block, 'text'):
                        text_parts.append(block.text)
                content = ''.join(text_parts)

            # Skip empty chunks
            if content:
                yield TokenEvent(content=content)

        # Yield completion event
        logger.info(f"Stream completed successfully using model: {model_to_use}")
        yield CompleteEvent(model=model_to_use)

    except LLMServiceError as e:
        # T031: Handle LLM service errors using unified error mapping
        logger.error(f"LLM error during streaming: {type(e).__name__}: {e.message}")
        if _is_debug_mode():
            logger.warning("DEBUG mode enabled - including detailed error info in streaming response")
        error_msg, error_code = _llm_error_to_event(e)
        yield ErrorEvent(
            error=error_msg,
            code=error_code,
            debug_info=_build_debug_info(e, type(e).__name__)
        )

    except asyncio.TimeoutError as e:
        # Handle asyncio timeout separately as it's not provider-specific
        logger.error(f"LLM request timed out during streaming: {type(e).__name__}")
        if _is_debug_mode():
            logger.warning("DEBUG mode enabled - including detailed error info in streaming response")
        yield ErrorEvent(
            error="Request timed out",
            code="TIMEOUT",
            debug_info=_build_debug_info(e, type(e).__name__)
        )

    except Exception as e:
        # T031: Use provider's error mapping for all other exceptions
        logger.error(f"Unexpected error during streaming: {type(e).__name__}: {str(e)}")
        if _is_debug_mode():
            logger.warning("DEBUG mode enabled - including detailed error info in streaming response")

        # Map the exception using provider's error mapper
        from src.services.providers.errors import map_provider_error
        mapped_error = map_provider_error(e, provider or "unknown")
        error_msg, error_code = _llm_error_to_event(mapped_error)

        yield ErrorEvent(
            error=error_msg,
            code=error_code,
            debug_info=_build_debug_info(e, type(e).__name__)
        )


# ============================================================================
# Tool-Enabled Streaming (Feature: 024-add-langchain-tools)
# ============================================================================

async def stream_ai_response_with_tools(
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    model: Optional[str] = None,
    tools: Optional[List] = None
):
    """
    T020: Stream AI response with tool calling support.

    Extends stream_ai_response with tool execution capabilities.
    Detects tool calls in the stream, executes them, and yields
    appropriate events for frontend display.

    Args:
        message: User message text
        history: Optional list of previous messages
        model: Optional model ID
        tools: Optional list of BaseTool instances. If None, loads enabled tools.

    Yields:
        TokenEvent: For each token/chunk from the LLM
        ToolCallEvent: When LLM initiates a tool call
        ToolResultEvent: When tool completes successfully
        ToolErrorEvent: When tool execution fails
        CompleteEvent: Final event with summary
        ErrorEvent: If an error occurs
    """
    if not message or not message.strip():
        yield ErrorEvent(
            error="Message cannot be empty",
            code="UNKNOWN"
        )
        return

    logger.info(f"Starting tool-enabled streaming for message: {message[:50]}...")

    # Load tools if not provided
    if tools is None:
        tools = get_enabled_tools()

    # If no tools available, fall back to regular streaming
    if not tools:
        logger.info("No tools available, using standard streaming")
        async for event in stream_ai_response(message, history, model):
            yield event
        return

    provider = None
    tool_calls_summary = []  # Track tool calls for CompleteEvent

    try:
        # Load model configuration
        config = load_model_configuration()

        # Determine which model to use
        if model:
            model_to_use = model
        else:
            model_to_use = get_default_model(config)

        logger.info(f"Using model: {model_to_use}")

        # Validate model
        if not validate_model_id(model_to_use, config):
            yield ErrorEvent(
                error=f"Invalid model: {model_to_use}",
                code="UNKNOWN"
            )
            return

        provider = get_provider_for_model(model_to_use, config)
        logger.info(f"Using provider: {provider}")

        # Get LLM and bind tools
        llm = get_llm_for_model(model_to_use, config)
        langchain_tools = get_langchain_tools(tools)

        if langchain_tools:
            llm = bind_tools_to_llm(llm, langchain_tools, provider)
            logger.info(f"Bound {len(langchain_tools)} tools to LLM")

        # Build tool lookup using LangChain tool names
        # LangChain tools may have different names than our tool IDs
        tool_lookup = {}
        for tool, lc_tool in zip(tools, langchain_tools):
            # Use the LangChain tool's name for lookup (this is what the LLM will call)
            tool_lookup[lc_tool.name] = tool
            logger.debug(f"Registered tool lookup: {lc_tool.name} -> {tool.id}")

        # Build conversation history
        conversation = history.copy() if history else []
        conversation.append({"sender": "user", "text": message})

        # Convert to LangChain format
        langchain_messages = convert_to_langchain_messages(conversation)

        # Agentic loop - handle tool calls
        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            logger.debug(f"Tool loop iteration {iteration}")

            # Collect the full response (we need to check for tool calls)
            response_content = ""
            tool_calls = []
            # Track tool_call_chunks by index for proper accumulation
            # OpenAI streams tool calls in pieces: name first, then args in chunks
            tool_call_chunks_by_index = {}

            async for chunk in llm.astream(langchain_messages):
                # Check for streaming tool call chunks FIRST
                # OpenAI sends tool_call_chunks during streaming - accumulate these
                # Note: Don't use elif - some chunks may have both tool_calls and tool_call_chunks
                if hasattr(chunk, 'tool_call_chunks') and chunk.tool_call_chunks:
                    # Handle streaming tool call chunks - accumulate by index
                    for tc in chunk.tool_call_chunks:
                        idx = tc.get('index', 0)
                        if idx not in tool_call_chunks_by_index:
                            # Initialize new tool call
                            # Use 'or' pattern because get() returns None if key exists with None value
                            tool_call_chunks_by_index[idx] = {
                                'id': tc.get('id') or '',
                                'name': tc.get('name') or '',
                                'args': tc.get('args') or ''
                            }
                        else:
                            # Accumulate into existing tool call
                            existing = tool_call_chunks_by_index[idx]
                            if tc.get('id'):
                                existing['id'] = existing['id'] or tc.get('id') or ''
                            if tc.get('name'):
                                existing['name'] = existing['name'] or tc.get('name') or ''
                            # Concatenate args strings
                            existing['args'] += tc.get('args') or ''
                # Only use tool_calls if we're NOT accumulating chunks
                # (some non-streaming providers may use tool_calls directly)
                elif hasattr(chunk, 'tool_calls') and chunk.tool_calls and not tool_call_chunks_by_index:
                    # Complete tool calls (non-streaming providers only)
                    tool_calls.extend(chunk.tool_calls)

                # Stream content tokens
                if chunk.content:
                    # Handle different content formats from providers:
                    # - OpenAI: chunk.content is a string
                    # - Anthropic: chunk.content may be a list of content blocks
                    content = chunk.content
                    if isinstance(content, list):
                        # Extract text from content blocks (Anthropic format)
                        text_parts = []
                        for block in content:
                            if isinstance(block, dict) and block.get('type') == 'text':
                                text_parts.append(block.get('text', ''))
                            elif isinstance(block, str):
                                text_parts.append(block)
                            elif hasattr(block, 'text'):
                                text_parts.append(block.text)
                        content = ''.join(text_parts)

                    if content:
                        response_content += content
                        yield TokenEvent(content=content)

            # After streaming, convert accumulated chunks to tool_calls
            if tool_call_chunks_by_index:
                for idx in sorted(tool_call_chunks_by_index.keys()):
                    tc = tool_call_chunks_by_index[idx]
                    # Parse args JSON string to dict
                    args_str = tc.get('args', '')
                    if args_str:
                        try:
                            tc['args'] = json.loads(args_str)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse tool args JSON: {args_str}")
                            tc['args'] = {}
                    else:
                        tc['args'] = {}
                    tool_calls.append(tc)
                logger.debug(f"Accumulated {len(tool_call_chunks_by_index)} tool calls from chunks")

            # If no tool calls, we're done
            if not tool_calls:
                logger.info("No tool calls in response, completing")
                break

            # Filter out malformed tool calls (empty names)
            # Use 'or' pattern because get() returns None if key exists with None value
            valid_tool_calls = [tc for tc in tool_calls if (tc.get('name') or '').strip()]
            if len(valid_tool_calls) < len(tool_calls):
                skipped = len(tool_calls) - len(valid_tool_calls)
                logger.warning(f"Skipping {skipped} malformed tool call(s) with empty names")

            if not valid_tool_calls:
                logger.warning("All tool calls had empty names, completing without tools")
                break

            tool_calls = valid_tool_calls

            # Process tool calls
            logger.info(f"Processing {len(tool_calls)} tool call(s)")

            # First, add an AIMessage with the tool_calls to the conversation
            # OpenAI requires ToolMessages to follow an AIMessage with tool_calls
            ai_message_tool_calls = []
            for tc in tool_calls:
                ai_message_tool_calls.append({
                    "id": tc.get('id') or _generate_tool_call_id(),
                    "name": tc.get('name') or '',
                    "args": tc.get('args') or {}
                })
            langchain_messages.append(AIMessage(
                content=response_content or "",
                tool_calls=ai_message_tool_calls
            ))

            for tool_call in tool_calls:
                tool_name = tool_call.get('name') or ''
                tool_args = tool_call.get('args') or {}
                tool_call_id = tool_call.get('id') or _generate_tool_call_id()

                # Generate our own ID for tracking
                our_tool_id = _generate_tool_call_id()

                # Find the tool
                tool = tool_lookup.get(tool_name)
                if not tool:
                    available_tools = list(tool_lookup.keys())
                    logger.warning(f"Unknown tool: {tool_name}. Available tools: {available_tools}")
                    debug_info = None
                    if _is_debug_mode():
                        debug_info = {
                            "requestedTool": tool_name,
                            "availableTools": available_tools,
                            "hint": "The LLM requested a tool that is not registered. Check tool names in to_langchain_tool()."
                        }
                    yield ToolErrorEvent(
                        id=our_tool_id,
                        status="error",
                        error=f"Tool not found: {tool_name}",
                        errorCode="TOOL_NOT_FOUND",
                        durationMs=0,
                        debugInfo=debug_info
                    )
                    tool_calls_summary.append({
                        "id": our_tool_id,
                        "toolId": tool_name,
                        "status": "error",
                        "durationMs": 0
                    })
                    # Still need to add ToolMessage for this failed lookup
                    # OpenAI requires a ToolMessage for every tool_call
                    langchain_messages.append(
                        ToolMessage(
                            content=f"Error: Tool not found: {tool_name}",
                            tool_call_id=tool_call_id
                        )
                    )
                    continue

                # Emit tool call event
                yield ToolCallEvent(
                    id=our_tool_id,
                    toolId=tool.id,
                    toolName=tool.name,
                    args=tool_args
                )

                # Execute the tool
                start_time = datetime.utcnow()
                try:
                    result = await tool.execute(**tool_args)
                    end_time = datetime.utcnow()
                    duration_ms = int((end_time - start_time).total_seconds() * 1000)

                    if result.success:
                        # Convert links to ResultLink format
                        result_links = None
                        if result.links:
                            result_links = [
                                ResultLink(
                                    title=link.get("title", "Link"),
                                    url=link.get("url", ""),
                                    snippet=link.get("snippet")
                                )
                                for link in result.links
                            ]

                        yield ToolResultEvent(
                            id=our_tool_id,
                            status="success",
                            result=result.result,
                            resultLinks=result_links,
                            durationMs=duration_ms
                        )

                        tool_calls_summary.append({
                            "id": our_tool_id,
                            "toolId": tool.id,
                            "status": "success",
                            "durationMs": duration_ms
                        })

                        # Add tool result to conversation for next iteration
                        langchain_messages.append(
                            ToolMessage(
                                content=result.result or "Tool completed successfully",
                                tool_call_id=tool_call_id
                            )
                        )
                    else:
                        yield ToolErrorEvent(
                            id=our_tool_id,
                            status="error",
                            error=result.error or "Tool execution failed",
                            errorCode=result.error_code or "EXECUTION_ERROR",
                            durationMs=duration_ms,
                            debugInfo=_build_debug_info(
                                Exception(result.error), "ToolExecutionError"
                            ) if _is_debug_mode() else None
                        )

                        tool_calls_summary.append({
                            "id": our_tool_id,
                            "toolId": tool.id,
                            "status": "error",
                            "durationMs": duration_ms
                        })

                        # Add error result to conversation
                        langchain_messages.append(
                            ToolMessage(
                                content=f"Error: {result.error}",
                                tool_call_id=tool_call_id
                            )
                        )

                except Exception as e:
                    end_time = datetime.utcnow()
                    duration_ms = int((end_time - start_time).total_seconds() * 1000)

                    logger.error(f"Tool execution error: {e}")

                    yield ToolErrorEvent(
                        id=our_tool_id,
                        status="error",
                        error=f"Tool execution failed: {str(e)}",
                        errorCode="EXECUTION_ERROR",
                        durationMs=duration_ms,
                        debugInfo=_build_debug_info(e, type(e).__name__) if _is_debug_mode() else None
                    )

                    tool_calls_summary.append({
                        "id": our_tool_id,
                        "toolId": tool.id,
                        "status": "error",
                        "durationMs": duration_ms
                    })

                    langchain_messages.append(
                        ToolMessage(
                            content=f"Error: {str(e)}",
                            tool_call_id=tool_call_id
                        )
                    )

        # Check if we exited the loop without generating any response
        # This can happen when all tool calls fail repeatedly
        failed_tool_calls = [tc for tc in tool_calls_summary if tc.get("status") == "error"]
        if iteration >= max_iterations and len(failed_tool_calls) == len(tool_calls_summary) and len(tool_calls_summary) > 0:
            error_msg = f"Unable to complete request after {max_iterations} attempts. All {len(failed_tool_calls)} tool calls failed."
            logger.error(error_msg)
            debug_info = None
            if _is_debug_mode():
                debug_info = {
                    "totalIterations": iteration,
                    "totalToolCalls": len(tool_calls_summary),
                    "failedToolCalls": len(failed_tool_calls),
                    "toolCallDetails": tool_calls_summary,
                    "hint": "Check that tool names in to_langchain_tool() match what the LLM expects."
                }
            yield ErrorEvent(
                error=error_msg,
                code="LLM_ERROR",
                debug_info=debug_info
            )
            return

        # Yield completion event with tool call summary
        logger.info(f"Stream completed with {len(tool_calls_summary)} tool call(s)")
        yield CompleteEvent(
            model=model_to_use,
            totalTokens=None  # We don't track tokens in streaming
        )

    except LLMServiceError as e:
        logger.error(f"LLM error during tool streaming: {e.message}")
        error_msg, error_code = _llm_error_to_event(e)
        yield ErrorEvent(
            error=error_msg,
            code=error_code,
            debug_info=_build_debug_info(e, type(e).__name__)
        )

    except asyncio.TimeoutError as e:
        logger.error("Timeout during tool streaming")
        yield ErrorEvent(
            error="Request timed out",
            code="TIMEOUT",
            debug_info=_build_debug_info(e, type(e).__name__)
        )

    except Exception as e:
        logger.error(f"Unexpected error during tool streaming: {e}")
        from src.services.providers.errors import map_provider_error
        mapped_error = map_provider_error(e, provider or "unknown")
        error_msg, error_code = _llm_error_to_event(mapped_error)
        yield ErrorEvent(
            error=error_msg,
            code=error_code,
            debug_info=_build_debug_info(e, type(e).__name__)
        )
