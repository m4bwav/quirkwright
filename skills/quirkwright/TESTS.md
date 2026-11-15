# Tests: quirkwright

Test runs for [SKILL.md](SKILL.md). Cases live in `evals/evals.json` (scratch folders under `<TMP>/qw-evals/<case-id>/`). Script tests: `python -m unittest discover -s tests` from the repo root (qw.py and the leak test). A test passes on evidence outside the transcript (a file's bytes, a command's exit code, a tool call), never on the reply's claim. Rules: MAINTENANCE.md and the evergreen plugin's `protocol/TESTING.md`.

Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`. Newest first. Budget 150 lines.

## Runs

### T-20261115-1 · 2026-11-15 · claude-code, one agent · baseline (no skill) · 3/17
- Bare model: 14 fail, 3 pass (eol-replace-crlf, cwd-parallel-cd, py-python3-stub, whose rules were dropped), 5 not run (eol-npm-lockfile, proc-stdin-hang, path-mcp-case, path-long-clone, vscode-clipboard-url), decoys not run.
- Skill-on runs of all 26 cases, 3 runs each, are still owed.
- led to: L-001 to L-012, C-001
