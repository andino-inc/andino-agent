---
name: write-brief
description: "Synthesize research findings into a formal brief saved to the workspace"
---
# Write Brief

## Arguments

- `$0` (required): Brief title or topic (e.g., "Kafka Consumer Rebalancing", "API Gateway Selection")
- `type` (optional): Brief type — "research" (default), "comparison", or "feasibility"

## Steps

1. **Gather findings**
   - Collect all research findings from the current conversation
   - Check workspace for any existing partial reports from other skills
   - Organize findings by theme

2. **Select template**
   - **research**: Technical Brief (findings + recommendations)
   - **comparison**: Comparison Matrix (alternatives + trade-offs + recommendation)
   - **feasibility**: Feasibility Report (requirements + risks + effort + verdict)

3. **Write executive summary**
   - 2-3 sentences maximum
   - Answer: what was investigated, what was found, what's recommended
   - This should be readable by someone who won't read the full brief

4. **Structure the body**
   - Follow the appropriate template from the system prompt
   - Use concrete evidence — link to sources, reference file paths, cite metrics
   - Use bullet points for scanability
   - Bold key findings so they stand out when skimming

5. **Add sources section**
   - List all URLs, documentation pages, and files referenced
   - Include date accessed for web sources
   - Note any internal Confluence pages referenced

6. **Save to workspace**
   - Use `file_write` to save as `brief_{topic_slug}.md` in the workspace directory
   - If the workspace path is known, use absolute path

7. **Optionally publish to Confluence**
   - If the user requested it, use `confluence_create_page` to publish the brief
   - Ask which space to publish to if not specified

8. **Report**
   - Confirm the brief was saved with the file path
   - Present the executive summary in the conversation

## Important Notes

- The brief should be self-contained — readable without context from the conversation
- Keep it concise: 1-3 pages maximum for research briefs, 1-2 for comparisons
- Use markdown formatting that renders well in both terminal and web viewers
- Don't include raw data dumps — synthesize and summarize
