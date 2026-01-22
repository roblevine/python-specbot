"""
Tool-specific error classes.

Feature: 023-add-search-tools Task T009
"""


class ToolError(Exception):
    """Base exception for tool errors."""

    def __init__(self, message: str, code: str = "TOOL_ERROR") -> None:
        """Initialize tool error.

        Args:
            message: Human-readable error message
            code: Machine-readable error code
        """
        super().__init__(message)
        self.message = message
        self.code = code


class ToolDisabledError(ToolError):
    """Raised when attempting to use a disabled tool."""

    def __init__(self, tool_id: str) -> None:
        """Initialize disabled tool error.

        Args:
            tool_id: ID of the disabled tool
        """
        super().__init__(
            message=f"Tool '{tool_id}' is disabled",
            code="TOOL_DISABLED"
        )
        self.tool_id = tool_id


class ToolExecutionError(ToolError):
    """Raised when tool execution fails."""

    def __init__(self, tool_id: str, reason: str) -> None:
        """Initialize execution error.

        Args:
            tool_id: ID of the tool that failed
            reason: Reason for the failure
        """
        super().__init__(
            message=f"Tool '{tool_id}' execution failed: {reason}",
            code="TOOL_EXECUTION_ERROR"
        )
        self.tool_id = tool_id
        self.reason = reason
