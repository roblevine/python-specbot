# Quickstart: LangChain Tool Integration

**Feature**: 024-add-langchain-tools
**Date**: 2026-01-26

## Prerequisites

- Python 3.13+
- Node.js 18+ (for frontend)
- Existing python-specbot setup working
- At least one LLM provider configured (OpenAI, Anthropic, or Ollama)

---

## 1. Install Dependencies

```bash
# Backend
cd backend
pip install ddgs beautifulsoup4 lxml
```

Or add to `requirements.txt`:
```text
ddgs>=7.0.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
```

> **Note**: The `ddgs` package replaces the deprecated `duckduckgo-search` package.
> If you have `duckduckgo-search` installed, uninstall it first: `pip uninstall duckduckgo-search`

---

## 2. Configure Tools

Add to your `.env` file:

```bash
# Tool Configuration
TOOLS='[
  {"id": "duckduckgo-search", "name": "Web Search", "description": "Search the web using DuckDuckGo", "enabled": true},
  {"id": "web-browser", "name": "Browse URL", "description": "Fetch and read web page content", "enabled": true}
]'
```

### Configuration Options

| Tool ID | Description | Requirements |
|---------|-------------|--------------|
| `duckduckgo-search` | Search the web | None (no API key) |
| `web-browser` | Read web pages | None |

### Disable a Tool

Set `enabled: false` to disable:

```bash
TOOLS='[
  {"id": "duckduckgo-search", "name": "Web Search", "description": "...", "enabled": true},
  {"id": "web-browser", "name": "Browse URL", "description": "...", "enabled": false}
]'
```

---

## 3. Verify Tool Loading

Start the backend server and check logs:

```bash
cd backend
python main.py
```

Expected output:
```
INFO:     Tool loaded: duckduckgo-search (Web Search)
INFO:     Tool loaded: web-browser (Browse URL)
INFO:     2 tools available
```

If a tool fails to load:
```
WARNING:  Failed to load tool: web-browser - ModuleNotFoundError: beautifulsoup4
INFO:     1 tools available
```

---

## 4. Test Tool Execution

### Via UI

1. Open the chatbot frontend
2. Select a model that supports tools (GPT-4, Claude, llama3.1)
3. Ask a question that triggers tool use:
   - "What are the latest news headlines?"
   - "Search for Python 3.13 new features"
   - "Read the content from https://example.com"

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"text": "Search for the latest Python news"}'
```

Expected SSE stream:
```
data: {"type":"token","content":"I'll search for that."}

data: {"type":"tool_call","id":"tool-xxx","toolId":"duckduckgo-search","toolName":"Web Search","args":{"query":"latest Python news"}}

data: {"type":"tool_result","id":"tool-xxx","status":"success","result":"Found 5 results...","durationMs":2500}

data: {"type":"token","content":"Here's what I found..."}

data: {"type":"complete","model":"gpt-4","totalTokens":150}
```

---

## 5. Frontend Tool Display

Tool calls appear as collapsible elements in the chat:

```
┌─────────────────────────────────────────┐
│ 🔧 Web Search • ✓ Success         [▼]  │
└─────────────────────────────────────────┘
```

Click to expand:
```
┌─────────────────────────────────────────┐
│ 🔧 Web Search • ✓ Success         [▲]  │
├─────────────────────────────────────────┤
│ Query: "latest Python news"             │
│                                         │
│ Results:                                │
│ • Python 3.13 Released - python.org     │
│ • New Features in Python - realpython   │
│ • Python Update News - dev.to           │
│                                         │
│ Duration: 2.5s                          │
└─────────────────────────────────────────┘
```

---

## 6. Provider Compatibility

| Provider | Tool Support | Notes |
|----------|--------------|-------|
| OpenAI (GPT-4, GPT-4o) | ✅ Full | Recommended |
| Anthropic (Claude 3+) | ✅ Full | Use claude-3-5-sonnet or newer |
| Ollama (llama3.1+) | ⚠️ Limited | Experimental, may not always invoke tools |

### Ollama Note

For Ollama, ensure you're using a model that supports tool calling:

```bash
# Pull a tool-capable model
ollama pull llama3.1

# Configure in .env
OLLAMA_MODELS='[{"id": "llama3.1", "name": "Llama 3.1", "description": "Supports tool calling"}]'
```

---

## 7. Debug Mode

Enable debug mode to see detailed tool execution info:

```bash
DEBUG=true python main.py
```

Error events will include debug info:
```json
{
  "type": "tool_error",
  "id": "tool-xxx",
  "error": "Connection timeout",
  "errorCode": "TIMEOUT",
  "debugInfo": {
    "exception": "TimeoutError",
    "stackTrace": "...",
    "timeout_seconds": 30
  }
}
```

---

## 8. Troubleshooting

### Tools not appearing in conversation

1. Check tool configuration in `.env`
2. Verify tools loaded at startup (check logs)
3. Ensure model supports tool calling

### Search returns no results

1. **Check you're using `ddgs` package** (not `duckduckgo-search`)
   - The old `duckduckgo-search` package is deprecated and returns 0 results
   - Run: `pip uninstall duckduckgo-search && pip install ddgs`
2. DuckDuckGo may rate-limit aggressive queries
3. Try a different search term
4. Check network connectivity

### Web browser times out

1. Default timeout is 30 seconds
2. Some sites block automated requests
3. Try a different URL

### Ollama not calling tools

1. Verify using llama3.1 or newer
2. Tool calling on Ollama is experimental
3. Consider using OpenAI or Anthropic for reliable tool support

---

## Next Steps

- Configure additional tools as they become available
- Adjust tool timeouts via environment variables
- Review tool call history in conversation details
