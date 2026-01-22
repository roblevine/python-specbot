# Developer Quickstart: Add Search Tools

**Feature**: 023-add-search-tools | **Date**: 2026-01-22

## Overview

This guide helps developers implement the search tools feature for SpecBot. You'll add a modular tool system with Google Search and BBC News tools.

---

## Prerequisites

- Python 3.13+ with existing backend running
- Node.js 18+ for frontend development
- Tavily API key (for Google Search tool)
- Understanding of existing provider pattern in `backend/src/services/providers/`

---

## Quick Setup

### 1. Get API Keys

```bash
# Sign up at https://tavily.com to get an API key
# BBC News uses RSS feeds - no key needed
```

### 2. Configure Environment

Add to `backend/.env`:

```bash
# Tools Configuration
TAVILY_API_KEY=tvly-your-api-key-here

# Optional: Explicitly enable/disable tools
TOOLS_GOOGLE_SEARCH_ENABLED=true
TOOLS_BBC_NEWS_ENABLED=true
```

### 3. Install Dependencies

```bash
cd backend
pip install tavily-python feedparser
```

---

## Implementation Guide

### Step 1: Create Tool Base (P1 - MVP)

Create `backend/src/services/tools/base.py`:

```python
from dataclasses import dataclass, field
from typing import Protocol, Any

@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    content: str
    sources: list[dict] = field(default_factory=list)
    error_code: str | None = None


class BaseTool(Protocol):
    """Protocol for all tools."""

    @property
    def id(self) -> str:
        """Unique tool identifier."""
        ...

    @property
    def name(self) -> str:
        """Human-readable name."""
        ...

    @property
    def description(self) -> str:
        """Description for LLM."""
        ...

    def is_enabled(self) -> bool:
        """Check if tool is available."""
        ...

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool."""
        ...
```

### Step 2: Create Tool Registry

Create `backend/src/services/tools/registry.py`:

```python
from typing import Dict
from .base import BaseTool

class ToolRegistry:
    """Registry for managing tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool."""
        self._tools[tool.id] = tool

    def get(self, tool_id: str) -> BaseTool | None:
        """Get tool by ID."""
        return self._tools.get(tool_id)

    def get_enabled(self) -> list[BaseTool]:
        """Get all enabled tools."""
        return [t for t in self._tools.values() if t.is_enabled()]

    def get_all(self) -> list[BaseTool]:
        """Get all registered tools."""
        return list(self._tools.values())

# Global registry instance
registry = ToolRegistry()
```

### Step 3: Implement Google Search Tool

Create `backend/src/services/tools/google_search.py`:

```python
import os
import logging
from langchain_core.tools import tool
from tavily import TavilyClient
from .base import ToolResult

logger = logging.getLogger(__name__)

class GoogleSearchTool:
    """Google web search tool using Tavily API."""

    id = "google_search"
    name = "Google Search"
    description = "Search the web for current information about any topic"

    def __init__(self):
        self._api_key = os.getenv("TAVILY_API_KEY")
        self._enabled = os.getenv("TOOLS_GOOGLE_SEARCH_ENABLED", "true").lower() == "true"

    def is_enabled(self) -> bool:
        return bool(self._api_key) and self._enabled

    async def execute(self, query: str) -> ToolResult:
        """Execute web search."""
        if not self.is_enabled():
            return ToolResult(
                success=False,
                content="Web search is not available",
                error_code="TOOL_DISABLED"
            )

        try:
            client = TavilyClient(api_key=self._api_key)
            response = client.search(query, max_results=5)

            sources = [
                {"title": r["title"], "url": r["url"], "snippet": r.get("content", "")}
                for r in response.get("results", [])
            ]

            content = "\n".join(
                f"- {s['title']}: {s['snippet']}" for s in sources
            )

            return ToolResult(success=True, content=content, sources=sources)

        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return ToolResult(
                success=False,
                content="Web search temporarily unavailable",
                error_code="TOOL_ERROR"
            )

    def as_langchain_tool(self):
        """Convert to LangChain tool."""
        @tool
        async def google_search(query: str) -> str:
            """Search the web for current information about any topic.

            Args:
                query: The search query

            Returns:
                Search results with titles and snippets
            """
            result = await self.execute(query=query)
            return result.content

        return google_search
```

### Step 4: Implement BBC News Tool

Create `backend/src/services/tools/bbc_news.py`:

