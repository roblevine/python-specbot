# LLM Library Research and Recommendation

**Date**: 2025-12-30
**Project**: python-specbot
**Feature**: 005-llm-integration
**Python Version**: 3.13.11
**FastAPI Version**: 0.115.0

## Executive Summary

> **⚠️ UPDATED RECOMMENDATION (2025-12-30)**: Use **LangChain** instead of OpenAI SDK
>
> **Context Change**: After initial research recommended OpenAI SDK, requirements clarification revealed that multi-provider support (OpenAI, Anthropic, Ollama, local models), RAG integration, and MCP (Model Context Protocol) support are all **coming within days to weeks**. Given this imminent roadmap, LangChain is the appropriate choice despite higher initial complexity.
>
> **Previous Recommendation**: OpenAI Python SDK (for OpenAI-only use case)
> **Current Recommendation**: LangChain (for imminent multi-provider + RAG + MCP roadmap)

**RECOMMENDATION: Use LangChain (`langchain`, `langchain-openai`)**

After comprehensive research and evaluation including clarification of the product roadmap, LangChain is the appropriate choice for this chatbot project. While it has higher initial complexity than the OpenAI SDK, the imminent requirements for multi-provider support, RAG, and MCP integration justify this choice. Starting with a simpler library would result in complete rework within days/weeks.

## Updated Decision (Post-Requirements Clarification)

### Selected Library: LangChain

**Package**: `langchain`, `langchain-openai`, `langchain-anthropic`, `langchain-community`
**Latest Version**: LangChain 0.3.x (as of December 2025)
**Python Compatibility**: Python 3.9+ (including Python 3.13)
**License**: MIT

### Key Reasons for LangChain

1. **Imminent Multi-Provider Requirement**: Support for OpenAI, Anthropic Claude, Ollama, and local models needed within days/weeks
2. **Built-in RAG Support**: Vector stores, retrievers, document loaders, and embeddings all included
3. **MCP Integration Ready**: Agent framework and tool calling support for Model Context Protocol
4. **Unified Interface**: Same code works across all LLM providers (swap model with one line change)
5. **Production-Ready**: Despite complexity concerns, widely used in production by major companies
6. **Avoid Rework**: Starting with OpenAI SDK would require complete rewrite in days/weeks
7. **Streaming Support**: Works across all providers with consistent API
8. **Memory Management**: Built-in conversation memory and context window handling

### Justification for Complexity

While LangChain has higher complexity than OpenAI SDK:
- **Not speculative**: All features (multi-provider, RAG, MCP) are confirmed for imminent implementation
- **YAGNI doesn't apply**: "You Aren't Gonna Need It" assumes features are uncertain - these are certain and imminent
- **Lower total cost**: One-time learning curve vs. multiple rewrites
- **Future-proof**: Architecture supports planned features without refactoring

### Migration Path

**Phase 1 (Current - Days 1-7)**: Basic OpenAI streaming
- Use `ChatOpenAI` from `langchain-openai`
- Simple conversation chain with memory
- Streaming responses via `astream()`

**Phase 2 (Week 2)**: Multi-provider support
- Add `ChatAnthropic` from `langchain-anthropic`
- Add Ollama support from `langchain-community`
- Provider abstraction already in place (just swap model class)

**Phase 3 (Week 3-4)**: RAG integration
- Add vector store (Chroma, FAISS, or Pinecone)
- Implement document loading and chunking
- Build retrieval chain

**Phase 4 (Week 4-5)**: MCP integration
- Use LangChain agent framework
- Implement tool calling for MCP servers
- Build agent executor

---

## Original Decision (Superseded)

> **Note**: The sections below reflect the initial research for an OpenAI-only use case. This decision was superseded when requirements clarification revealed the imminent multi-provider + RAG + MCP roadmap.

### ~~Selected Library: OpenAI Python SDK (openai)~~ (SUPERSEDED)

**Package**: `openai`
**Latest Version**: 2.14.0 (as of December 2025)
**Python Compatibility**: Python 3.9+ (including Python 3.13 and 3.14)
**License**: Apache 2.0

