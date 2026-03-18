from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx
from strands import tool

logger = logging.getLogger(__name__)

_CREDS_ERROR = (
    "Datadog credentials not configured. "
    "Set DD_API_KEY and DD_APP_KEY environment variables."
)


def _dd_auth() -> tuple[str, str, str]:
    """Return (api_key, app_key, site) from environment."""
    api_key = os.environ.get("DD_API_KEY", "").strip()
    app_key = (os.environ.get("DD_APP_KEY", "") or os.environ.get("DD_APPLICATION_KEY", "")).strip()
    site = os.environ.get("DD_SITE", "datadoghq.com").strip()
    return api_key, app_key, site


def _ok(text: str) -> dict:
    return {"status": "success", "content": [{"text": text}]}


def _err(text: str) -> dict:
    return {"status": "error", "content": [{"text": text}]}


async def _dd_request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> tuple[bool, dict | list | str]:
    """Execute a Datadog API request.

    Returns (success, data_or_error_message).
    """
    api_key, app_key, site = _dd_auth()
    if not api_key or not app_key:
        return False, _CREDS_ERROR

    url = f"https://api.{site}{path}"
    headers = {
        "DD-API-KEY": api_key,
        "DD-APPLICATION-KEY": app_key,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                method, url, headers=headers, params=params, json=json_body,
            )
    except httpx.HTTPError as exc:
        logger.exception("datadog_request_failed method=%s path=%s", method, path)
        return False, f"HTTP error while contacting Datadog: {exc}"

    if resp.status_code == 200:
        return True, resp.json()
    return False, f"Datadog API error {resp.status_code}: {resp.text[:500]}"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@tool
async def datadog_search_logs(
    query: str,
    time_from: str = "now-1h",
    time_to: str = "now",
    limit: int = 25,
) -> dict:
    """Search Datadog logs matching a query within a time range.

    Uses the Datadog Logs Search API to find log entries. The query uses
    Datadog log search syntax (e.g. "service:web status:error",
    "@http.status_code:5*", "source:nginx").

    Args:
        query: Datadog log search query string.
        time_from: Start of time range (e.g. "now-1h", "now-15m", ISO timestamp).
        time_to: End of time range (e.g. "now", ISO timestamp).
        limit: Maximum number of logs to return (default 25, max 50).

    Returns:
        A dict with matching log entries.
    """
    limit = min(limit, 50)
    body: dict[str, Any] = {
        "filter": {"query": query, "from": time_from, "to": time_to},
        "page": {"limit": limit},
        "sort": "-timestamp",
    }

    ok, data = await _dd_request("POST", "/api/v2/logs/events/search", json_body=body)
    if not ok:
        return _err(data)

    logs = data.get("data", [])
    if not logs:
        return _ok(f"No logs found for query: {query}")

    lines = [f"Found {len(logs)} log(s) for query: {query}"]
    for log_entry in logs:
        attrs = log_entry.get("attributes", {})
        ts = attrs.get("timestamp", "?")
        service = attrs.get("service", "?")
        status = attrs.get("status", "?")
        message = attrs.get("message", "")[:200]
        host = attrs.get("host", "?")
        lines.append(f"  [{ts}] {status} {service}@{host}: {message}")

    return _ok("\n".join(lines))


@tool
async def datadog_query_metrics(
    query: str,
    time_from: int,
    time_to: int,
) -> dict:
    """Query Datadog metrics timeseries data.

    Uses the Datadog Metrics Query API to retrieve timeseries data points.
    Common metric queries: "avg:system.cpu.user{*}", "sum:trace.http.request.hits{service:web}",
    "avg:system.mem.used{host:myhost}".

    Args:
        query: Datadog metrics query string.
        time_from: Start time as Unix epoch seconds.
        time_to: End time as Unix epoch seconds.

    Returns:
        A dict with timeseries data.
    """
    ok, data = await _dd_request(
        "GET", "/api/v1/query",
        params={"query": query, "from": time_from, "to": time_to},
    )
    if not ok:
        return _err(data)

    series = data.get("series", [])
    if not series:
        return _ok(f"No data for query: {query}")

    lines = [f"Metrics query: {query}"]
    for s in series:
        scope = s.get("scope", "?")
        metric = s.get("metric", "?")
        points = s.get("pointlist", [])
        unit = s.get("unit", [{}])
        unit_name = unit[0].get("name", "") if unit else ""

        lines.append(f"\n  Series: {metric} ({scope})")
        lines.append(f"  Points: {len(points)}")

        if points:
            # Show first, last, and summary stats
            values = [p[1] for p in points if p[1] is not None]
            if values:
                lines.append(f"  Min: {min(values):.2f}{unit_name}")
                lines.append(f"  Max: {max(values):.2f}{unit_name}")
                lines.append(f"  Avg: {sum(values) / len(values):.2f}{unit_name}")
                lines.append(f"  Latest: {values[-1]:.2f}{unit_name}")

    return _ok("\n".join(lines))


