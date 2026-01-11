"""
Unit Tests for LLM Service

Tests LLM service initialization, configuration, and core functionality in isolation.

Feature: 006-openai-langchain-chat Phase 2 (Foundational)
Tests: T004 (TDD - these should FAIL before implementation)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.unit
def test_chatgpt_initialization_with_api_key():
    """
    T004: Unit test for ChatOpenAI initialization with valid API key.

    Validates that the LLM service properly initializes ChatOpenAI
    with the provided API key and model configuration.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.llm_service import initialize_llm

    with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
        mock_instance = Mock()
        mock_chat.return_value = mock_instance

        # Initialize with explicit config
        llm = initialize_llm(api_key="test-key", model="gpt-3.5-turbo")

        # Verify ChatOpenAI was called with correct params
        mock_chat.assert_called_once_with(
            api_key="test-key",
            model="gpt-3.5-turbo"
        )
        assert llm == mock_instance


@pytest.mark.unit
def test_config_loading_from_environment():
    """
    T004: Unit test for loading configuration from environment variables.

    Validates that the service loads OPENAI_API_KEY and OPENAI_MODEL
    from environment variables.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.llm_service import load_config

    # Mock environment variables
    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'env-test-key',
        'OPENAI_MODEL': 'gpt-4'
    }):
        config = load_config()

        assert config['api_key'] == 'env-test-key'
        assert config['model'] == 'gpt-4'


@pytest.mark.unit
def test_config_loading_with_default_model():
    """
    T004: Unit test for default model when OPENAI_MODEL not set.

    Validates that gpt-3.5-turbo is used as default when OPENAI_MODEL
    is not provided in environment.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.llm_service import load_config

    # Mock environment with only API key (no model)
    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key'
    }, clear=True):
        config = load_config()

        assert config['api_key'] == 'test-key'
        assert config['model'] == 'gpt-3.5-turbo'  # Default


@pytest.mark.unit
def test_config_loading_missing_api_key():
    """
    T004: Unit test for error handling when API key is missing.

    Validates that appropriate error is raised when OPENAI_API_KEY
    is not configured.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.llm_service import load_config

    # Mock environment without API key
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            load_config()


@pytest.mark.unit
def test_llm_service_singleton_pattern():
    """
    T004: Unit test for LLM service singleton/caching behavior.

    Validates that the LLM instance is reused rather than recreated
    on every call (performance optimization).

    Expected: FAIL (service not implemented yet)
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_llm_instance

    # Clear cached instance before test
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            mock_instance = Mock()
            mock_chat.return_value = mock_instance

            # Call twice
            llm1 = get_llm_instance()
            llm2 = get_llm_instance()

            # Should only initialize once
            assert mock_chat.call_count == 1
            assert llm1 is llm2

    # Clean up: clear cached instance after test
    llm_service._llm_instance = None