### Key Reasons

1. **YAGNI Compliance**: Provides exactly what we need—nothing more, nothing less
2. **Direct Integration**: First-party library with official support from OpenAI
3. **Simplicity**: Minimal abstraction layer, straightforward API
4. **Excellent Streaming Support**: Built-in async streaming with SSE compatibility
5. **FastAPI Integration**: Proven patterns with `AsyncOpenAI` and `StreamingResponse`
6. **Production-Ready**: Used by thousands of production applications
7. **GPT-5 Support**: Latest SDK (v2.11.0+) includes GPT-5, GPT-5.1, and GPT-5.2 support
8. **Active Maintenance**: Regular releases throughout 2025

## Evaluation Details

### 1. OpenAI Python SDK

**Strengths:**
- Official first-party library from OpenAI
- Zero abstraction overhead—direct API access
- Native async/await support with `AsyncOpenAI`
- Simple conversation history management (pass list of messages)
- Excellent error handling with specific exception types
- Comprehensive documentation and examples
- Large community (used by virtually all OpenAI API consumers)
- Built-in retry logic and rate limiting
- Python 3.13 fully supported
- GPT-5 family support confirmed (GPT-5, GPT-5 mini, GPT-5 nano, GPT-5.1, GPT-5.2)

**Weaknesses:**
- Locked to OpenAI API only (but this matches current requirements)
- Future multi-provider support would require refactoring (addressed in architecture section)

**Complexity Rating**: ⭐ Low (1/5)
**Streaming Complexity**: ⭐ Low (1/5)
**FastAPI Integration**: ⭐ Excellent
**Documentation Quality**: ⭐⭐⭐⭐⭐ Excellent

**Python 3.13 Compatibility**: ✅ Fully supported. OpenAI Python SDK officially supports Python 3.9+, with explicit Python 3.13 support confirmed in the Agents SDK and core library.

### 2. LangChain

**Strengths:**
- Rich ecosystem with many integrations
- Advanced features for RAG, agents, and complex workflows
- Memory management abstractions
- LangGraph for stateful multi-agent systems
- Supports multiple LLM providers

**Weaknesses:**
- Significant complexity overhead for simple chatbot use case
- Violates YAGNI principle—includes features we don't need
- Multiple dependency packages increase attack surface
- Steeper learning curve and more verbose code
- Community feedback indicates it adds "unnecessary complexity" for simple applications
- Development teams have reported removing LangChain to "just code"
- Dependency bloat even for basic features
- Python 3.13 compatibility issues with some integrations (e.g., langchain-pinecone, numpy version conflicts)

**Complexity Rating**: ⭐⭐⭐⭐ High (4/5)
**Streaming Complexity**: ⭐⭐⭐ Medium (3/5)
**FastAPI Integration**: ⭐⭐⭐ Good (requires more setup)
**Documentation Quality**: ⭐⭐⭐⭐ Good (but overwhelming for simple use cases)

**Python 3.13 Compatibility**: ⚠️ Mostly supported with caveats. Core LangChain and LangGraph support Python 3.13, but some integration packages have dependency conflicts (numpy version requirements, pinecone integration, fireworks integration).

**Real-World Feedback**: "After growing frustrations, Octomind's team decided to remove LangChain entirely in 2024, reporting 'Once we removed it… we could just code,' noting that no longer being constrained by LangChain made their team far more productive."

### 3. LiteLLM

**Strengths:**
- Unified interface for 100+ LLM providers
- Excellent for multi-provider scenarios
- Built-in cost tracking and monitoring
- Proxy server for enterprise deployments
- Lightweight compared to LangChain
- Streaming support across all providers
- 6.5x performance improvement with fastuuid (2025)
- Python 3.13 fully supported

**Weaknesses:**
- Adds abstraction layer we don't currently need
- More complex than direct OpenAI SDK for single-provider use
- Introduces another dependency when we only need OpenAI
- Proxy server features are overkill for this application

