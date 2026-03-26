"""Human-in-the-loop approval hook for gating tool execution."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ToolApprovalHook:
    """Strands HookProvider that interrupts before configured tools for human approval.

    Uses an :class:`~andino.access.AccessEvaluator` to determine which tools
    require approval.  Falls back to a simple name-set check when constructed
    with a plain list of tool names (for backward compat / tests).
    """

    def __init__(self, evaluator: Any = None, *, require_approval: list[str] | None = None) -> None:
        if evaluator is not None:
            self._evaluator = evaluator
            self._tools: set[str] | None = None
        else:
            self._evaluator = None
            self._tools = set(require_approval or [])

    def register_hooks(self, registry: Any, **kwargs: Any) -> None:
        from strands.hooks import BeforeToolCallEvent

        registry.add_callback(BeforeToolCallEvent, self._check_approval)

    def _needs_approval(self, tool_name: str) -> bool:
        if self._evaluator is not None:
            return self._evaluator.needs_approval(tool_name)
        return tool_name in (self._tools or set())

    def _check_approval(self, event: Any) -> None:
        tool_name = event.tool_use["name"]
        if not self._needs_approval(tool_name):
            return

        reason = {
            "tool_name": tool_name,
            "tool_input": event.tool_use.get("input", {}),
        }
        response = event.interrupt(f"approve:{tool_name}", reason=reason)

        if response != "approved":
            event.cancel_tool = f"Tool '{tool_name}' denied: {response}"
            logger.info("tool_denied tool=%s response=%s", tool_name, response)
        else:
            logger.info("tool_approved tool=%s", tool_name)
