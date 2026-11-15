# Processes, pids, killing

Checked: Claude Code 2.1.x, Git Bash and PowerShell 7, Windows 11, 2026-11-15.

| Quirk | Rule | Repro |
|---|---|---|
| `taskkill /IM python.exe`, `Stop-Process -Name node`, `pkill python` end every match: other sessions' jobs and long-running local servers. | Kill only what you started, by pid, after checking its start time and command line: `qw.py pid "<script and args>"`. | none (destructive) |
| `$!` after a Bash-tool background job is the MSYS pid, not the Windows pid; `tasklist` says no such task while it runs. | Find and record the real pid with `qw.py pid` (CIM command-line match). | `sleep 60 & echo $!`, then `qw.py pid "sleep 60"` |
| A command-line match also hits a Monitor or wait loop whose own command line holds the same word, and killing it ends your watch. | Match the full argument list; `qw.py pid` sets wait loops aside unless `--all`. | `qw.py pid <word>` while a Monitor greps for that word |
| A Bash-tool call that reads stdin (`cat > /dev/null`, a prompt) hangs until the 120 s timeout. | Never run stdin readers; feed input from a file or argument. Stop a hung background one with TaskStop. | `cat > /dev/null` |
| An app launcher can start its own copy of a server at the same moment as yours; the loser dies "port in use". | Before deciding a launch failed, list who holds the process and port; do not assume the serving process is yours. | none |
