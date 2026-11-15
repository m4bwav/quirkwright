The plugin ships `hooks/hooks.json`, which Claude Code loads from an installed plugin. Since 0.2.1 it turns two hooks on. A third stays off in `hooks/hooks.example.json`, a file name Claude Code ignores.

| Hook | State | Event | Does |
|---|---|---|---|
| `guards.py kill` | on | PreToolUse, Bash and PowerShell | Blocks a kill by image name and points to `qw.py pid` |
| `guards.py check` | on | PostToolUse, Write and Edit | Runs `qw.py check` on the written file and adds a warning; never blocks |
| `guards.py heredoc` | off | PreToolUse, Bash | Warns when a heredoc feeding Python carries a backslash; never blocks |

All three run `py -3`, so they need the Windows `py` launcher.

## Kill guard

It refuses `taskkill /IM`, `Stop-Process -Name`, and `pkill` or `killall` aimed at python or node. The tool call is blocked (exit 2) and the agent sees:

```text
quirkwright: refused a kill by image name; it ends other sessions' jobs and servers. Find the pid with qw.py pid "<full command>" and kill that pid.
```

`taskkill /F /PID 1234` passes with no output.

## Byte check

After a Write or Edit, a file with control bytes gets:

```text
{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "quirkwright: esc.py has control-bytes; fix before relying on it."}}
```

and a file with a BOM:

```text
{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "quirkwright: bom.md has bom; fix before relying on it."}}
```

A clean file gets nothing. The hook runs `check` without `--expect-eol`, so a file saved with CRLF passes silently; run `qw.py check FILE --expect-eol lf` yourself when line endings matter.

## Turning hooks on or off

- To turn the heredoc warning on: copy its entry from `hooks.example.json` into `hooks.json` in the installed plugin folder and restart. An update of the plugin replaces that folder, so the change does not survive one. Copying the entry into `~/.claude/settings.json` with the plugin path written out does survive.
- To turn a hook off: remove its entry from `hooks.json`, with the same caveat; or disable the plugin.
