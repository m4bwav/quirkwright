# Plugin cache and the VS Code panel

Checked: Claude Code 2.1.x (VS Code extension), Windows 11, 2026-11-15.

## Plugin cache

| Quirk | Rule | Repro |
|---|---|---|
| The plugin cache keeps every old version; a glob plus `head -1` reads the oldest. | Read `installPath` from `~/.claude/plugins/installed_plugins.json` (`qw.py doctor --plugin <name>`). | `ls ~/.claude/plugins/cache/<marketplace>/<plugin>/` |
| A skill installed mid-session is not callable with the Skill tool ("Unknown skill"). | Read the installed SKILL.md and run its scripts from `installPath`. | install, then call it in the same session |
| claude.ai-synced skill copies under `~/.claude/skills/synced/` can be truncated. | Never edit or trust a synced copy; find the authoring source. | compare sizes with the source |

## VS Code chat panel

- Code spans cannot be selected or copied there, so a URL the user must paste elsewhere goes on the clipboard (`Set-Clipboard '<url>'`) and as a link.
- Bare `file:///` URLs and backticked paths render as dead text: name files as markdown links with forward slashes and `%20` for spaces.