**Complexity Rating**: ⭐⭐ Low-Medium (2/5)
**Streaming Complexity**: ⭐⭐ Low-Medium (2/5)
**FastAPI Integration**: ⭐⭐⭐⭐ Very Good
**Documentation Quality**: ⭐⭐⭐⭐ Very Good

**Python 3.13 Compatibility**: ✅ Fully supported. LiteLLM requires Python >=3.9 and <4.0, with explicit Python 3.13 support confirmed.

**When to Consider**: LiteLLM is excellent when you need multi-provider support from day one or require enterprise features like centralized cost tracking. For our use case, it adds unnecessary abstraction.

## Comparison Matrix

| Criteria | OpenAI SDK | LangChain | LiteLLM |
|----------|-----------|-----------|---------|
| **Simplicity** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **YAGNI Compliance** | ✅ Excellent | ❌ Poor | ⚠️ Good |
| **Streaming** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **FastAPI Integration** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Documentation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Python 3.13** | ✅ Full | ⚠️ Partial | ✅ Full |
| **GPT-5 Support** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Conversation History** | Simple list | Complex abstractions | Simple list |
| **Error Handling** | Excellent | Good | Excellent |
| **Community Size** | Massive | Large | Growing |
| **Learning Curve** | Minimal | Steep | Moderate |
| **Overhead** | None | High | Low |

## Best Practices for OpenAI SDK

### 1. Installation

```bash
pip install openai python-dotenv
```

### 2. Environment Configuration

```bash
# .env file
OPENAI_API_KEY=sk-...
```

### 3. Basic Setup

```python
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)
```

### 4. Streaming Implementation with FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel
import os

app = FastAPI()
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    messages: list[dict[str, str]]
    model: str = "gpt-5"

