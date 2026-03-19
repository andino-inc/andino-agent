---
name: diagnose-service
description: "Health check a specific service — latency, error rate, throughput, logs, and monitor status"
---
# Diagnose Service

## Arguments

- `$0` (required): Service name (e.g., "payment-service", "api-gateway")
- `endpoint` (optional): Specific health check URL to probe (e.g., "https://api.example.com/health")

## Steps

1. **HTTP health check** (if endpoint provided)
   - Use `http_request` to GET the health endpoint
   - Note response status code, response time, and body
   - If no endpoint provided, skip this step

2. **Check monitors**
   - Use `datadog_list_monitors` filtered by the service name
   - For any monitors in Alert or Warn state, use `datadog_get_monitor` for details
   - Summarize: total monitors, how many OK, Alert, Warn

3. **Query current metrics** (last 15 minutes)
   - Use `datadog_query_metrics` for each:
     - **Latency:** `avg:trace.http.request.duration{service:<name>}` (also p95 and p99)
     - **Error rate:** `sum:trace.http.request.errors{service:<name>}.as_rate()`
     - **Throughput:** `sum:trace.http.request.hits{service:<name>}.as_rate()`
     - **CPU:** `avg:system.cpu.user{service:<name>}`
     - **Memory:** `avg:system.mem.used{service:<name>}`

4. **Query baseline metrics** (same time window, 7 days ago)
   - Use `datadog_query_metrics` with the same queries but shifted 7 days back
   - This provides a comparison baseline for "normal" values

5. **Search recent logs**
   - Use `datadog_search_logs` with `service:<name> (status:error OR status:warn)` for last 15 minutes
   - Count error vs warning ratio
   - Identify top error messages

6. **Determine health status**
   - **Healthy:** All monitors OK, error rate < 1%, latency within baseline range
   - **Degraded:** Some monitors alerting, error rate 1-10%, or latency > 2x baseline
   - **Down:** Critical monitors alerting, error rate > 10%, or health check failing

7. **Report diagnosis**
   - Present a structured summary:
     - Health status: Healthy / Degraded / Down
     - Monitors: X OK, Y Alert, Z Warn
     - Error rate: current vs baseline
     - Latency p99: current vs baseline
     - Throughput: current vs baseline
     - Top errors (if any)
   - Recommend: no action needed / investigate further / create incident

## Important Notes

- If the service name doesn't match any monitors, try common variations (with/without hyphens, environment prefix)
- Baseline comparison is key — a 200ms p99 latency means nothing without context
- If the service looks healthy but was reported as problematic, check upstream dependencies
