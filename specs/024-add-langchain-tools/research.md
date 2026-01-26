# Research: LangChain Tool Integration

**Feature**: 024-add-langchain-tools
**Date**: 2026-01-26

## Research Summary

This document captures technical decisions and research findings for integrating LangChain tools into python-specbot.

---

## 1. DuckDuckGo Search Tool

### Decision
Use `DuckDuckGoSearchResults` from `langchain_community.tools.ddg_search` for structured search results.

### Rationale
- Returns JSON-formatted results with links (required for expanded tool view)
- No API key required (privacy-focused, no rate limiting concerns)
- Standard LangChain BaseTool interface, works with `bind_tools()`

### Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| `DuckDuckGoSearchRun` | Returns plain text, no structured links |
| SerpAPI | Requires paid API key |
| Google Search API | Requires paid API key, complex setup |
| Tavily | Requires paid API key |

### Implementation Details

```python
from langchain_community.tools.ddg_search import DuckDuckGoSearchResults

search_tool = DuckDuckGoSearchResults(
    max_results=5,
    backend="text"
)
```

**Package Dependency**: `duckduckgo-search` (add to requirements.txt)

---

## 2. Web Browser Tool

### Decision
Use `WebBaseLoader` with `BeautifulSoupTransformer` wrapped in a custom LangChain tool.

### Rationale
- Lightweight, no external services required
- Works with static HTML content (sufficient for most use cases)
- Uses `requests` (already available via langchain dependencies)
- BeautifulSoup provides clean text extraction

### Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| AsyncChromiumLoader | Requires Playwright, adds complexity |
| FirecrawlLoader | Requires paid API key |
| Selenium-based | Heavy dependency, not async-friendly |
| LangChain WebBrowser | Python version not available (JS/TS only) |

### Implementation Details

```python
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_core.tools import tool

@tool
def browse_url(url: str) -> str:
    """Fetch and read content from a web page URL."""
    loader = WebBaseLoader(url)
    docs = loader.load()
    transformer = BeautifulSoupTransformer()
    transformed = transformer.transform_documents(docs, tags_to_extract=["p", "h1", "h2", "h3", "article"])
    return transformed[0].page_content[:4000]  # Truncate for context limits
```

**Package Dependencies**:
- `beautifulsoup4` (add to requirements.txt)
- `lxml` (optional, for faster parsing)

---

## 3. Cross-Provider Tool Binding

### Decision
Use LangChain's `bind_tools()` method available on all three providers, with provider-specific considerations.

### Provider Support Matrix

| Provider | Tool Support | Parallel Calls | Notes |
|----------|--------------|----------------|-------|
| ChatOpenAI | ✅ Full | ✅ Yes | Most reliable, recommended default |
| ChatAnthropic | ✅ Full | ✅ Yes | Use `strict=True` for schema enforcement |
| ChatOllama | ⚠️ Limited | ❌ No | Only llama3.1+ models; experimental |

### Rationale
- All three providers inherit from `BaseChatModel` with `bind_tools()` support
- Follows existing provider abstraction pattern in codebase
- Tool binding happens at LLM instance level, not provider level

### Implementation Pattern

```python
# In llm_service.py
def get_llm_with_tools(model_id: str, tools: List) -> BaseChatModel:
    llm = get_llm_for_model(model_id, config)

    # Provider-specific configuration
    provider = get_provider_for_model(model_id)
    if provider == "anthropic":
        return llm.bind_tools(tools, strict=True)
    elif provider == "ollama":
        # Log warning about experimental support
        logger.warning(f"Tool calling with Ollama is experimental")
        return llm.bind_tools(tools)
    else:
        return llm.bind_tools(tools)
```

### Ollama Consideration
For Ollama models without tool support, gracefully degrade:
- Check if model supports tools before binding
- Return informative error if tools requested but not supported
- Log which models support tools at startup

---

## 4. Streaming with Tool Calls

### Decision
Extend existing SSE streaming to emit new event types for tool calls and results.

### Rationale
- Maintains existing streaming architecture
- Frontend can handle tool events in same EventSource stream
- Tool execution visible in real-time to users

### New SSE Event Types