async def generate_stream(messages: list, model: str):
    """Generate streaming response from OpenAI."""
    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                # Format as Server-Sent Events
                content = chunk.choices[0].delta.content
                yield f"data: {content}\n\n"

        # Send completion signal
        yield "data: [DONE]\n\n"

    except Exception as e:
        # Send error in SSE format
        yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Stream chat completions to the client."""
    return StreamingResponse(
        generate_stream(request.messages, request.model),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

### 5. Conversation History Management

```python
# Simple conversation history - just maintain a list of messages
conversation_history = [
    {"role": "system", "content": "You are a helpful assistant."},
]

# Add user message
conversation_history.append({
    "role": "user",
    "content": "What is Python?"
})

# Send to API with full history
response = await client.chat.completions.create(
    model="gpt-5",
    messages=conversation_history,
    stream=True
)

# Add assistant response to history
assistant_message = ""
async for chunk in response:
    if chunk.choices[0].delta.content:
        assistant_message += chunk.choices[0].delta.content

conversation_history.append({
    "role": "assistant",
    "content": assistant_message
})
```

### 6. Error Handling Patterns

```python
from openai import (
    AsyncOpenAI,
    APIError,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    AuthenticationError,
    APIStatusError,
)
import asyncio

async def call_openai_with_retry(messages: list, model: str, max_retries: int = 3):
    """Call OpenAI API with exponential backoff retry logic."""

    for attempt in range(max_retries):
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
            )
            return response

        except AuthenticationError as e:
            # Don't retry authentication errors
            raise ValueError("Invalid API key. Please check your configuration.") from e

        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise ValueError("The AI service is temporarily busy. Please try again in a moment.") from e
            # Exponential backoff
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)

        except APITimeoutError as e:
            if attempt == max_retries - 1:
                raise ValueError("Request timed out. Please check your network and try again.") from e
            await asyncio.sleep(2 ** attempt)

        except APIConnectionError as e:
            if attempt == max_retries - 1:
                raise ValueError("Connection lost. Please check your network and try again.") from e
            await asyncio.sleep(2 ** attempt)

        except APIStatusError as e:
            # Log the request ID for debugging
            request_id = e.response.headers.get("x-request-id")
            print(f"API Error - Request ID: {request_id}")

            if e.status_code >= 500:
                # Server error - retry
                if attempt == max_retries - 1:
                    raise ValueError("The AI service encountered an error. Please try again.") from e
                await asyncio.sleep(2 ** attempt)
            else:
                # Client error - don't retry
                raise ValueError(f"Request failed: {e.message}") from e

        except Exception as e:
            # Unexpected error - log and raise
            print(f"Unexpected error: {type(e).__name__}: {str(e)}")
            raise ValueError("An unexpected error occurred. Please try again.") from e
```

### 7. Stream Interruption Pattern

```python
import asyncio

async def generate_stream_with_cancellation(messages: list, model: str, stop_event: asyncio.Event):
    """Generate streaming response with cancellation support."""
    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )

        async for chunk in stream:
            # Check if stop requested
            if stop_event.is_set():
                yield "data: {\"interrupted\": true, \"message\": \"conversation interrupted by user\"}\n\n"
                yield "data: [DONE]\n\n"
                return

            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                yield f"data: {content}\n\n"

        yield "data: [DONE]\n\n"

    except asyncio.CancelledError:
        yield "data: {\"interrupted\": true, \"message\": \"conversation interrupted by user\"}\n\n"
        yield "data: [DONE]\n\n"
```

### 8. Model Selection

```python
# GPT-5 family models supported
AVAILABLE_MODELS = {
    "gpt-5": "gpt-5",              # Latest GPT-5 model
    "gpt-5-mini": "gpt-5-mini",    # Smaller, faster GPT-5
    "gpt-5-nano": "gpt-5-nano",    # Most efficient GPT-5
    "gpt-5.1": "gpt-5.1",          # GPT-5.1 (smarter, more conversational)
    "gpt-5.2": "gpt-5.2",          # Latest flagship model
}

# For this project, we'll use:
DEFAULT_MODELS = {
    "general": "gpt-5",             # General conversation
    "codex": "gpt-5",               # Note: GPT-5 Codex not explicitly mentioned in docs
}

# Note: Verify GPT-5 Codex availability in OpenAI documentation
# May need to use "gpt-5.2" with system prompt optimization for coding tasks
```

### 9. Configuration Management

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    openai_model_default: str = "gpt-5"
    openai_max_tokens: int = 4096
    openai_temperature: float = 0.7
    openai_timeout: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### 10. Testing Strategy

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_streaming_response():
    """Test streaming chat completion."""
    mock_stream = AsyncMock()
    mock_chunk = AsyncMock()
    mock_chunk.choices = [AsyncMock(delta=AsyncMock(content="Hello"))]
    mock_stream.__aiter__.return_value = [mock_chunk]

    with patch("openai.AsyncOpenAI") as mock_client:
        mock_client.return_value.chat.completions.create.return_value = mock_stream

        # Test your streaming function
        result = []
        async for chunk in generate_stream([{"role": "user", "content": "Hi"}], "gpt-5"):
            result.append(chunk)

        assert len(result) > 0
```

## Architecture for Future Multi-Provider Support

While the OpenAI SDK is the right choice today, the specification requires supporting future LLM providers. Here's the recommended architecture:

### Provider Interface Pattern

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def stream_completion(
        self,
        messages: list[dict],
        model: str,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion from the LLM provider."""
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Return list of available models."""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI implementation."""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def stream_completion(
        self,
        messages: list[dict],
        model: str,
        **kwargs
    ) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            **kwargs
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def get_available_models(self) -> list[str]:
        return ["gpt-5", "gpt-5.1", "gpt-5.2"]

# Future providers can implement the same interface
class LocalLLMProvider(LLMProvider):
    """Example: Local LLM implementation (future)."""
    # Implementation would go here
    pass

# Provider factory
def get_provider(provider_name: str) -> LLMProvider:
    if provider_name == "openai":
        return OpenAIProvider(api_key=os.environ["OPENAI_API_KEY"])
    # Add other providers as needed
    raise ValueError(f"Unknown provider: {provider_name}")
