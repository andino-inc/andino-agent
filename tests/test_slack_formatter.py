from __future__ import annotations

from andino.channels.slack import _md_to_mrkdwn


class TestMdToMrkdwn:
    def test_bold(self):
        assert _md_to_mrkdwn("**hello**") == "*hello*"

    def test_italic(self):
        assert _md_to_mrkdwn("*hello*") == "_hello_"

    def test_strikethrough(self):
        assert _md_to_mrkdwn("~~deleted~~") == "~deleted~"

    def test_heading(self):
        assert _md_to_mrkdwn("## Section Title") == "*Section Title*"

    def test_link(self):
        assert _md_to_mrkdwn("[text](https://example.com)") == "<https://example.com|text>"

    def test_image(self):
        assert _md_to_mrkdwn("![alt](https://img.png)") == "<https://img.png|alt>"

    def test_code_block_preserved(self):
        text = "```python\nprint('hello')\n```"
        assert _md_to_mrkdwn(text) == text

    def test_inline_code_preserved(self):
        text = "Use `**bold**` syntax"
        result = _md_to_mrkdwn(text)
        assert "`**bold**`" in result


class TestTableConversion:
    def test_simple_table(self):
        md = (
            "| Campo | Detalle |\n"
            "|-------|----------|\n"
            "| ID | 12345 |\n"
            "| Nombre | Test |\n"
        )
        result = _md_to_mrkdwn(md)
        assert "```" in result
        assert "Campo" in result
        assert "12345" in result
        # Separator row should be gone
        assert "|----" not in result

    def test_table_alignment(self):
        md = (
            "| Severity | Criteria |\n"
            "|----------|----------|\n"
            "| SEV1 | Full outage |\n"
            "| SEV2 | Partial |\n"
        )
        result = _md_to_mrkdwn(md)
        # Should be a code block
        assert result.startswith("```\n")
        assert result.strip().endswith("```")
        # Header separator should exist (dashes)
        lines = result.strip().strip("`").strip().splitlines()
        assert len(lines) == 4  # header, separator, 2 data rows

    def test_table_with_bold_cells(self):
        md = (
            "| **Name** | Value |\n"
            "|----------|-------|\n"
            "| A | 1 |\n"
        )
        result = _md_to_mrkdwn(md)
        # Bold inside code block stays as ** (code blocks are protected)
        assert "```" in result

    def test_no_table_passthrough(self):
        text = "This is just normal text\nwith multiple lines"
        assert _md_to_mrkdwn(text) == text

    def test_table_mixed_with_text(self):
        md = (
            "Here is the summary:\n\n"
            "| Key | Value |\n"
            "|-----|-------|\n"
            "| A | 1 |\n"
            "\nEnd of report."
        )
        result = _md_to_mrkdwn(md)
        assert "Here is the summary:" in result
        assert "```" in result
        assert "End of report." in result

    def test_table_single_column(self):
        md = (
            "| Item |\n"
            "|------|\n"
            "| A |\n"
            "| B |\n"
        )
        result = _md_to_mrkdwn(md)
        assert "```" in result
        assert "A" in result
        assert "B" in result
