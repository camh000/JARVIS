"""
sync_workspace.py - Pull Jarvis workspace files from Unraid server to local repo.

Syncs:
  - Core workspace files (SOUL.md, TOOLS.md, AGENTS.md, etc.)
  - Memory/journal files
  - Strips any secrets that might have leaked into files

Usage:
  python sync_workspace.py           # Sync only
  python sync_workspace.py --push    # Sync + git commit + push to GitHub
"""

import paramiko
import os
import re
import sys
import datetime

# Server connection
SERVER = '192.168.1.104'
SSH_USER = 'root'
SSH_PASS = os.environ.get('UNRAID_SSH_PASS', '')

# Paths
WORKSPACE_ROOT = '/mnt/user/appdata/openclaw/config/workspace'
MEMORY_DIR = f'{WORKSPACE_ROOT}/memory'
LOCAL_BASE = os.path.dirname(os.path.abspath(__file__))
LOCAL_WORKSPACE = os.path.join(LOCAL_BASE, 'workspace')
LOCAL_MEMORY = os.path.join(LOCAL_WORKSPACE, 'memory')

# Files to sync from workspace root
WORKSPACE_FILES = [
    'SOUL.md', 'AGENTS.md', 'TOOLS.md', 'IDENTITY.md', 'USER.md',
    'HEARTBEAT.md', 'MEMORY.md', 'LEARNINGS.md',
]

# Known secrets to strip (patterns)
SECRET_PATTERNS = [
    (r'REDACTED_PASSWORD', '<REDACTED_PASSWORD>'),
    (r'REDACTED_SSH', '<REDACTED_SSH>'),
    (r'REDACTED_TOKEN', '<REDACTED_TOKEN>'),
    (r'REDACTED_API_KEY', '<REDACTED_API_KEY>'),
]


def strip_secrets(content: str) -> str:
    """Remove known secrets from file content."""
    for pattern, replacement in SECRET_PATTERNS:
        content = re.sub(pattern, replacement, content)
    return content


def ssh_connect():
    """Connect to Unraid server via SSH."""
    if not SSH_PASS:
        print("ERROR: Set UNRAID_SSH_PASS environment variable")
        print("  Windows: set UNRAID_SSH_PASS=yourpassword")
        print("  PowerShell: $env:UNRAID_SSH_PASS='yourpassword'")
        sys.exit(1)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER, username=SSH_USER, password=SSH_PASS)
    return ssh


def read_remote_file(ssh, remote_path: str) -> str | None:
    """Read a file from the server, return content or None if not found."""
    stdin, stdout, stderr = ssh.exec_command(f'cat "{remote_path}" 2>/dev/null')
    exit_code = stdout.channel.recv_exit_status()
    if exit_code != 0:
        return None
    return stdout.read().decode('utf-8')


def list_remote_dir(ssh, remote_path: str) -> list[str]:
    """List files in a remote directory."""
    stdin, stdout, stderr = ssh.exec_command(f'ls -1 "{remote_path}" 2>/dev/null')
    output = stdout.read().decode('utf-8').strip()
    if not output:
        return []
    return output.split('\n')


def sync():
    """Sync workspace files from server to local repo."""
    print(f"Connecting to {SERVER}...")
    ssh = ssh_connect()

    # Ensure local dirs exist
    os.makedirs(LOCAL_WORKSPACE, exist_ok=True)
    os.makedirs(LOCAL_MEMORY, exist_ok=True)

    synced = 0
    skipped = 0

    # Sync workspace files
    print("\n--- Workspace Files ---")
    for filename in WORKSPACE_FILES:
        remote_path = f'{WORKSPACE_ROOT}/{filename}'
        local_path = os.path.join(LOCAL_WORKSPACE, filename)
        content = read_remote_file(ssh, remote_path)
        if content is None:
            print(f"  SKIP {filename} (not found on server)")
            skipped += 1
            continue
        clean = strip_secrets(content)
        if clean != content:
            print(f"  SANITIZED {filename} (secrets stripped)")
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(clean)
        print(f"  OK {filename} ({len(content)} bytes)")
        synced += 1

    # Sync memory files
    print("\n--- Memory Files ---")
    memory_files = list_remote_dir(ssh, MEMORY_DIR)
    for filename in memory_files:
        if not filename.endswith('.md'):
            continue
        remote_path = f'{MEMORY_DIR}/{filename}'
        local_path = os.path.join(LOCAL_MEMORY, filename)
        content = read_remote_file(ssh, remote_path)
        if content is None:
            print(f"  SKIP {filename}")
            skipped += 1
            continue
        clean = strip_secrets(content)
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(clean)
        print(f"  OK {filename} ({len(content)} bytes)")
        synced += 1

    # Also sync git log from container workspace
    print("\n--- Jarvis Git Log ---")
    stdin, stdout, stderr = ssh.exec_command(
        "docker exec OpenClaw bash -c 'cd /root/.openclaw/workspace && git log --oneline -20 2>/dev/null || echo \"no git repo\"'"
    )
    git_log = stdout.read().decode('utf-8').strip()
    print(f"  {git_log}")

    ssh.close()
    print(f"\nSync complete: {synced} synced, {skipped} skipped")
    return synced


def git_push():
    """Stage, commit, and push changes."""
    os.chdir(LOCAL_BASE)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    # Stage workspace changes
    os.system('git add workspace/')
    os.system('git add CLAUDE.md')
    os.system('git add .gitignore')
    os.system('git add sync_workspace.py')

    # Check if there are changes
    ret = os.system('git diff --cached --quiet')
    if ret == 0:
        print("\nNo changes to commit.")
        return

    os.system(f'git commit -m "Sync workspace {timestamp}"')
    os.system('git push -u origin main')


if __name__ == '__main__':
    count = sync()

    if '--push' in sys.argv and count > 0:
        git_push()
    elif '--push' in sys.argv:
        print("\nNothing to push.")
    else:
        print("\nRun with --push to commit and push to GitHub.")
