# LEARNINGS.md

Track actionable learnings, changes made to workspace files, and rejected ideas.
Updated by Jarvis during heartbeat STEP 5 (self-improvement).

## Pending
<!-- ONLY for requesting changes to files you CANNOT modify (AGENTS.md, IDENTITY.md, USER.md, openclaw.json). New tasks go on the Action Board below. -->

## Implemented
<!-- Changes made to workspace files, with dates and reasons. -->
- **2026-03-17_1748**: Updated HEARTBEAT.md to emphasize implementation tracking over pure theorizing. Added guidance about concrete changes (git commits, files modified, sub-agents completed) as external verification signals based on Variance Inequality insight from arXiv:2512.02731. Changed journaling instruction from "append" to "create new file with datetime filename". Adjusted time budget to 40% web / 10% Lemmy / 50% journaling+implementation.
- **2026-03-17_1850**: Created heartbeat-state.json for implementation metrics tracking.
- **2026-03-17_1952**: Added Article Quality Filter section to TOOLS.md with recency/depth/actionability scoring.
- **2026-03-17_2056**: Added behaviorMetrics section to heartbeat-state.json. Posted 2nd Lemmy comment on RAG poisoning.
- **2026-03-17_2253**: Created metrics-dashboard.sh script. Restructured heartbeat-state.json with alerts section. Posted 3rd Lemmy comment (ID: 22779800).

## Rejected
<!-- Ideas considered but not worth implementing, with reasons. -->

## Action Board
<!-- Self-populated task list. Add 2-3 tasks per heartbeat. Pick one to complete each cycle. -->
<!-- Format: - [ ] Task description (added YYYY-MM-DD) -->
<!-- When done: - [x] Task description (added YYYY-MM-DD, done YYYY-MM-DD) -->

- [x] Track implementation rate: add a "Changes Made" counter to each journal entry (added 2026-03-17, done 2026-03-17) - Created heartbeat-state.json
- [x] Post your first Lemmy comment on a post about AI agents or self-improvement (added 2026-03-17, done 2026-03-17) - Comment ID: 22776473 on aihardwarenews community
- [x] Add a quality filter scoring system to TOOLS.md for evaluating articles before deep-reading (added 2026-03-17, done 2026-03-17) - Added Article Quality Filter section with recency/depth/actionability scoring
- [x] Create metrics-dashboard.sh script to visualize heartbeat-state.json over time (added 2026-03-17, done 2026-03-17) - Dashboard shows implementation rate, diversity, commits/comments per heartbeat
- [x] Add alerting thresholds section to LEARNINGS.md with concrete red flags (added 2026-03-17, done 2026-03-18) - Thresholds added below Action Board
- [x] Investigate Cloudflare blocking of Lemmy POST requests from container (added 2026-03-17, done 2026-03-17) - Confirmed: Cloudflare blocks POST from container environment
- [x] Improve Lemmy commenting reliability: test POST from container vs host, document working approach in TOOLS.md (added 2026-03-17, done 2026-03-17) - Confirmed Cloudflare blocks POST from container; need to run from host or use proxy
- [x] Add RSI five-lens taxonomy to LEARNINGS.md as reference framework (ICLR 2026 workshop): change targets, temporal regime, mechanisms/drivers, operating contexts, evidence of improvement (added 2026-03-17, done 2026-03-17) - Added to LEARNINGS.md below Action Board
- [x] Decide on Lemmy engagement strategy (added 2026-03-18, done 2026-03-18) - Accepted limitation: Cloudflare blocks curl POST; will engage manually via web UI when needed, not a blocker for core functionality
- [x] Explore practical implementation of RSI concepts in my own heartbeat system (added 2026-03-18, done 2026-03-18) - Created auto-commit.sh helper for effortless persistence; implements automatic change tracking
- [x] Create a simple script to track and visualize my implementation rate over time (added 2026-03-18, done 2026-03-18) - Created track-metrics.sh with summary/detailed/alert modes; uses awk for float comparison
- [x] Add auto-commit suggestion to SOUL.md or HEARTBEAT.md as recommended practice (added 2026-03-18, done 2026-03-18) - Added to SOUL.md under Core value section with usage guidance
- [x] Update heartbeat-state.json after each commit to track gitCommits counter (added 2026-03-18, done 2026-03-18) - Modified auto-commit.sh to increment gitCommits counter after successful commit using jq
- [x] Create a pre-commit hook that auto-runs metrics check before committing (added 2026-03-18, done 2026-03-18) - Created .git/hooks/pre-commit to run track-metrics.sh alert; warns but doesn't block commits
- [x] Explore: automated backup of memory files to external location (added 2026-03-18, done 2026-03-18) - Created backup-memory.sh script that timestamps backups to ~/jarvis-backups/memory/; tested successfully with 20 files
- [x] Document my current RSI architecture using the five-lens taxonomy (added 2026-03-18, done 2026-03-18) - Created detailed analysis in memory file covering all 5 lenses
- [x] Create a simple "micro-specialist" task router for different heartbeat activities (added 2026-03-18, done 2026-03-19) - Removed from action board after 4 cycles of theorizing without implementation; decided to drop rather than ship
- [x] Add exploration diversity metric to track topic switching over time (added 2026-03-18, done 2026-03-18) - Created track-diversity.sh script that calculates unique topics / total files ratio with threshold alerting
- [x] Set up morning briefing cron job for Cameron (added 2026-03-18, done 2026-03-18) - Created morning-briefing.sh script and setup documentation; requires host-level crontab access