```

This pattern allows:
- Starting simple with OpenAI SDK directly
- Adding new providers by implementing the `LLMProvider` interface
- No premature abstraction or complexity
- Easy migration when multi-provider support is needed

## Implementation Recommendations

### Phase 1: MVP (This Feature)
1. Use OpenAI SDK directly
2. Implement streaming with `AsyncOpenAI`
3. Use simple list-based conversation history
4. Support GPT-5 and GPT-5 Codex model selection
5. Implement production error handling patterns

### Phase 2: Future Enhancement (When Needed)
1. Add provider abstraction layer (only when second provider is confirmed)
2. Consider LiteLLM if supporting 3+ providers
3. Implement provider-specific configuration
4. Add cost tracking if needed

## Risk Assessment

### OpenAI SDK Risks
- **Vendor Lock-in**: Mitigated by clean architecture and provider interface
- **API Changes**: Low risk - OpenAI maintains excellent backward compatibility
- **Service Availability**: Same risk across all providers; handle with retries and error messages

### LangChain Risks
- **Complexity Overhead**: High - team productivity impact documented by real users
- **Dependency Bloat**: High - increases security surface area
- **Breaking Changes**: Medium - framework under active development
- **Over-Engineering**: High - violates YAGNI for this use case

### LiteLLM Risks
- **Unnecessary Abstraction**: Medium - adds layer we don't need yet
- **API Differences**: Low - designed for compatibility
- **Maintenance**: Low - actively maintained

## Conclusion

The OpenAI Python SDK is the optimal choice for this chatbot project. It provides:

✅ **Simplicity**: Minimal abstraction, straightforward implementation
✅ **Production-Ready**: Proven in thousands of applications
✅ **Excellent Streaming**: Native async/await with FastAPI integration
✅ **GPT-5 Support**: Latest models including GPT-5, GPT-5.1, and GPT-5.2
✅ **Python 3.13 Compatible**: Fully supported and tested
✅ **Great Documentation**: Comprehensive guides and examples
✅ **Active Maintenance**: Regular updates and improvements
✅ **YAGNI Compliant**: No unnecessary features or complexity

By starting with the OpenAI SDK and implementing a clean provider interface, we can deliver a robust MVP quickly while maintaining flexibility for future multi-provider support when (and if) it's actually needed.

## Sources

### OpenAI Python SDK & FastAPI Integration
- [How to forward OpenAI's stream response using FastAPI in python?](https://community.openai.com/t/how-to-forward-openais-stream-response-using-fastapi-in-python/963242)
- [GitHub - OpenAI Agents Streaming API](https://github.com/ahmad2b/openai-agents-streaming-api)
- [GitHub - StreamingFastAPI](https://github.com/SidJain1412/StreamingFastAPI)
- [Real-time OpenAI response streaming with FastAPI](https://sevalla.com/blog/real-time-openai-streaming-fastapi/)
- [Building a Real-time Streaming API with FastAPI and OpenAI](https://medium.com/@shudongai/building-a-real-time-streaming-api-with-fastapi-and-openai-a-comprehensive-guide-cb65b3e686a5)
- [Scalable Streaming of OpenAI Model Responses with FastAPI and asyncio](https://medium.com/@mayvic/scalable-streaming-of-openai-model-responses-with-fastapi-and-asyncio-714744b13dd)
- [Async Streaming with Azure OpenAI and Python Fast API](https://medium.com/version-1/async-streaming-with-azure-openai-and-python-fast-api-bc311bd59bde)

### GPT-5 Model Support
- [Using GPT-5.2 | OpenAI API](https://platform.openai.com/docs/guides/latest-model)
- [GPT-5.2 Model | OpenAI API](https://platform.openai.com/docs/models/gpt-5.2)
- [GPT-5 Model | OpenAI API](https://platform.openai.com/docs/models/gpt-5)
- [Python OpenAI SDK Update What GPT 5.2 Support Means](https://python.plainenglish.io/python-openai-sdk-update-what-gpt-5-2-support-means-a976edb4fa71)

### Conversation Memory Patterns
- [Conversation Management | OpenAI Agents Python](https://deepwiki.com/raphaelhou25/openai-agents-python/3.3-conversation-management)
- [Solving Chatbot Amnesia: Building an AI Agent with Persistent Memory](https://medium.com/@kpdebree/solving-chatbot-amnesia-building-an-ai-agent-with-persistent-memory-using-python-openai-and-b9ec166c298a)
- [Context Engineering - Session Memory with OpenAI Agents SDK](https://cookbook.openai.com/examples/agents_sdk/session_memory)

### Error Handling
- [Error codes | OpenAI API](https://platform.openai.com/docs/guides/error-codes)
- [Complete Guide to the OpenAI API 2025](https://zuplo.com/learning-center/openai-api)
- [Error Handling In Openai-Python](https://www.restack.io/p/openai-python-answer-error-handling-cat-ai)

### Library Comparisons
- [14 AI Agent Frameworks Compared](https://softcery.com/lab/top-14-ai-agent-frameworks-of-2025-a-founders-guide-to-building-smarter-systems)
- [Langchain vs LiteLLM](https://medium.com/@heyamit10/langchain-vs-litellm-a9b784a2ad1a)
- [Comparing Open-Source AI Agent Frameworks](https://langfuse.com/blog/2025-03-19-ai-agent-comparison)
- [LiteLLM: A Deep Dive](https://skywork.ai/skypage/en/LiteLLM-A-Deep-Dive-into-the-Unified-Gateway-for-AI-Models/1972870863895195648)

### LangChain Complexity Issues
- [Why Developers Say LangChain Is "Bad"](https://www.designveloper.com/blog/is-langchain-bad/)
- [Is LangChain Still Worth It? A 2025 Review](https://sider.ai/blog/ai-tools/is-langchain-still-worth-it-a-2025-review-of-features-limits-and-real-world-fit)
- [Challenges & Criticisms of LangChain](https://shashankguda.medium.com/challenges-criticisms-of-langchain-b26afcef94e7)
- [Why we no longer use LangChain for building our AI agents](https://news.ycombinator.com/item?id=40739982)
- [Is LangChain becoming too complex/bloated for simple RAG applications in 2025?](https://github.com/orgs/community/discussions/182015)

### Python 3.13 Compatibility
- [GitHub - openai/openai-python](https://github.com/openai/openai-python)
- [OpenAI Agents SDK](https://pypi.org/project/openai-agents/)
- [LangChain - LangGraph is now compatible with Python 3.13](https://changelog.langchain.com/announcements/langgraph-is-now-compatible-with-python-3-13)
- [langchain-pinecone 0.2.0 doesn't support Python 3.13](https://github.com/langchain-ai/langchain/issues/28153)
- [Python 3.13 needs Numpy > 2.0](https://github.com/langchain-ai/langchain/issues/26026)
- [litellm · PyPI](https://pypi.org/project/litellm/)
- [Python 3.13 Readiness](https://pyreadiness.org/3.13/)

### LiteLLM Resources
- [GitHub - BerriAI/litellm](https://github.com/BerriAI/litellm)
- [LiteLLM - Getting Started](https://docs.litellm.ai/)
- [Streaming + Async | liteLLM](https://docs.litellm.ai/docs/completion/stream)
- [Deploy a Streaming RAG Chatbot with FastAPI](https://khalidrizvi.com/posts/rag_fastapi/)

### LangChain Streaming
- [Server Side Events (SSE) with FastAPi and Langchain](https://gist.github.com/oneryalcin/2921408da70266aa61f9c40cb2973865)
- [#30DaysOfLangChain – Day 25: FastAPI for LangGraph Agents & Streaming](https://mlvector.com/2025/06/30/30daysoflangchain-day-25-fastapi-for-langgraph-agents-streaming-responses/)
- [Deploying Streaming AI Agents with LangGraph, FastAPI, and Google Cloud Run](https://medium.com/@chirazchahbeni/deploying-streaming-ai-agents-with-langgraph-fastapi-and-google-cloud-run-5e32232ef1fb)
