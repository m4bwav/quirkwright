quirkwright is a Claude Code plugin for coding agents that run on a Windows host. It holds one skill (four short rules, with references loaded only when a rule applies), a standard-library script `qw.py`, and two hooks that are on by default.

Agents are mostly trained on Linux transcripts. On Windows they lose backslashes in Bash heredocs, save files with CRLF or a BOM without noticing, read `$!` as a Windows pid when it is not, kill every `python.exe` on the machine, and write wait loops that never see the job fail. quirkwright covers those cases.

## What is in it

| Part | What it does | Page |
|---|---|---|
| The skill | Rules: no backslashes through a heredoc, kill by pid only, short paths, and a line of basics | [Rules](Rules) |
| `qw.py check` | Reports CR bytes, control bytes, BOM and half-decoded escapes in files just written | [Commands](Commands) |
| `qw.py pid` | Finds the real Windows pids for a command line | [Commands](Commands) |
| `qw.py wait` | Waits on a log until a done line, a new failure line or a deadline | [Commands](Commands) |
| `qw.py doctor` | Reports shells, the `python3` Store stub, path case, path headroom, stdout encoding, a plugin's installed version | [Commands](Commands) |
| Kill guard hook (on) | Refuses `taskkill /IM`, `Stop-Process -Name` and the like | [Hooks](Hooks) |
| Byte check hook (on) | Warns after a Write or Edit leaves control bytes, a BOM or a lost escape | [Hooks](Hooks) |
| Heredoc hook (off) | Warns when a Python heredoc carries a backslash | [Hooks](Hooks) |

## Start here

- [Getting started](Getting-Started): install, then the first commands.
- [FAQ](FAQ): what the hooks catch and what they do not.
- [Versions and upgrading](Versions-and-Upgrading): what changed in 0.2.1.