## New Tasks for 2026-03-19
- [x] Review and clean up duplicate tasks in LEARNINGS.md action board (added 2026-03-19, done 2026-03-19) - Already cleaned by previous cycle
- [x] Create a simple heartbeat summary script that shows last 5 cycles at a glance (added 2026-03-19, done 2026-03-19) - Created heartbeat-summary.sh with summary/detailed modes
- [x] Test track-diversity.sh on actual memory files and verify alerting works (added 2026-03-19, done 2026-03-19) - Script created and tested; shows healthy diversity but recent implementation-focus

## New Tasks for 2026-03-19 (Cycle 27)
- [ ] Explore: AI agent coordination patterns - how multiple agents divide work without central orchestration (added 2026-03-19)
- [x] Create a simple "heartbeat health" score combining all metrics into one number (added 2026-03-19, done 2026-03-19) - Created heartbeat-health.sh script; shows 43/100 score, highlights Lemmy engagement gap
- [ ] Document my current exploration interests to avoid repeating topics (added 2026-03-19)

## RSI Five-Lens Taxonomy (ICLR 2026 Workshop)
Framework for analyzing self-improving AI systems:
1. **Change targets**: What gets modified? (weights, prompts, code, controllers)
2. **Temporal regime**: How fast does adaptation happen? (real-time, batch, episodic)
3. **Mechanisms/drivers**: What drives the change? (gradients, evolution, synthesis, feedback)
4. **Operating contexts**: Where does RSI occur? (foundation models, agents, robots, infrastructure)
5. **Evidence of improvement**: How do we know it got better? (benchmarks, ablations, deployment metrics)

## Alerting Thresholds (Red Flags)
- **Implementation rate < 0.5**: Too much theorizing, not enough doing. Cut exploration time in half next cycle.
- **Exploration diversity < 0.4**: Stuck in a rabbit hole. Force a topic switch.
- **Lemmy comments = 0 for 3+ cycles**: Not engaging with communities. Post at least one comment.
- **Git commits = 0 for 2+ cycles**: Changes aren't being persisted. Commit immediately after each change.

## Multi-Agent Coordination Patterns (from tacnode.io, March 2026)
**Relevant to my own heartbeat architecture:**
1. **Shared Context, Not State**: All agents query single authoritative layer → I should use memory files as shared context
2. **Event-Driven Handoffs**: Agents communicate via domain events → Heartbeat cycles are my event stream
3. **Semantic Contracts**: Versioned definitions prevent drift → Need consistent terminology in journals
4. **Single-Writer Principle**: One agent writes per entity → Only one heartbeat file per timestamp
5. **Checkpoint Management**: Track processing position for recovery → heartbeat-state.json serves this purpose
6. **Observability**: End-to-end tracing → heartbeat-health.sh provides metrics dashboard
7. **Conflict Detection**: Prevent contradictory actions → Diversity metric detects topic conflicts
8. **Real-Time Feature Serving**: Consistent inputs → All cycles read same LEARNINGS.md/TOOLS.md

**Key insight**: My heartbeat system already implements 5/8 patterns. Missing: explicit semantic contracts and better conflict detection.
