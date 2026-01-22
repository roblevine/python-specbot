# Research: Add Search Tools to Chatbot

**Feature**: 023-add-search-tools | **Date**: 2026-01-22 | **Updated**: 2026-01-22

## Executive Summary

This document captures technology decisions for implementing search tools in SpecBot. Key decisions: use **DuckDuckGo Search** via LangChain (free, no API key), **BBC RSS feeds** for news search (free, reliable), and **LangChain's native tool system** for integration.

---

## 1. Web Search API Selection

### Decision: DuckDuckGo Search (via LangChain)

**Rationale**: DuckDuckGo Search is built into `langchain-community`, requires no API key, and is completely free - removing external dependencies for the initial implementation.

### Alternatives Considered

| API | Pros | Cons | Decision |
|-----|------|------|----------|
| **DuckDuckGo** | Free, no API key, built into LangChain, privacy-focused | Less comprehensive than Google | ✅ SELECTED |
| **Tavily** | AI-native, LLM-ready output, 1000 free/month | Requires API key, external dependency | Rejected - unnecessary cost/complexity |
| **SerpAPI** | Reliable, fast, 20+ engines | Requires API key, $50/mo | Rejected - cost |
| **Google Custom Search** | Direct Google results, official | Limited free tier, requires CSE setup | Rejected - setup complexity |

### Why DuckDuckGo

1. **Zero Cost**: Completely free with no usage limits
2. **No API Key**: Works immediately without signup or configuration
3. **LangChain Native**: Built into `langchain-community` package we'll already need
4. **Privacy-Focused**: No tracking, good for user trust
5. **Sufficient Quality**: Good enough for most search queries

### Usage

```python
from langchain_community.tools import DuckDuckGoSearchRun

# No API key needed - works immediately
search = DuckDuckGoSearchRun()
result = search.invoke("current weather in London")
```

### Configuration

```bash
TOOLS_WEB_SEARCH_ENABLED=true  # Enable/disable tool (no API key needed)
```

### Future Enhancement Path

If richer search results are needed later, can add Tavily as a "premium" option:
```bash
TAVILY_API_KEY=tvly-...  # Optional: enables Tavily instead of DuckDuckGo
```

---

## 2. BBC News Search Implementation

### Decision: BBC RSS Feed Parsing

**Rationale**: BBC provides free, reliable RSS feeds that can be parsed without API keys.

### Available BBC RSS Feeds

| Category | Feed URL |
|----------|----------|
| Top Stories | `feeds.bbci.co.uk/news/rss.xml` |
| World | `feeds.bbci.co.uk/news/world/rss.xml` |
| UK | `feeds.bbci.co.uk/news/uk/rss.xml` |
| Business | `feeds.bbci.co.uk/news/business/rss.xml` |
| Technology | `feeds.bbci.co.uk/news/technology/rss.xml` |
| Science | `feeds.bbci.co.uk/news/science_and_environment/rss.xml` |
| Health | `feeds.bbci.co.uk/news/health/rss.xml` |

### Alternatives Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **RSS Feed Parsing** | Free, no API key, reliable, official BBC source | Limited to recent items (~50) | ✅ SELECTED |
| **NewsAPI.org** | Multiple sources, search capability | Paid for production, includes non-BBC sources | Rejected - unnecessary cost |
| **Web Scraping** | Full content access | Fragile, ToS concerns, maintenance burden | Rejected - unreliable |

### Implementation Approach

1. Fetch relevant RSS feed(s) based on query topic
2. Parse XML with `feedparser` library (well-established Python RSS parser)
3. Match query terms against titles and descriptions
4. Return top 5 relevant articles with title, link, description, publish date

### Configuration

```bash
TOOLS_BBC_NEWS_ENABLED=true  # Enable/disable tool (no API key needed)
```

---

## 3. LangChain Tool Integration

### Decision: Use LangChain Community Tools + Custom Wrapper

**Rationale**: LangChain provides DuckDuckGo search out of the box. We wrap it in our tool protocol for consistency.

### Tool Definition Pattern

```python
from langchain_community.tools import DuckDuckGoSearchRun

class WebSearchTool:
    """Web search tool using DuckDuckGo."""

    id = "web_search"
    name = "Web Search"
    description = "Search the web for current information about any topic"

    def __init__(self):
        self._search = DuckDuckGoSearchRun()
        self._enabled = os.getenv("TOOLS_WEB_SEARCH_ENABLED", "true").lower() == "true"

    def is_enabled(self) -> bool:
        return self._enabled

    async def execute(self, query: str) -> ToolResult:
        """Execute web search."""
        try:
            result = self._search.invoke(query)
            return ToolResult(success=True, content=result)
        except Exception as e:
            return ToolResult(success=False, content=str(e), error_code="SEARCH_ERROR")
```

### Model Integration

```python
# Bind tools to model
model_with_tools = llm.bind_tools([web_search, bbc_news_search])

# Use in streaming
async for chunk in model_with_tools.astream(messages):
    if chunk.content:
        yield TokenEvent(content=chunk.content)
    if chunk.tool_calls:
        yield ToolCallEvent(...)
```

### Streaming with Tools

LangChain's astream() natively supports tools:
- Text tokens arrive as `chunk.content`
- Tool calls arrive as `chunk.tool_calls` (complete, not streamed)
- Tool results are provided via `ToolMessage` for next iteration

### Agentic Loop Pattern

