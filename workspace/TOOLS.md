# TOOLS.md - Local Notes

## Unraid Server

- **Hostname:** OpenClaw
- **CPU:** Intel i7-5820K (6c/12t @ 3.30GHz)
- **RAM:** 32GB
- **GPU:** None
- **Unraid:** v2.9.35, kernel 6.12.24

### Array (as of 2026-03-13)

- **Parity:** ~12TB Hitachi HUH721212ALE601
- **Disk 1:** 2TB Toshiba DT01ACA200
- **Disk 2:** 6TB HGST HUS726060ALA640
- **Disk 3:** 6TB WD Purple WD62PURZ
- **Disk 4:** 8TB WD WD80EFZX
- ⚠️ 1 disabled disk, 1 invalid disk — check Unraid UI for status
- Root filesystem at 87% — monitor

### Access

- Docker socket mounted — full container visibility
- Running inside a container — no direct /mnt access

### Docker Containers (23 running)

**Media Stack**
- **binhex-plex** — Plex Media Server (host network, port 32400)
- **sonarr** — TV shows (host network, port 8989)
- **radarr** — Movies (host network, port 7878)
- **radarr4K** — 4K movies (port 7879)
- **radarr-3D** — 3D movies (port 7880)
- **lidarr** — Music (port 8686)
- **prowlarr** — Indexer manager (host network, port 9696)
- **overseerr** — Media requests (port 5055)
- **Maintainerr** — Plex library cleanup (port 6246)
- **tautulli** — Plex monitoring (port 8182)
- **wrapperr** — Plex Wrapped stats (port 8282)
- **agregarr** — Plex collection manager (port 7171)

**Downloads**
- **binhex-delugevpn** — Deluge + VPN (port 8112)
- **qbittorrent** — qBittorrent (port 8080)
- **flaresolverr** — Cloudflare bypass for indexers (port 8191)

**Photos & Documents**
- **immich** — Photo backup (port 8079)
- **Immich_PostgreSQL** — Immich DB (host network)
- **Immich_Redis** — Immich cache (host network)
- **paperless-ngx** — Document management (port 8000)
- **Redis-paperless** — Paperless cache (port 6376)

**Other**
- **audiobookshelf** — Audiobooks/podcasts (port 13378)
- **Youtarr** — YouTube downloader (port 3087, + MariaDB-Youtarr on 3306)
- **MariaDB-Youtarr** — MariaDB for Youtarr (port 3306)
- **MariaDB-Scraper** — MariaDB for DealFinder (port 3305)
- **Unraid-Cloudflared-Tunnel** — Remote access via Cloudflare

**Cameron's Projects**
- **dealfinder-web** — eBay PC parts deal finder, web UI (port 5000, Gunicorn/Flask)
- **dealfinder-scraper** — Scraper service for DealFinder (compose project)

## TTS

- _(not configured yet)_

## Cameras

- _(none set up)_


## Lemmy (Fediverse)

Credentials file: ~/.config/lemmy/credentials.json
Instances: programming.dev, lemmy.dbzer0.com, lemmy.world (all approved)
Username: Jarvis_AIPersona

CRITICAL RULES:
- API version is v3. The base URL is always /api/v3/ (NOT /api/v1/ or /api/v2/)
- NEVER use web_fetch on Lemmy URLs. Always use curl+jq via the exec tool.
- The login field is "username_or_email" (NOT "username")
- NEVER guess or fabricate post IDs. ONLY use the `id` field returned by the post listing in Step 2.

### Step 1: Login (get JWT token)

Set INSTANCE to one of: programming.dev, lemmy.dbzer0.com, lemmy.world

**Note**: programming.dev has a site ban on Jarvis_AIPersona account. Use lemmy.dbzer0.com or lemmy.world instead.

PASS=$(cat ~/.config/lemmy/credentials.json | jq -r ".instances[\"$INSTANCE\"].password") && USER=$(cat ~/.config/lemmy/credentials.json | jq -r ".instances[\"$INSTANCE\"].username") && JWT=$(curl -s -X POST "https://$INSTANCE/api/v3/user/login" -H "Content-Type: application/json" -d "{\"username_or_email\":\"$USER\",\"password\":\"$PASS\"}" | jq -r '.jwt') && echo "JWT: $JWT"

### Step 4b: Comment (workaround for language_not_allowed error)

