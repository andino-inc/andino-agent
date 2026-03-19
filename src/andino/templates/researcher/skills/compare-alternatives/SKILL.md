---
name: compare-alternatives
description: "Structured comparison of technologies or approaches with evaluation matrix and trade-off analysis"
---
# Compare Alternatives

## Arguments

- `$0` (required): What to compare (e.g., "Redis vs Memcached vs DynamoDB for session storage", "REST vs GraphQL vs gRPC for our API")
- `criteria` (optional): Specific evaluation criteria to prioritize (e.g., "latency, cost, team experience")

## Steps

1. **Parse the comparison**
   - Identify the alternatives to compare (2-4 options)
   - Understand the use case / context for the decision
   - If criteria were provided, use them; otherwise define criteria in step 2

2. **Define evaluation criteria**
   - Select 5-8 criteria relevant to the decision. Common ones:
     - **Performance**: latency, throughput, scalability
     - **Developer experience**: learning curve, documentation, ecosystem
     - **Operational**: hosting, monitoring, maintenance, cost
     - **Maturity**: community size, adoption, release stability
     - **Fit**: integration with existing stack, team skills, licensing
   - Weight criteria: Critical / Important / Nice-to-have

3. **Research each alternative**
   - For each option, use `http_request` to gather:
     - Official documentation / getting started guide
     - Performance benchmarks (from reputable sources)
     - Known limitations and gotchas
     - Pricing model (if applicable)
   - Check Confluence for any internal experience: `confluence_search`

4. **Build comparison matrix**
   - Score each alternative against each criterion
   - Use concrete evidence, not feelings
   - Note the source for each score

5. **Analyze trade-offs**
   - What do you gain with each option?
   - What do you lose or risk?
   - Are there migration paths between options?
   - What's the long-term trajectory of each? (growing, stable, declining)

6. **Formulate recommendation**
   - Based on the weighted matrix, which option wins?
   - Is the winner clear or is it a close call?
   - Under what conditions would a different option be better?

7. **Write comparison report**
   - Use `file_write` to save to workspace as `comparison_{topic_slug}.md`
   - Use the Comparison Matrix format from the system prompt
   - Include the full matrix table, trade-offs, and recommendation

8. **Report summary**
   - Present the recommendation with top 3 reasons
   - Highlight the key trade-off the decision-maker should be aware of

## Important Notes

- Never recommend a technology just because it's popular — evaluate against the specific use case
- If the team already has experience with one option, weight that heavily (operational cost matters)
- Look for benchmarks from independent sources, not vendor marketing
- If two options are too close to call, say so and explain what additional information would break the tie
