# quirkwright hooks (off)

These hooks are built and tested but **not enabled**. The plugin ships `hooks.example.json`, which Claude Code ignores; they stay off until the owner agrees to turn them on.

| Mode | Event | Does |
|---|---|---|
| `guards.py kill` | PreToolUse, Bash and PowerShell | Blocks `taskkill /IM`, `Stop-Process -Name`, `pkill`/`killall` aimed at python or node, and points to `qw.py pid`. |
| `guards.py heredoc` | PreToolUse, Bash | Adds a warning when a heredoc feeding Python carries a backslash. Never blocks. |
| `guards.py check` | PostToolUse, Write and Edit | Runs `qw.py check` on the written file and reports CR, control bytes, BOM, half-decoded escapes. Never blocks. |

To turn them on: rename `hooks.example.json` to `hooks.json` and reinstall the plugin, or copy the entries into `~/.claude/settings.json` with the plugin path written out. Tests: `tests/test_hooks.py`.
