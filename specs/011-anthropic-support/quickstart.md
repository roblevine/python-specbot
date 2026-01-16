# Quickstart: Anthropic Claude Model Support

**Feature**: 011-anthropic-support
**Date**: 2026-01-15

## Prerequisites

- Existing SpecBot installation with OpenAI support working
- Anthropic API key from [console.anthropic.com](https://console.anthropic.com/)

## Setup Steps

### 1. Install Dependencies

```bash
cd backend
pip install langchain-anthropic
```

Or add to requirements.txt:
```
langchain-anthropic>=0.2.0
```

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Anthropic Models (JSON array)
ANTHROPIC_MODELS='[
  {
    "id": "claude-3-5-sonnet-20241022",
    "name": "Claude 3.5 Sonnet",
    "description": "Most capable Claude model for complex tasks",
    "provider": "anthropic",
    "default": false
  },
  {
    "id": "claude-3-haiku-20240307",
    "name": "Claude 3 Haiku",
    "description": "Fast and efficient for simple tasks",
    "provider": "anthropic",
    "default": false
  }
]'
```

### 3. Update OpenAI Models (if needed)

Add the `provider` field to existing OpenAI models:

```bash
# Update OPENAI_MODELS to include provider field
OPENAI_MODELS='[
  {
    "id": "gpt-4",
    "name": "GPT-4",
    "description": "Most capable OpenAI model",
    "provider": "openai",
    "default": true
  },
  {
    "id": "gpt-3.5-turbo",
    "name": "GPT-3.5 Turbo",
    "description": "Fast and efficient",
    "provider": "openai",
    "default": false
  }
]'
```

**Important**: Exactly one model across all providers must have `"default": true`.

### 4. Restart the Application

```bash
# Backend
cd backend && uvicorn src.main:app --reload

# Frontend (separate terminal)
cd frontend && npm run dev
```

### 5. Verify Setup

1. Open the application in your browser
2. Check the model selector dropdown
3. You should see both OpenAI and Anthropic models listed
4. Select a Claude model and send a test message

## Configuration Options

### Single Provider Setup

**Anthropic Only** (no OpenAI):
```bash
# Unset or remove OPENAI_API_KEY
# Set ANTHROPIC_API_KEY and ANTHROPIC_MODELS
# Make sure one Anthropic model has default: true
```

**OpenAI Only** (existing behavior):
```bash
# Keep OPENAI_API_KEY and OPENAI_MODELS
# Don't set ANTHROPIC_API_KEY
# System behaves as before
```

### Available Claude Models

| Model ID | Name | Best For |
|----------|------|----------|
| `claude-3-5-sonnet-20241022` | Claude 3.5 Sonnet | Complex reasoning, coding, analysis |
| `claude-3-opus-20240229` | Claude 3 Opus | Most capable, nuanced tasks |
| `claude-3-haiku-20240307` | Claude 3 Haiku | Fast responses, simple tasks |

## Troubleshooting

### Models Not Appearing

1. Check `ANTHROPIC_API_KEY` is set correctly
2. Verify `ANTHROPIC_MODELS` is valid JSON
3. Check backend logs for configuration errors

### Authentication Errors

1. Verify API key is valid at [console.anthropic.com](https://console.anthropic.com/)
2. Check key has appropriate permissions
3. Look for "AI service configuration error" in responses

### Model Selector Disabled

- This is expected behavior when a conversation has messages
- Start a new conversation to change models
- See FR-007 in spec for details

## API Key Security

- Never commit API keys to version control
- Use `.env` files (gitignored) for local development
- Use environment variables or secrets management in production