@tool
async def datadog_list_monitors(
    query: str = "",
    tags: str = "",
) -> dict:
    """List Datadog monitors, optionally filtered by name or tags.

    Args:
        query: Filter monitors by name (partial match).
        tags: Comma-separated tags to filter by (e.g. "env:prod,service:web").

    Returns:
        A dict with matching monitors and their statuses.
    """
    params: dict[str, Any] = {}
    if query:
        params["query"] = query
    if tags:
        params["monitor_tags"] = tags

    ok, data = await _dd_request("GET", "/api/v1/monitor", params=params)
    if not ok:
        return _err(data)

    if not isinstance(data, list):
        data = []

    if not data:
        return _ok("No monitors found.")

    lines = [f"Found {len(data)} monitor(s):"]
    for m in data[:50]:  # Cap output
        name = m.get("name", "Unnamed")
        status = m.get("overall_state", "?")
        mon_type = m.get("type", "?")
        mon_id = m.get("id", "?")
        mon_query = m.get("query", "")[:100]
        lines.append(f"  [{status}] #{mon_id} {name} ({mon_type})")
        lines.append(f"    Query: {mon_query}")

    return _ok("\n".join(lines))


@tool
async def datadog_get_monitor(monitor_id: int) -> dict:
    """Get details of a specific Datadog monitor by ID.

    Args:
        monitor_id: The numeric monitor ID.

    Returns:
        A dict with full monitor details including status, query, thresholds, and message.
    """
    ok, data = await _dd_request("GET", f"/api/v1/monitor/{monitor_id}")
    if not ok:
        return _err(data)

    name = data.get("name", "Unnamed")
    status = data.get("overall_state", "?")
    mon_type = data.get("type", "?")
    query = data.get("query", "")
    message = data.get("message", "")[:300]
    created = data.get("created", "?")
    modified = data.get("modified", "?")
    tags = ", ".join(data.get("tags", []))
    options = data.get("options", {})
    thresholds = json.dumps(options.get("thresholds", {}))

    lines = [
        f"Monitor #{monitor_id}: {name}",
        f"Status: {status}",
        f"Type: {mon_type}",
        f"Query: {query}",
        f"Thresholds: {thresholds}",
        f"Tags: {tags or 'none'}",
        f"Created: {created}",
        f"Modified: {modified}",
        f"Message: {message}",
    ]
    return _ok("\n".join(lines))


@tool
async def datadog_search_traces(
    query: str,
    time_from: str = "now-1h",
    time_to: str = "now",
    limit: int = 25,
) -> dict:
    """Search APM traces/spans matching a query within a time range.

    Uses the Datadog Spans Search API. Query uses Datadog APM search syntax
    (e.g. "service:web resource_name:/api/users", "env:prod status:error",
    "@duration:>1s").

    Args:
        query: Datadog APM span search query string.
        time_from: Start of time range (e.g. "now-1h", "now-15m", ISO timestamp).
        time_to: End of time range (e.g. "now", ISO timestamp).
        limit: Maximum number of spans to return (default 25, max 50).

    Returns:
        A dict with matching traces/spans.
    """
    limit = min(limit, 50)
    body: dict[str, Any] = {
        "data": {
            "type": "search_request",
            "attributes": {
                "filter": {"query": query, "from": time_from, "to": time_to},
                "page": {"limit": limit},
                "sort": "-timestamp",
            },
        },
    }

    ok, data = await _dd_request("POST", "/api/v2/spans/events/search", json_body=body)
    if not ok:
        return _err(data)

    spans = data.get("data", [])
    if not spans:
        return _ok(f"No traces found for query: {query}")

    lines = [f"Found {len(spans)} span(s) for query: {query}"]
    for span in spans:
        attrs = span.get("attributes", {})
        service = attrs.get("service", "?")
        resource = attrs.get("resource_name", "?")
        ts = attrs.get("timestamp", "?")
        duration = attrs.get("duration", 0)
        status = attrs.get("status", "?")
        trace_id = attrs.get("trace_id", "?")
        duration_ms = duration / 1_000_000 if isinstance(duration, (int, float)) else 0
        lines.append(f"  [{ts}] {service} {resource} {duration_ms:.1f}ms ({status}) trace:{trace_id}")

    return _ok("\n".join(lines))


@tool
async def datadog_list_events(
    query: str = "",
    time_from: str = "now-1h",
    time_to: str = "now",
) -> dict:
    """List Datadog events matching a query within a time range.

    Events include deployments, alerts, configuration changes, and custom events.

    Args:
        query: Datadog event search query (e.g. "source:deploy", "priority:normal").
        time_from: Start of time range (e.g. "now-1h", ISO timestamp).
        time_to: End of time range (e.g. "now", ISO timestamp).

    Returns:
        A dict with matching events.
    """
    params: dict[str, Any] = {
        "filter[from]": time_from,
        "filter[to]": time_to,
    }
    if query:
        params["filter[query]"] = query

    ok, data = await _dd_request("GET", "/api/v2/events", params=params)
    if not ok:
        return _err(data)

    events = data.get("data", [])
    if not events:
        return _ok(f"No events found{' for query: ' + query if query else ''}.")

    lines = [f"Found {len(events)} event(s):"]
    for ev in events:
        attrs = ev.get("attributes", {})
        title = attrs.get("title", attrs.get("message", "?"))[:100]
        ts = attrs.get("timestamp", "?")
        source = attrs.get("evt", {}).get("name", "?")
        lines.append(f"  [{ts}] {source}: {title}")

    return _ok("\n".join(lines))
