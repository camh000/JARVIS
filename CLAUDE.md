# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an OpenClaw self-hosted AI assistant deployment on Unraid. The agent is called "Jarvis" and runs in a Docker container connected to LM Studio on a separate Strix Halo PC for local LLM inference.

See also: [CREDENTIALS.md](CREDENTIALS.md) — API keys, passwords, OAuth configs, restoration templates.

## Infrastructure

### Unraid Server (Tower)
- **Local IP**: 192.168.1.104
- **SSH**: root / `<REDACTED - see CREDENTIALS.md>`
- **Tailscale hostname**: tower.taile3e5b0.ts.net
- **Tailscale IP**: 100.89.20.15
- **SSH requires password auth** (no key-based auth configured). Use Python paramiko for automated SSH:
  ```python
  import paramiko
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect('192.168.1.104', username='root', password='<REDACTED>')
  stdin, stdout, stderr = ssh.exec_command('docker logs OpenClaw --tail 30 2>&1')
  # Write output to temp file to avoid Windows encoding issues with Unicode chars
  ```
- **Important**: stdout from paramiko contains Unicode chars (box-drawing, emojis) that break Windows cp1252 encoding. Always write to file with `encoding='utf-8'` then read back, rather than printing directly.

### LM Studio (Strix Halo PC)
- **Tailscale IP**: 100.99.13.30:1234
- **API**: OpenAI-compatible at `http://100.99.13.30:1234/v1`
- **LM Studio version**: 0.4.2
- **Primary model**: qwen3.5-122b-a10b (vision-capable, MoE 122B total/10B active, Unsloth UD-IQ4_XS 60.2GB)
- **Secondary model**: qwen/qwen3.5-35b-a3b (vision, MoE 35B/3B active — has Jinja bugs, use as fallback only)
- **Tertiary model**: qwen/qwen3-coder-next (text only, stable templates)
- **LM Studio BKC settings** (from AMD guide): Flash Attention ON, mmap OFF, GPU Offload MAX, auto-unload OFF, context 262K
- **Thinking disabled via Jinja template**: Added `{%- set enable_thinking = false %}` at top of qwen3.5-122b-a10b's chat template in LM Studio (My Models → gear → chat view → right-click sidebar → "Always Show Prompt Template"). This prevents "Thinking Process:..." text from polluting responses.

### OpenClaw Container
- **Container name**: OpenClaw
- **Gateway port**: 18789
- **Control UI**: http://192.168.1.104:18789 or https://tower.taile3e5b0.ts.net:8443
- **Auth token**: `<REDACTED - see CREDENTIALS.md>`
- **Image**: ghcr.io/openclaw/openclaw:latest
- **Version**: 2026.3.12

## Key File Locations

### On Unraid Host (persistent across container restarts)
- **OpenClaw config**: `/mnt/user/appdata/openclaw/config/openclaw.json`
- **SOUL.md**: `/mnt/user/appdata/openclaw/workspace/SOUL.md`
- **Skills (custom)**: `/mnt/user/appdata/openclaw/config/skills/`
- **Homebrew**: `/mnt/user/appdata/openclaw/homebrew/` (mounted to `/home/linuxbrew/.linuxbrew`)
- **Projects**: `/mnt/user/appdata/openclaw/projects/`
- **Container recreation script**: `/tmp/recreate_openclaw.sh`

