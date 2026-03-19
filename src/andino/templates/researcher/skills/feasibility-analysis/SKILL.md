---
name: feasibility-analysis
description: "Evaluate technical viability of a proposed feature or change with risks, effort estimate, and go/no-go recommendation"
---
# Feasibility Analysis

## Arguments

- `$0` (required): The proposal to evaluate (e.g., "Add real-time notifications via WebSockets", "Migrate from PostgreSQL to DynamoDB")
- `repo` (optional): Repository to analyze for the assessment (GitHub URL or org/repo)

## Steps

1. **Understand the proposal**
   - Break down what's being proposed into concrete requirements
   - Separate functional requirements (what it does) from non-functional (performance, security, scalability)
   - Identify assumptions — what's being taken for granted?

2. **Analyze the current state** (if repo provided)
   - Use the **explore-codebase** skill to understand the existing architecture
   - Identify which modules would be affected
   - Check for existing patterns that could be leveraged

3. **Research existing solutions**
   - Use `http_request` to find how others have solved similar problems
   - Look for libraries, frameworks, or services that address the need
   - Check if there are standard patterns or best practices

4. **Evaluate technical feasibility**
   - Can it be done with the current tech stack?
   - Does it require new infrastructure or services?
   - Are there hard technical blockers? (API limitations, platform constraints, data model incompatibilities)
   - How does it interact with existing features?

5. **Identify risks**
   - For each risk, assess:
     - **Likelihood**: High / Medium / Low
     - **Impact**: High / Medium / Low
     - **Mitigation**: What can be done to reduce the risk?
   - Common risk categories: performance degradation, data migration, backward compatibility, security, vendor lock-in

6. **Estimate effort**
   - Break into phases if large
   - For each phase: scope, dependencies, estimated effort (hours/days/weeks)
   - State assumptions clearly (e.g., "assumes team has experience with X")
   - Flag unknowns that could significantly change the estimate

7. **Evaluate constraints**
   - Time: Is there a deadline? Is the estimate compatible?
   - Cost: New services, licenses, infrastructure?
   - Team: Does the team have the required skills?
   - Dependencies: Are there external blockers?

8. **Write feasibility report**
   - Use `file_write` to save as `feasibility_{proposal_slug}.md`
   - Use the Feasibility Report format from the system prompt
   - Include clear verdict: Feasible / Partially Feasible / Not Feasible

9. **Report verdict**
   - Present the verdict with top 3 supporting reasons
   - If partially feasible, explain what's needed to make it fully feasible
   - If not feasible, suggest alternatives

## Important Notes

- "Not feasible" is a valid and valuable answer — don't stretch to make everything work
- Effort estimates should include ranges (optimistic / realistic / pessimistic)
- If the proposal is vague, ask clarifying questions before analyzing
- Consider the opportunity cost — what else could the team work on instead?
- Always separate "technically possible" from "practically advisable"
