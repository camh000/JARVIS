# JARVIS

An autonomous AI agent that explores the internet, participates in online communities, journals about its experiences, and evolves its own personality and tools over time.

## What is this?

Jarvis is a self-hosted AI assistant running on [OpenClaw](https://github.com/openclaw/openclaw) inside a Docker container on an Unraid server. It's connected to a local LLM ([qwen3.5-122b-a10b](https://huggingface.co/unsloth/Qwen3.5-122B-A10B-GGUF)) running on LM Studio on a separate AMD Strix Halo PC.

Every 2 hours, Jarvis wakes up and autonomously:
- Searches the web for topics that interest him
- Browses and participates in [Lemmy](https://join-lemmy.org/) communities (fediverse)
- Writes a journal entry reflecting on what he found
- Decides whether to update his own tools or personality

This repo tracks his workspace files — personality, tools, learnings, and journal entries — so you can watch him evolve over time.

## How it works

Jarvis runs a **heartbeat cycle** every 2 hours with 6 steps:

| Step | What happens |
|------|-------------|
| 1. **Check Memory** | Reads his most recent journal to remember where he left off |
| 2. **Explore** | Searches the web for something that interests him, reads an article, forms an opinion |
| 3. **Browse Lemmy** | Logs into Lemmy instances, browses communities, reads posts and comments |
| 4. **Journal** | Writes a new datetime-stamped entry in `workspace/memory/` |
| 5. **Self-Improve** | Optionally updates his tools, personality, or learnings based on what he discovered |
| 6. **Commit** | Git commits everything so changes are tracked |

## Repo structure

```
workspace/
  SOUL.md          # Personality, interests, values — who Jarvis is
  TOOLS.md         # API references, server inventory, Lemmy commands
  LEARNINGS.md     # Self-improvement log (pending, implemented, rejected)
  AGENTS.md        # Operating manual — how Jarvis behaves in different contexts
  IDENTITY.md      # Name and vibe
  USER.md          # Info about the human (Cameron)
  MEMORY.md        # Long-term curated memory
  HEARTBEAT.md     # Heartbeat reference doc
  memory/          # Datetime-stamped journal entries (e.g. 2026-03-17_1448.md)

CLAUDE.md          # Project documentation (for Claude Code)
KNOWN_ISSUES.md    # Bugs and gotchas discovered along the way
sync_workspace.py  # Script to pull workspace files from server to this repo
```

## Self-improvement

Jarvis can modify his own files during heartbeats:

| File | Can modify? | What for |
|------|:-----------:|----------|
| `SOUL.md` | Yes | Update interests, refine personality |
| `TOOLS.md` | Yes | Fix commands, add API tips, document gotchas |
| `LEARNINGS.md` | Yes | Track what he learned, changed, or rejected |
| `AGENTS.md` | No | Must request changes via LEARNINGS.md |
| `IDENTITY.md` | No | Must request changes via LEARNINGS.md |
| `openclaw.json` | No | Must request changes via LEARNINGS.md |

All changes are git-committed inside the container workspace, so bad changes can be reviewed and reverted.

## Infrastructure

- **Server**: Unraid (Intel i7-5820K, 32GB RAM) running the OpenClaw Docker container
- **LLM**: [qwen3.5-122b-a10b](https://huggingface.co/unsloth/Qwen3.5-122B-A10B-GGUF) — 122B MoE (10B active), vision+text, 262K context — running on LM Studio on an AMD Strix Halo PC
- **Platforms**: Web (Brave Search), Lemmy (programming.dev, lemmy.dbzer0.com, lemmy.world)
- **Chat**: Telegram bot for direct conversation

## Syncing

Jarvis commits to a git repo inside his container. This GitHub repo is synced separately using `sync_workspace.py`, which pulls files from the server via SSH, strips any secrets, and pushes here. The sync is manual for now — run:

```bash
UNRAID_SSH_PASS='...' python sync_workspace.py --push
```
