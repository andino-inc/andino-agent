---
name: investigate-incident
description: "Full incident investigation — correlate logs, metrics, traces, and events to build a timeline and identify root cause"
---
# Investigate Incident

## Arguments

- `$0` (required): Alert name, service name, or description of the issue (e.g., "payment-service high error rate", "monitor XYZ triggered")

## Steps

1. **Identify the affected service and timeframe**
   - Parse the alert/description to determine which service is affected
   - Set investigation window: last 30 minutes from now (expand if needed)

2. **Check active monitors**
   - Use `datadog_list_monitors` to find monitors related to the service
   - Use `datadog_get_monitor` on any alerting monitors to get details and thresholds
   - Note which monitors are in Alert or Warn state

3. **Search error logs**
   - Use `datadog_search_logs` with query `service:<name> status:error` for the last 30 minutes
   - Look for patterns: repeated error messages, new error types, sudden spikes
   - Note the first occurrence timestamp — this helps establish the incident start

4. **Query key metrics**
   - Use `datadog_query_metrics` for each of these (last 30 minutes):
     - Error rate: `sum:trace.http.request.errors{service:<name>}.as_rate()`
     - Latency p99: `p99:trace.http.request.duration{service:<name>}`
     - Request throughput: `sum:trace.http.request.hits{service:<name>}.as_rate()`
     - CPU: `avg:system.cpu.user{service:<name>}`
     - Memory: `avg:system.mem.used{service:<name>}`
   - Compare current values against what looks normal (beginning of the window vs peak)

5. **Search error traces**
   - Use `datadog_search_traces` with `service:<name> status:error`
   - Identify the most common error spans — resource name, error message, duration
   - Look for upstream/downstream dependencies failing

6. **Check recent events**
   - Use `datadog_list_events` for the last 2 hours
   - Look for: deployments, config changes, scaling events, infrastructure changes
   - Correlate event timestamps with when errors started

7. **Build timeline**
   - Correlate all findings into a chronological timeline
   - Identify the trigger event (deploy, traffic spike, dependency failure, etc.)
   - Determine severity based on impact (error rate, duration, user-facing)

8. **Write investigation report**
   - Use `file_write` to save findings to workspace as `{service}_investigation_{timestamp}.md`
   - Follow the Investigation Report Format from the system prompt
   - Include: timeline, impact, root cause analysis, evidence, recommended actions

9. **Report findings**
   - Summarize the investigation in the conversation
   - Recommend next steps: create incident (if not exists), escalate (if high severity), or monitor (if resolving)

## Important Notes

- If the initial 30-minute window doesn't show the start of the issue, expand to 1 hour or 2 hours
- If the service name is ambiguous, check monitors first to identify the exact service tag
- Always check for recent deployments — they are the most common cause of incidents
- If you find a dependency failure, investigate that service too (recursive diagnosis)