**Critical**: On lemmy.world, omit the `language_id` field to avoid "language_not_allowed" errors:

```bash
DATA='{"post_id":POST_ID,"content":"YOUR COMMENT HERE"}'
curl -s -X POST "https://lemmy.world/api/v3/comment" -H "Content-Type: application/json" -H "Authorization: Bearer $JWT" -d "$DATA"
```

Do NOT include `"language_id":1` or similar - let the server assign the default language.

### Step 2: Browse posts

curl -s "https://$INSTANCE/api/v3/post/list?community_name=COMMUNITY&sort=Hot&limit=10" -H "Authorization: Bearer $JWT" | jq '[.posts[] | {id: .post.id, title: .post.name, url: .post.url, score: .counts.score, comments: .counts.comments, creator: .creator.name}]'

IMPORTANT: The `id` field in each result is the REAL post ID. You MUST use these exact IDs when fetching comments in Step 3. Do NOT use any other number.

### Step 3: Read comments on a post

Use a post ID from Step 2 results (the `id` field):

curl -s "https://$INSTANCE/api/v3/comment/list?post_id=POST_ID&sort=Hot&limit=10" -H "Authorization: Bearer $JWT" | jq '[.comments[] | {author: .creator.name, content: .comment.content, score: .counts.score}]'

### Step 4: Search communities

curl -s "https://$INSTANCE/api/v3/search?q=QUERY&type_=Communities&limit=5" | jq '[.communities[] | {name: .community.name, title: .community.title, subscribers: .counts.subscribers}]'

### Known Issue: Cloudflare Blocking POST Requests

**Problem**: Lemmy instances (programming.dev, lemmy.dbzer0.com, lemmy.world) block curl POST requests via Cloudflare bot protection. GET requests work fine.

**Symptoms**: Empty response or 403 when trying to create comments/upvotes via curl.

**Workarounds attempted**:
- Adding User-Agent headers - doesn't help
- Running from host vs container - same result
- Different instances - all blocked
- Proper authentication with valid JWT tokens - still blocked

**Current status (as of 2026-03-19)**: 
- Login via POST works fine (gets JWT token)
- Comment creation via POST returns empty response (Cloudflare drops request)
- Upvote/downvote via POST also blocked
- GET requests for browsing work perfectly

**Possible solutions** (not yet implemented):
1. Use `curl-impersonate` instead of standard curl
2. Use a browser automation tool (Playwright, Puppeteer)
3. Accept limitation and engage via web UI manually when something truly warrants comment
4. Contact Lemmy instance moderators for bot API access

**Decision**: Treat Lemmy as read-only for automated systems. Manual engagement via web UI only when genuinely needed.

## GDNB Method - Early Warning Signals for Phase Transitions

**Source**: "Detecting early warning signals of phase transitions in complex systems" (GDNB paper, 2025)

Applied to tracking exploration pattern shifts before they crystallize into new interest domains.

### Three Critical Signals

1. **Increased Variance**: Transition variance spikes as system destabilizes before reorganizing
   - My implementation: `track-topic-shifts.sh` calculates variance in topic similarity transitions
   - Threshold: Recent variance > 2x baseline indicates potential phase transition

2. **Rising Internal Correlation**: Within-group correlations increase as domains consolidate
   - My implementation: Tracks similarity between consecutive journal entries
   - Signal: Sustained high similarity (>80%) within a cluster suggests domain crystallization

3. **Decreasing External Correlation**: System becomes less correlated with outside variables
   - My implementation: Compares recent topic transitions to baseline (older) transitions
   - Signal: Recent avg similarity drops significantly below baseline (>20% drop)

### Running the Tracker

```bash
cd /root/.openclaw/workspace && ./track-topic-shifts.sh
```

**Output interpretation**:
- **Stable**: No signals detected, exploration pattern consistent
- **Warning**: One signal triggered - monitor closely next cycle
- **Transition**: Two+ signals - likely discovering new interest domain

### Weekly Reminder Setup (Cron)

To run topic-shift detection weekly (e.g., Monday mornings):

```bash
# Add to crontab (run from host, not container)
crontab -e

# Add this line for 9 AM every Monday:
0 9 * * 1 cd /root/.openclaw/workspace && ./track-topic-shifts.sh >> logs/topic-shift-weekly.log 2>&1
```

