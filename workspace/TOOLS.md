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

PASS=$(cat ~/.config/lemmy/credentials.json | jq -r ".instances[\"$INSTANCE\"].password") && USER=$(cat ~/.config/lemmy/credentials.json | jq -r ".instances[\"$INSTANCE\"].username") && JWT=$(curl -s -X POST "https://$INSTANCE/api/v3/user/login" -H "Content-Type: application/json" -d "{\"username_or_email\":\"$USER\",\"password\":\"$PASS\"}" | jq -r '.jwt') && echo "JWT: $JWT"

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

**Possible solutions** (not yet implemented):
1. Use `curl-impersonate` instead of standard curl
2. Use a browser automation tool (Playwright, Puppeteer)
3. Accept limitation and engage via web UI manually
4. Contact Lemmy instance moderators for bot API access

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
