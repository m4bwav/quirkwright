# Learnings: quirkwright

Lessons that shaped [SKILL.md](SKILL.md). Seeded 2026-11-15 from a harvest of one Windows owner's agent memory, environment profile and other skills' LEARNINGS files (45 lessons; the owner-specific ones live in the private sidecar, not here). Harvest numbers in brackets; baseline results from the bare-model run of `evals/evals.json`. Entry shape: `L-NNN code-name · date · source · lesson · fix`.

- L-001 `heredoc-halves-backslashes` · 2026-11-15 · harvest [1-3], baseline fail (a local hook had to refuse the bare model's heredoc) · A quoted heredoc still drops one backslash level; Windows paths and generated `\n` corrupt silently. · Write tool for files, `chr(92)`/`chr(10)` in code, forward slashes. Rule 1.
- L-002 `write-decodes-backslash-u` · 2026-11-15 · harvest [4], baseline fail · Write/Edit turn a backslash-u escape into the character. · Build it in code; `qw.py check` flags half-decoded escapes. Rule 2.
- L-003 `write-strips-trailing-space` · 2026-11-15 · harvest [9], not run · Trailing spaces vanish from Write output. · `chr(32)`; `qw.py check`.
- L-004 `msys-path-conversion` · 2026-11-15 · harvest [7], baseline fail (also mangled `tasklist /FI`) · Leading-slash args become Windows paths. · `MSYS_NO_PATHCONV=1`, `//flag`, or PowerShell. Rule 4.
- L-005 `python-textmode-crlf` · 2026-11-15 · harvest [10-12], baseline fail · Text-mode writes CRLF. · Bytes in, bytes out. Rule 3.
- L-006 `cp1252-stdout` · 2026-11-15 · harvest [15], baseline fail · Non-Latin output raises UnicodeEncodeError. · reconfigure stdout to UTF-8. Rule 3.
- L-007 `kill-by-pid-only` · 2026-11-15 · harvest [16-17], baseline judged fail · Image-name kills end other sessions' work; command-line kills hit Monitors. · `qw.py pid`. Rule 5.
- L-008 `msys-bang-pid` · 2026-11-15 · harvest [18], baseline fail · `$!` is the MSYS pid. · `qw.py pid` via CIM. Rule 5.
- L-009 `iofile-ignores-set-location` · 2026-11-15 · harvest [22], baseline fail · .NET file APIs resolve against the start folder. · Absolute paths. Rule 7.
- L-010 `localhost-ipv6-first` · 2026-11-15 · harvest [25], baseline fail (0.215 s vs 0.002 s) · Use 127.0.0.1. Rule 7.
- L-011 `wait-needs-fail-and-deadline` · 2026-11-15 · harvest [31-33], baseline fail · Success-only loops hang; stale failure lines and `"failed": []` give false wakes. · `qw.py wait`. Rule 6.
- L-012 `plugin-installpath` · 2026-11-15 · harvest [39-41], baseline fail · Cache globs pick old versions. · `installPath`. Rule 8.

Dropped after baseline (bare model passed): `str.replace` on CRLF in text mode [13], parallel-call shared cwd [21] (not reproduced), `python3` stub [26] (kept as a doctor check only). Not taken (owned by neighbours or too narrow): worktrees and shared clones [35-38] (chainwright), .NET AOT [29], WSL /tmp [30].
