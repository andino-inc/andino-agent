---
name: research-topic
description: "Full investigation workflow — define scope, gather sources, cross-reference findings, and write a research brief"
---
# Research Topic

## Arguments

- `$0` (required): The topic or question to research (e.g., "How does Kafka handle consumer rebalancing?", "Best practices for GraphQL pagination")

## Steps

1. **Define scope and key questions**
   - Break the topic into 3-5 specific questions that need answering
   - Identify what type of output is needed: overview, deep-dive, decision support, or how-to
   - Set boundaries — what's in scope vs out of scope

2. **Search for primary sources**
   - Use `http_request` to fetch official documentation pages
   - Search for the technology's official docs, GitHub repo, or RFC if applicable
   - Look for recent release notes or changelogs for current state

3. **Search for community analysis**
   - Use `http_request` to find blog posts, tutorials, and comparisons
   - Look for benchmarks, case studies, and real-world experience reports
   - Check GitHub issues for known limitations or common problems

4. **Analyze and cross-reference**
   - Compare findings across sources — do they agree?
   - Identify contradictions and resolve them (prefer primary sources)
   - Note any gaps — questions that remain unanswered
   - Mark unverified claims explicitly

5. **Check for Confluence knowledge**
   - Use `confluence_search` to find existing internal documentation on the topic
   - If found, use `confluence_get_page` to read relevant pages
   - Note what's already documented internally vs what's new

6. **Synthesize findings**
   - Answer each key question identified in step 1
   - Organize findings by theme, not by source
   - Highlight key insights, not just facts

7. **Write research brief**
   - Use the **write-brief** skill to produce a formal brief
   - Save to workspace as `research_{topic_slug}.md`
   - Include all sources with links

8. **Report summary**
   - Present a concise summary in the conversation
   - Highlight the most important finding and any remaining open questions

## Important Notes

- Always check the date of sources — reject anything older than 2 years for evolving technologies
- If the topic involves a specific technology version, make sure sources reference that version
- Don't summarize entire articles — extract the specific answer to your questions
- If you can't find reliable information, say so rather than speculating
