The skill keeps four rules. Each one failed for a model without the skill on a clean run before it went in (2026-11-15 baseline); rules the model already followed are folded into rule 4.

| Rule | Why | Reference in the repository |
|---|---|---|
| 1. No backslashes through a Bash heredoc | The Bash tool turns a doubled backslash into one before the shell runs, so Windows paths and `"\n"`-style escapes in generated code arrive broken. Write files with the Write tool, build a backslash in code with `chr(92)`, use forward slashes in paths. | `references/escapes.md` |
| 2. Kill by pid only | `taskkill /IM python.exe` ends every Python on the machine, including other sessions' jobs and local servers. `$!` in Git Bash is the MSYS pid, not the Windows one. Use `qw.py pid`. | `references/processes.md` |
| 3. Short clone and build paths | Windows paths stop at 260 characters; keep clone paths under about 150. Start MCP sessions from the path spelt exactly as in `~/.claude.json`. | `references/paths.md` |
| 4. Basics | `qw.py check` after writing, byte-mode Python edits, UTF-8 stdout, `MSYS_NO_PATHCONV=1`, `qw.py wait` with a failure match and deadline, absolute paths for `[IO.File]`, `127.0.0.1` over `localhost`, a plugin's version from `installPath`. | `eol-encoding.md`, `waits.md`, `plugins-and-panel.md` |

Every reference row names the harness and shell it was checked on and a repro. When a quirk has not shown itself in the session, run its repro before relying on it.

## Neighbours

- Git worktrees and the shared session log: chainwright.
- Installing Git Bash, pwsh or Python: evergreen-setup.
- MCP config and persistent shells: desktop-commander.
