"""Unified access control — authorization + tool approval in one file."""

from __future__ import annotations

import fnmatch
import logging
from pathlib import Path

import yaml
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AccessGroup(BaseModel):
    slack_id: str
    name: str = ""


class AccessRule(BaseModel):
    tool: str  # tool name or glob pattern ("shell", "datadog_*", "*")
    allow: str = "all"  # group name or "all"
    require_approval: bool = False
    approvers: str = "all"  # group name or "all"


class AccessConfig(BaseModel):
    groups: dict[str, list[AccessGroup]] = {}
    rules: list[AccessRule] = []


class AccessEvaluator:
    """Evaluate access rules for tool authorization and approval.

    Without an access config (or with an empty one), everything is allowed
    and nothing requires approval — the agent is fully autonomous.
    """

    def __init__(self, config: AccessConfig | None = None) -> None:
        self._config = config or AccessConfig()
        self._group_ids: dict[str, set[str]] = {}
        for group_name, members in self._config.groups.items():
            self._group_ids[group_name] = {m.slack_id for m in members}

    @classmethod
    def from_yaml(cls, path: str) -> AccessEvaluator:
        """Load access config from a YAML file."""
        p = Path(path)
        if not p.is_file():
            logger.info("access_file_not_found path=%s — fully autonomous", path)
            return cls()
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        config = AccessConfig.model_validate(raw)
        logger.info("access_loaded path=%s groups=%d rules=%d", path, len(config.groups), len(config.rules))
        return cls(config)

    def _find_rule(self, tool_name: str) -> AccessRule | None:
        """Find the first matching rule for a tool name."""
        for rule in self._config.rules:
            if fnmatch.fnmatch(tool_name, rule.tool):
                return rule
        return None

    def _user_in_group(self, user_id: str, group: str) -> bool:
        """Check if a user belongs to a group."""
        if group == "all":
            return True
        ids = self._group_ids.get(group)
        if ids is None:
            logger.warning("access_unknown_group group=%s", group)
            return False
        return user_id in ids

    def can_request(self, user_id: str, tool_name: str) -> bool:
        """Check if a user is allowed to trigger a task that uses this tool.

        Called in the channel handler BEFORE the task is submitted.
        Without rules, everything is allowed.
        """
        rule = self._find_rule(tool_name)
        if rule is None:
            return True  # no rule = allowed
        return self._user_in_group(user_id, rule.allow)

    def needs_approval(self, tool_name: str) -> bool:
        """Check if a tool requires human approval before execution.

        Replaces hitl.require_approval.
        """
        rule = self._find_rule(tool_name)
        if rule is None:
            return False
        return rule.require_approval

    def can_approve(self, user_id: str, tool_name: str) -> bool:
        """Check if a user can approve a tool execution.

        Replaces hitl.approvers.
        """
        rule = self._find_rule(tool_name)
        if rule is None:
            return True
        return self._user_in_group(user_id, rule.approvers)

    @property
    def tools_requiring_approval(self) -> list[str]:
        """Return tool patterns that require approval (for ToolApprovalHook)."""
        return [r.tool for r in self._config.rules if r.require_approval]

    @property
    def has_rules(self) -> bool:
        return len(self._config.rules) > 0
