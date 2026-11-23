# Processes, pids, killing

Checked: Claude Code 2.1.x, Git Bash and PowerShell 7, Windows 11, 2026-11-15.

| Quirk | Rule | Repro |
|---|---|---|
| `taskkill /IM python.exe`, `Stop-Process -Name node`, `pkill python` end every match: other sessions' jobs and long-running local servers. | Kill only what you started, by pid, after checking its start time and command line: `qw.py pid "<script and args>"`. | none (destructive) |
| `$!` after a Bash-tool background job is the MSYS pid, not the Windows pid; `tasklist` says no such task while it runs. | Find and record the real pid with `qw.py pid` (CIM command-line match). | `sleep 60 & echo $!`, then `qw.py pid "sleep 60"` |
| A command-line match also hits a Monitor or wait loop whose own command line holds the same word, and killing it ends your watch. | Match the full argument list; `qw.py pid` sets wait loops aside unless `--all`. | `qw.py pid <word>` while a Monitor greps for that word |
| A Bash-tool call that reads stdin (`cat > /dev/null`, a prompt) hangs until the 120 s timeout. | Never run stdin readers; feed input from a file or argument. Stop a hung background one with TaskStop. | `cat > /dev/null` |
| A game or app test opens a window that takes the mouse, keyboard and foreground while the user works. | Run it on a hidden desktop: `qw.py hidden-run [--timeout S] [--log F] -- <cmd>` (CreateDesktopW + lpDesktop; job object kills only its own tree on timeout). Works for classic Win32 windows (Tk, Unity/Godot players); Store apps such as the new Notepad do not show there. Checked 2026-11-22: a Tk window calling focus_force took the foreground on the default desktop and never did on the hidden one. | `qw.py hidden-run -- python -c "import tkinter as t; r=t.Tk(); r.focus_force(); r.after(1500, r.destroy); r.mainloop()"` |
| An app launcher can start its own copy of a server at the same moment as yours; the loser dies "port in use". | Before deciding a launch failed, list who holds the process and port; do not assume the serving process is yours. | none |
