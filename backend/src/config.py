"""
LLM Configuration Module

Manages LLM provider settings, API keys, and model configurations for the chatbot.
Supports multiple LLM providers (OpenAI, Anthropic, Ollama, local models) via LangChain.

Feature: 005-llm-integration
"""

import os
from typing import Dict, Literal
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLMConfig(BaseSettings):
    """
    LLM configuration settings loaded from environment variables.

    Environment variables are loaded from backend/.env file.
    See backend/.env.example for required configuration.
    """

    # OpenAI Configuration
    openai_api_key: str = ""
    openai_org_id: str | None = None

    # Model Configuration
    default_llm_model: Literal["gpt-5", "gpt-5-codex"] = "gpt-5"
    available_models: str = "gpt-5,gpt-5-codex"

    # Streaming Configuration
    stream_timeout: int = 30  # seconds
    max_tokens: int = 4096
    temperature: float = 0.7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra env vars not in this config


# Global configuration instance
settings = LLMConfig()


# Model ID mappings for LangChain
MODEL_MAPPINGS: Dict[str, str] = {
    "gpt-5": "gpt-5",
    "gpt-5-codex": "gpt-5-codex",
    # Future multi-provider support (imminent - Week 2):
    # "claude-3-opus": "claude-3-opus-20240229",
    # "claude-3-sonnet": "claude-3-sonnet-20240229",
    # "llama-3-70b": "llama3:70b",
    # "codellama-34b": "codellama:34b",
}


def get_model_id(model_name: str) -> str:
    """
    Get the LangChain model ID for a given model name.

    Args:
        model_name: User-facing model name (e.g., "gpt-5", "gpt-5-codex")

    Returns:
        LangChain-compatible model ID

    Raises:
        ValueError: If model_name is not supported
    """
    if model_name not in MODEL_MAPPINGS:
        raise ValueError(
            f"Unsupported model: {model_name}. "
            f"Available models: {', '.join(MODEL_MAPPINGS.keys())}"
        )
    return MODEL_MAPPINGS[model_name]


def get_available_models() -> list[str]:
    """
    Get list of available model names.

    Returns:
        List of user-facing model names
    """
    return list(MODEL_MAPPINGS.keys())


def validate_api_key() -> bool:
    """
    Validate that the OpenAI API key is configured.

    Returns:
        True if API key is present and non-empty
    """
    return bool(settings.openai_api_key and settings.openai_api_key.strip())