```python
import os
import logging
import feedparser
from .base import ToolResult

logger = logging.getLogger(__name__)

BBC_FEEDS = {
    "top": "https://feeds.bbci.co.uk/news/rss.xml",
    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "science": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
}

class BBCNewsTool:
    """BBC News search tool using RSS feeds."""

    id = "bbc_news"
    name = "BBC News Search"
    description = "Search BBC News for recent news articles on a topic"

    def __init__(self):
        self._enabled = os.getenv("TOOLS_BBC_NEWS_ENABLED", "true").lower() == "true"

    def is_enabled(self) -> bool:
        return self._enabled

    async def execute(self, query: str, category: str = "top") -> ToolResult:
        """Search BBC News."""
        if not self.is_enabled():
            return ToolResult(
                success=False,
                content="BBC News search is not available",
                error_code="TOOL_DISABLED"
            )

        try:
            feed_url = BBC_FEEDS.get(category, BBC_FEEDS["top"])
            feed = feedparser.parse(feed_url)

            # Simple keyword matching
            query_terms = query.lower().split()
            matches = []

            for entry in feed.entries[:20]:
                title = entry.get("title", "").lower()
                summary = entry.get("summary", "").lower()

                if any(term in title or term in summary for term in query_terms):
                    matches.append({
                        "title": entry.get("title"),
                        "url": entry.get("link"),
                        "snippet": entry.get("summary", "")[:200],
                        "published": entry.get("published")
                    })

            if not matches:
                return ToolResult(
                    success=True,
                    content="No BBC News articles found matching your query",
                    sources=[]
                )

            sources = matches[:5]
            content = "\n".join(
                f"- {s['title']}" for s in sources
            )

            return ToolResult(success=True, content=content, sources=sources)

        except Exception as e:
            logger.error(f"BBC News search failed: {e}")
            return ToolResult(
                success=False,
                content="BBC News search temporarily unavailable",
                error_code="TOOL_ERROR"
            )
```

### Step 5: Register Tools

Create `backend/src/services/tools/__init__.py`:

```python
from .registry import registry, ToolRegistry
from .base import BaseTool, ToolResult
from .google_search import GoogleSearchTool
from .bbc_news import BBCNewsTool

def _register_tools():
    """Register all available tools."""
    registry.register(GoogleSearchTool())
    registry.register(BBCNewsTool())

_register_tools()

__all__ = ["registry", "ToolRegistry", "BaseTool", "ToolResult"]
```

### Step 6: Integrate with LLM Service

Update `backend/src/services/llm_service.py`:

```python
from src.services.tools import registry as tool_registry

async def stream_ai_response(message, history, model_id):
    """Stream AI response with tool support."""
    llm = get_llm_for_model(model_id)
    messages = convert_to_langchain_messages(history)

    # Get enabled tools
    enabled_tools = tool_registry.get_enabled()
    langchain_tools = [t.as_langchain_tool() for t in enabled_tools]

    # Bind tools if any are available
    if langchain_tools:
        model_with_tools = llm.bind_tools(langchain_tools)
    else:
        model_with_tools = llm

    # Agentic loop for tool usage
    max_iterations = 5
    for iteration in range(max_iterations):
        chunks = []
        async for chunk in model_with_tools.astream(messages):
            if chunk.content:
                yield TokenEvent(content=chunk.content)
            if chunk.tool_calls:
                for tc in chunk.tool_calls:
                    yield ToolCallEvent(tool=tc["name"], args=tc["args"])
            chunks.append(chunk)

        # Merge chunks
        response = AIMessage.from_chunks(chunks)

        if not response.tool_calls:
            break  # No more tools needed

        # Execute tools
        messages.append(response)
        for tool_call in response.tool_calls:
            tool = tool_registry.get(tool_call["name"])
            result = await tool.execute(**tool_call["args"])
            yield ToolResultEvent(
                tool=tool_call["name"],
                success=result.success,
                sources=result.sources
            )
            messages.append(ToolMessage(
                tool_call_id=tool_call["id"],
                content=result.content
            ))

    yield CompleteEvent(model=model_id)
```

### Step 7: Add Tools Endpoint

Create `backend/src/api/routes/tools.py`:

```python
from fastapi import APIRouter
from pydantic import BaseModel
from src.services.tools import registry

router = APIRouter(tags=["Tools"])

class ToolInfo(BaseModel):
    id: str
    name: str
    description: str
    enabled: bool

class ToolsResponse(BaseModel):
    tools: list[ToolInfo]

@router.get("/tools", response_model=ToolsResponse)
async def list_tools():
    """List all available tools."""
    tools = [
        ToolInfo(
            id=t.id,
            name=t.name,
            description=t.description,
            enabled=t.is_enabled()
        )
        for t in registry.get_all()
    ]
    return ToolsResponse(tools=tools)
```

---

## Testing

### Unit Tests

```bash
cd backend
pytest tests/unit/tools/ -v
```

### Integration Tests

```bash
pytest tests/integration/test_tool_execution.py -v
```

### Manual Testing

```bash
# Start backend
cd backend && uvicorn src.api.routes.main:app --reload

# Test tools endpoint
curl http://localhost:8000/api/v1/tools

# Test with streaming (use frontend or curl)
```

---

## Troubleshooting

### Tool Not Appearing

1. Check `TAVILY_API_KEY` is set correctly
2. Verify `TOOLS_*_ENABLED` is not set to `false`
3. Check logs for registration errors

### Search Returns Empty

1. Verify API key is valid (test at tavily.com)
2. Check network connectivity
3. Review query formatting

### SSE Events Missing

1. Ensure `Accept: text/event-stream` header is set
2. Check browser dev tools for SSE connection
3. Verify frontend handles new event types

---

## Next Steps

1. Run `/speckit.tasks` to generate implementation tasks
2. Follow TDD approach: tests first, then implementation
3. Implement P1 (Google Search) fully before P2 (BBC News)
4. Update architecture.md with tool subsystem diagram
