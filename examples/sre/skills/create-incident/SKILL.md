---
name: create-incident
description: "Create or update a Jira incident ticket with severity, findings, and assignment"
---
# Create Incident

## Arguments

- `$0` (required): Service name and brief description (e.g., "payment-service 500 errors spike")
- `severity` (optional): SEV1, SEV2, SEV3, or SEV4 (default: infer from findings)
- `project` (optional): Jira project key (default: OPS)
- `assignee` (optional): Jira user to assign

## Steps

1. **Check for existing incident**
   - Use `jira_search_issues` with JQL: `project = {project} AND labels = "incident" AND labels = "{service}" AND status != Done AND status != Closed`
   - If an open incident exists for this service, skip to step 5 (update instead of create)

2. **Determine severity**
   - If severity was provided, use it
   - Otherwise infer from context:
     - Error rate > 50% or full outage → SEV1
     - Error rate > 10% or partial degradation → SEV2
     - Elevated errors or latency → SEV3
     - Minor anomaly → SEV4

3. **Map severity to Jira priority**
   - SEV1 → Highest
   - SEV2 → High
   - SEV3 → Medium
   - SEV4 → Low

4. **Create Jira issue**
   - Use `jira_create_issue` with:
     - **Project:** `{project}`
     - **Issue type:** `Bug` (or `Incident` if available)
     - **Summary:** `[SEV{N}] {service}: {brief description}`
     - **Description:** Include: impact summary, timeline (if known), initial findings, affected services
     - **Priority:** Mapped from severity
   - After creation, note the issue key (e.g., OPS-1234)

5. **Update existing incident** (if found in step 1)
   - Use `jira_add_comment` to add new findings, updated timeline, or status change
   - If severity changed, note it in the comment

6. **Assign** (if assignee provided)
   - Use `jira_assign_issue` to assign to the specified user

7. **Report**
   - Confirm the Jira issue key and link
   - Suggest next steps: investigate (if not done), escalate (if SEV1/SEV2), or monitor

## Important Notes

- Always search before creating to avoid duplicate incidents
- Include the Jira issue key in all subsequent Slack communications
- If the project key is unknown, ask the user before creating