```python
# Simplified flow
while True:
    async for chunk in model_with_tools.astream(messages):
        # Emit tokens and tool calls
        ...

    if not has_tool_calls(response):
        break  # Done

    # Execute tools, add ToolMessage, continue loop
    for tool_call in response.tool_calls:
        result = await tools[tool_call.name].arun(**tool_call.args)
        messages.append(ToolMessage(tool_call_id=..., content=result))
```

---

## 4. Tool Registry Architecture

### Decision: Follow Existing Provider Pattern (Protocol + Registry)

**Rationale**: SpecBot already has a proven Pattern + Registry architecture for providers. Tools will follow the same pattern for consistency.

### Architecture

```
backend/src/services/tools/
├── __init__.py          # Export registry
├── base.py              # BaseTool Protocol, ToolResult, ToolError
├── registry.py          # ToolRegistry class
├── web_search.py        # WebSearchTool (DuckDuckGo)
└── bbc_news.py          # BBCNewsTool
```

### BaseTool Protocol

```python
from typing import Protocol

class BaseTool(Protocol):
    """Protocol for all tools."""

    @property
    def name(self) -> str:
        """Unique tool identifier."""
        ...

    @property
    def description(self) -> str:
        """Description for LLM to understand when to use tool."""
        ...

    def is_enabled(self) -> bool:
        """Check if tool has required configuration."""
        ...

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given arguments."""
        ...

    def as_langchain_tool(self) -> callable:
        """Convert to LangChain tool format."""
        ...
```

---

## 5. SSE Event Extensions

### Decision: Add Tool-Specific Event Types

**Current Events** (Feature 009):
- `TokenEvent`: `{"type": "token", "content": "..."}`
- `CompleteEvent`: `{"type": "complete", "model": "..."}`
- `ErrorEvent`: `{"type": "error", "error": "...", "code": "..."}`

**New Events**:
- `ToolCallEvent`: `{"type": "tool_call", "tool": "web_search", "args": {...}}`
- `ToolResultEvent`: `{"type": "tool_result", "tool": "web_search", "success": true}`

### Frontend Handling

```javascript
// Extended streamMessage handler
if (event.type === 'tool_call') {
    showToolIndicator(event.tool);  // "Searching the web..."
} else if (event.type === 'tool_result') {
    hideToolIndicator();
}
```

---

## 6. Configuration Pattern

### Decision: Environment Variables Matching Provider Pattern

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TOOLS_WEB_SEARCH_ENABLED` | No | `true` | Enable/disable web search |
| `TOOLS_BBC_NEWS_ENABLED` | No | `true` | Enable/disable BBC news |

### No API Keys Required

Both tools work without API keys:
- **Web Search**: DuckDuckGo is free and keyless
- **BBC News**: RSS feeds are publicly accessible

### Auto-Disable Logic

Tools automatically disabled when:
- Explicitly disabled via `TOOLS_*_ENABLED=false`
- (Future) If premium provider configured but key missing

---

## 7. Error Handling Strategy

### Decision: Graceful Degradation with User Communication

| Error Type | Handling |
|------------|----------|
| Network Timeout | Return error result to LLM, let it respond without tool |
| Invalid Response | Log error, return empty result |
| Tool Disabled | LLM never sees tool, responds with base knowledge |
| Rate Limiting | DuckDuckGo has no rate limits; BBC RSS is public |

### Error Result Format

```python
@dataclass
class ToolResult:
    success: bool
    content: str  # Results or error message
    sources: list[str] = field(default_factory=list)
    error_code: str | None = None
```

---

## 8. Dependencies

### New Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `langchain-community` | ^0.3.0 | DuckDuckGo search tool |
| `duckduckgo-search` | ^6.0.0 | DuckDuckGo API (peer dep) |
| `feedparser` | ^6.0.0 | RSS feed parsing |

### Existing Dependencies (reused)

- `langchain-core` - Tool primitives
- `langchain-openai`, `langchain-anthropic`, `langchain-ollama` - Tool binding per provider
- `httpx` - HTTP client (already used)

---

## 9. Provider Compatibility

### Tool Calling Support by Provider

| Provider | Tool Support | Notes |
|----------|--------------|-------|
| OpenAI (gpt-4, gpt-4o) | ✅ Full | Native function calling |
| OpenAI (gpt-3.5-turbo) | ✅ Full | Native function calling |
| Anthropic (Claude) | ✅ Full | XML tool_use format |
| Ollama | ⚠️ Model-dependent | Some models support tools |

### Graceful Fallback

If a model doesn't support tools:
- Tools not bound to model
- Chat works normally without tool capability
- No errors, just reduced functionality

---

## References

### DuckDuckGo Search
- [DuckDuckGoSearch - LangChain Docs](https://docs.langchain.com/oss/javascript/integrations/tools/duckduckgo_search)
- [Free LangChain Tools Guide](https://medium.com/@nwatch117/stop-paying-for-apis-3-free-langchain-tools-to-power-your-ai-projects-89da85e7c48f)
- [LangChain Local Deep Researcher](https://github.com/langchain-ai/local-deep-researcher)

### BBC RSS Feeds
- [Top BBC RSS Feeds](https://rss.feedspot.com/bbc_rss_feeds/)
- [BBC News RSS Feeds Guide](https://www.kaggle.com/code/gpreda/bbc-news-rss-feeds)

### LangChain Tools
- LangChain Core tools module
- Existing SpecBot streaming implementation (Feature 009)
