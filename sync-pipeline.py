#!/usr/bin/env python3
"""Claude Bridge 一键同步: git commit + Project Files 推送 + Drive KB 同步."""

import subprocess
import sys
import os
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
CB_HOME = os.path.expanduser("~/.claude-bridge")
SCRIPTS = os.path.expanduser("~/.openclaw/scripts")
PROJECT_ID = "019cc6a8-2b99-7052-bc59-63ddae533682"


def log(msg):
    ts = datetime.now(CST).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def run(cmd, cwd=None, check=True):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  STDERR: {result.stderr.strip()}")
    return result


def step_git():
    log("=== 1/3 Git commit ===")
    status = run(["git", "status", "--porcelain"], cwd=CB_HOME)
    if not status.stdout.strip():
        log("  No changes to commit")
        return
    ts = datetime.now(CST).strftime("%Y-%m-%d %H:%M")
    run(["git", "add", "-A"], cwd=CB_HOME)
    result = run(["git", "commit", "-m", f"sync: {ts}"], cwd=CB_HOME, check=False)
    if result.returncode == 0:
        log(f"  Committed: sync: {ts}")
    else:
        log(f"  Commit skipped: {result.stdout.strip()}")

    # Push if remote exists
    remote = run(["git", "remote"], cwd=CB_HOME, check=False)
    if remote.stdout.strip():
        push = run(["git", "push"], cwd=CB_HOME, check=False)
        if push.returncode == 0:
            log("  Pushed to remote")
        else:
            log(f"  Push failed: {push.stderr.strip()}")


def step_project_files():
    log("=== 2/3 Push Project Files to claude.ai ===")
    result = run([
        sys.executable,
        os.path.join(SCRIPTS, "push-project-files.py"),
        "--project-id", PROJECT_ID,
        "--source-dir", os.path.join(CB_HOME, "project-files"),
    ], check=False)
    print(result.stdout)
    if result.returncode != 0:
        log("  Project Files push failed")
        print(result.stderr)
        return False
    return True


def step_drive_kb():
    log("=== 3/3 Sync Drive KB ===")
    result = run([
        sys.executable,
        os.path.join(SCRIPTS, "manage-kb-drive.py"),
        "--source-dir", os.path.join(CB_HOME, "kb-content"),
        "--folder", "Claude-Bridge-KB",
        "--glob", "CB-KB-*.md",
        "sync",
    ], check=False)
    print(result.stdout)
    if result.returncode != 0:
        log("  Drive KB sync failed")
        print(result.stderr)
        return False
    return True


def main():
    log("=== Claude Bridge Sync Pipeline ===")
    step_git()
    pf_ok = step_project_files()
    kb_ok = step_drive_kb()

    if pf_ok and kb_ok:
        log("=== All done ===")
    else:
        log("=== Completed with errors ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
