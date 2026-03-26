from __future__ import annotations

from andino.access import AccessConfig, AccessEvaluator, AccessGroup, AccessRule


def _make_evaluator(**kwargs) -> AccessEvaluator:
    config = AccessConfig(**kwargs)
    return AccessEvaluator(config)


class TestAccessEvaluatorNoRules:
    def test_empty_config_allows_all(self):
        ev = AccessEvaluator()
        assert ev.can_request("U123", "shell") is True
        assert ev.can_request("U123", "jira_create_issue") is True

    def test_empty_config_no_approval(self):
        ev = AccessEvaluator()
        assert ev.needs_approval("shell") is False

    def test_empty_config_can_approve(self):
        ev = AccessEvaluator()
        assert ev.can_approve("U123", "shell") is True

    def test_has_rules_false(self):
        ev = AccessEvaluator()
        assert ev.has_rules is False


class TestCanRequest:
    def test_allow_all(self):
        ev = _make_evaluator(rules=[AccessRule(tool="shell", allow="all")])
        assert ev.can_request("anyone", "shell") is True

    def test_allow_group(self):
        ev = _make_evaluator(
            groups={"admins": [AccessGroup(slack_id="U111")]},
            rules=[AccessRule(tool="shell", allow="admins")],
        )
        assert ev.can_request("U111", "shell") is True
        assert ev.can_request("U999", "shell") is False

    def test_glob_pattern(self):
        ev = _make_evaluator(
            rules=[AccessRule(tool="datadog_*", allow="all")],
        )
        assert ev.can_request("U1", "datadog_search_logs") is True
        assert ev.can_request("U1", "datadog_query_metrics") is True
        assert ev.can_request("U1", "jira_create_issue") is True  # no rule = allowed

    def test_wildcard_catch_all(self):
        ev = _make_evaluator(
            groups={"admins": [AccessGroup(slack_id="U111")]},
            rules=[
                AccessRule(tool="shell", allow="admins"),
                AccessRule(tool="*", allow="all"),
            ],
        )
        assert ev.can_request("U999", "shell") is False
        assert ev.can_request("U999", "datadog_search_logs") is True


class TestNeedsApproval:
    def test_no_approval(self):
        ev = _make_evaluator(rules=[AccessRule(tool="shell", allow="all")])
        assert ev.needs_approval("shell") is False

    def test_with_approval(self):
        ev = _make_evaluator(
            rules=[AccessRule(tool="shell", allow="all", require_approval=True)],
        )
        assert ev.needs_approval("shell") is True
        assert ev.needs_approval("jira_create_issue") is False

    def test_tools_requiring_approval(self):
        ev = _make_evaluator(
            rules=[
                AccessRule(tool="shell", allow="all", require_approval=True),
                AccessRule(tool="file_write", allow="all", require_approval=True),
                AccessRule(tool="*", allow="all"),
            ],
        )
        assert sorted(ev.tools_requiring_approval) == ["file_write", "shell"]


class TestCanApprove:
    def test_default_all(self):
        ev = _make_evaluator(
            rules=[AccessRule(tool="shell", allow="all", require_approval=True)],
        )
        assert ev.can_approve("anyone", "shell") is True

    def test_group_approvers(self):
        ev = _make_evaluator(
            groups={"admins": [AccessGroup(slack_id="U111")]},
            rules=[
                AccessRule(tool="shell", allow="all", require_approval=True, approvers="admins"),
            ],
        )
        assert ev.can_approve("U111", "shell") is True
        assert ev.can_approve("U999", "shell") is False


class TestFromYaml:
    def test_nonexistent_file(self):
        ev = AccessEvaluator.from_yaml("/nonexistent/access.yaml")
        assert ev.has_rules is False
        assert ev.can_request("anyone", "anything") is True

    def test_real_file(self, tmp_path):
        p = tmp_path / "access.yaml"
        p.write_text(
            "groups:\n"
            "  admins:\n"
            "    - slack_id: U111\n"
            "      name: Admin\n"
            "rules:\n"
            "  - tool: shell\n"
            "    allow: admins\n"
            "    require_approval: true\n"
            "    approvers: admins\n"
        )
        ev = AccessEvaluator.from_yaml(str(p))
        assert ev.has_rules is True
        assert ev.can_request("U111", "shell") is True
        assert ev.can_request("U999", "shell") is False
        assert ev.needs_approval("shell") is True
