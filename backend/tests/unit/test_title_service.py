"""
Unit Tests for Title Generation Service

Tests the title generation service including prompt construction,
post-processing, and truncation.

Feature: 019-llm-conversation-titles
Tasks: T004, T035
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

# Import will fail until service is implemented - this is expected for TDD
try:
    from src.services.title_service import (
        build_title_prompt,
        truncate_title,
        clean_title_response,
        generate_title,
    )
    SERVICE_AVAILABLE = True
except ImportError:
    SERVICE_AVAILABLE = False


@pytest.mark.skipif(not SERVICE_AVAILABLE, reason="Title service not yet implemented")
class TestBuildTitlePrompt:
    """Tests for title prompt construction."""

    def test_build_prompt_with_user_and_assistant_messages(self):
        """Test prompt construction with standard user/assistant exchange."""
        messages = [
            {"sender": "user", "text": "How do I implement a binary search tree in Python?"},
            {"sender": "system", "text": "To implement a binary search tree..."}
        ]

        prompt = build_title_prompt(messages)

        assert "binary search tree" in prompt.lower() or "conversation" in prompt.lower()
        assert "60 characters" in prompt or "concise" in prompt.lower()

    def test_build_prompt_includes_instruction_for_brevity(self):
        """Test that prompt instructs LLM to be brief."""
        messages = [
            {"sender": "user", "text": "Hello"},
            {"sender": "system", "text": "Hi there!"}
        ]

        prompt = build_title_prompt(messages)

        # Should contain instruction about title generation
        assert len(prompt) > 0
        # Should mention being concise or having a max length
        assert "title" in prompt.lower()


@pytest.mark.skipif(not SERVICE_AVAILABLE, reason="Title service not yet implemented")
class TestTruncateTitle:
    """Tests for title truncation."""

    def test_truncate_short_title_unchanged(self):
        """Test that short titles are not modified."""
        title = "Short Title"

        result = truncate_title(title, max_length=60)

        assert result == "Short Title"

    def test_truncate_exactly_60_chars_unchanged(self):
        """Test that 60-char titles are not modified."""
        title = "A" * 60

        result = truncate_title(title, max_length=60)

        assert result == title
        assert len(result) == 60

    def test_truncate_long_title_at_word_boundary(self):
        """Test that long titles are truncated at word boundary."""
        title = "This is a very long conversation title that exceeds the maximum allowed characters"

        result = truncate_title(title, max_length=60)

        assert len(result) <= 60
        # Should not cut in the middle of a word
        assert not result.endswith(" ")
        # Should still be meaningful
        assert len(result) > 20

    def test_truncate_single_long_word(self):
        """Test truncation of a single very long word."""
        title = "A" * 100

        result = truncate_title(title, max_length=60)

        assert len(result) <= 60

    def test_truncate_with_trailing_ellipsis_option(self):
        """Test that truncation can optionally add ellipsis."""
        title = "This is a very long conversation title that needs truncating"

        result = truncate_title(title, max_length=60)

        assert len(result) <= 60


@pytest.mark.skipif(not SERVICE_AVAILABLE, reason="Title service not yet implemented")
class TestCleanTitleResponse:
    """Tests for cleaning LLM title response."""

    def test_clean_removes_surrounding_quotes(self):
        """Test that surrounding quotes are removed."""
        assert clean_title_response('"Hello World"') == "Hello World"
        assert clean_title_response("'Hello World'") == "Hello World"

    def test_clean_strips_whitespace(self):
        """Test that whitespace is stripped."""
        assert clean_title_response("  Hello World  ") == "Hello World"
        assert clean_title_response("\n\tHello World\n") == "Hello World"

    def test_clean_removes_title_prefix(self):
        """Test that common LLM prefixes are removed."""
        assert clean_title_response("Title: Hello World") == "Hello World"
        assert clean_title_response("Conversation title: Hello World") == "Hello World"

    def test_clean_handles_empty_response(self):
        """Test handling of empty response."""
        assert clean_title_response("") == ""
        assert clean_title_response("   ") == ""

    def test_clean_preserves_normal_title(self):
        """Test that normal titles are preserved."""
        assert clean_title_response("Binary Search Implementation") == "Binary Search Implementation"


@pytest.mark.skipif(not SERVICE_AVAILABLE, reason="Title service not yet implemented")
class TestGenerateTitle:
    """Tests for the generate_title function."""

    @pytest.mark.asyncio
    async def test_generate_title_success(self):
        """Test successful title generation."""
        messages = [
            {"sender": "user", "text": "How do I sort a list in Python?"},
            {"sender": "system", "text": "You can use the sorted() function..."}
        ]

        with patch('src.services.title_service.get_llm_for_model') as mock_llm:
            mock_model = MagicMock()
            mock_model.ainvoke = AsyncMock(return_value=MagicMock(content="Python List Sorting"))
            mock_llm.return_value = mock_model

            result = await generate_title(messages, "gpt-3.5-turbo")

            assert result == "Python List Sorting"
            mock_llm.assert_called_once_with("gpt-3.5-turbo")

    @pytest.mark.asyncio
    async def test_generate_title_truncates_long_response(self):
        """Test that long LLM responses are truncated."""
        messages = [
            {"sender": "user", "text": "Hello"},
            {"sender": "system", "text": "Hi there!"}
        ]

        long_title = "A" * 100

        with patch('src.services.title_service.get_llm_for_model') as mock_llm:
            mock_model = MagicMock()
            mock_model.ainvoke = AsyncMock(return_value=MagicMock(content=long_title))
            mock_llm.return_value = mock_model

            result = await generate_title(messages, "gpt-3.5-turbo")

            assert len(result) <= 60

    @pytest.mark.asyncio
    async def test_generate_title_handles_empty_response(self):
        """Test handling of empty LLM response."""
        messages = [
            {"sender": "user", "text": "Hello"},
            {"sender": "system", "text": "Hi!"}
        ]

        with patch('src.services.title_service.get_llm_for_model') as mock_llm:
            mock_model = MagicMock()
            mock_model.ainvoke = AsyncMock(return_value=MagicMock(content=""))
            mock_llm.return_value = mock_model

            # Should either return empty or fallback - depends on implementation
            result = await generate_title(messages, "gpt-3.5-turbo")

            # Result should be a string (empty or fallback)
            assert isinstance(result, str)


@pytest.mark.skipif(not SERVICE_AVAILABLE, reason="Title service not yet implemented")
class TestGenerateTitleErrorHandling:
    """Tests for error handling in title generation (T035)."""

    @pytest.mark.asyncio
    async def test_generate_title_logs_llm_error(self):
        """Test that LLM errors are logged appropriately."""
        messages = [
            {"sender": "user", "text": "Hello"},
            {"sender": "system", "text": "Hi!"}
        ]

        with patch('src.services.title_service.get_llm_for_model') as mock_llm:
            mock_model = MagicMock()
            mock_model.ainvoke = AsyncMock(side_effect=Exception("LLM error"))
            mock_llm.return_value = mock_model

            with patch('src.services.title_service.logger') as mock_logger:
                with pytest.raises(Exception):
                    await generate_title(messages, "gpt-3.5-turbo")

                # Verify error was logged
                mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_generate_title_with_invalid_model(self):
        """Test error handling for invalid model ID."""
        messages = [
            {"sender": "user", "text": "Hello"},
            {"sender": "system", "text": "Hi!"}
        ]

        with patch('src.services.title_service.get_llm_for_model') as mock_llm:
            mock_llm.side_effect = ValueError("Model not found: invalid-model")

            with pytest.raises(ValueError) as exc_info:
                await generate_title(messages, "invalid-model")

            assert "invalid-model" in str(exc_info.value)
