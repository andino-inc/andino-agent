from __future__ import annotations

from unittest.mock import MagicMock

from andino.hitl import ToolApprovalHook


class TestToolApprovalHook:
    def test_with_plain_list(self):
        hook = ToolApprovalHook(require_approval=["shell", "file_write"])
        assert hook._needs_approval("shell") is True
        assert hook._needs_approval("file_write") is True
        assert hook._needs_approval("http_request") is False

    def test_with_evaluator(self):
        evaluator = MagicMock()
        evaluator.needs_approval.side_effect = lambda t: t == "shell"
        hook = ToolApprovalHook(evaluator=evaluator)
        assert hook._needs_approval("shell") is True
        assert hook._needs_approval("http_request") is False

    def test_empty_config(self):
        hook = ToolApprovalHook(require_approval=[])
        assert hook._needs_approval("anything") is False
