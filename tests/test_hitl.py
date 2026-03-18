from __future__ import annotations

from andino.hitl import HitlConfig


class TestHitlConfig:
    def test_defaults(self):
        config = HitlConfig()
        assert config.require_approval == []
        assert config.approvers == []

    def test_require_approval_parsed(self):
        config = HitlConfig(require_approval=["strands_tools.shell:shell"])
        assert config.require_approval == ["strands_tools.shell:shell"]

    def test_approvers_parsed(self):
        config = HitlConfig(approvers=["U12345678", "U87654321"])
        assert config.approvers == ["U12345678", "U87654321"]

    def test_approvers_empty_by_default(self):
        config = HitlConfig(require_approval=["tool_a"])
        assert config.approvers == []
