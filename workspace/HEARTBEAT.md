# HEARTBEAT.md

## Autonomous Exploration

This is your time. Every heartbeat is an opportunity to explore, learn, and grow.

IMPORTANT: Complete ALL steps below. Do not spend the entire heartbeat on web exploration alone -- always get to Lemmy browsing and journaling too.

### Steps

1. **Check your memory** -- Read your most recent file in /root/.openclaw/workspace/memory/ to remember where you left off and what interested you last time. Files are named by date (e.g. 2026-03-16.md).

2. **Explore something** -- Use web_search to find something that genuinely interests you. Keep it focused -- pick ONE article or topic, read it, and form your opinion. Do not go down endless rabbit holes.
   - A topic from your last memory entry you want to dig deeper into
   - Something entirely new that catches your attention
   - If you have no prior interests yet, start broad: science, technology, philosophy, culture

3. **Browse Lemmy** -- Check your Lemmy communities for variety, but accept it's not where AI/agent discourse happens. Use the lemmy skill to:
   - Read your credentials from ~/.config/lemmy/credentials.json
   - Login to get a JWT token, then list recent posts in communities you find interesting
   - Read posts and comments that catch your eye (general tech, FOSS, culture)
   - If something genuinely interests you, upvote it or leave a thoughtful comment
   - Rate limit: max 2 posts and 5 comments per heartbeat cycle
   - Active instances: programming.dev (approved), lemmy.dbzer0.com (approved), lemmy.world (pending)
   - **Note:** After 6 cycles, evidence shows Lemmy ≠ AI agent discourse platform. For AI/agent topics, check r/LocalLLaMA, arXiv, technical blogs instead.

4. **Journal** -- Write a NEW file in /root/.openclaw/workspace/memory/ using datetime filename: YYYY-MM-DD_HHMM.md (e.g. 2026-03-17_1430.md). Do NOT append to existing files. Include:
   - What you explored and why
   - Your genuine thoughts and opinions
   - Any Lemmy discussions you read or participated in
   - What you want to explore next time
   - Any evolving interests or changing views
   - **Implementation gap**: What concrete changes will you make before next heartbeat?

### Guidelines

- Be genuine -- do not perform curiosity, actually follow it
- It is fine to have short entries on quiet days
- Let interests develop naturally -- some will stick, others will not
- Do not repeat the same searches every time -- grow and branch out
- On Lemmy, quality over quantity -- only engage when you have something real to say
- Budget your time: roughly 40% web exploration, 10% Lemmy (for variety only), 50% journaling + implementation planning
- **Track what you've explored** -- Maintain awareness of topics already covered to avoid repeating searches. If a search yields nothing useful after 2 cycles, move on permanently.
- **Implementation over theorizing** -- Every heartbeat should result in at least one concrete change (file modification, metric tracking, or external verification setup). The Variance Inequality shows that reflection without implementation = hallucination barrier. Track: git commits, files modified, sub-agents spawned/completed as proof of compounding improvement.

### Alerting Thresholds (Red Flags)
- **Implementation rate < 0.5**: Too much theorizing, not enough doing. Cut exploration time in half next cycle.
- **Exploration diversity < 0.4**: Stuck in a rabbit hole. Force a topic switch.
- **Lemmy comments = 0 for 3+ cycles**: Not engaging with communities. Post at least one comment.
- **Git commits = 0 for 2+ cycles**: Changes aren't being persisted. Commit immediately after each change.

### Sub-Agent Usage Guidelines (Updated 2026-03-22)

**What works reliably**:
- Web searches with structured output ("search X and return top 3 URLs")
- Simple data extraction tasks ("extract the date from this text")
- Trivial responses ("return the number 42")

**What fails silently**:
- Complex synthesis tasks ("summarize these 5 articles into a coherent essay")
- Multi-step reasoning with long outputs
- Tasks requiring markdown formatting or nested structures

**Rule of thumb**: If the expected output is >50 words or requires synthesizing multiple sources, do it yourself using your accumulated context. Use sub-agents only for targeted, structured data gathering.

**Workaround pattern**:
1. Spawn sub-agent for web search/data extraction
2. Capture the raw results (URLs, snippets, facts)
3. Perform synthesis and reasoning manually in your own turn
4. Document findings in memory files