```
# Tool call initiated by LLM
data: {"type":"tool_call","id":"call_abc123","name":"search","args":{"query":"latest news"}}

# Tool execution started
data: {"type":"tool_start","id":"call_abc123"}

# Tool result received
data: {"type":"tool_result","id":"call_abc123","status":"success","result":"...","links":[...]}

# Tool error
data: {"type":"tool_error","id":"call_abc123","error":"Network timeout","code":"TIMEOUT"}
```

### Detection Pattern

```python
async for chunk in llm.astream(messages):
    # Check for tool calls in chunk
    if hasattr(chunk, 'tool_call_chunks') and chunk.tool_call_chunks:
        for tool_call in chunk.tool_call_chunks:
            yield ToolCallEvent(
                id=tool_call.get("id"),
                name=tool_call.get("name"),
                args=tool_call.get("args")
            )

    # Regular content tokens
    if chunk.content:
        yield TokenEvent(content=chunk.content)
```

---

## 5. Tool Configuration Pattern

### Decision
Follow existing model configuration pattern with provider-specific environment variables.

### Configuration Format

```bash
# Environment variables
TOOLS='[
  {"id": "duckduckgo-search", "name": "Web Search", "description": "Search the web", "enabled": true},
  {"id": "web-browser", "name": "Browse URL", "description": "Read web pages", "enabled": true}
]'
```

### Registry Pattern

```python
# backend/src/services/tools/__init__.py
from .search import DuckDuckGoSearchTool
from .browser import WebBrowserTool

TOOL_REGISTRY = {
    "duckduckgo-search": DuckDuckGoSearchTool,
    "web-browser": WebBrowserTool,
}

def load_enabled_tools(config: List[ToolConfig]) -> List[BaseTool]:
    tools = []
    for tool_config in config:
        if tool_config.enabled:
            tool_class = TOOL_REGISTRY.get(tool_config.id)
            if tool_class:
                tools.append(tool_class())
                logger.info(f"Loaded tool: {tool_config.id}")
            else:
                logger.warning(f"Unknown tool: {tool_config.id}")
    return tools
```

---

## 6. Tool Call Persistence

### Decision
Extend `ConversationMessage` schema to include optional `toolCalls` field.

### Schema Extension

```python
class ToolCallRecord(BaseModel):
    """Record of a single tool invocation"""
    id: str
    name: str
    args: Dict[str, Any]
    status: Literal["pending", "success", "error"]
    result: Optional[str] = None
    error: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None
    started_at: str  # ISO-8601
    completed_at: Optional[str] = None  # ISO-8601

class ConversationMessage(BaseModel):
    # ... existing fields ...
    toolCalls: Optional[List[ToolCallRecord]] = None  # NEW
```

### Storage Schema Version
Bump from v1.0.0 to v1.1.0 (backward compatible - new optional field)

---

## 7. Frontend Tool Call Display

### Decision
Create new `ToolCallBubble.vue` component with collapsible detail view.

### Component Structure

```
ToolCallBubble
├── Collapsed: [Icon] Tool Name • Status (Success/Fail)
└── Expanded:
    ├── Input: { query: "..." }
    ├── Output: [Results/Links]
    └── Error (if any): [Message + Debug]
```

### Styling
- Follow existing MessageBubble patterns
- Use existing color palette (success: green, error: red)
- Collapsible animation (already exists for error details)

---

## 8. Error Handling

### Decision
Create tool-specific error types extending existing error hierarchy.

### Error Types

| Error | Cause | User Message |
|-------|-------|--------------|
| ToolTimeoutError | Tool execution exceeded timeout | "The search took too long. Please try again." |
| ToolNetworkError | Network unavailable | "Unable to connect. Check your internet connection." |
| ToolNotFoundError | Tool ID not in registry | "Tool not available." |
| ToolExecutionError | Tool raised exception | "Something went wrong. See details." |

### Debug Mode
When `DEBUG=true`, tool errors include:
- Full exception traceback
- Request/response details
- Timing information

---

## Dependencies to Add

```text
# backend/requirements.txt additions
duckduckgo-search>=6.0.0
beautifulsoup4>=4.12.0
lxml>=5.0.0  # Optional, for faster HTML parsing
```

---

## Research Sources

- LangChain DuckDuckGoSearchResults API Reference
- LangChain Tool Calling Documentation
- LangChain Streaming Guide
- Existing python-specbot provider implementations
- LangChain ChatOllama GitHub Issues (tool support limitations)
