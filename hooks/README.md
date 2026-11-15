# quirkwright hooks

Since 0.2.1 the plugin ships `hooks.json` with two hooks on: the kill guard and the byte check. The heredoc warning stays off in `hooks.example.json`.

| Mode | Event | Does |
|---|---|---|
| `guards.py kill` | PreToolUse, Bash and PowerShell | Blocks `taskkill /IM`, `Stop-Process -Name`, `pkill`/`killall` aimed at python or node, and points to `qw.py pid`. |
| `guards.py heredoc` | PreToolUse, Bash | Adds a warning when a heredoc feeding Python carries a backslash. Never blocks. |
| `guards.py check` | PostToolUse, Write and Edit | Runs `qw.py check` on the written file and reports CR, control bytes, BOM, half-decoded escapes. Never blocks. |

To turn the heredoc warning on: copy its entry from `hooks.example.json` into `hooks.json` and reinstall the plugin. To turn a hook off, remove its entry from `hooks.json`. Tests: `tests/test_hooks.py`.
