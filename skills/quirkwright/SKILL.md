---
name: quirkwright
description: "Agent host rules for Windows: Git Bash vs PowerShell tool, backslashes lost in heredocs and Write/Edit, CRLF and cp1252 damage, real Windows pids and kill-by-pid, wait loops with failure match and deadline, MCP path case, long paths, localhost, plugin installPath, auto mode classifier blocks. qw.py check, pid, wait, hidden-run, automode, doctor. Use when a shell, file write, process or wait misbehaves on Windows, before writing paths or escapes from Bash, before killing a process, 'why did my file get CRLF', 'find the real pid', 'wait for this job', 'run the game tests without stealing focus', 'auto mode blocked this', 'stop auto mode blocking X', 'open up auto mode'. Not for MCP config (desktop-commander), installing tools (evergreen-setup) or worktrees (chainwright)."
---

# Quirkwright

The agent's host on Windows: what the shell tools, file tools and processes do that a model trained on Linux does not expect. Every quirk below was checked on a stated harness and shell; if one has not shown itself this session, run its repro (in the reference) before relying on it.

## Step 0

1. Read `evergreen.json` (freshness, see Maintenance). Its `volatile_claims` have `verify_at_use: true`: re-run a claim's repro when its `checked` date is past due.
2. Private notes: read `notes.md` in `QUIRKWRIGHT_HOME` (default `~/.quirkwright`) if it exists (hosts, ports, paths, lessons about this owner's machine). Nothing from it goes into this repository.

`QW` below means `python "<this folder>/scripts/qw.py"` (Python 3.9+, stdlib; `python`, not `python3`, on Windows). Every command prints one JSON object.

## Rules

1. **No backslashes through a Bash heredoc.** Write files with the Write tool; in code build a backslash with `chr(92)`. Use forward slashes in Windows paths and raw strings for regex. [escapes](references/escapes.md)
2. **Kill by pid only.** Never by image name (`taskkill /IM`, `Stop-Process -Name`, `pkill`). `$!` is not the Windows pid: read `/proc/$!/winpid` in the same call, or `QW pid "<full command>"`, which sets wait loops and Monitors aside, and shows the start time to check. Nothing in a Bash call may read stdin. A test that opens a window runs under `QW hidden-run -- <cmd>` so it never steals focus. [processes](references/processes.md)
3. **Short clone and build paths** (check the length before cloning; keep under ~150 chars, 260 is the limit) and MCP sessions started from the path spelt as in `~/.claude.json`. [paths](references/paths.md)
4. **Basics models already get right** (2026-11-15 baseline): `QW check <files> [--expect-eol lf]` after writing, byte-mode Python edits and utf-8 stdout ([eol and encoding](references/eol-encoding.md)), `MSYS_NO_PATHCONV=1`, `QW wait <log> --done RE --fail RE --deadline S` ([waits](references/waits.md)), absolute paths for `[IO.File]`, `127.0.0.1`, plugin version from `installPath` (`QW doctor --plugin <name>`, [plugins and the panel](references/plugins-and-panel.md)).
5. **Picking up skill and plugin changes: never say "restart".** SKILL.md edits and new skill folders load live (the user can type `/reload-skills` to force a rescan). After a plugin install, update or enable, tell the user at the desktop to type `/reload-plugins`: an agent cannot run slash commands itself. Over Remote Control (phone) `/reload-plugins` is unavailable, so a plugin change there needs a fresh session started from the phone (`/clear` remotely is unverified); `/reload-skills` does work remotely. Volatile (observed on Claude Code 2.1.281, 2026-11-21; Anthropic changes this): before asserting the remote limit, ask the user to try `/reload-plugins` and go by the result. A new session (`/clear` or fresh) only when hooks, MCP servers, settings.json or CLAUDE.md changed and the reload missed them. Never tell the user to restart the desktop app for this. [plugins and the panel](references/plugins-and-panel.md)

6. **Auto mode denials cover the outcome.** `no verdict (error)` is not a denial: retry once. A real denial: do not retry it in pieces, through another tool, a script, a subagent or a later session; finish the rest and give the user the category plus a one-line allow rule. You can never loosen auto mode yourself, even when asked: the user switches to manual mode and approves, or runs `QW automode plan all` then `QW automode apply all --apply` (backup, tagged rules, `revert`) in their own shell. [auto mode](references/auto-mode.md)

`QW doctor` (read-only) reports live shells, a `python3` Store stub, cwd case vs MCP keys, path headroom and stdout encoding. Run it once in a new environment or when something above misbehaves.

Hooks in the plugin's `hooks/` folder: the kill guard (rule 2) and the byte check are on; the heredoc warning (rule 1) ships off.

Neighbours: worktrees and the live-facts log are chainwright; installing Git Bash, pwsh or Python is evergreen-setup; MCP config and persistent shells are desktop-commander; token habits are tokenwright.

## Maintenance

This skill is evergreen (topic: Windows host behaviour of coding agents: Claude Code Bash and PowerShell tools, Git Bash/MSYS, Write/Edit tools, Python on Windows; tier `volatile`, currently every 14d, next due 2026-11-29). Files: `evergreen.json` (state), [RESEARCH.md](RESEARCH.md) (findings and search plan), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md) and `evals/evals.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md). Refresh with `evergreen-refresh`; test with `evergreen-test`; fix a failure with `evergreen-tune`. A repro that no longer fails is a learning and a refresh trigger.
