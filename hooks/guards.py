#!/usr/bin/env python3
"""quirkwright hooks (shipped OFF; see hooks/README.md).

  guards.py kill      PreToolUse Bash|PowerShell: refuse kills by image name of python/node
  guards.py heredoc   PreToolUse Bash: warn when a heredoc writes a .py file holding a backslash
  guards.py check     PostToolUse Write|Edit: run qw.py check on the written file, report damage

Reads the hook JSON on stdin. Exit 2 with a message on stderr blocks (kill only);
the others never block and print JSON with additionalContext.
"""
import json
import os
import re
import subprocess
import sys

BS = chr(92)
KILL_PATTERNS = [
    r"taskkill\b[^|;&]*(/|//|-)im\s+\"?(python|pythonw|py|node)(\.exe)?",
    r"Stop-Process\b[^|;&]*-Name\s+\"?(python|pythonw|py|node)",
    r"\b(pkill|killall)\b[^|;&]*\b(python3?|node)\b",
]


def kill_verdict(cmd):
    for p in KILL_PATTERNS:
        if re.search(p, cmd, re.IGNORECASE):
            return ("quirkwright: refused a kill by image name; it ends other sessions' jobs and servers. "
                    "Find the pid with qw.py pid \"<full command>\" and kill that pid.")
    return None


def heredoc_verdict(cmd):
    m = re.search(r"<<-?\s*['\"]?(\w+)['\"]?", cmd)
    if not m:
        return None
    if not re.search(r"\.py\b|python", cmd):
        return None
    body = cmd[m.end():]
    if BS in body:
        return ("quirkwright: this heredoc carries backslashes into Python; the Bash tool halves them. "
                "Write the file with the Write tool, or build backslashes with chr(92).")
    return None


def emit(event, text):
    sys.stdout.write(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    ti = data.get("tool_input") or {}
    if mode == "kill":
        msg = kill_verdict(ti.get("command") or "")
        if msg:
            sys.stderr.write(msg + "\n")
            return 2
    elif mode == "heredoc":
        msg = heredoc_verdict(ti.get("command") or "")
        if msg:
            emit("PreToolUse", msg)
    elif mode == "check":
        path = ti.get("file_path")
        if path and os.path.isfile(path):
            hw = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills", "quirkwright", "scripts", "qw.py")
            r = subprocess.run([sys.executable, hw, "check", path], capture_output=True, text=True, encoding="utf-8")
            if r.returncode == 1:
                try:
                    issues = json.loads(r.stdout)["files"][path].get("issues", [])
                except (ValueError, KeyError):
                    issues = ["unreadable"]
                emit("PostToolUse", "quirkwright: %s has %s; fix before relying on it." % (path, ", ".join(issues)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
