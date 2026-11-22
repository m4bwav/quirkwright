# Plugin cache and the VS Code panel

Checked: Claude Code 2.1.x (VS Code extension), Windows 11, 2026-11-15.

## Plugin cache

| Quirk | Rule | Repro |
|---|---|---|
| The plugin cache keeps every old version; a glob plus `head -1` reads the oldest. | Read `installPath` from `~/.claude/plugins/installed_plugins.json` (`qw.py doctor --plugin <name>`). | `ls ~/.claude/plugins/cache/<marketplace>/<plugin>/` |
| A skill installed mid-session is not callable with the Skill tool ("Unknown skill"). | Ask the user to type `/reload-plugins` (agents cannot run slash commands); until then read the installed SKILL.md and run its scripts from `installPath`. |
| Advice to "restart Claude Code" or "start a new session" to load a change is outdated. | Skill edits load live (`/reload-skills` forces it); plugin install, update or enable: the user types `/reload-plugins`; new session only for hooks, MCP, settings.json or CLAUDE.md the reload missed; never restart the desktop app. | install, then call it in the same session |
| claude.ai-synced skill copies under `~/.claude/skills/synced/` can be truncated. | Never edit or trust a synced copy; find the authoring source. | compare sizes with the source |

## VS Code chat panel

- Code spans cannot be selected or copied there, so a URL the user must paste elsewhere goes on the clipboard (`Set-Clipboard '<url>'`) and as a link.
- Bare `file:///` URLs and backticked paths render as dead text: name files as markdown links with forward slashes and `%20` for spaces.
