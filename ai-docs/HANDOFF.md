# HANDOFF: quirkwright

Status: 0.1.0 built (step E); step F (prove) done 2026-11-15, see notes/prove.md: clean baseline 3/20 fail, with skill 25/26, worth TRIM (applied). Private repo, working name.

## State
- Step G done 2026-11-15: owner-specific notes live in the sidecar ($QUIRKWRIGHT_HOME/ai-docs/); leak test covers every tracked file. 23 unit tests pass.
- Evals: see the sidecar's ai-docs/notes/prove.md (clean baseline 3/20 fail; with skill 26/26 after fixes; worth TRIM applied).
- 0.2.1: kill guard and byte check hooks on (owner agreed 2026-11-15); heredoc hook stays off (hooks.example.json).

## Next
1. Wiki: written with wikiwright pinned to 0.2.1 (2026-11-15).
2. QUIRKWRIGHT_HOME must point at the private sidecar for the leak test.
3. Evergreen refresh due 2026-11-29 (see skills/quirkwright/evergreen.json).
