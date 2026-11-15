# Research: quirkwright

Findings behind [SKILL.md](SKILL.md). Newest first.

## Search plan

1. Claude Code changelog and docs (code.claude.com/docs): Bash tool on Windows, PowerShell tool, `CLAUDE_CODE_GIT_BASH_PATH` and shell selection, Write/Edit escaping, Monitor and background tasks, plugin cache and `installed_plugins.json`.
2. Claude Code GitHub issues: labels `platform:windows`; search "heredoc backslash", "CRLF", "unicode escape Write", "MSYS".
3. Git for Windows release notes: MSYS path conversion, `core.longpaths`.
4. Python docs "What's new": UTF-8 mode (PEP 686) default status on Windows, which would retire the cp1252 rule.
5. Prior-art plugins for Windows agent hosts (an MSYS toolchain plugin covers path conversion in depth; link, do not copy).
6. Re-run every volatile claim's repro in `evergreen.json` on the current harness.

## R-001 · 2026-11-15 · harvest and prior art
- 45 lessons harvested from one owner's agent memory and skills; 22 eval cases written; bare baseline 14 fail, 3 pass, 5 not run.
- Prior art: no plugin covers the Claude Code tool-level quirks (heredoc, Write decoding, `$!`); an existing Windows toolchain plugin covers MSYS path conversion and is linked rather than duplicated.
- Python 3.15 is due to make UTF-8 mode the default (PEP 686); recheck L-006 on that release.
