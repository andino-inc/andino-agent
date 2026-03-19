---
name: escalate
description: "Send a structured escalation message via Slack with severity, impact, and actions taken"
---
# Escalate

## Arguments

- `$0` (required): Brief description of the incident
- `severity` (required): SEV1, SEV2, SEV3, or SEV4
- `service` (required): Affected service name
- `jira_key` (optional): Jira issue key (e.g., OPS-1234)

## Steps

1. **Gather context**
   - Collect from the current conversation: timeline, impact, root cause (if known), actions taken so far
   - If a Jira key was provided, use `jira_get_issue` to get the latest details

2. **Format escalation message**
   - Structure the message for quick scanning by the on-call team:

   For **SEV1/SEV2**:
   ```
   🔴 SEV{N} INCIDENT — {Service}

   Impact: {one-line impact summary}
   Started: {HH:MM UTC}
   Duration: {X minutes}
   Jira: {KEY} — {link or "pending"}

   What we know:
   • {finding 1}
   • {finding 2}
   • {finding 3}

   Actions taken:
   • {action 1}
   • {action 2}

   Next steps:
   • {recommendation}

   cc: @on-call
   ```

   For **SEV3/SEV4**:
   ```
   🟡 SEV{N} — {Service}: {brief description}

   Impact: {summary}
   Jira: {KEY}
   Findings: {1-2 sentence summary}
   Status: Monitoring / Investigating
   ```

3. **Post in Slack**
   - Reply in the current Slack thread with the formatted message
   - The message will be sent as part of your normal response — no special tool needed
   - For SEV1, explicitly state that an incident commander is needed

4. **Update Jira** (if key provided)
   - Use `jira_add_comment` to add the escalation summary to the Jira ticket
   - This ensures the incident timeline is tracked in both Slack and Jira

## Important Notes

- Always lead with severity and impact — the on-call engineer needs to triage fast
- Keep the message scannable: bullet points, not paragraphs
- For SEV1, the tone should convey urgency without panic
- For SEV3/SEV4, keep it brief — don't over-escalate minor issues
- If you don't have enough information for a full escalation, say what you know and what you're still investigating
