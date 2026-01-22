# Research: Add Search Tools to Chatbot

**Feature**: 023-add-search-tools | **Date**: 2026-01-22

## Executive Summary

This document captures technology decisions for implementing search tools in SpecBot. Key decisions: use **Tavily** for web search (AI-native, LLM-optimized), **BBC RSS feeds** for news search (free, reliable), and **LangChain's native tool system** for integration.

---

## 1. Web Search API Selection

### Decision: Tavily API

**Rationale**: Tavily is an AI-native search API designed specifically for LLM applications.

### Alternatives Considered

| API | Pros | Cons | Decision |
|-----|------|------|----------|
| **Tavily** | AI-native, LLM-ready output, 1000 free/month, LangChain integration, single-call workflow | Newer service | ✅ SELECTED |
| **SerpAPI** | Reliable, fast (0.072s), 20+ engines | Requires extra scraping step, $10/1000 searches | Rejected - extra complexity |
| **Google Custom Search** | Direct Google results, official | Limited free tier, requires CSE setup, no LLM optimization | Rejected - not LLM-optimized |
| **Serper** | Fast, affordable | Less LLM-focused than Tavily | Rejected - less suitable |

### Why Tavily

1. **AI-Native Design**: Aggregates up to 20 sites per call, uses AI to score and rank relevance
2. **LLM-Ready Output**: Returns clean, summarized content ready for LLM consumption
3. **Single-Call Workflow**: No separate scraping step needed - search + extract in one call
4. **Free Tier**: 1,000 free searches monthly, then $0.008/request
5. **LangChain Integration**: First-class support via `langchain-community` package

### Configuration

```bash
TAVILY_API_KEY=tvly-...
TOOLS_GOOGLE_SEARCH_ENABLED=true  # Enable/disable tool
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

### Decision: Native LangChain Tool System with @tool Decorator

**Rationale**: LangChain provides robust tool support that integrates with all providers (OpenAI, Anthropic, Ollama).

### Tool Definition Pattern

```python
from langchain_core.tools import tool

@tool
async def google_search(query: str) -> str:
    """Search the web for current information about a topic.

    Args:
        query: The search query string

    Returns:
        Search results with titles, snippets, and source URLs
    """
    # Tavily API call
    ...
```

### Model Integration

```python
# Bind tools to model
model_with_tools = llm.bind_tools([google_search, bbc_news_search])

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
├── google_search.py     # GoogleSearchTool
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
- `ToolCallEvent`: `{"type": "tool_call", "tool": "google_search", "args": {...}}`
- `ToolResultEvent`: `{"type": "tool_result", "tool": "google_search", "success": true}`

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
| `TAVILY_API_KEY` | For Google Search | - | Tavily API key |
| `TOOLS_GOOGLE_SEARCH_ENABLED` | No | `true` if key present | Enable/disable |
| `TOOLS_BBC_NEWS_ENABLED` | No | `true` | Enable/disable (no key needed) |

### Auto-Disable Logic

Tools automatically disabled when:
- Required API key not configured (e.g., Tavily key missing → Google Search disabled)
- Explicitly disabled via `TOOLS_*_ENABLED=false`

---

## 7. Error Handling Strategy

### Decision: Graceful Degradation with User Communication

| Error Type | Handling |
|------------|----------|
| API Rate Limit | Return partial results or inform user, don't crash |
| Network Timeout | Return error result to LLM, let it respond without tool |
| Invalid Response | Log error, return empty result |
| Tool Disabled | LLM never sees tool, responds with base knowledge |

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
| `tavily-python` | ^0.4.0 | Tavily API client |
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

### Web Search APIs
- [Beyond Tavily - Complete Guide to AI Search APIs](https://websearchapi.ai/blog/tavily-alternatives)
- [Best SERP API Comparison 2025](https://dev.to/ritza/best-serp-api-comparison-2025-serpapi-vs-exa-vs-tavily-vs-scrapingdog-vs-scrapingbee-2jci)
- [Tavily Documentation](https://docs.tavily.com/documentation/about)

### BBC RSS Feeds
- [Top BBC RSS Feeds](https://rss.feedspot.com/bbc_rss_feeds/)
- [BBC News RSS Feeds Guide](https://www.kaggle.com/code/gpreda/bbc-news-rss-feeds)

### LangChain Tools
- LangChain Core tools module
- Existing SpecBot streaming implementation (Feature 009)
