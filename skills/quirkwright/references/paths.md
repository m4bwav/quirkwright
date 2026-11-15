# Working directory, paths, network names, interpreters

Checked: Claude Code 2.1.x, Git Bash and PowerShell 7, Windows 11, 2026-11-15.

| Quirk | Rule | Repro |
|---|---|---|
| .NET file APIs (`[IO.File]::ReadAllText`, `::Exists`) ignore `Set-Location`; relative paths resolve against the process start folder. | Pass absolute paths to `[IO.File]`, or `(Resolve-Path x).Path`. | `Set-Location $env:TEMP; New-Item n.txt; [IO.File]::Exists("n.txt")` is False |
| Local-scope MCP servers are keyed by the exact path string in `~/.claude.json`; a session opened as `d:\x` misses servers added under `D:/x`. | Start the session from the folder spelt as the key; `qw.py doctor` reports a case-only mismatch. | `claude mcp list` from both spellings |
| Paths over about 260 characters fail (git "Filename too long" even with `core.longpaths`, .NET test hosts, Python opens). | Keep clone, build and test targets short (under ~150 chars); `qw.py doctor` shows headroom; `\\?\` prefix for long opens in code. | `git clone <repo> <200-char path>` |
| `localhost` tries `::1` first: an IPv4-only server costs ~0.2-2 s per request. | Write `127.0.0.1` for local services. | `curl -w "%{time_total}" http://localhost:<port>` vs `127.0.0.1` |
| `python3` in Git Bash may be the Windows Store stub. | Use `python` or `py -3` on Windows in every shell; `qw.py doctor` reports the stub. | `python3 --version` |
| A quoted interpreter path with spaces breaks hook commands run through PowerShell. | `py -3 "<script>"` or a space-free interpreter path. | none |
| `cmd //c mklink /J` from Git Bash fails ("syntax incorrect"). | Make junctions from PowerShell: `New-Item -ItemType Junction -Path a -Target b`. | `cmd //c mklink /J a b` |

Parallel Bash calls were reported to share one cwd (a `cd` in one breaking a sibling); not reproduced 2026-11-15. Absolute paths in every call cost nothing either way.