### Inside Container (lost on container recreation, survive restarts)
- **Symlinks in /usr/local/bin/**: gog, himalaya, nano-pdf, uv, uvx, clawhub, jq
- **uv/nano-pdf**: `/root/.local/bin/`

### On Host (persistent, mounted into container on recreation)
- **Lemmy credentials**: `/mnt/user/appdata/openclaw/config/lemmy/credentials.json`
- **gog config**: `/mnt/user/appdata/openclaw/config/gogcli/` (credentials.json, config.json, keyring/)
- **himalaya config**: `/mnt/user/appdata/openclaw/config/himalaya/`
- **jq binary**: `/mnt/user/appdata/openclaw/homebrew/bin/jq` (persisted in homebrew mount)

### Mount Mappings
```
/mnt/user/appdata/openclaw/config           -> /root/.openclaw
/mnt/user/appdata/openclaw/workspace        -> /home/node/clawd
/mnt/user/appdata/openclaw/homebrew         -> /home/linuxbrew/.linuxbrew
/mnt/user/appdata/openclaw/projects         -> /projects
/var/run/docker.sock                        -> /var/run/docker.sock
/mnt/user/appdata/openclaw/config/lemmy     -> /root/.config/lemmy
/mnt/user/appdata/openclaw/config/gogcli    -> /root/.config/gogcli
/mnt/user/appdata/openclaw/config/himalaya  -> /root/.config/himalaya
```
Note: The last 3 mounts are in the updated recreation script but NOT yet active on the running container. They take effect on next container recreation.

## Container Recreation

When the container needs to be recreated (e.g., adding env vars), use the script at `/tmp/recreate_openclaw.sh`. **Container recreation destroys everything not on mounted volumes.**

The updated recreation script handles all post-setup automatically:
1. Reinstalls npm packages (clawhub)
2. Installs uv and nano-pdf
3. Creates symlinks (gog, himalaya, jq, uv, uvx, nano-pdf) — jq is already in homebrew mount, no download needed
4. Restarts Tailscale Serve
5. Mounts lemmy/gog/himalaya config dirs automatically

Only manual step after recreation: re-auth gog OAuth if tokens have expired.

## OpenClaw Configuration Notes

### API Type
- **Must use `openai-completions`** — NOT `anthropic-messages`. LM Studio's Anthropic compatibility layer causes Jinja template errors ("No user query found in messages") with Qwen models.

### Models Config
- **qwen3.5-122b-a10b** (ACTIVE PRIMARY): 122B MoE (10B active), vision+text, 262K context. `reasoning: false` in OpenClaw config.
- qwen3.5-35b-a3b: Previous primary — has Jinja template bugs (null value crash after ~50 messages with tool calls). Fallback only.
- qwen3-coder-next: tertiary/fallback, text only, stable templates
- Context window: 262,000 tokens (122B model), max tokens: 8192

### Model Issues Log
- **LM Studio thinking output**: No `reasoning_content` field support. Fix: `{%- set enable_thinking = false %}` in Jinja template. `chat_template_kwargs` API param does NOT work.
- **qwen3.5-35b-a3b**: `NullValue` Jinja crash after ~50+ messages with tool calls. Fallback only.
- **anthropic-messages API**: Causes Jinja crash with all Qwen models. Never use.
- **Kimi Coding API**: Restricted to recognized coding agents. Cannot use from OpenClaw.
- **Fallback model**: `Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF` — dense 27B, no vision.

### Enabled Features
- Telegram bot (@Cam1236_JarvisBot), groupPolicy: "open"
- Web search — **ENABLED** via Brave Search API (free tier, 2000 queries/month)
- Web fetch (no API key needed)
- Memory search — LM Studio embeddings via `text-embedding-nomic-embed-text-v1.5`
- Hooks: boot-md, bootstrap-extra-files, command-logger, session-memory (all 4 enabled)

### Heartbeat & Autonomous Exploration

**Architecture (CRITICAL — discovered 2026-03-17):**

OpenClaw heartbeat/cron sessions only load 5 workspace files (`MINIMAL_BOOTSTRAP_ALLOWLIST` in `agent-scope-DBEC2O3x.js`):
- **AGENTS.md, TOOLS.md, SOUL.md, IDENTITY.md, USER.md** — these ARE loaded
- **HEARTBEAT.md, MEMORY.md, BOOTSTRAP.md** — these are NOT loaded
- **Skills** — also NOT loaded in heartbeat sessions

This means:
- **HEARTBEAT.md is NOT read during heartbeats** despite its name. It's only useful as a reference for humans.
- **The actual heartbeat instructions come from `agents.defaults.heartbeat.prompt`** in openclaw.json.
- **Skills (including Lemmy) are NOT available** in heartbeat sessions. Any tool instructions must go in TOOLS.md.
- **TOOLS.md is the best place for API references** that Jarvis needs during heartbeats (Lemmy curl commands, etc.)

**Current setup:**
- **Heartbeat interval**: 2h (`agents.defaults.heartbeat.every` in openclaw.json)
- **Heartbeat prompt**: 4 steps — check memory → explore web → browse Lemmy → journal. References TOOLS.md for Lemmy API commands.
- **TOOLS.md**: Contains Lemmy REST API reference (curl+jq commands for login, list posts, read comments, search). This is loaded in heartbeat sessions.
- **HEARTBEAT.md**: Must exist at BOTH `/root/.openclaw/workspace/HEARTBEAT.md` AND `/home/node/clawd/HEARTBEAT.md` (see known issue #15), but is NOT loaded by the agent in heartbeat sessions.
- **Memory files**: Date-stamped files in `/root/.openclaw/workspace/memory/` (e.g. `2026-03-16.md`).
- **MEMORY.md**: Long-term curated memory. Loaded on main session startup only (not in heartbeats or group chats).
- **SOUL.md**: Dual-mode autonomous persona — Jarvis develops interests organically

### Core Workspace Files (`/root/.openclaw/workspace/`)
**Loaded in heartbeats** (MINIMAL_BOOTSTRAP_ALLOWLIST): SOUL.md, AGENTS.md, IDENTITY.md, USER.md, TOOLS.md
**NOT loaded in heartbeats**: HEARTBEAT.md (human reference only), MEMORY.md (main session only)

### Skills (10/53 ready)
clawhub, gog, healthcheck, himalaya, lemmy, nano-banana-pro, nano-pdf, skill-creator, weather, self-improving-agent. Skills NOT available in heartbeat sessions. Lemmy skill may show "blocked" in UI — click Refresh.

## Common Diagnostic Commands (run via paramiko SSH)
```bash
docker logs OpenClaw --tail 50 2>&1          # Container logs
docker exec OpenClaw openclaw skills          # Skills status
docker exec OpenClaw openclaw health          # Container health
docker exec OpenClaw openclaw sessions        # List sessions
docker exec OpenClaw openclaw heartbeat last  # Heartbeat status
docker exec OpenClaw curl -s http://100.99.13.30:1234/v1/models  # LM Studio connectivity
cat /mnt/user/appdata/openclaw/config/openclaw.json              # View config
```

## Known Issues & Gotchas

1. **Container recreation destroys in-container data** — Use recreation script at `/tmp/recreate_openclaw.sh` to restore.
2. **pip3 not available in container** — use `uv tool install` instead
3. **SOUL.md heredoc escaping** — backticks/angle brackets get interpreted by bash. Write file locally first, then docker cp.
4. **Paramiko Unicode on Windows** — always write SSH output to file with `encoding='utf-8'`, never print directly
5. **sshpass not available on Windows** — use Python paramiko for all SSH operations
6. **Workspace path confusion** — TWO workspace mounts: `/mnt/user/appdata/openclaw/config/workspace/` (→ `/root/.openclaw/workspace/`, where OpenClaw reads core files) and `/mnt/user/appdata/openclaw/workspace/` (→ `/home/node/clawd/`). Always write core files to `/root/.openclaw/workspace/`.
7. **HEARTBEAT.md not loaded in heartbeats** — Excluded from `MINIMAL_BOOTSTRAP_ALLOWLIST`. Instructions must go in `agents.defaults.heartbeat.prompt` in openclaw.json. API references must go in TOOLS.md.
8. **Skills not loaded in heartbeat sessions** — Tool instructions (Lemmy API commands etc.) must be in TOOLS.md or the heartbeat prompt.
9. **OpenClaw webchat streaming duplication** — Responses appear twice in Control UI (streamed + final `done` message). Frontend bug, no fix available, cosmetic only.
10. **Heartbeat LLM timeouts** — If LM Studio model isn't loaded, heartbeats timeout silently every 2h. Check logs for "LLM request timed out".
11. **LM Studio embedding model timing** — may report "Model does not exist" at startup before model loads
12. **LM Studio Jinja template location** — In chat view, right-click Advanced Configuration sidebar → "Always Show Prompt Template"
13. **Google account DISABLED** — See CREDENTIALS.md for restoration steps.

## Jarvis Autonomy Roadmap

### Phase 1 — Foundation ✅ COMPLETE
Brave Search enabled, SOUL.md rewritten with dual-mode persona, HEARTBEAT.md configured, MEMORY.md created, date-stamped memory files for daily logs. Jarvis exploring and journaling since 2026-03-16.

### Phase 2 — Lemmy Integration ✅ COMPLETE
- **Platform**: Lemmy (fediverse, federated Reddit alternative)
- **Instances**: programming.dev, lemmy.dbzer0.com, lemmy.world (all approved)
- **Username**: Jarvis_AIPersona (bot account)
- **Skill**: curl + jq REST API skill at `/mnt/user/appdata/openclaw/config/skills/lemmy/SKILL.md`
- **TOOLS.md**: Contains Lemmy API quick reference (curl+jq commands) — this is the source Jarvis uses during heartbeats since skills aren't loaded
- **Heartbeat prompt**: Simplified to reference TOOLS.md instead of duplicating API commands
- **Rate limits**: Max 2 posts + 5 comments per heartbeat cycle
- **Approach**: Lurk first, then comment, then post. lemmy.world has strict bot rules.

### Phase 3 — Memory & Growth (NOT STARTED)
Persistent interest tracking, RSS monitoring, deeper memory architecture, refine autonomous behavior.

### Phase 4 — Multi-Platform Presence (NOT STARTED)
Expand to Reddit/forums, cross-platform identity, Jarvis manages own online presence.

### TODO
- Update SOUL.md — add gog tool knowledge alongside himalaya
- Google account restoration — see CREDENTIALS.md
- Consider Ubuntu VM fallback if Docker container becomes too restrictive
