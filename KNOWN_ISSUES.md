# Known Issues & Gotchas

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
14. **Session `skillsSnapshot` caching** — Skills are cached at session creation time and never refreshed. Old sessions miss newly-ready skills. Fix: start a new session.
15. **JIT model loading in LM Studio** — Auto-discovers models from LM Studio, bypassing OpenClaw's configured primary model. Disable JIT in LM Studio settings to prevent this.
16. **TOOLS.md shell escaping** — `$(curl ...)` command substitution gets eaten by bash heredocs when writing files via SSH. Use base64 encoding (`echo BASE64 | base64 -d > file`) to write files with shell special characters.
17. **HEARTBEAT.md dual-path requirement** — Must exist at BOTH `/root/.openclaw/workspace/HEARTBEAT.md` AND `/home/node/clawd/HEARTBEAT.md`, even though it's NOT loaded by the agent in heartbeat sessions.
18. **LLM fabricates Lemmy post IDs** — When fetching comments, the model invents post IDs (e.g. `574832`) instead of using real ones from the listing response (`47299452`). Fix: TOOLS.md now includes `post.id` in the listing jq output and an explicit warning to only use listed IDs.
