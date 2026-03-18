from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from andino.tools.datadog import (
    _dd_auth,
    _dd_request,
    datadog_get_monitor,
    datadog_list_events,
    datadog_list_monitors,
    datadog_query_metrics,
    datadog_search_logs,
    datadog_search_traces,
)


class TestDdAuth:
    def test_reads_env_vars(self, monkeypatch):
        monkeypatch.setenv("DD_API_KEY", "api-123")
        monkeypatch.setenv("DD_APP_KEY", "app-456")
        monkeypatch.setenv("DD_SITE", "datadoghq.eu")
        assert _dd_auth() == ("api-123", "app-456", "datadoghq.eu")

    def test_defaults(self, monkeypatch):
        monkeypatch.delenv("DD_API_KEY", raising=False)
        monkeypatch.delenv("DD_APP_KEY", raising=False)
        monkeypatch.delenv("DD_APPLICATION_KEY", raising=False)
        monkeypatch.delenv("DD_SITE", raising=False)
        api_key, app_key, site = _dd_auth()
        assert api_key == ""
        assert app_key == ""
        assert site == "datadoghq.com"

    def test_fallback_application_key(self, monkeypatch):
        monkeypatch.setenv("DD_API_KEY", "api-123")
        monkeypatch.delenv("DD_APP_KEY", raising=False)
        monkeypatch.setenv("DD_APPLICATION_KEY", "app-fallback")
        _, app_key, _ = _dd_auth()
        assert app_key == "app-fallback"


class TestDdRequest:
    async def test_missing_credentials(self, monkeypatch):
        monkeypatch.delenv("DD_API_KEY", raising=False)
        monkeypatch.delenv("DD_APP_KEY", raising=False)
        monkeypatch.delenv("DD_APPLICATION_KEY", raising=False)
        ok, msg = await _dd_request("GET", "/api/v1/test")
        assert not ok
        assert "DD_API_KEY" in msg

    @patch("andino.tools.datadog.httpx.AsyncClient")
    async def test_success_response(self, mock_client_cls, monkeypatch):
        monkeypatch.setenv("DD_API_KEY", "key")
        monkeypatch.setenv("DD_APP_KEY", "app")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"data": []}

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        ok, data = await _dd_request("GET", "/api/v1/test")
        assert ok
        assert data == {"data": []}

    @patch("andino.tools.datadog.httpx.AsyncClient")
    async def test_error_response(self, mock_client_cls, monkeypatch):
        monkeypatch.setenv("DD_API_KEY", "key")
        monkeypatch.setenv("DD_APP_KEY", "app")

        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        ok, msg = await _dd_request("GET", "/api/v1/test")
        assert not ok
        assert "403" in msg


class TestSearchLogs:
    @patch("andino.tools.datadog._dd_request")
    async def test_returns_logs(self, mock_req):
        mock_req.return_value = (True, {
            "data": [
                {
                    "attributes": {
                        "timestamp": "2026-03-18T10:00:00Z",
                        "service": "web",
                        "status": "error",
                        "message": "Connection refused",
                        "host": "web-1",
                    }
                }
            ]
        })
        result = await datadog_search_logs(query="service:web status:error")
        assert result["status"] == "success"
        assert "web" in result["content"][0]["text"]

    @patch("andino.tools.datadog._dd_request")
    async def test_no_logs(self, mock_req):
        mock_req.return_value = (True, {"data": []})
        result = await datadog_search_logs(query="nothing")
        assert "No logs found" in result["content"][0]["text"]


class TestQueryMetrics:
    @patch("andino.tools.datadog._dd_request")
    async def test_returns_metrics(self, mock_req):
        mock_req.return_value = (True, {
            "series": [{
                "metric": "system.cpu.user",
                "scope": "host:web-1",
                "pointlist": [[1710000000, 45.2], [1710000060, 48.1]],
                "unit": [{"name": "%"}],
            }]
        })
        result = await datadog_query_metrics(query="avg:system.cpu.user{*}", time_from=1710000000, time_to=1710000120)
        assert result["status"] == "success"
        text = result["content"][0]["text"]
        assert "system.cpu.user" in text
        assert "Min:" in text

    @patch("andino.tools.datadog._dd_request")
    async def test_no_series(self, mock_req):
        mock_req.return_value = (True, {"series": []})
        result = await datadog_query_metrics(query="nothing", time_from=0, time_to=1)
        assert "No data" in result["content"][0]["text"]


class TestListMonitors:
    @patch("andino.tools.datadog._dd_request")
    async def test_returns_monitors(self, mock_req):
        mock_req.return_value = (True, [
            {"id": 123, "name": "CPU Alert", "overall_state": "Alert", "type": "metric alert", "query": "avg:cpu{*} > 90"},
        ])
        result = await datadog_list_monitors()
        assert result["status"] == "success"
        assert "CPU Alert" in result["content"][0]["text"]
        assert "Alert" in result["content"][0]["text"]

    @patch("andino.tools.datadog._dd_request")
    async def test_no_monitors(self, mock_req):
        mock_req.return_value = (True, [])
        result = await datadog_list_monitors()
        assert "No monitors" in result["content"][0]["text"]


class TestGetMonitor:
    @patch("andino.tools.datadog._dd_request")
    async def test_returns_monitor_detail(self, mock_req):
        mock_req.return_value = (True, {
            "id": 123, "name": "CPU Alert", "overall_state": "OK",
            "type": "metric alert", "query": "avg:cpu{*} > 90",
            "message": "CPU is high", "created": "2026-01-01",
            "modified": "2026-03-01", "tags": ["env:prod"],
            "options": {"thresholds": {"critical": 90}},
        })
        result = await datadog_get_monitor(monitor_id=123)
        assert result["status"] == "success"
        text = result["content"][0]["text"]
        assert "CPU Alert" in text
        assert "env:prod" in text
        assert "90" in text


class TestSearchTraces:
    @patch("andino.tools.datadog._dd_request")
    async def test_returns_traces(self, mock_req):
        mock_req.return_value = (True, {
            "data": [{
                "attributes": {
                    "service": "api", "resource_name": "GET /users",
                    "timestamp": "2026-03-18T10:00:00Z",
                    "duration": 15000000, "status": "ok", "trace_id": "abc123",
                }
            }]
        })
        result = await datadog_search_traces(query="service:api")
        assert result["status"] == "success"
        text = result["content"][0]["text"]
        assert "api" in text
        assert "15.0ms" in text

    @patch("andino.tools.datadog._dd_request")
    async def test_no_traces(self, mock_req):
        mock_req.return_value = (True, {"data": []})
        result = await datadog_search_traces(query="nothing")
        assert "No traces found" in result["content"][0]["text"]


class TestListEvents:
    @patch("andino.tools.datadog._dd_request")
    async def test_returns_events(self, mock_req):
        mock_req.return_value = (True, {
            "data": [{
                "attributes": {
                    "title": "Deployment v2.1.0",
                    "timestamp": "2026-03-18T10:00:00Z",
                    "evt": {"name": "deploy"},
                }
            }]
        })
        result = await datadog_list_events(query="source:deploy")
        assert result["status"] == "success"
        assert "Deployment" in result["content"][0]["text"]

    @patch("andino.tools.datadog._dd_request")
    async def test_no_events(self, mock_req):
        mock_req.return_value = (True, {"data": []})
        result = await datadog_list_events()
        assert "No events found" in result["content"][0]["text"]
