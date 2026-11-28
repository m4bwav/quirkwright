# AGENTS.md: quirkwright

Claude Code plugin (one skill) with Windows host rules for coding agents.

- Layout: `.claude-plugin/plugin.json`; `skills/quirkwright/` (SKILL.md hub, references/, scripts/qw.py, evals/, evergreen files); `hooks/` (kill guard and byte check on; heredoc off); `tests/`.
- Before committing: `python -m unittest discover -s tests` with `QUIRKWRIGHT_HOME` pointing at the private sidecar so the leak test uses the full term list.
- Never put owner paths, hosts, ports or names in any tracked file, ai-docs/ included. Owner facts go to the sidecar (`QUIRKWRIGHT_HOME/notes.md`).
- Hooks: kill guard and byte check are on in `hooks/hooks.json`; the heredoc warning stays off (`hooks.example.json`) until the owner asks.
- Python edits keep line endings; write Python with backslashes via a file tool, not a Bash heredoc.
- State and handoff: [ai-docs/HANDOFF.md](ai-docs/HANDOFF.md), log [ai-docs/log/](ai-docs/log/) (one file per event), index [ai-docs/INDEX.md](ai-docs/INDEX.md).