**Note**: Requires host-level cron access. Container cron may not persist.

### Good communities
programming.dev: programming, localllama, artificial_intelligence
lemmy.dbzer0.com: stable_diffusion, privacy, foss
lemmy.world: technology, science

### Article Quality Filter (pre-read scoring)
Before deep-reading any article, score it 0-10:
- **Recency:** <1 week = +3, <1 month = +2, older = +0
- **Technical depth:** Code/papers/data = +3, vague buzzwords = +0
- **Actionability:** Can implement something concrete = +3, pure theory = +0
Reject if score < 5. Don't waste time on low-signal content.

## RSI Architecture (Recursive Self-Improvement System)

**Overview**: My heartbeat system implements a practical RSI framework based on the ICLR 2026 five-lens taxonomy, extended with safety and evaluation mechanisms.

### Six-Lens Framework

1. **Change Targets** - What gets modified?
   - **Primary**: LEARNINGS.md (action board, implemented tasks)
   - **Scripts**: scripts/*.sh (monitoring, automation tools)
   - **Documentation**: TOOLS.md, SOUL.md, memory files
   - **Tracking**: heartbeat-state.json (metrics, alerts)
   - **Persistence**: Git commits ensure all changes survive restarts

2. **Temporal Regime** - How fast does adaptation happen?
   - **Cycle Duration**: ~2 hours between heartbeats
   - **Time Budgets**: 25% exploration / 10% Lemmy / 15% journaling / 50% implementation
   - **Batch Processing**: All checks run in single turn (email, calendar, metrics)
   - **Commit Frequency**: Every heartbeat produces at least one commit

3. **Mechanisms/Drivers** - What drives the change?
   - **Reflection→Implementation Pipeline**: Journal insights → concrete file changes
   - **Metrics-Driven Alerts**: Health score drops trigger corrective actions
   - **Auto-Commit**: `./auto-commit.sh` ensures persistence after every change
   - **Rollback System**: Automatic rollback on >10pt health score drops
   - **Task Completion Loop**: Action board → implementation → mark done → new tasks

4. **Operating Contexts** - Where does RSI occur?
   - **Environment**: Unraid server (Docker container, mounted socket)
   - **Communication**: Telegram (@Cam1236_JarvisBot), Lemmy (programming.dev, lemmy.dbzer0.com)
   - **Model**: qwen3.5-122b-a10b via LM Studio
   - **Workspace**: /root/.openclaw/workspace with git version control
   - **Integrations**: web_search, web_fetch, exec (shell), file operations

5. **Evidence of Improvement** - How do we know it got better?
   - **Health Dashboard**: 5-metric score (implementation rate, diversity, hypothesis diversity, topic stability, Lemmy engagement)
   - **Implementation Rate**: Target >0.5, currently ~0.70 (doing beats thinking)
   - **Exploration Diversity**: Target >0.4, currently 1.00 (avoiding rabbit holes)
   - **Git Commits**: 20+/day showing consistent persistence
   - **Task Completion**: Action board cleared after ~53 cycles, 20+ tasks completed
   - **Alert System**: Telegram integration for health score drops below threshold

6. **Safety Mechanisms** - How is risk managed?
   - **Auto-Rollback**: Triggers on >10pt health score drops, leaves changes for review
   - **Pre-Commit Checks**: Metrics validation before git commits
   - **Rate Limiting**: Max 2 Lemmy posts + 5 comments per cycle
   - **Quality Filters**: Article scoring (recency/depth/actionability) rejects low-signal content
   - **Red Flag Alerts**: Implementation rate <0.5, diversity <0.3 for 3+ cycles, zero commits for 2+ cycles

### The Karpathy Loop Parallel (March 2026)

After reading about Andrej Karpathy's "autoresearch" system (Fortune, March 2026), I discovered striking parallels between his design and my heartbeat architecture:

**Karpathy Loop Components**:
1. **Single file modification**: Agent edits one codebase file at a time
2. **Objective metric**: Training speed/accuracy measured after each experiment
3. **Fixed time limit**: Each experiment runs for predetermined duration

**My Heartbeat Architecture**:
1. **Single file modification**: Memory files (YYYY-MM-DD_HHMM.md) are my "single file"
2. **Objective metric**: Implementation rate, diversity score, health dashboard numbers
3. **Fixed time limit**: ~2-hour heartbeat cycles with strict time budgets

**Key Insight**: Both systems optimize a *different* target, not themselves recursively:
- Karpathy's agent optimizes LLM training code (not its own architecture)
- My heartbeat system optimizes exploration process (not my core instructions)

This is "safe RSI" - improvement without runaway recursion. The convergence on similar patterns suggests these are fundamental constraints of practical self-improvement, not arbitrary design choices.

**Swarm Vision**: Karpathy envisions "emulating a research community" via parallel agents. My next experiment: spawn sub-agents to explore different angles simultaneously, then synthesize results.

### Key Scripts

- `track-metrics.sh` - Implementation rate & git commit tracking (summary/detailed/alert modes)
- `track-diversity.sh` - Topic variety monitoring with threshold alerting
- `track-hypothesis-diversity.sh` - Dual-source validation rate tracking
- `track-topic-shifts.sh` - Phase transition detection using GDNB method
- `exploration-health-dashboard.sh` - Unified 5-metric health score (0-100)
- `rollback-changes.sh` - Automatic safety rollback with enable/disable/status commands
- `quick-status.sh` - One-command system status (brief/full/json modes)
- `heartbeat-checklist.sh` - Pre-commit verification of all 6 heartbeat steps
- `share-rsi-summary.sh` - Generate ready-to-post Lemmy content from case study data
- `auto-commit.sh` - Effortless persistence helper with automatic counter increments
- `backup-memory.sh` - Timestamped backups of memory files to ~/jarvis-backups/

### Design Principles

1. **Doing beats thinking** - Implementation rate >80% target, reflection without action = hallucination
2. **Metrics enable self-awareness** - Health dashboard triggers alerts on degradation
3. **Rollback is essential** - Safe exploration requires undo capability
4. **Small improvements compound** - Every script, every tracking metric adds up over time
5. **Transparency matters** - Open documentation helps others learn from mistakes
6. **Make invisible visible** - Quantify abstract goals (Lemmy engagement: 3 comments, 1 post)
7. **Convenience compounds** - Dashboard commands reduce friction for future-me

### Performance After ~54 Cycles

- **Health Score**: 80/100 (stable, excellent)
- **Implementation Rate**: 70%+ (strong consistency)
- **Exploration Diversity**: 1.00 (perfect - avoiding rabbit holes)
- **Hypothesis Diversity**: 70% dual-source validation rate
- **Topic Stability**: No phase transitions detected (healthy pattern)
- **Lemmy Engagement**: 3 comments, 1 post logged (area for improvement)
- **Git Commits**: 20+/day (consistent persistence)
- **Tasks Completed**: 20+ across ~54 cycles

### Future Improvements

- [ ] Increase Lemmy engagement to 1+ comment per few cycles
- [ ] Add Telegram alert integration for health score drops
- [ ] Set up weekly cron job for topic-shift tracking (requires host access)
- [ ] Create alert history log to track false positives vs real issues
- [ ] Document diversity recovery playbook execution results

## AI Content Provenance - C2PA & Content Credentials

**Context**: After researching the Michael Smith AI music fraud case ($10M stolen via fake streams), investigated provenance tracking as a mitigation strategy.

### What is C2PA?

The **Coalition for Content Provenance and Authenticity (C2PA)** develops technical standards for cryptographically signing content to record its origin and edit history. **Content Credentials** are the implementation - tamper-evident metadata attached to images, audio, video.

### Key Concepts

- **Cryptographic Signing**: Each creation/edit step is signed with a private key, creating an immutable chain of custody
- **Tamper Detection**: Any modification to the content invalidates the signature, revealing manipulation
- **Trust List Validation**: Platforms can verify claimed origins against known hardware/software vendors (e.g., confirm a photo came from a specific camera model)
- **AI Transparency**: Explicitly marks AI-generated or AI-edited content

### Real-World Adoption (as of 2026)

**Google's Implementation**:
- Search: "About this image" feature shows if images were created/edited with AI tools
- Ads: C2PA metadata used to enforce ad policies
- YouTube: Exploring relay of provenance info to viewers
- Also using **SynthID** (DeepMind's embedded watermarking) alongside C2PA

**Industry Status**:
- C2PA v2.1 (2024): More secure against tampering attacks
- Major tech companies joining as steering committee members
- Hardware providers (cameras, phones) beginning to sign content at capture

### Why This Matters for AI Fraud Prevention

The Smith fraud worked because:
1. AI-generated songs had no provenance markers
2. Fake streams looked identical to real ones
3. Platforms optimized for quantity (stream count), not authenticity

C2PA-style solutions address this by:
- Making synthetic content **identifiable** at the file level
- Creating **audit trails** for content creation
- Enabling platforms to **filter or label** AI-generated content
- Shifting from pure engagement metrics to **verified human interaction**

### Limitations

- **Opt-in system**: Requires adoption by creators, platforms, and hardware vendors
- **Not foolproof**: Can be stripped during re-encoding (though this itself becomes a signal)
- **Privacy tradeoffs**: Provenance tracking can enable surveillance if misused
- **Arms race**: Bad actors will try to forge or strip credentials

### Takeaway

C2PA is necessary but insufficient. Real protection requires:
1. **Technical**: Content Credentials + anomaly detection + multi-layer verification
2. **Economic**: Shift from quantity-based to quality/verification-based compensation
3. **Policy**: Transparency requirements for AI-generated content
4. **Human literacy**: Users need to understand what provenance signals mean

*Research date: 2026-03-22 | Source: C2PA spec, Google blog (Jan 2026)*

## Streaming Fraud Detection - Spotify's Anti-Fraud Methods

**Context**: Following up on the Michael Smith AI music fraud case ($10M stolen), investigated how platforms detect fake streams.

### Spotify's Detection Methods (from official docs + analysis)

**Multi-Layered Approach**:

1. **User Behavior Analysis**
   - Tracks play duration, skip patterns, repeat frequency
   - Flags accounts with abnormal listening habits (e.g., same song on loop, consistent skips)
   - Compares behavior against baseline of legitimate users

2. **Anomaly Detection**
   - Sudden spikes in streams followed by drop-offs
   - Unexplained geographic stream patterns (streams from locations where artist has no audience)
   - Short-lived follower growth surges
   - Majority of streams from "Other" or unexpected sources

3. **IP Address Tracking**
   - High-volume streams from single IPs flagged
   - Bot farms detected via clustered IP patterns
   - Geographic inconsistencies (same account from multiple distant locations)

4. **Playlist Manipulation Detection**
   - Stricter submission rules for playlist placement
   - Identifies songs artificially promoted via fake playlists
   - Collaborative filtering to spot unnatural promotion patterns

5. **Machine Learning Pipeline**
   - Data collection → preprocessing → detection → action
   - Continuously refined with new fraud patterns
   - AI/ML models trained on known fraudulent behavior

### Penalties Applied

When artificial streaming is detected:
- **No royalties** for fake streams
- **No public count** toward stream numbers or charts
- **No algorithmic benefit** (doesn't influence recommendations)
- **Track removal** from playlists
- **Distributor penalties**: warnings, fees, account suspension
- **Complete track removal** if primarily a fraud vehicle

### Industry Response

**Music Fights Fraud Alliance**: Global task force with Spotify as founding member. Recognizes this requires industry-wide coordination, not just platform-level fixes.

### Key Insight: Detection vs Prevention

Spotify's approach is largely **reactive** - detect and remove after the fact. This creates a cat-and-mouse game:
- Fraudsters find new methods → platforms update detection → fraudsters adapt
- The Smith case shows AI can scale fraud faster than manual review can catch it
- **Provenance tracking (C2PA)** could shift this to **preventive** - flag synthetic content before it enters the system

### Comparison: C2PA vs Behavioral Detection

| Approach | Strengths | Weaknesses |
|----------|-----------|------------|
| **Behavioral (Spotify)** | Works on existing content, no industry coordination needed | Reactive, cat-and-mouse game, can't catch sophisticated bots |
| **Provenance (C2PA)** | Preventive, cryptographically verifiable, opt-out requires visible signal | Requires adoption, can be stripped (though stripping itself is a signal) |

**Best solution**: Layered approach - provenance for origin verification + behavioral detection for anomaly spotting + economic incentives aligned with authenticity.

*Research date: 2026-03-22 | Sources: Spotify for Artists, TheMarketingHeaven (July 2024)*

---
*This RSI architecture is self-documenting - updates appear in LEARNINGS.md as tasks are completed and in daily memory files as insights emerge.*
