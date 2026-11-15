# Changelog: quirkwright

Every change to [SKILL.md](SKILL.md) and its scripts, with the reason. Newest first.

## C-002 · 2026-11-15 · 0.2.0 · first public release
- Renamed from the working name hostwright (an active project owns that name); `qw.py`, `QUIRKWRIGHT_HOME`.
- `qw.py pid` matches Git Bash's quoted exe command lines (`"...sleep.exe" 60` matches `sleep 60`).
- Leak test covers every tracked file; working notes moved to the private sidecar. README, SECURITY.md, LICENSE, marketplace.json.
- because: step F eval proc-msys-pid found no match for a Git Bash process; going public.

## C-001 · 2026-11-15 · 0.1.0 · created
- Hub SKILL.md with eight rules, six references loaded on demand, `scripts/qw.py` (check, pid, wait, doctor), hooks shipped off, leak test.
- because: L-001 to L-012 (harvest plus bare-model baseline); rules whose baseline case passed bare were dropped (see LEARNINGS).
