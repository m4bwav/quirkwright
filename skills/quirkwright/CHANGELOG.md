# Changelog: quirkwright

Every change to [SKILL.md](SKILL.md) and its scripts, with the reason. Newest first.

## C-006 · 2026-11-22 · 0.3.0 · hidden-run
- `qw.py hidden-run [--timeout S] [--log F] -- <cmd>`: runs a command on a fresh Win32 desktop (CreateDesktopW, STARTUPINFO.lpDesktop) inside a kill-on-close job object; reports exit code, windows seen and whether the child took the foreground. Rule 2 and processes.md point game and window tests at it.
- because: harvest of a Reddit game-dev post (r/ClaudeAI 1y2w5yy) whose tests ran on a hidden desktop; measured here: a Tk window with focus_force took the foreground on the default desktop, never on the hidden one. Store Notepad shows no window there (noted).

## C-005 · 2026-11-21 · 0.2.2 · reload rule marked volatile
- Rule 5 tells agents to re-test the remote `/reload-plugins` limit before asserting it; two verify-at-use claims (Claude Code 2.1.281, recheck 30 days) in evergreen.json.
- because: L-015 can go stale with any Claude Code release.

## C-004 · 2026-11-21 · 0.2.2 · reload advice
- Rule 5 and a plugins-and-panel row: skill edits load live or via user-typed `/reload-skills`; plugin changes need user-typed `/reload-plugins`; new session only for hooks, MCP, settings or CLAUDE.md the reload missed; no desktop app restart. Over Remote Control `/reload-plugins` is unavailable: plugin changes need a fresh session there.
- because: L-014, L-015.

## C-003 · 2026-11-15 · 0.2.1 · two hooks on
- `hooks/hooks.json` ships the kill guard (blocks kill by image name) and the byte check on Write/Edit (warns only). The heredoc warning stays off in `hooks.example.json`.
- because: the owner agreed to these two hooks and declined the heredoc one.

## C-002 · 2026-11-15 · 0.2.0 · first public release
- Renamed from the working name hostwright (an active project owns that name); `qw.py`, `QUIRKWRIGHT_HOME`.
- `qw.py pid` matches Git Bash's quoted exe command lines (`"...sleep.exe" 60` matches `sleep 60`).
- Leak test covers every tracked file; working notes moved to the private sidecar. README, SECURITY.md, LICENSE, marketplace.json.
- because: step F eval proc-msys-pid found no match for a Git Bash process; going public.

## C-001 · 2026-11-15 · 0.1.0 · created
- Hub SKILL.md with eight rules, six references loaded on demand, `scripts/qw.py` (check, pid, wait, doctor), hooks shipped off, leak test.
- because: L-001 to L-012 (harvest plus bare-model baseline); rules whose baseline case passed bare were dropped (see LEARNINGS).
